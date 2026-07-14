"""Abstract Data Source Adapter contract (``MARKET_SCANNER_ARCHITECTURE.md`` §11).

An adapter's only job is to produce a normalized, chronologically-ordered stream of
:class:`~ai_trader.market_scanner.types.RawBar` (and, optionally,
:class:`~ai_trader.market_scanner.types.RawTick` / :class:`~ai_trader.market_scanner.types.CalendarEvent`)
events. It never touches the scanner's internals directly; the orchestrator reads events from the
adapter and feeds them to the scanner's ``ingest_*``/``advance_clock`` API — this keeps every
adapter interchangeable (architecture §11: "swapping adapters changes the source, never the
``MarketContext`` shape").
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator

from ai_trader.market_scanner.types import CalendarEvent, Mode, RawBar, RawTick


class DataSourceAdapter(ABC):
    """Base class every concrete adapter implements."""

    @property
    @abstractmethod
    def mode(self) -> Mode:
        """Which :class:`~ai_trader.market_scanner.types.Mode` this adapter represents."""

    @property
    @abstractmethod
    def source_id(self) -> str:
        """An opaque, human-readable identifier for this adapter's concrete feed/dataset."""

    @abstractmethod
    def bars(self) -> Iterator[RawBar]:
        """Yield every bar this adapter provides, in non-decreasing ``ts_open`` order."""

    def ticks(self) -> Iterator[RawTick]:
        """Yield ticks, if this adapter provides any (optional feed; default: none)."""
        return iter(())

    def calendar_events(self) -> Iterator[CalendarEvent]:
        """Yield calendar events, if this adapter provides any (optional feed; default: none)."""
        return iter(())
