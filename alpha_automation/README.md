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
- **Phase 2** — minimum working orchestrator: **done** (bounded runs + resume).
- **Phase 2.5** — TradingView Research Environment (TVRE): **done** — Alpha researches on the live
  TradingView instance (see below).
- **Phase 3** — candidate freeze/hash/handoff + duplicate/novelty gate + notification: *pending*.
- **Phase 4** — controlled continuous mode + endurance: *pending*.

## Phase 2.5 — TradingView Research Environment (`tv/`)

Alpha becomes an active researcher on the TradingView Desktop instance (dedicated to Alpha per CEO
decision 2026-07-22). Every action passes a **capability gate** (`tv/capabilities.py`) and is
**logged + linked** to the investigation (`tv/workspace.py`). Alpha may read the chart, indicators
and custom Pine output, navigate symbols/timeframes/replay, add research indicators, author Pine
research tools, draw research objects, and capture screenshots. Hard-denied: trades, broker,
alerts, and Strategy-Tester/backtest as edge evidence (also scanned in `boundaries.py`).

- **Data discipline** (`tv/mode.py`): `replay_pre_cutoff` (holdout-safe — replay anchored < cutoff,
  fail-closed cursor verification before every observation) or `live_observation` (tagged
  `live_post_holdout`, never validation). Selectable per run via `--research-mode`.
- **Observation Dossier** (`tv/dossier.py`): chart state + OHLCV + indicators + Pine
  lines/labels/tables/boxes + quote + bar-by-bar replay track + screenshots + optional numeric
  multi-TF context. Screenshots attach to the codex adapter via `-i` (multimodal).
- **Hybrid follow-ups** (`tv/environment.py`): Alpha may request a bounded number of extra
  observations (allowlisted verbs only); the orchestrator authorizes, executes, logs, and feeds
  them back for up to `max_followup_rounds`.
- **Node bridge** (`tv/bridge/tv_exec.mjs`): dispatches allowlisted verbs to tradingview-mcp's own
  `core/*` functions (batch-capable). A parity test keeps the bridge verbs ⊆ the capability registry.

Enable with `--use-tv-research`:
```bash
python -m alpha_automation.runner --use-tv-research --research-mode replay_pre_cutoff --adapter codex --max-passes 3
```
Known limits: the tradingview-mcp connection binds to one chart target, so multi-symbol/TF work is
sequential (panes/layouts), not parallel tabs (target-pinning enhancement deferred by CEO). Pine
compile/save is gated off by default (`tv_pine_apply`) since it may write to the account.

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
