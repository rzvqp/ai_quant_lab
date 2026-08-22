"""Real (governed) EV Decision Engine (mandate VE-AI-TRADER-GENERIC-EV-AUTHORITY-001).

PROBLEM: `EVDecisionEngine` (`ev_engine.py`) has exactly one implementation, `MockEVDecisionEngine` -- a
deterministic dict-key echo, no real economics. The only REAL, ratified EV/decision authority in this
repository is `ve_brain.decide_n6`, but it is permanently, deliberately sealed to its own internal catalog
of exactly 4 strategies (`trend_pullback`/`range_fade`/`trend_shadow`/`trend_experimental`) -- closing a
real, three-times-reopened exploit (`ve_brain/n6.py`'s own docstring: manual EligibilityDecision
construction, an injectable registry parameter, and a consumer-populable open-registration API were each
tried and each let a consumer redefine `range_fade` as a trend strategy and bypass the RANGE block). None
of those patterns may be recreated here.

ROOT CAUSE (mandate section 6's own required audit, full detail in
`VE_GENERIC_STRATEGY_EV_AUTHORITY_ARCHITECTURE.md`): `ve_brain.decide_n6` = (a) a SEALED catalog gate,
permanently scoped to its own 4 strategies, PLUS (b) `ve_brain.run_ev` -- a separate, already-PUBLIC,
already-GENERIC, strategy-agnostic EV computation (`ve_brain.__all__` includes `run_ev`; it takes a
`DecisionRequest`'s geometry+probability inputs and returns an `EVOutcome` via `_ev_core`, the byte-identical
`bdd15e5` ratified engine -- it does not read or care about `strategy_id` at all). The catalog-gating half
is intentionally unextendable from outside `ve_brain`'s own release process; the EV-math half is a reusable
primitive built for exactly this kind of reuse.

`catalog.py`'s own docstring independently confirms the intended shape: AI-Trader's OWN `StrategyCatalog`
(NOT `ve_brain`'s) "is the generic admission point, independent of `ve_brain`'s sealed registry... a future
validated strategy is admitted HERE, never by waiting for a new `ve_brain` release." That catalog already
exists, is already tested, and already has zero VALIDATED entries (by design -- nothing has been validated
yet). What was missing was the EV step that can safely reach a governed decision for whatever the catalog
admits.

DESIGN, in one sentence: `RealEVDecisionEngine` re-verifies a `TradeHypothesis` against AI-Trader's OWN
`StrategyCatalog` (never trusting the hypothesis's own claims, exactly `decide_n6`'s "AUDIT, not
authoritative" discipline applied to a different, appropriate source of truth), builds a
`ve_brain.DecisionRequest` from the result (reusing the exact canonical schema, not inventing one), and
calls the exact same public, ratified `ve_brain.run_ev` used by `decide_n6` itself -- so a strategy admitted
through the generic catalog gets the SAME economic rigor as the 4 sealed ones, without `ve_brain` ever being
modified, without any new strategy being hardcoded here, and without reopening the closed injectable/open-
registration exploit (there is no public method on this class or anywhere in this module that lets a caller
DEFINE a catalog entry's content at runtime -- only AI-Trader's own, separately-built `StrategyCatalog`,
constructed by whoever assembles the pipeline for a given run, decides what is admitted).

`ve_brain.decide_n6` and its 4 sealed strategies are UNTOUCHED and UNINVOLVED here -- they continue to run,
byte-identically, through their own separate, pre-existing path (`new_brain_bridge/bridge.py`), which this
module does not call, import from, or interact with in any way.

SCOPE NOTE on `StrategyStatus`: only `VALIDATED` entries (mirroring `ve_brain`'s own RATIFIED/PROMOTED ->
`can_execute_real` distinction) may reach `TRADE_DECISION` here. `EVDecision.decision` itself only supports
`{TRADE_DECISION, NO_TRADE}` (`ev_engine.py`'s own `__post_init__`) -- there is no AI-Trader-side equivalent
of `ve_brain`'s three-way `SHADOW_TRADE_CANDIDATE`, so any non-VALIDATED status (including a future
ALPHA_CANDIDATE/shadow-analysis tier) resolves to `NO_TRADE`/`NO_ELIGIBLE_STRATEGY` here rather than
inventing a new EVDecision value the rest of the pipeline was never built to handle.

FAIL-CLOSED HARDENING (mandate `VE-S5-REAL-EV-RUNTIME-PACKAGING-001`, sections 3-4): the Statistician
independently confirmed, by executing this module's own `_decode_probability_inputs` in isolation
(`e54a2a5`/`9cfcc5f`), two fail-OPEN defects that pre-date that mandate: (A) a non-finite `sum_horizon_r`
(`NaN`/`+inf`/`-inf`) decoded to a "VALID" `ProbabilityInputs` and propagated a `NaN` EV -- fail-closed
only "by luck" of IEEE-754 comparison semantics, not by design; (B) an impossible count decomposition
(`n_target + n_horizon > n`, implying a negative `n_stop`) also decoded as "VALID" -- `ve_brain._ev_core.
ev_from_terms`'s own `if p_s < 0.0: p_s = 0.0` clamp then silently absorbed the corruption into a
plausible-looking but INFLATED EV (the more dangerous of the two: it fails open quietly). Both are fixed in
`_decode_probability_inputs` below, rejecting BEFORE either bad value ever reaches `ve_brain.run_ev` --
`ve_brain._ev_core` itself is sealed and was never a candidate for modification.

EVIDENCE IDENTITY BINDING (same mandate, section 9): a validated evidence package (e.g.
`s5_ev_evidence.S5_REAL_EV_EVIDENCE_V1`) renders itself into `expected_edge` via `ValidatedEVEvidence.
to_expected_edge()`, which adds OPTIONAL `evidence_*` keys alongside the five original ones. When present,
`decide()` cross-checks them generically against `entry`/`self.cost_model` -- the two real, independent
sources of truth already in scope -- before the evidence is trusted; no S5-specific code exists here, any
future strategy's evidence package gets the identical check. A payload lacking these optional keys (e.g.
the pre-existing fixture's) is unaffected and validates exactly as it always has.
"""

