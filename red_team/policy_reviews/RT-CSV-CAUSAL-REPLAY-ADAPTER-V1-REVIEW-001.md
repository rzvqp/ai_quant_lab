# RED TEAM — CSV CAUSAL REPLAY ADAPTER V1 · SCIENTIFIC CONTINUITY / NO-LOOKAHEAD AUDIT
### RT-CSV-CAUSAL-REPLAY-ADAPTER-V1-REVIEW-001 · Auditor: Red Team · 2026-08-30

Independent adversarial review of `CSV_CAUSAL_REPLAY_ADAPTER_V1` (commit `4d2b391`, repo
`ai_quant_lab-research-main`, branch `ai-trader-implementation`). VE's `VE_HANDOFF_PASS` not trusted
automatically. Bar 379 not semantically exposed; sealed boundary not extended; Q4 not resumed; adapter not
modified; S5/MGMT-004/Q4-P007-003 untouched.

---

## 0 — REQUIRED VERDICT

```
RED_TEAM_CSV_REPLAY_REVIEW_COMPLETE = YES
ARTIFACT_COMMIT = 4d2b39115be785cc66aa1fd82994f3ad7ba84ac4
ARTIFACT_IDENTITY_VERIFIED = YES
SOURCE_IDENTITY_VERIFIED = YES

BAR_379_PHYSICALLY_READ = YES (full-file SHA-256 during materialization + one boundary-triggering line read — provenance only)
BAR_379_PARSED = NO (OHLCV market data never parsed; only bar 379's timestamp field, to enforce the boundary)
BAR_379_ENGINE_ACCESS = NO
BAR_379_AI_EXPOSED = NO

FUTURE_ROW_INACCESSIBLE = PASS

BAR_SEQUENCE_PARITY = PASS
TIMESTAMP_PARITY = PASS
OHLC_PARITY = PASS
LEDGER_STATE_PARITY = PASS  (surfaced state; the EMA-50 streak is a non-surfaced test helper — see §6)

EMA50_VALUE_PARITY = FAIL
EMA50_STATE_PARITY = FAIL
P007_COUNTER_PARITY = FAIL
EMA_DIVERGENCE_SCIENTIFIC_IMPACT = NONBLOCKING (with a REQUIRED resume note — §6/§7)

POINTER_PERSISTENCE = PASS
DECISION_HANDSHAKE = PASS
CRASH_RECOVERY = PASS
FAIL_CLOSED = PASS

ATOMIC_MODE = PASS
HYBRID_MODE = PASS
P007_REQUIRES_ATOMIC_AT_RESUME = YES

TESTS_REPRODUCED = 50/50 PASS
OUT_OF_SCOPE_CHANGE = YES
OUT_OF_SCOPE_SCIENTIFIC_IMPACT = NONE

BLOCKING_FINDINGS = NONE
NONBLOCKING_FINDINGS = 3 (see §10)

RED_TEAM_VERDICT = PASS_WITH_NONBLOCKING_NOTES

SAFE_TO_EXTEND_SEALED_BOUNDARY_TO_BAR_379 = YES (adapter mechanically sound; conditional on the §6 EMA note being honored for P007 reasoning)
SAFE_FOR_NEW_AI_TRADER_SESSION = YES (conditional on the §6 EMA note: use the causal H1 EMA-50 for Q4-P007-003, not the adapter's M15 helper)

NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

## 1 — ARTIFACT + SOURCE IDENTITY (§2/§3)

`4d2b391` is the HEAD of `ai-trader-implementation` — the CSV adapter package (`ai_trader/csv_causal_replay/`,
24 files, 4847 insertions). **ARTIFACT_IDENTITY_VERIFIED = YES.** Source: `origin_source_content_hash =
57f4ed95…` (the canonical 2011-2026 OANDA_XAUUSD_M15 source — the same hash verified across the S5/F441/CRS-1
work as the full-history file that contains Q4 2020, not a post-2022 subset). Bar-378 mapping verified
independently from the sealed fixture: Q4 bar 1 `ts_open=1601510400` (2020-10-01T00:00Z), bar 378
`ts_open=1602036900`, close `1880.434`, vol `523` — matching `AI_TRADER_Q4_M15_LOG.md` verbatim.
**SOURCE_IDENTITY_VERIFIED = YES** (established without an additional full-file hash by RT, to avoid an
unnecessary physical read past the boundary).

## 2 — BAR-379 ACCESS (§4) — the physical/semantic split, precisely

The `SealedReader` reads the source **one physical CSV line at a time** (`csv.reader`; a line never `next()`'d
is never read off disk) and enforces the boundary **on the timestamp field alone, before any OHLCV field is
parsed** — for the row that would be Q4 bar 379 it raises `SealedBoundaryError` *before* `float()`-ing its
OHLCV, so bar 379's price/volume values are never sliced out, never assigned, never captured in an exception.
It deliberately rejects the `read_csv().head(N)` anti-pattern (which would parse the whole file into memory
first).

| category | bar 379 | evidence |
|---|---|---|
| A. PHYSICAL_FILE_READ | **YES** | `materialize_sealed_fixture` calls `hash_file(source_path)` which streams the **entire** multi-year file's bytes into a SHA-256 digest (that is how `origin_source_content_hash 57f4ed95` is computed); and the SealedReader physically reads bar 379's *line* to parse its timestamp before the boundary error |
| B. ROW_PARSE (OHLCV) | **NO** | boundary raised before `_parse_ohlcv`; only the timestamp `int()` of bar 379 is parsed, to detect it |
| C. DATAFRAME/MEMORY | **NO** | no pandas; streaming reader only |
| D. ENGINE_ACCESS | **NO** | the engine reads only the sealed fixture `Q4_SEALED_1_378.csv` (2378 rows = 2000 warm-up + 378 Q4; bar 379 is not in it) |
| E. AI/HUMAN EXPOSURE | **NO** | bar 379's OHLCV entered a one-way hash digest + a boundary check only; never surfaced to any reasoning |

The full-file SHA-256 is a **provenance** operation (a one-way digest), reported separately from semantic
exposure exactly as §4 requires. VE's manifest even declines to record the source's total row count
("deliberately not counted… doing so would require reading past the sealed boundary"). **No semantic exposure
of bar 379 occurred; the physical hash read is disclosed and acceptable.** `MAX_Q4_BAR_READ_DURING_DEVELOPMENT
= 378` is mechanically ratcheted by the reader itself (`max_q4_bar_index_read`), not merely asserted.

## 3 — SEALED READER (§5) — FUTURE_ROW_INACCESSIBLE = PASS

Attacked via iterator, buffering/read-ahead (line-at-a-time, none), dataframe (not used), exceptions (raised
before OHLCV parse — the exception object cannot capture 379's price), metadata (total-row-count deliberately
unrecorded), source-length checks (deliberately not done), restart/pointer. Bar 379's OHLCV market data is
**physically unreachable** through this reader; only its timestamp is read to stop. **PASS.**

## 4 — LEDGER PARITY THROUGH BAR 378 (§8)

| check | result |
|---|---|
| bar sequence 1-378, in order, no index gaps | **PASS** |
| timestamps (bar 1 = 1601510400, bar 378 = 1602036900) | **PASS** |
| OHLC (bars 375-378 closes 1875.888/1879.648/1879.44/1880.434; bar 378 vol 523) match the log verbatim | **PASS** |
| 4 known gaps GAP-151/152/153/154 at Q4 bars 85/177/269/361, MAINTENANCE/WEEKEND classifications | **PASS** |
| Q4-P007-003 OPEN at bar 378; trade count 0; MGMT-004 trigger count 0 | **PASS** |
| bar-378 pointer state (LAST_CONSUMED=378 / NEXT_UNSEEN=379) | **PASS** |

The adapter's **surfaced** state (what `RevealedBar` carries: OHLCV + gap + index) has full parity through 378.

## 5 — CAUSAL STATE MACHINE (§9/§10)

- **POINTER_PERSISTENCE = PASS**: `DurableState` persists `last_committed_bar`/`next_bar`/`pending_decision`;
  `seed_from_known_state` re-seeds at bar 378 without revealing it; `expected_pointer_before` cross-checks.
- **DECISION_HANDSHAKE = PASS**: `step`/`run_until_gate` refuse while a decision is pending; `commit_decision`
  validates bar_id + type + fields; wrong/missing/duplicate/out-of-order commits are refused.
- **CRASH_RECOVERY = PASS**; **FAIL_CLOSED = PASS** (source-hash mismatch, timestamp disorder,
  `SealedBoundaryError` uncaught past 378, pointer mismatch — all throw).
- **ATOMIC = PASS; HYBRID = PASS; P007_REQUIRES_ATOMIC_AT_RESUME = YES** — the engine **mechanically blocks
  HYBRID (`run_until_gate`) while Q4-P007-003 is OPEN**; only `step()` (ATOMIC) is reachable until a
  `P007_RESOLUTION` commit clears the lock (engine `run_until_gate` guard + `commit_decision` line 229). This
  directly satisfies §10's requirement.
- **50/50 tests reproduced** independently (`test_sealed_reader`, `test_engine`, `test_ema`, `test_adversarial`);
  substantive, not trivial (the sealed-reader boundary proof runs against the real source; adversarial suite
  drives crash/duplicate/out-of-order/hash-mismatch).

## 6 — EMA-50 PARITY (§6) — VE's ROOT CAUSE IS WRONG; corrected here

VE reports the log's "38 consecutive bars below EMA50" (bar 378) vs the adapter's **44**, and attributes it to
**warm-up-window sensitivity**. **Independently disproven.** The decisive fact VE missed: the Q4 log's EMA50 is
the **H1 EMA-50**, stated verbatim throughout (`"3-bar dip below H1 EMA50"` bar 27; `"first close below H1
EMA50"` bar 176; `"oscillating around H1 EMA50 (~1899.8)"` bar ~250). The adapter's `ema.py` computes an **M15
EMA-50** (period 50 on M15 closes). **These are different indicators.** Reproduced directly on the sealed
fixture:

