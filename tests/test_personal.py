import copy
import unittest

from sip_lab.personal import analyze


class PersonalTests(unittest.TestCase):
    def setUp(self):
        self.symbols = ['NIFTYBEES', 'NEXT50IETF']
        self.data = dict(as_of='2024-01-01', transactions=[
            dict(id=s, date='2023-01-01', symbol=s, side='BUY', quantity=10, total_paid=1000)
            for s in self.symbols], holdings={s: dict(quantity=10, price=110) for s in self.symbols})

    def test_known_returns(self):
        r = analyze(self.data, self.symbols)
        self.assertAlmostEqual(r['combined']['xirr'], .1)
        self.assertEqual(r['combined']['gain'], 200)

    def test_incomplete_history_rejected(self):
        self.data['holdings']['NIFTYBEES']['quantity'] = 11
        with self.assertRaises(ValueError):
            analyze(self.data, self.symbols)

    def test_duplicate_execution_rejected(self):
        self.data['transactions'].append(copy.deepcopy(self.data['transactions'][0]))
        with self.assertRaises(ValueError):
            analyze(self.data, self.symbols)

    def test_sale_rejected(self):
        self.data['transactions'][0]['side'] = 'SELL'
        with self.assertRaises(ValueError):
            analyze(self.data, self.symbols)

    def test_future_cashflow_rejected(self):
        self.data['transactions'][0]['date'] = '2024-01-02'
        with self.assertRaises(ValueError):
            analyze(self.data, self.symbols)
