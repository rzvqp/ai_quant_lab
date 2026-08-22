# S5_REAL_EV_RUNTIME_EVIDENCE_CONTRACT

**Mandate**: `VE-S5-REAL-EV-RUNTIME-PACKAGING-001`
**Implementation**: `ai_trader/new_brain_live/strategy_platform/s5_ev_evidence.py`
**Status**: normative for any strategy that packages verified EV aggregate evidence through
`RealEVDecisionEngine`, not S5-exclusive (the binding mechanism is generic; see "Reuse" below)

## 1. Purpose

Defines the immutable, versioned representation a validated strategy's EV aggregate evidence must take to
reach `RealEVDecisionEngine` (`ai_trader/new_brain_live/strategy_platform/real_ev_engine.py`,
mandate `VE-AI-TRADER-GENERIC-EV-AUTHORITY-001`) safely — bound to the exact strategy/cost identity it may
be used by, auditable back to its source evidence, and never confusable with synthetic test evidence.

## 2. The `ValidatedEVEvidence` dataclass

Frozen, `kw_only`, one instance per validated strategy's economic evidence package. Fields, grouped:

### 2.1 Artifact identity (mandate section 6 "artifact/version identity")

| Field | Type | Meaning |
|---|---|---|
| `schema_version` | `str` | This dataclass's own contract version (`"s5-ev-evidence-v1"` today) |

### 2.2 Strategy identity binding (section 9 — every field here is cross-checked against the runtime
`CatalogEntry` at decide()-time; a mismatch on ANY of them fails closed)

| Field | Type | Checked against |
|---|---|---|
| `strategy_id` | `str` | `CatalogEntry.strategy_id` |
| `strategy_version` | `str` | `CatalogEntry.strategy_version` |
| `implementation_fingerprint` | `str` | `CatalogEntry.implementation_fingerprint` |
| `config_fingerprint` | `str` | `CatalogEntry.config_fingerprint` |
| `alpha_candidate` | `str` | audit-only, not independently re-checked (no live Alpha-candidate registry exists) |
| `representative` | `str` | audit-only, same caveat |

### 2.3 Validation identity (section 7 — audit provenance; not independently re-verifiable against a
live registry, since none exists — trustworthiness comes from being a cited, source-controlled constant,
exactly like `CatalogEntry.validation_provenance` already is elsewhere in this codebase)

| Field | Type | Meaning |
|---|---|---|
| `validation_mandate` | `str` | the Red-Team/Statistician mandate id that produced the PASS verdict |
| `validation_commit` | `str` | the commit stamping that verdict |
| `validation_verdict` | `str` | e.g. `"INDEPENDENT_VALIDATION_PASS"` |
| `validation_ledger_sha256` | `str` | sha256 of the frozen trade ledger this evidence was extracted from |
| `validation_ledger_n` | `int` | trade count in that ledger (must equal `n` below) |

### 2.4 Evidence population identity (section 6)

| Field | Type | Meaning |
|---|---|---|
| `population_id` | `str` | which frozen validation population this evidence was extracted over |
| `population_ohlc_sha256` | `str` | sha256 of that population's OHLC data |
| `population_timeline_sha256` | `str` | sha256 of that population's timeline |
| `population_bars` | `int` | bar count in that population |

### 2.5 Cost identity (section 10 — the two fields cross-checked against the runtime `CostModel`)

| Field | Type | Checked against |
|---|---|---|
| `cost_model_id` | `str` | `CostModel.cost_model_id` |
| `cost_scenario` | `str` (`"BASE"` \| `"STRESS"`) | audit label for which scenario `round_trip_price` represents |
| `round_trip_price` | `float` | `CostModel.full_spread_price + entry_slippage_price + exit_slippage_price` (exact sum, tolerance `1e-9`) |

Validation-side spread was folded into slippage (the decomposition is not identified in the source
evidence, only the sum) — the runtime `CostModel`'s specific 3-way split does not matter, only that its
three fields sum to `round_trip_price`.

### 2.6 The REAL EV evidence (section 1/11 — the ONLY fields `ve_brain.run_ev` ever consumes, via
`_decode_probability_inputs`)

| Field | Type | Constraint |
|---|---|---|
| `n` | `int` | `>= 0` |
| `n_target` | `int` | `>= 0` |
| `n_horizon` | `int` | `>= 0` |
| `sum_horizon_r` | `float` | finite (never NaN/+-inf) |
| `credibility` | `float` | `0.0 < credibility < 1.0` |

