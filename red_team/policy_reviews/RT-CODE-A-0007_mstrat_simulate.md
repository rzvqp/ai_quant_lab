# RED TEAM — CODE ATTACK · `mstrat.simulate` (the research/backtest engine)
### RT-CODE-A-0007 · Target: `code/mstrat.py` (statistician-foundation) — the engine that produced EVERY screening number
**Date:** 2026-07-31 · **Auditor:** Red Team · **Mandate:** CEO — the last unattacked end (C-R3). Produced 34 candidates + 1,972 legacy + 40 edges; enforces no gate; never attacked; inherited by the whole statistical stack (S-R5). **No data run · nothing modified · no remedy designed.**
**Method:** full source of `simulate`/`simulate_ref`/`_pool`/`analytic_p` + the S5/S6 setup providers + `alpha_lab.CFG` read by Red Team at source; TICK/constant provenance via git archaeology. Every claim source- or git-verified.

## HEADLINE — the execution LOGIC is worst-case-correct (better than the demo engine), but the engine runs on a 10×-wrong TICK that was documented-as-wrong and never fixed. The tick moves EVERY raw screening/triage number (conservatively); it CANCELS in the matched-null p-values. Nothing was falsely promoted.
The defect the CEO feared — a demo-engine-D1-style *optimism* — is **absent**: `mstrat` resolves collisions stop-first worst-case and checks the entry bar. The real defect is a **constant**: `TICK=0.1` is 10× the instrument tick (0.01), confirmed against the CEO's live account, documented on 2026-07-29, and **never patched in code**. It biases raw statistics **conservatively** (too much cost), so it cannot have inflated a result — but the entire triage/archival ledger rests on cost-inflated numbers that were never re-run.

---

