# RANGE_STATE + longitudinal breakout events — contract, reachability & parity (ve_n1_replay 0.2.0)

Implements the **final** reconciled Statistician spec **STAT-RANGE-RECONCILED-SPEC-v1.0 (@`aca7801`)** with the
**`m_inference` FINAL amendment STAT-M-INFERENCE-FINAL-v1.0 (@`d0d08c1`, manifest v2.7.77, hash `aec8f07`)**, on the
reachability finding **RT-RANGE-0001 (@`5e56396`)**. RANGE_STATE is a **new additive longitudinal producer** — it never
reuses or reinterprets `StructBand.RANGE`, never routes through `applicable_regimes` (which is statically incapable of
producing RANGE), and never touches ve_brain / N3 / N4 / EV / N6 or the N1 engine. **N1 output stays byte-identical to
0.1.1.**

## Why a new producer (RT-RANGE-0001, confirmed two independent ways)

`applicable_regimes` emits `BREAKOUT_TRANSITION` only when `is_displacement AND structure=="range"`, but
`RawAxesBuilder` maps `structure` solely via `_BREAK_KIND_TO_STRUCTURE_DIRECTION` → `{strong, weak}`, so
`structure=="range"` is **statically unproducible**; `RANGE` was **retracted** by CEO `bd60c7a` and routes fail-closed to
`TRUE_RANGE_NOT_IDENTIFIABLE`. Empirically the canonical N1 ledger shows `BREAKOUT_TRANSITION` on **0 of 355,696 bars**.
So a *real* range and its breakout events require production, not relabeling — exactly this artifact.

## Version bumps (mandate §1 — seven, package-declared)

The N1 per-bar `evaluation_identity` (ve_brain-derived) is **unchanged** — that is what keeps N1 byte-identical. The
seven bumps are the package's 0.2.0 contract-surface identity, folded into the RANGE identity / ledger / snapshot:

| # | field | value |
|---|---|---|
| 1 | `n1_contract_version` (pkg) | `n1-replay-request-v2` |
| 2 | `raw_axis_schema_version` (pkg) | `raw-axis-schema-v2` |
| 3 | `router_version` (pkg) | `router-v2` |
| 4 | `range_state_contract_version` | `range-state-v1` |
| 5 | `range_event_contract_version` | `range-events-v1` |
| 6 | `snapshot_schema_version` (range) | `range-state-snapshot-v1` |
| 7 | `ledger_schema_version` (range) | `range-state-ledger-v1` |

Internal: `range_state_schema_version = range-state-schema-v1`, `producer_version = range-producer-0.2.0`.

## B — RANGE_STATE contract (producer)

Inputs (all ≤ evaluation instant): confirmed swings (symmetric 2k+1 fractals, k=2 → swing at i confirmed at i+k),
causal ATR14, close/high/low of **closed** bars. Consumes none of `StructBand`/`Direction`/`BREAKOUT_TRANSITION`.

- **Incremental state** (not a window recompute): `upper, lower, touches_upper, touches_lower, first/confirm bar,
  path_sum (Σ|Δclose|), net_disp, bars_in_state, last_update`.
- **Boundaries**: `upper` = max confirmed high-swing price in the episode, `lower` = min confirmed low-swing price.
  `boundary_validity ∈ {PROVISIONAL(<n_touch), CONFIRMED(≥n_touch both), EXTENDED(new swing moves the boundary, state
  survives), VIOLATED(accepted break)}`.
- **Timestamps**: `structural_start_ts` (first bar of the window satisfying the definition — retrospective) vs
  `actionable_start_ts = confirm_ts` (max confirmation time of the swings used — prospective).
  **`actionable_start_ts − structural_start_ts ≥ k bars` by construction** — execution has no access to the structural
  beginning.
- **`data_readiness ∈ {WARMUP, READY, DEGRADED}`** — warmup / missing structure / unavailable input / `direction=None`
  are **never** interpreted as RANGE_STATE (fail-closed).
- **`consolidation_state ∈ {NONE, FORMING, ESTABLISHED, DECAYING}`**: FORMING=PROVISIONAL; ESTABLISHED=CONFIRMED &
  ER≤ER_max & bars_in_state≥d_min; DECAYING=ER rises above ER_max without violation (signal, not invalidation).
  ER = `|close_end − close_start| / Σ|close_i − close_{i−1}|` — pure arithmetic on confirmed bars.
- **RANGE_MID** explicit (no entry). **Invalidation** on observable evidence only, never retroactive:
  `ACCEPTED_BREAK, MAX_DURATION, INPUT_UNAVAILABLE`; an invalidated range stays active in the journal on
  `[confirm_ts, t)`.
- **Reason codes**: `OK_RANGE, FEW_TOUCHES, ER_TOO_HIGH, TOO_SHORT, WIDTH_OUT_OF_GRID, WARMUP, INPUT_UNAVAILABLE,
  BOUNDARY_EXTENDED, ACCEPTED_BREAK, MAX_DURATION` (+ `NO_STRUCTURE` for the no-boundary-pair unavailable).
- **`range_spec_id`** = sha256 over the ordered dict `{n_touch, tol_atr, er_max, d_min_bars, width_filter,
  N_acceptance, precedence_rule, timeframe, swing_k, atr_window, range_state_schema_version, producer_version}`.
  `config_hash` extends it with operational params; **`run_hash = sha256(config_hash ‖ sha256(data_identity) ‖
  range_spec_id)`**. A result without `range_spec_id` is non-comparable by type.

## C — Longitudinal event contract (`range-events-v1`)

