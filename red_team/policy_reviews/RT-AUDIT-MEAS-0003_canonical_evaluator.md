# RED TEAM — ATTACK ON THE CANONICAL EVALUATOR (the ratification gate)
### RT-AUDIT-MEAS-0003 · `code/canonical_evaluator.py` @ `82acad9` run against the 17 canonical tests
**Date:** 2026-08-13 · **Auditor:** Red Team · **Mandate:** CEO — "Cele 17 teste devin POARTA DE RATIFICARE." Attack `canonical_evaluator` @ `82acad9`; run it against the 17 (VE's own 14 tests "aren't the bar — mine are"); **hunt a ninth divergence**; verify whether the evaluator **repairs or inherits** the shared violations T8/T15/T16/T17 (esp. T17 config-provenance / R11 immutable config_id — "VE spune că l-a implementat. Verifică."); verify the **S3 +0.395 BASE** finding (correct, or one error swapped for another?); and **hold the freeze**. **No engine modified; no repair; no real data.** Verified on synthetic fixtures + the evaluator's own imported source + VE's 14 tests re-run.

## VERDICT — **PASS_WITH_LIMITATIONS as a specification; NOT YET the ratification gate.**
The evaluator is a **genuine, correct closure of 7 of the 8 divergences** — it is the first artifact in this program that implements one coherent semantics (R1 tick, R2 next-open, R3 reject-not-widen, R4 spread-once, R5 entry-bar inclusive + SL-primacy, R6 explicit window `[ei, ei+H-1]`, R7 still-open-not-time-exit). VE's 14 tests pass; so do my 17 axes **on the normal path**. **But three items block it from being the gate:** (1) a **ninth divergence** I found by active hunt — the evaluator **drops SCREEN's gap-open guard**, so a trade whose entry gaps *through* its stop is booked as a **WIN**, and one that gaps *through* its target as a **forced loss**; SCREEN skips both. (2) **T15/T16 are not repaired — they are DROPPED:** the `StrategyReport` carries **no fat-tail metrics at all** (no `best_share`, no `trimmed_top1pct`), a regression from `_screen`. (3) **T17 is half-built:** config_id is produced and immutable (the tagging is real), but nothing **enforces** comparison-only-on-match, and the config_id is **data-blind** — it hashes the rules but not the symbol/period/population, so two results on *different instruments* share one config_id and read as "comparable."

---

## 1 · THE EVALUATOR AGAINST THE 17 — what it CLOSES (verified, imported source)
Run as `import canonical_evaluator; evaluate_signal(...)` on known-outcome synthetic bars:

| # | canonical test | evaluator | verified behaviour |
|---|---|---|---|
| 1 | signal i → entry `open[i+1]` | ✅ CLOSE | R2 `ei = signal_bar+1` |
| 2 | stop below minimum | ✅ CLOSE (as **REJECT**) | R3/D-2 → `Rejection(STOP_BELOW_MINIMUM)`, **no widening**, risk left un-extended; stays in the SIGNALS register, no fictional P&L |
| 3 | SL on entry bar | ✅ CLOSE | R5 scans from `ei` inclusive |
| 4 | **TP on entry bar** (the 6th divergence) | ✅ CLOSE | R5 counts the entry-bar target, SL-first — DEMO's "ignore" is overridden |
| 5 | SL & TP same bar | ✅ CLOSE | R5 SL primacy (stop checked before target) → loss, verified |
| 6/7 | window inclusive-vs-exclusive | ✅ CLOSE | R6 one convention `[ei, ei+H-1]`; hit at the last window bar is caught |
| 8 | dataset/block boundary as time-exit | ✅ CLOSE | R7 `still_open_at_end` (reported separately), **not** a time-exit; `NoEntry` at the dataset end |
| 12/13 | cost spread-once, per-execution slip | ✅ CLOSE | R4 `total = spread + entry_slip + exit_slip`; BASE **0.05**, STRESS **0.24** — spread **not** doubled |
| 14 | net calc | ✅ CLOSE | net R in USD, cost applied regardless of exit reason (incl. time-exit) |
| 9/10 | 17:00-NY / DST | ⏸ N/A in-evaluator | index-based; the anchor/day layer is the **caller's** (unchanged) |
| 11 | manifest population | ⏸ upstream | evaluator honours `block_end`; the block **manifest** is still the caller's — the evaluator handles the boundary right but does not define the population |
| **15** | single-trade concentration | ❌ **DROPPED** | see §3 |
| **16** | top-1% removal | ❌ **DROPPED** | see §3 |
| **17** | reject cross-config comparison | 🟠 **HALF** | see §3 |

**VE's 14 tests: all 14 pass** (re-run, `14 passed`). They faithfully cover R1–R7 and R11's *determinism*. **None covers a gap-open** — that is the blind spot the ninth divergence lives in.

## 2 · THE NINTH DIVERGENCE (actively hunted, found) — the missing gap-open guard
`_screen.simulate` skips a signal whose entry has already gapped through its own stop or target: `if side=="long" and entry <= stop: continue` and `entry >= tgt: continue`. **The canonical evaluator has no such guard.** It computes `risk = abs(entry − requested_stop)` and enters unconditionally (after the R3 floor check). Two verified consequences on synthetic bars:

- **Entry gaps THROUGH the stop (long, entry 97, stop 98 — stop now *above* entry):** on the entry bar `low ≤ 97 < 98` → immediate "stop" exit **at 98**, `dirn*(98−97)=+1` → **BASE net_R = +0.95. A WIN booked from a trade that gapped straight through its stop.** Economically nonsensical (a long entered below its own stop).
- **Entry gaps THROUGH the target (long, entry 105, target 102):** exits "target" at 102 < entry → **BASE net_R = −0.436, a forced loss** on a move already complete. SCREEN skips it entirely.

So for the **same signal + same config**, SCREEN produces *no trade* and the canonical evaluator produces a **win (or a forced loss)**. This is a true ninth divergence **and** an economic defect (a gapped-through stop must be a loss at the fill, never a +1R win). It is invisible to VE's 14 tests and to my first 17 (none exercised a gap-open). **It interacts with the T4 fix:** R5 "count the entry-bar target" is correct for the normal case, but by removing SCREEN's skip it opened the boundary hole — the entry-bar rule now also fires on gapped-beyond bars.

## 3 · SHARED VIOLATIONS — repaired, inherited, or dropped?
- **T8 (dataset-boundary time-exit) → REPAIRED.** R7 is a real fix: over-horizon trades are `still_open_at_end` (exit_bar = block end, reason `still_open_at_end`), and `ei > block_end` is `NoEntry`. The boundary is no longer a fake market exit. ✅
- **T15 / T16 (fat-tail metrics) → NOT repaired; DROPPED (regression).** `StrategyReport` fields are: `total_signals, eligible_trades, rejected, rejected_pct, rejection_reasons, no_entry, still_open_at_end, base_mean_R, stress_mean_R, base_minus_stress`. **There is no `best_share`, no `trimmed_top1pct`, no concentration metric of any kind** — `_screen.metrics` *had* both. The evaluator reports only mean-R. The CEO's fat-tail guard (best_share > 0.30 or top-1%-trimmed avg_R ≤ 0) **cannot be evaluated from this report at all.** This is worse than "inherited": the one engine that had the metric no longer feeds it. 🔴
- **T17 (config provenance / R11) → HALF-built.** Two gaps:
  1. **Produced, not enforced.** Every `ExecutedTrade`/`StrategyReport` carries an immutable 16-hex `config_id` (sha256 over the rules + scenarios + code_version). That part is real — the tagging VE claims *is* implemented. **But no function refuses to compare two mismatched-config results.** VE's own R11 test asserts only `diff.config_id != a.config_id` and *names* it "NON-COMPARABLE" in a comment; nothing in code prevents a consumer from comparing `a.net_R` to `diff.net_R`. The guard is a naming convention, not a structural barrier.
  2. **The config_id is DATA-BLIND.** Its payload keys are `R1_tick_size, R2_entry, R3_min_stop, R4_cost, R4_scenarios, R5_*, R6_holding, R7_boundary, code_version` — **no symbol, no date range, no block manifest, no instrument.** Two runs on *different instruments or periods or populations* produce the **same** config_id and would read as "comparable." The CEO's T17 asks provenance to cover "tick/cost/floor/window/**block**"; the block/population dimension is absent. So even a correct comparison-guard would pass mismatched *data*. 🟠

## 4 · THE S3 +0.395 BASE FINDING — correct number, wrong presentation
**Cost arithmetic verified:** old mstrat cost = `2·(spread_t+slip_t)·TICK = 2·(1+1)·0.1 = 0.40` (round-trip, spread doubled — the exact T12 defect). Canonical BASE = **0.05** (spread once, zero slip), 8× smaller; canonical STRESS = **0.24**. So correcting the doubled cost mechanically **raises** S3's R — the **direction is right and the engine is now correct on cost**. VE did **not** swap one engine error for another *inside the evaluator*.

**But +0.395 is not a usable verdict, for three reasons — and presenting it as "S3 is now positive" would be the new error:**
1. **It is the BASE scenario — the most optimistic, and explicitly UNCALIBRATED** (`calibrated=False`, "PROVISIONAL — NOT EMPIRICALLY CALIBRATED"). R4 **requires both** scenarios reported; the STRESS cost (0.24, ~5× BASE) drives S3's R materially lower. A number quoted from the 0.05 leg alone is cherry-picked.
2. **The population changed.** R3 now **rejects** (does not widen) sub-floor stops. If any S3 signals had small stops they are no longer traded, so the eligible set differs from the old widened-stop mstrat set. +0.395 is computed on a **different population** than the −0.39 it is being compared to.
3. **Therefore comparing +0.395 (canonical) to the prior −0.39 (old mstrat) is itself an R11 violation** — different tick, different cost structure, different floor semantics, different population ⇒ **NON-COMPARABLE by the evaluator's own contract.** The flip narrative ("was negative, now +0.395") compares across configs.

**Net:** the +0.395 is arithmetically correct *for the BASE-provisional leg on the re-populated set*, but it is **provisional, best-case, and non-comparable to the old number.** Under the freeze it is **not** a final positive verdict for S3.

## 5 · SEVERITY
- 🔴 **MEAS-9 · Ninth divergence — no gap-open guard.** Entry gapped through the stop → booked as a **win**; through the target → forced loss; SCREEN skips both. Economic defect + engine divergence; untested by VE's 14 and by my first 17. **Blocks the gate.**
- 🔴 **MEAS-10 · T15/T16 fat-tail metrics DROPPED.** `StrategyReport` has no concentration/trim metric; the CEO fat-tail guard is uncomputable from the canonical output. Regression from `_screen`. **Blocks the gate** (a ratified engine must feed the fat-tail rule).
- 🟠 **MEAS-11 · T17 config_id produced but not enforced, and data-blind.** No comparison-guard function; config_id omits symbol/period/block ⇒ cross-instrument results falsely comparable. R11's *tagging* is real; its *protection* is not.
- 🟡 **MEAS-12 · Population-shift disclosure.** R3 reject-not-widen (a valid D-2 decision) silently changes which signals are eligible vs the widen-era engines; any pre/post number comparison crosses populations.

## 6 · SUB-SPECIFICATIONS — do they CLOSE the gap or MOVE it? (CEO task 1)
- **T4 (entry-bar target precedence):** R5 = "SL and TP checked inclusive on the entry bar, SL primacy." **Closes** the original T4 gap (entry-bar target is now counted, deterministically, with worst-case stop-first) — **but simultaneously MOVES a boundary case into the open** by dropping SCREEN's gap guard (MEAS-9). The normal case is closed; the gapped-beyond case is a new hole. **Net: closes T4, opens MEAS-9.**
- **T12/13 (spread full-vs-half / double-count):** R4 `spread + entry_slip + exit_slip` **closes** it — spread appears exactly once; slippage is per-execution; BASE 0.05 / STRESS 0.24 verified. The full-vs-half ambiguity is dissolved because there is no `2·` factor anymore. **Closed, not moved.**

## 7 · WHAT SURVIVES (verified)
One coherent semantics for the first time: next-open entry; **reject** (not widen) sub-floor stops with the risk left un-extended and no fictional P&L; spread-once cost in USD with a single tick source (0.01); entry-bar SL+TP inclusive with SL primacy; one explicit window `[ei, ei+H-1]`; over-horizon trades reported still-open rather than time-exited at a data boundary; every result immutably tagged with a rule-config hash; both cost scenarios carried. VE's 14 tests pass; 7 of 8 divergences close on the normal path.

## VERDICT — **PASS_WITH_LIMITATIONS as a spec; the ratification gate is NOT YET open.**
The evaluator is the right structural move and closes seven divergences honestly. It is **not** ready to be the gate until: **MEAS-9** (add the gap-open no-trade guard so a gapped-through stop cannot be a win), **MEAS-10** (restore symmetric fat-tail metrics into `StrategyReport` so the CEO guard is computable), and **MEAS-11** (enforce config-match before comparison **and** extend config_id to cover symbol/period/block) are closed and re-verified against an expanded suite (17 → 18, adding the gap-open case). **S3's +0.395 is a provisional, best-case, non-comparable number, not a final verdict.**

**THE FREEZE HOLDS.** No leaderboard, no economic elimination, and **no S3 flip** is definitive until every engine — including this evaluator — passes the full suite against the canonical semantics **and** config provenance matches. Any presentation of +0.395 (or any single number) as final is flagged here.

## HANDOFF → CEO / Statistician
1. **Adopt R1–R7/R11 as the canonical semantics** — the evaluator implements them correctly on the normal path. Make **all three engines consume it** (they currently keep their own logic).
2. **Close MEAS-9 (blocking):** add the entry-beyond-stop / entry-beyond-target no-trade guard SCREEN already has; add it as **test 18** to the suite. A gapped-through stop must never book a win.
3. **Close MEAS-10 (blocking):** put `best_share` and `trimmed_top1pct` back into `StrategyReport`; the fat-tail guard cannot run without them.
4. **Close MEAS-11:** add a comparison function that raises on config_id mismatch, and extend the config_id payload to include symbol + date range + block-manifest id (today it is data-blind).
5. **S3:** publish **both** BASE and STRESS, mark the cost UNCALIBRATED, and do **not** compare +0.395 to the pre-fix −0.39 (different config/population — R11 forbids it).
6. **Keep the freeze** until the expanded suite passes on every engine with matching provenance.

Red Team designed no remedy, modified no engine, ran no data on the market, changed nothing outside `red_team/`.
