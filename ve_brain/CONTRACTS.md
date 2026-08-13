# ve_brain — CONTRACTE PUBLICE (gate 3) — v0.1.1

**Artefact:** `ve_brain` v0.1.0 · **Sursă:** `ai_quant_lab-wp5b @ discovery-mk-matrix-v1 @ dc28e4a` (geometrie strictă A2)
**Contract de măsurare:** `canonical-evaluator-v2.7.66-A2` · **STATUT: v1.0-DRAFT — NOT RATIFIED** (Red Team ratifică în paralel).
**BROKER_ORDER_SUBMISSION = DISABLED** — artefactul produce DECIZII, niciodată ordine reale.

## Poarta N6 (FAIL-1): `decide_n6(candidate: DecisionRequest, eligibility: EligibilityDecision)`
Ordinea OBLIGATORIE: `N1 RawAxes → StrategyRouter → EligibilityDecision → StrategyCandidate → EV → N6 → Risk Manager`.
`eligibility` e OBLIGATORIE; N6 verifică `strategy_id/strategy_version/market_event_id/regime_fingerprint/router_version/
is_eligible`; lipsă/nepotrivire ⇒ `MISSING_OR_INVALID_ELIGIBILITY`; range ⇒ `TRUE_RANGE_NOT_IDENTIFIABLE`.

## Contract N1 ADITIV (FAIL-2): `RawAxes`
`is_compressed`, `is_displacement` (INDEPENDENTE, ne-mutual-exclusive), `direction`, `structure`, `volatility_state`
(rezumat — INTERZIS ca unică sursă), `n1_contract_version`, `raw_axis_schema_version`. Contract vechi ⇒ `INCOMPATIBLE_N1_CONTRACT`.

## Intrare — `DecisionRequest` (`ve.decision_request.v1`)
Câmpuri validate la runtime (nepotrivire ⇒ `SCHEMA_VALIDATION_FAILED`):
`contract_id, strategy_id, strategy_version, validation_status, market_event_id, regime_fingerprint, market_state_ref,
regime_label, bias_direction, market_map_available, levels_available, confirmation_available, entry_price, stop_price,
target_kind∈{rr,price,none}, target_param, holding_window≥1, atr>0, probability_inputs, full_spread_price,
entry_slippage_price, exit_slippage_price, symbol, timeframe, block_start≤block_end, segment_id, manifest_hash,
n1_contract_version, raw_axis_schema_version, router_version, eligibility_policy_version, measurement_contract_version,
configuration_fingerprint`. Populația oficială = **4 blocuri**.

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

## Taxonomia semantică — MULTI-AXIALĂ (post-decizia CEO pe range)
`applicable_regimes(vol, struct, dir)` întoarce o **MULȚIME** (fără precedență, fără partiție): o bară
COMPRESSED+STRONG+UP e SIMULTAN `{COMPRESSION, TREND_UP}` ⇒ activează AMBELE familii.
`COMPRESSION`←vol=compressed · `BREAKOUT_TRANSITION`←struct=range(flip)∧vol=high_directional ·
`TREND_UP`←struct∈{weak,strong}∧dir∈{up,weak_up} · `TREND_DOWN`←…{down,weak_down} · `UNCERTAIN`←axă absentă / fără potrivire.
- ⛔ **`RANGE` RETRAS** (DECIZIE CEO): `RANGE_STRATEGY_ROUTING=DISABLED`. `Direction.NEUTRAL` conflatează range real /
  lipsă de structură / WARMUP / fail-closed → RANGE e NEIDENTIFICABIL, NICIODATĂ produs. Strategiile care cer RANGE ⇒
  `eligible=FALSE`, `TRUE_RANGE_NOT_IDENTIFIABLE` (fail-closed, persistat). Dezambiguizarea = work item SEPARAT
  (câmpuri aditive `data_readiness` / `consolidation_state`, cu spec cauzală + preînregistrare + Red Team + CEO).
- ⚠ `BREAKOUT_TRANSITION` PĂSTRAT: folosește struct=range(|run|=1) ca dovadă de INSTABILITATE (flip proaspăt), NU de
  consolidare (warmup→struct Unavailable→UNCERTAIN, deci fără range) — utilizare semantic DIFERITĂ de cea interzisă.
  E proxy PER-BARĂ; versiunea strictă cere detectorul de tranziție 2-stări peste N1 — SEMNALAT, neinventat.

## Amprenta (T17/A5) — `configuration_fingerprint`
`sha256(config_hash ‖ sha256(data_identity))` la nivel de măsurare, apoi `decision_fingerprint` peste
**date · config · STRATEGIE · MOTOR · versiunea contractului**. `compare_decisions()` RIDICĂ pe nepotrivire.

## Reason codes
`TRADE_VALIDATED_EDGE, SHADOW_CANDIDATE_EV_POSITIVE, NO_ELIGIBLE_STRATEGY, MISSING_LEVEL_INPUT,
MISSING_CONFIRMATION, MISSING_PROBABILITY_INPUTS, NEGATIVE_EXPECTED_VALUE, INCOMPATIBLE_CONTRACT,
SCHEMA_VALIDATION_FAILED, INVALID_EXECUTION, STOP_BELOW_MINIMUM, ROUTER_ELIGIBLE, ROUTER_BREAKOUT_ARMED,
INELIGIBLE_REGIME, INELIGIBLE_DIRECTION, BELOW_MIN_REGIME_CONFIDENCE, UNCERTAIN_REGIME, NO_BREAKOUT`.
