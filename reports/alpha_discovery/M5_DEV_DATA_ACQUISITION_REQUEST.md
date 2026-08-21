# DATA ACQUISITION REQUEST — Native M5 XAUUSD for DEV discovery blocks

**From:** Alpha Discovery (Flow B) · **To:** Data Acquisition division (`ai_quant_lab-data-acq`) · **Date:** 2026-08-21
**Authorization:** CEO `ALPHA ECONOMIC PROFILE DIRECTIVE` (2026-08-21) + CEO decision "A+C in parallel".
**Priority:** unblocks the M5 causal-trigger layer of the M15/H1/H4-edge economic-profile program.

## 1. Why
The economic-profile directive requires an **M5 causal-trigger / entry layer** beneath M15/H1/H4 edges. Native `data/market/OANDA_XAUUSD_M5.csv` covers **2021-07-27 → present only** → **zero** M5 bars in the DEVELOPMENT discovery blocks. M5 is finer than the M15 base and **cannot** be aggregated from it. Interim H4/H1 research proceeds with a next-bar-open entry proxy (`PENDING_M5`), but true M5 execution quality, tight-stop placement, and intrabar SL-vs-TP path resolution are blocked until this lands.

## 2. Exactly what is needed
| field | requirement |
|---|---|
| symbol / venue | XAUUSD, **OANDA** (match existing `OANDA_XAUUSD_*` provenance) |
| resolution | **M5** (5-minute) native bars — NOT resampled from any coarser series |
| **required windows** | **block0: 2011-07-26 → 2013-09-27** and **block1: 2016-01-11 → 2018-04-06** (the DEV discovery blocks). Extending to full 2011→2018 continuous is fine; DEV coverage is the hard requirement. |
| nice-to-have | full CALIBRATION block2 (2020-08-11 → 2021-09-05) — currently only a Jul–Sep 2021 sliver (7,787 bars) exists |
| schema | `time` (unix s, UTC), `open`, `high`, `low`, `close`, `volume` — identical to existing M5 file |
| **must NOT** | touch/ship the VALIDATION region (2022-12-16 → 2025-10-12) into any discovery-labeled file; that block stays SEALED (`VALIDATION_ACCESS=0`) |

## 3. Integrity / gating requirements (Alpha will not consume otherwise)
1. **Manifest-gated & provenance-stamped** to `config/split_manifest.json`, same block-existence discipline as the `_from_M15_v2` H1/H4/D1 series.
2. **No cross-gap bridging:** the 2013-09-27 → 2016-01-11 unratified gap must remain a gap (per-block files or an explicit gap marker), consistent with the same-discovery-block guard VE established in `ed57853`.
3. **Alignment check:** M5 must reconcile to the existing M15 base on the overlap (M5 OHLC aggregated ×3 should reproduce M15 within tolerance) — supply the reconciliation report.
4. **Supply-never-ratify:** deliver as candidate data; Alpha/Statistician gate it. Report row counts, date span, gap inventory, and OHLC sha256 per block.

## 4. Handshake
On delivery, notify Alpha Discovery with: file path(s), per-block row counts + date spans, sha256 per block, M15-reconciliation result, and confirmation the VALIDATION region is excluded. Alpha will then run the full M5-triggered economic-profile campaign (Profiles A/B) on the gated DEV population.

**Status:** `M5_DEV_ACQUISITION_REQUESTED` — Alpha proceeds with interim H4/H1 (option C) in parallel.
