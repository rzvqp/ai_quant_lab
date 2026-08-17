"""Orchestratorul `run_tower_chain` (RT-TOWER-0007): legătura N2→N3→N4 impusă STRUCTURAL în artefact. Testul
decisiv: o valoare inventată de apelant NU poate ajunge ca n2_fingerprint în run_n3 — imposibil structural + respins."""

from __future__ import annotations

import dataclasses
import os
import sys

import pytest

_PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PKG not in sys.path:
    sys.path.insert(0, _PKG)

import ve_tower as vt  # noqa: E402
from ve_tower import (  # noqa: E402
    ChainRequest, CHAIN_REQUEST_CONTRACT_VERSION, N2_CONTRACT_VERSION, N3_CONTRACT_VERSION, N4_CONTRACT_VERSION,
    parse_chain_request, run_tower_chain,
)

T0 = 1_600_000_000; AS_OF = T0 + 50_000_000


def _h1(bump: float = 0.0, close_override: tuple[float, ...] | None = None) -> tuple[tuple[float, ...], ...]:
    o = []; h = []; l = []; c = []; t = []
    for j in range(400):
        b = 100.0 + j * 0.5 + bump
        o.append(b); h.append(b + 0.8); l.append(b - 0.8); c.append(b + 0.3); t.append(T0 + j * 3600)
    if close_override is not None:
        c = list(close_override)
    return tuple(o), tuple(h), tuple(l), tuple(c), tuple(t)


