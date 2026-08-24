# VE_CURRENT_REGIME_TEMPORAL_CAUSALITY_REPAIR_REPORT

**Mandate**: `VE-CURRENT-REGIME-TEMPORAL-CAUSALITY-REPAIR-001`
**Repo / branch**: `ai_quant_lab-alpha-automation` / `alpha-automation-v1`
**Source audit**: Statistician independent review `STAT-CRS1-INDEPENDENT-REVIEW-FDR-001`, commit `4163382`,
branch `statistician-foundation` — read in full before this repair began, not accepted from summary alone.

> **VERDICT: `CURRENT_REGIME_CAUSAL_INFRASTRUCTURE_PASS` / `READY_FOR_ALPHA_EXACT_CAUSAL_REPLAY`** — see
> section 8 for the full requirement-by-requirement evidence.

## 1. Root cause (confirmed by direct code inspection)

`reports/alpha_discovery/cur_screen.py::like_at`:

```python
def like_at(times):
    _,LK=_load(); h4=(np.asarray(times,np.int64)//14400)*14400
    return np.array([bool(LK.get(int(t),False)) for t in h4])
```

`times` are M15 entry timestamps. `h4 = floor(times/14400)*14400` computes the **START** of each entry's
own H4 bucket (14400s = 4h), and looks up a `like` boolean keyed by that same start in `LK` (loaded from
`__cur_cache__/current_like_h4.parquet`, built by `sig_build.py`).

Traced `sig_build.py::descriptors()`: `vol_norm`, `vol_rel`, `effic`, `ddfh`, `ret60` **all depend on the H4
bucket's own `close`** (directly, or via `atr`/`atr_ma`/`effic` fields computed through that bucket's own
row). The `like` flag at bucket-start `T` is therefore only truly knowable once that bucket **closes**, at
`T+14400`. Confirmed via `cur_data.py::agg()`: `h4["time"]` is unambiguously the bucket's own **start**
(a separately-computed `close_time` field, `= time + 900` past the last M15 sub-bar's own open, proves the
codebase itself already distinguishes the two — `sig_build.py` indexes its output by `time`, not
`close_time`).

**Consequence**: any M15 timestamp `t` in `[T, T+14400)` — i.e. essentially every M15 bar inside the
bucket — was mapped to a label that, from that bar's own point of view, depended on data up to 240 minutes
in the future. Statistician measured 100% of tested entries affected, median lookahead ≈135min, max 240min.
This exactly matches direct code inspection: the bug is unconditional, not probabilistic — every entry
except the rare one landing in the final M15 sub-bar of a bucket sees at least some forming-bar dependency,
and the vast majority see the *entire* bucket's worth.

**Materiality, reproduced from the Statistician's own report** (not re-derived — cited for completeness):
correcting only the alignment (every frozen constant untouched) collapsed CRS-1 from N=298 avgR=+0.4507
(PF 1.87, best10%-removed +0.279, raw p=3.17e-08) to N=267 avgR=+0.0669 (PF 1.10, best10%-removed -0.148,
raw p=0.243). 85% of the apparent edge was the lookahead itself.

## 2. Frozen state (per mandate §1 — no historical artifact overwritten)

Recorded, not rewritten into any prior report:

```
CURRENT_REGIME_CR1_CR15_TEMPORAL_LEAK_CONFIRMED
CRS1_INVALIDATED
CURRENT_REGIME_SURVIVOR = 0
```

All CR-1 through CR-15 evidence that depends on `cur_screen.like_at` (or an equivalent affected pattern,
see §4) is `REVALIDATION_REQUIRED`. `ALPHA_CRS1_H4DIV_FADE_FROZEN.md`, `ALPHA_CURRENT_REGIME_RESCREEN_
LEDGER.md`, and every `cur_cr*.py` script are left byte-unmodified by this mandate except the one shared
dependency being repaired (`cur_screen.py`) and its own data substrate (`cur_data.py`) — both infrastructure,
neither a strategy definition.

## 3. The fix (infrastructure only — no semantic/economic value touched)

Two files changed, both pure timestamp-alignment infrastructure:

