# RED TEAM — S5 & S20 CLEAN INDEPENDENT VALIDATION
### RT-ALPHA-S5-S20-CLEAN-INDEPENDENT-VALIDATION-001 · Auditor: Red Team · 2026-08-21

Independent two-environment validation of the frozen strategies **S5** (`C_2d587447`) and **S20**
(`C_09d2245b`) on the frozen clean 52,572-bar population, against the frozen Statistician gates A–H.
Strategies validated **separately** — no pooling, no portfolio, no cross-compensation.

---

## 0 — VERDICTS (independent)

```
S5_VALIDATION_EXECUTION_MODEL_INTEGRITY_PASS
S20_VALIDATION_EXECUTION_MODEL_INTEGRITY_PASS
S5  : INDEPENDENT_VALIDATION_PASS
S20 : INDEPENDENT_VALIDATION_FAIL   (gate G — risk degradation: max drawdown 23.6R > 15R)
```

No promotion authorized: not integrated into AI Trader, Strategy Catalog untouched, broker/live disabled.
Return to CEO.

---

## 1 — EVIDENCE IDENTITY PROOF (§1)

| property | required | RT-verified |
|---|---|---|
| start | 2023-07-24 10:30:00Z | ✓ (canonical idx 144522) |
| end | 2025-10-12 23:00:00Z | ✓ (idx 197093) |
| bars | 52,572 | ✓ exactly |
| population_ohlc_sha256 | `bac65b1a8840a0b8…457ea1` | ✓ reproduced (HLOC ×1e6 int64 LE) |
| timeline_sha256 | `4c9ce7b7f245bb9a…4728a` | ✓ reproduced |
| source file sha256 | `57f4ed95…ccd37` | ✓ |
| contiguous · inside B4 · manifest-gated | yes | ✓ |
| > consumed slice (ends 2023-07-24 10:15Z) | 0 overlap | ✓ |
| < ratified Final Holdout (starts 2025-10-23 09:15Z) | 0 holdout bars, 11-day margin | ✓ |
| `FINAL_HOLDOUT_ACCESS_COUNT` | 0 | **0 — never inspected** |

mstrat's loaded data over `[start,end]` is **byte-identical** (HLOC) to the frozen population hash.

## 2 — PROTOCOL & STRATEGY IDENTITY (§2)

Frozen Statistician artifacts (`ed49c2c`, branch statistician-foundation, local=remote ×4):
`STAT_S5_S20_CLEAN_VALIDATION_FREEZE.md` (operative gates A–H + execution contract), plus the two prep
protocols. Gates and population taken verbatim; **not redefined**.

| | S5 | S20 |
|---|---|---|
| candidate | `C_2d587447` | `C_09d2245b` |
| spec (frozen, unmodified) | `S5{session=ny, mode=breakout, side=up, stop=or_opp, exit=rr3}` | `S20{ctx=h4up, exit=rr3, lb=50, stop=atr, trig=breakout}` |
| representative | `7472f3d412f2` | `601e20753a4a` |
| direction | LONG-only | LONG |
| HTF context | native h4 (ed57853-consistent for 2023+) | `ed57853` `h4_trend_up` |

## 3 — EXECUTION-MODEL PROOF (§4) — the RT-CODE-A-0007 defect was NOT used

The engine ships `mstrat.TICK = 0.1` (the known 10× defect). `simulate` uses it in the stop floor
`max(2·spread·TICK, 5·TICK, 0.10·ATR)` → `5·TICK = 0.50` (wrong) and in the S5 stop buffer `2·TICK`.
**RT overrode it to the ratified `0.01`** before any execution, giving the correct floor `max(0.05, 0.10·ATR)`
and cost self-compensated via `slip_ticks = RT/(2·TICK)`. Verified independently:

- `TICK = 0.01` enforced; assertion that baseline was the 0.1 defect.
- STRESS round-trip = **0.24**, BASE = 0.05 (ratified cost model `AI_TRADER_SHADOW_COST_MODEL_v1.json`).
- min stop = `max(2·spread, 0.05, 0.10·ATR)` (spread folded into slippage → floor = max(0.05, 0.10·ATR)).
- **Fidelity**: the RT instrumented engine reproduces `mstrat.simulate` BASE R **exactly** (`allclose`, both at TICK=0.01) — no semantic drift.
- floor-binding fraction = **0%** for both strategies (real strategy stops always exceeded the floor), so the 0.05-vs-0.50 correction did not silently reshape either result — but the ratified model was enforced regardless.

`VALIDATION_EXECUTION_MODEL_INTEGRITY = PASS` for both.

## 4 — FROZEN TRADE-LEDGER HASHES (§5) — frozen before scoring

