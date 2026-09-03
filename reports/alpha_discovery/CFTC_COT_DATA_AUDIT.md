# CFTC COT — data audit (§2/§4/§5)

Public CFTC Commitments of Traders data, no purchase. Open-access historical files from cftc.gov.

## §2 acquisition + identity
```
COT_MARKET = COMEX GOLD ("GOLD - COMMODITY EXCHANGE INC.")
COT_MARKET_CODE = 088691 (CFTC_Contract_Market_Code) · CFTC_Market_Code = CMX
COT_REPORT_TYPE = Disaggregated Futures-Only (fut_disagg_txt_YYYY.zip, 2011-2026)
COT_HISTORY_START = 2011-01-04 · COT_HISTORY_END = 2026-08-25 · COT_REPORTS_TOTAL = 817 weekly reports (~15.6 yr)
Participant categories = Producer/Merchant, Swap Dealer, Managed Money, Other Reportables, Nonreportable (exact CFTC terms)
COT_DATA_GATE = PASS
```

## §4 point-in-time causality (absolute) — and a caught bug
Each weekly report references a **Tuesday** and is publicly released the following **Friday ~3:30 pm ET**. Frozen availability =
`reference_Tuesday + 3 days + 20:00 UTC`. For an XAU decision at T, the COT used is the most recent report with release-time ≤ T (searchsorted).
No daily interpolation — the latest released report is carried as the current state, and `COT_DATA_AGE_DAYS` is recorded (median 4.5 days;
groups 0-1d/2-3d/4-6d/7+d = 446/9,101/30,300/9,793 trades). **`FUTURE_COT_OBSERVATIONS_USED = 0`.**

★ A scaling bug in the first build (parquet stored datetimes as microseconds; the unix conversion assumed nanoseconds) had mapped every trade
to the last 2026 report — the causal-age audit (median 18,139 "days") surfaced it. It was fixed before any result was accepted; the reported
result uses the corrected point-in-time join (median age 4.5 days). `COT_CAUSALITY_GATE = PASS`.

## §5 revision policy (disclosed limitation)
The open historical CFTC files hold the current (possibly minor-revised) values, not a strict original-release archive; free point-in-time
original-release snapshots are unavailable. COT revisions are typically small and infrequent, so each report's value is assigned to its Friday
release time as the best defensible point-in-time reconstruction. This approximation is disclosed (§5) and is not material enough to invalidate
causal reconstruction (`COT_CAUSALITY_GATE = PASS`).

## Matched universe
Joined to the 3 frozen CTS setups (reusing GC price+volume+OI features): SETUP_1 13,418 · SETUP_2 11,605 · SETUP_3 24,617 = **49,640 trades**.
