# RANGE V4.4 — Alpha Discovery technical handoff

**Producer**: Validation Engine (VE). **Consumer**: Alpha Discovery department. **Date**: 2026-08-21.
**Status**: `V4_4_FROZEN_CONSERVATIVE_RESEARCH_BASELINE`. **Authorizing mandate**:
`VE-RANGE-V4_4-RESEARCH-BASELINE-CLOSE-001`.

This document is written to let you consume the RANGE V4.4 detector for feature/research purposes **without
reopening detector design**. If a question you have isn't answered here, that's a signal to ask VE/CEO before
inventing an interpretation — don't guess at semantics this document doesn't cover.

---

## 1 — Canonical detector identity

| Field | Value |
|---|---|
| Commit (frozen, do not use any other) | `3bb61cf` |
| Repo / branch | `ai_quant_lab-wp5b` / `discovery-mk-matrix-v1` |
| `contract_version` | `range-hierarchical-v4.4` |
| `config_id` | `23d98c07488913c1c99a7397b2f8791f4727115e04bdefc283fb6bfc4a468969` |
| Implementation fingerprint | `v4-4-implementation-freeze-2026-08-20` |

Before consuming any output, verify you are on `3bb61cf` (or a later commit that provably has NOT touched
`range_semantic_v4_4.py`/`range_engine_v4_4.py` — check with `git log -- <file>`), and that
`ConfigV44().config_id()` equals the value above. If it doesn't match, stop — you are not looking at the frozen
baseline.

**Do not use V4.4.1.** It exists in the same repo (`range_semantic_v4_4_1.py`, commit `4ed4eb4`) but is
**closed, not supported** (`V4_4_1_NOT_SUPPORTED_ON_F441`) — see §8 below.

---

## 2 — Import / API path

**V4.4 is source-only. It is not in any built `ve_n1_replay` wheel** (the shipped wheels stop at
`range_semantic_v3_1`/`range_engine_v3_1`, version 0.4.1 — confirmed by inspecting the wheel contents directly,
not assumed). Do not `pip install ve_n1_replay` and expect V4.4 to be present. Instead, import directly from
the source tree of this exact repo/commit:

```python
from ve_n1_replay.range_semantic_v4_4 import ConfigV44, RangeSemanticProducerV44, RangeSemanticResultV44
from ve_n1_replay.range_engine_v4_4 import RangeSemanticEngineV44
```

**Preferred entry point**: `RangeSemanticEngineV44` (composes canonical N1 + the RANGE producer — use this,
not the bare `RangeSemanticProducerV44`, unless you specifically need to drive the producer without N1).

```python
engine = RangeSemanticEngineV44(
    symbol="XAUUSD", timeframe="15m", bar_interval_seconds=900,
    implementation_commit=<N1 implementation commit>,
    range_config=ConfigV44(),
    acknowledge_construction_only=True,   # REQUIRED — see §9, this is not an optional flag to silence
)
n1_result, range_result, events = engine.observe_closed_bar(bar, as_of=None)
```

`RangeSemanticEngineV44.__init__` raises `ContractErrorV43` if `range_config.config_id()` doesn't match the
normative `RANGE_HIERARCHICAL_V4_4_NORMATIVE_CONFIG_ID` constant — this is a **feature**, not friction: it
means you cannot accidentally run against a silently-modified config. Do not catch and bypass this.

Batch replay: `engine.replay_batch(bars, as_of=None) -> RangeLedgerV44` (returns `run_hash`, full records,
`macro_history`/`internal_history`). Snapshot/restore: `engine.snapshot() -> RangeSnapshotV44`,
`engine.restore(snapshot)` — fail-closed on any identity mismatch (contract/config/N1-identity).

---

## 3 — Config identity (full registry, `ConfigV44`, all 21 fields — frozen, do not modify)

```
d_macro=29, d_internal=12, n_touch=2, K_reentry=22, N_accept=3, K_struct=2, n_external_swings=2,
atr_window=14, w_atr=0.8, atr_source=ai_trader.structural_observer.vendor_bridge.atr14,
atr_provenance_wheel_sha256=39673910666e13708b1d4cb7266d1730bb1c9ceea4e0b021a1bf3cfa1f8281f4,
contract_version=range-hierarchical-v4.4, ER_max=0.5, RND_max=1.0, ALT_MIN=0.5, MIN_TRAVERSALS=1, W=29,
ER_weakening=0.75, RND_weakening=2.0, WEAKENING_MAX_BARS=22, IOU_CONTINUE=0.5, GAP_MAX=12
```

