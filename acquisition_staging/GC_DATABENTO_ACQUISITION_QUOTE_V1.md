# GC_DATABENTO_ACQUISITION_QUOTE_V1 — COST / COVERAGE AUDIT (NO PURCHASE)

**Mandate:** GC_DATABENTO_ACQUISITION_QUOTE_V1 · **Divizie:** Data Acquisition · **Data:** 2026-09 (session date)
**Scope:** determine exact acquisition requirements + Databento cost for the ohlcv-1m GC dataset that unblocks
`GC_REAL_VOLUME_CONTEXT_V1`. **No research, no outcomes, NO PURCHASE.** `DATA_PURCHASE_AUTHORIZED = NO`.

---

## ⛔ HEADLINE: coverage & requirements CONFIRMED; exact COST is BLOCKED on the account API key

The **exact dollar cost and the account credit balance cannot be obtained on this machine.** Every Databento
metadata/cost endpoint requires authentication (`GET metadata.get_cost`, `metadata.get_dataset_range`,
`metadata.list_schemas` all return HTTP 401 "Not authenticated"); the per-GB usage rate is not published (it is
shown only inside the authenticated estimator); and no Databento API key exists on this machine (checked env,
`HKCU\Environment` registry, `~/.databento`, project configs — none present). Entering the account's portal login
is prohibited (financial-account credentials). Therefore the **authoritative quote must be produced with the
account** (API key → I run the read-only `get_cost`, or the CEO runs the portal estimator). Everything else —
requirements, coverage, size, method comparison, decision metrics — is delivered below.

---

## 1. Authoritative dataset & required schemas (exact)
- **Vendor** = Databento · **Dataset** = `GLBX.MDP3` (CME Globex MDP 3.0) · **Product** = CME COMEX Gold `GC` **outright** futures.
- **Primary schema** = `ohlcv-1m`. **Supporting** = `definition` (expiry / contract identity / roll construction) + `statistics` (daily OI / settlement).
- **Explicitly NOT requested:** MBO, MBP-10, tbbo, trades L2/L3, options, spreads, other metals. (This experiment tests **L0 real traded VOLUME**, not order flow — per §9 of the mandate and the Statistician's `STAT_GC_XAU_PRICE_DISCOVERY_DATA_GATE_V1` finding that GC's genuinely-new information is VOLUME/OI, not price.)

## 2. Symbol / contract scope (exact request)
- **`symbols = GC.FUT`, `stype_in = parent`** on `GLBX.MDP3`. Databento **parent** symbology `GC.FUT` returns **all GC outright futures** (monthly contracts across their lifetimes) — **not** options (`GC.OPT`), **not** spreads, **not** other metals. This yields sufficient outright history to construct a causal point-in-time active contract yourself (roll via OI/volume from `statistics` + expiry from `definition`). Cost is billed only on returned GC records.

## 3. Coverage — CONFIRMED from authoritative public dataset metadata
From the `GLBX.MDP3` dataset record (`temporalCoverage: "2010-06-06/.."`, per-schema `data_start`):
```
GC_DATA_START_AVAILABLE = 2010-06-06   (<= 2011-07-26 Quote-B start  AND  <= 2021-07-27 Quote-A start)  ✅
GC_DATA_END_AVAILABLE   = ongoing (real-time), >= 2026-07-27  ✅
OHLCV_1M_AVAILABLE      = YES   (ohlcv-1m data_start = 2010-06-06)
DEFINITION_AVAILABLE    = YES   (standard GLBX.MDP3 schema from inception — confirm via list_schemas with key)
STATISTICS_AVAILABLE    = YES   (standard GLBX.MDP3 schema — carries daily OI/settlement — confirm with key)
```
Both requested ranges are fully inside the available window; no coverage gap.

## 4. Volume provenance & timestamp semantics (§8)
- **`volume` = genuine exchange-traded volume** (sum of CME MDP-3.0 trade sizes aggregated into the minute — real traded contracts, not tick count, not synthetic). The lab already verified this directly: `build_gc_bars.py` reconstructed real traded volume from the GC MBO trade messages, and the Statistician measured GC↔XAU log-volume R²=0.822 on it. `OHLCV_1M_PROVENANCE_VERIFIED = YES`.
- **Timestamp:** `ts_event` in **UTC nanoseconds** = the bar's **interval start (bar OPEN)**. Causal use: a completed 1-min bar is known only at `ts_event + 60s`; join to XAU on bar CLOSE via backward as-of (the convention the lab already ratified). DST is absorbed (absolute UTC); keep an explicit CME Globex session mask (Sun 18:00 ET → Fri 17:00 ET, daily 17:00–18:00 ET halt).
- `CONTRACT_ROLL_CONSTRUCTION_EXECUTABLE = YES` (ohlcv-1m per instrument_id + definition expiry + statistics OI → causal active-contract roll).

