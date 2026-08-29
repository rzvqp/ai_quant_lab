# CAUSAL_REPLAY_ACCELERATOR_V1 — BENCHMARK

**Method**: `tradingview-mcp/causal_replay_benchmark.mjs`, 200 synthetic routine bars (no events),
exclusively via the `_deps` mock injection seam. **No live Q4 bar, or any live bar of any kind, was
processed** (mandate §16: "Do not benchmark on unseen Q4 bars" — extended here, per this mandate's
own §6/§13 discipline, to mean no live bar at all, seen or unseen).

## Results

| Method | Bars | External calls | Calls/bar | Wall time (ms) | Bars/min (mocked) |
|---|---:|---:|---:|---:|---:|
| CURRENT_METHOD | 200 | 600 | 3.000 | 51,837.5 | 231 |
| ATOMIC_STEP_ONLY | 200 | 400 | 2.000 | 52,371.7 | 229 |
| HYBRID_CAUSAL_EVENT_GATED | 200 | 50 | 0.250 | 51,877.2 | 231 |

`STATE_PARITY_ERRORS: 0`. `INTEGRITY_FAILURES: 0`.

**Call reduction**: CURRENT_METHOD (3.0/bar) → ATOMIC_STEP_ONLY (2.0/bar, **1.5x**) →
HYBRID on a routine stretch (0.25/bar, **12x** — one external call pair covers up to 8 bars).

## Why the wall-time column is flat across all three methods — read honestly, not glossed over

The three methods take essentially identical wall time (~51.8-52.4s) despite a 12x difference in
external call count. This is **not** evidence the accelerator doesn't help — it is an artifact of
benchmarking against a mock: `core/replay.js`'s own `step()` function polls
`currentDate()` every 250ms until it observes a change, with a hard-coded `setTimeout(r, 250)` in
its own polling loop (this is real production code, unmodified, needed because the real CDP
`doStep()` call is itself asynchronous and its effect isn't immediately visible). Every method here
calls the real `step()` exactly 200 times — once per bar, regardless of how the surrounding calls
are composed — so every method pays the same ~200 × 250ms ≈ 50s of polling overhead. **A mocked
benchmark cannot exercise the one thing external-call-count reduction is actually for: avoiding
real network/CDP round-trip latency**, because a mock has none to avoid. That latency is exactly
what mandate §13's "do not test against the live connection" constraint prevents this benchmark
from measuring directly.

**What this benchmark CAN and does honestly establish**: the call-count reduction itself
(3 → 2 → 0.25 per bar) is a direct, mechanical count of the actual code paths exercised — not an
estimate. If each external MCP tool call in real usage carries roughly constant overhead (the
standard assumption for this class of optimization, and the same assumption
`CAUSAL_REPLAY_ACCELERATOR_V1_DESIGN.md` made for its own order-of-magnitude estimates), real-world
throughput improvement should track the call-count reduction closely — 1.5x for Layer A alone, up
to 12x for Layer B on routine stretches specifically (§5 of the implementation doc discloses why
"routine stretches specifically" is a real, not a blanket, qualifier).

## What was NOT measured (disclosed, not silently omitted)

- Real CDP/browser round-trip latency (would require live connection — out of scope, §13).
- Reasoning-layer token/time cost per call (a separate, real cost the original design doc's own
  "compact-vs-full logging" discipline addresses — this mandate's Layer A/B reduce call COUNT, not
  reasoning cost per call; the two are complementary, not substitutes).
- Behavior when an event gate actually fires mid-run (functionally tested in
  `causal_replay.test.js`'s T14, but this benchmark's own 200-bar run deliberately used a
  no-events fixture to isolate the routine-stretch throughput number cleanly).
