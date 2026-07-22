"""Controlled vocabularies for Context Memory -- Phase 7 Checkpoint 9.

IMPLEMENTATION CHOICE (Checkpoint 9 §B, a required, disclosed design decision): every controlled
vocabulary this package needs that ORIGINATES in an upstream package (Market Intelligence's regime
enums, Edge Intelligence's ``EdgeState``, ``market_scanner``'s ``DataQualityLevel``) is reproduced here
as a LOCAL, string-valued ``Enum`` with IDENTICAL member values -- never imported as a live dependency on
``market_intelligence``/``edge_intelligence``/``market_scanner``. This is deliberately the stronger of
the two options the checkpoint authorization offered ("depend on the stable public enum type" vs. "store
a canonical serialized representation with an explicit source-schema version"): a canonical serialized
representation was chosen because (1) it gives Context Memory a genuinely ZERO-import dependency on
every upstream intelligence package, satisfying "the package must remain passive and independently
testable" more strongly than a one-directional import would; (2) a persisted record's own interpretability
must never depend on an upstream enum's SHAPE remaining unchanged forever -- a canonical string value
paired with an explicit ``SchemaVersion`` (see ``CONTEXT_MEMORY_SCHEMA_VERSION`` usage throughout
``contracts.py``) stays interpretable even if, say, ``market_intelligence.types.TrendDirection`` gains or
loses a member in some future checkpoint; (3) it matches this repository's own already-established
precedent of a caller-adapted LOCAL type rather than a live cross-package import
(``ai_trader.decision_intelligence.types.ResearchStats`` deliberately does not import
``ai_trader.shadow_evidence.types.StrategyResearchSummary`` for the identical reason).

Every enum below is validated at construction time in ``contracts.py`` (an unrecognized string is
rejected, never silently accepted) -- this is strict validation of a controlled vocabulary, not a loose
string field.
"""

from __future__ import annotations

from enum import Enum


# ---------------------------------------------------------------------------------------------------
# Mirrors of Market Intelligence's own regime vocabulary (values identical to
# ai_trader.market_intelligence.types as of market_intelligence_schema_version "mi-v1" -- see
# contracts.py::MARKET_INTELLIGENCE_SCHEMA_VERSION). A future Market Intelligence schema change requires
# a NEW schema version constant, never an in-place edit of these values.
# ---------------------------------------------------------------------------------------------------


class ContextTrendDirection(str, Enum):
    UP = "UP"
    DOWN = "DOWN"
    FLAT = "FLAT"
    UNKNOWN = "UNKNOWN"


class ContextStructureState(str, Enum):
    BULLISH_BOS = "BULLISH_BOS"
    BEARISH_BOS = "BEARISH_BOS"
    BULLISH_CHOCH = "BULLISH_CHOCH"
    BEARISH_CHOCH = "BEARISH_CHOCH"
    RANGING = "RANGING"
    UNKNOWN = "UNKNOWN"


class ContextMomentumState(str, Enum):
    OVERBOUGHT = "OVERBOUGHT"
    OVERSOLD = "OVERSOLD"
    NEUTRAL = "NEUTRAL"
    UNKNOWN = "UNKNOWN"


