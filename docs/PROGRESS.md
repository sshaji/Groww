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

The first manual review is now saved in `reports/mf-review-2026-09-19.md`;
the original setup is preserved in `reports/mf-setup-2026-09-19.md`. MFapi histories
were matched by scheme code/ISIN and latest NAV against AMFI; PPFAS also matched
its AMC page. Source snapshots and calculated metrics are cached under
`data/mf-review-2026-09-19/`. Official NSE daily snapshots were retrieved for
benchmark context. The report identifies a screening candidate but no purchase
amount; complete allocation/cash information and further fund-context review
remain outstanding. Initial observed levels are saved in the private watchlist
to distinguish existing conditions from new crossings on subsequent runs.


The user also requested attention to brief event-related dips. Morning MF reviews
should inspect one-session and five-trading-session fund/benchmark moves and
any rebound, without waiting for the longer-term drawdown thresholds. Verify
news attribution; do not assume war-related declines recover within days or
promise an observed NAV for a new purchase. Manual runs are not intraday monitoring.

On 20 September 2026, the user shared a full Groww Mutual Funds dashboard
screenshot: 12 holdings, ₹66,96,435 current value, ₹60,72,146 invested, +10.28%
total return, 10.40% XIRR. Saved as `portfolio_dashboard_snapshot_2026_09_20`
in `data/mf-watchlist.json`, with a summary and two open items added to
`MY-MF-PLAN.md`: (1) ICICI Prudential Flexi Cap is held twice — once as the
tracked Direct-plan SIP, once as a separate External Regular-plan holding of
the same scheme, which only adds expense-ratio drag, not diversification; (2)
7 of the 12 holdings (~₹19.7L) sit outside the daily dip-review's 4-fund scope
and get no systematic drawdown tracking. Neither item has been acted on — no
SIP change, switch, or consolidation was authorized or made. The user then
confirmed (20 September 2026) that moving money out of the Regular-plan
holdings, after checking tax (capital gains) and cost (exit load) implications
themselves, is already their own plan — not an open question for the assistant
to keep raising. Record the actual switch/redemption once the user executes it.

Also on 20 September 2026: the user confirmed the ₹10,000 HDFC Nifty 50 SIP
cut (₹50k→₹40k) was intentional, freed for manual dip top-ups rather than a
fixed SIP. They then replaced the old ₹10 lakh/12-month top-up budget entirely
with a simpler monthly cap: **₹2,00,000–₹2,50,000/month total, combined across
SIPs + manual top-ups** — against the ₹1,50,000/month fixed SIP, this leaves
roughly ₹50,000–₹1,00,000/month of flexible top-up capacity. `MY-MF-PLAN.md`
and `data/mf-watchlist.json` (`topup_budget_inr` set to null,
`topup_budget_superseded`, `monthly_investment_capacity_confirmed_2026_09_20`)
were updated to reflect this as the new governing budget. Two things still
unconfirmed: whether unused monthly flexible capacity rolls forward to the
next month, and actual liquid cash on hand today (`available_topup_cash_now_inr`
remains unset) — relevant given HDFC Nifty 50 is the live -10.66% candidate.

A default monthly top-up sizing rule was also agreed and saved in
`MY-MF-PLAN.md`: tiers of 5/10/15/20% decline from 52-week high map to
~15-20%/40-50%/70-100%/100% of that month's flexible budget, defaulting to a
~20-25k top-up into HDFC Nifty 50 if nothing else qualifies, with a
15-20%-of-holding-value-per-3-months guardrail against overconcentration.

The user twice asked about replacing an existing SIP fund (ICICI Prudential
Flexicap, then SBI Gold) with a high-performing small-cap fund (prompted by a
Bandhan Small Cap Fund screenshot) -- both declined: ICICI Flexicap's edge
over Bandhan has closed to near-parity on 1Y trailing returns and it fills a
distinct aggressive-domestic role alongside Parag Parikh; gold is the
portfolio's only non-equity ballast and swapping it for small-cap would
increase correlation, not diversify it. The user then reframed the idea as
small-cap for a dip-only top-up strategy (no SIP), which was agreed as sound.
Bandhan Small Cap Fund Direct Growth was added to
`data/mf-watchlist.json` -> `watch_only_candidates` (not held; 52-week-high
tracking only, wider 10/15/20/25% dip tiers, funded only from flexible top-up
capacity, never the fixed SIP list) and documented in `MY-MF-PLAN.md`. Its
AMFI scheme code/ISIN still needs confirming on the next review run, and fund
selection vs Nippon India/HDFC/Quant Small Cap was based on aggregator data,
not yet cross-checked against the AMC's own factsheet.

