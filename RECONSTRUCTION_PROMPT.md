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
3. `PHASE_6_10_EDGE_PORTFOLIO_DIRECTION.md` (in full) — the current official architectural direction.
4. `PROJECT_STATE_v2.md` (in full) — the complete, consolidated project state, including its own §7
   covering all of Phase 6.10 to date.

Then verify LIVE (do not trust any document's own claims blindly):

- repository path
- current branch (`git branch --show-current`)
- current HEAD commit (`git log -1`)
- working tree status (`git status --porcelain`)
- protected-directory diff: `git status --porcelain -- code/ results/ knowledge/` (must be empty)
- `ai_trader/`-since-last-validation diff: compare against the commit named in `NEXT_SESSION.md` §D's
  own "verified live" block — if `git diff --stat <that commit> HEAD -- ai_trader/` is non-empty, the
  test/mypy/coverage figures in `NEXT_SESSION.md` are STALE and must be re-run before being cited, not
  assumed still valid.

Confirm these match what `NEXT_SESSION.md` and `PROJECT_STATE_v2.md` claim. If anything disagrees,
trust the live `git`/`pytest`/`mypy`/`coverage` output over any document, and say so explicitly.

DO NOT search or use any other repository (not `ai_quant_lab`, not `AI-Research-Lab`, not
`tradingview-mcp`).

After reconstruction, report back:

1. Current repository state: path, branch, HEAD commit hash and message, working-tree status.
2. Every CLOSED phase through Phase 6.9A, one line each (`PROJECT_STATE_v2.md` §3–§6).
3. Phase 6.10's exact status: pre-scope diagnostic, Shadow Evidence Architecture Design + adversarial
   review verdict, Implementation Checkpoints 1A and 1B, the Edge Portfolio direction re-frame — CLOSED/
   DONE/NOT STARTED for each, with commit hashes where applicable (`PROJECT_STATE_v2.md` §7,
   `NEXT_SESSION.md` §A/§D/§E).
4. The current official architectural direction in one paragraph: a generic Edge Portfolio (any
   validated market edge, "edge" = the existing `strategy_id`/`RuntimeEvaluator` unit), S10 used only as
   the first validation target, no edge-specific architecture anywhere in `ai_trader/shadow_evidence/`.
5. What has been implemented in code to date, exactly: the `ai_trader/shadow_evidence/` package
   (`config.py`, `types.py`, `engine.py`) plus the two small, additive touches to
   `ai_trader/simulation/config.py` and `ai_trader/simulation/harness.py` — nothing else in `ai_trader/`
   has changed since Phase 6.9A's own close.
6. What must NOT be modified (`NEXT_SESSION.md` §G) — in particular: Checkpoint 1C is NOT authorized by
   anything read above; no Strategy Health integration policy has been selected; no capital-allocation
   architecture exists.
7. The exact next authorized checkpoint: **none yet — Checkpoint 1C requires its own, separate, explicit
   CEO approval.** State the recommended (not yet approved) scope for it, from
   `PHASE_6_10_EDGE_PORTFOLIO_DIRECTION.md` §7 and the design document's own §14.
8. Confirm no new implementation has begun since the last official checkpoint save's own close.

Then **STOP**. Wait for the CEO's next instruction. Do not begin Checkpoint 1C or any other
implementation, design change, or architectural decision on your own initiative.