from __future__ import annotations

import dataclasses
import math

import ve_brain  # type: ignore[import-untyped]

from ai_trader.new_brain_live.market_state import MarketState, market_state_identity
from ai_trader.new_brain_live.strategy_platform import reason_codes as rc
from ai_trader.new_brain_live.strategy_platform.catalog import CatalogEntry, StrategyCatalog, StrategyStatus
from ai_trader.new_brain_live.strategy_platform.ev_engine import NO_TRADE, TRADE_DECISION, EVDecision
from ai_trader.new_brain_live.strategy_platform.trade_hypothesis import TradeHypothesis

# ── identity (mandate section 11) ──
REAL_EV_ENGINE_VERSION = "real-ev-engine-v1"
EXPECTED_EDGE_SCHEMA_VERSION = "real-ev-expected-edge-v1"
_MY_ROUTER_VERSION = "real-ev-engine-admission-v1"
_MY_ELIGIBILITY_POLICY_VERSION = "real-ev-engine-eligibility-v1"

#: ve_brain package versions this authority has been built and regression-tested against. Constructing
#: this engine against any other installed ve_brain version fails closed (mandate section 10).
_VERIFIED_VE_BRAIN_VERSIONS: tuple[str, ...] = ("0.1.3",)

#: Only VALIDATED may reach TRADE_DECISION here -- see module docstring's SCOPE NOTE.
_REAL_TRADE_ELIGIBLE_STATUSES = frozenset({StrategyStatus.VALIDATED})


class RealEVAuthorityError(RuntimeError):
    """Fail-closed at construction time: the real authority cannot be safely installed (mandate section
    10 -- 'runtime must fail closed if REAL is requested but not properly installed/authorized')."""