## TARGET 1 — INTRABAR ORDER: CORRECT, and more complete than the demo engine
`simulate` exit loop (`mstrat.py:63-74`):
- **Scans from `j=ei` — the entry bar is INCLUDED** (not skipped). So an entry-bar stop-out is caught. *(This is exactly what the demo engine's D1 got wrong by starting at `ei+1`.)*
- **`target_first` defaults `False` = STOP-FIRST worst-case** (`:62,72-74`): on any bar where both stop and target are touchable, STOP wins → loss. `target_first=True` is a **measurement-only** toggle (`bracket_69.py:18-20`, "best-case bracket … Measurement only"); production `backtest()` uses `CFG` with no such key → default worst-case. Verified no production path sets it True.
- **Floored trade resolving on its own entry bar → INVALID/excluded** (`:80`, `widened and xi==ei`) — implementing the prereg's third INVALID clause (same-bar ambiguous fill) that the demo engine **omitted** (RT-CODE-A-0005 R1). Non-floored entry-bar resolutions are counted stop-first (correct).
- **VERDICT: NO D1, NO R1.** `mstrat` is the worst-case-correct reference; **the demo engine REGRESSED from it.** The screening numbers are not optimistically inflated by an execution-order bug.

## TARGET 4 — LOOKAHEAD: clean where checked
- The one risky feature — `or_high/or_low` broadcast to all bars of a block (`:20`, no shift) — is **gated safe**: `s5_setups:283` requires `bar_in_sess ≥ 4`, i.e. entries only **after** the opening range (bars 0-3) is complete, so the max is available, not peeked. S6 gates on `bis>10` and uses prev-session levels (`shift(1)`).
- Feature layer is shift/running/`merge_asof`-on-availability throughout: `prev_sess_*`/`pd_*`/`pw_*` via `avail` = next-period timestamp (backward as-of); `vwap` running cumulative; `atr_ma`/`compress` trailing then used at next-open. Lookahead-safe by construction where verified.
- *(Scope note: I verified the shared engine + S5/S6; a full per-family causal audit of all 20 providers was not run this pass. The gating pattern is sound where checked.)*

## TARGET 3 — HORIZON / EXIT: sound
- Pure structural exits (`rr`, `opp_liq`, `opp_struct`, `time`, `trailing`) plus a **hard 48-bar timeout cap on every trade** (`:58,63,75` — `to=48` default; window `[ei, ei+to)`; unresolved → exit at close `cl[xi]`). Level exits that never fill within 48 bars time-stop at close. Window boundary is handled (close exit), no out-of-bounds. Non-overlap enforced by the `last=xi` cursor (single position). Sound. *(48 and the trailing `1.5×ATR` are hardcoded execution magic numbers — see Target 6.)*

## TARGET 2 + 6 — 🔴 THE TICK: 10× wrong, documented, UNFIXED in code
**Git-verified:** `mstrat.py:10 = TICK=0.1` on **all seven branches**, introduced `8585723` (2026-07-13), **never changed** (the only two later touches, `6959dcd`/`7fa06e3`, left it untouched).

**The true tick is 0.01** — `STATISTICIAN_COST_CONSTANT_CORRECTION_…v1.0.md` (2026-07-29): "TICK = 0,01 dolari. Sursa: specificația instrumentului, nu codul — cotare pe 2 zecimale, confirmat direct de contul tău real (`4033,84/4033,89`). **Factor de eroare confirmat: 10×.**" The correction is **prose only** — the manifest states it was "verified at the instrument-spec source, **not the code**," and the doc footer says **"Nimic re-rulat."** No commit ever changed `TICK` in any `.py`.

**`simulate` uses the module `TICK`, not `CFG['tick']`** (`:45,53,63`). Two independent cost engines exist: `mstrat.simulate` reads module `TICK`; `alpha_lab.py`/`families.py` read `CFG['tick']`. Both are 0.1 today; **a partial "fix" of `CFG['tick']=0.01` would leave `mstrat.simulate` silently at 0.1** — a live divergence hazard. (Separately, the live execution repo already uses 0.01 while the research engine uses 0.1 — backtest and live already price at different ticks.)

**The `$0.40` provenance (exactly):** `cost=(spread_ticks+slip_ticks)*TICK=(1+1)*0.1=0.20` (`:45`); `R` subtracts **`2*cost=0.40`** round-trip (`:82`). The CEO's cited formula `2×0,1=0,40` is itself arithmetically 0.20 — the doubling lives at line 82, not the lines quoted. The Statistician doc flags this too.

**Quantified impact (corrected config = TICK 0.01, spread_ticks=slip_ticks=5, per the doc):**
- **Cost: 2× too high, universally.** Old round-trip `2*cost=0.40`; corrected `2*(5+5)*0.01=0.20`. (Net 2×, not 10×, because the correction re-scales `spread_ticks` 1→5 to keep the dollar spread realistic.) Every trade's `R` carries ~0.20px/risk of excess cost — for a ~15px stop, ~+0.013R per trade under correction; larger for tight stops.
- **Stop floor `5*TICK`: 10× too large** (0.5 vs 0.05) and `2*spread_ticks*TICK` 2× — but the floor `max(2*spread*TICK, 5*TICK, 0.10*ATR)` is **usually dominated by `0.10*ATR`** (ATR~10 → 1.0). The tick floor terms bind **only at low ATR (<5)**, where they were 10× too wide — widening stops and **inflating the INVALID-exclusion count**. The doc concedes this reopens "58.225 tranzacții INVALID … contra unei podele de zece ori prea mari" — documented, **not executed.**
- **Direction: CONSERVATIVE.** A too-large cost and too-wide floor make strategies look **worse**. Correcting **raises** every expectancy. So the error **cannot have inflated/falsely-promoted** anything — the opposite of the demo-engine D1 (which was optimistic and, once fixed, sank the leaders).

## TARGET 5 — THE PIVOTAL QUESTION: does the tick cancel in the matched-null, or bias calibration?
**It CANCELS in the matched-null p-value — verdicts are robust; raw screening numbers are NOT.**
- `matched_null.py` routes **both** the observed and the null through `MS.simulate` (`:2,19,91`) → **both carry the identical `2*cost` and the identical floor.** The p-value compares observed mean_R against the null distribution; a **uniform cost shift subtracts equally from both sides, so the difference — and thus the p-value — is invariant** to the tick. The floor bites on matched risk profiles (the null preserves the observed risk/ATR profile), so it too largely cancels.
- **Therefore the matched-null calibration and the scoped-FDR verdict are robust to the tick error** — unlike the demo-engine D1, which was an *entry-timing-dependent* optimism that would not cancel between structured and random entries. Here the bias is a **uniform cost**, and mstrat has **no** timing-dependent execution optimism → nothing to fail-to-cancel.
- **What does NOT cancel:** the **raw screening/triage statistics** (expectancy, PF, DD, total R) are *absolute*, not differences — they carry the full 2× cost + low-ATR floor distortion.

## WHAT MOVES, AND BY HOW MUCH (CEO's direct question)
- **MOVES — every raw screening/triage number** for all 34 candidates + 1,972 legacy + 40 edges (they only ever ran at TICK=0.1). Correcting **raises** all expectancies by ~+0.01–0.08R/trade (cost) plus a low-ATR-selective floor effect. **Conservative direction** (nothing inflated). The archival **negative/insufficient classifications** and the "none crossed zero at +0.075R" robustness claim rest on an **estimate, never a corrected-engine re-run**, and did not include the floor effect — they must be re-verified. The 5 archived-negative MK candidates (−0.45…−0.14R) are unlikely to flip, but **0022 (−0.157) and 0024 (−0.138)** are the doc's own "closest to zero" and the ranking is not guaranteed stable under correction (opposite direction to the D1 case, where fixing sank the leaders).
- **DOES NOT MOVE — the matched-null p-values and the scoped-FDR verdict** (cost cancels observed-vs-null). The "1 scoped-FDR survivor, fails OOS 0.0779" verdict (RT-CODE-A-0006) stands regardless of the tick.

## SEVERITY
- 🔴 **DEFECT M-D1 · `TICK=0.1` is 10× the true instrument tick, documented-wrong (2026-07-29) but never fixed in `mstrat.simulate`.** Every screening/triage number produced under it. Biases raw statistics conservatively (2× cost universal; 10× floor at low ATR); no corrected-engine re-run exists; the "correction" is prose + two throwaway scripts that themselves kept `FROZEN_TICK=0.10`.
- 🟠 **RISK M-R1 · Two divergent cost constants** (module `TICK` vs `CFG['tick']`) — a partial fix would silently split the two engines; and research (0.1) already diverges from live-execution (0.01).
- 🟡 **UNDOCUMENTED M-U1 · Hardcoded execution magic numbers** (`to=48` timeout, `1.5×ATR` trailing, `2500` null-pool size) with no cited provenance.
- 🟡 **M-U2 · `analytic_p` (the invalidated normal-approx null) is still in the engine** (`:139-145`), diagnostic-only but live in the code path via `pilot_pvalue`.

## WHAT SURVIVES (verified)
Worst-case intrabar order (stop-first, entry bar included, floored-same-bar INVALID) — **no D1/no R1**; lookahead clean where checked (`or_high` gated by `bis≥4`); horizon/exit sound (48-bar cap, timeout→close, non-overlap); **matched-null calibration robust to the tick (cost cancels)**; the demo engine's D1 is a regression *from* this engine, not inherited *by* it.

## VERDICT — **`mstrat.simulate` SURVIVES on execution logic; FAILS on a constant.**
The engine every number depends on is **worst-case-correct in its execution** — and demonstrably more correct than the enforcement engine that was built later. But it runs on a **tick that is 10× wrong, known-wrong for days, and unfixed**, so **every raw screening and triage statistic in the project is biased (conservatively) and none has been re-run through a corrected engine.** The matched-null verdicts are shielded (the cost cancels); the triage/archival ledger is not. **Nothing was falsely promoted** (the bias is pessimistic) — but the answer to "what depends on it" is: **every screening number moves when the tick is fixed, upward, and the archival classifications must be re-verified under a genuine corrected-engine re-run** (which does not exist).

## HANDOFF → Statistician, then CEO
1. **M-D1** — patch `mstrat.py:10` (and reconcile with `CFG['tick']` and the corrected `spread_ticks/slip_ticks=5`), then **re-run the full campaign** (34 + 1,972 + 40) through the corrected engine; the current triage/archival ledger and the "none crossed zero" claim are un-rerun estimates.
2. **M-R1** — collapse the two cost constants to one source of truth; align research and live ticks.
3. Matched-null/scoped-FDR verdicts need **no** re-run for the tick (cost cancels) — but remain subject to RT-CODE-A-0006's out-of-domain caveats (structural stops, small-n).
4. M-U1/M-U2 — source or retire the magic numbers; consider removing the invalidated `analytic_p` from the live path.

This closes the three unattacked ends from RT-AUDIT-CHAIN-0001 (enforce → RT-CODE-A-0005; validate → RT-CODE-A-0006; produce → this). Red Team designed no remedy, ran no data, modified nothing outside `red_team/`.