def _m15() -> tuple[tuple[float, ...], ...]:
    o = []; h = []; l = []; c = []; t = []
    for j in range(40):
        b = 100.0 + (1.0 if (j // 5) % 2 else -1.0)
        o.append(b); h.append(b + 1.5); l.append(b - 1.5); c.append(b + 0.3); t.append(T0 + j * 900)
    return tuple(o), tuple(h), tuple(l), tuple(c), tuple(t)


def _m5(level: float = 102.5) -> tuple[tuple[float, ...], ...]:
    # bare M5 centrate pe `level`: 16 sub-nivel (ca atr14 la bara de hit să aibă ≥14 istoric), penetrare, fereastră, post
    rows = [(level - 0.5, level - 1.5, level - 1.0)] * 16 + [(level + 1.0, level - 1.0, level + 0.5)] + \
           [(level + 1.2, level + 0.1, level + 0.8)] * 3 + [(level + 1.1, level + 0.0, level + 0.7)] * 6
    h = tuple(r[0] for r in rows); l = tuple(r[1] for r in rows); c = tuple(r[2] for r in rows)
    t = tuple(T0 + i * 300 for i in range(len(rows)))
    return h, l, c, t


def _req(**over: object) -> ChainRequest:
    h1o, h1h, h1l, h1c, h1t = _h1(close_override=over.pop("h1_close", None))  # type: ignore[arg-type]
    m15o, m15h, m15l, m15c, m15t = _m15()
    m5h, m5l, m5c, m5t = _m5()
    base: dict[str, object] = dict(
        contract_version=CHAIN_REQUEST_CONTRACT_VERSION, market_event_id="ev1", correlation_id="corr1",
        symbol="XAUUSD", as_of=AS_OF, configuration_fingerprint="cfg1", n1_fingerprint="n1fp",
        regime_axes_status=("available", "available", "available"),
        h1_open=h1o, h1_high=h1h, h1_low=h1l, h1_close=h1c, h1_time=h1t,
        m15_open=m15o, m15_high=m15h, m15_low=m15l, m15_close=m15c, m15_time=m15t,
        m5_high=m5h, m5_low=m5l, m5_close=m5c, m5_time=m5t,
        h1_source_identity="h1feed", m15_source_identity="m15feed", m5_source_identity="m5feed",
        strategy_id="S1", strategy_version="v1", side=1,
        expected_n2_contract=N2_CONTRACT_VERSION, expected_n3_contract=N3_CONTRACT_VERSION,
        expected_n4_contract=N4_CONTRACT_VERSION)
    base.update(over)
    return ChainRequest(**base)  # type: ignore[arg-type]


def _req_ok() -> ChainRequest:
    """Rulează o dată pentru a descoperi ancora N3 rank-1, apoi centrează M5 pe ea ⇒ OK_CHAIN determinist."""
    probe = run_tower_chain(_req())
    assert probe.n3 is not None and probe.n3.market_map
    anchor = probe.n3.market_map[0].price_anchor
    m5h, m5l, m5c, m5t = _m5(anchor)
    return _req(m5_high=m5h, m5_low=m5l, m5_close=m5c, m5_time=m5t)


# ═══ testul DECISIV + binding ═══
def test_caller_cannot_supply_n2_fingerprint_structural() -> None:
    assert "n2_fingerprint" not in {f.name for f in dataclasses.fields(ChainRequest)}   # nu există câmp
    assert "bias_available" not in {f.name for f in dataclasses.fields(ChainRequest)}


def test_parse_rejects_unknown_field_n2_fingerprint() -> None:
    good = {f.name: getattr(_req(), f.name) for f in dataclasses.fields(ChainRequest)}
    with pytest.raises(vt.UnknownRequestFieldError):
        parse_chain_request({**good, "n2_fingerprint": "deadbeefdeadbeef"})
    with pytest.raises(vt.UnknownRequestFieldError):
        parse_chain_request({**good, "bias_available": True})


def test_n3_uses_exactly_n2_output_fingerprint() -> None:
    r = run_tower_chain(_req())
    assert r.n2 is not None and r.n3 is not None and r.n2.output_fingerprint
    # recompunem N3 direct cu fingerprintul N2 REAL → același node_input_fingerprint ca în lanț (dovada legării)
    direct = vt.run_n3(vt.N3Request(
        contract_version=N3_CONTRACT_VERSION, market_event_id="ev1", symbol="XAUUSD", timeframe="M15",
        source_identity="m15feed", open=_m15()[0], high=_m15()[1], low=_m15()[2], close=_m15()[3], time=_m15()[4],
        as_of=AS_OF, regime_available=True, bias_available=True, n1_fingerprint="n1fp",
        n2_fingerprint=r.n2.output_fingerprint, atr=None))
    assert direct.node_input_fingerprint == r.n3.node_input_fingerprint
    # un fingerprint N2 INVENTAT dă alt node_fp — deci lanțul NU a folosit o valoare inventată
    forged = vt.run_n3(vt.N3Request(
        contract_version=N3_CONTRACT_VERSION, market_event_id="ev1", symbol="XAUUSD", timeframe="M15",
        source_identity="m15feed", open=_m15()[0], high=_m15()[1], low=_m15()[2], close=_m15()[3], time=_m15()[4],
        as_of=AS_OF, regime_available=True, bias_available=True, n1_fingerprint="n1fp",
        n2_fingerprint="deadbeefdeadbeef", atr=None))
    assert forged.node_input_fingerprint != r.n3.node_input_fingerprint


# ═══ lanț complet + cascadă ═══
def test_full_chain_ok() -> None:
    r = run_tower_chain(_req_ok())
    assert r.chain_status == "ok_chain" and r.terminal_reason_code == "ok_chain"
    assert r.n2.bias_available and r.n3.market_map_available and r.n4.confirmation_available   # type: ignore[union-attr]
    assert r.chain_binding_version == "tower-chain-binding-v1" and r.tower_version == vt.VE_TOWER_VERSION


# ═══ ATR (remediere TOWER_CHAIN_ATR) ═══
def test_chain_computes_atr_internally_and_n4_not_atr_unavailable() -> None:
    # DECISIV: pe fixture valid, lanțul ajunge la N4 FĂRĂ atr_unavailable (ATR real ajunge la N4)
    r = run_tower_chain(_req_ok())
    assert r.n4 is not None and r.n4.reason_codes != ("atr_unavailable",)
    assert r.n4.confirmation_available   # date suficiente ⇒ confirmarea depinde de date, nu de lipsa ATR


def test_atr_provenance_recorded_m15_for_n3_and_band_for_n4() -> None:
    r = run_tower_chain(_req_ok())
    assert r.n3_atr_provenance is not None and r.n3_atr_provenance.timeframe == "M15"
    assert r.n3_atr_provenance.source_module == "market_state" and r.n3_atr_provenance.period == 14
    assert r.n4_atr_provenance is not None and r.n4_atr_provenance.timeframe == "M15_band_1xATR"   # SPEC2 §3, NU M5
    assert r.n4_atr_provenance.available and r.n4_atr_provenance.atr_value is not None


def test_caller_cannot_supply_atr_fields() -> None:
    fields = {f.name for f in dataclasses.fields(ChainRequest)}
    assert fields.isdisjoint({"atr", "n3_atr", "n4_atr", "atr_fingerprint"})
    good = {f.name: getattr(_req(), f.name) for f in dataclasses.fields(ChainRequest)}
    for bad in ("atr", "n3_atr", "n4_atr"):
        with pytest.raises(vt.UnknownRequestFieldError):
            parse_chain_request({**good, bad: [1.0, 2.0]})


def test_m15_insufficient_atr_unavailable() -> None:
    # M15 prea scurt (<15) ⇒ atr14 NaN ⇒ N3 indisponibil (atr canonic lipsă)
    o = tuple([100.0] * 10); h = tuple([101.0] * 10); l = tuple([99.0] * 10); c = tuple([100.0] * 10)
    t = tuple(T0 + j * 900 for j in range(10))
    r = run_tower_chain(_req(m15_open=o, m15_high=h, m15_low=l, m15_close=c, m15_time=t))
    assert r.chain_status in ("n3_unavailable", "n4_unavailable")
    assert r.n3 is not None and not r.n3.market_map_available


def _m15_amp(amp: float) -> tuple[tuple[float, ...], ...]:
    o = []; h = []; l = []; c = []; t = []
    for j in range(40):
        b = 100.0 + (amp if (j // 5) % 2 else -amp)
        o.append(b); h.append(b + 1.5 * amp); l.append(b - 1.5 * amp); c.append(b + 0.3 * amp); t.append(T0 + j * 900)
    return tuple(o), tuple(h), tuple(l), tuple(c), tuple(t)


def _req_amp_ok(amp: float) -> ChainRequest:
    m15o, m15h, m15l, m15c, m15t = _m15_amp(amp)
    probe = run_tower_chain(_req(m15_open=m15o, m15_high=m15h, m15_low=m15l, m15_close=m15c, m15_time=m15t))
    assert probe.n3 is not None and probe.n3.market_map
    anchor = probe.n3.market_map[0].price_anchor
    m5h, m5l, m5c, m5t = _m5(anchor)
    return _req(m15_open=m15o, m15_high=m15h, m15_low=m15l, m15_close=m15c, m15_time=m15t,
                m5_high=m5h, m5_low=m5l, m5_close=m5c, m5_time=m5t)


def test_n3_provenance_equals_atr_consumed_by_zone_map_three_fixtures() -> None:
    # DECISIV (RT-TOWER-0009): atr_value = ATR-ul EFECTIV consumat de zone_map = level.band / band_mult (0.25).
    # Prinde vechiul bug (provenance = atr14[-1] = banda N4) vs consumed (atr14[i-1]).
    for amp in (1.0, 1.7, 2.3):                                       # ATR variabil
        r = run_tower_chain(_req_amp_ok(amp))
        assert r.n3 is not None and r.n3.market_map and r.n3_atr_provenance is not None
        lvl = r.n3.market_map[0]
        consumed = lvl.band / 0.25                                    # zone_map: band = 0.25 × atr14[i-1]
        assert r.n3_atr_provenance.atr_value == pytest.approx(consumed, abs=1e-9), amp
        # vechiul bug ar fi raportat banda N4 (atr14[-1]); acum diferă de N4 prin construcție
        assert r.n4_atr_provenance is not None
        assert r.n3_atr_provenance.atr_value != r.n4_atr_provenance.atr_value


def test_provenance_indices_bound_to_ratified_rule() -> None:
    r = run_tower_chain(_req_ok())
    p3 = r.n3_atr_provenance; p4 = r.n4_atr_provenance
    assert p3 is not None and p4 is not None
    assert p3.evaluation_index == 39 and p3.consumed_atr_index == 38          # i=n-1, i-1
    assert p4.consumed_atr_index == 39                                        # banda = atr14[-1]
    assert p3.consumed_bar_timestamp == T0 + 38 * 900 and p4.consumed_bar_timestamp == T0 + 39 * 900


def test_n4_band_and_decision_unchanged_regression() -> None:
    # regresie: banda N4 rămâne atr14(M15)[-1] și confirmarea funcționează (decizia neschimbată vs 0.5.1)
    r = run_tower_chain(_req_ok())
    ms = __import__("ve_tower").tower_module("market_state")
    ok = _req_ok()
    m15_atr = ms.atr14(list(ok.m15_high), list(ok.m15_low), list(ok.m15_close))
    assert r.n4_atr_provenance.atr_value == pytest.approx(m15_atr[-1], abs=1e-9)   # banda neschimbată
    assert r.n4.confirmation_available and r.chain_status == "ok_chain"            # decizia neschimbată


def test_chain_fingerprint_includes_atr_identity() -> None:
    base = run_tower_chain(_req_ok())
    # schimbă barele M15 (deci și ATR-ul M15/banda) ⇒ chain_fingerprint diferit
    o, h, l, c, t = _h1()  # placeholder to reuse structure
    okreq = _req_ok()
    m15c2 = tuple(list(okreq.m15_close[:20]) + [okreq.m15_close[20] + 0.5] + list(okreq.m15_close[21:]))
    mut = dataclasses.replace(okreq, m15_close=m15c2)
    assert run_tower_chain(mut).chain_fingerprint != base.chain_fingerprint


def test_cascade_n2_unavailable() -> None:
    r = run_tower_chain(_req(regime_axes_status=("unavailable", "unavailable", "unavailable")))
    assert r.chain_status == "n2_unavailable" and r.n3 is None and r.n4 is None
    assert r.terminal_reason_code == "cascade_regime_all_axes_unavailable"


def test_cascade_n3_unavailable_stale_m15() -> None:
    r = run_tower_chain(_req(m15_max_staleness_s=1))          # M15 stale ⇒ N3 indisponibil
    assert r.chain_status == "n3_unavailable" and r.n4 is None and r.n2.bias_available   # type: ignore[union-attr]


def test_no_default_long_on_cascade() -> None:
    r = run_tower_chain(_req(regime_axes_status=("unavailable", "unavailable", "unavailable")))
    assert r.n2 is not None and r.n2.factors == () and r.n2.output_fingerprint is None    # NU un LONG fabricat


# ═══ refuzuri de identitate / date ═══
def test_incompatible_chain_contract_fail_closed() -> None:
    r = run_tower_chain(_req(contract_version="tower-chain-request-vX"))
    assert r.chain_status == "incompatible_contract"


def test_nan_in_h1_refused() -> None:
    o, h, l, c, t = _h1()
    r = run_tower_chain(_req(h1_close=tuple(list(c[:-1]) + [float("nan")])))
    assert r.chain_status == "n2_unavailable" and r.n2.reason_codes == ("non_finite_value",)   # type: ignore[union-attr]


def test_missing_source_h1_refused() -> None:
    r = run_tower_chain(_req(h1_source_identity=""))
    assert r.chain_status == "n2_unavailable" and r.n2.reason_codes == ("source_identity_missing",)  # type: ignore[union-attr]


# ═══ chain_fingerprint + determinism ═══
def test_chain_fingerprint_deterministic() -> None:
    assert run_tower_chain(_req()).chain_fingerprint == run_tower_chain(_req()).chain_fingerprint


def test_chain_fingerprint_changes_on_identity_change() -> None:
    base = run_tower_chain(_req()).chain_fingerprint
    assert run_tower_chain(_req(configuration_fingerprint="cfg2")).chain_fingerprint != base
    assert run_tower_chain(_req(market_event_id="ev2")).chain_fingerprint != base
    assert run_tower_chain(_req(strategy_id="S2")).chain_fingerprint != base


def test_chain_fingerprint_changes_on_bars_change() -> None:
    base = run_tower_chain(_req()).chain_fingerprint
    o, h, l, c, t = _h1()
    c2 = tuple(list(c[:200]) + [c[200] + 0.01] + list(c[201:]))
    assert run_tower_chain(_req(h1_close=c2)).chain_fingerprint != base


# ═══ producția folosește DOAR orchestratorul ═══
def test_production_entrypoint_is_chain_only() -> None:
    assert vt.PRODUCTION_ENTRYPOINT == "run_tower_chain"
    assert set(vt.UNBOUND_DIRECT_API) == {"run_n2", "run_n3", "run_n4"}
    # ChainRequest nu poate transporta un N3Response / n2_fingerprint / output_fingerprint
    names = {f.name for f in dataclasses.fields(ChainRequest)}
    assert names.isdisjoint({"n2_fingerprint", "bias_available", "n3_response", "output_fingerprint", "n2_response"})


def test_no_forbidden_imports_in_tower() -> None:
    import re
    root = os.path.join(_PKG, "ve_tower")
    forbidden = ("market_intelligence", "ai_trader", "risk_manager", "execution_engine", "broker",
                 "risk", "execution")
    # verifică STATEMENT-uri de import, nu mențiuni în comentarii/docstring
    imp = re.compile(r"^\s*(?:import|from)\s+([a-zA-Z_][\w.]*)", re.M)
    for dirpath, _dirs, files in os.walk(root):
        for fn in files:
            if fn.endswith(".py"):
                src = open(os.path.join(dirpath, fn), encoding="utf-8").read()
                for mod in imp.findall(src):
                    top = mod.split(".")[0]
                    assert top not in forbidden, f"{fn} importă modul interzis: {mod}"
