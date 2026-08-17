# AI_TRADER_TIME_DUAL_CLOCK_N1_HYDRATION_REPORT

RT-TIME-0001 (sections A + B) + RT-N1-HYDRATION-0001. Per-commit verdicts, separate — Commit C is
**CONDITIONAL**, not READY. Nothing in this report was deployed, restarted, cut over, or full-regressed
as part of this delivery step; LIVE_SHADOW ran the entire time this work was done and was not touched.

## Verdicts

| Commit | Hash | Status |
|---|---|---|
| A — request-scoped time fix | `7905236` | `TOWER_REQUEST_TIME_FIX_READY` |
| B — M5 dual-clock | `6b45ee1` | `COMMIT_B_DUAL_CLOCK_CODE_READY` |
| C — N1 startup hydration | `8607d01` (+ adversarial test `5ac10eb`) | **`N1_STARTUP_HYDRATION_CONDITIONAL`** — not READY |

All three pushed to `trader/ai-trader-implementation`; local `HEAD` (`5ac10eb`) verified byte-identical
to the remote after a fresh `git fetch` (see "Worktree inventory" below).

## A — diff and tests

`7905236` (`TOWER_REQUEST_TIME_FIX_READY`): `wall_clock.py` (new — `MonotonicWallClock`,
`ClockRollbackError`), `event_identity.py` (+20, additive optional fields), `bridge.py` (`TowerDependencies
.now` removed → `wall_clock_provider`; `_query_tower_chain` takes `event_as_of`/`data_cutoff`, clamps the
latter `<= event_as_of`, anchors every bar fetch to `data_cutoff`, refuses `FUTURE_EVENT_REJECTED` before
any fetch, refuses `WALL_CLOCK_ROLLBACK_DETECTED` on a backward clock read), `test_bridge_request_scoped_
time.py` (new, 11 tests — process-uptime-never-stales at 10/30/120min, fake-clock-advances-without-restart,
historical-catchup-zero-lookahead, future-event-refused, clock-rollback-fail-closed, genuine-staleness-
still-reported, restart-produces-identical-anchor), `entrypoint.py` (`now=` dropped from construction).

## B — diff and tests

`6b45ee1` (`COMMIT_B_DUAL_CLOCK_CODE_READY`): `bridge.py` (+6 public aliases — `query_tower_chain`,
`ChainQueryResult`, `side_from_strategy`, `side_provenance`, `PLACEHOLDER_TARGET_RR`,
`ELIGIBILITY_POLICY_VERSION`, `FP` — unmodified re-exports, chain-binding without reimplementation),
`bar_feed.py` (`watermark_key_suffix` param, additive), `new_brain_live/dual_clock/` (new — `upstream_
context.py`: `CachedUpstreamContext`/`build_context`/`UpstreamContextStore`; `context_refresh_loop.py`:
`ContextRefreshLoop`, its own `LiveBarFeed` with `watermark_key_suffix="dual_clock_context"`;
`m5_decision_loop.py`: `M5DecisionLoop`, the only tower call is `bridge.query_tower_chain`). 11 tests
(`test_m5_decision_loop.py`): missing/stale/future context all reject with zero tower contact; ineligible
strategy never reaches tower; genuinely eligible strategy reaches the real chain with real TowerN2/N3/N4
traces (distinct `input_fingerprint`s, `worker.connection_count == 1`); LEGACY authority never reaches
tower; broker gate default-disabled (structural); a candidate reaching the gate is blocked with
`order_send_calls`/`orders_created`/`positions_created == 0`; second tick with no new bar processes
nothing new; `ContextRefreshLoop`'s feed and the main M15 loop's own feed proven to hold independent
watermarks; upstream context serialization round-trips exactly.

### Lookahead fix — `CONTEXT_FROM_FUTURE`

