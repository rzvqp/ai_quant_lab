# N1 CANONICAL RERUN — FEASIBILITY BLOCKER (fail-closed, evidence-backed)

**Status:** `ALPHA_RERUN_BLOCKED_N1_REPLAY_PERFORMANCE`
**Division:** Alpha Discovery (Flow B) · **Date:** 2026-08-16
**This is NOT a correctness defect** — smoke parity PASSED (see `N1_INSTALL_AND_PARITY_VERIFICATION.md`). It is a
**computational-scaling** blocker specific to bulk historical replay.

## The blocker
The canonical rerun requires a canonical N1 regime reading at **every** M15 bar of the research history
(**355,696 bars**, 2011→2026) to segment regime episodes and gate eligibility. The delivered
`ve_n1_replay 0.1.0` engine, by design, **accumulates all bars and recomputes RawAxes over the entire
accumulated history on every `observe_closed_bar`** (its own docstring: *"derives the CURRENT RawAxes from the
full accumulated history on each call … single continuous block, growing, never reset"*). That makes a full
replay **O(n²)–O(n³)**.

### Measured cost (isolated venv, this machine)
Whole-sequence timing:

| bars n | total | per-bar |
|---|---|---|
| 100 | 0.048 s | 0.48 ms |
| 200 | 0.201 s | 1.00 ms |
| 400 | 1.013 s | 2.53 ms |
| 800 | 8.830 s | 11.04 ms |

Marginal per-bar cost as history deepens (fresh engine primed to `history`, then time next bars):

| history depth | marginal per-bar |
|---|---|
| ~200 | 2.87 ms |
| ~600 | 18.28 ms |
| ~1000 | 54.62 ms |

Per-bar cost is itself growing super-linearly → total is at least O(n²), empirically closer to O(n³).

### Extrapolation to the full history (355,696 bars)
Even taking the **optimistic O(n²)** lower bound anchored at n=800 (8.83 s):
`8.83 s × (355696 / 800)² ≈ 1.75 × 10⁶ s ≈ 20 days` of continuous compute — and the marginal-cost curve implies
materially worse. RECENT_PRIMARY alone (~71k bars) is still multi-day. **Infeasible as delivered.**

No bounded-window / incremental / max-history option exists in the engine (only `reset` → zero bars, and an
`as_of` horizon cap that does not reduce cost).

## The fix is feasible — proven
RawAxes depends only on **bounded recent history**. A windowed reading (feed only the last W bars) is
**byte-identical** to the full-history reading:

| eval bar | W=500 | W=800 |
|---|---|---|
| 1000 | identical ✓ | identical ✓ |
| 1150 | identical ✓ | identical ✓ |
| 1300 | identical ✓ | identical ✓ |

(W must be ≥ the `compression()` window of 460 bars; W≈500 suffices in these tests.) This proves an
**incremental engine maintaining a rolling ~W-bar buffer would produce the exact same RawAxes at O(W) amortized
per bar → O(n·W) total ≈ minutes**, not days — with zero change to the numerical result.

## Requested resolution (Architect / VE — I will not reimplement the artifact)
Per the mandate ("Nu recrea RawAxesBuilder. Nu copia vendor_bridge."), Alpha cannot build this itself. One of:

1. **PREFERRED — `ve_n1_replay ≥ 0.1.1` with an incremental bounded-window research-replay mode**: a rolling
   W-bar buffer (W ≥ 460, exposed/pinned), O(n·W) total, **byte-identical** to the current full-history RawAxes.
   Alpha will supply the windowed-parity harness above as the acceptance gate.
2. **ALTERNATIVE — explicit authorization to run a bounded-trailing-window replay** at the research layer using
   the *unmodified* engine (fresh engine per eval bar, primed with the last W bars, W pinned ≥ 460), accompanied
   by a full windowed-vs-full parity proof over a sampled grid. Note this is still O(n·W²) and likely multi-day;
   acceptable only as a checkpointed detached background job.
3. **LAST RESORT — authorize a ~20-day checkpointed detached O(n²) full-history replay.** Impractical; listed for
   completeness.

## What is preserved (nothing lost, nothing faked)
- All **355** hypotheses, **16** duplicate tombstones, m_total **357**, hypothesis count **355** — untouched.
- The rerun manifest (`reports/N1_RERUN_MANIFEST.json`) stands: all 355 flagged `needs_n1_rerun=TRUE`.
- Old noncanonical results are **NOT** promoted, compared, or relabeled as canonical. No cost gate, no MDE, no
  edge verdict, no OOS access (count remains **0**) were computed — the rerun did not start.
- Official cost model `AI_TRADER_SHADOW_COST_MODEL_v1` (BASE round-trip 0.05, STRESS 0.24, calibration RATIFIED,
  config-fp `b7bb9a9aed17a1c8`, content_hash `1341f228…`, SE UNAVAILABLE) is located and ready to bind into the
  run hash the moment the replay is feasible.

**Standing status:** `ALPHA_BLOCKED_CANONICAL_N1_REPLAY_PERFORMANCE`. Install + parity PASS; awaiting an
incremental replay artifact (or explicit authorization for a windowed/long background job) before the 355 rerun,
cost, MDE, and shortlist can be produced.
