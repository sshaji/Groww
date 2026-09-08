import argparse
import json
from pathlib import Path

from .broker import GrowwReader
from .paper import simulate_monthly
from .public_data import yahoo_history


def write_json(path, value):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def main():
    parser = argparse.ArgumentParser(description='Stock paper-trading research; no live orders')
    parser.add_argument('--config', default='config.json')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('holdings', help='Read Groww CASH holdings')
    quote = sub.add_parser('quote', help='Read a CASH-segment quote')
    quote.add_argument('symbol')
    fetch = sub.add_parser('fetch', help='Download completed daily CASH candles')
    fetch.add_argument('symbol')
    fetch.add_argument('--start', required=True)
    fetch.add_argument('--end', required=True)
    fetch.add_argument('--output', default='data/stock-history.json')
    public = sub.add_parser('download-public-history', help='Download public Yahoo Finance daily history for research')
    public.add_argument('symbol')
    public.add_argument('--period', default='10y')
    public.add_argument('--output', default='data/public-stock-history.json')
    paper = sub.add_parser('paper-monthly', help='Compare monthly fixed and trend paper strategies')
    paper.add_argument('--prices', required=True)
    paper.add_argument('--amount', type=float)
    paper.add_argument('--lookback', type=int)
    paper.add_argument('--output', default='reports/paper-monthly.json')
    args = parser.parse_args()
    try:
        config = json.loads(Path(args.config).read_text())
        if args.command == 'download-public-history':
            write_json(args.output, yahoo_history(args.symbol, args.period))
            print('Public research history written to ' + args.output)
            return
        if args.command == 'paper-monthly':
            data = json.loads(Path(args.prices).read_text())
            amount = args.amount or config['paper_monthly_budget']
            lookback = args.lookback or config['trend_lookback_sessions']
            results = [simulate_monthly(data['bars'], amount, lookback,
                                        config['cost_bps'], config['slippage_bps'], trend)
                       for trend in (False, True)]
            report = {'source': data.get('source', 'User-supplied prices; provenance unverified'),
                      'monthly_amount': amount, 'lookback_sessions': lookback,
                      'cost_bps': config['cost_bps'], 'slippage_bps': config['slippage_bps'],
                      'results': results,
                      'limitations': ['Paper simulation only; no order was placed',
                                      'No taxes, interest on cash, dividends, or corporate actions',
                                      'A backtest does not establish future outperformance']}
            write_json(args.output, report)
            for result in results:
                rate = 'n/a' if result['xirr'] is None else format(result['xirr'], '.2%')
                print(f"{result['strategy']:14} value ₹{result['final_value']:,.2f} | cash ₹{result['cash']:,.2f} | XIRR {rate}")
            print('Paper report written to ' + args.output)
            return
        broker = GrowwReader()
        if args.command == 'holdings':
            print(json.dumps(broker.holdings(), indent=2))
        elif args.command == 'quote':
            print(json.dumps(broker.quote(args.symbol), indent=2))
        else:
            rows = broker.history([args.symbol], args.start, args.end)
            bars = [{'date': row['date'], 'open': row[args.symbol]['open'],
                     'close': row[args.symbol]['close']} for row in rows]
            write_json(args.output, {'source': 'Groww completed daily CASH candles; adjustment status unverified',
                                     'symbol': args.symbol, 'bars': bars})
            print('Price history written to ' + args.output)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(2, 'Error: ' + str(exc) + '\n')
    except Exception as exc:
        # Do not print SDK messages: they can contain request details. The class
        # name is safe and distinguishes access/entitlement failures for support.
        parser.exit(2, 'Error: Groww request failed (' + type(exc).__name__ + '). Check API entitlement and inputs.\n')


if __name__ == '__main__':
    main()