The user's habit of splitting redemption proceeds equally across the four SIP
funds was reviewed and changed: proceeds should instead follow the same
dip-tier table as monthly top-ups (saved in `MY-MF-PLAN.md`), so money favors
whichever fund is actually dipped rather than whichever fund is one of the
four regardless of price. The user wants to be asked each time before this is
applied, not treated as standing authorization. The user then confirmed
(20 September 2026) they have already used this financial year's ₹1.25 lakh
LTCG exemption moving some Regular-plan money, so the next Regular-plan
redemption tranche won't happen until April 2027 (new FY, exemption resets) —
do not prompt about further Regular-plan redemptions before then. The user indicated the exact amount/date isn't important to log; noting only
that a major share of this FY's move was out of Canara Robeco ELSS Tax Saver
Fund (Regular, External) — one of the holdings in
`portfolio_dashboard_snapshot_2026_09_20`. ELSS carries a 3-year lock-in from
each investment date, presumably already checked by the user alongside the
LTCG timing above.

## Capital gains statement (FY 2026-27) reviewed — 20 September 2026

The user shared Groww's official Capital Gains Statement PDF for FY 2026-27
(1 April 2026 - 31 March 2027, generated as of ~8 September 2026). Confirmed
figures, superseding the qualitative "used up the exemption" statement above
with exact numbers:

- **Long-term capital gains realized so far this FY: ₹1,23,488.65** — only
  ₹1,511.35 of the ₹1.25 lakh Section 112A exemption remains unused. Do not
  suggest any further LTCG-realizing redemption before April 2027 (new FY);
  there is essentially no headroom left.
- **Short-term capital gains realized: ₹2,311.94** — fully taxable regardless
  of the LTCG exemption (STCG gets no exemption allowance).
- **Small realized loss in the "Debt (Unspecified)" category: -₹401.33**
  (from ICICI Prudential US Bluechip Equity Direct Plan Growth, an
  international fund-of-funds taxed under debt rules).

**Scope correction**: this FY's consolidation was much larger than just
Canara Robeco ELSS. Funds already fully exited (Regular plans unless noted,
all redeemed between 10 April and 8 September 2026, so they no longer appear
in `portfolio_dashboard_snapshot_2026_09_20`): ICICI Prudential Large & Mid
Cap Fund, ICICI Prudential Large Cap Fund, ICICI Prudential Active Momentum
Fund, ICICI Prudential Quality Fund, ICICI Prudential Manufacturing Fund,
ICICI Prudential Multi Asset Allocation Fund (both Regular and a small
Direct-plan lot), ICICI Prudential Balanced Advantage Fund, Motilal Oswal
Large and Midcap Fund (Regular — a separate holding from the Direct-plan SIP
position still held), Kotak Mid Cap Fund (multiple folios), Nippon India
Multi Cap Fund, and a small Regular-plan HDFC NIFTY 50 Index Fund lot (also
separate from the tracked Direct-plan SIP). Canara Robeco ELSS is the only
one of this group still partially remaining, matching the April 2027 forward
plan above.

The full transaction-level detail (280+ matched purchase/redemption lines) is
not transcribed here — the user's Groww-exported PDF is the primary record.
This summary is for continuity only; if exact per-transaction figures are
needed later, ask the user to re-share the statement.

## Folio-level holdings detail confirmed — 20 September 2026

