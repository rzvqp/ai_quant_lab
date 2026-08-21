# VE_GENERIC_STRATEGY_EV_AUTHORITY_ARCHITECTURE

**Mandate**: `VE-AI-TRADER-GENERIC-EV-AUTHORITY-001`
**Repo**: `ai_quant_lab-research-main`, branch `ai-trader-implementation`
**Closes the gap explicitly disclosed and left open by**: `AI_TRADER_NEW_BRAIN_ARCHITECTURE.md` section 8,
`AI_TRADER_NEW_BRAIN_IMPLEMENTATION_REPORT.md` section 7 item 1, and
`AI_TRADER_VALIDATED_STRATEGY_ONBOARDING_CONTRACT.md`'s closing section ("What this contract does NOT
cover") — all three state, verbatim, that no real ratified `EVDecisionEngine` exists for any strategy
admitted through AI-Trader's own `StrategyCatalog`, and that closing this requires "a separate, explicitly
CEO/Statistician/Red-Team-ratified EV/decision-rule authority... a second, separate, not-yet-authorized
mandate." This document is that mandate's architecture record.

## 1. Root cause audit (mandate section 6)

### 1.1 Exact source of the blocker

`ve_brain.decide_n6` (`ai_quant_lab-wp5b/ve_brain/ve_brain/n6.py`) is the only ratified EV/decision
authority that exists anywhere in this project's dependency graph. Its gating sequence, read byte-for-byte:

0. N1 contract version check -> `INCOMPATIBLE_N1_CONTRACT`
1. `validate_request()` -> `SCHEMA_VALIDATION_FAILED`
2. catalog sealed + version/hash check -> `CATALOG_NOT_SEALED` / `CATALOG_VERSION_MISMATCH`
3. resolve `(strategy_id, strategy_version)` from the **sealed** registry -> `UNKNOWN_STRATEGY`
4. recompute + verify `strategy_policy_fingerprint` -> `STRATEGY_POLICY_MISMATCH`
5. `requires_true_range(canon)` gate (independent of eligibility/EV)
6. eligibility / regime / market-map / confirmation checks
7. `run_ev(candidate)` -> `NEGATIVE_EXPECTED_VALUE` / `MISSING_PROBABILITY_INPUTS`
8. `TRADE` (if `can_execute_real`) or `SHADOW_TRADE_CANDIDATE`

Step 3 is the blocker: the registry it resolves against is `_canonical_catalog.CANONICAL_STRATEGIES`, a
`tuple` of exactly 4 `StrategyContract` literals (`trend_pullback`, `range_fade`, `trend_shadow`,
`trend_experimental`), sealed at import time via `SealedRegistry.build()`. Any `strategy_id` outside this
set fails at step 3 with `UNKNOWN_STRATEGY`, **before** eligibility, before `requires_true_range`, before
`run_ev` — regardless of how well-formed or economically sound the request is.

### 1.2 Why the registry is sealed shut (not an oversight)

`n6.py`'s own module docstring records this as the **4th through 6th instance of a closed defect**:
(4) manual `EligibilityDecision` + candidate construction with matching IDs, (5) an injectable registry
**parameter**, (6) a consumer-populable open-registration API (`register_canonical_strategy()`, empty
registry, first-registrant-wins). Each of these let a consumer register `range_fade` (a strategy the
system must be able to identify and block in RANGE regimes) *as* `trend_pullback`, bypassing the RANGE
block entirely. The remedy adopted was: embed the catalog as Python literals, seal it at import via
`SealedRegistry.build()`, version + hash it, and reject any registry that doesn't match the approved
hash. The governing principle, quoted directly from the module: *"Consumatorul poate CERE încărcarea unei
strategii aprobate; nu poate defini conținutul ei"* — the consumer may **request** loading an approved
strategy; it may never **define** its content.

This rules out, categorically, any design in this mandate that reopens `_SEALED_CATALOG`, adds a 5th
literal to it, accepts an injectable registry parameter, or exposes any registration API on `ve_brain`
itself. Doing so would be the exact 7th recurrence of a defect `ve_brain` has already been hardened
against three times.

### 1.3 The separable primitive: `run_ev` is not part of the seal

`ve_brain.ev_engine.run_ev(req: DecisionRequest) -> EVOutcome` is public (`ve_brain.__all__`), and — read
in full — **never reads `strategy_id` and never touches the sealed catalog**. It computes
`EV_R = p_t·RR − p_s·1 + p_h·E[X|h] − c/R` (LCB-guarded) via `_ev_core`, purely from geometry
(entry/stop/target), cost, and `ProbabilityInputs`. The catalog-gating logic (section 1.1, steps 2-4) and
the EV math (step 7) are two independent concerns that happen to be composed inside one sealed function.
`run_ev`, `DecisionRequest`, `validate_request`, `ProbabilityInputs`, `data_identity`, `regime_fingerprint`,
and `decision_fingerprint` are all public, generic, and strategy-agnostic — reusable for any strategy's
inputs without touching the seal.

