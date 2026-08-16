"""ALPHA DISCOVERY — PERMANENT DETACHED SERVICE wrapper.

Runs the alpha_loop forever (until a PAUSED_BY_CEO flag), auto-recovering from crashes, resuming from
the last checkpoint (idempotent by run_hash — never re-runs a finalized candidate). Designed to run
DETACHED via Windows Task Scheduler (like AI Trader's processes) so it survives chat-session close.

Uses DURABLE code snapshots (C:\\Users\\MEDION GAMING\\.alpha_vendor\\...) — NOT the session scratchpad,
which is cleaned per session. Niced (below-normal priority) so AI Trader keeps CPU priority.

Heartbeat + log are written to loop_state/ so liveness is verifiable from OUTSIDE the chat:
  loop_state/service_heartbeat.json   — {ts, pid, cycles, m_total, loop_state, phase}
  loop_state/service.log              — append-only log

Stop: create loop_state/PAUSED_BY_CEO (any content) → the service exits cleanly at the next cycle.
"""
from __future__ import annotations
import os, sys, json, time, traceback

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(_HERE)
os.chdir(_REPO)
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

# DURABLE snapshots (survive session close)
os.environ.setdefault("RATIFIED_CODE_DIR", r"C:\Users\MEDION GAMING\.alpha_vendor\ratified_code")
os.environ.setdefault("CANONICAL_CODE_DIR", r"C:\Users\MEDION GAMING\.alpha_vendor\canonical_code")

STATE_DIR = os.path.join(_HERE, "loop_state")
os.makedirs(STATE_DIR, exist_ok=True)
HB = os.path.join(STATE_DIR, "service_heartbeat.json")
LOG = os.path.join(STATE_DIR, "service.log")
PAUSE_FLAG = os.path.join(STATE_DIR, "PAUSED_BY_CEO")
CYCLE_SLEEP = 45     # seconds between cycles when idle (grid exhausted) — niced, CPU-yielding


def _log(msg):
    line = f"{int(time.time())} {msg}\n"
    with open(LOG, "a") as f:
        f.write(line)


def _hb(cycles, m_total, loop_state, phase):
    tmp = HB + ".tmp"
    with open(tmp, "w") as f:
        json.dump(dict(ts=int(time.time()), pid=os.getpid(), cycles=cycles, m_total=m_total,
                       loop_state=loop_state, phase=phase, detached=True), f, indent=2)
    os.replace(tmp, HB)


STALE_S = 180


def _pid_alive(pid):
    try:
        os.kill(pid, 0); return True
    except (OSError, ProcessLookupError):
        return False


def _is_alpha_service(pid):
    """Verify a PID is THIS service (never AI Trader) before any controlled restart."""
    try:
        import psutil
        cl = " ".join(psutil.Process(pid).cmdline())
        return "alpha_service" in cl
    except Exception:
        return False


def _owner_status():
    """Returns ('owned_alive', pid) | ('stalled', pid) | ('free', None). Real watchdog: a live PID with a
    STALE heartbeat is a frozen process (STALLED), not a valid owner."""
    try:
        hb = json.load(open(HB)); pid = hb.get("pid"); age = int(time.time()) - hb.get("ts", 0)
        if pid and pid != os.getpid() and _pid_alive(pid):
            return (("owned_alive", pid) if age < STALE_S else ("stalled", pid))
    except Exception:
        pass
    return ("free", None)


def main():
    owner, pid = _owner_status()
    if owner == "owned_alive":
        _log(f"pid={os.getpid()} exiting — pid {pid} owns the loop, heartbeat fresh (singleton)")
        return
    if owner == "stalled":
        if _is_alpha_service(pid):        # controlled restart ONLY after exact-identity verification
            try:
                os.kill(pid, 9); _log(f"ALPHA_SERVICE_STALLED: pid {pid} frozen (stale heartbeat) — killed; taking over")
            except Exception as e:
                _log(f"could not kill stalled pid {pid}: {e}")
        else:
            _log(f"stale heartbeat pid {pid} is NOT alpha_service (or unverifiable) — NOT killing (never touch AI Trader); taking over")
    try:
        import psutil  # optional: lower priority further
        psutil.Process(os.getpid()).nice(psutil.BELOW_NORMAL_PRIORITY_CLASS if os.name == "nt" else 19)
    except Exception:
        pass
    _log(f"SERVICE START pid={os.getpid()} detached (took ownership)")
    cycles = 0
    while True:
        if os.path.exists(PAUSE_FLAG):
            _log("PAUSED_BY_CEO flag found — exiting cleanly")
            _hb(cycles, _mtot(), "PAUSED_BY_CEO", "stopped")
            return
        cycles += 1
        try:
            from edge_research.alpha_loop import run
            _hb(cycles, _mtot(), "ACTIVE", "run")
            rep = run()                       # processes pending grid (idempotent); returns quickly if none
            _log(f"cycle {cycles}: processed={rep.get('processed_this_run')} m_total={rep.get('m_total')} "
                 f"grid_remaining={rep.get('grid_remaining')} shortlist={len(rep.get('ACTIVE_PROVISIONAL_SHORTLIST', []))}")
            _hb(cycles, rep.get("m_total"), rep.get("status", "ACTIVE"), "idle" if not rep.get("grid_remaining") else "run")
        except Exception as e:
            _log(f"cycle {cycles} ERROR (auto-recover): {e}\n{traceback.format_exc()[:800]}")
            _hb(cycles, _mtot(), "ACTIVE", f"recovered_from_error")
        time.sleep(CYCLE_SLEEP)


def _mtot():
    try:
        return json.load(open(os.path.join(STATE_DIR, "loop_state.json"))).get("m_total")
    except Exception:
        return None


if __name__ == "__main__":
    main()
