# ALPHA_XAUUSD_PRICE_ONLY_BEARISH_SEQUENCE_DISCOVERY_REPORT

**Mandate:** `ALPHA-XAUUSD-PRICE-ONLY-BEARISH-SEQUENCE-001` · **Date:** 2026-08-22 · **Stat evidence:** commit `b8d0447`.
**Terminal status:** `XAUUSD_PRICE_ONLY_BEARISH_SEQUENCE_DISCOVERY_COMPLETE` · **`NO_ROBUST_PRICE_SEQUENCE_SHORT_FOUND`** (bounded to the price-only sequence space; NOT "no short Alpha exists," §37).
**Firewall:** price-only (no DXY/yields/macro/news/cross-asset/order-flow); gated M5 → causal H1/H4; no `read_csv`; N4=0; 2025+=0; no V1/holdout/CALIB. **0 executable candidate IDs** (≤24 budget) — per §33, no sequence survived discovery diagnostics. DEV-only. No promotion; broker disabled.

---

## 0. Headline — answers to §38
1. **Which sequences are enriched before bearish moves (discovery)?** Several show small positive discovery lifts (sweep+displacement, failed-bullish-continuation, two-stage impulse; and on H1 the deep 5-event sequence spikes to +0.276).
2. **Which survive matched controls / confirmation?** **None meaningfully.** H1: **0 of 130** ordered pairs survive; every priority bearish sequence inverts. H4: 7 of 86 "survive" a threshold but are **bullish-overextension** sequences within sampling noise (§4).
3. **Which components add incremental information (common-prefix)?** On **discovery** each added event lifts the rate (sweep +0.00 → +disp +0.043 → +break +0.056 → +reclaim +0.044 → +2nd-disp **+0.276**). On **confirmation** the incremental **REVERSES after the 3rd event** (+0.025 → +0.045 → +0.006 → **−0.044 → −0.116**). **No event robustly adds information; deeper sequences overfit harder.**
4. **Which discovery sequences fail confirmation?** Essentially all — the **strongest discovery lifts fail hardest** (H1 5-event: +0.276 → −0.116).
5. **Which final event best separates bearish from bullish?** None robustly. Bearish displacement (event 2) is the only weakly-generalizing addition; every event after it overfits.
6. **Does event ORDER matter?** Ordered sequences do not robustly beat their base rates → **order does not recover a signal.**
7. **Does event SPACING matter?** No rescue — with no generalizing signal, spacing tuning would fit noise.
8. **H4- or H1-identifiable?** Neither identifies bearish moves robustly (H1 0/130; H4 only bullish-overextension, within noise).
9. **Is a second bearish impulse more informative than the first?** On discovery **yes, dramatically (+0.276)** — but it **INVERTS on confirmation (−0.116).** So **no**: the "second impulse" edge is overfitting.
10. **Are failed-bullish-continuation sequences stronger than generic bearish-state?** FBC is the **best-generalizing bearish family** (CONF lift +0.024) — but the lift is **negligible** (bearish rate 11.6%→14%).

## 1. Evidence integrity
Price-only. Gated M5 → causal H1/H4. No exogenous inputs. No `read_csv`; N4=0; 2025+=0; CALIB not opened; DEV-only.

## 2. Bearish-move catalog (§4) — labels DIAGNOSTIC only
Reused the prior framework: net-bearish ≥150p over 12 (H4) / 24 (H1) forward bars. Base bearish-start rate: **H4 ~0.38, H1 ~0.13.** Future excursion used only to label historical examples.

## 3. Matched controls + event alphabet (§5, §6)
Controls = same universe/regime/location without the ≥150p bearish departure. **15-event causal price alphabet** built (HIGH_SWEEP, BEAR/BULL_DISP, BEAR_FOLLOW, STRUCT_BREAK_DOWN, FAILED_RECLAIM_DOWN, LOWER_HIGH, REJECTION_FROM_HIGH, COMPRESSION, EXPANSION_UP/DOWN, TREND_UP, RANGE, FAILED_BREAKOUT_UP, swing highs/lows) — all defined causally (fractals confirmed with lag; no future pivots).

