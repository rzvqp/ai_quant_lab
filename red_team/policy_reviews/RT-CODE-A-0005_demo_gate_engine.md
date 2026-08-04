# RED TEAM — CODE ATTACK · DEMO gate-enforcement engine
### RT-CODE-A-0005 · Targets: `demo_gate_engine/pdh_pdl_demo_engine.py` (`86304e7`) + `dynamic_exit_engine.py`
**Date:** 2026-07-29 · **Auditor:** Red Team · **Mandate:** CEO — first independent attack on the engine that imposes S1/S2/S3 (built after ledger close, previously only VE self-verified; audit risk C-R1). **No data run · engine not modified · no remedy designed.**
**Method:** full source of both engines + both test files + `docs/MIN_STOP_FLOOR_PREREG.md`, read at source. Working tree == `86304e7` for the pinned file (verified, empty diff).

## HEADLINE — does the gate impose what it claims? **PARTIALLY. It does NOT fully impose S1.**
S2, S3, and the audit trail are correctly and completely enforced. The S1 worst-case hierarchy is correct **for every bar after entry** — but the **entry bar's own stop is unguarded for non-floored trades**, and because the bar's open is its first tick, a wick through the stop on the entry bar is a **real post-entry stop-out** that the engine can report as a **TARGET (win)**. This is demonstrated by the engine's **own test fixture**. **Do not wire the three waiting policies live on this engine until it is closed. The VE BLOCK stands, now for a second, independent reason.**

---

## 🔴 DEFECT D1 — S1 is not imposed on the ENTRY BAR for non-floored trades (a stop-out can be reported as a win)
Both engines scan exits from `entry_idx+1` (`pdh:112,145`; `dynamic:36,60`). The **entry bar `ei` is checked for the stop ONLY when the trade is floored** (`pdh:139-142`, `dynamic:56-58`). For a **non-floored** trade the entry bar is skipped entirely, so an intrabar stop-out on `ei` is never registered.

**Why it is a real stop-out, not a timing artifact:** the bar's **open is its first traded price by definition**; entry = `open[ei]`. Therefore any `low[ei] ≤ exec_stop` (long) / `high[ei] ≥ exec_stop` (short) is a move that happened **after** entry — a genuine post-entry stop breach. Worst-case (and expected-case) resolution is STOP. The engine ignores it.

**Demonstrated by the engine's OWN test** — `test_invalid_execution_is_narrow_floored_only`, part (b) (`test_pdh_pdl_demo_engine.py:141-143`):
- Fixture: long, `open=100`, `strategy_stop=99.0` → `exec_stop=99.0`, **not floored**; **`low[ei=1]=98.9`** (through the 99.0 stop); bar 2 `high=105` hits the target.
- Engine result: **`ExitReason.TARGET`** at 104 (`net_R > 0`, a WIN).
- Reality: entered at 100, the entry bar traded to 98.9 → **stopped out at 99.0 (a LOSS)** before any target.
- The test asserts only `exit_reason != INVALID_EXECUTION` — **true, because it is TARGET** — so the suite **passes while encoding the optimistic misclassification**. The gate's own fixture turns a loss into a reported win and green-ticks it.

**Scope:** every surviving non-floored trade (flooring is the exception, so this is the majority) whose entry bar wicks to the stop and recovers. Entries are next-open right after a level touch — the entry bar wicking back to the level/stop is exactly the common case. Symmetric on the short side. **This directly contradicts the S1 claim "STOP over everything" and is the precise failure mode S1 exists to prevent.** Present in **both** engines.

