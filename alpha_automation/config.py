"""Run configuration -- pure stdlib dataclass with JSON-file + CLI overrides.

Follows the lab convention (Python-literal defaults + argv), extended with an optional JSON
config file. No YAML dependency. The canonical holdout values live in
edge_research/_common.py; they are mirrored here as defaults and re-checked against the
canonical module at data-load time (see data_access.assert_holdout_matches) so drift fails
closed rather than silently loading contaminated data.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict, fields
from pathlib import Path
from typing import List, Optional

# Canonical location of the tradingview-mcp repo (live data path). Overridable via config/env.
DEFAULT_TV_MCP_DIR = r"C:\Users\MEDION GAMING\tradingview-mcp"

# Mirrors edge_research/_common.py -- re-verified at load time, never trusted blindly.
DEFAULT_HOLDOUT_CUTOFF = "2025-10-23T09:15:00+00:00"
DEFAULT_DATA_SPLIT_ID = "pre_holdout_2025-10-23T09-15-00Z_v1"

# Directory of THIS package (…/alpha_automation).
_PKG_DIR = Path(__file__).resolve().parent


@dataclass
class Config:
    # --- execution ---
    mode: str = "bounded"                      # bounded | continuous (continuous is Phase 4)
    max_passes: int = 5                        # bounded ceiling; also a hard cap in continuous mode
    delay_s: float = 0.0                       # inter-pass delay
    seed: int = 20260721                       # master seed -> deterministic run
    dry_run: bool = False                      # no data pull, no Alpha call; stub-only smoke path

    # --- adapter (Alpha reasoning backend) ---
    adapter: str = "stub"                      # stub | codex
    codex_model: Optional[str] = None          # e.g. "gpt-5-codex"; None => codex default
    codex_timeout_s: float = 180.0
    adapter_max_retries: int = 2               # schema/boundary re-request attempts

    # --- market data ---
    instrument_live: str = "OANDA:XAUUSD"      # symbol as TradingView expects it
    instrument_csv: str = "XAUUSD"             # label for csv provenance
    timeframes: List[str] = field(default_factory=lambda: ["M15", "H1", "H4", "D1"])
    data_source: str = "auto"                  # auto (live->csv fallback) | live | csv
    holdout_cutoff: str = DEFAULT_HOLDOUT_CUTOFF
    data_split_id: str = DEFAULT_DATA_SPLIT_ID
    tv_mcp_dir: str = DEFAULT_TV_MCP_DIR

    # --- window selection ---
    window_span_bars: int = 400                # nominal window size in bars
    avoid_recent_windows: int = 12             # exclusion horizon for reviewed windows (per edge/tf)

    # --- perspective / task ---
    avoid_recent_perspectives: int = 4         # do not repeat the last K research stances
    avoid_recent_questions: int = 200          # de-dup horizon for asked questions

    # --- TradingView Research Environment (Phase 2.5) ---
    use_tv_research: bool = False              # when True, build the observation dossier via TVRE
    research_mode: str = "replay_pre_cutoff"  # replay_pre_cutoff (holdout-safe) | live_observation
    tv_multi_tf: List[str] = field(default_factory=lambda: ["H1", "H4", "D1"])  # context TFs for dossier
    tv_replay_samples: int = 8                 # bar-by-bar replay snapshots per dossier
    tv_screenshots: bool = True                # capture chart screenshots into the dossier
    tv_pine_apply: bool = False                # allow applying Pine to chart (kept off: may cloud-save)
    max_followup_rounds: int = 2               # bounded Alpha-directed observation follow-ups (hybrid)
    max_followup_requests: int = 4             # max observation requests honored per round

    # --- safety / observability ---
    max_retries: int = 2                       # per-pass bounded retries (data/adapter transient)
    max_consecutive_failures: int = 5          # circuit-breaker threshold -> run FAILED
    max_wallclock_s: Optional[float] = None    # None => unbounded (bounded by max_passes)

    # --- persistence ---
    state_dir: str = str(_PKG_DIR / "state")

    # -------- construction helpers --------
    @classmethod
    def from_dict(cls, d: dict) -> "Config":
        known = {f.name for f in fields(cls)}
        unknown = set(d) - known
        if unknown:
            raise ValueError(f"unknown config keys: {sorted(unknown)}")
        return cls(**d)

    @classmethod
    def from_json_file(cls, path) -> "Config":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_dict(data)

    def merged(self, **overrides) -> "Config":
        d = asdict(self)
        for k, v in overrides.items():
            if v is None:
                continue
            if k not in d:
                raise ValueError(f"unknown override: {k}")
            d[k] = v
        return Config.from_dict(d)

    def validate(self) -> None:
        if self.mode not in ("bounded", "continuous"):
            raise ValueError(f"mode must be bounded|continuous, got {self.mode!r}")
        if self.adapter not in ("stub", "codex"):
            raise ValueError(f"adapter must be stub|codex, got {self.adapter!r}")
        if self.data_source not in ("auto", "live", "csv"):
            raise ValueError(f"data_source must be auto|live|csv, got {self.data_source!r}")
        if self.research_mode not in ("replay_pre_cutoff", "live_observation"):
            raise ValueError(
                f"research_mode must be replay_pre_cutoff|live_observation, got {self.research_mode!r}")
        if self.max_passes < 1:
            raise ValueError("max_passes must be >= 1")
        for tf in self.timeframes:
            if tf not in ("M15", "H1", "H4", "D1"):
                raise ValueError(f"unsupported timeframe {tf!r} (data only exists for M15/H1/H4/D1)")

    def as_dict(self) -> dict:
        return asdict(self)

    # convenience paths
    @property
    def state_path(self) -> Path:
        return Path(self.state_dir)

    @property
    def runs_dir(self) -> Path:
        return self.state_path / "runs"

    @property
    def memory_dir(self) -> Path:
        return self.state_path / "memory"

    @property
    def id_allocator_path(self) -> Path:
        return self.state_path / "id_allocator.json"
