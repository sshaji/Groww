import unittest
from datetime import date

from sip_lab.public_data import parse_yahoo_chart


class PublicDataTests(unittest.TestCase):
    def test_parses_daily_bars_in_india_timezone(self):
        payload = {'chart': {'result': [{'timestamp': [1735756200, 1735842600],
                   'indicators': {'quote': [{'open': [100, 101], 'close': [101, 102]}]}}]}}
        result = parse_yahoo_chart(payload, 'TEST')
        self.assertEqual(result['symbol'], 'TEST')
        self.assertEqual(len(result['bars']), 2)
        self.assertEqual(result['bars'][0]['open'], 100.0)

    def test_rejects_missing_bar(self):
        payload = {'chart': {'result': [{'timestamp': [1735756200],
                   'indicators': {'quote': [{'open': [None], 'close': [100]}]}}]}}
        with self.assertRaisesRegex(ValueError, 'missing price'):
            parse_yahoo_chart(payload, 'TEST')

    def test_excludes_unfinished_or_future_daily_bar(self):
        payload = {'chart': {'result': [{'timestamp': [1735756200, 1735842600],
                   'indicators': {'quote': [{'open': [100, 101], 'close': [101, 102]}]}}]}}
        result = parse_yahoo_chart(payload, 'TEST', completed_through=date(2025, 1, 2))
        self.assertEqual(len(result['bars']), 1)
