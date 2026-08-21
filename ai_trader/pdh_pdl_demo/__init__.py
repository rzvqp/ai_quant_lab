"""Status: LEGACY_NON_AUTHORITY (CEO decision, AI Trader New Brain Architecture mandate
AI-TRADER-NEW-BRAIN-ARCHITECTURE-IMPLEMENTATION-001).

CAND-0001 (PDH-PDL v2.0 DEMO) -- an independent recognition -> risk -> order path built and CEO-
authorized live 2026-08-03, predating the canonical N1-N6/`ve_brain`/`new_brain_live` chain and the new
generic Strategy Catalog/Router/EV/Risk architecture built under this mandate.

**Preserved, not deleted** -- for audit, historical reproducibility, and rollback/migration reference.
**No production decision authority**: does not feed, override, OR-gate, veto, supplement, or bypass
N1-N6, MarketState, the Strategy Catalog, the Strategy Router, the EV/Decision Engine, the Risk Engine,
or the Execution Orchestrator, and never will while this status holds.

**Real order-submission capability is structurally quarantined**, not merely dormant: the only path
from this package to a real MT5 DEMO order is `ai_trader.mt5_demo_execution.gating.
send_after_dry_run_gate`, whose `LEGACY_TRADING_AUTHORITY_QUARANTINED` flag unconditionally blocks the
order-submitting leg regardless of any caller-supplied parameter -- proven by
`ai_trader/mt5_demo_execution/tests/test_legacy_quarantine_ast_guard.py` (source-level: no other direct
MT5 order call exists anywhere in this package -- also enforced by this package's own pre-existing
`tests/test_import_independence.py`) and `test_gating.py` (behavioral: the flag holds even on an
otherwise-fully-approved candidate). `BROKER_ORDER_SUBMISSION` (the separate, unrelated `new_brain_*`
gate) was already, independently, DISABLED and remains so.

**No automatic startup**: confirmed (2026-08-21, read-only `Get-ScheduledTask` audit) that no Windows
Scheduled Task registers or auto-restarts this package's `entrypoint.py` -- there is currently nothing
to disable. If a Scheduled Task or other auto-launch mechanism for this package is ever (re)created, it
must remain disabled while this status holds.

CAND-0001 has no automatic grandfathering into the new Strategy Catalog. It may enter the new
architecture only through the future validated-strategy onboarding process, after Alpha -> Statistician
-> Red Team -> CEO ratification of a genuinely validated strategy -- never by virtue of this package's
prior live history."""
