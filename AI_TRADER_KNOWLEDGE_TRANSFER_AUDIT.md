# AI Trader — Knowledge Transfer Audit

**Mode: READ-ONLY audit and reporting only.** No code, configuration, threshold, or document was modified
to produce this report. No DEMO run was started. Repo: `ai_quant_lab-research-main`, branch
`ai-trader-implementation` (the branch actually checked out; other branches were inspected read-only via
`git show <branch>:<path>`, never checked out).

---

## Executive Summary

**Verdict: NOT READY** (see §9 for full reasoning).

Two independent findings, each sufficient on its own to block a continuous DEMO run:

1. **No live signal source exists.** `CandidateSignal` — the type that starts a trade candidate through
   the live orchestrator (`recognition → confidence → risk → portfolio → order → MT5`) — is constructed
   exactly **once** in the entire repository, in a test fixture
   (`execution_orchestrator/tests/_fixtures.py:31`). Nothing in `market_scanner`, `signal_engine`,
   `strategy_runtime`, or anywhere else in production code ever builds one. The live pipeline is wired
   end-to-end and fully tested, but **structurally dormant** — it currently cannot produce a trade from
   any source, Research-Lab-derived or otherwise.
2. **Zero Research Lab edges or strategies have been transferred into the live decision chain, at the
   code level.** A repo-wide search for every Research Lab identifier convention (`E0xx` edge IDs,
   `DC-00xx` Red Team candidate IDs, `EDGE_DISCOVERY_REGISTRY`, `CRITIQUE_BATTERY`, `red_team`) inside
   `ai_trader/` returns **zero hits**. The one place a Research-Lab artifact genuinely is loaded live
   (`edge_intelligence/contracts.py` loading the 51-file `knowledge/strategies/` Strategy Library) loads
   only the *structural* contract fields (execution rules, required data) — the statistical-validation
   evidence in the same files (`matched_null_status`, `global_fdr_status`, `walk_forward_status`,
   `holdout_status`) is parsed into memory and then never read by any verdict logic, and the whole
   `edge_intelligence` snapshot it produces is itself never consumed by `confidence_engine` or anything
   downstream. `confidence_engine.ScoreComponents.strategy_health_component` is a permanent, explicitly
   disabled `None` — Strategy Health's ACTIVE/WATCHLIST/PROBATION/SUSPENDED governance has zero live
   enforcement.

No Research Lab edge or strategy has an explicit "approved for AI Trader" statement anywhere on either
side of the codebase — this is consistent on both sides, not a discrepancy. Nothing explicitly
**REJECTED** on the Research Lab side (data-mining artifacts, failed-OOS calendar effects, closed S21-S40
negatives) has leaked into `ai_trader/` code either — a genuinely good finding, but one that holds only
because nothing at all has been wired, not because a guard prevents it.

---

## 1. Research Lab landscape — three structurally distinct tracks (do not conflate)

| Track | What it is | ID space | Governance |
|---|---|---|---|
| **1 — Edge Discovery Registry** | Quantitative, protocol-driven hypotheses | `E001`–`E040` | `EDGE_DISCOVERY_REGISTRY_v1.md`, Flow A protocol |
| **2 — Strategy families / Strategy Library** | Backtest-engine campaign + the JSON contracts AI Trader can actually load | `S1`–`S51` (`knowledge/strategies/S01_.../strategy.json` etc.) | `STRATEGY_REGISTRY.md`, `KNOWLEDGE_REGISTRY.md`, `CEO_STRATEGY_PERFORMANCE_ATLAS.md`, Strategy Health |
| **3 — Alpha Discovery Candidates** | Qualitative, visually observed chart patterns, reviewed by Red Team | `DC-0001`–`DC-0018` | `red_team/` (branch `red-team-foundation`/`alpha-automation-v1`, **not merged to `ai-trader-implementation`**) |

