# Project checkpoint

Updated: 7 September 2026. Read this when resuming work in a new IDE session.

## Objective and user preferences

Develop and validate investment rules that aim to improve net returns over the
existing ₹2,000 Monday NIFTYBEES / ₹1,000 Tuesday NEXT50IETF SIPs. Compare equal
contributions, including costs, cash drag and risk. No strategy is proven better.
User wants the assistant to run commands and use saved credentials directly.
Do not ask the user to paste Python code or repeat completed setup.

## Completed

- Groww credentials stored locally in `.env`, Git-ignored, permissions 0600.
  Never include their contents in logs or documentation.
- Read-only account refresh verified. Use `.venv/bin/python -m sip_lab.connect`.
  Network restrictions may require an approved tool escalation.
- Account snapshot, imported transactions, reconciled history, personal valuation
  inputs and XIRR report exist in Git-ignored `data/` and `reports/`.
- User's original XLSX is in Downloads; its source filename is recorded in
  `data/imported-transactions.json`. It was read without modifying it.
- September 7 API buy was added to the transaction history. Both ETF quantities
  reconciled. Personal return was calculated using the user's screenshot prices,
  assuming September 7 valuation, excluding fees. See the report for amounts.
- Fixed SIP, reserve-funded dip-buying and momentum-tilt allocation simulations
  implemented (`sip_lab/engine.py`, strategies `fixed`/`dip_reserve`/`momentum`).
  Contribution-only underweight allocation is not implemented yet. Synthetic
  demo is not market evidence.
- README cleaned up; technical details in `docs/development.md`. Last full test
  run passed 21 tests before the current strategy-research milestone.

## Active work: real-data strategy comparison

User authorized proceeding with research and implementation. No trading, SIP
changes or subscription purchases are authorized by that request.

Public Yahoo Finance chart downloads succeeded and are saved locally:

- `data/NIFTYBEES-yahoo-raw.json`: 2,474 daily timestamps, September 2016–September 7, 2026.
- `data/NEXT50IETF-yahoo-raw.json`: 680 daily timestamps, December 12, 2023–September 7, 2026.

Endpoint pattern used:
`https://query1.finance.yahoo.com/v8/finance/chart/SYMBOL.NS?range=10y&interval=1d&events=div%2Csplits`

These are raw downloaded provider data, not yet an approved comparison dataset.
The September 7 closes agree with the user's screenshot to displayed precision.
No corporate-action events were returned; that does not prove none occurred.

NSE's December 14, 2023 circular confirms ICICINXT50 → NEXT50IETF:
https://nsearchives.nseindia.com/content/circulars/CML59760.pdf
An attempted Yahoo download for the former symbol returned HTTP 404; no usable
older history was saved. Do not substitute a different Next 50 ETF silently.

Data quality issues identified and resolved (7 September 2026), each checked against
authoritative NSE records, never interpolated or silently dropped:

