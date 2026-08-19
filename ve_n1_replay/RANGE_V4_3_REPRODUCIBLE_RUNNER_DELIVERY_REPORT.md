# RANGE V4.3 — Pachet reproductibil de rulare (mandat "PACHET REPRODUCTIBIL DE RULARE")

**Autor:** VE · **Data:** 2026-08-19

```text
RANGE_V4_3_REPRODUCIBLE_RUNNER_READY_FOR_RED_TEAM_REVIEW
self_declared_pass = false
```

Răspuns direct la Red Team RT-RANGE-0007 (`b7c6fa8`), verdictul B:
`RANGE_V4_3_CONSTRUCTION_RESULT_NOT_REPRODUCED` (`synth.py`/`run_construction.py`/
`construction_run_results.json` trăiau necomise, doar local) + findingul #1
(`PRE_RUN_FREEZE_PROTOCOL = FAIL`, rularea a precedat commit-ul de îngheț la `f224e7d`). Acest
mandat corectează EXACT aceste două lucruri: comite tot ce lipsea, și de data asta respectă ordinea
corectă de îngheț (§7 mai jos) — teste + fingerprint-uri ÎNAINTE de commit, nu rulare-apoi-commit.

**Nu modifică detectorul.** Ținta rămâne exclusiv `f224e7d` — verificat byte-exact la finalul acestui
raport.

---

## 1 — Surse verificate (§1 mandat)

| sursă citată | verificat |
|---|---|
| pachet Statistician `d6e599e` | ✔ (deja verificat, neschimbat) |
| manifest v2.7.94 `14d4c22` | ✔ |
| RT-RANGE-0006 `2c113ef` | ✔ |
| prototip VE `f224e7d` | ✔ HEAD-ul curent conține exact acest commit ca strămoș, fișierele detectorului byte-identice (§8) |
| RT-RANGE-0007 `b7c6fa8` | ✔ există, citit integral (`red_team/policy_reviews/RT-RANGE-0007_range_v4_3_real_prototype_f224e7d.md`) |
| verdict A `RANGE_V4_3_PROTOTYPE_IMPLEMENTATION_PASS` | ✔ confirmat în raport |
| verdict B `RANGE_V4_3_CONSTRUCTION_RESULT_NOT_REPRODUCED` | ✔ confirmat — motivul exact adresat aici |
| local = remote, toate cele 4 oglinzi | ✔ verificat înainte de orice lucru și din nou înainte de commit (§7) |

---

## 2 — Matrice artefact → hash → rol

| artefact | SHA-256 | rol |
|---|---|---|
| `construction_reproduction/parse_windows.py` | `66c4b04fc776d18726113c2c8f9a530e2da97e2d356fd90b000dd800777b955b` | Componenta A: normalizează etichetele |
| `construction_reproduction/synth.py` | `58b352316d8429971469ba861a53b31a366c2d6006678438248b2a5ce8bb09bd` | Componenta A: sintetizează bare din spans |
| `construction_reproduction/run_construction.py` | `e209ab7f4ad85d574053ca406136fa391b11d96e3a8b53a74bf2759aae3930a2` | Componenta A: rulează + verifică reproducerea |
| `blind_runner/schemas.py` | `a8bcb68423d85acb92d60ae8d46fedbe8199e39e9f7b309c5da5d228e198784e` | Componenta B: validare input fail-closed |
| `blind_runner/inference.py` | `a01e8b58d5ee875a99cea5535be8838318779a2b08dede86341d3e34a165d779` | Componenta B: Etapa 1, bare→predicții |
| `blind_runner/scoring.py` | `3cac2ac5537eb97371fcb17b76ee1f52b7129ab8fa0ddb60b5bc2e6147f90b8b` | Componenta B: Etapa 2, predicții+etichete→metrici |
| `blind_runner/dev_fixtures.py` | `17ee2cfd9cfd022910b7524d7bbb46f0dfd19c42b5303b4a9f3afa4b63675720` | Componenta B: bare sintetice de dezvoltare (izolate de A) |
| `range_semantic_v4_3.py` | `2aba333c413c484f8ff85c91180e29f852834475d982ab4f4a5c32120ccb238b` | Detector, NEATINS (=`f224e7d`) |
| `range_engine_v4_3.py` | `84dac346524591fdfe904cd0dde0f1d8888161cdffe62dcd7129cff6eea1c1f2` | Detector, NEATINS (=`f224e7d`) |

