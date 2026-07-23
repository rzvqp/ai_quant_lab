# Recognition Engine — Phase 0: Repository Diagnostics

**Status**: DIAGNOSTIC ONLY, per explicit CEO authorization (2026-07-23). No production code was written or
modified, no contract was changed, no test was run, and Recognition Engine itself was not implemented.
This was a pure read-only investigation: source inspection (`grep`/`find`) and a repository-wide search
for persisted data files — no script executed, nothing written to disk by this diagnostic beyond this
report.

**Objective** (verbatim from the CEO's authorization): inventory existing `Outcome`/`PositionOutcome`
records; determine how many are complete/usable; analyze their distribution across contexts and edges;
estimate whether the current data population is sufficient for Recognition Engine to produce useful
verdicts rather than uniform `INSUFFICIENT_EVIDENCE`; recommend **READY FOR IMPLEMENTATION** or **COLLECT
MORE DATA FIRST**.

---

## 1. Method

Context Memory's `Outcome`/`PositionOutcome` records live in an append-only JSONL repository
(`ai_trader/context_memory/repository.py`, `_JsonlStream`, 5 streams: `context_snapshots.jsonl`,
`observations.jsonl`, `outcomes.jsonl`, `operational_metadata.jsonl`, `interim_realizations.jsonl` +
`position_outcomes.jsonl`, the last two/six added by Learning/Research Feedback Sprint 1/2). Rather than
writing a new instrumentation script (which itself would be a form of new code, and the CEO's own
authorization asked for an inventory of what EXISTS, not a fresh simulation run), this diagnostic went
straight to the two questions that settle the matter:

1. **Where would such a repository's data files physically live, if any run had ever produced one?**
   Searched the entire repository tree (excluding `venv/`, `.git/`) for any directory resembling a Context
   Memory repository root, and for every `*.jsonl` file anywhere outside `tests/`.
2. **Does any production code path ever actually open a real (non-test, non-`tmp_path`) `ContextMemoryRepository`?**
   Traced `ContextMemoryRepository`'s only production constructor call site and every caller above it, up
   to the harness's own public API and every root-level pipeline/backtest script in the repository.

## 2. Findings

**(a) No Context Memory JSONL files exist anywhere in the repository outside test directories.** The six
expected stream files (`context_snapshots.jsonl`, `observations.jsonl`, `outcomes.jsonl`,
`operational_metadata.jsonl`, `interim_realizations.jsonl`, `position_outcomes.jsonl`) were not found
anywhere. The only `*.jsonl` files present at repo scope belong to a completely unrelated system — the
Research Lab's own knowledge/hypothesis registry (`KNOWLEDGE_REGISTRY.jsonl`,
`knowledge/BEHAVIOR_REGISTRY.jsonl`, `knowledge/experiments/EXPERIMENT_REGISTRY.jsonl`,
`knowledge/generator/GENERATED_HYPOTHESES_v1.jsonl`, `knowledge/ontology/GENERATED_HYPOTHESES.jsonl`,
`knowledge/ontology/KNOWLEDGE_GRAPH.jsonl`) — different record shape entirely (`id`/`hypothesis_id`/
`knowledge_id`/`kind` keys, not the Context Memory envelope's `record_id`/`sequence`/`payload` shape),
confirmed unrelated by inspection.

**(b) No production code path ever supplies a real repository path.** `ContextMemoryRepository.__init__`
(`ai_trader/context_memory/repository.py:436`) takes a caller-supplied `root_path: Path` — no default, no
hardcoded location anywhere in the class itself. The only production construction site is
`ai_trader/simulation/harness.py:255`:
```python
if learning_feedback_repository_path is not None:
    self._lf_repo = ContextMemoryRepository(learning_feedback_repository_path)
```
guarded by a parameter (`SimulationHarness.__init__`, `harness.py:106`) that **defaults to `None`** — the
harness's own docstring states this explicitly (`harness.py:175-176`): with the default, "Learning/
Research Feedback is completely inert this run." `learning_feedback/capture.py`'s every capture function
takes `repository: ContextMemoryRepository` as a caller-supplied argument (never constructs or paths one
itself) — pure injection, by design, matching the Learning/Research Feedback isolation discipline recorded
in `PROJECT_STATE_v2.md` §8.27.

**Critically**: `grep -rn "learning_feedback_repository_path"` across the entire repository, excluding
`harness.py` itself and `tests/`, returns **zero matches** — not in `ai_trader/simulation/api.py` (the
harness's own public production entry point, which constructs `SimulationHarness(context,
self._symbol_meta, self._data_dir)` with no such argument), and not in any root-level pipeline/backtest
script (`phase69_*.py`, `phase610_*.py`, `relevance12m_*.py`, `ceo_strategy_*.py`,
`portfolio_architect_*.py`, etc. — none of these predate Learning Feedback's own existence, and none was
ever updated to pass this parameter). Every historical simulation run in this repository's history — Wave
D, Phase 6.9, the relevance audit, Phase 6.9A, every Phase 6.10 checkpoint, every Phase 7 checkpoint, every
Strategy Health/Portfolio Architect run — necessarily ran with Learning Feedback capture INERT, because the
capability did not exist yet at the time of most of them, and even after Phase F/Sprint 2 built it, no
caller has ever turned it on outside of tests (which use `tmp_path`, discarded at test-process exit).

## 3. Answers to the 4 required questions

1. **Inventory of existing `Outcome`/`PositionOutcome` records: ZERO.** Not "sparse" — genuinely zero,
   confirmed by the absence of any repository data file anywhere the code could have written one, and by
   the absence of any production call site that ever supplied a path for one to be written to.
2. **How many are complete/usable: N/A** — there is nothing to assess completeness of.
3. **Distribution across contexts and edges: N/A** — there is no distribution to analyze; the population
   is empty in every dimension simultaneously (no `strategy_id`, no `OutcomeKind`, no context signature, no
   time range).
4. **Is the current data population sufficient for Recognition Engine to produce useful verdicts: NO.**
   With zero underlying `Outcome` records, `evidence.aggregate_evidence()` (Checkpoint 13, unmodified)
   would return `EvidenceStatus.UNAVAILABLE` for every `(context, strategy_id)` pair with the reason
   `"strategy_id=... was not PRESENT in any retrieved episode"` or an equivalent no-history reason — every
   single `RecognitionReading` the design document's own `classify()` function (§9 of
   `RECOGNITION_ENGINE_DESIGN.md`) would ever produce today collapses to `UNAVAILABLE`. This is exactly
   the failure mode Maturity Verdict item 1 in that design document flagged as a real risk before
   authorizing implementation — now confirmed, not merely suspected.

## 4. Root cause (why the population is zero, not just currently low)

This is not a data-collection lag (e.g. "the pipeline has been running for a week and just needs more
time") — it is that **the pipeline has never been turned on in any production or research run.** Turning
it on requires one explicit, currently-nonexistent wiring step: some caller (most likely
`ai_trader/simulation/api.py`, or a dedicated new backtest/replay script) must supply a real
`learning_feedback_repository_path` to `SimulationHarness`, then run it — over live data, a replay, or a
historical backtest window — for Outcome/PositionOutcome records to begin accumulating at all. Nothing in
this diagnostic implemented that step (explicitly out of scope, per the CEO's own rules 5-7); it is
identified here only as the necessary precondition for "collect more data" to mean anything concrete.

Two realistic sources exist once wiring happens, per `PROJECT_STATE_v2.md` §8.27: **`PORTFOLIO`-kind**
Outcomes from the real competitive portfolio (rare — the single-shared-slot architecture already measured,
Phase 6.9A, only ~0.48% of opportunities ever reach a real ALLOW) and **`STRATEGY`-kind** Outcomes from
Shadow Evidence (far denser — every one of the 43 registered strategies accumulates independently, the
same reasoning that made Strategy Health choose Shadow as its own evidence source, `shadow_gate.py`).
Recognition Engine's own design document (§4) already anticipated `STRATEGY`/Shadow as "the realistic
default" for exactly this reason.

## 5. Recommendation

**COLLECT MORE DATA FIRST.**

This is not a judgment that the Recognition Engine architecture is flawed — `RECOGNITION_ENGINE_DESIGN.md`
was accepted on its own merits and nothing in this diagnostic contradicts it. It is a factual finding that
implementing it today would produce a system that is, by construction, 100% `UNAVAILABLE` on every
verdict — architecturally honest (the system would correctly refuse to fabricate confidence it doesn't
have) but practically useless, and unable to validate even the classification-threshold question
(Maturity Verdict item 2 of the design document) since there would be no real evidence to calibrate
against.

**Concrete precondition before re-attempting this diagnostic**: wire `learning_feedback_repository_path`
into at least one real run (most plausibly a Shadow-Evidence-enabled backtest over a meaningful historical
window, given `STRATEGY`-kind density) and let it accumulate. This wiring decision and the run itself are
NOT authorized by this diagnostic and are not proposed for immediate action here — they require their own
explicit CEO decision (which window, which strategy set, real-portfolio vs. Shadow vs. both, and whether
this itself needs a Sprint-style design review given it touches how a production entry point is called) —
this report only identifies the precondition, per the CEO's own scope boundary for Phase 0 (diagnostics
only, no implementation).

**No code was written. No contract was changed. Recognition Engine was not implemented.**
