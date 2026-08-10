# RED TEAM — CODE ATTACK · Validation precondition (three verdict-blocking components)
### RT-CODE-A-0013 · Target: `code/restante_validation.py` @ `c73d2d5` (statistician-foundation)
**Date:** 2026-08-06 · **Auditor:** Red Team · **Spec:** STAT-DOMAIN-MISMATCH-AND-RESIDUALS-v1.0 + RT-CODE-A-0006. **If this passes, the four pilots receive the project's first formal verdict.** Checklist only: lookahead, leakage, circularity, ambiguity, overfitting, hidden params, reproducibility. **No real-data run** (Red Team does not backtest) — the statistical algorithm was verified on synthetic distributions (pure-function copies, no data-load); nothing modified; no remedy.

## VERDICT — **PASS_WITH_LIMITATIONS.**
The three components are correctly implemented; the **FPR repair is verified complete** (buggy→FPR≡0, fixed→~0.05, and the gate correctly rejects heavy-tailed shapes); the four pilots pass the calibration **robustly** (0.011–0.043, far below any reasonable gate); lookahead/leakage/circularity/reproducibility are clean. **The pilots can receive a formal verdict — conditioned on the Statistician addressing the one load-bearing unverified assumption: cross-day independence in the day-block (Target A).** If a pilot's trades cluster on recurring structures across days, its p-value is anti-conservative and the verdict overstated.

---

## OWN TARGET — the FPR≡0 repair: **VERIFIED COMPLETE, no other mis-centering path.**
The bug was that the inner oracle's null was centered at the global 0, not at the synthetic set's own resampled mean `obs`. The fix (`calibrate_candidate:124`): `ss_c = ss - obs*sz` re-centers each synthetic set to its own mean before the inner oracle. **Verified numerically** (pure-function copies, synthetic known-null):
- **Buggy version (no re-center): FPR = 0.0000** on normal/skew/heavy — reproduces the reported symptom exactly, confirming the cause.
- **Fixed version: FPR = 0.045 (normal), 0.034 (skew), 0.063 (heavy-tailed)** — calibrated to ~0.05. ✅
- **No other mis-centering path:** the actual `calendar_block_bootstrap` (component 1) centers `dsum0` at the candidate mean and tests the RAW `observed` against it — the standard, correctly-centered bootstrap-of-the-mean. The two centerings (candidate-global at `_day_blocks`, synthetic-set-obs at the oracle) are both correct and independent.
- **Bonus finding — the gate WORKS:** the heavy-tailed case fails the gate (FPR 0.063, **CI-upper 0.080 > 0.07**). So the per-candidate calibration genuinely **catches shape-induced miscalibration** — it is not a formality, and it is almost certainly why CAND-0013/0018/0022/0024 fail (heavy-tailed/skewed net_R) while the four pilots (smoother shapes) pass.

## SPEC TARGET A — does the day-block contain the ENTIRE TRADE-level dependence? **NO — it contains BAR dependence, assumes cross-day independence. (Load-bearing.)**
The block = one trading day; the bootstrap resamples **whole days**, so **within-day** dependence is preserved (the day-sum carries it — verified: a per-day shared effect does not inflate FPR). **But two trades on DIFFERENT days keyed to the same structure** (same PDH/session level/zone/regime, touched days apart) land in **different blocks and are treated as independent.** The spec's "day > 4×H" argument bounds the **bar-outcome** horizon (~H bars), **not** structural reuse across days. If a candidate's edge concentrates on a few recurring structures, the day-block **overstates the effective sample → understates variance → anti-conservative p-value.**
- **Severity is candidate-dependent and unmeasured.** Day-keyed candidates (CAND-0001 PDH/PDL — a *new* level each day) likely have low cross-day reuse; **persistent-structure candidates (FVG/OB/zone — CAND-0002/0003/0007)** can reuse the same zone across days and are more exposed. **This is the one assumption that could invalidate a formal p-value** — the Statistician must measure each pilot's cross-day trade autocorrelation (how concentrated are trades on recurring structures) before crediting the verdict.

## SPEC TARGET B — does centering at 0 preserve enough SHAPE? **YES — shape adequate; the residual is cross-day dependence, not the centering.**
Centering subtracts the mean, producing a mean-0 null while resampling **whole day-sums**, so the day-sum distribution's **skew and tails are preserved** (verified: skew/heavy shapes flow through and the gate reacts to them). This is legitimate for a **location-shift null of the mean.** What centering does NOT preserve is **cross-day autocorrelation** (destroyed by resampling days independently) — but that is Target A, not a centering defect. **So centering is adequate; the per-candidate gate is precisely the check that the preserved shape does not break the oracle** (and it fails the shapes that do). Verified.

