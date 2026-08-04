# RED TEAM — CODE ATTACK · Level-2 H1 bias factors
### RT-CODE-A-0011 · Target: `code/bias_h1.py` @ `81a0a62` (discovery-mk-matrix-v1)
**Date:** 2026-08-04 · **Auditor:** Red Team · **Spec:** STAT-LEVEL2-BIAS-H1-SPEC-v1.0 (`1b2933c`, manifest v2.7.51). Level 2, step 3. Checklist only: lookahead, leakage, circularity, ambiguity, overfitting, hidden params, reproducibility. **No data run · nothing modified · no remedy.** Numeric verification on synthetic H1 (module + deps imported read-only from branch).

## VERDICT — **PASS_WITH_LIMITATIONS.**
The emitted factors are **causal (proven — stricter than required)**, overfitting-free, fully-parameter-disclosed, reproducible; the vocabulary restriction loses nothing legitimate; the second redundancy tier **does** catch the injected displacement edge. **But the falsifiability metric `zero_eligible_fraction` is computed with LOOKAHEAD and materially OVERSTATES falsifiability — the number that justified admitting the liquidity factor is wrong as computed** — and, as the spec itself concedes, none of the four factors is independent of what the candidates trigger on.

---

## CHECKLIST

**Lookahead — PASS, PROVEN (and stricter than the spec requires).** `compute_bias(…, i)` slices every series to `[0, n_avail)` with `n_avail = min(i, len)`, so bar `i` is physically unreachable; factors read only the last CLOSED bar `i-1`. **Numeric proof:** scrambling every bar `≥ i` to a sentinel leaves **all factors + `zero_eligible_fraction` identical** → the output is a function of `[0,i)` alone. Non-lookahead by construction, not convention. ✅

**Leakage — FAIL (in the falsifiability DIAGNOSTIC; the emitted factor is clean).** The `zero_eligible_fraction` loop builds `pools = _unswept_above_pools(...)` **once on the full `[0,i)` window** — excluding every pool swept *anywhere* up to `i-1` — then reuses that set at each historical bar `j`. A pool swept **after** bar `j` is therefore dropped from bar `j`'s eligibility count, which **cannot be known at `j`**. Effect: eligible counts at earlier bars are understated → the zero-fraction is **overstated**. **Measured (synthetic):** code `zero_frac = 0.978` vs a causal per-bar recompute (`pools` unswept as-of-`j` only) `= 0.801` — **~18 points too high.** The **emitted factor** (`liquidity_above` at `i-1`) is causal and correct (sweeps up to `i-1` are known at `i-1`); **only the diagnostic leaks** — but that diagnostic (§7.2) is the *entire justification* for admitting the factor, so **the reported "99.21% zero → falsifiability restored" is overstated and must be recomputed causally.** (B-L1.)

**Circularity — disclosed by the spec, confirmed.** "Zero dintre cei patru factori sunt complet independenți de primitivele pe care candidații declanșează; singura axă genuin independentă rămâne ȘTIRILE." `structure_run_h1` is the **same `detect_breaks` run** used by Level 1 and by the structure candidates (verified via the redundancy map: `detect_breaks/detect_swings/build_pools/detect_sweeps` all map to gen_cand0020-0025). So the factors are redundant-by-construction with the candidates they would condition; only NEWS (absent here) is independent. (B-L2.)

**Ambiguity — minor (B-U1).** The INJECTED attribution is coarse: it labels `"MODULE_LEVEL_INJECTED:all_gen_cand_receiving_it"` without identifying *which* generators receive the value.

**Overfitting — PASS.** `K_ATR = 1.0` is the v2.7.41-ratified value **reused, not chosen here**; `DAY_H1=23`/`WEEK_H1=115` are **measured** (23.08/115.30), not transplanted; the docstring explicitly forbids tuning `k` to pass the criterion ("nu se ajustează `k` … asta ar fi tuning").

**Hidden params — PASS.** Every constant named with provenance; the `schema_payload` pre-registers the ordered factor list + primitives + thresholds + windows for the `schema_hash`.

**Reproducible — PASS.** Deterministic; `ratified_vocabulary()` derives from module introspection (survives module changes); the 66.39% Level-1 agreement reproduces the Statistician's figure (per VE); 24 tests + mypy.

## SPECIFIC TARGETS

**T1 — a factor active on <1% of bars: factor or decor? (with the reverse)** The reported 99.21%-zero (→ <1% active) is **inflated by B-L1**; causally the factor fires materially more (my synthetic: ~20% non-zero, not ~2%). So it is **not decor** — and the leakage *understated* its coverage. Even on the zero bars, "0 eligible pools above" is a real state (no near unswept liquidity), not absence. **The useful range** is firing neither ~0 (rare/low-coverage) nor ~1 (saturated/no-discrimination); the *reported* 0.79% sits at the rare edge, but the **causal** coverage is inside the useful band. So: a legitimate factor whose true coverage the leakage hid — recompute causally before judging its worth.