`catalog.py` (AI-Trader's own `StrategyCatalog`, not `ve_brain`'s) independently confirms this exact
reading in its own docstring, written before this mandate existed: *"An AI-Trader-owned registry,
deliberately NOT ve_brain's own internal catalog... a future validated strategy is admitted HERE, never
by waiting for a new ve_brain release."*

### 1.4 Selected fix: closest to mandate option C, composed with reuse

Of the mandate's own options (A: new `ve_brain` version: rejected, see 1.2; B: generic validated-strategy
decision adapter; C: versioned external strategy authority contract), the implemented fix is a hybrid,
closest to **C**: a new, separate, versioned decision authority — `RealEVDecisionEngine`
(`strategy_platform/real_ev_engine.py`) — that:

- **Never imports or calls `ve_brain.decide_n6`** (mechanically proven, section 4.3).
- Performs its **own** admission gate against AI-Trader's **own**, already-built `StrategyCatalog` —
  the registry `catalog.py` already documented as the intended generic admission point.
- Reuses `ve_brain`'s **public**, generic, already-ratified EV primitives (`run_ev`, `DecisionRequest`,
  `validate_request`, `ProbabilityInputs`) directly, so the economic decision rule itself is not
  reinvented or duplicated — only composed with a different (and independently sealed-safe) admission
  front-end.

This satisfies mandate section 2's constraints simultaneously: no strategy is hardcoded into AI Trader
core (admission is table-driven off `StrategyCatalog`, section 2 below); the Risk Engine, Execution
Adapter, and N1-N6 are untouched (section 4); `ve_brain`'s seal is never reopened, weakened, or routed
around (section 1.2); and any future `VALIDATED` `StrategyCatalog` entry reaches this same authority
through the same contract, with zero code change (section 5, fixture proof).

## 2. Architecture

```
canonical N1-N6 --> MarketState --> StrategyCatalog --> StrategyRouter --> validated Strategy
    --> TradeHypothesis --> RealEVDecisionEngine (NEW) --> Risk Engine (unmodified)
    --> Execution Adapter (unmodified, broker gate disabled) --> ShadowLedger
```

`RealEVDecisionEngine` sits exactly where `MockEVDecisionEngine` already sat, behind the same
`EVDecisionEngine` Protocol (`ev_engine.py`), so `pipeline.run_cycle` calls either engine identically —
`ev_engine.decide(hypothesis) -> EVDecision`. No new pipeline stage, no new call site shape.

### 2.1 Admission gate (`RealEVDecisionEngine.decide`, mandate section 8)

Fails closed, in order, before any EV math runs:

1. `catalog.lookup(strategy_id, strategy_version)` returns `None` -> `UNKNOWN_STRATEGY`
2. entry not `enabled` -> `STRATEGY_DISABLED`
3. `hypothesis.strategy_config_fingerprint != entry.config_fingerprint` -> `STRATEGY_POLICY_MISMATCH`
4. `entry.status not in {VALIDATED}` -> `NO_ELIGIBLE_STRATEGY` (mandate section 10 scope note, section
   2.4 below)
5. `entry.validation_provenance is None` -> `STRATEGY_POLICY_MISMATCH` (structurally can't happen once
   past `CatalogEntry.__post_init__`, checked again here for defense in depth)
6. `hypothesis.market_state_identity != market_state_identity(self.market_state)` -> `MARKET_STATE_MISMATCH`
7. `market_state.atr is None or market_state.entry_price is None` -> `MARKET_STATE_INVALID`
8. `axes.n1_contract_version != ve_brain.N1_CONTRACT_VERSION` -> `INCOMPATIBLE_N1_CONTRACT`
9. NaN/inf on `intended_entry`/`invalidation`, or timestamp ordering violations, or an unparsable
   `exit_specification` -> `SCHEMA_VALIDATION_FAILED`
10. `ve_brain.validate_request()` raises -> `SCHEMA_VALIDATION_FAILED`
11. `_decode_probability_inputs()` returns `None` (missing/malformed `expected_edge`) ->
    `MISSING_PROBABILITY_INPUTS`
12. `ve_brain.run_ev(req)` -> `not outcome.enter` -> `NEGATIVE_EXPECTED_VALUE` (LCB not positive) or
    `INFEASIBLE_GEOMETRY` (feasibility reason)
13. otherwise -> `TRADE_DECISION`, reason `REAL_EV_VALIDATED_EDGE`

