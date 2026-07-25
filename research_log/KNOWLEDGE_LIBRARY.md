# LIVING KNOWLEDGE LIBRARY — Alpha
Consulted during every replay session. **Observe the market first; consult this only afterwards.**
Never force a match. Living document — updated whenever evidence changes.

Sources: lab registries (`KNOWLEDGE_REGISTRY.md`, `EDGE_DISCOVERY_REGISTRY_v1.md`,
`discovery_candidates/`) + my own `research_log/`. Lab-side entries are quoted, not paraphrased.

---
## 0. STANDING PROCEDURE — Library Concept Scan (CEO directive, 2026-07-22)
**Before registering any Discovery Candidate**, scan this entire library and record, as Section 6 of
the candidate, every concept identifiable in the event: K-claims, primitives (Volatility / Trend /
Structure), E-program themes, existing DCs, prior negative results, and recurring behaviours.

Rules:
- **List, do not judge.** Presence of a concept is neither support nor refutation.
- Do **not** attempt to validate or reject the candidate. Evaluation belongs to Red Team and the
  Statistician.
- Include concepts that appear to *cut against* the candidate as readily as those that fit — the aim
  is a complete conceptual description of the event, not a case for or against it.
- Include *cautionary precedents* (e.g. a prior mechanism in the same family that failed OOS).

Applied retroactively to DC-0002/0003/0004 on 2026-07-22 via addendum (hashes recomputed, handoff log
appended — never edited).

---
## 1. FROZEN DISCOVERY CANDIDATES (official)
| ID | Title | Status | My evidence |
|---|---|---|---|
| **DC-0001** | Isolated Single-Bar Velocity Outlier Followed by Gradual Multi-Bar Continuation | **FROZEN** (2026-07-21), Alpha 1 officially closed 2026-07-25 | ⚠️ Flagged against OBS-0014 (independent H1 operationalization, |body|/ATR>1.5, isolated: continuation *absent*, mild reversal, n.s., n=485). **Reconciled at the definitional level 2026-07-25** — see `DC0001_OBS0014_RECONCILIATION_NOTE.md`: distinct timeframe (M15 vs H1), distinct outlier definition, distinct forward horizon; not the same test of the same claim. The underlying scientific question (does DC-0001 survive a matched, correctly-scoped test?) remains open — reconciliation closes the comparison task, not the science. |

## 2. LAB KNOWLEDGE CLAIMS (K-registry) — highest-value prior knowledge
- **K01** (med, exploratory): raw **liquidity sweeps WITHOUT a confirmation stage produced non-positive expectancy**; confirmed variants better. S21 raw sweep — *all 48 variants negative*.
  → **Agrees with my OBS-0001** (prior-day sweep→reversal unsupported). Sweeps alone are a known dead end. Conditioning/confirmation is where any content lives.
- **K02** (high): **breakout/expansion-chasing and pullback-continuation variants generally negative**. Contradicted only by S39.
- **K03** (LOW, weak): trend continuation **weakly positive OOS only when gated by high trend-efficiency** (S39, +OOS .02). "does NOT demonstrate a validated efficiency effect"; tiny effect, threshold-selected, 2 RW.
  → ⚠️ **Probable convergence with LINE-A** — see §4.
- **K04** (high, OVERFIT/failed-OOS): **calendar / day-of-week / month-boundary effects strong in-sample but FAILED to replicate OOS** (S31 OOS −.44). "one weekday (Fri) OOS+ (selection-suspect)".
  → **Matches my OBS-0009** (weak Fri>Mon vol gradient, no return effect). **Do not pursue weekday effects.**
- **K05** (high, UNRESOLVED): of ~13 OOS-positive candidates, **11 are long-only in a 2023-2025 gold bull trend**; timing-alpha vs long-gold-beta **unresolved** pending a beta/regime-matched null.
  → **This is the same confound I kept rediscovering** (OBS-0001 trend contamination, OBS-0005 PDC, OBS-0017 swing-low bounce = buy-the-dip). My observations independently corroborate K05.

## 3. EDGE PROGRAM (E001–E040) — status themes
Many edges closed **DISCOVERY_COMPLETE — V0 NOT SUPPORTED** (incl. "reversal rate ~52% on both M15 and H1" = coin-flip; "NOT SUPPORTED as an Asia-specific mechanism"; "clean, complete null"; "NOT SUPPORTED as an inside-bar-specific mechanism"; one killed by a random-matched-distance control). Several remain DISCOVERY_IN_PROGRESS / CLEAN_RERUN_COMPLETE. **E014-V1** is the program's only frozen V1 candidate.
→ Lesson encoded: this market has repeatedly returned ~coin-flip reversal rates at structure. My own nulls are the norm here, not bad luck.

