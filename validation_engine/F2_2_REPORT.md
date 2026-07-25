# F2.2 — RAPORT DE LIVRARE
### Rezolvarea golurilor G3, G4, G5 · Capability Registry v1.2 · verificarea Q1–Q3 împotriva scripturilor Alpha

**Document ID:** VE-F22-REPORT-v1.0
**Data:** 2026-07-24 · **Autor:** Validation Engine
**Autoritate:** decizie CEO 2026-07-24 (aprobarea analizei G3–G5, ordinea de lucru impusă)
**Statut:** livrat, în așteptarea aprobării. **F3 NU a fost început. Nicio metodă statistică nu a fost implementată. Nicio dată de piață nu a fost citită.**

---

## 1. Ordinea de lucru impusă — respectată integral

| Pas | Cerut | Livrat |
|---|---|---|
| 1 | gramatică + validator pentru G5 | `test_ref`, `predicate_ref` în gramatică; rezolvare + unicitate globală de id-uri în validator |
| 2 | registrul pentru G5 | 13 descriptori retipizați |
| 3 | implementează + validează G3 | `indicator@v1` + regula de disponibilitate recursivă + detectare de cicluri |
| 4 | documentează normativ G4 | 4 reguli noi în registru; teste de invariant |
| 5 | publică Capability Registry v1.2 | `capabilities.json` + `CAPABILITY_REGISTRY_v1.2.md` |
| 6 | actualizează specificația de referință DC-0004 | 15/15 structural, cu regresia de control |
| 7 | construiește specificația de referință DC-0008 | grad de exprimare măsurat; gol nou G6 |
| 8 | extinde bateria de mutații și testele | +21 mutații, +33 teste |

Ordinea internă (gramatică înaintea registrului) a fost respectată; **G5 a precedat G3**, pentru că indicatorul alimentează `regression_control@v1.exposure_ref`, retipizat prin G5.

---

## 2. Fișiere create, modificate, șterse

Toate sub `ai_quant_lab/validation_engine/`. **Nimic în afara acestui director nu a fost creat sau modificat.** Scripturile Alpha au fost **citite** pentru verificare, niciodată atinse.

### Create (7)

| Fișier | Rol |
|---|---|
| `CAPABILITY_REGISTRY_v1.2.md` | catalogul publicat, v1.2 |
| `SPEC_TEMPLATE_v1.2.json` | șablonul oficial, cu exemplu `indicator@v1` |
| `tests/fixtures/reference_spec_dc0008.json` | a doua specificație de referință (DC-0008) |
| `tests/test_reference_spec.py` | rescris — DC-0004 15/15 + DC-0008 grad de exprimare |
| `REGISTRY_GAPS_G3_G4_G5_ANALYSIS.md` | analiza aprobată (livrată în pasul anterior) |
| `SCRIPT_VERIFICATION_Q1_Q3.md` | verificarea Q1–Q3 împotriva scripturilor in-sample |
| `F2_2_REPORT.md` | acest document |

### Modificate (7)

| Fișier | Modificare |
|---|---|
| `capabilities.json` | v1.1 → v1.2 (detaliat în §3) |
| `ve/spec/domains.py` | `test_ref`, `predicate_ref` în tipurile de referință |
| `ve/spec/registry_validator.py` | rezolvarea `test_ref`/`predicate_ref`; graful de variabile (cicluri + disponibilitate recursivă); unicitate globală de id-uri; verificarea câmpului `indicator@v1` |
| `ve/spec/loader.py` | mesajul de refuz YAML reformulat ca decizie de politică (A1) |
| `SPEC_SCHEMA_v1.0.md` | referințe la v1.2; exemple `indicator@v1` și note G3/G5 |
| `tests/fixtures/fixture_baseline_spec.json` | registru 1.2 |
| `tests/mutations.py`, `tests/test_schema_and_registry.py` | +21 mutații, +9 teste de invariant |
| `VE_BACKLOG.md` | G3/G4/G5 `REZOLVAT`; G6, G7 noi; Q1–Q3 actualizate |

### Șterse (1)

| Fișier | Motiv |
|---|---|
| `SPEC_TEMPLATE_v1.1.json` | înlocuit de `SPEC_TEMPLATE_v1.2.json` |

**Nemodificat, verificat prin hash:** `SPEC_SCHEMA_v1.0.json` (`f1ba7009…`), `ve/spec/schema_validator.py`, `ve/spec/validate.py`, `ve/errors.py`, `ve/audit/access_audit.py`, `ve/clarification.py`, `ve/cli.py`, `ve/paths.py`, `CAPABILITY_REGISTRY_v1.0/1.1.md`, `VALIDATION_ENGINE_ARCHITECTURE_v1.0.md`, contractul și constituția.

---

## 3. Diferențele exacte v1.1 → v1.2

### 3.1 Identificare