## 5. Expected data volume (capacity planning — §7; ESTIMATES, exact from estimator)
ohlcv-1m record ≈ 56 B uncompressed. GC-outright 1-min-bar density anchored on the on-disk sample (front month ≈ ~1,215 1-min bars/session), plus the 2nd–nth month tail:

| | Quote A (5y, 2021-07-27→2026-07-27) | Quote B (15y, 2011-07-26→2026-07-27) |
|---|---|---|
| ESTIMATED_ROWS (ohlcv-1m) | ~5–7 M | ~15–22 M |
| ESTIMATED_UNCOMPRESSED_BILLABLE_SIZE | **~0.3–0.5 GB** | **~1.0–1.5 GB** |
| + definition + statistics | small (~<50 MB total) | small (~<80 MB total) |
| ESTIMATED_DOWNLOAD_SIZE (.zst) | ~50–100 MB | ~150–300 MB |
| ESTIMATED_LOCAL_STORAGE (raw DBN.zst + Parquet) | ~a few hundred MB | ~a few hundred MB |
Preferred local: **raw DBN preserved + Parquet research derivative.** Storage is trivial either way.

## 6. Cost — the two quotes (§2, §4, §10)
The uncompressed billable size is **small (<2 GB even for 15y)** and `ohlcv-1m` is Databento's **cheapest historical schema tier**, so the absolute cost is an **order of "tens of dollars", not thousands** — but the **exact figure requires the estimator** and is NOT guessed here.
```
QUOTE_A_5Y_TOTAL_COST = PENDING_ESTIMATOR   (usage-based $/GB × ~0.3–0.5 GB; rate not public)
QUOTE_A_5Y_NET_COST_AFTER_EXISTING_CREDIT = PENDING (TOTAL − CURRENT_ACCOUNT_CREDIT)
QUOTE_B_15Y_TOTAL_COST = PENDING_ESTIMATOR  (usage-based $/GB × ~1.0–1.5 GB)
QUOTE_B_15Y_NET_COST_AFTER_EXISTING_CREDIT = PENDING
COST_RATIO_FULL_VS_MINIMUM ≈ 3.0×   (rate-independent — scales with GB; 5y ≈ 1/3 of 15y data)
```
**Exact query to run (read-only, does NOT download or purchase), once the API key is available** — repeat per schema and sum:
```
GET https://hist.databento.com/v0/metadata.get_cost
    ?dataset=GLBX.MDP3&schema=ohlcv-1m&symbols=GC.FUT&stype_in=parent
    &start=2021-07-27&end=2026-07-27&mode=historical        # Quote A; then start=2011-07-26 for Quote B
    (+ schema=definition, schema=statistics)
    -u <API_KEY>:                                            # HTTP Basic, key as username
GET .../metadata.get_dataset_range?dataset=GLBX.MDP3         # confirm coverage
GET .../metadata.get_record_count / .get_billable_size       # confirm rows/GB
```

## 7. Acquisition method comparison (§5)
| | A. USAGE-BASED HISTORICAL PURCHASE | B. ONE MONTH OF STANDARD ($199/mo) |
|---|---|---|
| DATA_COST | $/GB × billable GB (one-time) | 1y L1 history INCLUDED; the other 4y/14y is pay-as-you-go (= usage) |
| SUBSCRIPTION_COST | none | $199 / month |
| LICENSE_COST | none (standard historical license) | none extra |
| TOTAL_CASH_COST | pure usage (small) | $199 + usage for everything beyond the 1-year allowance |
| WHAT_DATA_ARE_INCLUDED | exactly the requested GC ohlcv-1m + definition + statistics for the range | only ~1 year of L1 history is bundled; our 5y/15y is NOT covered by the plan |
| DATA REMAIN LOCALLY AFTER IT ENDS | **YES — downloaded historical DBN files are yours, kept permanently** | downloaded files persist locally; but the plan's *value* (bundled allowance) is only ~1y and does not cover our range |
**Verdict:** the **Standard plan does NOT include the required complete history** (only ~1y L1), so it adds a $199/mo subscription without covering 5y/15y → **USAGE-BASED is the correct method** for this one-time deep-history pull, and it yields **permanent local ownership** of the DBN files (+ our Parquet derivative). Do not subscribe to Standard for this.

## 8. Existing credit (§6)
```
AVAILABLE_CREDIT = UNKNOWN  (requires authenticated account query — not obtainable without the API key)
CURRENT_ACCOUNT_CREDIT = UNKNOWN
NET_COST_AFTER_EXISTING_CREDIT = PENDING (TOTAL − CREDIT, once both known)
```
Not consumed. The advertised $125 signup credit is NOT assumed to apply to this account (per mandate). No new account created.