**T2 — other edges lost the same way? does the second tier catch all?** The second tier **works on the known mechanism**: `expansion` (injected into `gen_cand0002/0008/0009` as a parameter, invisible to intra-function inspection) is correctly flagged **`INJECTED`** — verified. **But it is a coarse heuristic, not a proof of completeness:** (a) it attributes to "all_gen_cand_receiving_it" by *name presence at module level*, **without verifying the value actually flows into a generator** → it can **over-attribute** any ratified primitive called at module level for an unrelated reason; (b) it inspects only the two given files → it is **blind to cross-module injection** (a runner in a third module) and to **indirect dispatch** (`functools.partial`, `getattr`, function tables). So it catches **the ones searched for** (same-module module-level calls), not provably **all** lost edges.

**T3 — does the vocabulary restriction drop anything legitimate?** No (verified): functions IN (`detect_breaks/expansion/build_pools/atr14/detect_sweeps/detect_swings`), data-structures OUT (`Block/PoolSide/BreakKind/LiquidityPool/PoolTier`). Excluding classes (else "all candidates use blocks → all redundant", a true-but-vacuous warning) and re-exports is correct, and nothing legitimate among the current **plain-function** primitives is lost. **Limitation (B-U2):** `inspect.isfunction` would also drop a ratified primitive ever exposed as a **callable class / `staticmethod` / `partial`** — none exist today, so not future-proof but currently clean.

**T4 — is the 95% non-redundancy threshold an anchor or a convenience? at 66% agreement, info or resolution noise?** 95% is a **declared convenience cutoff** (like Level-1's equal-occupancy), not a derived boundary. At **66.39%** agreement, `structure_run_h1` is the **same `detect_breaks` mechanism at a finer resolution** (H1 vs the Level-1 H4) — so the 34% disagreement is a **resolution difference of one mechanism, not an independent axis**. The agreement rate **cannot by itself** separate information from resolution-noise; that requires a Level-6 **incremental-value** measurement. So the 95% rule **passes** the factor, but its marginal value over Level-1 structure is **unquantified** (may be resolution noise) — consistent with the spec's own concession that only NEWS is independent.

## SEVERITY
- 🟠 **B-L1 · Lookahead in the falsifiability metric** — `zero_eligible_fraction` reuses end-of-window unswept pools at earlier bars, overstating the zero-fraction (97.8% vs 80.1% causal, ~18 pt). The emitted factor is clean; the **justification metric** is not. Recompute causally before relying on "falsifiability restored."
- 🟠 **B-L2 · Redundancy/circularity by construction** — none of the four factors is independent of the primitives candidates trigger on (`structure_run_h1` = the same `detect_breaks` at H1 resolution, 66% Level-1 agreement); only NEWS would be independent. Non-redundancy passes at 95% but marginal value is unquantified.
- 🟡 **B-U1 · Second redundancy tier is coarse & incomplete** — catches same-module injection (works on `expansion`), but attributes without dataflow and misses cross-module/indirect injection.
- 🟡 **B-U2 · Vocabulary restriction not future-proof** — a ratified callable-class/partial primitive would be silently dropped (none today).
- 🟡 **B-U3 · 95% is a convenience anchor** — the info-vs-resolution-noise question is deferred to Level-6 incremental value.

## WHAT SURVIVES (verified)
Lookahead-free by construction (proven, stricter than required); factors-not-probability correctly separated (the four are FACTORS; probability is Level 6's); overfitting-free (K_ATR reused, windows measured, no k-tuning); all params disclosed + schema pre-registered; reproducible (Level-1 agreement reproduces the Statistician); vocabulary restriction loses nothing legitimate; the second tier successfully surfaces the injected displacement edge that static inspection had been blind to.

## HANDOFF → CEO / Statistician
1. **B-L1 (highest):** recompute `zero_eligible_fraction` causally (per-bar unswept-as-of-j); the "99.21% → falsifiability restored" figure that admitted the liquidity factor is overstated as computed. The factor value itself is causal — only the metric needs recomputing.
2. **B-L2/B-U3:** the four factors are not independent of the candidates; before crediting `structure_run_h1`/`displacement_h1`, measure their Level-6 **incremental** value over Level-1 (agreement rate ≠ information).
3. **B-U1/B-U2:** the redundancy inspection is a good mechanical improvement but is not sound-and-complete — treat its INJECTED flags as coverage of the *known* mechanism, and its vocabulary as function-only.

Red Team designed no remedy, ran no data on the market, modified nothing outside `red_team/`.