Track 1's `E`-numbers and Track 2's `S`-numbers are unrelated ID spaces — an `S1` strategy is not a
transfer target for an `E001` edge, or vice versa, despite both being called "edges" informally in
conversation. This distinction matters directly for §7 (per CEO instruction: do not assume a transfer
from name similarity).

---

## 2. Full edge/strategy inventory

### 2.1 Track 1 — Edge Discovery Registry (E001–E040)

**Program-level fact, `EDGE_DISCOVERY_REGISTRY_v1.md`**: opened 2026-07-20, all 40 entries frozen at
**Version V0**. *"No edge below has been implemented, and no Final Verdict has been issued on any
edge"* (available data ~3.6yr, short of the protocol's 5-6yr requirement).

- **35/40 — status UNSTUDIED** (never run): E001 London Open Liquidity Hunt, E002 Frankfurt Pre-Market
  Trap, E003 NY Silver Fix Momentum, E004 US Market Open First FVG, E005 London Close Reversal, E006 Asia
  Range Expansion Failure, E007 Central Bank Whisper, E008 Friday Profit Taking Shift, E009 Change of
  Character Retest, E010 Breaker Block Snatch, E011 Failed 3 Drive Pattern, E012 Inverted Fair Value Gap,
  E013 Mitigation Block Sniping, E014 Inside Bar False Breakout, E015 Order Block Re-Mitigation, E016
  Propulsion Block Entry, E017 Equal Highs/Lows Target, E018 B-Book Stop Hunt (flagged unobservable as
  worded), E019 Volume Climax Exhaustion, E020 Delta Divergence, E021 Iceberg Order Absorption, E022 VWAP
  Touch And Go, E023 High Relative Volume Breakout, E024 SP500/Gold Delta Shift, E027 Midnight Open
  Anchor, E030 Tick Speed Acceleration, E031 3 Std Dev VWAP, E033 DXY Lead, E034 US10Y Lead, E035 Silver
  Leading Indicator, E036 USDJPY Inversion, E037 NFP First Wave Liquidation, E038 CPI Initial Reaction
  Reversal, E039 FOMC Slingshot, E040 Flash PMI Sentiment Flip.
- **5/40 — Discovery-stage run once, then quarantined by a holdout breach** (status field literally reads
  `DISCOVERY_IN_PROGRESS / HOLDOUT_CONTAMINATED / CLEAN_RERUN_REQUIRED`):

| Edge | Hypothesis | Discovery-pass finding | Red Team | Statistical validation |
|---|---|---|---|---|
| E025 Round Numbers | S/R/magnet at round $10/$50/$100 | NOT supported as stated; **opposite sign** at $50 (breaks through more, not less), p=0.0059/0.0022 | Not reviewed (Red Team scope is DC-####, not E-numbers) | None |
| E026 ADR Exhaustion | Less continuation past ADR threshold | Real for UP only (p=2.4e-6); absent for DOWN; possible session confound | Not reviewed | None |
| E028 Fibonacci OTE | 61.8-79% retracement favorable for continuation | NOT supported — **reverse of claim** (shallow retracements continue more, p=0.0023) | Not reviewed | None |
| E029 Weekly Gap Fill | Fri-close→Sun/Mon-open gap fills | Real (88.9% fill) but possibly indistinguishable from generic mean-reversion (no matched control) | Not reviewed | None |
| E032 Premium/Discount Flip | Price moves toward 50% equilibrium | Strong with daily range def, weak with weekly; possibly generic overextension mean-reversion, not the specific ICT construct | Not reviewed | None |

**Holdout breach, official record** (`PROJECT_STATE_v2.md` §8.23): *"TERMINAL HOLDOUT BREACHED"* —
2025-10-23→2026-07-13 sealed holdout was inadvertently loaded by all 5 edges' shared loader
(`edge_research/_common.py::load()`, no date cutoff). CEO-confirmed as *"a process and governance breach,
not evidence that the five edges' own Discovery-stage findings are false."* Flow A status: **PAUSED for
remediation**; E017+ blocked until clean rerun + protocol-level holdout enforcement.

**No edge of any status has any AI-Trader-authorization statement anywhere.** `EDGE_DISCOVERY_REGISTRY_v1.md`
explicitly states the three `market_intelligence` modules that share names with edge concepts
(`structure.py`, `volatility.py`, `session_behavior.py`) — *"None of them has been wired into this
program, modified, or run against any edge below."* (Those `market_intelligence` modules were in fact
built earlier, for an unrelated Checkpoint, before the Edge Discovery Program even opened — see §7.)