```
S5_VALIDATION_TRADES_SHA256  = cd4e8d4aae0104cd1041898cf136917b9ec3194c343ba6840fab0bdb7831e1d7   (295 trades)
S20_VALIDATION_TRADES_SHA256 = 53622efc93b77fe7f443ea8914b9fc31189ab2ae110c9c2f0987ff71dd91ca42   (553 trades)
```
Env A (execution) produced immutable ledgers; Env B (scoring) re-verified both hashes fail-closed and never
re-executed a strategy.

## 5 — GATES A–H

| gate | criterion | S5 | S20 |
|---|---|---|---|
| **A** sample | n ≥ 100 | **PASS** (295) | **PASS** (553) |
| **B** BASE | BASE net > 0 | **PASS** (0.2098) | **PASS** (0.1485) |
| **C** STRESS | STRESS net > 0 @ RT 0.24 | **PASS** (0.1925) | **PASS** (0.1027) |
| **D** temporal | ≥2/3 thirds >0, none < −0.10 | **PASS** [0.273, 0.153, 0.201] | **PASS** [0.202, 0.046, 0.188] |
| **E** tail | best-1%-removed BASE > 0 | **PASS** (0.1907) | **PASS** (0.1225) |
| **F** delay | +1-bar entry BASE > 0 | **PASS** (0.1581) | **PASS** (0.0876) |
| **G** risk | maxDD ≤ 15R ∧ maxLoss ≤ 2.0R | **PASS** (DD −6.44R, loss −1.03R) | **FAIL** (DD **−23.59R** > 15R; loss −1.04R OK) |
| **H** fidelity | exact spec/config, engine reproduced | **PASS** | **PASS** |

**S5: A–H all PASS → `INDEPENDENT_VALIDATION_PASS`.**
**S20: gate G FAIL → `INDEPENDENT_VALIDATION_FAIL`.** Every other gate passes; the failure is risk degradation
— the equity curve draws down 23.6R (≈57% over the 15R limit), driven by clustered losses at a 32% win rate,
**not** by any single oversized loss (max loss −1.04R is within 2.0R).

## 6 — BASE / STRESS / TEMPORAL THIRDS (§8/§10)

3 equal-bar chronological thirds of the 52,572-bar window (boundaries **2024-04-19 11:45Z** / **2025-01-15 18:45Z**):

| | S5 third BASE (n) | S20 third BASE (n) |
|---|---|---|
| T1 | 0.273 (97) | 0.202 (162) |
| T2 | 0.153 (91) | 0.046 (170) |
| T3 | 0.201 (107) | 0.188 (221) |

All six thirds positive; none below −0.10. Both pass D. S20's middle third (0.046) is thin but positive.

## 7 — TAIL ANALYSIS (§9)

| | S5 | S20 |
|---|---|---|
| top-10% share | 1.226 | 2.005 |
| top-5% | 0.677 | 0.985 |
| top-2% | 0.242 | 0.401 |
| top-1% | 0.097 | 0.182 |
| best-trade share | 0.048 | 0.036 |
| best-1%-removed BASE | 0.1907 | 0.1225 |
| winsor-99 BASE | 0.2098 | 0.1485 |
| classification | **LEGITIMATE_POSITIVE_SKEW** | **LEGITIMATE_POSITIVE_SKEW** |

Both survive removal of the best 1% and remain strongly positive (S5 0.191, S20 0.123). Neither is
outlier-dependent. S20's edge is more tail-weighted (top-1% carries 18.2% of total R) but robust to best-1%
removal. **Note:** S20's positive expectancy is genuine, but its tail-weighting co-exists with the deep
drawdown that fails gate G.

## 8 — EXECUTION DELAY (§8 gate F)

| delay +1 bar | S5 | S20 |
|---|---|---|
| BASE | 0.1581 | 0.0876 |
| STRESS | 0.1370 | 0.0164 |

Both remain BASE-positive under a one-bar entry delay (F PASS). S20's delayed STRESS (0.016) is barely
positive — a further fragility signal, though F is judged on BASE.

## 9 — DRAWDOWN / RISK (§8 gate G)

| | S5 | S20 |
|---|---|---|
| max drawdown | **−6.44R** (≤15R ✓) | **−23.59R** (>15R ✗) |
| max single loss | −1.03R (≤2.0R ✓) | −1.04R (≤2.0R ✓) |
| win rate | 0.549 | 0.324 |
| profit factor | 1.609 | 1.219 |

S20's low win rate (0.324) with RR3 geometry produces long losing runs → a 23.6R peak-to-trough drawdown that
breaches the risk ceiling. This is the decisive failure.

## 10 — TRADE GEOMETRY (§7) — neither is micro-scalping

| | S5 | S20 |
|---|---|---|
| SL median | $12.44 / **124.4 pips** | $4.75 / **47.5 pips** |
| SL P25/P50/P75 ($) | 9.07 / 12.44 / 17.15 | 3.34 / 4.75 / 6.58 |
| TP median | $37.32 / **373.2 pips** | $14.26 / **142.6 pips** |
| TP P25/P50/P75 ($) | 27.20 / 37.32 / 51.44 | 10.02 / 14.26 / 19.73 |
| TP min / max ($) | 5.85 / 180.96 | 3.94 / 60.77 |
| **% TP ≥ 70 pips** | **99.3%** | **92.4%** |
| **% TP ≥ 80 pips** | **99.3%** | **86.1%** |
| **% TP ≥ 100 pips** | **99.0%** | **75.0%** |

