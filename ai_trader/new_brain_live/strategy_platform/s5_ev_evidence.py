"""S5 real EV runtime evidence artifact (mandate `VE-S5-REAL-EV-RUNTIME-PACKAGING-001`, section 6).

This is the "smallest immutable/versioned runtime evidence representation" the mandate asks for -- it
binds the Statistician/Red-Team-verified S5 EV aggregate evidence to the EXACT strategy/cost identity it
may be used by, so `RealEVDecisionEngine` can generically (no S5-specific code in `real_ev_engine.py`)
verify the binding before ever letting the evidence reach `ve_brain.run_ev`.

**Provenance chain** (mandate section 7 -- "must not reduce the evidence to anonymous numeric counters"):

- Independent S5 validation: `RT-ALPHA-S5-S20-CLEAN-INDEPENDENT-VALIDATION-001`, commit `633bd5da`,
  verdict `INDEPENDENT_VALIDATION_PASS` (gates A-H), frozen ledger sha256 `cd4e8d4a...` (295 trades).
- Red Team escrow aggregate extraction: `RT-S5-EV-ESCROW-AGGREGATE-EXTRACTION-001`, commit `8228ded`,
  artifact `S5_VALIDATED_EV_AGGREGATES_V1` -- aggregates-only, escrow boundary intact, raw ledger sealed
  in `escrow_red_team/` (never opened, never read by this codebase).
- Statistician EV evidence contract (pre-ledger): `e54a2a5` -- specified the canonical evidence schema
  this dataclass's field names are drawn from directly (`statistician/STAT_S5_CANONICAL_EV_EVIDENCE_
  REPORT.md` section 11's own YAML), and independently proved (section 5 of that report, an explicit
  arithmetic demonstration) that `n_target := round(WR * n)` would be a *>=3x* falsification --
  `WR=0.549` cannot substitute for `n_target` because most of S5's "winners" are positive-horizon exits,
  not target hits (`avg winner = +1.009 R` at a `rr3` geometry directly implies this).
- Statistician/Red-Team bracket reconciliation: RT found `n_stop=84` outside a naive `[99,147]` bracket
  (`8228ded`, `BRACKET_FAIL`); Statistician (`9cfcc5f`) proved the `>=99` floor was mis-derived from
  *total losing trades* (133), not *stop exits* specifically (`n_losers = n_stop + negative-horizon
  losers = 84 + 49 = 133` -- the floor was never violated, it was measuring the wrong count). Red Team
  re-stamped the artifact READY (`b4cb441`) with byte-identical economic values.

**What this artifact deliberately does NOT contain** (Statistician `e54a2a5` section 11's own explicit
list, honored here): no `win_rate`, no scalar `expected_edge`, no `avg_R`, no `PF`, no `maxDD`, no
confidence interval, and no individual ledger trade -- only the four raw counters `ve_brain.run_ev` itself
consumes (`n`, `n_target`, `n_horizon`, `sum_horizon_r`), plus the identity/provenance fields needed to
bind them to exactly one strategy and detect misattachment.

**Two fingerprints, both opaque, both copied byte-for-byte from Red Team's report, never recomputed**:
`evidence_fingerprint` (stable across status re-stamps, invariant to status/reconciliation metadata) and
`source_artifact_fingerprint` (the specific `READY` re-stamp's own fingerprint). Red Team's own restamp
report explicitly does not publish the canonicalization recipe (field order/serialization/separator
convention) for either -- this codebase therefore cannot independently recompute them and does not
attempt to; they are propagated as opaque, cited identity labels for audit provenance (mandate section 8),
not cryptographically re-verified against the fields below. This is a disclosed limitation, not a silent
gap -- see `VE_S5_REAL_EV_RUNTIME_PACKAGING_REPORT.md` section on tamper-test results for exactly what
this does and does not detect.
"""

from __future__ import annotations

import dataclasses
import math

EXPECTED_EDGE_SCHEMA_VERSION = "real-ev-expected-edge-v1"  # unchanged from VE-AI-TRADER-GENERIC-EV-AUTHORITY-001
EVIDENCE_SCHEMA_VERSION = "s5-ev-evidence-v1"  # matches the Statistician's own `artifact_version` (e54a2a5)


