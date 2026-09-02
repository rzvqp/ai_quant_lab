"""The mechanical (non-LLM) tick loop: causal bar ingestion, S5-occurrence episode detection,
mechanical resolution scoring. Deliberately does NOT attempt the Section 8-10 qualitative reasoning
itself -- that requires genuine judgment (an LLM pass, `qualitative_review.py`'s own consumer),
which this loop only ever prepares for (freezes a complete, self-contained snapshot) and never
performs. This keeps the always-on daemon simple, deterministic, and auditable, while the harder
reasoning work happens on a separately-scheduled cadence."""

from __future__ import annotations

import datetime
import time
import uuid

from ai_trader.apprenticeship_v2 import durable_store
from ai_trader.apprenticeship_v2.mt5_read_only_source import (
    TIMEFRAME_H1, TIMEFRAME_H4, TIMEFRAME_M5, TIMEFRAME_M15, XAUUSD, ReadOnlyBar, fetch_causal_closed_bars,
)
from ai_trader.apprenticeship_v2.resolution import all_horizons_available, compute_horizon_metrics, compute_s5_structural_resolution
from ai_trader.apprenticeship_v2.s5_observer import S5Observer
from ai_trader.apprenticeship_v2.schemas import RESOLUTION_HORIZONS_M15, EpisodeRecord, ResolvedEpisode

WARMUP_M15_BARS = 40  # matches soak_loop.py's own STARTUP_WARMUP_BARS convention
SNAPSHOT_BAR_COUNTS = {"H4": 12, "H1": 24, "M15": 60, "M5": 48}
FORWARD_LOOKAHEAD_FETCH = max(RESOLUTION_HORIZONS_M15) + 4  # a little slack


def _atr14(bars: list[ReadOnlyBar]) -> float | None:
    if len(bars) < 15:
        return None
    trs = []
    for i in range(1, len(bars)):
        prev_close = bars[i - 1].close
        b = bars[i]
        tr = max(b.high - b.low, abs(b.high - prev_close), abs(b.low - prev_close))
        trs.append(tr)
    window = trs[-14:]
    return sum(window) / len(window)


def _bar_to_dict(b: ReadOnlyBar) -> dict[str, object]:
    return {
        "ts_open": b.ts_open, "ts_close": b.ts_close, "open": b.open, "high": b.high, "low": b.low,
        "close": b.close, "volume": b.volume,
    }


def _snapshot(h4: list[ReadOnlyBar], h1: list[ReadOnlyBar], m15: list[ReadOnlyBar], m5: list[ReadOnlyBar]) -> dict[str, list[dict[str, object]]]:
    return {
        "H4": [_bar_to_dict(b) for b in h4[-SNAPSHOT_BAR_COUNTS["H4"]:]],
        "H1": [_bar_to_dict(b) for b in h1[-SNAPSHOT_BAR_COUNTS["H1"]:]],
        "M15": [_bar_to_dict(b) for b in m15[-SNAPSHOT_BAR_COUNTS["M15"]:]],
        "M5": [_bar_to_dict(b) for b in m5[-SNAPSHOT_BAR_COUNTS["M5"]:]],
    }


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


