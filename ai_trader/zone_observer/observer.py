"""`ZoneObserver` -- pure observation, feeds the Level-3 confluence map (CEO instruction, 2026-08-04:
"Doar observare, fara politici. Zero semnale, zero ordine."). Same recompute-from-scratch,
diff-against-recorded convention as `structural_observer.observer.StructuralObserver` -- every
vendored detector is a stateless pure function over the whole accumulated array; `observe()` reruns
each one every bar and only journals what has not already been recorded.

**Single continuous block**, same as `structural_observer`: one `Block(0, len(bars))`, growing,
never reset.

**In-memory bar history, same disclosed limitation as `structural_observer`**: does not survive a
restart. Already-recorded observations remain in the persisted journal; the observer re-accumulates
from whatever bars the loop feeds it next.

**`detect_fvgs` is computed here but NEVER recorded as its own event** -- `structural_observer`
already records FVG_FORMED/FVG_REACTION from the byte-identical function, live. It is recomputed here
ONLY because `detect_inverse_fvgs`/`count_bpr` require the FVG list as an input; recomputation is a
technical necessity of a separate process with its own bar array, not a duplicated observation."""

from __future__ import annotations

from ai_trader.live_signal_source.types import Bar
from ai_trader.pdh_pdl_demo.day_index import day_boundary_start_utc
from ai_trader.zone_observer.journal import ZoneObservationLog
from ai_trader.zone_observer.types import ZoneEventKind, ZoneObservation
from ai_trader.zone_observer.vendor_bridge import (
    Block,
    compute_prior_session_levels,
    compute_prior_week_levels,
    count_bpr,
    derive_session_index,
    derive_week_index,
    detect_demand_zones,
    detect_fvgs,
    detect_inverse_fvgs,
    detect_liquidity_voids,
    detect_session_level_touches,
    detect_session_mid_touches,
    session_labels,
)

_BPR_TOLERANCES = (0.0, 0.10, 0.25)


