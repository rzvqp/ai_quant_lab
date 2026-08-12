# RED TEAM — MEASUREMENT CONFORMANCE SUITE · the 17 canonical tests
### RT-AUDIT-MEAS-0002 · known-outcome synthetic trades run against EACH engine (SCREEN / MSTRAT / DEMO)
**Date:** 2026-08-13 · **Auditor:** Red Team · **Mandate:** CEO step 5 — build the 17 canonical conformance tests; for the same input+config, all engines must produce the same trade register and net results. Test 12 (tick↔USD) is decisive. Actively hunt a sixth divergence. **Block ratification if unexplained differences remain.** Engines run as verbatim behavioral replicas (SCREEN=`_screen.simulate`, MSTRAT=`mstrat.simulate`, DEMO=`demo_gate` per RT-CODE-A-0010). **No engine modified; no repair.**

## VERDICT — **FAIL · RATIFICATION BLOCKED.** No engine implements the canonical semantics; the engines diverge on ≥6 axes.
Every difference is **explained** (cause identified below) — but **none is reconciled**: for the same input+config the three engines produce **different registers and different net R** on the cost, floor, window, block, entry-bar-target, and cost-formula axes. **A SIXTH divergence was found** (T4, entry-bar target). Per the CEO rule, ratification cannot proceed until all engines are reconciled to one canonical semantics.

---

## THE 17 TESTS — result per engine (✓ conforms to canonical / ✗ diverges)
| # | test | SCREEN | MSTRAT | DEMO | finding |
|---|---|---|---|---|---|
| 1 | signal N → entry open N+1 | ✓ | ✓ | ✓ | **entry CONVERGES** (all next-open); net diverges on cost only |
| 2 | stop below minimum (D-2) | ✗ | ✓ | ✓ | **floor FLIPS the outcome:** SCREEN (no floor) → noise stop-out **−1.0**; MSTRAT/DEMO (floor) → survives → **+0.1 win**. SCREEN non-canonical (no floor) |
| 3 | SL on entry bar | ✓ | ✓ | ✓ | all catch it (entry bar scanned); net diverges on cost |
| 4 | **TP on entry bar** | count | count | **ignore** | **★ SIXTH DIVERGENCE:** SCREEN/MSTRAT count the entry-bar target (**win +1.0/+0.8**); DEMO's S3 ignores it → **time-exit −0.2**. Same trade, win vs loss |
| 5 | SL & TP same bar | ✓ | ✓ | ✓ | **precedence CONVERGES** (all stop-first worst-case); cost diverges |
| 6 | expiry exactly at last allowed bar | ✗ | ✓ | ✓ | **window off-by-one:** SCREEN `[ei,ei+h]` inclusive → **target +1.0**; MSTRAT/DEMO exclusive → **time −0.2** |
| 7 | inclusive vs exclusive holding | — | — | — | = T6 (SCREEN inclusive vs MSTRAT/DEMO exclusive) |
| 8 | dataset boundary as time-exit | ✗ | ✗ | ✗ | **ALL THREE** clip the window to `n-1` and time-exit at the **dataset end** — all violate the canonical (horizon must be live-valid, not the data boundary) |
| 9 | 17:00-NY rollover | ✓ | ✓ | ✓ | anchor CONVERGES (both 17:00-NY); not exercised inside `simulate` (feeds blocks) |
| 10 | DST transitions | ✓ | ✓ | — | handled by pandas `tz_convert('America/New_York')` in the day-index layer |
| 11 | manifest segmentation | ✗ | ✓ | — | SCREEN >72h-gap blocks vs MSTRAT manifest segments → **different populations** |
| **12** | **cost: ticks vs USD** | n/a | ✗ | ✗ | **decisive — see below.** Formula applies **spread TWICE** (0.60 vs canonical 0.35); USD-as-ticks bug = **58–100× too small** |
| 13 | spread once, slippage per exec | n/a | ✗ | ✗ | `2·(spread+slip)·tick` = **2·spread + 2·slip**; canonical = **1·spread + 2·slip** → spread double-counted |
| 14 | net profit calc | ✗ | ✓ | ✓ | SCREEN is GROSS (no cost); MSTRAT/DEMO net — the net calc itself diverges (M-1) |
| 15 | single-trade concentration | ✓ | ✗ | — | `_screen.metrics` has `best_share_of_total`; MSTRAT metrics have **no** equivalent → asymmetric |
| 16 | top-1% removal | ✓ | ✗ | — | `_screen.metrics` has `trimmed_top1pct`; MSTRAT has none → asymmetric |
| 17 | reject cross-config comparison | ✗ | ✗ | ✗ | **NO engine** tags verdicts with tick/cost/floor/window/block provenance → nothing prevents comparing different configs (canonical §11 unmet) |

**Full convergence on: none.** (T9/T10 converge on the anchor but it is not part of `simulate`.) Every test that touches cost, floor, window, blocks, entry-bar target, or metrics diverges.

