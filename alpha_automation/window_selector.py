"""Market Window Selector -- reproducible, non-repeating, holdout-safe window selection.

Given a task's window hint and the set of already-reviewed windows (from research memory), it
picks a contiguous slice of the historical bar series. Properties:

  * seeded + reproducible: same (task, pass, reviewed set, timestamps) -> same window;
  * avoids accidental repetition: rejects a window that overlaps a recently-reviewed window
    for the same (edge, timeframe);
  * never crosses the holdout cutoff: it only selects from timestamps the data layer already
    restricted to `dt < cutoff`, and re-asserts the end is below the cutoff defensively;
  * records why the window was selected and an overlap key for exclusion bookkeeping.

Pure module: it takes a `timestamps(tf)` provider (list of ISO strings, ascending) so it can be
unit-tested without pandas or a live chart.
"""

from __future__ import annotations

from datetime import datetime
from typing import Callable, List, Optional, Sequence

from . import seeds
from . import schemas

TimestampsProvider = Callable[[str], List[str]]

_MAX_TRIES = 256


def _parse(iso: str) -> datetime:
    return datetime.fromisoformat(iso)


def _overlaps(a_start: str, a_end: str, b_start: str, b_end: str) -> bool:
    return not (_parse(a_end) < _parse(b_start) or _parse(a_start) > _parse(b_end))


class MarketWindowSelector:
    def __init__(self, master_seed: int, instrument: str, data_split_id: str, holdout_cutoff: str):
        self.master_seed = int(master_seed)
        self.instrument = instrument
        self.data_split_id = data_split_id
        self.holdout_cutoff = holdout_cutoff

    def select(
        self,
        task: dict,
        pass_no: int,
        timestamps: Sequence[str],
        reviewed_windows: Sequence[dict] = (),
    ) -> Optional[dict]:
        """Return a MarketWindow dict, or None if the series is empty."""
        ts = list(timestamps)
        if not ts:
            return None
        hint = task["window_hint"]
        tf = hint["timeframe"]
        span = int(hint["span_bars"])
        edge = task.get("edge_ref")
        n = len(ts)

        # Recent windows for the same (edge, tf) to avoid overlapping.
        recent = [
            w for w in reviewed_windows
            if w.get("timeframe") == tf and (w.get("edge_ref") == edge or edge is None or w.get("edge_ref") is None)
        ]

        if n <= span:
            start, end = ts[0], ts[-1]
            reason = (f"Series for {tf} has {n} bars <= requested span {span}; using full "
                      f"available pre-holdout range.")
            return self._build(tf, start, end, span, reason, edge)

        max_start = n - span
        candidate_starts = list(range(0, max_start + 1))
        rng = seeds.rng_labelled(self.master_seed, pass_no, "window")
        rng.shuffle(candidate_starts)

        first = None
        for i in candidate_starts[:_MAX_TRIES]:
            start, end = ts[i], ts[i + span - 1]
            if first is None:
                first = (start, end)
            if not any(_overlaps(start, end, w["start"], w["end"]) for w in recent):
                reason = (f"Seeded selection of a {span}-bar {tf} window not overlapping the "
                          f"{len(recent)} recently-reviewed window(s) for this edge/timeframe.")
                return self._build(tf, start, end, span, reason, edge)

        # All sampled candidates overlap something reviewed -> take the seeded-first and disclose it.
        start, end = first
        reason = (f"All sampled {tf} windows overlapped reviewed ranges; using seeded-first "
                  f"window and flagging for coverage review.")
        return self._build(tf, start, end, span, reason, edge)

    def _build(self, tf: str, start: str, end: str, span: int, reason: str, edge) -> dict:
        # Defensive holdout re-assertion: the data layer already excludes >= cutoff, but never trust.
        if self.holdout_cutoff and _parse(end) >= _parse(self.holdout_cutoff):
            raise ValueError(
                f"window end {end} is at/after holdout cutoff {self.holdout_cutoff} -- refusing "
                f"(fail-closed holdout protection)")
        win = {
            "instrument": self.instrument,
            "timeframe": tf,
            "start": start,
            "end": end,
            "n_bars_requested": span,
            "data_split_id": self.data_split_id,
            "holdout_cutoff": self.holdout_cutoff,
            "selection_reason": reason,
            "overlap_key": f"{edge}|{tf}|{start}|{end}",
        }
        errs = schemas.validate(win, schemas.load_schema("market_window"))
        if errs:  # pragma: no cover
            raise AssertionError(f"generated invalid window: {errs}")
        return win