class ApprenticeshipTick:
    """One instance persists across `run_forever`'s loop iterations (rebuilds its own S5Observer's
    internal opening-range state via warmup replay on construction, then only feeds strictly-newer
    bars on subsequent ticks -- safe to reconstruct from scratch on every process restart)."""

    def __init__(self) -> None:
        self._s5 = S5Observer()
        self._warmed_up = False

    def _warmup(self, now_fn) -> int | None:
        m15 = fetch_causal_closed_bars(symbol=XAUUSD, timeframe=TIMEFRAME_M15, count=WARMUP_M15_BARS, now_fn=now_fn)
        state = durable_store.load_runtime_state()
        last_processed = state.get("last_processed_m15_ts_close")
        replay_bars = [b for b in m15 if last_processed is None or b.ts_close <= last_processed]
        for b in replay_bars:
            self._s5.observe(b)
        self._warmed_up = True
        return last_processed

    @staticmethod
    def _s5_notionally_open(m15_bars: list[ReadOnlyBar], as_of_ts_close: int) -> bool:
        """True if any prior, still-unresolved S5_OCCURRENCE episode's mechanically-simulated
        stop/target/max_hold has not yet been reached as of `as_of_ts_close` -- i.e. a real S5
        execution would still be holding that position, so a fresh trigger on this bar is the same
        continuing signal, not a new independent episode (Section 20)."""
        import json as _json

        for episode_id in durable_store.read_open_episode_ids_without_resolution():
            row = durable_store.read_episode_row(episode_id)
            if row is None or row["episode_type"] != "S5_OCCURRENCE":
                continue
            frozen_bar_ts = int(row["frozen_at_bar_ts"])
            if frozen_bar_ts >= as_of_ts_close:
                continue
            ref_levels = _json.loads(row["reference_levels_json"])
            if "stop" not in ref_levels:
                continue
            entry_price = float(ref_levels.get("entry", row["current_price"]))
            stop = float(ref_levels["stop"])
            target = entry_price + 3.0 * (entry_price - stop)
            forward = [b for b in m15_bars if frozen_bar_ts < b.ts_close <= as_of_ts_close]
            if not forward:
                continue
            resolution = compute_s5_structural_resolution(
                entry=entry_price, stop=stop, target=target, entry_bar_ts=frozen_bar_ts,
                max_hold_bars=48, forward_bars=forward,
            )
            if resolution is None:
                return True  # still open as of this bar
        return False

    def tick(self, now_fn=time.time) -> dict[str, object]:
        if not self._warmed_up:
            self._warmup(now_fn)

        state = durable_store.load_runtime_state()
        last_processed = state.get("last_processed_m15_ts_close")

        m15 = fetch_causal_closed_bars(symbol=XAUUSD, timeframe=TIMEFRAME_M15, count=max(WARMUP_M15_BARS, FORWARD_LOOKAHEAD_FETCH + 5), now_fn=now_fn)
        h1 = fetch_causal_closed_bars(symbol=XAUUSD, timeframe=TIMEFRAME_H1, count=SNAPSHOT_BAR_COUNTS["H1"] + 2, now_fn=now_fn)
        h4 = fetch_causal_closed_bars(symbol=XAUUSD, timeframe=TIMEFRAME_H4, count=SNAPSHOT_BAR_COUNTS["H4"] + 2, now_fn=now_fn)
        m5 = fetch_causal_closed_bars(symbol=XAUUSD, timeframe=TIMEFRAME_M5, count=SNAPSHOT_BAR_COUNTS["M5"] + 2, now_fn=now_fn)

        new_m15 = [b for b in m15 if last_processed is None or b.ts_close > last_processed]
        new_episode_ids: list[str] = []

        for bar in new_m15:
            hypothesis = self._s5.observe(bar)
            if hypothesis is not None and self._s5_notionally_open(m15, bar.ts_close):
                # Section 20: do not count a still-continuing signal as a fresh independent episode --
                # a prior S5_OCCURRENCE episode from this same notional position is still open
                # (mechanically simulated stop/target/max_hold not yet reached), so this bar's own
                # trigger is a continuation of that same causal episode, not a new one.
                hypothesis = None
            if hypothesis is not None:
                atr = _atr14(m15)
                episode = EpisodeRecord(
                    episode_id=f"S5-{bar.ts_close}-{uuid.uuid4().hex[:8]}",
                    timestamp_utc=_now_iso(), frozen_at_bar_ts=bar.ts_close, episode_type="S5_OCCURRENCE",
                    symbol=XAUUSD, current_price=bar.close, setup_direction=str(hypothesis.direction),
                    reference_levels={
                        "entry": hypothesis.intended_entry, "stop": hypothesis.invalidation,
                        "or_high": self._s5._strategy._or_high, "or_low": self._s5._strategy._or_low,
                        "atr14": atr if atr is not None else -1.0,
                    },
                    snapshot=_snapshot(h4, h1, m15, m5),
                )
                durable_store.append_episode_to_ledger(episode)
                new_episode_ids.append(episode.episode_id)
            last_processed = bar.ts_close

        # Mechanical resolution scoring for every open (unresolved) episode -- independent of the
        # qualitative-review status; a PENDING episode can still resolve mechanically before a human/
        # LLM pass ever reasons about it, and that is fine -- the frozen prediction, once made, is
        # scored against the mechanical outcome exactly as it was, never adjusted.
        resolved_count = 0
        for episode_id in durable_store.read_open_episode_ids_without_resolution():
            row = durable_store.read_episode_row(episode_id)
            if row is None:
                continue
            frozen_bar_ts = int(row["frozen_at_bar_ts"])
            forward = [b for b in m15 if b.ts_close > frozen_bar_ts]
            if not all_horizons_available(forward):
                continue
            import json as _json

            ref_levels = _json.loads(row["reference_levels_json"])
            entry_price = ref_levels.get("entry", row["current_price"])
            atr_val = ref_levels.get("atr14")
            atr_val = None if atr_val is None or float(atr_val) < 0 else float(atr_val)
            direction = row.get("setup_direction") or None
            horizons = {
                str(n): compute_horizon_metrics(
                    entry_price=float(entry_price), setup_direction=direction, forward_bars=forward,
                    horizon_n=n, atr=atr_val,
                ).to_json_dict()
                for n in RESOLUTION_HORIZONS_M15
            }
            structural = None
            if row["episode_type"] == "S5_OCCURRENCE" and "stop" in ref_levels:
                target = float(entry_price) + 3.0 * (float(entry_price) - float(ref_levels["stop"]))
                s5_res = compute_s5_structural_resolution(
                    entry=float(entry_price), stop=float(ref_levels["stop"]), target=target,
                    entry_bar_ts=frozen_bar_ts, max_hold_bars=48, forward_bars=forward,
                )
                structural = s5_res.to_json_dict() if s5_res is not None else None
            resolved = ResolvedEpisode(
                episode_id=episode_id, resolved_at_utc=_now_iso(), atr_at_episode_start=atr_val,
                horizons=horizons, structural_resolution=structural,
            )
            durable_store.append_resolved_episode(resolved)
            resolved_count += 1

        state["last_processed_m15_ts_close"] = last_processed
        state["last_tick_utc"] = _now_iso()
        state["last_causal_bar_seen"] = last_processed
        durable_store.save_runtime_state(state)

        return {"new_bars": len(new_m15), "new_episodes": new_episode_ids, "resolved_this_tick": resolved_count, "last_processed_m15_ts_close": last_processed}
