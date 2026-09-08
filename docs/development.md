# Development reference

Routine account requests are handled by the assistant using saved credentials.
These commands are for development and troubleshooting, not user setup each time.
Run from the project root.

## Commands

```bash
# Refresh holdings and today's orders using .env
.venv/bin/python -m sip_lab.connect

# Read holdings without saving a snapshot
.venv/bin/python -m sip_lab holdings

# Recalculate using the dates and prices already in the input file
.venv/bin/python -m sip_lab personal-return --input data/personal.json

# Merge raw Yahoo downloads into verified, engine-ready real-market bars
.venv/bin/python -m sip_lab build-real-history

# Offline synthetic experiments (not actual market results)
.venv/bin/python -m sip_lab demo
.venv/bin/python -m sip_lab compare --prices data/demo.json
.venv/bin/python -m sip_lab compare --prices data/demo.json --monthly-budget 15000

# Real-market comparison (bounded by NEXT50IETF's December 2023 listing date)
.venv/bin/python -m sip_lab compare --prices data/real-history.json

# Tests
.venv/bin/python -m unittest discover -s tests -v
```

The comparison command defaults to overwriting `reports/comparison.json`.
Use `--output` to keep different experiments. A personal-return run uses the
input's valuation date, not today's date or fresh market prices.

## Installation on another machine

