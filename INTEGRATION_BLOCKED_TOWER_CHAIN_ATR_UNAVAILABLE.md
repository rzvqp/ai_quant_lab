# INTEGRATION_BLOCKED_TOWER_CHAIN_ATR_UNAVAILABLE

**Directive**: RT-TOWER-0008 ("REIA INTEGRAREA DE LA COMMIT 54cf26e")
**Target status (not reached)**: `READY_FOR_LIVE_SHADOW_REVIEW_CANDIDATE_V2_CORRELATED`
**Actual status**: `INTEGRATION_BLOCKED_TOWER_CHAIN_ATR_UNAVAILABLE` / `WAITING_FOR_TOWER_CHAIN_ATR_FIX`
**Base commit**: `54cf26e9744845711a0fd97239dcaafaed740a90`

## What this checkpoint delivers

Everything listed below is complete, real, and tested against the genuinely installed `ve_tower` 0.5.0 artifact — no stub, no fixture standing in for the artifact itself.

1. **`ve_tower` 0.5.0 pin** — `tower_identity_pin.py` updated to the verified sidecar values (`package_build_commit=b128d8b`, `state_delivery_commit=26470f5`, wheel SHA-256 `6d99baf6...4df7`, plus the five new chain-binding fields). `verify_pin` extended to exact-match all of them, fail-closed on any mismatch or `None`.
2. **Chain protocol v3** — `tower_protocol.py` (client) and `tower_worker/src/ve_tower_worker/protocol.py` (worker) rewritten around `TowerChainRequest`/`TowerChainResponse`. `_ALLOWED_CHAIN_REQUEST_FIELDS` is an exhaustive allowlist; `parse_chain_request` rejects any unknown field (`UNKNOWN_REQUEST_FIELD`), structurally — not by convention. No `n2_fingerprint`, `bias_available`, or synthetic intermediate identity is representable on the wire at all.
3. **Worker uses exclusively `run_tower_chain`** — `decision.py` rewritten; the only `ve_tower` call anywhere in the module is `ve_tower.run_tower_chain(...)`.
4. **AST guard** (`tower_worker/tests/test_decision_ast_guard.py`, new) — walks `decision.py`'s AST for any `run_n2`/`run_n3`/`run_n4` reference (attribute, name, import, or exact-string constant — catches `getattr` evasion too) and fails if found. Confirms the module both avoids the direct API and genuinely calls `run_tower_chain`.
5. **`bridge.py` chain rewrite** — fetches real H1/M15/M5 bars (`fetch_tower_chain_bar_windows`, correct `MT5_TIMEFRAME_H1=16385`), builds `TowerChainRequest` field-for-field, calls `tower.client.request_chain(...)`, consumes the real `ChainResponse`. `side` is derived only from the selected strategy's own `StrategyContract.allowed_directions[0]` — never a default, never copied from N2. Per-(bar, side) tower-call memoization (not per-bar alone, since N2/N4 depend on side).
6. **N2/N3/N4/chain identity propagation** — `EventIdentity` carries the full chain identity (`chain_fingerprint`, `chain_binding_version`, `chain_status`, `terminal_reason_code`) plus distinct per-node N2/N3/N4 identity fields (`data_identity`, `node_input_fingerprint`, `event_fingerprint`, and N2's own `output_fingerprint`) — never forced equal across nodes. Three real node traces (`TowerN2`, `TowerN3`, `TowerN4`) replace the prior two. `risk_gate.py`'s `build_risk_manager_trace` / `execution_shadow.py`'s `build_execution_adapter_trace` already correlate via the shared `trace_id` column that has run through every node (N1 → … → N6 → RiskManager → ExecutionAdapter) since before this remediation — confirmed structurally, not re-plumbed, since that correlation column already existed and both builders already consume `outcome.event_identity.trace_id`.
7. **`regime_axes_status` correction** — found and fixed a genuine bug in this division's own `bridge.py` (not `ve_tower`): the field was built as `"is_compressed=False"`-style strings. Read against the installed artifact's own ratified `bias_h1.Status` enum (source-introspected directly, not guessed), the expected vocabulary is the two literal strings `"available"`/`"unavailable"` per axis — `run_tower_chain`'s own `regime_available = any(s == "available" for s in req.regime_axes_status)` depends on it exactly. Fixed to derive that vocabulary from whether each `RawAxes` field is `None` (unmeasured) or populated. This one fix took N3 from permanently cascade-failing to genuinely returning real levels on both synthetic and live MT5 data — proof included below.
8. **`test_e2e_readiness.py` migrated** — `_tower_request`/`TowerRequest`/`TowerN3N4Result`/`request_n3_n4` fully replaced by `_tower_chain_request`/`TowerChainRequest`/`TowerChainResult`/`request_chain`. Test 20b's malformed-request trigger rebuilt around `expected_n2_contract` mismatch (the old trigger — an invalid `bias_direction` string inside `n2_output` — has no wire equivalent under v3, by design). Tests 04/09 rebuilt against `n3_output`'s own `data_identity`/`reason_codes`.
9. **Targeted tests aferente** — every test file touching the tower client/protocol/launcher/identity pin/sidecar verification updated for the 0.5.0 pin and the chain shapes (stub-pin monkeypatch blocks extended with the 5 new fields; `test_wrong_package_build_commit_is_a_mismatch` fixed to read the pin dynamically instead of a stale hardcoded commit).

## Validation run

```
301/301 teste țintite PASS
  256  ai_trader/new_brain_bridge + ai_trader/mandate2_readiness   (main venv)
   45  tower_worker/tests                                          (isolated tower venv)
main venv: ve_tower / ve_tower_worker ABSENT (pip show — not found, both packages)
tower venv: ve_tower_worker resolves to site-packages (non-editable install confirmed;
            no editable install anywhere is being treated as final)
```

Full `ai_trader/` regression: **NOT started** — deliberately, per this checkpoint's own scope. The correlated-run blocker (below) means a 4+ hour regression would not change today's verdict.

## Operational safety (unchanged, reconfirmed)

- `LIVE_SHADOW`: not started.
- `set_authority()`: never called.
- `BROKER_ORDER_SUBMISSION`: `DISABLED` — `broker_gate.py` untouched this session (`git diff HEAD -- .../broker_gate.py` is empty).
- `ve_brain` / `ve_tower` internals: untouched (never modified, never re-vendored, never patched).
- Legacy / `market_intelligence` fallback: not reactivated.

## What is NOT included in this checkpoint (by design, per explicit instruction)

- No complete-candidate proof.
- No `READY_FOR_LIVE_SHADOW` verdict.
- No fabricated N4 result.
- No test marked passing that actually depends on a real ATR reaching N4.
- No editable worker install represented as the final install.
- The single correlated-run replay script (§7 of RT-TOWER-0008) — **not built**, since it cannot honestly reach an approved candidate today (see blocker below); building it now would either produce a script that never demonstrates its own stated purpose, or tempt fabricating `confirmation_available=True`, both explicitly forbidden.
- The remaining ~18 decisive tests from §9 that depend on the correlated run — not written, for the same reason.

## The blocker, reproducible

**Root cause** (confirmed by reading the installed `ve_tower` 0.5.0 artifact's own source directly — `ve_tower.chain`, `ve_tower.n3`, `ve_tower.n4`, `ve_tower.contracts` — not inferred from behavior alone):

- `ve_tower.ChainRequest` (real dataclass, fields enumerated directly via `dataclasses.fields`) has **no `atr` field** — there is no path for a caller to supply ATR into the chain at all.
- `ve_tower.chain.run_tower_chain` calls both `run_n3(N3Request(..., atr=None, ...))` and `run_n4(N4Request(..., atr=None, ...))` — **hardcoded**, unconditional.
- N3's underlying ratified module (`zone_map.build_zone_map`) tolerates `atr=None` — it still returns a real market map (confirmed: real zone prices, `market_map_available=True`, on both a synthetic fixture and live MT5 H1/M15/M5 data, after the `regime_axes_status` fix above).
- N4's underlying ratified module (`level4-v2.0-w3`) does **not** tolerate `atr=None` — it deterministically returns `confirmation_available=False`, `reason_codes=("atr_unavailable",)`.

**Consequence**: `run_tower_chain` can never produce `confirmation_available=True` as this artifact is currently built — regardless of strategy, market data (synthetic or real, tested both), or probability inputs. Since `ve_brain.decide_n6` requires `confirmation_available=True` to reach the EV stage, no real call through the installed artifact can reach `TRADE`/`SHADOW_TRADE_CANDIDATE` today. This blocks §7/§8 of RT-TOWER-0008 (a genuinely-approved candidate reaching the broker gate) at the artifact level, not in this division's own wiring.

**What would resolve it** (VE's decision, not this division's): either add an ATR input to `ChainRequest`/thread a real value through to `run_n4`, or have `run_tower_chain` compute ATR internally from the M15/M5 bars it already receives.

## Files intentionally left uncommitted

None from this segment's work — every modified/new file relevant to RT-TOWER-0008 is included in the checkpoint commit. Untouched, pre-existing untracked files (`full_regression_a98a0a4_output.txt`, `full_regression_commit_a98a0a4.txt`, `scratch_verify/`, `scratchpad_verify/`) are leftovers from an earlier, already-delivered directive (Candidate V2 FINAL, commit `a98a0a4`) and are out of scope for this checkpoint — left as-is, not committed, not deleted.

## Rollback

`git revert` of this checkpoint's commit returns the tree to `54cf26e` (last known-good `RT-MANDATE2-0002` partial remediation state) — no other repository, no `ve_brain`/`ve_tower` state, and no live process is touched by this checkpoint, so rollback is a pure single-commit revert.

## Next step

Hold at `WAITING_FOR_TOWER_CHAIN_ATR_FIX`. No further work on the correlated-run script or the full regression until VE ships a `ve_tower` build where `run_tower_chain` can produce `confirmation_available=True` for at least one real scenario (`TOWER_CHAIN_ATR_PASS`).
