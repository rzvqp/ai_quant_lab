# AI Trader — Official Decisions Log

**Last updated**: 2026-07-25. This document records CEO decisions that govern AI Trader's scope and
authorization state — not technical design decisions (those live in the per-phase design docs) and not
implementation status (see `AI_TRADER_PROJECT_AUDIT.md`). Entries are dated and, where the decision was
stated verbatim, quoted.

1. **Phases 2-10 are approved and closed**, under the sweeping CEO authorization of 2026-07-24/25
   ("Continuă conform autorizației existente. Phase 2, Phase 3 și Phase 4 sunt considerate aprobate...
   Continuă cu: Phase 5 ... Phase 10"), subject to the standing discipline (reuse-check → design →
   implement → test → mypy strict → regression → report → commit → clean tree) and the standing
   safety rules (no LIVE trading, no MetaTrader5 import outside the Broker Adapter, no risk/portfolio
   control removed, fail-closed everywhere).

2. **XAUUSD remains the primary trading instrument. BTCUSD is NOT an approved strategy or symbol.**
   BTCUSD was authorized exactly once (2026-07-25) solely to validate the Phase 10 execution
   infrastructure while XAUUSD's market was closed for the weekend. CEO's own framing: *"Acesta NU este un
   test al strategiei și NU este un test de performanță. Este exclusiv un test al infrastructurii de
   execuție MT5."* This does not extend to any future use of BTCUSD without separate, explicit
   authorization.

3. **Continuous / unattended DEMO execution is NOT yet authorized.** Nothing in Phases 2-10, including
   the successful BTCUSD test, constitutes authorization to run the pipeline unattended or repeatedly.
   (It is also currently impossible regardless of authorization — no live signal source exists, per
   `AI_TRADER_PROJECT_STATE.md` §7.) The stated plan (CEO, 2026-07-25): once XAUUSD's market reopens
   Monday, continue exclusively on XAUUSD, DEMO account — but this still requires its own explicit
   go-ahead, not implied by Phase 10's closure.

4. **5%-of-equity risk per trade is a stated requirement, not an authorized implementation.** The CEO
   has specified the target risk model (5% of current DEMO equity per trade, volume computed
   automatically from stop-loss distance and instrument value, never a fixed lot) and explicitly required
   a design-only deliverable first: *"Nu implementa încă această logică; prezintă-mi mai întâi designul și
   aşteaptă aprobarea mea înainte de orice modificare de cod."* The design
   (`RISK_SIZING_5PCT_XAUUSD_DESIGN.md`) is delivered and committed (`125e171`), pending CEO decisions on
   5 open items (most importantly the current 0.01-lot hard safety ceiling, which as configured today
   would reject any correctly-sized 5%-risk order). **No code for this feature exists.**

5. **Audit sequence, as ordered by the CEO**: Knowledge Transfer Audit → Decision Logic Audit → Risk
   Audit → Demo Readiness Audit. The **Knowledge Transfer Audit is complete**
   (`AI_TRADER_KNOWLEDGE_TRANSFER_AUDIT.md`, 2026-07-25, verdict **NOT READY** — zero Research Lab
   edges/strategies are transferred into the live decision chain at the code level, and no live signal
   source exists to carry them even if they were). **Decision Logic Audit, Risk Audit, and Demo Readiness
   Audit have not started** and require separate, explicit authorization each — none is implied by the
   Knowledge Transfer Audit's completion.

6. **This official-save task itself** (2026-07-25) is explicitly inventory/documentation/verification
   only — no new functionality, no logic changes, no optimization, no new audit, no continuous DEMO run.
   Scope confirmed against the CEO's own instruction before execution.

7. **Standing prohibitions, still in force, restated for a future session's benefit**: no LIVE trading
   account access (structurally impossible, not just policy); no `import MetaTrader5` outside the Broker
   Adapter (statically enforced per-package); no removal of any risk or portfolio control; no automatic
   AlgoTrading activation (no code path exists that could do this even if attempted); no bypassing safety
   checks; no auto-retry on order submission beyond the existing idempotency mechanism; no terminal/account
   setting changes by code (AlgoTrading was enabled manually, by the CEO, in the terminal UI, between
   BTCUSD test attempts — never by any script in this repo).
