"""ORCHESTRATORUL DE LANȚ `run_tower_chain` (RT-TOWER-0007) — SINGURA suprafață autorizată pentru traseul
live/replay/shadow.

Impune STRUCTURAL legătura N2→N3→N4: rulează cele trei noduri INTERN, în aceeași cursă, și obține `n2_fingerprint`,
`bias_available`, identitatea N3 EXCLUSIV din rezultatele funcțiilor executate. Apelantul dă DOAR date primare +
rezultate N1 oficiale — nu poate injecta `n2_fingerprint` (nu există câmp; `parse_chain_request` respinge orice câmp
necunoscut). `run_n3`/`run_n4` rămân UNBOUND_DIRECT_API (compat/research), INTERZISE pe calea de producție.

Cascadă fail-closed: N2 indisponibil ⇒ N3/N4 nu rulează ca disponibile (N2_UNAVAILABLE); N3 indisponibil ⇒ N4 nu
confirmă (N3_UNAVAILABLE); N4 indisponibil ⇒ N4_UNAVAILABLE. Orice mismatch de identitate ⇒ CHAIN_IDENTITY_MISMATCH.
Fără valori fabricate, fără default LONG.
"""

from __future__ import annotations

from .canonical import canonical_hash
from .contracts import (ChainRequest, ChainResponse, N2Request, N2Response, N3Request, N3Response, N4Request,
                        N4Response, SUPPORTED_CHAIN_CONTRACTS)
from .fingerprint import event_fingerprint, same_event
from .n2 import run_n2
from .n3 import run_n3
from .n4 import run_n4
from .reason_codes import ReasonCode
from .version import (CHAIN_RESPONSE_CONTRACT_VERSION, TOWER_CHAIN_BINDING_VERSION, VE_TOWER_VERSION)


def _chain_fingerprint(req: ChainRequest, n2: N2Response | None, n3: N3Response | None,
                       n4: N4Response | None) -> str:
    """Amprenta de lanț — include cel puțin: event id, config fp, N2 output_fingerprint, N3 node/event identity,
    N4 node/event identity, strategy_id, versiunile de contract, versiunea artefactului. Se schimbă la orice
    schimbare de identitate per nod."""
    return canonical_hash({
        "market_event_id": req.market_event_id,
        "configuration_fingerprint": req.configuration_fingerprint,
        "n2_output_fingerprint": n2.output_fingerprint if n2 else None,
        "n3_node_input_fingerprint": n3.node_input_fingerprint if n3 else None,
        "n3_event_fingerprint": n3.event_fingerprint if n3 else None,
        "n4_node_input_fingerprint": n4.node_input_fingerprint if n4 else None,
        "n4_event_fingerprint": n4.event_fingerprint if n4 else None,
        "strategy_id": req.strategy_id,
        "contracts": [req.expected_n2_contract, req.expected_n3_contract, req.expected_n4_contract],
        "chain_contract": req.contract_version,
        "artifact_version": VE_TOWER_VERSION,
    })


def _resp(req: ChainRequest, n2: N2Response | None, n3: N3Response | None, n4: N4Response | None,
          status: ReasonCode, terminal: str) -> ChainResponse:
    return ChainResponse(
        contract_version=CHAIN_RESPONSE_CONTRACT_VERSION, tower_version=VE_TOWER_VERSION,
        chain_binding_version=TOWER_CHAIN_BINDING_VERSION, market_event_id=req.market_event_id,
        correlation_id=req.correlation_id, configuration_fingerprint=req.configuration_fingerprint,
        n2=n2, n3=n3, n4=n4, chain_fingerprint=_chain_fingerprint(req, n2, n3, n4),
        chain_status=status.value, terminal_reason_code=terminal)


def run_tower_chain(req: ChainRequest) -> ChainResponse:
    """Rulează N2→N3→N4 INTERN, cu legătura impusă în artefact. Determinist. Fail-closed pe orice cale de eșec."""
    if req.contract_version not in SUPPORTED_CHAIN_CONTRACTS:
        return _resp(req, None, None, None, ReasonCode.INCOMPATIBLE_CONTRACT,
                     ReasonCode.INCOMPATIBLE_CONTRACT.value)

    regime_available = any(s == "available" for s in req.regime_axes_status)

    # ── N2 (H1) ──
    n2 = run_n2(N2Request(
        contract_version=req.expected_n2_contract, market_event_id=req.market_event_id, symbol=req.symbol,
        timeframe="H1", source_identity=req.h1_source_identity, open=req.h1_open, high=req.h1_high, low=req.h1_low,
        close=req.h1_close, time=req.h1_time, as_of=req.as_of, regime_axes_status=req.regime_axes_status,
        n1_fingerprint=req.n1_fingerprint, max_staleness_s=req.h1_max_staleness_s))
    if not n2.bias_available or n2.output_fingerprint is None:
        return _resp(req, n2, None, None, ReasonCode.N2_UNAVAILABLE, n2.reason_codes[0])

    # ── N3 (M15) — primește fingerprintul N2 REAL, obținut din rezultatul de mai sus ──
    n3 = run_n3(N3Request(
        contract_version=req.expected_n3_contract, market_event_id=req.market_event_id, symbol=req.symbol,
        timeframe="M15", source_identity=req.m15_source_identity, open=req.m15_open, high=req.m15_high,
        low=req.m15_low, close=req.m15_close, time=req.m15_time, as_of=req.as_of, regime_available=regime_available,
        bias_available=n2.bias_available, n1_fingerprint=req.n1_fingerprint, n2_fingerprint=n2.output_fingerprint,
        atr=None, max_staleness_s=req.m15_max_staleness_s))
    if not n3.market_map_available:
        return _resp(req, n2, n3, None, ReasonCode.N3_UNAVAILABLE, n3.reason_codes[0])
    if not n3.market_map:                          # hartă vidă ⇒ niciun nivel de confirmat
        return _resp(req, n2, n3, None, ReasonCode.N4_UNAVAILABLE, ReasonCode.ZONE_UNAVAILABLE.value)

    # ── N4 (M5) — LEGAT de răspunsul N3 real (rank-1), obținut din rezultatul de mai sus ──
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
        w=3, atr=None, max_staleness_s=req.m5_max_staleness_s))

    # ── verificare defensivă de identitate: același eveniment prin tot lanțul ──
    efp = event_fingerprint(market_event_id=req.market_event_id, symbol=req.symbol, as_of=req.as_of)
    ids_ok = (n2.event_fingerprint == efp and n3.event_fingerprint == efp and n4.event_fingerprint == efp
              and n2.market_event_id == n3.market_event_id == n4.market_event_id == req.market_event_id)
    if not ids_ok or not same_event(n2.event_fingerprint, n2.market_event_id, n3.event_fingerprint, n3.market_event_id):
        return _resp(req, n2, n3, n4, ReasonCode.CHAIN_IDENTITY_MISMATCH, ReasonCode.CHAIN_IDENTITY_MISMATCH.value)

    if not n4.confirmation_available:
        return _resp(req, n2, n3, n4, ReasonCode.N4_UNAVAILABLE, n4.reason_codes[0])
    return _resp(req, n2, n3, n4, ReasonCode.OK_CHAIN, ReasonCode.OK_CHAIN.value)
