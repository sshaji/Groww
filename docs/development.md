# Development reference

All commands run from the project root. Groww access is read-only.

```bash
.venv/bin/python -m sip_lab.connect
.venv/bin/python -m sip_lab holdings
.venv/bin/python -m sip_lab quote RELIANCE
.venv/bin/python -m sip_lab fetch RELIANCE --start 2025-01-01 --end 2026-09-07
.venv/bin/python -m sip_lab download-public-history RELIANCE --output data/reliance-history.json
.venv/bin/python -m sip_lab paper-monthly --prices data/stock-history.json
.venv/bin/python -m unittest discover -s tests -v
```

`fetch` requires historical-candle API access and cannot request today. It writes
a normalized, one-symbol daily price file. `paper-monthly` compares monthly fixed
contributions with a 200-session trend filter using completed prior closes. No
live order endpoint is implemented.

`download-public-history` obtains unadjusted daily data from Yahoo Finance for
research only. It excludes the current, incomplete trading day's bar. It is not
a broker price feed and cannot be used for execution.

Credentials remain in Git-ignored `.env`; never print or commit them. Account
snapshots and reports are local financial records.