The user also shared Groww's official Holdings PDF (as on 2026-09-20), which
reconciles exactly with `portfolio_dashboard_snapshot_2026_09_20` in
`data/mf-watchlist.json` but breaks each fund down by folio. Several Direct
SIP funds (HDFC Nifty 50, HDFC Mid Cap, Parag Parikh, ICICI Flexicap) are
each split across 2-3 separate folios rather than one — this doesn't change
any totals already recorded. The operationally relevant finding, saved in
`data/mf-watchlist.json` -> `regular_external_folio_detail_2026_09_20`: folio
18034601 is a single shared ICICI Prudential AMC folio holding three
different things at once (Regular ICICI Flexicap, a Direct ICICI Flexicap
lot, and one of the two ICICI Retirement Fund lots) — redemption in April
2027 must target the specific scheme within that folio, not the folio as a
whole. Also, ICICI Prudential Retirement Fund Pure Equity is itself split
across two folios (30486629 and 18034601), both needing redemption to fully
exit that fund.

## Order history (Apr-Sep 2026) reviewed — 20 September 2026

The user shared Groww's Order History PDF for 1 April - 20 September 2026
(70+ transactions). Not transcribed line-by-line — the PDF is the source of
truth — but approximate rounded totals for context:

- **Purchases via Groww this FY so far**: HDFC Nifty 50 ~₹10.90L, HDFC Mid
  Cap ~₹10.10L, Parag Parikh ~₹5.92L, ICICI Flexicap (Direct) ~₹3.13L, SBI
  Gold ~₹0.65L — total ~₹30.7L.
- **Redemptions via Groww this FY so far**: ~₹13.5L, matching most of the
  capital-gains-statement redemptions (Canara Robeco ₹3.4L across three
  dates, plus Kotak Mid Cap, ICICI Multi Asset Allocation, Manufacturing,
  Active Momentum, Quality Fund, Large & Mid Cap, and Motilal Oswal Regular).
- **Not found in this Groww order history** despite appearing in the capital
  gains statement: ICICI Prudential Balanced Advantage, HDFC NIFTY 50
  (Regular), and Nippon India Multi Cap redemptions. Likely executed via a
  different platform rather than through Groww's order flow — not confirmed
  with the user yet.
- **Real redeployment pattern was not an equal split** across the four core
  SIP funds, despite the user's own recollection of dividing proceeds
  equally: Nifty 50 and Mid Cap together received roughly 68% of total
  purchases this FY, with Parag Parikh and ICICI Flexicap receiving the
  remainder — actual money flow already skewed toward the core/cheaper
  holdings before the dip-tier rule was formally agreed today, consistent
  with (not contradicting) that rule.

## Additional strategies saved — 20 September 2026

At the user's request, four additional investment strategies were documented
in `MY-MF-PLAN.md` with trigger conditions, each to surface at the right time
rather than needing to be remembered cold: (1) target allocation + annual
rebalancing (highest priority — `target_allocation` in
`data/mf-watchlist.json` is still unset), (2) value averaging as a future
evolution of the dip-tier rule, (3) annual tax-loss/gain harvesting on
Direct-plan holdings using the ₹1.25L exemption every year (not just for the
Regular-plan exit), starting FY2027-28 and reviewed alongside the scheduled
Feb 2027 LTCG-limit check, (4) STP for large lump sums (April 2027 proceeds
or a gifted lump sum). Momentum/trend-timing was explicitly flagged as not
recommended, per the paper-trading lab's own earlier finding that a
200-session trend rule showed no consistent advantage over fixed monthly
investing. Noted honestly that proactive reminding is limited to what
surfaces in a future session or a scheduled cloud routine (no standing
access to the user's live portfolio data outside a session).

On 19 September 2026, the skill (`daily-mf-topup-review/SKILL.md`) was extended
with a concrete, per-fund notability rule for these short-term moves instead of a
flat percentage: score the latest 1-session/5-session move against that fund's
own trailing ~60-session daily volatility, flag when |score| >= 1.5, and state a
"short-term dip watch" line at the top of every report even when nothing is
flagged. `MY-MF-PLAN.md` was updated to match. Today's report
(`reports/mf-review-2026-09-19.md`) was also updated with a worked example: a
computed 1-session/5-session table for all four funds plus Nifty 50, and a news
check on the broader January-to-date decline, which attributed it to oil
prices/FII outflows/bond yields rather than a single war shock (secondary
sources; not independently verified). No new top-up signal resulted from that
check.