| Câmp | v1.1 | v1.2 |
|---|---|---|
| `registry_id` / `registry_version` | `VE-CAPREG-v1.1` / `1.1` | `VE-CAPREG-v1.2` / `1.2` |
| `revision.supersedes` | `1.0` | `1.1` |
| `revision.changes` | 3 (G1/G2) | 4 (G1→G5 istoricul consolidat pentru v1.2: G5 tipuri, G5 gramatică, G3, G4) |

### 3.2 G3 — o primitivă nouă

```
+ variable_primitives["indicator@v1"] = {
+   required_params: { predicate: "predicate" },
+   note: "variabilă 0/1 dintr-un predicat; sub garda de leakage;
+          availability ≥ max(availability variabile din predicat), recursiv; cicluri respinse"
+ }
```
`variable_primitives`: **15 → 16**.

### 3.3 G5 — 13 descriptori retipizați

| Intrare · parametru | v1.1 | v1.2 |
|---|---|---|
| `lag@v1.variable_ref`, `forward_excess@v1.forward_return_ref`/`baseline_ref`, `rolling_quantile@v1.variable_ref`, `dip_test@v1.variable_ref`, `gaussian_mixture@v1.variable_ref`, `changepoint@v1.variable_ref`, `regression_control@v1.outcome_ref`/`exposure_ref`, `descriptive_measurement@v1.variable_ref` (10) | `string` | `variable_ref` |
| `placebo_control@v1.base_test_ref`, `multiverse@v1.base_test_ref` (2) | `string` | `test_ref` |
| `proportion@v1.predicate_ref` (1) | `string` | `predicate_ref` |

Verificare: **0 parametri cu sufix `_ref` rămași `string`** (test `test_g5_no_reference_parameter_remains_a_plain_string`).

### 3.4 G4 — 5 reguli noi în `rules`

`predicate_list_conjunction`, `empty_predicate_lists`, `per_criterion_denominator`, `indicator_availability`, `reference_types_resolved`. `rules`: **9 → 14**.

### 3.5 Neschimbat

`data_sources` (4, hash-uri identice), `sealed_registry`, `roles`, `availability_rules`, `population_predicates` (10), `statistics` (7), `test_methods` (12), `correction_methods` (3), **toate cele 15 statusuri de calibrare**. Nicio metodă adăugată, eliminată sau promovată.

---

## 4. Noile tipuri de referință și regulile lor

| Tip | Trimite la | Verificat de validator | Eroare la nerezolvare |
|---|---|---|---|
| `test_ref` | un `test_id` declarat în `tests` | `resolve("test_ref", …)` | E2 |
| `predicate_ref` | id-ul unui predicat declarat **oriunde** în specificație | `resolve("predicate_ref", …)` peste `ctx.predicate_ids` | E2 |

Reguli asociate:

- **Rezolvare fail-closed înainte de orice acces la date** — o referință inexistentă oprește la etapa 2 (E2), niciodată amânată la execuție. Aceasta închide clasa de defecte G2/G5.
- **Unicitate globală a id-urilor de predicat** — fiindcă predicatele sunt acum referibile, id-urile lor trebuie unice pe întreaga specificație (include + exclude + celule + predicatele lui `indicator@v1`), nu doar în `include`. Colectarea și verificarea sunt recursive (`_all_predicate_roots` + `_iter_predicates`).

---

## 5. Implementarea G3, G4, G5

### 5.1 G3 — `indicator@v1`

- **Primitivă:** o variabilă cu un singur parametru, `predicate`, validat recursiv prin tipul de referință `predicate` deja existent (aceeași cale ca `and@v1`/`or@v1`).
- **Regula de disponibilitate (nouă, obligatorie):** implementată în `_check_variable_graph`. Se construiește graful de dependențe între variabile — din parametrii tipizați `variable_ref` și, pentru `indicator@v1`, din toate variabilele folosite de predicat (`_predicate_variable_refs`, recursiv). Regula impusă: `offset_bars(variabilă) ≥ offset_bars(dependență)` — o variabilă nu poate exista înaintea intrărilor ei. Generică, nu doar pentru indicator.
- **Detectarea ciclurilor:** DFS cu marcaje (alb/gri/negru) peste graful de dependențe; un ciclu produce E2 și exclude nodurile din verificarea de disponibilitate (pentru a nu dubla erorile). Ciclurile devin posibile prin noua gramatică (un indicator poate referi o variabilă care îl referă înapoi) — de aceea detectarea a fost o cerință explicită.

### 5.2 G4 — documentare normativă

Semantica listelor de predicate este acum scrisă în `rules`: conjuncție pentru `include`/celule; excludere la orice potrivire pentru `exclude`; `exclude: []` = nicio excludere; `predicates: []` = toată populația; denominator per criteriu bazat pe id-uri unice. **Zero cod nou** — semantica devine executabilă la F4, cu fixturi de conformitate (planificat). Testele de invariant verifică prezența regulilor.

