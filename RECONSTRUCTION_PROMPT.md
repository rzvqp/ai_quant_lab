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
3. `PHASE_7_CHECKPOINT_13_REPORT.md` → `PHASE_7_CHECKPOINT_12_REPORT.md` →
   `PHASE_7_CHECKPOINT_11_REPORT.md` → `PHASE_7_CHECKPOINT_10_REPORT.md` →
   `PHASE_7_CHECKPOINT_9_REPORT.md` → `PHASE_7_CHECKPOINT_8_CONTEXT_MEMORY_DESIGN.md` (in full) — the
   current official architectural frontier: **Context Memory** — deterministic per-edge Contextual
   Evidence Aggregation, built on deterministic hierarchical-relaxation Retrieval, built on a
   deterministic episode-collapsed Historical Index, built on an append-only Repository, built on
   immutable contracts and deterministic SHA-256 identities. Produces evidence reports only, fully
   disconnected from Decision Intelligence and every execution-adjacent package.
4. `PHASE_7_CHECKPOINT_7_REPORT.md` → `PHASE_7_CHECKPOINT_6_REPORT.md` → `PHASE_7_CHECKPOINT_5_REPORT.md`
   (in full) — the PRIOR official architectural frontier, still current: Decision Intelligence (which
   edge, if any, deserves execution) built on Edge Intelligence (which registered strategies' edges
   currently exist) built on Market Intelligence (what the market is doing right now).
5. `PROJECT_STATE_v2.md` (in full) — the complete, consolidated project state, including its own §7
   (Phase 6.10, now CLOSED in full) and §8 (Phase 7, Checkpoints 5–13 plus all three official saves).

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
(`edge_intelligence/`) is a separate, read-only RECOGNITION layer built on top of it. Phase 7's
"Decision Intelligence" (`decision_intelligence/`) is a layer built on top of Edge Intelligence,
producing a RECOMMENDATION (never an executed trade). Phase 7's "**Context Memory**"
(`context_memory/`) is the newest and architecturally distinct from all three — it stores, indexes,
retrieves, and aggregates evidence about HISTORICAL contexts, never evaluates the present moment, and
produces evidence reports only (never a recommendation). Do not conflate any of the four — see
`NEXT_SESSION.md` §B for the full disambiguation.

After reconstruction, report back:

1. Current repository state: path, branch, HEAD commit hash and message, working-tree status.
2. Every CLOSED phase through Phase 6.9A, one line each (`PROJECT_STATE_v2.md` §3–§6).
3. Phase 6.10's exact status: pre-scope diagnostic, Shadow Evidence Architecture Design + adversarial
   review verdict, Implementation Checkpoints 1A/1B/1C/2/3/4, the Edge Portfolio direction re-frame, the
   first official checkpoint save — all CLOSED/DONE, with commit hashes (`PROJECT_STATE_v2.md` §7,
   `NEXT_SESSION.md` §A). Phase 6.10 as a whole is now CLOSED; no further checkpoint is expected unless
   the CEO explicitly reopens it.
4. Phase 7's exact status: Checkpoint 5 (Market Intelligence), Checkpoint 6 (Edge Intelligence),
   Checkpoint 7 (Decision Intelligence), Checkpoint 8 (Context Memory architecture design, ACCEPTED),
   Checkpoint 9 (Context Memory immutable contracts + identities), Checkpoint 10 (Append-Only Context
   Repository), Checkpoint 11 (Episode Collapsing and Historical Index), Checkpoint 12 (Deterministic
   Context Retrieval), Checkpoint 13 (Contextual Evidence Aggregation) — all DONE, with commit hashes
   (`PROJECT_STATE_v2.md` §8, `NEXT_SESSION.md` §A/§D), plus three official project saves (after
   Checkpoint 6, after Checkpoint 7, and after Checkpoints 10–13). Checkpoint 14 (Decision Intelligence
   v2 / Context Memory integration) is PROPOSED but NOT AUTHORIZED.
5. The current official architectural frontier in two paragraphs: (a) Market Intelligence answers "what
   is the market doing right now"; Edge Intelligence answers "which registered strategies' edges
   currently exist" (PRESENT/POSSIBLE/ABSENT per strategy, with disclosed evidence); Decision
   Intelligence answers "which edge, if any, deserves execution" (ACCEPT/REJECT per PRESENT candidate via
   four disclosed eligibility gates, deterministically ranked, one recommendation or explicit NO TRADE).
   All three are pure, read-only, deterministic functions over an already-produced `MarketContext`, never
   wired into `harness.py` or any execution path. (b) Context Memory answers "how did edges perform in
   contexts similar to this one, historically?" — an append-only repository of immutable Context
   Snapshot/Observation/Outcome records, a deterministic episode-collapsed historical index, a fixed-
   priority hierarchical-relaxation retrieval mechanism (no k-NN, no weighted distance), and per-edge
   evidence aggregation with a controlled sufficiency status. It never evaluates the present moment and
   never produces a recommendation — only historical evidence reports — and is not wired into Decision
   Intelligence or any execution path.
6. What has been implemented in code to date, exactly: the full `ai_trader/shadow_evidence/` package
   (config/types/engine/aggregation/research/comparison/portfolio_research), the full
   `ai_trader/market_intelligence/` package, the full `ai_trader/edge_intelligence/` package, the full
   `ai_trader/decision_intelligence/` package, the full `ai_trader/context_memory/` package
   (contracts/enums/validation/identities/codec/repository/episodes/index/retrieval/evidence), plus a
   small number of disclosed, additive touches to `ai_trader/simulation/` — every other `ai_trader/`
   module (`risk_manager/`, `execution_engine/`, `signal_engine/`, `scoring_engine/`,
   `strategy_manager/`, `strategy_runtime/`, `strategy_health/`) remains byte-for-byte unchanged since
   Phase 6.9A's own close.
7. What must NOT be modified (`NEXT_SESSION.md` §F) — in particular: Checkpoint 14 is NOT authorized by
   anything read above; no Strategy Health integration policy has been selected; no capital-allocation
   architecture exists; `market_intelligence/`/`edge_intelligence/`/`decision_intelligence/`/
   `context_memory/` must remain pure/read-only in the sense that matters for each;
   `context_memory/` must never output a BUY/SELL/entry/stop/target/size/execution/recommendation;
   `edge_intelligence/` must not import `shadow_evidence`; `decision_intelligence/` must not import
   `shadow_evidence`/`signal_engine`/`scoring_engine`/`risk_manager`/`execution_engine`;
   `context_memory/` must not import `decision_intelligence`/`signal_engine`/`scoring_engine`/
   `risk_manager`/`execution_engine`/`shadow_evidence`.
8. The exact next authorized checkpoint: **none yet — Checkpoint 14 requires its own, separate, explicit
   CEO approval.** The CEO's own Checkpoints 10–13 batch authorization explicitly excluded it — state
   this plainly, do not guess or propose scope for it unprompted.
9. Confirm no new implementation has begun since the last official project save's own close.

Then **STOP**. Wait for the CEO's next instruction. Do not begin Checkpoint 8 or any other
implementation, design change, or architectural decision on your own initiative.
