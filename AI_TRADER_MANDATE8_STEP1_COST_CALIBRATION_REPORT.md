# AI Trader — Mandate: Real Cost Measurement, Step 8 — Report

**Scope**: (1) report the REAL, persisted spread as a distribution (median + percentiles, not means);
(2) build the mechanism to collect REAL slippage, at entry AND exit, from actual fills only — ready for
the first live execution, since zero policy fills exist today. No live policy was changed. No standard
was auto-promoted; the calibration below is presented for CEO ratification, not applied.

## 1. Spread distribution — real, persisted data

Source: `spread_collection.observations` (all 5 live-process state stores; the shared XAUUSD M15 feed's
own `spread_collection_state/xauusd_m15.db` is authoritative). 218 raw observations across 4 calendar
days (2026-08-04, 08-10, 08-11, 08-12).

**Methodology, disclosed**: 43 of the 218 raw observations are duplicate re-emissions from the
2026-08-11 duplicate-bar incident (window `2026-08-10 22:39:13`→`2026-08-11 08:48:44 UTC`, already
marked, not deleted). Excluded here via time-clustering (any observation within 100s of the previous
KEPT one in that window is the same underlying bar, re-emitted; the LAST reading in each cluster is
kept) — this dropped exactly 43, matching the independently-estimated duplicate count from the prior
incident report (window duration ÷ 900s ≈ 40–41 true bars vs. 84 raw readings). **Both distributions are
reported below; the CLEAN one is the one to use going forward.**

| | n | mean | median (p50) | p10 | p25 | p75 | p90 | p95 | p99 | min | max |
|---|---|---|---|---|---|---|---|---|---|---|---|
| RAW (includes duplicates) | 218 | 0.0803 | 0.0700 | 0.0500 | 0.0500 | 0.0900 | 0.1200 | 0.2000 | 0.2000 | 0.0500 | 0.2800 |
| **CLEAN (deduplicated)** | **175** | **0.0809** | **0.0700** | **0.0500** | **0.0500** | **0.0900** | **0.1240** | **0.2000** | **0.2000** | **0.0500** | **0.2000** |

By session (clean):

| session | n | median | p90 | mean |
|---|---|---|---|---|
| asia | 38 | 0.0500 | 0.1000 | 0.0647 |
| london | 33 | 0.0700 | 0.1200 | 0.0721 |
| ny | 83 | 0.0800 | 0.1200 | 0.0835 |
| late | 21 | 0.0900 | 0.2000 | 0.1133 |

Touch-conditioned (the trigger-conditioned subsample `spread_collection`'s own type already tags,
`is_level_touch=True`): **n=1** (median 0.20). Too small to be meaningful on its own — not extrapolated,
flagged as a gap for continued collection, not filled in.

Distinct calendar days: 4 (2026-08-04 isolated before the known operator pause; 08-10→08-12 the current
continuous run). Progress toward the 20-distinct-day target: effectively 3 continuous days so far, not
counting duplicated bars within them.

## 2. Slippage collection — mechanism built, zero fills to measure yet

