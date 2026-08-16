"""ADAPTORUL N2 — bias direcțional H1 versionat peste `bias_h1.compute_bias` RATIFICAT (NU-l modifică, NU-l re-vendorizează).

`bias_h1` e DEJA vendat în ve_tower (byte-identic cu blob-ul git @850815f). Acest adaptor doar îl EXPUNE ca producător
versionat: timeframe STRICT H1 · data_identity + node_input_fingerprint · output_fingerprint (pe care N3/N4 îl primesc
în loc de bias_direction/default LONG) · NaN/Inf REFUZ · sursă obligatorie · reason codes · N2_UNAVAILABLE fail-closed.

N2 emite FACTORI DETERMINIȘTI (structure/displacement/liquidity/momentum → LONG/SHORT/UNKNOWN), NU probabilitate, NU EV,
NU decizie. `emits_probability=False` în modulul ratificat.
"""

from __future__ import annotations

from typing import Any

from ._bootstrap import tower_module
from .canonical import NonFiniteValueError, canonical_hash
from .contracts import (N2Factor, N2Request, N2Response, SUPPORTED_N2_CONTRACTS, SchemaValidationError,
                        validate_n2_request)
from .data_identity import DataIdentity, DataIdentityError, build_data_identity
from .fingerprint import event_fingerprint
from .reason_codes import ReasonCode, from_ratified_reason
from .version import N2_CONTRACT_VERSION, N2_EXPECTED_TIMEFRAME


def _n2_code_version() -> str:
    """code_version-ul N2 = SCHEMA_VERSION al modulului ratificat (citit din bias_h1, nu inventat)."""
    bias: Any = tower_module("bias_h1")
    return str(bias.SCHEMA_VERSION)


def _unavailable(req: N2Request, efp: str, reason: ReasonCode, di: DataIdentity | None = None,
                 nif: str | None = None) -> N2Response:
    return N2Response(
        contract_version=N2_CONTRACT_VERSION, n2_code_version=_n2_code_version(), market_event_id=req.market_event_id,
        event_fingerprint=efp, data_identity=di, node_input_fingerprint=nif, output_fingerprint=None,
        bias_available=False, factors=(), direction_share_long=None, direction_share_short=None,
        as_of_index=None, valid_until_index=None, reason_codes=(reason.value,))


def _bars_closed_and_ordered(time: tuple[int, ...], as_of: int) -> bool:
    if len(time) == 0:
        return False
    prev = time[0]
    for t in time[1:]:
        if t <= prev:
            return False
        prev = t
    return time[-1] <= as_of


def _node_input_fingerprint(req: N2Request, di: DataIdentity) -> str:
    return canonical_hash({
        "node": "N2", "n2_code_version": _n2_code_version(), "contract_version": req.contract_version,
        "data_identity": di.to_dict(),
        "regime_axes_status": list(req.regime_axes_status), "n1_fingerprint": req.n1_fingerprint,
    })


def run_n2(req: N2Request) -> N2Response:
    """Poarta N2. Determinist. Indisponibilitate explicită pe orice cale de eșec — nu fabrică factori, niciun default LONG."""
    efp = event_fingerprint(market_event_id=req.market_event_id, symbol=req.symbol, as_of=req.as_of)
    if req.contract_version not in SUPPORTED_N2_CONTRACTS:
        return _unavailable(req, efp, ReasonCode.INCOMPATIBLE_CONTRACT)
    if req.timeframe != N2_EXPECTED_TIMEFRAME:                       # TIMEFRAME STRICT — refuză orice ≠ H1
        return _unavailable(req, efp, ReasonCode.INVALID_TIMEFRAME)
    try:
        validate_n2_request(req)
    except SchemaValidationError:
        return _unavailable(req, efp, ReasonCode.SCHEMA_VALIDATION_FAILED)
    if not _bars_closed_and_ordered(req.time, req.as_of):
        return _unavailable(req, efp, ReasonCode.BARS_NOT_CLOSED_OR_ORDERED)
    if req.max_staleness_s is not None and (req.as_of - req.time[-1]) > req.max_staleness_s:
        return _unavailable(req, efp, ReasonCode.DATA_STALE)

    vectors: dict[str, tuple[float, ...]] = {"open": req.open, "high": req.high, "low": req.low, "close": req.close}
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

    bias: Any = tower_module("bias_h1")
    lo: Any = tower_module("level_output")
    # i = len(close): consumă TOATE barele închise (canonic — ca în market_bus). Non-lookahead prin construcția modulului.
    result = bias.compute_bias(req.open, req.high, req.low, req.close, len(req.close),
                               regime_axes_status=list(req.regime_axes_status))
    if not lo.is_available(result):
        return _unavailable(req, efp, from_ratified_reason(getattr(result, "reason", "")), di, nif)

    state = result.value
    factors: list[N2Factor] = []
    for fo in state.factors:
        if lo.is_available(fo):
            fd = fo.value
            factors.append(N2Factor(name=fd.name, direction=fd.direction.value, available=True,
                                    primitive=fd.primitive, assumption=fd.assumption))
        else:
            factors.append(N2Factor(name=getattr(fo, "reason", "unknown"), direction="UNKNOWN", available=False,
                                    primitive="", assumption=False))
    # output_fingerprint: identitatea IEȘIRII N2 (factori + shares + identitatea nodului). N3/N4 primesc ASTA.
    output_fingerprint = canonical_hash({
        "node_input_fingerprint": nif,
        "factors": [[f.name, f.direction, f.available, f.primitive, f.assumption] for f in factors],
        "direction_share_long": state.direction_share_long, "direction_share_short": state.direction_share_short,
    })
    return N2Response(
        contract_version=N2_CONTRACT_VERSION, n2_code_version=_n2_code_version(), market_event_id=req.market_event_id,
        event_fingerprint=efp, data_identity=di, node_input_fingerprint=nif, output_fingerprint=output_fingerprint,
        bias_available=True, factors=tuple(factors), direction_share_long=state.direction_share_long,
        direction_share_short=state.direction_share_short, as_of_index=result.as_of,
        valid_until_index=result.valid_until, reason_codes=(ReasonCode.OK_BIAS_FACTORS.value,))
