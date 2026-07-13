# S21–S40 IMPLEMENTATION REPORTS (branch family-implementation-s21-s40)

Each family implemented as a NEW provider in `code/mstrat_ext.py`, executed through the FROZEN official engine
(`MS.simulate`, v2 stop-floor, same costs/overlap, same feature frame `MS.load`, same Discovery-Screen
definitions copied verbatim). `mstrat.py` is byte-identical to baseline `1bc0ffb`. Research segment = first 60%;
validation = next 20% (val_exp); holdout = last 20% SEALED. No parameter optimization: a negative family is
documented and closed. No verdicts (matched-null validated but global-FDR is CEO-gated).

Screen definitions (identical to S1–S20): HIST_PROFITABLE = n>0 & sumR>0 & exp>0 & PF>1.00. RESEARCH_WORTHY =
n≥25 & exp>0 & PF≥1.02 & maxDD≤25R & (wo1>0 or t1<0.5) & months≥2 & years≥2.

---

## S21 — Equal-highs / equal-lows liquidity-pool raid  →  **NEGATIVE, CLOSED**
- **Economic mechanism.** Breakout/stop orders pool at clusters of equal highs/lows (a level tested ≥2×);
  larger players sweep the pool to fill size, then price reverses. Loser = the clustered breakout/stop crowd.
- **Exact definition (as implemented).** For a side (high→short, low→long): reference level = prior rolling
  extreme `rmax{lb}` / `rmin{lb}` (lb∈{20,50}, lookahead-safe, shift(1)). "Pool" = ≥`min_touches`∈{2,3} of the
  last 20 bars tagged the level (extreme within 0.20·ATR). Raid+reject trigger: bar sweeps beyond the level
  (`high>lvl` / `low<lvl`) AND closes back inside (`close<lvl` / `close>lvl`). Entry = next open; stop =
  beyond the raid extreme or structural (rmax20/rmin20); exit ∈ {rr2, rr3, time}.
- **Grammar:** 2 side × 2 lb × 2 min_touches × 2 stop × 3 exit = **48 hypotheses.** Parity PASS, smoke PASS,
  lookahead-safe.
- **Results (research segment).** generated 48 · valid(n≥25) 48 · **HIST_PROFITABLE 0 · RESEARCH_WORTHY 0**.
  - Expectancy: all negative, range [−0.443, −0.092]; **best (long) −0.092**, mean long −0.162, mean short −0.378.
  - PF ≤ 0.91 (long) / ≤ 0.67 (short). maxDD of the "best" variant ≈ 262R. Win rate ≈ 21%. OOS val_exp ≈ −0.09.
- **Observations / why negative.**
  1. Signal fires far too often (n = 863–2354; ~every 21–32 bars) — the rolling-extreme-proximity proxy for a
     "pool" does not isolate rare genuine equal-highs clusters; it collapses to a broad "failed poke of the
     rolling extreme" fade.
  2. **Key mechanistic finding:** S21 is essentially **S1's sweep WITHOUT S1's confirmation stage**
     (displacement / close-beyond / consecutive-2). S1 (with confirmation) is profitable; S21 (raw sweep-reject,
     immediate entry) is strongly negative. → **the edge in the liquidity-sweep family lives in the
     change-of-behaviour CONFIRMATION, not in the raw sweep.** This is a reusable KB insight.
  3. Short side is much worse than long (−0.378 vs −0.162) — fading rolling-extreme pokes shorts into a bull
     trend. Consistent with the S1–S20 lesson that counter-trend fades without regime conditioning lose.
- **Comparison with existing families.** Overlaps S1 (liquidity sweep) and S2 (failed-breakout fade) but is
  strictly WEAKER (no confirmation, no specific level type). Adds no positive edge beyond them.
- **New economic mechanism introduced?** **No.** It is a degenerate (confirmation-stripped) subset of S1/S2.
- **Decision.** CLOSED as negative. Not optimized. A future redesign would need a genuine swing-pivot cluster
  detector AND a confirmation stage — but that would essentially reconstruct S1, so it is not pursued.

---

## S23 — Squeeze breakout + HTF directional filter  (redesign of S4)  →  **NEGATIVE, CLOSED**
- **Economic mechanism.** Volatility mean-reverts: compression precedes expansion. S4 failed because the
  expansion direction was random; the redesign takes the squeeze breakout ONLY in the HTF (h4/h1) trend
  direction. Loser = range faders / premium sellers at the regime change.