## TEST 12 (the most important) — tick↔USD cost convergence — **DIVERGES on TWO axes.**
Real XAUUSD: spread 0.25 USD, slippage 0.05 USD, **tick 0.01**.
- **Canonical USD** (spread ONCE + slippage per execution, per §13): `1·0.25 + 2·0.05 = 0.35 USD`.
- **Formula `2·(spread+slip)·tick` via ticks** (spread_ticks=25, slip_ticks=5): `2·(25+5)·0.01 = 0.60 USD` → **DIVERGES from 0.35 — the formula pays the spread TWICE.** The tick↔USD *conversion* is fine (25 ticks × 0.01 = 0.25 USD); the **structure** is wrong (round-trip = 2·spread, not 1·spread).
- **The unit bug** (spread MEASURED in USD plugged into the ×tick formula): `2·(0.25+0.05)·0.01 = 0.006 USD` — **~58–100× too small** (exactly the CEO's "0.0005 USD" failure). This is unit confusion (USD treated as ticks then re-multiplied by tick).
- **Third hazard:** whether `spread_ticks` is the FULL or HALF spread is **undocumented** — the `2·` factor is only correct if it is the half-spread; if it is the full spread, the round-trip double-counts.
**So the cost is triply unsafe:** wrong tick (0.1 vs 0.01, M-5), possible USD-as-ticks (58–100×), and a spread-once-vs-twice structural ambiguity. **No two engines are guaranteed to agree on cost in USD.**

## THE SIXTH DIVERGENCE (actively hunted, found)
**T4 — entry-bar TARGET handling.** A trade whose target is touched on the **entry bar**: SCREEN and MSTRAT **count it as a win** (they scan the entry bar for the target); DEMO's **S3 deliberately ignores** the entry-bar target (scans target from `ei+1`) → the same trade becomes a **time-exit (loss)**. This is invisible to the RT-AUDIT-MEAS-0001 SCREEN-vs-MSTRAT comparison (those two agree here); it surfaces only when the DEMO engine is included. **The canonical must specify entry-bar target precedence** — DEMO drops legitimate same-bar wins; SCREEN/MSTRAT count them (with stop-first when both hit). Sixth confirmed, explained divergence.

## THE SIX (now eight) DIVERGENCES — consolidated
1. **Cost gross-vs-net** (T1/3/5/14) — SCREEN gross, MSTRAT/DEMO net.
2. **Risk floor present/absent** (T2) — and it **flips outcomes** (loss↔win), not just magnitude.
3. **Window off-by-one** (T6/7) — SCREEN inclusive, MSTRAT/DEMO exclusive.
4. **Block population** (T11) — gap vs manifest.
5. **TICK=0.1 ecosystem contamination** (T12) — mstrat ecosystem carries it, screen doesn't.
6. **★ Entry-bar target** (T4) — SCREEN/MSTRAT count, DEMO ignores. *(the newly found sixth)*
7. **Cost formula double-counts the spread** (T12/13) — `2·spread` vs canonical `1·spread`.
8. **Shared canonical violations** (T8 dataset-boundary time-exit; T17 no provenance guard; T15/16 asymmetric fat-tail metrics).

## WHAT THIS MEANS
- **No engine is the reference.** SCREEN violates the floor (T2) and the window (T6) and lacks cost (T14); MSTRAT/DEMO carry the tick+floor+cost-structure errors (T2/T12) and the window/entry-bar issues; DEMO additionally drops entry-bar targets (T4). All three violate the dataset-boundary and provenance rules (T8/T17).
- **Ratification is BLOCKED.** The differences are all explained but none reconciled; the same strategy produces different registers on different engines. Until the `CANONICAL_TRADE_SIMULATION_CONTRACT` (RT-AUDIT-MEAS-0001 §6) is adopted and every engine is brought to it and re-verified against these 17 tests, **no leaderboard and no economic elimination is definitive** (CEO directive, standing).

## HANDOFF → CEO / Statistician
1. **Adopt the canonical contract** (RT-AUDIT-MEAS-0001 §6) and, additionally, **specify entry-bar-target precedence** (the T4 sixth divergence) and **the spread half/full definition** (the T12/13 double-count) — these were under-specified even in that contract; this suite forces their resolution.
2. **Make these 17 tests the ratification gate:** an engine ratifies only when it passes all 17 against the canonical expected results; two engines' numbers compare only when both pass and their config provenance matches (T17).
3. **Fix, per the contract, the shared violations** (T8 dataset-boundary → treat over-horizon trades as incomplete; T15/16 → symmetric fat-tail metrics; T17 → provenance-tag every verdict).
4. **Keep the freeze:** no leaderboard/elimination definitive until all engines pass the 17.

Red Team designed no remedy, modified no engine, ran no data on the market, changed nothing outside `red_team/`.
