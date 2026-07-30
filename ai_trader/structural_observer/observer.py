"""`StructuralObserver` -- Mandate 4 (2026-07-29): connects the vendored, frozen structural detectors to
the append-only journal as a pure OBSERVER. CEO: "Nu produce semnale. Nu evalueaza. INREGISTREAZA."

**Single continuous block** (CEO instruction, confirmed by Step 2's own investigation): every vendored
`Block`-based function receives exactly ONE `Block(0, len(bars))`, growing as new bars arrive -- never
reset, matching live's own lack of research-quarantine boundaries.

**Recompute-from-scratch, disclosed**: the vendored detectors are stateless pure functions over the
whole array (Step 2's own finding for `market_structure.py`, now confirmed to apply to every wired
detector) -- `observe()` re-runs every detector over the FULL accumulated bar history on every call,
diffing against what has already been recorded to avoid duplicate journal entries. A months-long run
needs a windowing/truncation strategy eventually; not built here.

**New, disclosed limitation this step introduces**: the accumulated bar array itself (`self._times`
etc.) is IN-MEMORY ONLY -- unlike the bar-feed watermark, the journal, or the equity high-water mark
(all persisted since Mandate 2), this observer's own bar history does not survive a process restart. A
restart means the observer starts empty and re-accumulates from whatever bars the loop feeds it next --
already-recorded observations remain in the (persisted) `StructuralObservationLog`, but detectors that
need a deep trailing window (`compression`'s 460 bars) will read `is_valid=False`/`None` again until
enough bars re-accumulate. Not solved here -- the same class of gap Step 2 already flagged for
`compression()` specifically, now a property of the whole observer.

Order Block breaker/mitigation/rejection tracking follows each OB until it is MUTED (a breaker occurs)
-- once an OB is known-broken, no further mitigation/rejection scan runs for it, matching
`order_flow.py`'s own `_breaker_stop` semantics (which would return the identical, already-recorded set
of events every time regardless -- skipping is an optimization, not a behavior change).
"""

from __future__ import annotations

from ai_trader.live_signal_source.types import Bar
from ai_trader.structural_observer.journal import StructuralObservationLog
from ai_trader.structural_observer.types import StructuralEventKind, StructuralObservation
from ai_trader.structural_observer.vendor_bridge import (
    Block,
    compression,
    detect_breaks,
    detect_fvg_reactions,
    detect_fvgs,
    detect_mitigations,
    detect_order_blocks,
    detect_rejections,
    detect_swings,
    expansion,
    label_structure,
    sessions,
    track_breaker,
)


