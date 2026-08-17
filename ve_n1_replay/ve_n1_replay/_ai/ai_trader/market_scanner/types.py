"""Core value types for the Market Scanner.

These mirror ``MARKET_SCANNER_API.md`` §0 exactly. All are plain, immutable dataclasses (value
objects) — no behaviour, no hidden state. Timestamps are always UTC epoch seconds
(``MARKET_SCANNER_ARCHITECTURE.md`` §4.1). Nothing here reads or depends on Research Lab code.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum

from ai_trader.market_scanner.exceptions import InvalidBarError, InvalidTickError


class Mode(str, Enum):
    """The scanner's data-source mode, echoed in every ``MarketContext.meta.mode``."""

    LIVE = "LIVE"
    REPLAY = "REPLAY"
    LAB_PARITY = "LAB_PARITY"


class ImpactLevel(str, Enum):
    """Calendar-event impact level (``MARKET_CONTEXT_SCHEMA.json#/properties/calendar``)."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class DataQualityLevel(str, Enum):
    """Overall data-quality classification for a ``MarketContext`` or a single timeframe."""

    OK = "OK"
    DEGRADED = "DEGRADED"
    STALE = "STALE"
    INSUFFICIENT = "INSUFFICIENT"


class SufficiencyLevel(str, Enum):
    """Whether a ``MarketContext`` satisfies the aggregated strategy requirements."""

    SUFFICIENT = "SUFFICIENT"
    PARTIAL = "PARTIAL"
    INSUFFICIENT = "INSUFFICIENT"


class SessionName(str, Enum):
    """Session tag, matching the frozen research UTC-hour mapping (parity requirement, §4.3)."""

    ASIA = "asia"
    LONDON = "london"
    NY = "ny"
    LATE = "late"


def _is_finite_number(value: float) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


@dataclass(frozen=True, slots=True)
class SymbolMeta:
    """Static reference data for one tracked instrument (``MARKET_SCANNER_API.md`` §0).

    Attributes:
        symbol: the instrument identifier, e.g. ``"XAUUSD"``.
        tick_size: the minimum price increment (must be strictly positive).
        point_value: the monetary value of one price point per unit size (must be strictly positive).
        price_precision: number of decimal digits used when a price is rendered for display.
        session_anchor: the session-anchoring convention this scanner instance uses, e.g.
            ``"NY_17:00"``. Must match the research convention for parity (architecture §10).
        trading_hours: optional free-text description of the instrument's trading hours.
    """

    symbol: str
    tick_size: float
    point_value: float
    price_precision: int
    session_anchor: str = "NY_17:00"
    trading_hours: str | None = None

    def __post_init__(self) -> None:
        if not self.symbol:
            raise ValueError("SymbolMeta.symbol must be non-empty")
        if not (_is_finite_number(self.tick_size) and self.tick_size > 0):
            raise ValueError(f"SymbolMeta.tick_size must be > 0, got {self.tick_size!r}")
        if not (_is_finite_number(self.point_value) and self.point_value > 0):
            raise ValueError(f"SymbolMeta.point_value must be > 0, got {self.point_value!r}")
        if self.price_precision < 0:
            raise ValueError("SymbolMeta.price_precision must be >= 0")


@dataclass(frozen=True, slots=True)
class RawBar:
    """A single OHLCV bar as normalized by the Data Source Adapter, before the scanner ingests it.

    Attributes:
        symbol: the instrument this bar belongs to.
        timeframe: the canonical timeframe code, e.g. ``"M15"``.
        ts_open: UTC epoch seconds of the bar's open.
        ts_close: UTC epoch seconds of the bar's close (``ts_open + timeframe_seconds``).
        open, high, low, close: OHLC prices.
        volume: traded volume, or ``None`` if unavailable.
        complete: ``False`` marks a still-forming bar (its OHLC may still change); ``True`` marks a
            closed, final bar. Only complete bars ever enter a rolling window (architecture §8).
    """

    symbol: str
    timeframe: str
    ts_open: int
    ts_close: int
    open: float
    high: float
    low: float
    close: float
    volume: float | None
    complete: bool

    def __post_init__(self) -> None:
        if not self.symbol:
            raise InvalidBarError("RawBar.symbol must be non-empty")
        if self.ts_close <= self.ts_open:
            raise InvalidBarError(
                f"RawBar.ts_close ({self.ts_close}) must be > ts_open ({self.ts_open})"
            )
        for name, value in (("open", self.open), ("high", self.high), ("low", self.low), ("close", self.close)):
            if not _is_finite_number(value):
                raise InvalidBarError(f"RawBar.{name} must be a finite number, got {value!r}")
        if self.high < self.low:
            raise InvalidBarError(f"RawBar.high ({self.high}) must be >= low ({self.low})")
        if not (self.low <= self.open <= self.high):
            raise InvalidBarError(f"RawBar.open ({self.open}) must be within [low, high]")
        if not (self.low <= self.close <= self.high):
            raise InvalidBarError(f"RawBar.close ({self.close}) must be within [low, high]")
        if self.volume is not None:
            if not _is_finite_number(self.volume) or self.volume < 0:
                raise InvalidBarError(f"RawBar.volume must be a finite number >= 0, got {self.volume!r}")

    @property
    def available_at(self) -> int:
        """The lookahead-safe availability timestamp of this bar: its close (architecture §9)."""
        return self.ts_close


@dataclass(frozen=True, slots=True)
class RawTick:
    """An optional tick/quote update (``MARKET_SCANNER_API.md`` §0).

    At least one of ``bid``/``ask``/``last`` must be provided.
    """

    symbol: str
    ts: int
    bid: float | None = None
    ask: float | None = None
    last: float | None = None
    volume: float | None = None

    def __post_init__(self) -> None:
        if not self.symbol:
            raise InvalidTickError("RawTick.symbol must be non-empty")
        if self.bid is None and self.ask is None and self.last is None:
            raise InvalidTickError("RawTick must carry at least one of bid/ask/last")
        for name, value in (("bid", self.bid), ("ask", self.ask), ("last", self.last)):
            if value is not None and not _is_finite_number(value):
                raise InvalidTickError(f"RawTick.{name} must be a finite number, got {value!r}")
        if self.bid is not None and self.ask is not None and self.bid > self.ask:
            raise InvalidTickError(f"RawTick.bid ({self.bid}) must be <= ask ({self.ask})")

    @property
    def mid(self) -> float | None:
        """The mid price, if both sides of the quote are known."""
        if self.bid is not None and self.ask is not None:
            return (self.bid + self.ask) / 2.0
        return self.last


@dataclass(frozen=True, slots=True)
class CalendarEvent:
    """An optional economic/holiday calendar event (``MARKET_SCANNER_API.md`` §0)."""

    ts: int
    impact: ImpactLevel
    kind: str | None = None
    symbol: str | None = None


@dataclass(slots=True)
class TimeframeRequirement:
    """One strategy's requirement for a single timeframe, prior to aggregation."""

    fields: frozenset[str]
    lookback_bars: int
    optional_fields: frozenset[str] = field(default_factory=frozenset)