class ContextVolatilityRegime(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    EXTREME = "EXTREME"
    UNKNOWN = "UNKNOWN"


class ContextLiquidityState(str, Enum):
    THIN = "THIN"
    NORMAL = "NORMAL"
    THICK = "THICK"
    UNKNOWN = "UNKNOWN"


class ContextExpansionState(str, Enum):
    COMPRESSED = "COMPRESSED"
    EXPANDING = "EXPANDING"
    NORMAL = "NORMAL"
    UNKNOWN = "UNKNOWN"


class ContextAgreementLevel(str, Enum):
    STRONG = "STRONG"
    MODERATE = "MODERATE"
    WEAK = "WEAK"
    UNKNOWN = "UNKNOWN"


class ContextDataQualityState(str, Enum):
    """Mirrors ``ai_trader.market_scanner.types.DataQualityLevel``."""

    OK = "OK"
    DEGRADED = "DEGRADED"
    STALE = "STALE"
    INSUFFICIENT = "INSUFFICIENT"


class ContextEdgeStatus(str, Enum):
    """Mirrors ``ai_trader.edge_intelligence.types.EdgeState``. A :class:`~ai_trader.context_memory.
    contracts.PresentEdgeReference` is only ever constructed for an edge Edge Intelligence classified
    PRESENT, so this value is trivially always ``PRESENT`` in Checkpoint 9's own usage -- stored
    explicitly anyway (rather than assumed/omitted) so the record is self-describing and this type
    remains directly reusable if a future checkpoint ever needs to record POSSIBLE/ABSENT edges too."""

    PRESENT = "PRESENT"
    POSSIBLE = "POSSIBLE"
    ABSENT = "ABSENT"


# ---------------------------------------------------------------------------------------------------
# Vocabularies genuinely new to Context Memory (no upstream equivalent exists).
# ---------------------------------------------------------------------------------------------------


class OutcomeStatus(str, Enum):
    """The resolution state of one Outcome record (Checkpoint 8 §4.5, Checkpoint 9 §G). Unifies the
    CEO's own "evidence resolution state" and "outcome resolution state" vocabulary requests -- Checkpoint
    8's design treats "evidence" and "outcome" as the same underlying record (one row per
    observation/edge/horizon), so one status vocabulary serves both names."""

    PENDING = "PENDING"
    RESOLVED = "RESOLVED"
    INVALID = "INVALID"
    UNAVAILABLE = "UNAVAILABLE"


class SourceType(str, Enum):
    """Where an Outcome's own normalized result came from (Checkpoint 8 §4.3's two deliberately-separate
    horizon families). Outcome CALCULATION is explicitly out of scope for Checkpoint 9 -- this
    vocabulary exists so the *contract* can label provenance once a future checkpoint computes one.

    ``REAL_PORTFOLIO_LEDGER`` added per the Learning/Research Feedback Normative Model (ADR
    ``ADR_OUTCOME_IDENTITY_VS_SOURCE.md``, Option B, CEO-approved): an open, growing "where from" axis,
    orthogonal to :class:`OutcomeKind`'s closed "what" axis below."""

    PRICE_ONLY = "PRICE_ONLY"
    SHADOW_EVIDENCE_ADAPTER = "SHADOW_EVIDENCE_ADAPTER"
    REAL_PORTFOLIO_LEDGER = "REAL_PORTFOLIO_LEDGER"


class OutcomeKind(str, Enum):
    """What an Outcome represents (the Learning/Research Feedback Normative Model's "what" axis,
    orthogonal to :class:`SourceType`'s own "where from" axis -- ADR ``ADR_OUTCOME_IDENTITY_VS_SOURCE.md``,
    Option B, CEO-approved). Small, closed, stable: expected to remain exactly these two members for the
    foreseeable future. Phase A of the implementation adds this type only; wiring it onto :class:`~ai_trader.
    context_memory.contracts.Outcome` itself is a separate, later phase."""

    STRATEGY = "STRATEGY"
    PORTFOLIO = "PORTFOLIO"


class ContextRiskDecision(str, Enum):
    """Local mirror of ``ai_trader.risk_manager.types.Decision``, per this module's own established
    "zero import dependency on upstream vocab" convention (see module docstring). Backs
    :class:`~ai_trader.context_memory.contracts.OperationalMetadata`, a diagnostic-only companion type --
    never a learning target, never fed into :mod:`~ai_trader.context_memory.evidence`."""

    ALLOW = "ALLOW"
    DENY = "DENY"


class HorizonUnit(str, Enum):
    """The unit an Outcome's own ``horizon`` is expressed in. IMPLEMENTATION CHOICE: only ``BARS`` is
    defined -- Checkpoint 8's own accepted design only ever discussed base-timeframe bar-count horizons;
    a speculative second unit (e.g. seconds/hours) is deliberately NOT added until a real, concrete need
    for one exists (the CEO's own "do not introduce speculative categories" instruction, applied
    literally)."""

    BARS = "BARS"