(RR3 → TP = 3× risk exactly; convention 10 project pips = $1.00.) **Neither strategy is a micro-scalper** —
S5 targets a median 373 pips (99% of trades ≥100 pips); S20 a median 143 pips (75% ≥100 pips). This directly
satisfies the CEO's stated preference against micro-scalping, for both. Measured from the frozen strategies —
nothing was altered to enlarge targets.

## 11 — REALIZED PROFILE (§8)

| | S5 | S20 |
|---|---|---|
| trades | 295 | 553 |
| win rate | 0.549 | 0.324 |
| avg R (BASE) | 0.210 | 0.148 |
| median R | 0.125 | −1.008 |
| avg winner / loser | +1.009 / −0.763 | +2.556 / −1.004 |
| profit factor | 1.609 | 1.219 |
| gross / BASE / STRESS | 0.214 / 0.210 / 0.193 | 0.161 / 0.148 / 0.103 |
| holding median (P25/P75) bars | 49 (30.5 / 49) | 8 (3 / 19) |
| MAE / MFE median ($) | 6.83 / 10.42 | 4.80 / 5.49 |
| long fraction | 1.00 | 1.00 |

S5 is a slower, higher-win-rate breakout (median hold 49 bars); S20 is a faster, low-win-rate,
tail-carried trend strategy (median hold 8 bars, median R negative — it pays out through RR3 winners).

## 12 — HISTORICAL CONTAMINATION DISCLOSURES (§10/§17) — preserved

**S5:** the historical VALIDATION partition (2020-07-21 → 2023-07-24) was **consumed** — `rep_val_exp = 0.17885`
entered `robustness_score` and the confidence gate. Counterfactually removing `val_exp`, S5's rank stays **1**
and its representative stays **RR3** — the exposure changed neither ranking nor spec, but it does **not** restore
blindness. The current clean population (2023-07-24 → 2025-10-12) is the independent evidence, and S5 passes on it.

**S20:** `rep_val_exp = 0.08733` influenced family ranking; counterfactually the rank moved **4 → 6**.
Representative/specification selection was `val_exp`-free (`[fragile, stab, n, t1]` rule). This is disclosed, not
erased. S20 **fails** the clean validation regardless (gate G), so contamination does not affect the outcome.

## 13 — FINAL HOLDOUT (§13) · INTEGRITY (§14)

`FINAL_HOLDOUT_ACCESS_COUNT = 0` — the ratified final holdout (≥2025-10-23) was never loaded, sliced, or
inspected. No integrity-fail condition was triggered: population = frozen hash; holdout untouched; no
`mstrat.CFG`/defective tick used for cost or floor; specs identical to frozen; S20 HTF from `ed57853` only; no
trades deleted after metrics; no threshold changed after seeing results; no retuning; no M5 refinement; no
pooling. **INTEGRITY: PASS.**

## 14 — INDEPENDENT FINAL VERDICTS

```
S5  : INDEPENDENT_VALIDATION_PASS
S20 : INDEPENDENT_VALIDATION_FAIL   (gate G — max drawdown 23.6R exceeds the 15R risk ceiling)
```

## 15 — RECOMMENDATION TO CEO (§16)

- **S5** clears every pre-registered gate on genuinely clean, previously-unconsumed evidence, with legitimate
  positive skew, positive stress/delay expectancy, controlled drawdown (−6.4R), and non-scalping geometry (373-pip
  median target). It is the first S-family strategy to pass a clean independent validation. **Recommend: eligible
  for CEO consideration** — but per §16 it is **not** promoted here (no AI Trader, no Strategy Catalog, no broker);
  return to CEO for the promotion decision. The S5 historical-consumption disclosure (§12) should be carried
  forward as a known caveat on its provenance, not its clean-evidence result.
- **S20** has a real positive expectancy (BASE 0.148, STRESS 0.103, best-1%-removed 0.123) but **fails the risk
  ceiling** — a 23.6R drawdown at a 32% win rate. Under the frozen gates it is **NOT validated**. **Recommend:
  do not promote.** If desired, a future *separate* research cycle could examine S20's drawdown/position-sizing
  (a new strategy version, not this frozen candidate, and not on this now-consumed clean region).

Neither result authorizes any integration. Both verdicts return to CEO.

---

*Red Team · two-environment isolation · TICK=0.01 ratified (RT-CODE-A-0007 defect overridden) · engine fidelity
verified · Final Holdout access 0 · no pooling · no retuning · changes only in `red_team/` · LEDGER E97 (prev E96).*
