"""RANGE V2 — PIN de configurație (0.3.1): `w_atr` RATIFICAT, `s_max` DERIVAT STRUCTURAL. NU un patch semantic.

Sursă normativă: Statistician STAT-RANGE-V2-PREREG-PROTOCOL-v1.0 @`4e69e22` (precedență, comis ÎNAINTE de orice
atingere a datelor) → STAT-RANGE-V2-WATR-FINAL-v1.0 @`c29ac98` (rezultat: `w_atr=0,30`, `s_max=2×w_atr=0,60`,
control `RC-CONSTRUCTION-CHANNEL-NEW-01`, S=3,3781 >> s_max, canal respins insensibil la valoarea finală a lui
`w_atr`) → addendum @`2dde05a` → manifest v2.7.81 @`2611d22`, fingerprint `432170ff…` (verificat exact).

**Ce se schimbă (chirurgical, DOAR configurația):**
- `w_atr` = 0,30 (implicit RATIFICAT, înlocuiește implicitul NERATIFICAT 0,25 al 0.3.0).
- `s_max` NU mai există ca literal sau câmp INDEPENDENT — e o `@property` calculată STRUCTURAL ca `2 × w_atr`.
  Constructorul NU acceptă `s_max` (nu există parametru cu acest nume ⇒ `TypeError` la orice încercare).
  `from_dict` (parser) REFUZĂ explicit un câmp `s_max` primit din exterior — `LEGACY_S_MAX_REJECTED`.

**Ce NU se schimbă — reutilizare DIRECTĂ, nu reimplementare:** `_to_runtime_config()` traduce acest obiect
într-un `RangeConfigV2` (0.3.0, NEATINS) real, care alimentează `RangeStateProducerV2` (0.3.0, NEATINS,
IMPORTAT, nicio linie copiată) — mediana-ancoră, atingerea pe interval, acumularea cauzală, BOS/CHoCH intern,
mașina de stări, cele 11 evenimente, F7, zero-lookahead sunt EXACT codul care a rulat în 0.3.0. Singura diferență
observabilă e VALOAREA numerică a lui `w_atr`/`s_max` cu care acel cod e parametrizat.

0.3.0 (`range_state_v2.py`) rămâne BYTE-NEATINS, păstrat pentru audit — acest fișier e NOU, SEPARAT.
"""
from __future__ import annotations

import dataclasses as _dc
import hashlib
from typing import Any

from .range_state_v2 import RangeConfigV2, _K  # 0.3.0, NEATINS — reutilizat direct, nu reimplementat
from .version import (
    W_ATR_CANONICAL, S_MAX_DERIVATION_MULTIPLIER, S_MAX_DERIVATION_FORMULA,
    RANGE_PRODUCER_VERSION_V2_1, RANGE_CONFIG_SCHEMA_VERSION_V2_1, RANGE_STATE_SCHEMA_VERSION_V2,
    RANGE_V2_1_STATISTICIAN_PREREG_COMMIT, RANGE_V2_1_STATISTICIAN_RESULT_COMMIT,
    RANGE_V2_1_MANIFEST_COMMIT, RANGE_V2_1_MANIFEST_FINGERPRINT, LEGACY_S_MAX_REJECTED,
    BARS_PER_DAY_M15, BARS_PER_INTRADAY_SESSION_M15,
)


class LegacyConfigRejectedError(Exception):
    """Refuz fail-closed: o configurație/request/snapshot a încercat să furnizeze `s_max` INDEPENDENT.

    `s_max` are O SINGURĂ sursă de adevăr în 0.3.1 — derivarea structurală `2 × w_atr` — niciodată un literal
    sau câmp separat. Acest tip de excepție e distinct de `RangeSnapshotErrorV2`/`RangeContractErrorV2` (0.3.0)
    tocmai ca refuzul de configurație legacy să fie identificabil separat de un mismatch generic de identitate.
    """

    def __init__(self, message: str, *, reason_code: str = LEGACY_S_MAX_REJECTED) -> None:
        super().__init__(message)
        self.reason_code = reason_code


