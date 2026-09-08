"""Deterministic, buy-only simulation using prior closes and next session opens."""
import calendar
import math
from datetime import date, timedelta


def validate_config(c):
    if len(c['symbols']) != 2 or len(set(c['symbols'])) != 2:
        raise ValueError('Exactly two distinct symbols are required')
    if len(c['weekly_amounts']) != 2 or len(c['weekdays']) != 2:
        raise ValueError('Provide two amounts and two weekdays')
    for x in c['weekly_amounts']:
        if not math.isfinite(x) or x <= 0:
            raise ValueError('Weekly amounts must be finite and positive')
    if any(type(x) is not int or not 0 <= x <= 4 for x in c['weekdays']):
        raise ValueError('Weekdays must be integers from 0 (Monday) to 4')
    for key in ('reserve_fraction', 'dip_threshold', 'deep_dip_threshold'):
        if not math.isfinite(c[key]) or not 0 <= c[key] < 1:
            raise ValueError(key + ' must be in [0, 1)')
    if c['deep_dip_threshold'] <= c['dip_threshold']:
        raise ValueError('Deep dip threshold must exceed dip threshold')
    if type(c['lookback_sessions']) is not int or c['lookback_sessions'] < 2:
        raise ValueError('Lookback must be an integer >= 2')
    for key in ('cost_bps', 'slippage_bps'):
        if not math.isfinite(c[key]) or not 0 <= c[key] <= 1000:
            raise ValueError(key + ' must be between 0 and 1000')
    monthly = c.get('monthly_budget')
    if monthly is not None and (not math.isfinite(monthly) or monthly <= 0):
        raise ValueError('Monthly budget must be positive')


def validate_bars(bars, symbols):
    if not bars:
        raise ValueError('Price history is empty')
    previous = None
    for bar in bars:
        d = date.fromisoformat(bar['date'])
        if previous is not None and d <= previous:
            raise ValueError('Dates must be unique and strictly increasing')
        if d.weekday() > 5:
            raise ValueError('Sunday bars are unsupported')
        previous = d
        for symbol in symbols:
            for field in ('open', 'close'):
                value = bar[symbol][field]
                if not math.isfinite(value) or value <= 0:
                    raise ValueError('Prices must be finite and positive')


def momentum_target(histories, lookback, home):
    """Symbol index with the higher trailing return over completed prior sessions.
    Falls back to the home leg until both symbols have lookback sessions of history."""
    if any(len(h) < lookback for h in histories):
        return home
    returns = [h[-1] / h[-lookback] - 1 for h in histories]
    return returns.index(max(returns))


def contribution(day, index, c):
    if day.weekday() != c['weekdays'][index]:
        return 0.0
    if c.get('monthly_budget') is None:
        return float(c['weekly_amounts'][index])
    count = sum(date(day.year, day.month, n).weekday() == day.weekday()
                for n in range(1, calendar.monthrange(day.year, day.month)[1] + 1))
    weight = c['weekly_amounts'][index] / sum(c['weekly_amounts'])
    return c['monthly_budget'] * weight / count


def xirr(flows):
    """Annualized money-weighted return; None if no root in supported range."""
    start = flows[0][0]
    years = [((d - start).days / 365.0, amount) for d, amount in flows]
    if not any(t > 0 for t, _ in years):
        return None
    def npv(rate):
        return sum(amount / (1 + rate) ** t for t, amount in years)
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


def simulate(bars, c, strategy):
    validate_config(c)
    validate_bars(bars, c['symbols'])
    if strategy not in ('fixed', 'dip_reserve', 'momentum'):
        raise ValueError('Unknown strategy')
    symbols = c['symbols']
    cash, units, histories = [0.0, 0.0], [0, 0], [[], []]
    trades, curve, flows = [], [], []
    invested = fees = 0.0
    previous_day = date.fromisoformat(bars[0]['date']) - timedelta(days=1)
    previous_value = 0.0
    unit_nav = peak = 1.0
    max_dd = 0.0
    for bar in bars:
        day = date.fromisoformat(bar['date'])
        deposits = [0.0, 0.0]
        cursor = previous_day + timedelta(days=1)
        while cursor <= day:
            for i in range(2):
                deposits[i] += contribution(cursor, i, c)
            cursor += timedelta(days=1)
        total_deposit = sum(deposits)
        invested += total_deposit
        if total_deposit:
            flows.append((day, -total_deposit))
        for i, symbol in enumerate(symbols):
            old_cash = cash[i]
            cash[i] += deposits[i]
            # Execute only when a scheduled contribution is due. Holiday buys roll forward.
            if deposits[i]:
                allowance = cash[i]
                reason = 'scheduled'
                target = i
                if strategy == 'dip_reserve':
                    history = histories[i][-c['lookback_sessions']:]
                    drawdown = (1 - history[-1] / max(history)) if len(history) == c['lookback_sessions'] else 0
                    release = 1.0 if drawdown >= c['deep_dip_threshold'] else (0.5 if drawdown >= c['dip_threshold'] else 0.0)
                    allowance = deposits[i] * (1 - c['reserve_fraction']) + old_cash * release
                    reason = 'dip reserve release' if release else 'scheduled with reserve'
                elif strategy == 'momentum':
                    target = momentum_target(histories, c['lookback_sessions'], i)
                    reason = 'scheduled' if target == i else 'momentum tilt to ' + symbols[target]
                target_symbol = symbols[target]
                price = bar[target_symbol]['open'] * (1 + c['slippage_bps'] / 10000)
                per_unit = price * (1 + c['cost_bps'] / 10000)
                quantity = math.floor(min(allowance, cash[i]) / per_unit)
                if quantity:
                    cost = quantity * per_unit
                    fee = quantity * price * c['cost_bps'] / 10000
                    cash[i] -= cost
                    units[target] += quantity
                    fees += fee
                    trades.append(dict(date=bar['date'], symbol=target_symbol, quantity=quantity,
                                       simulated_price=price, fees=fee, total_cost=cost, reason=reason))
            histories[i].append(bar[symbol]['close'])
        value = sum(cash) + sum(units[i] * bar[s]['close'] for i, s in enumerate(symbols))
        # Daily return neutralizes contributions assumed available before today's open.
        base = previous_value + total_deposit
        if base:
            unit_nav *= value / base
        peak = max(peak, unit_nav)
        max_dd = max(max_dd, 1 - unit_nav / peak)
        curve.append(dict(date=bar['date'], value=value, contributed=invested, cash=sum(cash),
                          units=dict(zip(symbols, units)), unit_nav=unit_nav))
        previous_value, previous_day = value, day
    annualized = xirr(flows + [(previous_day, previous_value)]) if flows else None
    return dict(strategy=strategy, contributed=invested, final_value=previous_value,
                profit=previous_value - invested, cash=sum(cash), fees=fees,
                xirr=annualized, max_drawdown=max_dd, trades=trades, curve=curve)