Found while writing B's own tests, before any test existed against it: the original staleness check
(`if context is None or (bar.ts_close - context.market_timestamp) > threshold`) only bounded context age
from **above**. A negative age — a cached M15 context that closed *after* the M5 bar currently being
evaluated (a genuine possibility if `ContextRefreshLoop` and `M5DecisionLoop` ever tick out of order under
a backlog) — is numerically "not stale" and would have silently passed through as valid. Added a dedicated
fail-closed branch (`context.market_timestamp > bar.ts_close` → `CONTEXT_FROM_FUTURE`, zero tower contact)
with its own test (`test_context_from_the_future_is_rejected_not_silently_accepted`) before the rest of B's
suite was written.

## C — tests that pass, and the semantic limitation of the bounded snapshot

`8607d01` (`N1_STARTUP_HYDRATION_CONDITIONAL`): `vendor_bridge.py` (+`ATR_WINDOW`/`COMPRESSION_WINDOW`/
`COMPRESSION_PCTL`/`K_DEFAULT`/`DISP_MULT`/`BODY_FRAC`, additive re-exports of the vendored detectors' own
tunables), `bar_feed.py` (extracted `watermark_key()` as the one formula both `LiveBarFeed` and hydration
use), `n1_hydration/` (new — `identity.py`: `required_bar_count()` derived live as
`max(ATR_WINDOW, COMPRESSION_WINDOW, 2*K_DEFAULT+1)`, never a duplicated literal, verified both against the
real constants and against its own non-docstring source; `identity_matches_for_restore` compares only
structural fields, never data-range/watermark; `snapshot.py`: `N1Snapshot`/`N1SnapshotStore`, **bounded to
the trailing `required_bar_count()` bars by disclosed design** — `RawAxesBuilder` itself accumulates
forever, so a bounded snapshot cannot in general carry the full history a continuous run would have;
`hydrate.py`: `hydrate_n1` — restore-compatible-snapshot-and-catch-up-only-missing-bars, or fail-closed
full rebuild on any identity mismatch, reusing `LiveBarFeed` for every MT5 interaction, zero import of
Router/DecisionRequest/decide_n6/risk_gate/execution_shadow/broker-gate). 10 tests pass
(`test_hydrate.py`): required-bar-count derived not hardcoded; empty-state backfill matches a continuous
run; compatible-snapshot restore+catch-up matches a continuous run *over the same total bar count within
the bounded window*; incompatible snapshot (wrong `implementation_commit`) refused and rebuilt canonically;
future/unclosed bars never observed; repeated hydration with no new bars reproduces identical state;
this package's own non-docstring source never references a decision/broker module; the real `LiveBarFeed`
seeded from hydration's watermark sees exactly one new bar and never re-emits it; the persisted watermark
matches `LiveBarFeed`'s own key formula; a short flat sequence hydrates to `UNCERTAIN`, never a fabricated
regime.

**What those 10 tests do NOT cover — the reason for CONDITIONAL**: every one of them keeps total bars fed
within the bounded window, so the "restore matches continuous" claim is only proven *inside* that window.
It was never proven — until the adversarial test below — what happens when the real structural dependency
that produced the CURRENT regime sits *outside* the window.

## The adversarial test (`5ac10eb`, `test_unbounded_structure_dependency_blocker.py`)

VE's own code-level finding at checkpoint `e90bad7`, independently reproduced here: `expansion`/
`is_displacement` and `compression`/`is_compressed` are genuinely bounded (`RawAxesBuilder.observe()`
computes them over trailing `ATR_WINDOW`/`COMPRESSION_WINDOW` windows), but `structure`/`direction` are
**not** — `detect_swings`/`detect_breaks` always run over `Block(0, len(self._closes))`, the FULL
accumulated array, and report whichever break has the highest index ever seen, however old.

