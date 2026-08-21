# ALPHA_XAUUSD_H1_INTRARANGE_M5_DIRECTIONAL_REPORT

**Mandate:** `ALPHA-XAUUSD-H1-RANGE-INTRARANGE-M5-001` · **Date:** 2026-08-21 · **Stat evidence:** commit `b8d0447`.
**Terminal status:** `XAUUSD_H1_INTRARANGE_M5_DISCOVERY_COMPLETE` · **`INTRARANGE_DIRECTIONAL_ALPHA_CANDIDATES_READY_FOR_CEO_REVIEW`** — 1 robust, CALIB-generalizing, independent candidate (`IR-DIR-L-mid`), classified `ROBUST_ALPHA_BUT_PROFILE_MISMATCH`.
**Firewall (re-verified):** gated M5 loader only, no `read_csv` on `data/market/`, `N4_M5_TRIGGER_USAGE_COUNT = 0`, `ALPHA_ACCESS_2025_PLUS = 0`, no shadow_driver. 12 IDs (≤40). No promotion; broker disabled; existing candidates unaltered.

---

## 0. Headline — answers to the 7 key questions (§28)
1. **Are there tradeable M5 directional legs inside H1 ranges?** → **YES — a robust, generalizing intra-range DIRECTIONAL edge exists** (LONG from the lower zone toward the midpoint, when a directional leg is confirmed). It is genuinely distinct from the failed boundary mean-reversion branch — and it **generalizes to CALIBRATION** where mean-reversion did not.
2. **Which parts of the range produce them?** → The **lower zone (0–25%, strongest 0–10%), LONG only.** SHORT (upper zone) fails entirely.
3. **Does M5 provide real entry value?** → **NO.** The coarse **H1-directional** entry is *tail-superior* and beats the M5 leg on matched signals (timing Δ avgR negative). The M5 leg mechanisms capture a similar edge but with worse tail robustness and no timing advantage.
4. **Does M15 add anything between H1 and M5?** → **Moot / not adopted** — since M5 entry did not beat coarse H1, an M15-between layer has no case; not pursued for the winning candidate.
5. **Can these trades support 70–80+ pip targets?** → **YES** (median room 92 pips; ≥70p for 100%, ≥80p for 78% of setups).
6. **Profile A or B?** → **Neither cleanly** — WR 43–53% at RR ≈2.5 → `ROBUST_ALPHA_BUT_PROFILE_MISMATCH` (moderate WR / moderate-high RR).
7. **Independent from trend Alpha?** → **YES, fully** — regime-disjoint from `HR-TU-pb-L` (same-day overlap 0, Jaccard 0.000); fires in RANGE regime, i.e. **exactly when the trend strategy is inactive.**

## 1. Range-container construction
H1 = **container** (context + room), not signal. Causal H1 range over 24 H1 bars: `range_high/low` (shifted rolling), `mid`, `width`; in-range ⇔ |efficiency| < 0.35 & width ∈ [40,600] pips & ≥2 touches per boundary. DEV container bars = 4,352; CALIB = 1,204. Median range width **268 pips** (ample room). The directional edge comes from **internal structure + directional confirmation**, not the boundary.

## 2–3. LONG results / lower-zone results — the winning candidate `IR-DIR-L-mid`
**Thesis:** price in the H1 lower/mid zone (loc ≤ 0.60) **and a directional leg is confirmed (H1 bar closes up)** → LONG toward the H1 **midpoint**. Stop = H1 3-bar structural swing low − 0.10·ATR (H1 owns the stop). Entry = coarse (next M5 open after the H1 directional bar).
| metric | DEV | CALIB (out-of-DEV) |
|---|---|---|
| N | 46 | 19 |
| win rate | 0.435 | **0.526** |
| avg realized R (STRESS) | **+0.523** | **+0.612** |
| profit factor | 1.86 | — |
| best-1% / 5% / **10%-removed** | +0.401 / +0.302 / **+0.121** | — / +0.256 / — |
| max drawdown | 5.58R | — |
| median SL | **37 pips** (H1 swing) | — |
| median room / target | **92 pips** (mid) | — |
| effective RR (median) | 2.52 | — |
| % room ≥70 / ≥80 / ≥100 / ≥150 | 1.00 / 0.78 / 0.35 / 0.04 | — |
| median MAE / MFE | 30 / 70 pips | — |
| median range width | 268 pips | — |
**`IR-DIR-L-mid` is tail-robust (best-10%-removed POSITIVE +0.121) and GENERALIZES to CALIBRATION (+0.612, best-5%-removed +0.256)** — the decisive gate the entire mean-reversion branch failed.