### 2.2 Track 2 — Strategy families (S1–S51) and the Strategy Library

- **`KNOWLEDGE_REGISTRY.md`** — 5 falsifiable claims (K01-K05), deliberately weakened to avoid causal
  over-claims, all status **EXPLORATORY** except K04 (**OVERFIT** — failed OOS replication) and K05
  (**UNRESOLVED** — 11/13 OOS-positive candidates may just be long gold beta, not timing alpha).
- **`STRATEGY_REGISTRY.md`** — 2,300 hypotheses tested, 375 flagged research-worthy/profitable/fragile.
  Explicit blanket status: *"strict_validation = STRICT VALIDATION PENDING for all"* (matched-null done,
  **global-FDR CEO-gated**, not run).
- **`STRATEGY_PROFILES.md`** — 22 deduplicated candidates, header: *"No validated alpha; strict
  validation (matched-null → global-FDR) CEO-gated."*
- **`TOP_STRATEGIES_SHORTLIST.md`** — ~8 candidates, explicit: *"Nothing here is alpha."* Explicitly names
  S29/S31 as data-mining artifacts: *"Do NOT validate as edges."*
- **`docs/S21_S31_TIERB_CONSOLIDATED.md`** — 14 S21-S40 families: only 2 **KEEP** (S22, S39), 3
  **EXPLORATORY**, **9 NEGATIVE — CLOSED** (S21, S23, S25, S26, S27, S28, S30, S38, S40).
- **`docs/ALPHA_REGISTRY.md`** — self-flagged in its own header as **"STALE / HISTORICAL /
  NON-AUTHORITATIVE"**: its p-values come from *"the analytic p-value engine that was later
  INVALIDATED."*
- **`docs/MONTE_CARLO_AUDIT.md`** — confirms the analytic p-value engine is a proven artifact (the S6
  case: p=2.1e-54 driven by 5 outlier trades; sign flips negative once removed). Block-bootstrap adopted
  instead; under it, *"none of the current Research Candidates are statistically significant."*
- **`docs/MATCHED_NULL_VALIDATION.md`** — the matched-null **engine** itself is validated (✅), but *"No
  strategy verdict is issued here."* A 10-hypothesis pilot found only `S5_representative` significant
  both research and OOS; under the frozen global-FDR (m=1552), *"none of these would be significant."*
- **`CEO_STRATEGY_PERFORMANCE_ATLAS.md`** — 43 strategies, A/B/C/D/E performance labels cross-tagged with
  a *separate* Strategy Health state (ACTIVE/WATCHLIST/PROBATION/SUSPENDED). Six strategies (S1, S13,
  S39, S40, S46, S48) went through a dedicated root-cause verdict process — **all six verdicted
  PORTFOLIO-LIMITED** (underperformance attributed to the scoring engine's cross-strategy conflict
  penalty, not intrinsic edge quality — *"None qualifies as STRATEGY-LIMITED..."*).
- **The Strategy Library** — `knowledge/strategies/S01_.../strategy.json` ... 51 files. Each carries a
  rich `evidence` block, e.g. S01: `matched_null_status: {status: "INCONCLUSIVE", p: 0.0069}`,
  `global_fdr_status: "NOT_RUN"`, `walk_forward_status: "NOT_RUN"`,
  `validation_status: "EXPLORATORY — ... Holdout SEALED..."`, `provenance.holdout_status: "SEALED"`.
  **This is the only Research-Lab artifact that AI Trader's live-adjacent code (`edge_intelligence`)
  actually loads by file — see §3.**

