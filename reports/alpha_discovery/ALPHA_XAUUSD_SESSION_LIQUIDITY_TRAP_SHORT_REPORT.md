# ALPHA_XAUUSD_SESSION_LIQUIDITY_TRAP_SHORT_REPORT

**Mandate:** `ALPHA-XAUUSD-SESSION-LIQUIDITY-TRAP-SHORT-001` · **Date:** 2026-08-22 · **Stat evidence base:** commit `b8d0447`.
**Terminal status:** `XAUUSD_SESSION_LIQUIDITY_TRAP_DISCOVERY_COMPLETE` · **`SESSION_LIQUIDITY_SIGNAL_FOUND_EXECUTION_UNSOLVED`**.
**Firewall:** 100% XAUUSD price-only (no DXY/yields/macro/news/cross-asset/order-flow assumptions); gated M5 → causal M15/H4; no `read_csv`; N4=0; 2025+=0; no V1/holdout/CALIB. **~12 executable configs tested (S1/S2/S4/S5 × mid/low × session; ≤24, checkpoint honored), 0 frozen.** DEV-only. No promotion; broker disabled; 9 frozen strategies untouched.

---

## 0. Headline — answers to the §27 questions
1. **Is Asia-High liquidity-taking predictive of a bearish move?** **Yes, as a probability** — a sweep that *returns inside* the Asia range (trap) has P(reach Asia mid) **0.508** vs a sweep that is *accepted above* (valid breakout) **0.189** (+0.32 separation, matched control). **But not as positive expectancy.**
2. **More useful in London or New York?** **London** (232 of 329 parent sweeps) + **Overlap** (83); NY-only sweeps are rare (14 — the Asia high is usually already swept by NY time). Overlap has the highest confirmation P(mid) (0.864).
3. **Does return inside range add value?** **Yes** (P(mid): S0 0.46→S1 0.55 DISC; 0.40→0.47 CONF).
4. **Does bearish displacement add value?** **For probability, strongly** (S1→S2 P(mid) 0.55→0.78 DISC, 0.47→0.76 CONF — holds) — **but it HURTS expectancy** (late entry vs a distant structural stop).
5. **Does failed reclaim add value?** **No** — S3 (as defined: return up to Asia-High, close back below) *selects days price rallied back* and is less bearish (P(mid) drops to 0.47/0.34).
6. **Does the second bearish impulse add value?** Marginal/no (S5 thin, mixed).
7. **Trend short or mean reversion?** The *probability* signal is mean-reversion-flavoured (S2 P(mid) 0.76 > P(low) 0.54) — **but neither target is tradeable** (both net negative on confirmation).
8. **Is Asia mid a better target than a trend target?** Mid = higher hit-rate/worse RR; low = better RR/lower hit-rate; **both net negative** on confirmation.
9. **Does Asia range width matter?** **Yes, suggestively** — wide Asia days (≥120p) are the only positive width bucket (S2 mid +0.126, n17, in-sample); narrow days strongly negative. Thin.
10. **Does sweep magnitude matter?** **Weakly** — mid-size sweeps (25–60p) least bad; no monetizable edge.
11. **Can we distinguish failed breakout from valid breakout?** **Yes — the cleanest finding** (trap P(mid) 0.508 vs valid breakout 0.189).
12. **Does M5 improve entry?** **N/A by design** (§14/§24: M5 only if the M15 parent survives — no layer cleared the execution gate).
13. **Is there a robust session-specific SHORT strategy?** **No executable one** — signal found, execution unsolved.

## 1. Session definitions + timezone/DST audit (§2) — frozen before testing, verified
Canonical timezone handling via `tz_convert` (verified: London offset +1:00 Jun / 0:00 Dec; NY −4:00 / −5:00; Tokyo +9:00 both — no DST). **Frozen sessions:** ASIA = 00:00–07:00 UTC (Tokyo 09:00–16:00 JST; **Japan has no DST → fixed UTC, DST-safe**); LONDON = 08:00–16:00 Europe/London local (DST-correct); NEW YORK = 08:00–17:00 America/New_York local (DST-correct); OVERLAP = both. No historical session is mis-shifted by DST (London/NY boundaries move with their own DST; Asia is DST-immune).

## 2. Asia range construction (§3) — causal
Per UTC day, Asia High/Low/Mid/Width computed from M15 bars in 00:00–07:00 UTC, **complete at 07:00 UTC** before any London/NY bar uses it (no partial-session leakage). Accepted days = 564/680 (≥12 Asia M15 bars). Median Asia width **75.9p**.

