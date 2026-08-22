# ALPHA_EARLY_TRAP_E1_EXECUTION_CONVERSION_REPORT

**Mandate:** `ALPHA-EARLY-TRAP-E1-EXECUTION-CONVERSION-001` · **Date:** 2026-08-22.
**Lineage:** discovery `6a5d535` · audit `de35453` · canonical freeze `edbc687`.
**Terminal status:** `EARLY_TRAP_E1_EXECUTION_RESEARCH_COMPLETE` · **`EARLY_TRAP_E1_SIGNAL_SUPPORTED_EXECUTION_NOT_SOLVED`**.
**Scope:** execution research ONLY on the FROZEN `EARLY-TRAP-E1 v1.0.0` signal (118 canonical episodes, consumed unchanged). NO signal retuning. DEV-only; no CALIB/V1/2025+/promotion. **0 executable candidates frozen.** Net of STRESS cost. Broker disabled.

---

## 0. Headline — answers to the §35 questions
1. **Can EARLY-TRAP-E1 be monetized?** **No** — no entry/stop/target architecture achieves positive, generalizing net expectancy.
2. **Is immediate E1 execution profitable?** **No** (baseline EA-sweep-mid: EXEC_DISC −0.075, EXEC_CONF −0.303).
3. **Does waiting for a retest improve economics?** **No — worse.** Fill rate 0.29; 53 clean winners reach mid *before* the retest (missed); the 34 fills average −0.57 (WR 0.21).
4. **Does M5 timing add value?** **N/A** — no parent policy survived to refine (M5 only refines a working entry; none worked). Removed per §7.
5. **Which structural stop best survives adverse path?** **Neither.** Sweep-extreme (STOP-A) → RR<1; E1-high (STOP-B) → stopped even more (66–69% stop-then-mid). Both fail.
6. **How often does each stop lose before the signal is directionally correct?** **53–69%** — the decisive "right-signal/wrong-geometry" number.
7. **Is Asia midpoint economically tradeable?** **No** (negative both splits; executable WR ~0.40, not the 0.81 selection rate).
8. **Is Asia Low better?** Marginally better *average* but **median −1.05, best-10%-removed negative, 2021/2022 negative** — a tail lottery, not tradeable.
9. **Does a larger continuation target exist?** **Diagnostically yes** (MFE median 69p; 44% ≥80p, 30% ≥100p) — but **not capturable** (stop hit first).
10. **Is partial-midpoint + runner useful?** **No** (avg −0.062, negative both splits).
11. **Does execution survive 2021/2022/2023?** **No** — only 2023 positive; **2021 and 2022 negative**.
12. **Does it pass tail gates?** **No** — best-10%-removed negative everywhere; median R ≈ −1.0.
13. **Final product — mean-reversion / continuation / both?** **`DIRECTIONAL_SIGNAL_NOT_ECONOMICALLY_EXECUTABLE`** with honest structural stops on this population.
14. **Executable SHORT candidate worthy of Statistician review?** **No** — signal remains supported; execution is the wall.

## 1. Canonical signal identity + fingerprint verification (§34)
Consumed `EARLY-TRAP-E1 v1.0.0` via `early_trap_e1_signal.py`. **Reproduction PASS** (329 parents / 118 fires / 118 days; DISC 68 P(mid) 0.794, CONF 50 P(mid) 0.840) and fingerprints verified equal to `edbc687` before any execution: `implementation_fingerprint=33bec449…`, `episode_set_identity=920dee40…`. The signal was not modified.

## 2. Execution evidence split (§26)
New chronological **EXEC_DISCOVERY / EXEC_CONFIRMATION** split over the 118 episodes (independent of the old Alpha DISC/CONF): DISC 70, CONF 48 (cut 2023-05-08). Policies frozen on EXEC_DISC, evaluated unchanged on EXEC_CONF. No CALIB.