### 2.3 Track 3 — Alpha Discovery Candidates (DC-0001–DC-0018), Red Team-reviewed

Exists only on branches `alpha-automation-v1`/`red-team-foundation`, **not merged to
`ai-trader-implementation`**. Methodology (`CRITIQUE_BATTERY.md` v1.0): 5 critiques → 3 verdicts (🟢
CONTINUE / 🟡 NEEDS BETTER EVIDENCE, *"not a rejection"* / 🔴 NOT RECOMMENDED, *"does NOT mean
'rejected'"*), explicitly *"quality control, not candidate destruction."* All 18 reviewed, tally **🟢 7 ·
🟡 11 · 🔴 0** (zero outright rejections). No statistical validation applied to any DC (out of the
Critique Battery's scope), and no DC has any AI-Trader-authorization statement.

| Verdict | DCs |
|---|---|
| 🟢 (7) | DC-0002, DC-0003, DC-0004, DC-0008, DC-0013, DC-0016, DC-0017 |
| 🟡 (11) | DC-0001, DC-0005, DC-0006, DC-0007, DC-0009, DC-0010, DC-0011, DC-0012, DC-0014, DC-0015, DC-0018 |

### 2.4 Statistician division — not found in this repository

Searched every branch in this repo; no "Statistician" file or directory exists here. (It appears to
belong to a separate project directory per prior context, out of this audit's scope, which is
`ai_quant_lab-research-main` exclusively per your instruction.)

---

## 3. Where each track actually appears in AI Trader — verified by code, not name

### 3.1 Track 1 (E-numbered edges): zero code presence

Repo-wide search across `ai_trader/` for `E0[0-9]{2,3}`, `EDGE_DISCOVERY_REGISTRY` → **zero hits**, in
`.py`, `.md`, and `.json` alike. `market_intelligence`'s `structure.py`/`volatility.py`/
`session_behavior.py` are real, live-wired modules (via `context_engine`), but they were built earlier,
for an unrelated checkpoint, and are explicitly disclaimed by the Edge Registry itself as never having
been run against any Track-1 edge (§2.1). Same name, unrelated provenance — flagged per your instruction
not to assume a transfer from naming alone.

### 3.2 Track 2 (S-numbered strategies / Strategy Library): loaded, but structurally inert

- `ai_trader/edge_intelligence/contracts.py:13-30::load_strategy_contracts()` wraps
  `ai_trader.strategy_manager.loader.load_all(DEFAULT_LIBRARY_PATH)`, which reads the real
  `knowledge/strategies/S01_.../strategy.json` ... S51 files, parsed in full (including `evidence`) by
  `strategy_manager/contract.py:261-424`.
- **But** `edge_intelligence`'s own evidence modules (`directional.py:18-19`, `data_availability.py:17-18`)
  only read `contract.execution.*`/`contract.semantics.required_data` — never `contract.evidence.*`.
  `verdict.py:14-22`'s `determine_edge_state` combines only the tags those modules produce.
  **The matched-null/global-FDR/walk-forward/holdout status loaded from the Strategy Library is parsed
  into memory and then never read by any live verdict logic.**
- Worse: `context_engine/engine.py:42-47` computes the `edge_intelligence` snapshot and attaches it to
  `MarketContextSnapshot.edge_intelligence`, but a repo-wide grep for `.edge_intelligence` attribute
  access outside tests shows **zero hits** in `risk_manager_live`, `portfolio_manager_live`,
  `order_manager`, `execution_orchestrator`, `mt5_demo_execution`, or `confidence_engine`. **The entire
  `edge_intelligence` output — the one genuine live link to the Strategy Library — is computed and then
  never consumed by anything downstream.**
- `confidence_engine.types.ScoreComponents.strategy_health_component` (`types.py:62-64`) is permanently
  `None`, with an explicit docstring: *"No authorized live strategy-health signal exists in this pipeline
  today."* Strategy Health's ACTIVE/WATCHLIST/PROBATION/SUSPENDED states are used only by the batch/Shadow
  harness — `strategy_health` is explicitly forbidden by import-independence tests in every live package
  that has one (`recognition_engine_live`, `confidence_engine`, `risk_manager_live`,
  `portfolio_manager_live`, `order_manager`).
- `scoring_engine` (batch, NOT live) genuinely does enforce Track-2 validation status at runtime:
  `components.py:26-36` maps `Lifecycle` (EXPERIMENTAL/EXPLORATORY/CANDIDATE/VALIDATED/PROMOTED) to a
  maturity prior, and `components.py:57-66::_validation_bonus` adds score for each PASSing
  matched-null/walk-forward/global-FDR gate. **This is real, functioning Research-Lab-status enforcement
  — but it lives exclusively in the batch scoring path.** No live package imports `scoring_engine`'s
  logic; the only reuse anywhere in the live tree is `scoring_engine.types.Quality`, a bare 5-value enum
  with zero scoring logic attached (`confidence_engine/types.py:10`, `risk_manager_live/types.py:12`).

### 3.3 Track 3 (DC-numbered Alpha candidates): zero code presence, and not even on this branch

Repo-wide search for `DC-00`, `CRITIQUE_BATTERY`, `red_team` (case-insensitive) inside `ai_trader/` →
**zero hits**. The Red Team package itself lives only on unmerged branches — it cannot be referenced from
`ai-trader-implementation` even in principle without a merge that hasn't happened.

### 3.4 The pattern/recognition layer is generic, not edge-specific

`recognition_engine_live/patterns.py:14-21`'s `AUTHORIZED_PATTERNS` catalog is one entry per
`ContextDimension` (15 total: SESSION, TREND×4 timeframes, STRUCTURE_STATE, MOMENTUM×4, VOLATILITY_REGIME,
LIQUIDITY_STATE, EXPANSION_STATE, MULTI_TIMEFRAME_AGREEMENT, DATA_QUALITY_STATE), with IDs literally
`f"REC-{dimension.value}-STRATEGY"`. These are generic statistical buckets over market context, **not**
implementations of any specific Research-Lab edge's structure (no liquidity-sweep, order-block, FVG, or
any other named-edge-specific pattern logic exists anywhere in this package). `RecognitionResult`/
`RecognitionCandidate` (`types.py:36-89`) have **no field of any kind** for an edge ID or source
experiment — confirmed by direct reading of the dataclass fields, not inference.

### 3.5 No signal source exists to carry any of this to a decision anyway

`CandidateSignal` (`execution_orchestrator/types.py:42-68`) — the type an actual trade candidate would
need to be — is constructed exactly once in the whole repository, in
`execution_orchestrator/tests/_fixtures.py:31`. Its own docstring (lines 43-45) states entry/stop/target
generation is *"another module's job (signal_engine/strategy_runtime), never this orchestrator's own
logic"* — and no such production caller exists yet. **Whatever this audit concludes about edge transfer
is, today, moot in practice: the live chain has nothing feeding it.**

---

## 4. Research Lab → AI Trader transfer matrix

| Item | Research Lab status | AI Trader code presence | Classification |
|---|---|---|---|
| E001-E024, E027, E030-E040 (35 edges) | UNSTUDIED | None | **NOT TRANSFERRED** |
| E025, E026, E028, E029, E032 (5 edges) | Discovery-stage only, holdout-contaminated, no Red Team, no statistical validation | None | **NOT TRANSFERRED** |
| Strategy Library structural fields (execution/semantics, all 51) | Contract-defined, no strict validation | Loaded and actively used by `edge_intelligence` evidence checks | **PARTIALLY TRANSFERRED** (structure only) |
| Strategy Library evidence fields (matched-null/global-FDR/walk-forward/holdout, all 51) | STRICT VALIDATION PENDING (global-FDR CEO-gated, not run) | Loaded into memory, never read by any verdict/scoring logic in the live path | **DOCUMENTED ONLY** (present in data, inert in live code) |
| Strategy Library evidence fields, batch path only | same | Read and enforced by `scoring_engine` (batch, not live) | **PARTIALLY TRANSFERRED** (batch pipeline only, not live) |
| Strategy Health states (ACTIVE/WATCHLIST/PROBATION/SUSPENDED) | Governance layer over Track 2 | Explicitly forbidden import in every live package; `strategy_health_component` permanently `None` | **NOT TRANSFERRED** |
| S22, S39 (Track-2 "KEEP" candidates) | Positive, unvalidated (no global-FDR) | None (no code references these IDs) | **NOT TRANSFERRED** |
| S29, S31, S17, and the 9 "NEGATIVE — CLOSED" S21-S40 families | Explicitly REJECTED / data-mining artifacts / failed-OOS | None found anywhere | **REJECTED — correctly excluded** (see §7) |
| DC-0001–DC-0018 (all) | 🟢/🟡 Red Team-triaged, no statistical validation, not on this branch | None; package not even merged | **NOT TRANSFERRED** |
| Live pattern/recognition layer (`REC-{dimension}-STRATEGY`) | N/A — no Research-Lab edge maps to these | Fully implemented, generic | **N/A — not a transfer of any specific edge, independently built machinery** |
| `CandidateSignal` (live decision entry point) | N/A | Constructed only in test fixtures | **NO LIVE SOURCE EXISTS** — blocks all of the above regardless |

---

## 5. Fully transferred edges

**None.** No edge or strategy from any of the three Research Lab tracks has both (a) a code-level
reference inside `ai_trader/`'s live path and (b) an actual influence on a live decision output. The one
candidate that comes closest — the Strategy Library's structural contract fields — is loaded and used for
evidence-gate checks, but this qualifies as partial (§6), not full, because the accompanying validation
status is ignored and the resulting `edge_intelligence` snapshot is itself never consumed downstream.

## 6. Partially transferred

1. **Strategy Library structural contracts (51 files)** — genuinely loaded and used by
   `edge_intelligence`'s evidence checks (`directional.py`, `data_availability.py`) for execution rules
   and required-data checks. Validation status is loaded but ignored (§3.2); the resulting snapshot is
   itself unused downstream (§3.2) — so even this partial transfer currently has **no path to actually
   influencing a live decision**.
2. **`scoring_engine.types.Quality` enum** — a bare value type shared between the batch scoring engine and
   two live packages (`confidence_engine`, `risk_manager_live`). Carries no scoring logic, no
   Research-Lab-specific content — a naming/type-reuse convenience, not a knowledge transfer.
3. **Strategy Library validation-status enforcement, batch path only** — `scoring_engine.components.py`
   genuinely reads and enforces matched-null/global-FDR/walk-forward/lifecycle status from the same
   Strategy Library, but only within the batch/backtest scoring pipeline, never reachable from the live
   pipeline.

## 7. Missing edges (documented, but not transferred at all)

All 40 Track-1 edges (§2.1), all Track-2 strategy IDs beyond the inert structural-contract link (§6), and
all 18 Track-3 candidates (§2.3). None of these appear anywhere in `ai_trader/` code, by any of their own
naming conventions, confirmed by exhaustive grep (§3.1, §3.3). Reiterating the naming-similarity warning
per your instruction #7: `market_intelligence`'s modules sharing words with Track-1 edge names
(`structure`, `volatility`, `session_behavior`) were built independently, before the Edge Discovery
Program existed, and the Program's own registry explicitly disclaims any wiring to them — a textbook case
of the exact false-transfer trap you asked this audit to guard against.

## 8. Rejected edges/strategies that must be excluded — verified absent

Explicitly rejected/closed on the Research Lab side: **S29** (Friday-up, flagged data-mining artifact,
*"Do NOT validate as edges"*), **S31** (month-boundary-short, same), **S17**-pwhigh-breakout (EXPLORATORY,
negative OOS), and the 9 S21-S40 families marked **NEGATIVE — CLOSED** (S21, S23, S25, S26, S27, S28,
S30, S38, S40). K04's calendar-effect cluster (S18/S29/S31) is separately marked **OVERFIT**.

**Verified: none of these IDs appear anywhere in `ai_trader/` code.** This is a genuinely good finding —
nothing rejected has leaked in — but it holds only because *nothing at all* has been wired yet (§3), not
because a structural guard exists. `RecognitionCandidate.strategy_id`/`CandidateSignal.strategy_id` are
both free-form strings validated only for non-emptiness, with **no membership check against any strategy
registry** (`recognition_engine_live/types.py:48-49` confirmed by direct read). If a signal source is ever
built without also adding this check, there is currently nothing in the type system that would stop a
rejected ID from reaching a live decision.

## 9. Traceability — direct answers to your six questions (§6 of your request)

For any live-generated signal, can the system demonstrate:

| Question | Answer |
|---|---|
| Which edge generated it | **NO** — no field for an edge/source ID exists anywhere in `RecognitionResult`, `RecognitionCandidate`, or `CandidateSignal` (all three types read in full; none has it) |
| Which experiment it came from | **NO** — same reason; no provenance field of any kind |
| What validation status it has | **NO** — no live type carries matched-null/global-FDR/holdout/Red-Team-verdict status; `ConfidenceAssessment` doesn't either |
| What conditions were met | **PARTIAL** — `CalculationTraceStep` traces and `reason_codes` give a genuine, comprehensive audit trail of internal pipeline checks (data quality, MTF agreement, sufficiency, risk/portfolio gates) |
| What conditions were missing | **PARTIAL** — same mechanism, same caveat below |
| Why accepted or rejected | **PARTIAL for internal pipeline logic; NO for edge-specific logic** |

The "PARTIAL" answers are real and well-built — the never-short-circuit, full-reason-code discipline
established across Phases 2-10 genuinely does explain every internal engine's own accept/reject decision.
But that trace explains *pipeline mechanics* (was data fresh, did MTF agree, was there enough margin) —
it cannot explain "why this counts as edge E015" or "why this passed Red Team," because no code path ever
attaches that information in the first place. **Traceability back to Research Lab is broken at the first
link, structurally, not due to a missing report or a bug** — and moot in current practice since no live
signal is ever generated at all (§3.5).

Direct answers to §5 of your request (does AI Trader concretely know structure/confirmations/invalidation
/regime/no-trade conditions/score contribution per edge): **No, for all six**, for the same root reason —
`AUTHORIZED_PATTERNS` are generic per-dimension statistical buckets (§3.4), not implementations of any
specific edge's structure, confirmation checklist, invalidation rule, or regime-of-validity finding (e.g.
E026's UP-only significance or S39's efficiency-gating are Research-Lab findings that exist only in
markdown, never encoded as a live condition anywhere).

