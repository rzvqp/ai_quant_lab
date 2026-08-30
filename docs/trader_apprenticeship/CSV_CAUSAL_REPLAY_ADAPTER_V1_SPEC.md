# CSV_CAUSAL_REPLAY_ADAPTER_V1 — SPEC

Replaces TradingView live replay as Q4's DATA SOURCE only. The causal abstraction — current bar
only, persistent pointer, decision-commit handshake, next-bar lock — is unchanged from
`causal_replay.js` (`tradingview-mcp`), this mandate's own named conceptual reference (read in full
before writing this implementation, not reconstructed from memory). Scientific methodology
(ONE-STEP-ONE-READ, NO FUTURE LEAKAGE, FREEZE BEFORE REVEAL, the P007/MGMT-004/NO_TRADE handshake
vocabulary) does not change.

## 1. Why this exists

`tradingview-mcp`'s replay pointer is entirely live TradingView Desktop browser state (no
server-side persistence at all — established during the earlier accelerator mandate). TradingView
MCP had become an operational blocker for continuing Q4. This adapter provides the same causal
guarantees from a static, already-verified CSV extract instead, with genuine durable persistence
(mandate section 7) — something the live-browser variant structurally could not offer.

## 2. Package layout (`ai_trader/csv_causal_replay/`)

```
identity.py       -- SourceIdentity, ADAPTER_VERSION, Q4_START_TS, MAX_Q4_BAR_INDEX, hash_file()
errors.py         -- fail-closed exception hierarchy (one class per named refusal, mandate section 8)
types.py          -- Bar, GapRecord/GapClassification, DurableState, PendingDecision,
                      REQUIRED_EVENT_FIELDS, RevealedBar, RunUntilGateResult
gap_classification.py -- classify_gap() (MAINTENANCE/WEEKEND/EXTENDED_PAUSE/UNEXPECTED)
sealed_reader.py  -- SealedReader: bounded, line-at-a-time streaming CSV reader (section 4)
persistence.py    -- DurablePointerStore: atomic JSON read/write (section 7)
engine.py         -- CSVCausalReplayEngine: step / commit_decision / run_until_gate / seeding
ema.py            -- causal_ema / sub_ema_streak (section 12, EMA-50 only, scope disclosed)
fixtures/
  materialize_sealed_fixture.py -- one-time, bounded builder for the dev/test fixture
  benchmark.py                  -- section 13 performance measurement
  data/Q4_SEALED_1_378.csv      -- the materialized fixture (bars 1-378 + 2000 warm-up)
  data/Q4_SEALED_1_378_MANIFEST.json
tests/            -- 50 tests, section 14
```

`Bar`/`GapRecord`/`GapClassification` are redeclared locally (not imported from
`ai_trader.live_signal_source.types`) — that package's own `__init__.py` unconditionally imports
`bar_feed` → `execution_engine` → `signal_engine` → `market_scanner.schema_validation` →
`fastjsonschema` (not installed in this environment, and none of it CSV-replay-related). Confirmed
by attempting the import first, not assumed. `gap_classification.classify_gap` is copied verbatim
from `live_signal_source.gap_classification` for the same reason — same CEO-specified MAINTENANCE
formula, same empirically-measured 72h WEEKEND/EXTENDED_PAUSE threshold, not reinterpreted.

## 3. The causal state machine (section 6)

```
DurableState.next_bar = N       -- only bar N can be revealed
engine.step()                   -- reveals bar N, sets pending_decision(bar_index=N), next_bar STAYS N
engine.commit_decision(bar_id=N.ts_open, decision_type, decision_record)
                                 -- validates, clears pending_decision, next_bar becomes N+1
```

`next_bar` is pinned to the currently-pending bar's own index while a decision is outstanding (not
advanced speculatively) — `DurableState.__post_init__` enforces `pending_decision.bar_index ==
next_bar` whenever a decision is pending, so a state file that violates this invariant is refused
(`RestartAmbiguityError`) rather than guessed at.

**Two modes**, both gated the same way `causal_replay.js` gates them:

- **ATOMIC** (`step`): one bar per call, always available.
- **HYBRID** (`run_until_gate`): up to `MAX_HEARTBEAT_BARS=8` bars per call, only the LAST bar left
  pending a commit — identical internal-loop shape to `causal_replay.js`'s own `_stepAndSnapshot`
  tight loop (only the FIRST bar's `expected_pointer_before` is checked). **New in this adapter,
  not in the JS version**: refused outright (`HybridModeLockedError`) whenever
  `DurableState.open_event_state_reference` is set — mandate section 9's requirement that AI Trader
  resume in ATOMIC mode only, since Q4-P007-003 is OPEN at the real bar-378 boundary. A
  `P007_RESOLUTION` commit clears the reference and unlocks HYBRID.

Event gates (mandate section 3) — same three mechanically-checkable categories as
`causal_replay.js`'s `EVENT_GATE_DEFS`, same honest limitation disclosed there ported here
unchanged: `STRUCTURAL_LEVEL_TOUCH`, `MATERIAL_VOLATILITY_TRANSITION`, `GAP_OR_INTEGRITY_ANOMALY`.
The other categories in the mandate's own taxonomy are not reimplemented — they remain the
reasoning layer's own judgment, covered only by the 8-bar heartbeat ceiling, exactly as the prior
design doc for the TradingView-backed version reasoned through for its own rejected filtering-runner
option.

## 4. What is genuinely new relative to `causal_replay.js` (not merely ported)

1. **Durable, persisted state** (`persistence.DurablePointerStore`, atomic `os.replace` write)
   instead of an in-memory flag — mandate section 7. A live TradingView tab has its own ground-truth
   pointer to fall back on; a CSV read does not, so the pending-commit handshake itself must survive
   a process restart.
2. **HYBRID locked behind `open_event_state_reference`** (mandate section 9), not present in the JS
   version.
3. **Sealed boundary is absolute** (`SealedBoundaryError`), never silently downgraded to an ordinary
   heartbeat-ceiling stop — mandate section 1's BAR_379+ = SEALED is treated as a different kind of
   limit than "ran out of routine bars to batch."
4. **Source identity pinning** (`SourceIdentity.fingerprint()`, checked on every `step()`) — a CSV
   file can be silently swapped or edited on disk in a way a live browser tab cannot; this adapter
   refuses (`SourceIdentityMismatchError`) rather than trust a file that no longer matches what
   durable state was last committed against.

## 5. Indicator causality (section 12)

The only indicator this package computes is a causal EMA-50 (`ema.py`) — a strict left-to-right
fold, `result[i]` depending only on `values[0..i]`, independently verified by
`tests/test_ema.py::test_changing_a_later_value_never_changes_an_earlier_ema`. H1/H4/session context
for AI Trader's own reasoning is expected to keep coming from the canonical Pine indicator exactly
as before — this adapter does not reimplement it (mandate section 15: no scope creep). See
`CSV_Q4_PARITY_1_378_V1.md` for the disclosed, measured gap between this EMA-50's own streak count
and the log's reported one.

## 6. What was deliberately left out (section 15)

No H1/H4/ATR aggregation, no new market-intelligence detector, no change to P007/MGMT-004
thresholds, no execution/broker code, no S5 or Strategy Catalog interaction. `AI Trader` was never
invoked to build or inspect this adapter (section 2).