## 3. Path decomposition (§22) — where expectancy is created/destroyed
| class | n | share |
|---|---|---|
| A — mid reached, no new high | 63 | 53.4% |
| B — new high first, then mid | 36 | 30.5% |
| C — new high, mid never | 19 | 16.1% |
| D — no new high, mid never | 0 | 0.0% |
P(reach mid) 0.839, P(new high after E1) 0.466. **The 30.5% (B) reach the mid but only *after* a new high — i.e. after any honest structural stop is already hit.** That class is the graveyard of the strategy.

## 4. Entry architectures (§7, §8)
- **ENTRY-A (immediate, next M15 open after E1):** the mandatory baseline — see §5/§6 grids.
- **ENTRY-B (Asia-High retest, K=8):** fill rate **0.29** (34/118). Outcomes: 53 reached mid before retest (missed winners), 24 invalidated, 7 timed out. Filled economics: mid avg **−0.571** (WR 0.21, med −1.17), low avg −0.214 (med −1.17). **Strictly worse than ENTRY-A** — the retest selects episodes that continue up into the stop and forfeits the clean straight-to-mid winners.
- **ENTRY-C (M5 timing):** not evaluated — no parent policy survived to refine; M5 refines entry only (§7), so it was removed.

## 5. Stops (§9–§13) + target grid (ENTRY-A, net STRESS) — EXEC_DISC | EXEC_CONF
| policy | DISC avg / med / b10 | CONF avg / med / b10 | %stop→mid |
|---|---|---|---|
| EA · STOP-A(sweep) · mid | −0.075 / −0.156 / −0.319 | −0.303 / −1.118 / −0.526 | 0.53 |
| EA · STOP-A · low | +0.055 / −1.055 / −0.449 | +0.078 / −1.119 / −0.282 | 0.58 |
| EA · STOP-A · RR1.0 | −0.140 / −1.031 / −0.274 | −0.331 / −1.071 / −0.446 | 0.60 |
| EA · STOP-A · RR1.5 | −0.133 / −1.047 | −0.237 / −1.100 | 0.62 |
| EA · STOP-A · RR2.0 | −0.198 | −0.185 | 0.63 |
| EA · STOP-B(E1 high) · mid | −0.166 / −0.778 | −0.256 / −1.121 | 0.55 |
| EA · STOP-B · low | −0.036 / −1.096 | +0.281 / −1.129 | 0.62 |
| EA · STOP-B · RR1.0 | −0.173 | −0.315 | 0.65 |
| EA · STOP-B · RR1.5 | −0.230 | −0.269 | 0.66 |
| EA · STOP-B · RR2.0 | −0.187 | −0.154 | 0.69 |
**Zero policies survive EXEC_DISC→CONF with positive expectancy.** The only positive-average cells (Asia-low targets) have **median R ≈ −1.05** (most trades stopped) and **best-10%-removed negative** — tail lotteries, not edges. STOP-B (tighter) raises the stop-then-mid rate to 0.66–0.69 (stops out more of the eventually-correct trades).

## 6. Causal execution timestamp (§6, §21)
Entry = M15 open at `e1_index + 1` (strictly after E1 close_time; the canonical `earliest_execution_time`). Same-bar SL/TP ambiguity resolved **conservatively (stop first)**. No lookahead. Cost = STRESS RT 2.4 project pips, subtracted per trade; expectancy is **net** (gross mid-target is also negative — cost is not the deciding factor).

## 7. Midpoint vs Asia-low vs continuation (§14, §15, §16)
- **Asia mid** (primary mean-reversion): negative both splits — executable WR ~0.40 (not 0.81) because the ~47% new-high excursions hit the stop before the mid.
- **Asia low** (deeper): better RR, positive average on some splits, but median −1.05, tail-fragile, single-year.
- **Larger downside (diagnostic):** MFE median 69p, P75 118p, P90 152p; P(MFE≥80p) 0.44, ≥100p 0.30, ≥150p 0.11. **The downside room genuinely exists** — the constraint is capturing it past the adverse path, not target availability.