class EVEvidenceIdentityError(ValueError):
    """Raised at construction time if this artifact's own fields are not jointly self-consistent -- fail
    closed before the module even finishes importing, never a bad artifact silently reaching a decision."""


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class ValidatedEVEvidence:
    """Immutable, versioned runtime evidence artifact. One instance per validated strategy's economic
    evidence package -- constructed once, as a module-level constant, never mutated, never constructed
    from caller-supplied values (mirrors `_canonical_catalog.py`'s own "consumer can REQUEST, never
    DEFINE" discipline, applied to evidence instead of strategy identity)."""

    schema_version: str

    # ── strategy identity binding (mandate section 9) ──
    strategy_id: str
    strategy_version: str
    implementation_fingerprint: str
    config_fingerprint: str
    alpha_candidate: str
    representative: str

    # ── validation identity (mandate section 7) -- audit provenance, not independently re-verifiable
    # against a live registry (there isn't one); trustworthiness comes from being a cited, source-
    # controlled constant, exactly like `CatalogEntry.validation_provenance` already is elsewhere. ──
    validation_mandate: str
    validation_commit: str
    validation_verdict: str
    validation_ledger_sha256: str
    validation_ledger_n: int

    # ── evidence population identity (mandate section 6) ──
    population_id: str
    population_ohlc_sha256: str
    population_timeline_sha256: str
    population_bars: int

    # ── cost identity (mandate section 10) -- the ECONOMICS this evidence assumes; RealEVDecisionEngine
    # verifies the actual runtime CostModel's summed price fields match round_trip_price, since the
    # validation-side spread was folded into slippage (decomposition not identified, only the SUM is). ──
    cost_model_id: str
    cost_scenario: str  # "BASE" | "STRESS" -- declared, never assumed (Statistician e54a2a5 section 9)
    round_trip_price: float

    # ── the actual REAL EV evidence -- the ONLY fields `ve_brain.run_ev` ever consumes (via
    # `_decode_probability_inputs`); n_stop is intentionally NOT a stored field, see the n_stop property. ──
    n: int
    n_target: int
    n_horizon: int
    sum_horizon_r: float
    credibility: float

    # ── Red Team fingerprints (mandate section 8) -- opaque, cited, see module docstring ──
    evidence_fingerprint: str
    source_artifact_fingerprint: str
    source_artifact_id: str
    source_commit: str

    def __post_init__(self) -> None:
        for name in ("strategy_id", "strategy_version", "implementation_fingerprint", "config_fingerprint",
                     "validation_mandate", "validation_commit", "validation_verdict", "validation_ledger_sha256",
                     "population_id", "population_ohlc_sha256", "population_timeline_sha256",
                     "cost_model_id", "cost_scenario", "evidence_fingerprint", "source_artifact_fingerprint",
                     "source_artifact_id", "source_commit"):
            if not getattr(self, name):
                raise EVEvidenceIdentityError(f"ValidatedEVEvidence.{name} must not be empty")
        if self.cost_scenario not in ("BASE", "STRESS"):
            raise EVEvidenceIdentityError(f"cost_scenario must be BASE or STRESS, got {self.cost_scenario!r}")
        if self.n < 0 or self.n_target < 0 or self.n_horizon < 0:
            raise EVEvidenceIdentityError("n/n_target/n_horizon must be non-negative")
        if self.n_target + self.n_horizon > self.n:
            raise EVEvidenceIdentityError(
                f"impossible count geometry: n_target({self.n_target}) + n_horizon({self.n_horizon}) "
                f"> n({self.n}) -- would imply a negative n_stop")
        if not math.isfinite(self.sum_horizon_r):
            raise EVEvidenceIdentityError(f"sum_horizon_r must be finite, got {self.sum_horizon_r!r}")
        if not (0.0 < self.credibility < 1.0):
            raise EVEvidenceIdentityError(f"credibility must be in (0,1), got {self.credibility!r}")
        if not (self.round_trip_price == self.round_trip_price and self.round_trip_price >= 0.0
                and self.round_trip_price != float("inf")):
            raise EVEvidenceIdentityError(f"round_trip_price must be finite and non-negative, got {self.round_trip_price!r}")

    @property
    def n_stop(self) -> int:
        """Materialized for audit only (mandate section 6) -- ALWAYS derived, never stored, so it can
        never independently drift from n/n_target/n_horizon."""
        return self.n - self.n_target - self.n_horizon

    def to_expected_edge(self) -> dict[str, float | str | None]:
        """Renders into `TradeHypothesis.expected_edge`'s existing, frozen `real-ev-expected-edge-v1`
        shape (mandate section 11 -- "map into the EXISTING empirical-Bayes input contract", not a new
        one) plus additive, OPTIONAL identity-binding keys `RealEVDecisionEngine` cross-checks generically
        against whatever `CatalogEntry`/`CostModel` it already has -- a payload lacking these optional
        keys (e.g. the pre-existing fixture's) is unaffected and validates exactly as it always has."""
        return {
            "edge_schema": EXPECTED_EDGE_SCHEMA_VERSION,
            "n": float(self.n), "n_target": float(self.n_target), "n_horizon": float(self.n_horizon),
            "sum_horizon_r": self.sum_horizon_r, "credibility": self.credibility,
            "evidence_strategy_id": self.strategy_id,
            "evidence_strategy_version": self.strategy_version,
            "evidence_implementation_fingerprint": self.implementation_fingerprint,
            "evidence_config_fingerprint": self.config_fingerprint,
            "evidence_cost_model_id": self.cost_model_id,
            "evidence_round_trip_price": self.round_trip_price,
            "evidence_fingerprint": self.evidence_fingerprint,
            "source_artifact_fingerprint": self.source_artifact_fingerprint,
        }


