"""CONTRACTE VERSIONATE N3/N4 (v2) — remedierea TOWER_HANDOFF_FAIL.

DOUĂ identități separate:
  1. event_fingerprint  — COMUNĂ N3/N4 (identitatea evenimentului: id·symbol·as_of; fără timeframe).
  2. data_identity + node_input_fingerprint — PER NOD; N3 și N4 NU au același node_input_fingerprint (date diferite).

Timeframe STRICT la runtime (N3=M15, N4=M5). Lipsă/stale/NaN/Inf/sursă absentă/timeframe greșit/identitate
inconsistentă ⇒ INDISPONIBILITATE EXPLICITĂ cu reason code, niciodată valori fabricate. N4 e LEGAT EXPLICIT de
răspunsul N3 pe care îl confirmă (identitatea N3 intră în node_input_fingerprint-ul N4).

Upgrade/rollback: `SUPPORTED_N3_CONTRACTS`/`SUPPORTED_N4_CONTRACTS`.
"""

from __future__ import annotations

from dataclasses import dataclass

from .data_identity import DataIdentity
from .version import IncompatibleTowerContractError, N2_CONTRACT_VERSION, N3_CONTRACT_VERSION, N4_CONTRACT_VERSION

SUPPORTED_N2_CONTRACTS: tuple[str, ...] = (N2_CONTRACT_VERSION,)
SUPPORTED_N3_CONTRACTS: tuple[str, ...] = (N3_CONTRACT_VERSION,)
SUPPORTED_N4_CONTRACTS: tuple[str, ...] = (N4_CONTRACT_VERSION,)


class SchemaValidationError(ValueError):
    """Cererea nu respectă schema. Reason: SCHEMA_VALIDATION_FAILED (fail-closed în adaptor)."""


# ── N2 (H1 directional bias FACTORS — determiniști, NU probabilitate) ──
@dataclass(frozen=True)
class N2Request:
    contract_version: str
    market_event_id: str
    symbol: str
    timeframe: str                             # VALIDAT strict la H1
    source_identity: str
    open: tuple[float, ...]                     # H1 INCHISE, ordonate
    high: tuple[float, ...]
    low: tuple[float, ...]
    close: tuple[float, ...]
    time: tuple[int, ...]
    as_of: int
    regime_axes_status: tuple[str, ...]        # statusurile axelor N1 (cascada N1→N2). Toate "unavailable" ⇒ cascadă.
    n1_fingerprint: str                        # identitatea ieșirii N1 (intră în node_input_fingerprint)
    max_staleness_s: int | None = None
    dataset_id: str | None = None
    segment_id: str | None = None
    manifest_hash: str | None = None


@dataclass(frozen=True)
class N2Factor:
    name: str                                  # structure / displacement / liquidity / momentum
    direction: str                             # LONG / SHORT / UNKNOWN (măsurat) — sau None dacă factorul e Unavailable
    available: bool
    primitive: str
    assumption: bool                           # True doar pentru liquidity_above


@dataclass(frozen=True)
class N2Response:
    contract_version: str
    n2_code_version: str                       # SCHEMA_VERSION al bias_h1 ratificat (citit din modul)
    market_event_id: str
    event_fingerprint: str                     # COMUN cu N3/N4
    data_identity: DataIdentity | None
    node_input_fingerprint: str | None
    output_fingerprint: str | None             # amprenta IEȘIRII N2 — o primesc N3/N4 (nu bias_direction, nu default)
    bias_available: bool
    factors: tuple[N2Factor, ...]              # factorii determiniști (ordonați: structure, displacement, liquidity, momentum)
    direction_share_long: float | None         # DESCRIPTIV, NU previziune
    direction_share_short: float | None
    as_of_index: int | None
    valid_until_index: int | None
    reason_codes: tuple[str, ...]


# ── N3 (zone map) ──
@dataclass(frozen=True)
class N3Request:
    contract_version: str
    market_event_id: str
    symbol: str
    timeframe: str                             # VALIDAT strict la M15
    source_identity: str                       # feed id (LIVE) / dataset id (replay/research) — OBLIGATORIU
    open: tuple[float, ...]
    high: tuple[float, ...]
    low: tuple[float, ...]
    close: tuple[float, ...]
    time: tuple[int, ...]                      # epoch s, STRICT ascending, all <= as_of (bare INCHISE, ordonate)
    as_of: int
    regime_available: bool                     # N1 (cascada)
    bias_available: bool                       # N2 (cascada)
    n1_fingerprint: str                        # identitatea ieșirii N1 (intră în node_input_fingerprint)
    n2_fingerprint: str                        # identitatea ieșirii N2
    atr: tuple[float, ...] | None = None
    max_staleness_s: int | None = None
    band_mult: float = 0.25                    # config N3
    dataset_id: str | None = None
    segment_id: str | None = None
    manifest_hash: str | None = None


@dataclass(frozen=True)
class LevelProvenance:
    family: str
    instance_count: int


@dataclass(frozen=True)
class N3Level:
    zone_id: str
    price_anchor: float
    band: float
    provenance: tuple[LevelProvenance, ...]
    distance_atr: float
    age_bars: int
    attribute: str
    relative_rank: int


