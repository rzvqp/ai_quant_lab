# AI Trader — CAND-0001 PDH-PDL v2.0 DEMO Wiring — Report

**Nature of this document**: the CEO's own required pre-first-order deliverable ("Raporteaza-mi ca
lantul e complet si testat, cu cate un exemplu de audit per tip de rezolvare. Nu trimite nimic pana nu
confirm."). **Nothing in this step has sent, or can send, a real order** — every test below runs
against fakes; the code exists and is tested, but is not wired into any running process. Waiting for
explicit confirmation before any live invocation.

## 1. Provenance confirmed

- `demo_gate_engine/pdh_pdl_demo_engine.py` @ `86304e7578ff461fcf23826c07f0295272b1fbc5` (worktree
  `ai_quant_lab-alpha-automation`, branch `alpha-automation-v1`) — commit hash matches exactly.
- `POLICY_PDH_PDL_v2.md` @ `1558397` — matches exactly.
- `STATISTICIAN_CAND0001_DEMO_CRITERIA_v1.0.md`, manifest v2.7.34 @ `a11dde7`, criteria commit
  `c6305d5` (worktree `ai_quant_lab`, branch `statistician-foundation`) — both match exactly.
- `institutional_levels.py`: confirmed **byte-identical** between my existing vendor pin (`61cbd58`,
  used since Mandate 4 Step 3) and the policy's own cited grounding commit (`8edbf99`) — `git diff`
  between the two commits for this one file is empty. No re-pin needed.
- **New submodule**: `vendor/alpha_automation_demo_gate`, pinned to `86304e7` on `alpha-automation-v1` —
  a second submodule into the same source repository (different branch/commit than
  `vendor/alpha_automation_detectors`), justified the same way: exact-commit provenance, self-contained
  (confirmed by reading — only imports `dataclasses`/`enum`/`typing`, nothing from `code/`), never
  modified.

## 2. What was built

`ai_trader/pdh_pdl_demo/`:

- **`day_index.py`** — live, per-bar 17:00-NY DST-aware day boundary (`zoneinfo`, not pandas).
  **Numerically verified against `resample_ny.py`** (the CEO's own required step) over all 83,279 real
  OANDA XAUUSD M15 bars, 2023-01-01 through 2026-07-13, 7+ DST transitions — **zero mismatches**. Exact
  by construction, not approximate: US DST transitions occur at 02:00 NY local time, fifteen hours from
  the 17:00 anchor, so the anchor is never ambiguous or nonexistent for any calendar date.
- **`vendor_bridge.py`** — bridges both submodules: `institutional_levels.compute_prior_day_levels`/
  `detect_level_touches`/`LevelKind` (Part A, ratified, unchanged from v1.2) and `market_state.atr14`
  (S2's `atr` input, reused not recalculated) from the existing pin; `pdh_pdl_demo_engine`'s
  `DemoSignal`/`DemoTradeResult`/`ExitReason`/`min_executable_risk`/`simulate_demo_trade(s)` from the
  new pin. Nothing in either vendored tree is modified.
- **`recognition_rule.py`** — `PdhPdlRecognitionRule`: **replaces `ObservingNullRecognitionRule` for
  this policy only** (task item 1), implementing the same `RecognitionRule` Protocol. Recompute-from-
  scratch, single continuous block (the same pattern `structural_observer` established). Detects a
  FRESH first-touch on the bar that just closed; computes S2's floor **live**, from a freshly-read
  bid/ask tick, via the frozen engine's own `min_executable_risk` (called early, never re-derived);
  applies Part B's own entry-vs-stop/entry-vs-target validity guards against the live reference price;
  emits a `LiveCandidate` only when none of these NO_TRADE conditions fire. Every NO_TRADE path is
  journaled with a coded `reason_code` — nothing is silently dropped.
- **`orchestration.py`** — `PdhPdlOrchestrator`: converts `LiveCandidate` 1:1 to `CandidateSignal`
  (task item 2 — confirmed field-identical, `live_signal_source/types.py`'s own docstring already
  anticipated this exact bridge) and sends it through the **existing, unmodified**
  `mt5_demo_execution.gating.send_after_dry_run_gate` (task item 5) — the same dry-run-then-demo gate
  BTCUSD used. Builds **no new order-construction logic**: `CandidateSignal.stop`/`.target` are already
  turned into a native broker-side SL/TP bracket by `execution_engine/builder.py` (confirmed by reading
  it), so S1's worst-case hierarchy is executed by the broker itself, mechanically — no monitoring loop
  of this package's own. Tracks one open position at a time; a second candidate while one is open is
  refused and journaled (`ALREADY_IN_POSITION`), not queued or silently dropped.
- **Day-end closer** (task 4/CEO Section 3, confirmed approved) — `observe_bar`, called once per closed
  bar: freezes `day_end_idx` the instant a NEW day starts; if the position is STILL open at that point,
  submits ONE mechanical close — the frozen policy's own third exit condition, nothing else. No stop
  adjustment, no partial close, no additional criteria (verified by the dedicated test below).
- **Post-hoc audit** (task 4/CEO Section 4, confirmed approved) — `run_post_hoc_audit`: calls
  `simulate_demo_trade` **exactly once**, only after the position is confirmed closed and the complete
  day's bars are available; its output is the sole audit record. Never called mid-trade.
- **`risk_snapshot.py`** — a REAL `SymbolRiskSnapshot` for the generic (separate, pre-existing)
  `risk_manager` gate: live ATR (`StreamingIndicatorEngine`, already-built), live current spread, a
  disclosed volume-ratio liquidity proxy, gap detection reusing `LiveBarFeed`'s own `GapRecord`/
  `GapClassification`. **Disclosed, not silently improved beyond precedent**: `is_past_friday_cutoff`/
  `is_near_session_close` (no established live definition exists anywhere in this codebase — confirmed
  by inspection) and `minutes_to_high_impact_event` (no calendar feed) are left at the SAME values
  Phase 10's own BTCUSD pilot used (`False`/`False`/`999.0`) — matching, not exceeding, the one existing
  precedent.
- **`market_context.py`** — a real `MarketContext` dict built from the SAME accumulated bars the
  recognition rule already holds. `OrchestratorConfig(recognition_pattern_id=None)` throughout (the
  exact config every `mt5_demo_execution` gating test already uses) — Part A's trigger lives entirely in
  `recognition_rule.py`, never the generic feature-confidence path.

## 3. Effective_spread / cost (task item 3)

- **`effective_spread`** (feeds S2's floor, and only S2's floor): the LIVE bid/ask spread, read
  immediately before order submission — **never a modeled constant, never derived from a fill**
  (confirmed correct by the CEO: "S2... din spread-ul real citit atunci... singura parte care trebuie
  live").
- **`cost`** (the `DemoSignal` field the post-hoc engine call uses): computed from REALIZED fills only,
  after the position closes — entry slippage (`order_result.avg_price` vs. the requested price) plus
  exit slippage (the realized close price, read via `history_deals_get` — the already-proven
  `MT5HistoryGateway` capability from Mandate 3 — vs. whichever of the stop/target it landed closest
  to). Neither is ever a modeled constant.

## 4. One audit example per resolution type (required before any order)

All five produced by `run_post_hoc_audit` calling the frozen `simulate_demo_trade`, verified in
`test_orchestration.py`:

| Exit reason | Scenario | Result |
|---|---|---|
| **STOP** | SHORT (PDH touch), price rises through the executable stop on the very next bar | `net_R < 0`, `intrabar_ordering` shows the stop hierarchy applied |
| **TARGET** | LONG (PDL touch), price reaches the opposite prior-day level before the stop | `net_R > 0` |
| **TIME_STOP** | Neither stop nor target touched through `day_end_idx` | exits at the day's own closing price, `exit_reason="time_stop"` |
| **INVALID_EXECUTION** | A gap through the S2-FLOORED stop on the entry bar itself (narrow convention case, not a routine stop) | `floored=True`, `exit_reason="invalid_execution"` |
| **NO_TRADE** | The live tick passed the pre-trade check, but the bar's own RECORDED open (once available) is already past the structural stop — the disclosed dual-entry-price divergence | `net_R=None`, `exit_reason="no_trade"` |

## 5. Constraints respected, verified by static test, not merely by intent

`test_import_independence.py` (new, 4 checks): no direct `order_send`/`order_check` call anywhere in
this package (every real send routes through the unmodified `send_after_dry_run_gate`); the vendored
`demo_gate_engine`/`institutional_levels` code is reached ONLY via `vendor_bridge.py`; `code/mstrat.py`
is never referenced at all; none of the frozen engine's own types/functions
(`DemoSignal`/`DemoTradeResult`/`simulate_demo_trade`/`min_executable_risk`) are redefined anywhere
outside the vendor bridge — S1/S2/S3 are called, never reimplemented.
`ai_trader/execution_engine/adapters/tests/test_static_no_trading_calls.py` (the CEO's own
"poarta ramane" gate) — **not modified**, re-ran as part of the reduced-scope suite below, still passing.

## 6. A real, previously-undetected bug found and fixed en route

While preparing this step I re-ran `mypy --strict` on `live_signal_source/bar_feed.py` (touched during
Mandate 5's live-observation activation) and found it was NOT actually clean, contrary to what I
reported at the time — a stale-cache artifact, not a real fix. The underlying `_read_field` helper's
`isinstance(value, (int, float))` numeric check (added while satisfying mypy) would have **silently
rejected every real `time`/`tick_volume` field** from MT5's actual numpy structured array, because
`numpy.int64` is confirmed NOT an instance of Python's `int` (verified directly; `numpy.float64` IS, via
genuine inheritance, which is why this asymmetry is easy to miss). Caught before it shipped by
re-verifying against a real numpy-shaped array, not just trusting the type-checker's silence. Fixed with
`isinstance(value, numbers.Real)` (numpy registers both `int64` and `float64` as `numbers.Real` virtual
subclasses) — reverified against real numpy data and the full 55-test `live_signal_source` suite, both
clean. Also fixed a second, narrower gap the same review surfaced: a genuinely-missing structured-array
field raises `ValueError` in real numpy (not `TypeError`/`IndexError`/`KeyError`, the only exceptions the
original fix caught) — widened the catch, verified directly.

## 7. Validation

- `pytest ai_trader/pdh_pdl_demo` → **31 passed**, 0 failed (day_index: 7, recognition_rule: 6,
  risk_snapshot: 5, orchestration: 9 incl. the 5 audit examples, import_independence: 4).
- `pytest ai_trader/live_signal_source` (bar_feed.py fix) → **55 passed**, 0 failed.
- `mypy --strict` on `pdh_pdl_demo` (15 files) and `live_signal_source` (13 files) → **0 errors**, both.
- Git-stash proof: the whole `pdh_pdl_demo` package stashed → pytest collects zero tests (genuine
  failure) → restored → 31/31 pass again.
- **Full `ai_trader/` tree validation launched in the background** (`bar_feed.py` is imported by four
  packages now — the scope rule requires it, no exceptions) — still running at the time of this report;
  will report the result separately, without stopping the live observation process (Mandate 5) to wait
  for it.

## 8. Disclosed limitations — not solved here, not invented around

- **Same-bar double touch** (both PDH and PDL touched within one M15 bar): `RecognitionRule.evaluate()`
  can only return one candidate per call (a Protocol shape, not this rule's own choice). The first is
  processed (deterministic PDH-then-PDL order); the second is journaled as explicitly skipped
  (`SAME_BAR_MULTIPLE_TOUCHES_ONLY_FIRST_PROCESSED`), never silently dropped. Vanishingly rare (would
  require one M15 bar to sweep the entire prior day's range) but real.
- **`risk_snapshot.py`'s two disclosed placeholders** (Section 2) — matches, does not exceed, the one
  existing precedent (BTCUSD).
- **No real-terminal wiring exists yet**: every test above runs against fakes (`FakeMT5DemoGateway`,
  `_FakeFillReader`). Building and testing the REAL dependency factory (`MT5AccountBridge`,
  `MT5PortfolioStateSource`, a real `RealizedFillReader` over `history_deals_get`) against the actual
  DEMO terminal, and the entrypoint that would call `submit_candidate`/`observe_bar` from the running
  `live_observation` loop, is the next step — **not built yet, and will not be, before you confirm this
  report.**

## 9. Status

Chain built and tested end-to-end with fakes, per the required deliverable. Live observation (Mandate 5)
continues unchanged in the background, unaffected by any of this. **Nothing sends an order. Awaiting
your confirmation before any further step.**
