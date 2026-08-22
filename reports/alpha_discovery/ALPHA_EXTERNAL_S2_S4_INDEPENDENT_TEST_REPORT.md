# ALPHA_EXTERNAL_S2_S4_INDEPENDENT_TEST_REPORT

**Mandate:** `ALPHA-XAUUSD-EXTERNAL-S2-S4-INDEPENDENT-TEST-001` (priority frontier inside the continuous loop) · **Date:** 2026-08-22.
**Final statuses:** `S2_RANGE_BREAKOUT_ALPHA_TEST_COMPLETE` · **`S2_NOT_SUPPORTED`** ; `S4_SWEEP_REVERSAL_ALPHA_TEST_COMPLETE` · **`S4_NOT_SUPPORTED`** ; **`S4_TREND_ALIGNED_SUBFAMILY_NOT_SUPPORTED`**.
**Discipline:** rules formalized and FROZEN before results (`EXTERNAL_RULE_MAPPING.md`); external win-rates (S2 ~52%, S4 ~67%, "9/9") treated as **non-evidence** and **not reproduced** (§21, §36); no definition altered to reach profitability (§36); price-only; no news/M1/exogenous; no non-causal D1/H4 merge. Alpha does not self-ratify (moot — no survivor).

---

## 0. Headline
- **Both external strategies are NOT_SUPPORTED** under project standards. The faithful frozen formalizations are **adverse-first dominated** (S2 advFirst 0.72–0.89; S4 0.84–0.91) with best-5/10%-removed negative, never all-years-positive, DISC/CONF negative.
- **S2:** gold **false-breaks** these close-based boxes; the external *free-path* and *volume* increments make it **worse**, not better.
- **S4:** sweeps/reclaims **fail** (get swept further / run over). The predeclared **"golden pattern" trend-aligned subfamily is the WORST** cell — refuting "9/9". `+1-bar delay` degrades every cell; invalidation-exit does not rescue.
- No survivor to freeze; per §38 both are graveyarded with lessons, and the continuous loop **continues**.

## 1. External-rule mapping & deterministic specs
Full frozen mapping in [`EXTERNAL_RULE_MAPPING.md`](EXTERNAL_RULE_MAPPING.md). Every ambiguous clause resolved with the *simplest faithful* interpretation and frozen before any outcome inspection. Implementations: [`s2_test.py`](s2_test.py), [`s4_test.py`](s4_test.py), [`external_common.py`](external_common.py) (path-first engine). `swing_base.py` imported read-only (COMP-CONT-L fingerprint preserved).

## 2. Data identity & causality audit
- **Population:** gated native M5 (`edge_research._common.load`, file_sha `cbb6eebe…`, manifest 2.7.94) -> M15/H1/H4/D1 causal aggregation. **DEV 2021-07-27..2023-12-29** selection; CALIB untouched here (not needed — nothing survived to robustness-test). No 2025+/N4/V1/protected-2024/exogenous.
- **Causality:** entry = next-bar OPEN (no same-bar hindsight fill); boxes/levels from PRIOR bars (rolling `.shift(1)`); HTF context via last-completed-bar `close_time <= signal.time` (**no non-causal D1/H4 merge** — the Statistician-flagged lookahead path is NOT used); stop wins same-bar ties (conservative). Leak assertions pass (no bar >= 2025).
- **Not testable (disclosed):** `M1_CONFIRMATION_NOT_TESTABLE` (finest authorized = M5); `HVN_NOT_RECONSTRUCTED` (no causal HVN -> free-path uses prior opposing swing structure instead); `NEWS_FILTER_NOT_INCLUDED_IN_PRIMARY_PRICE_ONLY_TEST`. Volume = aggregated-M5 (tick-based), tested only as an increment and disclosed.

## 3. S2 — RANGE BREAKOUT results (24 frozen configs: H1/H4 × {body_env, close_ext, close_iqr} × L/S × entry-A/B)
- **Path-first (§11, §29):** median MFE ≈ median MAE; **adverse-first 0.72–0.89**; **P(+1R before −1R) ≈ 0.40–0.52**. Gold **mostly false-breaks** these boxes — the core question answered negatively.
- **Economics (STRESS):** avgR negative in ~all cells at RR1.0 (−0.06 to −0.30); occasional marginal RR1.5/2.0 positives (best: H4 body_env L rr1.5 +0.155) are **tail-carried (best-10%-removed −0.10 to −0.45)**, **never all-years-positive**, DISC/CONF negative. Fails the frozen gate everywhere.
- **Incremental conditions add NO value:** free-path filter → **worse** (`+free` more negative); 1.3× volume → **worse** (`+vol` more negative). Retest entry (B) is occasionally less-bad than breakout (A) but **lowers frequency without creating an edge**. Larger-TF (H4) boxes have better MFE/lower advFirst than H1 but remain negative.
- **Natural geometry:** median SL H1 ~24–41p, H4 ~47–99p (H4 body_env B ~99p is in-band but negative).
- **Verdict:** `S2_NOT_SUPPORTED`. Close-based box construction does not beat the noise; breakout-close entry does not work; retest/volume/free-path do not rescue.