- NIFTYBEES null bar on October 24, 2025: confirmed a genuine trading session via
  NSE CM bhavcopy (matches the user's screenshot); patched.
- NEXT50IETF null bars on January 18, August 27, October 30, November 5, 2024:
  confirmed genuine trading sessions via NSE CM bhavcopy; patched.
- NEXT50IETF null bars on January 15, May 1, May 28, June 26, 2026: confirmed
  official NSE CM-segment holidays (Maharashtra municipal election, Maharashtra
  Day, Bakri Id, Muharram) via the NSE holiday-master API; excluded, not patched.
- Both ETFs have a valid Saturday session on February 1, 2025 (Union Budget special
  live trading), confirmed via NSE CM bhavcopy matching Yahoo exactly. A second
  genuine Saturday session, NIFTYBEES-only Diwali Muhurat trading on November 14,
  2020, was also confirmed (bhavcopy volume 901,758 shares) but falls before
  NEXT50IETF's listing so does not affect the merged comparison range.
- `sip_lab/engine.py` `validate_bars` now rejects only Sunday bars, not all weekends.

Implementation: `sip_lab/history.py` (`build_real_bars`) merges the two raw Yahoo
downloads, applying hardcoded, sourced patches or holiday exclusions per date —
an unrecognized null bar raises rather than passing through silently. Run via
`.venv/bin/python -m sip_lab build-real-history`. Output: `data/real-history.json`
(676 bars, 2023-12-12 to 2026-09-07, engine-ready) and `reports/data-quality.json`
(every patch/exclusion with its NSE source). Covered by `tests/test_history.py`
and `tests/test_engine.py::test_saturday_session_accepted_sunday_rejected`.
22 -> 26 tests pass.

## First real-data comparison (7 September 2026)

Ran `.venv/bin/python -m sip_lab compare --prices data/real-history.json --output
reports/comparison.json` — single in-sample window, 2023-12-12 to 2026-09-07
(~2.75 years, bounded by NEXT50IETF's listing date), current `config.json` weekly
amounts, default 10 bps cost / 5 bps slippage. Not a held-out or multi-period test.

| | Fixed | Dip-reserve |
|---|---|---|
| Contributed | ₹429,000 | ₹429,000 |
| Final value | ₹443,105.65 | ₹442,444.00 |
| XIRR | 2.38% | 2.27% |
| Max drawdown | 18.96% | 17.60% |
| Idle cash at end | ₹128.19 | ₹14,984.47 |

Fixed SIP led on terminal value and XIRR; dip-reserve's smaller drawdown came with
substantial idle-cash drag (₹14,984 unreleased reserve at period end). One short
in-sample window is not evidence either strategy is better — no conclusion drawn.

## Two-period split (7 September 2026)

To get a first honest robustness check without new data (proxy-splicing) or engine
changes (a single-ETF test needs the two-symbol constraint relaxed), the same
676-bar real-history file was split at its midpoint into two non-overlapping,
roughly 16-month windows and each run independently through unmodified `compare`
(config parameters were never tuned to this data, so nothing needed "freezing"):

| | Period 1 (2023-12-12 – 2025-04-28) | Period 2 (2025-04-29 – 2026-09-07) |
|---|---|---|
| Fixed XIRR | 3.81% | -0.49% |
| Dip-reserve XIRR | 2.18% | 0.81% |
| Fixed drawdown | 18.96% | 14.52% |
| Dip-reserve drawdown | 17.60% | 12.42% |
| Winner on XIRR | Fixed | Dip-reserve |

The winner flips between the two halves — fixed clearly ahead in period 1, dip-reserve
ahead (and with a smaller drawdown) in period 2. This instability, on top of the full
2.75-year result (fixed narrowly ahead), is itself the finding: over the data available
so far neither strategy shows a consistent edge. Files: `data/real-history-period1.json`,
`data/real-history-period2.json`, `reports/comparison-period1.json`,
`reports/comparison-period2.json`. These 16-month windows are still short for the
60-session lookback signal; treat this as a first robustness check, not a final verdict.

## Momentum-tilt strategy added and tested (7 September 2026)

`sip_lab/engine.py` gained a third strategy, `momentum`: each scheduled contribution
is invested fully into whichever of the two ETFs had the higher trailing return over
`lookback_sessions` (reuses the existing config key, no new tunables), using only
completed prior sessions; falls back to its own scheduled ETF during warm-up or when
history is insufficient. Wired into the `compare` CLI. Tests in `tests/test_engine.py`
(`test_momentum_*`). 26 -> 29 tests pass.

Result on the same real data, all three strategies:

| | Full 2.75y | Period 1 | Period 2 |
|---|---|---|---|
| Fixed XIRR | 2.38% | 3.81% | -0.49% |
| Dip-reserve XIRR | 2.27% | 2.18% | 0.81% |
| Momentum XIRR | 2.74% | 1.16% | 1.00% |
| Fixed drawdown | 18.96% | 18.96% | 14.52% |
| Dip-reserve drawdown | 17.60% | 17.60% | 12.42% |
| Momentum drawdown | 21.34% | 21.34% | 14.83% |

No strategy wins consistently: fixed led period 1, momentum led the full period and
(barely) period 2, but momentum was worst in period 1 and had the highest drawdown of
the three in every window. Momentum is taking on more risk without reliably better
return — not a demonstrated edge. See `reports/comparison*.json` for full detail.

## Next actions

1. No strategy (fixed, dip-reserve, momentum) has shown a consistent, risk-adjusted
   edge across the periods available. Current honest conclusion: keep the fixed SIP
   unless/until one shows robustness across more, longer, independent periods.
2. Revisit extending real history further back (e.g. a Nifty Next 50 TRI proxy
   spliced with the real ETF from December 2023) if a longer, more conclusive
   out-of-sample test is wanted — only with proxy-tracking-error risk disclosed.
3. Add contribution-only underweight allocation as the remaining unimplemented
   candidate experiment.
4. Add risk/cash metrics beyond drawdown and idle cash (concentration, etc.).
   Freeze candidate rules before evaluating; no tuned "winner" claims.
5. Produce a reproducible comparison and an honest conclusion. Risk limits remain
   to be agreed before selecting or deploying a strategy. Forward paper testing
   and execution are later stages.

## Resume and update practice

Read `AGENTS.md`, this checkpoint, then relevant code and local report timestamps.
Update this file after milestones, data discoveries or blockers. Keep personal
financial figures in the existing local reports rather than this versionable file.
Credentials and local reports survive IDE closure but are not included in Git.
