"""CONTRACTUL STRATEGIILOR — interfața prin care Alpha introduce strategii FĂRĂ recablarea AI Trader.

Fiecare strategie DECLARĂ metadatele + geometria tranzacției. Statutul de validare guvernează cât de departe ajunge:
nicio strategie nu ajunge la execuție doar fiindcă există în cod. Până la promovare: N6 = NO_TRADE, reason
NO_VALIDATED_STRATEGY.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol


class ValidationStatus(Enum):
    EXPERIMENTAL = "EXPERIMENTAL"          # numai în research
    SHADOW_ELIGIBLE = "SHADOW_ELIGIBLE"    # evaluată live, FĂRĂ ordine
    RATIFIED = "RATIFIED"                  # poate ajunge la N6
    PROMOTED = "PROMOTED"                  # poate ajunge la N6
    RETIRED = "RETIRED"                    # scoasă din uz


# AMENDAMENT CEO A1: dreptul de ANALIZĂ prin N6 ≠ dreptul de EXECUȚIE reală.
#  · SHADOW_ELIGIBLE POATE traversa N1-N6 + motorul EV → poate produce SHADOW_TRADE_CANDIDATE sau NO_TRADE;
#    Risk Manager + Execution Adapter pot procesa în shadow, dar BROKER_ORDER_SUBMISSION = DISABLED.
#  · DOAR RATIFIED / PROMOTED pot produce un TRADE real (drept de execuție).
_N6_ANALYSIS_ELIGIBLE: frozenset[ValidationStatus] = frozenset(
    {ValidationStatus.RATIFIED, ValidationStatus.PROMOTED, ValidationStatus.SHADOW_ELIGIBLE})
_REAL_EXECUTION_ELIGIBLE: frozenset[ValidationStatus] = frozenset(
    {ValidationStatus.RATIFIED, ValidationStatus.PROMOTED})


def can_reach_n6(status: ValidationStatus) -> bool:
    """Dreptul de ANALIZĂ prin N6/EV: RATIFIED / PROMOTED / SHADOW_ELIGIBLE. Dacă NICIUNA nu e eligibilă nici măcar
    pentru shadow ⇒ N6 = NO_TRADE, reason NO_ELIGIBLE_STRATEGY."""
    return status in _N6_ANALYSIS_ELIGIBLE


def can_execute_real(status: ValidationStatus) -> bool:
    """Dreptul de EXECUȚIE REALĂ (TRADE, nu SHADOW_TRADE_CANDIDATE): DOAR RATIFIED / PROMOTED."""
    return status in _REAL_EXECUTION_ELIGIBLE


@dataclass(frozen=True)
class TradeProposal:
    """Geometria tranzacției pe care o strategie o emite când își RECUNOAȘTE montajul. Prețurile sunt în USD.
    Conversia în `Signal` canonic (bara de semnal → open[i+1]) o face motorul, nu strategia."""
    direction: int                        # +1 long / −1 short
    signal_bar: int                       # bara ÎNCHISĂ i (intrarea va fi open[i+1], R2)
    stop_price: float                     # stopul INTENȚIONAT (nu se extinde — R3 respinge dacă e sub podea)
    target_kind: str                      # 'rr' | 'price' | 'none'
    target_param: float | None
    holding_window: int                   # max_holding_bars (R6, inclusiv bara de intrare)

# Contractul COMPLET al strategiei (câmpurile de rutare per-regim) + `StrategyRegistry` + `StrategyRouter` trăiesc în
# `regime_routing` (ca să nu ciclăm cu taxonomia SemanticRegime). Aici rămân doar STATUTUL și drepturile.
_ = field  # păstrat pentru compatibilitate de import
