"""Reason codes ai TURNULUI — cod EXPLICIT pe fiecare ieșire N3/N4 și pe fiecare indisponibilitate. Valorile enum-ului
sunt IDENTICE cu string-urile de `reason` ale modulelor ratificate (pass-through direct, fără traducere ascunsă) plus
codurile de nivel-contract adăugate de adaptor. Lipsă/stale/incompatibil ⇒ un cod, niciodată o valoare fabricată."""

from __future__ import annotations

from enum import Enum


class ReasonCode(Enum):
    # ── pozitive ──
    OK_BIAS_FACTORS = "ok_bias_factors"            # N2: factori direcționali produși (determiniști, fără probabilitate)
    OK_MARKET_MAP = "ok_market_map"                 # N3: hartă produsă (poate fi și mulțime vidă = Ok)
    OK_CONFIRMATION = "ok_confirmation"             # N4: descriptor măsurat (inclusiv UNDETERMINED)

    # ── indisponibilități din modulele RATIFICATE (string-uri exacte) ──
    INCOMPLETE_WINDOW = "incomplete_window"                          # N3/N4: fereastră insuficientă
    CASCADE_LEVEL1_OR_LEVEL2_UNAVAILABLE = "cascade_level1_or_level2_unavailable"  # N3: N1/N2 indisponibil
    ATR_UNAVAILABLE = "atr_unavailable"                             # N3/N4: ATR nefinit
    INVALID_SIDE = "invalid_side"                                   # N4: side ∉ {+1,-1}
    ZONE_UNAVAILABLE = "zone_unavailable"                           # N4: nivelul N3 nefinit (cascada N3→N4)
    NO_PENETRATION = "no_penetration"                              # N4: nu intră în populație
    CASCADE_REGIME_ALL_AXES_UNAVAILABLE = "cascade_regime_all_axes_unavailable"   # N2: toate axele N1 indisponibile
    N2_UNAVAILABLE = "n2_unavailable"                              # N2: indisponibil (fail-closed generic)
    # ── orchestrator de lanț (RT-TOWER-0007): status-uri + refuzuri de identitate ──
    OK_CHAIN = "ok_chain"                                          # lanț complet N2→N3→N4 disponibil
    N3_UNAVAILABLE = "n3_unavailable"                             # cascadă: N3 indisponibil ⇒ N4 nu confirmă
    N4_UNAVAILABLE = "n4_unavailable"                             # cascadă: N4 indisponibil
    CHAIN_IDENTITY_MISMATCH = "chain_identity_mismatch"          # mismatch event/config/source/contract/link ⇒ fail-closed
    UNKNOWN_REQUEST_FIELD = "unknown_request_field"              # câmp necunoscut (ex. n2_fingerprint) în cererea de lanț

    # ── indisponibilități de nivel-CONTRACT (adaugate de adaptor, fail-closed) ──
    SCHEMA_VALIDATION_FAILED = "schema_validation_failed"           # cererea nu respectă schema
    INCOMPATIBLE_CONTRACT = "incompatible_contract"                 # contract_version nesuportat
    BARS_NOT_CLOSED_OR_ORDERED = "bars_not_closed_or_ordered"       # bare neordonate / cu timp > as_of (lookahead)
    DATA_STALE = "data_stale"                                       # ultima bară mai veche decât max_staleness
    DATA_INCOMPLETE = "data_incomplete"                            # serii de lungimi inegale / prea scurte
    EVENT_IDENTITY_MISMATCH = "event_identity_mismatch"            # N4: event_id/fingerprint ≠ cele de la N3
    # ── remediere TOWER_HANDOFF_FAIL: timeframe strict + dublă identitate + hash canonic ──
    INVALID_TIMEFRAME = "invalid_timeframe"                        # N3≠M15 / N4≠M5 / valoare necunoscută
    NON_FINITE_VALUE = "non_finite_value"                          # NaN/Inf în bare/vectori (politica = REFUZ)
    SOURCE_IDENTITY_MISSING = "source_identity_missing"           # feed/source id absent
    DATA_IDENTITY_INCONSISTENT = "data_identity_inconsistent"     # serii incoerente / identitate imposibil de construit
    N3_LINK_MISMATCH = "n3_link_mismatch"                         # N4 legat de un răspuns N3 care nu se potrivește


_RATIFIED_REASONS: frozenset[str] = frozenset({
    ReasonCode.INCOMPLETE_WINDOW.value, ReasonCode.CASCADE_LEVEL1_OR_LEVEL2_UNAVAILABLE.value,
    ReasonCode.ATR_UNAVAILABLE.value, ReasonCode.INVALID_SIDE.value, ReasonCode.ZONE_UNAVAILABLE.value,
    ReasonCode.NO_PENETRATION.value, ReasonCode.CASCADE_REGIME_ALL_AXES_UNAVAILABLE.value,
})


def from_ratified_reason(reason: str) -> ReasonCode:
    """Împachetează string-ul de reason al modulului ratificat într-un ReasonCode canonic (pass-through)."""
    if reason in _RATIFIED_REASONS:
        return ReasonCode(reason)
    # necunoscut ⇒ tratează ca indisponibilitate de schemă (fail-closed, nu-l ascunde)
    return ReasonCode.SCHEMA_VALIDATION_FAILED
