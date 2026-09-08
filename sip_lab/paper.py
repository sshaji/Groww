"""Monthly, single-ETF paper-strategy research. Never connects to a broker."""
import math
from datetime import date

def xirr(flows):
    """Annualized money-weighted return, if a numerical root can be found."""
    start = flows[0][0]
    years = [((day - start).days / 365.0, amount) for day, amount in flows]
    if not any(amount > 0 for _, amount in years):
        return None
    def npv(rate):
        return sum(amount / (1 + rate) ** elapsed for elapsed, amount in years)
    lo, hi = -0.9999, 100.0
    if npv(lo) * npv(hi) > 0:
        return None
    for _ in range(150):
        mid = (lo + hi) / 2
        if npv(mid) > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def validate_daily_bars(bars):
    if not bars:
        raise ValueError('Price history is empty')
    previous = None
    for bar in bars:
        day = date.fromisoformat(bar['date'])
        if previous is not None and day <= previous:
            raise ValueError('Dates must be unique and strictly increasing')
        previous = day
        for field in ('open', 'close'):
            value = bar[field]
            if not math.isfinite(value) or value <= 0:
                raise ValueError('Prices must be finite and positive')


def simulate_monthly(bars, monthly_amount, lookback_sessions, cost_bps, slippage_bps, trend):
    """Compare a monthly fixed investment with a cash-when-below-trend rule.

    Funding is deposited on the first supplied session each calendar month. The
    trend decision uses only closes before that session. All cash remains in the
    simulated portfolio and earns zero interest.
    """
    validate_daily_bars(bars)
    if not math.isfinite(monthly_amount) or monthly_amount <= 0:
        raise ValueError('Monthly amount must be finite and positive')
    if type(lookback_sessions) is not int or lookback_sessions < 2:
        raise ValueError('Lookback must be an integer >= 2')
    if any(not math.isfinite(x) or not 0 <= x <= 1000 for x in (cost_bps, slippage_bps)):
        raise ValueError('Costs and slippage must be between 0 and 1000 bps')

    cash = 0.0
    units = 0
    closes = []
    flows = []
    trades = []
    curve = []
    last_month = None
    fees = 0.0
    for bar in bars:
        day = date.fromisoformat(bar['date'])
        month = (day.year, day.month)
        funded = month != last_month
        if funded:
            cash += monthly_amount
            flows.append((day, -monthly_amount))
            last_month = month
            signal_ready = len(closes) >= lookback_sessions
            above_trend = signal_ready and closes[-1] > sum(closes[-lookback_sessions:]) / lookback_sessions
            should_buy = not trend or above_trend
            if should_buy:
                execution_price = bar['open'] * (1 + slippage_bps / 10000)
                per_unit = execution_price * (1 + cost_bps / 10000)
                quantity = math.floor(cash / per_unit)
                if quantity:
                    cost = quantity * per_unit
                    fee = quantity * execution_price * cost_bps / 10000
                    cash -= cost
                    units += quantity
                    fees += fee
                    trades.append({'date': str(day), 'quantity': quantity, 'price': execution_price,
                                   'cost': cost, 'fee': fee,
                                   'reason': 'above prior moving average' if trend else 'monthly fixed'})
        value = cash + units * bar['close']
        curve.append({'date': str(day), 'value': value, 'cash': cash, 'units': units})
        closes.append(bar['close'])
    final_value = curve[-1]['value']
    flows.append((date.fromisoformat(bars[-1]['date']), final_value))
    return {'strategy': 'monthly_trend' if trend else 'monthly_fixed',
            'contributed': monthly_amount * len({row['date'][:7] for row in bars}),
            'final_value': final_value, 'cash': cash, 'units': units, 'fees': fees,
            'xirr': xirr(flows), 'trades': trades, 'daily_values': curve}
