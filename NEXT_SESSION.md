# NEXT_SESSION.md — Official Handoff (Single Entry Point)

**Rewritten in full on 2026-07-20 as an OFFICIAL PROJECT SAVE, after Checkpoints 14–15** (Decision
Intelligence v2 — Context Memory Integration, and the v1-vs-v2 falsification study; no other package
modified, no architecture outside these two new packages changed). This document, together with
`PROJECT_STATE_v2.md` (the complete, consolidated state document, now including Phase 7 §8 through
Checkpoint 15), `RECONSTRUCTION_PROMPT.md` (the single entry point for a genuinely new conversation),
`PHASE_7_CHECKPOINT_15_REPORT.md`/`_14_REPORT.md` (the current architectural frontier), `CHANGELOG.md`,
and every phase's own dedicated report, is designed to let a BRAND-NEW chat reconstruct this project
100% with NO access to any prior conversation. Every fact below was verified directly against `git log`/
`git status`/`git diff` at this save's own close, and against the ONE full-repository `pytest`/`mypy`/
`coverage` run this batch's own validation policy authorizes (two checkpoints closing together) —
nothing here is carried forward unverified.

**Read, in this exact order:**
1. **This document** — the exact current state and the exact next-session procedure.
2. **`RECONSTRUCTION_PROMPT.md`** — if this is a genuinely new conversation, start there; it points
   back here with the exact verification steps to run first.
3. **`PHASE_7_CHECKPOINT_15_REPORT.md`** → **`PHASE_7_CHECKPOINT_14_REPORT.md`** — the current official
   architectural frontier: **Decision Intelligence v2** (`ai_trader/decision_intelligence_v2/`), a
   SEPARATE, additive system wrapping v1 (unmodified) with an explainable, per-candidate Context Memory
   evidence attachment — `DecisionReportV2`'s own recommendation is construction-time-guaranteed
   identical to v1's, so Context Memory can never change eligibility/ranking/scoring/Risk/Sizing/
   Execution or generate BUY/SELL — and the **v1-vs-v2 falsification study**
   (`ai_trader/decision_comparison/`), whose verdict is **`V1_REMAINS_ACTIVE`**: every trade-outcome
   metric is provably identical between v1 and v2 under the current architecture (proven, confirmed over
   real data), and v2's only measured differences are richer explanations and (as-yet-unmeasurable-for-
   real-data) confidence calibration.
4. **`PHASE_7_CHECKPOINT_13_REPORT.md`** → **`_12_`** → **`_11_`** → **`_10_`** → **`_9_REPORT.md`** →
   **`PHASE_7_CHECKPOINT_8_CONTEXT_MEMORY_DESIGN.md`** — the complete Context Memory subsystem Checkpoint
   14 consumes: per-edge Contextual Evidence Aggregation, built on deterministic hierarchical-relaxation
   Retrieval, built on a deterministic episode-collapsed Historical Index, built on an append-only
   Repository, built on immutable contracts and deterministic SHA-256 identities.
5. **`PHASE_7_CHECKPOINT_7_REPORT.md`** → **`PHASE_7_CHECKPOINT_6_REPORT.md`** →
   **`PHASE_7_CHECKPOINT_5_REPORT.md`** — Decision Intelligence v1 built on Edge Intelligence built on
   Market Intelligence — still current, unmodified, and the SOLE ACTIVE recommendation system.
6. **`PROJECT_STATE_v2.md`** — the complete state through Phase 6.9A (§2–§6), Phase 6.10 in full and now
   CLOSED (§7), and Phase 7 Checkpoints 5–15 plus all four official saves (§8). The single most complete
   document in the repository.
7. **`PHASE_6_10_EDGE_PORTFOLIO_DIRECTION.md`** — background only: the architectural direction behind
   the now-CLOSED Phase 6.10 (generic Edge Portfolio, S10 as validation edge only). Do not confuse Phase
   6.10's "Edge Portfolio," Phase 7's "Edge Intelligence," "Context Memory," "Decision Intelligence v1,"
   and "Decision Intelligence v2" — see §B below for the full disambiguation.