**Confirmed before building anything** (investigated, not assumed): entry-side requested/realized prices
already existed inline (`candidate.entry` vs. the order acknowledgement's fill price), computed and used
by `_compute_realized_cost()` in both `pdh_pdl_demo.orchestration.PdhPdlOrchestrator` and
`multi_policy_live.orchestration.PolicyOrchestrator` — but only as a private input folded into one
combined-cost scalar, never persisted as an independent, queryable record. Exit-side had no
`close_requested_price` field at all — no order either orchestrator submits carries a discrete "close now
at X" request (SL/TP execute server-side); the existing code inferred a reference post-hoc (whichever of
the strategy's own stop/target the realized close landed nearer to).

**Built**: `ai_trader/pdh_pdl_demo/slippage.py` — `SlippageObservation`/`SlippageLog`, the same
append-only persistence pattern as `SpreadObservationLog`/`PdhPdlAuditJournal`. Records:
`symbol, magic_number, client_order_id, leg (ENTRY|EXIT), as_of, direction, requested_price,
realized_price, signed_slippage (realized − requested, NOT abs()'d), close_reason`.

**Wired, additively**: `PdhPdlOrchestrator`/`PolicyOrchestrator` both gained an optional
`slippage_log: SlippageLog | None = None` constructor parameter (default `None` = byte-for-byte
pre-existing behavior, every existing test and caller unaffected). When provided:
- **Entry leg** — recorded the instant an order is filled (`order_result.avg_price is not None`), inside
  `submit_candidate`, using the exact same requested/realized values `_compute_realized_cost()` already
  reads.
- **Exit leg** — recorded ONLY when `close_reason == "BROKER_SLTP"`, inside `_close_pending`, using the
  same stop-or-target reference `_compute_realized_cost()` already infers, now persisted explicitly.

Both entrypoints (`pdh_pdl_demo/entrypoint.py`, `multi_policy_live/entrypoint.py`) now construct a
`SlippageLog` against their own existing `SqliteStateStore` and pass it into every orchestrator instance
— **wired into the code, not yet exercised by a real fill** (zero policy fills exist across all 4
policies, confirmed in the prior report). It activates automatically the moment the first real order
fills; nothing further needs to be built or restarted for that to happen, since it's already inside the
running processes' own code path once this commit is deployed.

**Disclosed limitation, not fixed here (out of this mandate's scope, a live-behavior change would need
separate approval)**: exit slippage is captured ONLY for `BROKER_SLTP` closes — the one case with a
genuine closing deal in MT5's own history to read. For `TIME_STOP` (or any other mechanical-close
reason), no exit observation is recorded, because no real closing order is currently submitted for that
path at all — `orchestration.py`'s own module docstring claims a mechanical CLOSE order is sent at
day-end, but no code anywhere in this repo actually sends one (`_close_pending` only detects and
journals a close). Recording a reference price for a fill that doesn't exist would misrepresent it as
measured. This is a pre-existing gap in the exit mechanics themselves, found during this investigation,
disclosed here rather than silently worked around or silently fixed.

## 3. Cost standard — provisional, awaiting real calibration

**Approved provisionally** (CEO, this mandate) — explicitly NOT empirical calibration, explicitly not a
measured live cost, per the CEO's own instruction that the zero-slippage installation-test result must
never be presented as one:

| | spread | slippage (each end) | total |
|---|---|---|---|
| BASE_PROVISIONAL | 0.05 | 0.00 | 0.05 |
| STRESS_PROVISIONAL | 0.08 | 0.08 | 0.24 |

**Once real slippage data exists**, the calibration formula (already agreed, not yet computable):

```
BASE   = median(spread) + median(slippage)   -- per execution, both legs
STRESS = upper percentiles                    -- threshold set by Statistician + Red Team, not by
                                                  this division
```

The spread median already measured here (CLEAN, 0.0700) differs from BASE_PROVISIONAL's spread
component (0.05) — this is disclosed, not reconciled or auto-applied. **No standard changes
automatically when data arrives.** The calibration will be computed and PRESENTED for CEO ratification
once real slippage observations exist (currently zero); BASE_PROVISIONAL/STRESS_PROVISIONAL remain in
effect, unchanged, until that ratification happens.

## Validation

`ai_trader/pdh_pdl_demo/tests/test_slippage.py` (7 new tests: in-memory/persisted/reload round-trips,
signed-not-abs, multi-policy magic_number discrimination) + 4 new orchestration wiring tests per package
(entry recorded, rejected-order records nothing, BROKER_SLTP exit recorded with the correct reference,
TIME_STOP exit records nothing) — `pdh_pdl_demo` and `multi_policy_live` each. Full blast-radius suite
(`pdh_pdl_demo`, `multi_policy_live`, `live_signal_source`, `live_loop`, `persistent_state`): 243 passed.
`mypy --strict`: clean, 67 source files. One static-guard false positive (the module docstring's own
prose mentioning MT5's order-acknowledgement API tripped `test_no_direct_order_send_or_order_check_call`
via a literal substring match) — rephrased, not suppressed.

## What was NOT done

No live policy behavior changed — `slippage_log=None` is the byte-identical default every existing test
already proves; the new parameter is purely additive observability. No restart of the 5 running
processes was performed as part of this mandate (this report and the code are ready; deploying it to the
live processes requires a restart, which — per this engagement's own standing convention — is the CEO's
decision, not assumed here). No cost standard was changed. The TIME_STOP-never-submits-a-close-order gap
found during investigation was disclosed, not fixed.
