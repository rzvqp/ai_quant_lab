# WAVE_1_CLAUDE_CODEX_REVIEW — implementation review of the Wave-1 harness (pre-run)

Branch `wave1-execution`. Reviewed artifacts: `code/wave1_harness.py`, `code/run_wave1.py`,
`tests/test_wave1_harness.py`, against the FROZEN engine (`mstrat.py`, `mstrat_ext.py`, `matched_null.py`)
and the FROZEN spec (`knowledge/experiments/WAVE_1_SPEC.md`). Review completed BEFORE the full run.

## 0. Roles (per WAVE1_HANDOFF)
- **Claude** = methodology guardian: harness/driver correctness, claim limits, mechanism-vs-execution separation.
- **Codex** = semantic-equivalence, leakage, placebo, multiplicity, tabular checks.

## 1. Codex status — PARTIAL (filesystem stale, as documented)
- A full filesystem review was attempted via the Codex MCP server (read-only, cwd = repo root). **The session
  TIMED OUT** before returning — consistent with the standing PROJECT_AUDIT status "CODEX FILESYSTEM REVIEW
  PENDING (its MCP sandbox is stale; all Codex reviews so far are INLINE)". So the filesystem-level Codex review
  remains PENDING and is NOT counted as independent verification of the whole tree.
- A **lightweight INLINE Codex check** (no filesystem; two snippets pasted) DID return and is recorded below.
  This is the inline fallback the handoff prescribes; its scope is limited to what was pasted.

### Codex inline findings (verbatim summary)
1. **Placebo directional logic (A):** the upper-tail p `P(shuffled ≥ real)` is the *correct* one-sided statistic
   for "real > shuffled" (no sign error). **BLOCKER raised:** the mapping `p > 0.5 ⇒ CONTRADICTS CLAIM` is too
   strong — `p > 0.5` means "no support / real below the null median", NOT formal evidence the level is spurious.
2. **Holm-Bonferroni (B):** confirmed CORRECT step-down: factors `(m−r) ≥ 1` guarantee adjusted ≥ raw, and the
   ascending-rank running-max enforces monotonicity. No issue.

### Resolution of the Codex BLOCKER (applied before the run)
- `label_shuffle_placebo` now also returns the **lower-tail** p `p_low = P(shuffled ≤ real)`.
- `decide()` placebo branch now emits **CONTRADICTS CLAIM only if `p_low < 0.05`** (real *significantly worse*
  than the placebo — the level identity actively hurts). Otherwise a non-supporting result is **NO DIFFERENCE
  DETECTED**, not CONTRADICTS. Unit tests still 10/10. This is a strictly more conservative claim policy.

## 2. Claude methodology review — findings

| sev | area | finding | disposition |
|---|---|---|---|
| — | **leakage** | `load_segments` returns only research `[:a]` (a=int(n·0.6)) and OOS `[a:b]` (b=int(n·0.8)); the terminal holdout `[b:]` is never constructed, never passed to any setups/simulate/matched-null call. `test_no_holdout_leak` asserts `len(res)+len(val)==b`. Features are backward-looking (rolling/ewm), so slicing after `MS.load()` introduces no lookahead — identical to `run_full_campaign.py`. | **OK / holdout SEALED** |
| — | **no parallel backtester** | Every arm's per-trade R is produced by `MS.simulate` (via `sim_R`) or by `MN.matched_null_p` (which itself calls `MS.simulate`). `metrics_R` computes only summary stats on R vectors. Entry-price/delay in the decomposition are for REPORTING only, never feed R. | **OK** |
| — | **parity** | `sweep_setups(confirm=True)==MS.s1_setups` and `cont_setups(gate=True)==MSX.s39_setups` are asserted byte-for-byte (si,ei,dir,stop,exit_kind,exit_param) in the tests. Control arms therefore differ in EXACTLY one dimension (the toggle). | **OK / parity-locked** |
| MINOR | **EXP-01 primary interpretation** | The paired primary contrast (confirmed vs raw on the identical confirmed-event universe) bundles confirmation's *timing* components (entry delay + entry-price shift + exposure) — it is NOT a pure confirmation-as-filter test. This is the faithful reading of the spec's H0 ("confirmed ≤ raw on the identical signal set"). The *selection* component is reported separately (`raw_all` vs `raw_confirmed_only`). Report must state this and NOT claim simple causality (CEO directive). | **carried into report** |
| MINOR | **EXP-01 exposure** | Holding time per trade is not measured: `MS.simulate` returns `(R, si, ei)` only; the exit index is not exposed by the frozen engine. Reported as an explicit limitation rather than instrumenting the engine (out of scope; would touch a frozen file). | **documented limitation** |
| MINOR | **EXP-02 null conservatism** | The gate-ON trades are members of the pool the null samples from (random size-n_on subsets of the whole executed universe). This makes the test slightly *conservative* (the good trades are in the null pool), which is acceptable for a "does the gate beat random selection" question. | **acceptable, noted** |
| MAJOR | **EXP-03/04 stratified null not calibration-validated** | The beta/regime-matched null uses `matched_null_p` with a session×vol×trend composite stratum. Only the *unstratified* config passed the matched-null calibration/power/adversarial battery; the stratified config is NOT separately validated. Therefore EXP-03/04 are **DIAGNOSTIC-grade**, and the validated unstratified null is reported alongside as an anchor. The caveat is embedded in the result record. | **caveated; status capped** |
| MINOR | **EXP-03/04 single-direction reps** | The pre-registered representatives are single-side (S1 side=low=long; S5 side=up=long). The opposite side is reported as `side_mirror` so "long and short reported separately" is honoured, but the primary p is the representative side only. | **documented** |
| MINOR | **frozen `matched_null.py` multi-strata latent bug** | Passing a multi-column strata list to `matched_null_p` crashes (equal-length key tuples collapse to a 2-D ndarray → unhashable). NOT triggered by the pilot (strata=None). Worked around WITHOUT modifying the frozen module by passing a single composite `strat_combo` column (routes through the hashable len==1 branch). Flagged for a future frozen-engine fix (out of Wave-1 scope). | **worked around; logged** |
| MINOR | **placebo residual identity** | The donor-transplant placebo occasionally draws a nearby day whose level coincides with a genuine nearby level (partial identity retention). With `window_days=30` on daily levels this is rare and only *weakens* (never inflates) a positive placebo result. | **noted** |
| — | **multiplicity** | ONE Wave-1 Holm-Bonferroni across the 6 primary p's; global S1–S51 FDR NOT applied (`bh_fdr` is reported as a secondary q=0.10 view only). Holm verified correct (test + Codex). | **OK** |
| — | **status vocabulary** | `decide()` returns only the allowed set; `run()` asserts membership. "VALIDATED ALPHA / PRODUCTION READY / FINAL STRATEGY" are never emitted. | **OK** |

## 3. Verdict
- **SHIP for the frozen run**, with the MAJOR caveat (EXP-03/04 stratified null = diagnostic-grade) and the two
  MINOR interpretation notes (EXP-01 timing-vs-filter; placebo residual identity) carried explicitly into
  `WAVE_1_EXECUTION_REPORT.md`.
- The one Codex BLOCKER (placebo CONTRADICTS mapping) was fixed before the run.
- Codex FILESYSTEM review remains PENDING (sandbox stale) — this review is Claude-led with an inline Codex
  cross-check on the two highest-risk logic bits. Recorded as a known verification gap.