## 4. S4 — SWEEP REVERSAL results (3 level defs × L/S × {BASE, +quality, anti-fade, TREND-ALIGNED})
- **Levels (causal, ≥1 day):** PDH/PDL (D1), H4 10-bar swing, H1 24-bar hi/lo. Raw sweep+reclaim signals plentiful (1.1k–1.6k/side) → deduped to N≈100–690.
- **Path-first:** **adverse-first 0.84–0.91**; P(+1R before −1R) ≈ 0.43–0.58. Reclaims **fail** — price sweeps further / runs the reversal over.
- **Economics (STRESS):** avgR negative in essentially every cell (−0.02 to −0.29); **best-5/10%-removed negative everywhere; never all-years-positive; DISC/CONF negative.** Median SL 13–20p (tight — the sweep-extreme+$0.50 stop is small, so noise-stopped).
- **Execution overlays (§16, §25, §26):** `+1-bar delay` **degrades** every cell (external delay-sensitivity confirmed, but no base edge to protect); `INVALIDATION` (M5 close back beyond sweep extreme) does **not** rescue; reclaim-`+quality` (upper/lower third) marginally less-bad but still fails the gate. **No overlay rescues a negative parent (§26 honored).**
- **Least-bad cell:** H4_swing SHORT +quality rr1 +0.029 — but best5 −0.02 / best10 −0.07, not all-years-positive, +1bar −0.075 (delay-fragile). **Not a survivor.**
- **Verdict:** `S4_NOT_SUPPORTED`.

## 5. S4 TREND-ALIGNED "golden pattern" (predeclared subfamily, §20)
- Tested exactly as predeclared (sweep against D1 direction → reclaim → enter WITH causal D1 trend; L/S separate; no non-causal merge). Result: **the trend-aligned subfamily is the WORST subfamily in every level variant** — LONG rr1 −0.275/−0.275/−0.285, SHORT rr1 −0.291/−0.153/−0.183; DISC/CONF strongly negative; advFirst 0.88–0.91.
- Economic reading: "sweep support in an uptrend then long" is buying a dip that frequently continues down first; "sweep resistance in a downtrend then short" gets run over. The external **"9/9" claim is not reproducible** and is consistent with small-sample selection (ignored as evidence per §21).
- **Verdict:** `S4_TREND_ALIGNED_SUBFAMILY_NOT_SUPPORTED`.

## 6. Frequency (§33) & portfolio overlap (§34)
- Raw frequency was ample (S4 tpm 5–31; S2 hundreds of DEV events) — **frequency was never the binding constraint; robustness was.** Neither strategy is weakened to chase frequency (§33 honored).
- **Portfolio overlap:** N/A — no survivor. Nothing to compare against S5 / COMP-CONT-L / H4-bo-raw-S. (§35: S2 and S4 kept separate; not combined.)

## 7. Limitations (bounded, §37)
- M1 breakout-strength and news filters untestable/excluded — the *supplied* strategies partly depend on data outside the authorized price-only scope; the price-only parents (which the mandate required regardless, §6/§23) have no edge, so the missing components cannot be the sole load-bearing element unless they carry the entire edge (untestable here).
- Volume tested only as aggregated-M5 (tick) increment; it did not help.
- Conclusions bounded to the 2021-2023 DEV population and these frozen formalizations — **not** a universal-impossibility claim (§37). (The frozen SHORT `H4-bo-raw-S` shows a breakdown edge *can* exist on a different, older population.)

## 8. Final verdict
| strategy | status |
|---|---|
| **S2 RANGE BREAKOUT** | `S2_NOT_SUPPORTED` — false-break dominated; free-path & volume add negative value |
| **S4 SWEEP REVERSAL** | `S4_NOT_SUPPORTED` — reclaims fail; noise-stopped; overlays don't rescue |
| **S4 TREND-ALIGNED (golden)** | `S4_TREND_ALIGNED_SUBFAMILY_NOT_SUPPORTED` — worst subfamily; "9/9" not reproducible |

Per §38: both graveyarded with lessons; no freeze; **continuous loop continues immediately.** No parameter rescue, no reinterpretation, no MI/S5/frozen-strategy change; broker disabled; DEV-only; firewall intact.

**Terminal:** `S2_NOT_SUPPORTED` · `S4_NOT_SUPPORTED` · `S4_TREND_ALIGNED_SUBFAMILY_NOT_SUPPORTED` · loop remains `ALPHA_CONTINUOUS_RESEARCH_ACTIVE`.
