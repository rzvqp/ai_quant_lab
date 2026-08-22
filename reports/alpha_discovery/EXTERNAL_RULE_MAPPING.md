# EXTERNAL_RULE_MAPPING — S2 (range breakout) & S4 (sweep reversal)

**Mandate:** `ALPHA-XAUUSD-EXTERNAL-S2-S4-INDEPENDENT-TEST-001`. **FROZEN BEFORE RESULTS.** Every ambiguous external clause is resolved with the *simplest faithful* interpretation and frozen here prior to any outcome inspection (§2). External win-rates (S2 ~52%, S4 ~67%, "9/9") are **NOT evidence/priors/targets** and are not reproduced (§21, §36). No outcome-driven reinterpretation. Data = gated M5 -> M15/H1/H4/D1 causal, DEV 2021-07-27..2023-12-29 selection, CALIB 2024-01..2024-06 robustness-only; price-only; no news/M1/exogenous; no non-causal D1/H4 merge (all HTF context via last-completed-bar `close_time <= signal.time`).

## Global frozen conventions
- **Entry execution:** external "enter at close" is not causally fillable; canonical next-executable = **next signal-TF bar OPEN** (disclosed §16). No same-bar hindsight fill.
- **Cost:** GROSS 0.00 / BASE 0.05 / **STRESS 0.24** USD round-trip; TICK 0.01. R = net USD / risk_usd. Project pip = 0.10 USD.
- **Intrabar:** stop wins same-bar ties (conservative, lower-bound WR).
- **Volume:** only the aggregated gated-M5 volume exists (tick/aggregated, NOT exchange contract volume). Tested as an *incremental* condition and disclosed as such. **M1 confirmation = `M1_CONFIRMATION_NOT_TESTABLE`** (finest authorized data is M5).
- **News:** `NEWS_FILTER_NOT_INCLUDED_IN_PRIMARY_PRICE_ONLY_TEST` (§23). No volatility proxy for news.
- **Account risk % (5%/2.5%):** execution governance, NOT Alpha; research in R only (§24).

---

## S2 — RANGE BREAKOUT (frozen deterministic rules)
- **Parent TFs:** H1, H4 (the "larger-TF box quality" arms; M5/M15 boxes are graveyard — RANGE_M15_M5 net-negative — so excluded to avoid re-running dead frontiers, disclosed).
- **Box window:** `W = 5` bars (external "4-6 overlapping candles").
- **Consolidation gate (genuine box):** box_range `< atr_ma` (box tighter than the recent ATR norm) — the "overlapping candles" requirement made mechanical.
- **Box definitions (3 materially-distinct, close-based per §4, all causal = prior W bars, shifted):**
  1. `body_env` — [min(min(open,close)), max(max(open,close))] (body envelope, wicks ignored).
  2. `close_ext` — [min(close), max(close)] (close extremes).
  3. `close_iqr` — [pctile25(close), pctile75(close)] (robust dense-close band).
- **Breakout trigger:** a candle **CLOSES** beyond the box (up: close>box_high; down: close<box_low). Never intrabar (§5).
- **LTF-confirm mapping (variant, causal):** H4 box -> first M15 close beyond; H1 box -> first M5 close beyond. Primary = same-TF close.
- **No-chase filter (§7, predeclared external threshold):** breakout close within **$4.0** of the broken box edge.
- **Entry arms (tested SEPARATELY, no post-hoc pick §7):** **S2-A** = breakout bar, enter next-open. **S2-B** = first causal **retest** of the broken edge (a later bar wick-touches the edge and closes back on the breakout side), enter next-open.
- **Stop (§9, natural):** opposite box side (up: SL=box_low; down: SL=box_high). risk=|entry-SL|. Must survive a full retest by construction.
- **Target (§10, frozen arithmetic):** TP1 = **1.0R** (covers risk; literal "SL/0.9"=1.11R noted, not separately optimized). Runner economics reported via RR{1.5, 2.0} and MFE distribution — NOT chosen retrospectively.
- **Free-path (§8, price-only causal):** obstacle = nearest **prior opposing swing extreme** (rolling 50-bar high above entry / low below entry, causal); require **>=100 project pips** clear. Tested INCREMENTALLY (parent with & without). `HVN_NOT_RECONSTRUCTED` (no causal HVN from authorized data -> excluded per §8).
- **Volume (§6, incremental):** breakout-bar volume `>= 1.3 x mean(volume,20)`. Reported as increment; disclosed as aggregated-M5 volume.

## S4 — SWEEP REVERSAL (frozen deterministic rules)
- **Reclaim TF:** M5. **Level TFs:** D1/H1/H4 (all levels must pre-exist the sweep, §13).
- **Structural level (3 faithful variants, each `>=1 day` old = >=288 M5 bars before the sweep):**
  1. `PDH_PDL` — prior completed D1 high / low (causal via close_time).
  2. `H1_pivot` — H1 local pivot high/low (max/min over +/-3 H1 bars) at least 24h old.
  3. `H4_swing` — H4 swing extreme (rolling 10-bar high/low) at least 24h old.
- **Sweep + reclaim (§14):** price trades beyond the level (LONG: M5 low < support; SHORT: M5 high > resistance), THEN an **M5 candle CLOSES back inside** (LONG: close > level; SHORT: close < level). That reclaim close = signal. Wick-only w/o reclaim = NO SIGNAL.
- **Reclaim quality (§15, incremental):** LONG close in **upper third** of the reclaim candle ((close-low)/range >= 0.66); SHORT lower third. Tested as base vs +quality.
- **Entry:** reclaim candle, enter **next M5 open** (canonical, disclosed). **Execution degradation: +1 bar delay** (enter M5 open one bar later) reported (§16 — S4 claims delay-sensitivity).
- **Stop (§17, frozen buffer):** beyond the sweep extreme +/- **$0.50** (LONG: SL = min sweep low - 0.50; SHORT: SL = max sweep high + 0.50). risk=|entry-SL|. Buffer NOT optimized.
- **Target (§18):** simplified full-position RR{1.0, 1.5, 2.0} (A); faithful partial/BE overlay (B) reported separately, must not rescue a negative parent (§26).
- **Early-invalidation (§25, predeclared):** BASE = hard SL only; INVALIDATION = also exit if a later M5 **closes back beyond the sweep extreme** (thesis negated).
- **Anti-fade pressure exclusion (§19, predeclared):** exclude sweeps where the `P=12` M5 bars before the sweep show monotone approach into the level (LONG: falling-lows compression into support; SHORT: rising-highs into resistance) — i.e., structural pressing, not exhaustion. Compare raw vs excluded.
- **S4-TREND-ALIGNED subfamily (§20, predeclared "golden pattern", causal HTF only):** sweep AGAINST the prevailing D1 direction then reclaim WITH it. LONG = sweep below support while D1 EMA20>EMA50 (uptrend) -> reclaim -> long. SHORT = sweep above resistance while D1 EMA20<EMA50 -> reclaim -> short. `NO_NON_CAUSAL_D1_H4_MERGE` — D1 context via last-completed-D1 close_time only.

## Predeclared falsification gates (§32, §36 — no rescue)
A parent/candidate is **NOT_SUPPORTED** unless, at STRESS: avgR>0 AND best-5%-removed>0 AND best-10%-removed>0 AND DISC>0 AND CONF>0 AND all-years>0 AND N>=30 AND not top-trade-concentrated. Path-first kill: if median MAE >> median MFE or adverse-first is pervasive, kill at the screen (no eventization can recover a wrong-way path). Definitions are FROZEN above; if S2/S4 fail, they are graveyarded — definitions are NOT altered to reach profitability (§36).
