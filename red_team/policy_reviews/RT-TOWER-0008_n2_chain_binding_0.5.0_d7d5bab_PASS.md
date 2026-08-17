# RED TEAM — N2 CHAIN BINDING · DELTA revalidation of ve_tower 0.5.0
### RT-TOWER-0008 · **N2_HANDOFF_PASS · N2_CHAIN_BINDING_PASS**
**Date:** 2026-08-17 · **Auditor:** Red Team · **Artefact:** `ve_tower 0.5.0`, wheel `ve_tower-0.5.0-py3-none-any.whl` SHA-256 `6d99baf62f9a245031722a3b59c4df59b98211707c26d587641eff424cd94df7`, build `b128d8b`, delivery `d7d5bab` (HEAD), wheel-commit `26470f5`, sidecar `HANDOFF_MANIFEST-0.5.0.json`. Predecessor verdict: **RT-TOWER-0007 N2_HANDOFF_CONDITIONAL · N2_CHAIN_BINDING_REQUIRED** (`4a16c9a`). **DELTA review — N2 already accepted; provenance/semantics not reopened (no new defect found).** No engine modified; SYNTHETIC data only; instrumentation was observe/attack-only; nothing changed outside `red_team/`.

# VERDICT — **N2_HANDOFF_PASS · N2_CHAIN_BINDING_PASS**
The RT-TOWER-0007 gap is **closed structurally.** 0.5.0 adds `run_tower_chain`, a versioned in-artefact orchestrator that runs N2→N3→N4 **internally**, deriving `n2_fingerprint`/`bias_available`/the N3 identity **exclusively from the executed functions**. The caller can no longer control the N2→N3 link: `ChainRequest` **has no such fields** (structural), and `parse_chain_request` **rejects any unknown field** (`UNKNOWN_REQUEST_FIELD`). Every PASS condition is met and independently verified from the installed wheel (32/32 Red Team checks + 68/68 artefact tests).

---

## §1 — ARTEFACT IDENTITY · PASS
Wheel SHA-256 `6d99baf…94df7` **exact**; **git-stored bytes == working wheel**. Build `b128d8b` ("chain orchestrator run_tower_chain, remediate N2_CHAIN_BINDING RT-TOWER-0007"); wheel physically committed at `26470f5`; delivery HEAD `d7d5bab` ("stamp manifest state_delivery_commit 26470f5"). METADATA `0.5.0`, `py>=3.12`, `numpy>=1.24`/`pandas>=2.0`. **Sidecar describes the wheel exactly** (version, `package_build_commit=b128d8b`, `state_delivery_commit=26470f5`, `wheel_sha256=6d99baf…94df7`, `production_entrypoint=run_tower_chain`, `unbound_direct_api=[run_n2,run_n3,run_n4]`, chain/N2/N3/N4 contract versions, `tower_chain_binding_version=tower-chain-binding-v1`, 13 `vendored_blob_sha1`, `vendored_source_identity=sha256:4c0dee…69e1c`, predecessor wheels 0.4.0/0.3.0). Clean-venv install → import **only from site-packages**; **smoke test `run_tower_chain` runs from the installed wheel**. **Complete pin:** package `0.5.0` · build `b128d8b` · delivery `26470f5`/`d7d5bab` · wheel SHA · `vendored_source_identity` · N2 `tower-n2-request-v1` / N3 `tower-n3-request-v2` / N4 `tower-n4-request-v2` · chain req/resp `tower-chain-request-v1`/`tower-chain-response-v1` · `TOWER_CHAIN_BINDING_VERSION=tower-chain-binding-v1` · `PRODUCTION_ENTRYPOINT=run_tower_chain` · deps pinned.

## §2 — DELTA 0.4.0 → 0.5.0 · PASS (limited, semantics unchanged)
Module-by-module diff: **NEW** `chain.py`; **DIFFER** `__init__.py`, `contracts.py` (chain contract + `parse_chain_request`), `reason_codes.py` (chain codes), `version.py` (pin). **SAME (byte-identical):** all 13 vendored `_tower/*`, **`n2.py`, `n3.py`, `n4.py`**, `canonical.py`, `data_identity.py`, `fingerprint.py`, `_bootstrap.py`. **N2/N3/N4 contracts unchanged.** All 13 vendored modules **git-anchored to the installed wheel** (`git rev-parse <commit>:code/<mod>.py` == `git hash-object <site-packages>/_tower/<mod>.py`, 13/13) — `bias_h1`@`850815f`, `zone_map`@`5888978`, `zone_confirmation`@`7f2694f` untouched. ve_brain / N1 / Router / EV / N6 absent from the wheel → untouched.

## §3 — DECISIVE INJECTION TEST · PASS (structurally impossible + explicitly rejected)
From the installed wheel: `ChainRequest` **has no** `n2_fingerprint`/`bias_available`/`output_fingerprint`/`n2`/`n3` field (introspected). Every caller injection attempt is stopped **before any node runs**:
- `parse_chain_request({…, n2_fingerprint: real / "LONG" / "placeholder" / "" / deadbeef×8})` → **`UnknownRequestFieldError`**; same for `bias_available=True`, `output_fingerprint="invented"`, a caller-built `n2` payload.
- `ChainRequest(**{…, n2_fingerprint:"x"})` → **`TypeError`** (no such field).
**None of these values can reach `run_n3`.** The caller cannot control the N2→N3 link at all.