Joint constraint (both enforced at construction AND at decode-time, independently — defense in depth):
`n_target + n_horizon <= n`. `n_stop` is **never** a stored field — it is always the derived
`@property n_stop = n - n_target - n_horizon`, so it can never independently drift from the three counts
above or be tampered in isolation.

**What must NEVER appear here** (Statistician `e54a2a5` section 11's own explicit prohibition, honored):
`win_rate`, a scalar `expected_edge`, `avg_R`, `PF`, `maxDD`, any confidence interval, any individual
ledger trade. Only the four raw counters plus `credibility` (a POLICY default, not evidence) are
permitted — `ve_brain.run_ev` derives its own probability terms (`p_t_lcb`, `p_h_hat`, `e_x_h`, etc.)
internally; this contract supplies inputs to that derivation, never its outputs.

### 2.7 Red Team fingerprints (section 8 — opaque identity labels)

| Field | Type | Meaning |
|---|---|---|
| `evidence_fingerprint` | `str` (64 hex) | stable across status re-stamps; invariant to status/reconciliation metadata |
| `source_artifact_fingerprint` | `str` (64 hex) | the specific `READY` re-stamp's own fingerprint |
| `source_artifact_id` | `str` | e.g. `"S5_VALIDATED_EV_AGGREGATES_V1"` |
| `source_commit` | `str` | the commit that produced `source_artifact_fingerprint` |

**Disclosed limitation**: Red Team's own reports do not publish the canonicalization recipe (field
order/serialization/separator convention) for either fingerprint. This codebase cannot independently
recompute them and does not attempt to — they are propagated as opaque, cited identity labels for audit
provenance, never cryptographically re-verified against the fields in 2.6. See section 6 below.

## 3. `to_expected_edge()` — the runtime binding

Renders a `ValidatedEVEvidence` into `TradeHypothesis.expected_edge`'s existing, frozen
`dict[str, float | str | None]` shape, still tagged `edge_schema="real-ev-expected-edge-v1"` (the ORIGINAL
schema from `VE-AI-TRADER-GENERIC-EV-AUTHORITY-001` — not a new version; this is additive, backward-
compatible schema evolution):

```python
{
    "edge_schema": "real-ev-expected-edge-v1",
    "n": <float>, "n_target": <float>, "n_horizon": <float>, "sum_horizon_r": <float>, "credibility": <float>,
    "evidence_strategy_id": <str>, "evidence_strategy_version": <str>,
    "evidence_implementation_fingerprint": <str>, "evidence_config_fingerprint": <str>,
    "evidence_cost_model_id": <str>, "evidence_round_trip_price": <float>,
    "evidence_fingerprint": <str>, "source_artifact_fingerprint": <str>,
}
```