Eight events, each carrying `confirm_ts` (known without future bars), reason codes, and the information *not yet
available* at confirmation. State machine (the **only** machine-state transitions):

```
ESTABLISHED → {LOW_REJECTION, HIGH_REJECTION, MID, SWEEP_REVERSAL}   (in-state emissions, stay ESTABLISHED)
ESTABLISHED → BREAKOUT_CANDIDATE
BREAKOUT_CANDIDATE → BREAKOUT_ACCEPTED  XOR  FAILED_BREAKOUT          (mutually exclusive by construction)
BREAKOUT_ACCEPTED  → {BREAKOUT_RETEST, ∅}   and RANGE_STATE → VIOLATED
FAILED_BREAKOUT    → ESTABLISHED (the range survives)
```

- Priority per ESTABLISHED bar (mutually exclusive by close position): close beyond a CONFIRMED boundary → CANDIDATE;
  else wick beyond + close inside (D6 signature) → SWEEP_REVERSAL; else close in the tol band of a boundary →
  LOW/HIGH_REJECTION; else close strictly between → RANGE_MID.
- **ACCEPTED** = `N_acceptance` consecutive closes beyond (delay of N bars after candidate). **FAILED** = close back
  inside before N. These are different bars on different branches — never simultaneous.
- **RETEST** = after ACCEPTED, price returns into the tol band of the broken boundary without re-closing inside, within
  `retest_window`. **SWEEP_REVERSAL** = wick beyond + close inside on the same bar (reuse of the ratified D6 signature,
  `liquidity_mechanics.py` @`2d795bc`).
- Per-event invalidation: CANDIDATE expires (→ indeterminate) if neither ACCEPTED nor FAILED in N+1 bars; RETEST expires
  outside its window. Zero-lookahead per event. `MISSED_BEFORE_ACCEPTANCE` is a reporting requirement across the N grid
  (like `MISSED_BEFORE_CONFIRMATION` at N4) — the producer emits every N deterministically for that curve.

Any transition outside the machine raises `RangeContractError` (fail-closed).

## D — Precedence

`TREND_PAUSE ⊆ RANGE_STATE`, `precedence_rule = RANGE_STATE_OVER_TREND_PAUSE` (declared, entering `range_spec_id`). A
bar satisfying both is labeled RANGE_STATE while the N1 trend direction is kept as the `trend_context` **attribute**
(never lost). The taxonomy is **not** a partition and is not claimed to be. The ledger reports an **occupancy matrix**
(bars per consolidation_state + per event) so a rare label is distinguishable from one precedence swallowed.

## E — Disjoint test populations

F3/F4 (breakout) and F5/F6 (failed/sweep) take opposite sides on the same boundary → negative dependence → PRDS
violation. The machine makes their populations **disjoint by construction**: from BREAKOUT_CANDIDATE, ACCEPTED and
FAILED are mutually exclusive, so no event lands in both. The disjunction repairs PRDS; it does **not** reduce the
hypothesis count.

## F / F7 — Primary definition & the SAFETY_GUARD

Pre-registered primary (one definition; the grid is sensitivity-only): `n_touch=2, tol=0.25×ATR, ER_max=0.40,
d_min=1 day = 96 M15 bars (ratified: "D1 = 96 M15 bars"), N_acceptance=2, precedence=RANGE_STATE_OVER_TREND_PAUSE,
width_filter=off`.

**F7 `RANGE_MID_NO_ENTRY` — SAFETY_GUARD (final amendment @`d0d08c1`)**: not a strategy and not a hypothesis (produces
no p-value / MDE / threshold; `m_inference` is F1–F6 = 26, rank-1 0.001923, MDE 0.0869). It is an **executable
prohibition**: `RANGE_MID` is emitted as an explicit state carrying `safety_guard=RANGE_MID_NO_ENTRY`; `entry_decision`
returns a **refusal** for it (zero entry, zero candidate, zero p-value, zero broker reach, by construction); it is
counted in a **separate `n_guards`** register (`SAFETY_GUARDS`), present in the audit — never deduced from an absence of
trades. It survives snapshot/restart.

## Reachability & parity (all verified — `tests/test_range_state.py`, 34 tests)

- **N1 byte-identical** to a bare `N1IncrementalReplayEngine` (hence to 0.1.1) over trend_up/down/uncertain/oscillation.
- **Confirmed-swing stream byte-identical** to the ratified `detect_swings` (strict D2) over the full history.
- **RANGE_STATE + all 8 events reachable** on canonical fixtures (`test_reachability_all_events_and_range_state`).
- Actionable only after `confirm_ts`; `actionable_start_ts ≥ structural_start_ts + k`; FORMING has no actionable ts.
- F7: RANGE_MID emitted + guarded; entry refused; never a candidate; `n_guards>0` in the ledger; guard persists after
  snapshot/restart.
- candidate→accepted; candidate→failed; **accepted XOR failed**; retest; sweep+reversal; ACCEPTED_BREAK & MAX_DURATION
  invalidation.
- Zero-lookahead (future bars never change past outputs/events); chunk invariance via snapshot; **snapshot/restart in
  every machine state** (FORMING/ESTABLISHED/CANDIDATE/ACCEPTED); two instances share no state; `run_hash` invalidates
  on data/config change; foreign-identity snapshot rejected; **no MT5/broker/order_send/set_authority/probability_inputs**.

`RANGE_STATE_HANDOFF_PASS` is **not** self-declared; submitted as `READY_FOR_RANGE_STATE_HANDOFF_REVALIDATION`.
