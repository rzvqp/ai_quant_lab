# Real MT5 E2E Run — Findings

Executed `ai_trader/apprenticeship_v2/tests/test_mt5_e2e_integration.py` for real, against a live MetaTrader 5 terminal, per CEO mandate. **No code was changed in this session** — diagnostic investigation only, per the mandate's explicit "do not redesign or invent a fix" instruction.

## Environment used

The repo has its own dedicated virtualenv at `ai_quant_lab-research-main/venv` (Python 3.14.6) with `MetaTrader5==5.0.5735` installed — not previously checked in either prior report (both correctly, at the time, found no `MetaTrader5` via the bare `python`/`py` commands, which resolve to a different, non-venv interpreter). `terminal64.exe` (MetaTrader 5's own process) was already running. Connection confirmed live: `terminal_info().connected = True`, broker `FP Trading LLC`, server `FPTradingLLC-Demo` (a demo account, login 7406404, balance 3221.46 EUR — no real funds at risk), real XAUUSD tick data retrieved successfully.

## Result

`ai_trader/apprenticeship_v2/tests/` via the venv's Python: **176 passed, 1 failed, 0 skipped** (177 total — the 6 previously-skipped real-MT5 tests all executed for real this time; 5 of those 6 passed).

**Failing test**: `test_mt5_e2e_integration.py::test_no_duplicate_processing_on_second_tick_with_no_new_bars`, specifically the assertion `second["last_processed_m15_ts_close"] == first["last_processed_m15_ts_close"]` — observed off by exactly 1 (e.g. `1788690550 == 1788690549`). **Intermittent**: failed 3 of 5 separate attempts in this session (roughly 60%).

**What did NOT fail, in every single occurrence**: `second["new_general_episodes"] == []` — no duplicate episode was ever actually created, in any observed failure.

## Root cause, verified directly (not guessed)

A targeted, isolated reproduction (outside pytest, outside `GeneralObserverTick`) proves this precisely:

- Calling `mt5_read_only_source.fetch_causal_closed_bars` twice with a **fixed** `now_fn` (identical cutoff both times) across 45 combined attempts at two different gap lengths (0.15s and 0.7s): **0 mismatches**.
- Calling it twice with the **real**, advancing `now_fn=time.time` (matching `GeneralObserverTick.tick()`'s own default) at a realistic ~0.7s gap: **11 of 15 mismatches**, with the returned "last bar's" `ts_close` incrementing by **exactly 1** on each successive call in a tight loop — a smooth, second-by-second climb (`...821 → 822 → 823 → 824 → 825...`), never a ~900-second jump (which is what a genuinely new M15 bar closing would look like).

This isolates the mechanism precisely: `mt5_read_only_source.measure_broker_offset_seconds()` computes the broker-clock offset from the **latest live tick's own timestamp** (`symbol_info_tick`). During a quiet market moment (no new tick arriving between two calls — plausible and observed here), the offset calculation attributes the real elapsed wall-clock time entirely to "clock drift" rather than "tick staleness," so `_bar_from_rate`'s `true_ts_open = int(round(rate["time"] - offset_seconds))` drifts upward by approximately the real elapsed time between calls, for every bar returned, including already-fully-closed historical bars — not just the currently-forming one.

**This is a property of pre-existing, unmodified S5 code** (`mt5_read_only_source.py` — its own docstring already discloses the offset is "measured fresh from a live tick every call"; the file makes no claim of cross-call timestamp stability, and this delivery has never touched it). **General Observer's own new code** (`tick.py`'s `last_processed_m15_ts_close`/`GO_STATE_H1_KEY` watermarks) uses exact integer equality to detect "already processed" bars — an assumption of timestamp stability across repeated fetches that this pre-existing mechanism does not actually guarantee under quiet-tick conditions.

**Practical consequence, as observed**: the same already-processed bar can be re-examined by the detector pipeline on a subsequent tick. In every occurrence observed in this session, the existing dedup safety net (`is_duplicate`, keyed on level/price/direction/family — never on raw timestamp) correctly prevented this from creating an actual duplicate episode. This is an empirical observation across the runs performed here, not an exhaustive proof covering every detector/dedup-key combination (e.g., whether a `DISPLACEMENT` episode's own `underlying_move_id`-keyed dedup path behaves identically under this drift was not separately, exhaustively tested).

## Not attempted

No fix, redesign, or workaround was written or proposed for `tick.py`'s watermark logic or for `mt5_read_only_source.py`'s offset measurement, per the mandate's explicit instruction. This is a diagnostic report only.
