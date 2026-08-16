# IMPLEMENTATION_QUEUE — declarative specs (SPEC-ONLY, no evaluation)

**Division:** Alpha Discovery (Flow B) · **Date:** 2026-08-16 · **Mandate:** CEO 2026-08-16.

**Hard constraints honored here:**
- These are **specifications only**. No hypothesis is evaluated. **`m` is NOT incremented** for any spec below.
- **No substitute is invented for a missing primitive.** A mechanism whose primitive is absent is marked
  `IMPLEMENTATION_BLOCKED_MISSING_PRIMITIVE` and stops there.
- Every "permitted regime" is defined in **canonical N1** terms. New evaluations on the noncanonical swing
  classifier are forbidden, and canonical N1 is `ALPHA_BLOCKED_CANONICAL_N1_HANDOFF`. **Therefore all five,
  even the spec-ready ones, are evaluation-deferred until `N1_HANDOFF_PASS`.**

Available Alpha primitives (verified in `edge_research/regime.py`, `_screen.py`): `trend_regime`,
`compression_flags`, `episodes`, `last_swing_levels`, `detect_swings`, `label_structure`, `day_index_ny17`,
and the canonical evaluator `mstrat.simulate` via `canonical_evaluate`. Canonical exit menu (`exit_kind`):
`rr`, `trailing`, `time`, `opp_liq`. **No regime-state exit exists in that menu.**

---

## 1. EXIT_ON_REGIME_INVALIDATION — `IMPLEMENTATION_BLOCKED_MISSING_PRIMITIVE`
- **Economic rationale:** hold a trend-following position only while the regime that justified it persists;
  close the instant the regime is invalidated (e.g. a long taken in TREND_UP is closed when structure flips
  out of TREND_UP), rather than waiting for a fixed time/ATR/RR stop. Thesis: most give-back happens after
  the regime has already turned but before a static stop fires.
- **Primitives required:** (a) a **per-bar regime-state stream** the exit can read; (b) a **regime-state
  exit hook** in the canonical evaluator that closes a position when `regime[i] != entry_regime`.
- **Primitive status — MISSING (both):**
  - (b) The canonical `mstrat.simulate` exit menu is `{rr, trailing, time, opp_liq}` — **no regime-state
    exit**. Adding one is a change to the lab's single ratified evaluator, not Alpha's to make; the local
    `_screen.simulate` substitute is **eliminated** (forbidden). No substitute permitted.
  - (a) A *canonical* per-bar regime stream is the N1 producer itself, which is `BLOCKED_ON_N1_ARTIFACT`.
- **Input/output contract (for when unblocked):** in: OHLC + per-bar canonical regime label; out: canonical
  trades whose exit index = first bar with `regime != entry_regime` (or the static backstop, whichever first).
- **Permitted regime:** TREND_UP (long) / TREND_DOWN (short), canonical N1.
- **Tests required:** deterministic exit-on-flip fixture; no-lookahead (exit uses `regime[<=i]`); backstop
  still applies; parity of the regime stream with N1.
- **Distinct from existing clusters?** Yes — it is an **exit mechanism**, orthogonal to the entry clusters
  (pullback/continuation/momentum/breakout). It would form a new `exit_mechanism` axis, not a new entry cluster.
- **Action:** BLOCKED. Do not implement. Do not grow `m`. Revisit after the canonical evaluator exposes a
  regime-state exit AND `N1_HANDOFF_PASS` delivers the per-bar regime stream.

---

## 2. session-conditioned — `SPEC_READY · EVALUATION_DEFERRED`
- **Economic rationale:** the trend-continuation edge is not uniform across the day; condition entry on the
  session (e.g. London / NY overlap vs Asia) where directional follow-through concentrates.
- **Primitives required:** per-bar session label. **PRESENT** — deterministically derivable from bar
  timestamps; `day_index_ny17` already anchors the NY-17:00 boundary, session windows extend it. No new
  detector, no missing primitive.
- **Input/output contract:** in: OHLC + ts→session map + a base entry mechanism; out: entries filtered to
  the permitted session set. Overlay only — does not alter the base entry/stop/exit.
- **Permitted regime:** any canonical trend regime the base mechanism already permits.
- **Tests required:** session boundaries correct across DST; no-lookahead (session known at bar open);
  **distinctness test** (below).
- **Distinct from existing clusters?** **Contested — must be proven, not assumed.** A session gate on an
  existing pullback is a *variant* unless the gate changes **which mechanism survives** (not merely
  subsamples an existing survivor). Distinctness gate: a session-conditioned mechanism counts as new ONLY if
  it survives where its unconditioned parent does NOT (or vice versa). Otherwise it is a variant and **must
  not grow `m`.** Its own `mechanism_cluster` = `<regime>|session:<set>`.
- **Action:** spec ready; evaluation deferred to post-`N1_HANDOFF_PASS`. `m` unchanged.

---