- **Exact definition.** Sustained compression = `compress`∈{last min_sq bars all set}, min_sq∈{3,6}
  (`compress` = engine's m_atr<0.8·atr_ma). Squeeze range = prior rolling high/low over min_sq. Long breakout:
  `close>sq_high` AND HTF trend up; short: `close<sq_low` AND HTF down. Entry next open; stop = opposite side
  of the squeeze range or 1.5·ATR; exit ∈ {rr2, rr3, trailing, time}. htf∈{h4,h1}.
- **Grammar:** 2 htf × 2 min_sq × 2 stop × 4 exit = **32 hypotheses.** Parity PASS, smoke PASS, lookahead-safe.
- **Results (research).** generated 32 · valid 32 · **HIST_PROFITABLE 0 · RESEARCH_WORTHY 0**.
  Expectancy all negative [−0.379, −0.091], best −0.091; mean −0.194; PF ≤ 0.88; win ≈ 28%; n = 612–1627.
- **Observations / why negative.** The HTF filter does NOT rescue the mechanism. The breakout ENTRY itself is
  the problem: on M15 XAUUSD the squeeze-breakout fakeout rate dominates, and entering on the breakout close
  chases the move (poor fill) with a squeeze-width stop that is easily run. This **partially refutes the S23
  design hypothesis** that "direction was S4's only flaw" — the entry style is also flawed.
- **Comparison with existing families.** Reinforces a ROBUST cross-family lesson: breakout/expansion CHASING
  loses on XAUUSD M15 — S3 (breakout-retest) marginal, S4/S15 negative, now S23 negative. The lab's positive
  edges are FADES-with-confirmation (S1) and specific level reactions (S5 opening-range, S17 weekly), not
  chasing expansions.
- **New economic mechanism introduced?** **No** (a filtered variant of the S4 breakout mechanism; still negative).
- **Decision.** CLOSED as negative. Not optimized.

---

## S26 — Developing value-area rejection / acceptance  →  **NEGATIVE, CLOSED**
- **Economic mechanism.** Price spends most time inside a value area; excursions beyond the VA edge are
  rejected (fade to value) or accepted (follow migration). Institutions anchor to value. Loser = breakout
  traders faded at value edges, or mean-reverters run over on acceptance.
- **Exact definition.** VA proxy = session VWAP ± k·rolling-σ (`m_std`), k∈{2,3}. **Reject:** ONSET of an
  excursion beyond the edge that closes back inside → fade toward VWAP. **Accept:** onset of a close beyond
  the edge → follow. Entry next open; stop = 1.5·ATR or beyond the excursion bar; exit ∈ {rr2, rr3, VWAP-target
  (reject only), time}.
  - *Definitional note:* k=1.0 was excluded BEFORE looking at its PnL — ±1σ ≈ the value area (~70%), so a 1σ
    "excursion" is inside value and failed the discrete-setup selectivity gate (17% of bars). Structural, not
    result-driven.
- **Grammar:** 2 mode × 2 k × 2 stop × 4 exit = **32 hypotheses.** Parity PASS, smoke PASS (k≥2), lookahead-safe.
- **Results (research).** generated 32 · valid 32 · **HIST_PROFITABLE 0 · RESEARCH_WORTHY 0**.
  Expectancy all negative [−0.392, −0.123]; best −0.123. **Reject** best −0.123 (mean −0.221, win 31%);
  **Accept** best −0.159 (mean −0.234, win 29%). PF ≤ 0.85. n = 424–3826.
- **Observations / why negative.** Both the mean-reversion (reject) and momentum (accept) legs lose. Two
  likely causes: (1) the VWAP±σ band is a WEAK proxy for a true value area (which is a 70%-of-VOLUME price
  range from a volume-at-price profile, not a σ-band) — the faithful mechanism needs a session volume profile
  not built here; (2) high signal frequency → the per-trade 2×cost drag dominates the small edge. Consistent
  with the emerging pattern: broad high-frequency signals lose to costs.
- **Comparison with existing families.** Related to S8 (extension-MR vs SMA/VWAP) and S12 (range rotation),
  both of which were also weak/negative. Adds no positive edge.
- **New economic mechanism introduced?** Conceptually yes (auction/value-area), but **not validated** — and
  not faithfully implementable without a volume-profile value area (a larger build, deferred).
- **Decision.** CLOSED as negative under the σ-band proxy. A proper volume-profile VA is a future redesign
  (documented, not pursued now to avoid result-chasing).

---

## S38 — Patient pullback-into-zone (trend continuation)  (redesign of S7/S10)  →  **NEGATIVE, CLOSED**
- **Economic mechanism.** In an established HTF trend, enter on the pullback into a discount zone WITHOUT the
  confirmation wait that made S7/S10 late; edge = better fill + trend persistence. Loser = the impatient
  market-on-confirmation crowd.
- **Exact definition.** HTF trend (h4/h1). Discount zone ∈ {EMA20, EMA50, mid-of-recent-range (fib-0.5 proxy)}.
  Long (uptrend): ONSET of `low ≤ zone`; short (downtrend): onset of `high ≥ zone`. Entry next open (market
  approximation of a limit fill — the engine has no limit orders). Stop = recent swing (rmin20/rmax20) or
  1.5·ATR; exit ∈ {rr2, rr3, trailing}.
- **Grammar:** 2 htf × 3 zone × 2 stop × 3 exit = **36 hypotheses.** Parity PASS, smoke PASS, lookahead-safe.
- **Results (research).** generated 36 · valid 36 · **HIST_PROFITABLE 0 · RESEARCH_WORTHY 0**.
  Expectancy all negative [−0.412, −0.098], best −0.098; PF ≤ 0.88; n = 998–2269.
- **Observations / why negative.** Entering earlier (no confirmation) does NOT rescue trend-continuation.
  Pullbacks to EMA/mid-range are frequent and whipsaw; the continuation edge is eaten by reversals + costs.
  **Robust cross-family conclusion:** trend-continuation via pullback is negative on XAUUSD M15 regardless of
  entry timing — S7 (confirmation) neg, S10 neg, S15 neg, S38 (early) neg. The instrument does not reward
  pullback-continuation on this timeframe.
- **Comparison with existing families.** Same continuation thesis as S7/S10/S15, different execution; still
  negative — isolates that the failure is the THESIS (M15 pullback-continuation), not the entry timing.
- **New economic mechanism introduced?** **No** (execution variant of a known-negative continuation thesis).
- **Decision.** CLOSED as negative. Not optimized. Limit-fill execution (the design's true edge) is not
  supported by the frozen engine — a genuine test would require an engine change (CEO-gated), out of scope.

---

## S39 — Trend-efficiency-gated continuation  (redesign of S15)  →  **POSITIVE (2 Research-Worthy)** ✅
- **Economic mechanism.** S15 bought raw acceleration (bought local tops → negative). Fix: take
  continuation ONLY when the trend is CLEAN — Kaufman efficiency ratio ER = |net move| / path-length over L
  bars ≥ threshold. Clean trends persist; noisy "trends" whipsaw. Loser = counter-trend faders in efficient trends.
- **Exact definition.** ER over L∈{10,20}. Signal = expansion bar (range>1.5·ATR, in M-trend direction) AND
  ER ≥ er_thr∈{0.3,0.5}, onset only. Entry next open; stop = swing (rmin20/rmax20) or 1.5·ATR; exit ∈ {rr2, rr3, trailing}.
- **Grammar:** 2 L × 2 er_thr × 2 stop × 3 exit = **24 hypotheses.** Parity PASS, smoke PASS, lookahead-safe.
- **Results (research).** generated 24 · valid 24 · **HIST_PROFITABLE 2 · RESEARCH_WORTHY 2**.
  Expectancy range [−0.324, +0.031]; best +0.031. The 2 RW (both L=20, er_thr=0.5, swing stop):
  - `13752e544049` (rr2): n=320, exp=0.029, PF=1.08, maxDD=11.6R, win=0.47, 14/27 pos months, 4 years,
    **t1=0.02 (NOT outlier-driven)**, **OOS val_exp=+0.018**.
  - `1ed10ae976dd` (rr3): n=314, exp=0.031, PF=1.09, maxDD=11.5R, 11/27 pos months, OOS −0.006.
- **Observations.** Only the **high-efficiency** variants (er_thr=0.5) are positive; er_thr=0.3 stays negative.
  → **the trend-efficiency gate IS a meaningful filter**: it converts a robustly-negative continuation thesis
  (S15/S38) into a modest positive edge by trading only clean trends. Edge is small (exp≈0.03, PF≈1.08) and
  narrow (2/24 variants), so mechanism-robust but tuning-sensitive — must go through matched-null + global-FDR.
- **Comparison with existing families.** Directly fixes S15 (raw acceleration, negative). The efficiency filter
  is an axis absent from S1–S20. Magnitude is in the S1/S9 range (small-edge momentum).
- **New economic mechanism introduced?** **YES (qualified)** — trend-QUALITY (efficiency-ratio) gating as a
  continuation filter. First evidence that trend-quality conditioning matters on XAUUSD M15.
- **Decision.** KEEP as a Research-Candidate family (2 RW). Not optimized (grammar fixed; the er_thr=0.5
  selection is the mechanism working, not a post-hoc tune). Send representative to matched-null/global-FDR later.

---

## S40 — Regime router (trend-continuation / range-reversion)  →  **NEGATIVE, CLOSED**
- **Economic mechanism.** Deploy each sub-edge only where its mechanism holds: TREND regime (efficiency
  ER≥thr) → efficient continuation; RANGE regime (ER<thr) → fade rolling extremes back to the range middle.
  Addresses the S11/S12 regime-blind failures.
- **Exact definition.** ER(20) regime split at er_thr∈{0.3,0.5}. Trend: expansion bar in m-trend direction →
  continuation. Range: excursion beyond rmax/rmin{lb∈{20,50}} that closes back → fade to range mid. Entry next
  open; stop = swing or 1.5·ATR; exit = rr (trend) or range-mid target (range).
- **Grammar:** 2 er_thr × 2 range_lb × 2 stop × 2 exit = **16 hypotheses.** Parity PASS, smoke PASS, lookahead-safe.
- **Results (research).** generated 16 · valid 16 · **HIST_PROFITABLE 0 · RESEARCH_WORTHY 0**.
  Expectancy all negative [−0.311, −0.118], best −0.118; PF ≤ 0.83; **n = 1521–3453 (very high).**
- **Observations / why negative.** The router is ALWAYS active (it emits a setup in every regime), so it just
  doubles the trade count and cost drag. The range-fade sub-edge (S12-style) is negative and the regime
  condition doesn't rescue it; the continuation sub-edge is less tightly efficiency-gated than S39's winner.
  **Finding:** a naive always-on router adds no value — a useful router must STAND ASIDE most of the time and
  fire only high-conviction sub-setups. This one is too active.
- **Comparison with existing families.** Combines S39-style continuation with S12-style range fade; inherits
  S12's negativity and adds cost drag. No incremental edge.
- **New economic mechanism introduced?** **No** (a combination layer; the combination is net-negative here).
- **Decision.** CLOSED as negative. Not optimized. A selective, mostly-stand-aside router is a future redesign.

---

# TIER-A COMPLETION SUMMARY (S21, S23, S26, S38, S39, S40)

| family | mechanism | hyps | valid | profitable | RW | bestExp | verdict |
|---|---|---|---|---|---|---|---|
| S21 | equal-highs/lows liquidity-pool raid | 48 | 48 | 0 | 0 | −0.092 | NEGATIVE, closed |
| S23 | squeeze breakout + HTF filter | 32 | 32 | 0 | 0 | −0.091 | NEGATIVE, closed |
| S26 | value-area rejection/acceptance | 32 | 32 | 0 | 0 | −0.123 | NEGATIVE, closed |
| S38 | patient pullback continuation | 36 | 36 | 0 | 0 | −0.098 | NEGATIVE, closed |
| **S39** | **trend-efficiency-gated continuation** | 24 | 24 | **2** | **2** | **+0.031** | **POSITIVE — keep** |
| S40 | regime router | 16 | 16 | 0 | 0 | −0.118 | NEGATIVE, closed |
| **Σ** | | **188** | **188** | **2** | **2** | | 1/6 families positive |

## Cross-family knowledge produced (the real deliverable)
1. **The edge in liquidity-sweep reversal is the CONFIRMATION stage, not the sweep** (S21 = S1 without
   confirmation → negative).
2. **Chasing breakouts/expansions loses on XAUUSD M15 even with an HTF filter** (S23; consistent with S3/S4/S15).
3. **Trend-continuation via pullback loses regardless of entry timing** (S38 early vs S7/S10 late — both negative).
4. **Trend-QUALITY (efficiency-ratio) gating is a genuine, new positive filter** (S39): it turns a negative
   continuation thesis into a modest edge by trading only clean trends. Only high-efficiency (ER≥0.5) works.
5. **A naive always-on regime router adds no value** — it doubles cost drag; a router must mostly stand aside (S40).
6. **Recurring theme:** broad high-frequency signals lose to the per-trade 2×cost drag; the surviving edges
   (S1-confirmed, S5, S17, and now S39) are selective and context-specific.

## Registry & artifacts
- `results/ext_families/EXT_FAMILY_RESULTS.parquet` (all 188 hyps, same schema as FAMILY_RESULTS.parquet).
- Per-family parquets `results/ext_families/S{21,23,26,38,39,40}_results.parquet`.
- Code: `code/mstrat_ext.py` (new families, engine untouched), `code/run_ext_family.py` (runner replicating the
  official metrics/screen). `mstrat.py` byte-identical to baseline 1bc0ffb.

## Recommendation for the next step (CEO decision)
- **S39** is the only Tier-A survivor (2 RW, +OOS on the best). It joins the eligible candidate set for the
  eventual matched-null → global-FDR pass (do NOT validate yet — universe incomplete per CEO).
- **Tier B (S22, S24, S25, S27, S28, S29, S30, S31)** are T0 (existing data) and can be implemented next on the
  same pattern. Expectation, given the evidence: mostly negative except possibly the level-reaction / calendar
  ones; each still adds mechanism knowledge.
- **Tier C/D (S32–S37)** need NEW DATA (DXY, real yields, SPX/VIX, econ-calendar, COT, options) — **blocked on a
  CEO data-acquisition gate.** These are the highest economic-value, drift-breaking families for gold.
- Suggested: authorize Tier B implementation to complete the T0 universe, and decide on Tier-C data acquisition.