class CostModelIdentityError(ValueError):
    """Raised when a `CostModel` is malformed -- fail-closed, never a silently-defaulted cost."""


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class CostModel:
    """Explicit, versioned cost assumptions (mandate section 7 'cost assumptions', section 8 'cost model
    identity validates'). Constructed once by whoever assembles the pipeline for a run; never invented
    ad hoc per-hypothesis, never read from the hypothesis itself (a strategy proposing its own cost
    model would be the strategy grading its own homework)."""

    cost_model_id: str
    full_spread_price: float
    entry_slippage_price: float
    exit_slippage_price: float

    def __post_init__(self) -> None:
        if not self.cost_model_id:
            raise CostModelIdentityError("CostModel.cost_model_id must not be empty")
        for name, v in (("full_spread_price", self.full_spread_price),
                        ("entry_slippage_price", self.entry_slippage_price),
                        ("exit_slippage_price", self.exit_slippage_price)):
            if not (v == v and v >= 0.0 and v != float("inf")):  # NaN/inf/negative all rejected
                raise CostModelIdentityError(f"CostModel.{name} must be a finite, non-negative float, got {v!r}")


def _verify_ve_brain_installed() -> None:
    version = getattr(ve_brain, "VE_BRAIN_VERSION", None)
    if version not in _VERIFIED_VE_BRAIN_VERSIONS:
        raise RealEVAuthorityError(
            f"ve_brain version {version!r} is not one this authority has been verified against "
            f"{_VERIFIED_VE_BRAIN_VERSIONS} -- fail-closed, refusing to construct. Do not bypass this "
            f"check; re-verify (regression + new equivalence tests) before adding a new version here.")


def _no_trade(hypothesis: TradeHypothesis, *reasons: str, evidence_fingerprint: str = "") -> EVDecision:
    return EVDecision(hypothesis=hypothesis, decision=NO_TRADE, reason_codes=tuple(reasons) or (rc.EV_BELOW_THRESHOLD,),
                       evidence_fingerprint=evidence_fingerprint)


def _decode_count(raw: object) -> int | None:
    """Decode one count field (`n`/`n_target`/`n_horizon`). Rejects: `bool` (a Python `int` subclass --
    `int(True) == 1` would otherwise silently coerce a stray boolean into a count, mandate section 5);
    any non-`int`/`float` type; a non-finite float (`+inf`/`-inf`/`NaN` -- `int(float('inf'))` raises
    `OverflowError`, which the PRE-hardening code's `except (KeyError, TypeError, ValueError)` did NOT
    catch, a latent crash-instead-of-fail-closed bug fixed here too); and a FRACTIONAL float (e.g. `294.7`)
    -- `int(294.7) == 294` would otherwise silently truncate corrupt evidence rather than reject it
    (mandate section 5 "do not silently coerce corrupt evidence")."""
    if isinstance(raw, bool) or not isinstance(raw, (int, float)):
        return None
    if isinstance(raw, float) and (not math.isfinite(raw) or not raw.is_integer()):
        return None
    return int(raw)


