"""ORCHESTRATORUL DE LANȚ `run_tower_chain` (RT-TOWER-0007 + remediere ATR TOWER_CHAIN_ATR) — SINGURA suprafață
autorizată pentru traseul live/replay/shadow.

Impune STRUCTURAL legătura N2→N3→N4 (apelantul nu poate injecta n2_fingerprint/bias_available/identitatea N3) ȘI
calculează ATR INTERN din barele primite (apelantul nu poate furniza atr/n3_atr/n4_atr). ATR-ul e primitiva CANONICĂ
`market_state.atr14` (period 14, TR = max(h-l,|h-c₋₁|,|l-c₋₁|)) — NU un al doilea detector, NU ATR din AI Trader.

Convenția de timeframe (justificată din git, raportată înainte de implementare):
- N3 primește ATR M15 (`atr14(M15)`).
- N4 primește BANDA M15 1×ATR (`atr14(M15)[-1]`) — `zone_confirmation` măsoară progresul contra benzii M15
  (SPEC2 §3: „NU ATR M5"; `progress_reference="M15_band_1xATR"`, `market_bus.py` wire `atr=[m15_atr[-1]]*len(m5)`).
  A folosi ATR M5 pentru N4 ar schimba semantica modulului ratificat — INTERZIS.

Fail-closed pe fiecare nod: bare insuficiente/incomplete/neordonate/stale/NaN/Inf ⇒ ATR_UNAVAILABLE, nod indisponibil,
reason explicit, zero fallback, zero valoare implicită.
"""

from __future__ import annotations

import math
from typing import Any

from ._bootstrap import tower_module
from .canonical import canonical_hash
from .contracts import (AtrProvenance, ChainRequest, ChainResponse, N2Request, N2Response, N3Request, N3Response,
                        N4Request, N4Response, SUPPORTED_CHAIN_CONTRACTS)
from .fingerprint import event_fingerprint, same_event
from .n2 import run_n2
from .n3 import run_n3
from .n4 import run_n4
from .reason_codes import ReasonCode
from .version import (CHAIN_RESPONSE_CONTRACT_VERSION, TOWER_CHAIN_BINDING_VERSION, VENDORED_SOURCE_COMMITS,
                      VE_TOWER_VERSION)

_ATR_PERIOD: int = 14
_ATR_TR: str = "max(h-l,|h-c_prev|,|l-c_prev|)"


def _atr_prov(*, timeframe: str, as_of: int, last_bar_time: int, source_identity: str, value: float | None,
              available: bool, evaluation_index: int | None, consumed_atr_index: int | None,
              consumed_bar_timestamp: int | None) -> AtrProvenance:
    return AtrProvenance(
        source_module="market_state", source_commit=VENDORED_SOURCE_COMMITS["market_state"], function="atr14",
        timeframe=timeframe, period=_ATR_PERIOD, true_range_convention=_ATR_TR, as_of=as_of,
        last_closed_bar_time=last_bar_time, source_identity=source_identity, atr_value=value, available=available,
        reason_code="atr_ok" if available else ReasonCode.ATR_UNAVAILABLE.value, evaluation_index=evaluation_index,
        consumed_atr_index=consumed_atr_index, consumed_bar_timestamp=consumed_bar_timestamp)


def _atr_at(series: list[float], idx: int) -> float | None:
    """Valoarea ATR la un index (0<=idx<len), finită și >0, altfel None."""
    if 0 <= idx < len(series) and math.isfinite(series[idx]) and series[idx] > 0.0:
        return float(series[idx])
    return None


def _chain_fingerprint(req: ChainRequest, n2: N2Response | None, n3: N3Response | None, n4: N4Response | None,
                       n3_atr: AtrProvenance | None, n4_atr: AtrProvenance | None) -> str:
    return canonical_hash({
        "market_event_id": req.market_event_id,
        "configuration_fingerprint": req.configuration_fingerprint,
        "n2_output_fingerprint": n2.output_fingerprint if n2 else None,
        "n3_node_input_fingerprint": n3.node_input_fingerprint if n3 else None,
        "n3_event_fingerprint": n3.event_fingerprint if n3 else None,
        "n4_node_input_fingerprint": n4.node_input_fingerprint if n4 else None,
        "n4_event_fingerprint": n4.event_fingerprint if n4 else None,
        # identitatea ATR intră EXPLICIT în chain_fingerprint (pe lângă data_identity din node fingerprints)
        "n3_atr": [n3_atr.timeframe, n3_atr.atr_value, n3_atr.source_commit] if n3_atr else None,
        "n4_atr": [n4_atr.timeframe, n4_atr.atr_value, n4_atr.source_commit] if n4_atr else None,
        "strategy_id": req.strategy_id,
        "contracts": [req.expected_n2_contract, req.expected_n3_contract, req.expected_n4_contract],
        "chain_contract": req.contract_version,
        "artifact_version": VE_TOWER_VERSION,
    })


