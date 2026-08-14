"""Console-script entrypoint (`ve-tower-worker`, see `pyproject.toml`'s `[project.scripts]`). This is the
ONLY supported way to start the worker -- installed into the tower venv's `Scripts/` directory by a
non-editable `pip install .`, so at runtime it is invoked as `<tower_venv>\\Scripts\\ve-tower-worker.exe`,
never as `python -m` against a path inside the AI Trader repository (see `env/launch_tower_worker.ps1`).

Order of operations is deliberate: the startup audit (`startup_audit.enforce_startup_audit`) runs BEFORE
any other import in this package that isn't already loaded -- `protocol`, `server`, and `decision` are
already imported by the time `main()` runs (Python resolves imports at module load), but the audit itself
inspects `sys.path`/`sys.modules` as they stood at process start, before this script did any importing of
its own beyond the stdlib -- so a contaminated launch is caught even though the check runs a few lines
into `main()`, not literally the first bytecode executed.
"""

from __future__ import annotations

import argparse
import signal
import sys
from types import FrameType

from ve_tower_worker.decision import real_decision
from ve_tower_worker.server import TowerWorkerServer
from ve_tower_worker.startup_audit import TowerWorkerStartupFailed, enforce_startup_audit

DEFAULT_PORT = 8765


def _install_signal_handlers(server: TowerWorkerServer) -> None:
    def _handle(signum: int, frame: FrameType | None) -> None:
        server.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, _handle)
    signal.signal(signal.SIGTERM, _handle)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ve-tower-worker")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args(argv)

    try:
        enforce_startup_audit()
    except TowerWorkerStartupFailed as exc:
        print(str(exc), file=sys.stderr)
        return 1

    server = TowerWorkerServer(host=args.host, port=args.port, decision_fn=real_decision)
    _install_signal_handlers(server)
    print(f"TOWER_WORKER_READY host={server.host} port={server.port}", flush=True)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
