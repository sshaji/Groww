import argparse
import json
import math
from datetime import date, timedelta
from pathlib import Path

from .engine import simulate, validate_config, validate_bars
from .broker import GrowwReader
from .personal import analyze
from .history import build_real_bars


def demo(symbols):
    bars = []
    day = date(2023, 1, 2)
    for n in range(1095):
        d = day + timedelta(days=n)
        if d.weekday() < 5:
            row = {'date': str(d)}
            for i, s in enumerate(symbols):
                price = (200 + i * 100) * math.exp(n * 0.00018 + (0.10 + i * 0.04) * math.sin(n / 85))
                row[s] = {'open': round(price, 2), 'close': round(price * (1 + 0.002 * math.sin(n)), 2)}
            bars.append(row)
    return {'source': 'SYNTHETIC DEMO — not historical market prices', 'bars': bars}


def write_json(path, value):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def main():
    p = argparse.ArgumentParser(description='Groww ETF SIP research; no live orders')
    p.add_argument('--config', default='config.json')
    sub = p.add_subparsers(dest='command', required=True)
    personal = sub.add_parser('personal-return', help='Calculate buy-only personal XIRR from reconciled transaction JSON')
    personal.add_argument('--input', required=True)
    personal.add_argument('--output', default='reports/personal-return.json')
    sample = sub.add_parser('demo', help='Generate clearly labelled artificial price history')
    sample.add_argument('--output', default='data/demo.json')
    compare = sub.add_parser('compare', help='Compare fixed SIP and reserve-funded dip buying')
    compare.add_argument('--prices', required=True)
    compare.add_argument('--output', default='reports/comparison.json')
    compare.add_argument('--monthly-budget', type=float)
    sub.add_parser('holdings', help='Read Groww holdings')
    quote = sub.add_parser('quote', help='Read a configured ETF quote')
    quote.add_argument('symbol')
    history = sub.add_parser('fetch', help='Download completed daily ETF candles')
    history.add_argument('--start', required=True)
    history.add_argument('--end', required=True)
    history.add_argument('--output', default='data/history.json')
    repair = sub.add_parser('build-real-history',
                             help='Merge raw Yahoo downloads into verified bars, patching or excluding null sessions')
    repair.add_argument('--niftybees', default='data/NIFTYBEES-yahoo-raw.json')
    repair.add_argument('--next50ietf', default='data/NEXT50IETF-yahoo-raw.json')
    repair.add_argument('--output', default='data/real-history.json')
    repair.add_argument('--quality-report', default='reports/data-quality.json')
    args = p.parse_args()
    try:
        c = json.loads(Path(args.config).read_text())
        if getattr(args, 'monthly_budget', None) is not None:
            c['monthly_budget'] = args.monthly_budget
        validate_config(c)
        if args.command == 'personal-return':
            result = analyze(json.loads(Path(args.input).read_text()), c['symbols'])
            write_json(args.output, result)
            print(json.dumps(result, indent=2, allow_nan=False))
        elif args.command == 'demo':
            write_json(args.output, demo(c['symbols']))
            print('Synthetic demo written to ' + args.output)
        elif args.command == 'compare':
            data = json.loads(Path(args.prices).read_text())
            results = [simulate(data['bars'], c, s) for s in ('fixed', 'dip_reserve', 'momentum')]
            report = {'source': data.get('source', 'User-supplied prices; provenance unverified'),
                      'config': c, 'results': results,
                      'limitations': ['Simulation only; no guaranteed outperformance',
                                      'No taxes, distributions, corporate actions or interest on cash',
                                      'Costs and slippage are estimates, not a broker tariff',
                                      'XIRR is annualized; short periods can be misleading']}
            write_json(args.output, report)
            print(report['source'])
            for r in results:
                rate = 'n/a' if r['xirr'] is None else format(r['xirr'], '.2%')
                print(f"{r['strategy']:12} contributed ₹{r['contributed']:,.2f} | value ₹{r['final_value']:,.2f} | cash ₹{r['cash']:,.2f} | XIRR {rate} | drawdown {r['max_drawdown']:.2%}")
            print('Detailed simulated trades and daily values: ' + args.output)
        elif args.command == 'build-real-history':
            bars, quality_report = build_real_bars({'NIFTYBEES': args.niftybees, 'NEXT50IETF': args.next50ietf})
            validate_bars(bars, c['symbols'])
            write_json(args.output, {'source': 'NIFTYBEES and NEXT50IETF daily bars from Yahoo Finance, '
                                      'repaired against NSE bhavcopy/holiday records; see quality report',
                                      'bars': bars})
            write_json(args.quality_report, quality_report)
            print(f'{len(bars)} verified bars written to {args.output}')
            print(f'{len(quality_report)} anomalies resolved; report at {args.quality_report}')
        else:
            if args.command == 'quote' and args.symbol not in c['symbols']:
                raise ValueError('Symbol must be one of the configured ETFs')
            broker = GrowwReader()
            try:
                if args.command == 'holdings':
                    print(json.dumps(broker.holdings(), indent=2))
                elif args.command == 'quote':
                    print(json.dumps(broker.quote(args.symbol), indent=2))
                else:
                    bars = broker.history(c['symbols'], args.start, args.end)
                    validate_bars(bars, c['symbols'])
                    write_json(args.output, {'source': 'Groww daily candles; adjustment status unverified', 'bars': bars})
                    print('Price history written to ' + args.output)
            except ValueError:
                raise
            except Exception:
                # SDK errors can contain request headers; never echo them or the access token.
                raise ValueError('Groww request failed. Check token validity, API access, symbols and requested dates.') from None
    except (ValueError, KeyError, TypeError, OSError) as exc:
        p.exit(2, 'Error: ' + str(exc) + '\n')


if __name__ == '__main__':
    main()
