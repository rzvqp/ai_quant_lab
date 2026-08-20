"""V4.4 snapshot/restore robustness (mandat §11): missing fields, corrupt fields, wrong contract/config/
implementation-fingerprint, cross-version (V4.3 snapshot into V4.4 and vice versa), no partial state mutation
on any refused restore -- at both the producer level (`restore_state`) and the engine level (`restore`, which
composes N1)."""
from __future__ import annotations

import dataclasses as _dc
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_range_semantic_v4_3 import KW, cfg43, legs_bars   # noqa: E402

from ve_n1_replay.range_engine_v4_3 import RangeSemanticEngineV43, RangeSnapshotV43   # noqa: E402
from ve_n1_replay.range_engine_v4_4 import (   # noqa: E402
    RangeSemanticEngineV44, RangeSnapshotErrorV44, RangeSnapshotV44,
)
from ve_n1_replay.range_semantic_v4_3 import ContractErrorV43   # noqa: E402
from ve_n1_replay.range_semantic_v4_4 import ConfigV44, RangeSemanticProducerV44   # noqa: E402


def cfg44(**kw: Any) -> ConfigV44:
    return ConfigV44(**kw)


MACRO_LEGS: list[tuple[float, int]] = [
    (100, 0), (120, 6), (100, 6), (120, 6), (100, 6), (120, 6), (100, 6),
    (108, 5), (112, 5), (108, 5), (112, 5), (108, 5)]


def _engine44() -> RangeSemanticEngineV44:
    return RangeSemanticEngineV44(range_config=cfg44(), acknowledge_construction_only=True, **KW)


# ═══════════════════════════════════ nivel producator -- `restore_state` ═══════════════════════════════════

def test_restore_state_round_trip_succeeds_as_a_sanity_baseline() -> None:
    """Dovada ca testele de refuz de mai jos NU sunt vacue -- un round-trip GENUIN reuseste."""
    cfg = cfg44()
    prod = RangeSemanticProducerV44(cfg)
    bars = legs_bars(MACRO_LEGS)
    for b in bars[:40]:
        prod.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close, atr=1.0)
    snap = prod.snapshot_state()
    prod2 = RangeSemanticProducerV44(cfg)
    prod2.restore_state(snap)   # nu trebuie sa ridice nimic
    assert prod2.snapshot_state() == prod.snapshot_state()


def test_restore_state_refuses_missing_field() -> None:
    cfg = cfg44()
    prod = RangeSemanticProducerV44(cfg)
    for b in legs_bars(MACRO_LEGS)[:20]:
        prod.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close, atr=1.0)
    snap = prod.snapshot_state()
    del snap["registry"]
    prod2 = RangeSemanticProducerV44(cfg)
    pre = prod2.snapshot_state()
    raised = False
    try:
        prod2.restore_state(snap)
    except KeyError:
        raised = True
    assert raised
    assert prod2.snapshot_state() == pre


def test_restore_state_refuses_wrong_contract_version() -> None:
    cfg = cfg44()
    prod = RangeSemanticProducerV44(cfg)
    for b in legs_bars(MACRO_LEGS)[:20]:
        prod.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close, atr=1.0)
    snap = prod.snapshot_state()
    snap["contract_version"] = "range-hierarchical-v4.3"
    prod2 = RangeSemanticProducerV44(cfg)
    pre = prod2.snapshot_state()
    raised = False
    try:
        prod2.restore_state(snap)
    except ContractErrorV43:
        raised = True
    assert raised
    assert prod2.snapshot_state() == pre


def test_restore_state_refuses_wrong_config_id() -> None:
    cfg = cfg44()
    prod = RangeSemanticProducerV44(cfg)
    for b in legs_bars(MACRO_LEGS)[:20]:
        prod.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close, atr=1.0)
    snap = prod.snapshot_state()
    snap["config_id"] = "0" * 64
    prod2 = RangeSemanticProducerV44(cfg)
    pre = prod2.snapshot_state()
    raised = False
    try:
        prod2.restore_state(snap)
    except ContractErrorV43:
        raised = True
    assert raised
    assert prod2.snapshot_state() == pre


def test_restore_state_refuses_wrong_implementation_fingerprint() -> None:
    cfg = cfg44()
    prod = RangeSemanticProducerV44(cfg)
    for b in legs_bars(MACRO_LEGS)[:20]:
        prod.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close, atr=1.0)
    snap = prod.snapshot_state()
    snap["implementation_fingerprint"] = "NOT_THE_REAL_FINGERPRINT"
    prod2 = RangeSemanticProducerV44(cfg)
    pre = prod2.snapshot_state()
    raised = False
    try:
        prod2.restore_state(snap)
    except ContractErrorV43:
        raised = True
    assert raised
    assert prod2.snapshot_state() == pre


def test_restore_state_refuses_v43_snapshot_shape() -> None:
    """Un snapshot V4.3 real (fara campurile v44_*, fara `implementation_fingerprint`) trebuie refuzat
    fail-closed, nu acceptat partial/silentios."""
    from ve_n1_replay.range_semantic_v4_3 import RangeSemanticProducerV43
    prod43 = RangeSemanticProducerV43(cfg43())
    for b in legs_bars(MACRO_LEGS)[:20]:
        prod43.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close, atr=1.0)
    snap43 = prod43.snapshot_state()

    prod44 = RangeSemanticProducerV44(cfg44())
    pre = prod44.snapshot_state()
    raised = False
    try:
        prod44.restore_state(snap43)
    except (ContractErrorV43, KeyError):
        raised = True
    assert raised
    assert prod44.snapshot_state() == pre


