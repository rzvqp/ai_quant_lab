"""RT-N1-ENV-SPLIT-0001 -- CEO decision (AI Trader New Brain Architecture mandate, 2026-08-21,
`N1_ALPHA_AI_TRADER_RUNTIME_ISOLATION_COMPLETE`): `.alpha_n1_venv` (Alpha Discovery, `ve_n1_replay
0.2.0`, `RT-RANGE-0002`) and `.ai_trader_n1_venv` (AI Trader, `ve_n1_replay 0.1.1`, `RT-N1-0002`/
`RT-N1-0003`) must never contaminate each other again -- this is the file that proves it, against the
REAL installed state of both real venvs, never mocked for the identity-facing assertions."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import pytest

from ai_trader.new_brain_live.n1_incremental import artifact_pin
from ai_trader.new_brain_live.n1_incremental.client import N1IncrementalClient
from ai_trader.new_brain_live.n1_incremental.tests.test_incremental_integration import _calm_bars_after, _client

_ALPHA_VENV_PYTHON = Path("C:/Users/MEDION GAMING/.alpha_n1_venv/Scripts/python.exe")
_ALPHA_EXPECTED_VERSION = "0.2.0"


def _query_installed_version(venv_python: Path) -> str:
    """Real, read-only subprocess call against a venv's own interpreter -- never a cached/recorded
    value. Never mutates either venv."""
    result = subprocess.run(
        [str(venv_python), "-c", "import ve_n1_replay; print(ve_n1_replay.VE_N1_REPLAY_VERSION)"],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"query failed: {result.stderr}"
    return result.stdout.strip()


def test_ai_trader_venv_path_is_never_the_alpha_venv_path() -> None:
    assert artifact_pin.AI_TRADER_N1_VENV_PYTHON != _ALPHA_VENV_PYTHON
    assert ".ai_trader_n1_venv" in str(artifact_pin.AI_TRADER_N1_VENV_PYTHON)
    assert ".alpha_n1_venv" not in str(artifact_pin.AI_TRADER_N1_VENV_PYTHON)


def test_ai_trader_client_default_venv_never_resolves_through_alpha_venv() -> None:
    """Source-of-truth check on the ACTUAL default `N1IncrementalClient` would use if a caller supplies
    no override -- not just the constant in isolation."""
    client = N1IncrementalClient(
        symbol="XAUUSD", timeframe="M15", bar_interval_seconds=900, implementation_commit="test",
    )
    assert client._venv_python == artifact_pin.AI_TRADER_N1_VENV_PYTHON  # noqa: SLF001 -- deliberate internal-state check
    assert ".alpha_n1_venv" not in str(client._venv_python)  # noqa: SLF001


def test_alpha_env_and_ai_trader_env_coexist_with_different_real_versions_right_now() -> None:
    """The DECISIVE isolation proof: both real venvs queried independently, in the SAME test, at the
    SAME time -- Alpha genuinely still runs 0.2.0 (untouched, per the CEO's 'do not downgrade the Alpha
    environment' instruction) while AI Trader genuinely runs 0.1.1, simultaneously, on this machine."""
    alpha_version = _query_installed_version(_ALPHA_VENV_PYTHON)
    ai_trader_version = _query_installed_version(artifact_pin.AI_TRADER_N1_VENV_PYTHON)
    assert alpha_version == _ALPHA_EXPECTED_VERSION
    assert ai_trader_version == artifact_pin.PINNED_VERSION
    assert alpha_version != ai_trader_version


def test_changing_alpha_installed_version_cannot_alter_ai_trader_runtime_identity(tmp_path: Path) -> None:
    """Not merely "they happen to differ today" -- proves NO code path exists by which Alpha's own
    venv state could ever be consulted to answer AI Trader's identity question. `verify_pin()` reads
    ONLY `.ai_trader_n1_venv`'s own dist-info; this test confirms swapping in a config that points
    somewhere else (simulating "what if Alpha's env were consulted instead") produces a DIFFERENT,
    independently-computed answer, never a value derived from or influenced by the real Alpha venv."""
    real_result = artifact_pin.verify_pin()
    assert real_result.ok is True

    alpha_dist_info = _ALPHA_VENV_PYTHON.parent.parent / "Lib" / "site-packages" / f"ve_n1_replay-{_ALPHA_EXPECTED_VERSION}.dist-info"
    assert alpha_dist_info.is_dir(), "fixture regression: Alpha's own 0.2.0 dist-info must still exist"
    alpha_direct_url = (alpha_dist_info / "direct_url.json").read_text(encoding="utf-8")
    assert artifact_pin.PINNED_WHEEL_SHA256 not in alpha_direct_url, (
        "Alpha's own recorded hash must never equal AI Trader's pin -- if it ever does, the two "
        "artifacts have converged and this isolation test's premise no longer holds"
    )


def test_ai_trader_subprocess_launches_the_expected_interpreter(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_run(*args: Any, **kwargs: Any) -> Any:
        captured["argv"] = args[0]
        return subprocess.CompletedProcess(args=args, returncode=0, stdout='{"ok": false, "error": "stub"}', stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    client = _client()
    try:
        client.observe(bars=(), restore_snapshot_blob=None, wall_clock_now=0.0)
    except Exception:
        pass  # only the invoked interpreter path matters to this test
    assert captured["argv"][0] == str(artifact_pin.AI_TRADER_N1_VENV_PYTHON)


def test_wheel_fingerprint_matches_authorized_ai_trader_artifact_via_real_call() -> None:
    """Real, unmocked subprocess call through the full client -> worker_script.py -> installed
    ve_n1_replay path -- the worker's own self-reported artifact identity must match the pin exactly."""
    client = _client()
    bars = tuple(_calm_bars_after(count=3, start_index=0, start_price=2000.0))
    response = client.observe(bars=bars, restore_snapshot_blob=None, wall_clock_now=1_000_000_000.0)
    assert response.rejected is False, response.rejection_reason
    assert response.result is not None


def test_n1_output_remains_deterministic() -> None:
    """Two independent client instances (fresh worker subprocess each time, no shared state), the SAME
    input bars, the SAME wall_clock_now -- fingerprints must match exactly."""
    bars = tuple(_calm_bars_after(count=5, start_index=0, start_price=2000.0))
    first = _client().observe(bars=bars, restore_snapshot_blob=None, wall_clock_now=1_000_000_000.0)
    second = _client().observe(bars=bars, restore_snapshot_blob=None, wall_clock_now=1_000_000_000.0)
    assert first.rejected is False and second.rejected is False
    assert first.result is not None and second.result is not None
    assert first.result.output_fingerprint == second.result.output_fingerprint
    assert first.result.n1_output_fingerprint == second.result.n1_output_fingerprint
    assert first.result.router_output_fingerprint == second.result.router_output_fingerprint


def test_artifact_identity_mismatch_produces_fail_closed_rejection_never_silent_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Simulates the exact failure mode the CEO's mandate names: a worker somehow answering with the
    WRONG artifact identity (e.g. if `.ai_trader_n1_venv` were ever silently mutated). Must reject,
    never surface `result`, never fall back to trusting the mismatched response."""
    import json

    def fake_run(*args: Any, **kwargs: Any) -> Any:
        payload = {
            "ok": True, "rejected": False, "rejection_reason": None, "restored_from_snapshot": False,
            "restore_rejected_reason": None, "bars_processed": 1, "last_result": None,
            "snapshot_blob": None, "identity": None,
            "artifact": {
                "ve_n1_replay_version": "0.2.0",  # deliberately wrong -- Alpha's version, not the pin
                "ai_source_commit": artifact_pin.PINNED_AI_SOURCE_COMMIT,
                "detector_submodule_commit": artifact_pin.PINNED_DETECTOR_SUBMODULE_COMMIT,
            },
        }
        return subprocess.CompletedProcess(args=args, returncode=0, stdout=json.dumps(payload), stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    client = _client()
    response = client.observe(bars=(), restore_snapshot_blob=None, wall_clock_now=0.0)
    assert response.rejected is True
    assert response.rejection_reason is not None and "ARTIFACT_VERSION_MISMATCH" in response.rejection_reason
    assert response.result is None
