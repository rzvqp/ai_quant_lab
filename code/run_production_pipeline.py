"""Orchestrator de producție pentru SMC_S1 (= LM-001) — SCHELET GARDAT, FĂRĂ EXECUȚIE (Mandat 5.10).

Integrare software + compilare, atât. NU rulează în această tură: fără `.load()` efectiv, fără P&L, fără
scriere de rezultate. mypy --strict. NU atinge cele șapte module primitive și nici `trading_strategies.py`
(înghețate, auditate).

Fluxul (când gardurile se ridică): loader-ul oficial v6 (`edge_research/_common.py`) → SMC_S1
(`trading_strategies.detect_s1`, construit peste detectorul din `liquidity_mechanics.py` — sweep-reject de
bazin extern, D6+D7, FĂRĂ nicio dependență de displacement) → vectorul net_R conform Open-R (stop la
spike + 2 pips, eligibilitate [10,1;65,0) pips, orizont 20 bare, ieșire pură pe TIMP, fără take-profit).

DOUĂ GARDURI, INDEPENDENTE (nu unul):
  GARD 1 — GATED_BY_CTO: oprește ORICE execuție (`.execute()` ridică `CtoGateError`).
  GARD 2 — segmentul de date, fail-closed PRIN CONSTRUCȚIE: implicit livrează DOAR `DISCOVERY`; accesul la
           `SEALED` cere un parametru DISTINCT (`WrittenAuthorization`), care ridică `SealedAccessError`
           dacă lipsește sau e incomplet. NU un boolean comutat odată cu primul — o A DOUA decizie, la un
           al DOILEA moment. GARD 2 se aplică INDEPENDENT de GARD 1 (dacă cineva ridică GARD 1, sigilatul
           tot nu se deschide fără autorizare scrisă — exact scenariul în care holdout-ul original și Set B
           s-au ars tăcut de două ori).

SEGMENTAREA: loader-ul v6 aplică deja masca la runtime, discovery-only, cu invariantul de contabilitate
`n_before == delivered + quarantine + sealed`. O FOLOSESC — NU reimplementez masca, NU recalculez barele.
GARD 2 e stratul superior, VIZIBIL în orchestrator, peste fail-closed-ul deja existent al loader-ului.

CORECȚIE DE CIFRĂ (Mandat 5.10): descoperirea M15_v2 = 130.491 bare (52.403 + 52.851 + 25.237), interval
semi-deschis [start_epoch, end_epoch). NU o recalculez — o iau din contabilitatea `meta` a loader-ului.
⚠ SEMNALARE: nu există o funcție cu numele literal `in_range()` în `edge_research/split_manifest.py`;
regula semi-deschisă e implementată acolo prin `segmentation_plan()` + `_range()` + masca half-open din
loader. Nu reimplementez nimic — deleg loader-ului; semnalez doar discrepanța de nume.

⚠ VERDICT S10 (merge separat la Statistician, NU aici): substituția BOS-ca-displacement decuplează
magnitudinea de structură (poartă de magnitudine = banda absolută [10,1;65) pips, nu relativă la ATR) —
schimbare de natură teoretică, nu aproximare. NU afectează SMC_S1 (sweep-reject D6+D7, fără displacement).
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Any, Sequence

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_HERE, _ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from edge_research._common import (  # loader oficial v6, discovery-only fail-closed
    PRE_HOLDOUT_SPLIT_ID, RESEARCH_HOLDOUT_CUTOFF_UTC, load,
)
from market_structure import Block  # noqa: E402
from trading_strategies import StrategySignal, detect_s1, net_R  # noqa: E402  # SMC_S1 peste liquidity_mechanics

# ── GARD 1 ────────────────────────────────────────────────────────────────────────────────────────
GATED_BY_CTO: bool = True      # COBORÂT la loc după rularea descriptivă pe AN calendaristic (9 tipuri). Se ridică EXCLUSIV per rulare, prin
#                               decizie CTO. GARD 2 (segmentul sigilat) neatins mereu.

# ── parametrii Open-R pentru SMC_S1 (= LM-001) ──────────────────────────────────────────────────────
HORIZON_S1 = 20              # orizont GRUPA A, ieșire pură pe timp
TIMEFRAME_S1 = "M15_v2"      # descoperirea segmentată a LM-001 (130.491 bare, per contabilitatea loader-ului)


class DataSegment(Enum):
    DISCOVERY = "discovery"  # implicit — in-sample, deschis; livrat de loader-ul v6 (fail-closed)
    SEALED = "sealed"        # holdout — consumabil O SINGURĂ DATĂ; cere GARD 2


class CtoGateError(RuntimeError):
    """GARD 1: `.execute()` apelat cât timp GATED_BY_CTO e True."""


class SealedAccessError(RuntimeError):
    """GARD 2: segmentul sigilat cerut fără autorizare scrisă completă."""


@dataclass(frozen=True)
class WrittenAuthorization:
    """Autorizarea scrisă cerută de GARD 2. Fail-closed: toate câmpurile trebuie non-goale. NU un boolean —
    un obiect DISTINCT (a doua decizie, al doilea moment), cu referință la documentul scris de autorizare."""

    authorized_by: str
    reason: str
    document_ref: str        # referință (commit/doc) la autorizarea scrisă de desigilare

    def assert_complete(self) -> None:
        for name, value in (("authorized_by", self.authorized_by), ("reason", self.reason),
                            ("document_ref", self.document_ref)):
            if not value or not value.strip():
                raise SealedAccessError(
                    f"GARD 2: WrittenAuthorization.{name} gol — acces la sigilat refuzat (fail-closed).")


def structure_net_R_vector(
    signals: Sequence[StrategySignal], open_: Sequence[float], close: Sequence[float],
) -> list[float]:
    """Vectorul net_R conform Open-R: intrare = open[entry_idx], IEȘIRE PURĂ PE TIMP la entry+20 (fără
    take-profit), net_R via `trading_strategies.net_R`. SEMNĂTURĂ care structurează vectorul — se apelează
    DOAR cu prețuri reale, DUPĂ ridicarea ambelor garduri (Corecția 3, Mandat 5.9)."""
    n = len(close)
    out: list[float] = []
    for s in signals:
        exit_idx = min(s.entry_idx + HORIZON_S1, n - 1)          # ieșire pură pe timp
        out.append(net_R(s, float(open_[s.entry_idx]), float(close[exit_idx])))
    return out


class ProductionPipeline:
    """Orchestrator SMC_S1 (LM-001). SCHELET: integrare + compilare; NU se rulează în această tură."""

    def authorize_segment(
        self, segment: DataSegment, authorization: WrittenAuthorization | None = None,
    ) -> DataSegment:
        """GARD 2, PUR, fără I/O. `DISCOVERY` (implicit) trece. `SEALED` cere `WrittenAuthorization`
        completă, altfel `SealedAccessError`. INDEPENDENT de GARD 1 — se aplică chiar dacă GARD 1 s-a ridicat."""
        if segment is DataSegment.DISCOVERY:
            return segment
        if authorization is None:
            raise SealedAccessError(
                "GARD 2: acces la jumătatea sigilată fără autorizare scrisă — refuzat (fail-closed). "
                "Sigilatul e consumabil o singură dată; cere un WrittenAuthorization explicit și distinct.")
        authorization.assert_complete()
        return segment

    def _load_segment(
        self, segment: DataSegment, authorization: WrittenAuthorization | None,
    ) -> tuple[Any, dict[str, Any]]:
        """Încarcă barele segmentului cerut. GARD 2 se aplică AICI mai întâi. DISCOVERY → loader-ul v6
        (discovery-only, fail-closed; NU reimplementez masca). SEALED autorizat → procedura F8 de
        desigilare, NEIMPLEMENTATĂ (sigilatul rămâne neatins în această tură)."""
        seg = self.authorize_segment(segment, authorization)
        if seg is DataSegment.DISCOVERY:
            return load(TIMEFRAME_S1, data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
        raise NotImplementedError(
            "Segmentul sigilat necesită procedura F8 de desigilare, neimplementată — sigilatul rămâne neatins.")

    def _detect_s1(self, df: Any) -> list[StrategySignal]:
        """Conectează SMC_S1 (peste detectorul din liquidity_mechanics) la barele încărcate."""
        n = int(len(df))
        return detect_s1(df["open"].tolist(), df["high"].tolist(), df["low"].tolist(),
                         df["close"].tolist(), [Block(0, n)])

    def execute(
        self, *, segment: DataSegment = DataSegment.DISCOVERY,
        authorization: WrittenAuthorization | None = None,
    ) -> list[float]:
        """GARD 1 → GARD 2 → pipeline. Cât timp GATED_BY_CTO e True, ridică `CtoGateError` ÎNAINTE de orice
        acces la date sau P&L. Chiar dacă GARD 1 s-ar ridica, GARD 2 tot cere autorizare pentru sigilat."""
        if GATED_BY_CTO:
            raise CtoGateError("GARD 1: GATED_BY_CTO=True — orice execuție e oprită.")
        self.authorize_segment(segment, authorization)          # GARD 2, independent de GARD 1
        df, _meta = self._load_segment(segment, authorization)
        signals = self._detect_s1(df)
        return structure_net_R_vector(signals, df["open"].tolist(), df["close"].tolist())