def _decode_probability_inputs(expected_edge: dict[str, float | str | None] | None) -> "ve_brain.ProbabilityInputs | None":
    """Decode a single-cell empirical-Bayes probability input from `TradeHypothesis.expected_edge`'s
    existing, frozen `dict[str, float|str|None]` shape (mandate section 7 -- schema recovered from the
    canonical `ve_brain.ProbabilityInputs`/`OutcomeCell`, not invented incompatibly, but ENCODED through
    the one extensibility point `TradeHypothesis` already has, since that dataclass is itself frozen/out
    of this mandate's scope to modify). Requires `edge_schema == EXPECTED_EDGE_SCHEMA_VERSION` plus the 5
    numeric fields; anything else (missing, wrong schema, wrong types) returns None -- the caller then
    fails closed to MISSING_PROBABILITY_INPUTS, exactly `ve_brain.run_ev`'s own 'never invented' discipline.

    HARDENED (mandate `VE-S5-REAL-EV-RUNTIME-PACKAGING-001` sections 3-4, see module docstring): rejects
    non-finite `sum_horizon_r` (Defect A) and impossible count geometry `n_target + n_horizon > n`
    (Defect B) BEFORE either can reach `ve_brain.run_ev` -- both previously decoded as "VALID"."""
    if not expected_edge:
        return None
    if expected_edge.get("edge_schema") != EXPECTED_EDGE_SCHEMA_VERSION:
        return None

    n = _decode_count(expected_edge.get("n"))
    n_target = _decode_count(expected_edge.get("n_target"))
    n_horizon = _decode_count(expected_edge.get("n_horizon"))
    if n is None or n_target is None or n_horizon is None:
        return None
    if n < 0 or n_target < 0 or n_horizon < 0:
        return None
    if n_target + n_horizon > n:
        # Defect B: an impossible decomposition implying a negative n_stop = n - n_target - n_horizon.
        # ve_brain._ev_core.ev_from_terms clamps the resulting p_s to 0.0 rather than rejecting -- fail
        # closed HERE, before that sealed clamp ever gets a chance to inflate the EV.
        return None

    raw_sum = expected_edge.get("sum_horizon_r")
    if isinstance(raw_sum, bool) or not isinstance(raw_sum, (int, float)):
        return None
    sum_horizon_r = float(raw_sum)
    if not math.isfinite(sum_horizon_r):
        # Defect A: NaN/+-inf must never reach ve_brain.run_ev. Explicit math.isfinite(), not an implicit
        # `sum_horizon_r == sum_horizon_r` NaN-comparison trick -- "do not rely on IEEE comparison
        # behavior to fail accidentally" (mandate section 3's own instruction).
        return None

    raw_credibility = expected_edge.get("credibility", 0.80)
    if isinstance(raw_credibility, bool) or not isinstance(raw_credibility, (int, float)):
        return None
    credibility = float(raw_credibility)
    if not math.isfinite(credibility) or not (0.0 < credibility < 1.0):
        return None

    cell = ve_brain.OutcomeCell(n=n, n_target=n_target, n_horizon=n_horizon, sum_horizon_R=sum_horizon_r)
    return ve_brain.ProbabilityInputs(hierarchy=(ve_brain.HierarchyLevel(cell=cell),), credibility=credibility)


