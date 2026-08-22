# DATA_ACQ_DXY_H1_PROVISIONING_REPORT

**Mandate:** DATA-ACQ-DXY-H1-HISTORICAL-RATIFIED-001 · **Divizie:** Data Acquisition · **Data:** 2026-08-13

> ## ✅ VERDICT: RESEARCH-READY
> `DXY_H1_HISTORICAL_DATA_ACQUIRED` · `DXY_TIMESTAMP_CONTRACT_VERIFIED` · `DXY_RESEARCH_SLICES_GOVERNED` · `DXY_H1_RESEARCH_DATA_RATIFIED` · `READY_FOR_ALPHA_DXY_RESEARCH_HANDOFF`
> Exact ICE DXY (cash index), H1, causal timestamps, quality-verified, 2024+ firewalled. DATA ONLY — no Alpha testing, no strategy touched, no main manifest modified.

## 1. Source
Official **ICE U.S. Dollar Index** — provider ICE (Intercontinental Exchange US), provider symbol `ICEUS:DXY` → `ICEUS_DLY:DXY` (delayed feed). **Cash/index** series (type=index; volume=0 → confirms cash index, NOT `DX` futures). Access route: TradingView Desktop (delayed ICE index) via CDP replay-walk (`pull_dxy_h1.mjs`, overlapping-window backward walk, provisional-cursor-bar fix, adaptive stall recovery). No vendor mixing; no proxy.

## 2. Exact acquired coverage (RAW)
**76,007 H1 bars, 2011-07-14T23:00:00Z → 2024-01-05T00:00:00Z.** Continuity 69.5% (654 weekend gaps + 50 US-holiday gaps + the ICE session calendar — NOT data holes; accounting invariant holds). Deepest bar 2011-07-14 is **below** b0 start (2011-07-26) → b0 fully covered with margin. Source floor ≈ 2011-07-14 (ICE DXY H1 on TradingView begins there).

## 3. Exact DEV/research block coverage (governed slices)
| Slice | Canonical UTC bounds | Bars | First → Last |
|---|---|---|---|
| **DXY_B0_RESEARCH_SLICE** (b0) | 2011-07-26T16:30 → 2013-09-27T16:45 | **13,267** | 2011-07-26T17:00 → 2013-09-27T16:00 |
| **DXY_B1_RESEARCH_SLICE** (b1) | 2016-01-11T09:00 → 2018-04-06T11:52 | **13,583** | 2016-01-11T09:00 → 2018-04-06T11:00 |
| **DXY_2021_2023_RESEARCH_SLICE** | 2021-07-27T00:00 → 2023-12-30T00:00 | **14,846** | 2021-07-27T00:00 → 2023-12-29T21:00 |
b0/b1 bounds = `context_derived_htf.m15_v2_discovery_blocks[0]/[1]`; 2021-2023 = Native Alpha DEV window.

## 4. Calibration coverage
No structured CALIBRATION data-partition is defined in the repository manifest (v2.7.73) — only statistical-recalibration prose. No CALIBRATION slice was bound. The continuous DXY series covers 2011-07-14 → 2023-12-29 so any future-defined CALIBRATION block within that span (and ≥ the b0 floor) is already physically available for slicing on request.

## 5. Raw hashes
- `RAW_DXY_H1_ICEUS.csv` sha256 **`7e112b9d8b3cd667117f59a76211a187bf3ae55fa74a69620c56a41ad768a6f0`** (76,007 bars, 2011-07-14→2024-01-05).

## 6. Normalized hashes
- `NORMALIZED_DXY_H1.csv` sha256 **`8b8cf4dd5a0c71d784712fe22887674f22a986bd31c6cb0fe22f45c1d064fc5f`** (75,934 bars, research region ≤2023-12-31, 2011-07-14→2023-12-29).
- `DXY_B0_RESEARCH_SLICE.csv` sha256 `86f1d337f22262eb0265e05959ce7f8689f0cf24df6673ddc6fef18f822f6cf9`.
- `DXY_B1_RESEARCH_SLICE.csv` sha256 `7e057857a8a4907110579ddc9bd040198681b6dbba9bb65779c6d61eccd15f67`.
- `DXY_2021_2023_RESEARCH_SLICE.csv` sha256 `3d445992d88c9ef287aef91d58f7a0e7232ce5e865655310b6a3b346be7c4b22`.
- Code fingerprints: `pull_dxy_h1.mjs` `4d828595991b9e76…`, `dxy_process.py` `5161c9606c537dbe…`.

