"""ADAPTORUL N4 (v2) — confirmare de zonă versionată peste `zone_confirmation.classify_zone_confirmation` RATIFICAT.

Remediere FAIL: timeframe STRICT M5 · data_identity + node_input_fingerprint per nod (DISTINCT de N3) · NaN/Inf REFUZ ·
sursă obligatorie · LEGAT EXPLICIT de răspunsul N3 (identitatea N3 intră în node_input_fingerprint-ul N4; un răspuns N3
nepotrivit ⇒ refuz). event_fingerprint rămâne COMUN cu N3. UNDETERMINED e un Ok măsurat, nu indisponibilitate.
"""

from __future__ import annotations

from typing import Any

from ._bootstrap import tower_module
from .canonical import NonFiniteValueError, canonical_hash
from .contracts import N4Request, N4Response, SUPPORTED_N4_CONTRACTS, SchemaValidationError, validate_n4_request
from .data_identity import DataIdentity, DataIdentityError, build_data_identity
from .fingerprint import event_fingerprint
from .reason_codes import ReasonCode, from_ratified_reason
from .version import N4_CODE_VERSION, N4_CONTRACT_VERSION, N4_EXPECTED_TIMEFRAME


def _unavailable(req: N4Request, efp: str, reason: ReasonCode, di: DataIdentity | None = None,
                 nif: str | None = None) -> N4Response:
    return N4Response(
        contract_version=N4_CONTRACT_VERSION, n4_version=N4_CODE_VERSION, market_event_id=req.market_event_id,
        event_fingerprint=efp, data_identity=di, node_input_fingerprint=nif, confirmation_available=False,
        confirmation=None, confirmation_value=None, persistence=None, progress_atr=None, encounters=None,
        hit_idx=None, window_end_idx=None, descriptor_available_idx=None, as_of=req.as_of,
        reason_codes=(reason.value,))


def _bars_closed_and_ordered(time: tuple[int, ...], as_of: int) -> bool:
    if len(time) == 0:
        return False
    prev = time[0]
    for t in time[1:]:
        if t <= prev:
            return False
        prev = t
    return time[-1] <= as_of


def _node_input_fingerprint(req: N4Request, di: DataIdentity) -> str:
    return canonical_hash({
        "node": "N4", "n4_version": N4_CODE_VERSION, "contract_version": req.contract_version,
        "data_identity": di.to_dict(),
        "level": req.level, "side": req.side, "strategy_id": req.strategy_id,
        "strategy_version": req.strategy_version, "w": req.w, "search_start": req.search_start,
        "n1_fingerprint": req.n1_fingerprint, "n2_fingerprint": req.n2_fingerprint,
        # LEGĂTURA cu răspunsul N3 pe care îl confirmă (identitate + provenanță)
        "n3_node_input_fingerprint": req.n3_node_input_fingerprint, "n3_event_fingerprint": req.n3_event_fingerprint,
        "n3_level_zone_id": req.n3_level_zone_id,
        "n3_level_provenance": [list(p) for p in req.n3_level_provenance],
    })


def run_n4(req: N4Request) -> N4Response:
    """Poarta N4. Determinist. Indisponibilitate explicită pe orice cale de eșec — nu fabrică o confirmare."""
    efp = event_fingerprint(market_event_id=req.market_event_id, symbol=req.symbol, as_of=req.as_of)
    if req.contract_version not in SUPPORTED_N4_CONTRACTS:
        return _unavailable(req, efp, ReasonCode.INCOMPATIBLE_CONTRACT)
    if req.timeframe != N4_EXPECTED_TIMEFRAME:                       # TIMEFRAME STRICT — refuză M15/orice≠M5
        return _unavailable(req, efp, ReasonCode.INVALID_TIMEFRAME)
    # LEGĂTURA cu N3: același eveniment (id + event_fingerprint). Alt răspuns N3 / alt eveniment ⇒ refuz.
    if req.n3_event_fingerprint != efp or req.n3_market_event_id != req.market_event_id:
        return _unavailable(req, efp, ReasonCode.N3_LINK_MISMATCH)
    try:
        validate_n4_request(req)
    except SchemaValidationError:
        return _unavailable(req, efp, ReasonCode.SCHEMA_VALIDATION_FAILED)
    if not _bars_closed_and_ordered(req.time, req.as_of):
        return _unavailable(req, efp, ReasonCode.BARS_NOT_CLOSED_OR_ORDERED)
    if req.max_staleness_s is not None and (req.as_of - req.time[-1]) > req.max_staleness_s:
        return _unavailable(req, efp, ReasonCode.DATA_STALE)
    if len(req.close) < 2:
        return _unavailable(req, efp, ReasonCode.DATA_INCOMPLETE)
    if not req.n3_market_map_available:                              # cascada N3→N4
        return _unavailable(req, efp, ReasonCode.ZONE_UNAVAILABLE)

    vectors: dict[str, tuple[float, ...]] = {"high": req.high, "low": req.low, "close": req.close}
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

    zc: Any = tower_module("zone_confirmation")
    lo: Any = tower_module("level_output")
    result = zc.classify_zone_confirmation(
        req.high, req.low, req.close, req.level, req.side, w=req.w, atr=req.atr, search_start=req.search_start)
    if not lo.is_available(result):
        return _unavailable(req, efp, from_ratified_reason(getattr(result, "reason", "")), di, nif)

    r = result.value
    return N4Response(
        contract_version=N4_CONTRACT_VERSION, n4_version=N4_CODE_VERSION, market_event_id=req.market_event_id,
        event_fingerprint=efp, data_identity=di, node_input_fingerprint=nif, confirmation_available=True,
        confirmation=r.confirmation.name, confirmation_value=r.confirmation.value, persistence=r.persistence,
        progress_atr=r.progress_atr, encounters=r.encounters, hit_idx=r.hit_idx, window_end_idx=r.window_end_idx,
        descriptor_available_idx=r.descriptor_available_idx, as_of=req.as_of,
        reason_codes=(ReasonCode.OK_CONFIRMATION.value,))