def _resp(req: ChainRequest, n2: N2Response | None, n3: N3Response | None, n4: N4Response | None,
          n3_atr: AtrProvenance | None, n4_atr: AtrProvenance | None, status: ReasonCode,
          terminal: str) -> ChainResponse:
    return ChainResponse(
        contract_version=CHAIN_RESPONSE_CONTRACT_VERSION, tower_version=VE_TOWER_VERSION,
        chain_binding_version=TOWER_CHAIN_BINDING_VERSION, market_event_id=req.market_event_id,
        correlation_id=req.correlation_id, configuration_fingerprint=req.configuration_fingerprint,
        n2=n2, n3=n3, n4=n4, n3_atr_provenance=n3_atr, n4_atr_provenance=n4_atr,
        chain_fingerprint=_chain_fingerprint(req, n2, n3, n4, n3_atr, n4_atr),
        chain_status=status.value, terminal_reason_code=terminal)


def run_tower_chain(req: ChainRequest) -> ChainResponse:
    """Rulează N2→N3→N4 INTERN, cu legătura și ATR-ul impuse în artefact. Determinist. Fail-closed."""
    if req.contract_version not in SUPPORTED_CHAIN_CONTRACTS:
        return _resp(req, None, None, None, None, None, ReasonCode.INCOMPATIBLE_CONTRACT,
                     ReasonCode.INCOMPATIBLE_CONTRACT.value)

    regime_available = any(s == "available" for s in req.regime_axes_status)
    ms: Any = tower_module("market_state")

    # ── N2 (H1) ──
    n2 = run_n2(N2Request(
        contract_version=req.expected_n2_contract, market_event_id=req.market_event_id, symbol=req.symbol,
        timeframe="H1", source_identity=req.h1_source_identity, open=req.h1_open, high=req.h1_high, low=req.h1_low,
        close=req.h1_close, time=req.h1_time, as_of=req.as_of, regime_axes_status=req.regime_axes_status,
        n1_fingerprint=req.n1_fingerprint, max_staleness_s=req.h1_max_staleness_s))
    if not n2.bias_available or n2.output_fingerprint is None:
        return _resp(req, n2, None, None, None, None, ReasonCode.N2_UNAVAILABLE, n2.reason_codes[0])

    # ── ATR M15 CANONIC (intern). Legat de REGULA RATIFICATĂ din zone_map: `i = n-1`, ATR consumat = `atr14[i-1]`
    # (RT-TOWER-0009). N4 folosește banda M15 = `atr14[-1]` (indexul n-1). NU hardcodat orb — derivat din i. ──
    m15_atr = ms.atr14(list(req.m15_high), list(req.m15_low), list(req.m15_close))
    n_m15 = len(req.m15_close)
    eval_i = n_m15 - 1                                    # indexul de evaluare al zone_map
    n3_consumed_idx = eval_i - 1                          # zone_map: atr14[i-1]
    n4_band_idx = n_m15 - 1                               # banda M15 = atr14[-1]
    m15_bar_t = req.m15_time[-1] if req.m15_time else req.as_of
    n3_val = _atr_at(m15_atr, n3_consumed_idx)            # ATR-ul EFECTIV consumat de N3
    band_val = _atr_at(m15_atr, n4_band_idx)              # banda M15 pentru N4
    n3_atr = _atr_prov(
        timeframe="M15", as_of=req.as_of, last_bar_time=m15_bar_t, source_identity=req.m15_source_identity,
        value=n3_val, available=n3_val is not None, evaluation_index=eval_i, consumed_atr_index=n3_consumed_idx,
        consumed_bar_timestamp=(req.m15_time[n3_consumed_idx] if 0 <= n3_consumed_idx < len(req.m15_time) else None))

    # ── N3 (M15): ATR-ul e canonicul `atr14(M15)`. `zone_map` îl calculează INTERN din ACELEAȘI bare M15 (verificat:
    # chain m15_atr == atr14 intern). Trecem atr=None ca să nu dublăm seria (warmup-ul NaN al atr14 ar fi refuzat de
    # data_identity); proveniența înregistrează explicit ATR-ul M15 canonic. ──
    n3 = run_n3(N3Request(
        contract_version=req.expected_n3_contract, market_event_id=req.market_event_id, symbol=req.symbol,
        timeframe="M15", source_identity=req.m15_source_identity, open=req.m15_open, high=req.m15_high,
        low=req.m15_low, close=req.m15_close, time=req.m15_time, as_of=req.as_of, regime_available=regime_available,
        bias_available=n2.bias_available, n1_fingerprint=req.n1_fingerprint, n2_fingerprint=n2.output_fingerprint,
        atr=None, max_staleness_s=req.m15_max_staleness_s))
    if not n3.market_map_available:
        return _resp(req, n2, n3, None, n3_atr, None, ReasonCode.N3_UNAVAILABLE, n3.reason_codes[0])
    if not n3.market_map:
        return _resp(req, n2, n3, None, n3_atr, None, ReasonCode.N4_UNAVAILABLE, ReasonCode.ZONE_UNAVAILABLE.value)

    # ── banda M15 1×ATR pentru N4 (SPEC2 §3) = atr14[-1]. Bandă nefinită ⇒ ATR_UNAVAILABLE, fără a chema run_n4 cu NaN ──
    n4_atr = _atr_prov(
        timeframe="M15_band_1xATR", as_of=req.as_of, last_bar_time=m15_bar_t,
        source_identity=req.m15_source_identity, value=band_val, available=band_val is not None,
        evaluation_index=eval_i, consumed_atr_index=n4_band_idx,
        consumed_bar_timestamp=(req.m15_time[n4_band_idx] if 0 <= n4_band_idx < len(req.m15_time) else None))
    if band_val is None:
        return _resp(req, n2, n3, None, n3_atr, n4_atr, ReasonCode.N4_UNAVAILABLE, ReasonCode.ATR_UNAVAILABLE.value)

    # ── N4 (M5) — LEGAT de răspunsul N3 real (rank-1), cu banda M15 ca reper de ATR ──
    lvl = n3.market_map[0]
    n4 = run_n4(N4Request(
        contract_version=req.expected_n4_contract, market_event_id=req.market_event_id, symbol=req.symbol,
        timeframe="M5", source_identity=req.m5_source_identity, high=req.m5_high, low=req.m5_low, close=req.m5_close,
        time=req.m5_time, level=lvl.price_anchor, side=req.side, as_of=req.as_of, strategy_id=req.strategy_id,
        strategy_version=req.strategy_version, regime_available=regime_available, bias_available=n2.bias_available,
        n1_fingerprint=req.n1_fingerprint, n2_fingerprint=n2.output_fingerprint,
        n3_market_event_id=n3.market_event_id, n3_event_fingerprint=n3.event_fingerprint,
        n3_node_input_fingerprint=n3.node_input_fingerprint or "", n3_market_map_available=n3.market_map_available,
        n3_level_zone_id=lvl.zone_id, n3_level_provenance=tuple((p.family, p.instance_count) for p in lvl.provenance),
        w=3, atr=tuple([band_val] * len(req.m5_close)), max_staleness_s=req.m5_max_staleness_s))

    efp = event_fingerprint(market_event_id=req.market_event_id, symbol=req.symbol, as_of=req.as_of)
    ids_ok = (n2.event_fingerprint == efp and n3.event_fingerprint == efp and n4.event_fingerprint == efp
              and n2.market_event_id == n3.market_event_id == n4.market_event_id == req.market_event_id)
    if not ids_ok or not same_event(n2.event_fingerprint, n2.market_event_id, n3.event_fingerprint, n3.market_event_id):
        return _resp(req, n2, n3, n4, n3_atr, n4_atr, ReasonCode.CHAIN_IDENTITY_MISMATCH,
                     ReasonCode.CHAIN_IDENTITY_MISMATCH.value)

    if not n4.confirmation_available:
        return _resp(req, n2, n3, n4, n3_atr, n4_atr, ReasonCode.N4_UNAVAILABLE, n4.reason_codes[0])
    return _resp(req, n2, n3, n4, n3_atr, n4_atr, ReasonCode.OK_CHAIN, ReasonCode.OK_CHAIN.value)