## 8. Fixed-RR diagnostic (§17)
RR 1.0/1.5/2.0 all negative (both stops, both splits). Higher RR lowers WR faster than it raises payoff; no RR rescues the payoff surface.

## 9. Stop-out-before-target (§23) — the decisive diagnostic
**53–69% of stopped-out trades later reach the mid.** The signal is directionally correct (P(mid) 0.84) but the honest structural stop — which *must* sit above the sweep extreme because 46.6% make a new high after E1 — is hit before the reversion completes. This is **RIGHT SIGNAL / WRONG GEOMETRY**, quantified.

## 10. Partial + runner (§19)
One predeclared 50/50 (mid + Asia-low, stop sweep): avg **−0.062**, median −0.45, best-10%-removed −0.366, negative both splits. Trade management does not rescue a geometry problem (as §19 anticipated).

## 11. Session (§24) + year (§25) attribution — diagnostic only
- **Session (EA-sweep-low):** LONDON avg +0.104 (median −1.10, b10 −0.403), OVERLAP −0.052 — London-concentrated but median-negative/tail-fragile.
- **Year:** 2021 **−0.117**, 2022 **−0.120**, 2023 +0.190. **Positive only in 2023; 2022 negative** — fails temporal robustness. Per §33 these remain diagnostic; **no London-only or 2023-only filter was added** (that would create a new signal requiring fresh discovery/audit).

## 12. Tail robustness (§29)
Every policy fails the serious gate: median R ≈ −1.0, best-10%-removed < 0. The positive-average Asia-low policies are carried by a few large winners (top-slice concentration), not a broad edge.

## 13. Candidate ranking + graveyard (§27, §28)
**No executable candidate.** Closest = EA-STOP-A-Asia-low (positive avg both splits) — killed by median −1.05 + best-10%-removed<0 + 2021/2022-negative + single-period dependence (§28 triggers). All other policies negative. ENTRY-B falsified. Partial+runner negative. Recorded in `exec_convert.py` / `exec_convert2.py`.

## 14. CEO recommendation
1. **`EARLY_TRAP_E1_SIGNAL_SUPPORTED_EXECUTION_NOT_SOLVED`.** The independently-supported EARLY-TRAP-E1 **selector is directionally correct** (P(reach Asia mid) 0.84, MFE median 69p) but **cannot be monetized with any honest structural geometry** on this population. The binding constraint is quantified: **53–69% of stopped trades later reach the mid** — the sweep that defines the signal means ~47% poke a new high after E1, so the stop (necessarily above the sweep extreme) is hit before the ~21p reward to the mid is captured; reward < risk, and tighter stops only get hit more.
2. **The signal's economic role is `DIRECTIONAL_SIGNAL_NOT_ECONOMICALLY_EXECUTABLE`** as a standalone short here — neither a clean mean-reversion nor a continuation edge survives. This is the **same wall as the session-trap mandate (RR-geometry), now definitively established for the frozen early signal** with a proper EXEC split, path decomposition, and stop-out-before-target diagnostic.
3. **The signal remains SUPPORTED and FROZEN** (nothing here changes `edbc687`); its value is as a **selector**, potentially useful only in combination with information that reduces the new-high adverse path — which would require a **new signal** (new discovery + audit), explicitly **not** built here (§33). Diagnostic leads (London-concentration, larger MFE availability) are recorded, not promoted.
4. **No candidate for Statistician review; no promotion; broker disabled; DEV-only; no CALIB.** The 9 frozen strategies are unaltered; portfolio SHORT remains only frozen `H4-bo-raw-S`.

**Terminal status:** `EARLY_TRAP_E1_EXECUTION_RESEARCH_COMPLETE` · `EARLY_TRAP_E1_SIGNAL_SUPPORTED_EXECUTION_NOT_SOLVED`. **STOP.**