### 5.3 G5 — retipizare completă

13 descriptori `string` → tipuri de referință rezolvabile. Două ramuri noi de rezolvare în validator; verificarea de unicitate a id-urilor de predicat extinsă de la `include`/`exclude` la întreaga specificație.

---

## 6. Rezultatele bateriei de mutații

**74 de mutații** (F2: 53, F2.1: +7, F2.2: **+14**), fiecare schimbând exact un lucru; toate produc oprire, niciuna acceptare.

| Cod | Nr. | Etapă |
|---|---|---|
| E1 (câmp absent) | 18 | 1 |
| E2 (formă/vocabular/referință) | 45 | 1–2 |
| E3 (vocabular inexistent / necalibrat) | 9 | 2 |
| E5 (autorizare) | 2 | 2 |

### 6.1 Mutațiile noi F2.2

| ID | Mutație | Cod |
|---|---|---|
| M61 | G3: indicator valabil + regresie de control (se oprește doar pe calibrare) | E3 |
| M62 | G3: indicator cu predicat inexistent | E3 |
| M63 | G3: indicator cu variabilă nedeclarată în predicat | E2 |
| M64 | G3: indicator disponibil înaintea variabilei din predicat | E2 |
| M65 | G3: **ciclu de referință** indicator ↔ lag | E2 |
| M66 | G3: obiect-predicat malformat (chei lipsă) | E2 |
| M67 | G3: predicatul indicatorului duplică un id existent | E2 |
| M68 | G5: `forward_return_ref` inexistent | E2 |
| M69 | G5: `base_test_ref` inexistent (`test_ref`) | E2 |
| M70 | G5: `base_test_ref` valid (se oprește doar pe calibrare) | E3 |
| M71 | G5: `predicate_ref` inexistent | E2 |
| M72 | G5: `predicate_ref` valid (se oprește doar pe calibrare) | E3 |
| M73 | G5: `dip_test.variable_ref` inexistent | E2 |
| M74 | G5: `regression_control.exposure_ref` inexistent | E2 |

Toate cerințele obligatorii sunt acoperite mecanic: referință inexistentă respinsă înainte de orice acces la date (M62/M63/M68/M69/M71/M73/M74), duplicate de id respinse (M67), cicluri detectate (M65), disponibilitate recursivă (M64).

---

## 7. Rezultatele testelor

```
../venv/Scripts/python.exe -m pytest tests -q
313 passed in 1.21s
```

| Fișier | F2.1 | F2.2 |
|---|---|---|
| `test_schema_and_registry.py` | 50 | 56 |
| `test_mutation_battery.py` | 64 | 78 |
| `test_no_data_access.py` | 68 | 82 |
| `test_clarification.py` | 64 | 78 |
| `test_reference_spec.py` | 14 | 19 |
| **Total** | **260** | **313** |

---

## 8. Dovada zero accesări de date

- Toate cele 74 de mutații: `data_accesses == []` (test dedicat, per mutație).
- Toate cazurile E1/E2/E3: `data_accesses == []`, cu numărare per cod.
- Ambele specificații de referință: `data_accesses == []`.
- Controlul detectorului (prinde o deschidere reală de fișier de date; garda abandonează operațiunea) rămâne verde.

Verificare independentă: hash-urile SHA-256 ale celor patru surse de piață sunt **identice** cu cele din F1, după rularea completă a suitei.

---

## 9. DC-0004 exprimat 15/15 structural

`tests/fixtures/reference_spec_dc0004.json` (v1.2) validează cu **exact 7 × E3 (poarta de calibrare), zero erori non-E3, zero accesări de date**. Al 15-lea element — regresia de control obligatorie (§11 pas 3) — este acum exprimabil prin `indicator@v1` (expunerea-eveniment `sweep_event`) + `regression_control@v1` cu `exposure_ref` rezolvat.

Restructurare necesară, conform analizei §2: populația este acum **cohorta eligibilă** (nu doar evenimente), iar indicatorul marchează expunerea — condiție pentru ca regresia să aibă grup de comparație. Controlul negativ (eliminarea autorizării → E5) confirmă că protecția holdout-ului nu este decorativă.

**Notă de fidelitate:** definiția „prima bară a zilei" folosită structural (`bar_position` index 0) este un substituent nenormativ. Evenimentul in-sample real este „prima bară care depășește nivelul" — neexprimabil (gol G7, §11). 15/15 se referă la exprimabilitatea **tipurilor** de element de design, nu la fidelitatea numerică față de in-sample, care depinde de Q1/Q3 (deschise) și de G7.

---

## 10. Gradul de exprimare al DC-0008 și golul nou G6

