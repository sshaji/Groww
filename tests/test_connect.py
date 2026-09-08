import unittest
from unittest.mock import Mock
from sip_lab.connect import snapshot


class SnapshotTests(unittest.TestCase):
    def test_reads_paginated_orders_without_trading(self):
        client = Mock()
        client.get_holdings_for_user.return_value = {'holdings': []}
        client.get_order_list.side_effect = [
            {'order_list': [{'groww_order_id': str(i)} for i in range(25)]},
            {'order_list': [{'groww_order_id': 'last'}]}]
        result = snapshot(client)
        self.assertEqual(len(result['today_orders']), 26)
        self.assertEqual(client.get_order_list.call_args.kwargs['page'], 1)
        client.place_order.assert_not_called()

    def test_repeated_page_rejected(self):
        client = Mock()
        client.get_holdings_for_user.return_value = {'holdings': []}
        client.get_order_list.return_value = {'order_list': [{'groww_order_id': str(i)} for i in range(25)]}
        with self.assertRaises(ValueError):
            snapshot(client)
