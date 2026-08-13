# ve_brain — STATUTUL GATE-URILOR DE PREDARE

Red Team emite `VE_HANDOFF_PASS` sau `VE_HANDOFF_FAIL`. VE NU-și declară singur PASS. Amendamentele CEO (A2 geometrie
strictă + routing per regim) sunt OBLIGATORII înainte de PASS — ambele aplicate mai jos.

## Cele 12 gate-uri inițiale
| # | gate | statut | dovadă |
|---|---|---|---|
| 1 | artefact instalabil + versionat | ✅ | `pyproject.toml` v0.1.0, `version.py`, `INSTALL.md` |
| 2 | commit-ul sursă exact | ✅ | `SOURCE_COMMIT=3344bff`, `build_info()` |
| 3 | documentul contractelor publice | ✅ | `CONTRACTS.md` |
| 4 | schema fiecărui input/output | ✅ | `contracts.py` + `validate_request/response` |
| 5 | adaptorul EV vechi → contract actual | ✅ | `ev_engine.py` (matricea de adaptare + adaptor) |
| 6 | teste unitare + contractuale | ✅ | `tests/test_router_and_n6.py` (19) + evaluator (24) |
| 7 | fixture-uri canonice cu rezultate cunoscute | ✅ | `tests/fixtures_canonical.py` (EV known-outcome) |
| 8 | lista dependențelor | ✅ | `DEPENDENCIES.md` (stdlib-only) |
| 9 | instalare/upgrade/rollback | ✅ | `INSTALL.md` |
| 10 | dovada că EV nu mai folosește nivelurile vechi | ✅ | `_ev_core` zero importuri proiect + byte-identic `bdd15e5` |
| 11 | NO_TRADE determinist fără strategie validată | ✅ | `test_n6_experimental_status_no_eligible_strategy`, `..._no_probability_inputs...` |
| 12 | changelog + compatibilitate | ✅ | `CHANGELOG.md` |

## Adăugat de amendamentul de routing
| item | statut | dovadă |
|---|---|---|
| RegimeState (semantic) | ✅ | `semantic_regime()` — 6 stări ← 4 axe N1 |
| StrategyRegistry | ✅ | `regime_routing.StrategyRegistry` |
| StrategyRouter | ✅ | `regime_routing.StrategyRouter` |
| EligibilityDecision + reason_codes | ✅ | `EligibilityDecision` + `reason_codes.py` |
| testele de cauzalitate | ✅ | test 09 (fără lookahead), fingerprint include N1+regulile |
| cele 12 teste de router | ✅ | `test_01..test_12` |

## Cele 5 condiții de range (DECIZIE CEO — VE_HANDOFF_PASS nu e blocat de absența range-ului dacă:)
| # | condiție | statut | dovadă |
|---|---|---|---|
| 1 | strategiile de range sunt fail-closed | ✅ | `test_range_cond1_fail_closed` (orice piață) |
| 2 | StructBand.RANGE și Direction.NEUTRAL NU le pot activa | ✅ | `test_range_cond2_...` (RANGE niciodată în applicable) |
| 3 | reason code-ul e PERSISTAT | ✅ | `test_range_cond3_reason_persisted` = `TRUE_RANGE_NOT_IDENTIFIABLE` |
| 4 | celelalte familii funcționează | ✅ | `test_range_cond4_other_families_work` (trend/compression/breakout) |
| 5 | NU există fallback / rutare implicită către range | ✅ | `test_range_cond5_...` + `applicable_regimes` nu produce RANGE |

Router MULTI-AXIAL (fără regulă globală de precedență): `test_12_multiaxial_...` — COMPRESSION+TREND simultan.

## Corecții VE_HANDOFF_FAIL (verdict Red Team ACCEPTAT)
| defect | corecție | dovadă |
|---|---|---|
| **FAIL-1** router ocolibil (N6 fără eligibility → TRADE) | `decide_n6(candidate, eligibility)` — eligibility OBLIGATORIE; verifică strategy_id/version/market_event_id/regime_fingerprint/router_version/is_eligible; lipsă/nepotrivire → `MISSING_OR_INVALID_ELIGIBILITY`; range → `TRUE_RANGE_NOT_IDENTIFIABLE`. Fără semnătură legacy. | `test_f1_01..10` |
| **FAIL-2** partiția mutată în stringul de volatilitate | contract N1 ADITIV: `RawAxes.is_compressed`/`is_displacement` INDEPENDENTE; `volatility_state` doar telemetrie; router citește axele brute; `INCOMPATIBLE_N1_CONTRACT` la contract vechi. | `test_f2_01..10` |
| **A5** identitate + enforcement | `data_identity` (symbol/timeframe/block_start/end/segment_id/manifest_hash, 4 blocuri) în amprentă; amprenta acoperă date‖config‖strategie‖motor‖contract‖N1‖router; `compare_decisions` RIDICĂ. | `test_a5_*` |
| **FAIL-4** re-pin | `SOURCE_COMMIT=dc28e4a`, `MEASUREMENT_CONTRACT_VERSION=…-A2` (NU asimetricul 3344bff). | `version.py` |

**Inventarul căilor de comparație (A5):** în artefactul `ve_brain` NU există cod intern de leaderboard / selecție de
candidați / agregare de rapoarte — pachetul PRODUCE decizii, nu le compară. UNICA cale de comparație e
`compare_decisions()` (guard care RIDICĂ). Comparația directă a câmpurilor de amprentă e interzisă prin contract.
Calea COMPLETĂ e demonstrată de `test_full_path_n1_router_eligibility_ev_n6` (nu componente izolate).

## DESCHIS — de ce VE nu poate cere PASS
- Contractul de măsurare `canonical-evaluator-v2.7.66-A2` = **NOT RATIFIED** (Red Team, suită extinsă).
- **BREAKOUT_TRANSITION** e proxy per-bară; versiunea strictă cere un detector de tranziție 2-stări peste N1
  (SEMNALAT, neinventat — cere mandat).
- Verdictul îl dă Red Team. VE nu ratifică.
