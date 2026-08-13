# ve_brain — CONTRACTE PUBLICE (gate 3)

**Artefact:** `ve_brain` v0.1.0 · **Sursă:** `ai_quant_lab-wp5b @ discovery-mk-matrix-v1 @ 3344bff` (+ corectiv A2 `dc28e4a`)
**Contract de măsurare:** `canonical-evaluator-v2.7.66-A2` · **STATUT: v1.0-DRAFT — NOT RATIFIED** (Red Team ratifică în paralel).
**BROKER_ORDER_SUBMISSION = DISABLED** — artefactul produce DECIZII, niciodată ordine reale.

## Intrare — `DecisionRequest` (`ve.decision_request.v1`)
Câmpuri validate la runtime (nepotrivire ⇒ `SCHEMA_VALIDATION_FAILED`):
`contract_id, strategy_id, strategy_version, validation_status, market_state_ref, regime_label, bias_direction,
market_map_available, levels_available, confirmation_available, entry_price, stop_price, target_kind∈{rr,price,none},
target_param, holding_window≥1, atr>0, probability_inputs (ProbabilityInputs|None), full_spread_price,
entry_slippage_price, exit_slippage_price, measurement_contract_version, configuration_fingerprint`.

`ProbabilityInputs` = ierarhie empiric-Bayes (`HierarchyLevel{cell:OutcomeCell, siblings}`,
`OutcomeCell{n, n_target, n_horizon, sum_horizon_R}`) + `credibility∈(0,1)`. **Absentă ⇒ NO_TRADE** (nu se inventează).

## Ieșire — `DecisionResponse` (`ve.decision_response.v1`)
`contract_id, decision∈{TRADE, SHADOW_TRADE_CANDIDATE, NO_TRADE}, expected_value_net, expected_reward,
expected_loss, estimated_cost, probability_assumptions, strategy_id, configuration_fingerprint, reason_codes,
engine_version`.

**Formula EV (motor real, nu edge=bool):** `EV_R = p_t·RR − p_s·1 + p_h·E[X|h] − c/R`, gardă pe LCB (strict > 0).
`rr = target/R`, `r = |entry−stop|` USD, `cost = full_spread + entry_slip + exit_slip` USD (spread O DATĂ).

## Contractul strategiei (rutare per regim)
`strategy_id, strategy_family, allowed_regimes, allowed_directions, arming_regimes, trigger_transition,
minimum_regime_confidence, required_N2_bias, required_N3_map, required_N4_confirmation, entry_rule,
invalidation_rule, exit_rule, holding_window, validation_status, strategy_version, measurement_contract_version,
exit_on_regime_change, exit_on_transition`.

**Statuturi:** `EXPERIMENTAL` (research), `SHADOW_ELIGIBLE` (N1-N6+EV, produce SHADOW_TRADE_CANDIDATE, FĂRĂ ordin),
`RATIFIED`/`PROMOTED` (TRADE real), `RETIRED`. Nicio strategie eligibilă nici pentru shadow ⇒ `NO_ELIGIBLE_STRATEGY`.

## Taxonomia semantică (6 stări ← 4 axe N1)
`COMPRESSION`←vol=compressed · `BREAKOUT_TRANSITION`←struct=range(flip)∧vol=high_directional ·
`TREND_UP`←struct∈{weak,strong}∧dir∈{up,weak_up} · `TREND_DOWN`←…{down,weak_down} ·
`RANGE`←dir=neutral∧vol∈{low,normal} · `UNCERTAIN`←axă absentă / fără potrivire.
⚠ `BREAKOUT_TRANSITION` e proxy PER-BARĂ; versiunea strictă (din COMPRESSION/RANGE anterioară) cere un detector de
tranziție cu 2 stări peste N1 — SEMNALAT, neinventat.

## Amprenta (T17/A5) — `configuration_fingerprint`
`sha256(config_hash ‖ sha256(data_identity))` la nivel de măsurare, apoi `decision_fingerprint` peste
**date · config · STRATEGIE · MOTOR · versiunea contractului**. `compare_decisions()` RIDICĂ pe nepotrivire.

## Reason codes
`TRADE_VALIDATED_EDGE, SHADOW_CANDIDATE_EV_POSITIVE, NO_ELIGIBLE_STRATEGY, MISSING_LEVEL_INPUT,
MISSING_CONFIRMATION, MISSING_PROBABILITY_INPUTS, NEGATIVE_EXPECTED_VALUE, INCOMPATIBLE_CONTRACT,
SCHEMA_VALIDATION_FAILED, INVALID_EXECUTION, STOP_BELOW_MINIMUM, ROUTER_ELIGIBLE, ROUTER_BREAKOUT_ARMED,
INELIGIBLE_REGIME, INELIGIBLE_DIRECTION, BELOW_MIN_REGIME_CONFIDENCE, UNCERTAIN_REGIME, NO_BREAKOUT`.