## 🔴 DEFECT D2 (confirms C-D1) — the dynamic engine's time-stop is the BLOCK boundary = Finding H′, and `day_end_idx` carries two meanings
- `pdh_pdl_demo_engine.py:57`: `day_end_idx` = **"ultima bară a ZILEI"** (day boundary — live-valid).
- `dynamic_exit_engine.py:6-7,67`: the **same `DemoSignal.day_end_idx` field** = **"granița de BLOC … n-1"** (block boundary). A block is a discovery-data construct → the block-boundary time-stop **never fires on a live forward account** (Finding H′). The dynamic engine's *only* backstop besides stop/opposing-expansion is therefore inert live.
- **Two engines sharing one dataclass assign its field opposite meanings** with no type-level distinction — a caller wiring `dynamic` with a day boundary, or `pdh` with a block boundary, is silently "valid."
- **Affected candidates:** the dynamic engine names **CAND-0002** (Compression-Expansion, DEMO_BASELINE) and covers any policy whose exit is a forward *event* (not a price level). CAND-0002's Part B Finding H′ was **never remediated at the policy level** (session/persistent policies were) and is now faithfully embedded in executable code.

## 🟠 RISK R1 — the prereg's THIRD INVALID_EXECUTION condition is not implemented
`MIN_STOP_FLOOR_PREREG.md:29-31` defines INVALID as (a) gap through the floored stop at entry, (b) zero/negative risk after flooring, **OR (c) "entry/exit inside the same bar with ambiguous fill that the worst-case model cannot resolve."** The engine implements (a) (`pdh:139-142`) and (b) (`pdh:129-131`) but **not (c)**. The one place (c) arises — entry on the day's last bar (`entry_idx == day_end_idx`, empty scan loop) — is resolved as **TIME_STOP at close** (`pdh:162-163`), i.e. a clean open→close hold, **ignoring any intrabar stop on that bar**. Optimistic, and a direct deviation from the prereg's prescribed handling (mark INVALID). Bounded (last-bar entries only), but same optimism family as D1.

## 🟠 RISK R2 (confirms C-R7, and broader) — undeclared index preconditions, no asserts (F3-class)
- `dynamic_exit_engine.py:71` reads `open_[j+1]`; safe only because the boundary guard makes `j+1 ≤ scan_end` **and** the caller must set `day_end_idx ≤ n-1`. No internal assertion.
- Broader, in **both** engines: nothing asserts `entry_idx ≤ day_end_idx ≤ n-1`. If a caller passes `entry_idx > day_end_idx`, the scan loop is empty and the engine returns a time-stop at `close[scan_end]` with **`exit_idx < entry_idx`** — an exit *before* entry, and a `net_R` computed off a pre-entry price (silent garbage). Same undeclared-precondition shape as the F3 defect Red Team found in `market_structure.py`.

## 🟠 RISK R3 — gap-through-stop on a non-entry bar fills at the stop price, not the (worse) gap open
When `hitS` on a later bar, exit fills at `exec_stop_price` exactly (`pdh:150-155`), even if the bar gapped *through* the stop (open beyond it), where a live fill is worse. The residual slippage is folded into the single observed `cost` constant, which cannot capture a tail gap. Minor optimism; the S1 *ordering* mandate is met, but the fill-price worst-case is not. Flagged, not a gate failure.

## 🟡 UNDOCUMENTED U1 — prereg constants are hardcoded copies
`K_SPREAD=2, K_TICK=5, K_ATR=0.10` (`pdh:34-36`) are hand-copied from `MIN_STOP_FLOOR_PREREG.md:15-17` ("NU re-derivate aici"). Values match today, but a prereg edit silently diverges — the same two-independent-definitions hazard as `ATR_WINDOW`.

---