**`cur_data.py`**: added `TF_SECONDS` (a named constant replacing an inline dict already duplicated once)
and the single canonical function `causal_bucket_asof(times, bucket_starts, tf)` — full contract and
rationale in `ALPHA_CURRENT_REGIME_CAUSAL_CONTRACT.md`. Uses a proper backward-asof search (`np.searchsorted`
over `bucket_starts + TF_SECONDS[tf]`), not fixed-offset arithmetic — a fixed one-bucket-back shift was
tried first and found to silently discard valid information across every session/weekend/holiday gap
(5,352 of 355,696 M15 bars, 97% at the Sunday reopen — full detail in the contract doc). The asof form was
cross-validated to exactly reproduce this codebase's own already-established, independent correct
convention (`cur_cr13_trade.py`'s `h4_up_map`, `merge_asof(..., direction="backward")` on `close_time`)
across the complete 355,696-bar canonical history — zero divergence.

**`cur_screen.py`**: `like_at` now calls `CD.causal_bucket_asof(times, _LK_STARTS, "H4")` instead of the
floor-only formula; `_load()` additionally caches the sorted array of available H4 bucket-start timestamps
(`_LK_STARTS`) once, alongside the existing `_LK` dict, so repeated `like_at` calls don't re-sort.

**Not touched by this repair**: `sig_build.py` (the `like` computation itself is legitimately backward-
looking FROM EACH H4 BAR'S OWN PERSPECTIVE — using a bar's own close to describe THAT bar is not a
causality violation; the violation was entirely in how `cur_screen.py` looked that value up from a
DIFFERENT, finer-grained timestamp). Every frozen strategy rule, RR, stop, target, threshold, dedup,
session window, or regime-economics claim in every `cur_cr*.py` file — none of that logic was read for the
purpose of modifying it, only (where relevant) to confirm it depends on the now-fixed `like_at`.

## 4. Blast radius

Independent audit (separate investigation, cross-checked against direct reading of the key files below)
covering both `ai_quant_lab-alpha-automation` and `ai_quant_lab-alpha-discovery`. Method: traced every
caller of `cur_screen.like_at` (direct and indirect via `rescreen()`), grepped both repos for any
independently-duplicated `(t//14400)*14400`/`(t//3600)*3600`-style bucket-floor-then-lookup pattern, and
read `market_mode.py` plus its own 9 downstream consumers.

| Artifact | Code path | Affected | Reason |
|---|---|---|---|
| `cur_screen.py` | `like_at()` | **YES — root cause, now fixed** | See §1/§3. |
| `cur_cr2.py`,`cur_cr3.py`,`cur_cr3_trade.py`,`cur_cr4.py`,`cur_cr5.py`,`cur_cr6.py`,`cur_cr6_trade.py`,`cur_cr7.py`,`cur_cr8.py`,`cur_cr9.py`,`cur_cr10.py`,`cur_cr11.py`,`cur_cr12.py`,`cur_cr13.py`,`cur_cr13_trade.py`,`cur_cr13_verify.py`,`cur_cr13_robust.py`,`cur_cr14.py`,`cur_cr15.py` (19 files) | `from cur_screen import like_at`, called directly on entry timestamps | **YES — inherited, now fixed** | Confirmed: none reimplement the arithmetic locally (the literal `14400`/`3600` bucket-width appears in `cur_data.py` only); all call the one shared function, so all 19 are repaired simultaneously by the single fix, not 19 separate edits. |
| `cur_verify.py`,`cur_info.py`,`cur_info2.py`,`cur_info3.py` (4 files) | same direct `like_at(...)` call pattern | **YES — inherited, now fixed** | Same as above. |
| `cur_p4.py`,`cur_p5.py`,`cur_p6.py`,`cur_p7.py` (4 files) | do not import `like_at` by name — call `cur_screen.rescreen(...)`, whose own body calls `like_at` internally | **YES — inherited (indirect), now fixed** | Confirmed by reading `rescreen()`'s own body; a name-only grep for `like_at` would have missed these. |
| `cur_p8.py` | `downtrend_short()` | **NO** | Pure M15-native rolling 20-day-MA regime with `.shift(1)` — no H4 aggregation or bucket join of any kind, despite the similar filename. Confirmed by reading the function; replayed anyway (§7) for completeness, its own numbers are unchanged by this repair since it was never affected. |
| `cur_regime.py` | `label_h4()`, `main()` | **NO (currently) — disclosed watch item** | Its own H4 descriptors have the same "needs the bucket's own close" shape as `sig_build.py`, but the file never joins the label back to a finer-grained timestamp — `main()` only prints H4-indexed population stats. No defect is exercised because no cross-timeframe join exists yet here. Flagged for re-audit if any future screen consumes this output directly — not silently cleared. |
| `market_mode.py` | `mode()` | **NO by itself** | Same "needs own bar's close" shape, but never performs the cross-timeframe join itself — safety depends entirely on the caller. |
| `displacement_info.py`,`liquidity_cont.py`,`liquidity_event.py`,`s18_session.py`,`s2_failbreak.py`,`s2_trade.py`,`s4_compexp.py`,`s4_hold.py`,`s4_verify.py` (9 files) | route `market_mode.mode()` through `align_mode()`→`hist_data.align_causal`/`hist_m15_data.align_causal`/`swing_base.align_context` | **NO** | All 9 confirmed to use the safe `close_time`-gated searchsorted/`merge_asof` join; `hist_data.py` additionally hard-asserts a `"CAUSAL VIOLATION"` if it's ever wrong. |
| `bull_xscale_long.py`,`accept_above_long.py`,`sweep_reversal.py` | `d1_trend_map()`; `cur_cr13_trade.py`'s own `h4_up_map()` | **NO** | Both D1 and H4 context arrive via the safe `merge_asof`/`close_time` helpers — notably `cur_cr13_trade.py` itself contains BOTH the affected `like_at` call and this safe, independent H4-trend join in the same file (§1). |
| `acquisition_staging/generate_htf_context.py` | data-prep for raw H1/H4/D1 CSVs | **UNCLEAR, leans NO — disclosed, not exhaustively resolved** | Bucket-start-keyed output, no `close_time` column; its one known consumer (`hist_data.py`) derives causality independently and safely, but not every conceivable reader of these CSVs was traced. |
| `ai_trader/scoring_engine/tests/test_components.py` | `test_range_regime_is_neutral()` | **NO — false positive on search** | An unrelated `regime: "RANGE"` string literal on a scoring-engine test fixture; different subsystem, no timestamp logic. |
| `ai_quant_lab-alpha-discovery` (whole repo) | — | **NO** | No `cur_screen`/`cur_data`/`sig_build`/`market_mode`/`like_at`/`RANGE_REGIME` reference and no bucket-floor-then-lookup pattern anywhere in the repo. |

**28 artifacts total inherited the exact same defect through the one shared function** (`cur_screen.
like_at`): the root cause plus 27 direct/indirect callers. All 28 are repaired simultaneously by the single
fix in §3 — not by 28 separate edits — because none of them duplicated the alignment arithmetic locally.
**Zero independently-duplicated instances of the unsafe idiom were found anywhere in either repo.**

**Structural finding worth recording**: this codebase already consistently used exactly two cross-timeframe
join idioms before this repair — one safe (`merge_asof(...,direction="backward")` on `close_time`, or the
equivalent `align_causal`/`align_context` searchsorted-on-`close_time`), used correctly in ~25 other files
across the RANGE_REGIME_V1 program, the 6-regime taxonomy, and the older `liquidity_event`/
`displacement_info`/`s2`/`s4` family (§6) — and the one unsafe raw-dict-keyed-by-bucket-start idiom, which
occurred in exactly one place (`sig_build.py`'s cache + `cur_screen.like_at`) before this repair. The defect
was isolated, not systemic; the blast radius is wide only because many files legitimately share that one
function, which is exactly why fixing it once (§3) rather than patching each caller closes the whole class.

## 5. Fail-closed regression tests (mandate §5)

`test_cur_causal_alignment.py`, 14 tests, all passing, runnable directly or under pytest:

| Required case | Test(s) |
|---|---|
| M15 at H4 bucket start | `test_01` |
| M15 inside H4 bucket | `test_02`, `test_07` (exhaustive, every M15 instant across 400 buckets) |
| M15 immediately before H4 close | `test_03` |
| M15 exactly at/after H4 close | `test_04`, `test_05` |
| Day boundary | `test_08` |
| Week boundary | `test_09` (also the gap-carries-forward case that motivated the asof redesign) |
| No M15 decision can access the forming bucket | `test_07` (exhaustive invariant: resolved bucket's own close must be `<= t`, and resolved bucket must never be the one containing `t`) |
| Regression coverage for the exact Statistician counterexample | `test_22` (an M15 entry inside a real historical bucket must return the PRIOR bucket's flag via the actual `like_at` call, never its own bucket's not-yet-closed flag) |

Two additional tests not explicitly required but directly relevant: `test_10` (contract holds for H1 too,
not just H4 — genericity check) and `test_21` (cross-validation against the independent `merge_asof`
reference over the full real dataset).

**Verified to actually catch the defect, not merely assert against it**: `test_20` and `test_22` were
re-run against an in-memory monkey-patch of `like_at` reverted to the exact original formula
(`(t//14400)*14400`, no file touched) — both failed as expected, then passed again once the patch was
removed. An earlier draft of these two tests checked only the standalone `causal_bucket_asof` helper and
did NOT actually exercise `like_at`'s own returned values — this was caught by the same monkey-patch check
(the draft tests passed even under the buggy `like_at`) and corrected before being counted as coverage.

## 6. RANGE / multi-regime impact assessment (mandate §6)

**Mechanically determined, not assumed from association with the affected `cur_*` family:**

| Artifact | Code path | Affected YES/NO | Reason |
|---|---|---|---|
| `range_regime.py` (RANGE_REGIME_V1) | `map_to_m15()` | **NO** | Own docstring states "Mapped to M15 causally (merge_asof backward on H4 close_time)" and the code matches exactly — an independent, correct implementation of the same safe idiom `cur_cr13_trade.py`'s H4-trend gate uses. |
| `range_fade.py`, `rs2_continuation.py`, `rs3_pullback.py` | `d1_trend_map()` / breakout entry via `close_time` | **NO** | Same safe join pattern, confirmed by reading each file. |
| `highvol_bull_regime.py`, `lowvol_bull_regime.py`, `lowvol_bear_regime.py`, `midvol_bear_regime.py`, `midvol_bull_regime.py` (the 6-regime taxonomy) | `build_h4()` + `map_to_m15()` in each file | **NO** | All 5 independently re-implement the identical safe `merge_asof(...,right_on="close_time",direction="backward")` join — not copy-pasted from `cur_screen.py`, and not sharing its defect. |
| `hb_rescreen.py`, `hb_info.py`, `hb_xscale.py`, `lb_screen.py`, `lvbear_accept.py`, `lvbear_gate.py`, `broad_bear_accept.py` | consume the regime modules' own `map_to_m15()` | **NO** | Satellite harnesses; none reimplement the join themselves. |

**Conclusion: RANGE_REGIME_V1 and the entire subsequent multi-regime program (6-regime taxonomy plus its
satellite screens) do NOT inherit the temporal-causality defect.** They were built with an independently
correct, already-causal join convention from the start — the same one this repair made canonical for the
`cur_*` current-regime family (§3). No artifact in this program is invalidated by association; each was
checked on its own code, not assumed safe or assumed affected by proximity or naming similarity.

## 7. Exact replay harness (CR-1..CR-15) — mandate §7

`cur_replay_harness.py`: imports and calls each script's own existing entry point unchanged (its own
`main()` where one exists; `runpy.run_path` — equivalent to `python <file>.py` — for the handful that
inline their logic directly under their own `if __name__=="__main__":` instead). No modification, no
parameter selection, no new filter added anywhere in this harness or the 29 files it replays. Full
manifest (§4's 27 inherited-and-now-fixed callers, plus `cur_p8.py` for completeness though it was never
affected) ran successfully end to end; raw output preserved in `cur_replay_manifest_output.txt`.

**Per the mandate's own explicit instruction, the table below reports only what each script's OWN
pre-registered logic already printed — no new Alpha interpretation, selection, or discovery is performed
here:**

| Frontier | Own self-reported result under the now-causal infrastructure |
|---|---|
| CR-13 tradeable (CRS-1) | N=267 avgR=+0.0669 PF=1.10 WR=0.378 best10%rm=-0.1395 — its own script prints `-> NOT a survivor`. Matches Statistician's independently-computed causal figures exactly (N=267, avgR +0.0669, PF 1.10). |
| CR-13 skepticism gate | leave-one-year-out worst-case avgR=+0.0182; 214 distinct H4-up episodes; diagnostic non-current-like avgR=-0.1128, H4-DOWN version avgR=-0.0680. |
| CR-13 label-dependency probe | label-free reconstruction avgR=-0.1667 (weaker) — its own script's conclusion ("not dependent on the SIGNATURE_V1 label") is a statement about label-DEPENDENCE, orthogonal to the causal-alignment question this mandate addresses. |
| CR-3 tradeable | N=524 avgR=+0.132 — its own script prints `-> NOT a survivor (tail-dependent or partition-negative)`. |
| CR-6 tradeable | N=489 avgR=-0.0415 — its own script prints `-> NOT a survivor`. |
| CR-9 | N=235 avgR=-0.0223 — its own script prints `-> NOT a survivor`. |
| CR-11 | N=462 avgR=-0.1732 — its own script prints `-> NOT a survivor`. |
| CR-12 | N=462 avgR=+0.0274, best-10%-removed=-0.0362 — its own script prints `-> NOT a survivor`. |
| CR-14 | N=2559 avgR=-0.0889 — its own script prints `-> NOT a survivor`. |
| CR-15 | all three decomposition subsets (H1-up-all, H1-up&H4-up, H1-up&H4-DOWN) print `-> no`. |
| CR-2,4,5,7,8,10 (info-first, no P&L) | own printed ordering/excursion statistics preserved in the manifest output file — these were never P&L screens, so this repair's own effect on them is confined to which bars are included in the current-like partition, not a survivor/non-survivor verdict. |
| CR-1 first-pass family (`cur_screen`,`cur_info*`,`cur_verify`,`cur_p4-p7`) | own printed statistics in the manifest output file; `cur_p7`'s own pre-skepticism-gate screen still prints `-> CURRENT_REGIME_SURVIVOR-candidate` for its widest-stop variant, exactly as the original ledger recorded — and `cur_verify.py`'s own skepticism-gate output for the same construction still shows best-10%-removed=-0.247 (tail-dependent), the same rejection signature the ledger already documented (-0.226) before this repair. |
| CR-1 (`cur_p8`, confirmed-downtrend) | N=5293 avgR=-0.067 — unaffected by this repair (§4), numbers unchanged from before. |

**This table is a factual replay record, not a re-validation.** Whether any of these self-reported results
now constitutes a genuine finding, a changed conclusion, or grounds for any action is an Alpha/Statistician
question, explicitly out of this mandate's scope (§8, "Do NOT run Alpha interpretation or discover new
strategies"). `CURRENT_REGIME_SURVIVOR` is recorded as `0` per §1 pending that separate review — CR-13's
own script self-reporting "NOT a survivor" under the repaired infrastructure is consistent with, not a
substitute for, that formal determination.

## 8. Verdict

Per mandate §8, checked against each stated requirement:

| Requirement | Status |
|---|---|
| Defect fixed | **YES** — §3, single canonical function, empirically verified to catch the original defect (reverted-and-confirmed-failing, then restored) |
| Blast radius documented | **YES** — §4, 28 artifacts (root cause + 27 inherited callers), zero independently-duplicated instances of the unsafe idiom found elsewhere |
| Regression tests passing | **YES** — §5, 14/14 passing, covering every case mandate §5 lists plus H1-genericity and cross-validation against this codebase's own independent correct convention |
| Exact replay capability ready | **YES** — §7, full CR-1..CR-15 manifest (29 files) runs end to end against the repaired infrastructure, unmodified, no new filters |
| No unresolved higher-TF lookahead | **YES** — the one unsafe idiom found in either repo is fixed at its single source; every other cross-timeframe join (RANGE_REGIME_V1, the 6-regime taxonomy, the `market_mode`/`align_causal` family) was independently confirmed to already use the safe convention |

**`CURRENT_REGIME_CAUSAL_INFRASTRUCTURE_PASS`**

**`READY_FOR_ALPHA_EXACT_CAUSAL_REPLAY`**

Two items disclosed, not silently resolved, for whoever picks this up next: (1) not every conceivable
downstream reader of `acquisition_staging/generate_htf_context.py`'s output CSVs was traced — only its one
declared consumer; (2) `cur_regime.py` has the same "needs bucket's own close" descriptor shape as
`sig_build.py` but currently performs no cross-timeframe join at all — flagged as a watch item for re-audit
if a future screen ever consumes its output directly against a finer-grained timestamp.
