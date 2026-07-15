"""The artifact/report writer (``IMPLEMENTATION_CHOICES.md`` §8): persists a run's trade history,
execution log, equity curve, and full report as JSON Lines / JSON files under
``results/simulation_runs/<run_id>/``, plus a checksummed manifest. Every write is atomic (write to a
``.tmp`` sibling, then ``os.replace`` onto the final name) -- a crash mid-write can never leave a
corrupt artifact at the canonical path.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from ai_trader.simulation.config import RecordConfig
from ai_trader.simulation.performance_analyzer import Artifacts
from ai_trader.simulation.portfolio_simulator import SimAccount


def _json_default(obj: Any) -> Any:
    if is_dataclass(obj) and not isinstance(obj, type):
        return asdict(obj)
    if hasattr(obj, "value"):  # Enum
        return obj.value
    raise TypeError(f"object of type {type(obj)!r} is not JSON serializable")


def _atomic_write_text(path: Path, content: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)


def _sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


class ArtifactWriter:
    """One instance per run. ``base_dir`` defaults to ``results/simulation_runs`` relative to the
    repository root, overridable for tests (never writes outside the given directory)."""

    def __init__(self, run_id: str, base_dir: Path) -> None:
        self.run_id = run_id
        self.run_dir = base_dir / run_id

    def write(self, account: SimAccount, report_dict: dict[str, Any], record: RecordConfig) -> Artifacts:
        self.run_dir.mkdir(parents=True, exist_ok=True)
        written: dict[str, Path] = {}

        if record.trade_history:
            path = self.run_dir / "trade_history.jsonl"
            lines = "\n".join(json.dumps(asdict(t), default=_json_default) for t in account.trade_ledger)
            _atomic_write_text(path, lines + ("\n" if lines else ""))
            written["trade_history_ref"] = path

        if record.equity_curve:
            path = self.run_dir / "equity_curve.jsonl"
            lines = "\n".join(json.dumps(asdict(p), default=_json_default) for p in account.equity_curve)
            _atomic_write_text(path, lines + ("\n" if lines else ""))
            written["equity_curve_ref"] = path

        if record.execution_log:
            # A real gap a review caught: this was gated on ``record.risk_events`` and wrote
            # ``account.risk_events`` -- ``record.execution_log`` was dead config, and the file
            # actually promised by ``IMPLEMENTATION_CHOICES.md`` §8 ("one JSON object per order-
            # lifecycle event") never existed. Now writes the real ``execution_log`` (fills).
            path = self.run_dir / "execution_log.jsonl"
            lines = "\n".join(json.dumps(asdict(e), default=_json_default) for e in account.execution_log)
            _atomic_write_text(path, lines + ("\n" if lines else ""))
            written["execution_log_ref"] = path

        report_path = self.run_dir / "report.json"
        _atomic_write_text(report_path, json.dumps(report_dict, indent=2, default=_json_default))

        manifest = {
            "run_id": self.run_id,
            "files": {
                p.name: {"sha256": _sha256_of(p), "bytes": p.stat().st_size}
                for p in [*written.values(), report_path]
            },
        }
        _atomic_write_text(self.run_dir / "manifest.json", json.dumps(manifest, indent=2))

        return Artifacts(
            trade_history_ref=_rel(written.get("trade_history_ref")),
            execution_log_ref=_rel(written.get("execution_log_ref")),
            equity_curve_ref=_rel(written.get("equity_curve_ref")),
        )


def _rel(path: Path | None) -> str | None:
    return path.name if path is not None else None
