# ALPHA_XAUUSD_POSTSWEEP_PULLBACK_SHORT_REPORT

**Mandate:** `ALPHA-XAUUSD-POSTSWEEP-PULLBACK-SHORT-001` · **Date:** 2026-08-22 · **Stat evidence:** commit `b8d0447`.
**Terminal status:** `XAUUSD_POSTSWEEP_PULLBACK_SHORT_DISCOVERY_COMPLETE` · **`NO_ROBUST_POSTSWEEP_PULLBACK_SHORT_ALPHA_FOUND`**.
**Firewall:** gated M5 → causal H1/H4; no `read_csv`; N4=0; 2025+=0; **CALIB not opened**. 10 IDs (≤24). DEV-only. No promotion; broker disabled; existing candidates frozen.

---

## 0. Headline — answers to §24
1. **Does waiting for the post-break rally solve the stop problem? NO — it makes it worse.** The pullback high is a *tighter* stop than the sweep high, so the continued bullish recovery hits it more easily. Pullback entry avgR −0.057 vs immediate +0.025.
2. **Failed reclaim of broken structure tradeable? NO** (P2 sparse, n=11 — insufficient events).
3. **Lower-high entry tradeable? NO** (P3 avgR −0.250).
4. **H1 or M15 best pullback entry? Neither** — H1 fails uniformly; M15 not warranted.
5. **Capture the bearish moves the old stop missed? NO** — pullback entries have median R ≈ −1.0 (stopped out), capturing *fewer*, not more.
6. **Does 2022 become profitable? NO** — pullback entry 2022 avgR −0.435 (P1). The selloff year stays negative.
7. **Positive median R? NO** — ≈ −1.0 for every pullback mechanism.
8. **Pass tail gates? NO** — best-5%-removed negative; top-10% net-profit share 999% for all.
9. **Beat immediate entry? NO** — worse by −0.08 to −0.34.
10. **Did sweep+structure-break finally become executable SHORT Alpha? NO.**

## 1. Frozen parent predictor (§3, §4) — unchanged
From the prior mandate, **frozen**: H4 liquidity sweep (first breach of a prior confirmed swing high) + bearish displacement (body > 1.0·ATR within i…i+4) + bearish structure break (close below the pre-sweep swing low). No definitions or thresholds tuned.

## 2. Parent opportunities (§3) — the sample constraint
**Frozen parent events: n=21** (2021–2023). Regime distribution: **OTHER 13, TREND_UP 5, TREND_DOWN 3** — confirming §17 (mostly outside strict TREND_DOWN). **This is the binding limitation:** the prior 82% P(bearish) was measured on the *broader* structure-break set; requiring the full conjunction (sweep AND displacement AND structure break) yields only **21 tradeable parents** — a rare event, statistically thin.

## 3. Conversion diagnostic (§14) — cost of waiting
Of the 21 parents, causal post-break entry fires: **P1 first-pullback-turn 21 (100%), P3 lower-high 19 (90%), P2 failed-reclaim 11 (52%), P5 pullback-displacement 11 (52%).** So the pullback entry is *available* on most parents — availability is not the problem; *profitability* is.

## 4. Post-break pullback anatomy — the hypothesis, falsified
The CEO hypothesis: the bullish recovery that stopped the immediate short provides the correct short entry, with the stop around the **pullback high** (not the sweep high). Result (STRESS, H1 entry, RR 2.0):
| entry policy | n | WR | avg R | median R | best-5%-rem | top-10% share | vs immediate |
|---|---|---|---|---|---|---|---|
| **A — immediate** (old geometry, stop above sweep high) | 21 | 0.143 | **+0.025** | −0.701 | −0.074 | 770.7% | — |
| B — P1 first-pullback-turn | 21 | 0.238 | **−0.057** | −1.039 | −0.159 | 999% | **−0.082** |
| B — P3 lower-high | 19 | 0.211 | **−0.250** | −1.028 | −0.375 | 999% | −0.275 |
| B — P2 failed-reclaim | 11 | — | — | — | — | — | SPARSE |
| B — P5 pullback-displacement | 11 | — | — | — | — | — | SPARSE |
**The pullback entry is WORSE than immediate on every mechanism.** Mechanism: the "pullback" after the structure break is frequently a **genuine resumption of the uptrend** (this is a long-biased market), not a failing recovery — so it rallies *past* the pullback high, hitting the (tighter) pullback stop. Median R ≈ −1.0 confirms systematic stop-outs. Higher RR (3.0) is worse still (B-P1 −0.356, B-P3 −0.353).

