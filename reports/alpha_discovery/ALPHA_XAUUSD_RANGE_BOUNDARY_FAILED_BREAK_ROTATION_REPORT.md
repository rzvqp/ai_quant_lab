# ALPHA_XAUUSD_RANGE_BOUNDARY_FAILED_BREAK_ROTATION_REPORT

**Mandate:** `ALPHA-XAUUSD-RANGE-BOUNDARY-FAILED-BREAK-ROTATION-001` · **Date:** 2026-08-22.
**Terminal statuses:** `RANGE_UPPER_ROTATION_DISCOVERY_COMPLETE` · **`NO_ROBUST_RANGE_UPPER_SHORT_SIGNAL_FOUND`** ; `RANGE_LOWER_ROTATION_DISCOVERY_COMPLETE` · **`NO_ROBUST_RANGE_LOWER_LONG_SIGNAL_FOUND`**.
**Reason (both):** the **parent population is EMPTY** — the FROZEN RANGE v4.4 detector confirms **ZERO macro ranges** on the Alpha authorized native-M5 evidence window (2021-07-27→2023-12-29). This is a frozen-detector property (§40), **reported, not fixed**.
**Scope:** RANGE v4.4 = CONTEXT ONLY (no MI retuning, §1/§40); price-only; native-M5; DEV-only; no CALIB/V1/2025+/N4/execution. Canonical boundary **recovered, not invented** (§4). No promotion; broker disabled.

---

## 0. Headline
- **The §4 boundary gate PASSES** — the canonical RANGE v4.4 boundary representation exists and was recovered by running the frozen engine unchanged (`RangeSemanticEngineV44`, config_id `23d98c07…`, contract `range-hierarchical-v4.4`, verified). It exposes `macro_boundary_upper` / `macro_boundary_lower` on CONFIRMED macro state. **No boundary was invented.**
- **But the parent is EMPTY:** run over full history through 2023-12-29, the frozen detector produced **0 CONFIRMED macro-range bars in the entire Alpha window (2021-2023).** Verified by year: **2021 = 15,934 CANDIDATE / 0 CONFIRMED · 2022 = 873 CANDIDATE / 0 CONFIRMED · 2023 = 23,563 CANDIDATE / 0 CONFIRMED.** After 2020 the macro state machine sits **permanently in CANDIDATE**, never reaching FORMING or CONFIRMED.
- **Consequence:** zero valid range boundaries on the native-M5 evidence → **zero boundary attacks** → both UPPER and LOWER families have **no parent episodes**. The rotation hypotheses cannot be tested on this evidence without modifying the frozen detector, which is **forbidden** (§40).

## 1. Artifact lineage + RANGE v4.4 identity (§1, §44)
- Authoritative RANGE baseline: **RANGE v4.4** (`3bb61cf`, contract `range-hierarchical-v4.4`, config_id `23d98c07488913c1c99a7397b2f8791f4727115e04bdefc283fb6bfc4a468969`, status `RANGE_V4_4_RESEARCH_BASELINE_FROZEN`).
- Engine: `ve_n1_replay.range_engine_v4_4.RangeSemanticEngineV44` (source-only import, `acknowledge_construction_only=True`), the same lineage as the pre-existing `build_v44_dev.py`. **No thresholds/boundaries/state-semantics/MACRO logic changed** (§40).

