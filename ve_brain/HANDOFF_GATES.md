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

## DESCHIS — de ce VE nu poate cere PASS
- Contractul de măsurare `canonical-evaluator-v2.7.66-A2` = **NOT RATIFIED** (Red Team, suită extinsă).
- **BREAKOUT_TRANSITION** e proxy per-bară; versiunea strictă cere un detector de tranziție 2-stări peste N1
  (SEMNALAT, neinventat — cere mandat).
- Verdictul îl dă Red Team. VE nu ratifică.