Use `ConfigV44()` (all defaults) — do not override any field. If you believe a different value is needed for
your research question, that is a request to VE for a new detector variant, not something to patch locally;
silently running a modified config breaks reproducibility and the `config_id` guard above will catch it anyway.

---

## 4 — Causal input requirements

`observe()`/`observe_closed_bar()` requires, per **closed** bar, in strict chronological order (no lookahead —
V4.4 processes bars one at a time and never reads ahead):

| Input | Type | Notes |
|---|---|---|
| `ts_close` | int | bar close timestamp |
| `open_`, `high`, `low`, `close` | float | OHLC of the closed bar |
| `atr` | float \| None | canonical ATR14 (via N1's `_axes_builder.atr14()` when using the engine wrapper — do not compute your own ATR and feed it in, the provenance wheel hash is part of the frozen identity) |
| `trend_context` | str \| None | optional, passed through from N1's raw-axes direction |

The detector is a **pure incremental state machine** — same bar sequence in, same output out, deterministic,
snapshot/restart-invariant (verified via a 96/288/480-bar causality suite during implementation). It has no
knowledge of anything after the current bar.

---

## 5 — Output schema (`RangeSemanticResultV44`, 21 fields, returned every bar)

```python
available: bool                          # False only if ATR unavailable at this bar
bar_index: int
ts_close: int
macro_id: int | None                     # None when no active MACRO structure
macro_reason: str                        # one of 40 reason codes — see §6
macro_state: str | None                  # CANDIDATE / FORMING / CONFIRMED / WEAKENING / TERMINATED
macro_weakening_reason: str | None       # EXCURSION_PENDING / TRAILING_DEGRADATION, only when macro_state=WEAKENING
macro_boundary_upper: float | None
macro_boundary_lower: float | None
macro_confirm_ts: int | None             # bar index the structure reached CONFIRMED, None if never confirmed
macro_role: str | None
macro_continued_from_id: int | None      # episode-identity link to a predecessor MACRO (EPISODE_CONTINUATION/MERGE only)
regime: str | None
internal_id: int | None                  # F4/INTERNAL depth — byte-identical to V4.3, NOT part of the V4.4 MACRO release scope
internal_reason: str | None
internal_state: str | None
internal_boundary_upper: float | None
internal_boundary_lower: float | None
internal_role: str | None
config_id: str
contract_version: str
```

**A confirmed RANGE, for Alpha research purposes, is `macro_state == "CONFIRMED"`** (i.e., `macro_confirm_ts is
not None`). `macro_state in ("CANDIDATE", "FORMING")` is an **unconfirmed candidate** — do not treat this as a
detected RANGE; it is exactly the population V4.4's known limitation (§8) under-serves, and using it as if it
were a positive detection will import that bias directly into your feature.

---

## 6 — State semantics

`MacroStateV44 = "CANDIDATE" | "FORMING" | "CONFIRMED" | "WEAKENING" | "TERMINATED"`. Lifecycle: a candidate
forms from two opposing rejected/pending swings (`CANDIDATE`/`FORMING`), advances to `CONFIRMED` only once the
efficiency/net-displacement/traversal/alternation gates (T1–T3) are jointly satisfied, may enter `WEAKENING`
(excursion pending or trailing-close degradation) and either recover or terminate, and always ends in
`TERMINATED` (via breakout, degeneracy kill, or weakening-persistence). 40 total reason codes populate
`macro_reason`/emitted events — the 11 V4.4-specific ones are `INSUFFICIENT_EFFICIENCY`,
`INSUFFICIENT_TRAVERSAL`, `INSUFFICIENT_ALTERNATION_EVIDENCE`, `EXCESSIVE_NET_DISPLACEMENT`,
`RANGE_CANDIDATE_PRESENT`, `RANGE_WEAKENING`, `WEAKENING_RECOVERED`, `WEAKENING_PERSISTENCE_TERMINATED`,
`EPISODE_CONTINUATION`, `EPISODE_MERGED` (structurally unreachable, documented), `EPISODE_REPLACEMENT`; the
other 29 are inherited from V4.3 unchanged. `EpisodeAction = "MERGE" | "CONTINUATION" | "REPLACEMENT"` governs
how a new MACRO candidate is linked to the structure that just terminated — relevant if your research treats a
CONTINUATION/MERGE pair as one logical RANGE episode rather than two separate detections.

---

## 7 — How Alpha research may consume RANGE

Permitted: use `macro_state == "CONFIRMED"` spans (with their `macro_boundary_upper`/`_lower`,
`macro_confirm_ts`, `macro_id`) as a **feature/context input** into Alpha hypothesis generation, backtesting,
or signal construction — e.g., "is price currently inside a V4.4-confirmed RANGE," "how long has the current
RANGE been confirmed," "what is the RANGE's boundary width relative to ATR." Treat V4.4 exactly as you would
any other engineered feature: as an input to be tested, not as ground truth.

Do NOT treat V4.4's output as a proxy for the CEO's own RANGE semantics — it is a conservative approximation
with a known, one-directional bias (§8). Any Alpha result that depends on V4.4's recall being high, or on it
catching every genuine RANGE, is standing on a known-false assumption.

---

## 8 — Known limitations (do not omit when reporting results built on V4.4)

- **Misses genuine RANGE structures.** Mechanism: a never-confirmed candidate can occupy the single active-MACRO
  slot indefinitely once correctly rejected as directional by the confirmation gate, with nothing to release it
  — blocking a fresh, better-anchored candidate from ever forming. Diagnosed `b1dcf92`; independently confirmed
  again via V4.4.1's fresh-blind result (9 of the missed ranges in a 26-range sample were exactly this failure
  mode, F441/`8e550ae`).
