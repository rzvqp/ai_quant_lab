# ve_brain — CHANGELOG & compatibilitate declarată (gate 12)

## 0.1.0 — 2026-08-13 (predare inițială Mandat 1, pașii 1-4 + amendamente A1/A2/A5 + routing)
Contracte: `ve.decision_request.v1` / `ve.decision_response.v1` / `ve.strategy.v1`.
Contract de măsurare: `canonical-evaluator-v2.7.66-A2` — **v1.0-DRAFT, NOT RATIFIED**.

- **Inventariere (pasul 1):** N1-N4 + bus + motor EV (`bdd15e5`, count-table, NU tipuri de nivel) + runtime AI Trader
  (replay-only, izolat de turn) — din Git.
- **Contracte versionate (pasul 2):** `DecisionRequest`/`DecisionResponse` validate la runtime; version + fingerprint
  + reason_codes.
- **Pachet instalabil (pasul 3):** stdlib-only, versiune + commit sursă, scheme validate, compatibilitate controlată,
  upgrade/rollback, eroare explicită la incompatibilitate.
- **Adaptare motor EV (pasul 4):** `_ev_core` (byte-identic `bdd15e5`) + adaptor geometrie ACTUALĂ → `DecisionInput`;
  motor real (nu edge=bool); NO_TRADE determinist fără date/probabilități/strategie eligibilă.
- **A1 (SHADOW_ELIGIBLE):** ajunge la N6/EV → `SHADOW_TRADE_CANDIDATE`; `BROKER_ORDER_SUBMISSION=DISABLED`.
- **A2 (geometrie strictă):** corectiv în contractul de măsurare (`dc28e4a`) — risc≤0 OR recompensă≤0 → INVALID_EXECUTION.
- **A5 (T17):** `decision_fingerprint` peste date·config·strategie·motor·contract; `compare_decisions` RIDICĂ.
- **Routing per regim:** taxonomia 6-stări ← 4 axe N1; `StrategyRouter`/`EligibilityDecision`; BREAKOUT_WATCH;
  cele 12 teste de router + cauzalitate.

### Compatibilitate
Prima versiune — fără versiuni anterioare cu care să fie comparabilă. Rezultatele sub `-A2` sunt NON-COMPARABLE cu
cele sub varianta asimetrică (run_hash diferit prin CODE_VERSION).

### DESCHIS (blochează VE_HANDOFF_PASS)
- Contractul de măsurare NOT RATIFIED (Red Team, suita extinsă). BREAKOUT_TRANSITION strict cere un detector de
  tranziție 2-stări (semnalat). Verdictul PASS/FAIL îl dă Red Team, nu VE.
