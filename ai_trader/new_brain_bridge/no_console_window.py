"""RT-NEW-BRAIN-ARCH-0001 section 35: a single shared `subprocess.run`/`Popen` kwarg to stop this
codebase's periodic child-process launches (watchdog's `powershell` identity check, the N1-incremental
worker, the tower worker) from popping a visible console window and stealing foreground focus on
Windows -- the concrete cause identified for a user-observed recurring transient CMD window.

`CREATE_NO_WINDOW` only exists on `subprocess` when running under Windows; `getattr(..., 0)` makes this
a no-op everywhere else (this codebase's tests run on Windows too, but nothing here should hard-crash a
non-Windows import). Purely additive: affects OS-level window visibility only, never captured
stdout/stderr, return codes, or timing."""

from __future__ import annotations

import subprocess

NO_CONSOLE_WINDOW_CREATIONFLAGS: int = getattr(subprocess, "CREATE_NO_WINDOW", 0)
