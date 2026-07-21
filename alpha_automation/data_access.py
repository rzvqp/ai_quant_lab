"""Data access -- live TradingView Desktop primary, local CSV fallback.

CEO refinement #1: the live TradingView + tradingview-mcp path is the PRIMARY market-data
source; local CSV is a FALLBACK only. Concretely:

  * The local CSV catalog (via edge_research/_common.load) is the reliable index of *which*
    bars exist and their timestamps -- so window selection stays reproducible and holdout-safe.
  * For the *content* of a selected window, `get_window()` prefers a live pull from TradingView
    Desktop (through a small Node bridge that reuses tradingview-mcp's own connection/chart
    modules). If the live path is unavailable (Desktop not running / CDP unreachable) it falls
    back to the CSV bars. Every result stamps `data_source: live_tv | csv_fallback`.

The Alpha adapter receives a compact DESCRIPTIVE summary of the window (not raw frames and not
any tradability metric), keeping Alpha inside its scientific boundary.

pandas is imported lazily and only on the CSV path, so the rest of the orchestrator stays
pure-stdlib.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from statistics import mean, median
from typing import Dict, List, Optional, Tuple

_BRIDGE = Path(__file__).resolve().parent / "bridge" / "tv_pull.mjs"

# tf label -> TradingView resolution string (used by the live bridge).
TF_TO_TV = {"M15": "15", "H1": "60", "H4": "240", "D1": "D"}


class DataUnavailable(RuntimeError):
    pass


def assert_holdout_matches(config) -> None:
    """Fail closed if the config's holdout values drift from the canonical loader constants."""
    try:
        from edge_research import _common  # type: ignore
    except Exception:
        return  # loader not importable here (pure-stdlib env); csv path will surface it later
    if config.holdout_cutoff != _common.RESEARCH_HOLDOUT_CUTOFF_UTC:
        raise ValueError(
            f"holdout_cutoff drift: config={config.holdout_cutoff!r} vs canonical "
            f"{_common.RESEARCH_HOLDOUT_CUTOFF_UTC!r}")
    if config.data_split_id != _common.PRE_HOLDOUT_SPLIT_ID:
        raise ValueError(
            f"data_split_id drift: config={config.data_split_id!r} vs canonical "
            f"{_common.PRE_HOLDOUT_SPLIT_ID!r}")


def summarize_bars(bars: List[dict], timeframe: str) -> dict:
    """Compact, descriptive, boundary-safe summary of a window's bars.

    `bars` is a list of dicts with keys dt, o, h, l, c, v and optionally session.
    """
    if not bars:
        return {"timeframe": timeframe, "n_bars": 0}
    highs = [b["h"] for b in bars]
    lows = [b["l"] for b in bars]
    closes = [b["c"] for b in bars]
    ranges = [b["h"] - b["l"] for b in bars]
    vols = [b.get("v", 0) or 0 for b in bars]
    sessions: Dict[str, int] = {}
    for b in bars:
        s = b.get("session")
        if s:
            sessions[s] = sessions.get(s, 0) + 1
    sample = bars[-5:]
    return {
        "timeframe": timeframe,
        "n_bars": len(bars),
        "start": bars[0]["dt"],
        "end": bars[-1]["dt"],
        "price": {
            "first_close": closes[0],
            "last_close": closes[-1],
            "min_low": min(lows),
            "max_high": max(highs),
            "mean_close": round(mean(closes), 5),
        },
        "bar_range": {
            "mean": round(mean(ranges), 5),
            "median": round(median(ranges), 5),
            "max": round(max(ranges), 5),
        },
        "volume": {"mean": round(mean(vols), 2) if vols else 0},
        "session_counts": sessions,
        "sample_last_bars": [
            {"dt": b["dt"], "o": b["o"], "h": b["h"], "l": b["l"], "c": b["c"], "v": b.get("v", 0)}
            for b in sample
        ],
    }