## 3. volatility-conditioned — `SPEC_READY · EVALUATION_DEFERRED`
- **Economic rationale:** trend edges depend on the volatility regime; condition entry on a vol band (e.g.
  only when Parkinson log-range / ATR sits in a target band), avoiding both dead-calm and blow-off tape.
- **Primitives required:** per-bar volatility measure. **PRESENT** — `atr14` (canonical, used by the engine)
  and the lab's official Parkinson log-range `ln(H/L)` (E000 primary metric) are both derivable. No missing
  primitive.
- **Input/output contract:** in: OHLC + per-bar vol + band thresholds + base mechanism; out: entries filtered
  to the permitted vol band. Overlay only.
- **Permitted regime:** any canonical trend/transition regime the base mechanism permits.
- **Tests required:** vol computed causally (`vol[<=i]`); band edges deterministic; **distinctness test** as §2.
- **Distinct from existing clusters?** Same caveat as §2 — a vol gate is a *conditioning overlay*; it is a new
  mechanism only if it survives disjointly from its unconditioned parent. `mechanism_cluster` =
  `<regime>|vol:<band>`. Do not grow `m` unless the distinctness gate passes.
- **Action:** spec ready; evaluation deferred. `m` unchanged.

---

## 4. breakout continuation — `SPEC_READY · DISTINCTNESS_CONTESTED · EVALUATION_DEFERRED`
- **Economic rationale:** after a confirmed BREAKOUT_TRANSITION break, ride the *post-break trend* by
  entering on the first resumption following the initial impulse — capturing the continuation leg, not the
  break itself.
- **Primitives required:** break event (`detect_breaks`/BOS) + a resumption trigger (fresh extreme after the
  break). **PRESENT.**
- **Input/output contract:** in: OHLC + break events; out: entry on the first post-break resumption bar,
  trend-direction only.
- **Permitted regime:** BREAKOUT_TRANSITION → TREND (canonical N1).
- **Tests required:** the entry strictly *follows* a confirmed break (no entry at the break bar); no-lookahead;
  distinctness vs the `breakout` and `continuation` clusters.
- **Distinct from existing clusters?** **Must be proven.** It sits between the existing `breakout` cluster
  (enter AT the break / its retest) and `TREND_UP|continuation` (fresh rolling-max within an established
  trend). Distinctness claim: it enters the *transition-to-trend hand-off* specifically. If its eligible set
  substantially coincides with either neighbor, it is a variant, not a mechanism — **do not grow `m`.**
- **Action:** spec ready; distinctness must clear before it earns a cluster; evaluation deferred.

---

## 5. compression-to-expansion — `POTENTIAL_DUPLICATE_OF_EXISTING_CLUSTER · EVALUATION_DEFERRED`
- **Economic rationale:** enter as a compression regime resolves into expansion (range coils, then displaces);
  trade the expansion leg.
- **Primitives required:** `compression_flags` + `expansion`/displacement. **PRESENT.**
- **Input/output contract:** in: OHLC + compression flag + expansion flag; out: entry on the
  compression→expansion transition bar, in the displacement direction.
- **Permitted regime:** COMPRESSION → BREAKOUT_TRANSITION (canonical N1).
- **Distinct from existing clusters?** **Likely NOT distinct.** The existing `COMPRESSION|compression_breakout`
  cluster (`comp_break`) already enters on the qualifying expansion bar out of compression — this appears to
  be the **same economic mechanism**. Unless a distinctness proof shows a materially different eligible set
  (e.g. requiring a sustained compression *state* transition vs a single expansion bar), this is a
  **`DUPLICATE_HYPOTHESIS`** of `comp_break` and **must not grow `m`** — it would be logged as a tombstone,
  consistent with the HSF dedup rule.
- **Tests required:** if pursued, an explicit distinctness test vs `comp_break`'s eligible set; else retire
  as duplicate.
- **Action:** do NOT implement as a new cluster without a passing distinctness proof. `m` unchanged.

---

## Summary
| # | mechanism | state | primitive | grows m? |
|---|---|---|---|---|
| 1 | EXIT_ON_REGIME_INVALIDATION | `IMPLEMENTATION_BLOCKED_MISSING_PRIMITIVE` | regime-state exit + per-bar N1 regime — **MISSING** | no |
| 2 | session-conditioned | `SPEC_READY · EVALUATION_DEFERRED` | present | only if distinctness passes |
| 3 | volatility-conditioned | `SPEC_READY · EVALUATION_DEFERRED` | present | only if distinctness passes |
| 4 | breakout continuation | `SPEC_READY · DISTINCTNESS_CONTESTED` | present | only if distinctness passes |
| 5 | compression-to-expansion | `POTENTIAL_DUPLICATE` of `comp_break` | present | no, unless distinctness passes |

All evaluation is deferred to **`N1_HANDOFF_PASS`**. No spec here increments `m`. No substitute primitive
was invented.
