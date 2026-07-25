# AI Trader — Project Audit (Implemented vs Tested vs Validated vs Documented vs Unaudited vs Unauthorized)

**Last updated**: 2026-07-25. Companion to `AI_TRADER_PROJECT_STATE.md`. This document exists to keep six
distinct claims separate, since conflating them has been an explicit risk called out earlier this session
(README-vs-code contradictions found in `AI_TRADER_KNOWLEDGE_TRANSFER_AUDIT.md` §10): **implemented**
(code exists and runs), **tested** (has automated test coverage), **validated** (operationally proven
against something real — a live terminal, real data), **documented only** (described in a `.md` file with
no or partial code backing), **not yet audited** (nobody has independently checked it against its own
claims), **not authorized** (explicitly not permitted to run, regardless of technical readiness).

---

## 1. IMPLEMENTED — code exists, unit-tested, mypy-strict clean

All of Phases 1-10 (`ai_trader/execution_engine` Phase 1 broker adapter, `risk_manager_live`,
`order_manager`, `portfolio_manager_live`, `telegram_notifier`, `context_engine`,
`recognition_engine_live`, `confidence_engine`, `execution_orchestrator`, `mt5_demo_execution`). Confirmed
this session: `pytest` across these packages + their direct dependencies (`execution_engine`,
`risk_manager`, `edge_intelligence`, `market_intelligence`, `context_memory`, `scoring_engine`) →
**1332 passed, 2 skipped, 0 failed**; `mypy --strict` on the 9 Phase 2-10 packages → **clean, 107 source
files**. Full detail and per-package counts: `AI_TRADER_TEST_STATUS.md`.

## 2. TESTED — has real automated coverage, not just present

Same set as §1 — every phase's own test suite (37+43+37+34+19+23+23+18+43 = 277 originally reported,
re-confirmed at 1332 total when counting all dependency-package tests together) plus static
import-independence tests per package (no literal `MetaTrader5` outside Phase 1/10, no forbidden
cross-package imports, no order-submission vocabulary in packages that shouldn't have it).
**Distinction from "validated" (§3): these are all fake/fixture-driven unit and integration tests. Only
the items in §3 have been checked against a real external system.**

## 3. VALIDATED — operationally proven against something real

- **MT5 real-terminal connectivity, DEMO/server verification, AlgoTrading detection** (Phase 1,
  `MT5_CONNECTIVITY_PROBE_REPORT.md`) — real terminal.
- **Phase 10 send path, end-to-end, once, for one symbol (BTCUSD)**: ticket `491745557`, confirmed,
  closed, verified flat — `BTCUSD_PHASE10_OPERATIONAL_TEST_REPORT.md`. This is the only real order this
  project has ever sent.
- **Market-closed detection gate**: proven against the real terminal for XAUUSD (stopped correctly at
  `PENDING_MARKET_OPEN`) and implicitly exercised (bypassed by design, since BTCUSD trades weekends) for
  BTCUSD.
- **AlgoTrading-disabled fail-closed refusal**: proven against the real terminal (BTCUSD attempt 1).
- **Full project regression** (2714 passed, 2 skipped, 0 failed, ~4h14m) — run once, historically, before
  Phase 10's first DEMO attempt, per the CEO's own "before first DEMO execution" requirement. **Not
  re-run in full during this official-save session** (a scoped regression covering all Phase 1-10
  packages was run instead — §1 — full-suite re-run would take ~4h and was judged out of scope for a
  documentation/inventory task; recommend a fresh full run before authorizing anything beyond this save).

**Explicitly NOT validated**: the XAUUSD send path itself (only BTCUSD's identical code path has been
exercised — §6 of `AI_TRADER_PROJECT_STATE.md`); any continuous/unattended run; 5%-risk sizing (not even
implemented); any Research-Lab-edge-driven decision (none exist in code to validate — §5 below).

## 4. DOCUMENTED ONLY — described in a `.md` file, with no or partial code backing

- **5%-equity-risk dynamic sizing** — `RISK_SIZING_5PCT_XAUUSD_DESIGN.md` is a design document only. Zero
  lines of implementation code exist for it. Explicitly not to be treated as built.
- **Strategy Library validation evidence in the live path** — the `evidence` block (matched-null,
  global-FDR, walk-forward, holdout status) inside each of the 51 `knowledge/strategies/*.json` files is
  *loaded* by `edge_intelligence/contracts.py` but never *read* by any live verdict logic — present in
  data, inert in code. Full detail: `AI_TRADER_KNOWLEDGE_TRANSFER_AUDIT.md` §3.2, §6.
- **Three older packages' "no runtime code" README claims** (`scoring_engine/README.md`,
  `risk_manager/README.md`, `strategy_manager/README.md`) — documented as fact in those files, but
  contradicted by the packages' own substantial `.py` implementations. Reported, not corrected, per
  standing instruction. Full detail: `AI_TRADER_KNOWLEDGE_TRANSFER_AUDIT.md` §10.
- **"Research Lab: NO" assurance for the 9 live-wired Phase 2-10 packages** — this assurance exists in
  documentation for older batch packages (`execution_engine`, `risk_manager`, `scoring_engine`,
  `signal_engine`) but was never written down for the newer live packages themselves; true by code
  inspection today, but not documented at the architecture level for the packages where it actually
  matters most.