The current workspace is already installed and connected. For a fresh checkout:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e '.[groww]'
```

Then use `Save Groww Credentials.command` to enter credentials privately once.
Python 3.9+ is required. A current Python linked to OpenSSL avoids the LibreSSL
warning seen with Apple's older system Python. Do not disable TLS verification.

## Authentication and refresh

`sip_lab.auth` reads the project-root `.env` without shell evaluation. Nonempty
process environment variables override file values. API key/secret authentication
takes precedence over an access token. Tokens are generated per command and are
not saved. An existing process-level credential override may need to be cleared
when changing accounts or rotating credentials.

`Save Groww Credentials.command` authenticates before atomically saving credentials
with mode 0600. `Connect Groww.command` refreshes without credential prompts.
`.env` is plaintext on disk and Git-ignored. Neither launcher places orders.
The setup launcher is retained for rotation or recovery, not routine refreshes.

Refresh reads holdings and paginates today's CASH orders, writing a timestamped
snapshot only after all reads succeed. It does not merge orders into imported
history automatically. Failed refreshes leave the previous snapshot unchanged.
Check timestamps before reporting account values. SDK error details are suppressed
to avoid exposing credentials. Check network access and Groww daily approval
before asking for new credentials. No refresh runs in the background.

## Optional paid data capabilities

The user's current free plan excludes these endpoints. Do not treat them as
required steps for account connection or purchase a plan during routine work.

```bash
.venv/bin/python -m sip_lab quote NIFTYBEES
.venv/bin/python -m sip_lab fetch --start 2023-01-01 --end 2026-09-06
.venv/bin/python -m sip_lab compare --prices data/history.json
```

The adapter uses `get_historical_candles`, requests at most 180 calendar days per
chunk, and rejects mismatched ETF session dates. End dates must precede today.
History and live-quote access have not been verified on a paid plan.

## Calculate your personal SIP return

The `personal-return` command calculates individual and combined annualized XIRR from complete buy-only transaction history. It needs no API subscription or live quote call. It rejects duplicate execution IDs, transactions after the valuation date, and quantities that do not match the supplied holdings. Sells, distributions, transfers and corporate actions need additional reconciliation before using this initial calculator.

Download your complete Stocks transaction/order history through Groww Profile → Reports, from your first purchase through the valuation date. See [Groww's report instructions](https://groww.in/help/my-account/ma-others/where-can-i-get-the-transaction-history). The documented API order list covers orders placed during the day, not complete historical SIP transactions.

Place the original export in the git-ignored `data/` folder. Its actual columns must be inspected and mapped before import; the CLI does not yet directly import Groww Excel reports. Use the following normalized JSON structure in `data/personal.json` after reconciliation. These are **illustrative values, not your holdings or returns**:

```json
{
  "as_of": "2024-01-01",
  "source": "Illustrative example only",
  "transactions": [
    {"id": "example-1", "date": "2023-01-01", "symbol": "NIFTYBEES", "side": "BUY", "quantity": 10, "total_paid": 1000},
    {"id": "example-2", "date": "2023-01-01", "symbol": "NEXT50IETF", "side": "BUY", "quantity": 10, "total_paid": 1000}
  ],
  "holdings": {
    "NIFTYBEES": {"quantity": 10, "price": 110},
    "NEXT50IETF": {"quantity": 10, "price": 110}
  }
}
```

`total_paid` is the purchase cash outflow including known charges. Each ID identifies a distinct execution; include only executed purchases. `price` is the market price on `as_of`, not average purchase cost. Include the full position quantity, including unsettled purchases where applicable. Holdings and prices must share the same valuation date. If fees are unavailable, label the result as excluding them in `source`. Quantity reconciliation detects many missing records but cannot prove that the history or valuations are correct.

```bash
python -m sip_lab personal-return --input data/personal.json
```

The report is saved to `reports/personal-return.json`. The first account analysis was completed as of 7 September 2026 using imported orders, that day's API purchase, and screenshot market prices. Refreshing an account snapshot does not automatically update transaction history or this valuation.

## Experiment rules

Defaults in `config.json` reproduce ₹2,000 on Monday and ₹1,000 on Tuesday. This is roughly ₹13,000/month averaged over 52 weeks, not a fixed monthly amount. Both strategies receive exactly the same contributions on the same dates.

- **Fixed:** Invest available cash for the corresponding ETF when its contribution is due.
- **Dip reserve:** Invest 80% of each contribution. Keep 20% plus rounding leftovers in that ETF's cash reserve. At scheduled purchases, release half the existing reserve when the preceding close is at least 5% below the highest close in the previous 60 sessions; release all the existing reserve at a 10% fall. Each ETF has its own signal. Repeated qualifying purchases can release the remaining reserve again. These thresholds are research parameters, not validated recommendations.
- Signals use only completed prior sessions. Purchases use the current session's open plus estimated slippage. Before 60 sessions are available, no reserve is released.
- Buys use whole units, cannot borrow, and include estimated proportional costs. There are no sells. Reserve cash earns zero interest and can remain uninvested indefinitely.
- Holidays roll contributions to the next supplied session. Input must contain every actual session; jointly missing dates cannot be distinguished from holidays. Saturday bars are accepted (NSE has held genuine Saturday sessions); Sunday bars are rejected.
- `--monthly-budget 15000` divides that month's budget in a 2:1 ratio across its scheduled Mondays and Tuesdays. Funding arrives on scheduled dates, not all on the first day. Partial months include only dates within the input range; end-of-range holidays without a following session are not funded. It replaces the fixed weekly amounts for **both** strategies.

## Real-market data repair

`data/NIFTYBEES-yahoo-raw.json` and `data/NEXT50IETF-yahoo-raw.json` are raw
downloads from Yahoo Finance and contain null bars on some sessions. `sip_lab.history`
resolves each one against authoritative NSE records rather than dropping or
interpolating it: a null bar is either patched with the real NSE CM-segment
bhavcopy price, or excluded as a confirmed NSE CM holiday (checked against the
official holiday-master API). An unrecognized null bar raises instead of passing
through. Genuine Saturday sessions (e.g. Union Budget special trading) are kept.
Hardcoded patches/holidays are in `sip_lab/history.py`; re-verify and extend them
if new raw downloads introduce new null dates.

```bash
.venv/bin/python -m sip_lab build-real-history
```

Writes `data/real-history.json` (engine-ready bars) and `reports/data-quality.json`
(every patch/exclusion with its NSE source). The merged range is bounded by
NEXT50IETF's December 12, 2023 listing date — a short window, not yet a robust
multi-period comparison.

## Input and interpretation

You can supply a JSON file instead of fetching prices:

```json
{
  "source": "Describe provider, date range and corporate-action adjustments",
  "bars": [
    {"date": "2025-01-06", "NIFTYBEES": {"open": 260, "close": 261}, "NEXT50IETF": {"open": 70, "close": 71}}
  ]
}
```

Dates must be increasing, unique, and matched across both ETFs; prices must be positive and finite. Missing data should be repaired from its source. Use a consistent, verified treatment of splits and distributions. The engine does not model corporate actions, distributions, taxes, broker minimum fees, spread changes, liquidity constraints, or API subscription costs. Default 10 bps costs and 5 bps slippage are placeholders, not current Groww charges. These omissions can change which strategy appears better.

XIRR uses actual contribution dates and terminal portfolio value including cash. It returns null when undefined or outside the supported numerical bracket. Drawdown uses a daily return series neutralizing contributions at the beginning of each session; it is an approximation when overnight moves coincide with funding. Starting holdings are zero: this is not a measurement of your personal SIP return. That requires your dated transaction history.

An API provides consistent execution of rules; this project does not establish that dip buying outperforms SIPs. The return figures pasted in the original conversation have not been used as verified inputs. Compare multiple real market periods, costs, and cash drag before drawing conclusions.

## Remaining work

- Primary milestone: compare candidate investment rules with the fixed SIP benchmark
  using verified historical ETF data and identical contributions. Establish risk
  limits before choosing a strategy. Evaluate held-out periods, net terminal wealth,
  XIRR, drawdown, concentration, idle cash and all material costs.
- Add a repeatable Groww report importer and deduplicated daily-order reconciliation.
- Add same-date valuation inputs and explicit handling of fees, sells, distributions
  and corporate actions.
- Compare real historical periods and out-of-sample results before evaluating
  momentum, allocation changes, or contribution-only rebalancing.
- Add persistent forward paper trading and an exchange calendar.
- Treat any future live execution as a separate project stage, including order
  recovery, cash checks, partial fills, quote freshness and broker requirements.

## Official references

Reviewed on 7 September 2026:

- [Groww Python SDK](https://groww.in/trade-api/docs/python-sdk)
- [Historical candles and request limits](https://groww.in/trade-api/docs/python-sdk/backtesting)
- [Quotes](https://groww.in/trade-api/docs/python-sdk/live-data)
- [Holdings](https://groww.in/trade-api/docs/python-sdk/portfolio)
- [Parameter values](https://groww.in/trade-api/docs/python-sdk/annexures)

No live orders are placed by any command in this project.
