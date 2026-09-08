"""Money-weighted return for reconciled buy-only holdings, without live quotes."""
import math
from datetime import date

from .engine import xirr


def analyze(data, symbols):
    """Input is normalized JSON, not an assumed Groww export schema."""
    as_of = date.fromisoformat(data['as_of'])
    if not data.get('transactions'):
        raise ValueError('Complete dated purchase history is required')
    if set(data['holdings']) != set(symbols):
        raise ValueError('Provide valuations for exactly the configured ETFs')
    grouped = {s: [] for s in symbols}
    seen = set()

    def number(value, positive=False):
        if isinstance(value, bool) or not isinstance(value, (float, int)):
            raise ValueError('Amounts and quantities must be numbers')
        if not math.isfinite(value) or value < 0 or (positive and value == 0):
            raise ValueError('Invalid amount or quantity')
        return value

    for row in data['transactions']:
        identity = row['id']
        if not isinstance(identity, str) or not identity.strip() or identity in seen:
            raise ValueError('Each execution must have a unique nonempty ID')
        seen.add(identity)
        if row['side'] != 'BUY':
            raise ValueError('This initial personal-return calculator supports buys only; sells, transfers and corporate actions require reconciliation')
        day = date.fromisoformat(row['date'])
        if day > as_of:
            raise ValueError('Transaction occurs after valuation date')
        if row['symbol'] not in grouped:
            raise ValueError('Unexpected symbol in transaction history')
        grouped[row['symbol']].append((day, number(row['quantity'], True), number(row['total_paid'], True)))

    results, all_flows = [], []
    for symbol in symbols:
        rows = sorted(grouped[symbol])
        holding = data['holdings'][symbol]
        quantity = number(holding['quantity'], True)
        price = number(holding['price'], True)
        if not rows or not math.isclose(sum(r[1] for r in rows), quantity, abs_tol=1e-6, rel_tol=0):
            raise ValueError('Purchase quantities do not reconcile with holdings for ' + symbol)
        flows = [(day, -paid) for day, _, paid in rows]
        value = quantity * price
        invested = sum(r[2] for r in rows)
        all_flows.extend(flows)
        results.append(dict(symbol=symbol, quantity=quantity, invested=invested,
                            market_value=value, gain=value-invested,
                            xirr=xirr(flows + [(as_of, value)])))
    all_flows.sort()
    total_value = sum(r['market_value'] for r in results)
    total_invested = sum(r['invested'] for r in results)
    return dict(as_of=str(as_of), source=data.get('source', 'User supplied; unverified'),
                results=results, combined=dict(invested=total_invested, market_value=total_value,
                gain=total_value-total_invested, xirr=xirr(all_flows + [(as_of, total_value)])),
                limitations=['Buy-only calculation; requires complete history and no distributions or corporate actions',
                             'User must supply same-date market prices and actual purchase cash outflows',
                             'XIRR is annualized; short holding periods can produce misleading annualized figures'])
