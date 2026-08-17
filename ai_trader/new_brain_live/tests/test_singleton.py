"""`SingletonLock` decisive tests (RT-N1-PERSIST-0001 section 5). Real subprocesses, not simulated --
"two simultaneous launches" is only a genuine proof when a SECOND OS process actually attempts
acquisition, and "crash recovery" is only genuine when a process is actually, forcibly killed."""

from __future__ import annotations

import subprocess
import sys
import time
import uuid
from pathlib import Path

import pytest

from ai_trader.new_brain_live.singleton import (
    AlreadyRunningError,
    ProcessIdentityRecord,
    SingletonLock,
    current_process_identity,
    query_process_command_line,
    verify_process_identity,
)

_PYTHON = sys.executable


def _unique_mutex_name() -> str:
    return rf"Global\AITraderTest_{uuid.uuid4().hex}"


def _spawn_holder(mutex_name: str, *, hold_seconds: float = 10.0) -> subprocess.Popen[str]:
    """A real second process that acquires `mutex_name` and holds it until `hold_seconds` elapse or it
    is killed -- whichever comes first."""
    script = (
        "import sys, time; sys.path.insert(0, r'{repo}'); "
        "from ai_trader.new_brain_live.singleton import SingletonLock; "
        "lock = SingletonLock(name={name!r}); lock.acquire(); "
        "print('ACQUIRED', flush=True); time.sleep({hold})"
    ).format(repo=str(Path(__file__).resolve().parents[3]), name=mutex_name, hold=hold_seconds)
    return subprocess.Popen([_PYTHON, "-c", script], stdout=subprocess.PIPE, text=True)


def _wait_for_line(proc: subprocess.Popen[str], expected: str, *, timeout: float = 15.0) -> None:
    deadline = time.time() + timeout
    assert proc.stdout is not None
    while time.time() < deadline:
        line = proc.stdout.readline()
        if expected in line:
            return
    raise AssertionError(f"subprocess never printed {expected!r} within {timeout}s")


def test_two_simultaneous_launches_only_one_active() -> None:
    mutex_name = _unique_mutex_name()
    holder = _spawn_holder(mutex_name, hold_seconds=8.0)
    try:
        _wait_for_line(holder, "ACQUIRED")

        second_attempt = SingletonLock(name=mutex_name)
        with pytest.raises(AlreadyRunningError):
            second_attempt.acquire()
    finally:
        holder.kill()
        holder.wait(timeout=10)


def test_pid_stale_recovery_after_clean_exit() -> None:
    """A prior holder exits CLEANLY (not a crash) -- Windows releases the mutex on any process exit,
    clean or not, so a fresh acquire must succeed immediately afterward. This is the "PID stale ->
    recuperare" scenario: whatever PID-based record a caller might still be holding onto is stale the
    moment the process exits, and the mutex (not the PID) is the actual source of truth."""
    mutex_name = _unique_mutex_name()
    holder = _spawn_holder(mutex_name, hold_seconds=0.5)
    _wait_for_line(holder, "ACQUIRED")
    holder.wait(timeout=10)  # clean exit

    recovered = SingletonLock(name=mutex_name)
    recovered.acquire()  # must not raise
    recovered.release()


def test_crash_mutex_recoverable() -> None:
    """The holder is forcibly killed (`taskkill /F`) -- a genuine crash, not a clean exit. The OS must
    still release the mutex; a fresh acquire immediately afterward must succeed."""
    mutex_name = _unique_mutex_name()
    holder = _spawn_holder(mutex_name, hold_seconds=30.0)
    try:
        _wait_for_line(holder, "ACQUIRED")
        subprocess.run(["taskkill", "/F", "/PID", str(holder.pid)], capture_output=True, timeout=15)
        holder.wait(timeout=10)

        recovered = SingletonLock(name=mutex_name)
        recovered.acquire()  # must not raise -- OS released the mutex on the killed process's exit
        recovered.release()
    finally:
        if holder.poll() is None:
            holder.kill()


def test_foreign_process_with_matching_pid_but_wrong_command_line_is_not_treated_as_ours() -> None:
    """A PID that genuinely exists right now (this very test process), but whose real command line does
    NOT contain the expected markers -- must never be treated as "our" process. Proves `nu omorî
    niciodată un PID fără verificarea command line/executable` holds even when the PID number itself is
    real and alive."""
    own_pid = __import__("os").getpid()  # this pytest worker process -- alive, but not new_brain_live
    fake_record = ProcessIdentityRecord(pid=own_pid, executable="irrelevant", command_line="irrelevant")

    assert verify_process_identity(fake_record, markers=("ai_trader.new_brain_live.entrypoint",)) is False


def test_nonexistent_pid_is_not_treated_as_ours() -> None:
    fake_record = ProcessIdentityRecord(pid=999_999_999, executable="x", command_line="x")
    assert verify_process_identity(fake_record) is False


def test_current_process_identity_round_trips_through_json() -> None:
    identity = current_process_identity()
    restored = ProcessIdentityRecord.from_json(identity.to_json())
    assert restored == identity


def test_query_process_command_line_returns_none_for_nonexistent_pid() -> None:
    assert query_process_command_line(999_999_999) is None