@dataclass(slots=True)
class Requirements:
    """The aggregated context requirement the Strategy Manager registers with the scanner
    (``MARKET_SCANNER_API.md`` §0 / §1 ``register_requirements``).

    Attributes:
        timeframes: the union of timeframes any active strategy needs.
        fields_by_timeframe: per timeframe, the union of REQUIRED feature names.
        lookback_by_timeframe: per timeframe, the max lookback (in bars) any strategy needs.
        symbols: the symbols in scope.
        optional_fields_by_timeframe: per timeframe, feature names that are nice-to-have but whose
            absence must not block a strategy (mirrors the Strategy Manager's Context Aggregator).
    """

    timeframes: frozenset[str]
    fields_by_timeframe: dict[str, frozenset[str]]
    lookback_by_timeframe: dict[str, int]
    symbols: frozenset[str]
    optional_fields_by_timeframe: dict[str, frozenset[str]] = field(default_factory=dict)


@dataclass(slots=True)
class CompatibilityReport:
    """The result of :meth:`MarketScanner.register_requirements`."""

    satisfiable: bool
    missing_fields: list[str]
    missing_timeframes: list[str]
    feature_dictionary_version: str


@dataclass(slots=True)
class WarmupStatus:
    """The result of :meth:`MarketScanner.warmup_status`."""

    satisfied: bool
    by_timeframe: dict[str, bool]
    bars_needed: dict[str, int]


@dataclass(slots=True)
class ScannerHealth:
    """The result of :meth:`MarketScanner.health` (``MARKET_SCANNER_API.md`` §4)."""

    state: str
    feeds: list[str]
    sync_ok: bool
    gaps_open: int
    staleness_ms_by_symbol: dict[str, int]
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ProvidedFeatures:
    """The result of :meth:`MarketScanner.get_provided_features`."""

    feature_dictionary_version: str
    fields_by_timeframe: dict[str, frozenset[str]]


@dataclass(slots=True)
class ScannerVersions:
    """The result of :meth:`MarketScanner.versions`."""

    context_schema_version: str
    feature_dictionary_version: str
    scanner_version: str
    interface_version: str
