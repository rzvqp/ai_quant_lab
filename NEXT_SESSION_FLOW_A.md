# NEXT_SESSION_FLOW_A.md — Alpha Discovery Laboratory (Flow A)

**Scope of this document**: Flow A ONLY — the 40-Edge Alpha Discovery Program. Split out of the
former single `NEXT_SESSION.md` on 2026-07-20, per explicit CEO instruction, so Flow A and Flow B each
have their own operational document. Do not write Flow B (AI Trader Development) content here — see
`NEXT_SESSION_FLOW_B.md` for that. See `NEXT_SESSION.md` for the short, common orientation pointer.

---

## Current state

**Status: IN PROGRESS** (5 of 40 edges have completed a first Discovery-stage pass; the remaining 35
are still `UNSTUDIED`/`V0`, unchanged since the registry's own opening). The program itself opened
`READY TO START` (commit `d60fa63`) and its first research session has now run.

**Governing documents** (unchanged since the program opened): `EDGE_DISCOVERY_REGISTRY_v1.md` (the
40-edge backlog), `EDGE_RESEARCH_PROTOCOL.md` (the one shared six-stage pipeline: V0 → Discovery →
Frozen Candidate → Validation → Walk Forward → Final Verdict, plus the permanent-record rules), and
`EDGE_DISCOVERY_ROADMAP.md` (recommended sequencing, data-availability-driven).

## Last Flow A commit

```
eed1634  Flow A: first Alpha Discovery session — Discovery pass on E025/E026/E029/E032/E028
```

Re-verify live before trusting this — `git log -1`, `git branch --show-current`, `git status
--porcelain` — do not assume it is still the current HEAD in any future session (Flow B and other work
may have landed commits since).

## Edges studied (first Discovery-stage pass, 2026-07-20 session)

In order run: **E025 (Round Numbers) → E026 (ADR Exhaustion) → E029 (Weekly Gap Fill) → E032 (Premium
Discount Flip) → E028 (Fibonacci OTE)**. Full per-edge evidence, method disclosure, and answers to all
9 mandatory Discovery questions live in `edge_research/E0XX_<slug>.md` (one file per edge, permanent,
append-only), alongside each edge's own analysis script and JSON/CSV output (also in `edge_research/`,
committed). Every edge's registry `Status` field was updated from `UNSTUDIED` to
`DISCOVERY_IN_PROGRESS` for these 5 edges only; every `V0` hypothesis wording is unedited (per protocol
§1) — any informal, unfrozen "V1 candidate" framing suggested by this session's own evidence lives only
in the per-edge logs, never in the registry itself.

**No Final Verdict was issued on any edge.**

## Results (Discovery-stage, exploratory — none of these are Final Verdicts)

- **E025 Round Numbers**: NOT supported as stated at $10 or $100 granularity. At **$50 granularity, a
  significant EFFECT IN THE OPPOSITE DIRECTION from V0** was found — round $50 levels break through
  more often than a matched non-round control (p=0.0022 pooled, p=0.0059 approaching-from-above), i.e.
  a tentative liquidity-sweep/breakthrough pattern rather than a magnet/support-resistance one. Sign is
  consistent across an out-of-time split-half check.
- **E026 ADR Exhaustion**: Real, significant, and monotonic for **upside** ADR consumption (p=2.4e-6);
  absent for **downside** consumption. The upside effect may be partly confounded with session-of-day
  (only individually significant in the Asia session) — flagged as unresolved.
- **E029 Weekly Gap Fill**: Clean rate/size/speed pattern (88.9% overall fill rate within 5 trading
  days; large gaps fill far less reliably (77.8%) and 11× slower than small gaps (100%, same-bar)) —
  but this pass found **43% of raw week-boundary "gaps" are a data-feed artifact** (exact $0.00 gap,
  excluded before analysis) and did not yet build a control to rule out plain generic level-
  revisitation as the explanation.
