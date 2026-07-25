# AI Trader — Next Session Orientation

**Last updated**: 2026-07-25. Read this file FIRST in any new session working on AI Trader. It tells you
exactly where things stand, what not to redo, and what to check before touching anything.

## 1. Where to resume

Phases 1-10 are built, tested, and closed. The **BTCUSD Phase 10 operational test is ACCEPTED and
CLOSED** — the send path is proven end-to-end, once, manually. **The Knowledge Transfer Audit is
complete**, verdict **NOT READY** for continuous DEMO (no live signal source exists; zero Research-Lab
edges are code-linked into the live decision chain). **This official-save task itself is now closing** —
read `AI_TRADER_PROJECT_STATE.md` for the full current-state narrative, then the other 5
`AI_TRADER_*.md` documents for their respective angles (audit breakdown, component inventory, test
status, decisions log).

**Stated next step** (CEO, 2026-07-25): once XAUUSD's market reopens Monday, continue exclusively on
XAUUSD, DEMO account — but this requires its own explicit go-ahead, and structurally cannot happen yet
regardless (no live signal source exists — see §7 of `AI_TRADER_PROJECT_STATE.md`). **Do not treat
"Monday" as a standing authorization to start anything without the CEO explicitly saying so in that
session.**

**Audit sequence stated by the CEO**: Knowledge Transfer Audit (done) → Decision Logic Audit → Risk Audit
→ Demo Readiness Audit. None of the remaining three has started.

## 2. What is CLOSED — do not redo

- Phases 1-10 (broker adapter through MT5 demo execution). Do not re-implement, re-design, or "improve"
  any of them without a demonstrated bug and explicit authorization — this was the standing rule for the
  entire Phases 2-10 sequence and remains in force.
- The BTCUSD operational test and its 5-attempt history. Do not re-run it "to be sure" — it already
  succeeded and was explicitly accepted; a real order was placed, confirmed, and closed. Re-running it
  would place another real (if small) order without new authorization.
- The comment-length fix (`_COMMENT_MAX_LENGTH = 27`) — already applied, tested, and documented. Do not
  "restore" it to 31 or otherwise touch `request_builder.py` without a new, demonstrated reason.
- The Knowledge Transfer Audit — complete, verdict recorded. Do not re-run it from scratch; if new
  Research-Lab work lands on this branch later, a *follow-up* audit citing what changed would be
  appropriate, not a full redo.

## 3. What is NOT authorized — do not start without explicit go-ahead

- Continuous / unattended DEMO execution.
- Any code that constructs a live `CandidateSignal` (i.e., any real signal source) — building this is
  the single biggest step toward actual live trading and has not been requested yet.
- The 5%-equity-risk dynamic sizing implementation — design only exists
  (`RISK_SIZING_5PCT_XAUUSD_DESIGN.md`), uncommitted, with 5 open decisions the CEO has not yet answered.
  **Do not write any code for this until those decisions come back.**
- Decision Logic Audit, Risk Audit, Demo Readiness Audit.
- Alpha 1, Alpha 2, Red Team, Statistician, or Validation Engine work of any kind from this repo/session.
- Treating BTCUSD as anything other than a one-time infrastructure-validation exercise.
- Any LIVE or CONTEST account interaction (also structurally impossible by design, not just policy).

Full authoritative list with CEO quotes: `AI_TRADER_DECISIONS.md`.

## 4. Documents to read in a new chat, in order

1. `AI_TRADER_PROJECT_STATE.md` — full current-state narrative (architecture, phases, MT5/Telegram
   integration, XAUUSD/BTCUSD distinction, DEMO execution state, limitations, tech debt, unvalidated
   items).
2. `AI_TRADER_DECISIONS.md` — what's authorized vs not, with CEO quotes.
3. `AI_TRADER_PROJECT_AUDIT.md` — implemented/tested/validated/documented-only/not-audited/not-authorized
   breakdown, plus the Alpha/Red-Team/Statistician/Validation-Engine spot-check.
4. `AI_TRADER_COMPONENT_INVENTORY.md` — per-component file/class/responsibility/I-O/dependencies/tests.
5. `AI_TRADER_TEST_STATUS.md` — test counts, regression results, the BTCUSD operational-test chronology,
   secrets sweep result.
6. `AI_TRADER_KNOWLEDGE_TRANSFER_AUDIT.md` — the full Research-Lab-to-AI-Trader transfer audit (why the
   verdict is NOT READY, in detail).
7. If picking up the risk-sizing thread specifically: `RISK_SIZING_5PCT_XAUUSD_DESIGN.md` (uncommitted —
   check `git status` first, it may not exist yet if this file was later committed or discarded).
8. `AI_TRADER_PHASES_2_10_FINAL_REPORT.md` and `BTCUSD_PHASE10_OPERATIONAL_TEST_REPORT.md` for full
   narrative detail beyond the summaries in `AI_TRADER_PROJECT_STATE.md`.

Older, Research-Lab-side documents (`PROJECT_STATE_v2.md`, `PROJECT_AUDIT.md`, `NEXT_SESSION.md`,
`RECONSTRUCTION_PROMPT.md`, `EDGE_DISCOVERY_REGISTRY_v1.md`, `STRATEGY_REGISTRY.md`,
`CEO_STRATEGY_PERFORMANCE_ATLAS.md`) are relevant only if the next task is Research-Lab-side or another
Knowledge-Transfer-style audit — not needed to resume AI Trader engineering itself.

## 5. Git checks to run before doing anything

```bash
git status --short           # confirm working tree is clean, or see exactly what's pending
git log --oneline -5         # confirm you're looking at the commit you think you are
git branch --show-current    # confirm you're on ai-trader-implementation
git remote -v                # confirm remote state (none configured as of this save — see below)
```

**Remote**: none configured (`git remote -v` returns empty) as of this save. If a remote has since been
added, do not push without explicit authorization — pushing was explicitly deferred in this session even
had a remote existed.

## 6. Information that exists only in prior conversation, not fully confirmed in the repository

- The exact wording of the CEO's various Romanian authorization messages is paraphrased/quoted from
  memory in the `AI_TRADER_*.md` documents where load-bearing, but the repo itself has no chat-log
  artifact — if verbatim wording ever matters legally/procedurally, it is not recoverable from the repo
  alone.
- The real-world timing/reason for AlgoTrading being manually enabled in the MT5 terminal UI (a CEO
  action, not a repo action) is documented in prose but has no corresponding repo artifact beyond the
  test's own before/after behavior.
- Why the terminal holdout breach happened procedurally (`edge_research/_common.py::load()` lacking a
  date cutoff) is documented in `PROJECT_STATE_v2.md` on the Research-Lab side; this AI-Trader-side
  document set does not re-verify that root cause independently, only cites it.
- Full verbatim justification for each individual audit-sequence step (why Decision Logic before Risk
  before Demo Readiness) was stated conversationally by the CEO but is only summarized, not quoted in
  full, in `AI_TRADER_DECISIONS.md`.
