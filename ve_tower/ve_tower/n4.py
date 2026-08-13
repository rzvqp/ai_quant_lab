"""ADAPTORUL N4 — confirmare de zonă versionată peste `zone_confirmation.classify_zone_confirmation` RATIFICAT
(NU-l modifică).

Rezolvă: validare de schemă · bare M5 INCHISE+ordonate (fără lookahead) · stale · cascada N3→N4 · identitatea de
eveniment prin lanț · incompatibilitate de contract. Orice problemă ⇒ INDISPONIBILITATE EXPLICITĂ cu reason code
(fail-closed). UNDETERMINED e un rezultat MĂSURAT (confirmation_available=True), NU indisponibilitate. Ieșirea poartă
ACELAȘI market_event_id + configuration_fingerprint ca N3.
"""

from __future__ import annotations

from typing import Any

from ._bootstrap import tower_module
from .contracts import (N4Request, N4Response, SUPPORTED_N4_CONTRACTS, SchemaValidationError, validate_n4_request)
from .fingerprint import configuration_fingerprint
from .reason_codes import ReasonCode, from_ratified_reason
from .version import N4_CODE_VERSION, N4_CONTRACT_VERSION


def _unavailable(req: N4Request, fp: str, reason: ReasonCode) -> N4Response:
    return N4Response(
        contract_version=N4_CONTRACT_VERSION, n4_version=N4_CODE_VERSION, market_event_id=req.market_event_id,
        configuration_fingerprint=fp, confirmation_available=False, confirmation=None, confirmation_value=None,
        persistence=None, progress_atr=None, encounters=None, hit_idx=None, window_end_idx=None,
        descriptor_available_idx=None, as_of=req.as_of, reason_codes=(reason.value,))


def _bars_closed_and_ordered(req: N4Request) -> bool:
    if len(req.time) == 0:
        return False
    prev = req.time[0]
    for t in req.time[1:]:
        if t <= prev:
            return False
        prev = t
    return req.time[-1] <= req.as_of


def run_n4(req: N4Request) -> N4Response:
    """Poarta N4. Determinist. Indisponibilitate explicită pe orice cale de eșec — nu fabrică o confirmare."""
    fp = configuration_fingerprint(market_event_id=req.market_event_id, symbol=req.symbol, as_of=req.as_of)
    if req.contract_version not in SUPPORTED_N4_CONTRACTS:
        return _unavailable(req, fp, ReasonCode.INCOMPATIBLE_CONTRACT)
    # IDENTITATEA DE EVENIMENT prin lanț: id + fingerprint de la N3 trebuie să coincidă cu ale acestui eveniment
    if req.upstream_market_event_id != req.market_event_id or req.upstream_configuration_fingerprint != fp:
        return _unavailable(req, fp, ReasonCode.EVENT_IDENTITY_MISMATCH)
    try:
        validate_n4_request(req)
    except SchemaValidationError:
        return _unavailable(req, fp, ReasonCode.SCHEMA_VALIDATION_FAILED)
    if not _bars_closed_and_ordered(req):
        return _unavailable(req, fp, ReasonCode.BARS_NOT_CLOSED_OR_ORDERED)
    if req.max_staleness_s is not None and (req.as_of - req.time[-1]) > req.max_staleness_s:
        return _unavailable(req, fp, ReasonCode.DATA_STALE)
    if len(req.close) < 2:
        return _unavailable(req, fp, ReasonCode.DATA_INCOMPLETE)
    # CASCADA N3→N4: harta N3 indisponibilă ⇒ zonă indisponibilă
    if not req.n3_available:
        return _unavailable(req, fp, ReasonCode.ZONE_UNAVAILABLE)

    zc: Any = tower_module("zone_confirmation")
    lo: Any = tower_module("level_output")
    result = zc.classify_zone_confirmation(
        req.high, req.low, req.close, req.level, req.side, w=req.w, atr=req.atr, search_start=req.search_start)
    if not lo.is_available(result):
        return _unavailable(req, fp, from_ratified_reason(getattr(result, "reason", "")))

    r = result.value
    return N4Response(
        contract_version=N4_CONTRACT_VERSION, n4_version=N4_CODE_VERSION, market_event_id=req.market_event_id,
        configuration_fingerprint=fp, confirmation_available=True, confirmation=r.confirmation.name,
        confirmation_value=r.confirmation.value, persistence=r.persistence, progress_atr=r.progress_atr,
        encounters=r.encounters, hit_idx=r.hit_idx, window_end_idx=r.window_end_idx,
        descriptor_available_idx=r.descriptor_available_idx, as_of=req.as_of,
        reason_codes=(ReasonCode.OK_CONFIRMATION.value,))