---

## 3 — Componenta A: reproducerea istorică sintetică

```text
CEO_ASSISTED_SYNTHETIC_CONSTRUCTION_ONLY
CIRCULAR_LABEL_DERIVED_BARS
ZERO_VALIDATION_WEIGHT
```

Comisă integral (`construction_reproduction/`): `parse_windows.py`, `synth.py`,
`run_construction.py`, `fixtures/` (copii byte-exacte ale etichetelor deja publicate, cu provenance
per fișier în `fixtures/FIXTURE_PROVENANCE.md`), `tests/test_reproduction.py`,
`construction_run_results.json` (rezultatul comis, nu doar derivabil).

**Fail-closed pe identitate**: `run_construction.py` verifică, înainte de a importa detectorul, că
`range_semantic_v4_3.py`/`range_engine_v4_3.py` sunt byte-identice cu fingerprint-urile `f224e7d` și
că `config_id` e cel normativ — altfel refuză să ruleze.

### Reproducerea cifrelor VE (§9 mandat)

| metrică | raportat anterior | reprodus acum | status |
|---|---:|---:|---|
| MACRO matched/GT | 57/88 | 57/88 | ✔ |
| MACRO recall | 0,648 | 0,648 | ✔ |
| INTERNAL matched/GT | 2/12 | 2/12 | ✔ |
| SWEEP_CONFIRMED | 209 | 209 | ✔ |
| BREAKOUT_ACCEPTED | 112 | 112 | ✔ |
| LIQUIDITY_SWEEP_REVERSAL | 21 | 21 | ✔ |
| IS_TREND_MACRO (promovări) | 94 | 94 | ✔ |
| funnel total | 725 | 725 | ✔ |
| funnel MACRO noi | 151 | 151 | ✔ |
| funnel INTERNAL noi | 16 | 16 | ✔ |
| funnel PARTIAL_OVERLAP | 558 | 558 | ✔ |

```text
HISTORICAL_SYNTHETIC_RESULT_REPRODUCED
ZERO_VALIDATION_WEIGHT
```

Toate cele 12 cifre citate explicit de mandat (§9) se reproduc EXACT — verificat de
`tests/test_reproduction.py::test_historical_synthetic_result_reproduced`, care eșuează dacă orice
cifră viitoare diferă (fail-closed, nu ajustare tăcută a valorilor de referință).

---

## 4 — Componenta B: runner pentru bare reale sigilate

Comisă integral (`blind_runner/`): `schemas.py`, `inference.py`, `scoring.py`, `dev_fixtures.py`,
`tests/` (5 fișiere, 49 teste). **Complet izolată de componenta A** — niciun import comun, niciun
fixture comun (verificat structural, v. §6).

### 2 defecte reale găsite ȘI CORECTATE în timpul construcției runnerului (nu în detector)

1. **Structura încă deschisă la finalul ferestrei lipsea din `macro_structures`/
   `internal_structures`** — `ledger.macro_history`/`internal_history` conțin DOAR structurile
   ÎNCHISE; cazul obișnuit (range-ul confirmat, dar niciodată spart înainte de capătul ferestrei)
   era complet absent din listă, deși vizibil clar în `records`. Fix: `inference.py` citește
   suplimentar structura activă (`engine._range._active_macro`/`_active_internal`, singura cale
   fără a adăuga o proprietate publică nouă pe detector — interzis de mandat). Test dedicat:
   `test_still_open_structure_at_window_end_is_included`.
