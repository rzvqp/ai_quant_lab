# ve_tower worker — isolated, IPC-only

CEO mandate, 2026-08-14: "TOWER WORKER IZOLAT. Forma same-process e PROHIBITA." This package hosts
`ve_tower` (N3/N4: market map, levels, confirmation) in its own OS process, its own Python 3.12 venv, and
its own dependency set, reachable from AI Trader only over a local, versioned TCP IPC boundary. It never
imports `ai_trader`; it is never installed into the AI Trader venv (`venv/` at the repo root).

## Why

The AI Trader repo's own `vendor_bridge.py` files (`structural_observer`, `pdh_pdl_demo`,
`multi_policy_live`, `spread_collection`, `zone_observer`) each insert a vendored code directory at
`sys.path[0]` and bare-import from it. Nine names are confirmed already live that way in the running
processes today: `market_state`, `market_structure`, `order_flow`, `institutional_levels`,
`imbalance_mechanics`, `interactions`, `pdh_pdl_demo_engine`, `session_levels`, `order_block_void` (see
`AI_TRADER_VE_TOWER_RUNTIME_INVENTORY.md`). If `ve_tower`'s own bootstrap shares any of those names,
running it in the same process/venv risks a silent, import-order-dependent substitution. Separately, this
machine has one Python installation (3.14.6) -- newer than either `ve_brain`'s stated 3.11 or `ve_tower`'s
stated 3.12 -- and `ve_tower`'s own numpy/pandas requirement is unverified against it. Isolation removes
both risks structurally rather than managing them at runtime.

## Layout

```
tower_worker/
  pyproject.toml            # ve-tower-worker, console-script entrypoint, zero declared dependencies
  src/ve_tower_worker/
    startup_audit.py        # the nine-host-name + repo-path self-check, enforced first in cli.main
    protocol.py              # wire format: TowerRequest/TowerResponse, no pickle, 4-byte length-prefixed JSON
    server.py                 # TCP loopback listener (127.0.0.1 only)
    decision.py                # the ve_tower seam -- returns TOWER_UNAVAILABLE today (ve_tower not installed)
    decision_stub.py            # FAKE, isolation-test-only, never wired into cli.main
    cli.py                        # `ve-tower-worker` entrypoint: audit -> serve
  tests/                     # run under the TOWER venv's own pytest, never the main venv's
  env/
    requirements.lock       # numpy==2.5.1 + pandas==3.0.3, SHA-256 pinned, matches the main venv's own pins
    install_tower_env.ps1   # reproducible: installs Python 3.12 if absent, creates the venv, hash-locked deps, non-editable package install
    rollback_tower_env.ps1  # deletes the venv directory -- nothing else to unwind
    verify_tower_wheel.py   # SHA-256 pre-install gate for the eventual ve_tower wheel (see below)
    launch_tower_worker.ps1 # -I, cleared PYTHONPATH, CWD outside the repo, installed entrypoint
```

The isolated venv itself lives OUTSIDE this repository: `C:\Users\MEDION GAMING\ve_tower_venv`.

## What exists today (2026-08-14)

- Python 3.12.10 installed via the official `py install` manager (signature-verified against
  python.org's own index), alongside the existing 3.14.6 -- additive, nothing removed or changed.
- The isolated venv created, numpy==2.5.1/pandas==3.0.3 installed hash-verified from `requirements.lock`
  (versions deliberately matched to the main venv's own already-proven pins).
- `ve-tower-worker` built as a real wheel and installed non-editably into that venv -- the entrypoint runs
  entirely from site-packages, no path back to this repo.
- **`ve_tower` itself is NOT installed anywhere.** 0.1.0 was rejected (`TOWER_HANDOFF_FAIL`); no repaired
  version exists yet. `decision.real_decision` reflects this honestly: it returns `TOWER_UNAVAILABLE`
  today, which is correct production behavior, not a stand-in for one.
- The main AI Trader venv (`venv/`) is verified byte-identical (same package set, same versions) to its
  state before this segment -- see `AI_TRADER_TOWER_WORKER_ISOLATION_REPORT.md`.

## Post-`TOWER_HANDOFF_PASS` procedure (NOT executed -- documentation only, per explicit CEO instruction)

1. Red Team verifies the delivered wheel's SHA-256, size, and filename.
2. Those three values get written into `env/verify_tower_wheel.py`'s `PINNED_TOWER_WHEEL_SHA256` /
   `PINNED_TOWER_WHEEL_SIZE_BYTES` / `PINNED_TOWER_WHEEL_FILENAME` (currently all `None` -- the script
   fails closed, refusing to verify anything, until this step happens).
3. Run `venv\Scripts\python.exe tower_worker\env\verify_tower_wheel.py <path-to-wheel>` (main venv, since
   this script reuses `ai_trader.mandate2_readiness.wheel_verification.verify_wheel_hash` -- an
   admin/build-time check, never something the isolated worker itself runs).
4. On PASS only: `& "C:\Users\MEDION GAMING\ve_tower_venv\Scripts\pip.exe" install --no-deps <wheel>` --
   **the tower venv ONLY.** Never `venv\Scripts\pip.exe` (the main AI Trader venv). Do not rebuild the
   wheel from source; install exactly the artifact whose hash was verified.
5. Replace `decision.real_decision`'s `NotImplementedError` body with the real call into `ve_tower`'s own
   ratified API -- the only code change this step requires; `protocol.py`, `server.py`, `startup_audit.py`,
   `cli.py`, and the client side (`tower_client.py`/`tower_protocol.py`) need none.
6. Run the full canonical fixture suite through the real IPC path (real worker subprocess, real
   `TowerClient`, `ve_tower`'s own ratified fixtures) -- not the `decision_stub.fake_decision` stand-in,
   which stops being used at this point.
7. Still gated on a **separate, later** Red Team verification before the authority switch or
   `bridge.py`'s hardcoded `market_map_available=False`/`levels_available=False`/
   `confirmation_available=False` change -- both remain explicitly out of scope until then.

Authority stays `NEACTIVATA`. `LIVE_SHADOW` does not start from any part of this document.
