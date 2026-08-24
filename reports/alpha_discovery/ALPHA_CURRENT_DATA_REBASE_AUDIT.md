# ALPHA_CURRENT_DATA_REBASE_AUDIT — CURRENT_DATA_REBASE_AUTHORIZED

Mandate `ALPHA-XAUUSD-CURRENT-REGIME-SPECIALIST-DISCOVERY-001` + addendum `CURRENT_DATA_REBASE_AUTHORIZED`. Records exactly what data is now exposed for CURRENT-REGIME research (§7). No ambiguity about what Alpha has seen.

## Newly authorized data source (canonical, ratified)
- File: `C:\Users\MEDION GAMING\ai_quant_lab-wp5b\data\market\OANDA_XAUUSD_M15.csv` (the canonical ratified M15, the same series RANGE vNext was ratified on).
- Coverage: **2011-07-26 16:30 UTC → 2026-07-27 16:15 UTC**, **355,696 M15 bars**, latest close $4085.2. Also available at this source: M5, H1, H4 (and `_from_M15_v2` derivatives).
- Latest fully closed observation used: 2026-07-27 16:15 UTC (time=1785168900+). Only mechanically closed bars used; no forming/live bars.

## Former sealed / firewall cutoffs (now superseded for current-regime research)
- Prior Alpha `swing_base` firewall: gated M5 → M15/H1/H4, **DEV 2021-07-27→2023-12-29, CALIB 2024-01→2024-06-20, NO 2025+** (leak-asserted `dt < 2025-01-01`). Historical hist_data/hist_m15_data: b0 2011-2013 + b1 2016-2018.
- Prior EDGE_RESEARCH_PROTOCOL: Set A `dt < 2025-10-23`, Set B sealed after.
- RANGE vNext / S5 clean validation sealed holdout: `2025-10-23+` (final-holdout).

## Exposed range (loses untouched/OOS status — §2)
- **Everything after 2024-06-20 through 2026-07-27 is now RESEARCH-EXPOSED for current-regime work**: the old CALIB tail (2024-06→2024-12), and the previously-SEALED **2025-01 → 2026-07** (incl the EDGE_RESEARCH Set B and any 2025-10-23+ holdout that overlapped).
- These observations **permanently lose untouched-validation status** and must NEVER later be represented as independent OOS. Recorded here.
- **NOT affected**: S5's EXISTING independent validation (done historically on its clean population through 2025-10-12; §13 S5 untouched — not re-validated here). Its historical PASS stands under the protocol that produced it; I simply will not use post-exposure data as fresh S5 OOS.

## Data identity / hash
- (M15 CSV sha256 recorded at signature-freeze time in `sig_build.py` output / signature doc.)

## New research partition (current-regime; §3/§11 addendum)
To preserve validation integrity after exposure, current-regime work partitions the CURRENT_LIKE population (defined in ALPHA_CURRENT_MARKET_SIGNATURE_V1) by TIME:
- OLDER current-like episodes → DISCOVERY
- MID current-like → CONFIRMATION
- LATEST current-like (most recent contiguous slice) → RECENT OOS (best available, now that it is exposed it is "recent-but-once-touched"; forward MT5 DEMO becomes the true untouched confirmation per addendum §3).
- If recent current-like N is insufficient for a meaningful OOS slice, that is stated explicitly and reliance shifts to DISC/CONF + strict robustness + forward DEMO.

## Governance status
`CURRENT_DATA_REBASE_DONE` — data exposed + audited. Old cross-era verdicts (R1-R32, A-R) remain historically valid; not rewritten. Next: freeze CURRENT_XAUUSD_MARKET_SIGNATURE_V1 (no P&L) → CURRENT_LIKE_POPULATION_V1 → re-screen.
