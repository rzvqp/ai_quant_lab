"""Market Intelligence data structures -- Phase 7 Checkpoint 5.

Every reading is a frozen dataclass; every field is either a directly-observed value (never
fabricated) or ``None``/``UNKNOWN`` when the underlying data is unavailable -- the SAME "never
fabricate, honest None when data insufficient" discipline this codebase already established in
:mod:`ai_trader.strategy_health.metrics`/:mod:`ai_trader.shadow_evidence.research`. No field here is a
composite/weighted score across dimensions (that would cross into Strategy Health's own, separate,
unselected scoring methodology) -- ``ContextConfidence`` is the one explicit exception the CEO's own
Checkpoint 5 mandate calls for, and its own formula is a simple, disclosed average, never a black-box
composite (see :mod:`ai_trader.market_intelligence.confidence`).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TrendDirection(str, Enum):
    """Per-timeframe trend direction. ``FLAT`` is only ever produced on M15 (the one timeframe where
    a continuous EMA20/EMA50 spread is available to detect "no meaningful separation" -- H1/H4/D1
    expose only a boolean ``{tf}_trend_up`` flag, `market_scanner/features.py`'s own frozen output, so
    those timeframes are always ``UP``/``DOWN``/``UNKNOWN``, never ``FLAT``. This asymmetry is a
    disclosed property of the underlying feature set, not something this module invents to paper
    over)."""

    UP = "UP"
    DOWN = "DOWN"
    FLAT = "FLAT"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class TrendReading:
    """One timeframe's own trend reading. ``strength`` (the normalized EMA20/EMA50 spread,
    ``(ema20 - ema50) / close``) is only available on M15 -- ``None`` on H1/H4/D1, never fabricated
    from the boolean flag alone."""

    timeframe: str
    direction: TrendDirection
    strength: float | None


class VolatilityRegime(str, Enum):
    """ATR/ATR-moving-average ratio bands. Bounds mirror ``risk_manager``'s own documented
    "too dead / too wild" filter thresholds (``RISK_POLICY.md`` §5: outside [0.25x, 4x] denies a
    trade) for the OUTER (``EXTREME``) band -- reused for consistency across this codebase, never
    re-derived independently -- with two additional, purely descriptive inner bands
    (``LOW``/``NORMAL``/``HIGH``) this module adds for finer-grained description. This is a
    DESCRIPTIVE classification only; it never gates or denies anything (that remains
    ``risk_manager``'s own, unmodified, frozen responsibility)."""

    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    EXTREME = "EXTREME"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class VolatilityReading:
    atr: float | None
    atr_ma: float | None
    atr_ratio: float | None  # atr / atr_ma
    volatility_rank: float | None  # m_volrank -- Parkinson-based percentile rank, already computed
    regime: VolatilityRegime


class MomentumState(str, Enum):
    OVERBOUGHT = "OVERBOUGHT"
    OVERSOLD = "OVERSOLD"
    NEUTRAL = "NEUTRAL"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class MomentumReading:
    """``rate_of_change`` (``roc3``, a 3-bar rate of change) is only available on M15 -- the same
    disclosed asymmetry as :class:`TrendReading`'s own ``strength`` field."""

    timeframe: str
    rsi: float | None
    state: MomentumState
    rate_of_change: float | None


class StructureState(str, Enum):
    """Market structure state, in the standard sense this project's own strategy families already use
    informally (e.g. ``s11_structure_break_reversal_choch.py``'s own inline CHoCH logic) -- centralized
    here for the first time as a shared, generic primitive. ``BOS`` (break of structure): price closes
    beyond the prior swing extreme in the SAME direction as the prevailing structure. ``CHOCH`` (change
    of character): price closes beyond the prior swing extreme in the OPPOSITE direction, the first
    signal a trend may be reversing."""

    BULLISH_BOS = "BULLISH_BOS"
    BEARISH_BOS = "BEARISH_BOS"
    BULLISH_CHOCH = "BULLISH_CHOCH"
    BEARISH_CHOCH = "BEARISH_CHOCH"
    RANGING = "RANGING"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class SwingPoint:
    """One detected swing high/low -- a local extreme confirmed by ``fractal_bars`` bars on each
    side (Design choice, :mod:`ai_trader.market_intelligence.structure`)."""

    kind: str  # "HIGH" | "LOW"
    price: float
    as_of: int  # the swing bar's own ts_close


@dataclass(frozen=True, slots=True)
class StructureReading:
    timeframe: str
    state: StructureState
    last_swing_high: SwingPoint | None
    last_swing_low: SwingPoint | None


class LiquidityState(str, Enum):
    THIN = "THIN"
    NORMAL = "NORMAL"
    THICK = "THICK"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class LiquidityReading:
    """``volume``/``avg_volume`` are the SAME raw bar-volume signal ``harness.py::_build_risk_context``
    already uses as its own ``liquidity_proxy`` (``simulation/harness.py``) -- reused, not
    reinvented, extended here with a rolling-average comparison for a genuine "behavior" read rather
    than a single bar's own raw value."""

    volume: float | None
    avg_volume: float | None
    volume_ratio: float | None  # volume / avg_volume
    state: LiquidityState


class ExpansionState(str, Enum):
    COMPRESSED = "COMPRESSED"
    EXPANDING = "EXPANDING"
    NORMAL = "NORMAL"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class ExpansionReading:
    """Reuses ``compress``/``disp`` verbatim from `market_scanner/features.py` (already computed:
    ``compress`` = ATR below 0.8x its own moving average; ``disp`` = bar range above 1.5x ATR) --
    this module only labels the combined state, computing nothing new."""

    state: ExpansionState
    is_compressed: bool | None
    is_displacement: bool | None


@dataclass(frozen=True, slots=True)
class SessionReading:
    """Reuses the M15 session features verbatim (`market_scanner/session.py`'s own
    ``SessionEngine``, already computed) -- session name, position within the developing session,
    and gap, described together for the first time."""

    session_name: str | None
    bar_in_session: int | None
    inside_opening_range: bool | None
    above_session_vwap: bool | None
    gap: float | None


class AgreementLevel(str, Enum):
    STRONG = "STRONG"
    MODERATE = "MODERATE"
    WEAK = "WEAK"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class MultiTimeframeAgreement:
    """How many of the (up to 4) timeframes with a known trend direction agree with the majority.
    ``agreement_score`` is ``max(n_up, n_down) / n_known`` -- ``None`` if no timeframe has a known
    direction at all."""

    directions_by_timeframe: dict[str, TrendDirection]
    agreement_score: float | None
    level: AgreementLevel


@dataclass(frozen=True, slots=True)
class ContextConfidence:
    """A simple, disclosed, EXPLAINABLE composite -- see
    :mod:`ai_trader.market_intelligence.confidence` for the exact formula. Deliberately NOT a
    percentile-rank/PCA-derived score (that is Strategy Health's own separate methodology,
    ``PHASE_6_10_SHADOW_EVIDENCE_ARCHITECTURE_DESIGN.md`` §11, untouched here) -- every component
    below is named and independently inspectable, never hidden inside one opaque number."""

    score: float | None  # 0.0-1.0
    data_quality_ok: bool
    agreement_component: float | None
    volatility_penalty: float


@dataclass(frozen=True, slots=True)
class MarketIntelligenceSnapshot:
    """The complete, immutable Market Intelligence read for one symbol at one bar -- the single
    output of :func:`ai_trader.market_intelligence.engine.build_market_intelligence`, and the stable
    contract every future reasoning component (Edge Intelligence, Decision AI, ...) is designed to
    consume without needing to know how any individual reading was computed."""

    symbol: str
    as_of: int
    trend: dict[str, TrendReading]
    momentum: dict[str, MomentumReading]
    structure: StructureReading
    volatility: VolatilityReading
    liquidity: LiquidityReading
    expansion: ExpansionReading
    session: SessionReading
    multi_timeframe_agreement: MultiTimeframeAgreement
    confidence: ContextConfidence
