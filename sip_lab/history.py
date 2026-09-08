"""Repairs raw Yahoo Finance daily bars into the engine's bars schema.

Every null bar in the raw Yahoo downloads was individually checked against
authoritative NSE records (checked 7 September 2026): either the NSE CM-segment
bhavcopy (nsearchives.nseindia.com) for a genuine trading session, or the official
NSE holiday master (nseindia.com/api/holiday-master) for an exchange holiday. No
gap is silently dropped or interpolated without one of these two resolutions.
"""
import json
from datetime import datetime
from pathlib import Path

PATCHES = {
    ('NIFTYBEES', '2025-10-24'): {
        'open': 294.99, 'close': 291.04,
        'source': 'NSE CM bhavcopy 2025-10-24 (matches user screenshot to displayed precision)'},
    ('NEXT50IETF', '2024-01-18'): {
        'open': 56.65, 'close': 55.95, 'source': 'NSE CM bhavcopy 2024-01-18'},
    ('NEXT50IETF', '2024-08-27'): {
        'open': 75.60, 'close': 77.91, 'source': 'NSE CM bhavcopy 2024-08-27'},
    ('NEXT50IETF', '2024-10-30'): {
        'open': 75.50, 'close': 73.19, 'source': 'NSE CM bhavcopy 2024-10-30'},
    ('NEXT50IETF', '2024-11-05'): {
        'open': 73.70, 'close': 72.69, 'source': 'NSE CM bhavcopy 2024-11-05'},
}

HOLIDAYS = {
    '2026-01-15': 'Municipal Corporation Election - Maharashtra (NSE CM holiday master)',
    '2026-05-01': 'Maharashtra Day (NSE CM holiday master)',
    '2026-05-28': 'Bakri Id (NSE CM holiday master)',
    '2026-06-26': 'Muharram (NSE CM holiday master)',
}

# Genuine NSE weekday>4 sessions confirmed via bhavcopy, not data errors. Recorded
# for provenance; the engine now accepts Saturday bars and only rejects Sunday.
SPECIAL_SESSIONS = {
    '2020-11-14': 'Diwali Muhurat trading (Saturday); NSE historical bhavcopy volume 901,758 shares',
    '2025-02-01': 'Union Budget special live trading session (Saturday); NSE CM bhavcopy matches Yahoo exactly',
}


def load_yahoo_bars(path):
    """Returns {date: {'open': float|None, 'close': float|None}} for one symbol."""
    result = json.loads(Path(path).read_text())['chart']['result'][0]
    quote = result['indicators']['quote'][0]
    gmtoffset = result['meta']['gmtoffset']
    bars = {}
    for i, ts in enumerate(result['timestamp']):
        day = datetime.utcfromtimestamp(ts + gmtoffset).date().isoformat()
        bars[day] = {'open': quote['open'][i], 'close': quote['close'][i]}
    return bars


def build_real_bars(symbol_paths):
    """symbol_paths: {symbol: raw Yahoo chart json path}. Returns (bars, quality_report)."""
    per_symbol = {symbol: load_yahoo_bars(path) for symbol, path in symbol_paths.items()}
    all_dates = sorted(set().union(*per_symbol.values()))
    bars, quality_report = [], []
    for day in all_dates:
        row = {'date': day}
        for symbol, series in per_symbol.items():
            entry = series.get(day)
            if entry is None:
                continue
            if entry['open'] is not None and entry['close'] is not None:
                row[symbol] = {'open': entry['open'], 'close': entry['close']}
                continue
            patch = PATCHES.get((symbol, day))
            if patch:
                row[symbol] = {'open': patch['open'], 'close': patch['close']}
                quality_report.append({'date': day, 'symbol': symbol, 'issue': 'null bar in Yahoo download',
                                       'resolution': 'patched from NSE bhavcopy', 'source': patch['source']})
            elif day in HOLIDAYS:
                quality_report.append({'date': day, 'symbol': symbol, 'issue': 'null bar in Yahoo download',
                                       'resolution': 'excluded: confirmed exchange holiday',
                                       'source': HOLIDAYS[day]})
            else:
                raise ValueError(f'Unresolved null bar for {symbol} on {day}; verify against NSE records '
                                  'before adding a patch or holiday entry')
        if all(symbol in row for symbol in per_symbol):
            bars.append(row)
    for day, note in SPECIAL_SESSIONS.items():
        if any(bar['date'] == day for bar in bars):
            quality_report.append({'date': day, 'symbol': None, 'issue': 'genuine weekday>4 session',
                                   'resolution': 'retained', 'source': note})
    return bars, quality_report
