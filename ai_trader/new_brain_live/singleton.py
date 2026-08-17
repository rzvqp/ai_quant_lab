"""OS-level singleton enforcement for `new_brain_live` (RT-N1-PERSIST-0001 section 1, Red Team's own
flagged gap: no explicit singleton existed before this).

**A real Windows named mutex (`kernel32.CreateMutexW`), not a PID file** -- a PID file goes stale the
moment its process crashes (nothing updates or deletes it), so "is this PID still really our process"
always needs a separate, fallible check. A named kernel object has no such failure mode: Windows itself
closes every handle a process holds, including mutex handles, the instant that process terminates for
ANY reason (clean exit, unhandled exception, `taskkill /F`, power loss recovery on next boot) -- there is
no "stale mutex" state to recover from, because the object simply stops existing. This is why "mutex
eliberat după crash/exit" is a structural property here, not a behavior this module has to implement.

**A supplementary `ProcessIdentityRecord`** is still written alongside the mutex (never as the sole
enforcement mechanism, per the CEO's own explicit prohibition) -- purely for the watchdog's own
diagnostic use: "is the PID number I see right now actually running OUR process, or did Windows just
happen to reuse that PID number for something unrelated after a crash" (`verify_process_identity`)."""

from __future__ import annotations

import ctypes
import ctypes.wintypes
import dataclasses
import json
import os
import subprocess
import sys
from pathlib import Path

_ERROR_ALREADY_EXISTS = 183
MUTEX_NAME = r"Global\AITraderLiveShadowSingleton"

_IDENTITY_MARKERS = ("ai_trader.new_brain_live.entrypoint",)


class AlreadyRunningError(Exception):
    """Raised by `SingletonLock.acquire()` when another instance already holds the named mutex --
    the CEO's own required `ALREADY_RUNNING` outcome. The caller must exit cleanly on this, never
    retry-loop, never fall back to running without the lock."""


@dataclasses.dataclass(frozen=True, slots=True)
class ProcessIdentityRecord:
    pid: int
    executable: str
    command_line: str

    def to_json(self) -> str:
        return json.dumps(dataclasses.asdict(self))

    @staticmethod
    def from_json(text: str) -> "ProcessIdentityRecord":
        data = json.loads(text)
        return ProcessIdentityRecord(pid=data["pid"], executable=data["executable"], command_line=data["command_line"])


def current_process_identity() -> ProcessIdentityRecord:
    return ProcessIdentityRecord(pid=os.getpid(), executable=sys.executable, command_line=" ".join(sys.argv))


class SingletonLock:
    """One instance per Windows session-wide mutex name. `acquire()` raises `AlreadyRunningError`
    immediately (never blocks, never waits) if another holder already exists -- matching the CEO's own
    "a doua lansare -> ALREADY_RUNNING și exit curat" requirement exactly: the caller decides how to
    exit, this class only decides whether the caller may proceed."""

    def __init__(self, name: str = MUTEX_NAME, *, identity_path: Path | None = None) -> None:
        self._name = name
        self._handle: int | None = None
        self._identity_path = identity_path

    def acquire(self) -> None:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateMutexW.restype = ctypes.wintypes.HANDLE
        kernel32.CreateMutexW.argtypes = [ctypes.c_void_p, ctypes.c_bool, ctypes.c_wchar_p]
        handle = kernel32.CreateMutexW(None, False, self._name)
        last_error = ctypes.get_last_error()
        if not handle:
            raise OSError(f"SingletonLock: CreateMutexW failed, GetLastError={last_error}")
        if last_error == _ERROR_ALREADY_EXISTS:
            kernel32.CloseHandle(handle)
            raise AlreadyRunningError(f"another instance already holds mutex {self._name!r}")
        self._handle = handle
        if self._identity_path is not None:
            self._identity_path.write_text(current_process_identity().to_json(), encoding="utf-8")

    def release(self) -> None:
        if self._handle is not None:
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel32.ReleaseMutex(self._handle)
            kernel32.CloseHandle(self._handle)
            self._handle = None

    def __enter__(self) -> "SingletonLock":
        self.acquire()
        return self

    def __exit__(self, *_exc_info: object) -> None:
        self.release()


def query_process_command_line(pid: int) -> str | None:
    """Real, read-only OS query -- never trusts a cached/recorded value for "is this PID alive right
    now." Returns `None` if no process with that PID currently exists. Uses the SAME
    `Get-CimInstance Win32_Process` mechanism already established throughout this session for PID
    verification (no new dependency)."""
    result = subprocess.run(
        [
            "powershell", "-NoProfile", "-Command",
            f"(Get-CimInstance Win32_Process -Filter \"ProcessId={pid}\").CommandLine",
        ],
        capture_output=True, text=True, timeout=15,
    )
    output = result.stdout.strip()
    return output if output else None


def verify_process_identity(record: ProcessIdentityRecord, *, markers: tuple[str, ...] = _IDENTITY_MARKERS) -> bool:
    """`True` only if PID `record.pid` is CURRENTLY running AND its real, freshly-queried command line
    contains every expected marker. A PID that no longer exists, or that exists but belongs to an
    unrelated process (Windows reused the number after our process exited), both return `False` --
    "nu omorî niciodată un PID fără verificarea command line/executable" is enforced HERE, not left to
    the caller to remember to check."""
    live_command_line = query_process_command_line(record.pid)
    if live_command_line is None:
        return False
    return all(marker in live_command_line for marker in markers)
