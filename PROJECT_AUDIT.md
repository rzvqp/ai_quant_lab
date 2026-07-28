# PROJECT_AUDIT — open defects, debts, method validity (2026-07-13)

## A. Confirmed defects
| id | severity | description | status |
|---|---|---|---|
| D1 | HIGH | Analytic normal-approx p-value invalid in extreme tail (heavy-tailed R) → spurious tiny p / false FDR passes. Proven: S6 analytic 2.14e-54 vs empirical bootstrap ~0.12. | retracted from verdict role; needs official empirical engine |
| D2 | HIGH | R-normalization / tiny-stop explosion: structure stops (prev_ext/beyond_sweep/structural) can be ~0 from entry → R=pnl/risk explodes (S6 R up to +166; top-5=71% profit; maxDD 89.8R v1 → 85R v2). | partially mitigated by v2 stop-floor; INVALID-EXECUTION not wired |
| D3 | HIGH | Matched-null (Test B, PRIMARY alpha test) miscalibrated: p≈0 on synthetic-null (construction/scale mismatch). | **RESOLVED 2026-07-13.** Original commits `28c35b6`→`aa5bee3`→`69747fd` (branch matched-null-validation / flow-c-foundation, base `1bc0ffb`), cherry-picked onto `statistician-foundation` 2026-07-25. Rebuilt on synthetic PRICE series routed through mstrat.simulate; a 2nd defect (absolute-risk bootstrap → FPR 0.97 under drift) fixed via risk/ATR rescaling. Calibration+power+adversarial+parity all PASS → **VALIDATED (Verdict A)**, unstratified + ATR-scaled config ONLY. See docs/MATCHED_NULL_VALIDATION.md. **Scope caveat (2026-07-25):** validated regime = 1.5×ATR stops on generic signals; structural-stop families (the D2 sources) were never in the calibration battery → matched-null is NOT validated for them. D2 remains HIGH/OPEN and gates any structural-stop use. |
| D4 | MED | Discovery Screen V1 thresholds calibrated on S1-S10 results = DEVELOPMENT-TUNED (selection-bias). | frozen; S11-S20 = prospective test |
| D5 | LOW | run_full_campaign.py %-profitable display bug (÷valid=0 → 400% for S19). Counts correct. | cosmetic |
| D6 | MED | Top-by-expectancy / top-by-profit-DD lists dominated by low-n flukes (S1 n=3-5, PF≈99). | use RESEARCH_WORTHY + monthly-stability lists |
| D7 | INFRA | Lab code+data were only in ephemeral Temp scratchpad. | fixed: copied to durable ai_quant_lab/; GC MBO raw (data2) still Temp-only (re-downloadable) |
| D8 | INFRA | Secondary hardcoded Temp paths remain in NON-campaign scripts: resample_ny.py, quality_and_resample.py, run_prod.py (data-rebuild), run_cycle.py, build_gc_bars.py, foundation_gc/engine.py (GC foundation). | deferred: not on the official S1–S20 campaign path; repoint only if those scripts are rerun. Campaign path (mtf.py) FIXED 2026-07-13. |
| D9 | INFRA | requirements.txt omits a parquet engine (pyarrow) though the campaign writes/reads FAMILY_RESULTS.parquet. | add `pyarrow` to requirements.txt (installed manually this session). |
| D10 | DOC | Docs state M15=84,151 bars; actual file = 84,152 (wc off-by-one, no trailing newline). Proven benign (exact reproduction; holdout 16,831 matches). | correct the figure in docs; no data/result change. |
| D11 | HIGH | The 428/1972-ID universe contains fewer DISTINCT strategies than IDs. Confirmed by full audit (`docs/DUPLICATE_AUDIT_v1.0.md`, commit `80fb243`): **1972 IDs → 1440 distinct (532 redundant, 27.0%)**; **428 ATR → 360 distinct (68 redundant, 15.9%)**. Root cause SYSTEMATIC, not accidental: lookback params (`liq_lb`/`lb`) are conditionally inert whenever `liq_ref != 'swing'` (87% of clusters), plus smaller config-specific collapses (`exit` rr2/rr3, `mode`, `target`). Family size for any future FDR/multiple-testing correction on either corpus is wrong if computed from raw ID count. | mandatory mechanical deduplication pre-screening specified in §F below; EXECUTED against the full corpus (Research Lab, commit `80fb243`) using exactly this criterion; the deduplicated counts (1440/360) are now the required `m` for any future correction on these corpora. |

