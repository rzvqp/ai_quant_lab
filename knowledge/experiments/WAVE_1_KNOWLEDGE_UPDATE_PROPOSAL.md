# WAVE_1_KNOWLEDGE_UPDATE_PROPOSAL — proposed Knowledge-Graph edits (NOT APPLIED)

These are PROPOSED edits derived from `WAVE_1_EXECUTION_REPORT.md`. **Nothing here is written to
`knowledge/ontology/KNOWLEDGE_GRAPH.*`, `BEHAVIOR_REGISTRY.*`, `RELATIONS.md`, or `INVARIANTS.md` yet.**
Applying them requires an explicit CEO gate. Each item gives: target node/edge · current state · proposed
change · Wave-1 evidence · confidence. All evidence is research-segment, family-wise (Holm) corrected,
holdout SEALED; EXP-03/04 are DIAGNOSTIC-grade (stratified null not calibration-validated).

## A. Edges — mechanism ingredients (EXP-01, EXP-02): DOWNGRADE to unconfirmed
1. **Edge `P001 IMPROVED_BY C_confirmation`** (current confidence: *medium*, basis S1 vs S21-raw matched contrast).
   - **Proposed:** downgrade to **INCONCLUSIVE / unconfirmed at the paired bar**; annotate: "Wave-1 EXP-01 (paired,
     identical sweep-event sample, n=337): Δ(confirmed−raw)=+0.107R, 95% CI [−0.047,+0.261] **straddles 0**,
     Holm adj p=0.44. The apparent S1-vs-raw gap decomposes into confirmation-as-SELECTION (drop 15% non-confirming
     sweeps: −0.145→−0.031) + confirmation-as-TIMING (delay 3.07 bars + worse entry: −0.031→+0.032); neither is a
     clean single factor. Edge NOT refuted, NOT confirmed."
   - Confidence: keep the edge but mark **evidence = mixed/unresolved**.
2. **Edge `P001 OUTPERFORMS_MATCHED_VARIANT P011`** (current *medium*): annotate with the EXP-01 decomposition
   (selection vs timing split, delay 3.07 bars, entry-price shift +0.84) — the outperformance is **mechanically
   confounded**, as the edge note already warns (C1). No confidence change; add the quantified decomposition.
3. **Edge `P005 IMPROVED_BY C_efficiency` (P005 vs P012 generic continuation)** (current low).
   - **Proposed:** mark **unconfirmed**; annotate: "Wave-1 EXP-02 (same-universe partition, n_on=159): the
     efficiency-labeled subset does NOT beat random equal-size subsets of the continuation universe (Δ=+0.046R,
     p=0.30, Holm adj 0.53); both arms negative in-sample. The gate does not select better-than-random trends at
     the Wave-1 bar. (S39-as-registered is marginally +0.029 but that is its specific onset, not the isolated gate.)"
   - Confidence: **P005 remains low; efficiency-gate SELECTION value not demonstrated.**

## B. Edges — beta axis (EXP-03, EXP-04): the highest-information update
4. **NEW edge (proposed) `P001 SURVIVES_BETA_REGIME_MATCHED_NULL`** — diagnostic-grade.
   - Evidence: EXP-03, long side n=399, obs +0.032R vs session×vol×trend-matched null −0.139, p=0.00695,
     **Holm adj p=0.0417 (only family-wise survivor)**; validated *unstratified* anchor agrees (p=0.0046).
   - **Confidence: LOW / diagnostic.** MUST carry the caveats: stratified null not calibration-validated; effect
     small; **OOS expectancy negative (−0.061)**; "survives null" ≠ profitable (short mirror survives its null yet
     loses). **Explicitly NOT a promotion of P001 and NOT tradable-alpha evidence.**
5. **Relation `I7 (Beta Confound) → P001`:** propose annotate "**partially relaxed on research** — sweep timing
   carries information beyond direction/regime/beta (EXP-03, diagnostic-grade), pending a calibration-validated
   stratified null and a durable OOS/holdout test." Do NOT downgrade I7 globally.
6. **NEW edge (proposed) `P003 CONSISTENT_WITH_BETA`** / strengthen `I7 → P003`.
   - Evidence: EXP-04, obs +0.076R vs β/regime-matched null +0.019, p=0.177 (NOT significant); the null itself
     earns +0.019 once matched on NY-session×vol×trend, i.e. **most of the opening-range edge is regime/beta**.
     (Unstratified anchor is significant at p=0.034 — precisely the beta the diagnostic strips out.)
   - **Confidence: medium.** **I7 STANDS for P003.** This is Wave-1's single most decision-relevant negative.

## C. Invariant / node annotations — level identity (EXP-05, EXP-06): inconclusive
7. **`I8 (Level-Type Association)` and edge context `P001/P010`, `P002`:** propose annotate "Level-label placebos
   (EXP-05 S1, EXP-06 S2) are **inconclusive**: real out-performs the shuffled level (real > 88% / 76% of shuffles)
   but not at the family-wise bar (Holm adj 0.47 / 0.53); NOT shown spurious (lower-tail p high). Placebo
   construction validated (frequency preserved to 0.5% / 7%)." No confidence change to I8; record the negative
   controls as CLEAN-BUT-UNDERPOWERED.
8. **Nodes `P010 (Liquidity Memory)`, `P002 (Failed-Breakout Fade)`:** no status change; attach the EXP-05/06
   placebo evidence as "level identity neither confirmed nor refuted."

## D. Node status recommendations (proposed, for CEO ratification)
| node | current | proposed after Wave 1 |
|---|---|---|
| P001 Confirmed Liquidity Sweep | SUPPORTED-EXPLORATORILY (med) | keep status; **add beta-axis positive (diagnostic, research-only, −OOS)**; confirmation-ingredient UNCONFIRMED |
| P003 Opening-Range Momentum | SUPPORTED-EXPLORATORILY (med) | keep status; **flag substantially BETA/REGIME (I7 stands)** |
| P005 Trend Efficiency (gated) | SUPPORTED-EXPLORATORILY (low) | keep low; **efficiency-gate selection value UNCONFIRMED** |
| P011 Raw Sweep | REPEATEDLY-NEGATIVE (high) | unchanged (raw all-sweeps exp −0.145 reconfirmed) |
| I7 Beta Confound | high (caution) | unchanged globally; **relaxed for P001 (partial), stands for P003** |
| I8 Level-Type Association | medium | unchanged; add two clean-but-underpowered placebo controls |

## E. Recommendation for the CEO (do NOT act without gate)
- **Apply B (beta-axis) edits first** — they are the highest-information and rest partly on the validated
  unstratified anchor. But gate any P001 beta-positive edge on: (i) building & CALIBRATING the stratified null,
  (ii) a durable OOS/holdout confirmation (currently OOS is negative). **No promotion of P001.**
- **A and C are downgrades/annotations** (confirmation & efficiency unconfirmed; placebos inconclusive) — low risk.
- Nothing here justifies opening the holdout, running global FDR, or declaring alpha.

*(This file lists proposals only. The Knowledge Graph is UNCHANGED on disk.)*
