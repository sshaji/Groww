# Groww SIP Lab

## Project goal

Develop and validate a rule-based investment approach that aims to increase net
returns over your current fixed ETF SIPs, within the same contribution budget and
an agreed level of risk. Account connectivity and return tracking support this goal.

The benchmark is ₹2,000 each Monday in Nifty BeES and ₹1,000 each Tuesday in ICICI
Next 50. Compare alternatives using identical dated contributions, starting
holdings, and valuation dates. Your historical lump-sum purchases must be included
equally when comparing from your actual portfolio; a larger contribution is not a
strategy improvement. ₹15,000/month remains an optional separate budget scenario.

Candidate experiments are reserve-funded dip buying, directing new contributions
toward underweight holdings, and momentum-based allocation between the two ETFs.
Only the fixed and dip-reserve simulations currently exist. None has yet shown
verified outperformance on real historical data in this project.

Success means better net terminal wealth and money-weighted return across multiple
unseen test periods, with drawdown, concentration, idle cash and costs reported.
Set acceptable risk limits before selecting a strategy. A single winning backtest
or a short period of better performance is not sufficient evidence.

The next milestone is a real-data comparison against fixed SIPs, followed by
forward paper testing. Include fees, slippage, data subscription costs, and taxes
where applicable. Keep a fixed-SIP outcome as a valid choice if alternatives do
not demonstrate a robust advantage. Live execution is a later, separately
authorized stage; this objective does not itself change your existing SIPs.

## Connected workflow

Your Groww account is connected through API credentials saved locally in `.env`.
The assistant can refresh your holdings and today's orders directly. **You do not
need to paste code or commands into Terminal for routine use.**

## How to use it

Ask the assistant to:

- “Refresh my Groww holdings.”
- “Check today's ETF purchases.”
- “Reconcile my transactions and update my SIP return.”
- “Compare my fixed SIP with the dip-reserve experiment.”

The assistant uses saved credentials when a refresh is needed. Groww may still
require daily approval on its API Keys page. The connection is used on request;
it is not a continuously running service.

## What is ready

| Capability | Status |
|---|---|
| Saved-credential login | Verified with this account on 7 September 2026 |
| Holdings and today's orders | Read-only refresh verified |
| ETF identification | `NIFTYBEES` and `NEXT50IETF` matched to holdings |
| Purchase history | Initial report imported and reconciled with the September 7 purchase |
| Personal return | First XIRR analysis completed as of September 7, 2026 |
| Strategy comparison | Fixed SIP and reserve-funded dip buying implemented; demo tested |
| Live quotes and historical candles | Require access outside the current free plan |

The first personal return uses screenshot market prices and excludes fees.
A fresh holdings snapshot alone does not refresh XIRR: complete transactions and
same-date market valuations are also needed. Average purchase cost is not market
value. The order API supplies today's orders, so older gaps may need a Groww report.

This project reads account data and simulates purchases. No live orders, SIP
changes, automatic trading, or background scheduling are implemented.

## Local files

| File | Purpose |
|---|---|
| `.env` | Private credentials; automatically loaded and excluded from Git |
| `config.json` | ETF symbols, weekly amounts and experiment parameters |
| `data/account-snapshot.json` | Latest successful account refresh, with timestamp |
| `data/imported-transactions.json` | Imported purchase history and source references |
| `data/personal.json` | Transactions and dated valuation inputs for personal XIRR |
| `reports/transaction-reconciliation.json` | Quantity reconciliation and missing inputs |
| `reports/personal-return.json` | Latest calculated personal-return report |
| `reports/comparison.json` | Latest strategy experiment; check its data source |
| `data/real-history.json` | Verified real-market bars, built from raw Yahoo downloads |
| `reports/data-quality.json` | Every repaired/excluded price gap, with its NSE source |

Personal data and reports are excluded from Git. Existing files are retained;
refresh timestamps and report valuation dates determine how current they are.

## Credentials and optional launchers

Credentials are already saved. The `.env` file is local plaintext with owner-only
permissions. Do not share it or put credentials in chat.

- **Connect Groww.command** is an optional double-click account refresh.
- **Save Groww Credentials.command** is for replacing credentials if they change.

There is no need to run either launcher for a normal request to the assistant.

## Development

The [project checkpoint](docs/PROGRESS.md) records completed work, current research,
data issues and next actions so a new IDE session can resume without repeating setup.

See [the development reference](docs/development.md) for commands, fresh-machine
setup, input formats, strategy rules, limitations and remaining work.
[AGENTS.md](AGENTS.md) records the saved-credentials workflow for future sessions.

An API makes rules repeatable; it does not guarantee higher returns. Synthetic
experiments are software checks, not evidence of market outperformance.
