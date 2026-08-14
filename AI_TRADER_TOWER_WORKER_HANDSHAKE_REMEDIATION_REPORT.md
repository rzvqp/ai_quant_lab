# AI Trader — Tower Worker Handshake Remediation (Red Team `TOWER_HANDOFF_CONDITIONAL`)

**Date**: 2026-08-14. Red Team verdict on `ve_tower` 0.3.0: PASS on all material points; VE enters
`WAITING`. Three remediations, exclusively AI Trader's own: worker identity handshake, bounded cache,
mandatory loopback. **`ve_tower` 0.3.0 remains NOT installed anywhere.** `STAGED_INSTALL` stays
unauthorized until this report is revalidated by Red Team and the CEO explicitly authorizes it.

## Status requested: `READY_FOR_TOWER_PHASE1_REVALIDATION`

## 1. Worker identity handshake

**Protocol bumped to v2** (`tower_worker/.../protocol.py` and its deliberately-duplicated client copy,
`ai_trader/new_brain_bridge/tower_protocol.py`) — a `type` discriminator (`handshake` vs `n3n4_request`)
now routes every frame; every N3/N4 response carries `session_id` + `worker_identity_fingerprint`.

**Two independent sources of truth, per the CEO's own correction** — never conflated:
- **Session possession (HMAC)**: the launching parent (`TowerWorkerLauncher`) generates a fresh
  `session_id` and a 32-byte cryptographically random `session_secret` **before** spawning the worker,
  hands both off over the worker's own **stdin** (never argv, never the TCP socket) immediately after
  `Popen`. The worker reads exactly one JSON line at startup, before binding anything. On handshake, the
  client sends a fresh random challenge; the worker computes
  `HMAC-SHA256(secret, challenge + canonical_identity_json + session_id)` and returns it plus its real
  identity; the client independently recomputes the same HMAC with its own copy of the secret and
  `hmac.compare_digest`s the result. A responder that doesn't know the secret — the exact "server fals"
  defect Red Team demonstrated — can never produce a matching HMAC, regardless of how plausible its
  claimed fields look (`test_tower_launcher.py::test_1`).
- **Artifact identity (`tower_identity_pin.verify_pin`)**: field-by-field comparison against a versioned,
  committed pin — `ve_tower_package_version=0.3.0`, `package_build_commit=6daf2aa`,
  `state_delivery_commit=0207ffa` (kept SEPARATE from `package_build_commit`, per the CEO's own
  correction), `wheel_sha256=0c2581c0...`. **`vendored_source_identity`, `n3_contract_version`, and
  `n4_contract_version` are `None` — PENDING, not fabricated.** `verify_pin` fails closed on any `None`
  expected field, so the handshake genuinely cannot pass today even once `ve_tower` is installed, until
  VE's manifest supplies these three values. Disclosed as a real, standing blocker for Phase 2, not
  something this remediation resolves on its own.

**The worker never trusts what a client sends for its own identity.** `artifact_identity.py` reads
`importlib.metadata.version("ve_tower")` (today: `None` — not installed) and an `InstallManifest`
(`install_manifest.py`) written **only after** `verify_tower_wheel.py`'s SHA-256 check passes, living in
the tower venv's own root (`<venv>/ve_tower_install_manifest.json`) — no such manifest exists yet, so
every `ve_tower`-derived field is honestly `None` today. `server.py`'s `_stamp_session` is the ONE place
`session_id`/`worker_identity_fingerprint` become authoritative on outgoing responses, unconditionally
overwriting whatever `decision_fn` returned — `decision.py`/`decision_stub.py` stay session-unaware by
construction, eliminating an entire class of "decision logic accidentally forges its own identity" bugs.

**Session binding on every response, not only at handshake time**: `TowerClient` checks
`response.session_id`/`worker_identity_fingerprint` against the ONE established session on every single
N3/N4 reply — a stale/wrong/old-session response is refused (`STALE_SESSION`) even if every other field
matches perfectly. Proven for real: `test_tower_isolation.py::test_6_response_from_the_previous_sessions_worker_after_restart_is_refused`
spins up two REAL, sequential worker subprocesses and confirms a client bound to session A is refused by
session B's real, honest response.

