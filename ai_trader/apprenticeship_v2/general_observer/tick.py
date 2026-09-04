"""Genuinely wired, independently-schedulable tick loop for General Observer V1.1. Mirrors
`loop.py::ApprenticeshipTick`'s own structure (warmup + per-bar tick, causal bar fetch, durable
runtime-state bookkeeping) but lives in a COMPLETELY SEPARATE module: never imported by
`loop.py`/`main.py`, never imports either of them. `loop.py` and `main.py` are BYTE-UNCHANGED by this
delivery (verify with `git diff` -- zero lines touched in either file) -- the already-running,
production `AITraderApprenticeshipV2` Windows Scheduled Task's own behavior is therefore provably
unaffected by this module's mere existence. Running General Observer at all requires deliberately
starting the SEPARATE entrypoint in `main_general_observer.py`, under its own singleton lock name,
never automatically (Section 30) and never as a side effect of the existing S5 task running.

Runtime state is namespaced under a `go_` prefix inside the SAME `AI_TRADER_RUNTIME_STATE.json` file
S5 already uses (`durable_store.load_runtime_state()`/`save_runtime_state()` do a plain dict
read-modify-write) -- S5's own keys (`last_processed_m15_ts_close`, etc.) and this module's `go_*`
keys can never collide, so sharing the file is safe and avoids inventing a second state file for no
reason.

Combines two independent cadences the design doc places in the same subsystem: the per-M15-bar
general-observer trigger pipeline (`episode_builder.build_episodes_for_bar`, Section 8) and the
per-H1-bar missed-move audit (`missed_move_audit`, Section 10) -- run back-to-back in one `tick()`
call for operational simplicity (one process, one poll loop), but each keeps its own independent
`go_last_processed_*` watermark, so neither cadence's timing depends on the other's.
"""

from __future__ import annotations

import datetime
import time

from ai_trader.apprenticeship_v2 import durable_store
from ai_trader.apprenticeship_v2.general_observer.episode_builder import build_episodes_for_bar
from ai_trader.apprenticeship_v2.general_observer.missed_move_audit import (
    advance_cluster_state, audit_candidate, classify_for_clustering, cluster_from_dict,
)
from ai_trader.apprenticeship_v2.mt5_read_only_source import (
    TIMEFRAME_H1, TIMEFRAME_H4, TIMEFRAME_M5, TIMEFRAME_M15, XAUUSD, fetch_causal_closed_bars,
)

GO_STATE_M15_KEY = "go_last_processed_m15_ts_close"
GO_STATE_H1_KEY = "go_last_processed_h1_ts_close"
GO_STATE_ACTIVE_CLUSTER_KEY = "go_active_missed_move_cluster"

# Generous fetch counts -- comfortably cover the 32-M15-bar underlying-move window, ATR14/swing
# history, and the H4/H1/M15/M5 snapshot sizes (12/24/60/48), with margin. Cheap: read-only, local
# MT5 terminal calls, once per 15-minute tick.
M15_FETCH_COUNT = 100
H1_FETCH_COUNT = 60
H4_FETCH_COUNT = 14
M5_FETCH_COUNT = 50


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


class GeneralObserverTick:
    """One instance persists across `run_forever`'s loop iterations. Unlike `ApprenticeshipTick`,
    there is no in-memory strategy state to warm up (every general-observer function is a pure,
    stateless computation over freshly-fetched causal bars plus the durable ledger) -- `_warmed_up`
    exists only to mirror `ApprenticeshipTick`'s own shape and leave room for a future warmup step,
    should one become necessary; today it is a no-op."""

    def __init__(self) -> None:
        self._warmed_up = False

    def tick(self, now_fn=time.time) -> dict[str, object]:
        self._warmed_up = True
        state = durable_store.load_runtime_state()
        last_m15 = state.get(GO_STATE_M15_KEY)
        last_h1 = state.get(GO_STATE_H1_KEY)

        m15 = fetch_causal_closed_bars(symbol=XAUUSD, timeframe=TIMEFRAME_M15, count=M15_FETCH_COUNT, now_fn=now_fn)
        h1 = fetch_causal_closed_bars(symbol=XAUUSD, timeframe=TIMEFRAME_H1, count=H1_FETCH_COUNT, now_fn=now_fn)
        h4 = fetch_causal_closed_bars(symbol=XAUUSD, timeframe=TIMEFRAME_H4, count=H4_FETCH_COUNT, now_fn=now_fn)
        m5 = fetch_causal_closed_bars(symbol=XAUUSD, timeframe=TIMEFRAME_M5, count=M5_FETCH_COUNT, now_fn=now_fn)

        new_episode_ids: list[str] = []
        new_m15_count = 0
        for i, bar in enumerate(m15):
            if last_m15 is not None and bar.ts_close <= last_m15:
                continue
            new_m15_count += 1
            existing_rows = durable_store.read_all_general_episode_rows()
            episodes = build_episodes_for_bar(
                bar, symbol=XAUUSD, h4=h4, h1=h1, m15_causal_bars_up_to_and_including_bar=m15[: i + 1],
                m5=m5, existing_general_episode_rows=existing_rows,
            )
            for ep in episodes:
                durable_store.append_general_episode_to_ledger(ep)
                new_episode_ids.append(ep.episode_id)
            last_m15 = bar.ts_close

        active_cluster_dict = state.get(GO_STATE_ACTIVE_CLUSTER_KEY)
        active_cluster = cluster_from_dict(active_cluster_dict) if active_cluster_dict else None
        finalized_cluster_ids: list[str] = []
        for i, bar in enumerate(h1):
            if last_h1 is not None and bar.ts_close <= last_h1:
                continue
            candidate = audit_candidate(h1, i)
            if candidate is not None:
                existing_rows = durable_store.read_all_general_episode_rows()
                classification = classify_for_clustering(candidate, existing_rows)
                active_cluster, finalized = advance_cluster_state(classification, candidate, active_cluster)
                if finalized is not None:
                    durable_store.append_missed_move_cluster(finalized)
                    finalized_cluster_ids.append(finalized.cluster_id)
            last_h1 = bar.ts_close

        state[GO_STATE_M15_KEY] = last_m15
        state[GO_STATE_H1_KEY] = last_h1
        state[GO_STATE_ACTIVE_CLUSTER_KEY] = active_cluster.to_json_dict() if active_cluster is not None else None
        state["go_last_tick_utc"] = _now_iso()
        durable_store.save_runtime_state(state)

        return {
            "new_m15_bars": new_m15_count, "new_general_episodes": new_episode_ids,
            "finalized_missed_move_clusters": finalized_cluster_ids,
            "last_processed_m15_ts_close": last_m15, "last_processed_h1_ts_close": last_h1,
        }
