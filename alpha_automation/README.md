# Alpha Automation v1.0

Persistent, autonomous **Continuous Discovery** orchestrator for the **Alpha** research
division of the AI Quant Lab. It turns Alpha from a manually-prompted chat workflow into a
restartable research loop that generates a research perspective, selects an investigation and a
market window, obtains data, invokes Alpha through a structured adapter, validates the response
against a schema, and persists the result — repeating without manual "continue".

> **Scientific boundary (unchanged from Alpha's charter, `EDGE_RESEARCH_PROTOCOL.md`):** Alpha
> **observes, compares, questions, and produces Discovery Candidates only.** It does **not**
> validate profitability, optimize parameters, run backtests as proof of edge, design
> strategies, or claim causality. "No candidate" (a NEGATIVE finding) is the normal, expected
> outcome. Strategies may emerge later from *validated* discoveries — Alpha does not jump there.

## Delivery status

- **Phase 1** — reconstruction & design: **accepted** by CEO.
- **Phase 2** — minimum working orchestrator: **this delivery** (bounded runs + resume).
- **Phase 3** — candidate freeze/hash/handoff + duplicate/novelty gate + notification: *pending*.
- **Phase 4** — controlled continuous mode + endurance: *pending*.

## Architecture (Phase 2)

```
PerspectiveGenerator ─▶ ResearchTaskSelector ─▶ MarketWindowSelector ─▶ DataAccess ─▶ AlphaAdapter ─▶ ResearchMemory
   (rotates the           (precise question,        (seeded, non-          (live TV     (codex | stub,   (append-only
    whole stance)          de-duped)                 overlapping,           primary;     strict JSON      JSONL +
                                                     holdout-safe)          CSV fallback) contract)       indexes)
```

- **Perspective Generator** (`perspective.py`) — deterministically rotates the *entire* research
  stance (lens × style × framing × regime) so the loop never converges on one investigation
  style. Distinct component from task selection (CEO refinement #3).
- **Research Task Selector** (`task_selector.py`) — picks a precise, answerable, descriptive
  question *within* the current perspective; avoids re-asking a near-duplicate question.
- **Market Window Selector** (`window_selector.py`) — seeded, reproducible, non-overlapping,
  never crosses the holdout cutoff.
- **Data Access** (`data_access.py`) — **live TradingView Desktop primary** (Node bridge in
  `bridge/tv_pull.mjs`, reusing tradingview-mcp), **local CSV fallback** (CEO refinement #1).
- **Alpha Adapter** (`adapters/`) — backend-agnostic. `codex` shells out to the local `codex
  exec` CLI (no external Python SDK, CEO refinement #2); `stub` is deterministic for dry-run and
  tests. Output is validated against `schemas/alpha_response.schema.json` and scanned for
  boundary-violating language (`boundaries.py`).
- **Research Memory** (`memory.py`) — append-only JSONL ledgers (source of truth) + rebuilt
  indexes; distinguishes internal records / negatives / tentative observations / candidate
  proposals; survives restart.
- **Runner** (`runner.py`) — bounded loop, atomic checkpoint per pass, resume, graceful
  shutdown, bounded retries, consecutive-failure circuit breaker, wall-clock ceiling, dry-run.

## Usage

```bash
# from the worktree root, using the lab venv (has pandas):
python -m alpha_automation.runner --dry-run --max-passes 3            # no data, no external calls
python -m alpha_automation.runner --adapter stub --data-source csv --max-passes 5
python -m alpha_automation.runner --resume R-20260721T101500Z          # resume an interrupted run
```

Config precedence: built-in defaults → optional `--config file.json` → CLI flags. See
`config.example.json`.

## State layout (`state/`, git-ignored)

```
state/
  id_allocator.json
  runs/<run_id>/{run_state.json, run.log.jsonl}
  memory/{investigations,negatives,tentative,candidates_proposed,
          questions_asked,windows_reviewed,perspectives}.jsonl
```

## Tests

```bash
"<lab venv>/Scripts/python.exe" -m pytest tests/alpha_automation -q
```

## Known Phase-2 limitations (carried to later phases / risks)

- Candidate **freeze/hash/handoff** and the **duplicate/novelty gate** are Phase 3;
  `CANDIDATE_PROPOSED` outcomes are recorded to `candidates_proposed.jsonl` and left for the gate.
- **Notification** policy is Phase 3.
- **Continuous mode** and endurance controls are Phase 4; Phase 2 is bounded by `--max-passes`.
- Checkpoint is written immediately after each pass is persisted; a crash in the narrow window
  between the memory append and the state write could re-run one pass on resume (at-least-once).
- The live data path requires TradingView Desktop with CDP on port 9222; otherwise CSV fallback.
