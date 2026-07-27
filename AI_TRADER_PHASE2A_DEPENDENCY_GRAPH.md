# AI Trader — Phase 2A: Safety Precondition Dependency Graph

**Mode: DESIGN ONLY**, except where explicitly marked DONE below. This orders the 10 "DOESN'T EXIST"
preconditions from `AI_TRADER_DEMO_READINESS_AUDIT.md` by dependency, not severity, per explicit
instruction. The 4 "PARTIAL" preconditions from that audit are out of scope here (not requested). One
ordering constraint is imposed externally (persistent suspension state first); everything else below is
derived, not assumed.

## Validation scope rule (CEO decision, 2026-07-26)

Step 4 stopped a full-tree `pytest ai_trader/` run (unbounded, pulling in unrelated heavy research
suites) and rescoped to Step 3's own precedent — the same named list of packages, not the whole
repository. That was the right call for Step 4 specifically, because `mt5_account_bridge` is a brand-new
package nothing else imports. But the same reduced scope was also used for Step 3, which modified two
EXISTING, already-shared files (`execution_orchestrator/engine.py`, `reason_codes.py`) — and that worked
out correctly only because nothing outside the named list happened to import those two files in a way the
change could break. It was not verified, it was fortunate. **Standing rule, effective now:**

- **Adding a new, standalone package nothing imports yet** → reduced scope (that package + its own direct
  dependencies) is sufficient. State in the report why the package is currently unimported, so the reduced
  scope is a justified fact, not an assumption.
- **Modifying an EXISTING file that anything outside the current step's named scope imports** → run the
  entire `ai_trader/` tree, regardless of how long it takes. No exceptions, no scope negotiation after the
  fact — decide this BEFORE choosing the pytest invocation, not after judging the result looks fine.

## Approved order (CEO decision, 2026-07-25) and status

1. **#1 Persistent suspension state — DONE.** `a27802d`, pushed to `trader/ai-trader-implementation`,
   confirmed on remote (`git ls-remote --heads trader` → `a27802d71e4cbb4e06a6eafca6fa383bdbb1662e`).
   See `AI_TRADER_PHASE2A_STEP1_PERSISTENT_SUSPENSION_REPORT.md`.
2. **#10, #11 — DONE.** `5d8e57a`, pushed and confirmed on remote. See
   `AI_TRADER_PHASE2A_STEP2_DIRECTION_STOP_AND_DAILY_RESET_REPORT.md`.
   **Observation, not a task (CEO note, 2026-07-25, confirmed as a standing precedent — the correct
   reading of the "no test that fails" rule is as a definition of work surface, not just a change
   -verification gate: if a defect can't be demonstrated, it isn't touched):** `TradeProposal`'s and
   `CandidateSignal`'s new invariant (entry != stop, correctly sided for direction) is enforced only in
   `__post_init__`, which a frozen dataclass's own `object.__setattr__` can bypass after construction —
   confirmed directly, since two of Step 2's own tests use exactly this bypass deliberately, to reach the
   risk gate's own independent check. The invariant is therefore NOT tamper-proof against a caller that
   deliberately or accidentally mutates a constructed instance. Not itemized in any of the four audits;
   not authorized as a fix; recorded here as a known, disclosed limitation only.
3. **#2 — DONE.** New package `ai_trader/mt5_pnl_source/`: the ONE real implementation of
   `PortfolioStateSource`, fail-closed on missing/incomplete MT5 data (never defaults, never estimates).
   Also closed an adjacent gap the real implementation exposed: `orchestrate()` didn't wrap the circuit
   check in a try/except, so a raising source would have crashed past its own "never propagates"
   contract — now denies with `CIRCUIT_DATA_UNAVAILABLE`. See
   `AI_TRADER_PHASE2A_STEP3_PNL_SOURCE_REPORT.md`. Virtual/shadow implementation deliberately not
   built (same interface, later authorization, per CEO instruction).