## 2. Boundary identity (§4) — canonical, recovered not invented
The canonical executable boundary = `rng.macro_boundary_upper` / `rng.macro_boundary_lower` (+ `macro_id`, mid) emitted by the frozen engine **only when `macro_state == "CONFIRMED"** (the RANGE state). This is the exact representation used by the ratified `build_v44_dev.py`. Reproduced artifact for 2011-2018 (`v44_dev.json`) contains 5,832 CONFIRMED bars with populated upper/lower — so the representation is real and executable. **The §4 escape (`RANGE_BOUNDARY_IDENTITY_NOT_CANONICAL`) does NOT apply** — the boundary is canonical; the problem is the empty parent on the Alpha window.

## 3. Evidence firewall (§3) — dates reported
- Boundary build: frozen engine over `load("M15_v2", PRE_HOLDOUT_SPLIT_ID, cutoff=2025-10-23)`, **warmup from 2011-07-26, collect only 2021-07-27→2023-12-29** (Alpha DEV; stops at DEV_END, no CALIB-2024/2025+/holdout). Artifact `v44_alpha.json` (`alpha_confirmed_bars=0`).
- Micro-path intended on native gated M5 (Alpha authorized), DEV = 2021-07-27→2023-12-29 (121,949 M5 bars).
- Verification run `v44_years.json` (warmup 2020-08→2023-12) for the by-year state audit.

## 4. Parent construction — EMPTY (the decisive result)
Intended parent (§4): episodes where RANGE v4.4 is causally CONFIRMED **and** a valid boundary is available before the attack. Actual on 2021-2023:
| year | bars processed | CANDIDATE | FORMING | **CONFIRMED** | other |
|---|---|---|---|---|---|
| 2020 (ref, warmup) | 9,693 | 2,502 | 5,448 | **920** | 823 |
| **2021** | 15,944 | 15,934 | 0 | **0** | 10 |
| **2022** | 873 | 873 | 0 | **0** | 0 |
| **2023** | 23,563 | 23,563 | 0 | **0** | 0 |
**Zero CONFIRMED macro bars in 2021, 2022, 2023** → 0 M5 bars with an active confirmed boundary → **FAMILY U parent attacks = 0, FAMILY L parent attacks = 0.** (2022's low bar count reflects an M15_v2 data gap, but the result is identical in the well-populated 2021 and 2023.)

## 5. Why — the frozen detector's known limitation (§40, diagnostic only)
From 2021 onward the macro state machine is **perpetually CANDIDATE** — it identifies candidate ranges but never promotes them to CONFIRMED. This is precisely the **documented, CEO-accepted V4.4 limitation** (`RANGE_V4_4_RESEARCH_BASELINE`: "can miss genuine RANGE via **stale-candidate slot-blocking**"), here manifesting *completely* on the post-2020 regime. **This is a Market-Intelligence property, not an Alpha finding, and — per §40 — it is reported, NOT fixed inside Alpha.** No detector modification was made or attempted.

## 6. Family analyses — N/A (no parent)
FAMILY U (upper→SHORT), FAMILY L (lower→LONG): **not computable** — zero boundary attacks. The 4-class construction (A clean rotation / B new-extreme-first / C breakout / D stalled), E0–E4 landmarks, failed-acceptance, failed-extension, inward-displacement, position controls, range-geometry/maturity/compression, attack-velocity, DISC/CONF, year-by-year, path-survivability, and same-parent controls (§8–§38) are all **vacuous on this evidence** — there is nothing to classify. The analysis harness (`range_rotation.py` / `range_rotation2.py`) is complete and would execute these on any non-empty parent; it returns 0 parents here.

## 7. §41 / §42 / §43 questions — answered
**UPPER (§41) and LOWER (§42):** Q1 "how many valid boundary attacks?" = **0** (no CONFIRMED ranges) — every downstream question (clean-rotation fraction, new-extreme-first, breakout, velocity, maturity, compression, landmark informativeness, robust signal) is **N/A: no parent population on the Alpha evidence.** **Cross-side (§43):** symmetry/superiority/tradeability are undecidable — both sides are empty.

## 8. Limitations
- The finding is bounded to the **Alpha authorized native-M5 evidence (2021-2023)** under the **frozen** RANGE v4.4. RANGE v4.4 *does* confirm ranges pre-2021 (2011-2020: e.g., 5,832 CONFIRMED bars in 2011-2018, 920 in 2020) — but that period predates the native-M5 evidence (only M15_v2 exists there), so the M5 boundary-attack micro-path the mandate requires cannot be built on it.
- Reproducible artifacts: `build_v44_alpha.py`, `verify_v44_years.py`, `v44_alpha.json` (alpha_confirmed_bars=0), `v44_years.json` (by-year state audit), `range_rotation.py`/`range_rotation2.py` (harness).

## 9. CEO recommendation
1. **`NO_ROBUST_RANGE_UPPER_SHORT_SIGNAL_FOUND` and `NO_ROBUST_RANGE_LOWER_LONG_SIGNAL_FOUND` — because the parent population is EMPTY, not because rotations were tested and failed.** The frozen RANGE v4.4 detector confirms **zero macro ranges** on the Alpha native-M5 window (2021-2023); its post-2020 state machine is permanently CANDIDATE (the documented stale-candidate slot-blocking limitation, complete on this regime).
2. **This is a frozen-Market-Intelligence property, surfaced honestly and NOT fixed inside Alpha (§40).** The boundary representation is canonical (recovered, not invented, §4). To study RANGE boundary rotation on the Alpha evidence, a **CEO/VE decision on the RANGE detector** would be required — either (a) VE addresses the post-2020 stale-candidate slot-blocking under a Market-Intelligence mandate (out of Alpha's scope), or (b) authorize a RANGE-state source that confirms ranges on 2021-2023. **Neither is Alpha's to decide.**
3. **Also available as a scientific datapoint:** RANGE v4.4 confirms ranges on 2011-2020 (M15_v2), so the rotation study is *feasible in principle* — but only where native-M5 does not exist, so the early-landmark M5 micro-path cannot be built there. A future mandate could run the rotation 4-class analysis at **M15 resolution on 2011-2020** if the CEO wants the RANGE-rotation science despite the resolution/period trade-off.
4. **No promotion; no MI retuning; no execution; broker disabled; DEV-only; no CALIB.** RANGE v4.4 (`3bb61cf`) and all frozen strategies untouched; portfolio SHORT still only frozen `H4-bo-raw-S`.

**Terminal statuses:** `RANGE_UPPER_ROTATION_DISCOVERY_COMPLETE` · `NO_ROBUST_RANGE_UPPER_SHORT_SIGNAL_FOUND` ; `RANGE_LOWER_ROTATION_DISCOVERY_COMPLETE` · `NO_ROBUST_RANGE_LOWER_LONG_SIGNAL_FOUND`. **STOP.**