`tests/fixtures/reference_spec_dc0008.json` validează cu **8 × E3, zero non-E3, zero accesări de date**. Toată mașinăria statistică a designului este exprimabilă: dip test + GMM + changepoint (bimodalitate §11a), măsurare descriptivă a pragului (§11b), `indicator@v1` pentru clasificare pe prag preînregistrat, regresie de control care prezice outcome controlând volatilitatea (§12), multiverse (§11c/g), power_simulation (§10), corecție Bonferroni (§11d).

**Gol nou G6:** variabila de expunere reală a DC-0008 — R = (volumul celei mai mari sub-lumânări M1/M5) ÷ (volumul total M15) — **NU este exprimabilă**. Nu există sursă la timeframe mai fin de M15 și nicio primitivă de agregare sub-bară. Fixtura folosește `bar_range_ratio@v1` pe M15 ca **substituent structural explicit nenormativ**, exclusiv pentru a exercita restul mașinăriei.

Conform instrucțiunii permanente, **G6 este înregistrat în backlog și NU a fost rezolvat.** Gradul de exprimare al DC-0008: mașinărie statistică integral exprimabilă; variabila de expunere centrală blocată de G6.

---

## 11. Verificarea Q1–Q3 împotriva scripturilor Alpha in-sample

Statisticianul a răspuns la Q1–Q3 (`STATISTICIAN_OPERATIONAL_DEFINITIONS_v1.0.md`) și a cerut confirmarea împotriva scripturilor originale. **Am avut acces** și am făcut verificarea (`SCRIPT_VERIFICATION_Q1_Q3.md`).

**Rezultat: definițiile propuse de Statistician contrazic material convențiile in-sample.**

| Aspect | Statistician (propus) | Scripturi in-sample (obs0003/0008/0012/0013 prin `_lab`/`_common`) |
|---|---|---|
| Granița zilei | 17:00 America/New_York, DST | **data calendaristică UTC (00:00 UTC)** |
| Sesiuni | 3, ancorate local, DST | **4** (asia/london/ny/**late**), cupe de oră UTC fixă, fără DST |
| NY (UTC) | 12:00–21:00 / 13:00–22:00 | **13:00–21:00 fix** |
| Londra (UTC) | 07:00–15:30 / 08:00–16:30 | **08:00–13:00 fix** |
| Asia (UTC) | 00:00–06:00 | **00:00–08:00 fix** |
| Eveniment | „prima bară a zilei" | **prima bară care depășește nivelul** |
| K6/K12 familie | aceeași | consistent |

Consecință: un re-test pe holdout cu definițiile Statisticianului **nu ar fi o replicare** a testului in-sample, ci un test diferit. Reconcilierea („replicăm exact in-sample vs. adoptăm definiția nouă") aparține Statisticianului + CEO. **Validation Engine nu a ales și nu a blocat nicio definiție.**

Verificarea a descoperit și golul **G7** (`first-in-scope`): evenimentul in-sample „prima bară care depășește nivelul" nu este exprimabil. Înregistrat, nerezolvat.

---

## 12. Confirmarea că Q1–Q3 au rămas nerezolvate

- **Q1** (graniță de zi / definiția evenimentului): `DESCHIS — CONTRAZIS de in-sample`.
- **Q2** (familia K6/K12): răspuns compatibil cu in-sample; nu este blocat ca oficial, dar nu prezintă discrepanță.
- **Q3** (sesiuni): `DESCHIS — CONTRAZIS de in-sample`.

Fixturile rămân nenormative pe Q1/Q3 (câmp `_nonnormative`, respins de schemă). **Nicio valoare neconfirmată nu a fost introdusă într-o specificație normativă.** Nicio definiție a Statisticianului nu a fost blocată ca oficială, exact pentru că verificarea a arătat că nu coincide cu in-sample.

---

## 13. Confirmarea că toate metodele rămân neexecutabile

| Verificare | Rezultat |
|---|---|
| `status` registru | `PUBLISHED_NOT_EXECUTABLE` |
| Metode de test `UNVALIDATED` | 12 / 12 |
| Metode de corecție `UNVALIDATED` | 3 / 3 |
| `ve capabilities` → metode executabile | **0** |
| DC-0004 (15/15) | HALTED, 7 × E3 (calibrare) |
| DC-0008 | HALTED, 8 × E3 (calibrare) |
| fixtura minimală | HALTED, 2 × E3 (calibrare) |

---

## 14. Confirmarea că F3 nu a fost început

Nu s-a implementat nicio metodă statistică, niciun population builder, niciun strat de date, niciun holdout loader, niciun manifest sau bundle, niciun `rehearse`/`run`/`verify`. `SPEC_SCHEMA_v1.0.json` neschimbat. Hash-urile celor patru surse de piață neschimbate. Nicio dată de piață citită.

---

**Validation Engine se oprește aici și așteaptă aprobarea CEO după F2.2.**