## 10. Contradictions found (reported as-is, not corrected, per your instruction)

1. `scoring_engine/README.md:7-9` states: *"This package is documentation and JSON Schema only. No
   runtime code, no executable logic... It modifies nothing: Research Lab, engine, Strategy Library... are
   all untouched."* This is contradicted by the package's actual `.py` files (`components.py`,
   `evidence.py`, `engine.py`), which are real, executable Python that reads (not writes) the Strategy
   Library's `matched_null_status`/`walk_forward_status`/`global_fdr_status`/`Lifecycle` fields as a live
   scoring input (§3.2, §6.3).
2. `risk_manager/README.md:9-11` and `strategy_manager/README.md:8-9` carry near-identical
   "documentation only, no runtime code" language, also contradicted by those packages' substantial real
   `.py` implementations (`strategy_manager/manager.py`, `loader.py`, `contract.py`, etc.).
3. `execution_engine/EXECUTION_ENGINE_ARCHITECTURE.md:185`, `risk_manager/RISK_API.md:103`,
   `scoring_engine/SCORING_API.md:91`, `signal_engine/SIGNAL_ENGINE_ARCHITECTURE.md:217,220` all assert
   *"Research Lab / Knowledge Base / Strategy Library: NO, never."* This is accurate for every package
   named except `scoring_engine`, whose own architecture doc makes the same "never" claim (line 145,149)
   while its code (item 1 above) does read Strategy Library evidence — i.e., the contradiction is
   internal to `scoring_engine`'s own documentation, not just stale relative to a sibling package.
