"""WP-5' — generator de null STRUCTURAL pentru LM-001. SCHELET NEIMPLEMENTAT.

Nul construit pe MECANISMUL REAL de dependență al LM-001 — ferestre de orizont SUPRAPUSE peste
șocuri i.i.d. per bară — NU pe un proxy AR(1). `block_bootstrap@v1` a fost INVALIDATED_FOR_THIS_SCALE
(manifest v2.5.7, STAT-BLOCKBOOTSTRAP-MK-SMC-v1.0) fiindcă a fost calibrat contra unui AR(1): un AR(1)
are memorie INFINITĂ (decadere geometrică ce nu se anulează niciodată), pe când mecanismul real are
memorie FINITĂ — autocorelația scade LINIAR și devine exact 0 dincolo de lag ~H. Un bloc L≥H conține
INTEGRAL dependența finită — proprietate pe care niciun AR(1) n-o are la nicio lungime de bloc. Deci
curba AR(1) răspundea la altă întrebare; nulul de aici pune întrebarea corectă.

Definiții pure. NU citește prețuri, NU apelează `load()`, NU rulează backtest, NU atinge axa prețurilor.
Reproduce STRUCTURA DE SUPRAPUNERE, nu un coeficient de autocorelație — diferența e chiar motivul
eșecului lui block_bootstrap.

MECANISM (manifest v2.5.7, `wp5_prime_sizing_for_lm001`):
  1. șocuri i.i.d. per bară (increment i.i.d., fără memorie);
  2. rezultatul fiecărui eveniment = suma șocurilor pe fereastra de orizont H=20 bare, [c, c+H];
  3. pozițiile evenimentelor eșantionate la distribuția EMPIRICĂ a spațierii inter-eveniment
     (histograma de grad măsurată de VE, NU doar media ≈6,2 bare).
  Invarianți de reprodus (măsurați de VE, Mandat 5.5): grad mediu de suprapunere concurentă = 7,64;
  orizont partajat = 69% = (H − spațiere_medie)/H = (20 − 6,2)/20; confinare pe segment de descoperire
  (suprapunerea NU traversează carantina, analog D4).

UTILIZARE (aval, NU fixat aici): seria-null se trece prin `block_bootstrap@v1` la L ∈ {10, 20, 28, 40}
prin harness-ul EXISTENT `ve/calibration/synthetic_block_bootstrap.py` — se schimbă DOAR generatorul de
null, nicio infrastructură nouă. **L VARIAZĂ, nu se fixează** (constructorul expune seria; L e parametrul
estimatorului, în aval). Dacă FPR@0,05 iese nominal la L≥28, block_bootstrap@v1 devine validat SPECIFIC
pentru mecanismul real de suprapunere — rezultat mai puternic decât orice mapare pe AR(1).

ÎNTREBĂRI DESCHISE (enumerate, NErezolvate — le trimit Statisticianului; clasificate ca la MK-03/04):

  Q1 (invariantul de suprapunere) — BLOCHEAZĂ COMPLET `sample_event_positions`.
     Ce se păstrează EXACT la re-eșantionare: media gradului (7,64), distribuția completă (histograma
     de grad), sau ambele? Nu se poate eșantiona fără a ști ce invariant e ținta. Ce trebuie decis:
     media vs distribuția vs ambele.
  Q2 (granițe de bloc / alocare pe segmente) — BLOCHEAZĂ PARȚIAL (distribuția pe segmente, nu mecanismul).
     Suprapunerea nu poate traversa carantina (D4). Numărul de evenimente per segment de descoperire se
     fixează la cel empiric (bear/bull/correction), proporțional, sau se re-eșantionează? Fereastra [c,c+H]
     care ar depăși capătul segmentului — exclusă (ca la audit) sau trunchiată? Ce trebuie decis: alocarea
     pe segmente + tratamentul ferestrei la graniță.
  Q3 (structura de sesiune) — BLOCHEAZĂ PARȚIAL (realismul per-sesiune, nu FPR-ul agregat).
     Densitatea diferă pe sesiuni (london 9,85 / ny 9,36 vs asia 6,92 / late 6,27). Nulul reproduce
     densitatea PER SESIUNE sau doar agregatul 7,64? Ce trebuie decis: densitate agregată vs stratificată
     pe sesiune.
  Q4 (semnificația lui „69% orizont partajat") — CLARIFICARE (neblocantă dacă e derivat).
     E o CONSECINȚĂ derivată a spațierii + orizontului (se reproduce automat odată ce spațierea empirică
     e reprodusă), sau un invariant INDEPENDENT de impus separat? Ce trebuie decis: 69% derivat vs impus.
  Q5 (distribuția șocurilor i.i.d.) — BLOCHEAZĂ PARȚIAL (realismul distribuției, nu mecanismul dependenței).
     Șocurile per bară: normale (varianță unitară) sau potrivite la distribuția empirică a randamentelor
     (cozi grele)? Mecanismul de suprapunere e independent de forma șocului; realismul cozii nu e. Ce
     trebuie decis: normal vs empiric.
  Q6 (agregarea pe orizont) — CLARIFICARE (neblocantă).
     Rezultatul LM-001 e net_R la exit c+H (close-to-close); suma șocurilor pe [c, c+H] o aproximează ca
     structură de dependență. E aproximarea suficientă pentru calibrarea FPR, sau contează forma exactă a
     agregării? Ce trebuie decis: sumă de șocuri vs randament reprodus fidel.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np


@dataclass(frozen=True)
class OverlapNullConfig:
    """Configurația nulului structural — invarianții măsurați de VE + geometria de segmente."""

    horizon: int
    """H — fereastra de rezultat, în bare M15 (20 = o sesiune london)."""

    n_events: int
    """Numărul total de evenimente de reprodus (21.048)."""

    segment_lengths: Sequence[int]
    """Lungimile segmentelor de descoperire (bare). Suprapunerea e confinată în segment (D4)."""

    spacing_histogram: Mapping[int, int]
    """Distribuția EMPIRICĂ a gradului/spațierii inter-eveniment (histograma de grad a VE) — nu doar media."""

    target_avg_concurrent: float
    """Invariant: gradul mediu de suprapunere concurentă (7,64)."""

    shared_horizon_frac: float
    """Invariant: fracția de orizont partajat, (H − spațiere_medie)/H (0,69). Vezi Q4."""

    session_densities: Mapping[str, float] | None = None
    """Opțional: densitatea concurentă per sesiune (london/ny/asia/late). None = doar agregat. Vezi Q3."""


class Wp5StructuralNullGenerator:
    """Generează serii-null care reproduc STRUCTURA DE SUPRAPUNERE a LM-001 (nu un AR(1)).

    Constructorul expune seria; lungimea de bloc L a estimatorului `block_bootstrap@v1` e aplicată în
    AVAL (L ∈ {10,20,28,40}, variabilă — vezi docstring-ul modulului). NEIMPLEMENTAT: schelet inert.
    """

    def __init__(self, config: OverlapNullConfig) -> None:
        self.config = config

    def sample_event_positions(self, rng: np.random.Generator) -> list[list[int]]:
        """Re-eșantionează pozițiile temporale ale evenimentelor per segment, la spațierea empirică,
        confinat în segment (D4). Returnează, per segment, indicii barelor-eveniment.

        NEIMPLEMENTAT — depinde de Q1 (ce invariant de suprapunere se fixează) și Q2 (alocarea pe segmente).
        """
        raise NotImplementedError("WP-5': Q1 (invariant de suprapunere) + Q2 (alocare pe segmente)")

    def generate_iid_shocks(self, n_bars: int, rng: np.random.Generator) -> np.ndarray:
        """Șocuri i.i.d. per bară (fără memorie) — sursa increment-ului.

        NEIMPLEMENTAT — depinde de Q5 (distribuția șocurilor: normal vs empiric).
        """
        raise NotImplementedError("WP-5': Q5 (distribuția șocurilor i.i.d.)")

    def horizon_sum_outcomes(
        self, shocks: np.ndarray, event_positions: Sequence[int],
    ) -> np.ndarray:
        """Rezultatul fiecărui eveniment = suma șocurilor pe fereastra de orizont [c, c+H]. Ferestrele
        suprapuse creează dependența cu MEMORIE FINITĂ (→0 dincolo de lag H).

        NEIMPLEMENTAT — depinde de Q2 (tratamentul ferestrei la graniță) și Q6 (agregarea pe orizont).
        """
        raise NotImplementedError("WP-5': Q2 (graniță) + Q6 (agregare pe orizont)")

    def generate_null_series(self, rng: np.random.Generator) -> np.ndarray:
        """Seria-null completă (net_R-like) pentru cele `n_events` evenimente, ce se dă lui
        `block_bootstrap@v1` în aval la L variabil.

        NEIMPLEMENTAT — compune sample_event_positions + generate_iid_shocks + horizon_sum_outcomes;
        depinde de toate întrebările deschise de mai sus.
        """
        raise NotImplementedError("WP-5': schelet — depinde de Q1-Q6 (vezi docstring-ul modulului)")
