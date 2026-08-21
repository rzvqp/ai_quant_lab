"""RT-NEW-BRAIN-ARCH-0001 section 35: proves every periodic/production `subprocess.run`/`Popen` call
site identified in the console-window audit actually passes `NO_CONSOLE_WINDOW_CREATIONFLAGS` -- not
just that the source line looks right, but that the real call reaches `subprocess` with that kwarg.
Each test monkeypatches `subprocess.run`/`Popen` to capture kwargs rather than spawning a real child
process, then lets the caller fail downstream on the fake response (irrelevant to what's being proven
here)."""

from __future__ import annotations

import io
import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from ai_trader.new_brain_bridge.no_console_window import NO_CONSOLE_WINDOW_CREATIONFLAGS
from ai_trader.new_brain_bridge.tower_launcher import TowerWorkerLauncher
from ai_trader.new_brain_live.entrypoint import current_git_commit
from ai_trader.new_brain_live.n1_incremental.client import N1IncrementalClient, N1IncrementalWorkerError
from ai_trader.new_brain_live.singleton import query_process_command_line
from ai_trader.new_brain_live.watchdog import query_task_state, real_notify


def test_no_console_window_creationflags_is_nonzero_on_this_platform() -> None:
    """This whole fix is a no-op unless the constant actually resolves to Windows' real flag."""
    assert NO_CONSOLE_WINDOW_CREATIONFLAGS == subprocess.CREATE_NO_WINDOW
    assert NO_CONSOLE_WINDOW_CREATIONFLAGS != 0


def test_query_process_command_line_suppresses_console_window(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_run(*args: Any, **kwargs: Any) -> Any:
        captured.update(kwargs)
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    query_process_command_line(123)
    assert captured.get("creationflags") == NO_CONSOLE_WINDOW_CREATIONFLAGS


def test_query_task_state_suppresses_console_window(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_run(*args: Any, **kwargs: Any) -> Any:
        captured.update(kwargs)
        return subprocess.CompletedProcess(args=args, returncode=1, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    query_task_state("SomeTask")
    assert captured.get("creationflags") == NO_CONSOLE_WINDOW_CREATIONFLAGS


def test_real_notify_suppresses_console_window(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_run(*args: Any, **kwargs: Any) -> Any:
        captured.update(kwargs)
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    real_notify("label", "detail")
    assert captured.get("creationflags") == NO_CONSOLE_WINDOW_CREATIONFLAGS


def test_current_git_commit_suppresses_console_window(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_run(*args: Any, **kwargs: Any) -> Any:
        captured.update(kwargs)
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="abc1234\n", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert current_git_commit() == "abc1234"
    assert captured.get("creationflags") == NO_CONSOLE_WINDOW_CREATIONFLAGS


def test_n1_incremental_client_observe_suppresses_console_window(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_run(*args: Any, **kwargs: Any) -> Any:
        captured.update(kwargs)
        # A malformed/"not ok" worker response is a fine outcome for THIS test -- it still proves
        # subprocess.run was reached with the right kwarg; the client's own real-response-shape
        # handling is exercised elsewhere (test_incremental_integration.py, against the real artifact).
        return subprocess.CompletedProcess(args=args, returncode=0, stdout=json.dumps({"ok": False}), stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    client = N1IncrementalClient(
        symbol="XAUUSD", timeframe="M15", bar_interval_seconds=900, implementation_commit="test",
    )
    with pytest.raises(N1IncrementalWorkerError):
        client.observe(bars=(), restore_snapshot_blob=None, wall_clock_now=0.0)
    assert captured.get("creationflags") == NO_CONSOLE_WINDOW_CREATIONFLAGS


class _FakeStdout:
    def readline(self) -> str:
        return ""  # never reports ready -- readiness wait must give up quickly (short timeout below)


def test_tower_launcher_popen_suppresses_console_window(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    captured: dict[str, Any] = {}

    class _FakeProcess:
        def __init__(self) -> None:
            self.stdin = io.StringIO()
            self.stdout = _FakeStdout()

        def poll(self) -> None:
            return None  # never exits -- readiness wait must give up on the short timeout instead

    def fake_popen(*args: Any, **kwargs: Any) -> Any:
        captured.update(kwargs)
        return _FakeProcess()

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    launcher = TowerWorkerLauncher(tower_python=tmp_path / "python.exe", timeout_seconds=0.05)
    result = launcher.launch_and_handshake()
    assert captured.get("creationflags") == NO_CONSOLE_WINDOW_CREATIONFLAGS
    assert result is not None  # HandshakeFailure, expected -- the fake process never reports ready