Every failure path is a **named, registered** reason code (`reason_codes.py`, 10 new additive constants —
section 4.2), never a free-text string invented at the call site.

### 2.2 Generic Strategy Decision Contract (mandate section 7)

No new duplicate schema was invented. The contract is the composition of two schemas that already exist
and are already ratified:

- **`TradeHypothesis`** (`trade_hypothesis.py`, `TRADE_HYPOTHESIS_SCHEMA_VERSION="trade-hypothesis-v1"`) —
  carries `strategy_id`, `strategy_version`, `direction`, entry hypothesis (`intended_entry`),
  `invalidation` (SL), `exit_specification` (TP/RR), `market_state_identity`,
  `strategy_config_fingerprint`, `research_validation_identity`, `dedup_key`, timestamps, and the one
  free-form field, `expected_edge` — this is where `RealEVDecisionEngine` reads its EV inputs
  (`edge_schema`, `n`, `n_target`, `n_horizon`, `sum_horizon_r`, `credibility`) under its own versioned
  sub-schema, `EXPECTED_EDGE_SCHEMA_VERSION = "real-ev-expected-edge-v1"`, decoded by
  `_decode_probability_inputs` and never accepted unversioned.
- **`ve_brain.DecisionRequest`** (`contracts.py`) — `RealEVDecisionEngine` builds one internally per
  `decide()` call, carrying the causal data fingerprint (`ve_brain.data_identity`), regime fingerprint
  (`ve_brain.regime_fingerprint(axes)`), and a `configuration_fingerprint`
  (`ve_brain.decision_fingerprint`) — the same fingerprint machinery `decide_n6` itself uses, so a
  `RealEVDecisionEngine` decision is reproducible and comparable using the project's existing tooling
  (`ve_brain.compare_decisions`), not a bespoke one.

