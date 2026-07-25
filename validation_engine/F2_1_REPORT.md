# F2.1 — RAPORT DE LIVRARE
### Rezolvarea golurilor G1 și G2 · Capability Registry v1.1 · decizia JSON-only (A1)

**Document ID:** VE-F21-REPORT-v1.0
**Data:** 2026-07-24 · **Autor:** Validation Engine
**Autoritate:** decizie CEO 2026-07-24, pe `REGISTRY_GAPS_G1_G2_ANALYSIS.md` §6 și pe backlog A1/A5/A6/A7
**Statut:** livrat, în așteptarea aprobării. **F3 nu a fost început. Nicio metodă statistică nu a fost implementată. Nicio dată de piață nu a fost citită.**

---

## 1. Fișiere create, modificate și șterse

Toate sub `ai_quant_lab/validation_engine/`. **Niciun fișier din afara acestui director nu a fost atins.**

### Create (5)

| Fișier | Linii | Rol |
|---|---|---|
| `CAPABILITY_REGISTRY_v1.1.md` | 225 | catalogul publicat, versiunea 1.1 |
| `SPEC_TEMPLATE_v1.1.json` | 131 | șablonul oficial, JSON |
| `tests/fixtures/reference_spec_dc0004.json` | 376 | specificația de referință — transcrierea designului DC-0004 |
| `tests/test_reference_spec.py` | 145 | dovada de acoperire a designului |
| `F2_1_REPORT.md` | — | acest document |

### Modificate (8)

| Fișier | Modificare |
|---|---|
| `capabilities.json` | registrul v1.0 → v1.1 (detaliat în §2) |
| `ve/spec/domains.py` | `statistic_call` adăugat în tipurile de referință (pasul 1 al ordinii impuse) |
| `ve/spec/registry_validator.py` | rezolvarea `statistic_call`; verificarea câmpului `raw_series@v1` față de coloanele declarate ale sursei |
| `ve/spec/loader.py` | mesajul de refuz YAML reformulat din limitare de mediu în decizie de politică |
| `SPEC_SCHEMA_v1.0.md` | JSON-only în §1; exemple rescrise în JSON; secțiuni noi pentru `raw_series@v1` și `statistic_call`; §8 actualizat |
| `tests/fixtures/fixture_baseline_spec.json` | registru 1.1; statistica devine apel parametrizat |
| `tests/mutations.py` | M40 adaptată; **M54–M60 adăugate** (7 mutații noi pentru G1/G2) |
| `tests/conftest.py`, `tests/test_schema_and_registry.py` | fixtura specificației de referință; 8 teste noi de invarianți v1.1 și JSON-only |

### Șterse (1)

| Fișier | Motiv |
|---|---|
| `SPEC_TEMPLATE_v1.0.yaml` | decizia JSON-only (A1). Un șablon într-un format pe care motorul îl refuză ar fi contrazis documentația corectată. Adnotările lui sunt preluate integral în `SPEC_SCHEMA_v1.0.md` §3 |

**Nemodificate, deliberat:** `SPEC_SCHEMA_v1.0.json` (extinderea vocabularului nu cere versiune nouă de schemă — invariantul F1), `VALIDATION_ENGINE_ARCHITECTURE_v1.0.md`, `CAPABILITY_REGISTRY_v1.0.md` (păstrat ca istoric), `F2_REPORT.md`, contractul și constituția Statisticianului.

---

## 2. Diferențele exacte între registrul v1.0 și v1.1

### 2.1 Identificare

| Câmp | v1.0 | v1.1 |
|---|---|---|
| `registry_id` | `VE-CAPREG-v1.0` | `VE-CAPREG-v1.1` |
| `registry_version` | `1.0` | `1.1` |
| `human_readable` | `CAPABILITY_REGISTRY_v1.0.md` | `CAPABILITY_REGISTRY_v1.1.md` |
| `revision` | — | bloc nou: `supersedes`, `authority`, `scope`, 4 intrări de schimbare |

### 2.2 G1 — o intrare nouă