- **E032 Premium Discount Flip**: A strong, highly significant reversion pattern using a **daily**
  range definition (Spearman r=0.53, p≈4e-299) but a much weaker one using a **weekly** range
  definition (r=0.04–0.07) — the registry's own "range-defining logic used" variable is confirmed
  load-bearing. Not yet distinguished from generic overextension mean-reversion (same open question as
  E026's own finding).
- **E028 Fibonacci OTE**: NOT supported on the continuation-RATE dimension — shallow retracements
  continue significantly MORE often (64.6%) than the OTE zone (57.3%, p=0.0023) — the reverse of V0.
  Continuation magnitude, conditional on continuation happening, is modestly higher in the OTE zone by
  median (0.117 vs 0.087) — a much weaker, non-decisive signal on that second dimension.

## Limitations (must be respected on any revisit)

- **No Final Verdict is possible yet on any edge studied so far.** The M15/H1/H4/D1 data on disk
  (~3.6 years, 2022-12-16→2026-07-13) is short of `EDGE_RESEARCH_PROTOCOL.md` §2's own ~5-6 year
  requirement for any Final Verdict (including an early REFUTED verdict). Every edge studied so far
  remains in **Stage 2 — Discovery, first pass complete** — not Frozen, not Validated, not
  Walk-Forwarded.
- **Recurring open question across this session's edges, worth closing before further "reversion-
  flavored" edges are studied**: several of the "significant" patterns found (E026 upside, E032
  daily-range) may be restatements of a single, generic, already-known market property — large/
  stretched recent moves partially mean-revert — rather than edge-specific mechanisms. No edge studied
  this session has yet been checked against that generic-reversion control. **E031 (3-SD VWAP) is a
  likely future candidate for the same confound** — worth building the control before or alongside
  studying it.
- No multiple-comparison correction has been applied to any of the above p-values — they are
  Discovery-stage screening signals, not confirmed findings.

## Next edge (per `EDGE_DISCOVERY_ROADMAP.md` Tier 1 order)

**E017 — Equal Highs / Lows Target** (candidate reuse noted by the prior session: a from-scratch
structure/swing detector analogous in spirit to, but not imported from,
`ai_trader/market_intelligence/structure.py` — Flow A does not import `ai_trader` code, per the
two-flow separation). After E017, in order: **E009, E010, E012, E015, E013, E016, E011, E014**, then
the session-timing edges **E006, E008, E005, E027**.

## Resume instructions

1. Re-verify git state live: `git branch --show-current`, `git log -1`, `git status --porcelain`.
2. Read, in this order:
   - **This document** — current state, summarized above.
   - **`EDGE_DISCOVERY_ROADMAP.md`** — full data-availability gap analysis (M15 is the finest
     resolution that exists; no tick/M1 data; no DXY/US10Y/XAGUSD/USDJPY/SPX data; no economic
     calendar — 17 of 40 edges are blocked on a data-acquisition decision not yet made) and the
     complete tier ordering.
   - **`EDGE_RESEARCH_PROTOCOL.md`** — the mandatory six-stage pipeline, the permanent-record rules
     (nothing ever deleted or retroactively edited), the 9 mandatory Discovery questions, and the
     5-verdict taxonomy.
   - **`EDGE_DISCOVERY_REGISTRY_v1.md`** — look up the specific edge(s) to continue with: V0
     hypothesis, category, required data/timeframes/instruments/observable variables/measured outcome.
   - **`PROJECT_STATE_v2.md` §1.1/§8.19/§8.20** — how Flow A relates to the rest of the project
     (context only, not required to continue research).
3. **Before starting or continuing Discovery on any edge**: verify `git status --porcelain` is clean,
   confirm which Roadmap tier the edge belongs to, and create (or continue) that edge's own permanent
   research log (`edge_research/E0XX_<slug>.md`, per `EDGE_RESEARCH_PROTOCOL.md` §6) before recording
   any finding.
4. Report the reconstructed state back to the CEO before proceeding on anything new.

## Warnings relevant to research

- **No edge may be optimized until it becomes profitable.**
- **No negative observation/exception/falsification may ever be removed** from an edge's own permanent
  record, at any stage.
- **No hypothesis may be edited retroactively after seeing results** — refinements are new, appended
  versions (V1, V2, …), never edits to a prior version. V0 itself is frozen forever.
- **No protocol stage may be skipped.**
- **A Final Verdict never itself authorizes implementation** — turning a studied edge into an actual
  strategy requires its own separate, explicit, future CEO decision.
- **Naming**: Flow A's "Alpha Edge" / "Edge" (E001–E040) is a completely different, unrelated concept
  from Phase 6.10's "Edge Portfolio" or Phase 7's "Edge Intelligence" (both `ai_trader/`-internal,
  Flow B concepts). Flow A's "Edge" means a raw, unimplemented research hypothesis in
  `EDGE_DISCOVERY_REGISTRY_v1.md` — never a registered `strategy_id`/`RuntimeEvaluator`. Do not conflate
  the two vocabularies.
- **Flow A does not import `ai_trader` code** — any candidate reuse of an `ai_trader/market_intelligence/`
  concept (e.g. `structure.py`'s swing/BOS/CHoCH logic) is built from scratch, analogous in spirit only,
  never imported directly, per the two-flow separation (`PROJECT_STATE_v2.md` §1.1).
- **No branch or worktree separation exists yet** — Flow A and Flow B currently share one branch
  (`ai-trader-implementation`) and one working tree. A concurrent Flow B (or other) session may be
  editing shared files at the same time; verify git state live before assuming any prior session's
  described state still holds.
