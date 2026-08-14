# AI Trader — Isolated `ve_tower` Worker Infrastructure

**Date**: 2026-08-14. CEO mandate: "TOWER WORKER IZOLAT. Forma same-process e PROHIBITA." Built ahead of
VE's repaired `ve_tower` delivery, per explicit instruction: infrastructure only, nothing installed in
runtime. `ve_tower` 0.1.0 remains rejected (`TOWER_HANDOFF_FAIL`) and is NOT installed anywhere by this
segment's work.

## 1. Separate venv

- Python **3.12.10** installed via the official `py install` manager (signature verified against
  python.org's own `index-windows.json`) -- additive alongside the pre-existing 3.14.6, nothing removed.
- Isolated venv created at `C:\Users\MEDION GAMING\ve_tower_venv` (outside this repository).
- `numpy==2.5.1`, `pandas==3.0.3` installed via `pip install --require-hashes -r
  tower_worker/env/requirements.lock` -- SHA-256 pinned, versions deliberately matched to the main venv's
  own already-proven pins to minimize behavioral divergence between the two environments. Confirmed a
  hash-locked `--dry-run` reinstall resolves to exactly these versions with no drift.
- `tower_worker/env/install_tower_env.ps1` / `rollback_tower_env.ps1`: reproducible create-and-populate /
  delete-the-venv-directory. Rollback is trivial by construction -- the venv is a fully separate
  directory tree the main venv never references, so there is nothing to reconcile.
- `tower_worker/env/verify_tower_wheel.py`: SHA-256 pre-install gate for the eventual `ve_tower` wheel,
  reusing `mandate2_readiness.wheel_verification.verify_wheel_hash` (already built and tested for
  `ve_brain`'s own wheel). **Fails closed today** -- confirmed by direct run (`ARTIFACT_HASH_MISMATCH: no
  PINNED_TOWER_WHEEL_SHA256 recorded yet`), since no repaired wheel exists to pin against.
- `ve_tower` itself: confirmed **not installed** anywhere on this machine.

## 2. Isolated launch

`ve-tower-worker` built as a real wheel (`pip install --no-deps .`, non-editable) and installed into the
tower venv's own site-packages -- confirmed the installed `.exe` launcher and the package's own
`__file__` both resolve entirely inside `ve_tower_venv\`, with zero string reference to the AI Trader
repo path (verified via `strings` against the launcher binary).

`tower_worker/env/launch_tower_worker.ps1` invokes `<tower_venv>\Scripts\python.exe -I -m
ve_tower_worker.cli --port <port>` from a CWD outside the repo, with `PYTHONPATH` explicitly cleared
(redundant with `-I`'s own PYTHONPATH-ignoring behavior -- deliberate defense in depth, not reliance on a
single mechanism).

`startup_audit.py` runs first in `cli.main()`, checking (a) no AI Trader repo path anywhere in `sys.path`
and (b) none of the nine confirmed host module names already in `sys.modules`. Verified for real, twice,
by direct process launch:
- **Clean launch** (CWD = `C:\Users\MEDION GAMING`, no poisoned env): `TOWER_WORKER_READY host=127.0.0.1
  port=18765`.
- **Contaminated launch** (`PYTHONPATH` set to the AI Trader repo root): `TOWER_WORKER_STARTUP_FAILED: AI
  Trader repo path present in sys.path: C:\Users\MEDION GAMING\ai_quant_lab-research-main`, exit code 1.

## 3. Versioned IPC

Transport: **TCP loopback (`127.0.0.1` only) with a 4-byte big-endian length prefix + deterministic
(`sort_keys=True`) UTF-8 JSON, no pickle.** Rejected alternatives and why, documented in
`tower_worker/src/ve_tower_worker/protocol.py`'s own module docstring: `multiprocessing.connection` (its
convenience `send()`/`recv()` pickle by default -- a standing footgun avoided by not depending on the
module at all), named pipes (needs `pywin32` on Windows, adding a dependency to both venvs), gRPC/protobuf
(disproportionate for a minimal, auditable dependency surface).

Contract fields present in every request/response, exactly as specified: `protocol_version`,
`schema_version` (request and response versioned independently), `request_id`, `market_event_id`,
`event_fingerprint`, `data_identity`, `node_input_fingerprint`, `symbol`, `as_of`, `n1_output`,
`n2_output`, `m15_closed_bars`, `m5_closed_bars`, `strategy_id`/`strategy_version` (N4's strategy
identity), `tower_version`, `reason_codes`. `request_id` doubles as the correlation id.

Deliberately **duplicated, not shared**, between `tower_worker/.../protocol.py` (server) and
`ai_trader/new_brain_bridge/tower_protocol.py` (client) -- publishing a third package installed into both
venvs would quietly reintroduce a shared dependency surface between them, undermining the isolation this
whole architecture exists to enforce. `PROTOCOL_VERSION` is the real safety net against the two copies
drifting, not the import boundary.

## 4. Operational safety

Implemented in `ai_trader/new_brain_bridge/tower_client.py` (`TowerClient`) and
`ve_tower_worker/server.py`:

| Requirement | Implementation |
|---|---|
| timeout | `TowerClientConfig.timeout_seconds`, applied to the socket connect/send/recv |
| payload size limit | `MAX_PAYLOAD_BYTES` (4 MiB), enforced on send AND on the incoming length prefix (bounds allocation against a hostile/corrupt prefix before a single payload byte is read) |
| invalid response -> fail-closed | `MALFORMED_RESPONSE` -> `TowerUnavailableResult` |
| worker down -> NO_TRADE/TOWER_UNAVAILABLE | connection refused/timeout -> `CONNECTION_FAILED`; worker's own honest absence-of-`ve_tower` -> `TOWER_UNAVAILABLE` |
| restart controlled, health check | `TowerClient.health_check()` (bare connect-and-close, never raises); SIGINT/SIGTERM handled in `cli.py` for controlled shutdown |
| duplicate request -> idempotent | in-process cache keyed by `(request_id, event_fingerprint)` -- proven to never re-hit the network on a repeat call |
| request/response identity mismatch -> refuse | `RESPONSE_IDENTITY_MISMATCH` |
| late response for a different event -> refuse | `STALE_RESPONSE` (same `request_id`, different `event_fingerprint`) |
| zero fallback to `market_intelligence`/legacy, zero broker access | structural: `tower_client.py`/`tower_protocol.py` import neither, enforced by a static AST scan test |

Worker produces **only** N3/N4 -- structural, not a runtime check: the protocol carries no decision or
order fields at all.

**Not wired into `bridge.py`'s production path.** `market_map_available=False`, `levels_available=False`,
`confirmation_available=False` remain exactly as they were -- confirmed by a dedicated static test
(`test_bridge_py_does_not_yet_call_the_tower_client`).

## 5. Isolation tests

All nine items, all passing, all against the **real** worker subprocess and the **real** `TowerClient**
(not fakes) where the item calls for it:

1. **Host modules preloaded in main process, worker starts clean** — `structural_observer.vendor_bridge`
   imported for real in the test process (confirmed `market_state`/`market_structure` land in that
   process's own `sys.modules`), then the real worker subprocess launched and confirmed
   `TOWER_WORKER_READY`.
2. **Worker's modules never appear in the main process's `sys.modules`** — structural (separate OS
   process), asserted directly.
3. **Worker crash -> AI Trader stays alive, produces NO_TRADE** — real worker killed mid-session; the next
   `TowerClient.request_n3_n4` call returns `TowerUnavailableResult(reason=CONNECTION_FAILED)` without
   raising; the test process itself keeps running.
4. **Restart -> no duplication** — worker A stopped, worker B started fresh; both produce the same
   (`TOWER_UNAVAILABLE`, deterministic) result shape for the identical request — a restart never produces
   an inconsistent or duplicated answer.
5. **Incompatible protocol version -> fail closed** — a hand-crafted request with `protocol_version:
   "99.9"` sent to the real running worker; real response: `ok=false`,
   `reason_codes=(PROTOCOL_VERSION_MISMATCH,)`.
6. **Tampered fingerprint/identity in transit -> refuse** — the defense is identical regardless of cause
   (tampering, bug, or reuse); exercised directly against a fully controlled fake responder in
   `test_tower_client.py` (`test_response_identity_mismatch_is_refused`,
   `test_stale_response_same_request_id_different_event_is_refused`), cross-referenced from the isolation
   suite.
7. **Stopping the worker doesn't affect the 5 live processes** — proven structurally: a static AST scan
   (`test_tower_import_independence.py`) confirms `pdh_pdl_demo`, `multi_policy_live`, and
   `market_intelligence` import neither `tower_client` nor `tower_protocol` anywhere. No code path exists
   for a worker outage to reach.
8. **Main venv byte/dependency-identical before and after** — `pip freeze` captured before this segment
   (`AI_TRADER_VE_TOWER_RUNTIME_INVENTORY.md`) diffed against `pip freeze` now: **identical**, package for
   package, version for version (the one line that differs, `ve_brain`'s own `file://` URI, differs only
   in a session-local temp path in its install-source string — the package name, version, and SHA-256
   pin are byte-identical).

Test files: `tower_worker/tests/{test_startup_audit,test_protocol,test_server_roundtrip}.py` (tower venv,
21 tests) + `ai_trader/new_brain_bridge/tests/{test_tower_protocol,test_tower_client,test_tower_isolation,
test_tower_import_independence}.py` (main venv, 30 tests). All pass. `mypy --strict` clean in both venvs
(10 files tower-side, 25 files main-side, including all new modules).

## 6. After VE delivery (documented, not executed)

Full procedure in `tower_worker/README.md`'s own "Post-`TOWER_HANDOFF_PASS` procedure" section: Red Team
verifies SHA-256 -> pin recorded in `verify_tower_wheel.py` -> install EXACTLY that wheel, ONLY in the
tower venv, never rebuilt, never in the main venv -> wire `decision.real_decision`'s one `NotImplementedError`
body -> run the full canonical fixture suite through the real IPC path. Authority stays `NEACTIVATA`
throughout; `LIVE_SHADOW` does not start from any part of this document.

## Regression proof

`ai_trader/{new_brain_bridge,mandate2_readiness,pdh_pdl_demo,multi_policy_live,structural_observer}` —
**300 passed, 4 skipped** (the same 4 genuinely `BLOCKED_ON_TOWER_HANDOFF` tests, unchanged), zero
failures, zero new skips. The 5 live processes remain unrestarted and unmodified.