```
+ variable_primitives["raw_series@v1"] = {
+   required_params: { source_id: data_source_id,
+                      field: [open, high, low, close, volume, sub] },
+   note: "câmpul trebuie să existe în coloanele declarate ale sursei;
+          availability.offset_bars selectează bara (0 = bara evenimentului)"
+ }
```

`variable_primitives`: **14 → 15**.

### 2.3 G2 — cinci schimbări de domeniu

| Intrare | Parametru | v1.0 | v1.1 |
|---|---|---|---|
| `matched_null@v1` | `statistic` | `statistic_id` | `statistic_call` |
| `block_bootstrap@v1` | `statistic` | `statistic_id` | `statistic_call` |
| `iid_bootstrap@v1` | `statistic` | `statistic_id` | `statistic_call` |
| `permutation_test@v1` | `statistic` | `statistic_id` | `statistic_call` |
| `descriptive_measurement@v1` | `statistics` | `list[statistic_id]` | `list[statistic_call]` |

### 2.4 G2 — completare descoperită prin mutația M56

Șapte parametri din catalogul de statistici erau tipizați ca `string`, deși sunt semantic referințe: o statistică putea numi o variabilă niciodată declarată, iar motorul ar fi întâlnit referința nerezolvabilă abia la execuție — aceeași clasă de defect ca G2 însuși.

| Intrare | Parametri | v1.0 | v1.1 |
|---|---|---|---|
| `mean@v1`, `median@v1`, `trimmed_mean@v1`, `proportion@v1`, `sum@v1`, `difference_in_means@v1` | `variable_ref` | `string` | `variable_ref` |
| `difference_in_means@v1` | `group_ref` | `string` | `variable_ref` |

Aceeași slăbiciune există în alte primitive (`lag@v1`, `forward_excess@v1`, `regression_control@v1` ș.a.). **Nu a fost corectată** — depășește scopul aprobat; consemnată în backlog ca **G5**.

### 2.5 Reguli noi

```
+ rules.statistic_call_shape      — forma {id, statistic, params}; motorul nu deduce
+                                    niciodată cărei variabile i se aplică o statistică
+ rules.raw_series_availability   — pentru raw_series@v1, offset_bars SELECTEAZĂ bara,
+                                    spre deosebire de primitivele calculate
```

`rules`: **7 → 9**.

### 2.6 Neschimbat

`data_sources` (4 surse, hash-uri identice) · `sealed_registry` (graniță `2025-10-23T09:15:00Z`, status provizoriu) · `roles` · `availability_rules` · `population_predicates` (10) · `correction_methods` (3) · `deliberately_absent` · **toate cele 15 statusuri de calibrare**.

**Nicio metodă nu a fost adăugată, eliminată sau promovată.**

### 2.7 Notă de formă

Fișierul `capabilities.json` a fost rescris programatic la pasul §2.4 și este acum indentat uniform (834 de linii). Conținutul semantic este cel descris mai sus; diferența de formatare nu poartă informație.

---

## 3. Teste rulate

```
../venv/Scripts/python.exe -m pytest tests -q
260 passed in 0.99s
```

| Fișier | F2 | F2.1 | Δ |
|---|---|---|---|
| `tests/test_schema_and_registry.py` | 42 | 50 | +8 invarianți v1.1 și JSON-only |
| `tests/test_mutation_battery.py` | 57 | 64 | +7 mutații (M54–M60) |
| `tests/test_no_data_access.py` | 61 | 68 | +7 (aceleași mutații) |
| `tests/test_clarification.py` | 57 | 64 | +7 (aceleași mutații) |
| `tests/test_reference_spec.py` | — | 14 | nou |
| **Total** | **217** | **260** | **+43, 0 eșecuri** |

### 3.1 Mutațiile noi

