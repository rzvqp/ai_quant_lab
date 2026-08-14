"""ADAPTORUL N3 (v2) — hartă de zone versionată peste `zone_map.build_zone_map` RATIFICAT (NU-l modifică).

Remediere FAIL: timeframe STRICT M15 · data_identity + node_input_fingerprint per nod · NaN/Inf REFUZ · sursă
obligatorie · răspunsul persistă identitatea datelor consumate. event_fingerprint rămâne COMUN cu N4.
"""

from __future__ import annotations

from typing import Any

from ._bootstrap import tower_module
from .canonical import NonFiniteValueError, canonical_hash
from .contracts import (LevelProvenance, N3Level, N3Request, N3Response, SUPPORTED_N3_CONTRACTS,
                        SchemaValidationError, validate_n3_request)
from .data_identity import DataIdentity, DataIdentityError, build_data_identity
from .fingerprint import event_fingerprint
from .reason_codes import ReasonCode, from_ratified_reason
from .version import N3_CODE_VERSION, N3_CONTRACT_VERSION, N3_EXPECTED_TIMEFRAME


def _unavailable(req: N3Request, efp: str, reason: ReasonCode, di: DataIdentity | None = None,
                 nif: str | None = None) -> N3Response:
    return N3Response(
        contract_version=N3_CONTRACT_VERSION, n3_version=N3_CODE_VERSION, market_event_id=req.market_event_id,
        event_fingerprint=efp, data_identity=di, node_input_fingerprint=nif, market_map_available=False,
        levels_available=False, market_map=(), levels=(), reference_price=None, as_of_index=None,
        valid_until_index=None, reason_codes=(reason.value,))


def _bars_closed_and_ordered(time: tuple[int, ...], as_of: int) -> bool:
    if len(time) == 0:
        return False
    prev = time[0]
    for t in time[1:]:
        if t <= prev:
            return False
        prev = t
    return time[-1] <= as_of


def _node_input_fingerprint(req: N3Request, di: DataIdentity) -> str:
    return canonical_hash({
        "node": "N3", "n3_version": N3_CODE_VERSION, "contract_version": req.contract_version,
        "data_identity": di.to_dict(),
        "n1_fingerprint": req.n1_fingerprint, "n2_fingerprint": req.n2_fingerprint,
        "regime_available": req.regime_available, "bias_available": req.bias_available,
        "band_mult": req.band_mult,
    })


def run_n3(req: N3Request) -> N3Response:
    """Poarta N3. Determinist. Indisponibilitate explicită pe orice cale de eșec — nu fabrică o hartă."""
    efp = event_fingerprint(market_event_id=req.market_event_id, symbol=req.symbol, as_of=req.as_of)
    if req.contract_version not in SUPPORTED_N3_CONTRACTS:
        return _unavailable(req, efp, ReasonCode.INCOMPATIBLE_CONTRACT)
    if req.timeframe != N3_EXPECTED_TIMEFRAME:                       # TIMEFRAME STRICT — refuză M5/BANANA/orice≠M15
        return _unavailable(req, efp, ReasonCode.INVALID_TIMEFRAME)
    try:
        validate_n3_request(req)
    except SchemaValidationError:
        return _unavailable(req, efp, ReasonCode.SCHEMA_VALIDATION_FAILED)
    if not _bars_closed_and_ordered(req.time, req.as_of):
        return _unavailable(req, efp, ReasonCode.BARS_NOT_CLOSED_OR_ORDERED)
    if req.max_staleness_s is not None and (req.as_of - req.time[-1]) > req.max_staleness_s:
        return _unavailable(req, efp, ReasonCode.DATA_STALE)

    # IDENTITATEA DATELOR M15 — sursă obligatorie, NaN/Inf REFUZ, serii coerente
    vectors: dict[str, tuple[float, ...]] = {"open": req.open, "high": req.high, "low": req.low, "close": req.close}
    if req.atr is not None:
        vectors["atr"] = req.atr
    try:
        di = build_data_identity(
            symbol=req.symbol, timeframe=req.timeframe, source_identity=req.source_identity, time=req.time,
            vectors=vectors, as_of=req.as_of, contract_version=req.contract_version,
            dataset_id=req.dataset_id, segment_id=req.segment_id, manifest_hash=req.manifest_hash)
    except NonFiniteValueError:
        return _unavailable(req, efp, ReasonCode.NON_FINITE_VALUE)
    except DataIdentityError as e:
        reason = ReasonCode.SOURCE_IDENTITY_MISSING if "source_identity" in str(e) else ReasonCode.DATA_IDENTITY_INCONSISTENT
        return _unavailable(req, efp, reason)
    nif = _node_input_fingerprint(req, di)

    zm: Any = tower_module("zone_map")
    lo: Any = tower_module("level_output")
    result = zm.build_zone_map(
        req.high, req.low, req.close, req.open, req.time, atr=req.atr, band_mult=req.band_mult,
        regime_available=req.regime_available, bias_available=req.bias_available)
    if not lo.is_available(result):
        return _unavailable(req, efp, from_ratified_reason(getattr(result, "reason", "")), di, nif)

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
        event_fingerprint=efp, data_identity=di, node_input_fingerprint=nif, market_map_available=True,
        levels_available=bool(level_prices), market_map=tuple(levels), levels=level_prices,
        reference_price=zmap.reference_price, as_of_index=result.as_of, valid_until_index=result.valid_until,
        reason_codes=(ReasonCode.OK_MARKET_MAP.value,))