## 7. Manifest identities
`RAW_DXY_SOURCE` = RAW_DXY_H1_ICEUS.csv; `NORMALIZED_DXY_H1` = NORMALIZED_DXY_H1.csv; slices `DXY_B0_RESEARCH_SLICE` / `DXY_B1_RESEARCH_SLICE` / `DXY_2021_2023_RESEARCH_SLICE`. Governance classification in `DXY_EVIDENCE_MANIFEST.json`. **The main `config/split_manifest.json` was NOT modified** (Statistician's; this is a separate DXY evidence manifest).

## 8. Data-quality results (RAW and NORMALIZED)
| Check | RAW | NORMALIZED |
|---|---|---|
| duplicate timestamps | 0 | 0 |
| strictly monotonic | True | True |
| off-grid (non-3600s) timestamps | 0 | 0 |
| OHLC constraint violations (high≥o/c/l, low≤o/c/h) | **0** | **0** |
| zero/negative-price bars | **0** | **0** |
| bar-accounting invariant (present+missing==grid) | OK | OK |
Timestamps understood (UTC epoch, bar-open); causal availability defined (see DXY_DATA_CONTRACT.md).

## 9. Gaps
654 weekend gaps (Fri→Sun, ~1/week over 12.5y) + 50 intra-week gaps = **US market holidays** (e.g. New Year 2013-12-31→2014-01-02 26h, Thanksgiving 2011-11-23→25 25h, July-4 2012 25h). All structural (index closed); none forward-filled or interpolated. Continuity 69.5% = weekends + holidays + hourly grid over a ~24×5 session.

## 10. Existing-M5 overlap
n/a for DXY (this mandate provisions DXY, not M5). The existing XAUUSD M5/H1 files were NOT modified.

## 11. M5→M15 consistency
n/a (DXY H1 mandate). Cross-market overlap vs XAUUSD is §15 below.

## 12. Partition / firewall proof
- 2024+ **PROTECTED:** RESEARCH_END = 2023-12-31. The RAW upper bound (2024-01-05) yielded a 73-bar 2024 head (2024-01-02→05) which is **EXCLUDED** from NORMALIZED and every slice, and classified PROTECTED in `DXY_EVIDENCE_MANIFEST.json`. No 2025/2026 data acquired.
- No unrestricted future rows handed to Alpha; slices are date-bounded and hashed.

## 13. Alpha access instructions
Consume the three governed slices (or NORMALIZED filtered to a slice's bounds). Perform the research join yourself under the causal contract: `DXY_FEATURE_AVAILABLE_AT (= time+3600) <= XAUUSD_DECISION_TIME` — see `DXY_DATA_CONTRACT.md`. Do NOT read a DXY bar whose close is at/after the decision instant. Do NOT use 2024+.

## 14. Known limitations
- Feed is **delayed** ICE DXY (fine for historical research; not real-time).
- Source floor 2011-07-14 (no earlier H1 from this source; b0 covered).
- `TVC:DXY` (TradingView's own aggregate) was rejected in favour of the exact ICE series; if the CEO ever wants the TVC series it is a separate decision.
- XAUUSD ratified research H1 (`H1_from_M15_v2`) covers only its discovery sub-ranges in 2021-2023, so matched evidence there is bounded by the XAUUSD side (6,772h), not DXY.

## 15. Cross-market overlap audit (DXY H1 vs XAUUSD H1 = `data/market/OANDA_XAUUSD_H1_from_M15_v2.csv`)
| Block | DXY start→end | XAUUSD H1 hours | DXY H1 hours | Overlapping hours | % of XAUUSD | Missing-overlap hours |
|---|---|---|---|---|---|---|
| b0 | 2011-07-26→2013-09-27 | 13,397 | 13,267 | **13,053** | **97.4%** | 344 |
| b1 | 2016-01-11→2018-04-06 | 13,213 | 13,583 | **12,918** | **97.8%** | 295 |
| 2021-2023 | 2021-07-27→2023-12-29 | 6,777 | 14,846 | **6,772** | **99.9%** | 5 |
Missing-overlap = XAUUSD hours with no same-hour DXY bar (session/holiday calendar differences); Alpha's backward-availability join handles them. Full detail: `DXY_COVERAGE_OVERLAP_REPORT.json`.

## 16. (Deliverables index — see §19 of the mandate)
This report; `DXY_DATA_CONTRACT.md`; `DXY_EVIDENCE_MANIFEST.json`; `DXY_COVERAGE_OVERLAP_REPORT.json`; `NORMALIZED_DXY_H1.csv` + 3 governed slices; `RAW_DXY_H1_ICEUS.csv`; acquisition/normalization code (`pull_dxy_h1.mjs`, `dxy_process.py`); `DXY_PROCESS_REPORT.json` (machine-readable fingerprints + QA). All under `acquisition_staging/dxy/`.

## 17. Exact readiness verdict
**RESEARCH-READY.** `DXY_H1_HISTORICAL_DATA_ACQUIRED` · `DXY_TIMESTAMP_CONTRACT_VERIFIED` · `DXY_RESEARCH_SLICES_GOVERNED` · `DXY_H1_RESEARCH_DATA_RATIFIED` · `READY_FOR_ALPHA_DXY_RESEARCH_HANDOFF`.
Constraints honored: exact DXY (no proxy), causal timestamps, no interpolated history, 2024+ protected, full provenance + fingerprints, DATA ONLY, no Alpha testing, no strategy changes, main manifest untouched.