def _sha(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


@_dc.dataclass(frozen=True, slots=True)
class RangeConfigV2Pinned:
    """Configurație V2 cu PIN structural: `w_atr` e singurul grad de libertate pe zonă; `s_max` e ÎNTOTDEAUNA
    `2 × w_atr`, calculat, niciodată stocat. Câmpurile rămase sunt identice cu `RangeConfigV2` (0.3.0)."""
    n_touch: int = 2
    w_atr: float = W_ATR_CANONICAL             # 0.30 — RATIFICAT (Statistician @c29ac98)
    d_min_bars: int = BARS_PER_DAY_M15
    duration_class: str = "MULTIDAY_RANGE"
    n_acceptance: int = 2
    precedence_rule: str = "RANGE_STATE_OVER_TREND_PAUSE"
    timeframe: str = "15m"
    swing_k: int = _K
    atr_window: int = 14
    range_window: int = 512
    max_duration_bars: int | None = None
    retest_window_bars: int = 12
    candidate_expiry_bars: int | None = None

    @property
    def s_max(self) -> float:
        """UNICA sursă de adevăr pt. s_max: derivat, nu stocat. `RangeStateProducerV2` (0.3.0) citește `cfg.s_max`
        exact ca înainte — proprietatea satisface acel contract fără nicio modificare a codului care o citește."""
        return S_MAX_DERIVATION_MULTIPLIER * self.w_atr

    @property
    def derived_s_max(self) -> float:
        """Alias explicit, pt. citire/provenance — aceeași valoare ca `.s_max`, nume care nu lasă loc de ambiguitate
        asupra faptului că e CALCULATĂ, nu configurată."""
        return self.s_max

    @classmethod
    def intraday(cls, **kw: Any) -> "RangeConfigV2Pinned":
        kw.setdefault("d_min_bars", BARS_PER_INTRADAY_SESSION_M15)
        kw.setdefault("duration_class", "INTRADAY_RANGE")
        return cls(**kw)

    @classmethod
    def multiday(cls, **kw: Any) -> "RangeConfigV2Pinned":
        kw.setdefault("d_min_bars", BARS_PER_DAY_M15)
        kw.setdefault("duration_class", "MULTIDAY_RANGE")
        return cls(**kw)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "RangeConfigV2Pinned":
        """„Parserul" cerut de mandat — refuză EXPLICIT orice request/config serializat(ă) care furnizează `s_max`
        separat, fail-closed, înainte de a construi obiectul. Fără alias, fără fallback, fără valoare legacy."""
        if "s_max" in d:
            raise LegacyConfigRejectedError(
                f"configurație legacy refuzată: câmpul 's_max' (valoare {d['s_max']!r}) nu mai e acceptat — "
                f"s_max se DERIVĂ exclusiv din w_atr ({S_MAX_DERIVATION_FORMULA}); nicio sursă secundară admisă")
        return cls(**{k: v for k, v in d.items() if k != "s_max"})

    def provenance(self) -> dict[str, Any]:
        """Audit explicit: formula de derivare, nu doar valoarea rezultată."""
        return {
            "w_atr": self.w_atr,
            "derived_s_max": self.derived_s_max,
            "s_max_derivation_formula": S_MAX_DERIVATION_FORMULA,
            "s_max_derivation_multiplier": S_MAX_DERIVATION_MULTIPLIER,
            "statistician_prereg_commit": RANGE_V2_1_STATISTICIAN_PREREG_COMMIT,
            "statistician_result_commit": RANGE_V2_1_STATISTICIAN_RESULT_COMMIT,
            "statistician_manifest_commit": RANGE_V2_1_MANIFEST_COMMIT,
            "statistician_manifest_fingerprint": RANGE_V2_1_MANIFEST_FINGERPRINT,
        }

    def range_spec_id(self) -> str:
        """Recalculat — include `w_atr`, REGULA de derivare (nu doar valoarea rezultată a lui s_max) și versiunea
        de producător 0.3.1 ⇒ diferă structural de 0.3.0, nu doar numeric. Rezultatele 0.3.0 devin automat
        NON-COMPARABILE PRIN TIP."""
        return _sha(
            f"n_touch={self.n_touch}", f"w_atr={self.w_atr}",
            f"s_max_derivation_formula={S_MAX_DERIVATION_FORMULA}",
            f"s_max_derivation_multiplier={S_MAX_DERIVATION_MULTIPLIER}",
            f"d_min_bars={self.d_min_bars}", f"duration_class={self.duration_class}",
            f"N_acceptance={self.n_acceptance}", f"precedence_rule={self.precedence_rule}",
            f"timeframe={self.timeframe}", f"swing_k={self.swing_k}", f"atr_window={self.atr_window}",
            f"range_state_schema_version={RANGE_STATE_SCHEMA_VERSION_V2}",
            f"range_config_schema_version={RANGE_CONFIG_SCHEMA_VERSION_V2_1}",
            f"producer_version={RANGE_PRODUCER_VERSION_V2_1}",
        )

    def config_hash(self) -> str:
        return _sha(
            self.range_spec_id(), f"range_window={self.range_window}",
            f"max_duration_bars={self.max_duration_bars}", f"retest_window_bars={self.retest_window_bars}",
            f"candidate_expiry_bars={self.candidate_expiry_bars}",
        )

    def run_hash(self, data_identity: str) -> str:
        return _sha(self.config_hash(), _sha(data_identity), self.range_spec_id())

    def _to_runtime_config(self) -> RangeConfigV2:
        """Traduce în `RangeConfigV2` (0.3.0, NEATINS) — SINGURUL scop e alimentarea `RangeStateProducerV2`
        (0.3.0) neschimbat cu valorile PIN-uite. `s_max` transmis = valoarea DERIVATĂ, niciodată o valoare
        independentă — traducerea nu introduce o a doua sursă de adevăr, doar satisface tipul cerut de codul
        reutilizat NEMODIFICAT."""
        return RangeConfigV2(
            n_touch=self.n_touch, w_atr=self.w_atr, s_max=self.s_max,
            d_min_bars=self.d_min_bars, duration_class=self.duration_class,
            n_acceptance=self.n_acceptance, precedence_rule=self.precedence_rule,
            timeframe=self.timeframe, swing_k=self.swing_k, atr_window=self.atr_window,
            range_window=self.range_window, max_duration_bars=self.max_duration_bars,
            retest_window_bars=self.retest_window_bars, candidate_expiry_bars=self.candidate_expiry_bars,
        )
