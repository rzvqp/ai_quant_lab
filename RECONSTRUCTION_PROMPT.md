# RECONSTRUCTION_PROMPT.md

**Purpose**: this is a literal, self-contained prompt. Paste its contents (everything below the `---`)
into a brand-new Claude conversation, pointed at this repository, to reconstruct full project context
with no other input. It is kept up to date at every official checkpoint save — if you are reading this
file directly rather than pasting it, treat it the same way: follow the instructions below yourself.

---

Repository: `ai_quant_lab-research-main`

Before doing anything else, read, in this exact order:

1. `NEXT_SESSION.md` (in full) — the current, authoritative handoff document.
2. `RECONSTRUCTION_PROMPT.md` itself, if you have not already (this file) — it points back to
   `NEXT_SESSION.md` and lists the verification steps below.
3. `PHASE_7_CHECKPOINT_6_REPORT.md` then `PHASE_7_CHECKPOINT_5_REPORT.md` (in full) — the current
   official architectural frontier: Edge Intelligence (which registered strategies' edges currently
   exist) built on Market Intelligence (what the market is doing right now).
4. `PROJECT_STATE_v2.md` (in full) — the complete, consolidated project state, including its own §7
   (Phase 6.10, now CLOSED in full) and §8 (Phase 7, Checkpoints 5–6).

Then verify LIVE (do not trust any document's own claims blindly):

- repository path
- current branch (`git branch --show-current`)
- current HEAD commit (`git log -1`)
- working tree status (`git status --porcelain`)
- protected-directory diff: `git status --porcelain -- code/ results/ knowledge/` (must be empty)
- `ai_trader/`-since-last-validation diff: compare against the commit named in `NEXT_SESSION.md` §E's
  own "verified live" block — if `git diff --stat <that commit> HEAD -- ai_trader/` is non-empty, the
  test/mypy/coverage figures in `NEXT_SESSION.md` are STALE and must be re-run before being cited, not
  assumed still valid.

Confirm these match what `NEXT_SESSION.md` and `PROJECT_STATE_v2.md` claim. If anything disagrees,
trust the live `git`/`pytest`/`mypy`/`coverage` output over any document, and say so explicitly.

DO NOT search or use any other repository (not `ai_quant_lab`, not `AI-Research-Lab`, not
`tradingview-mcp`).

**Naming disambiguation before reading further**: Phase 6.10's "Edge Portfolio" (`shadow_evidence/`) is
the multi-strategy Shadow virtual-execution/statistics PLATFORM. Phase 7's "Edge Intelligence"
(`edge_intelligence/`) is a separate, newer, read-only RECOGNITION layer built on top of it. Do not
conflate the two — see `NEXT_SESSION.md` §B for the full disambiguation.

After reconstruction, report back:

1. Current repository state: path, branch, HEAD commit hash and message, working-tree status.
2. Every CLOSED phase through Phase 6.9A, one line each (`PROJECT_STATE_v2.md` §3–§6).
3. Phase 6.10's exact status: pre-scope diagnostic, Shadow Evidence Architecture Design + adversarial
   review verdict, Implementation Checkpoints 1A/1B/1C/2/3/4, the Edge Portfolio direction re-frame, the
   2026-07-17 official checkpoint save — all CLOSED/DONE, with commit hashes (`PROJECT_STATE_v2.md` §7,
   `NEXT_SESSION.md` §A). Phase 6.10 as a whole is now CLOSED; no further checkpoint is expected unless
   the CEO explicitly reopens it (Strategy Health integration policy and capital allocation across edges
   remain unselected/undesigned by deliberate scope boundary, not oversight).
4. Phase 7's exact status: Checkpoint 5 (Market Intelligence layer) and Checkpoint 6 (Edge Intelligence
   layer) — both DONE, with commit hashes (`PROJECT_STATE_v2.md` §8, `NEXT_SESSION.md` §A/§D). Checkpoint
   7 is NOT STARTED, NOT AUTHORIZED.
5. The current official architectural frontier in one paragraph: Market Intelligence answers "what is
   the market doing right now" (Trend/Structure/Momentum/Volatility/Liquidity/Expansion/Session/
   Agreement/Confidence); Edge Intelligence answers "which registered strategies' edges currently exist"
   (PRESENT/POSSIBLE/ABSENT per strategy, with disclosed evidence) by combining that snapshot with each
   strategy's own declared Contract fields. Both are pure, read-only, deterministic, never wired into
   `harness.py` or any execution path.
6. What has been implemented in code to date, exactly: the full `ai_trader/shadow_evidence/` package
   (config/types/engine/aggregation/research/comparison/portfolio_research), the full
   `ai_trader/market_intelligence/` package, the full `ai_trader/edge_intelligence/` package, plus a
   small number of disclosed, additive touches to `ai_trader/simulation/` — every other `ai_trader/`
   module (`risk_manager/`, `execution_engine/`, `signal_engine/`, `scoring_engine/`, `strategy_manager/`,
   `strategy_runtime/`, `strategy_health/`) remains byte-for-byte unchanged since Phase 6.9A's own close.
7. What must NOT be modified (`NEXT_SESSION.md` §F) — in particular: Checkpoint 7 is NOT authorized by
   anything read above; no Strategy Health integration policy has been selected; no capital-allocation
   architecture exists; `market_intelligence/`/`edge_intelligence/` must remain pure and read-only;
   `edge_intelligence/` must not import `shadow_evidence`.
8. The exact next authorized checkpoint: **none yet — Checkpoint 7 requires its own, separate, explicit
   CEO approval.** The CEO's own Checkpoint 6 closing text named Decision AI as the next conceptual
   component (the layer that would consume `edge_intelligence.present_strategy_ids()` to choose
   whether/what to trade) — state this as context, not as a pre-approved scope.
9. Confirm no new implementation has begun since the last official project save's own close.

Then **STOP**. Wait for the CEO's next instruction. Do not begin Checkpoint 7 or any other
implementation, design change, or architectural decision on your own initiative.
