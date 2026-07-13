# RELATIONS — typed edges (OBSERVATIONAL, evidence + confidence)

Relations are observational (Codex review): one-family evidence cannot support causal claims. Vocabulary: IMPROVED_BY / ASSOCIATED_WITH_FAILURE_WITHOUT / OUTPERFORMS_MATCHED_VARIANT / CONSISTENT_WITH_BETA / CONSISTENT_WITH / UNDERPERFORMED_WITH / NO_INCREMENTAL_EDGE_DETECTED / FAILED_OOS / CORRELATED_WITH / ASSOCIATED_WITH / SUPPORTS.

| source | relation | target | evidence | confidence |
|---|---|---|---|---|
| P001 | IMPROVED_BY | C_confirmation | S1 confirmed positive; S21 raw negative (matched contrast) | medium |
| P011 | ASSOCIATED_WITH_FAILURE_WITHOUT | C_confirmation | S21 all negative | medium |
| P001 | OUTPERFORMS_MATCHED_VARIANT | P011 | sweep with vs without confirmation; NOTE confirmation also shifts entry/exposure (not a clean single factor) (C1) | medium |
| P005 | IMPROVED_BY | C_efficiency | S39 er>=0.5 positive; low-efficiency negative | low-medium |
| P012 | ASSOCIATED_WITH_FAILURE_WITHOUT | C_efficiency | S7/S10/S15/S38 negative | medium |
| P005 | OUTPERFORMS_MATCHED_VARIANT | P012 | efficiency-gated vs generic continuation (C2) | low-medium |
| P004 | IMPROVED_BY | C_psych_level | S22 breakout positive; reject negative | low-medium |
| P004 | OUTPERFORMS_MATCHED_VARIANT | P013 | round-number vs generic break (C4) | low-medium |
| P013 | ASSOCIATED_WITH_FAILURE_WITHOUT | C_psych_level | S3/S23 generic breakouts negative | medium |
| P006 | IMPROVED_BY | C_extreme_return | S42 fade of large 6-bar move positive (small n) | low |
| P006 | OUTPERFORMS_MATCHED_VARIANT | P014 | return-ranked vs value-reference reversion (C5) | low |
| P002 | IMPROVED_BY | C_structural_level | S2 fade at prior-day level positive | low-medium |
| P003 | ASSOCIATED_WITH | C_session_window | S5 opening-range positive | low-medium |
| P003 | OUTPERFORMS_MATCHED_VARIANT | P013 | opening-range vs generic break (C7) | low-medium |
| P007 | CONSISTENT_WITH_BETA | I7 | S9/S20 long-momentum in bull; beta plausibly explains it (not proven) | medium |
| P007 | CORRELATED_WITH | P003 | monthly-corr with the momentum cluster | medium |
| P014 | UNDERPERFORMED_WITH | C_vwap_reference | sigma-band VA a weak proxy; S8 marginal exception | low-medium |
| P019 | NO_INCREMENTAL_EDGE_DETECTED | C_volume | S41/S46 negative (needs ablation + more power) | low-medium |
| P018 | NO_INCREMENTAL_EDGE_DETECTED | C_divergence | S43 negative | low-medium |
| P017 | NO_INCREMENTAL_EDGE_DETECTED | C_intrabar | S44 negative (OHLC proxy; tick data untested) | low-medium |
| P016 | NO_INCREMENTAL_EDGE_DETECTED | C_regime_label | S40 always-on router negative | low-medium |
| P015 | FAILED_OOS | C_calendar | strong in-sample, OOS-refuted (S29/S31); calendar not proven causal | high |
| P011 | CONSISTENT_WITH | C_cost_drag | high-frequency + no edge | medium |
| P013 | CONSISTENT_WITH | C_cost_drag | frequent breakouts, cost-dominated | medium |
| P001 | SUPPORTS | I1 | positive conditioned version | high |
| P004 | SUPPORTS | I1 | positive conditioned version | high |
| P005 | SUPPORTS | I1 | positive conditioned version | high |
| P006 | SUPPORTS | I1 | positive conditioned version | high |
| P011 | SUPPORTS | I1 | negative unconditioned version | high |
| P012 | SUPPORTS | I1 | negative unconditioned version | high |
| P013 | SUPPORTS | I1 | negative unconditioned version | high |
| P015 | SUPPORTS | I6 | OOS-refuted calendar | high |
| P002 | SUPPORTS | I8 | level-type dependence | medium |
| P004 | SUPPORTS | I8 | level-type dependence | medium |
| P019 | SUPPORTS | I9 | unhelpful ingredient | medium |
| P017 | SUPPORTS | I9 | unhelpful ingredient | medium |
| P018 | SUPPORTS | I9 | unhelpful ingredient | medium |
| P016 | SUPPORTS | I9 | unhelpful ingredient | medium |