`strategy_id`/`strategy_version`/`strategy_fingerprint` (mandate section 7's own vocabulary) map onto
`TradeHypothesis.strategy_id`/`strategy_version`/`strategy_config_fingerprint`; `strategy_status` maps onto
`CatalogEntry.status`; `MarketState identity` onto `market_state_identity`; dedup identity onto
`TradeHypothesis.dedup_key`; causal data fingerprint onto `ve_brain.data_identity`.

### 2.3 Separation of Strategy Alpha from EV authority (mandate section 9)

`real_ev_engine.py` contains **no** strategy-specific branch. Mechanically proven, not merely asserted:
`test_no_strategy_id_branch_exists_in_real_ev_engine_source` parses the module with `ast.parse`, strips
the docstring (`tree.body[1:]` when the first node is an `Expr`), and asserts none of
`FIXTURE_FUTURE_VALIDATED_STRATEGY`, `MOCK_LONG_ON_FIXED_FIXTURE`, `trend_pullback`, `range_fade`,
`trend_shadow`, `trend_experimental`, or `S5` appear anywhere in the remaining **code** (the docstring is
excluded deliberately, since explanatory prose legitimately discusses these names — the guard is on
executable logic, not prose). `Strategy.evaluate()` owns WHEN/direction/entry/SL-TP/evidence;
`RealEVDecisionEngine.decide()` owns economic admissibility only.

### 2.4 Scope note on `StrategyStatus` (mandate section 10)

`EVDecision.decision` is a 2-value type (`TRADE_DECISION` / `NO_TRADE` only — no 3rd "shadow" value,
unlike `ve_brain`'s own `DecisionResponse`). Only `StrategyStatus.VALIDATED` reaches `TRADE_DECISION`
through `RealEVDecisionEngine`; all 5 other statuses (`MOCK_TEST_ONLY`, `RESEARCH_ONLY`,
`ALPHA_CANDIDATE`, `DISABLED`, `RETIRED`) fail closed to `NO_ELIGIBLE_STRATEGY`. This intentionally does
not attempt to invent a shadow-grade decision tier inside the real engine — `MockEVDecisionEngine` remains
the correct engine for `MOCK_TEST_ONLY` pipeline-mechanics testing (section 2.5), and no strategy reaches
`RealEVDecisionEngine` at all except through a real `StrategyCatalog` entry.

### 2.5 Mock/Real no-ambiguity (mandate section 10)

A real, previously-latent bug was found and fixed during implementation (not a hypothetical the mandate
asked to guard against in the abstract — an actually-reproduced defect): `pipeline._fingerprints()` stamped
every `ShadowLedgerRecord` with a **hardcoded module constant**, `EV_ENGINE_VERSION = "mock-ev-engine-v1"`,
regardless of which engine instance actually produced the decision. A smoke test running
`RealEVDecisionEngine` through the real pipeline confirmed the ledger recorded `"mock-ev-engine-v1"` even
though the real engine ran — the audit trail would have silently lied about which engine produced every
decision, directly against this section's "no ambiguity" requirement.

Fix: `engine_version` is now a **read-only `@property`** on the `EVDecisionEngine` Protocol (not a plain
`str` attribute — a plain annotation requires a *settable* attribute under mypy structural typing, which a
frozen dataclass field, `RealEVDecisionEngine`'s own shape, cannot satisfy). `MockEVDecisionEngine` exposes
it as a class attribute (`MOCK_EV_ENGINE_VERSION`); `RealEVDecisionEngine` exposes it as a frozen dataclass
field (`REAL_EV_ENGINE_VERSION`). `pipeline._fingerprints()` now takes `ev_engine_version` as an explicit
keyword (default = the Mock constant, used only at the two pre-EV-decide call sites where no engine
instance exists yet), and all 4 post-decide call sites pass `ev_engine.engine_version` explicitly. Runtime
identity and audit trail can now never drift apart.

### 2.6 Fail-closed if REAL requested but not installed (mandate section 10)

`RealEVDecisionEngine.__post_init__` calls `_verify_ve_brain_installed()`, which raises
`RealEVAuthorityError` unless `ve_brain.VE_BRAIN_VERSION` is in a pinned tuple of verified versions
(`("0.1.3",)` today). Tampering with the installed `ve_brain.VE_BRAIN_VERSION` (wrong string, or `None` —
simulating an uninstalled/unreadable artifact) fails construction itself, before any hypothesis is ever
evaluated — the engine cannot silently degrade to an unverified `ve_brain` build.

## 3. Versioning (mandate section 11)

| Identity | Value |
|---|---|
| `RealEVDecisionEngine.engine_version` | `real-ev-engine-v1` |
| Expected-edge sub-schema | `real-ev-expected-edge-v1` |
| Router-version stamped on the internal `DecisionRequest` | `real-ev-engine-admission-v1` |
| Eligibility-policy-version stamped on the internal `DecisionRequest` | `real-ev-engine-eligibility-v1` |
| Verified `ve_brain` versions | `("0.1.3",)` |
| `TradeHypothesis` schema (reused, unchanged) | `trade-hypothesis-v1` |

No date-stamped human "implementation fingerprint" label (the convention used in the sibling
`ve_n1_replay`/RANGE work) is adopted here — confirmed via a full read of `ve_brain`'s own version/manifest
modules that this is **not** a `ve_brain` convention; `ve_brain` uses semver + `SOURCE_COMMIT` + an
explicit `artifact_manifest(delivery_commit)` instead, and `strategy_platform` itself has no prior
manifest/fingerprint convention beyond the string constants above and the delivering git commit itself.
Following the project's own local convention rather than importing an unrelated one: **the delivering git
commit hash is the artifact identity** for this change, recorded in the implementation report (section
5) and this repo's own `## DELIVERED`-style chronological register precedent (`PROJECT_STATE.md` in the
sibling `ai_quant_lab-wp5b` repo; this repo's own `AI_TRADER_PROJECT_STATE.md` is updated the same way,
section 5 of the implementation report).

No sealed release is mutated: `ve_brain` (version `0.1.3`) is not touched, not repackaged, not
re-versioned. `real_ev_engine.py` is a wholly new module version-stamped independently.

## 4. What was deliberately NOT done

- `ve_brain.n6.decide_n6`, `_SEALED_CATALOG`, `_canonical_catalog.py` — **not modified, not called, not
  imported** by `real_ev_engine.py` (mechanically verified, section 2.3 / implementation report section 4).
- Risk Engine (`risk_manager_live.engine.evaluate_trade_proposal`) and Execution Adapter
  (`risk_execution_adapter.py`, `execution_shadow.py`) — **not modified**. `RealEVDecisionEngine` produces
  the same `EVDecision` shape `MockEVDecisionEngine` already produced; everything downstream is unaware
  which engine ran.
- N1-N6, `MarketState`, RANGE V4.4 semantics — **not touched** (mandate section 4).
- S5 — **not implemented, not onboarded, not referenced anywhere in `real_ev_engine.py`'s code** (mandate
  section 5, section 2.3 above). The fixture strategy used to prove the generic path
  (`future_strategy_fixture.py`) is explicitly and unambiguously named `FIXTURE_FUTURE_VALIDATED_STRATEGY_
  {POSITIVE,NEGATIVE}` — it is not, and cannot be mistaken for, S5 or any real candidate.
- Broker submission — remains structurally `DISABLED` (`BrokerOrderSubmissionGate(enabled=False)`,
  untouched); every test that reaches `TRADE_DECISION` is proven to terminate at
  `BLOCKED_AT_GATE:` before any order attempt (mandate section 15/16, implementation report section 6).