## 3. Raw Asia-High sweep catalog (§4, §19) — raw-signal-first
| stage | N (DEV) |
|---|---|
| parent Asia-High sweeps | **329** |
| — LONDON | 232 |
| — NY (fresh) | 14 |
| — OVERLAP | 83 |
| S1 returned inside range | 255 (77%) |
| median sweep distance above Asia High | 20.3p |
Discovery/confirmation split by day (fixed before search): **DISCOVERY 2021-07→2023-04-27 (197 sweeps), CONFIRMATION 2023-04-27→2023-12-29 (132 sweeps).** Confirmation is essentially 2023 (a known limitation — the chronological split yields a single-year OOS window).

## 4. Common-parent attribution (§6) — P(reach Asia MID) | P(reach Asia LOW)
| layer | DISC n | P(mid) | P(low) | CONF n | P(mid) | P(low) |
|---|---|---|---|---|---|---|
| S0 sweep only | 197 | 0.462 | 0.228 | 131 | 0.397 | 0.221 |
| S1 +return inside | 152 | 0.553 | 0.296 | 103 | 0.466 | 0.282 |
| S2 +bearish displacement | 86 | **0.779** | 0.465 | 50 | **0.760** | 0.540 |
| S3 +failed reclaim | 94 | 0.468 | 0.266 | 61 | 0.344 | 0.230 |
| S4 +structure break | 58 | **0.948** | 0.586 | 34 | **0.912** | 0.676 |
| S5 +second impulse | 27 | 0.778 | 0.444 | 17 | 0.765 | 0.706 |
**The probability signal is genuine and generalizes:** return-inside and especially bearish-displacement / structure-break raise P(reach mid) to 0.76–0.91 and *hold on confirmation*. S3 (failed reclaim) subtracts (selects rallying days).

## 5. Matched control (§7, §20) — the cleanest positive finding
| population | n | P(reach mid) | P(reach low) |
|---|---|---|---|
| **TRAP** (sweep → returned inside) | 254 | **0.508** | 0.280 |
| **VALID BREAKOUT** (sweep → accepted above) | 74 | **0.189** | 0.041 |
A **+0.32** separation in P(mid): the *failure to sustain* the Asia-High breakout genuinely predicts a higher chance of reverting into the range. This is the real, novel session-conditioning signal — absent from the generic swing-sweep family.

## 6. Execution expectancy (§14, §15, §16, §22) — NEGATIVE on confirmation (the wall)
Short at next M15 open after the layer event; **structural stop = sweep extreme + buffer** (§15); STRESS cost; one trade/day (non-overlapping). Expectancy R (avg / median / best-5%-rem / best-10%-rem):

**Mean-reversion (Asia MID) target:**
| layer | DISC avg/med/b10 | CONF avg/med/b10 |
|---|---|---|
| S1 | −0.014 / −0.088 / −0.298 | −0.281 / −1.053 / −0.504 |
| S2 | −0.120 / −0.083 / −0.240 | −0.333 / −0.336 / −0.427 |
| S4 | −0.103 / −0.095 / −0.182 | −0.288 / −0.294 / −0.349 |

**Trend (Asia LOW) target:**
| layer | DISC avg/med/b10 | CONF avg/med/b10 |
|---|---|---|
| S1 | +0.062 / −1.047 / −0.458 | −0.154 / −1.082 / −0.500 |
| S4 | +0.062 / +0.074 / −0.086 | −0.107 / −0.132 / −0.229 |
| S5 | −0.072 / −0.105 / −0.244 | +0.106 / +0.109 / −0.010 (n17) |

**Every layer and both targets are negative on confirmation.** The lone positive (S5 trend CONF +0.106) is n=17, best-10%-removed −0.010 (noise). **Root cause of the dissociation:** the high hit-rates come from entering *after* the bearish confirmation, so the reward remaining to the mid is small while the honest structural stop (sweep high) is far above → RR < 1, and the ~24–46% full stop-outs (−1R) sink the expectancy. 2023 (the confirmation year) was strongly bull for gold, so trap-shorts were run over.