```
M15 EMA-50 @ bar 378 = 1890.390 → streak 44   (reproduces VE's 44 exactly)
H1  EMA-50 @ bar 378 = 1901.160 → streak 39   (matches the log's 38 to within one bar — the residual IS warm-up)
```

**ROOT_CAUSE_OF_38_VS_44 = TIMEFRAME MISMATCH** (log = H1 EMA-50 → ~38-39; adapter's helper = M15 EMA-50 → 44).
Warm-up explains only the residual 39-vs-38 (one bar) once the correct timeframe is used, **not** the 6-bar
44-vs-38 gap. The two EMAs differ by ~11 points (1890.39 vs 1901.16), so the reclaim level for the OPEN
Q4-P007-003 is materially different between them.

`EMA50_VALUE_PARITY = FAIL`, `EMA50_STATE_PARITY = FAIL`, `P007_COUNTER_PARITY = FAIL` — the `ema.py` helper is
the wrong-timeframe indicator.

**Why this is NONBLOCKING (§7), not a data defect.** `ema.py` is imported **only by itself and `test_ema.py`**
— it is a Parity-Test-B helper and is **never surfaced by the engine**: `RevealedBar` carries only OHLCV + gap
+ index ("never anything about the bar after it"), no EMA field. So the wrong M15 EMA is **not fed to the AI
Trader's reasoning**, and the adapter's actual data output (OHLCV) is correct — from which the **correct H1
EMA-50 is recomputable** (I did: streak 39 ≈ log's 38). The EMA formula itself is the standard causal one
(SMA seed, α=2/51) and its causality is sound (`test_ema` proves later values never change earlier EMAs).

**REQUIRED resume note (minimal remediation, per §7 "reproduce the original causal semantics over redefining
P007"):** at resume, Q4-P007-003's reclaim must be judged against the **causal H1 EMA-50** (aggregate the
revealed M15 bars to H1 and apply the same causal EMA-50) — **not** the adapter's `ema.py` M15 helper. VE's
parity doc's root-cause line ("warm-up sensitivity") should be corrected to "H1-vs-M15 timeframe mismatch." No
change to the adapter's data path is needed; this is a documentation + resume-protocol correction.

`EMA_DIVERGENCE_SCIENTIFIC_IMPACT = NONBLOCKING` — because the wrong EMA is not surfaced and the correct H1
EMA-50 is recoverable from the correct OHLCV; but the correction is mandatory before Q4-P007-003 is reasoned.

## 7 — OUT-OF-SCOPE (§13)

`MEMORY.md` compaction and `xauusd-monday-plan.md` deletion (per VE's own report) are **not** in the audited
commit `4d2b391` (whose 24 files are all `csv_causal_replay/` + its docs) and not in the current tree/recent
log. **OUT_OF_SCOPE_CHANGE = YES; OUT_OF_SCOPE_SCIENTIFIC_IMPACT = NONE** — neither touches the CSV adapter,
the Q4 durable record, S5, MGMT-004, or Q4-P007-003. Not restored or modified here (§13).

## 8 — PERFORMANCE (§12)

Not audited for speed. No performance construct compromises causal isolation: the streaming reader is the
performance mechanism *and* the safety mechanism (bounded read); the engine's `run_until_gate` is capped and
gated. Honestly represented.

## 9 — TRADINGVIEW (§14)

No TradingView MCP used or required (its tools are disconnected). The intended Q4 path is CSV causal replay if
this adapter passes; no TradingView infrastructure work reopened.

## 10 — FINDINGS

**BLOCKING: NONE.** No lookahead, no semantic exposure of bar 379, no unsafe pointer advance, no fail-open, no
retrospective classification. The engine's data output has full parity through bar 378 and mechanically
enforces ATOMIC-only while P007-003 is open.

**NONBLOCKING (3):**
1. **EMA-50 timeframe mismatch + incorrect VE diagnosis (§6).** The 38-vs-44 is an **H1-vs-M15 timeframe
   mismatch** (proven: log H1 EMA-50 → 39≈38; adapter M15 EMA-50 → 44), **not** the warm-up sensitivity VE
   claimed. Nonblocking because `ema.py` is a test-only helper never surfaced by the engine, and the correct
   OHLCV allows the causal H1 EMA-50 to be recomputed. **REQUIRED before Q4-P007-003 is reasoned at resume:**
   use the causal H1 EMA-50, not the M15 helper; correct the parity doc's root-cause.
2. **Bar-379 physical read via full-file SHA-256 (§4).** `hash_file(origin_source)` at materialization
   physically streamed the whole multi-year file (incl. 379+) into a one-way digest; the reader also physically
   read bar 379's line to parse its timestamp before stopping. **No semantic parse/exposure** of bar 379's
   OHLCV. Disclosed (manifest declines to count total rows). Provenance operation, acceptable.
3. **Out-of-scope MEMORY.md / xauusd-monday-plan.md changes (§13)** — not in the audited commit; no scientific
   impact; not restored.

## 11 — CONCLUSION

The CSV adapter is a **causally sound, no-lookahead data source**: the sealed reader makes bar 379's market
data physically unreachable, bar-379 access is limited to a disclosed provenance hash + a timestamp-only
boundary read, the state machine is fail-closed with a persistent pointer and a decision handshake, HYBRID is
mechanically blocked while Q4-P007-003 is OPEN, and OHLC/timestamp/gap/ledger parity through bar 378 is exact.
The one material correction to VE's handoff is scientific, not causal: **the 38-vs-44 EMA discrepancy is a
timeframe mismatch (H1 vs M15), not warm-up**, and the adapter's `ema.py` M15 helper must not stand in for the
P007-relevant H1 EMA-50 — but because that helper is never surfaced to reasoning and the correct OHLCV is
provided, it is nonblocking with a required resume note.

```
RED_TEAM_VERDICT = PASS_WITH_NONBLOCKING_NOTES
SAFE_TO_EXTEND_SEALED_BOUNDARY_TO_BAR_379 = YES (conditional on the §6 EMA note)
SAFE_FOR_NEW_AI_TRADER_SESSION = YES (conditional on the §6 EMA note)
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

Bar 379 not semantically exposed, sealed boundary not extended, Q4 not resumed, adapter/S5/MGMT-004/Q4-P007-003
not modified. Control returned to CEO.

---

*Red Team · independent adversarial review · commit identity + source identity verified · sealed reader +
bar-379 boundary proven · EMA root-cause independently corrected (H1-vs-M15, not warm-up) · 50/50 tests
reproduced · bar 379 not semantically exposed · LEDGER E103 (prev E102).*
