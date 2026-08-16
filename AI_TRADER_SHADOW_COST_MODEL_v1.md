# AI Trader — Shadow Cost Model v1 (canonical, project-wide)

**Date**: 2026-08-16 · **Status**: `RATIFIED` by CEO decision (this directive) as the canonical cost
subcontract for all strategies — the general Mandate 2 contract may remain unratified on other points;
this subcontract is ratified independently. Source of truth: `ai_trader/mandate2_readiness/
shadow_cost_model.py` (import this, not this file — this document and `AI_TRADER_SHADOW_COST_MODEL_v1.json`
are frozen, human/Red-Team-readable snapshots of what that module returns).

**Nothing below is new data.** Every number is copied, verbatim, from a git-committed source that already
existed before this directive — this document is a publication/export, not a measurement.

---

## 1. What's published

| Field | Value | Source |
|---|---|---|
| `full_spread_price` (BASE) | 0.05 | `AI_TRADER_MANDATE8_STEP1_COST_CALIBRATION_REPORT.md` §3, "BASE_PROVISIONAL" |
| `entry_slippage_price` (BASE) | 0.00 | same |
| `exit_slippage_price` (BASE) | 0.00 | same |
| `full_spread_price` (STRESS) | 0.08 | same, "STRESS_PROVISIONAL" |
| `entry_slippage_price` (STRESS) | 0.08 | same |
| `exit_slippage_price` (STRESS) | 0.08 | same |
| Round-trip total | BASE 0.05 · STRESS 0.24 | derived, `full_spread + entry_slippage + exit_slippage` |

**Units**: instrument quote-price (XAUUSD bid/ask price scale — `spread=0.05` means `ask − bid = 0.05` in
quote price, never pips or basis points).

**Formula** (already agreed, from the same source report):
```
BASE   = median(spread) + median(slippage)   -- per execution, both legs
STRESS = upper percentiles                    -- threshold set by Statistician + Red Team, not this division
```
**Currently in effect**: BASE_PROVISIONAL/STRESS_PROVISIONAL above — explicitly NOT empirical calibration
(the source report's own words: "explicitly NOT empirical calibration, explicitly not a measured live
cost"). They remain in effect, unchanged, until real slippage data exists AND a ratified calibration
supersedes them.

## 2. Real, measured shadow data — spread (supporting evidence, not the standard itself)

Source: `spread_collection.observations` — real live-tick reads, `SpreadCollector`, persisted per closed
M15 bar across all 5 live-process state stores. **n = 175** clean (deduplicated) observations, 4 distinct
calendar days (`2026-08-04`, `2026-08-10`, `2026-08-11`, `2026-08-12`).

| | n | mean | median (p50) | p10 | p25 | p75 | p90 | p95 | p99 | min | max |
|---|---|---|---|---|---|---|---|---|---|---|---|
| CLEAN | 175 | 0.0809 | 0.0700 | 0.0500 | 0.0500 | 0.0900 | 0.1240 | 0.2000 | 0.2000 | 0.0500 | 0.2000 |

By session: asia n=38 median=0.05, london n=33 median=0.07, ny n=83 median=0.08, late n=21 median=0.09.

**Note the median (0.07) does not equal BASE_PROVISIONAL's spread component (0.05)** — disclosed, not
reconciled, exactly as the original ratifying report already stated. This gap is the reason
BASE_PROVISIONAL is still called PROVISIONAL.

## 3. Slippage — mechanism real, data `COST_MODEL_UNAVAILABLE`

`ai_trader/pdh_pdl_demo/slippage.py`'s `SlippageObservation`/`SlippageLog` is real, tested, and wired
into every live orchestrator (`PdhPdlOrchestrator`, `PolicyOrchestrator`) — but **zero real fills exist
across any live policy to date**. `shadow_cost_model.real_measured_slippage(leg=...)` raises
`CostModelUnavailableError` unconditionally, for both legs, always — **never `0.0` as a silent
fallback**, per the CEO's own explicit instruction ("Zero NU e fallback").

## 4. Broker, symbol, order types

- Broker: `FusionMarkets-Demo` (`Fusion Markets Pty Ltd`), symbol `XAUUSD`.
- Entry: MARKET orders (unset price field — realized fill price read from the order acknowledgement).
- Exit: broker-side SL/TP bracket (`BROKER_SLTP`) — no discrete closing order is currently submitted by
  this codebase for any other close reason (a pre-existing, disclosed gap — see the source report §2).

## 5. Provenance identity

| Field | Value |
|---|---|
| `shadow_cost_model_version` | `v1` |
| `source_report_path` | `AI_TRADER_MANDATE8_STEP1_COST_CALIBRATION_REPORT.md` |
| `source_report_commit` | `351f789` |
| `source_report_blob_sha1` | `0e8207a4e81349fae11104db524206910b7b0816` |
| `slippage_mechanism_path` | `ai_trader/pdh_pdl_demo/slippage.py` |
| `slippage_mechanism_blob_sha1` | `4f59f114da73054c0a9dc246fc5d4c153cee057f` |
| `configuration_fingerprint` | `46f96944bb42bcab` |
| `content_hash` | `c1fa84777c4cb1dcc8bcd158553bab36de776bfe4baced9348c3b1c0f441cde8` |

`content_hash` covers every published numeric field (BASE/STRESS tiers + both spread distributions +
source blob anchor); `configuration_fingerprint` covers this publication's own identity (version + commit
+ source blobs). Both re-verified deterministic across calls by `tests/test_shadow_cost_model.py`; the
source blob hashes are independently re-derived via `git hash-object` against the live working tree
before any test trusts the numbers, so an un-noticed future edit to the source report cannot silently
desync this publication.

