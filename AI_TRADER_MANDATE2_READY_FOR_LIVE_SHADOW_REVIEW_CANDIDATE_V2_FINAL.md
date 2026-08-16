# AI Trader — READY_FOR_LIVE_SHADOW_REVIEW_CANDIDATE_V2_FINAL

**Date**: 2026-08-16 · **Commit**: `a98a0a4ef853a7e69885e08cd9920a401175ead8` · **Branch**: `ai-trader-implementation`
**Remote**: `trader` (`https://github.com/rzvqp/ai_quant_lab-research-main.git`) · local HEAD == remote HEAD, verified.

This supersedes `AI_TRADER_MANDATE2_READY_FOR_LIVE_SHADOW_REVIEW_CANDIDATE_V2.md` (commit `96562cb`). That
version computed EV on the real path using `bridge.py`'s own hardcoded cost literal
(`0.10/0.05/0.05`), which matched neither the ratified BASE nor STRESS cost scenario — a defect this
division found and disclosed itself. This document is the corrected, final candidate.

## 1. What changed since V2 (non-final)

| | V2 (non-final, `96562cb`) | V2_FINAL (`a98a0a4`) |
|---|---|---|
| Cost source in `DecisionRequest` | hardcoded `0.10/0.05/0.05` in `bridge.py` | `shadow_cost_model.resolve_cost_components(tier="BASE")` — zero literals in `bridge.py` |
| Cost model status | `PROVISIONAL`, not yet consumed by the real path | `RATIFIED`, consumed exclusively and exactly |
| `configuration_fingerprint` | `46f96944bb42bcab` | `b7bb9a9aed17a1c8` (changed — proves the RATIFIED-status hash mechanism works) |
| Missing/mismatched cost model | not handled on the real path | fails closed to `decision=None` (`COST_MODEL_UNAVAILABLE` / `COST_MODEL_FINGERPRINT_MISMATCH`) — never a fallback zero |
| Node trace sequence | `N1 → Router → EV → N6` | `N1 → Router → CostModel → EV → N6` |
| Statistical provenance | n=175/4 days disclosed in prose only | `cost_provenance_window` (exact 4-day set) now in `configuration_fingerprint`; `COST_EXTRAPOLATED_OUTSIDE_PROVENANCE_WINDOW` disclosed on every live decision today |

Full derivation, formulas, and disclosure of every ratified value: [AI_TRADER_SHADOW_COST_MODEL_v1.md](AI_TRADER_SHADOW_COST_MODEL_v1.md).

## 2. Cost model — RATIFIED, consumed exclusively (proof)

From the published manifest (`AI_TRADER_SHADOW_COST_MODEL_v1.json`, same commit):

```
calibration_status:         RATIFIED
configuration_fingerprint:  b7bb9a9aed17a1c8
content_hash:                1341f228bb627e8bd33dc38822e2cc834efddd322a70f10561a120c4789f0111
base_ratified:               full_spread=0.05  entry_slippage=0.00  exit_slippage=0.00  (round-trip 0.05)
stress_ratified:             full_spread=0.08  entry_slippage=0.08  exit_slippage=0.08  (round-trip 0.24)
cost_provenance_window:      2026-08-04, 2026-08-10, 2026-08-11, 2026-08-12 (non-contiguous, exact day-set)
spread_dispersion_iqr:       0.04
standard_error:              UNAVAILABLE (honestly disclosed -- raw 175 observations never committed to git)
n_clean_observations:        175
broker / symbol / server:    Fusion Markets Pty Ltd / XAUUSD / FusionMarkets-Demo
source_report_commit:        351f789
```

**BASE's `0.00`/`0.00` slippage is the RATIFIED official value for the BASE scenario, not a claim of a
measured real fill** — zero real fills exist; `real_measured_slippage()` raises `CostModelUnavailableError`
unconditionally.

`bridge.py` no longer contains `full_spread_price=0.10`, `entry_slippage_price=0.05`, or
`exit_slippage_price=0.05` anywhere in its own source — enforced by an AST-based static guard
(`test_bridge_source_contains_no_hardcoded_cost_literals`) plus a literal substring check. A real
`evaluate_bar` call's `CostModel` NodeTrace fingerprint is proven, by test, to equal
`shadow_cost_model.configuration_fingerprint()` exactly, and its cost output fingerprint to equal
`BASE_RATIFIED`'s exactly (`test_bridge_decision_request_consumes_exactly_base_ratified`). A caller-pinned
`expected_cost_model_fingerprint` mismatch degrades every catalog strategy to `decision=None` with
`COST_MODEL_FINGERPRINT_MISMATCH` — proven never to fall back to a substituted zero
(`test_missing_cost_model_via_fingerprint_pin_degrades_to_no_trade_never_a_fallback_zero`). The same BASE
cost is proven identical across `shadow_cost_model.py`, a real `ve_brain.DecisionRequest`, and the public
`AI_TRADER_SHADOW_COST_MODEL_v1.json` fixture Alpha consumes
(`test_same_fixture_produces_the_same_cost_in_shadow_cost_model_and_the_public_json_manifest`).

29 dedicated tests (22 in `test_shadow_cost_model.py` + 7 in `test_bridge_cost_model_wiring.py`), all
passing as part of the full regression below.

## 3. Real-data path — rerun against the corrected bridge