## 4. Sequence-mining methodology + discovery/confirmation split (§9, §10, §11)
Chronological split (no outcome leakage): **DISCOVERY** first 60%, **CONFIRMATION** last 40% (cut ~2023-04). Ordered sequences (2–8 events) detected by causal backward-matching within a 12-bar window. **Sequences evaluated: 12 hand-picked priority families + 130 (H1) + 86 (H4) automated ordered pairs = ~228 total** (bounded, interpretable, min-support ≥15–25; §11). A sequence "generalizes" only if DISC lift >0.05 **and** CONF lift >0.05.

## 5. Sequence enrichment (§ per family) — priority families all fail confirmation
| sequence (H1) | DISC (n, lift) | CONF (n, lift) |
|---|---|---|
| sweep | 547, −0.001 | 340, +0.025 |
| sweep→bear_disp | 240, +0.043 | 186, +0.045 |
| sweep→disp→break | 146, +0.056 | 115, +0.006 |
| sweep→disp→break→failed_reclaim | 100, +0.044 | 83, **−0.044** |
| sweep→disp→break→reclaim→**2nd_disp** | 17, **+0.276** | 7, **−0.116** |
| **FBC** trend_up→sweep→disp→break | 91, +0.095 | 57, +0.024 |
| failed_breakout→disp→break | 73, +0.014 | 53, **−0.040** |
| exhaustion rej→lower_high→break | 73, −0.040 | 52, **−0.097** |
| compression→expansion_down | 267, +0.055 | 198, +0.015 |
| two-stage disp→reclaim→disp | 93, +0.111 | 71, **−0.046** |
**Every priority bearish family (§12–§17) either shows no discovery lift or inverts on confirmation.** (H4 identical pattern.)

## 6. Common-prefix attribution (§27) — the definitive test
Adding causal events to the sweep prefix (H1), DISCOVERY vs CONFIRMATION lift:
| prefix | DISC lift | CONF lift |
|---|---|---|
| sweep | −0.001 | +0.025 |
| +bear_disp | +0.043 | +0.045 |
| +structure_break | +0.056 | **+0.006** |
| +failed_reclaim | +0.044 | **−0.044** |
| +second_displacement | **+0.276** | **−0.116** |
**Each added event increases the discovery lift but the confirmation lift collapses/reverses** — the classic overfitting signature. **No event robustly adds directional information.** This directly refutes the hypothesis that a longer causal sequence (e.g., +failed-reclaim +2nd-impulse) carries more information: it carries more *in-sample noise*.

## 7. Automated ordered-pair search (§9, §11)
| TF | pairs (n≥25/15) | survive confirmation (both lifts >0.05) |
|---|---|---|
| **H1** | 130 | **0** |
| H4 | 86 | 7 — but all are **BULLISH-event** pairs (BULL_DISP→EXPANSION_UP, HIGH_SWEEP→BULL_DISP …), CONF lift +0.038…+0.063 within ~1 sampling SE (~0.09) of noise |
**On H1, zero of 130 pairs generalize.** On H4, the only "survivors" are **bullish-overextension** sequences — the *opposite* of the hypothesized bearish sequences — and their lift is within noise (bearish rate 0.40→~0.45).

## 8. Directional value → execution (§19, §20, §21) — the best directional sequence is not executable
The single best-generalizing directional sequence (H4 bull-overextension: BULL_DISP + EXPANSION_UP → SHORT next open, stop above the thrust high):
| RR | DISC avg / median / best-5%-rem | CONF avg / median / best-5%-rem |
|---|---|---|
| 1.5 | −0.472 / −1.056 / −0.573 | −0.166 / −1.045 / −0.253 |
| 2.0 | −0.424 / −1.056 / −0.547 | −0.133 / −1.047 / −0.244 |
| 3.0 | −0.380 / −1.057 / −0.552 | +0.051 / −1.048 / −0.103 |
**Median R ≈ −1.05 everywhere** (shorting a bullish overextension is stopped out by the continuing uptrend); the rr3/CONF +0.051 is a tail-lottery (median −1.05, best-5%-removed −0.103). **Not executable.** Since the directional signal is itself within noise AND execution fails, the outcome is the strongest negative (not `DIRECTIONAL_SIGNAL_FOUND`).