## WHAT SURVIVES (verified correct)
- **S1 hierarchy on bars `ei+1 … day_end` — CORRECT.** All collisions resolve worst-case: STOP∧TARGET→STOP (`pdh:150-155`, tested `:38`), STOP∧TIME-STOP→STOP (tested `:65`), TIME-STOP∧TARGET→TIME-STOP at close, not target (`pdh:156-158`, tested `:54`), triple→STOP (`pdh:151`, correct by inspection). Short-side symmetric (tested `:161`). The optimistic-target assumption on the boundary bar is correctly forbidden.
- **S2 — CORRECT and well-tested.** Floor on the corrected distance; `strategy_stop_distance` preserved not overwritten (`pdh:107,125`, tested `:76`); 1R sized on the floored distance; `effective_spread` is the **observed** value used directly, not a modeled constant (tested `:91`). Formula/constants match the prereg exactly.
- **S3 — CORRECT and well-tested.** `scan_start = ei+1` (`pdh:112`); an entry-bar target touch is ignored (tested `:101`); a prior same-day visit *before* entry is below the window (tested `:112`).
- **INVALID narrow (a)+(b) — CORRECT** (`pdh:129-131,139-142`, tested `:134,:146`); ordinary collisions are not marked INVALID; the entry guard (open beyond target/stop → NO_TRADE) is separate (tested `:153`).
- **Audit fields — COMPLETE.** Every path routes through `_mk`, populating all S1/S2/S3 fields for every outcome including NO_TRADE/INVALID (`pdh:115-127`, tested `:123`). The gate is auditable — which is exactly how D1 is provable from its own fixture.

## TEST COVERAGE (Target 7) — what is NOT exercised
- **The entry-bar non-floored stop (D1)** — the one fixture that triggers it (`:141`) asserts only "not INVALID," never the exit reason → the defect is **masked, not tested**.
- **The triple collision** STOP∧TARGET∧TIME-STOP on the boundary (`stop_over_target_time_stop`, `pdh:151`) — code correct, **no test**.
- **`entry_idx == day_end_idx` / `> day_end_idx`** (empty-loop / exit-before-entry, R1/R2) — **no test**.
- **Prereg INVALID clause-3** — **no test** (because unimplemented).
- **Gap-through-stop fill price** (R3) — **no test**.
- **Dynamic engine (3 tests):** no floor/INVALID test at all (imports `min_executable_risk`, never exercises flooring on the dynamic path); no entry-bar-stop test; no `open_[j+1]` boundary-safety test; no test distinguishing the block-vs-day `day_end_idx` semantic (D2). The 3 tests cover only the happy path + stop-over-opposing + block time-stop.

---

## VERDICT — **SURVIVES on S2 / S3 / audit / post-entry S1; FAILS to fully impose S1 at the entry bar.**
**Direct answer to the CEO: the gate does NOT impose everything it claims.** S1's worst-case is enforced only from `entry_idx+1`; the entry bar's own stop is unguarded for non-floored trades, and since the open is the first tick, a wick through the stop there is a real post-entry stop-out the engine can report as a target/time-stop **win** (D1, shown by its own fixture). The dynamic variant additionally embeds the inert block-boundary time-stop (D2 = Finding H′). **These are exactly the optimistic resolutions S1/H′ exist to forbid, now living in the enforcement code itself — precisely the class of defect that independent review, not self-verification, exists to catch (audit risk C-R1 realized).**

**BLOCK any live wiring of the three waiting policies on this engine until D1 and D2 are closed.** The VE gate BLOCK on CAND-0001 already held for a different reason (mstrat couldn't be shown to enforce the gates); it now holds for a second: even the purpose-built gate engine under-imposes S1.

## HANDOFF → Statistician, then CEO
1. **D1 (entry-bar non-floored stop)** — highest: the gate can convert a loss to a reported win; must be closed before any live wiring, and the masking test rewritten to assert STOP.
2. **D2 (dynamic block-boundary time-stop = Finding H′; `day_end_idx` dual meaning)** — CAND-0002 must not wire live on this; the field's two meanings need separating.
3. **R1 (prereg INVALID clause-3), R2 (undeclared `entry_idx ≤ day_end_idx ≤ n-1` / `open_[j+1]`), R3 (gap-fill price), U1 (copied constants)** — carry.
4. **Coverage:** add tests for the entry-bar stop, the triple collision, the empty-loop path, and the dynamic-engine floor/INVALID/boundary cases.

Next Red Team target per the CEO queue: the statistical stack (`matched_null`, `pilot_pvalue`, `scoped_fdr`) — W9 still open there. One at a time. Red Team designed no remedy, ran no data, modified nothing outside `red_team/`.