Source: `CANDIDATE_V2_FULL_PATH_EVIDENCE.json`, regenerated against commit `a98a0a4` by
`demonstrate_candidate_v2_full_path.py`.

**Part 1 — real MT5 closed bars → N1 → Router (live)**: 250 real bars observed, last bar closes
2026-08-16. Today's regime resolves `UNCERTAIN_REGIME` at the Router — an honest real-market outcome, not
engineered.

**Part 1b — direct real N3/N4 tower probe on the same live data** (bypassing the Router's regime gate to
prove the isolated tower itself is alive and real): tower v0.3.0, real IPC round-trip,
`n3_market_map_available=true`, **37 real N3 levels**, `n4_confirmation_available=true`. This proves the
real N1→N2→IPC→N3→N4 path is fully functional; Part 1's `UNCERTAIN_REGIME` is a real market condition
upstream at the Router, not a tower failure.

**Part 2 — a fully-approved candidate reaches the broker gate and is BLOCKED**:
- `risk_manager_approved = true`, zero risk denial reason codes
- `reached_broker_gate = true`, `blocked = true`
- `block_reason = "BrokerOrderSubmissionGate: order submission is DISABLED -- Mandate 2 integration not yet ratified by Red Team -- default-closed"`
- **Zero `order_send` calls, zero orders, zero positions.**
- Broker state before: `positions=0, orders=0, balance=1800.34, equity=1800.34`
- Broker state after: `positions=0, orders=0, balance=1800.34, equity=1800.34`
- **`broker_state_unchanged = true`**

## 4. Full regression — commit `a98a0a4` (the corrected commit itself, not a prior one)

Ran with the repository's own `venv` (`ai_quant_lab-research-main\venv\Scripts\python.exe -m pytest
ai_trader/ -q`) — the entire tree, not a reduced scope.

```
3393 passed, 2 skipped, 4 warnings in 15594.95s (4:19:54)
EXIT_CODE=0
```

- **0 failed.**
- **2 skipped** — both are the module-level `pytest.mark.skipif` gates on the two real-broker-order
  integration tests (`mt5_demo_execution/tests/test_mt5_demo_real_terminal_integration.py`,
  `execution_engine/adapters/tests/test_mt5_real_terminal_integration.py`), each requiring an explicit
  operator-set environment variable (`MT5_REAL_DEMO_ORDER_TEST=1` / `MT5_REAL_TERMINAL_TEST=1`) to run
  against a real, already-open MT5 terminal capable of transmitting an order. Both env vars were (correctly)
  unset for this run. This is the intended, deliberate safety gate — these tests exist specifically so they
  never run unattended. No other skip source triggered: the isolated tower venv and the real VE sidecar
  manifest were both present on this machine, so every tower/sidecar-gated test ran for real, not skipped.
- **4 warnings** — all four are the same pre-existing `RuntimeWarning: divide by zero encountered in
  divide` in `vendor/alpha_automation_detectors/code/market_state.py:92` (Parkinson log-range on a
  zero-range bar), raised by 4 `structural_observer` tests unrelated to this correction.
- A first attempt at this run used the system Python instead of the repo's `venv` and failed at collection
  (`ModuleNotFoundError: fastjsonschema`) — an environment/tooling mistake on my part, not a code defect;
  corrected and rerun with the right interpreter before this result was accepted.

## 5. Operational safety — unchanged, verified

- `LIVE_SHADOW`: **not started**.
- `set_authority()`: **never called** — the only references in the tree are the function's own definition
  (`new_brain_bridge/authority.py`) and its dedicated unit test; zero production call sites.
- `BROKER_ORDER_SUBMISSION`: **DISABLED** (unchanged) — proven live by Part 2's block above.
- Orders sent: **0**. Positions opened: **0**. Balance/equity: unchanged throughout (`1800.34`).
- `ve_tower`: runs exclusively in the isolated `ve_tower_venv`, separate process, separate interpreter —
  confirmed via live process inventory during this task (`ve_tower_venv\Scripts\...` and a dedicated
  external interpreter launching `ve-tower-worker.exe`/`ve_tower_worker.cli`, never the main repo `venv`).
- `ve_brain`/`ve_tower` internals: **not modified** — only `ai_trader`'s own `shadow_cost_model.py` and
  `bridge.py` were touched.

## 6. Rollback procedure

If Red Team finds a defect requiring reversion:

```bash
git revert a98a0a4        # reverts the cost-model correction cleanly (single, self-contained commit)
```

or, to return to the last-known-good pre-correction state for comparison:

```bash
git checkout 96562cb -- ai_trader/new_brain_bridge/bridge.py ai_trader/mandate2_readiness/shadow_cost_model.py
```

`8c4ef2a` (original PROVISIONAL cost-model publication, not yet consumed by `bridge.py`) and `96562cb`
(CANDIDATE_V2 non-final, consumed the wrong literal) remain reachable on `ai-trader-implementation`'s
history for a full diff at any time. No destructive history rewrite was performed at any point.

## 7. Status

**READY_FOR_LIVE_SHADOW_REVIEW_CANDIDATE_V2_FINAL.**

Stopping here for Red Team review, per standing instruction. `LIVE_SHADOW` remains not started,
`set_authority()` remains uncalled, `BROKER_ORDER_SUBMISSION` remains DISABLED.
