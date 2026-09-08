import copy
import json
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import Mock

from sip_lab.engine import simulate, xirr, momentum_target
from sip_lab.__main__ import demo
from sip_lab.broker import GrowwReader


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.c = json.loads(Path('config.json').read_text())
        self.c.update(cost_bps=0, slippage_bps=0)

    def bars(self, days, price=100):
        return [dict(date=d, **{s: dict(open=price, close=price) for s in self.c['symbols']}) for d in days]

    def test_exact_weekly_sip_and_accounting(self):
        r = simulate(self.bars(['2025-01-06', '2025-01-07']), self.c, 'fixed')
        self.assertEqual(r['contributed'], 3000)
        self.assertEqual([t['quantity'] for t in r['trades']], [20, 10])
        self.assertEqual(r['profit'], 0)

    def test_holiday_rolls_forward(self):
        r = simulate(self.bars(['2025-01-03', '2025-01-07']), self.c, 'fixed')
        self.assertEqual(r['contributed'], 3000)
        self.assertEqual(len(r['trades']), 2)
        self.assertTrue(all(t['date'] == '2025-01-07' for t in r['trades']))

    def test_same_funding_and_no_borrowing(self):
        bars = demo(self.c['symbols'])['bars']
        a, b = [simulate(bars, self.c, s) for s in ('fixed', 'dip_reserve')]
        self.assertEqual(a['contributed'], b['contributed'])
        for r in (a, b):
            self.assertTrue(all(p['cash'] >= -1e-8 for p in r['curve']))
            self.assertAlmostEqual(sum(t['total_cost'] for t in r['trades']) + r['cash'], r['contributed'])

    def test_monthly_budget_in_five_week_month(self):
        self.c['monthly_budget'] = 15000
        days = [str(date(2025, 3, 1) + timedelta(days=i)) for i in range(31)
                if (date(2025, 3, 1) + timedelta(days=i)).weekday() < 5]
        r = simulate(self.bars(days), self.c, 'fixed')
        self.assertAlmostEqual(r['contributed'], 15000)

    def test_no_same_day_close_signal(self):
        self.c['lookback_sessions'] = 2
        bars = self.bars(['2025-01-02', '2025-01-03', '2025-01-06'])
        changed = copy.deepcopy(bars)
        changed[-1]['NIFTYBEES']['close'] = 50
        a = simulate(bars, self.c, 'dip_reserve')
        b = simulate(changed, self.c, 'dip_reserve')
        self.assertEqual(a['trades'], b['trades'])

    def test_bad_data_rejected(self):
        for bad in (0, -1, float('nan'), float('inf')):
            with self.assertRaises(ValueError):
                simulate(self.bars(['2025-01-06'], bad), self.c, 'fixed')
        with self.assertRaises(ValueError):
            simulate(self.bars(['2025-01-06', '2025-01-06']), self.c, 'fixed')

    def test_saturday_session_accepted_sunday_rejected(self):
        r = simulate(self.bars(['2025-01-31', '2025-02-01']), self.c, 'fixed')
        self.assertEqual(r['curve'][-1]['date'], '2025-02-01')
        with self.assertRaises(ValueError):
            simulate(self.bars(['2025-01-31', '2025-02-02']), self.c, 'fixed')

    def test_momentum_target_falls_back_during_warmup(self):
        self.assertEqual(momentum_target([[100], [100]], 2, 0), 0)
        self.assertEqual(momentum_target([[100], [100]], 2, 1), 1)

    def test_momentum_target_picks_higher_trailing_return(self):
        histories = [[100, 90], [100, 120]]
        self.assertEqual(momentum_target(histories, 2, 0), 1)

    def test_momentum_redirects_contribution_to_stronger_symbol(self):
        self.c['lookback_sessions'] = 2
        days = ['2025-01-06', '2025-01-07', '2025-01-08', '2025-01-09', '2025-01-10', '2025-01-13']
        bars = self.bars(days)
        bars[4]['NEXT50IETF'] = dict(open=100, close=150)
        r = simulate(bars, self.c, 'momentum')
        monday_trade = next(t for t in r['trades'] if t['date'] == '2025-01-13')
        self.assertEqual(monday_trade['symbol'], 'NEXT50IETF')
        self.assertIn('momentum tilt', monday_trade['reason'])
        self.assertEqual(r['contributed'], 5000)

    def test_deep_dip_releases_only_existing_reserve(self):
        self.c['lookback_sessions'] = 3
        bars = self.bars(['2025-01-06', '2025-01-07', '2025-01-10', '2025-01-13'])
        bars[2]['NIFTYBEES']['close'] = 80
        r = simulate(bars, self.c, 'dip_reserve')
        trades = [t for t in r['trades'] if t['symbol'] == 'NIFTYBEES']
        self.assertEqual([t['quantity'] for t in trades], [16, 20])
        self.assertEqual(trades[-1]['reason'], 'dip reserve release')

    def test_xirr_known_cashflows(self):
        self.assertAlmostEqual(xirr([(date(2023, 1, 1), -1000), (date(2024, 1, 1), 1100)]), 0.1)

    def test_costs_reduce_value(self):
        self.c['cost_bps'] = 100
        r = simulate(self.bars(['2025-01-06']), self.c, 'fixed')
        self.assertGreater(r['fees'], 0)
        self.assertAlmostEqual(r['profit'], -r['fees'])

    def test_drawdown_excludes_deposits(self):
        r = simulate(self.bars(['2025-01-06', '2025-01-07']), self.c, 'fixed')
        self.assertAlmostEqual(r['max_drawdown'], 0)

    def test_adapter_read_only_contract(self):
        client = Mock()
        client.get_historical_candles.return_value = {'candles': [['2025-01-06T00:00:00', 100, 101, 99, 100, 10]]}
        rows = GrowwReader(client).history(self.c['symbols'], '2025-01-06', '2025-01-06')
        self.assertEqual(rows[0]['NIFTYBEES']['open'], 100)
        self.assertEqual(client.get_historical_candles.call_args.kwargs['groww_symbol'], 'NSE-NEXT50IETF')
        client.place_order.assert_not_called()


if __name__ == '__main__':
    unittest.main()
