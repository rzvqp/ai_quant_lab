# GC_FULL15Y_ACQUISITION_REPORT

**Mandate:** ACQUIRE GC FULL 15Y DATASET (Databento GLBX.MDP3, cap USD 25.00) · **Divizie:** Data Acquisition · **Data:** 2026-09

> # ⛔ STOPPED — `DATABENTO_API_KEY` NOT LOCALLY CONFIGURED (mandate §2)
> Nothing was purchased, requested, or downloaded. No credential was exposed (none exists to expose). The
> acquisition is fully prepared and one command from completion the moment the key is present.

## Why stopped (mandate §2: "If the key is not available: STOP")
`DATABENTO_API_KEY` is **not available anywhere on this machine** — verified (existence only, values never read/printed):
- shell/process env: UNSET · Windows **User** scope: unset · **Machine** scope: unset · registry `HKCU\Environment`: absent (only Path/TEMP/TMP/OneDrive/TELEGRAM_*).
- No `~/.databento`, no `%APPDATA%\databento`, no `.config/databento`, no `.env` / databento config in any repo, no file containing `DATABENTO_API_KEY` or a `db-…` key.
- `databento` python **0.86.0 IS installed** — but without the key it cannot authenticate.

The CEO's quotes were "obtained directly from the Databento account" (likely the web portal); the API key itself is not configured on this machine, so I cannot run the mandatory read-only `get_cost` recheck (§3) nor download. Per §2 this is a hard STOP.

## What is ready (executes in one step once the key is configured)
`acquisition_staging/gc_databento_full15y/acquire_gc_full15y.py` — reads `DATABENTO_API_KEY` from the environment only (never printed/logged/committed), and:
1. **READ-ONLY `metadata.get_cost`** for all three schemas (§3);
2. sums to `FINAL_TOTAL_COST`; **if > 25.00 USD → STOP, no paid request** (`PURCHASE_BLOCKED_COST_CAP=YES`) — the cap is enforced mechanically;
3. if ≤ 25.00 → downloads the three raw DBN streams to `raw/`, preserves them exactly;
4. checksums → `GC_FULL15Y_RAW_MANIFEST.json` (vendor/dataset/schema/symbol/stype/start/end/download-ts/lib-version; **no credentials**).

Verified: the script STOPs cleanly on the missing key (exit 2, "No request made") — no network call, no exposure.

**Exact requests (NOT broadened — §1/§4/§5/§6):**
| request | dataset | schema | symbols | stype_in | range (end EXCLUSIVE) |
|---|---|---|---|---|---|
| OHLCV | GLBX.MDP3 | `ohlcv-1m` | `GC.v.0` | `continuous` | 2011-07-26 → 2026-07-28 |
| definition | GLBX.MDP3 | `definition` | `GC.FUT` | `parent` | 2011-07-26 → 2026-07-28 |
| statistics | GLBX.MDP3 | `statistics` | `GC.FUT` | `parent` | 2011-07-26 → 2026-07-28 |
(`2026-07-28` exclusive includes all of 2026-07-27. `GC.v.0` continuous convention is fixed and will NOT be changed after seeing data, per §4/§7. Continuous-contract causality audit — §11 — will run against Databento's authoritative `GC.v.0` metadata BEFORE any derived build; if it implies a forward-looking roll, the issue is returned to the CEO and no Alpha research starts.)

## REQUIRED FINAL OUTPUT (§16)
```
GC_FULL15Y_ACQUISITION_COMPLETE = NO   (blocked: DATABENTO_API_KEY not locally configured)

PURCHASE_AUTHORIZED_BY_CEO = YES
MAX_AUTHORIZED_COST_USD = 25.00

FINAL_OHLCV_COST = NOT_QUERIED (no API key; CEO's read-only quote was 18.841074481606 USD)
FINAL_DEFINITION_COST = NOT_QUERIED (CEO quote 2.361728437245 USD)
FINAL_STATISTICS_COST = NOT_QUERIED (CEO quote 0.915424749255 USD)
FINAL_TOTAL_COST = NOT_QUERIED (CEO expected ~22.12 USD, under the 25.00 cap)
COST_CAP_RESPECTED = YES (nothing purchased; cap enforced by the script before any paid request)

DATABENTO_DATASET = GLBX.MDP3
GC_OHLCV_SCHEMA = ohlcv-1m
GC_OHLCV_SYMBOL = GC.v.0 (stype_in=continuous)
GC_HISTORY_START = NOT_ACQUIRED (target 2011-07-26; coverage confirmed available from 2010-06-06)
GC_HISTORY_END = NOT_ACQUIRED (target 2026-07-27; coverage ongoing)

OHLCV_ROWS = NOT_ACQUIRED
DEFINITION_ROWS = NOT_ACQUIRED
STATISTICS_ROWS = NOT_ACQUIRED

RAW_FILES_SHA256_VERIFIED = NO (nothing downloaded)
DATA_QUALITY_GATE = NOT_RUN

REAL_TRADED_VOLUME_PRESENT = NOT_VERIFIED (ohlcv-1m volume is genuine exchange-traded per prior lab verification; to confirm on the acquired file)
TIMESTAMP_SEMANTICS_VERIFIED = NOT_RUN (ts_event UTC-ns bar-open, per Databento docs; to confirm on the file)
CONTINUOUS_CONTRACT_CAUSALITY = NOT_RUN (GC.v.0 roll audit pending the data + Databento metadata)

GC_1M_RESEARCH_READY = NO
GC_15M_RESEARCH_READY = NO

READY_FOR_ALPHA_GC_REAL_VOLUME_CONTEXT_V1 = NO

NEXT_AUTHORIZED_ACTION = CEO configures DATABENTO_API_KEY locally (e.g. set the User env var
  DATABENTO_API_KEY, or place it in the databento config) — then re-run
  `python acquisition_staging/gc_databento_full15y/acquire_gc_full15y.py`
  which rechecks cost read-only, enforces the 25.00 cap, downloads, checksums, and manifests.
  I will then run the completeness / causality / derived-build audits (§10–§12, §15).
```
STOP.

## Safety confirmation
No API key was printed, logged, written, committed, sent to Telegram, or stored in memory (there was none to handle). No paid request was made. The request was NOT broadened beyond the authorized dataset/schemas.