class ZoneObserver:
    def __init__(self, symbol: str, journal: ZoneObservationLog) -> None:
        self._symbol = symbol
        self._journal = journal
        self._times: list[int] = []
        self._opens: list[float] = []
        self._highs: list[float] = []
        self._lows: list[float] = []
        self._closes: list[float] = []

        self._recorded_session_levels: set[tuple[int, str]] = set()
        self._recorded_session_touches: set[tuple[int, str]] = set()
        self._recorded_demand_zones: set[int] = set()
        self._recorded_ifvg: set[int] = set()
        self._last_bpr_counts: dict[float, int] = {t: 0 for t in _BPR_TOLERANCES}
        self._recorded_weekly_levels: set[tuple[int, str]] = set()
        self._recorded_voids: set[int] = set()

    @property
    def current_bar_count(self) -> int:
        return len(self._closes)

    def observe(self, bar: Bar) -> None:
        """Feeds one newly-closed bar and records every newly-detected zone fact. Call once per bar
        the loop's own feed emits -- never on a forming bar (the caller, `LiveBarFeed`, already
        guarantees this)."""
        self._times.append(bar.ts_open)
        self._opens.append(bar.open)
        self._highs.append(bar.high)
        self._lows.append(bar.low)
        self._closes.append(bar.close)

        block = Block(0, len(self._closes))
        as_of = bar.ts_close

        self._observe_session_levels(block, as_of)
        self._observe_demand_zones(block, as_of)
        self._observe_imbalance_derivatives(block, as_of)
        self._observe_weekly_levels(block, as_of)
        self._observe_liquidity_voids(as_of)

    def _record(self, kind: ZoneEventKind, as_of: int, detail: dict[str, object]) -> None:
        self._journal.record(
            ZoneObservation(symbol=self._symbol, as_of=as_of, kind=kind, detail=detail)
        )

    def _observe_session_levels(self, block: Block, as_of: int) -> None:
        session_index = derive_session_index(self._times)
        session_label = session_labels(self._times)

        levels = compute_prior_session_levels(self._highs, self._lows, session_index, session_label, [block])
        for lv in levels:
            key = (int(lv.source_session_start), str(lv.kind.value))
            if key not in self._recorded_session_levels:
                self._recorded_session_levels.add(key)
                self._record(ZoneEventKind.SESSION_LEVEL_FORMED, as_of, {
                    "level_kind": str(lv.kind.value), "price": float(lv.price),
                    "source_session_start": int(lv.source_session_start),
                    "available_idx": int(lv.available_idx), "expiry_idx": int(lv.expiry_idx),
                    "session_label": str(lv.session_label),
                })

        hl_touches = detect_session_level_touches(self._highs, self._lows, levels)
        mid_touches = detect_session_mid_touches(self._highs, self._lows, levels)
        for t in (*hl_touches, *mid_touches):
            key = (int(t.level.source_session_start), str(t.level.kind.value))
            if key in self._recorded_session_touches:
                continue
            self._recorded_session_touches.add(key)
            self._record(ZoneEventKind.SESSION_LEVEL_TOUCH, as_of, {
                "level_kind": str(t.level.kind.value), "price": float(t.level.price),
                "source_session_start": int(t.level.source_session_start),
                "touch_idx": int(t.touch_idx), "session_label": str(t.level.session_label),
            })

    def _observe_demand_zones(self, block: Block, as_of: int) -> None:
        zones = detect_demand_zones(self._opens, self._highs, self._lows, self._closes, block.end)
        for z in zones:
            key = int(z.formation_idx)
            if key in self._recorded_demand_zones:
                continue
            self._recorded_demand_zones.add(key)
            self._record(ZoneEventKind.DEMAND_ZONE_FORMED, as_of, {
                "formation_idx": key, "zone_kind": str(z.kind.value),
                "zone_lower": float(z.zone_lower), "zone_upper": float(z.zone_upper),
            })

    def _observe_imbalance_derivatives(self, block: Block, as_of: int) -> None:
        fvgs = detect_fvgs(self._highs, self._lows, [block])  # input only -- never recorded itself

        ifvgs = detect_inverse_fvgs(self._highs, self._lows, self._closes, fvgs, [block])
        for ifvg in ifvgs:
            key = int(ifvg.formed_idx)
            if key in self._recorded_ifvg:
                continue
            self._recorded_ifvg.add(key)
            original = next(
                (f for f in fvgs if f.lower == ifvg.lower and f.upper == ifvg.upper and f.formed_idx < ifvg.formed_idx),
                None,
            )
            self._record(ZoneEventKind.INVERSE_FVG_FORMED, as_of, {
                "inversion_idx": key, "new_kind": str(ifvg.kind.value),
                "lower": float(ifvg.lower), "upper": float(ifvg.upper),
                "original_formed_idx": int(original.formed_idx) if original is not None else None,
            })

        counts = count_bpr(fvgs, [block], tolerances=_BPR_TOLERANCES)
        if any(counts[t] > self._last_bpr_counts[t] for t in _BPR_TOLERANCES):
            self._last_bpr_counts = dict(counts)
            self._record(ZoneEventKind.BPR_COUNT, as_of, {
                f"tolerance_{t}": int(counts[t]) for t in _BPR_TOLERANCES
            })

    def _observe_weekly_levels(self, block: Block, as_of: int) -> None:
        day_index = [day_boundary_start_utc(t) for t in self._times]
        day_ordinal = [d // 86_400 for d in day_index]
        week_index = derive_week_index(day_ordinal)

        levels = compute_prior_week_levels(self._highs, self._lows, day_index, week_index, [block])
        for lv in levels:
            key = (int(lv.source_period_start), str(lv.kind.value))
            if key in self._recorded_weekly_levels:
                continue
            self._recorded_weekly_levels.add(key)
            self._record(ZoneEventKind.WEEKLY_LEVEL_FORMED, as_of, {
                "level_kind": str(lv.kind.value), "price": float(lv.price),
                "source_period_start": int(lv.source_period_start),
                "available_idx": int(lv.available_idx),
                "days_contributing": lv.days_contributing, "completeness": lv.completeness,
            })

    def _observe_liquidity_voids(self, as_of: int) -> None:
        voids = detect_liquidity_voids(self._opens, self._closes, self._times)
        for v in voids:
            key = int(v.at_idx)
            if key in self._recorded_voids:
                continue
            self._recorded_voids.add(key)
            self._record(ZoneEventKind.LIQUIDITY_VOID, as_of, {
                "at_idx": key, "void_kind": str(v.kind.value),
                "gap_seconds": int(v.gap_seconds), "price_jump": float(v.price_jump),
            })
