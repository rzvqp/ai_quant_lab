"""ADAPTORUL N3 — hartă de zone versionată peste `zone_map.build_zone_map` RATIFICAT (NU-l modifică).

Rezolvă: validare de schemă la runtime · bare INCHISE+ordonate (fără lookahead) · data freshness (stale) · cascada
N1/N2 · incompatibilitate de contract. Orice problemă ⇒ INDISPONIBILITATE EXPLICITĂ cu reason code (fail-closed),
niciodată valori fabricate. Ieșirea poartă ACELAȘI market_event_id + configuration_fingerprint.
"""

from __future__ import annotations

from typing import Any

from ._bootstrap import tower_module
from .contracts import (LevelProvenance, N3Level, N3Request, N3Response, SUPPORTED_N3_CONTRACTS,
                        SchemaValidationError, validate_n3_request)
from .fingerprint import configuration_fingerprint
from .reason_codes import ReasonCode, from_ratified_reason
from .version import N3_CODE_VERSION, N3_CONTRACT_VERSION


def _unavailable(req: N3Request, fp: str, reason: ReasonCode) -> N3Response:
    return N3Response(
        contract_version=N3_CONTRACT_VERSION, n3_version=N3_CODE_VERSION, market_event_id=req.market_event_id,
        configuration_fingerprint=fp, market_map_available=False, levels_available=False, market_map=(),
        levels=(), reference_price=None, as_of_index=None, valid_until_index=None, reason_codes=(reason.value,))


def _bars_closed_and_ordered(req: N3Request) -> bool:
    if len(req.time) == 0:
        return False
    prev = req.time[0]
    for t in req.time[1:]:
        if t <= prev:                 # STRICT crescător (ordonate, fără duplicate)
            return False
        prev = t
    return req.time[-1] <= req.as_of  # nicio bară cu timp > as_of (fără lookahead)


def run_n3(req: N3Request) -> N3Response:
    """Poarta N3. Determinist. Indisponibilitate explicită pe orice cale de eșec — nu fabrică o hartă."""
    fp = configuration_fingerprint(market_event_id=req.market_event_id, symbol=req.symbol, as_of=req.as_of)
    # incompatibilitate de contract ⇒ fail-closed (explicit)
    if req.contract_version not in SUPPORTED_N3_CONTRACTS:
        return _unavailable(req, fp, ReasonCode.INCOMPATIBLE_CONTRACT)
    # schema la runtime
    try:
        validate_n3_request(req)
    except SchemaValidationError:
        return _unavailable(req, fp, ReasonCode.SCHEMA_VALIDATION_FAILED)
    # bare INCHISE + ordonate (prinde lookahead)
    if not _bars_closed_and_ordered(req):
        return _unavailable(req, fp, ReasonCode.BARS_NOT_CLOSED_OR_ORDERED)
    # data freshness
    if req.max_staleness_s is not None and (req.as_of - req.time[-1]) > req.max_staleness_s:
        return _unavailable(req, fp, ReasonCode.DATA_STALE)

    zm: Any = tower_module("zone_map")
    lo: Any = tower_module("level_output")
    result = zm.build_zone_map(
        req.high, req.low, req.close, req.open, req.time, atr=req.atr, band_mult=req.band_mult,
        regime_available=req.regime_available, bias_available=req.bias_available)
    if not lo.is_available(result):
        return _unavailable(req, fp, from_ratified_reason(getattr(result, "reason", "")))

    zmap = result.value
    levels: list[N3Level] = []
    for z in zmap.zones:
        prov = tuple(LevelProvenance(family=fam, instance_count=cnt) for fam, cnt in z.composition)
        levels.append(N3Level(
            zone_id=z.zone_id, price_anchor=z.price_anchor, band=z.band, provenance=prov,
            distance_atr=z.distance_atr, age_bars=z.age_bars, attribute=z.attribute, relative_rank=z.relative_rank))
    level_prices = tuple(z.price_anchor for z in zmap.zones)
    return N3Response(
        contract_version=N3_CONTRACT_VERSION, n3_version=N3_CODE_VERSION, market_event_id=req.market_event_id,
        configuration_fingerprint=fp, market_map_available=True, levels_available=bool(level_prices),
        market_map=tuple(levels), levels=level_prices, reference_price=zmap.reference_price,
        as_of_index=result.as_of, valid_until_index=result.valid_until, reason_codes=(ReasonCode.OK_MARKET_MAP.value,))