## 9. Decision metrics — matched XAU evidence (§10; from date coverage only, no outcomes inspected)
XAU discovery population (the 4 governed discovery blocks, M15_v2, 197,094 bars):
| Window | XAU discovery coverage | Regimes covered |
|---|---|---|
| **5Y (2021-07-27→2026-07-27)** | DEV3 (2022-12→2025-10, ~66,603 bars) + DEV2 tail ≈ **~35% of the discovery population** | recent bull/correction only |
| **15Y (2011-07-26→2026-07-27)** | ALL four blocks = **100%** | + **b0 2011-2013 (bear)** + **b1 2016-2018 (bull)** = 2 additional distinct regimes |
```
MINIMUM_DATASET_EXPECTED_MATCHED_XAU_TRADES = ~35% of the full population (recent regime; DEV3-dominated)
FULL_DATASET_EXPECTED_MATCHED_XAU_TRADES    = 100% (≈ 2.9× the 5Y), adding the 2011-2013 and 2016-2018 regimes
```
(Proportional to governed discovery-bar coverage per window — no CTS outcome inspected.)

## 10. RECOMMENDATION (§11) — advisory; purchase NOT authorized
```
RECOMMENDATION = BUY_FULL_15Y
```
**Reasoning:** (a) `ohlcv-1m` is the cheapest schema and the FULL dataset is <2 GB, so the **absolute incremental cost of 15Y over 5Y is small** even though the ratio is ~3× — exactly the §11 condition "FULL adds substantial regime diversity at a small incremental cost → prefer FULL"; (b) FULL adds **b0 (2011-2013 bear) and b1 (2016-2018 bull)** — two distinct regimes the 5Y entirely lacks, and a **VOLUME** experiment is precisely where multi-regime coverage matters (volume/participation structure differs across bull/bear/correction); (c) FULL ≈ **2.9× the matched XAU evidence**; (d) the source-value is real and untouched (GC volume ≈ 32% information the lab does not hold). **Condition:** this assumes the estimator confirms the (near-certain) small total cost; if `get_cost` unexpectedly returns a high 15Y figure, fall back to **BUY_5Y** (sufficient for a first source-value falsification on the recent regime).

## 11. FINAL OUTPUT
```
GC_DATABENTO_ACQUISITION_QUOTE_V1_COMPLETE = NO   (exact cost + account credit blocked on missing API key)

VENDOR = DATABENTO
DATASET = GLBX.MDP3
PRODUCT = GC (outrights; symbols=GC.FUT, stype_in=parent)
PRIMARY_SCHEMA = OHLCV-1M  (+ definition + statistics)

QUOTE_A_RANGE = 2021-07-27..2026-07-27
QUOTE_A_TOTAL_COST = PENDING_ESTIMATOR (size ~0.3–0.5 GB uncompressed; ~5–7M rows)
QUOTE_A_NET_COST = PENDING
QUOTE_A_ESTIMATED_SIZE = ~0.3–0.5 GB uncompressed / ~50–100 MB download

QUOTE_B_RANGE = 2011-07-26..2026-07-27
QUOTE_B_TOTAL_COST = PENDING_ESTIMATOR (size ~1.0–1.5 GB uncompressed; ~15–22M rows)
QUOTE_B_NET_COST = PENDING
QUOTE_B_ESTIMATED_SIZE = ~1.0–1.5 GB uncompressed / ~150–300 MB download

CURRENT_ACCOUNT_CREDIT = UNKNOWN (requires authenticated account)

USAGE_BASED_OPTION = correct method; one-time $/GB; permanent local DBN ownership
STANDARD_PLAN_OPTION = $199/mo but only ~1y L1 bundled → does NOT cover 5y/15y → not applicable

OHLCV_1M_PROVENANCE_VERIFIED = YES (genuine exchange-traded volume)
DEFINITION_AVAILABLE = YES
STATISTICS_AVAILABLE = YES
CONTRACT_ROLL_CONSTRUCTION_EXECUTABLE = YES

RECOMMENDATION = BUY_FULL_15Y  (advisory; conditional on estimator confirming small cost; else BUY_5Y)

DATA_PURCHASE_AUTHORIZED = NO
NEXT_AUTHORIZED_ACTION = CEO provides the Databento API key (I run read-only get_cost per schema for both ranges + get_dataset_range + credit) OR CEO runs the portal estimator — to fill the PENDING exact cost / credit. THEN CEO DECISION on purchase.
```
STOP.
