import unittest

from sip_lab.paper import simulate_monthly


def bars(prices):
    return [{'date': f'2025-{i + 1:02d}-01', 'open': price, 'close': price} for i, price in enumerate(prices)]


class PaperTests(unittest.TestCase):
    def test_fixed_invests_each_month(self):
        result = simulate_monthly(bars([100, 100, 100]), 1000, 2, 0, 0, False)
        self.assertEqual(result['units'], 30)
        self.assertEqual(result['cash'], 0)

    def test_trend_retains_cash_below_prior_average(self):
        result = simulate_monthly(bars([100, 90, 80, 70]), 1000, 2, 0, 0, True)
        self.assertEqual(result['units'], 0)
        self.assertEqual(result['cash'], 4000)

    def test_trend_uses_only_prior_closes(self):
        result = simulate_monthly(bars([100, 90, 120]), 1000, 2, 0, 0, True)
        self.assertEqual(result['units'], 0)  # 120 close cannot authorize its own buy


if __name__ == '__main__':
    unittest.main()
