"""Read-only Groww adapter using the shared local credential loader."""
from .auth import authenticated_client
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo


class GrowwReader:
    def __init__(self, client=None):
        if client is not None:
            self.client = client
            return
        self.client = authenticated_client()

    def holdings(self):
        return self.client.get_holdings_for_user(timeout=10)

    def quote(self, symbol):
        return self.client.get_quote(exchange='NSE', segment='CASH', trading_symbol=symbol)

    def history(self, symbols, start, end):
        start, end = date.fromisoformat(start), date.fromisoformat(end)
        if start > end or end >= datetime.now(ZoneInfo('Asia/Kolkata')).date():
            raise ValueError('Use an ordered date range ending before today (completed sessions only)')
        by_symbol = {}
        for symbol in symbols:
            rows = {}
            cursor = start
            while cursor <= end:
                last = min(cursor + timedelta(days=179), end)
                response = self.client.get_historical_candles(
                    exchange='NSE', segment='CASH', groww_symbol='NSE-' + symbol,
                    start_time=str(cursor) + ' 00:00:00', end_time=str(last) + ' 23:59:59',
                    candle_interval='1day')
                if not isinstance(response, dict) or not response.get('candles'):
                    raise ValueError('Empty or unexpected candle response; check symbol and data access')
                for candle in response['candles']:
                    timestamp = datetime.fromisoformat(candle[0])
                    if timestamp.tzinfo:
                        timestamp = timestamp.astimezone(ZoneInfo('Asia/Kolkata'))
                    day = timestamp.date().isoformat()
                    if not cursor <= date.fromisoformat(day) <= last:
                        raise ValueError('Candle outside requested range')
                    value = dict(open=float(candle[1]), close=float(candle[4]))
                    if day in rows:
                        raise ValueError('Duplicate daily candle returned')
                    rows[day] = value
                cursor = last + timedelta(days=1)
            by_symbol[symbol] = rows
        dates = set(by_symbol[symbols[0]])
        if any(set(by_symbol[s]) != dates for s in symbols):
            raise ValueError('ETF histories have different session dates; repair missing data before comparing')
        return [dict(date=d, **{s: by_symbol[s][d] for s in symbols}) for d in sorted(dates)]