## 4–5. Directional confirmation is essential (NOT disguised mean-reversion) — §3/§6/§21
| variant | n | avg R | best-5%-rem |
|---|---|---|---|
| lower/mid-zone longs to mid **with H1-up-bar filter** | 46 | **+0.523** | +0.302 |
| lower/mid-zone longs to mid **without directional filter** (all) | 79 | **−0.075** | −0.509 |
Removing the directional filter **destroys the edge**. Buying the lower zone indiscriminately loses money; buying it **when a directional leg is underway** is the edge. This proves the candidate is **not** a disguised "LOW = BUY" boundary mean-reversion (§21) — it requires genuine directional confirmation (§3, §6).

## 6. Midpoint continuation + 13. midpoint as structural state
The H1 **midpoint functions as a reachable target** for lower-zone directional longs (room ≥70p; 78% ≥80p). The edge is *reaching* the midpoint from below with directional momentum — consistent with the midpoint as a magnet/continuation objective, not a mean-reversion pivot. (Upper-zone → midpoint SHORT continuation failed — §5.)

## 7. M5 internal-trend results (the M5 leg mechanisms)
Three causal M5 directional mechanisms tested as the entry layer: **BOS** (break-of-structure after higher-low), **compression→expansion**, **failed-counter-move**. Fast-falsification (M5 arm, DEV):
| mechanism | side | tp | n | WR | avg R | best-5%-rem | verdict |
|---|---|---|---|---|---|---|---|
| failed-counter | LONG | mid | 74 | 0.419 | +0.553 | +0.114 | SURVIVE (CALIB +0.655) |
| BOS | LONG | mid | 76 | 0.395 | +0.334 | −0.031 | TAIL_FRAGILE |
| comp→exp | LONG | mid | 62 | 0.403 | +0.078 | −0.334 | TAIL_FRAGILE |
| (all SHORT, all 'opp'-target) | — | — | — | — | ≤0 or tail-neg | — | FAIL / TAIL_FRAGILE |
Only `failcounter-L-mid` survives on the M5 arm and it **also generalizes** (CALIB +0.655) — **but it is tail-fragile (best-10%-removed −0.266)** vs the coarse arm's +0.121, and does not beat coarse on matched timing (below). So the M5 mechanisms add *trade frequency* at the cost of *tail robustness*.

## 8. M5 sub-range breakout
Covered by the compression→expansion mechanism (M5 micro-range contraction then directional expansion). It is tail-fragile (best-5%-removed −0.334) and does not produce a robust standalone edge on this population.

## 9. M15→M5 results (§11)
**Not adopted.** Because the M5 entry layer did **not** improve on the coarse H1-directional entry (§10 control), inserting an M15 internal-structure layer between H1 and M5 has no economic case for the winning candidate. Documented as a negative-by-implication (a lower-TF entry layer only helps if it beats coarse; here it does not).

## 10. Coarse-vs-M5 control (§12) — M5 does NOT earn its value here
Matched control (same thesis, same H1 SL, same target; only entry timing differs), pure-timing Δ avgR (M5 minus coarse on shared signals):
| mechanism (LONG, mid) | timing Δ avgR |
|---|---|
| BOS | −0.435 |
| compression→expansion | −0.365 |
| failed-counter | −0.217 |
**M5-timed entry is worse than coarse on every LONG-mid mechanism** — the M5 leg confirms later and higher, leaving less room to the fixed midpoint target. **Which timeframe owns the stop:** H1 (3-bar structural swing). **Conclusion:** for the intra-range directional long, the value is the **H1 directional thesis + immediate (coarse) entry**; M5 entry timing does not add robust value (and is tail-inferior). This refines the architecture: M5's demonstrated entry value remains specific to **trend-continuation** (`HR-TU-pb-L`), not intra-range directional legs.

## 11. Location analysis (§7) — where the edge lives
DEV avgR by entry zone (diagnostic, coarse arm):
| zone (loc) | avg R | n |
|---|---|---|
| 0–10% | **+0.994** | 15 |
| 10–25% | +0.215 | 29 |
| 25–50% | +1.461 | 2 |
Profit concentrates in the **lower zone (0–25%, strongest 0–10%)**. The zone was used diagnostically, not selected post-hoc; the candidate's thesis (loc ≤ 0.60 + directional filter) is the pre-registered form.

## 12. Range-room economics (§8, §23)
Median range width 268 pips; median room-to-target 92 pips; **100% of setups have ≥70p room, 78% ≥80p, 35% ≥100p.** Room is amply available — the container's economic space supports the requested moves. No trades were generated with insufficient room (< 70p filter enforced).

## 13. SL/TP geometry
Stop = **H1** structural swing (median 37 pips). Target = H1 midpoint (median 92 pips). RR ≈2.5. Not an M5-micro stop (§10 honored). Both stop and target are parent-timeframe structural levels.