**Port**: the worker binds `port=0` (OS-assigned) by default; the launcher never assumes a fixed port —
it reads the real bound port back from the worker's own stdout (the controlled channel). An explicitly
requested port that's already occupied by an unrelated process causes `TOWER_WORKER_STARTUP_FAILED`
(worker's own `bind()` fails) — the launcher never proceeds to handshake against the occupier
(`test_tower_launcher.py::test_7`, real, against a real pre-bound socket).

## 2. Cache — bounded, deterministic

`ai_trader/new_brain_bridge/tower_cache.py::BoundedTowerCache` replaces the unbounded dict. Explicit
`max_entries`, explicit `ttl_seconds`, `OrderedDict`-based LRU eviction, `clear()` called by
`TowerClient.bind_session()` on every session change/restart, `CacheMetrics` (size/hits/misses/evictions).
Verified both via direct API (`test_10_cache_never_exceeds_max_entries_via_direct_api`) and after 5,000
puts against a 100-entry cache (`test_10_cache_never_exceeds_max_entries_after_thousands_of_puts` —
exactly Red Team's own reproduction scale): size stays at 100, evictions land at exactly 4,900, LRU order
verified (not insertion order). TTL eviction proven with an injectable clock (`test_11_ttl_evicts_entries`).

**Request-ID-reuse rule, kept separate from normal caching**: same `request_id` + same fingerprint →
cached result (a genuine retry). Same `request_id` + different fingerprint → refused explicitly with
`REQUEST_ID_REUSE_MISMATCH`, before any network I/O
(`test_same_request_id_different_payload_is_refused_before_any_network_io`).

## 3. Loopback — mandatory, structural

`TowerWorkerServer.__init__` (worker) and `TowerWorkerLauncher.__init__` (client) both check `host` against
an explicit allowlist (`("127.0.0.1",)` — `::1` deliberately NOT implemented, per the CEO's own "optional...
daca e implementat si testat corect": adding untested IPv6 support would be exactly the kind of
half-verified addition this remediation exists to eliminate) **before any socket is touched**.
`--host 0.0.0.0` and any other non-loopback address raise `NonLoopbackBindError`/`ValueError`
(`NON_LOOPBACK_BIND_FORBIDDEN`) at construction — proven on both sides
(`test_zero_dot_zero_dot_zero_dot_zero_bind_is_forbidden`, `test_external_looking_address_bind_is_forbidden`,
worker-side; `test_14`/`test_15`, launcher-side) — never merely a default value that could be overridden.

## The 18 decisive tests

| # | Property | Evidence |
|---|---|---|
| 1 | server fals cu protocol corect → refuz | `test_tower_launcher.py::test_1` |
| 2 | worker cu versiune veche → refuz | `test_tower_launcher.py::test_2` |
| 3 | wheel hash diferit → refuz | `test_tower_launcher.py::test_3` |
| 4 | contract N3 sau N4 diferit → refuz | `test_tower_launcher.py::test_4` |
| 5 | alt session_id → refuz | `test_tower_launcher.py::test_5` |
| 6 | raspuns din sesiune anterioara dupa restart → refuz | `test_tower_isolation.py::test_6` (real, two sequential real workers) + `test_tower_client.py::test_response_from_a_different_session_is_refused` |
| 7 | port ocupat de alt proces → clientul NU se conecteaza | `test_tower_launcher.py::test_7` (real) |
| 8 | handshake valid → acceptat | `test_tower_launcher.py::test_8` (real, stub identity + monkeypatched pin) |
| 9 | N3/N4 response FARA worker identity → refuz | `test_tower_launcher.py::test_9` |
| 10 | cache nu depaseste limita | `test_tower_cache.py::test_10_*` (direct API + 5,000-request scale) |
| 11 | TTL elimina intrarile | `test_tower_cache.py::test_11_ttl_evicts_entries` |
| 12 | restart goleste cache-ul | `test_tower_client.py::test_bind_session_clears_the_cache` |
| 13 | acelasi request ID cu alt payload → refuz | `test_tower_client.py::test_same_request_id_different_payload_is_refused_before_any_network_io` |
| 14 | 0.0.0.0 → refuz | `test_server_roundtrip.py` + `test_tower_launcher.py::test_14` |
| 15 | adresa externa → refuz | `test_server_roundtrip.py` + `test_tower_launcher.py::test_15` |
| 16 | loopback → acceptat | `test_server_roundtrip.py` + `test_tower_launcher.py::test_16` |
| 17 | worker crash → AI Trader ramane VIU si produce NO_TRADE/TOWER_UNAVAILABLE | `test_tower_launcher.py::test_17`, `test_tower_isolation.py::test_worker_crash_*` (real) |
| 18 | venv-ul principal ramane NEMODIFICAT | see below |

## Full test results

- Tower venv (`ve_tower_venv`): **31 passed**, `mypy --strict` clean across 13 files.
- Main venv, `new_brain_bridge` alone: **98 passed**, `mypy --strict` clean across 31 files.
- Main venv, scoped regression (`new_brain_bridge` + `mandate2_readiness` + `pdh_pdl_demo` +
  `multi_policy_live` + `structural_observer`): **331 passed, 4 skipped** (the same 4 genuinely
  `BLOCKED_ON_TOWER_HANDOFF` tests, unchanged), zero failures, zero new skips.

## Item 18 — main venv unchanged

`pip freeze` (main venv), diffed against the snapshot captured before this whole tower-worker effort began
(`AI_TRADER_VE_TOWER_RUNTIME_INVENTORY.md`): **identical**, package for package, version for version. The
only line that differs at all is `ve_brain`'s own `file://` install-source URI, which differs solely in a
session-local temp path string — its package name, version, and SHA-256 pin are byte-identical. Confirmed
again just now, after this entire remediation.

## `bridge.py` still not connected. Authority still `NEACTIVATA`. `LIVE_SHADOW` still does not start.

`test_bridge_py_does_not_yet_call_the_tower_client` (unchanged from the prior segment) continues to pass —
`bridge.py`'s `market_map_available=False`/`levels_available=False`/`confirmation_available=False` hardcodes
are untouched. `set_authority()` is never called anywhere.

## Rollback

Nothing operational to roll back — no live process touched, no install performed. If this commit's own
changes needed reverting: `git revert` is safe and mechanical (every change is additive: new modules, new
optional dataclass fields with the server always stamping them, no existing function lost a parameter).
The tower venv itself can be rebuilt from scratch via `tower_worker/env/install_tower_env.ps1` +
`pip install --no-deps tower_worker/` at any time; nothing in it is hand-edited state.

## Worker/protocol versions

- `ve_tower_worker` package version: `0.2.0`.
- IPC protocol version: `2.0` (bumped from `1.0` — breaking change: handshake frames, `type` discriminator,
  `session_id`/`worker_identity_fingerprint` on every response).
- `worker_build_commit`: pinned in a follow-up commit immediately after this one, to the exact commit hash
  this remediation produced (see `artifact_identity.py`'s own docstring for why that's necessarily two
  steps).