## 4. MY RESEARCH LINES
### LINE-A — structural-break churn vs isolation → **now suspected ≡ trend-efficiency (K03)**
Claim: break reliability lives in ambient context (churn vs commitment), not break geometry.
- Support: 5 replay windows/3 regimes; 3 unforced sightings of compression→expansion (#003, LINE-A W1, #010).
- Against: geometry-null already established (OBS-0004, OBS-0017); M5 evidence that label density is a **volatility-scale artifact** (#005/#006).
- ⚠️ **Convergence:** "churn vs commitment" is plausibly the same conditioning variable as K03's **trend efficiency**. If so, the lab has *already* tested it statistically: result was **weakly positive at best (~.02R), threshold-selected, explicitly not validated.** This substantially **deflates** LINE-A's novelty.
- ✅ **But it hands me the definition I lacked** (#010: "I cannot defend a definition of compression"). **Trend efficiency** (net displacement / summed absolute movement) is standard and defensible.
- Maturity: structured phenomenon → **needs a decisive test against K03**: does churn/structure-context add anything *beyond* a plain efficiency metric? If not, LINE-A dies into K03.

### LINE-B (candidate, unopened) — failed excursion defines a consolidation boundary
From #008/#008-RESOLUTION: a large rejected excursion (Dec-4-2023 spike ~2,145) capped the market ~3 months, then was cleanly reclaimed. Refined claim: a failed excursion marks the **upper boundary of a consolidation**, not a top. Very low confidence; no directional content claimed.

## 5. FAILED / CLOSED HYPOTHESES (mine) — do not re-run as specified
| ID | Hypothesis | Result |
|---|---|---|
| OBS-0001 | prior-day sweep-reject vs break-hold aftermath | NEGATIVE (indistinguishable at 1–6h) |
| OBS-0002 | break-hold continuation = level or trend effect | NEGATIVE (dissolves into drift+noise) |
| OBS-0004 | sweep depth predicts reversion | NEGATIVE (corr≈0) |
| OBS-0005 | prior-day close is a magnet | NEGATIVE (opposite; confounded) |
| OBS-0010 | round-number clustering of daily extremes | NEGATIVE (refuted) |
| OBS-0015 | weekend gap fill | trivially true (~0 ATR gaps) |
| OBS-0016 | equity-style leverage effect on gold | NEGATIVE (vol symmetric in return sign) |
| OBS-0017 | marginal swing-high overshoot = reversal tell | NEGATIVE (overshoot uninformative) |

## 6. ROBUST / CONFIRMED BEHAVIOUR
- **Volatility structure is the robust thing in this market** (lab primitive PROMOTED; my OBS-0006/0007): Parkinson clustering acf1 +0.53; **hour-of-day profile with 4.3× peak/trough (NY-open peak 13–14h UTC)**; clustering survives deseasonalizing; residual day-to-day vol persistence; daily range persistence +0.26.
- Gold volatility is **symmetric in return sign** (no equity leverage effect) — OBS-0016.

## 7. OPEN QUESTIONS
1. **NRQ-1b / OBS-0008** — NY-session prior-day-high sweep-reject reversion. Uniquely distinguished among 6 cells, sign-stable both halves, matched-null p=0.021, **fails Bonferroni, n=42**. **Holdout-gated; CEO decision pending.** Note K01: this is a *conditioned* sweep, which is exactly where K01 says content might live.
2. Does LINE-A add anything beyond K03 trend-efficiency? (decisive)
3. ~~Reconcile OBS-0014 vs DC-0001 operationalization.~~ Definitional reconciliation CLOSED
   2026-07-25 (`DC0001_OBS0014_RECONCILIATION_NOTE.md`); the decisive matched test itself remains
   open, owned by Red Team / Statistician, not Alpha.
4. K05's unresolved timing-alpha vs long-beta split — my confound sightings feed this.
5. How often does compression *fail* to resolve into expansion? (never counted — survivorship risk)

## 8. RECURRING BEHAVIOURS OBSERVED (visual, unforced)
- **compression → expansion transition** ×3 (Oct 2023; Jan–Feb 2024; Feb–Mar 2024)
- failed counter-trend structure shift preceding a committed move (#003) — n=1
- large failed excursion capping a consolidation for weeks–months (#008) — n=1
- at M5 in thin tape, structure labels contradict the prevailing drift (#006) — treat sub-H1 "structure" with suspicion
