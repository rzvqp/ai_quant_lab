# ALPHA_XAUUSD_RANGE_TF_AUTHORITY_PARENT_RECOVERY_REPORT

**Mandate:** `ALPHA-XAUUSD-RANGE-TF-AUTHORITY-PARENT-RECOVERY-001` · **Date:** 2026-08-22 · **Read-only architecture/parent-availability diagnosis.**
**Terminal verdict:** **`RANGE_CANONICAL_PARENT_EXISTS_BUT_POST2020_UNAVAILABLE`** · **`RANGE_ALPHA_BLOCKED_BY_MI_STATE_MACHINE`**.
**Scope:** RANGE only; read-only; no MI retuning; no new boundary; no CANDIDATE-as-RANGE; no Alpha strategy test. Frozen RANGE v4.4 (`3bb61cf`, config_id `23d98c07…`) inspected/executed unchanged. Price-only, DEV-only. No promotion; broker disabled.

---

## 0. Headline
- **Timeframe authority is UNAMBIGUOUS: M15 is the sole canonical RANGE authority.** The frozen handoff entry point is `RangeSemanticEngineV44(timeframe="15m", bar_interval_seconds=900)`; the canonical population is "OANDA:XAUUSD **M15**"; the config is a single frozen bar-count calibration (`ConfigV44`, 21 fields). **No canonical H1/H4 RANGE state, config, or boundary exists anywhere in the lineage.**
- **The canonical parent (M15 `macro_state=="CONFIRMED"` spans + `macro_boundary_upper`/`_lower`/`macro_id`) genuinely EXISTS** — it produced 5,832 CONFIRMED bars on 2011-2018 — but on the modern Alpha window it is **empty: 0 CONFIRMED in 2021, 2022, 2023.**
- **Root cause diagnosed mechanically:** the single-active-MACRO slot (`forming_macro = self._active_macro is None`) is occupied for months by candidates that never satisfy the confirmation gate in the trending post-2020 regime. **Last CONFIRMED = 2020-12-31; thereafter candidates cycle 132→133→134, each `CANDIDATE`-only** (133 alone held the slot ~7 months). This is the documented, CEO-accepted V4.4 **"stale-candidate slot-blocking"** limitation.
- **Therefore RANGE Alpha on the modern native-M5 era is NOT blocked because it was tested and failed — it is blocked because the canonical parent is unavailable, gated by the MI state machine.** Not Alpha's to fix (§8 of the handoff, §40 of the prior mandate).

## 1. Governance correction (§1) — append-only, no history rewrite
The prior mandate (`ALPHA-XAUUSD-RANGE-BOUNDARY-FAILED-BREAK-ROTATION-001`, commit `11425fd`) returned status strings `NO_ROBUST_RANGE_UPPER_SHORT_SIGNAL_FOUND` / `NO_ROBUST_RANGE_LOWER_LONG_SIGNAL_FOUND`. Its **prose already stated the correct reason** ("EMPTY parent population… not because rotations were tested and failed"), but the status strings could be misread. **Corrected interpretation (append-only; prior report/commit untouched):**
- `RANGE_ROTATION_DISCOVERY_BLOCKED_EMPTY_CANONICAL_PARENT`
- `RANGE_UPPER_ALPHA_NOT_TESTED` · `RANGE_LOWER_ALPHA_NOT_TESTED`
- **NO conclusion about RANGE Alpha profitability.** All measured counts (0 CONFIRMED 2021/2022/2023; parent N=0) are preserved unchanged.

## 2. RANGE v4.4 lineage + N1–N6 role (§2)
Canonical detector (handoff §1/§2): commit **`3bb61cf`**, contract `range-hierarchical-v4.4`, source-only (not in any wheel), entry point `RangeSemanticEngineV44` which **composes canonical N1 + the RANGE producer**. **N1 supplies only `trend_context` (a direction axis)** computed from the same fed bar stream (`_trend_context(n1_result.raw_axes.direction)`), not an independent higher-timeframe input. The RANGE macro state + boundaries are produced by `RangeSemanticProducerV44` from the fed M15 bars. **V4.4.1 (`4ed4eb4`) is explicitly "do not use"; v2/v2_1/v3/v3_1/v4_3 are legacy — none canonical.**

