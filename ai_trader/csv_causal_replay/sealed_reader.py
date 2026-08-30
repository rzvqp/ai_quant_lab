"""The safety-critical piece of CSV_CAUSAL_REPLAY_ADAPTER_V1 (mandate section 4): a bounded,
line-at-a-time streaming CSV reader that makes a bar beyond an authorized boundary PHYSICALLY
unreachable through this reader, not merely blocked by a downstream check.

**Why not `read_csv().head(N)` (mandate's own explicitly-named anti-pattern)**: loading the whole
file into a DataFrame first means every future row has already been parsed into process memory
before `.head(378)` ever runs -- the boundary would be enforced only by which rows get RETURNED, not
by which rows get READ. A bug in the slicing call, a stray `df.tail()`, a debugger inspecting `df` at
a breakpoint, or an exception object capturing `df` in a traceback would all have real, live access
to bar 379+.

**What this does instead**: `csv.reader` over an open file handle reads one physical line at a time
-- calling `next()` on it performs the actual disk read for that one line; a line this reader never
calls `next()` for is never read off disk into any Python object at all, sealed or not. The boundary
check happens on the timestamp field ALONE (parsed first, cheap, not itself sensitive market data)
-- OHLCV fields for a row that would exceed the boundary are never sliced out of the row, never
passed to `float()`, and never assigned to a variable, matching `errors.SealedBoundaryError`'s own
docstring claim exactly.
"""

from __future__ import annotations

import csv
import dataclasses
from pathlib import Path
from typing import Iterator

from ai_trader.csv_causal_replay.errors import NonFiniteBarValueError, SealedBoundaryError, TimestampOrderError
from ai_trader.csv_causal_replay.gap_classification import classify_gap
from ai_trader.csv_causal_replay.types import Bar, GapRecord

_EXPECTED_HEADER = ("time", "open", "high", "low", "close", "volume")


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class SealedReaderConfig:
    symbol: str
    bar_interval_seconds: int
    q4_start_ts: int
    """The first Q4 bar's `ts_open` (2020-10-01T00:00:00 UTC = 1601510400 for this mandate) -- rows
    strictly before this are warm-up context (yielded with `q4_bar_index=None`); this row and every
    row after it are Q4 bars, indexed 1, 2, 3, ... matching `AI_TRADER_Q4_M15_LOG.md`'s own `BAR N`
    numbering."""
    max_q4_bar_index: int
    """The last Q4 bar index this reader will ever yield. Reading stops (`SealedBoundaryError`) the
    instant a row's Q4 index would exceed this -- `378` for every use in this mandate."""


@dataclasses.dataclass(frozen=True, slots=True)
class SealedRow:
    bar: Bar
    q4_bar_index: int | None
    gap_before: GapRecord | None


def _parse_ts(raw: str, *, line_no: int) -> int:
    try:
        return int(raw)
    except ValueError as exc:
        raise NonFiniteBarValueError(f"line {line_no}: timestamp field {raw!r} is not an integer") from exc


def _parse_ohlcv(fields: list[str], *, ts: int, line_no: int) -> tuple[float, float, float, float, float]:
    try:
        o, h, l, c, v = (float(x) for x in fields[1:6])
    except ValueError as exc:
        raise NonFiniteBarValueError(f"line {line_no} (ts={ts}): non-numeric OHLCV field") from exc
    for name, value in (("open", o), ("high", h), ("low", l), ("close", c), ("volume", v)):
        if value != value or value in (float("inf"), float("-inf")):  # NaN check without importing math
            raise NonFiniteBarValueError(f"line {line_no} (ts={ts}): {name}={value!r} is NaN/Infinite")
    return o, h, l, c, v


