# RED TEAM — CODE ATTACK · The statistical stack (the code that VALIDATES)
### RT-CODE-A-0006 · Targets: `matched_null.py`, `mn_calibration/adversarial/power`, `scoped_fdr_run.py`, `pilot_pvalue.py`, `synth_price.py`, the WP-5′ block-bootstrap oracle
**Date:** 2026-07-30 · **Auditor:** Red Team · **Mandate:** CEO — the second unattacked end from RT-AUDIT-CHAIN-0001 (C-R2). W9 still recorded open; verify. **No data run · nothing modified · no remedy designed.**
**Method:** full source of the matched-null engine + three batteries + scoped-FDR + synth generator read by Red Team at source; git-level W9 reconstruction and WP-5′/verdict-dependency archaeology via two evidence sweeps. Every claim below is source- or git-verified.

## HEADLINE — does the code that VALIDATES produce a wrong verdict? **NO defect that produces a wrong verdict was found — unlike the enforcement engine.** But the validation is **MIS-SCOPED**, its guarantees are **weaker than advertised**, and **my own W9 record was stale.** Nothing is promoted on any of these engines; the chain fail-closed again.
Contrary to the working suspicion ("do not assume what validates is healthier than what enforces"), the validation chain is **structurally sounder** than the DEMO gate: the FDR is correct, the window discipline is clean, the drift fix is present and passing. The problems are not wrong math — they are **domain mismatch** (validated for a stop type and a sample size the current candidates don't have) and **lenient calibration gates**.

---

## TARGET 1 — W9 · CORRECTED: the fix IS on the official line; my prior record conflated two objects

**Git-verified state (statistician-foundation @ HEAD):**
- The flow-c D3 fix was **cherry-picked** onto the official line on 2026-07-25 (`d4fb426`/`4259382`/`d4ee4bb`, new SHAs). `code/matched_null.py` and `code/mn_adversarial.py` are **byte-identical to flow-c** (`git diff` empty) — they carry the ATR-rescaling drift control (`matched_null.py:86`) and the `drift_long`/`trend_short` adversarial scenarios (`mn_adversarial.py:21-22`).
- The battery results are present and **PASS**: `calibration_summary.json CALIBRATED=true`; `adversarial_summary.json ALL_SCENARIOS_CALIBRATED=true`, **`drift_long fpr05=0.0`, `trend_short fpr05=0.0`**. `PROJECT_AUDIT.md:8` marks **D3 = RESOLVED**.

**Why W9 read "open" — a Red Team documentation defect I am correcting:** W9's verification keyed on (a) the three **original** commit SHAs (still uncontained) and (b) `flow-c-foundation` not merged (literally still true). **Both checks are blind to a cherry-pick** — the fix landed under new SHAs. So the ledger asserted "open on the official line" while the code was in fact present and passing. My entries [29]/[30] additionally **conflated two different objects**: the `code/` engine (fixed) and the Validation Engine's separate `validation_engine/` F6 reconstruction (a *different* test — DC event-cell, not strategy Test B — which genuinely still lacks the flow-c drift-beta mechanism).

**Corrected W9 status — three real residuals survive, the original framing does not:**
1. The passing battery JSONs are **byte-identical to flow-c → cherry-picked, never independently re-run** on the official line. "Validated on statistician-foundation" rests on flow-c's execution, not a fresh one.
2. The **VE's F6/F6.1/F6.2 reconstruction** (`validation_engine/`) is the artifact that lacks the drift-beta control; it is a **different object** and claims only a structural analog. "F6 lacks drift control" is true *of F6*, not of `code/matched_null.py`.
3. **SCOPE CAVEAT (the sharpest, and larger than W9 itself)** — see Target 1-bis.

## TARGET 1-bis — SCOPE GAP: the matched-null is validated ONLY for 1.5×ATR stops; every current SMC candidate uses STRUCTURAL stops
`PROJECT_AUDIT.md:8` (D3 row, verbatim scope caveat): "validated regime = **1.5×ATR stops on generic signals; structural-stop families (the D2 sources) were never in the calibration battery → matched-null is NOT validated for them.**" The calibration/power/adversarial batteries (`mn_*.py`) inject only `risk_kind='atr'` (and one `struct` scenario in adversarial, but the calibration corpus is ATR). **Yet the entire live/DEMO candidate pipeline uses structural stops** — PDH/PDL & session touch-bar extreme, sweep-wick extreme, OB floor, FVG edge (CAND-0001/0003/0007 DEMO pilots included). **The primary alpha test, run on the current candidates, would operate outside its validated domain.** This is not a coding defect; it is a **validity-of-application gap** that no candidate-level verdict can currently rest on soundly.

## TARGET 2 — WP-5′ oracle: validated at a SINGLE large n, no minimum-n, already applied outside its domain (disclosed)
- **Validation scope (verbatim, `MANDATE_5_7_STEP2_wp5_battery.md:34,39-42`):** `block_bootstrap@v1` is validated **specifically for the LM-001 finite-memory overlap null, at n = 21,048, L ≥ H = 20, FPR@0.05** — "Domeniu STRICT al concluziei (nu extrapolez)." **No minimum-n / minimum-number-of-blocks requirement** is stated anywhere; the battery ran at a **single point** n=21,048.
- **Predecessor invalidation persists:** the AR(1) engine is `INVALIDATED_FOR_THIS_SCALE`, and that failure "persistă la 10× cel mai mare punct calibrat — NU e un efect de eșantion finit" — so large-n calibration does **not** license small-n use here.
- **Already applied outside the validated point, by its own authors, with a disclosed warning** (`lm001_s1_execution.py:16-19`): applied **per-regime at n < 21,048** and to **`net_R`** (an extra transform vs the validated horizon-sum series) — "n per-regim < n validat … Raportez p-ul ca INSTRUIT și semnalez scopul — NU ajustez nimic."
- **Statistical reality:** a block bootstrap needs enough blocks. At n≈200, L=20 → ~10 blocks (marginal); at **n=7 (CAND-0023) with L≥20 → zero complete blocks — the bootstrap degenerates entirely.** The current candidate n-distribution spans tens-of-thousands down to **n=7 / 12 / 19** (CAND-0023/0018/0016). **The oracle is valid for the large-n mechanism it was calibrated on and NOT for the small-n per-regime populations it is being pointed at.** RISK, disclosed, not yet load-bearing (Target 5).

## TARGET 3 — FDR correction: BH step-up is CORRECT (not Bonferroni), over two distinct m's
- `scoped_fdr_run.py:87-95 bh_reject`: `if p <= i*ALPHA/M` over rank-sorted p, rejecting all ranks ≤ the largest passing rank. **The k-th smallest p faces `k·α/M`, exactly as the Statistician stated — NOT Bonferroni `α/M` for all.** ✓ Verified at source.
- **Two different m's, kept explicitly separate (both correct, must not be conflated):** the **scoped-FDR grammar M = 412** (ATR-stop-valid legacy hypotheses, `SCOPED_FDR_PREREGISTRATION_v1.0.md:42`) vs the **candidate-family m = 16** (the MK/session production line, `CAND0006…:196-199`). Different corpora, different BH thresholds (p₁≤1.21e-4 at 412; p₁≤0.0031 at 16). Correct as-is; the only hazard is a future reader conflating them.
- **Residual:** plain BH's FDR guarantee needs independence/PRDS; the 412 hypotheses share the **same 60% research segment** (strong dependence). Validity is *argued* (the W-partition removes the sole negative dependence) but the positive-dependence structure is **assumed, not verified**; BY (harmonic) would be the conservative fallback. Flag.

## TARGET 4 — circularity: NONE found in the statistical chain
- Scoped-FDR/pilot split **research 60% / validation 20% / holdout 20% SEALED (never loaded)** — disjoint (`scoped_fdr_run.py:26-27`, `pilot:60-61`). The subset `VALID_IDS` is enumerated from the grammar's `stop` field + frozen n≥25, **committed before any p** (`SCOPED_FDR_PREREGISTRATION_v1.0.md:5,16-18,54`) — **no val/holdout data enters selection; no selection leakage.**
- The matched-null is a **proper permutation null** (random entry timing, same risk-in-ATR profile, forward sim) — causal, no E010-style selection∩measurement window nesting. Exit encodings use entry-time targets, not outcomes. **Clean.** (Contrast the demo engine, where real defects were found — the validation chain's window discipline is sound.)

## TARGET 5 — verdict dependencies: NOTHING is promoted on these engines; the chain fail-closed
- **No candidate is PROMOTED** on matched-null / scoped-FDR / WP-5′. DEMO pilots = `DEMO_BASELINE, NOT VALIDATED`; MK/session = `SCREENING`/archived; PROMOTED requires `global_fdr_status=PASS`, held by none.
- **The single scoped-FDR research survivor (S18 `ce76669a3b2a`) does NOT clear:** OOS validation **p=0.0779 > 0.05** (does not confirm), and it is **`research_worthy=False`** (dd 33.4R > 25R) — two official criteria give opposite verdicts on the same object; routed to certification, **not promoted** (`SCOPED_FDR_RESULT_v1.0.md:12,23,111-112,99`).
- **matched-null/scoped-FDR and WP-5′ are independent engines** (grep confirms no cross-reference); WP-5′'s only consumer is the LM-001 line, **read-only, verdict deferred to the Statistician, no committed result.**
- **So no existing result is invalidated — because none is promoted, and the one near-positive fails OOS.** The validation chain fail-closed exactly as designed.

---

## SEVERITY-ORDERED FINDINGS

### 🔴 DEFECT
**S-D1 · Red Team's W9 record is factually stale (my division's error).** The fix is cherry-picked and present on the official line, byte-identical to flow-c, batteries passing, D3 marked RESOLVED — yet ledger [29]/[30] and the integrity register still assert "W9 open / F6 lacks drift on the official line," conflating `code/matched_null.py` (fixed) with the VE's separate F6 object. **Corrected here and in the register, append-only.**

### 🟠 RISK
**S-R1 · Matched-null validated ONLY for 1.5×ATR stops; every current SMC candidate uses structural stops.** The primary alpha test is outside its validated domain for the actual pipeline. No candidate verdict can soundly rest on it until the calibration battery includes structural-stop families. *(Larger practical exposure than W9.)*
**S-R2 · WP-5′ oracle validated at a single n=21,048, no minimum-n; block bootstrap degenerates at small n** (n=7 → zero blocks). Already applied per-regime at smaller n and to `net_R`, disclosed. Any small-n block-bootstrap p is outside the validated domain.
**S-R3 · Lenient, inconsistent calibration gates.** Adversarial pass = `CI∋0.05 OR fpr05≤0.10` (`mn_adversarial.py:66`) — tolerates **2× nominal**; power FPR-at-zero gate `≤0.15` (`mn_power.py:54`) — **3× nominal**; small N (40/50/120) → **low power to detect miscalibration.** "CALIBRATED"/"ALL_SCENARIOS_CALIBRATED" overstates the guarantee (though the *observed* drift FPRs were 0.0, comfortably inside).
**S-R4 · Production null is UNSTRATIFIED.** `STRATA=None` (`pilot:15`, `scoped_fdr`): controls risk/vol (ATR-scaled) but **not** session/month/regime *timing*; stratified path exists but is "deferred, not separately validated." A regime-timing edge would beat this null. Distinct from W9.
**S-R5 · The whole stack inherits `mstrat.simulate` (C-R3, unattacked).** Both observed and null route through it; if `mstrat` shares the demo-engine entry-bar-stop optimism (RT-CODE-A-0005 D1), calibration could be subtly biased (observed entries are structured, null entries random — the optimism need not cancel). `mstrat` remains the next unexamined dependency.
**S-R6 · BH independence/PRDS assumed, not verified** across same-segment hypotheses (Target 3 residual).

### 🟡 UNDOCUMENTED
**S-U1 · Passing battery results are cherry-picked, never independently re-run on the official line** (byte-identical JSONs) — reproducibility gap.
**S-U2 · Two m's (412 vs 16) unreconciled** — correct but conflation-prone; no single doc states both side by side as distinct denominators.
**S-U3 · `phase1_screening_results.json` (per-candidate n for all 36) is untracked/absent** — the n-distribution can only be read from transcribed doc values; session-batch n's are nowhere tracked.

## WHAT SURVIVES (verified)
BH step-up correctness; research/val/holdout disjointness + no selection leakage; the matched-null as a causal permutation null; the ATR-rescaling drift fix **present and passing** (drift FPR 0.0); adaptive-MC escalation unbiased/conservative; `k<25→p=1.0` fail-closed; **nothing promoted, chain fail-closed** (the one survivor fails OOS).

## VERDICT — **the validation code SURVIVES as correct math, but its GUARANTEES are narrower than the pipeline assumes.**
No verdict-producing defect (unlike the enforcement engine). The real exposure is **domain mismatch**: the matched-null is not validated for the structural stops every candidate uses (S-R1), and the WP-5′ oracle is not validated for the small-n populations it is pointed at (S-R2); the calibration gates that stamp "validated" are lenient (S-R3) and the null under-controls regime timing (S-R4). **Because nothing is promoted and the one near-positive fails OOS, no result is invalidated — but the moment a candidate is put forward for validation, it would be judged by an engine operating outside its validated domain.** That, not a broken calculation, is the accumulated-unverified risk at this end of the chain.

## HANDOFF → Statistician, then CEO
1. **Correct W9** — the code-level fix is present (cherry-picked); the open residuals are the un-rerun results, the VE-F6 object, and (most important) the structural-stop scope gap. *(Register corrected append-only below.)*
2. **S-R1** — before any candidate validation, extend the calibration/adversarial batteries to structural-stop families; until then the matched-null verdict on SMC candidates is out-of-domain.
3. **S-R2** — set a minimum-n / minimum-block requirement for the WP-5′ oracle; small-n per-regime block-bootstrap p's are out-of-domain.
4. **S-R3/S-R4/S-R6** — tighten the calibration pass criteria (2–3× nominal tolerated), decide whether stratified nulls are needed for regime-timing edges, and justify or replace plain BH under same-segment dependence.
5. **S-R5** — `mstrat.simulate` is the next unexamined dependency of the entire stack (C-R3) — attack it before relying on any matched-null number.

Red Team designed no remedy, ran no data, modified nothing outside `red_team/`.