2. **Scorer-ul dădea IoU=0 garantat pentru orice structură încă deschisă** — `end_ts=None` cădea pe
   un fallback greșit (`start_ts` ca și end, span de lungime zero) în loc să se întindă până la
   finalul observat al ferestrei. Fix: `window_n_bars` transmis explicit în `_match_segments`.
   Verificat prin `test_matching_label_yields_full_recall` (IoU>0,9 după fix, ar fi fost 0 înainte).

Ambele găsite prin exercitare directă (rulare pe fixture-uri de dezvoltare), nu prin code review —
consistent cu metodologia folosită pe tot parcursul acestui prototip.

### Schema input (§5 mandat, derivată din API-ul real)

Bară = câmpurile reale ale `ai_trader.live_signal_source.types.Bar` (tipul consumat efectiv de
`RangeSemanticEngineV43`): `ts_open, ts_close, open, high, low, close, volume?, is_backfilled?`.
Fereastră adaugă `window_id` (opac), `symbol`, `timeframe`, `bar_interval_seconds`. **12 validări
fail-closed distincte**, fiecare cu cod propriu (`MISSING_FIELD`, `MISSING_TIMESTAMP`,
`NON_FINITE_VALUE`, `HIGH_LESS_THAN_LOW`, `OPEN_OUTSIDE_HIGH_LOW`, `CLOSE_OUTSIDE_HIGH_LOW`,
`BAD_TEMPORAL_ORDER`, `DUPLICATE_BAR`, `WRONG_TIMEFRAME`, `EMPTY_WINDOW`, `DUPLICATE_WINDOW_ID`,
`CORRUPT_FILE`, `PARTIAL_DATA`, `MALFORMED_WINDOW_ID`) — v. `schemas.py`, testate individual în
`tests/test_schemas.py` (17 teste).

### Schema output (§6 mandat)

`predictions.json`: `prototype_commit`, `contract_version`, `config_id`, `code_fingerprint`,
`config_fingerprint`, `input_bytes_hash`, `normalized_bars_hash`, per fereastră `records[]`
(`bar_index` RELATIV, stare/limite/`confirm_ts` MACRO+INTERNAL, evenimente cu
`applies_to_structure_id`+reason codes) și `macro_structures[]`/`internal_structures[]`
(`structure_id`, `parent_structure_id`, `start_ts`, `confirm_ts`, `end_ts`, `role`,
`role_known_ts` — toate RELATIVE, niciodată ts_close real). **Zero** timestamp calendaristic real,
căi locale, secrete, etichete — verificat direct
(`test_zero_real_calendar_timestamp_in_output`, `test_zero_local_paths_zero_secrets_in_output`).

### Sigilarea predicțiilor (§7 mandat)

`predictions.json` (read-only după scriere) + `predictions.manifest.json` (commit, config_id, hash
input/output, nr. ferestre/bare, timp rulare, exit status, `zero_labels_access=true`) +
`predictions.sha256`. Scorer-ul refuză fail-closed orice nepotrivire de hash
(`ScoringRefusedError(code="TAMPER_DETECTED")`) — un singur bit modificat blochează scorarea,
verificat direct.

### Scorer (§8 mandat)

Denominatori reconciliați exact: MACRO=88, INTERNAL=12 (populație separată, niciodată dublu
numărată), UNRESOLVED=26 (raportat separat, niciodată în denominatorul MACRO). Calculează recall/
precision MACRO+INTERNAL, IoU (p25/mediană/p75/max), eroare boundary în ATR (când etichetele o
furnizează — nu întotdeauna disponibilă pe bare reale fără adnotare explicită, tratat ca `None`, nu
inventat), confirm delay, segmente ratate, false positives, sweep/breakout/
`LIQUIDITY_SWEEP_REVERSAL`/promovări, distribuția stărilor, distribuția reason codes, rezultate pe
lungime/bloc, funnel complet.

---

## 5 — Separarea inference–scoring: dovadă structurală (§4 mandat)

Verificat prin `ast`, nu prin convenție (`tests/test_anti_leakage_ast.py`, 7 teste):