## 14. Profile A/B (§16)
`IR-DIR-L-mid`: WR 0.435 (DEV) / 0.526 (CALIB) at RR ≈2.5 → **neither clean Profile A (70–80% WR) nor Profile B (1:3–4)**. CALIB WR 52.6% sits in Profile B's WR band but the RR (2.5) is below 3. Classification: **`ROBUST_ALPHA_BUT_PROFILE_MISMATCH`** — a healthy ~50%-WR / ~1:2.5 directional edge.

## 15. BASE/STRESS
All figures above are **STRESS** (round-trip 0.24). The edge is positive after full STRESS cost on both DEV (+0.523) and CALIB (+0.612); BASE (0.05) is marginally higher. Min tick 0.01 enforced.

## 16. Tail robustness (§24)
`IR-DIR-L-mid` (coarse): best-1%-removed +0.401, best-5%-removed +0.302, **best-10%-removed +0.121** — the edge survives removing the top 10% of trades → **not a few ranges escaping into trends.** (The M5 `failcounter` arm is weaker here: best-10%-removed −0.266.)

## 17. Temporal robustness (§25)
DEV by year: 2021 **+1.13** (n=8), 2022 **−0.01** (n=9), 2023 **+0.52** (n=29). Positive in 2021 and 2023 (the bulk of the sample), flat in 2022. Not dependent on a single year; no periods deleted. (Caveat: modest sample.)

## 18. Calibration (§26)
Frozen DEV thesis, no retuning: **CALIB avgR +0.612, WR 52.6%, best-5%-removed +0.256 (n=19).** The frozen intra-range directional edge **generalizes out-of-DEV** — the single most important result of this mandate, and the clean contrast with the mean-reversion branch (which was CALIB-negative everywhere).

## 19. Independence analysis (§27)
`IR-DIR-L-mid` vs `HR-TU-pb-L`: **same-day overlap 0, Jaccard 0.000.** Regime-disjoint by construction (intra-range fires in RANGE regime; HR-TU-pb-L in TREND_UP). **The intra-range candidate delivers signals precisely when the trend strategy is inactive** — a complementary, independent Alpha source. vs `H4-bo-raw-S`/`S5`: directionally distinct (LONG range-directional vs SHORT/LONG trend) → independent. (Existing candidates unaltered per §19.)

## 20. Graveyard
All SHORT mechanisms (BOS/comp-exp/failcounter × upper zone, mid+opp) — FAIL. All 'opp' (opposite-boundary) targets — tail-fragile (catch occasional big moves, not robust). M5 BOS-L and comp-exp-L — tail-fragile. The no-directional-filter lower-zone long (−0.075) — the disguised-mean-reversion control. Recorded in `intra_records.json`. **Distinct from `RANGE_MEAN_REVERSION_OLD` (prior branch); these are `INTRARANGE_DIRECTIONAL_NEW` IDs (`IR-…`).**

## 21. Final candidate portfolio + 22. recommendation to CEO
1. **Forward `IR-DIR-L-mid` to Statistician/Red Team** as a robust, CALIB-generalizing, **independent** intra-range directional LONG: lower-zone (0–25%) + H1-directional confirmation → H1 midpoint, **coarse H1 entry, H1 structural stop**. STRESS +0.523 DEV / **+0.612 CALIB**, tail-robust (best-10%-removed +0.121), regime-disjoint from the trend leader. **Caveats:** modest sample (46 DEV / 19 CALIB); 2022 flat; `ROBUST_ALPHA_BUT_PROFILE_MISMATCH` (WR ~50% @ RR ~2.5, not a clean profile). It is the **program's first robust RANGE-regime Alpha** and complements `HR-TU-pb-L` (trend) — together they cover trending and ranging regimes.
2. **Answers to §28 (headline §0):** intra-range directional longs ARE tradeable and generalize; they live in the lower zone; **M5 entry timing does NOT add value** (coarse H1-directional entry is tail-superior); M15 not warranted; 70–80+ pip targets supported; profile-mismatch; fully independent of trend Alpha.
3. **Architectural refinement for the CEO:** the intra-range directional edge is real but its source is the **H1 directional thesis + immediate entry**, not the M5 leg. M5's proven entry value stays confined to trend-continuation. The prior mean-reversion negative stands; this directional branch is the productive one inside ranges.
4. **No promotion; broker disabled; highest status = research candidate.** `S5`/`HR-TU-pb-L`/`H4-bo-raw-S`/`S20` unaltered.

**Terminal status:** `XAUUSD_H1_INTRARANGE_M5_DISCOVERY_COMPLETE` · `INTRARANGE_DIRECTIONAL_ALPHA_CANDIDATES_READY_FOR_CEO_REVIEW` (1: `IR-DIR-L-mid`). **STOP.**