4. None of the 9 live-wired packages built in Phases 2-10 (`recognition_engine_live`, `confidence_engine`,
   `context_engine`, `edge_intelligence`, `risk_manager_live`, `portfolio_manager_live`, `order_manager`,
   `execution_orchestrator`, `mt5_demo_execution`) has any architecture doc making a Research-Lab-access
   claim at all (positive or negative) — their only documentation is inline docstrings. This is not a
   contradiction, but a coverage gap worth naming: the "no Research Lab access" assurance that exists for
   the older batch packages was never restated for the newer live packages, even though the live packages
   are precisely where the question in this audit actually matters.

## 11. Risks before starting a continuous DEMO run

1. **No trade would ever be generated.** With `CandidateSignal` never constructed in production, a
   continuous DEMO run today produces zero activity regardless of any other finding in this report —
   this is the most immediate, structural blocker.
2. **If a signal source is built next without also closing the gaps above, nothing stops an
   unvalidated or explicitly rejected strategy from reaching a live order.** `strategy_id` fields are
   free-form and unchecked against any registry (§8); `edge_intelligence` loads but ignores validation
   status (§3.2); `strategy_health_component` is a disabled placeholder (§3.2) — there is currently no
   single enforcement point where "is this ID allowed to trade live" would be answered.
3. **The Strategy Library's own evidence is largely unvalidated by design right now** — *"strict
   validation = STRICT VALIDATION PENDING for all"* (global-FDR CEO-gated, not run) — so even a
   theoretically "connected" version of today's code would currently have nothing statistically validated
   to enforce.
