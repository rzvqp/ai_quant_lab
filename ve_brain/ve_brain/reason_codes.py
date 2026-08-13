"""Reason codes — cod de motiv EXPLICIT pe fiecare decizie și pe fiecare cădere de contract. Fără text liber, fără
default ascuns: fiecare NO_TRADE și fiecare respingere poartă un cod stabil, auditat până la nod."""

from __future__ import annotations

from enum import Enum


class ReasonCode(Enum):
    # ── decizie pozitivă ──
    TRADE_VALIDATED_EDGE = "TRADE_VALIDATED_EDGE"                 # RATIFIED/PROMOTED cu EV_net > 0 → TRADE real
    SHADOW_CANDIDATE_EV_POSITIVE = "SHADOW_CANDIDATE_EV_POSITIVE"  # SHADOW_ELIGIBLE cu EV_net > 0 → SHADOW_TRADE_CANDIDATE (fără ordin real)

    # ── NO_TRADE deterministe (fără strategie / fără date / fără contract) ──
    NO_ELIGIBLE_STRATEGY = "NO_ELIGIBLE_STRATEGY"               # nicio strategie eligibilă nici pentru shadow (A1)
    MISSING_MARKET_STATE = "MISSING_MARKET_STATE"                # market_state indisponibil (contract)
    MISSING_LEVEL_INPUT = "MISSING_LEVEL_INPUT"                  # un nivel din mulțimea necesară e Unavailable
    MISSING_CONFIRMATION = "MISSING_CONFIRMATION"                # N4 confirmare indisponibilă
    MISSING_PROBABILITY_INPUTS = "MISSING_PROBABILITY_INPUTS"    # nu se inventează probabilități → NO_TRADE
    NEGATIVE_EXPECTED_VALUE = "NEGATIVE_EXPECTED_VALUE"          # EV_net <= 0 sub costurile canonice
    STRATEGY_NOT_ELIGIBLE = "STRATEGY_NOT_ELIGIBLE"             # eligibility_constraints neîndeplinite

    # ── căderi de contract / incompatibilitate (eroare EXPLICITĂ, nu tăcere) ──
    INCOMPATIBLE_CONTRACT = "INCOMPATIBLE_CONTRACT"              # versiune/contract nesuportat
    SCHEMA_VALIDATION_FAILED = "SCHEMA_VALIDATION_FAILED"        # input/output nu respectă schema
    CONFIG_FINGERPRINT_MISMATCH = "CONFIG_FINGERPRINT_MISMATCH"  # comparație non-comparabilă (run_hash diferit)

    # ── execuție invalidă (din evaluatorul canonic; A2 geometrie strictă) ──
    INVALID_EXECUTION = "INVALID_EXECUTION"                      # risc≤0 OR recompensă≤0 (gap/open pe stop sau target)
    STOP_BELOW_MINIMUM = "STOP_BELOW_MINIMUM"                    # R3 reject-not-widen

    # ── RUTARE per regim (amendament regime-conditional) ──
    ROUTER_ELIGIBLE = "ROUTER_ELIGIBLE"                          # strategie eligibilă în regimul curent
    ROUTER_BREAKOUT_ARMED = "ROUTER_BREAKOUT_ARMED"             # BREAKOUT_WATCH armat (RANGE/COMPRESSION)
    INELIGIBLE_REGIME = "INELIGIBLE_REGIME"                      # regimul curent nu e în allowed/arming
    INELIGIBLE_DIRECTION = "INELIGIBLE_DIRECTION"               # direcția N2 nu e în allowed_directions
    BELOW_MIN_REGIME_CONFIDENCE = "BELOW_MIN_REGIME_CONFIDENCE"  # confidence sub minimum_regime_confidence
    UNCERTAIN_REGIME = "UNCERTAIN_REGIME"                        # axă necesară Unavailable → NO_TRADE
    NO_BREAKOUT = "NO_BREAKOUT"                                  # sweep/wick fără displacement+acceptare (N4)
    TRUE_RANGE_NOT_IDENTIFIABLE = "TRUE_RANGE_NOT_IDENTIFIABLE"  # DECIZIE CEO: range real neidentificabil (NEUTRAL conflatează 4 situații)