| ID | Mutație | Cod |
|---|---|---|
| M54 | G2: statistica dată ca identificator gol, fără parametri | E2 |
| M55 | G2: apel de statistică fără parametrul obligatoriu al statisticii | E2 |
| M56 | G2: apel de statistică ce referă o variabilă nedeclarată | E2 |
| M57 | G2: apel de statistică fără câmpul `id` | E2 |
| M58 | G1: serie brută cu câmp inexistent în sursă | E2 |
| M59 | G1: serie brută care cere coloana `sub` de la M15, sursă care nu o are | E2 |
| M60 | G1: serie brută de rol `exposure` care folosește o bară viitoare | E2 |

M59 și M60 sunt cele care contează pentru argumentul din analiză: seria brută **nu** deschide o ușă închisă. Câmpul este verificat față de coloanele reale ale sursei, iar garda de leakage se aplică nemodificat.

M56 este mutația care a găsit golul din §2.4 — a eșuat la prima rulare, semnalând că parametrul nu era verificat.

---

## 4. Dovada că specificația de referință exprimă complet un design real

Sursa transcrisă: `statistician/reviews/DC-0004/STATISTICIAN_PHASE1_DC-0004.md`, §3, §11, §13, §14, §15.

### 4.1 Rezultatul validării

```
specificație : tests/fixtures/reference_spec_dc0004.json
hash         : bef886cc04a17344c83a70012e6699cd1dd3bda924faf06fdbf6cf3e4f630d57
etapă atinsă : 2
status       : HALTED
accesări de date : 0

cauze (6): toate E3, toate de forma „metoda X are statusul UNVALIDATED"
  tests/0/method matched_null@v1 · tests/1/method matched_null@v1
  tests/2/method placebo_control@v1 · tests/3/method multiverse@v1
  tests/4/method power_simulation@v1 · multiple_testing/method bonferroni@v1
```

Specificația trece integral **forma** și **vocabularul**. Singurele opriri rămase sunt cele șase porți de calibrare — câte una pentru fiecare metodă folosită.

### 4.2 Acoperirea elementelor designului

| Element al designului | Sursă | Exprimat prin | Test |
|---|---|---|---|
| Nivel = prior-day high/low | §3 | `prior_period_extreme@v1` × 2 | `test_event_definition_is_expressible` |
| Eveniment = high > PDH și close < PDH (+ simetric pe PDL) | §3 | `raw_series@v1` × 3 + `compare/and/or@v1` — **posibil doar prin G1** | idem |
| Prima bară a zilei | §3 | `bar_position@v1` | idem |
| 6 celule sesiune × direcție | §3, §11 pas 1 | `session_label@v1` + celule enumerate explicit | `test_six_session_direction_cells_are_expressible` |
| Orizonturi K6 și K12 | §3 | `forward_return@v1` × 2 | `test_both_horizons_are_declared` |
| Baseline forward propriu al sesiunii | §3 | `baseline_forward_mean@v1` stratificat, `exclude_event_bars: true` | `test_baseline_is_session_stratified` |
| Matched-null pe toate celulele | §11 pas 1, §14(a) | `matched_null@v1` × 2, statistică parametrizată — **posibil doar prin G2** | validare |
| Corecție family-wise pe toate celulele | §11 pas 2, §14(b) | `bonferroni@v1`, 12 membri enumerați | `test_family_wise_correction_covers_all_cells` |
| Test placebo pe nivel arbitrar | §11 pas 4, §14(d) | `placebo_control@v1` | `test_placebo_and_multiverse_are_declared` |
| Sensibilitate: orizonturi și praguri alternative | §14(e) | `multiverse@v1`, grilă | idem |
| Robustețe pe subperioade | §14(h) | subperioade în grila multiverse | idem |
| Analiză de putere | §13 | `power_simulation@v1` + `min_n: 15` | `test_power_analysis_is_declared` |
| Verificare temporal/outcome leakage | §14(f)(g) | declarat structural prin `availability` + rolurile variabilelor | `test_leakage_declarations_are_consistent_with_roles` |
| Criterii preînregistrate | §15 | 4 criterii, praguri numerice | `test_prereg_criteria_are_numeric_and_resolvable` |
| Holdout-ul sigilat ca țintă | §11, §17 | fereastră post `2025-10-23T09:15:00Z` + autorizare declarată | `test_sealed_window_is_declared_not_stumbled_into` |
| **Regresia de control pentru volatilitatea orară** | **§11 pas 3, §14(c)** | **NEEXPRIMABIL — gol G3** | `test_volatility_control_variable_exists_but_regression_is_not_expressible` |

