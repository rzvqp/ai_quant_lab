# PROJECT_AUDIT — open defects, debts, method validity (updated 2026-07-14, pre-Wave1 consolidation)

> **Scope note (added 2026-07-19, Official Project Save; re-confirmed 2026-07-20 after Checkpoints
> 14–15; re-confirmed again 2026-07-20 at the fifth official save, the Flow A/Flow B bifurcation; and
> once more 2026-07-20 in the Flow B session that produced `STRATEGY_HEALTH_INTEGRATION_POLICY_DESIGN.md`
> — a design proposal only, no code, 0-diff against this document's own subject matter confirmed)**: this
> document audits the Research Lab (`code/`, `results/`, `knowledge/`) ONLY — its defect register,
> method-validity status, and frozen decisions below are unchanged and unaffected by any AI Trader work,
> since every AI Trader phase to date (6.1 through Phase 7 Checkpoint 15), the three interim research
> studies (Strategy Historical Performance Study, Strategy Constraint Root-Cause Study, CEO Strategy
> Performance Atlas), and the newly-opened 40-Edge Alpha Discovery Program (Flow A) have all confirmed
> 0-diff against `code/`/`results/`/`knowledge/` at every single close, including this save. **Flow A in
> particular touches none of this document's own subject matter at all** — it is a wholly separate,
> root-level-markdown-only research backlog (`EDGE_DISCOVERY_REGISTRY_v1.md`/
> `EDGE_RESEARCH_PROTOCOL.md`/`EDGE_DISCOVERY_ROADMAP.md`) with its own 40 unrelated hypotheses (E001–
> E040), sharing no strategy, no code, and no data file with the Research Lab's own S1–S51 strategy
> universe — see `PROJECT_STATE_v2.md` §1.1 for the full two-flow structure. For the AI Trader's own
> current state (Shadow Evidence, Market Intelligence, Edge Intelligence, Decision Intelligence v1/v2,
> Context Memory, the v1-vs-v2 falsification study, the interim research studies, and Flow A's own
> founding documents), see `PROJECT_STATE_v2.md` instead — that document is the authoritative source for
> everything built on top of this frozen Research Lab, not this one.
>
> **Note (2026-07-20)**: Phase 7 Checkpoint 13's own `ai_trader/context_memory/evidence.py` reuses two
> of this document's own already-established conventions verbatim, by explicit CEO instruction to ground
> new statistical thresholds in existing validated practice rather than inventing them: the
> `code/alpha_lab.py` `MINTR=25` minimum-trade-count gate (as the evidence-sufficiency default) and the
> §A0/§28 "UNRESOLVED if the CI straddles zero" small-n rule (as the `CONTRADICTORY` evidence-status
> trigger). This is a downstream REUSE only — nothing in this document itself was changed by that
> checkpoint. Phase 7 Checkpoint 15's own falsification study reused no additional convention from this
> document beyond what Checkpoint 13 already established.
>
> **Note (2026-07-21)**: the Strategy Health Integration Eligibility Policy layer
> (`ai_trader/strategy_health/shadow_gate.py`, roadmap Flow B step 1/6) reuses this document's own
> `code/alpha_lab.py` `MINTR=25` convention a second time, as `MIN_EVIDENCE_TRADES` — the minimum
> lifetime Shadow-sourced trade count below which a strategy is always classified `NEW` (Shadow-only)
> regardless of what the frozen Strategy Health classifier's own band would otherwise say. A downstream
> reuse only, matching the 2026-07-20 note above; nothing in this document itself was changed.
>
> **Incident note (2026-07-21) — TERMINAL HOLDOUT BREACHED**: this document's own §D "Frozen decisions"
> below records the Research Lab's terminal-holdout split ("terminal holdout 20% SEALED (never
> opened)"). On 2026-07-21 it was confirmed that Flow A's first five studied edges (E025, E026, E028,
> E029, E032, commit `eed1634`) had in fact loaded and analyzed data from that exact sealed period
> (2025-10-23 09:15 UTC → 2026-07-13 06:00 UTC), because the shared Flow A loader applied no date
> cutoff. **The old terminal holdout is CONSUMED / INVALIDATED** — it can no longer serve as an
> independent terminal evaluation for the Research Lab or for Flow A; simply re-running the five
> analyses with a cutoff does not restore its integrity. This is a process/governance breach, not a
> retraction of any Research Lab conclusion above (nothing in §A–§E below is changed by this note) — the
> breach originated entirely in Flow A's own tooling, which never read from or wrote to `code/`,
> `results/`, or `knowledge/`. Full incident record: `PROJECT_STATE_v2.md` §8.23. No new holdout period
> is designated by this note.

## A0. Consolidation & risk register (2026-07-14)
**Branches integrated into research-main:** master (baseline), matched-null-validation, family-implementation-s21-s40,
strategy-development. **Not integrated:** none (all merged; original refs retained). Conflicts: CHANGELOG (union),
2 report files (S1–S40 canonical + S1–S20 preserved). No CEO-decision conflict. Engine byte-frozen throughout.

**Methods VALIDATED:** matched-null Test B (Verdict A — calibration/power/adversarial/parity pass; unstratified config).
Block-bootstrap (Test A) interim-official under-validation. **Methods PENDING:** global-FDR (not run), walk-forward, Red Team.

**Retracted conclusions (history preserved):** "S1=drift", "S1/S5/S9 decorrelated", "no RC significant",
S1-standalone "6 candidates", analytic-p as verdict, and the earlier claim that broad mechanisms generalize
(most S21–S51 negatives). All logged in NEGATIVE_EVIDENCE_REGISTRY / knowledge/.

