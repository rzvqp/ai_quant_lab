"""Isolation from other divisions (Red Team / Flow C / AI Trader).

The automation must never read or write another division's files. We assert (a) the package
source contains no reference to other divisions' modules/paths, and (b) at runtime the runner
writes only under its configured state directory.
"""

import pathlib

from alpha_automation.config import Config
from alpha_automation.runner import Runner
from alpha_automation.adapters import StubAdapter
from conftest import FakeDataAccess

PKG = pathlib.Path(__file__).resolve().parents[2] / "alpha_automation"
FORBIDDEN_TOKENS = ["ai_trader", "red_team", "red-team", "flow_c", "flow-c"]


def test_source_has_no_other_division_references():
    offenders = []
    for py in PKG.rglob("*.py"):
        text = py.read_text(encoding="utf-8").lower()
        for tok in FORBIDDEN_TOKENS:
            if tok in text:
                offenders.append((py.name, tok))
    assert not offenders, f"other-division references found: {offenders}"


def test_runtime_writes_only_under_state_dir(tmp_path):
    state = tmp_path / "state"
    cfg = Config(adapter="stub", data_source="csv", delay_s=0.0,
                 max_passes=4, state_dir=str(state))

    # Structural guarantee: all persistence paths live under state_dir.
    for p in (cfg.runs_dir, cfg.memory_dir, cfg.id_allocator_path):
        assert str(p).startswith(str(state))

    r = Runner(cfg, data_access=FakeDataAccess(), adapter=StubAdapter(1), install_signals=False)
    r.start()

    # Every file produced under the temp root must be inside state_dir.
    produced = [p for p in tmp_path.rglob("*") if p.is_file()]
    assert produced, "run produced no files"
    for p in produced:
        assert str(p).startswith(str(state)), f"wrote outside state_dir: {p}"
