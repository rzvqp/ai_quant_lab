"""CONTRACTE VERSIONATE N3/N4 — scheme de intrare/ieșire, VALIDATE la runtime. Fiecare cerere poartă un
contract_version; nepotrivire ⇒ INCOMPATIBIL (fail-closed sau eroare explicită). Lipsă/stale/incompatibil ⇒
INDISPONIBILITATE EXPLICITĂ cu reason code — niciodată o valoare fabricată.

Upgrade/rollback: `SUPPORTED_N3_CONTRACTS`/`SUPPORTED_N4_CONTRACTS` sunt mulțimile suportate de acest artefact. Un
consumator poate face upgrade adăugând o versiune nouă sau rollback fixând una veche; o cerere în afara mulțimii ⇒
`IncompatibleTowerContractError` (eroare explicită) sau reason INCOMPATIBLE_CONTRACT (fail-closed) în adaptor.
"""

from __future__ import annotations

from dataclasses import dataclass

from .version import IncompatibleTowerContractError, N3_CONTRACT_VERSION, N4_CONTRACT_VERSION

SUPPORTED_N3_CONTRACTS: tuple[str, ...] = (N3_CONTRACT_VERSION,)
SUPPORTED_N4_CONTRACTS: tuple[str, ...] = (N4_CONTRACT_VERSION,)


class SchemaValidationError(ValueError):
    """Cererea nu respectă schema. Reason: SCHEMA_VALIDATION_FAILED (fail-closed în adaptor)."""


# ── N3 (zone map) ──
@dataclass(frozen=True)
class N3Request:
    contract_version: str
    market_event_id: str
    symbol: str
    timeframe: str
    open: tuple[float, ...]
    high: tuple[float, ...]
    low: tuple[float, ...]
    close: tuple[float, ...]
    time: tuple[int, ...]                      # epoch s, STRICT ascending, all <= as_of (bare INCHISE, ordonate)
    as_of: int                                 # decision timestamp (ultima bară închisă)
    regime_available: bool                     # N1 output (cascada)
    bias_available: bool                       # N2 output (cascada)
    atr: tuple[float, ...] | None = None
    max_staleness_s: int | None = None         # data freshness: as_of - time[-1] > max ⇒ DATA_STALE
    band_mult: float = 0.25


@dataclass(frozen=True)
class LevelProvenance:
    family: str                                # level / fvg / pool / ob (familia ratificată)
    instance_count: int


@dataclass(frozen=True)
class N3Level:
    zone_id: str
    price_anchor: float
    band: float
    provenance: tuple[LevelProvenance, ...]    # PROVENIENȚA nivelului (compoziția de familii)
    distance_atr: float
    age_bars: int
    attribute: str
    relative_rank: int


@dataclass(frozen=True)
class N3Response:
    contract_version: str
    n3_version: str
    market_event_id: str                       # ACELAȘI ca în cerere
    configuration_fingerprint: str             # constant prin lanț
    market_map_available: bool
    levels_available: bool
    market_map: tuple[N3Level, ...]
    levels: tuple[float, ...]                   # prețurile-ancoră (nivelele)
    reference_price: float | None
    as_of_index: int | None
    valid_until_index: int | None              # expirare (validity window)
    reason_codes: tuple[str, ...]


# ── N4 (zone confirmation) ──
@dataclass(frozen=True)
class N4Request:
    contract_version: str
    market_event_id: str
    symbol: str
    timeframe: str
    high: tuple[float, ...]                     # M5 INCHISE
    low: tuple[float, ...]
    close: tuple[float, ...]
    time: tuple[int, ...]                       # M5 epoch s, STRICT ascending, all <= as_of (INCHISE, ordonate)
    level: float                               # nivelul de la N3 (price_anchor al zonei alese)
    side: int                                  # +1 sus / -1 jos
    as_of: int
    strategy_id: str                           # identitatea strategiei
    regime_available: bool                     # N1
    bias_available: bool                       # N2
    n3_available: bool                         # N3 (cascada N3→N4)
    upstream_market_event_id: str              # de la N3 — verificat pentru identitatea de eveniment
    upstream_configuration_fingerprint: str    # de la N3 — verificat
    w: int = 3
    atr: tuple[float, ...] | None = None
    max_staleness_s: int | None = None
    search_start: int = 0


@dataclass(frozen=True)
class N4Response:
    contract_version: str
    n4_version: str
    market_event_id: str
    configuration_fingerprint: str
    confirmation_available: bool
    confirmation: str | None                   # numele ordinalului (ACCEPTANCE_BULLISH etc.)
    confirmation_value: int | None             # -2..+2
    persistence: float | None
    progress_atr: float | None
    encounters: int | None
    hit_idx: int | None
    window_end_idx: int | None                 # data freshness: fereastra se închide
    descriptor_available_idx: int | None       # cea mai devreme intrare permisă
    as_of: int
    reason_codes: tuple[str, ...]


# ── validare la RUNTIME ──
def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise SchemaValidationError(msg)


def _validate_ohlc(*series: tuple[float, ...]) -> None:
    lengths = {len(s) for s in series}
    _require(len(lengths) == 1, "serii OHLC de lungimi inegale")
    for s in series:
        for v in s:
            _require(isinstance(v, (int, float)) and v == v, "valoare OHLC nefinită/absentă")


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
    _require(bool(req.strategy_id), "strategy_id gol")
    _validate_ohlc(req.high, req.low, req.close)
    _require(len(req.time) == len(req.close), "time și close de lungimi diferite")
    if req.atr is not None:
        _require(len(req.atr) == len(req.close), "atr de lungime diferită de close")


def assert_n3_compatible(contract_version: str) -> None:
    """Eroare EXPLICITĂ dacă versiunea de contract N3 nu e suportată (upgrade/rollback controlat)."""
    if contract_version not in SUPPORTED_N3_CONTRACTS:
        raise IncompatibleTowerContractError(
            f"N3 contract {contract_version!r} nesuportat; suportate: {SUPPORTED_N3_CONTRACTS}")


def assert_n4_compatible(contract_version: str) -> None:
    if contract_version not in SUPPORTED_N4_CONTRACTS:
        raise IncompatibleTowerContractError(
            f"N4 contract {contract_version!r} nesuportat; suportate: {SUPPORTED_N4_CONTRACTS}")