## OWN TARGET — matrix scoping repair (the 7/10 CAND-0018-at-10-months noise): **n≥25 and 48 months — reasonable, not conservative.**
The repair adds `RESOLVE_MONTHS = 48` (a pair decides the rule only with ≥48 common months) and `N_MIN_VERDICT = 25`. **SE(r) ≈ 1/√(n-3):** at 48 months SE≈0.145 (matches the code's 0.14), at 10 months SE≈0.38 (matches the reported 0.35). So requiring ≥48 months makes SE≈0.14, and `NEG_MATERIAL=-0.3` is ~2·SE below 0 — **resolvable, but only marginally**: a pair at exactly 48 months with r≈−0.3 has a Fisher-z 95% CI whose upper end is near 0. **Two decoupling gaps:**
1. **n≥25 (trades) ≠ ≥48 (months):** a candidate can be verdict-eligible (n≥25) yet never resolvable (<48 months of activity) → **its PRDS is never verified, yet it still goes on BH.** The PRDS check covers only long-history pairs.
2. Material-negatives near the 48-month/−0.3 boundary are **weak evidence** for the partition; a stricter month floor (60–72) would tighten SE.

## OWN TARGET — the partition pivot (all 3 negatives share CAND-0016): **cannot be confirmed genuine — possible resolvability-selection artifact.**
The pivot is the candidate common to all *resolvable* material-negative pairs. **The resolvability filter (≥48 months) selects which negatives count** — so CAND-0016 could appear in all resolvable negatives simply because it has the **longest overlap**, not because it is uniquely anti-correlated. The code reports `material_negative_noise_excluded` as a **count only, not the pairs** — so we cannot see whether the sub-48-month negatives also center on 0016 (→ genuine pivot) or involve **other** candidates (→ the "0016 pivot" is partly a selection artifact). **The Statistician must inspect the noise-excluded negative pairs** before accepting "isolate 0016; rest on BH." As-is, the partition verdict is **plausible but unverified**.

## OWN TARGET — the FPR gate = 0.07: **a convenience threshold, but IMMATERIAL to the pilots.**
0.07 is a declared tolerance (1.4× nominal FPR — tighter than the 2× seen in RT-CODE-A-0006, still not a principled anchor). At 0.075, three of the four failing candidates (CI-upper 0.072–0.075) might flip to pass; CAND-0024 (0.077) still fails. **But the four PILOTS pass at 0.011/0.022/0.025/0.043 — far below 0.06/0.07/0.075 alike**, so the gate's exact value **does not touch the pilots' eligibility.** The 0.07-vs-0.075 question only decides the four *non-pilot* candidates, which are not receiving a verdict anyway.

## CHECKLIST
- **Lookahead — PASS.** `collect_per_trade` keys each realized net_R to its entry-bar day/month (available at trade time); the bootstrap resamples **observed** outcomes — no future data enters.
- **Leakage — PASS.** Pure resampling of collected results; per-candidate isolation.
- **Circularity — PASS.** Calibrating the oracle on the candidate's own centered (null) shape and testing the observed mean against the bootstrap null are distinct uses of the data; under H0 the shape *is* the null, so shape-calibration is definitional, not circular.
- **Ambiguity — minor.** The partition-pivot reporting hides the noise-negative pairs (above).
- **Overfitting — PASS.** No fitted parameters; the thresholds are declared choices.
- **Hidden params — PASS with note.** All thresholds named with rationale; three are **convenience values** (FPR_GATE 0.07, RESOLVE_MONTHS 48, NEG_MATERIAL −0.3) — declared, not derived.
- **Reproducible — PASS with fragility note.** Deterministic seeds; but the calibration seed is `7_000_000 + ci*1000` (enumeration-index-dependent), so adding/removing a candidate or crossing DAY_MIN reshuffles downstream seeds — reproducible only if the eligible list order is stable.

## SEVERITY
- 🟠 **RV-L1 · Day-block assumes cross-day independence (Target A)** — the load-bearing unverified assumption; anti-conservative for structure-reuse candidates. **Measure each pilot's cross-day trade autocorrelation before crediting the verdict.**
- 🟡 **RV-L2 · Partition pivot (CAND-0016) unverified** — possibly a resolvability-selection artifact; report the noise-negative pairs to confirm.
- 🟡 **RV-L3 · PRDS verified only for ≥48-month pairs** — short-history verdict-eligible candidates go on BH without a PRDS check.
- 🟡 **RV-U1 · Convenience thresholds** (0.07 / 48 / −0.3) — immaterial to the pilots; material to the family machinery. 🟡 **RV-U2 · Enumeration-index seed** (reproducibility fragility).

## WHAT SURVIVES (verified)
FPR repair complete (buggy≡0, fixed~0.05, gate rejects heavy tails); the four pilots calibrate robustly (0.011–0.043); the block/day count logic retracts L=28 correctly (block=day, count=distinct days, immune to trade frequency); centering preserves shape adequately (Target B); lookahead/leakage/circularity clean; the per-candidate gate is a functioning check, not a formality.

## VERDICT — **PASS_WITH_LIMITATIONS.** The precondition machinery is sound and the pilots pass it robustly — **the four pilots may receive the project's first formal verdict, conditioned on the Statistician (a) measuring cross-day trade autocorrelation for each pilot (RV-L1 — the only limitation that can invalidate the p-value), and (b) confirming the CAND-0016 partition against the noise-negative pairs (RV-L2).** RV-L3/U1/U2 are disclosures, not blockers, and none touches the pilots' individual calibration.

## HANDOFF → Statistician, then CEO
1. **RV-L1 (before the verdict):** for each pilot, measure how concentrated its trades are on recurring cross-day structures (same level/zone touched across days); if concentrated, the day-block p-value is anti-conservative — widen the block to the structure, or disclose the residual.
2. **RV-L2:** inspect the noise-excluded negative pairs; if they also center on CAND-0016, the pivot is genuine — else the partition is a selection artifact.
3. **RV-L3:** decide how to treat verdict-eligible-but-short-history candidates whose PRDS is unverified (BY fallback, or exclude from BH).
4. The FPR repair, the pilots' calibration, and the block-day logic are **verified clean** — the mechanism is ready.

Red Team designed no remedy, ran no data on the market, modified nothing outside `red_team/`.