## §4 — REAL ORCHESTRATION · PASS (independently instrumented)
Wrapping `chain.run_n2/run_n3/run_n4` with call-through spies (observe only) over a full `run_tower_chain`:
- **N3 receives EXACTLY the executed N2's `output_fingerprint`** (`n3_req.n2_fingerprint == n2_resp.output_fingerprint`, `6ac880c4…` == `6ac880c4…`).
- **`bias_available` into N3 comes from the executed N2**, not the caller.
- **N4 is bound to the executed N3 response**: `n4_req.n3_event_fingerprint == n3_resp.event_fingerprint` (`292a8486…`), `n3_node_input_fingerprint` matches, `level` = `n3_resp.market_map[0].price_anchor`, `n2_fingerprint` = the real N2 output.
- **Attack — substitute an intermediate:** monkeypatching `run_n3` to return a response with a forged `event_fingerprint` → `run_tower_chain` returns **`chain_identity_mismatch`**. The chain **detects and refuses** a substituted intermediate; a real caller cannot even reach this (no response field on `ChainRequest`).

## §5 — CHAIN IDENTITY · PASS (independently recomputed)
`ChainResponse` preserves `market_event_id`, `correlation_id`, `configuration_fingerprint`, `tower_version=0.5.0`, `chain_binding_version=tower-chain-binding-v1`, chain contract, N2(`data_identity`+`node_input_fingerprint`+`output_fingerprint`), N3(`data_identity`+`node_input_fingerprint`+`event_fingerprint`), N4(`data_identity`+`node_input_fingerprint`+`event_fingerprint`+N3-link), `strategy_id`, `chain_fingerprint`, `terminal_reason_code`, `chain_status`. **`chain_fingerprint` independently recomputed** via the documented composition → exact match (`86a6f0d8…`). Sensitivity: changing `market_event_id` / `configuration_fingerprint` / `strategy_id` / any H1 bar each changes `chain_fingerprint`.

## §6 — FAIL-CLOSED CASCADE · PASS
N2 unavailable (regime all-unavailable) → `n2_unavailable`, **n3=None, n4=None**, factors=(), `output_fingerprint=None` (**no fabricated LONG**). N3 unavailable (M15 stale) → `n3_unavailable`, **n4=None**. N4/empty-map/M5-stale → `n4_unavailable`, `confirmation_available=False` (no fabrication). Incompatible chain contract → `incompatible_contract`. H1 non-finite → `non_finite_value`; missing H1 source → `source_identity_missing`. Substituted intermediate identity → `chain_identity_mismatch` (§4). **Zero fallback, zero default LONG, zero probability from N2, zero fabricated node.**

## §7 — PRODUCTION SURFACE · PASS
`PRODUCTION_ENTRYPOINT = "run_tower_chain"`; `UNBOUND_DIRECT_API = ("run_n2","run_n3","run_n4")` (compat/research, marked). `run_tower_chain` builds every intermediate request **internally from executed results**, never from client-supplied identities, and cannot be bypassed via `ChainRequest`. **No forbidden imports** (import-statement grep over the installed wheel: no `market_intelligence`/`ai_trader`/`risk`/`execution`/`broker`; `chain.py` imports only ve_tower internals). No Risk Manager / Execution Adapter / broker / `order_send`.

## §8 — TESTS & COMPATIBILITY · PASS
- **68 tests, 0 failures** (matches VE's 68). **15 chain tests** (matches). Negative tests present: structural injection (`test_caller_cannot_supply_n2_fingerprint_structural`), unknown-field rejection, `test_n3_uses_exactly_n2_output_fingerprint` (real vs forged), cascades (N2/N3), no-default-LONG, incompatible-contract, NaN, missing-source, fingerprint determinism + identity/bars sensitivity, `test_production_entrypoint_is_chain_only`, `test_no_forbidden_imports_in_tower`.
- **mypy `--strict` on the 12 top-level modules: clean (exit 0)** — independently re-run (VE's claim verified).
- **Upgrade 0.4.0→0.5.0 reproducible; rollback 0.5.0→0.4.0 reproducible** (`run_tower_chain` gone at 0.4.0). AI Trader main venv untouched (this work used the separate sandbox tower venv).
- **Non-blocking hardening note (not a defect):** the committed suite has no explicit regression test that a *substituted intermediate N3/N4 response* yields `CHAIN_IDENTITY_MISMATCH` — that defensive guard is unreachable by a real caller (no response field on `ChainRequest`) and I verified it works via my own monkeypatch attack. Recommend VE add a committed test so the guard cannot silently regress.

---

## AUTHORIZATION (automatic on PASS)
AI Trader may now, in sequence: resume from `54cf26e`; install **exactly** `ve_tower-0.5.0-py3-none-any.whl` (`6d99baf…94df7`) **only** in the tower venv; update the pin + handshake; use **exclusively `run_tower_chain`**; remove `bias_direction="LONG"` and all synthetic N2 fingerprints; produce the **single correlated path**; run the full regression; deliver `READY_FOR_LIVE_SHADOW_REVIEW_CANDIDATE_V2_CORRELATED`. That correlated-chain delivery is the next, separate review (the RT-MANDATE2 track).

## STANDING CONSTRAINTS (reaffirmed)
**Do NOT start LIVE_SHADOW. Do NOT activate authority. Broker stays DISABLED. AI Trader stays HOLD until the correlated-chain verdict. Alpha stays `ALPHA_BLOCKED_CANONICAL_N1_HANDOFF`. CAND-T05 frozen.** Red Team modified no engine, ran no real market data, changed nothing outside `red_team/`.