@dataclass(frozen=True)
class N3Response:
    contract_version: str
    n3_version: str
    market_event_id: str
    event_fingerprint: str                     # COMUN N3/N4
    data_identity: DataIdentity | None         # identitatea datelor M15 consumate (None doar dacă n-a putut fi construită)
    node_input_fingerprint: str | None         # amprenta TUTUROR intrărilor N3 (distinctă de N4)
    market_map_available: bool
    levels_available: bool
    market_map: tuple[N3Level, ...]
    levels: tuple[float, ...]
    reference_price: float | None
    as_of_index: int | None
    valid_until_index: int | None
    reason_codes: tuple[str, ...]


# ── N4 (zone confirmation) — LEGAT de un răspuns N3 ──
@dataclass(frozen=True)
class N4Request:
    contract_version: str
    market_event_id: str
    symbol: str
    timeframe: str                             # VALIDAT strict la M5
    source_identity: str
    high: tuple[float, ...]                     # M5 INCHISE
    low: tuple[float, ...]
    close: tuple[float, ...]
    time: tuple[int, ...]                      # M5 epoch s, STRICT ascending, all <= as_of
    level: float                               # nivelul de la N3
    side: int                                  # +1 / -1
    as_of: int
    strategy_id: str
    strategy_version: str
    regime_available: bool                     # N1
    bias_available: bool                       # N2
    n1_fingerprint: str
    n2_fingerprint: str
    # ── LEGĂTURA EXPLICITĂ cu răspunsul N3 pe care îl confirmă ──
    n3_market_event_id: str
    n3_event_fingerprint: str                  # trebuie == event_fingerprint-ul N4 (același eveniment)
    n3_node_input_fingerprint: str             # identitatea SPECIFICĂ a răspunsului N3 (intră în amprenta N4)
    n3_market_map_available: bool              # False ⇒ cascada ZONE_UNAVAILABLE
    n3_level_zone_id: str                      # provenienta+identitatea nivelului de la N3
    n3_level_provenance: tuple[tuple[str, int], ...]
    w: int = 3
    atr: tuple[float, ...] | None = None
    max_staleness_s: int | None = None
    search_start: int = 0
    dataset_id: str | None = None
    segment_id: str | None = None
    manifest_hash: str | None = None


@dataclass(frozen=True)
class N4Response:
    contract_version: str
    n4_version: str
    market_event_id: str
    event_fingerprint: str                     # COMUN N3/N4
    data_identity: DataIdentity | None         # identitatea datelor M5 consumate
    node_input_fingerprint: str | None         # distinctă de N3
    confirmation_available: bool
    confirmation: str | None
    confirmation_value: int | None
    persistence: float | None
    progress_atr: float | None
    encounters: int | None
    hit_idx: int | None
    window_end_idx: int | None
    descriptor_available_idx: int | None
    as_of: int
    reason_codes: tuple[str, ...]


# ── validare la RUNTIME ──
def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise SchemaValidationError(msg)


def _validate_ohlc(*series: tuple[float, ...]) -> None:
    lengths = {len(s) for s in series}
    _require(len(lengths) == 1, "serii de lungimi inegale")
    # finitudinea se verifică în data_identity (NaN/Inf ⇒ NON_FINITE_VALUE); aici doar prezența numerică
    for s in series:
        for v in s:
            _require(isinstance(v, (int, float)), "valoare OHLC ne-numerică")


def validate_n2_request(req: N2Request) -> None:
    _require(bool(req.market_event_id), "market_event_id gol")
    _require(bool(req.symbol) and bool(req.timeframe), "symbol/timeframe gol")
    _validate_ohlc(req.open, req.high, req.low, req.close)
    _require(len(req.time) == len(req.close), "time și close de lungimi diferite")


def assert_n2_compatible(contract_version: str) -> None:
    if contract_version not in SUPPORTED_N2_CONTRACTS:
        raise IncompatibleTowerContractError(
            f"N2 contract {contract_version!r} nesuportat; suportate: {SUPPORTED_N2_CONTRACTS}")


def validate_n3_request(req: N3Request) -> None:
    _require(bool(req.market_event_id), "market_event_id gol")
    _require(bool(req.symbol) and bool(req.timeframe), "symbol/timeframe gol")
    _validate_ohlc(req.open, req.high, req.low, req.close)
    _require(len(req.time) == len(req.close), "time și close de lungimi diferite")
    if req.atr is not None:
        _require(len(req.atr) == len(req.close), "atr de lungime diferită de close")


def validate_n4_request(req: N4Request) -> None:
    _require(bool(req.market_event_id), "market_event_id gol")
    _require(bool(req.symbol) and bool(req.timeframe), "symbol/timeframe gol")
    _require(bool(req.strategy_id) and bool(req.strategy_version), "strategy_id/version gol")
    _validate_ohlc(req.high, req.low, req.close)
    _require(len(req.time) == len(req.close), "time și close de lungimi diferite")
    if req.atr is not None:
        _require(len(req.atr) == len(req.close), "atr de lungime diferită de close")


def assert_n3_compatible(contract_version: str) -> None:
    if contract_version not in SUPPORTED_N3_CONTRACTS:
        raise IncompatibleTowerContractError(
            f"N3 contract {contract_version!r} nesuportat; suportate: {SUPPORTED_N3_CONTRACTS}")


def assert_n4_compatible(contract_version: str) -> None:
    if contract_version not in SUPPORTED_N4_CONTRACTS:
        raise IncompatibleTowerContractError(
            f"N4 contract {contract_version!r} nesuportat; suportate: {SUPPORTED_N4_CONTRACTS}")
