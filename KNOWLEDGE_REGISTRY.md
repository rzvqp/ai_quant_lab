# KNOWLEDGE_REGISTRY (falsifiable claims)

Each claim is dataset/timeframe/regime-scoped and falsifiable. Wording WEAKENED per Codex TASK-5 review (no causal over-claims; "failed to replicate OOS" not "proven overfit"). Machine copy: KNOWLEDGE_REGISTRY.jsonl.

### K01  (confidence medium, status EXPLORATORY, selection-uncontrolled)
**Claim:** On XAUUSD M15 (2022-2025), in the tested S1 specifications, liquidity sweeps WITHOUT a confirmation stage produced non-positive expectancy, while confirmed variants performed better; the evidence is consistent with the confirmation stage carrying the S1 result (not proof of causation; selection and sample composition uncontrolled).

- For: S21 (raw sweep) all 48 variants negative; S1 confirmed variants multiple RW with +OOS
- Against: S1 low/pdh OOS ~+.01 (near null)
- Supporting families: S1 · Contradicting: S21
- Limitations: 4 years, bull sample, family-wise selection not corrected
- Next test: confirmed vs unconfirmed in frozen matched null

### K02  (confidence high, status EXPLORATORY)
**Claim:** On XAUUSD M15 (2022-2025), the tested breakout/expansion-chasing and pullback-continuation variants were generally negative across the entry-timing choices tested (not proven for all possible timings).

- For: S3/S4/S23/S30 and S7/S10/S15/S38 negative
- Against: S39 efficiency-gated continuation weakly positive
- Supporting families: S3,S4,S23,S30,S7,S10,S15,S38 · Contradicting: S39
- Limitations: entry-timing coverage not exhaustive
- Next test: exhaustive entry-timing sweep in matched null

### K03  (confidence low, status EXPLORATORY, weak)
**Claim:** On XAUUSD M15, trend continuation became weakly positive OOS only when gated by high trend-efficiency (S39, +OOS .02); this is weak and variant-dependent and does NOT demonstrate a validated efficiency effect.

- For: S39 high-efficiency variant +OOS; low-efficiency variants negative
- Against: effect size ~.02R, only 2 RW
- Supporting families: S39 · Contradicting: S15,S38
- Limitations: tiny effect, threshold-selected
- Next test: efficiency-gate ablation in matched null

### K04  (confidence high, status OVERFIT / failed-OOS)
**Claim:** On XAUUSD M15, calendar / day-of-week / month-boundary effects were strong in-sample but FAILED TO REPLICATE out-of-sample (S31 OOS -.44) — evidence consistent with overfitting under family-wise selection, not a proven persistent effect.

- For: S29/S31 in-sample exp up to .42 but OOS negative/near-zero
- Against: one weekday (Fri) OOS+ (selection-suspect)
- Supporting families: S18,S29,S31 · Contradicting: 
- Limitations: family-wise multiplicity; few events
- Next test: single pre-registered window, family-wise-corrected, untouched data

### K05  (confidence high, status UNRESOLVED)
**Claim:** On XAUUSD M15, of the ~13 OOS-positive distinct candidates, 11 are long-only in a 2023-2025 gold bull trend; the split between timing-alpha and long gold beta is UNRESOLVED and remains so until a beta/regime-matched null is run.

- For: exposure-weighted long dominance; only S1 high/pdh is short
- Against: matched-null (engine) removes drift-beta by construction but not yet applied to the full candidate set
- Supporting families: most · Contradicting: S1(short)
- Limitations: no beta-adjusted expectancy computed yet
- Next test: beta/regime/direction-matched null over the full candidate set in one global multiplicity procedure

