"""Configuration objects for the Market Scanner.

A single :class:`ScannerConfig` instance is supplied to :meth:`MarketScanner.configure` (or the
constructor) and never mutated afterwards — this keeps context assembly a pure function of
``(ingested data, clock, configuration)`` as required by ``MARKET_SCANNER_API.md`` ("Purity").
"""

from __future__ import annotations

from dataclasses import dataclass, field

#: The versions this build of the scanner emits/targets (architecture §12). Bump deliberately.
CONTEXT_SCHEMA_VERSION = "1.0.0"
FEATURE_DICTIONARY_VERSION = "1.0.0"
SCANNER_VERSION = "1.0.0"
DEFAULT_INTERFACE_VERSION = "1.0.0"

#: Default base heartbeat timeframe (architecture §3).
DEFAULT_BASE_TIMEFRAME = "M15"

#: Default set of higher-timeframe context the Strategy Library's families reference.
DEFAULT_CONTEXT_TIMEFRAMES: tuple[str, ...] = ("H1", "H4", "D1", "W1")

#: Fixed research-parity indicator windows (architecture §4.5 / §10 parity requirement). These are
#: NOT tunable per run — changing them would silently break parity with the Strategy Library's
#: researched metrics, so they are module constants, not config fields.
ATR_WINDOW = 14
ATR_MA_WINDOW = 50
EMA_FAST_SPAN = 20
EMA_SLOW_SPAN = 50
RSI_WINDOW = 14
SMA_WINDOW = 20
STD_WINDOW = 20
VOLRANK_WINDOW = 60
COMPRESS_RATIO = 0.8
DISPLACEMENT_ATR_MULT = 1.5
OPENING_RANGE_BARS = 4


@dataclass(slots=True)
class ScannerConfig:
    """Immutable-by-convention configuration for one :class:`MarketScanner` instance.

    Attributes:
        interface_version: the Strategy Interface version this scanner build serves.
        staleness_threshold_ms: beyond this age (now - last bar close), a timeframe's
            ``data_quality`` is marked ``STALE`` rather than ``OK``/``DEGRADED``.
        history_buffer_bars: how many COMPLETE bars are retained per (symbol, timeframe) rolling
            window, on top of the aggregated max lookback — the warmup margin from architecture §3.
        max_gap_bars_before_degraded: a single-timeframe gap of at least this many missing bars
            marks that timeframe's data_quality ``DEGRADED`` for the current cycle.
        weekend_gap_atr_threshold: a session-open gap whose magnitude exceeds this multiple of the
            base-timeframe ATR is flagged ``is_weekend_gap`` (architecture §7 / sequence §5). This
            is advisory bookkeeping only, distinct from the mechanical Friday/Monday day-of-week
            check which is unconditional.
        event_flag_window_seconds: calendar events within this many seconds of ``as_of`` (past or
            future) are surfaced in ``calendar.event_flags``.
        strict_schema_validation: when ``True`` (the default; production posture), every emitted
            ``MarketContext`` is validated against the JSON Schema before being returned, and a
            failure raises :class:`~ai_trader.market_scanner.exceptions.ContextValidationError`
            instead of returning a malformed object (architecture §14, API §5 contract #4).
    """

    interface_version: str = DEFAULT_INTERFACE_VERSION
    base_timeframe: str = DEFAULT_BASE_TIMEFRAME
    staleness_threshold_ms: int = 5 * 60 * 1000
    history_buffer_bars: int = 64
    max_gap_bars_before_degraded: int = 1
    weekend_gap_atr_threshold: float = 0.5
    event_flag_window_seconds: int = 30 * 60
    strict_schema_validation: bool = True
    context_schema_version: str = CONTEXT_SCHEMA_VERSION
    feature_dictionary_version: str = FEATURE_DICTIONARY_VERSION
    scanner_version: str = SCANNER_VERSION

    def __post_init__(self) -> None:
        if self.staleness_threshold_ms <= 0:
            raise ValueError("staleness_threshold_ms must be > 0")
        if self.history_buffer_bars < 1:
            raise ValueError("history_buffer_bars must be >= 1")
        if self.max_gap_bars_before_degraded < 1:
            raise ValueError("max_gap_bars_before_degraded must be >= 1")


@dataclass(slots=True)
class AdapterConfig:
    """Selects and configures a Data Source Adapter (architecture §11).

    Attributes:
        mode: which adapter to use.
        source_id: an opaque, human-readable identifier for the concrete feed/dataset (echoed in
            ``MarketContext.meta.source`` for audit — never a research-artifact handle).
        options: adapter-specific options (e.g. a replay adapter's ordering/backfill settings).
    """

    mode: str  # one of types.Mode values; kept as str to avoid a circular import at class body eval
    source_id: str = "unspecified"
    options: dict[str, object] = field(default_factory=dict)