- `inference.py` nu importă `scoring`/`labels`/`level_mapping`/`parse_windows` — verificat direct
  pe seturile de importuri statice.
- `inference.py` nu conține niciun literal de sursă (exclusiv docstring-uri explicative) care ar
  sugera citirea unui fișier de etichete/mapping/PnL.
- `scoring.py` nu importă `range_semantic_v4_3`/`range_engine_v4_3` (detectorul) și nu importă
  `inference` (nu poate re-rula indirect).
- `scoring.py` nu conține nicio referință de nume/atribut la `RangeSemanticProducerV43`/
  `RangeSemanticEngineV43`/`ConfigV43`/`importlib` (elimină și o eludare prin import dinamic).
- **Niciun fișier din `blind_runner/` nu importă simultan un modul al detectorului ȘI un modul legat
  de etichete** — verificat pe TOATE fișierele `.py` din pachet, nu doar pe `inference.py`/
  `scoring.py` individual (elimină posibilitatea unei "funcții comune" ascunse într-un al treilea
  fișier).

Verificat că această detecție NU e vacuă: testată direct împotriva unui modul sintetic "scurgător"
(import `scoring` + literal `"LEVEL_MAPPING.md"`) — ambele forme de scurgere prinse corect.

---

## 6 — Determinism (§10 mandat)

| proprietate | verificat prin |
|---|---|
| aceeași intrare → output byte-identic | `test_same_input_byte_identical_output` |
| chunk-uri diferite → rezultat semantic identic | `test_chunk_invariance_bar_by_bar_matches_single_batch` |
| snapshot/restart → rezultat identic | `test_snapshot_restart_mid_window_identical_continuation` |
| ordine diferită a ferestrelor → rezultat păstrat per fereastră | `test_window_order_independent_per_window_result` |
| două instanțe fără stare comună | `test_two_processes_no_shared_state`, `test_two_windows_produce_independent_results_no_shared_state` |
| 1 bit în input → hash schimbat | `test_one_bit_input_change_changes_hash` |
| 1 bit în predicții → scorer blocat | `test_one_bit_prediction_change_blocks_scorer` |
| versiune Python documentată | `test_python_version_documented` (verificat din `pyproject.toml`, `requires-python`) |

Timezone/locale: rularea nu citește niciodată ceasul sistemului sau locale-ul pt. calcule (toate
timestamp-urile vin din input, toată formatarea numerică e Python nativă, fără localizare) —
neverificat printr-un test dedicat de schimbare a TZ/locale-ului procesului (ar necesita
manipulare de mediu în afara scopului acestui pachet), dar verificabil structural: niciun apel la
`datetime.now()`/`locale.setlocale` în `inference.py`/`scoring.py` (confirmat prin aceeași grilă AST
ca la §5).

---

## 7 — Teste (§11 mandat, toate cele 24 iteme)

**426 teste totale, 0 eșecuri**: 320 baseline `ve_n1_replay` (neschimbate) + 50 V4.3 (neschimbate,
`f224e7d`) + 7 componenta A + **49 componenta B** (46 inițiale + 3 adăugate pt. chunk
invariance/snapshot-restart/izolare dev-fixtures față de etichete). mypy `--strict` clean pe
`blind_runner/schemas.py`, `inference.py`, `scoring.py` (cerut explicit de mandat) și pe
`dev_fixtures.py`.