**14 din 15 elemente sunt exprimabile.** Al 15-lea, regresia de control, cere o variabilă-indicator a evenimentului peste o populație care conține și non-evenimente; registrul nu are primitivă care să transforme un predicat într-o variabilă. Este consemnat ca **G3** și nu a fost rezolvat, revizuirea fiind strict limitată la G1 și G2.

Un control negativ confirmă că protecția holdout-ului nu este decorativă: eliminând autorizarea din aceeași specificație, apare E5 (`test_removing_the_authorization_reveals_the_sealed_window`).

### 4.3 Ce a produs, în plus, acest exercițiu

Poarta de publicare cerută de CEO — *o specificație completă pentru un design real, înainte de publicare* — a produs, la prima aplicare: **G3**, **G4** (semantica listelor de predicate nu e documentată nicăieri), **G5** (referințe tipizate ca `string` în alte primitive), plus completarea din §2.4. Toate sunt în backlog.

### 4.4 Avertisment asupra statutului fixturii

`reference_spec_dc0004.json` este un **artefact de inginerie, nu o specificație oficială a Statisticianului**. Identificatorii de candidat sunt marcați ca fixtură (`DC-0004-SHAPE-FIXTURE`, hash de îngheț nul, token de autorizare evident fals). Trei elemente pe care sursa nu le fixează numeric au fost completate pentru ca specificația să fie completă; sunt decizii statistice, deci nu aparțin Validation Engine și sunt consemnate ca întrebări deschise **Q1–Q3** în backlog:

- **Q1** — „prima bară H1 a zilei" admite două lecturi care produc populații diferite;
- **Q2** — sursa nu spune dacă cele două orizonturi formează o singură familie de teste;
- **Q3** — granițele numerice ale sesiunilor în UTC nu apar în artefactele citite.

---

## 5. Confirmarea că toate metodele rămân neexecutabile

| Verificare | Rezultat |
|---|---|
| `status` al registrului | `PUBLISHED_NOT_EXECUTABLE` |
| Metode de test cu `calibration_status: UNVALIDATED` | 12 / 12 |
| Metode de corecție cu `calibration_status: UNVALIDATED` | 3 / 3 |
| Metode executabile (`VALIDATED`) raportate de `ve capabilities` | **0** |
| Specificația de referință, complet corectă | **HALTED**, 6 × E3 (poarta de calibrare) |
| Specificația minimală, complet corectă | **HALTED**, 2 × E3 (poarta de calibrare) |
| Teste care impun invariantul | `test_no_method_is_executable`, `test_reference_spec_halts_only_on_calibration_gate`, `test_baseline_halts_only_on_calibration_gate` |

**Nicio specificație nu poate fi executată, oricât de corect ar fi scrisă.** Statusurile se schimbă individual, prin bateriile de calibrare din F5–F6.

---

## 6. Ordinea impusă — respectată

```
1. gramatică      ve/spec/domains.py: statistic_call adăugat, teste verzi
2. registru v1.1  capabilities.json + CAPABILITY_REGISTRY_v1.1.md
3. referință      fixtura DC-0004 + bateria actualizată
```

Auto-verificarea fail-closed (`registry_domains_are_parseable`) ar fi refuzat orice validare dacă registrul ar fi fost publicat înaintea gramaticii.

---

## 7. Stare

**F3 nu a fost început.** Nu s-a implementat nicio metodă statistică, niciun population builder, niciun strat de date, niciun holdout loader, niciun manifest sau bundle. Nicio dată de piață nu a fost citită; hash-urile celor patru surse rămân identice cu cele înregistrate.

**Validation Engine se oprește aici și așteaptă aprobarea.**