class SealedReader:
    """One `SealedReader` wraps exactly one open file handle for its own lifetime (`with SealedReader(...)
    as reader:`). Not reusable across two `with` blocks -- construct a fresh instance per pass, which
    is also what keeps "how far did this reader get" unambiguous for `tests/test_sealed_reader.py`'s
    own `MAX_Q4_BAR_READ_DURING_DEVELOPMENT` proof."""

    def __init__(self, path: Path, *, config: SealedReaderConfig) -> None:
        self._path = path
        self._config = config
        self._fh = None
        self._reader: csv.reader | None = None
        self._last_q4_bar_index_yielded: int | None = None
        self._max_q4_bar_index_read = 0
        """Ratchets up as rows are actually yielded -- the mechanical, queryable proof of
        `MAX_Q4_BAR_READ_DURING_DEVELOPMENT` mandate section 17 requires. Never set optimistically;
        only after a row has actually been parsed and handed to the caller."""

    @property
    def max_q4_bar_index_read(self) -> int:
        return self._max_q4_bar_index_read

    def __enter__(self) -> "SealedReader":
        self._fh = self._path.open("r", encoding="utf-8", newline="")
        self._reader = csv.reader(self._fh)
        header = tuple(next(self._reader))
        if header != _EXPECTED_HEADER:
            raise ValueError(f"{self._path}: expected header {_EXPECTED_HEADER!r}, got {header!r}")
        return self

    def __exit__(self, *exc_info: object) -> None:
        if self._fh is not None:
            self._fh.close()
            self._fh = None
            self._reader = None

    def iter_rows(self) -> Iterator[SealedRow]:
        """Yields every row in file order. Raises `SealedBoundaryError` (without reading the OHLCV
        fields of the offending line -- see module docstring) the instant a Q4 row's index would
        exceed `config.max_q4_bar_index`; the file handle is left open but no further `next()` call
        is ever made after that (the caller's `with` block exit still closes it)."""
        assert self._reader is not None, "iter_rows() must be called inside a `with SealedReader(...) as reader:` block"
        prev_ts: int | None = None
        line_no = 1  # header was line 1
        for raw_fields in self._reader:
            line_no += 1
            if not raw_fields:
                continue
            ts = _parse_ts(raw_fields[0], line_no=line_no)

            if prev_ts is not None and ts <= prev_ts:
                raise TimestampOrderError(
                    f"line {line_no}: ts={ts} is not strictly greater than the previous row's ts={prev_ts}"
                )

            if ts < self._config.q4_start_ts:
                q4_bar_index = None
            else:
                q4_bar_index = (
                    1 if self._last_q4_bar_index_yielded is None else self._last_q4_bar_index_yielded + 1
                )
                if q4_bar_index > self._config.max_q4_bar_index:
                    # Boundary enforced BEFORE raw_fields[1:] (OHLCV) is ever parsed for this line.
                    raise SealedBoundaryError(
                        f"line {line_no}: Q4 bar index {q4_bar_index} exceeds sealed boundary "
                        f"max_q4_bar_index={self._config.max_q4_bar_index} -- refusing to read this "
                        "row's OHLCV fields"
                    )

            o, h, l, c, v = _parse_ohlcv(raw_fields, ts=ts, line_no=line_no)
            gap_before = None
            if prev_ts is not None and ts - prev_ts != self._config.bar_interval_seconds:
                gap_before = GapRecord(
                    symbol=self._config.symbol, gap_start=prev_ts, gap_end=ts,
                    duration_seconds=ts - prev_ts, classification=classify_gap(prev_ts, ts),
                )
            bar = Bar(
                symbol=self._config.symbol, ts_open=ts, ts_close=ts + self._config.bar_interval_seconds,
                open=o, high=h, low=l, close=c, volume=v, is_backfilled=False,
            )
            if q4_bar_index is not None:
                self._last_q4_bar_index_yielded = q4_bar_index
                self._max_q4_bar_index_read = q4_bar_index
            prev_ts = ts
            yield SealedRow(bar=bar, q4_bar_index=q4_bar_index, gap_before=gap_before)
