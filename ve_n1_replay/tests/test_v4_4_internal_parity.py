"""V4.4 INTERNAL-depth parity vs V4.3, byte-for-byte (mandat §19: F4/INTERNAL out of scope, must not be
recoupled into the MACRO release). Proves the claim in `range_semantic_v4_4.py`'s module docstring
empirically rather than by code-inspection alone: identical bars through both producers must yield
identical INTERNAL output at every bar, on fixtures exercising confirmation, sweep, breakout, and channel
labeling."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_range_semantic_v4_3 import cfg43, legs_bars, osc_bars   # noqa: E402

from ve_n1_replay.range_semantic_v4_3 import ConfigV43, RangeSemanticProducerV43   # noqa: E402
from ve_n1_replay.range_semantic_v4_4 import ConfigV44, RangeSemanticProducerV44   # noqa: E402


def _cfg44_matching(cfg43_obj: ConfigV43) -> ConfigV44:
    """`ConfigV44` cu campurile V4.3 identice cu cele ale `cfg43_obj` -- restul (semnalele V4.4) la
    valorile calibrate implicite, irelevante pt. INTERNAL."""
    return ConfigV44(
        d_macro=cfg43_obj.d_macro, d_internal=cfg43_obj.d_internal, n_touch=cfg43_obj.n_touch,
        K_reentry=cfg43_obj.K_reentry, N_accept=cfg43_obj.N_accept, K_struct=cfg43_obj.K_struct,
        n_external_swings=cfg43_obj.n_external_swings, atr_window=cfg43_obj.atr_window,
        w_atr=cfg43_obj.w_atr, atr_source=cfg43_obj.atr_source,
        atr_provenance_wheel_sha256=cfg43_obj.atr_provenance_wheel_sha256,
    )


def _run_both(bars: list[Any], atr: float = 1.0) -> tuple[list[dict], list[dict]]:
    cfg3 = cfg43()
    cfg4 = _cfg44_matching(cfg3)
    prod3 = RangeSemanticProducerV43(cfg3)
    prod4 = RangeSemanticProducerV44(cfg4)
    out3, out4 = [], []
    for b in bars:
        res3, _ = prod3.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close, atr=atr)
        res4, _ = prod4.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close, atr=atr)
        out3.append({"internal_id": res3.internal_id, "internal_reason": res3.internal_reason,
                    "internal_state": res3.internal_state, "internal_boundary_upper": res3.internal_boundary_upper,
                    "internal_boundary_lower": res3.internal_boundary_lower, "internal_role": res3.internal_role})
        out4.append({"internal_id": res4.internal_id, "internal_reason": res4.internal_reason,
                    "internal_state": res4.internal_state, "internal_boundary_upper": res4.internal_boundary_upper,
                    "internal_boundary_lower": res4.internal_boundary_lower, "internal_role": res4.internal_role})
    return out3, out4


def _assert_internal_identical(bars: list[Any], atr: float = 1.0) -> None:
    out3, out4 = _run_both(bars, atr)
    assert len(out3) == len(out4)
    for i, (a, b) in enumerate(zip(out3, out4)):
        assert a == b, f"INTERNAL diverges at bar {i}: V4.3={a!r} V4.4={b!r}"


def test_internal_parity_oscillating_macro_plus_internal_rotations() -> None:
    macro_legs: list[tuple[float, int]] = [
        (100, 0), (120, 6), (100, 6), (120, 6), (100, 6), (120, 6), (100, 6),
        (108, 5), (112, 5), (108, 5), (112, 5), (108, 5), (112, 5)]
    _assert_internal_identical(legs_bars(macro_legs))


def test_internal_parity_oscillator_long_run() -> None:
    _assert_internal_identical(osc_bars(cycles=15))


def test_internal_parity_directional_move_no_macro_ever_forms() -> None:
    bars = legs_bars([(100, 0), (200, 40)])
    _assert_internal_identical(bars)


def test_internal_parity_across_atr_values() -> None:
    macro_legs: list[tuple[float, int]] = [(100, 0), (120, 6), (100, 6), (120, 6), (100, 6), (120, 6), (100, 6)]
    for atr in (0.65, 1.0, 1.85, 3.2):
        _assert_internal_identical(legs_bars(macro_legs), atr=atr)


def test_internal_parity_snapshot_restart() -> None:
    """Restart la jumatate -- INTERNAL trebuie sa ramana identic intre V4.3 si V4.4 chiar dupa restore."""
    macro_legs: list[tuple[float, int]] = [
        (100, 0), (120, 6), (100, 6), (120, 6), (100, 6), (120, 6), (100, 6),
        (108, 5), (112, 5), (108, 5), (112, 5)]
    bars = legs_bars(macro_legs)
    cfg3 = cfg43(); cfg4 = _cfg44_matching(cfg3)

    prod3a = RangeSemanticProducerV43(cfg3)
    prod4a = RangeSemanticProducerV44(cfg4)
    for b in bars[:20]:
        prod3a.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close, atr=1.0)
        prod4a.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close, atr=1.0)
    snap3 = prod3a.snapshot_state(); snap4 = prod4a.snapshot_state()
    prod3b = RangeSemanticProducerV43(cfg3); prod3b.restore_state(snap3)
    prod4b = RangeSemanticProducerV44(cfg4); prod4b.restore_state(snap4)
    for b in bars[20:]:
        res3, _ = prod3b.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close, atr=1.0)
        res4, _ = prod4b.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close, atr=1.0)
        assert res3.internal_id == res4.internal_id
        assert res3.internal_reason == res4.internal_reason
        assert res3.internal_state == res4.internal_state