## A.1 Reproducibility status (2026-07-13)
- Portability fix (D-critical `mtf.py`) applied; official campaign re-run on a fresh venv (pandas 3.0.3/numpy 2.5.1, newer than original) reproduced the baseline **EXACTLY** (Verdict A): 1972/1800/357/130/14/9; per-hypothesis parquet max abs diff 0.0; total trades 1,300,740 identical; boolean verdicts identical; 0 Temp reads; holdout SEALED. Baseline not overwritten (new run in results/reproduction_v2/). Pre-fix git checkpoint `85857234`. See PORTABILITY_AUDIT.md, REPRODUCIBILITY_AUDIT.md.

## B. Method validity status (ALL under validation)
- Analytic p-value: INVALID for verdicts (diagnostic only).
- IID bootstrap (Test A robustness): H0-centering proven correct; METHOD UNDER VALIDATION.
- Block bootstrap (Test A robustness): well-calibrated on 2 synthetic controls; METHOD UNDER VALIDATION (needs full battery).
- Matched-null (Test B, primary): MISCALIBRATED; fix required.
- Global-FDR: NOT yet run with a valid p-value. Universe = full eligible valid (m=1552; 1704 conservative diagnostic).

## C. Retracted conclusions (audit trail)
1. "S1 = mostly long-bias/drift" — REFUTED (drift_core.py: random-long baseline −0.087R; S1 excess +0.31R).
2. "S1/S5/S9 decorrelated" — RETRACTED (single unstable monthly-R point estimate; no CI/stability/canonical representative).
3. "No Research Candidate significant" — RETRACTED (only S1-rep + S6 tested under pilot; reformulated to those two only).
4. S1-standalone "6 Discovery Candidates" (s1.py) — SUPERSEDED (family-favorable ATR-null + per-family FDR; not a candidate under mstrat.py unified engine + global FDR).

## D. Frozen decisions (do not change without CEO gate)
- Primary statistic = mean expectancy R/trade, one-sided (H0: mean≤0).
- Discovery Screen V1 = n≥25 & exp_research>0 & PF≥1.02 & maxDD≤25R & research-only (no OOS).
- Stop-floor formula = max(2×spread, 5×tick, 0.10×ATR) (pre-registered).
- Data splits research 60% / validation 20% / terminal holdout 20% SEALED (never opened).
- **Deduplication (D11, §F) is a mandatory pre-screening step before any future multiple-testing
  correction on any corpus of hypothesis IDs.** Family size (`m`) for BH-FDR/Bonferroni/any correction
  must be the deduplicated distinct-strategy count, never the raw ID count, from the point this rule
  is frozen forward.

## F. Deduplication algorithm (D11) — mandatory pre-screening before multiple-testing correction

**Trigger:** confirmed via the three-regime persistence run (`docs/THREE_REGIME_PERSISTENCE_RESULT_v1.0.md`,
commit `7927441`) — the two `S2` IDs in the persistence leaderboard (`92481423c6b8`, `a53441048c3c`)
produce bit-identical trade logs because `lb` (lookback) is structurally inert when `ref=pdh_pdl` (a
fixed-level reference that never reads `lb`). The 428/1972-ID universe is therefore smaller, in
distinct-strategy terms, than its own ID count — and likely not only in this one case, since "inert
parameter for a specific reference type" is a code-structure property that can recur anywhere in the
S1-S51 grid, not a one-off coincidence.

### 1. Identity criterion — realized trade log, not summary statistics

**Two IDs A and B are declared duplicates if and only if their realized trade logs are bit-for-bit
identical over the same evaluated dataset**: the ordered sequence of `(entry_epoch, exit_epoch, R)`
tuples, in chronological order, for every trade either produced.

**Explicitly NOT the criterion:** matching summary statistics (`exp`, `win`, `pf`, `n`, `net1`, etc.).
Two genuinely different strategies could coincidentally produce similar aggregates without being the
same trades; conversely, floating-point aggregation order could make two IDENTICAL trade sequences
show trivially different rounded summary stats. Comparing the raw trade log side-steps both failure
directions — it is the only representation where "same economic bet" and "same computed object" are
provably the same check.

### 2. Mechanical detection, not inspection

For each hypothesis ID, on a fixed evaluated dataset (e.g., the pooled 3-regime discovery run already
computed, or the full research-side data for the 1972 body): serialize its trade log canonically —
`entry_epoch,exit_epoch,R` per trade, one line per trade, trades sorted by `entry_epoch` — and compute
`SHA-256` of the resulting byte string. **Two IDs are duplicates iff their trade-log hashes match
exactly.** This is a single pass per ID (no pairwise `O(n²)` comparison needed): group all IDs by their
hash: any hash bucket with more than one member is an equivalence class of duplicates.

Run once per dataset version (e.g., once for the 3-regime discovery run, again if/when the sealed half
is ever opened, again for any future dataset revision) — a structural-code property like `lb`-inertness
will reproduce identically on any dataset, so a single representative run is sufficient to establish
duplicate status, though re-confirming on a second dataset is a cheap, free cross-check.

