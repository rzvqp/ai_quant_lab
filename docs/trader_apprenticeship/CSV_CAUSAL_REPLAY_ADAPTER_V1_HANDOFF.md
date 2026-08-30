# CSV_CAUSAL_REPLAY_ADAPTER_V1 — HANDOFF

**Status at handoff**: implemented, tested (50/50), parity-verified against bars 1-378, benchmarked,
documented, NOT yet committed to git (this mandate's own final report explains why — see
`IMPLEMENTATION_COMMIT` there). **NOT connected to the live Q4 apprenticeship.**
`LAST_CONSUMED_BAR = 378`, `NEXT_UNSEEN_BAR = 379` — unchanged by this mandate. This document does
not itself authorize resuming Q4 — a separate, explicit CEO instruction is required, exactly as the
prior TradingView-backed accelerator's own handoff stated for itself.

## 1. What exists now

`ai_trader/csv_causal_replay/` (see `CSV_CAUSAL_REPLAY_ADAPTER_V1_SPEC.md` for the full design):

- `CSVCausalReplayEngine.step(expected_pointer_before)` — ATOMIC, one bar per call.
- `CSVCausalReplayEngine.run_until_gate(expected_pointer_before, max_bars, registered_levels,
  vol_range_threshold)` — HYBRID, up to 8 bars per call. **Refused while
  `open_event_state_reference` is set** — see step 3 below, this is exactly the Q4-P007-003 case.
- `CSVCausalReplayEngine.commit_decision(bar_id, decision_type, decision_record)` — required after
  every revealed bar, even routine ones (`decision_type="ROUTINE_NO_EVENT"`).
- `CSVCausalReplayEngine.status()` — read-only durable-state read.
- The sealed fixture (`fixtures/data/Q4_SEALED_1_378.csv`) backing all of this contains bars 1-378
  and 2000 pre-Q4 warm-up bars only — it is PHYSICALLY incapable of exposing bar 379, independent of
  any runtime check (see `CSV_Q4_PARITY_1_378_V1.md`'s `MAX_Q4_BAR_READ_DURING_DEVELOPMENT` proof).

## 2. Exactly how to resume from bar 378 without accidental advancement

**This adapter has never itself been seeded at bar 378 with a live, in-use durable-state file** —
every test that exercises the real bar-378 boundary (`seeded_engine` fixture) uses a fresh
`tmp_path`-scoped state file, torn down at test end, precisely so no test run of this mandate leaves
behind a durable-state file that a later, careless resume could accidentally treat as the real
session. The correct resume sequence, when CEO explicitly authorizes it:

1. Create the real durable-state file's directory (a location outside this package's own
   `fixtures/`, e.g. alongside the other `docs/trader_apprenticeship/AI_TRADER_Q4_*` ledgers this
   apprenticeship already treats as durable).
2. Construct `CSVCausalReplayEngine(sealed_csv_path=.../Q4_SEALED_1_378.csv, store=DurablePointerStore(that path))`
   and call `engine.seed_from_known_state(session_id=..., last_committed_bar_index=378,
   open_event_state_reference="Q4-P007-003:OPEN")` **exactly once**. This does not reveal or commit
   any bar — it only records the already-true fact that bar 378 was already consumed under the old
   TradingView-replay system. `seed_from_known_state` refuses (`RestartAmbiguityError`) if called a
   second time against the same state file, by design.
3. From then on, resuming a reasoning session is: call `engine.status()`, confirm
   `last_committed_bar == 1602036900` and `next_bar == 379` before doing anything else. **Do not
   call `step()` expecting it to succeed at this point** — bar 379 is sealed in this fixture; the
   correct next action is a SEPARATE, CEO-authorized step of extending the sealed fixture itself
   (materializing a new `Q4_SEALED_1_379_XXX.csv` from the same authoritative source, through
   whatever new boundary CEO authorizes) — this adapter deliberately does not, and structurally
   cannot, self-extend its own sealed boundary.
4. Once (and only once) a wider fixture is separately authorized and materialized,
   `step(expected_pointer_before=1602036900)` reveals bar 379 for the first time, and the same
   commit-then-next-bar cycle continues exactly as `CAUSAL_REPLAY_ACCELERATOR_V1_HANDOFF.md` section
   2 already describes for the TradingView-backed variant.

**If you are ever not certain what the last committed bar was**, re-derive it from
`AI_TRADER_Q4_M15_LOG.md` and siblings (the same durable ledgers this apprenticeship has always used
as ground truth), then verify it against `engine.status()` before calling `step()`. Never guess.

## 3. Q4-P007-003 (open at handoff) and the ATOMIC-mode lock

Seeding with `open_event_state_reference="Q4-P007-003:OPEN"` (as step 2 above does) makes
`run_until_gate` refuse outright (`HybridModeLockedError`) until a `P007_RESOLUTION` commit clears
it — mechanically enforcing mandate section 9's "resume in ATOMIC mode only" requirement, not merely
documenting it as a convention the reasoning layer has to remember on its own.

## 4. Rollback

Every file this package adds is new — no existing file in `ai_quant_lab-research-main` was modified.
Rollback is deleting `ai_trader/csv_causal_replay/` and any durable-state file created under step 2
above; nothing else in this repository references it yet.

## 5. Recommended before live use

Same standing recommendation as the TradingView-backed accelerator's own handoff: an independent
adversarial review (Red Team) of this implementation, not just this mandate's own 50-test
self-authored suite, before connecting it to the live Q4 apprenticeship — consistent with this lab's
standing practice for measurement-integrity-adjacent code, and specifically worth an independent
look at the EMA-50 divergence disclosed in `CSV_Q4_PARITY_1_378_V1.md` (whether a 6-bar streak
difference matters for anything downstream that reads this adapter's `sub_ema_streak` directly).

## 6. Explicit non-actions

This handoff does not resume Q4. `NEXT_UNSEEN_BAR = 379` remains unconsumed — not merely
undisclosed, but physically absent from every file this mandate produced. No live TradingView tool
was called anywhere in this mandate. AI Trader was not invoked to build, inspect, or use this
adapter. Connecting it to the live apprenticeship requires a separate, explicit CEO instruction.
