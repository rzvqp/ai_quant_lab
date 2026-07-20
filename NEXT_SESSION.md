# NEXT_SESSION.md — Official Handoff (Single Entry Point)

**Rewritten in full on 2026-07-20 as an OFFICIAL PROJECT SAVE — the official bifurcation into two
independent, parallel development flows.** This is a state-of-project closing (per explicit CEO
instruction: "Aceasta este o închidere de stare, NU o schimbare de direcție"), not a pivot — the
existing AI Trader roadmap is unsuspended and continues exactly as planned; a second, wholly separate
research program is opened alongside it. No code was implemented, no backtest was run, and no existing
document's content was removed as part of this save. This document, together with `PROJECT_STATE_v2.md`
(the complete, consolidated state document, §1.1/§8.19/§8.20 cover this save's own scope),
`RECONSTRUCTION_PROMPT.md` (the single entry point for a genuinely new conversation), `CHANGELOG.md`,
and every phase's/study's own dedicated report, is designed to let a BRAND-NEW chat reconstruct this
project 100% with NO access to any prior conversation.

## ⚑ FIRST: which flow is this session continuing?

- **Flow A — Alpha Discovery Laboratory** (the systematic study of 40 raw Alpha Edge hypotheses) →
  read §1 below, then jump straight to the Flow-A reading list.
- **Flow B — AI Trader Development** (the pre-existing main roadmap) → read §1 below, then jump to the
  Flow-B reading list.

Both flows are independent and non-conflicting (§1) — a session can freely continue either one without
needing to touch or wait on the other.

---

## 1. The two flows (official, this save)

| | Flow A — Alpha Discovery Laboratory | Flow B — AI Trader Development |
|---|---|---|
| **Status** | **READY TO START** | **ACTIVE** |
| **What it is** | Systematic research on 40 raw, unvalidated Alpha Edge hypotheses — session-timing, price-action/structure, liquidity, mathematical, intermarket, and news-based ideas. Not strategies. Not believed true. | The pre-existing main roadmap: Market Scanner → ... → Phase 7 Intelligence Layer (Market/Edge/Decision Intelligence, Context Memory) → next steps below. |
| **Governing documents** | `EDGE_DISCOVERY_REGISTRY_v1.md` (the 40-edge backlog, all `UNSTUDIED`/`V0`), `EDGE_RESEARCH_PROTOCOL.md` (the one shared six-stage pipeline every edge must follow), `EDGE_DISCOVERY_ROADMAP.md` (recommended sequencing, data-gap-driven) | `PROJECT_STATE_v2.md` §1–§9, `PHASE_7_CHECKPOINT_*_REPORT.md` series |
| **First activity** | Begin systematic Discovery-stage study of the registry, starting from the Roadmap's Tier 1 (18 edges testable with data already on disk — pure-arithmetic and structure-pattern edges first) | Continue the roadmap: **Strategy Health (integration/promotion policy) → Portfolio Architect → Learning / Research Feedback → Risk Integration → Execution Integration → MT5 Live** |
| **What is NOT authorized by this save** | Skipping a protocol stage for any edge; optimizing an edge until profitable; implementing any edge as a strategy before it earns a Final Verdict AND a separate explicit CEO decision to implement | Beginning Strategy Health integration/promotion policy (or any later step) without its own explicit CEO authorization — same standing rule as every prior Phase 7 checkpoint |
| **Where it lives** | New root-level markdown only so far; a future `edge_research/E0XX_*.md` per-edge log directory once Discovery starts (not created yet) | `ai_trader/` (all modules, §9 of `PROJECT_STATE_v2.md`) |
| **Conflict with the other flow / with the frozen Research Lab** | **None** — touches no file inside `ai_trader/`, `code/`, `results/`, or `knowledge/` | **None** — unchanged from every prior save |

**Why no conflict is possible**: Flow A produces documents and (once Discovery starts) per-edge research
logs — it does not modify, read from, or write to any file `ai_trader/` owns, and produces no strategy,
no `RuntimeEvaluator`, no code change of any kind unless and until a specific edge separately earns
implementation authorization (at which point it would join Flow B's own Strategy Library like any of
S1–S51, not create a competing system). Flow B continues to own everything it already owned. Both flows
can run in the same session or in entirely separate sessions/conversations without coordination.

---

## Reading order — Flow A

1. **This document** — you are here; §1 above is the only Flow-A-relevant summary you need before
   diving in.
2. **`EDGE_DISCOVERY_ROADMAP.md`** — which edge(s) to start with (Tier 1, 18 edges testable with data
   already on disk) and why, plus the full data-availability gap analysis (M15 is the finest resolution
   that exists; no tick/M1 data; no DXY/US10Y/XAGUSD/USDJPY/SPX data; no economic calendar — 17 of 40
   edges are blocked on a data-acquisition decision not yet made).
3. **`EDGE_RESEARCH_PROTOCOL.md`** — the mandatory six-stage pipeline (V0 → Discovery → Frozen Candidate
   → Validation → Walk Forward → Final Verdict), the permanent-record rules (nothing ever deleted or
   retroactively edited — negative observations, exceptions, and falsifications are kept with the same
   weight as positive ones), the 9 mandatory Discovery questions, and the 5-verdict taxonomy.
4. **`EDGE_DISCOVERY_REGISTRY_v1.md`** — look up the specific edge(s) to start with: V0 hypothesis,
   category, required data/timeframes/instruments/observable variables/measured outcome.
5. **`PROJECT_STATE_v2.md` §1.1/§8.19/§8.20** — how Flow A relates to the rest of the project (context
   only; not required to start research).

**Before starting Discovery on any edge**: verify `git status --porcelain` is clean, confirm which
Roadmap tier the edge belongs to, and create that edge's own permanent research log
(`edge_research/E0XX_<slug>.md`, per `EDGE_RESEARCH_PROTOCOL.md` §6) before recording any finding.

---

## Reading order — Flow B

1. **This document** — the exact current state and the exact next-session procedure.
2. **`RECONSTRUCTION_PROMPT.md`** — if this is a genuinely new conversation, start there; it points
   back here with the exact verification steps to run first.
3. **`PHASE_7_CHECKPOINT_15_REPORT.md`** → **`PHASE_7_CHECKPOINT_14_REPORT.md`** — the current official
   architectural frontier: **Decision Intelligence v2** (`ai_trader/decision_intelligence_v2/`), a
   SEPARATE, additive system wrapping v1 (unmodified) with an explainable, per-candidate Context Memory
   evidence attachment, and the **v1-vs-v2 falsification study** (`ai_trader/decision_comparison/`),
   whose verdict is **`V1_REMAINS_ACTIVE`**.
4. **`PHASE_7_CHECKPOINT_13_REPORT.md`** → **`_12_`** → **`_11_`** → **`_10_`** → **`_9_REPORT.md`** →
   **`PHASE_7_CHECKPOINT_8_CONTEXT_MEMORY_DESIGN.md`** — the complete Context Memory subsystem.
5. **`PHASE_7_CHECKPOINT_7_REPORT.md`** → **`PHASE_7_CHECKPOINT_6_REPORT.md`** →
   **`PHASE_7_CHECKPOINT_5_REPORT.md`** — Decision Intelligence v1 built on Edge Intelligence built on
   Market Intelligence — still current, unmodified, and the SOLE ACTIVE recommendation system.
6. **`CEO_STRATEGY_CONSTRAINT_ROOT_CAUSE_REPORT.md`** → **`CEO_STRATEGY_PERFORMANCE_STUDY_REPORT.md`**
   → **`CEO_STRATEGY_PERFORMANCE_ATLAS.md`** — interim research (not a checkpoint) on why the six
   current A-Candidate strategies (S1, S13, S39, S40, S46, S48) are constrained: **all six verdict as
   PORTFOLIO-LIMITED**. Directly relevant background for the next Flow B step (Strategy Health
   integration/promotion policy).
7. **`PROJECT_STATE_v2.md`** — the complete state through Phase 6.9A, Phase 6.10 (CLOSED), Phase 7
   Checkpoints 5–15, the interim research studies (§8.19), and this fifth official save (§8.20/§1.1).
8. **`PHASE_6_10_EDGE_PORTFOLIO_DIRECTION.md`** — background only, see §B for disambiguation.
9. **`PHASE_6_10_PRE_SCOPE_DIAGNOSTIC.md`** → **`PHASE_6_10_SHADOW_EVIDENCE_ARCHITECTURE_DESIGN.md`** —
   background on Shadow Evidence's own design, if depth is needed.
10. In detail, if deeper Phase 6.9A background is needed: `PHASE_6_9_ROLLING_HEALTH_GATED_BACKTEST_REPORT.md`
    → `CURRENT_XAUUSD_12M_RELEVANCE_REPORT.md` → `PHASE_6_9A_STRATEGY_EVIDENCE_FLOW_AUDIT_REPORT.md`.
11. `ROLLING_HEALTH_BACKTEST_HANDOFF.md` for the Strategy Health System's own full methodology.

**Common to both flows**: `PROJECT_STATE_v1.0.md` (Research Lab's frozen state), `CHANGELOG.md`'s top
entries.

---

## B. Naming disambiguation — read before touching any of the five intelligence/evidence/comparison packages

Phase 6.10's "**Edge Portfolio**" (`shadow_evidence/`) is the multi-strategy Shadow virtual-execution
PLATFORM. Phase 7's "**Edge Intelligence**" (`edge_intelligence/`) is a read-only RECOGNITION layer.
Phase 7's "**Decision Intelligence v1**" (`decision_intelligence/`) answers "which edge, if any,
deserves execution" — the SOLE ACTIVE recommendation system. Phase 7's "**Context Memory**"
(`context_memory/`) stores/indexes/retrieves/aggregates HISTORICAL evidence, never evaluates the
present, never recommends. Phase 7's "**Decision Intelligence v2**" (`decision_intelligence_v2/`) is a
SEPARATE, additive wrapper around v1 that attaches Context Memory's evidence to v1's own, unmodified
recommendation. Phase 7's "**Decision Comparison**" (`decision_comparison/`) is a read-only framework
comparing v1 and v2 — it modifies neither. **Flow A's "Alpha Edge" / "Edge" (E001–E040) is a completely
different, unrelated concept from all of the above** — it means a raw, unimplemented research hypothesis
in `EDGE_DISCOVERY_REGISTRY_v1.md`, never a registered `strategy_id`/`RuntimeEvaluator` (that concept is
what Phase 6.10 calls an "edge," S1–S51). Do not conflate the two "edge" vocabularies across the two
flows.

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
index, a fixed-priority hierarchical-relaxation retrieval mechanism, and per-edge Contextual Evidence
Aggregation with a controlled sufficiency status. Never outputs a recommendation.

**Checkpoint 14** (`decision_intelligence_v2/`): calls v1's `make_decision()` UNCHANGED, then attaches a
per-candidate Context Memory evidence report. `DecisionReportV2.recommended_strategy_id` is
construction-time-forced to equal v1's own.

**Checkpoint 15** (`decision_comparison/`): builds the falsification comparison framework. Every
trade-outcome metric is provably identical between v1 and v2 under the current architecture.
Explanation quality and confidence calibration are the only genuinely-differing dimensions measured.
**Falsification verdict: `V1_REMAINS_ACTIVE`.**

**None of Checkpoints 5–15's packages trades, sizes a position, sends an order, or is wired into
`harness.py` or any execution path.**

## E. Interim research (Flow B background, not a checkpoint) — see `PROJECT_STATE_v2.md` §8.19

Strategy Historical Performance Study (6 A-Candidates identified: S1, S13, S39, S40, S46, S48) →
Strategy Constraint Root-Cause Study (all six verdict PORTFOLIO-LIMITED; recommendation: run a
controlled sizing experiment and a controlled portfolio-slot experiment, separately) →
`CEO_STRATEGY_PERFORMANCE_ATLAS.md` (all 43 strategies consolidated, with an Evidence Level A–E
confidence label). No production file modified by any of the three.

## F. Official Git state (verify live — do not trust blindly)

```
Repository path:  C:\Users\MEDION GAMING\ai_quant_lab-research-main
Branch:           ai-trader-implementation
HEAD (pre-save):  d60fa63 "docs: launch 40-Edge Alpha Discovery Program infrastructure"
Working tree:     clean (verified live before this save's own commit)
```

**Commits since the Checkpoints 14–15 save (`028b620`), in order:**
```
7c3eb62  research: preserve strategy historical performance study
2650c3b  research: diagnose candidate strategy constraints
f4eba6b  docs: enrich strategy performance atlas with evidence levels
d60fa63  docs: launch 40-Edge Alpha Discovery Program infrastructure
```

**This save's own commit** (this file, `PROJECT_STATE_v2.md`, `PROJECT_AUDIT.md`) lands ONE commit
after `d60fa63` — run `git log -1` for the exact current HEAD; do not assume it is still that commit in
any future session.

**Re-verify `git branch --show-current`/`git log -1`/`git status --porcelain` directly before trusting
any git-state claim anywhere in this project's documentation.**

**No new test run was needed for this save** — no code changed, so the Checkpoints 14–15 batch's own
full-repository validation (`pytest ai_trader/ -q` → 2101 passed; `mypy --strict` → clean, 222 source
files; coverage → 12087 stmts, 432 miss, 96%) remains the current, valid figure; re-run it directly if
any doubt exists before trusting it in a future session.

## G. What must NOT be modified (standing, cumulative — unchanged by this save)

- `code/`, `results/`, `knowledge/` (Research Lab) — frozen, 0-diff.
- Every strategy contract, evaluator, and parameter.
- `ai_trader/strategy_health/`'s own scoring methodology — frozen since its own build.
- Scoring Engine weights, Risk Policy, Execution Engine rules.
- The sealed terminal holdout (2025-10-23 09:15 UTC → 2026-07-13 06:00 UTC) — never opened.
- No strategy is ever permanently eliminated based on any AI Trader analysis to date.
- **Phase 6.10 (CLOSED)**: no edge/strategy-specific architecture in `shadow_evidence/`; no Strategy
  Health integration policy selected; no capital-allocation architecture designed.
- **Phase 7 Checkpoints 5–15 (standing)**: `market_intelligence/`, `edge_intelligence/`,
  `decision_intelligence/` (v1) must remain pure, no execution; v1 must never be modified to
  accommodate v2/the comparison framework; `decision_intelligence_v2/` must not change
  eligibility/ranking/scoring/Risk/Sizing/Execution and its recommendation-equality invariant must
  never be relaxed; `decision_comparison/`/`context_memory/` remain read-only; none of these packages
  may be wired into `harness.py` without its own explicit CEO approval; the `V1_REMAINS_ACTIVE` verdict
  must not be silently reinterpreted.
- **Phase 7 Checkpoint 16+ must not begin without its own, separate, explicit CEO approval** —
  Checkpoint 15 being complete is not itself that approval.
- **Flow A (new, this save)**: no edge may be optimized until profitable; no negative
  observation/exception/falsification may ever be removed from an edge's record; no hypothesis may be
  edited retroactively after seeing results (refinements are new, appended versions only); no protocol
  stage may be skipped; a Final Verdict never itself authorizes implementation.
- No governance model, multi-position trading, Portfolio Orchestrator, Consensus Engine, Broker Adapter,
  or MT5 work without its own dedicated, separate CEO approval.

## H. Diagnostic artifacts preserved (cumulative)

`phase69_*.py`/`.json`, `relevance12m_*.py`/`.json`, `phase69a_*.py`/`.json`,
`phase610_prescope_analysis.py`/`.json`, `phase610_checkpoint1b_s10_validation.py`/`.json`,
`phase610_checkpoint1c_s10_validation.py`/`.json`, `ceo_strategy_performance_study.py`+`.json`,
`ceo_strategy_constraint_root_cause_study.py`+`.json`. All committed, all deliberately preserved.

## I. Exact next-session order

1. **Decide which flow** (§1) — read that flow's list above.
2. **Verify Git state directly** — `git branch --show-current`, `git log -1`, `git status --porcelain`.
3. **Report the reconstructed state back to the CEO** before proceeding on anything new.
4. **Flow A**: begin Discovery on the Roadmap's Tier 1, one edge (or a small batch) at a time, creating
   that edge's own permanent research log before recording any finding.
   **Flow B**: Strategy Health integration/promotion policy is the next named step, but still requires
   its own explicit CEO authorization to begin — **stop and ask before starting any further
   implementation.**

---

*Prior-session narrative history (Phases 6.1–6.9, Wave D, the Wave D Audit, the Strategy Health System's
own build, the Rolling Health-Gated Backtest, the Current XAUUSD 12-Month Relevance Audit, Phase 6.9A,
all of Phase 6.10, Phase 7 Checkpoints 5–15, and the interim research studies) remains available in git
history of this file (`git log -p -- NEXT_SESSION.md`) and in each phase's/study's own dedicated
report/handoff document listed above.*