## 5. Failed reclaim / lower high / retest (§ per-mechanism)
- **Failed reclaim (P2):** only 11 of 21 parents produce a causal failed-reclaim of the broken structure (§10 — distinct from the old failed-*acceptance*), below the 12-event minimum → SPARSE/inconclusive, but the available sample is negative-leaning like the rest.
- **Lower high (P3):** n=19, avgR −0.250 — the *worst* pullback mechanism (waiting for a confirmed lower high delays entry into a deeper recovery, then still stops out).
- **First-pullback-turn (P1):** n=21, −0.057 — least-bad but still negative and below immediate entry.

## 6. Stop geometry (§7, §11) — pullback stop is tighter, not safer
Median pullback-entry SL (H1, around the pullback high) is materially *tighter* than the H4 sweep-high stop. In a market where the post-break recovery routinely extends, a tighter stop is hit *more* often — the opposite of the intended effect. **The structure hierarchy (sweep high → break level → pullback high) does not contain a stop location that survives the bull drift.** No stop timeframe (H1 pullback high tested) yields a robust short.

## 7. Bearish-move capture (§15)
The immediate-entry A on the 21 parents is a **tail-lottery** (avgR +0.025 but median −0.701, top-10% share 770% — one large decline carries the positive mean). The pullback entries capture *fewer* of the eventual bearish moves (median −1.0 = stopped before the move), so waiting **misses winners** rather than avoiding losers. The 82%-P(bearish) predictive signal does not translate: the bearish departure (≥100p within 12 bars) materializes, but the *path* to it (recovery above both the sweep high and the pullback high) stops out any short first.

## 8. Incremental value (§16)
No pullback policy is positive, so incremental-over-baseline is moot (all below the sweep-only, sweep+displacement, and sweep+structure-break immediate references, and below PROJECT TREND_DOWN in absolute terms).

## 9. Tail + path robustness (§18, §19)
best-5%-removed and best-10%-removed are **negative for all executable pullback mechanisms**; top-10% net-profit share 999% (net ≤ 0). **Path robustness not reached** — no raw survivor (raw-first discipline correctly stops before serialization).

## 10. Temporal (§20) — 2022 explicitly investigated
| policy | 2021 | **2022 (selloff)** | 2023 |
|---|---|---|---|
| B-P1 (rr2) | +0.40 (n2) | **−0.435** (n5) | +0.012 (n14) |
| B-P3 (rr2) | −1.055 (n1) | −0.275 (n4) | −0.186 (n14) |
**2022 does NOT become profitable with pullback entry** (§24.6 answered: no). Even in the year of gold's largest bearish move, the post-break pullback shorts lose — the Mar–Sep 2022 down-legs were punctuated by sharp recoveries that stop out both immediate and pullback shorts.

## 11. Economic geometry (§12, §21)
Geometry is adequate (pullback-entry median TP 105–224p across RR; ≥80p targets available). The failure is edge, not target size. Effective RR = nominal (rr-exit).

## 12. Graveyard (§25)
All 10 IDs — P1/P2/P3/P5 × RR{2,3} (+ immediate-entry A references) — NO_EDGE (median −1.0, negative, tail-fragile; P2/P5 SPARSE). New `PSP-` IDs; frozen parent and existing candidates untouched.

## 13. Candidate recommendation
1. **No post-sweep pullback SHORT candidate — `NO_ROBUST_POSTSWEEP_PULLBACK_SHORT_ALPHA_FOUND`.** The specific hypothesis (waiting for the post-break pullback to fail converts the predictor into Alpha) is **falsified**: pullback entry is worse than immediate entry, median R ≈ −1.0, tail-fragile, and negative in 2022.
2. **Root cause (honest):** (a) the full tradeable conjunction is **rare (n=21)** — statistically thin; (b) in a **long-biased market** the post-break "pullback" is frequently a real uptrend resumption, so the pullback high is a *tighter* stop that gets hit *more*; (c) the 82%-P(bearish) predictive signal is about *eventual* direction over 12 bars, not the *path* — and the path (recovery first) stops out every tested short.
3. **This closes the liquidity-sweep SHORT line.** Across the immediate-entry campaign and this pullback-entry follow-up, the sweep+displacement+structure-break predictor is **genuinely predictive but not executable** as a short on the 2021–2024 population. Combined with the generic and transition SHORT negatives, the conclusion is firm: **no robust SHORT exists on this long-biased population by any tested mechanism or entry geometry.** A tradeable gold short would require a genuinely bearish population (e.g., 2011–2013, where `H4-bo-raw-S` lives).
4. **No promotion; broker disabled; CALIB not opened; DEV-only.** Frozen parent and existing candidates unaltered; portfolio SHORT exposure remains only the frozen `H4-bo-raw-S`.

**Terminal status:** `XAUUSD_POSTSWEEP_PULLBACK_SHORT_DISCOVERY_COMPLETE` · `NO_ROBUST_POSTSWEEP_PULLBACK_SHORT_ALPHA_FOUND`. **STOP.**
