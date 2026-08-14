"""DATA IDENTITY — identitatea DETERMINISTĂ a datelor pe care le consumă un nod. Persistată în request ȘI response,
ca două hărți diferite să NU mai poată fi prezentate cu aceeași proveniență.

Conține: symbol · timeframe VALIDAT · source/feed identity · prima bară · ultima bară ÎNCHISĂ · numărul de bare ·
as_of · content hash canonic al barelor (OHLC/HLC + time + orice vector auxiliar) · contract version. Pentru
replay/research: dataset/segment/manifest (când există). Pentru LIVE: doar source/feed id — NU se inventează manifest.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .canonical import canonical_hash


class DataIdentityError(ValueError):
    """Sursă lipsă / serii incoerente — fail-closed, nu identitate fabricată."""


@dataclass(frozen=True)
class DataIdentity:
    symbol: str
    timeframe: str                     # VALIDAT de nod (N3=M15, N4=M5)
    source_identity: str               # feed id (LIVE) sau dataset id (replay/research) — OBLIGATORIU
    first_bar_time: int
    last_closed_bar_time: int
    bar_count: int
    as_of: int
    bars_content_hash: str             # hash canonic al time + toate vectorii (OHLC/HLC/ATR/aux)
    contract_version: str
    dataset_id: str | None = None
    segment_id: str | None = None
    manifest_hash: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_data_identity(*, symbol: str, timeframe: str, source_identity: str, time: tuple[int, ...],
                        vectors: dict[str, tuple[float, ...]], as_of: int, contract_version: str,
                        dataset_id: str | None = None, segment_id: str | None = None,
                        manifest_hash: str | None = None) -> DataIdentity:
    """Construiește identitatea datelor. `source_identity` gol ⇒ DataIdentityError. Hash-ul barelor include TOATE
    seriile (NaN/Inf ⇒ NonFiniteValueError din `canonical`). Serii de lungimi inegale ⇒ DataIdentityError."""
    if not source_identity:
        raise DataIdentityError("source_identity gol — LIVE cere feed id, replay/research cere dataset id")
    if not time:
        raise DataIdentityError("serie de timp goală")
    n = len(time)
    for name, v in vectors.items():
        if len(v) != n:
            raise DataIdentityError(f"vectorul {name!r} are lungime {len(v)} != {n} (time)")
    # content hash canonic: time normalizate + vectorii, ordine fixă (canonical sortează cheile hărții)
    bars_content_hash = canonical_hash({
        "time": list(time),
        "vectors": {name: list(v) for name, v in vectors.items()},
    })
    return DataIdentity(
        symbol=symbol, timeframe=timeframe, source_identity=source_identity, first_bar_time=time[0],
        last_closed_bar_time=time[-1], bar_count=n, as_of=as_of, bars_content_hash=bars_content_hash,
        contract_version=contract_version, dataset_id=dataset_id, segment_id=segment_id, manifest_hash=manifest_hash)
