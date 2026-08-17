# LIVE_SHADOW Activation Report

**Status: `LIVE_SHADOW_ACTIVE` / `MANDATE_2_PASS` / `BROKER_ORDER_SUBMISSION_DISABLED`**

## Scope reminder

LIVE_SHADOW authorized. LIVE ORDER not authorized. Broker gate BLOCKED throughout. Alpha remains
`ALPHA_BLOCKED_CANONICAL_N1_HANDOFF`. `CAND-T05` remains frozen. Nothing in this activation touched
either.

## Commits

| Item | Commit |
|---|---|
| `new_brain_live` package + `fail_safe` extension | `eb97a80` |
| `LIVE_SHADOW_AUTHORIZATION_RECORD.md` | `04c339d` |
| `live_shadow_preflight.py` + `LIVE_SHADOW_PREFLIGHT_RESULT.json` | `0050dea` |
| Prior tower-chain authorization basis | `6e5a333` (code) / `bf9243d` (report) |

All pushed to `trader`/`ai-trader-implementation`; local HEAD verified equal to remote HEAD after each push.

## Configuration fingerprint

Static identity = the pin set in `LIVE_SHADOW_AUTHORIZATION_RECORD.md`: ve_brain `0.1.3`/`37b95393df85dc2b`,
ve_tower `0.5.2`/`b0cf2ea`/`60bf71b`/`a80d8a085dfc26e3042beb512a10aa5c5c1ccb62`, cost model
`v1`/`RATIFIED`/`b7bb9a9aed17a1c8`. Per-event `configuration_fingerprint` is computed fresh each event as
`_fp(trace_id, ve_brain.VE_BRAIN_VERSION)` (`bridge.py:473`) — e.g. the first processed event carried
`"701ae59f1a896e8f"`.

## Authorization record

`LIVE_SHADOW_AUTHORIZATION_RECORD.md` @ `04c339d`, `authorized_at_utc: 2026-08-17T18:41:30Z`.

## Timestamps

| Event | UTC |
|---|---|
| Authorization record committed | 2026-08-17T18:41:30Z |
| Preflight verdict GO (second/corrected run) | ~2026-08-17T18:45Z (see `LIVE_SHADOW_PREFLIGHT_RESULT.json`) |
| Authority switch `LEGACY` → `NEW_BRAIN` | ~2026-08-17T18:46Z |
| Process launch (confirmed via process creation time, converted from local `GTB Standard Time` UTC+3) | 2026-08-17T18:47:09Z |
| This report | 2026-08-17T18:50:21Z |

## Process identity

| Field | Value |
|---|---|
| Launch command | `venv\Scripts\python.exe -m ai_trader.new_brain_live.entrypoint` |
| Shell wrapper PID | `26880` (Git-Bash job-control parent; not the interpreter) |
| Real interpreter PID | `6232` (child of `26880`; printed the startup line; parent of the tower-worker process) |
| Tower worker process | PID `28632` (`ve_tower_venv` stub) → PID `14224` (real interpreter), spawned by `TowerWorkerLauncher` from within PID `6232` |
| stdout | `new_brain_live_state/stdout.log`: `new_brain_live: LIVE_SHADOW starting -- symbol=XAUUSD tower_version=0.5.2 db=...\new_brain_live_state\xauusd_m15.db` |
| stderr | empty |

Two PIDs (`26880`/`6232`) sharing one command line is a known artifact of how Git-Bash's `nohup ... &`
backgrounding launches a Windows process on this machine (parent job-control process + the actual
interpreter as its child) — confirmed benign because exactly one `"LIVE_SHADOW starting"` line was
printed and the tower-worker subprocess tree hangs off `6232` alone, i.e. there is exactly one live
`NewBrainLiveLoop` instance, not two competing ones.

## Authority

| | Before | After |
|---|---|---|
| `current_authority(state_store)` | `LEGACY` | `NEW_BRAIN` |

Verified via a fresh `SqliteStateStore` connection re-reading the persisted value after `set_authority`
returned (not just the same in-process connection).

## Legacy status

`pdh_pdl_demo` / `multi_policy_live` / `market_intelligence`: **zero instances currently running** on
this machine (confirmed via `Win32_Process` inventory immediately before and after the switch — only
one unrelated process, `alpha_service.py` PID `13616` from a different repo, was present). Demotion to
`LEGACY_SHADOW_TELEMETRY` is therefore moot for this activation: there is nothing legacy to demote. If
any of those three processes is started later while this authority record holds, `authority_check`
(each reads `current_authority` fresh) will correctly treat it as `LEGACY_SHADOW_TELEMETRY` per its own
existing wiring — this was not re-tested against a live legacy process today because none exists.

