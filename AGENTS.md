# Working in this project

Read `docs/PROGRESS.md` at the start of a resumed session. Update it after meaningful
milestones or discoveries so work can continue after closing and reopening the IDE.

## Objective

The project aims to increase net investment returns over the user's fixed ETF
SIPs through validated rule-based investing. Connectivity and reporting are
supporting capabilities. Prioritize a real-data, equal-contribution benchmark,
cost and risk evaluation, and forward paper testing. Do not claim that a strategy
is better without evidence or infer authorization to change SIPs or place trades.
Candidate strategies and acceptance criteria are recorded in README.md.

## Account workflow

The user's Groww API credentials are already configured in the local `.env`.
Authenticated holdings and today's order reads were verified on 7 September 2026.

- For requested account refreshes, run `.venv/bin/python -m sip_lab.connect`
  from the project root. Read `data/account-snapshot.json` after success and check
  its `fetched_at`. The user does not need to paste terminal commands, re-enter
  credentials, or provide holdings screenshots for data available through the API.
- Never print, copy into reports, or commit `.env` values. Let `sip_lab.auth`
  load them. Never source `.env` as shell code. Keep it private with mode 0600
  and Git-ignored. Use the setup launcher only for credential changes.
- If the sandbox blocks networking, use the approved network escalation mechanism
  for the requested read. Do not assume an authentication failure means bad keys.
  Groww may require daily approval; request user action only when needed.
- Account refresh is read-only. No order placement, subscription purchase, SIP
  changes, or background scheduler is authorized by a request to inspect data.
- The current free plan excludes live quotes and historical candles. Today's
  orders do not replace a full historical report. Explain a missing input only
  after checking existing local files and available account data.
- Preserve `data/`, `reports/`, the virtual environment, and credential files
  during cleanup. Financial records belong in Git-ignored local files, not docs.
- Keep historical transaction provenance, prevent duplicate imports, and reconcile
  quantities against same-date holdings before calculating returns. Never use an
  average purchase price as a current valuation. Label screenshot valuation dates,
  omitted fees, and synthetic demo results explicitly.
- Run `.venv/bin/python -m unittest discover -s tests -v` for relevant code changes.
  See `docs/development.md` for commands, schemas, and model limitations.
