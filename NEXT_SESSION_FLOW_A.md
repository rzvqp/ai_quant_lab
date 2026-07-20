# NEXT_SESSION_FLOW_A.md — Alpha Discovery Laboratory (Flow A)

**Scope of this document**: Flow A ONLY — the 40-Edge Alpha Discovery Program. Split out of the
former single `NEXT_SESSION.md` on 2026-07-20, per explicit CEO instruction, so Flow A and Flow B each
have their own operational document. Do not write Flow B (AI Trader Development) content here — see
`NEXT_SESSION_FLOW_B.md` for that. See `NEXT_SESSION.md` for the short, common orientation pointer.

---

## Current state

**Status: OVERNIGHT FULL-PROFILE SESSION IN PROGRESS (2026-07-22) — E010 done, auto-continuing to
E012 per standing CEO authorization (no per-edge approval required unless a governance issue arises).**
Following the TERMINAL HOLDOUT BREACH (identified 2026-07-21: all 5 edges studied first — E025, E026,
E028, E029, E032 — had loaded and analyzed data from the Research Lab's own sealed terminal holdout,
2025-10-23 09:15 UTC → 2026-07-13 06:00 UTC; **the old terminal holdout is CONSUMED / INVALIDATED**,
full incident record `PROJECT_STATE_v2.md` §8.23), the CEO authorized and this session completed
holdout remediation: (1) centralized holdout-cutoff enforcement in `edge_research/_common.py::load()`,
with a 17-test suite (`edge_research/test_loader.py`, all passing); (2) a clean rerun of all five
contaminated edges (`e0XX_..._clean.py`); (3) documentation of both the original (contaminated,
preserved verbatim) and clean results in each edge's own permanent log. **Registry status for these 5:
`DISCOVERY_IN_PROGRESS / CLEAN_RERUN_COMPLETE`.** The CEO then separately authorized **E017 — Equal
Highs / Lows Target** (V0 NOT supported — see below) and, after resolving a factual mismatch (an
earlier reference to "E009 — Previous Day High/Low" did not exist in the registry and was withdrawn),
**E009 — Change of Character Retest** (also V0 NOT supported — see below), both run entirely under the
post-remediation centralized-loader enforcement from the start (no contamination possible). The CEO then
authorized an **"overnight full edge profile" directive (2026-07-22)**: each edge now also gets a
timeframe profile, a 7-horizon/5-ATR-threshold movement profile, a context profile, controls/
falsification, a disciplined V1 search, and robustness checks — see `edge_research/_profile.py`, the
new shared library this required. **E010 — Breaker Block Snatch** was completed under this directive
(V0 NOT supported — see below); per the same authorization, this session auto-continues to the next
eligible edge without stopping for approval between edges unless a governance issue arises. The
remaining edges are unaffected and still `UNSTUDIED`/`V0`.

**Governing documents**: `EDGE_DISCOVERY_REGISTRY_v1.md` (the 40-edge backlog), `EDGE_RESEARCH_PROTOCOL.md`
(the six-stage pipeline, the permanent-record rules, and — new as of this incident — §8's mandatory
holdout-exclusion rule), and `EDGE_DISCOVERY_ROADMAP.md` (recommended sequencing, data-availability-
driven; its own top section now records the same pause and remediation-first next action).

## Last Flow A commits

```
eed1634  Flow A: first Alpha Discovery session — Discovery pass on E025/E026/E029/E032/E028
411a04b  docs: record holdout breach and quarantine affected edge research
360a410  Flow A: holdout remediation — centralized cutoff enforcement + clean rerun of 5 edges
be0e8d3  Flow A: E017 Discovery pass — Equal Highs/Lows Target (V0 not supported)
58338d7  Flow A: E009 Discovery pass — Change of Character Retest (V0 not supported)
<pending this session's own commit — E010 full-profile pass — see the E010 report for the exact hash>
```

Re-verify live before trusting this — `git log -1`, `git branch --show-current`, `git status
--porcelain` — do not assume it is still the current HEAD in any future session. This work now lives on
its own dedicated worktree/branch: `C:\Users\MEDION GAMING\ai_quant_lab-alpha-discovery`, branch
`alpha-discovery` (separated from Flow B's own `ai_quant_lab-research-main` / `ai-trader-implementation`
worktree, per CEO decision 2026-07-21).