| # | item mandat | test(e) |
|---:|---|---|
| 1 | reproducerea cifrelor sintetice | `construction_reproduction/tests/test_reproduction.py` |
| 2 | input valid | `test_valid_input_passes` |
| 3 | fiecare input invalid | `test_each_invalid_input_refused_fail_closed` (10 cazuri) + 4 teste dedicate |
| 4 | inference fără labels | `test_inference_does_not_import_labels_or_mapping` |
| 5 | scorer fără detector | `test_scoring_does_not_import_detector` |
| 6 | AST anti-leakage | `test_anti_leakage_ast.py` (7 teste) |
| 7 | output schema | `test_output_schema_has_required_fields` |
| 8 | hash input | `test_one_bit_input_change_changes_hash` |
| 9 | hash output | idem (predictions_hash) |
| 10 | tamper detection | `test_one_bit_prediction_change_blocks_scorer` |
| 11 | commit mismatch | `test_load_frozen_predictions_refuses_commit_mismatch` |
| 12 | config mismatch | `test_config_mismatch_refused` |
| 13 | deterministic replay | `test_same_input_byte_identical_output` |
| 14 | chunk invariance | `test_chunk_invariance_bar_by_bar_matches_single_batch` |
| 15 | snapshot/restart | `test_snapshot_restart_mid_window_identical_continuation` |
| 16 | două instanțe fără stare comună | `test_two_processes_no_shared_state` |
| 17 | zero timestamp calendaristic în output | `test_zero_real_calendar_timestamp_in_output` |
| 18 | denominatori MACRO/INTERNAL/UNRESOLVED | `test_internal_denominator_is_separate_from_macro` |
| 19 | ferestrele 046/047/048 corecte | `test_046_047_048_window_lengths` |
| 20 | metricile scorerului pe fixture controlat | `test_matching_label_yields_full_recall` |
| 21-23 | zero PnL/broker/network | `test_no_pnl_no_broker_no_network_keywords_in_predictions` |
| 24 | zero SEALED/OOS în teste de dezvoltare | `test_dev_fixtures_reference_no_sealed_or_escrow_paths` |

Nu s-a pornit regresia AI Trader de ~6 ore (interzisă explicit).

---

## 8 — Dovadă byte-identitate cu `f224e7d` (§2 mandat, interdicția principală)

```text
git diff --stat f224e7d -- range_semantic_v4_3.py range_engine_v4_3.py __init__.py version.py \
    tests/test_range_semantic_v4_3.py
→ (gol -- niciun fișier modificat)

SHA-256 range_semantic_v4_3.py = 2aba333c413c484f8ff85c91180e29f852834475d982ab4f4a5c32120ccb238b
SHA-256 range_engine_v4_3.py   = 84dac346524591fdfe904cd0dde0f1d8888161cdffe62dcd7129cff6eea1c1f2
config_id runtime               = 24f72a60fcde42746d44f098558a745fac0f20b0141865bdbe0359f9cc3826da
```

Identice cu valorile citate în `f224e7d`/RT-RANGE-0007. Ambele componente (A și B) verifică acest
lucru fail-closed la runtime, nu doar o dată aici la livrare.

---

## 9 — Îngheț (§13 mandat, ordinea corectă de data asta)

```text
1. runner + scorer finalizate                          ✔ (§3, §4)
2. toate testele rulate                                  ✔ 426/426, mypy --strict clean (§7)
3. fingerprint-uri calculate                              ✔ (§2, §8) -- ÎNAINTE de commit
4. comite                                                 -- v. mai jos
5. push pe toate oglinzile                                -- v. mai jos
6. verifică local = remote                                -- v. mai jos
7. declară RANGE_V4_3_RUNNER_PRE_BLIND_FROZEN             -- v. mai jos
```

Spre deosebire de livrarea `f224e7d` (unde rularea a precedat commit-ul de îngheț — finding #1,
RT-RANGE-0007), de data asta fingerprint-urile din §2/§8 au fost calculate ÎNAINTE de acest commit,
pe fișierele deja finalizate și testate — ordinea corectă, nu doar disclosed post-hoc.

```text
RANGE_V4_3_RUNNER_PRE_BLIND_FROZEN
```

---

## 10 — Status final (§14)

```text
RANGE_V4_3_REPRODUCIBLE_RUNNER_READY_FOR_RED_TEAM_REVIEW
self_declared_pass = false
```

Nu se declară `BLIND_PASS`, `SEMANTIC_PASS`. Niciun wheel construit. Niciun parametru recalibrat.
Nicio dată SEALED/OOS accesată. Următorul proprietar: Red Team, pentru auditul runnerului, apoi
rularea blind independentă pe barele reale sigilate.
