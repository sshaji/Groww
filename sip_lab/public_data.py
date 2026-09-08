"""Public price-data download for research only; never used for live execution."""
import json
import re
from datetime import date, datetime, timedelta
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo


def yahoo_history(symbol, period='10y'):
    if not re.fullmatch(r'[A-Z0-9&-]+', symbol):
        raise ValueError('Symbol must contain only uppercase letters, numbers, &, or -')
    query = urlencode({'range': period, 'interval': '1d', 'events': 'div,splits'})
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}.NS?{query}'
    try:
        request = Request(url, headers={'User-Agent': 'GrowwStockResearchLab/1.0'})
        with urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode('utf-8'))
    except Exception:
        raise ValueError('Public Yahoo Finance download failed.') from None
    return parse_yahoo_chart(payload, symbol)


def parse_yahoo_chart(payload, symbol, completed_through=None):
    try:
        result = payload['chart']['result'][0]
        timestamps = result['timestamp']
        quote = result['indicators']['quote'][0]
        opens, closes = quote['open'], quote['close']
    except (KeyError, IndexError, TypeError):
        raise ValueError('Unexpected Yahoo Finance price response.') from None
    if not (len(timestamps) == len(opens) == len(closes)):
        raise ValueError('Yahoo Finance response has inconsistent bar lengths.')
    completed_through = completed_through or (datetime.now(ZoneInfo('Asia/Kolkata')).date() - timedelta(days=1))
    bars = []
    for timestamp, opening, close in zip(timestamps, opens, closes):
        if opening is None or close is None:
            raise ValueError('Yahoo Finance response has a missing price bar.')
        try:
            day = datetime.fromtimestamp(timestamp, ZoneInfo('Asia/Kolkata')).date().isoformat()
            opening, close = float(opening), float(close)
        except (TypeError, ValueError, OverflowError):
            raise ValueError('Yahoo Finance response has an invalid price bar.') from None
        if opening <= 0 or close <= 0:
            raise ValueError('Yahoo Finance response has a non-positive price bar.')
        if date.fromisoformat(day) > completed_through:
            continue
        bars.append({'date': day, 'open': opening, 'close': close})
    if not bars or any(bars[i]['date'] >= bars[i + 1]['date'] for i in range(len(bars) - 1)):
        raise ValueError('Yahoo Finance response has invalid bar dates.')
    return {'source': f'Yahoo Finance daily NSE data for {symbol}.NS; unadjusted OHLC; research only',
            'symbol': symbol, 'bars': bars}
