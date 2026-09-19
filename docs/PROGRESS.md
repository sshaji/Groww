# Project checkpoint

Updated: 19 September 2026.

## Current objective

Fresh paper-only stock research using a ₹2,000 monthly budget. Mutual funds are
the core investment. Validate a rule on real completed data, benchmark it against
fixed monthly investing, and forward-paper-test it. No real orders are authorized.

The user is new to stock trading and wants the assistant to use Groww API access
to make the research disciplined and understandable. Keep explanations plain.
Do not offer tips, intraday trading, options, leverage, penny stocks, or automatic
execution. The user must explicitly approve every real purchase, separately.

## Current setup

- Groww credentials are configured locally. Refresh is read-only. On 8 September
  2026, Groww required fresh daily API-key approval. The user approved the key,
  and a subsequent read-only refresh succeeded and saved `data/account-snapshot.json`.
  `sip_lab.auth` now reports approval failures safely without exposing credential
  or request details. Full suite: 9 tests pass.
- The documented Groww Trading API covers CASH/FNO and has no dedicated mutual
  fund holdings or SIP endpoint.
- On 8 September 2026, account refresh succeeded but a read-only RELIANCE quote
  and completed-candle request both returned Groww's generic API exception. This
  establishes that account access works while stock market-data entitlement is
  unavailable or otherwise not enabled; it does not indicate a credential issue.
  Do not claim that the API can yet supply quotes or history for strategy testing.
- Public Yahoo Finance history was added as a research-only fallback. It rejects
  missing price bars and excludes the current incomplete session. Ten years of
  completed daily data were downloaded for the paper watchlist: RELIANCE, TCS,
  and HDFCBANK. The same monthly 200-session trend rule did not show a consistent
  advantage: fixed monthly buying led for RELIANCE and HDFCBANK; the trend rule
  only narrowly led for TCS while retaining substantial idle cash. No stock or
  rule is selected for paper entry, and no purchase is suggested. `public_data`
  tests plus the rest of the suite: 12 tests pass.
- The former ETF-SIP simulator, history repair, personal-return calculator, their
  configuration and tests were removed at the user's request. Git-ignored data,
  reports and credentials were preserved as financial records.
- New paper comparison: one symbol, fixed monthly buying vs prior 200-session
  moving-average filter. It never contacts the order endpoint.
- `data/paper-trading-plan.json` records the ₹2,000 paper budget and ₹1,000
  monthly / ₹3,000 cumulative loss-review thresholds.
- The user supplied a Groww Orders screenshot confirming both ETF delivery sales
  on 8 September 2026. The immediately preceding holdings API snapshot still
  showed the positions and omitted the orders, so treat it as a settlement/timing
  mismatch. The user-confirmed executions are recorded locally in
  `data/investment-status.json`; do not use the stale ETF holdings as an active
  allocation.

## Immediate next step

Define a small, liquid beginner-friendly paper watchlist, then obtain enough
completed price history before testing or suggesting any candidate rule. No
background polling is set up.

On 11 September 2026, the user asked about the Veegaland Developers IPO. The
screen was set to 10 lots (1,070 shares; up to ₹149,800), which is inconsistent
with the ₹2,000 monthly research budget. Research found improving FY24–FY26
revenue and PAT, but a roughly 25.6x post-issue FY26 P/E, Kerala/project
concentration, and negative FY26 operating cash flow. No order was authorized;
the conservative view is to skip, or—if the user independently accepts IPO risk—
limit exposure to one lot at cutoff rather than 10 lots.

## Next work

Add risk metrics and split the three completed histories into independent periods.
Only then forward-paper-test a candidate that survives. No background polling is
set up.

## Mutual-fund morning review — 19 September 2026

The user requested ongoing dip/top-up research for four existing Direct Growth
mutual funds, then chose to invoke a skill manually each morning. This is separate
from the stock paper lab. No investment execution or SIP changes are authorized.
The user explicitly asked that the plan and review history persist across sessions.

- Installed personal skill: `/Users/Shaji/.codex/skills/daily-mf-topup-review/SKILL.md`.
- Visible user guide: `MY-MF-PLAN.md` in the project root (Git-ignored because it
  contains personal financial details). Keep this guide and the private watchlist
  consistent when the user changes the agreed plan. It contains the morning
  checklist and links to review history.
- Private agreed budget, horizon, scheme IDs and screenshot provenance are in
  `data/mf-watchlist.json`; read it at the start of a mutual-fund review.
- AMFI's latest report was downloaded successfully to
  `data/mf-nav-source-2026-09-19.txt`. The new eight-column format separates scheme,
  plan and option. Each scheme's NAV date must be checked independently.
- Initial report: `reports/mf-review-2026-09-19.md`. Full 52-week history and
  portfolio allocation review remain outstanding; no current top-up signal has
  been established. Thresholds in the skill are review heuristics, not buy rules.
- Save each subsequent review under `reports/`; record purchases only when the
  user confirms execution, never when a recommendation is merely made.
- No scheduler is active. This session had no scheduling tool, and Computer Use
  refused access to the ChatGPT app. The user subsequently chose manual invocation.