## 5. Edge-transfer spot-check — Alpha 1, Alpha 2, Red Team, Statistician, Validation Engine

Per explicit instruction for this task: do not assume transfer, only note found / not found / unclear /
requires the Knowledge Transfer Audit. This is a naming spot-check, not a re-audit — the Knowledge
Transfer Audit itself (§6 below) already did the exhaustive, code-verified version of this question for
every Research Lab edge/strategy by ID.

| Division named | Found in this repo? | Detail | Transferred into `ai_trader/` live code? |
|---|---|---|---|
| **Alpha 1 / Alpha 2** | UNCLEAR | No division literally named "Alpha 1" or "Alpha 2" exists in `ai_trader-research-main`. The closest match is the Alpha Discovery Candidate program (DC-0001–DC-0018), which lives only on unmerged branches (`alpha-automation-v1`, `alpha-discovery`) — not on the checked-out `ai-trader-implementation` branch. Whether "Alpha 1"/"Alpha 2" refers to two iterations of that program, or to something else entirely, could not be confirmed from this repo alone — worth clarifying directly rather than guessing. | NOT TRANSFERRED (moot — not even merged to this branch) |
| **Red Team** | FOUND | `red_team/` package (methodology, verdicts ledger, intake register) exists on branch `red-team-foundation`, not merged to `ai-trader-implementation`. 18 candidates reviewed, 🟢7/🟡11/🔴0. | NOT TRANSFERRED — zero `DC-00xx`/`red_team`/`CRITIQUE_BATTERY` references anywhere in `ai_trader/` (repo-wide grep, confirmed) |
| **Statistician** | NOT FOUND | Exhaustive search across every branch in this repo (`alpha-automation-v1`, `alpha-discovery`, `red-team-foundation`, `strategy-development`, `strategy-library`, `family-implementation-s21-s40`, `matched-null-validation`, `flow-c-foundation`, `research-main`, `master`) found no "Statistician" file, directory, or division. Likely belongs to a different project directory, out of this repo's scope. | N/A — does not exist here to transfer |
| **Validation Engine** | UNCLEAR, likely FOUND under a different name | No division literally named "Validation Engine" exists. The closest match is the **matched-null validation engine** (`docs/MATCHED_NULL_VALIDATION.md`) — itself validated (calibration/power/adversarial-robustness batteries pass) as an engine, but explicitly issues **no strategy verdict**: a 10-hypothesis pilot found only one candidate significant both research- and OOS-side, and under the frozen global-FDR threshold *"none of these would be significant."* | NOT TRANSFERRED — confined to the batch/research side; no live `ai_trader/` package imports or references it |

**All four rows above point back to the same underlying, already-established fact**: the Knowledge
Transfer Audit's exhaustive repo-wide search found zero code-level presence of any Research-Lab edge,
strategy-validation-status, or Red-Team-verdict identifier inside `ai_trader/`'s live packages — this
spot-check is consistent with that finding, not a new one. **Deep audit was not performed here per
instruction** (item 11 explicitly reserved that for the Knowledge Transfer Audit, which has already run).

## 6. NOT YET AUDITED

- **Decision Logic** — how `TradeProposal`/`ApprovedTradeIntent` construction, confidence grading, and
  risk sizing interact end-to-end for correctness of trading logic (as opposed to structural/type
  correctness, which the unit tests already cover) has not been independently audited. Planned as
  "Decision Logic Audit," next after Knowledge Transfer Audit per `AI_TRADER_DECISIONS.md` item 5 — **not
  started, not authorized**.
- **Risk** — the risk-control stack (`risk_manager` guards/limits/filters, `risk_manager_live`'s
  additional volume-step/margin checks, `portfolio_manager_live`'s exposure caps) has been unit-tested per
  component but not independently audited as a *system* for gaps or interaction effects. Planned as "Risk
  Audit" — **not started, not authorized**.
- **Demo Readiness** — whether the system as a whole (not just Phase 10's own send mechanics) is ready for
  sustained DEMO operation has not been formally audited beyond this document's own observations. Planned
  as "Demo Readiness Audit" — **not started, not authorized**.
- **Research Lab knowledge transfer** — **audit completed** 2026-07-25,
  `AI_TRADER_KNOWLEDGE_TRANSFER_AUDIT.md`, verdict **NOT READY** (zero edges transferred at code level, no
  live signal source exists at all).

## 7. NOT AUTHORIZED

Regardless of technical readiness, the following are explicitly not permitted right now, per direct CEO
instruction (full record: `AI_TRADER_DECISIONS.md`):

- Continuous / unattended DEMO execution.
- Any LIVE or CONTEST account trading (also structurally impossible, not just policy — §4 of
  `AI_TRADER_PROJECT_STATE.md`).
- Treating BTCUSD as an approved trading strategy or symbol (it was infrastructure-validation only).
- Implementing the 5%-equity-risk sizing design.
- Starting Alpha 1, Alpha 2, Red Team, Statistician, or Validation Engine work from this session.
- Starting a new Knowledge Transfer Audit, Decision Logic Audit, Risk Audit, or Demo Readiness Audit
  without explicit authorization for each.