8. **`PHASE_6_10_PRE_SCOPE_DIAGNOSTIC.md`** → **`PHASE_6_10_SHADOW_EVIDENCE_ARCHITECTURE_DESIGN.md`**
   (including its own §17 adversarial review and §19 Checkpoint 1C correction) — background on Shadow
   Evidence's own design, if depth is needed.
9. In detail, if deeper Phase 6.9A background is needed:
   `PHASE_6_9_ROLLING_HEALTH_GATED_BACKTEST_REPORT.md` → `CURRENT_XAUUSD_12M_RELEVANCE_REPORT.md` →
   `PHASE_6_9A_STRATEGY_EVIDENCE_FLOW_AUDIT_REPORT.md`.
10. `ROLLING_HEALTH_BACKTEST_HANDOFF.md` for the Strategy Health System's own full methodology.
11. `PROJECT_STATE_v1.0.md` for the Research Lab's own frozen state.
12. `CHANGELOG.md`'s own top entries for verified, dated, session-by-session detail.

---

## A. Exact project state (summary)

**Two systems**: the Research Lab (`code/`, `results/`, `knowledge/` — FROZEN, 0-diff confirmed) and
the AI Trader (`ai_trader/` — active development). Since the third official project save (`07c070c`,
2026-07-20, after Checkpoints 10–13), TWO further checkpoints have landed: Checkpoint 14
(`ai_trader/decision_intelligence_v2/`, NEW) and Checkpoint 15 (`ai_trader/decision_comparison/`, NEW).
Every other `ai_trader/` module — including `ai_trader/decision_intelligence/` (v1) and
`ai_trader/context_memory/` — remains byte-for-byte unchanged since that save, confirmed live at this
save's own close.

**Phases CLOSED / COMPLETE** (unchanged from `PROJECT_STATE_v2.md` §3–§7): 6.1–6.6, 6.7, 6.8
Checkpoints 1–2 + Wave B, Wave D + Wave D Audit, Strategy Health System build, Phase 6.9, Current XAUUSD
12-Month Relevance Audit, Phase 6.9A, Phase 6.10 (Edge Portfolio Evidence System) in full.

**Phase 7 — AI Trader Intelligence Layer — Checkpoints 5–15 DONE, Checkpoint 16 NOT PROPOSED, NOT
AUTHORIZED:**

