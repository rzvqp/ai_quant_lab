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
| 6 | teste unitare + contractuale | ✅ | `tests/test_router_and_n6.py` (c01–c21 + FAIL-2 + A5) + evaluator (24) |
| 7 | fixture-uri canonice cu rezultate cunoscute | ✅ | `tests/test_fixtures_canonical.py` (EV known-outcome, calea completă) |
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

## Corecția VE_HANDOFF_CONDITIONAL + AUTO-ATAC (o singură reparație de la PASS)
A patra instanță a tiparului: `EligibilityDecision` + candidatul pot fi construite MANUAL cu ID-uri POTRIVITE
(is_eligible=TRUE, reason=ROUTER_ELIGIBLE) → range strategy returna TRADE. Remediul NU e un bool (falsificabil).

| închidere | mecanism | dovadă |
|---|---|---|
| proprietatea strategiei = sursă CANONICĂ, nu câmp al candidatului | `StrategyRegistry` (cheie `(id,version)`, imuabil per cheie); N6 rezolvă contractul din registru și recalculează `strategy_policy_fingerprint`; nepotrivire → `STRATEGY_POLICY_MISMATCH` | `test_c04/c05/c11/c13` |
| `requires_true_range` citit DIN REGISTRU, blocaj INDEPENDENT de reason_codes/is_eligible/EV | `decide_n6` aplică `TRUE_RANGE_NOT_IDENTIFIABLE` înainte de eligibilitate/EV, pe baza `allowed_regimes` din registru | `test_c01/c02/c03/c12` (fixture DECISIV: range, matching IDs, is_eligible=TRUE, EV+ → NO_TRADE) |
| **AUTO-ATAC 1: registrul nu poate fi injectat ca parametru** | `decide_n6(candidate, eligibility)` NU ia `registry` ca parametru; sursa canonică e internă; amprenta de politică se RECALCULEAZĂ din ea, nu se citește din obiectul primit | (istoric — vezi mai jos) |

## A 6-A SUPRAFAȚĂ (verdict Red Team, închisă înainte de predare): consumatorul nu poate DEFINI conținutul catalogului
Reproductibil: `register_canonical_strategy` era PUBLIC, registrul pornea GOL, primul care înregistra câștiga →
consumatorul înregistra `range_fade` ca TREND ⇒ `requires_true_range=False`, candidatul oglindea politica otrăvită ⇒
niciun `STRATEGY_POLICY_MISMATCH` ⇒ TRADE. `test_c16` prindea doar un candidat mincinos contra unui registru CORECT,
nu otrăvirea registrului însuși.

| închidere | mecanism | dovadă |
|---|---|---|
| **catalog CANONIC intern, versionat + SIGILAT** | `_canonical_catalog.py` — definiții APROBATE ca literali Python încorporați (fără fișier/mediu/rețea); `SealedRegistry.build()` sigilează + amprentă de integritate `content_hash`; N6 rezolvă proprietatea de aici | `test_c02/c03/c17`, `test_c21` (integritate) |
| **N6 REFUZĂ catalog nesigilat / versiune nepotrivită** | `decide_n6` verifică `sealed` + `catalog_version`/`content_hash` contra constantelor APROBATE încorporate → `CATALOG_NOT_SEALED` / `CATALOG_VERSION_MISMATCH` | `test_c18`, `test_c19` |
| **API-ul de definire arbitrară ELIMINAT din producție** | `register_canonical_strategy` / `reset_canonical_registry` / `set_registry_available` NU mai există pe `ve_brain`; hook-urile de fault sunt izolate în `ve_brain.testing`, blocate până la `unlock_for_tests(TOKEN)`; niciun modul de producție nu le importă | `test_c16` (absente din API + `decide_n6` are 2 params), `test_c20` (blocate fără unlock) |

**Principiul:** AI Trader NU poate defini `strategy_family`·`allowed_regimes`·`requires_true_range`·`validation_status`·
`strategy_policy_fingerprint` pentru o strategie canonică. Poate CERE încărcarea unei strategii aprobate; nu poate
decide conținutul ei. Proces corect: Alpha propune → validare → SHADOW_ELIGIBLE/RATIFIED → catalog versionat → VE
verifică → deployment controlat → catalog sigilat → N6 consumă.