- V4.4 is **not** a validated ground-truth reproduction of CEO RANGE semantics. It is a conservative baseline
  selected because the false-positive alternative was worse, not because it was shown correct.
- INTERNAL-depth output (`internal_*` fields) is byte-identical to V4.3 and was never part of V4.4's own
  development scope — treat it as a separate, unrelated signal if you use it at all.

---

## 9 — Forbidden interpretations

- Do not present V4.4 output as `FULLY_VALIDATED`, `GENERALIZATION_PASS`, or `LIVE_READY` in any downstream
  report — none of these are true. The correct status string is `V4_4_FROZEN_CONSERVATIVE_RESEARCH_BASELINE`.
- Do not use V4.4 (or any RANGE output) to submit orders, connect to a broker, or run in `LIVE_SHADOW`.
  `BROKER_ORDER_SUBMISSION` is disabled; this handoff does not change that.
- Do not promote V4.4 (or anything derived from it) directly into the Strategy Catalog or AI Trader without a
  separate, explicit authorization — this handoff is a research/feature-source grant only.
- Do not modify, retune, or "fix" V4.4's known limitation (§8) without a new CEO-authorized VE mandate —
  V4.4.1 was exactly that attempt, and it failed on fresh evidence (§1 of the closure report). If your research
  surfaces a case where V4.4's under-detection materially hurts your Alpha hypothesis, report it as evidence
  for CEO to weigh, not as license to patch the detector yourself.
- Do not construct `acknowledge_construction_only=True` as a stamp of production-readiness — it exists to force
  an explicit, conscious acknowledgment that this is research-only code, every time it's constructed.

---

## 10 — Data / evidence exclusions

| Evidence | Status | Rule |
|---|---|---|
| FB14 (13,511 bars) | Consumed detector-validation evidence | Do not reuse to tune or validate any Alpha hypothesis |
| F441 (14 windows) | Consumed detector-validation evidence | Do not reuse to tune or validate any Alpha hypothesis |
| MB3-001→024 | Diagnostic history | Informational only |
| **MB3-025→048** | **SEALED / UNTOUCHED** | Do not access for any purpose without separate CEO authorization |

CEO ground-truth labels from FB14/F441 validated the *detector*. Reusing them to select or tune an Alpha
strategy would silently contaminate whatever evidence you'd otherwise use to validate that strategy later —
treat them as spent, not as a bonus labeled dataset.

---

## 11 — Rollback reference

V4.4 at `3bb61cf` was independently rollback-tested twice: once during its own implementation mandate, and
again during V4.4.1's implementation (removing V4.4.1's files and confirming V4.4's 470/470 baseline test
suite is completely unaffected). If anything downstream of this handoff appears to depend on behavior that
isn't in this document, the fallback is: re-clone `ai_quant_lab-wp5b` at `3bb61cf`, run
`ve_n1_replay/tests/test_v4_4_*.py`, and confirm you get the same baseline described here before concluding
V4.4 itself has changed.
