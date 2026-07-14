"""Replay Data Source Adapter — streams a pre-built, ordered sequence of historical bars.

Covers both the ``replay`` and ``lab-parity`` modes (architecture §11): the mechanics are
identical; only the data handed to the constructor differs (arbitrary historical bars vs. the
exact market data used in research). This module does not read any file itself — callers construct
the ``bars``/``ticks``/``calendar_events`` sequences (e.g. from their own CSV loader) and pass them
in, keeping this adapter fully decoupled from any particular data source or file format.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator

from ai_trader.market_scanner.adapters.base import DataSourceAdapter
from ai_trader.market_scanner.types import CalendarEvent, Mode, RawBar, RawTick


class ReplayAdapter(DataSourceAdapter):
    """Deterministic, in-memory replay of a pre-ordered bar (and optional tick/calendar) sequence.

    Args:
        bars: an iterable of :class:`RawBar`, already sorted by ``ts_open`` (ascending). Not
            re-sorted here — the caller owns ordering, matching "streamed in order" (architecture
            §11); this keeps the adapter a pure pass-through with no hidden reordering logic.
        source_id: an opaque identifier for this dataset (echoed in ``MarketContext.meta.source``).
        mode: :attr:`Mode.REPLAY` (default) or :attr:`Mode.LAB_PARITY`.
        ticks: an optional iterable of :class:`RawTick`, already ordered by ``ts``.
        calendar_events: an optional iterable of :class:`CalendarEvent`.
    """

    def __init__(
        self,
        bars: Iterable[RawBar],
        source_id: str = "replay",
        mode: Mode = Mode.REPLAY,
        ticks: Iterable[RawTick] = (),
        calendar_events: Iterable[CalendarEvent] = (),
    ) -> None:
        self._bars = list(bars)
        self._ticks = list(ticks)
        self._calendar_events = list(calendar_events)
        self._source_id = source_id
        self._mode = mode

    @property
    def mode(self) -> Mode:
        return self._mode

    @property
    def source_id(self) -> str:
        return self._source_id

    def bars(self) -> Iterator[RawBar]:
        yield from self._bars

    def ticks(self) -> Iterator[RawTick]:
        yield from self._ticks

    def calendar_events(self) -> Iterator[CalendarEvent]:
        yield from self._calendar_events