## Worker health

Real HMAC handshake succeeded during preflight (`session_id` present, PID `28632` reported), zero pin
mismatches against all 15 pinned fields. The activation's own worker instance (spawned by PID `6232`)
is a separate, later handshake — its health is evidenced by the fact that 36 real events were
successfully evaluated (an `UNCERTAIN_REGIME` Router verdict on the sampled event below did not require
a tower-chain call for that particular bar, but `chart_get_state`-equivalent connectivity through N1 was
exercised and stdout shows no handshake failure `SystemExit`).

## First event trace (real, from the persisted telemetry log — not fabricated)

```json
{
  "event_identity": {
    "trace_id": "d03b796b16389bfe",
    "market_event_id": "XAUUSD:M15:1786985040",
    "market_timestamp": 1786985040,
    "brain_version": "0.1.3",
    "catalog_hash": "37b95393df85dc2b",
    "configuration_fingerprint": "701ae59f1a896e8f"
  },
  "strategy_id": "trend_pullback",
  "node_traces": [
    {"node_name": "N1", "output": "34d3ed98a5e335d0", "reason_codes": []},
    {"node_name": "Router", "output": "03aa6eb593ab6b93", "reason_codes": ["UNCERTAIN_REGIME"]}
  ]
}
```

## Activation summary (36 real events processed on first poll -- catch-up on already-closed bars)

- **First M15-closed event**: `XAUUSD:M15:1786985040` (`trend_pullback`), NO_TRADE, `UNCERTAIN_REGIME` at
  Router.
- **First real NO_TRADE**: same event, immediately.
- **First `SHADOW_TRADE_CANDIDATE`**: none yet -- all 36 events resolved `NO_TRADE`/`NO_DECISION`. This
  matches the documented, expected behavior: `load_probability_inputs` returns `None` in production (no
  ratified per-regime outcome-count table exists), so `decision` stays `None` for the overwhelming
  majority of events. Per the CEO's own words, "aproape toate evenimentele pot produce NO_TRADE. Acesta
  este comportamentul corect."
- **Unavailability/errors**: none. Zero exceptions, empty stderr.
- **Category breakdown**: `LIVE_SHADOW_NO_TRADE=36`, `LIVE_SHADOW_EVENT=0`, `LIVE_SHADOW_CANDIDATE=0`,
  `LIVE_SHADOW_BLOCKED_AT_BROKER=0`.

## Broker gate state

`BrokerOrderSubmissionGate()` default (`enabled=False`) throughout. `order_send` not imported by
`ai_trader/new_brain_live/` (AST-guard-proven, 3 tests). Zero candidates reached the gate this cycle
(none were eligible), so `LIVE_SHADOW_BLOCKED_AT_BROKER` has not yet had an occurrence to demonstrate --
that will be verified live the first time a `TRADE`/`SHADOW_TRADE_CANDIDATE` decision actually occurs,
consistent with the CEO's own instruction not to fabricate one.

## Orders / positions / balance / equity, before vs. after

| | Before (preflight) | After (post-activation) |
|---|---|---|
| Active orders (XAUUSD) | 0 | 0 |
| Open positions (XAUUSD) | 0 | 0 |
| Balance | 1800.34 PLN | 1800.34 PLN |
| Equity | 1800.34 PLN | 1800.34 PLN |

Zero change, as required.

## Targeted tests run before activation

`ai_trader/new_brain_live/` (23 tests: 7 deps, 5 journal, 3 AST guard, 8 entrypoint) +
`ai_trader/new_brain_bridge/tests/test_fail_safe.py` (3 tests) = **26/26 passed**.
`mypy --strict ai_trader/new_brain_live/`: clean, 10 source files.
No decision-logic code was modified by this directive (pure orchestration), so the ~6-hour full
`ai_trader/` regression from RT-TOWER-0010 was not repeated, per the CEO's own section 9 instruction.

## Rollback command

```bash
# find the PID (the child interpreter, e.g. 6232 above)
taskkill //PID 6232 //T
```
or send `SIGTERM`/`SIGINT` to the process group if launched from a POSIX-capable shell -- the installed
signal handler finishes the in-flight tick and closes the state store cleanly. No broker-side action is
ever required (zero orders/positions were ever created). Journal/telemetry data in
`new_brain_live_state/xauusd_m15.db` is preserved regardless.

---
Prepared by AI Trader division, `ai_quant_lab-research-main`, branch `ai-trader-implementation`.