| Checkpoint | Status | Commit |
|---|---|---|
| 5 — Market Intelligence layer | DONE | `8e2748a7980d2447fc3b33b8c9d96192d17f3450` |
| 6 — Edge Intelligence layer | DONE | `b94c93f1748f71a08657b5fb348ac240def5f17e` |
| 7 — Decision Intelligence v1 layer | DONE | `0346e070967228b35c87659a34a829f4aa5cda8f` |
| 8 — Context Memory architecture design | DONE (ACCEPTED) | `263b950d498c2f431e958c3ce09c85676d85838f` |
| 9 — Context Memory contracts + identities | DONE | `30213d0adf5c3fb6f2d860a84c8a81bc4b848cb2` |
| 10 — Append-Only Context Repository | DONE | `486aa61de180d8d0daca0b4bd14fe1938d5f566c` |
| 11 — Episode Collapsing and Historical Index | DONE | `9d273c49b000d6aaa1c0361c92c131225b04465d` |
| 12 — Deterministic Context Retrieval | DONE | `cf36e9879aed56c61011aad7d538e9ee48a53f2e` |
| 13 — Contextual Evidence Aggregation | DONE | `24457858c9c0da7d3b6b65f1e16d0589575c37df` |
| Third Official Project Save (after Checkpoints 10–13) | DONE (docs only) | `07c070c9623d6a9ac036db7abc071da3b9302b02` |
| 14 — Decision Intelligence v2 — Context Memory Integration | DONE | `dbcdb666ab7bbaffc3d19675fea13685844562e5` |
| 15 — Decision Intelligence v1 vs v2 Falsification Study | DONE | `069c47948982a82f3a2b801ff60954f28a931d8c` |
| Fourth Official Project Save (this document's own update) | IN PROGRESS — documentation only |
| Checkpoint 16 (no topic proposed) | NOT PROPOSED, NOT AUTHORIZED |

## B. Naming disambiguation — read before touching any of the five intelligence/evidence/comparison packages

Phase 6.10's "**Edge Portfolio**" (`shadow_evidence/`) is the multi-strategy Shadow virtual-execution
PLATFORM. Phase 7's "**Edge Intelligence**" (`edge_intelligence/`) is a read-only RECOGNITION layer.
Phase 7's "**Decision Intelligence v1**" (`decision_intelligence/`) answers "which edge, if any,
deserves execution" — the SOLE ACTIVE recommendation system. Phase 7's "**Context Memory**"
(`context_memory/`) stores/indexes/retrieves/aggregates HISTORICAL evidence, never evaluates the
present, never recommends. Phase 7's "**Decision Intelligence v2**" (`decision_intelligence_v2/`) is a
SEPARATE, additive wrapper around v1 that attaches Context Memory's evidence to v1's own, unmodified
recommendation — v2 never independently decides anything; its own recommendation is construction-time-
guaranteed identical to v1's. Phase 7's "**Decision Comparison**" (`decision_comparison/`) is a read-only
framework comparing v1 and v2 — it modifies neither. `edge_intelligence/` does not import
`shadow_evidence`; `decision_intelligence/` (v1) does not import `shadow_evidence`/`signal_engine`/
`scoring_engine`/`risk_manager`/`execution_engine`; `context_memory/` does not import
`decision_intelligence`/`signal_engine`/`scoring_engine`/`risk_manager`/`execution_engine`/
`shadow_evidence`; `decision_intelligence_v2/` and `decision_comparison/` do not import
`signal_engine`/`scoring_engine`/`risk_manager`/`execution_engine`/`shadow_evidence` and never write to
Context Memory's own repository — every one of these isolation choices is deliberate, verified by grep
and static AST scans at each checkpoint's own close.

## C. Phase 6.10 Implementation Checkpoint 1C — the one finding worth re-reading carefully

Checkpoint 1C implemented the full generic Shadow virtual position lifecycle. Its own S10 isolated-ledger
validation found a REAL divergence from Phase 6.9A's independently-verified isolated-run ground truth.
CEO ruling, binding on all future work in `shadow_evidence/`: this is a **documented semantic limitation,
not a defect**. Full detail: `PROJECT_STATE_v2.md` §7.7, `PHASE_6_10_CHECKPOINT_1C_REPORT.md`.

## D. Phase 7 Checkpoints 5–15 — what exists and what deliberately does not

**Checkpoints 5–7**: Market Intelligence → Edge Intelligence → Decision Intelligence v1
(`make_decision(context) -> DecisionReport`, ACCEPT/REJECT eligibility gates + deterministic ranking +
NO TRADE). Still the sole active recommendation system.

**Checkpoints 8–13**: the complete Context Memory subsystem — architecture design, immutable contracts
+ deterministic identities, an append-only repository, deterministic episode collapsing + a historical
index, a fixed-priority hierarchical-relaxation retrieval mechanism (no k-NN/weighted distance), and
per-edge Contextual Evidence Aggregation with a controlled sufficiency status
(SUFFICIENT/LIMITED/CONTRADICTORY/STALE/UNAVAILABLE/INCOMPATIBLE). Never outputs a recommendation.

**Checkpoint 14** (`decision_intelligence_v2/`): `make_decision_v2(context, context_memory_index=None,
...) -> DecisionReportV2` — calls v1's `make_decision()` UNCHANGED, then (if an index is supplied)
attaches a per-candidate Context Memory evidence report and a disclosed, four-part explanation (why
context found / what evidence / limitations / why status). `DecisionReportV2.recommended_strategy_id`
is construction-time-forced to equal v1's own — Context Memory literally cannot change the
recommendation in this architecture. Proven over 20 real XAUUSD bars: 0 divergences.

**Checkpoint 15** (`decision_comparison/`): builds the falsification comparison framework across every
CEO-named dimension. Central, proven (not assumed) fact: since v2's recommendation stream is
construction-time-identical to v1's, every trade-outcome metric (expectancy, win rate, drawdown, false
positive/negative rate, NO TRADE frequency, edge selection, recommendation-level regime robustness) is
provably identical between v1 and v2 — stated as a proof, never re-confirmed via a redundant backtest.
Explanation quality (v2 strictly richer whenever evidence attaches) and confidence calibration (machinery
built + tested, `n_samples=0` on real data pending real historical Context Memory population) are the
only genuinely-differing dimensions measured. **Falsification verdict: `V1_REMAINS_ACTIVE`.**

