# NEXT_SESSION_FLOW_B.md — AI Trader Development (Flow B)

**Scope of this document**: Flow B ONLY — AI Trader Development, the pre-existing main roadmap. Split
out of the former single `NEXT_SESSION.md` on 2026-07-20, per explicit CEO instruction, so Flow A and
Flow B each have their own operational document. Do not write Flow A (Alpha Discovery Laboratory)
content here — see `NEXT_SESSION_FLOW_A.md` for that. See `NEXT_SESSION.md` for the short, common
orientation pointer. This document, together with `PROJECT_STATE_v2.md` (the complete, consolidated
state document — §1.1/§8.19–§8.23 cover Flow B's current scope) and `RECONSTRUCTION_PROMPT.md`, is
designed to let a BRAND-NEW chat reconstruct Flow B's state 100% with no access to any prior
conversation.

---

## Cross-flow incident notice (2026-07-21) — TERMINAL HOLDOUT BREACHED

**Not a Flow B defect** — recorded here for visibility only, since the breached period is defined by
Flow B's own Research Lab documents. Flow A's first five studied edges loaded and analyzed data from
the Research Lab's sealed terminal holdout (2025-10-23 09:15 UTC → 2026-07-13 06:00 UTC). **The old
terminal holdout is CONSUMED / INVALIDATED** — it can no longer serve as an independent terminal
evaluation for the Research Lab or for Flow A. No Flow B file, script, or result was touched by the
breach or by this remediation entry; `ai_trader/`, `code/`, `results/`, and `knowledge/` all remain
0-diff. Full incident record: `PROJECT_STATE_v2.md` §8.23. Flow A is PAUSED for remediation
(`NEXT_SESSION_FLOW_A.md`) — this has no effect on Flow B's own roadmap or timeline.

## Current state

**Status: ACTIVE — roadmap step 1 of 6 (Strategy Health) IMPLEMENTED and validated, awaiting CEO
verdict before advancing to step 2.** Roadmap order, per explicit CEO instruction: **Strategy Health
(integration/promotion policy) → Portfolio Architect → Learning / Research Feedback → Risk Integration →
Execution Integration → MT5 Live.** `§8.18`'s own standing rule continues to govern exactly which step
may begin next: no further Phase 7 checkpoint, and no roadmap step, begins without its own explicit CEO
authorization. The CEO authorized implementation (verdict: mandatory five-state architecture NEW →
ACTIVE/WATCHLIST → PROBATION/DISABLED, Shadow Evidence active in every state, no absorbing lockout);
implementation is complete and fully validated (see `PROJECT_STATE_v2.md` §8.24 for the full record).
**Portfolio Architect (roadmap step 2) has NOT been authorized and has not begun.**

## Last Flow B commit

```
<FILLED IN AFTER COMMIT — see git log -1>  feat: implement Strategy Health Integration eligibility policy
```

Re-verify live before trusting this — `git log -1`, `git branch --show-current`, `git status
--porcelain` — do not assume it is still the current HEAD in any future session (Flow A and other work
may have landed commits since; as of this document's own creation, `eed1634` — a Flow A commit — landed
between `a53a3bc` and `b2a79fd`, i.e. Flow A and Flow B commits currently interleave on the same
branch).

## Strategy Health situation

Two different things share the name "Strategy Health," and both are now complete:

- **The Strategy Health SYSTEM** (scoring/classification: `ai_trader/strategy_health/types.py`/
  `metrics.py`/`scoring.py`/`classifier.py`/`evaluator.py`) — **COMPLETE**, built at Wave D, frozen
  since, **untouched by this implementation** (confirmed zero-diff). Computes a 0–100 Health Score and
  a 4-band classification (ACTIVE/WATCHLIST/PROBATION/DISABLED) for any strategy at any point in time.
- **The integration/promotion POLICY** (what a Health state actually does to the live/competitive
  portfolio) — **IMPLEMENTED**. New files: `ai_trader/strategy_health/shadow_gate.py` (the Eligibility
  Policy layer — `PolicyState` 5-state enum, `classify_policy_state`, `policy_states_at`,
  `real_eligible_strategy_ids_at`, all pure functions over Shadow Evidence's own trade ledger, zero new
  scoring logic, mirrors `rolling_gate.py`'s own established pattern) and a new, additive
  `health_eligible_ids: frozenset[str] | None = None` constructor parameter on
  `ai_trader.simulation.harness.SimulationHarness` (filters ONLY the opportunity list handed to the
  Risk Manager, strictly after Signal/Scoring Engine and the Shadow Evidence tap have both already run
  unfiltered — deliberately NOT a reuse of `strategy_id_filter`, which would starve Shadow Evidence and
  recreate the Phase 6.9 lockout). Full contract, test results, and validation record:
  `PROJECT_STATE_v2.md` §8.24.

## Approved design and remaining conditions

`STRATEGY_HEALTH_INTEGRATION_POLICY_DESIGN.md` (FINAL, §§1–15) — **CEO verdict: ACCEPTED WITH
CONDITIONS.** Five confirmed principles: Strategy Health stays a separate evaluation system; frozen
modules stay frozen; Shadow Evidence is the primary new-evidence source; Phase 6.9's ACTIVE-only
lockout must not repeat; reuse existing infrastructure where sufficient.

Five architectural clarifications were required before implementation and have been delivered, added to
the same document as §§11–15:

1. **Explicit lifecycle** (§11) — five states as a bidirectional state machine: `NEW` (a policy-layer
   label only, derived from the frozen classifier's own existing "no evidence → WATCHLIST" default,
   never a fifth classifier band) → `WATCHLIST` → `ACTIVE` → `PROBATION` → `DISABLED`, each with
   precise entry/exit conditions.
2. **Per-state influence, zero ambiguity** (§12) — ACTIVE and WATCHLIST both retain full
   real-portfolio competition (unchanged from today); **PROBATION and DISABLED are both Shadow-only**
   (excluded from new REAL trades, but Shadow Evidence tracking continues unconditionally for both).
   This refined the original v1 recommendation, which had only excluded DISABLED.
3. **Module contracts** (§13, interfaces only, no implementation) — Shadow Evidence → Strategy Health
   (unconditional, per-strategy, read-only) → a new Eligibility Policy layer (not yet built) →
   `harness.py`'s existing `strategy_id_filter`. Risk Manager's own contract is unchanged. No contract
   to Decision Intelligence in v1 (flagged as a future open question, not resolved).
4. **Non-absorbing recovery** (§14) — the load-bearing invariant: Shadow Evidence tracks every
   strategy, in every state, forever, so PROBATION/DISABLED strategies keep accumulating genuine new
   evidence and can recover (PROBATION→WATCHLIST at ≥45, DISABLED→PROBATION at ≥25) via real improved
   Shadow performance, never via a timer or evidence expiring.
5. **Performance-impact argument** (§15, structural, not empirical — no backtest has been run) — the
   lockout mechanism is broken by construction; the exact real-eligible roster under Shadow-sourced
   scoring is explicitly not claimed without a live recomputation.

**Remaining condition — SATISFIED**: the CEO confirmed the clarified architecture and explicitly
authorized implementation (mandatory five-state architecture, frozen-module list, implementation scope,
12 required tests, validation checklist — see `PROJECT_STATE_v2.md` §8.24 for the verbatim record).
Implementation is now complete and validated per that authorization.

## Next Flow B step

**Strategy Health Integration (roadmap step 1/6) is implemented and validated — awaiting CEO verdict on
whether it may be declared COMPLETE.** `health_eligible_ids=None` (the default) is proven byte-identical
to pre-existing competitive execution across the full validation suite, including the 43-production-
strategy run. **Portfolio Architect (roadmap step 2) must not begin without its own separate, explicit
CEO authorization** — the implementation being validated is not itself that authorization.

## Resume instructions

1. Re-verify git state live: `git branch --show-current`, `git log -1`, `git status --porcelain`.
2. Read, in this order:
   - **This document** — current state, summarized above.
   - **`RECONSTRUCTION_PROMPT.md`** — if this is a genuinely new conversation, start there.
   - **`STRATEGY_HEALTH_INTEGRATION_POLICY_DESIGN.md`** (FINAL, §§1–15) — the current, immediate
     frontier. Read this FIRST if continuing the current roadmap step.
   - **`PHASE_7_CHECKPOINT_15_REPORT.md`** → **`PHASE_7_CHECKPOINT_14_REPORT.md`** — Decision
     Intelligence v2 (additive, wraps v1 unmodified, attaches Context Memory evidence) and the
     v1-vs-v2 falsification study (verdict: `V1_REMAINS_ACTIVE`).
   - **`PHASE_7_CHECKPOINT_13_REPORT.md`** → **`_12_`** → **`_11_`** → **`_10_`** → **`_9_REPORT.md`**
     → **`PHASE_7_CHECKPOINT_8_CONTEXT_MEMORY_DESIGN.md`** — the complete Context Memory subsystem.
   - **`PHASE_7_CHECKPOINT_7_REPORT.md`** → **`PHASE_7_CHECKPOINT_6_REPORT.md`** →
     **`PHASE_7_CHECKPOINT_5_REPORT.md`** — Decision Intelligence v1 built on Edge Intelligence built
     on Market Intelligence — still current, unmodified, and the SOLE ACTIVE recommendation system.
   - **`CEO_STRATEGY_CONSTRAINT_ROOT_CAUSE_REPORT.md`** → **`CEO_STRATEGY_PERFORMANCE_STUDY_REPORT.md`**
     → **`CEO_STRATEGY_PERFORMANCE_ATLAS.md`** — interim research (not a checkpoint) on why the six
     current A-Candidate strategies (S1, S13, S39, S40, S46, S48) are constrained: all six verdict as
     PORTFOLIO-LIMITED. Directly cited by the Strategy Health design's own diagnosis of Phase 6.9's
     failure mechanism.
   - **`PROJECT_STATE_v2.md`** — the complete state through Phase 6.9A, Phase 6.10 (CLOSED), Phase 7
     Checkpoints 5–15, the interim research studies (§8.19), the official Flow A/B bifurcation
     (§8.20/§1.1), and the Strategy Health design proposal + its acceptance (§8.21/§8.22).
   - **`PHASE_6_10_EDGE_PORTFOLIO_DIRECTION.md`** — background only, see the naming-disambiguation
     warning below.
   - **`PHASE_6_10_PRE_SCOPE_DIAGNOSTIC.md`** → **`PHASE_6_10_SHADOW_EVIDENCE_ARCHITECTURE_DESIGN.md`**
     — background on Shadow Evidence's own design (its evidence-source data feeds the Strategy Health
     design's recommended approach).
   - **`PHASE_6_9_ROLLING_HEALTH_GATED_BACKTEST_REPORT.md`** — the one prior Strategy Health
     integration attempt, and precisely why it failed (essential reading before implementing the new
     design; already summarized in `STRATEGY_HEALTH_INTEGRATION_POLICY_DESIGN.md` §3) →
     `CURRENT_XAUUSD_12M_RELEVANCE_REPORT.md` → `PHASE_6_9A_STRATEGY_EVIDENCE_FLOW_AUDIT_REPORT.md` for
     deeper background if needed.
   - `ROLLING_HEALTH_BACKTEST_HANDOFF.md` for the Strategy Health System's own full methodology.
   - `PROJECT_STATE_v1.0.md` for the Research Lab's own frozen state.
   - `CHANGELOG.md`'s own top entries for verified, dated, session-by-session detail.
3. Report the reconstructed state back to the CEO before proceeding on anything new.

## Warnings relevant to implementation

- **Portfolio Architect (roadmap step 2) must not begin without its own separate, explicit CEO
  authorization** — Strategy Health Integration being implemented and validated is not itself that
  authorization.
- `code/`, `results/`, `knowledge/` (Research Lab) — frozen, 0-diff, confirmed at every close to date.
- Every strategy contract, evaluator, and parameter.
- `ai_trader/strategy_health/`'s own scoring methodology — frozen since its own build; confirmed 0-diff
  by this implementation (`types.py`/`metrics.py`/`scoring.py`/`classifier.py`/`evaluator.py`). The new
  Eligibility Policy layer (`shadow_gate.py`) is additive only, per the CEO's own mandatory scope.
- Scoring Engine weights, Risk Policy, Execution Engine rules — the Strategy Health design's own v1
  recommendation touches none of these; any future escalation to risk-scaled sizing or ranking-priority
  integration requires its own separate, explicit CEO decision to unfreeze the relevant module.
- The sealed terminal holdout (2025-10-23 09:15 UTC → 2026-07-13 06:00 UTC) — never opened.
- No strategy is ever permanently eliminated based on any AI Trader analysis to date.
- **Phase 6.10 (CLOSED)**: no edge/strategy-specific architecture in `shadow_evidence/`; no capital-
  allocation architecture designed (still out of scope).
- **Phase 7 Checkpoints 5–15 (standing)**: `market_intelligence/`, `edge_intelligence/`,
  `decision_intelligence/` (v1) must remain pure, no execution; v1 must never be modified to
  accommodate v2/the comparison framework; `decision_intelligence_v2/` must not change
  eligibility/ranking/scoring/Risk/Sizing/Execution and its recommendation-equality invariant must
  never be relaxed; `decision_comparison/`/`context_memory/` remain read-only; none of these packages
  may be wired into `harness.py` without its own explicit CEO approval; the `V1_REMAINS_ACTIVE` verdict
  must not be silently reinterpreted.
- **Phase 6.10 Checkpoint 1C** (the one Shadow Evidence finding worth re-reading carefully): its own
  S10 isolated-ledger validation found a real divergence from Phase 6.9A's independently-verified
  isolated-run ground truth. CEO ruling, binding on all future work in `shadow_evidence/` (including
  the new Strategy Health Shadow-sourced evidence path): this is a **documented semantic limitation,
  not a defect** — "Shadow Evidence evaluates how a configured strategy would execute from the
  conflict-adjusted `score_batch` produced inside the competitive run," not a truly isolated result.
  Disclose this caveat wherever Shadow-sourced Health scores are reported.
- **Phase 7 Checkpoint 16+ must not begin without its own, separate, explicit CEO approval** —
  Checkpoint 15 being complete is not itself that approval.
- No governance model, multi-position trading, Portfolio Orchestrator, Consensus Engine, Broker
  Adapter, or MT5 work without its own dedicated, separate CEO approval.
- **Naming**: Phase 6.10's "Edge Portfolio" (`shadow_evidence/`) is the multi-strategy Shadow
  virtual-execution PLATFORM. Phase 7's "Edge Intelligence" (`edge_intelligence/`) is a read-only
  RECOGNITION layer. "Decision Intelligence v1" (`decision_intelligence/`) is the SOLE ACTIVE
  recommendation system. "Context Memory" (`context_memory/`) stores/retrieves HISTORICAL evidence,
  never recommends. "Decision Intelligence v2" (`decision_intelligence_v2/`) is a SEPARATE, additive
  wrapper around v1. "Decision Comparison" (`decision_comparison/`) is read-only, modifies neither v1
  nor v2. **Flow A's "Alpha Edge" / "Edge" (E001–E040) is unrelated** — a raw research hypothesis, never
  a registered `strategy_id`/`RuntimeEvaluator`. Do not conflate the two "edge" vocabularies.
- **No branch or worktree separation exists yet** — Flow A and Flow B currently share one branch
  (`ai-trader-implementation`) and one working tree. A concurrent Flow A (or other) session may be
  editing shared files at the same time; verify git state live before assuming any prior session's
  described state still holds, and stage/commit only files this flow's own session actually authored.

## Reference: diagnostic artifacts preserved (cumulative, all committed)

`phase69_*.py`/`.json`, `relevance12m_*.py`/`.json`, `phase69a_*.py`/`.json`,
`phase610_prescope_analysis.py`/`.json`, `phase610_checkpoint1b_s10_validation.py`/`.json`,
`phase610_checkpoint1c_s10_validation.py`/`.json`, `ceo_strategy_performance_study.py`+`.json`,
`ceo_strategy_constraint_root_cause_study.py`+`.json`. All committed, all deliberately preserved for
reproducibility.