### 3. What is retained when IDs collapse — group, never delete

Both/all member IDs of a duplicate equivalence class **remain registered, inspectable, and citable** —
nothing is deleted or hidden. Mechanically:
- The equivalence class gets ONE **canonical ID**, chosen deterministically (not by judgment): the
  lexicographically lowest hex ID string in the class. This is an arbitrary but fully mechanical,
  disclosed tie-break — no domain judgment about which parameter value is "more meaningful" is required.
- Every other member is recorded as `DUPLICATE_OF: <canonical_id>`, with the specific inert parameter(s)
  and their differing values noted, so the mechanism (e.g., `lb` inert under `ref=pdh_pdl`) is visible,
  not just the fact of duplication.
- For any report, chart, or registry entry that would otherwise cite a non-canonical member, the
  canonical ID is used instead — but the non-canonical ID's own entry is never removed.

### 4. Reporting the real universe size vs. the ID count

Any corpus summary (e.g., "428 ATR-eligible", "1972 total") must report **both** numbers going forward:
the raw ID count, and the deduplicated distinct-strategy count (raw count minus one per non-canonical
member found). **Any future BH-FDR, Bonferroni, or other multiple-testing correction on this corpus
MUST use the deduplicated count as `m`** — using the raw ID count would inflate the apparent number of
independent tests and, backwards, could either over- or under-correct depending on how many duplicates
exist and whether they happen to be null or a persister (a persister duplicate, uncorrected, would be
double-counted as "2 independent confirmations" of what is mechanically one).

### 5. Scope and what this does NOT solve

This algorithm catches only **exact** duplication (correlation = 1.0). It does **not** address the
weaker, more pervasive problem of **partial correlation** between IDs that share the same underlying
entries with different exit rules (the already-documented S18 pattern: "3 signals × 2 exits ≠ 6
independent tests") — those IDs produce genuinely different trade logs (different exits change R per
trade) and will not hash-collide, yet are still far from statistically independent. Deduplication is
necessary but not sufficient for a correct family size; the partial-correlation problem remains open,
flagged, not solved here.

**Execution is NOT performed by this document** — this is a specification (Statistician's design
authority), not a run. Someone with access to the trade-log data (Research Lab / Validation Engine)
executes it as a mandatory pre-screening step before any future multiple-testing correction, exactly
per the mandate that introduced it.

### 6. Executed result (Research Lab, `docs/DUPLICATE_AUDIT_v1.0.md`, commit `80fb243`)

Run before this specification was even finished being written, using the same criterion (identical
trade series over the same window, confirmed by hash on the reconstituted R series) via a sensible
two-stage implementation: (1) a cheap pre-filter using existing `FAMILY_RESULTS` summary-stat
fingerprints to find CANDIDATE clusters without materializing all 1972 trade logs, then (2) each
candidate cluster CONFIRMED by the actual trade-log hash (canonical engine, only the clustered IDs
re-run) -- an efficient implementation of the specified criterion, not a substitute for it: the
deciding test remains the trade-log hash, the fingerprint stage is only a cost-saving pre-filter.

| universe | IDs | duplicate IDs (cluster >1) | clusters | distinct strategies | redundancy |
|---|---|---|---|---|---|
| full 1972 | 1972 | 1040 | 508 | **1440** | 532 (27.0%) |
| 428 ATR | 428 | 136 | 68 | **360** | 68 (15.9%) |

**Root cause, confirmed systematic:** lookback (`liq_lb`/`lb`) accounts for 444/508 clusters (87%) --
conditionally inert whenever `liq_ref != 'swing'` (i.e. `pdh_pdl` or `session`), a structural property
of the setup-provider code (`lb = int(h['liq_lb']) if h['liq_ref']=='swing' else 20`), not an accident
or a one-off. Smaller config-specific collapses: `exit` (rr2/rr3 colliding on timeout or a closer exit
firing first, 20 clusters), `mode` (S5, 48), `target` (S12, 8).

**Consequence for the legacy-428 persistence labels (`STATISTICIAN_LEGACY428_PERSISTENCE_VERDICT_v1.0.md`):**
the 367/58/3 labels there are assigned per raw ID, as mandated -- they are NOT recomputed to
distinct-strategy counts here (out of scope for this document). But 68 of the 428 raw IDs are known
redundant copies within those groups (confirmed: the persistence leaderboard's S2 pair is one such
cluster) -- any future formal statistical test or FDR correction drawn from this 428 pool must use
**360**, not 428, as `m`, per the frozen rule in §D above.

## E. Governance
- Holdout terminal: SEALED, never opened this session. Opening = CEO gate only.
- No live trading. No candidate optimization. No REJECTED verdicts while p-engine invalidated.