**None of Checkpoints 5–15's packages trades, sizes a position, sends an order, or is wired into
`harness.py` or any execution path.**

## E. Official Git state (verify live — do not trust blindly)

```
Repository path:  C:\Users\MEDION GAMING\ai_quant_lab-research-main
Branch:           ai-trader-implementation
HEAD (pre-close): 069c47948982a82f3a2b801ff60954f28a931d8c
                  "Phase 7 Checkpoint 15: Decision Intelligence v1 vs v2 Falsification Study"
Working tree:     clean (verified live before this checkpoint save's own commit)
```

**This checkpoint save's own commit** (this file, `PROJECT_STATE_v2.md`, `CHANGELOG.md`,
`RECONSTRUCTION_PROMPT.md`, `PROJECT_AUDIT.md`, and `PHASE_7_CHECKPOINTS_14_15_OFFICIAL_SAVE_REPORT.md`)
lands ONE commit after `069c47948982a82f3a2b801ff60954f28a931d8c` — run `git log -1` for the exact
current HEAD; do not assume it is still that commit in any future session.

**Re-verify `git branch --show-current`/`git log -1`/`git status --porcelain` directly before trusting
any git-state claim anywhere in this project's documentation** — the standing discipline every prior
handoff has followed, re-confirmed at this checkpoint.

**Verified live, at the close of the Checkpoints 14–15 batch (2026-07-20) — the ONE full-repository run
this batch's own policy authorizes:**
```
pytest ai_trader/ -q -> 2101 passed
mypy --strict ai_trader/ --exclude 'tests/' -> Success: no issues found in 222 source files
coverage: TOTAL 12087 stmts, 432 miss, 96% (decision_intelligence_v2/ + decision_comparison/: 100%,
                                             274/274 new stmts)
```
**Combined Context Memory + Decision Intelligence, run independently at each checkpoint's own close,
re-confirmed combined**: `pytest ai_trader/context_memory/ ai_trader/decision_intelligence/
ai_trader/decision_intelligence_v2/ ai_trader/decision_comparison/ -q` → 303 passed; `mypy --strict`
(same four packages) → clean, 28 source files.

## F. What must NOT be modified (standing, cumulative — unchanged, plus Checkpoint 14–15 additions)

- `code/`, `results/`, `knowledge/` (Research Lab) — frozen, 0-diff.
- Every strategy contract, evaluator, and parameter.
- `ai_trader/strategy_health/`'s own scoring methodology — frozen since its own build.
- Scoring Engine weights, Risk Policy, Execution Engine rules.
- The sealed terminal holdout (2025-10-23 09:15 UTC → 2026-07-13 06:00 UTC) — never opened.
- No strategy is ever permanently eliminated based on any AI Trader analysis to date.
- **Phase 6.10 (CLOSED, standing constraints remain in force)**: no edge/strategy-specific architecture
  in `shadow_evidence/`; no Strategy Health integration policy selected; no capital-allocation
  architecture designed.
