# PROJECT STATE — AI Quant Lab (persisted by CEO order)

Repo `ai_quant_lab-wp5b` · branch `discovery-mk-matrix-v1` · mirrored to 4 remotes (alpha1/discovery/lab/trader).
This document is the Git-persisted snapshot of program status; the conversation is not the system of record.

## PRIORITY
- **COMPLETE_AI_TRADER** — the single active critical path.
- Alpha **PAUSED_BY_CEO**; Statistician and Data Acquisition **on pause**.

## BLOCKER
- **MANDATE_2_REVIEW_CONDITIONAL · INTEGRATION_BLOCKED**.
- **LIVE_SHADOW forbidden**.
- Cause: **N3 and N4 were never packaged** into an installable artifact (they lived only in `code/`).

## DELIVERED
- **ve_brain 0.1.3**, wheel built from `a1d2a6d`, **ARTIFACT_PIN_PASS**.
  - SHA-256 `edd208ad6c2c943b17a11759ece1fdf5ab2a7025779b191764c383ecce987d11`.
  - `validated_core_commit fbc0f20` · `manifest_schema_version 1.0`.
- **AI Trader** `f4859a5` steps 1–4 · `7d836b3` steps 5–12 partial, **20/25 tests**.
- **ve_tower** — official N1–N4 phenomena provider.
  - **0.1.0 REJECTED** (TOWER_HANDOFF_FAIL: no strict timeframe, no per-node data identity). Wheel SHA-256 `e5457561…f08b2db5` kept for audit.
  - **0.2.0** (contract v2) — TOWER_HANDOFF_CONDITIONAL: identity/timeframe/substitution/byte-integrity closed, but the loader left partial modules on a failed attempt. Wheel SHA-256 `3ea791ba…cc2e91a8` kept for audit.
  - **0.3.0** (contract still v2; bootstrap-only, wheel from `6daf2aa`) — transactional loading: a failed attempt rolls back **everything it introduced**, restores pre-existing modules exactly (same identity), preserves the original exception. Wheel `ve_tower-0.3.0-py3-none-any.whl` SHA-256 `0c2581c068f3bd7d0c5beff1358af0aa906485d69ed74bf66c8a6d8d0c0120d2`; 38 tests; empty-venv verified. Sidecar `ve_tower/HANDOFF_MANIFEST-0.3.0.json`. **Physical wheel committed at `ve_tower/release/ve_tower-0.3.0-py3-none-any.whl`** (git-stored bytes hash to the pinned SHA). (2nd condition is at AI Trader: ve_tower runs in a SEPARATE process+venv; import in the main process forbidden.)

  - **0.4.0** (adds N2 producer; N3/N4 stay v2) — exposes `run_n2` over ratified `bias_h1` @850815f. N2_HANDOFF_CONDITIONAL (RT-TOWER-0007): `run_n3/run_n4` trusted any caller `n2_fingerprint`. Wheel SHA-256 `fe9f8b14…9a8852` kept for audit.
  - **0.5.0** (chain orchestrator) — `run_tower_chain` runs N2→N3→N4 internally; caller cannot supply `n2_fingerprint`. Defect: called `run_n4(atr=None)` → N4 always `atr_unavailable`. Wheel SHA-256 `6d99baf6…4cd94df7` kept for audit.
  - **0.5.1** (ATR internal; contracts unchanged) — orchestrator computes ATR from received bars via canonical `market_state.atr14`: N3←`atr14(M15)`, N4←M15 1×ATR band `atr14(M15)[-1]` (SPEC2 §3 — **not** M5 ATR; reported+justified). Caller cannot supply `atr`/`n3_atr`/`n4_atr`. `AtrProvenance` in `ChainResponse` + `chain_fingerprint`. Fixes TOWER_CHAIN_ATR: chain now reaches N4 without `atr_unavailable`. 73 tests. Awaiting Red Team TOWER_CHAIN_ATR.

## N2 (MANDATE N2, verdict B — N2_EXISTS_BUT_IS_NOT_PACKAGED)
- N2 = `code/bias_h1.py` @`850815f` (build `81a0a62`, spec STAT-LEVEL2-BIAS-H1-SPEC-v1.0 @`1b2933c` + SPEC3 @`404b6c8`, manifest **v2.7.61**). Deterministic directional factors; `emits_probability=False`. Inventory + verdict in `N2_INVENTORY.md` @`a5241fb`.
- Packaged in **ve_tower 0.4.0** (`run_n2`). AI Trader stays HOLD at `54cf26e` until Red Team N2_HANDOFF_PASS. Hints `v2.7.51`/`RT-CODE-A-0011`/`B-L1` were NOT confirmed in git.

**Artifact delivery channel (process lesson):** wheels must be COMMITTED into the repo (`<pkg>/release/*.whl`, `*.whl binary` in `.gitattributes`) so AI Trader can reach the bytes on any remote — chat/file-send delivery is not reachable by AI Trader's process. Neither wheel was tracked in git before this; ve_tower now is.

## CORRECTIONS (found during Mandate A inventory)
- `zone_map` head is **`5888978`** (re-anchored), not `11ae360`.
- `zone_confirmation` head is **`7f2694f`** (W=3), not `ca683ff`.
- `ve_brain` could not build a wheel — **`project.urls` invalid**; fixed in `a1d2a6d`.

## FROZEN
- **CAND-T05**, EV_net **+0.389R** recent, trimmed **+0.202** — **HIGHEST_PRIORITY_PROVISIONAL_CANDIDATE**.
- Canonical measurement contract **NOT RATIFIED**.
- Data **2025-11 → 2026-07 SEALED**.
- **5 live processes untouched, zero trades**.

## NEXT
- **VE**: Mandate A steps 4–7 **DELIVERED** (ve_tower wheel `e5457561…`). Awaiting Red Team verdict.
- **Red Team**: **TOWER_HANDOFF** on ve_tower, then PASS_FOR_LIVE_SHADOW.
- **AI Trader**: wire ve_tower → N3/N4 flags · the 5 tests · the 3,237 suite · `probability_inputs`.

## GUARDS (standing)
- **GARD 1** `GATED_BY_CTO=True` in `code/run_production_pipeline.py:57` — never commit it flipped.
- **GARD 2** sealed holdout — never touched.

_Last persisted: Mandate A in progress (foundation delivered at `c22c876`; N3/N4 contracts underway)._