4. **#5 — DONE.** New package `ai_trader/mt5_account_bridge/`: `MT5AccountBridge` projects
   `account_info()`/`symbol_info()` (already part of the frozen Phase 1 `MT5Gateway` Protocol, no gateway
   extension needed) into `AccountState`/`InstrumentSpecification`. Fail-closed on any missing/incomplete
   field, never caches (every call re-reads the gateway fresh). Not wired into `orchestrate()` or any
   other caller — this step built the bridge itself only. See
   `AI_TRADER_PHASE2A_STEP4_ACCOUNT_BRIDGE_REPORT.md`.
   **NEW — equity high-water-mark survives a process restart** (CEO-added, 2026-07-26, disclosed as
   Step 3's own limitation): `MT5PortfolioStateSource` only ratchets its high-water mark from whichever
   equity value it first observes after construction — a process restart during a months-long shadow run
   resets that reference. The circuit breaker would then compute drawdown against a false, lower peak,
   and could fail to trip when it should. Same class of problem as Step 1's persistent suspension state,
   on a different variable. Must exist **before Phase 3**. **Not authorized to build now.**
   **NEW — consecutive-loss detection beyond the weekly window** (CEO-added, 2026-07-26, disclosed as
   Step 3's own limitation): bounded to the same 7-day window fetched for weekly P&L; a losing streak
   older than 7 days would not be seen in full. Must exist **before Phase 3**. **Not authorized to build
   now.**
5. **#6 — DONE.** New package `ai_trader/live_signal_source/`: `LiveBarFeed` (Piesa 1, emits a bar only
   at close, proven via a dedicated forming-bar test), `CandidateSignalProducer` (Piesa 2, injected
   `RecognitionRule`, shipped only with `NullRecognitionRule`), `LiveSignalJournal` (Piesa 3,
   append-only, in-memory). Acceptance test passes verbatim: the pipeline runs end-to-end and produces
   zero candidates. Two disclosed design decisions, both explained in the report: (1) a new
   `LiveCandidate` type instead of importing `execution_orchestrator.types.CandidateSignal` directly,
   since that module transitively imports execution-capable machinery at load time; (2) the journal
   reuses `Direction` (the same shared type `shadow_evidence.types` itself reuses) rather than any of
   `shadow_evidence`'s six record dataclasses verbatim, none of which fit a pre-risk-evaluation event
   without fabricating fields. See `AI_TRADER_PHASE2A_STEP5_LIVE_SIGNAL_SOURCE_REPORT.md`. Not wired
   into `orchestrate()` or any other caller — no scheduler/loop drives it yet (that's item #7, next).
6. **NEW — long-running process robustness** (crash/restart/resume-from-correct-state/stopped-signal for
   a multi-week unattended shadow process). Not itemized in any of the four audits; added by CEO decision
   after this graph's own §7 flagged it as a gap item 6 alone doesn't cover.
7. **NEW — EMERGENCY_STOP reset operation** (this update, 2026-07-25) — see its own entry below. Must
   exist **before Phase 3** (the long-running shadow-mode operational run), not before Phase 3 is
   *designed*. **Not authorized to build now** — explicitly deferred, added to this graph only.
8. **#3, #4** — cross-candidate/per-cycle budget accounting, cost-model reconciliation. Moved AFTER #6 by
   explicit CEO decision: in shadow mode no order is ever sent (`Piesa 2` never receives the execution
   adapter, enforced statically) — nothing spends margin, so a per-cycle budget has nothing to exceed, and
   no commission is ever paid, so cost reconciliation changes nothing observed. Both remain real
   preconditions for DEMO execution specifically, not for observation; deferring them costs nothing, while
   every day of shadow observation delayed is a day of forward evidence that can never be recovered.
9. **#7** — confirm whether a separate scheduler/loop is needed at all once #6 is built, or whether the
   bar-close event already satisfies it (the CEO's own framing: "probabil da, verifică și raportează").
10. **#14** — validated edge connected. Entirely outside engineering control; not planned, not estimated.

The sections below are the ORIGINAL dependency analysis this order was built from — kept for the
reasoning/evidence behind each item, not superseded by the numbered list above.

---

## The one fixed constraint

**Persistent suspension state is first — not because it's the most severe finding, but because it's the
only item every other capability's safety depends on.** A system that can generate real candidates (item
6) or run unattended (item 7) but doesn't remember it already breached a limit is exactly the failure
mode the whole audit sequence exists to prevent. Everything below respects this as fixed; the rest of the
order is derived from actual dependency, and multiple valid orderings exist beyond the constraints noted.

## Graph (topological reading)

```
[1] Persistent suspension state  ─────────────────────────────────┐
      │ (needs real P&L to be TRUSTWORTHY, not just to be CODED)  │
      ▼                                                            │ (safety-first
[2] Automatic P&L computation                                      │  policy gate,
      │                                                             │  not a code
      ▼                                                             │  dependency)
[5] Live MT5 account/instrument/equity bridge                       │
      │           │                                                 │
      ▼           ▼                                                 │
[4] Cost-model   [3] Cross-candidate / per-cycle                    │
    reconciliation   budget accounting                              │
    (partly blocked   (freestanding to design;                      │
    outside code)     load-bearing once [6] exists)                 │
                            │                                       │
                            ▼                                       ▼
                      [6] Live signal source  ◄─────────── gated by [1]
                          (bar feed + candidate producer + journal)
                            │                    ▲
                            │                    │ substantially
                            ▼                    │ subsumed by [6]
                      [7] Scheduler/loop ─────────┘ as specified
                            │
                            ▼
                      [14] Live decision chain informed by a
                           validated edge — blocked externally
                           on Flow A / Statistician / Validation
                           Engine, not on this graph

[10] Direction-vs-stop validation  — no dependencies, freestanding
[11] PortfolioDailyState ownership/reset — no dependencies, freestanding
```

`[10]` and `[11]` have no edges to anything else in this graph — they're listed in the ordered table below
immediately after `[1]` because they're the smallest, most self-contained safety patches, not because
anything requires them first.

---

## Ordered table

| # | Precondition (Demo Readiness Audit item) | Depends on | What depends on it | Effort |
|---|---|---|---|---|
| 1 | **DONE (`a27802d`).** Persistent suspension state — unified `EngineState.SUSPENDED` (`guards.py`, previously thrown away at `risk_manager_live/engine.py:123`), the P&L fields item 2 will compute (currently the same injected `PortfolioStateSource` interface, no implementation yet), and `emergency_stop` (`execution_orchestrator/engine.py:69`) into one mechanism, `risk_manager_live/circuit_breaker.py::evaluate_circuit_state`. Verified fail-before/pass-after at three levels including a `git stash`-verified orchestrator integration test; pushed and confirmed on `trader` remote. | Nothing to be *coded* — the state-machine/persistence container can be built now. Depends on item 2 to be *trustworthy* rather than structurally present but fed placeholder P&L. | Items 3, 6, 7, and now item 16 below — none of them is safe to connect to anything real before this exists (the CEO's explicit ordering rule) | **M — DONE** |
| 2 | **Automatic P&L computation** from `open_positions`/`recent_closed_positions` (currently raw caller-supplied fields, `risk_manager/types.py:330-336`) | Nothing to be *coded* — a pure function over position/deal history, unit-testable with fixtures. Needs item 5 (or the existing `OrderLedger`) to receive *real* data once live. | Item 1 (to be meaningful, not just present) | **S/M** — bounded, pure-function scope; size depends on how much `OpenPosition`/`ClosedPosition` already carries vs. needs extending |
| 3 | **Cross-candidate / per-cycle budget accounting** — nothing threads an updated `PortfolioState`/`AccountState` between candidates evaluated in the same cycle | Freestanding to design (a state-threading mechanism can be built and tested with synthetic multi-candidate batches without item 6 existing yet) | Item 7 — an unattended loop evaluating multiple candidates per cycle is unsafe without this | **M** — real design decision (mutable accumulator vs. re-fetch-between-candidates), touches `execution_orchestrator`'s calling convention |
| 4 | **Cost-model reconciliation** — research assumes `cost_round_trip = 0.4 pts` (XAUUSD), no commission observed anywhere, one single-tick spread sample (0.07 vs. 0.1 assumed), unresolved 10× tick/point mismatch | Item 5's bridge, extended to also read deal/position history's commission field — an engineering extension. **Also blocked outside code entirely**: knowing this broker's actual per-lot commission rate is not something any amount of engineering effort here produces on its own. | Nothing else in this graph | **S** for the engineering piece (extend the bridge); **blocked regardless of effort** on external broker data — flagged, not estimated as if effort were the bottleneck |
| 5 | **Live MT5 account/instrument/equity bridge** — `AccountState`/`InstrumentSpecification`/`PortfolioState.equity` are constructed only in test fixtures repo-wide | Nothing new — reuses the already-validated, real-terminal-proven `MT5ReadOnlyBrokerAdapter`/`MT5DemoBrokerAdapter` (Phase 1/10), read-only | Items 2, 4 (real data); item 6 (real risk evaluation once it produces more than the Null rule) | **M** — new projection functions/types, tests, plus the empirical tick/point re-verification the risk-sizing design doc already flagged as needed before trusting a derived point-value |
| 6 | **Live signal source** (CEO's Piesa 1 bar feed + Piesa 2 candidate producer with injected `NullRecognitionRule` + Piesa 3 append-only journal reusing `shadow_evidence` types) | Policy-gated behind item 1 (safety-first rule, not a code dependency). Its own minimal acceptance test (zero candidates, `NullRecognitionRule`) needs neither item 5 nor real data. Needs item 5 before any *real* recognition rule is ever connected. | Item 3 (only load-bearing once this exists); item 14 (the "socket" a future validated edge plugs into) | **L** — three sub-pieces (bar producer, candidate producer + injected-rule interface, journal), a new static import-independence test mirroring `telegram_notifier`'s, and the end-to-end zero-candidates acceptance test |
| 7 | **Scheduler/loop mechanism** for unattended operation | Substantially satisfied by item 6 as specified — Piesa 1's bar-close events ARE the repeating, unattended trigger; this may not need to be a separate build at all. | Item 14 indirectly (a validated edge only matters once something keeps calling the pipeline) | **Not separately estimated** — flagged as likely subsumed by item 6; the one gap item 6 alone doesn't cover is long-running-process robustness (crash/restart/monitoring), which isn't itemized anywhere in the four audits and would need its own scoping if the CEO wants it covered |
| 10 | **Direction-vs-stop validation** — only `abs(entry - stop)` is checked anywhere (`risk_manager_live/engine.py:109`), never which side of entry the stop is on | None — self-contained | Item 6 — every real candidate a future signal source produces should pass this before being trusted; not needed for item 6's own Null-rule acceptance test | **S** — single validation rule, smallest and most independent item in this list |
| 11 | **`PortfolioDailyState` ownership/reset** — its own docstring names a Phase-9 owner that was never built (`portfolio_manager_live/types.py:48-51`) | None — an owner + reset function, testable with a fake clock, independent of anything live existing yet | Loosely related to item 3 (both are "state tracked/reset across cycles"), no hard dependency | **S** — small, self-contained, same shape as item 10 |
| 14 | **Live decision chain informed by a validated edge** — `AI_TRADER_KNOWLEDGE_TRANSFER_AUDIT.md`'s own verdict; `AUTHORIZED_PATTERNS` is scaffolding, not real patterns | Item 6 (needs the socket — the injected `RecognitionRule` interface — to exist before anything can plug into it) | Nothing — terminal node | **Not S/M/L** — the code change (one more `RecognitionRule` implementation, wired into an interface built to make this trivial) is likely small once unblocked; the actual constraint is Flow A / Statistician / Validation Engine's own research timeline, explicitly outside this graph's control and, per the CEO's own words, possibly months away |
| 15 | **NEW — long-running process robustness** (CEO-added, 2026-07-25): crash/restart/resume-from-correct-state/stopped-signal for a shadow process meant to run for months. Not itemized in any of the four audits. | Item 6 (nothing to make robust until the bar-feed/candidate-producer process exists) | Phase 3 (the actual multi-week shadow run) — cannot safely start without it | **Not yet scoped** — no design work done; flagged as needing its own investigation before an S/M/L estimate is meaningful |
| 16 | **NEW — `EMERGENCY_STOP` reset operation** (CEO-added, 2026-07-25, this update): item 1's own disclosed gap — once `EMERGENCY_STOP` is entered, it is currently permanent, with no clear/resume path. Harmless for short DEMO tests; unacceptable for a shadow process running for months, where a single virtual-P&L trip with no reset silently ends all further forward-evidence collection. **Explicit specification, given verbatim by the CEO — do not deviate without re-confirming:** the reset must be a **deliberate, explicitly-authorized action** (never automatic, never implicit on process restart), and every reset must be **journaled with its reason and timestamp**. Mirrors the frozen batch engine's own `clear_emergency()` precedent (guarded, explicit, never silent) rather than inventing a new pattern. | Item 1 (extends its `TradingCircuitState`/`EMERGENCY_STOP` concept directly) | Item 15 and Phase 3 — the long-running shadow process cannot safely run for months without this existing first | **Not yet scoped** — **NOT AUTHORIZED to build now**; this row exists to hold the requirement in the graph, not to schedule it |

---

## What this graph does and doesn't claim

- Items 1, 10, 11 have no code dependency on anything else — they could, in principle, be started in any
  order relative to each other. Item 1 is fixed first by explicit instruction, not by this analysis.
- Items 2 and 5 are each independently buildable (2 as a pure function, 5 as a read-only bridge reusing
  already-validated adapters) but only become *meaningful* once the other exists alongside real data —
  noted, not resolved, since resolving it is a build decision, not a dependency fact.
- Item 4's engineering piece is small; its actual constraint is a fact about the broker this repository
  cannot produce through code.
- Item 7 may not be a separate deliverable at all, depending on how item 6 is actually built — flagged
  rather than assumed either way.
- Item 14 is the only item whose primary blocker is a research timeline, not engineering — consistent
  with the CEO's own opening framing ("Punctul 3 așteaptă un edge validat, și acela poate întârzia luni de
  zile").
- Items 15 and 16 were not in the original 10-item Demo Readiness list — both surfaced from this graph's
  own analysis (§ "What this graph does and doesn't claim," item 7's flagged gap) and from disclosure in
  Step 1's own implementation report (`EMERGENCY_STOP` has no reset path). Both are held in this graph as
  requirements, neither is authorized to build yet.

**Current status**: item 1 done, pushed, confirmed on remote. Items 10/11 next, awaiting approval. Items
15/16 are documented requirements only — no design work, no code, not scheduled. Every item beyond 1
remains a dependency map, not a build plan, until explicitly authorized one at a time, with a report and
commit — and, per the CEO's standing instruction after Step 1, a `git`-verified fail-before/pass-after
demonstration — after each.
