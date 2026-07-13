# CLAUDE_CODEX_REVIEW — Lab Knowledge System (S1-S40)

Real Claude (Research Lead / Methodology Guardian) + Codex (Data & Code Analyst) collaboration, per CEO
workflow. Codex was consulted via **compact inline prompts** (its MCP filesystem snapshot is stale — see §3).

## 1. What Claude verified DIRECTLY on-disk (authoritative)
- Totals from the verified parquets: **S1-S40 = 2300 hypotheses, 375 historically-profitable, 139 Research-Worthy**
  (S1-S20: 1972/357/130; S21-S40: 328/18/9). Re-verified twice; clean git status; commit `a21dff7`.
- Reconstructed all canonical specs from the FROZEN grammars (`mstrat.py` + `mstrat_ext.py`, unchanged).
- Dedup: 139 RW → **22 distinct** economic candidates (mechanism-key + correlation validation).
- Read-only re-backtests recovered yearly / risk-ATR / long-short / monthly streams for the 22 representatives.
- Pairwise monthly-return correlations with bootstrap CIs (kb_correlations.json).
- Corrected a prior transcription error: my earlier Tier-B markdown Σ said 26 profitable/10 RW; the parquet is **18/9**.

## 2. What Codex REVIEWED inline (data supplied in-prompt; CODEX INLINE DATA REVIEW)
- **TASK 1 (schema):** confirmed FAMILY_RESULTS = 1972 rows and the shared 22-column schema. (Its ext counts were
  stale — see §3; resolved against the verified artifact.)
- **TASK 2 (dedup design):** delivered a full ruleset — hierarchical dedup (mechanism_id + execution_variant_id),
  quantitative thresholds (execution Jaccard ≥95% & R-corr ≥.98; parametric Gower ≤.20 & monthly-corr ≥.85;
  economic causal-signature + overlap ≥70%/corr ≥.80), medoid representative, over/under-clustering diagnostics.
- **TASK 3 (scoring):** delivered a concrete ranking formula (expectancy only 8%; penalties for negative-OOS,
  top1-dependence, small-n, cluster-redundancy, long-only beta; hard exclusions fragile/n<20/top1≥80%). Adopted.
- **TASK 4 (mechanism review):** classified all 13 mechanisms (SUPPORTED-EXPLORATORILY / MIXED / REPEATEDLY-
  NEGATIVE / OVERFIT), flagged over-strong claims, named the genuinely-distinct three, and the biggest risk.
- **TASK 5 (final review):** critiqued the shortlist + knowledge claims; stricter shortlist; claim-weakening; next test.

## 3. What Codex could NOT verify (CODEX FILESYSTEM REVIEW — PENDING)
Codex's MCP sandbox is a **stale snapshot**: it reads the 8 Tier-B ext result files as empty (sees 188/2/2
instead of 328/18/9), so **no Codex conclusion about Tier-B (S22, S24, S25, S27, S28, S29, S30, S31) is a
file-level Codex review.** All Tier-B numbers here are Claude-verified on-disk. A true Codex filesystem review
requires re-syncing its environment to commit `a21dff7`.

## 4. AGREEMENTS (Claude ↔ Codex)
- FAMILY_RESULTS = 1972 rows; shared schema.
- Dedup by economic mechanism, collapsing tuning dims; representative by robustness NOT expectancy.
- Keep different pools / opposite sides / reversal-vs-continuation SEPARATE even if correlated.
- The **long-momentum cluster (S9/S20/S17-break/S39, r .6–.88) is ONE bet** — not independent confirmations.
- **Calendar (S29/S31) = overfit** (family-wise selection); exclude from the shortlist despite raw score.
- Genuinely distinct SUPPORTED-EXPLORATORILY mechanisms: **confirmed liquidity sweep (S1), opening-range
  momentum (S5), failed-breakout fade (S2)** (+ round-number momentum S22, thinner).
- Repeatedly-negative: breakout/expansion chasing, pullback continuation, value/VWAP reversion, regime routing.
- **Biggest risk: multiple-testing selection + unremoved long gold beta; OOS alone does not cure family-wise selection.**
- Next step: one **frozen, direction/regime-matched null on untouched data in a single dependence-aware global
  multiplicity procedure, beta-adjusted, net of costs.** No alpha claim before that.

## 5. DISAGREEMENTS (kept visible)
- **Ext totals (resolved):** Codex 188/2/2 (stale) vs Claude 328/18/9 (verified on-disk) → Claude stands; Codex view stale.
- **Shortlist depth:** Claude's initial 8 included S1-low/pdh and S17-pw_low as full members; **Codex demoted both to
  reserve** (OOS +.01 ≈ null; +.08 insufficient). Reconciled: adopted Codex's demotion — both moved to reserve.
- **S1 low/swing:** Claude ranked it high (score 84.9); Codex kept it but flagged **high-uncertainty (n=43)**.
  Reconciled: shortlisted as **provisional/high-uncertainty**.
- **Momentum representative:** Claude defaulted to S20 (best cluster score); Codex insists it be chosen
  **mechanically** (simplicity/effective-n/cost), not by score. Reconciled: S20 default, to be re-checked mechanically.

## 6. Review limitations
- Codex saw only the inline data, not the files (stale sandbox) — so its review is design/critique-level, not a
  ledger-level recomputation.
- Correlations rest on ~26 common months → wide CIs; "low correlation" is not decorrelation.
- No beta-adjusted expectancy computed yet; timing-alpha vs gold-beta is unresolved.
- No global-FDR, no walk-forward, no holdout — all CEO-gated. Nothing here is validated alpha.

## 7. STATUS
- **CODEX INLINE REVIEW: COMPLETE** (TASKs 1-5 delivered on inline data; genuine independent design/scoring/mechanism/final review).
- **CODEX FILESYSTEM REVIEW: PENDING** (stale sandbox; re-sync to `a21dff7` required for a file-level Tier-B review).
