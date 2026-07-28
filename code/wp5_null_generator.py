"""WP-5' — generator de null STRUCTURAL pentru LM-001. IMPLEMENTAT (v2.5.9, 444e0e8).

Nul construit pe MECANISMUL REAL de dependență al LM-001 — ferestre de orizont SUPRAPUSE peste
șocuri i.i.d. per bară — NU pe un proxy AR(1). `block_bootstrap@v1` a fost INVALIDATED_FOR_THIS_SCALE
fiindcă a fost calibrat contra unui AR(1): AR(1) are memorie INFINITĂ (decadere geometrică), pe când
mecanismul real are memorie FINITĂ — autocorelația → 0 dincolo de lag ~H. Un bloc L≥H conține INTEGRAL
dependența finită — proprietate pe care niciun AR(1) n-o are.

Definiții pure — clasa NU citește prețuri; primește pozițiile de eveniment (structura de suprapunere
empirică) și pool-urile de șocuri empirice deja extrase, per segment. Reproduce STRUCTURA DE
SUPRAPUNERE, nu un coeficient de autocorelație.

DECIZII (Q1-Q6, RESOLVED, manifest v2.5.9):
  Q1 — reproduce distribuția EMPIRICĂ COMPLETĂ de spațiere/grad, NU media. Aici: se condiționează pe
     POZIȚIILE EMPIRICE EXACTE ale evenimentelor (realizarea exactă a histogramei — cea mai tare formă
     a lui Q1, nu o eșantionare aproximativă). Media rezultă automat.
  Q2 — numărători per segment FIXATE la empiric (bear/bull/correction); ferestrele [c,c+H] care depășesc
     capătul segmentului EXCLUSE (nu trunchiate) — deja aplicat la extragerea pozițiilor.
  Q3 — STRATIFICAT pe sesiune: fiecare eveniment poartă sesiunea barei-eveniment; FPR se raportează
     agregat ȘI per sesiune.
  Q4 — „69% orizont partajat" = CONSECINȚĂ DERIVATĂ (verificare post-generare), NU target impus.
  Q5 — șocuri i.i.d. reeșantionate bootstrap din randamentele REALE per-bară M15 (barele de descoperire),
     NU normale — cozi grele documentate; normalul ar subestima riscul de coadă (direcția periculoasă).
  Q6 — rezultat = SUMA șocurilor pe [c, c+H] = `close[c+H]−open[c+1]` (literal suma randamentelor). Scop:
     calibrează STRUCTURA DE DEPENDENȚĂ pentru FPR, NU pipeline-ul net_R complet (R geometric/cost/direcție).

UTILIZARE: `generate_null_series` → seria de rezultate per-eveniment (o realizare de null); se dă lui
`block_bootstrap@v1` la L ∈ {10,20,28,40} (harness existent). L VARIAZĂ, nu e fixat aici.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class OverlapNullConfig:
    """Structura empirică (pozitii + sesiuni + pool-uri de șocuri), per segment de descoperire."""

    horizon: int
    """H — fereastra de rezultat, în bare M15 (20)."""

    event_positions: Sequence[Sequence[int]]
    """Per segment: indicii barelor-eveniment EMPIRICI (Q1 exact; Q2 numărători; ferestre de margine deja excluse)."""

    event_sessions: Sequence[Sequence[str]]
    """Per segment: eticheta de sesiune a fiecărui eveniment (Q3), aliniată la `event_positions`."""

    shock_pools: Sequence[Sequence[float]]
    """Per segment: pool-ul de randamente REALE per-bară M15 din barele de descoperire (Q5)."""

    segment_lengths: Sequence[int]
    """Per segment: numărul de bare (pentru lungimea seriei de șocuri)."""


class Wp5StructuralNullGenerator:
    """Serii-null care reproduc STRUCTURA DE SUPRAPUNERE a LM-001. L e parametru în AVAL, nefixat aici."""

    def __init__(self, config: OverlapNullConfig) -> None:
        self.config = config

    def sample_event_positions(self) -> list[list[int]]:
        """Pozițiile evenimentelor per segment = realizarea EMPIRICĂ EXACTĂ (Q1, forma tare: reproduce
        distribuția completă de spațiere/grad exact, nu o eșantionează). Structura pe care se condiționează."""
        return [list(p) for p in self.config.event_positions]

    def resample_shocks(self, seg_i: int, rng: np.random.Generator) -> np.ndarray:
        """Șocuri i.i.d. pentru segmentul `seg_i` = bootstrap cu înlocuire din pool-ul empiric (Q5).
        Lungime = numărul de bare al segmentului. Fără presupunere distribuțională."""
        pool = np.asarray(self.config.shock_pools[seg_i], dtype=float)
        n_bars = self.config.segment_lengths[seg_i]
        return pool[rng.integers(0, len(pool), size=n_bars)]

    def horizon_sum_outcomes(self, shocks: np.ndarray, positions: Sequence[int]) -> np.ndarray:
        """Rezultatul fiecărui eveniment = suma șocurilor pe [c, c+H] (Q6). Ferestrele suprapuse (evenimente
        la < H bare) partajează șocuri → dependență cu MEMORIE FINITĂ (→0 dincolo de lag H)."""
        H = self.config.horizon
        cum = np.concatenate(([0.0], np.cumsum(shocks)))          # prefix-sum pentru sume O(1)
        out = np.empty(len(positions))
        for i, c in enumerate(positions):
            out[i] = cum[c + H] - cum[c]                           # suma șocurilor pe [c, c+H)
        return out

    def generate_null_series(self, rng: np.random.Generator) -> tuple[np.ndarray, list[str]]:
        """O realizare de null: per segment, reeșantionează șocuri (Q5) și calculează sumele pe orizont pe
        pozițiile empirice (Q1). Returnează (rezultate per-eveniment combinate, etichetele de sesiune). Fără
        edge injectat; `block_bootstrap` centrează și măsoară FPR pe structura reală de suprapunere."""
        positions = self.sample_event_positions()
        outcomes: list[np.ndarray] = []
        sessions: list[str] = []
        for seg_i in range(len(self.config.segment_lengths)):
            shocks = self.resample_shocks(seg_i, rng)
            outcomes.append(self.horizon_sum_outcomes(shocks, positions[seg_i]))
            sessions.extend(self.config.event_sessions[seg_i])
        return np.concatenate(outcomes), sessions