## 3. Timeframe authority map — answers to §3
| # | question | answer (mechanical) |
|---|---|---|
| 1 | Which TF owns macro RANGE state? | **M15** — frozen entry point `timeframe="15m"`, canonical population "OANDA:XAUUSD M15". |
| 2 | Which TF creates `macro_boundary_upper/lower`, `macro_id`? | **M15** — emitted only on `macro_state=="CONFIRMED"` from the M15-fed producer. |
| 3 | Is M15 the sole canonical authority? | **YES.** |
| 4 | Does H1 participate in RANGE confirmation? | **No.** N1 provides a trend-direction axis from the M15 stream; there is no H1 bar input to confirmation. |
| 5 | Does H1 expose an independently usable canonical RANGE state? | **NO** — no H1 detector/config exists. |
| 6 | Does H1 expose canonical causal boundaries? | **NO.** |
| 7 | Is M5 used only downstream (microstructure/execution)? | **YES** — RANGE is M15; the prior mandate correctly used M15 boundary → native-M5 micro-path. |
| 8 | Any parallel/legacy non-canonical RANGE detectors? | **YES** — `range_engine_v2/v2_1/v3/v3_1/v4_3` + `v4_4_1` exist in the repo but are **non-canonical**; only v4.4 is canonical. **Not used to manufacture a parent (§9/§10).** |

**H4/H1/M15/M5 roles:** H4 — not a RANGE authority (no H4 RANGE component). H1 — not a RANGE authority (no H1 RANGE state/config/boundary). **M15 — the sole RANGE-state + boundary authority.** M5 — downstream microstructure/entry-path only.

## 4. Config identity (§4) — frozen, TF-agnostic in form, M15 in calibration
`ConfigV44`: `d_macro=29, d_internal=12, n_touch=2, K_reentry=22, N_accept=3, K_struct=2, n_external_swings=2, atr_window=14, w_atr=0.80` (+ derived `tol_cluster=s_max=1.60`), canonical ATR `ai_trader.structural_observer.vendor_bridge.atr14`. Parameters are **dimensionless bar counts** (no `timeframe` field) — the engine is TF-parametric — **but the freeze, benchmarks, config_id and canonical population are all M15.** Running the M15-frozen config on H1 bars would apply a ~29-**H1**-bar (~5-day) macro scale never ratified — i.e., a **non-canonical configuration**, which §4 (no aggregation change) and §10 (no alternative boundary) forbid. **No config was modified or overridden.**

## 5. Modern evidence availability + M15 verification (§5, §6)
Frozen engine run over M15_v2 (sanctioned loader, warmup from 2011, config_id verified). Independent by-year state audit (`verify_v44_years.py` → `v44_years.json`):
| year | bars processed | CANDIDATE | FORMING | **CONFIRMED** |
|---|---|---|---|---|
| 2020 (ref) | 9,693 | 2,502 | 5,448 | **920** |
| **2021** | 15,944 | 15,934 | 0 | **0** |
| **2022** | 873 | 873 | 0 | **0** |
| **2023** | 23,563 | 23,563 | 0 | **0** |
**Reproduced: 0 CONFIRMED in 2021, 2022, 2023.** Also surfaced: **M15_v2 has a large data gap ~2021-09 → 2023** (2022 nearly absent, 873 bars) — a data-availability fact independent of the state machine; but both the well-populated 2021-Jan–Sep (15,934 bars) and 2023 (23,563 bars) show **zero CONFIRMED**.