## 7. Session / width / sweep-size / time-of-day (§9, §10, §11, §23)
- **Session (S2 mid):** LONDON CONF −0.411, OVERLAP CONF −0.151 (least bad). NY too sparse.
- **Asia range width (S2 mid, DEV):** [0,50) −0.351, [50,80) −0.240, [80,120) −0.195, **[120,∞) +0.126 (n17, b10 +0.013)** — wide-range days the only positive bucket, thin/in-sample.
- **Sweep magnitude:** [25,60)p least bad (−0.018); no edge from size.
- **Time-of-day (London hour):** early London [7,9) least bad (−0.045, WR 0.5); midday [11,13) worst (−0.494). No positive window.

## 8. Mean-reversion vs trend (§17) — separated, both fail
The signal is **mean-reversion-flavoured** (P(mid) > P(low) at every layer), but the Asia-mid target does **not** execute positive on confirmation (S1–S5 all −0.28 to −0.34). The trend (Asia-low) target is also negative. **Neither class survives** — so this is not reclassified as a mean-reversion candidate.

## 9. Lower-timeframe value (§24) — N/A by design
No layer cleared the directional→execution gate, so per §14/§24 M5 timing was not evaluated (M5 only earns a test when the M15 parent survives).

## 10. Candidate table (§28) — EMPTY (research lead recorded)
**Zero executable candidates frozen.** Recorded lead for the Statistician: *"Asia-High liquidity trap — sweep of Asia High during London/Overlap that returns inside the Asia range predicts P(reach Asia mid) ≈ 0.51 vs 0.19 for accepted breakouts (matched control), holding out-of-sample; bearish-displacement conditioning raises it to 0.76."* **This is a predictive-probability finding, not an executable edge** — RR geometry (structural stop above a late entry) makes it unprofitable, and confirmation is single-year 2023.

## 11. Graveyard (§26)
- S1/S2/S4/S5 executed shorts, mean-reversion (mid) and trend (low) targets — all negative on confirmation.
- S3 failed-reclaim layer — subtracts probability.
- Width/sweep-size/time-of-day slices — no positive, adequately-powered, out-of-sample bucket. Recorded in `session_trap.py` / `session_trap2.py`.

## 12. Remaining unexplored classes
Bounded to Asia-High traps with a single 2023 OOS window. Unexplored: (1) **tighter structural stops** (failed-reclaim high rather than sweep extreme) to fix RR — but requires care not to threshold-hunt; (2) **London-High → NY trap** as a primary family (only diagnostically touched here); (3) **multi-year OOS** via temporal CV (the binding limitation); (4) a **genuinely bearish population** (2011–2013). All price-only.

## 13. CEO recommendation
1. **`SESSION_LIQUIDITY_SIGNAL_FOUND_EXECUTION_UNSOLVED`.** Session conditioning surfaced a **real predictive-probability structure the generic swing-sweep family never produced**: an Asia-High sweep that *fails to sustain* (returns inside the range) predicts reversion to the Asia mid at 0.51 vs 0.19 for accepted breakouts, and bearish-displacement/structure-break conditioning raises P(reach mid) to 0.76–0.91 — **holding out-of-sample**. **But it does not monetize:** every executable layer/target is negative on confirmation because the honest structural stop (sweep high) sits far above the post-confirmation entry (RR < 1), and full stop-outs dominate.
2. **This answers the core question (§1):** session-specific Asia-High sweeps **do** carry directional information that generic swing-sweeps missed — but the information is a *conditional probability of range reversion*, not a positive-expectancy short with structural risk. **Execution, not selection, is the wall here** — the mirror image of the price-structure campaigns.
3. **Recommended next step (research, not promotion):** hand the trap→return probability structure to the **Statistician** for (a) a multi-year temporal-CV to confirm it survives outside 2023, and (b) an RR-geometry study (tighter structural invalidation) to test whether the +0.32 probability separation can be converted — under a fresh mandate, not by threshold-hunting here.
4. **§31/§26 honored:** no causal claim; no reproduction of the old generic sweep research; the finding is explicitly session+time+range-structure conditioned. **No promotion; broker disabled; DEV-only; no candidate; no CALIB.** The 9 frozen strategies are unaltered; portfolio SHORT remains only frozen `H4-bo-raw-S`.

**Terminal status:** `XAUUSD_SESSION_LIQUIDITY_TRAP_DISCOVERY_COMPLETE` · `SESSION_LIQUIDITY_SIGNAL_FOUND_EXECUTION_UNSOLVED`. **STOP.**