Fixture: a confirmed `bos_bull` break (`conftest.py`'s own hand-verified fixture, index 14) followed by
500 calm bars with no further break — so the only break in the entire history sits 500+ bars before the
end, well outside `required_bar_count()` (460).

- **Continuous, never-restarted run** over the full 518-bar history: `structure="strong"`,
  `direction="up"` — correct, the break is still the latest one.
- **Cold hydration** (first `hydrate_n1` call, no snapshot yet): fetches and replays all 518 bars —
  matches the continuous run, and persists a snapshot bounded to the trailing 460 bars (which excludes
  the BOS bars entirely — asserted directly: `bars_replayed_from_snapshot == required_bar_count()`).
- **Restart, restoring from that snapshot** (second `hydrate_n1` call, no new bars available): rebuilds
  `RawAxesBuilder` from only the 460 bars the snapshot carries → `structure=None`, `direction=None`
  (`UNCERTAIN`) — the break is gone. `ve_brain.applicable_regimes(...)` and
  `ve_brain.StrategyRouter(...).eligible(...)` were run on both sides and diverge: the Router verdict
  itself changes across a restart, for identical real market history, with nothing else different.

The test asserts this divergence explicitly and is meant to stay red — sorry, stay **documenting** this —
until one of the CEO's three named remediations lands: (1) incremental canonical state sufficient for the
unbounded dependency, (2) an official compatible snapshot from `ve_n1_replay` incremental, or (3) a
demonstrated-equivalent full/incremental replay. No incremental detector logic was invented locally to
route around this, and `ve_n1_replay` was not installed into the main AI Trader process — its own bootstrap
was not checked for collision with `ai_trader.*` imports already present, so that installation is
explicitly out of scope here, not attempted.

**Consequence, stated directly: Commit C's `hydrate_n1` must not feed live decisions in its current form.**
A restart at the wrong moment (a still-active regime whose founding break is more than ~460 bars back) can
silently downgrade a real TREND_UP/TREND_DOWN reading to UNCERTAIN — not a crash, not an error, a *quiet*
loss of information that only a targeted test like this one would ever surface.

## Migration plan (for when Red Team clears A + B, and C's blocker is closed)

1. Confirm Red Team has reviewed A (`7905236`) and B (`6b45ee1`) independently; C stays excluded from this
   round given its CONDITIONAL status.
2. Stop `AITraderLiveShadow` cleanly (same watermark/journal-baseline-capture procedure already proven in
   the `65798b4` cutover — nothing new to invent here).
3. `git pull`/verify `HEAD` on the machine running the task matches the Red-Team-cleared commit for A+B.
4. Wire `dual_clock.M5DecisionLoop`/`ContextRefreshLoop` into `entrypoint.py`'s `build_loop()`/`main()` —
   this file has deliberately never been touched by A or B; that wiring is itself a reviewable diff, not
   done here.
5. Restart the task, immediately re-run the same class of checks as the `65798b4` cutover (parent process
   is `svchost.exe`, singleton held, heartbeat fresh, authority `NEW_BRAIN`, gate `DISABLED`, zero orders/
   positions, zero duplicate bars) plus B-specific checks (three distinct watermarks advancing, M5 traces
   now showing real TowerN2/N3/N4 for eligible events).
6. C is added to this plan ONLY after a separate, dedicated closure of the adversarial test above.

## Rollback

Every change in A/B/(the safe parts of C) is additive at the file level — no existing call site was
rewired to a new code path anywhere in this delivery. If a wired cutover (a future step, not this one)
needs to be undone: stop the task, `git checkout` the task's working directory back to the pre-cutover
commit (`255eee6`, the commit the CURRENTLY running process was already built from — verified live below),
restart. No schema migration, no data format change, no snapshot to unwind for A/B. For C specifically: if
`hydrate_n1` were ever wired and needed rollback, deleting the `new_brain_live.n1_hydration.snapshot` key
from the state DB (or simply not calling `hydrate_n1` at all) returns the process to today's real behavior
— empty-state N1, no persisted hydration snapshot, exactly current LIVE_SHADOW.

## Scheduled Task XML review

No change needed and none made. `AITraderLiveShadow`'s registered action is unchanged:
`...\ai_quant_lab-research-main\venv\Scripts\python.exe -m ai_trader.new_brain_live.entrypoint`, working
directory the repo root, `State: Running`, `LastRunTime: 2026-08-17 23:12:37` — confirms none of A/B/C's
new code is referenced by the task definition; nothing to migrate at the task level until the cutover step
above actually wires `dual_clock`/`n1_hydration` into `entrypoint.py`.

## LIVE_SHADOW runtime identity (re-verified read-only, immediately before writing this report)

PID `25992`, `process_start_identity="25992:1786997557"` (matches OS `CreationDate` exactly, independently
re-cross-checked), `runtime_commit="255eee6"` (unchanged since the reconstruction earlier this session —
correctly still reflects the commit that was `HEAD` at the process's own start; none of today's commits on
disk affect an already-running process's in-memory code), `authority="NEW_BRAIN"`,
`broker_gate_state="DISABLED"`, `mt5_connected=true`, heartbeat age `28.9s` (fresh). `last_journal_sequence`
still `72` (unchanged — market closed, no new M15 bar since the earlier check today, consistent with your
own `MARKET_CLOSED_EXPECTED_NO_NEW_BAR` note).

## Broker DISABLED / zero orders / zero positions

Runtime: `broker_gate_state="DISABLED"`, `open_orders=0`, `open_positions=0`, `balance=equity=10000.34`
throughout (the `CEO_EXTERNAL_DEMO_ACCOUNT_DEPOSIT` baseline, unchanged). Code: `BrokerOrderSubmissionGate
.enabled: bool = False` (frozen dataclass, `kw_only=True`, no setter) — unchanged by any commit in this
report. Structural: `n1_hydration`'s own non-docstring source contains no reference to `BrokerOrderSubmiss
ionGate`/`order_send`/`submit_new_brain_candidate` (checked directly, not asserted from convention).

## Worktree inventory (both repos, confirmed clean immediately before this report)

**`ai_quant_lab-research-main`**, branch `ai-trader-implementation`: local `HEAD` = `5ac10eb`, `trader/
ai-trader-implementation` (fresh fetch) = `5ac10eb` — 0 ahead/0 behind, pushed and verified. `git status
--short`: only the same pre-existing, unrelated scratch entries noted in the earlier reconstruction
(`full_regression_a98a0a4_output.txt`/`full_regression_commit_a98a0a4.txt`/`scratch_verify/`/
`scratchpad_verify/`) — nothing from today's three commits left uncommitted.

**`tradingview-mcp`**: unchanged from the earlier reconstruction — local `main` still `c839e91`, still 1
ahead / 64 behind `origin/main`; the same legitimate DI/env-port diff and E015-SCALP scratch files; the two
stray files below still present, still untouched.

## The two stray files in `tradingview-mcp` — left untouched

`mypy_full_mandate4_step1.txt`, `pytest_full_mandate4_step1.txt` (both dated 2026-07-29, content is
`mypy`/`pytest` output referencing `ai_trader\...` paths — leaked from a session that ran a validation
command while `cwd` was actually this repo, not `tradingview-mcp`). Confirmed still present, still
untracked, still not deleted/moved/reverted, per your instruction. Awaiting your call.

## Explicit prohibitions honored this step

No deployment of A/B/C into `entrypoint.py`. LIVE_SHADOW not restarted, not cut over. No full `ai_trader/`
regression run in this step (only the targeted packages A/B/C touch, as in every prior delivery). The two
stray `tradingview-mcp` files not touched. Post-01:00 market-reopen verification (new tick, first M5/M15
close, watermark advance, journal continuity) intentionally deferred to a separate session and will not be
conflated with Commit C's own correctness — that verification is about M15's own live feed, unrelated to
the structural-history blocker documented above.

## Status

- `A` → `TOWER_REQUEST_TIME_FIX_READY`
- `B` → `COMMIT_B_DUAL_CLOCK_CODE_READY`
- `C` → `N1_HYDRATION_CONDITIONAL_PENDING_INCREMENTAL_STATE`
- This report → `READY_FOR_TIME_AND_DUAL_CLOCK_REVALIDATION`
