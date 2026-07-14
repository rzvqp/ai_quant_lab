"""Session Engine — session tagging, block ids, developing high/low, opening range, VWAP.

Per ``MARKET_SCANNER_ARCHITECTURE.md`` §6 and §4.3 (parity requirement): sessions use the frozen
research UTC-hour mapping (``hour<8`` asia, ``hour<13`` london, ``hour<21`` ny, else late), and the
session/day "block" id increments every time the session tag changes on consecutive base bars —
this mirrors the frozen research engine's ``blk`` column exactly (one instance runs per symbol).

Everything here is computed strictly from bars already ingested, in order; nothing here is
lookahead — developing highs/lows and the opening range only ever reflect bars *strictly before*
the current one, and "previous session" values only update once a session has fully closed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ai_trader.market_scanner.config import OPENING_RANGE_BARS
from ai_trader.market_scanner.types import SessionName


def session_name_for_hour(hour: int) -> SessionName:
    """Map a UTC hour-of-day (0-23) to the frozen research session tag."""
    if hour < 8:
        return SessionName.ASIA
    if hour < 13:
        return SessionName.LONDON
    if hour < 21:
        return SessionName.NY
    return SessionName.LATE


@dataclass(slots=True, frozen=True)
class OpeningRange:
    """The session's opening range, formed from its first ``OPENING_RANGE_BARS`` bars."""

    high: float | None
    low: float | None
    formed: bool


@dataclass(slots=True, frozen=True)
class SessionSnapshot:
    """Everything the Session Engine knows as of the bar just ingested."""

    name: SessionName
    block_id: int
    bar_in_session: int
    session_open_ts: int
    session_high: float | None
    session_low: float | None
    opening_range: OpeningRange
    is_new_session: bool
    prev_session_high: float | None
    prev_session_low: float | None
    prev_session_close: float | None
    vwap: float | None

    def to_schema_dict(self) -> dict[str, Any]:
        """Render as the ``session`` object from ``MARKET_CONTEXT_SCHEMA.json``."""
        return {
            "name": self.name.value,
            "block_id": self.block_id,
            "bar_in_session": self.bar_in_session,
            "session_open_ts": self.session_open_ts,
            "session_high": self.session_high,
            "session_low": self.session_low,
            "opening_range": {
                "high": self.opening_range.high,
                "low": self.opening_range.low,
                "formed": self.opening_range.formed,
            },
        }


class SessionEngine:
    """Per-symbol session state machine. Feed closed base bars, in order, via :meth:`update`."""

    __slots__ = (
        "_block_id",
        "_prev_session_name",
        "_bar_in_session",
        "_session_open_ts",
        "_dev_high",
        "_dev_low",
        "_or_high",
        "_or_low",
        "_or_formed",
        "_prev_block_high",
        "_prev_block_low",
        "_prev_block_close",
        "_cur_block_high",
        "_cur_block_low",
        "_cum_pv",
        "_cum_vol",
        "_prev_close_of_block",
    )

    def __init__(self) -> None:
        self._block_id = -1  # first update() will bump this to 0 (a "new session" by construction)
        self._prev_session_name: SessionName | None = None
        self._bar_in_session = 0
        self._session_open_ts = 0
        self._dev_high: float | None = None
        self._dev_low: float | None = None
        self._or_high: float | None = None
        self._or_low: float | None = None
        self._or_formed = False
        self._prev_block_high: float | None = None
        self._prev_block_low: float | None = None
        self._prev_block_close: float | None = None
        self._cur_block_high: float | None = None
        self._cur_block_low: float | None = None
        self._cum_pv = 0.0
        self._cum_vol = 0.0
        self._prev_close_of_block: float | None = None

    def update(self, ts_open: int, high: float, low: float, close: float, volume: float | None) -> SessionSnapshot:
        """Advance the session state by one closed base bar and return its snapshot.

        Args:
            ts_open: the bar's open timestamp (UTC epoch seconds) — the research convention keys
                the session-hour lookup off the bar's OPEN time.
            high, low, close: the bar's OHLC (open is not needed for session bookkeeping).
            volume: the bar's volume, or ``None`` (VWAP is ``None`` for the block if no bar in it
                carries a volume).

        Returns:
            The :class:`SessionSnapshot` valid as of this bar.
        """
        from datetime import UTC, datetime

        hour = datetime.fromtimestamp(ts_open, tz=UTC).hour
        name = session_name_for_hour(hour)
        is_new_session = name != self._prev_session_name

        # snapshot of "developing" high/low BEFORE this bar is folded in (excludes current bar)
        session_high_before = self._dev_high
        session_low_before = self._dev_low

        if is_new_session:
            # freeze the just-completed block's extremes/close as "previous session"
            if self._prev_session_name is not None:
                self._prev_block_high = self._cur_block_high
                self._prev_block_low = self._cur_block_low
                self._prev_block_close = self._prev_close_of_block
            self._block_id += 1
            self._bar_in_session = 0
            self._session_open_ts = ts_open
            self._dev_high = None
            self._dev_low = None
            self._or_high = None
            self._or_low = None
            self._or_formed = False
            self._cur_block_high = None
            self._cur_block_low = None
            self._cum_pv = 0.0
            self._cum_vol = 0.0
        else:
            self._bar_in_session += 1

        # opening range: accumulate only over the first OPENING_RANGE_BARS bars of the block
        if self._bar_in_session < OPENING_RANGE_BARS:
            self._or_high = high if self._or_high is None else max(self._or_high, high)
            self._or_low = low if self._or_low is None else min(self._or_low, low)
            if self._bar_in_session == OPENING_RANGE_BARS - 1:
                self._or_formed = True

        # developing session high/low + VWAP + block extremes, updated AFTER reporting the "before" snapshot
        self._dev_high = high if self._dev_high is None else max(self._dev_high, high)
        self._dev_low = low if self._dev_low is None else min(self._dev_low, low)
        self._cur_block_high = high if self._cur_block_high is None else max(self._cur_block_high, high)
        self._cur_block_low = low if self._cur_block_low is None else min(self._cur_block_low, low)
        self._prev_close_of_block = close
        if volume is not None:
            typical = (high + low + close) / 3.0
            self._cum_pv += typical * volume
            self._cum_vol += volume

        vwap = (self._cum_pv / self._cum_vol) if self._cum_vol > 0 else None
        self._prev_session_name = name

        return SessionSnapshot(
            name=name,
            block_id=self._block_id,
            bar_in_session=self._bar_in_session,
            session_open_ts=self._session_open_ts,
            session_high=session_high_before,
            session_low=session_low_before,
            opening_range=OpeningRange(high=self._or_high if self._or_formed else None,
                                        low=self._or_low if self._or_formed else None,
                                        formed=self._or_formed),
            is_new_session=is_new_session,
            prev_session_high=self._prev_block_high,
            prev_session_low=self._prev_block_low,
            prev_session_close=self._prev_block_close,
            vwap=vwap,
        )