- **Phase 7 Checkpoints 5–7 (standing)**: `market_intelligence/`, `edge_intelligence/`, and
  `decision_intelligence/` (v1) must remain pure — no execution, no order submission, no risk sizing, no
  scoring/health classification, ever. None may be wired into `harness.py` without its own explicit CEO
  approval. **v1 must never be modified to accommodate v2 or the comparison framework.**
- **Phase 7 Context Memory, Checkpoints 8–13 (standing)**: `context_memory/` must NEVER output a
  BUY/SELL/entry/stop/target/size/execution/recommendation — evidence only. Must not import
  `decision_intelligence`/`signal_engine`/`scoring_engine`/`risk_manager`/`execution_engine`/
  `shadow_evidence`. Must not be wired into `harness.py`. The Checkpoint 12 relaxation ladder order and
  the Checkpoint 13 evidence-sufficiency policy must not be silently changed.
- **Phase 7 Decision Intelligence v2 + falsification study, Checkpoints 14–15 (standing, NEW this
  save)**: `decision_intelligence_v2/` must not change eligibility, ranking, scoring, Risk, Position
  Sizing, or Execution, must never generate a BUY/SELL/order-submission token, and
  `DecisionReportV2.__post_init__`'s own recommendation-equality invariant must never be relaxed or
  bypassed. `decision_comparison/` must remain read-only — never modifies v1, v2, or Context Memory's
  repository. The Checkpoint 15 verdict (`V1_REMAINS_ACTIVE`) must not be silently reinterpreted as "v2
  is better" without a genuinely new, separately-authorized study measuring a real difference on real
  data.
- **Phase 7 Checkpoint 16+ (Context Memory influencing a decision, real Context Memory historical
  population, Decision Intelligence v2 promotion to active status) must not begin without its own,
  separate, explicit CEO approval** — Checkpoint 15 being complete is not itself that approval; the
  CEO's own Checkpoints 14–15 batch authorization ends with an explicit stop instruction and names no
  next topic.
- No governance model, multi-position trading, Portfolio Orchestrator, Consensus Engine, Broker Adapter,
  or MT5 work without its own dedicated, separate CEO approval.

## G. Diagnostic artifacts preserved (cumulative)

`phase69_*.py`/`.json`, `relevance12m_*.py`/`.json`, `phase69a_*.py`/`.json`,
`phase610_prescope_analysis.py`/`.json`, `phase610_checkpoint1b_s10_validation.py`/`.json`,
`phase610_checkpoint1c_s10_validation.py`/`.json`. All committed, all deliberately preserved. Phase 7
Checkpoints 5 through 15 have no standalone diagnostic scripts — all validated entirely through their
own committed test suites (Context Memory: 221 tests; Decision Intelligence v2: 26 tests; Decision
Comparison: 24 tests).

## H. Exact next-session order

1. **Read this document in full first**, then `RECONSTRUCTION_PROMPT.md` (if starting fresh), then
   `PHASE_7_CHECKPOINT_15_REPORT.md`/`_14_REPORT.md`, then `PROJECT_STATE_v2.md` §8.
2. **Verify Git state directly** — `git branch --show-current`, `git log -1`, `git status --porcelain`.
3. **Report the reconstructed state back to the CEO** before proceeding on anything new.
4. Phase 6.10 is fully CLOSED; Phase 7 Checkpoints 5–15 are DONE; this checkpoint save is
   documentation-only. **Checkpoint 16 is NOT PROPOSED, NOT AUTHORIZED** — Decision Intelligence v1
   remains the sole active recommendation system. **Stop and ask before starting any further
   implementation.**

---

*Prior-session narrative history (Phases 6.1–6.9, Wave D, the Wave D Audit, the Strategy Health System's
own build, the Rolling Health-Gated Backtest, the Current XAUUSD 12-Month Relevance Audit, Phase 6.9A,
all of Phase 6.10, and Phase 7 Checkpoints 5–15) remains available in git history of this file
(`git log -p -- NEXT_SESSION.md`) and in each phase's own dedicated report/handoff document listed above.*
