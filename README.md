# Groww Stock Research Lab

Fresh, paper-only stock-strategy research. The project retains read-only Groww
account access; it never places, modifies, cancels, or schedules orders.

The paper budget is ₹2,000/month. Mutual funds remain the core investment.
Candidate rules are tested against fixed monthly investing using completed market
data, then must pass forward paper testing before any real-money discussion.

```bash
.venv/bin/python -m sip_lab.connect
.venv/bin/python -m sip_lab holdings
.venv/bin/python -m sip_lab quote RELIANCE
.venv/bin/python -m sip_lab fetch RELIANCE --start 2025-01-01 --end 2026-09-07
.venv/bin/python -m sip_lab download-public-history RELIANCE --output data/reliance-history.json
.venv/bin/python -m sip_lab paper-monthly --prices data/stock-history.json
.venv/bin/python -m unittest discover -s tests -v
```

The paper comparison invests monthly only when the prior close is above a prior
200-session moving average. It reports estimated costs and cash drag, but does
not model taxes, dividends, corporate actions, or future returns.
Public Yahoo Finance history is unadjusted research data and is never used to
submit an order.