#: The S5 evidence package, READY_FOR_RUNTIME_PACKAGING per Red Team `b4cb441`. Every value below is
#: copied byte-for-byte from the cited source reports -- none derived, estimated, or approximated (mandate
#: CEO directive: VERIFIED_AGGREGATE_EVIDENCE_ONLY / NO_SYNTHETIC_PROBABILITIES).
S5_REAL_EV_EVIDENCE_V1 = ValidatedEVEvidence(
    schema_version=EVIDENCE_SCHEMA_VERSION,
    strategy_id="s5_c_2d587447_opening_range_breakout_long",
    strategy_version="rep_7472f3d412f2",
    implementation_fingerprint="s5_opening_range_breakout.py-impl-v1",
    config_fingerprint=(
        "S5-frozen-spec:session=ny,mode=breakout,side=up,stop=or_opp,exit=rr3;"
        "tick=0.01;or_bars=4;entry_window_bis=4-20;hold_bars=48;rr=3.0"
    ),
    alpha_candidate="C_2d587447",
    representative="7472f3d412f2",
    validation_mandate="RT-ALPHA-S5-S20-CLEAN-INDEPENDENT-VALIDATION-001",
    validation_commit="633bd5da",
    validation_verdict="INDEPENDENT_VALIDATION_PASS",
    validation_ledger_sha256="cd4e8d4aae0104cd1041898cf136917b9ec3194c343ba6840fab0bdb7831e1d7",
    validation_ledger_n=295,
    population_id="S5_S20_CLEAN_VALIDATION_POPULATION",
    population_ohlc_sha256="bac65b1a8840a0b82a384aa86bfafab9f38f36abb03cd030c6f7afdfbc457ea1",
    population_timeline_sha256="4c9ce7b7f245bb9a375edaec42bcf3355a78ba99d2dd2fbf8d897ecf2ed4728a",
    population_bars=52572,
    cost_model_id="AI_TRADER_SHADOW_COST_MODEL_v1",
    cost_scenario="STRESS",  # the more conservative of the two ratified scenarios (BASE=0.05, STRESS=0.24)
    round_trip_price=0.24,
    n=295, n_target=15, n_horizon=196, sum_horizon_r=102.2125344478, credibility=0.80,
    evidence_fingerprint="9ca6e2bd9884389b822518bed2341f7273288018187974c468016b20070593b4",
    source_artifact_fingerprint="ff1384a2fba6d37c859613887d89837bdd11a94614ade0a1ed034176653dddd4",
    source_artifact_id="S5_VALIDATED_EV_AGGREGATES_V1",
    source_commit="b4cb441",
)
