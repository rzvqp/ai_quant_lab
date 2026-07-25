# Phase 2A, Step 2 — Direction/Stop Validation (#10) and PortfolioDailyState Reset (#11) — Report

**Scope**: exclusively Decision Logic Audit #2 (direction-vs-stop) and Demo Readiness precondition #11
(`PortfolioDailyState` ownership/reset). No refactor, no improvement beyond these two documented items.
No live signal source built. No 5%-sizing logic implemented.

## #10 — Direction-vs-stop validation, per the CEO's exact specification

**Specification honored literally**: LONG requires stop strictly below entry; SHORT requires stop
strictly above entry. Violation is rejected, fail-closed, with its own reason code — never corrected.
Applied in all three places the audit named:

1. **`CandidateSignal.__post_init__`** (`execution_orchestrator/types.py`) — raises `ValueError`. The
   earliest possible check: a future signal source's own bug is caught before anything else runs.
2. **`TradeProposal.__post_init__`** (`risk_manager_live/types.py`) — raises `ValueError`, independently
   of `CandidateSignal`. Defense in depth: a future caller could construct a `TradeProposal` directly,
   bypassing the orchestrator entirely.
3. **`evaluate_trade_proposal`'s risk gate** (`risk_manager_live/engine.py`) — a new `STOP_DIRECTION_CHECKED`
   trace stage, denies with the new `STOP_WRONG_SIDE_OF_ENTRY` reason code (deliberately distinct from
   `RISK_NOT_CALCULABLE` — one means "cannot size at all," the other means "the input is known-corrupt").

**Consequence of layering 1+2**: since `CandidateSignal` and `TradeProposal` both validate at
construction, and `TradeProposal`'s fields are always copied unchanged from an already-valid
`CandidateSignal`, a wrong-sided stop can no longer be constructed through normal use at all — layer 3
is reachable today only via `object.__setattr__` forcing an invalid state onto an already-valid, frozen
instance (used explicitly in its own test, and in two pre-existing tests that needed updating —
see below). This is intentional, disclosed defense in depth, not dead code: it protects against any
future caller that constructs these types some other way.

**Considered and deliberately NOT done**: wrapping `orchestrate()`'s `TradeProposal(...)` construction in
a `try/except`. Since `candidate` is already validated before `orchestrate()` receives it, and
`TradeProposal`'s fields are copied unchanged from it, this construction can never actually raise on the
new invariant — there is no failing test that could prove it needs handling, and the CEO's own rule is
explicit: if you can't write a test that fails, you haven't understood the defect, don't touch it.

## #11 — `PortfolioDailyState` ownership/reset

New file `portfolio_manager_live/daily_reset.py::reset_if_new_day(current, as_of) -> PortfolioDailyState`
— pure function, UTC calendar-day boundary (disclosed IMPLEMENTATION CHOICE, not the broker's own
trading-day convention), fail-safe on backward/stale `as_of` (never resets except on a genuine forward
move into a new day). `execution_orchestrator.orchestrate()` now computes this unconditionally (not
opt-in, unlike circuit tracking — this is a bug fix to existing, always-active behavior) and uses the
result, not `deps.daily_state` directly, when calling Portfolio Manager. `OrchestrationResult.
daily_state_after` threaded through every return path, mirroring `circuit_state_after`'s exact pattern,
so a caller always knows what to persist for its next call.

## Test discipline: fails before, passes after, verified by `git stash`, at every layer

Per the CEO's explicit instruction to use the same method at every step, not just when it happened
naturally during development:

1. **Per-layer, in sequence during development** — each of `CandidateSignal`, `TradeProposal`, the risk
   gate, and `reset_if_new_day` had its own test written and confirmed to fail (`DID NOT RAISE`,
   `ModuleNotFoundError`, or — for the risk gate — a real reproduction of the actual bug:
   `assert True is False` on a proposal that was wrongly approved and sized, `calculated_volume=0.2,
   monetary_risk=200.0`) before being implemented.
2. **Combined `git stash` round, covering everything in this step at once**: stashed all five
   implementation files/new-module (`execution_orchestrator/{engine,types}.py`,
   `risk_manager_live/{engine,types,reason_codes}.py`, `portfolio_manager_live/daily_reset.py`) while
   leaving every test file in place. Re-ran the full set — **8 failures**, each for the expected reason:
   3× `CandidateSignal` `DID NOT RAISE`, 2× `TradeProposal` `DID NOT RAISE`, 1× `ImportError:
   STOP_WRONG_SIDE_OF_ENTRY`, 1× `ModuleNotFoundError: daily_reset`, and — the most telling —
   `test_stale_daily_state_from_a_prior_day_is_reset_before_use` failing with a **real**
   `PORTFOLIO_DAILY_TRADE_COUNT` denial (a stale daily count of 20, at the default limit, wrongly
   blocking the first trade of a genuinely new day). `git stash pop` restored the fix; the identical
   suite then passed in full.
3. **Two pre-existing tests updated, not silently broken**: `test_zero_stop_distance_is_not_calculable`
   and `test_denied_decision_never_carries_a_calculated_volume` used to construct
   `make_proposal(entry=2000.0, stop=2000.0)` directly — now structurally impossible for any direction
   (equality trips the new "strictly below/above" check both ways). Updated to build a validly-sided
   proposal and force the zero-distance state via `object.__setattr__`, with a comment explaining why —
   preserving the original tests' intent (proving the risk gate's OWN `stop_distance > 0` check still
   works) rather than deleting coverage.

## Validation

```
pytest ai_trader/risk_manager_live ai_trader/execution_orchestrator ai_trader/mt5_demo_execution \
  ai_trader/order_manager ai_trader/execution_engine ai_trader/risk_manager ai_trader/portfolio_manager_live -q
-> 670 passed, 2 skipped (gated real-terminal tests, unaffected), 0 failed

mypy --strict ai_trader/risk_manager_live ai_trader/execution_orchestrator ai_trader/mt5_demo_execution \
  ai_trader/order_manager ai_trader/portfolio_manager_live
-> Success: no issues found in 71 source files
```

## Exact diff surface

```
 ai_trader/execution_orchestrator/engine.py         | 49 ++++++++++++++--------
 ai_trader/execution_orchestrator/tests/test_types.py | 31 +++++++++++++
 ai_trader/execution_orchestrator/types.py          | 22 +++++++++
 ai_trader/risk_manager_live/engine.py              | 18 +++++++
 ai_trader/risk_manager_live/reason_codes.py        |  8 ++++
 ai_trader/risk_manager_live/tests/test_fail_closed.py | 36 +++++++++++++--
 ai_trader/risk_manager_live/tests/test_types.py    | 22 +++++++++
 ai_trader/risk_manager_live/types.py               | 14 +++++++
 8 files changed, 179 insertions(+), 21 deletions(-)
```
Plus 3 new files (`portfolio_manager_live/daily_reset.py` and two new test files). Exactly the two
packages Decision Logic Audit #2 named, plus `portfolio_manager_live` for the separately-approved #11.
Nothing else touched.

**Stopping here per instruction.** Report, commit, push, and remote-hash verification follow. Awaiting
approval before the next step in the approved order (#2 — automatic P&L computation).