## 6. Disclosed discrepancy — found by this canonicalization effort, NOT resolved here

`ai_trader/new_brain_bridge/bridge.py`'s own `DecisionRequest` construction (commit `bd59266`,
2026-08-14) uses a literal cost triple that does **not** match BASE_PROVISIONAL:

| | `full_spread_price` | `entry_slippage_price` | `exit_slippage_price` | round-trip |
|---|---|---|---|---|
| **BASE_PROVISIONAL** (ratified) | 0.05 | 0.00 | 0.00 | 0.05 |
| **`bridge.py`'s actual literal** | 0.10 | 0.05 | 0.05 | 0.20 |

A nearby test fixture comment (`mandate2_readiness/tests/test_brain_functional_proofs.py`, committed
`f4859a5`, ten hours before `bridge.py`'s own literal, same calendar day) explicitly — and incorrectly —
cites `0.10/0.05/0.05` as "BASE_PROVISIONAL... from `AI_TRADER_MANDATE8_STEP1_COST_CALIBRATION_REPORT.md`".
The report's own table never contained those numbers. This means **the currently-running
`new_brain_bridge` (new-brain) decision path does not actually feed N6 the ratified BASE_PROVISIONAL
standard today** — it feeds a third, never-independently-ratified number.

**Not fixed by this document or by `shadow_cost_model.py`** — per the CEO's own "NU recalibra"
instruction, silently changing either side to make them agree would itself be an undisclosed
recalibration. `shadow_cost_model.py` exposes `BRIDGE_PY_COST_LITERAL_MISMATCH = True` and the literal
value programmatically, so this is checkable by code, not just by this document. **Flagged for CEO/Red
Team decision.**

## 7. Consistency proof — one calculator, one number

`tests/test_shadow_cost_model.py::test_published_cost_fields_are_directly_consumable_by_ve_brain_decision_request`
constructs a real `ve_brain.DecisionRequest` using `shadow_cost_model.full_spread_price(tier="BASE")` /
`entry_slippage_price(tier="BASE")` / `exit_slippage_price(tier="BASE")` directly, with zero adaptation —
proving this module's published field names and units are exactly what `ve_brain`'s own contract expects.
Any consumer (this division, the evaluator, Alpha) that imports `shadow_cost_model` and calls these same
functions reads the identical number, from the identical place, under the identical name.

## 8. Fixtures with known results (for Red Team verification)

`ai_trader/mandate2_readiness/tests/test_shadow_cost_model.py` — 16 tests, every one hand-verifiable
against this document's own tables: BASE/STRESS exact values, spread distribution exact values (overall
and per-session, session `n`s sum to 175), `CostModelUnavailableError` on every unavailable path (unknown
tier, unknown leg, any slippage leg), determinism of `content_hash()`/`configuration_fingerprint()`/
`manifest()`, the `bridge.py` mismatch fact, source-blob re-verification against the live working tree,
and the `ve_brain.DecisionRequest` consumption proof. All 16 passing.

## 9. Versioning discipline (future updates)

Per the CEO's own instruction: new shadow data may produce a new version, **never a silent edit to `v1`**.
Any future change requires: a new version string, a new manifest, a new `content_hash`/
`configuration_fingerprint`, a rerun of every fixture test, and results declared `NON_COMPARABLE` between
versions. `shadow_cost_model.py`'s own `SHADOW_COST_MODEL_VERSION` constant is the single place that
version lives — bump it, never mutate `v1`'s own published numbers in place.

## 10. Link to shadow monitoring — confirmed, not assumed

- Spread: `ai_trader/spread_collection/observer.py::SpreadCollector` → `spread_collection.observations`
  append-log (SqliteStateStore) → the exact table this document's §2 quotes, per-M15-bar, real live-tick
  reads (`SpreadObservation.symbol/as_of/bid/ask/spread/session/atr/day_boundary_label/is_level_touch/
  touch_level_kind` — same field names this document's data traces to).
- Slippage: `ai_trader/pdh_pdl_demo/slippage.py::SlippageLog` → `pdh_pdl_demo.slippage` append-log, wired
  into `PdhPdlOrchestrator.submit_candidate`/`_close_pending` and `PolicyOrchestrator`'s own twin — the
  exact mechanism this document's §3 confirms is real but empty.

Not started: `LIVE_SHADOW`, `set_authority()`, any change to `BROKER_ORDER_SUBMISSION`. This publication
is a read-only export of already-existing, already-committed shadow-monitoring artifacts.