The first five keys are the pre-existing v1 contract, unchanged. The remaining eight `evidence_*`/
`source_artifact_fingerprint` keys are **additive and OPTIONAL** — `RealEVDecisionEngine._decode_
probability_inputs` and `_verify_evidence_identity` only act on them when present. A payload lacking them
entirely (e.g. the pre-existing generic fixture's minimal 5-key dict) decodes and validates EXACTLY as it
did before this mandate — this is the backward-compatibility mechanism, proven by
`test_evidence_without_identity_keys_is_unaffected_backward_compat` in `test_real_ev_engine.py`.

## 4. Runtime validation sequence (inside `RealEVDecisionEngine.decide()`)

1. Admission (pre-existing, unchanged): `catalog.lookup()`, `entry.enabled`, `hypothesis.strategy_config_
   fingerprint == entry.config_fingerprint`, `entry.status == VALIDATED`.
2. MarketState identity, N1 contract compatibility, hypothesis geometry/expiry (pre-existing, unchanged).
3. `probability_inputs = _decode_probability_inputs(hypothesis.expected_edge)` — hardened (section 5).
4. **NEW**: `_verify_evidence_identity(hypothesis, entry=entry, cost_model=self.cost_model)` — if the edge
   declares any `evidence_strategy_id`/`evidence_strategy_version`/`evidence_implementation_fingerprint`/
   `evidence_config_fingerprint` key, ALL FOUR must match `entry`'s corresponding fields exactly, or the
   decision fails closed with `EVIDENCE_IDENTITY_MISMATCH`. If the edge declares `evidence_cost_model_id`
   or `evidence_round_trip_price`, both must match `self.cost_model` (id exactly, round-trip sum within
   `1e-9`), or the decision fails closed with `EVIDENCE_COST_IDENTITY_MISMATCH`.
5. `ve_brain.run_ev(req)` — unchanged, the sealed, ratified economic core.

`evidence_fingerprint` (if the edge declares one) is propagated onto the returned `EVDecision.evidence_
fingerprint` regardless of outcome (mandate section 20/23 — audit trail must identify which evidence
package was involved even for a rejected/NO_TRADE decision), then threaded into
`ShadowLedgerRecord.ev_decisions`'s third tuple element.

## 5. Fail-closed hardening (mandate sections 3-4 — applies to EVERY strategy's evidence, not S5-specific)

Two defects, independently confirmed OPEN by the Statistician (`9cfcc5f` section 15, by direct execution
of the pre-mandate `_decode_probability_inputs`), are fixed in the SAME function:

- **Defect A**: `sum_horizon_r = NaN`/`+inf`/`-inf` decoded as "VALID" pre-mandate, propagating a `NaN`
  EV — fail-closed only "by luck" of IEEE-754 comparison semantics. Fixed: explicit `math.isfinite()`
  check.
- **Defect B**: `n_target + n_horizon > n` (impossible count geometry, implying a negative `n_stop`)
  decoded as "VALID" pre-mandate; `ve_brain._ev_core.ev_from_terms`'s own `if p_s < 0.0: p_s = 0.0` clamp
  then silently absorbed the corruption into a plausible-looking but INFLATED EV. Fixed: explicit
  `n_target + n_horizon <= n` rejection, before `ve_brain.run_ev` is ever called.

Also additively hardened (mandate section 5, not independently flagged by the Statistician but directly
implied by "do not silently coerce corrupt evidence"): rejects `bool` values masquerading as counts
(`int(True) == 1` would otherwise silently pass), rejects fractional counts (`int(294.7) == 294` would
otherwise silently truncate), and no longer crashes with an uncaught `OverflowError` on `n=+inf` (the
pre-hardening `except (KeyError, TypeError, ValueError)` clause did not catch it).

## 6. What tamper-detection this contract does and does not provide (mandate section 17, disclosed
honestly — see `test_s5_ev_evidence.py`'s own tamper-test suite for the executable proof of every claim
below)

**Detected**: mutating `n_target` or `n_horizon` in a way that violates `n_target + n_horizon <= n` — the
SAME Defect-B geometry guard section 5 describes.

**NOT detected** (disclosed limitation, not a silent gap): mutating `n` alone (keeping geometry valid),
or mutating `sum_horizon_r` to a different-but-still-finite value. There is no cryptographic
re-verification of `evidence_fingerprint` against the economic fields, because Red Team's own reports do
not publish the canonicalization recipe needed to recompute it (confirmed by direct inspection of both
source reports — see the implementation report). The practical protection against this class of tampering
is that `ValidatedEVEvidence` instances are frozen dataclasses, constructed exactly once as source-
controlled module-level constants (mirroring `_canonical_catalog.CANONICAL_STRATEGIES`'s own "consumer
can REQUEST, never DEFINE" discipline) — changing the numbers requires changing and re-reviewing the
source file itself, not a runtime data-tampering vector.

## 7. Versioning

No sealed release is mutated. `S5_REAL_EV_EVIDENCE_V1` is version-stamped (`schema_version="s5-ev-
evidence-v1"`) independently of `real_ev_engine.py`'s own `REAL_EV_ENGINE_VERSION`/`EXPECTED_EDGE_SCHEMA_
VERSION` (both unchanged by this mandate) and of `TradeHypothesis`'s `TRADE_HYPOTHESIS_SCHEMA_VERSION`
(also unchanged). A future evidence package for a different strategy is a NEW `ValidatedEVEvidence`
instance with its own field values — never a mutation of `S5_REAL_EV_EVIDENCE_V1`, and never requires a
schema version bump unless the `ValidatedEVEvidence` dataclass's own field set changes.

## 8. Reuse for a future strategy

`ValidatedEVEvidence`/`to_expected_edge()`/the identity-binding verification in `RealEVDecisionEngine` are
generic — nothing in `real_ev_engine.py` or `s5_ev_evidence.py`'s CODE (docstrings excluded) references
`S5` or any specific strategy id (mechanically AST-verified,
`test_no_strategy_id_branch_exists_in_real_ev_engine_source`). A future strategy's own verified evidence
package is a new, separate `ValidatedEVEvidence` instance (in that strategy's own module, or a shared
evidence module — not `s5_ev_evidence.py`) with its own cited field values, consumed through the identical
`to_expected_edge()` → `RealEVDecisionEngine.decide()` path, with zero change to this contract's
implementation.