**Open risks carried into Wave 1:**
- **Beta confound (I7):** most positives are long in a bull sample; timing-alpha vs gold beta unresolved (Wave-1 EXP-03/04 partial).
- **Multiple testing:** 2,432 hypotheses + 54 generated + 10 experiments reusing correlated events → hierarchical
  family-wise plan mandatory (EXPERIMENT_PRIORITY_MATRIX); no per-experiment significance hunting.
- **Small-n:** several positives (S42 n≈43, S1/swing n≈43, S31 n=38) — min-trades + UNRESOLVED-if-CI-straddles rules set.
- **Semantic duplication:** generator novelty gate is TAG-based (necessary not sufficient); v2 semantic-signature owed.
- **Codex filesystem review PENDING:** its MCP sandbox is stale; all Codex reviews to date are INLINE only.

## A. Confirmed defects
| id | severity | description | status |
|---|---|---|---|
| D1 | HIGH | Analytic normal-approx p-value invalid in extreme tail (heavy-tailed R) → spurious tiny p / false FDR passes. Proven: S6 analytic 2.14e-54 vs empirical bootstrap ~0.12. | retracted from verdict role; needs official empirical engine |
| D2 | HIGH | R-normalization / tiny-stop explosion: structure stops (prev_ext/beyond_sweep/structural) can be ~0 from entry → R=pnl/risk explodes (S6 R up to +166; top-5=71% profit; maxDD 89.8R v1 → 85R v2). | partially mitigated by v2 stop-floor; INVALID-EXECUTION not wired |
| D3 | HIGH | Matched-null (Test B, PRIMARY alpha test) miscalibrated: p≈0 on synthetic-null (construction/scale mismatch). | **RESOLVED 2026-07-13 (branch matched-null-validation).** Rebuilt on synthetic PRICE series routed through mstrat.simulate; a 2nd defect (absolute-risk bootstrap → FPR 0.97 under drift) fixed via risk/ATR rescaling. Calibration+power+adversarial+parity all PASS → **VALIDATED (Verdict A)**, unstratified config. See docs/MATCHED_NULL_VALIDATION.md. Not yet merged. |
| D4 | MED | Discovery Screen V1 thresholds calibrated on S1-S10 results = DEVELOPMENT-TUNED (selection-bias). | frozen; S11-S20 = prospective test |
| D5 | LOW | run_full_campaign.py %-profitable display bug (÷valid=0 → 400% for S19). Counts correct. | cosmetic |
| D6 | MED | Top-by-expectancy / top-by-profit-DD lists dominated by low-n flukes (S1 n=3-5, PF≈99). | use RESEARCH_WORTHY + monthly-stability lists |
| D7 | INFRA | Lab code+data were only in ephemeral Temp scratchpad. | fixed: copied to durable ai_quant_lab/; GC MBO raw (data2) still Temp-only (re-downloadable) |
| D8 | INFRA | Secondary hardcoded Temp paths remain in NON-campaign scripts: resample_ny.py, quality_and_resample.py, run_prod.py (data-rebuild), run_cycle.py, build_gc_bars.py, foundation_gc/engine.py (GC foundation). | deferred: not on the official S1–S20 campaign path; repoint only if those scripts are rerun. Campaign path (mtf.py) FIXED 2026-07-13. |
| D9 | INFRA | requirements.txt omits a parquet engine (pyarrow) though the campaign writes/reads FAMILY_RESULTS.parquet. | add `pyarrow` to requirements.txt (installed manually this session). |
| D10 | DOC | Docs state M15=84,151 bars; actual file = 84,152 (wc off-by-one, no trailing newline). Proven benign (exact reproduction; holdout 16,831 matches). | correct the figure in docs; no data/result change. |

## A.1 Reproducibility status (2026-07-13)
- Portability fix (D-critical `mtf.py`) applied; official campaign re-run on a fresh venv (pandas 3.0.3/numpy 2.5.1, newer than original) reproduced the baseline **EXACTLY** (Verdict A): 1972/1800/357/130/14/9; per-hypothesis parquet max abs diff 0.0; total trades 1,300,740 identical; boolean verdicts identical; 0 Temp reads; holdout SEALED. Baseline not overwritten (new run in results/reproduction_v2/). Pre-fix git checkpoint `85857234`. See PORTABILITY_AUDIT.md, REPRODUCIBILITY_AUDIT.md.

## B. Method validity status
- Analytic p-value: INVALID for verdicts (diagnostic only).
- IID bootstrap (Test A robustness): H0-centering proven correct; METHOD UNDER VALIDATION.
- Block bootstrap (Test A robustness): well-calibrated on 2 synthetic controls; METHOD UNDER VALIDATION (needs full battery).
- Matched-null (Test B, primary): **ENGINE VALIDATED (Verdict A)** — calibration/power/adversarial/parity all PASS (unstratified ATR-scaled config; see §A0, defect D3, docs/MATCHED_NULL_VALIDATION.md). APPLICATION SCOPE SO FAR: the 10-hypothesis pre-registered pilot ONLY. FULL-CAMPAIGN application (matched-null over the whole eligible S1–S51 universe) = **PENDING** (CEO-gated). [Corrected 2026-07-14, wave1-execution: this bullet previously read "MISCALIBRATED; fix required", stale relative to §A0/D3 which record the 2026-07-13 resolution. Documentary correction only — no methodology change.]
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

## E. Governance
- Holdout terminal: SEALED, never opened this session. Opening = CEO gate only.
- No live trading. No candidate optimization. No REJECTED verdicts while p-engine invalidated.
