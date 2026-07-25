# AI Trader — Phase 2A: Safety Precondition Dependency Graph

**Mode: DESIGN ONLY.** No code was written or modified. This orders the 10 "DOESN'T EXIST" preconditions
from `AI_TRADER_DEMO_READINESS_AUDIT.md` by dependency, not severity, per explicit instruction. The 4
"PARTIAL" preconditions from that audit are out of scope here (not requested). One ordering constraint is
imposed externally (persistent suspension state first); everything else below is derived, not assumed.

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
| 1 | **Persistent suspension state** — unify `EngineState.SUSPENDED` (`guards.py`, thrown away at `risk_manager_live/engine.py:123`), the P&L fields item 2 computes, and `emergency_stop` (`execution_orchestrator/engine.py:69`) into one mechanism | Nothing to be *coded* — the state-machine/persistence container can be built now. Depends on item 2 to be *trustworthy* rather than structurally present but fed placeholder P&L. | Items 3, 6, 7 — none of them is safe to connect to anything real before this exists (the CEO's explicit ordering rule) | **M** — touches 3 existing modules (`risk_manager/guards.py` reading, not modifying; `risk_manager_live/engine.py`; `execution_orchestrator/engine.py`), needs a new persistence concept, needs fail-before/pass-after tests per module |
| 2 | **Automatic P&L computation** from `open_positions`/`recent_closed_positions` (currently raw caller-supplied fields, `risk_manager/types.py:330-336`) | Nothing to be *coded* — a pure function over position/deal history, unit-testable with fixtures. Needs item 5 (or the existing `OrderLedger`) to receive *real* data once live. | Item 1 (to be meaningful, not just present) | **S/M** — bounded, pure-function scope; size depends on how much `OpenPosition`/`ClosedPosition` already carries vs. needs extending |
| 3 | **Cross-candidate / per-cycle budget accounting** — nothing threads an updated `PortfolioState`/`AccountState` between candidates evaluated in the same cycle | Freestanding to design (a state-threading mechanism can be built and tested with synthetic multi-candidate batches without item 6 existing yet) | Item 7 — an unattended loop evaluating multiple candidates per cycle is unsafe without this | **M** — real design decision (mutable accumulator vs. re-fetch-between-candidates), touches `execution_orchestrator`'s calling convention |
| 4 | **Cost-model reconciliation** — research assumes `cost_round_trip = 0.4 pts` (XAUUSD), no commission observed anywhere, one single-tick spread sample (0.07 vs. 0.1 assumed), unresolved 10× tick/point mismatch | Item 5's bridge, extended to also read deal/position history's commission field — an engineering extension. **Also blocked outside code entirely**: knowing this broker's actual per-lot commission rate is not something any amount of engineering effort here produces on its own. | Nothing else in this graph | **S** for the engineering piece (extend the bridge); **blocked regardless of effort** on external broker data — flagged, not estimated as if effort were the bottleneck |
| 5 | **Live MT5 account/instrument/equity bridge** — `AccountState`/`InstrumentSpecification`/`PortfolioState.equity` are constructed only in test fixtures repo-wide | Nothing new — reuses the already-validated, real-terminal-proven `MT5ReadOnlyBrokerAdapter`/`MT5DemoBrokerAdapter` (Phase 1/10), read-only | Items 2, 4 (real data); item 6 (real risk evaluation once it produces more than the Null rule) | **M** — new projection functions/types, tests, plus the empirical tick/point re-verification the risk-sizing design doc already flagged as needed before trusting a derived point-value |
| 6 | **Live signal source** (CEO's Piesa 1 bar feed + Piesa 2 candidate producer with injected `NullRecognitionRule` + Piesa 3 append-only journal reusing `shadow_evidence` types) | Policy-gated behind item 1 (safety-first rule, not a code dependency). Its own minimal acceptance test (zero candidates, `NullRecognitionRule`) needs neither item 5 nor real data. Needs item 5 before any *real* recognition rule is ever connected. | Item 3 (only load-bearing once this exists); item 14 (the "socket" a future validated edge plugs into) | **L** — three sub-pieces (bar producer, candidate producer + injected-rule interface, journal), a new static import-independence test mirroring `telegram_notifier`'s, and the end-to-end zero-candidates acceptance test |
| 7 | **Scheduler/loop mechanism** for unattended operation | Substantially satisfied by item 6 as specified — Piesa 1's bar-close events ARE the repeating, unattended trigger; this may not need to be a separate build at all. | Item 14 indirectly (a validated edge only matters once something keeps calling the pipeline) | **Not separately estimated** — flagged as likely subsumed by item 6; the one gap item 6 alone doesn't cover is long-running-process robustness (crash/restart/monitoring), which isn't itemized anywhere in the four audits and would need its own scoping if the CEO wants it covered |
| 10 | **Direction-vs-stop validation** — only `abs(entry - stop)` is checked anywhere (`risk_manager_live/engine.py:109`), never which side of entry the stop is on | None — self-contained | Item 6 — every real candidate a future signal source produces should pass this before being trusted; not needed for item 6's own Null-rule acceptance test | **S** — single validation rule, smallest and most independent item in this list |
| 11 | **`PortfolioDailyState` ownership/reset** — its own docstring names a Phase-9 owner that was never built (`portfolio_manager_live/types.py:48-51`) | None — an owner + reset function, testable with a fake clock, independent of anything live existing yet | Loosely related to item 3 (both are "state tracked/reset across cycles"), no hard dependency | **S** — small, self-contained, same shape as item 10 |
| 14 | **Live decision chain informed by a validated edge** — `AI_TRADER_KNOWLEDGE_TRANSFER_AUDIT.md`'s own verdict; `AUTHORIZED_PATTERNS` is scaffolding, not real patterns | Item 6 (needs the socket — the injected `RecognitionRule` interface — to exist before anything can plug into it) | Nothing — terminal node | **Not S/M/L** — the code change (one more `RecognitionRule` implementation, wired into an interface built to make this trivial) is likely small once unblocked; the actual constraint is Flow A / Statistician / Validation Engine's own research timeline, explicitly outside this graph's control and, per the CEO's own words, possibly months away |

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

**Stopping here per instruction.** No implementation order has been chosen — the table above is a
dependency map, not a build plan. Waiting for approval of the ordering before implementing anything, one
item at a time, with a report and commit after each.
