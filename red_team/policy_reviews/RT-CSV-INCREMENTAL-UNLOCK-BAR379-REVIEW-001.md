# RED TEAM — CSV INCREMENTAL UNLOCK (BAR-379 CHECKPOINT → AUTONOMOUS Q4 GATE)
### RT-CSV-INCREMENTAL-UNLOCK-BAR379-REVIEW-001 · Auditor: Red Team · 2026-08-30

Audit of the incremental CSV causal-unlock mechanism frozen at checkpoint `a87f42d` (branch
`ai-trader-implementation`), building on the accepted adapter `4d2b391` (RT verdict E103
PASS_WITH_NONBLOCKING_NOTES). State/code audit only. Bar 380 not exposed; Q4 not resumed; adapter/MT5/S5/
P007/MGMT-004 not modified.

---

## 0 — REQUIRED VERDICT

```
RED_TEAM_INCREMENTAL_UNLOCK_REVIEW_COMPLETE = YES
CHECKPOINT_COMMIT = a87f42d886a973cafe3e5bad2ee2646a415bdea2
CHECKPOINT_IDENTITY_VERIFIED = YES

INCREMENTAL_MATERIALIZER = PASS
ONE_BAR_UNLOCK_ENFORCED = FAIL
COMMIT_BEFORE_NEXT_BAR = PASS
POINTER_PERSISTENCE = PASS
CRASH_RECOVERY = PASS
RESTART_RESUME_EXACT = PASS

BAR_379_CHECKPOINT_PARITY = PASS
BAR_380_ACCESSED = NO

P007_H1_EMA_SEMANTIC = PASS
ATOMIC_LOCK_WHILE_P007_OPEN = PASS

SAFE_FOR_AUTONOMOUS_SEQUENTIAL_Q4 = NO

BLOCKING_FINDINGS = 1 (no fail-closed one-bar-unlock enforcement — §4/§9)
NONBLOCKING_FINDINGS = 1 (cosmetic durable-state symbol="UNKNOWN")

RED_TEAM_VERDICT = FAIL
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

**The bar-379 checkpoint itself is correct and safe for CEO-authorized per-step extension.** It FAILS the
**autonomous-continuation gate** this review exists to grant, on a single, narrow, well-defined blocker: there
is no mechanical guarantee that an unlock advances by exactly +1, so an autonomous AI Trader could bulk-unlock
future bars via `materialize_sealed_fixture --max-bar`. Minimal remediation in §2 finding 1.

## 1 — CHECKPOINT IDENTITY (§2) — verified

`a87f42d` is a descendant of `4d2b391` (HEAD of `ai-trader-implementation`), changing **exactly 5 files**:
`Q4_SEALED_1_379.csv` (+manifest), `materialize_sealed_fixture.py` (parameterization), `q4_durable_state.json`
(new), `AI_TRADER_Q4_M15_LOG.md` (+608 lines). **No MT5, runtime, engine, sealed_reader, ema, S5, P007, or
MGMT-004 change** (`git diff 4d2b391 a87f42d` on `engine.py`/`sealed_reader.py`/`ema.py`/`persistence.py` is
empty). **CHECKPOINT_IDENTITY_VERIFIED = YES** — only the intended bar-379 checkpoint / incremental-unlock
files.

## 2 — INCREMENTAL MATERIALIZER (§3) + ONE-BAR ENFORCEMENT (§4)

**INCREMENTAL_MATERIALIZER = PASS** (per-call boundedness). `materialize(source, *, max_q4_bar_index=378)`:
- writes to a **separately-named** `Q4_SEALED_1_{N}.csv` / manifest — **never overwrites** a lower-boundary
  fixture (each boundary's file remains as an audit trail); `Q4_SEALED_1_378.csv` verified **byte-unchanged**;
- reads the source through the **same `SealedReader`** the E103 review audited — `SealedBoundaryError` fires at
  Q4 bar `N+1` **before its OHLCV is parsed**, so bar `N+1`'s market data is never materialized;
- fail-closes if the source is exhausted before `N` (`reached_boundary`) or if it collects `≠ N` Q4 rows — so a
  fixture always contains a **contiguous 1..N** (no skip, no accidental multi-bar jump *inside* a fixture);
- streaming reader, no `read_csv()`/DataFrame; `origin_source_total_row_count` still deliberately unrecorded.

**ONE_BAR_UNLOCK_ENFORCED = FAIL** (the decisive finding). The CLI accepts an **arbitrary** `--max-bar N`
(default 378). Nothing reads the current durable-state boundary (379) and refuses `N > current + 1`. So
`materialize --max-bar 5900` would, in one call, parse Q4 bars 380..5900 and **write their OHLCV into a
plaintext fixture file** that is then directly readable — a bulk future exposure that the engine's per-bar
handshake does **not** prevent (the handshake gates *reveal*, not *materialization*).

- **TECHNICAL_CAPABILITY** = arbitrary future `N` (bulk-unlock possible).
- **AUTHORIZED_RUNTIME_PATH** (fail-closed, +1 only) = **does not exist** in this checkpoint.

**Minimal remediation (BLOCKING for autonomy):** add a fail-closed one-bar-extension guard — the extension
mechanism must read the current durable-state `sealed_through_bar_index` and **refuse** `max_q4_bar_index >
current_boundary + 1`, and ideally gate the extension on the prior bar's committed durable state (extend only
after `pending_decision == null` and `next_bar == current_boundary + 1`). Until then, fixture extension must
remain a **per-step CEO-authorized** action, not an autonomous one.

## 3 — COMMIT-BEFORE-NEXT-BAR + RESTART (§5/§6) — PASS (engine unchanged from E103)

`engine.py`/`persistence.py` are byte-unchanged since `4d2b391`, so the E103-verified guarantees hold and were
re-confirmed against the bar-379 state:
- **COMMIT_BEFORE_NEXT_BAR = PASS**: `step()` refuses while a decision is pending; `commit_decision` validates
  bar_id/type/fields; missing/wrong/duplicate/out-of-order commits refused (50/50 tests, incl. the adversarial
  suite, reproduced).
- **POINTER_PERSISTENCE = PASS**: `q4_durable_state.json` persists `last_committed_bar`/`next_bar`/
  `pending_decision`/`open_event_state_reference`/`source_identity` (with the fixture content-hash).
- **CRASH_RECOVERY = PASS**; **RESTART_RESUME_EXACT = PASS**: the durable JSON alone yields
  `LAST_COMMITTED_BAR = 379` (ts 1602037800), `NEXT_BAR = 380`, `PENDING_DECISION = null`,
  `Q4-P007-003:OPEN`, and `sealed_through=379` — recoverable **without** TradingView/UI/session memory; the
  `source_identity.content_hash 651b944f…` fail-closes a fixture-swap.

## 4 — BAR-379 CHECKPOINT PARITY (§7) — PASS

| check | result |
|---|---|
| `Q4_SEALED_1_378.csv` unchanged | **PASS** (empty diff `4d2b391..a87f42d`) |
| `Q4_SEALED_1_379.csv` max Q4 bar = 379 | **PASS** (`q4_bar_count=379`, `sealed_through=379`, `total_row_count=2379` = 2000 warm-up + 379; `max_q4_bar_index_read=379`) |
| bar 380 absent | **PASS** (not in fixture; never read/parsed) |
| durable state LAST_COMMITTED=379 / NEXT=380 / PENDING=null | **PASS** |
| Q4-P007-003 OPEN | **PASS** (`open_event_state_reference = "Q4-P007-003:OPEN"`) |
| bar-379 close/ts vs log | **PASS** (bar 379 `ts_open=1602037800`, `close=1880.496`; log bar-379 entry consistent) |
| **BAR_380_ACCESSED** | **NO** (no semantic exposure; `max_q4_bar_index_read=379`) |

## 5 — P007 / ATOMIC CONTRACT (§8) — PASS, and my E103 EMA correction was ADOPTED

**P007_H1_EMA_SEMANTIC = PASS.** The Q4 log's bar-379 bridge note adopts the E103 correction **verbatim**:
> *"Red Team's required resume note: 'EMA50' in this log has always meant the H1 EMA50 (never M15) … From this
> bar onward, EMA50 continues to mean the causal H1 EMA50, recomputed directly from the [source] … H1 EMA50 @
> bar 378 = 1901.160, streak = 39."*

This matches my E103 independent computation exactly (H1 EMA-50 = 1901.160, streak 39). The three counters —
historical TradingView-era 38 @ 378, canonical causal H1 recomputation 39 @ 378, prospective 40 @ 379 — are
preserved and the counter is correctly treated as **descriptive-only, non-decision-critical**. The M15 `ema.py`
helper remains test-only and is **not** used for P007. The scientific-continuity nonblocking note from E103 is
thereby **closed**.

**ATOMIC_LOCK_WHILE_P007_OPEN = PASS** (engine unchanged): `run_until_gate` (HYBRID) is mechanically
unreachable while `Q4-P007-003` is OPEN; only `step()` (ATOMIC) advances, until a `P007_RESOLUTION` commit
clears the lock. Verified in E103, unchanged here.

## 6 — AUTONOMOUS-Q4 SAFETY (§9) — NO

The engine's state machine preserves the no-lookahead invariant **within a fixture** (per-bar reveal +
commit-before-next-bar + ATOMIC-lock). It does **not** preserve it across the **fixture-extension** boundary:
extension is performed by a materializer CLI that accepts an arbitrary `--max-bar` and writes future OHLCV to a
readable file with no +1 constraint (§2 finding 1). Therefore an autonomous loop that extends fixtures could
bulk-unlock. **SAFE_FOR_AUTONOMOUS_SEQUENTIAL_Q4 = NO** until the fail-closed one-bar-extension guard is added.
Once added, the architecture (ATOMIC per bar, HYBRID only under the approved contract, commit-gated advance,
durable restart) is otherwise well-suited to autonomous sequential continuation.

## 7 — TESTS (§10)

**50/50 reproduced** (`test_sealed_reader`, `test_engine`, `test_ema`, `test_adversarial`) — no bar-380 exposure
(fixtures ≤ 379). The adversarial suite already covers missing/duplicate/out-of-order commit, pointer/hash
mismatch, crash/restart, and future-row inaccessibility. **Gap in coverage (feeds the §2 blocker):** there is no
test asserting that an extension **cannot jump more than +1** or that a bulk `--max-bar` is refused in the
autonomous path — because that guard does not yet exist. The remediation must ship with such a test.

## 8 — FINDINGS

**BLOCKING (1): No fail-closed one-bar-unlock enforcement (§4/§9).** The materializer accepts an arbitrary
`--max-bar`, enabling bulk materialization of future OHLCV into a readable fixture; there is no autonomous
runtime path constraining an unlock to `current_boundary + 1`. This blocks `SAFE_FOR_AUTONOMOUS_SEQUENTIAL_Q4`.
Remediation in §2 finding 1 (read the durable boundary, refuse `> current + 1`, gate on the prior commit, ship a
test). It does **not** affect the correctness or safety of the already-frozen bar-379 checkpoint.

**NONBLOCKING (1):** `q4_durable_state.json` `source_identity.symbol = "UNKNOWN"` (the manifest correctly carries
`OANDA:XAUUSD`) — cosmetic, non-scientific; recommend populating it for provenance completeness.

## 9 — CONCLUSION

The bar-379 checkpoint is **verified correct**: identity clean, 378 fixture byte-unchanged, 379 fixture bounded
to bar 379 with bar 380 absent and unaccessed, durable state exact and restart-recoverable, the engine's
commit-handshake and ATOMIC-lock intact, and — notably — the E103 EMA-50 timeframe correction (H1, not M15) has
been **adopted and documented** in the Q4 log, with the streak counter correctly descriptive-only. The single
blocker is the missing fail-closed **one-bar-unlock enforcement**: as delivered, extension is safe only under
per-step CEO authorization, not autonomously. **`SAFE_FOR_AUTONOMOUS_SEQUENTIAL_Q4 = NO`** until that guard
ships.

```
RED_TEAM_VERDICT = FAIL (autonomous-Q4 gate; single blocking finding — checkpoint state itself is correct)
SAFE_FOR_AUTONOMOUS_SEQUENTIAL_Q4 = NO
BAR_380_ACCESSED = NO
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

Bar 380 not exposed, Q4 not resumed, adapter/MT5/S5/P007/MGMT-004 not modified. Control returned to CEO.

---

*Red Team · incremental-unlock / autonomous-Q4 gate audit · checkpoint identity verified · 378 fixture
byte-unchanged · bar 380 not accessed · E103 EMA correction confirmed adopted · single blocker = no one-bar
enforcement · 50/50 tests reproduced · LEDGER E104 (prev E103).*