## 6. State-transition audit + stale-candidate diagnosis (§6, §7) — the exact gate
Read-only transition trace (`range_state_audit.py` → `v44_state_audit.json`, 2020-08→2021-09, the modern data before the gap):
- **Last `CONFIRMED` transition: 2020-12-31 05:45 UTC (macro_id 131).** Last `FORMING`: 2020-12-31 02:30 UTC (macro_id 131). 27 distinct CONFIRMED macro_ids up to end-2020.
- **Post-2020: 3 distinct slot occupants — macro_id 132, 133, 134 — every one `states=['CANDIDATE']` only.** None ever reached FORMING or CONFIRMED.
- **macro_id 133 held the single slot from 2021-01-06 to 2021-08-08 (~7 months) as a perpetual CANDIDATE.** Transition tail: 2020 shows healthy `CANDIDATE→FORMING→CONFIRMED→WEAKENING` lifecycles; post-2020 shows only `CANDIDATE→None→CANDIDATE`.
- **Exact gate (code, `range_semantic_v4_4.py` docstring + V4.3 core):** MACRO is **single-active-at-a-time by construction** — `forming_macro = self._active_macro is None`. A new MACRO candidate can form **only when the slot is empty**. Promotion CANDIDATE→FORMING→CONFIRMED requires the confirmation gate (`n_touch=2` touches per side + `N_accept=3` + alternation over the trailing window, etc.). In the strongly-trending post-2020 regime price does not oscillate between two opposing boundaries enough to satisfy that gate, so the live candidate **never promotes**; while it occupies the slot **no other range can confirm**; when it finally clears (→None) the next candidate immediately takes the slot and repeats. **This is precisely the documented, CEO-accepted V4.4 "stale-candidate slot-blocking" limitation** (handoff §8), here total for post-2020. **Diagnosed, not modified.**

## 7. H1 availability test (§5, §8) — no canonical H1 parent
There is **no canonical H1 RANGE state, config, or boundary** to run (§3 Q5/Q6). Feeding H1 bars into the M15-frozen engine would be a non-canonical configuration (§4) and is **forbidden** — not performed. **The modern RANGE Alpha parent is therefore unavailable on any canonical higher timeframe.** (§9 CANDIDATE-substitution and §10 alternative-boundary-invention were likewise not performed.)

## 8. Canonical-parent verdict (§13)
- The canonical RANGE parent **EXISTS and is well-defined** (M15 CONFIRMED spans + boundaries; the §4 boundary-identity is canonical, recovered not invented).
- It is **UNAVAILABLE on the modern Alpha window (2021-2023)** — 0 CONFIRMED — due to the **MI state machine** (single-active-macro slot + unmet confirmation gate in a trending regime = stale-candidate slot-blocking).
- The timeframe authority is **NOT ambiguous** (it is unambiguously M15), so the "ambiguous" verdict does not apply; and there is **no higher-TF canonical alternative** (H1 does not exist), so the "recovered on higher TF" verdict does not apply.
- ⇒ **`RANGE_CANONICAL_PARENT_EXISTS_BUT_POST2020_UNAVAILABLE` · `RANGE_ALPHA_BLOCKED_BY_MI_STATE_MACHINE`.**

## 9. Next-step recommendation
1. **RANGE Alpha on the modern native-M5 era is not researchable today** — its canonical parent (M15 CONFIRMED ranges) is empty post-2020 because of the frozen detector's known slot-blocking limitation. This is a **Market-Intelligence / VE decision, not Alpha's to make or fix** (handoff §8/§9; prior-mandate §40). Options for the CEO/VE (out of this mandate's scope): (a) a VE-authorized fix of the post-2020 stale-candidate slot-blocking under a Market-Intelligence mandate; (b) authorize a RANGE-state source that confirms ranges on 2021-2023; (c) accept that V4.4 (conservative by design) simply finds no macro ranges in the 2021-2023 trend regime.
2. **RANGE rotation science is feasible only where V4.4 confirms** — 2011-2020 (M15). But native M5 does not exist there, so the M5 early-landmark micro-path the rotation mandate requires cannot be built; a future mandate could run the 4-class rotation at **M15 resolution on 2011-2020** if the CEO wants the science despite the resolution/period trade-off.
3. **Do NOT** substitute CANDIDATE for CONFIRMED, invent a boundary, or run the M15 engine on H1 to manufacture a parent — all forbidden and all avoided here.
4. **No MI retuning; no Alpha strategy test; no promotion; broker disabled; DEV-only.** RANGE v4.4 (`3bb61cf`) and all frozen strategies untouched; portfolio SHORT still only frozen `H4-bo-raw-S`.

**Terminal verdict:** `RANGE_CANONICAL_PARENT_EXISTS_BUT_POST2020_UNAVAILABLE` · `RANGE_ALPHA_BLOCKED_BY_MI_STATE_MACHINE`. **STOP.**