def test_restore_state_refuses_wrong_type_fields() -> None:
    """Camp cu tip gresit (string in loc de dict pt. `registry`) -- trebuie refuzat, nu propagat silentios
    intr-o stare partial-corupta."""
    cfg = cfg44()
    prod = RangeSemanticProducerV44(cfg)
    for b in legs_bars(MACRO_LEGS)[:20]:
        prod.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close, atr=1.0)
    snap = prod.snapshot_state()
    snap["registry"] = "not_a_dict"
    prod2 = RangeSemanticProducerV44(cfg)
    pre = prod2.snapshot_state()
    raised = False
    try:
        prod2.restore_state(snap)
    except (TypeError, AttributeError, KeyError, ContractErrorV43):
        raised = True
    assert raised
    assert prod2.snapshot_state() == pre


# ═══════════════════════════════════ nivel motor -- `RangeSemanticEngineV44.restore` (compune N1) ═══════════════════════════════════

def test_engine_round_trip_succeeds_as_a_sanity_baseline() -> None:
    eng = _engine44()
    bars = legs_bars(MACRO_LEGS)
    for b in bars[:40]:
        eng.observe_closed_bar(b)
    snap = eng.snapshot()
    eng2 = _engine44()
    eng2.restore(snap)   # nu trebuie sa ridice nimic
    assert eng2.bars_observed == eng.bars_observed


def test_engine_refuses_foreign_snapshot_type() -> None:
    eng = _engine44()
    for b in legs_bars(MACRO_LEGS)[:20]:
        eng.observe_closed_bar(b)

    class _FakeForeignSnapshot:
        pass

    before = eng.bars_observed
    raised = False
    try:
        eng.restore(_FakeForeignSnapshot())
    except RangeSnapshotErrorV44:
        raised = True
    assert raised
    assert eng.bars_observed == before


def test_engine_refuses_v43_snapshot_object() -> None:
    """Un `RangeSnapshotV43` REAL (nu doar o forma falsa) trebuie refuzat de motorul V4.4 -- versiuni
    diferite, niciun downcast/upcast implicit."""
    eng43 = RangeSemanticEngineV43(range_config=cfg43(), acknowledge_construction_only=True, **KW)
    for b in legs_bars(MACRO_LEGS)[:20]:
        eng43.observe_closed_bar(b)
    snap43 = eng43.snapshot()
    assert isinstance(snap43, RangeSnapshotV43)

    eng44 = _engine44()
    for b in legs_bars(MACRO_LEGS)[:20]:
        eng44.observe_closed_bar(b)
    before = eng44.bars_observed
    raised = False
    try:
        eng44.restore(snap43)   # type: ignore[arg-type]
    except RangeSnapshotErrorV44:
        raised = True
    assert raised
    assert eng44.bars_observed == before


def test_engine_refuses_corrupted_range_state_engine_left_unchanged() -> None:
    eng = _engine44()
    for b in legs_bars(MACRO_LEGS)[:20]:
        eng.observe_closed_bar(b)
    snap = eng.snapshot()
    corrupted = _dc.replace(snap, range_state={"n": 5})
    before = eng.bars_observed
    raised = False
    try:
        eng.restore(corrupted)
    except RangeSnapshotErrorV44:
        raised = True
    assert raised
    assert eng.bars_observed == before, "restore esuat trebuie sa lase motorul complet NESCHIMBAT (atomic)"


def test_engine_refuses_mismatched_config_id_snapshot() -> None:
    eng_a = _engine44()
    for b in legs_bars(MACRO_LEGS)[:20]:
        eng_a.observe_closed_bar(b)
    snap = eng_a.snapshot()

    eng_b = RangeSemanticEngineV44(range_config=cfg44(), acknowledge_construction_only=True, **KW)
    tampered = _dc.replace(snap, config_id="0" * 64)
    before = eng_b.bars_observed
    raised = False
    try:
        eng_b.restore(tampered)
    except RangeSnapshotErrorV44:
        raised = True
    assert raised
    assert eng_b.bars_observed == before


def test_engine_construction_refuses_without_acknowledge_construction_only() -> None:
    from ve_n1_replay.range_semantic_v4_4 import ConfigNotRatifiedErrorV43
    raised = False
    try:
        RangeSemanticEngineV44(range_config=cfg44(), acknowledge_construction_only=False, **KW)
    except ConfigNotRatifiedErrorV43:
        raised = True
    assert raised


def test_engine_construction_refuses_mismatched_config_id() -> None:
    """Mandat §4: `V4_4_CONFIG_ID_MISMATCH` -- construirea insasi refuza daca `config_id()` nu se potriveste
    cu valoarea normativa (aici fortat printr-un camp modificat)."""
    bad_cfg = cfg44(GAP_MAX=cfg44().GAP_MAX + 5)
    raised = False
    try:
        RangeSemanticEngineV44(range_config=bad_cfg, acknowledge_construction_only=True, **KW)
    except ContractErrorV43:
        raised = True
    assert raised
