"""V4.4 causality invariants (mandat §8, §14): confirmation-timing invariance across 96/288/480-bar
containers with an identical causal prefix and DIFFERENT futures, plus NO_LOOKAHEAD / PREFIX_INVARIANCE /
CHUNK_INVARIANCE / DETERMINISTIC_REPLAY / SNAPSHOT_RESTART_INVARIANCE / CONFIG_ID_SENSITIVITY /
IMPLEMENTATION_ID_SENSITIVITY."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_range_semantic_v4_3 import legs_bars   # noqa: E402

from ve_n1_replay.range_semantic_v4_3 import ContractErrorV43   # noqa: E402
from ve_n1_replay.range_semantic_v4_4 import ConfigV44, RangeSemanticProducerV44   # noqa: E402


def cfg44(**kw: Any) -> ConfigV44:
    return ConfigV44(**kw)


PREFIX_LEGS: list[tuple[float, int]] = [
    (100, 0), (120, 6), (100, 6), (120, 6), (100, 6), (120, 6), (100, 6),
    (108, 5), (112, 5), (108, 5), (112, 5), (108, 5)]
PREFIX_BARS = legs_bars(PREFIX_LEGS)   # 61 bare, confirmed known -- reused unmodified as a shared prefix


def _run(bars: list[Any], atr: float = 1.0) -> list[dict[str, Any]]:
    cfg = cfg44()
    prod = RangeSemanticProducerV44(cfg)
    out = []
    for b in bars:
        res, evs = prod.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close, atr=atr)
        out.append({"macro_id": res.macro_id, "macro_reason": res.macro_reason, "macro_state": res.macro_state,
                   "macro_weakening_reason": res.macro_weakening_reason,
                   "internal_reason": res.internal_reason, "internal_state": res.internal_state,
                   "events": tuple(e.kind for e in evs)})
    return out


def _container(total_len: int, tail_seed: float) -> list[Any]:
    remaining = total_len - len(PREFIX_BARS)
    assert remaining > 0
    tail_legs: list[tuple[float, int]] = [(PREFIX_LEGS[-1][0], 0)]
    base = PREFIX_LEGS[-1][0]
    n = 0
    k = 0
    while n < remaining:
        step = min(6, remaining - n)
        base += tail_seed if k % 2 == 0 else -tail_seed * 0.6
        tail_legs.append((base, step))
        n += step
        k += 1
    tail_bars = legs_bars(tail_legs, start=len(PREFIX_BARS))
    return PREFIX_BARS + tail_bars[:remaining]


def test_confirmation_timing_invariant_across_96_288_480_bar_containers() -> None:
    """Mandat §8: prefixul cauzal identic, cu VIITOARE diferite (tail-uri diferite, semanate diferit), imbibat
    in containere de 96/288/480 -- cronologia PRIN prefixul comun trebuie sa fie identica, indiferent de ce
    urmeaza."""
    c96 = _container(96, tail_seed=3.0)
    c288 = _container(288, tail_seed=11.0)
    c480 = _container(480, tail_seed=27.0)
    assert len(c96) == 96 and len(c288) == 288 and len(c480) == 480
    for i in range(len(PREFIX_BARS)):
        assert (c96[i].ts_close, c96[i].open, c96[i].high, c96[i].low, c96[i].close) == \
               (c288[i].ts_close, c288[i].open, c288[i].high, c288[i].low, c288[i].close) == \
               (c480[i].ts_close, c480[i].open, c480[i].high, c480[i].low, c480[i].close)

    out96 = _run(c96)
    out288 = _run(c288)
    out480 = _run(c480)

    prefix_len = len(PREFIX_BARS)
    for i in range(prefix_len):
        assert out96[i] == out288[i] == out480[i], f"diverge la bara {i} in prefixul comun"

    # dovada ca fixture-ul chiar exercita ceva nebanal in prefix (nu doar BETWEEN_EPISODES peste tot)
    prefix_reasons = {r["macro_reason"] for r in out96[:prefix_len]}
    assert "OK_RANGE_MACRO" in prefix_reasons or "TOO_SHORT_MACRO" in prefix_reasons

    # si dovada ca tail-urile CHIAR difera dupa prefix (altfel testul de mai sus ar fi vacuu)
    tails_differ = any(out96[prefix_len + k] != out288[prefix_len + k]
                       for k in range(min(20, 96 - prefix_len, 288 - prefix_len)))
    assert tails_differ


def test_no_lookahead_truncated_replay_matches_full_replay_up_to_truncation_point() -> None:
    """NO_LOOKAHEAD: opreste replay-ul la jumatate -- rezultatele PANA ACOLO trebuie sa fie identice cu
    rularea completa (bara N nu poate fi afectata de bare > N, care nici nu existau inca la momentul N)."""
    bars = _container(200, tail_seed=5.0)
    full = _run(bars)
    half = _run(bars[:100])
    for i in range(100):
        assert full[i] == half[i]


def test_prefix_invariance_growing_the_container_never_rewrites_earlier_bars() -> None:
    """PREFIX_INVARIANCE: pt. fiecare N intre 10 si 90 (pas 10), primele N bare produc EXACT acelasi rezultat
    indiferent de lungimea totala a containerului."""
    bars = _container(150, tail_seed=7.0)
    reference = _run(bars)
    for n in (10, 20, 30, 40, 50, 60, 70, 80, 90):
        partial = _run(bars[:n])
        assert partial == reference[:n], f"prefixul de {n} bare difera de referinta"


def test_chunk_invariance_snapshot_restart_at_arbitrary_points_matches_continuous_replay() -> None:
    """CHUNK_INVARIANCE / SNAPSHOT_RESTART_INVARIANCE: sparge replay-ul in 3 bucati la puncte ARBITRARE
    (nu doar la granite convenabile), cu snapshot/restore intre ele -- rezultatul trebuie sa fie identic cu
    rularea continua, bara cu bara."""
    bars = _container(180, tail_seed=9.0)
    continuous = _run(bars)

    cfg = cfg44()
    prod = RangeSemanticProducerV44(cfg)
    chunked: list[dict[str, Any]] = []
    split_points = [37, 101, 158, len(bars)]
    start = 0
    for end in split_points:
        for b in bars[start:end]:
            res, evs = prod.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close, atr=1.0)
            chunked.append({"macro_id": res.macro_id, "macro_reason": res.macro_reason,
                           "macro_state": res.macro_state, "macro_weakening_reason": res.macro_weakening_reason,
                           "internal_reason": res.internal_reason, "internal_state": res.internal_state,
                           "events": tuple(e.kind for e in evs)})
        if end < len(bars):
            snap = prod.snapshot_state()
            prod = RangeSemanticProducerV44(cfg)
            prod.restore_state(snap)
        start = end

    assert chunked == continuous


def test_deterministic_replay_two_independent_runs_produce_identical_output() -> None:
    bars = _container(120, tail_seed=4.0)
    run_a = _run(bars)
    run_b = _run(bars)
    assert run_a == run_b


def test_config_id_sensitivity_snapshot_refuses_mismatched_config() -> None:
    """CONFIG_ID_SENSITIVITY: un snapshot produs sub o configuratie NU poate fi restaurat sub alta -- fail
    closed, refuzat explicit, nicio mutatie partiala de stare."""
    bars = _container(80, tail_seed=3.0)
    cfg_a = cfg44()
    prod_a = RangeSemanticProducerV44(cfg_a)
    for b in bars[:40]:
        prod_a.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close, atr=1.0)
    snap = prod_a.snapshot_state()

    cfg_b = cfg44(GAP_MAX=cfg_a.GAP_MAX + 1)   # orice camp -> config_id() diferit
    assert cfg_b.config_id() != cfg_a.config_id()
    prod_b = RangeSemanticProducerV44(cfg_b)
    pre_state = prod_b.snapshot_state()
    try:
        prod_b.restore_state(snap)
        raised = False
    except ContractErrorV43:
        raised = True
    assert raised
    assert prod_b.snapshot_state() == pre_state   # nicio mutatie partiala dupa refuz


def test_implementation_id_sensitivity_snapshot_refuses_mismatched_fingerprint() -> None:
    """IMPLEMENTATION_ID_SENSITIVITY: un snapshot cu o amprenta de implementare diferita e refuzat fail-closed,
    chiar daca `contract_version`/`config_id` se potrivesc."""
    bars = _container(70, tail_seed=2.0)
    cfg = cfg44()
    prod = RangeSemanticProducerV44(cfg)
    for b in bars[:30]:
        prod.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close, atr=1.0)
    snap = prod.snapshot_state()
    tampered = dict(snap)
    tampered["implementation_fingerprint"] = "TAMPERED_FINGERPRINT_VALUE"

    prod2 = RangeSemanticProducerV44(cfg)
    pre_state = prod2.snapshot_state()
    try:
        prod2.restore_state(tampered)
        raised = False
    except ContractErrorV43:
        raised = True
    assert raised
    assert prod2.snapshot_state() == pre_state