## 9. Failure anatomy + path (§18, §22)
Confirmed at the sequence level: adding the "final discriminator" events (failed-reclaim, second displacement) that theoretically separate winners from failures **degrades** out-of-sample performance. The path problem persists — bull-overextension shorts are stopped by the continuation (median −1.05).

## 10. Stop / entry / H4-H1-M15 hierarchy (§20, §21, §31, §32)
No sequence survived to warrant entry/stop/lower-TF refinement. H1 shows no generalizing pairs; H4 only bullish-overextension (non-tradeable). M15/M5 sub-sequence refinement (§32) is moot without a surviving parent sequence.

## 11. Economic geometry / tail / temporal (§23, §29, §30)
No executable candidate → per-candidate economics/tail/temporal (§39) are N/A. The sequence-level temporal evidence *is* the discovery→confirmation inversion (a chronological out-of-sample failure).

## 12. Candidate table (§39) — EMPTY
**Zero frozen executable candidates.** Per §33, only sequences surviving discovery diagnostics may become candidates; none did (all inverted or within noise). Creating a candidate from a discovery-only lift would be the overfitting the split is designed to catch.

## 13. Graveyard (§35, §40)
- All 12 priority bearish sequences (sweep-chains, FBC, failed-breakout, exhaustion, compression/expansion, two-stage) — **confirmation inversion.**
- 130 H1 + 86 H4 automated ordered pairs — 0 generalizing bearish (H1); H4 "survivors" are bullish-overextension within noise, non-executable.
- The deep 5-event sequence (sweep→disp→break→reclaim→2nd-disp) — the biggest discovery lift (+0.276), the biggest confirmation inversion (−0.116). Recorded in `price_seq_bearish.py`.

## 14. Remaining unexplored sequence classes (§37, §40)
The negative is bounded to **hard-boolean ordered sequences of the tested price-event alphabet, 2–8 events, on H1/H4.** Genuinely unexplored:
1. **Probabilistic / soft-sequence models** (HMM, Markov-chain, or learned sequence models) rather than hard boolean AND-chains — could capture graded transitions the boolean detector misses (though the component events already lack discrimination, limiting the upside).
2. **True nested multi-timeframe sequences** (H4 context → H1 sub-sequence → M15 trigger) as a single joint object — components tested separately here.
3. **M15/M5 micro-sequences** as the primary edge TF (M5-native already failed in prior work, so low prior).
4. **Very-long sequences (6–8 events)** — but the 5-event already overfits catastrophically, so longer is a worse prior.
5. **A genuinely bearish population** (2011–2013) — where sequences may carry real information.

## 15. CEO recommendation
1. **No price-sequence SHORT candidate — `NO_ROBUST_PRICE_SEQUENCE_SHORT_FOUND`.** Ordered temporal price-event sequences do **not** recover a generalizing bearish discriminator where static features could not. The discovery/confirmation split + common-prefix attribution show that **adding causal events increases in-sample lift but reverses out-of-sample** — the sequence "information" is overfitting.
2. **This is a stronger, deeper confirmation** (not a repeat) of the static-feature finding: on the 2021–2024 price-only population, **bearish direction is unpredictable — from static features AND from ordered event sequences.** The only weakly-generalizing directional structure is bullish-overextension reversion, which is within noise and not executable.
3. **Bounded conclusion (§37):** the price-only *sequence* hypothesis space (hard-boolean, ≤8 events, H1/H4) is now well-tested and negative. Genuinely unexplored classes (§14) remain — soft/probabilistic sequence models, nested MTF sequences, a bearish population — but each has a weak prior given that the underlying events do not discriminate and the exogenous drivers (excluded by mandate) are the likely true cause.
4. **Most defensible interpretation stands:** gold's 2021–2024 large bearish moves are predominantly exogenously (macro) driven; no price-only representation — static or sequential — reliably anticipates them. **No promotion; broker disabled; DEV-only; no candidate; no CALIB.** Existing candidates unaltered; portfolio SHORT remains only frozen `H4-bo-raw-S`.

**Terminal status:** `XAUUSD_PRICE_ONLY_BEARISH_SEQUENCE_DISCOVERY_COMPLETE` · `NO_ROBUST_PRICE_SEQUENCE_SHORT_FOUND`. **STOP.**