class DataAccess:
    def __init__(self, config, logger=None):
        self.config = config
        self.log = logger
        self._csv_cache: Dict[str, Tuple[list, dict]] = {}
        self._ts_cache: Dict[str, List[str]] = {}
        self._live_ok: Optional[bool] = None

    # ---------- CSV (fallback + catalog) ----------
    def _load_csv(self, tf: str):
        if tf in self._csv_cache:
            return self._csv_cache[tf]
        try:
            from edge_research import _common  # type: ignore
        except Exception as e:  # pragma: no cover
            raise DataUnavailable(f"CSV loader unavailable: {e}") from e
        df, meta = _common.load(
            tf, data_split_id=self.config.data_split_id, cutoff=self.config.holdout_cutoff)
        bars = [
            {
                "dt": str(r.dt), "o": float(r.open), "h": float(r.high), "l": float(r.low),
                "c": float(r.close), "v": float(getattr(r, "volume", 0) or 0),
                "session": getattr(r, "session", None),
            }
            for r in df.itertuples(index=False)
        ]
        self._csv_cache[tf] = (bars, meta)
        return bars, meta

    def timestamps(self, tf: str) -> List[str]:
        """Ascending ISO timestamps of available (pre-holdout) bars for `tf` -- from the CSV catalog."""
        if tf not in self._ts_cache:
            bars, _ = self._load_csv(tf)
            self._ts_cache[tf] = [b["dt"] for b in bars]
        return self._ts_cache[tf]

    def bounds(self, tf: str) -> Tuple[str, str]:
        ts = self.timestamps(tf)
        if not ts:
            raise DataUnavailable(f"no bars for {tf}")
        return ts[0], ts[-1]

    def _csv_window(self, window: dict) -> List[dict]:
        tf = window["timeframe"]
        bars, _ = self._load_csv(tf)
        start, end = window["start"], window["end"]
        return [b for b in bars if start <= b["dt"] <= end]

    # ---------- live TradingView bridge ----------
    def live_available(self) -> bool:
        if self._live_ok is not None:
            return self._live_ok
        if not _BRIDGE.exists():
            self._live_ok = False
            return False
        try:
            out = self._run_bridge(["--health"])
            self._live_ok = bool(out.get("ok"))
        except Exception as e:
            if self.log:
                self.log.warn("live_health_failed", error=str(e))
            self._live_ok = False
        return self._live_ok

    def _run_bridge(self, args: List[str]) -> dict:
        env = dict(os.environ, TV_MCP_DIR=self.config.tv_mcp_dir)
        proc = subprocess.run(
            ["node", str(_BRIDGE), *args],
            capture_output=True, text=True, env=env, timeout=120,
        )
        if proc.returncode != 0:
            raise DataUnavailable(f"bridge rc={proc.returncode}: {proc.stderr.strip()[:300]}")
        # The bridge prints a single JSON line as its last line of stdout.
        last = [ln for ln in proc.stdout.splitlines() if ln.strip()][-1]
        return json.loads(last)

    def _live_window(self, window: dict) -> List[dict]:
        from datetime import datetime, timezone
        tf = window["timeframe"]
        frm = int(datetime.fromisoformat(window["start"]).timestamp())
        to = int(datetime.fromisoformat(window["end"]).timestamp())
        res = self._run_bridge([
            "--symbol", self.config.instrument_live,
            "--tf", TF_TO_TV.get(tf, "60"),
            "--from", str(frm), "--to", str(to),
        ])
        if not res.get("ok"):
            raise DataUnavailable(f"live pull failed: {res.get('error')}")
        cutoff_ts = int(datetime.fromisoformat(self.config.holdout_cutoff).timestamp())
        bars = []
        for row in res.get("bars", []):
            t = int(row[0])
            if t >= cutoff_ts:  # defensive holdout enforcement on live data
                continue
            bars.append({
                "dt": datetime.fromtimestamp(t, tz=timezone.utc).isoformat(),
                "o": float(row[1]), "h": float(row[2]), "l": float(row[3]),
                "c": float(row[4]), "v": float(row[5] if len(row) > 5 else 0),
            })
        return bars

    # ---------- public ----------
    def get_window(self, window: dict) -> Tuple[dict, dict]:
        """Return (data_summary, provenance). Chooses the source per config.data_source."""
        tf = window["timeframe"]
        pref = self.config.data_source
        source = None
        bars: List[dict] = []

        if pref in ("live", "auto") and self.live_available():
            try:
                bars = self._live_window(window)
                source = "live_tv"
            except Exception as e:
                if pref == "live":
                    raise
                if self.log:
                    self.log.warn("live_window_failed_fallback_csv", error=str(e))

        if source is None:
            if pref == "live":
                raise DataUnavailable("live data required but TradingView Desktop is unavailable")
            bars = self._csv_window(window)
            source = "csv_fallback"

        summary = summarize_bars(bars, tf)
        provenance = {
            "data_source": source,
            "n_bars": len(bars),
            "timeframe": tf,
            "instrument": self.config.instrument_live if source == "live_tv" else self.config.instrument_csv,
            "data_split_id": self.config.data_split_id,
            "holdout_cutoff": self.config.holdout_cutoff,
        }
        return summary, provenance