4. **Terminal holdout breach (Track 1)** — a data-integrity incident on the Research Lab side, unrelated
   to AI Trader code, but relevant to how much trust any future manual port of those 5 edges' findings
   should carry until the clean rerun completes.
5. **README-vs-code contradictions (§10)** create a real risk of a future contributor trusting a stale
   "no runtime code" claim and missing that `scoring_engine` already does read Research-Lab statistical
   status — in either direction (assuming too little OR too much is connected).
6. **No architecture-level "Research Lab access" statement exists for any of the 9 live packages** — the
   one place this audit's central question is actually decided has no standing documentation answering it
   at all; today the answer is "no" by code inspection only (§3), not by any durable, reviewable
   assertion.

## 12. Final Verdict

# NOT READY

Not because anything built in Phases 2-10 is broken — every engine audited elsewhere in this repo passes
its own tests and follows its own fail-closed discipline correctly. This verdict is about a different
question: **whether Research Lab knowledge has actually reached AI Trader's live decision-making.** It
has not, at any point along the chain, and the chain itself currently has no entry point for a live
signal to begin with. Both facts must be resolved — a live signal source, and an actual, enforced,
traceable link from a specific validated edge to a specific live decision — before a continuous DEMO run
would exercise anything resembling transferred Research Lab knowledge, rather than either nothing at all
or an unvalidated, untraceable, unguarded input.

---

**Stopping here per your instruction.** No modification, implementation, optimization, threshold change,
or continuous DEMO run was performed or started. No next audit will begin without explicit authorization.