def _verify_evidence_identity(hypothesis: TradeHypothesis, *, entry: "CatalogEntry", cost_model: CostModel) -> str | None:
    """Generic evidence-identity-binding check (mandate section 9) -- NO strategy-specific code: cross-
    checks whatever `evidence_*` keys `expected_edge` happens to declare against the two real, independent
    sources of truth `decide()` already has (the looked-up `CatalogEntry`, `self.cost_model`). A payload
    declaring none of these optional keys (e.g. the pre-existing generic fixture's) is unaffected -- this
    returns None (no mismatch) for it exactly as before this mandate.

    Returns a reason code string on mismatch, or None if the binding is consistent (or not declared)."""
    edge = hypothesis.expected_edge or {}
    if any(k in edge for k in ("evidence_strategy_id", "evidence_strategy_version",
                                "evidence_implementation_fingerprint", "evidence_config_fingerprint")):
        if (edge.get("evidence_strategy_id") != entry.strategy_id
                or edge.get("evidence_strategy_version") != entry.strategy_version
                or edge.get("evidence_implementation_fingerprint") != entry.implementation_fingerprint
                or edge.get("evidence_config_fingerprint") != entry.config_fingerprint):
            return rc.EVIDENCE_IDENTITY_MISMATCH
    if any(k in edge for k in ("evidence_cost_model_id", "evidence_round_trip_price")):
        if edge.get("evidence_cost_model_id") != cost_model.cost_model_id:
            return rc.EVIDENCE_COST_IDENTITY_MISMATCH
        declared_rt = edge.get("evidence_round_trip_price")
        if isinstance(declared_rt, bool) or not isinstance(declared_rt, (int, float)):
            return rc.EVIDENCE_COST_IDENTITY_MISMATCH
        actual_rt = cost_model.full_spread_price + cost_model.entry_slippage_price + cost_model.exit_slippage_price
        if abs(float(declared_rt) - actual_rt) > 1e-9:
            return rc.EVIDENCE_COST_IDENTITY_MISMATCH
    return None


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class RealEVDecisionEngine:
    """Real implementation of the `EVDecisionEngine` Protocol (`ev_engine.py`). Constructed FRESH per
    evaluation cycle by whoever calls `pipeline.run_cycle` (exactly how `MockEVDecisionEngine()` is
    constructed today) -- `market_state` and `catalog` are the SAME objects that cycle's Router already
    used, so this engine re-verifies against the real, current admission state rather than trusting
    anything the hypothesis itself claims.

    No public method here lets a caller define what strategy is admitted or its policy -- admission is
    100% delegated to `catalog: StrategyCatalog`, built once, elsewhere, exactly like `MockEVDecisionEngine`
    already assumes but never governs. This is deliberate: the whole point is that this class contains no
    strategy-specific logic and cannot be extended into one without editing this file itself (which is
    exactly the audited, versioned, source-controlled surface the mandate requires)."""

    catalog: StrategyCatalog
    market_state: MarketState
    cost_model: CostModel
    engine_version: str = REAL_EV_ENGINE_VERSION

    def __post_init__(self) -> None:
        _verify_ve_brain_installed()

    def decide(self, hypothesis: TradeHypothesis) -> EVDecision:
        # 1) ADMISSION -- re-resolve from AI-Trader's OWN catalog. Never trust hypothesis.strategy_id/
        #    strategy_version/strategy_config_fingerprint as authoritative on their own (mirrors
        #    decide_n6's "AUDIT, not authoritative" discipline, applied to this catalog instead).
        entry = self.catalog.lookup(hypothesis.strategy_id, hypothesis.strategy_version)
        if entry is None:
            return _no_trade(hypothesis, rc.UNKNOWN_STRATEGY)
        if not entry.enabled:
            return _no_trade(hypothesis, rc.STRATEGY_DISABLED)
        if hypothesis.strategy_config_fingerprint != entry.config_fingerprint:
            return _no_trade(hypothesis, rc.STRATEGY_POLICY_MISMATCH)
        if entry.status not in _REAL_TRADE_ELIGIBLE_STATUSES:
            return _no_trade(hypothesis, rc.NO_ELIGIBLE_STRATEGY)
        if entry.validation_provenance is None:  # re-verified, not just trusted from CatalogEntry.__post_init__
            return _no_trade(hypothesis, rc.STRATEGY_POLICY_MISMATCH)

        # 2) MarketState identity -- the hypothesis must have been produced from EXACTLY this cycle's
        #    MarketState, never a stale/replayed/mismatched one.
        if hypothesis.market_state_identity != market_state_identity(self.market_state):
            return _no_trade(hypothesis, rc.MARKET_STATE_MISMATCH)
        if self.market_state.atr is None or self.market_state.entry_price is None:
            return _no_trade(hypothesis, rc.MARKET_STATE_INVALID)

        # 3) N1 contract compatibility (mirrors decide_n6 step 0 exactly, same reason vocabulary)
        axes = self.market_state.axes
        if axes.n1_contract_version != ve_brain.N1_CONTRACT_VERSION:
            return _no_trade(hypothesis, rc.INCOMPATIBLE_N1_CONTRACT)

        # 4) geometry sanity -- NaN/inf on the two fields TradeHypothesis itself doesn't already gate
        #    (LONG/SHORT SL/TP ordering IS already enforced by TradeHypothesis.__post_init__ at
        #    construction time; re-checked here defensively is redundant, so only finiteness is new)
        for name, v in (("intended_entry", hypothesis.intended_entry), ("invalidation", hypothesis.invalidation)):
            if not (v == v and v not in (float("inf"), float("-inf"))):
                return _no_trade(hypothesis, rc.SCHEMA_VALIDATION_FAILED)

        # 5) expiry -- a hypothesis whose eligible_entry_timestamp has already passed this cycle's own
        #    market_timestamp is stale; never silently evaluated as if fresh.
        if hypothesis.eligible_entry_timestamp > self.market_state.market_timestamp:
            return _no_trade(hypothesis, rc.SCHEMA_VALIDATION_FAILED)  # not yet eligible -- premature, not expired
        if hypothesis.signal_timestamp > hypothesis.eligible_entry_timestamp:
            return _no_trade(hypothesis, rc.SCHEMA_VALIDATION_FAILED)  # signal after its own entry -- malformed

        # 6) target_kind translation -- TradeHypothesis carries a string exit_specification
        #    ("rr:3.0" | "time:40" | "none"); ve_brain.DecisionRequest wants target_kind/target_param.
        target_kind, target_param = _parse_exit_specification(hypothesis.exit_specification)
        if target_kind is None:
            return _no_trade(hypothesis, rc.SCHEMA_VALIDATION_FAILED)

        probability_inputs = _decode_probability_inputs(hypothesis.expected_edge)

        # 6.5) evidence identity binding (mandate VE-S5-REAL-EV-RUNTIME-PACKAGING-001 section 9) -- see
        # module docstring / _verify_evidence_identity's own docstring. Generic: no strategy-specific code.
        mismatch = _verify_evidence_identity(hypothesis, entry=entry, cost_model=self.cost_model)
        # Audit trail (mandate section 20/23): record WHICH evidence package was attempted regardless of
        # whether it ultimately decoded/passed -- deliberately independent of `mismatch`/decode success, so
        # a rejected evidence package is still traceable to its own identity, not silently anonymized.
        evidence_fp = str((hypothesis.expected_edge or {}).get("evidence_fingerprint") or "")
        if mismatch is not None:
            return _no_trade(hypothesis, mismatch, evidence_fingerprint=evidence_fp)

        regime_fp = ve_brain.regime_fingerprint(axes)
        data_id = ve_brain.data_identity(
            symbol=self.market_state.symbol, timeframe=self.market_state.timeframe,
            block_start=self.market_state.market_timestamp, block_end=self.market_state.market_timestamp,
            segment_id="live_shadow", manifest_hash="n/a-live-shadow-mode",
        )
        config_fp = ve_brain.decision_fingerprint(
            measurement_run_hash=entry.config_fingerprint, data_id=data_id,
            strategy_id=hypothesis.strategy_id, strategy_version=hypothesis.strategy_version,
            engine_version=REAL_EV_ENGINE_VERSION, measurement_contract_version=ve_brain.MEASUREMENT_CONTRACT_VERSION,
            n1_contract_version=axes.n1_contract_version, raw_axis_schema_version=axes.raw_axis_schema_version,
            router_version=_MY_ROUTER_VERSION, eligibility_policy_version=_MY_ELIGIBILITY_POLICY_VERSION,
        )

        req = ve_brain.DecisionRequest(
            contract_id=ve_brain.INPUT_CONTRACT_ID,
            strategy_id=hypothesis.strategy_id, strategy_version=hypothesis.strategy_version,
            validation_status=ve_brain.ValidationStatus.RATIFIED,  # AUDIT field only; see module docstring
            strategy_family=entry.risk_contract_reference, strategy_policy_fingerprint=entry.config_fingerprint,
            market_event_id=self.market_state.market_event_id, regime_fingerprint=regime_fp,
            market_state_ref=hypothesis.market_state_identity, regime_label=str(axes.structure) if axes.structure else None,
            bias_direction=self.market_state.router_bias_direction,
            market_map_available=True, levels_available=True, confirmation_available=True,
            entry_price=hypothesis.intended_entry, stop_price=hypothesis.invalidation,
            target_kind=target_kind, target_param=target_param, holding_window=hypothesis.max_hold,
            atr=self.market_state.atr, probability_inputs=probability_inputs,
            full_spread_price=self.cost_model.full_spread_price,
            entry_slippage_price=self.cost_model.entry_slippage_price,
            exit_slippage_price=self.cost_model.exit_slippage_price,
            symbol=self.market_state.symbol, timeframe=self.market_state.timeframe,
            block_start=self.market_state.market_timestamp, block_end=self.market_state.market_timestamp,
            segment_id="live_shadow", manifest_hash="n/a-live-shadow-mode",
            n1_contract_version=axes.n1_contract_version, raw_axis_schema_version=axes.raw_axis_schema_version,
            router_version=_MY_ROUTER_VERSION, eligibility_policy_version=_MY_ELIGIBILITY_POLICY_VERSION,
            measurement_contract_version=ve_brain.MEASUREMENT_CONTRACT_VERSION, configuration_fingerprint=config_fp,
        )
        try:
            ve_brain.validate_request(req)
        except ve_brain.SchemaValidationError:
            return _no_trade(hypothesis, rc.SCHEMA_VALIDATION_FAILED, evidence_fingerprint=evidence_fp)

        if req.holding_window < 1:
            return _no_trade(hypothesis, rc.SCHEMA_VALIDATION_FAILED, evidence_fingerprint=evidence_fp)
        if req.atr <= 0.0:
            return _no_trade(hypothesis, rc.SCHEMA_VALIDATION_FAILED, evidence_fingerprint=evidence_fp)

        # 7) the REAL, ratified EV computation -- reused verbatim, never reinvented.
        if probability_inputs is None:
            return _no_trade(hypothesis, rc.MISSING_PROBABILITY_INPUTS, evidence_fingerprint=evidence_fp)
        outcome = ve_brain.run_ev(req)
        if not outcome.enter:
            # ve_brain._ev_core.Reason's own .value strings (verified directly against source, not guessed):
            # "no_trade_ev_lcb_not_positive" (EV_LCB <= 0) / "no_trade_feasibility" (RR <= c/R) /
            # "no_trade_missing_input" (unreachable here -- already gated above by probability_inputs is
            # None). Neither raw string is in strategy_platform's registered vocabulary -- map, don't leak.
            mapped = rc.NEGATIVE_EXPECTED_VALUE if outcome.reason == "no_trade_ev_lcb_not_positive" else rc.INFEASIBLE_GEOMETRY
            return _no_trade(hypothesis, mapped, evidence_fingerprint=evidence_fp)

        return EVDecision(hypothesis=hypothesis, decision=TRADE_DECISION, reason_codes=(rc.REAL_EV_VALIDATED_EDGE,),
                           evidence_fingerprint=evidence_fp)


def _parse_exit_specification(spec: str) -> tuple[str | None, float | None]:
    """`TradeHypothesis.exit_specification` -> `ve_brain.DecisionRequest`'s (target_kind, target_param).
    `"rr:3.0"` -> `("rr", 3.0)`; `"none"` -> `("none", None)`; `"time:40"` has no price/rr target (a pure
    time-stop) -> `("none", None)`, feasibility then rests on holding_window alone, matching ve_brain's own
    `_rr_r_cost`'s documented behavior for a target-less request (rr=0.0, feasibility gate rejects it
    downstream rather than this function inventing a synthetic target). Anything unparseable -> (None, None)."""
    if spec == "none":
        return "none", None
    if spec.startswith("rr:"):
        try:
            return "rr", float(spec[3:])
        except ValueError:
            return None, None
    if spec.startswith("time:"):
        return "none", None
    return None, None