**Auto-atac pe catalogul sigilat (cele 4 întrebări):** sigiliul nu se poate rupe+re-aplica în producție (`build()`
sigilat / `unsealed()` doar test-only gate-uit; un swap monkeypatch e prins de verificarea versiune+amprentă);
versiunea aprobată = constante încorporate (forjarea = rescrierea modulului, în afara contractului); entrypoint-ul de
test e izolat, gate-uit și neimportat de producție (`test_c20`); catalogul nu se încarcă din nicio sursă controlată de
consumator (literali, verificat: fără open/env/rețea). Monkeypatch-ul globalelor private rămâne în afara contractului.
Închis ÎNAINTE de predare, nu lăsat pentru Red Team.

**Inventarul căilor de comparație (A5):** în artefactul `ve_brain` NU există cod intern de leaderboard / selecție de
candidați / agregare de rapoarte — pachetul PRODUCE decizii, nu le compară. UNICA cale de comparație e
`compare_decisions()` (guard care RIDICĂ). Comparația directă a câmpurilor de amprentă e interzisă prin contract.
Calea COMPLETĂ e demonstrată de `test_full_path_n1_router_eligibility_ev_n6` (nu componente izolate).

## MANIFESTUL DE PIN (handoff tehnic — schema v1.0, 10 câmpuri, machine-readable + imuabil)
Emis DIRECT din constantele vii ale artefactului prin `ve_brain.artifact_manifest(delivery_commit)`; livrat ca
`ARTIFACT_MANIFEST.json`. AI Trader îl obține din pachetul INSTALAT (nu copiază din conversație, nu inventează, nu None).

**Cele TREI identități, SEPARATE (corecție de schemă — un câmp nu poate reprezenta două):**
- `measurement source = dc28e4a` — sursa contractului de măsurare (`version.SOURCE_COMMIT`, câmp DIFERIT).
- `validated_core_commit = fbc0f20` — nucleul brain verificat de Red Team (raport 46c462c). Constantă STABILĂ.
- `source_commit = <delivery>` — commitul EXACT din care AI Trader instalează pachetul. Furnizat de instalator
  (`git rev-parse HEAD` din propriul checkout) — un commit nu poate conține propriul hash, deci NU e literal încorporat;
  `artifact_manifest()` îl cere EXPLICIT și eșuează închis dacă lipsește.

| câmp | sursă | valoare |
|---|---|---|
| manifest_schema_version | `MANIFEST_SCHEMA_VERSION` | `1.0` |
| package_version | `VE_BRAIN_VERSION` | `0.1.3` |
| source_commit | `delivery_commit` (instalator) | commitul de livrare |
| validated_core_commit | `VALIDATED_CORE_COMMIT` | `fbc0f20` |
| catalog_version | `CANONICAL_CATALOG_VERSION` | `ve-canonical-catalog-v1` |
| catalog_hash | `CANONICAL_CATALOG_HASH` | `37b95393df85dc2b` |
| measurement_contract_version | `MEASUREMENT_CONTRACT_VERSION` | `canonical-evaluator-v2.7.66-A2` |
| n1_contract_version | `N1_CONTRACT_VERSION` | `n1-additive-raw-axes-v1` |
| router_version | `ROUTER_VERSION` | `router-v1` |
| ev_engine_version | `ENGINE_VERSION` | `ev-core@bdd15e5+ev-adapter-v1` |

`manifest_schema_version` fixează semantica câmpurilor ca IMUABILĂ + VERIFICABILĂ. Cele 8 valori derivate rămân
byte-identice cu fbc0f20: `git diff fbc0f20` atinge doar fișiere de manifest — `version.py`/`_canonical_catalog.py`/
`ev_engine.py` neatinse. `test_manifest.py` (5 teste) demonstrează separarea celor 3 identități, fail-closed pe
delivery_commit lipsă, și legarea JSON↔emitent. Versiunea rămâne 0.1.3 ca manifestul să corespundă EXACT nucleului
PASS-uit.

## DESCHIS — de ce VE nu poate cere PASS
- Contractul de măsurare `canonical-evaluator-v2.7.66-A2` = **NOT RATIFIED** (Red Team, suită extinsă).
- **BREAKOUT_TRANSITION** e proxy per-bară; versiunea strictă cere un detector de tranziție 2-stări peste N1
  (SEMNALAT, neinventat — cere mandat).
- Verdictul îl dă Red Team. VE nu ratifică.
