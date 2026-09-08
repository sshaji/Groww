import calendar
import json
import unittest
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

from sip_lab.history import build_real_bars


def yahoo_raw(entries):
    """entries: [(date_str, open, close)] -> raw Yahoo chart JSON with gmtoffset 0."""
    timestamps, opens, closes = [], [], []
    for d, o, c in entries:
        y, m, day = (int(x) for x in d.split('-'))
        timestamps.append(calendar.timegm((y, m, day, 0, 0, 0)))
        opens.append(o)
        closes.append(c)
    return {'chart': {'result': [{
        'meta': {'gmtoffset': 0},
        'timestamp': timestamps,
        'indicators': {'quote': [{'open': opens, 'close': closes}]},
    }]}}


class HistoryTests(unittest.TestCase):
    def write(self, tmp, name, entries):
        path = Path(tmp) / name
        path.write_text(json.dumps(yahoo_raw(entries)))
        return str(path)

    def test_patches_known_null_bar(self):
        with TemporaryDirectory() as tmp:
            a = self.write(tmp, 'a.json', [('2025-10-24', None, None)])
            b = self.write(tmp, 'b.json', [('2025-10-24', 70, 71)])
            bars, report = build_real_bars({'NIFTYBEES': a, 'NEXT50IETF': b})
            self.assertEqual(bars, [{'date': '2025-10-24',
                                     'NIFTYBEES': {'open': 294.99, 'close': 291.04},
                                     'NEXT50IETF': {'open': 70, 'close': 71}}])
            self.assertEqual(report[0]['resolution'], 'patched from NSE bhavcopy')

    def test_excludes_confirmed_holiday(self):
        with TemporaryDirectory() as tmp:
            a = self.write(tmp, 'a.json', [('2026-01-14', 100, 101), ('2026-01-15', 100, 101)])
            b = self.write(tmp, 'b.json', [('2026-01-14', 70, 71), ('2026-01-15', None, None)])
            bars, report = build_real_bars({'NIFTYBEES': a, 'NEXT50IETF': b})
            self.assertEqual([bar['date'] for bar in bars], ['2026-01-14'])
            self.assertEqual(report[0]['resolution'], 'excluded: confirmed exchange holiday')

    def test_unresolved_null_bar_raises(self):
        with TemporaryDirectory() as tmp:
            a = self.write(tmp, 'a.json', [('2030-01-01', None, None)])
            b = self.write(tmp, 'b.json', [('2030-01-01', 70, 71)])
            with self.assertRaises(ValueError):
                build_real_bars({'NIFTYBEES': a, 'NEXT50IETF': b})

    def test_dates_before_second_symbol_listing_are_dropped(self):
        with TemporaryDirectory() as tmp:
            a = self.write(tmp, 'a.json', [('2020-01-01', 100, 101), ('2020-01-02', 100, 101)])
            b = self.write(tmp, 'b.json', [('2020-01-02', 70, 71)])
            bars, _ = build_real_bars({'NIFTYBEES': a, 'NEXT50IETF': b})
            self.assertEqual([bar['date'] for bar in bars], ['2020-01-02'])


if __name__ == '__main__':
    unittest.main()