class StructuralObserver:
    def __init__(self, symbol: str, journal: StructuralObservationLog) -> None:
        self._symbol = symbol
        self._journal = journal
        self._times: list[int] = []
        self._opens: list[float] = []
        self._highs: list[float] = []
        self._lows: list[float] = []
        self._closes: list[float] = []

        self._recorded_swings: set[tuple[int, str]] = set()
        self._recorded_breaks: set[tuple[int, str]] = set()
        self._recorded_fvgs: set[int] = set()
        self._recorded_fvg_stage: dict[int, set[str]] = {}
        self._recorded_obs: set[int] = set()
        self._recorded_ob_breaker: set[int] = set()
        self._recorded_ob_mitigation: set[tuple[int, int]] = set()
        self._recorded_ob_rejection: set[tuple[int, int]] = set()

    def observe(self, bar: Bar) -> None:
        """Feeds one newly-closed bar and records every newly-detected structural fact. Call once per
        bar the loop's own feed emits -- never on a forming bar (the caller, `LiveBarFeed`, already
        guarantees this)."""
        self._times.append(bar.ts_open)
        self._opens.append(bar.open)
        self._highs.append(bar.high)
        self._lows.append(bar.low)
        self._closes.append(bar.close)

        block = Block(0, len(self._closes))
        as_of = bar.ts_close

        self._observe_structure(block, as_of)
        self._observe_fvgs(block, as_of)
        self._observe_regime(as_of)
        self._observe_order_blocks(block, as_of)

    def _record(self, kind: StructuralEventKind, as_of: int, detail: dict[str, object]) -> None:
        self._journal.record(
            StructuralObservation(symbol=self._symbol, as_of=as_of, kind=kind, detail=detail)
        )

    def _observe_structure(self, block: Block, as_of: int) -> None:
        swings = label_structure(detect_swings(self._highs, self._lows, [block]))
        for s in swings:
            key = (int(s.idx), str(s.kind.value))
            if key in self._recorded_swings:
                continue
            self._recorded_swings.add(key)
            self._record(StructuralEventKind.SWING, as_of, {
                "idx": int(s.idx), "confirmed_idx": int(s.confirmed_idx), "price": float(s.price),
                "swing_kind": str(s.kind.value), "label": str(s.label.value),
            })

        breaks = detect_breaks(self._closes, swings, [block])
        for b in breaks:
            key = (int(b.idx), str(b.kind.value))
            if key in self._recorded_breaks:
                continue
            self._recorded_breaks.add(key)
            self._record(StructuralEventKind.STRUCTURE_BREAK, as_of, {
                "idx": int(b.idx), "break_kind": str(b.kind.value), "close": float(b.close),
                "reference_price": float(b.reference_swing.price),
            })

    def _observe_fvgs(self, block: Block, as_of: int) -> None:
        fvgs = detect_fvgs(self._highs, self._lows, [block])
        for f in fvgs:
            key = int(f.formed_idx)
            if key not in self._recorded_fvgs:
                self._recorded_fvgs.add(key)
                self._record(StructuralEventKind.FVG_FORMED, as_of, {
                    "formed_idx": int(f.formed_idx), "fvg_kind": str(f.kind.value),
                    "upper": float(f.upper), "lower": float(f.lower), "ce_50": float(f.ce_50),
                })

        reactions = detect_fvg_reactions(self._highs, self._lows, self._closes, fvgs, [block])
        for r in reactions:
            recorded = self._recorded_fvg_stage.setdefault(int(r.formed_idx), set())
            if r.ce50_touch_idx is not None and "ce50" not in recorded:
                recorded.add("ce50")
                self._record(StructuralEventKind.FVG_REACTION, as_of, {
                    "formed_idx": int(r.formed_idx), "stage": "ce50_touch", "idx": int(r.ce50_touch_idx),
                })
            if r.full_fill_idx is not None and "full" not in recorded:
                recorded.add("full")
                self._record(StructuralEventKind.FVG_REACTION, as_of, {
                    "formed_idx": int(r.formed_idx), "stage": "full_fill", "idx": int(r.full_fill_idx),
                })
            if r.inversion_idx is not None and "inversion" not in recorded:
                recorded.add("inversion")
                self._record(StructuralEventKind.FVG_REACTION, as_of, {
                    "formed_idx": int(r.formed_idx), "stage": "inversion", "idx": int(r.inversion_idx),
                })

    def _observe_regime(self, as_of: int) -> None:
        exp = expansion(self._opens, self._highs, self._lows, self._closes)
        comp, valid = compression(self._highs, self._lows)
        sess = sessions(self._times)
        last = len(self._closes) - 1
        self._record(StructuralEventKind.REGIME, as_of, {
            "expansion": bool(exp[last]),
            "compression": bool(comp[last]) if valid[last] else None,
            "session": str(sess[last]),
        })

    def _observe_order_blocks(self, block: Block, as_of: int) -> None:
        obs = detect_order_blocks(self._opens, self._highs, self._lows, self._closes, block.end)
        for ob in obs:
            key = int(ob.formation_idx)
            if key not in self._recorded_obs:
                self._recorded_obs.add(key)
                self._record(StructuralEventKind.ORDER_BLOCK_FORMED, as_of, {
                    "formation_idx": int(ob.formation_idx), "ob_kind": str(ob.kind.value),
                    "zone_lower": float(ob.zone_lower), "zone_upper": float(ob.zone_upper),
                })

            if key in self._recorded_ob_breaker:
                continue  # already broken -- order_flow.py's own semantics stop tracking here too

            breaker = track_breaker(ob, self._highs, self._lows, self._closes, block.end)
            if breaker is not None:
                self._recorded_ob_breaker.add(key)
                self._record(StructuralEventKind.ORDER_BLOCK_BREAKER, as_of, {
                    "formation_idx": int(ob.formation_idx), "breaker_idx": int(breaker.breaker_idx),
                    "new_kind": str(breaker.kind.value),
                })
                continue  # muted -- no mitigation/rejection scan for a broken OB

            for m in detect_mitigations(ob, self._highs, self._lows, self._closes, block.end):
                mkey = (key, int(m.event_idx))
                if mkey in self._recorded_ob_mitigation:
                    continue
                self._recorded_ob_mitigation.add(mkey)
                self._record(StructuralEventKind.ORDER_BLOCK_MITIGATION, as_of, {
                    "formation_idx": key, "event_idx": int(m.event_idx),
                    "visit_number": int(m.visit_number),
                })

            for r in detect_rejections(ob, self._highs, self._lows, self._closes, block.end):
                rkey = (key, int(r.event_idx))
                if rkey in self._recorded_ob_rejection:
                    continue
                self._recorded_ob_rejection.add(rkey)
                self._record(StructuralEventKind.ORDER_BLOCK_REJECTION, as_of, {
                    "formation_idx": key, "event_idx": int(r.event_idx),
                    "visit_number": int(r.visit_number),
                })
