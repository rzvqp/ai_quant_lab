# EXPLORATORY_PORTFOLIO_DIAGNOSTICS (diagnostic only — NO weight optimization, NOT a validated portfolio)

## A. FACTS — exposure of the 22 distinct candidates
- Direction: **14 long, 6 short, 2 both**. The book is near-pure LONG gold.
- Common monthly window ≈ 26 months (2022-12 → 2025-02); correlations therefore have WIDE CIs.

## B. Correlation structure (monthly summed-R, 1500-boot 95% CI)
Strongest positive (redundant, CI excludes 0):

| pair | r | 95% CI |
|---|---|---|
| S9_c4h=up_conf1h=align ↔ S9_c4h=up_conf1h=any | +0.88 | [+0.74,+0.95] |
| S20_ctx=h4up_trig=breakout ↔ S9_c4h=up_conf1h=align | +0.75 | [+0.44,+0.90] |
| S20_ctx=h4up_trig=breakout ↔ S9_c4h=up_conf1h=any | +0.75 | [+0.26,+0.92] |
| S17_level=pw_high_mode=breakout ↔ S39_er_thr=0.5 | +0.60 | [+0.37,+0.80] |
| S1_side=low_liq_ref=pdh_pdl ↔ S22_mode=breakout | +0.55 | [-0.02,+0.79] |
| S5_session=ny_side=up ↔ S6_session=ny_mode=breakout_side=up | +0.53 | [+0.25,+0.74] |
| S17_level=pw_high_mode=breakout ↔ S9_c4h=up_conf1h=any | +0.52 | [+0.13,+0.73] |
| S1_side=low_liq_ref=swing ↔ S20_ctx=h4up_trig=breakout | +0.50 | [-0.09,+0.77] |

Strongest negative (complementary):

| pair | r | 95% CI |
|---|---|---|
| S14_side=down ↔ S8_ref=vwap_side=up | -0.40 | [-0.67,+0.05] |
| S29_dow=4_side=up ↔ S31_window=month_start_side=down | -0.40 | [-0.61,-0.11] |
| S1_side=high_liq_ref=swing ↔ S1_side=low_liq_ref=session | -0.39 | [-0.68,+0.18] |
| S1_side=high_liq_ref=pdh_pdl ↔ S8_ref=vwap_side=up | -0.38 | [-0.58,-0.12] |
| S17_level=pw_low_mode=reject ↔ S29_dow=3_side=up | -0.37 | [-0.68,-0.01] |
| S29_dow=3_side=up ↔ S6_session=london_mode=fade_side=down | -0.34 | [-0.70,+0.07] |

## C. CLAUDE INTERPRETATION
- **Long-momentum cluster** (S9-any/align, S20-break, S17-pwhigh-break, S39; r .6–.88, CI excludes 0) is ONE bet — redundant; collapse to one representative before validation.
- Most "complementary" pairs have CIs crossing 0 (26 months) → **low correlation is NOT decorrelation**. The only resolved diversifier is the single SHORT candidate (S1 high/pdh) vs the long book.
- **Bull-beta domination risk (HIGH):** 19/22 candidates are long in a 2023-25 gold bull. The shortlist is largely one long-gold-beta exposure; genuine diversification is minimal until a beta-matched null runs.
- Concentration: candidates lean on 2023-24-25 (bull years); no bear-regime evidence exists in-sample.

## D. Guardrail
- No weights optimized, no portfolio declared validated. Portfolio Architect stays deferred (correlations too uncertain at 26 months; beta not removed). CODEX FILESYSTEM REVIEW PENDING.