## Edges studied

**2026-07-20 session, first Discovery-stage pass (later found holdout-contaminated, then remediated
2026-07-21)**: **E025 (Round Numbers) → E026 (ADR Exhaustion) → E029 (Weekly Gap Fill) → E032 (Premium
Discount Flip) → E028 (Fibonacci OTE)**.

**2026-07-21/22 session, run entirely under the post-remediation centralized-loader enforcement (no
contamination possible)**: **E017 (Equal Highs / Lows Target) → E009 (Change of Character Retest) →
E010 (Breaker Block Snatch, first edge under the "overnight full profile" directive)**.

Full per-edge evidence, method disclosure, and answers to all 9 mandatory Discovery questions live in
`edge_research/E0XX_<slug>.md` (one file per edge, permanent, append-only), alongside each edge's own
analysis script and JSON/CSV output (also in `edge_research/`, committed). Every studied edge's registry
`Status` field was updated from `UNSTUDIED` to `DISCOVERY_IN_PROGRESS`; every `V0` hypothesis wording is
unedited (per protocol §1) — any informal, unfrozen "V1 candidate" framing suggested by a session's own
evidence lives only in the per-edge logs, never in the registry itself (none of E017's, E009's, or
E010's own logs offer a V1 candidate — see each log for why).

**No Final Verdict was issued on any edge.**

## Results — ORIGINAL (contaminated) vs. CLEAN RERUN (holdout-excluded, 2026-07-21)

**The original results below were HOLDOUT-CONTAMINATED** (see "Current state" above and
`PROJECT_STATE_v2.md` §8.23) — preserved verbatim as an audit trail, per the protocol's own
permanent-record rule; they never supported and still do not support promotion to Frozen Candidate,
Validation, or a Final Verdict. **The clean-rerun column is the one to rely on going forward.** Full
detail, including per-slice/per-session breakdowns, is in each edge's own `edge_research/E0XX_*.md` log.

| Edge | Original (contaminated) headline | Clean rerun (holdout-excluded) headline | Outcome |
|---|---|---|---|
| **E025 Round Numbers** | $50: round vs control p=0.0022 (4h horizon); approach-from-above p=0.0059 | $50 reaction_4 (~1h) CONFIRMS (p=0.00011); reaction_16 (~4h) and approach-from-above subslice no longer clear p<0.05 (p=0.072, p=0.121) | **PARTIALLY WEAKENED** |
| **E026 ADR Exhaustion** | Upside: Spearman r=−0.137, p=2.4e-6; downside null; Asia-only session significance | Upside: r=−0.171, **p=8.4e-8** (stronger); downside null unchanged; Asia-only pattern replicates identically | **CONFIRMED** (strengthened) |
| **E029 Weekly Gap Fill** | Fill rate 88.9%; large-tercile 77.8%, median TTF 11.0h; 43% artifact rate | Fill rate 91.3%; large-tercile 78.3% (CONFIRMS), median TTF 1.875h (**CHANGED**, small-n-sensitive); ~45% artifact rate (CONFIRMS) | **RATE PATTERN CONFIRMED; TTF FIGURE CHANGED** |
| **E032 Premium Discount Flip** | Daily-range Spearman r=0.527, p≈4e-299; weekly r=0.039, p=0.0049 | Daily r=0.522, p≈6.5e-235; weekly r=0.039, p=0.012 | **CONFIRMED** (near-identical, most robust of the five) |
| **E028 Fibonacci OTE** | Shallow 64.6% vs OTE 57.3% continuation rate, χ²=9.28, p=0.0023 | Shallow 63.0% vs OTE 57.0%, χ²=4.89, **p=0.027** (weaker test, same rates) | **CONFIRMED** |

**Open questions carried forward unresolved by the clean rerun** (identical in both runs): E026's
upside effect may still be a session-composition confound (only individually significant in Asia); E029
still lacks a matched intraday-revisitation control; E032 still lacks an overextension-confound control;
E028 still hasn't tested a coarser fractal `k`. None of these are resolved by holdout removal alone.

## Result — E017 Equal Highs / Lows Target (2026-07-21, clean-from-the-start)

**V0 NOT supported — REFUTED-leaning evidence, both sides, robust to every sensitivity check run:**
- **Reach rate, equal vs. isolated control**: no meaningful difference at any of 4 tolerances
  (0.10/0.15/0.25/0.40×ATR) × 3 horizons (1/5/20 trading days) — e.g. primary config (0.15×ATR, 5
  days): highs 93.2% vs 92.6% (p=0.826); lows 87.1% vs 86.2% (p=0.765).
- **Reach rate, equal vs. a random-matched-distance control** (no real swing structure, same distance
  profile): the RANDOM control reaches its target *more* reliably and far faster than real equal-highs/
  lows — highs 98.2% (median 1 bar) vs 93.2% (16 bars), p=0.0067; lows 92.8% (2 bars) vs 87.1% (13
  bars), p=0.043. The opposite direction from a "magnet" story.
- **Reversal magnitude after reach**: no boost from being "equal" — high side even trends the wrong
  direction (equal *less* reversing than isolated, p=0.056 borderline); low side n.s. either way.
- **Distance-quantile-matched comparison and session/volatility slices**: no effect recovered anywhere.
- **No V1 candidate offered** — the distinguishing "equal" property was tested directly and repeatedly
  found to add nothing; see `edge_research/E017_equal_highs_lows.md` for the full analysis, including a
  flagged open question (relevant to E009/E010/E012/E015/E013/E016/E011/E014, the other structure-
  pattern edges) about whether swing points in general carry the "liquidity magnet" property commonly
  claimed for them.

**No Final Verdict issued** (below the ~5-6yr horizon, same as every other edge studied so far).

## Result — E009 Change of Character Retest (2026-07-21, clean-from-the-start)

**V0 NOT supported.** An earlier reference in this session to "E009 — Previous Day High/Low" was
verified against the registry, found not to exist anywhere in it, and withdrawn by explicit CEO decision
before any research began — this pass studies the registry's own real, frozen E009.

- **CHoCH vs. its natural on-topic control, BOS** (both are real structural breaks; the only difference
  is whether the break agrees with (BOS) or contradicts (CHoCH) the preceding trend): no significant
  retest-rate, continuation-rate, or failure-rate difference at the primary config (k=5, 5-day horizon)
  — low-break p=0.516/0.220, high-break p=0.648/0.586 — nor at any of 3 fractal-k values (3/5/8) or 3
  horizons (1/5/20 trading days), nor in any session or volatility slice.
- **Important disclosed methodological finding**: the retest metric itself is close to saturated
  (90-99%) for CHoCH, BOS, **and** a random, no-structure, distance-matched control alike — at this
  swing scale, "does price touch a nearby recently-broken level again" is close to a foregone conclusion
  regardless of structural meaning, limiting how much this dimension alone could have discriminated a
  true effect even if one existed. The continuation and compound-outcome dimensions (86-94%, less
  saturated) told the same null story independently.
- **No V1 candidate offered** — CHoCH's defining property was tested directly against BOS and found to
  add nothing; see `edge_research/E009_choch_retest.md` for the full analysis, including a flagged
  concern (relevant to E010/E012/E015/E013/E016/E011/E014) about retest-metric saturation at this swing
  scale for any future "retest"-flavored edge.

**No Final Verdict issued** (below the ~5-6yr horizon, same as every other edge studied so far).

## Result — E010 Breaker Block Snatch (2026-07-22, full profile, clean-from-the-start)

**V0 NOT supported — one of the cleanest nulls found this program.** Tested on M15 (5,833 breaker
events) and H1 (1,550) — M1/M5 confirmed unavailable anywhere in this project's data.
- **After a breaker flip, continuation in the NEW direction is a coin flip**: 49.9% (M15) / 51.4% (H1),
  with MFE≈MAE at every horizon (1/3/5/10/20/50 bars) and every ATR threshold (0.25-2.0×) — the clearest
  possible signature of non-directional noise. Stable across 3 displacement thresholds (1.2/1.5/2.0×
  ATR), every session, volatility regime, trend context, day of week, and year in the sample.
- **Its own natural control — unflipped (never-violated) order blocks — shows a large, real,
  directional continuation effect instead**: 88.0% (M15) / 86.2% (H1) continuation in their ORIGINAL
  polarity, +1 ATR mean move within 1 bar. The gap between breaker (49.9%) and unflipped (88.0%)
  continuation is enormous (p=5.9e-119, M15) — this control also proves the methodology CAN detect a
  real effect when one exists, sharpening rather than undermining the breaker null.
- **No V1 candidate offered.** The unflipped-OB effect is flagged as a strong candidate for a future,
  separately-registered edge (not folded into E010, which would improperly substitute a different claim
  for V0's own).
- New shared library `edge_research/_profile.py` (movement/context/robustness helpers) built this pass,
  reusable for all edges going forward under the CEO's "full profile" directive.

**No Final Verdict issued** (below the ~5-6yr horizon, same as every other edge studied so far).

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

## Next step: auto-continuing to E012 (standing authorization, no per-edge approval needed)

Per the CEO's own "overnight full edge profile" authorization (2026-07-22), this session does **not**
stop between edges to ask approval — it continues automatically to the next Tier 1 edge after each
commit, one edge at a time, stopping only for a genuine governance issue (a contradictory registry, a
V0 that can't be operationalized without a CEO decision, a required protocol change, missing data, a
loader/test failure, anything that would require touching Flow B, or an audit-trail risk). **Next: E012
— Inverted Fair Value Gap**, then in order **E015, E013, E016, E011, E014**, then the session-timing
edges **E006, E008, E005, E027**.

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
3. **Under the standing "overnight full profile" authorization, new-edge Discovery may continue
   automatically** (one edge at a time, per commit) — stop only for a genuine governance issue (see
   "Next step" above for the exact stop conditions). Verify `git status --porcelain` is clean, and
   confirm `EDGE_RESEARCH_PROTOCOL.md` §8's enforcement is actually present in
   `edge_research/_common.py::load()` (it should require `data_split_id`/`cutoff` and raise if either
   is missing) before relying on any run's own `holdout_excluded=true` claim.
4. If resuming a fresh session (not a direct continuation), report the reconstructed state back to the
   CEO once before proceeding — the standing authorization covers continuing within an already-briefed
   session, not silently skipping the report on a brand-new one.

## Warnings relevant to research

- **TERMINAL HOLDOUT BREACHED, CONSUMED / INVALIDATED (2026-07-21)** — the old sealed period
  (2025-10-23 09:15 UTC → 2026-07-13 06:00 UTC) can no longer be treated as unseen. Do not describe it
  as "intact." Do not describe a future cutoff-enforced rerun as "restoring" it — it does not; only a
  new, separately-designated holdout (not yet decided) would give the project a genuinely unseen period
  again, and that decision has not been made.
- **`EDGE_RESEARCH_PROTOCOL.md` §8 (new, 2026-07-21; enforcement live as of this remediation)**: Alpha
  Discovery may not read, load, aggregate, or use data from a sealed holdout period, under any
  circumstance or research stage. Every future result must record its own min/max date used, bar count,
  data-split identifier, and an explicit `holdout_excluded=true` confirmation — absent evidence
  invalidates the run. Enforced centrally by `edge_research/_common.py::load()` — the module's only
  data-reading entry point; it takes no default split/cutoff and fails closed if either is missing.
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
- **Branch/worktree separation now exists (CEO decision, 2026-07-21)**: Flow A's official location is
  `C:\Users\MEDION GAMING\ai_quant_lab-alpha-discovery`, branch `alpha-discovery` — a dedicated git
  worktree, separate from Flow B's own `C:\Users\MEDION GAMING\ai_quant_lab-research-main`
  (`ai-trader-implementation` branch). Do not access or modify the `ai_quant_lab-research-main` worktree
  from a Flow A session, and do not modify `NEXT_SESSION_FLOW_B.md`,
  `STRATEGY_HEALTH_INTEGRATION_POLICY_DESIGN.md`, `ai_trader/`, or any Flow B report/implementation from
  here. Still verify git state live (`git branch --show-current`, `git log -1`, `git status
  --porcelain`) before assuming any prior session's described state still holds — other sessions may
  land commits on this branch too.
