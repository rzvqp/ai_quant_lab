# F2 — RAPORT DE LIVRARE
### Validatorul de specificație, taxonomia de erori, cererea de clarificare, bateria de mutații

**Document ID:** VE-F2-REPORT-v1.0
**Data:** 2026-07-24 · **Autor:** Validation Engine
**Fază:** F2, conform `VALIDATION_ENGINE_ARCHITECTURE_v1.0.md` §8
**Statut:** livrat, în așteptarea aprobării CEO. **Nicio metodă statistică nu a fost implementată. Nicio dată de piață nu a fost citită.**

---

## 1. Ce s-a implementat și ce nu

| În scopul F2 | Status |
|---|---|
| Validatorul de specificație (etapa 1 formă + etapa 2 vocabular) | ✅ implementat |
| Taxonomia de erori (E1–E9 declarate, E1/E2/E3/E5 active) | ✅ implementat |
| Cererea de clarificare (patru câmpuri, zero recomandări) | ✅ implementat |
| Bateria de mutații | ✅ 53 de mutații |
| Garda de acces la date (dovada „zero accesări") | ✅ implementat |

| În afara scopului F2 — deliberat neimplementat | Fază |
|---|---|
| Metode statistice (matched-null, bootstrap, dip test, regresie etc.) | F5–F6 |
| Acces la date reale, încărcare de serii | F4/F7 |
| Population builder, denominator, construcția variabilelor | F4+ |
| Holdout loader, consumul token-ului CEO | F8 |
| Execuția protocoalelor, manifest, bundle, ledger | F3/F7 |
| Subcomenzile `rehearse`, `run`, `verify` | F3/F7 |

---

## 2. Fișiere create

Toate sub `ai_quant_lab/validation_engine/`. **Niciun fișier din afara acestui director nu a fost creat sau modificat.**

| Fișier | Linii | Rol |
|---|---|---|
| `ve/__init__.py` | 16 | pachetul; instalează garda de acces (inactivă implicit) |
| `ve/paths.py` | 41 | rezolvarea rădăcinilor; NU citește date |
| `ve/errors.py` | 87 | taxonomia E1–E9, `VEError`, `ValidationResult` |
| `ve/audit/__init__.py` | 1 | — |
| `ve/audit/access_audit.py` | 118 | garda de acces la date (PEP 578 audit hook) |
| `ve/spec/__init__.py` | 1 | — |
| `ve/spec/loader.py` | 89 | încărcare + hash; nu injectează nimic |
| `ve/spec/domains.py` | 216 | gramatica închisă a domeniilor din registru |
| `ve/spec/schema_validator.py` | 106 | etapa 1 — forma, față de `SPEC_SCHEMA_v1.0.json` |
| `ve/spec/registry_validator.py` | 415 | etapa 2 — vocabularul, față de `capabilities.json` |
| `ve/spec/validate.py` | 63 | orchestrarea celor două etape, sub gardă |
| `ve/clarification.py` | 63 | randarea cererii de clarificare |
| `ve/cli.py` | 110 | `validate` și `capabilities` |
| `ve/__main__.py` | 3 | punct de intrare |
| `tests/conftest.py` | 26 | fixtures |
| `tests/mutations.py` | 249 | catalogul celor 53 de mutații |
| `tests/fixtures/fixture_baseline_spec.json` | 123 | specificația de referință |
| `tests/test_schema_and_registry.py` | 163 | invarianți F1 + gramatica domeniilor |
| `tests/test_mutation_battery.py` | 93 | bateria de mutații |
| `tests/test_no_data_access.py` | 129 | dovada zero accesări + controlul detectorului |
| `tests/test_clarification.py` | 83 | patru câmpuri, zero recomandări |
| `F2_REPORT.md` | — | acest document |

**Fișiere F1 modificate: niciunul.** `SPEC_SCHEMA_v1.0.json`, `capabilities.json`, `CAPABILITY_REGISTRY_v1.0.md`, `SPEC_SCHEMA_v1.0.md`, `SPEC_TEMPLATE_v1.0.yaml` și `VALIDATION_ENGINE_ARCHITECTURE_v1.0.md` sunt neatinse.

---

## 3. Teste rulate și rezultate

```
../venv/Scripts/python.exe -m pytest tests -q
217 passed in 0.86s
```

| Fișier de test | Rezultat |
|---|---|
| `tests/test_schema_and_registry.py` | 42 passed |
| `tests/test_mutation_battery.py` | 57 passed |
| `tests/test_no_data_access.py` | 61 passed |
| `tests/test_clarification.py` | 57 passed |
| **Total** | **217 passed, 0 failed** |

Mediu: Python 3.14.6, jsonschema 4.26.0, pytest 9.1.1.

### 3.1 Ce verifică suitele

**Invarianți ai artefactelor F1** — schema este o schemă Draft 2020-12 validă; **zero apariții ale cuvântului-cheie `default`**; `additionalProperties: false` la fiecare nivel de obiect; clauza de oprire are o singură valoare admisă; `threshold` este `{"type": "number"}`; `criteria_evaluation` absent (P1); registrul nu declară niciun parametru opțional; toate metodele sunt `UNVALIDATED`; granița sigilată este unică și marcată provizorie; schema nu conține lista de metode (o singură sursă de adevăr).

**Gramatica domeniilor** — 28 de cazuri de acceptare/respingere; un descriptor neacoperit ridică excepție în loc să fie tratat permisiv; auto-verificarea confirmă că toți descriptorii din registru sunt parsabili.

**Comportamentul etapelor** — etapa 2 nu rulează dacă etapa 1 a eșuat.

---

## 4. Dovada că erorile de schemă și de completitudine produc oprire

### 4.1 Specificația de referință — completă și corectă

`tests/fixtures/fixture_baseline_spec.json` trece integral etapa 1 și etapa 2. Singurul motiv de oprire rămas este **poarta de calibrare**:

```
specificație : tests/fixtures/fixture_baseline_spec.json
hash         : 64852523fbd3a07fcb7919fc30687f87e83c57bebb13f5978240add84e5962ea
etapă atinsă : 2
status       : HALTED
fișiere deschise în timpul validării : 3
accesări de date                     : 0

cauze (2):
  [E3 SPEC_UNSUPPORTED] tests/0/method: Metoda 'matched_null@v1' are statusul de calibrare
      'UNVALIDATED' și nu poate fi executată oficial.
  [E3 SPEC_UNSUPPORTED] multiple_testing/method: Metoda de corecție 'bonferroni@v1' are
      statusul 'UNVALIDATED' și nu poate fi executată oficial.
exit=2
```

Aceasta este proprietatea cerută la F1: registrul este vocabular, nu capacitate. **La v1.0, nicio specificație nu poate fi executată, oricât de corect ar fi scrisă.**

### 4.2 Bateria de mutații — 53 de cazuri

Fiecare mutație pornește de la specificația de referință și modifică exact un lucru. Toate produc oprire; niciuna nu produce acceptare.

| Grup | Mutații | Cod | Etapă |
|---|---|---|---|
| Câmpuri obligatorii absente | M01–M18 | E1 | 1 |
| Formă ambiguă sau invalidă | M19–M30 | E2 | 1 |
| Vocabular inexistent în registru | M31–M35 | E3 | 2 |
| Parametri și domenii | M36–M51 | E2 | 2 |
| Autorizare față de granița sigilată | M52–M53 | E5 | 2 |

Cazuri care merită menționate explicit:

- **M19** prag descriptiv („volatilitate ridicată") → E2. Interdicția din contract §1.2 este structurală: pragul este `number` în schemă.
- **M21** clauză de oprire permisivă (`continue_with_defaults`) → E2. Nu există mod permisiv.
- **M23** `criteria_evaluation` cerut în `return` → E2. **Punctul P1 este activ blocat**, nu doar nedecis.
- **M32** predicat specific unei ipoteze (`sweep_reject@v1`) → E3. Motorul nu conține logică de ipoteză.
- **M37** parametru necunoscut strecurat într-o metodă (`optimize_threshold`) → E2.
- **M41** variabilă de control cu `offset_bars: +3` → E2. Regula de disponibilitate este verificată, nu dedusă.
- **M49** identificator de predicat duplicat → E2. Denominatorul per criteriu ar deveni ambiguu.
- **M52/M53** fereastră care atinge holdout-ul sigilat fără autorizare → E5, inclusiv cazul-limită „exact la graniță, capăt inclusiv".

### 4.3 Exemplu de oprire multiplă

Specificație cu patru defecte simultane (secțiune absentă, prag descriptiv, clauză permisivă, câmp rezervat P1):

```
etapă atinsă : 1
status       : HALTED
accesări de date : 0
cauze (4):
  [E1 SPEC_INCOMPLETE] population: Câmp obligatoriu absent din specificație.
  [E2 SPEC_AMBIGUOUS] criteria/0/threshold: Tip greșit: se cere 'number'.
  [E2 SPEC_AMBIGUOUS] on_missing_or_ambiguous: Valoare neadmisă: singura valoare
      acceptată este 'halt_and_request_clarification'.
  [E2 SPEC_AMBIGUOUS] return: Câmp necunoscut... ('criteria_evaluation' was unexpected).
```

Cererea de clarificare generată conține, pentru fiecare cauză, exact patru câmpuri: cod, câmp, motiv, ce există în registru. Testele verifică lexical că secțiunile de cauze nu conțin vocabular de recomandare (*recomand, sugerez, propun, alegeți, setați la, valoare implicită*) și nici vocabular de verdict (*semnificativ, confirmat, respins statistic, robust, promițător*).

---

## 5. Dovada că la E1–E3 există zero accesări de date

### 5.1 Mecanismul

`ve/audit/access_audit.py` folosește `sys.addaudithook` (PEP 578), evenimentul `open`. Hook-ul prinde deschiderile indiferent de bibliotecă — `builtins.open`, `io.open`, `os.open` sau cod C — deci nu poate fi ocolit prin alegerea cititorului.

Validarea rulează în regim de **interdicție**: o deschidere sub o rădăcină de date ridică `DataAccessViolation` și interpretorul abandonează operațiunea. Garanția este **structurală**, nu doar observată prin test.

Rădăcinile considerate „date": `<lab>/data` și, dacă e definită, `AI_QUANT_DATA_DIR` — ambele, ca garda să nu poată fi ocolită prin mediu.

### 5.2 Controlul detectorului

O listă goală de accesări nu dovedește nimic dacă detectorul e stricat. Suita conține, înainte de orice afirmație de absență:

| Test | Ce demonstrează |
|---|---|
| `test_detector_catches_a_data_file_open` | detectorul PRINDE o deschidere de fișier de date (rădăcină falsă în `tmp_path`) |
| `test_guard_aborts_a_forbidden_data_open` | garda ABANDONEAZĂ operațiunea, cu excepție |
| `test_detector_ignores_non_data_files` | nu produce fals-pozitive pe fișiere care nu sunt date |
| `test_real_data_root_is_guarded_even_without_env` | rădăcina reală e păzită și fără variabila de mediu |

Controlul pozitiv folosește un director temporar, nu datele reale de piață: dovada că detectorul funcționează nu cere atingerea seriilor din `data/market/`.

### 5.3 Rezultatul

| Verificare | Rezultat |
|---|---|
| Fiecare dintre cele 53 de mutații, `data_accesses` | `[]` |
| Toate cazurile care produc E1, E2 sau E3, `data_accesses` | `[]` (test dedicat, cu numărare per cod) |
| Validare din fișier, `data_accesses` | `[]` |
| Fișiere deschise efectiv (cu memoriile golite) | doar `spec.json`, `SPEC_SCHEMA_v1.0.json`, `capabilities.json` |
| Fișiere deschise sub `data/market/` | 0 |
| Specificație YAML refuzată | E3, etapa 0, `data_accesses = []` |

Verificare independentă suplimentară: hash-urile SHA-256 ale celor patru fișiere de piață sunt **identice** cu cele înregistrate în `capabilities.json` la F1, după rularea completă a suitei.

---

## 6. Abateri față de arhitectura aprobată

| # | Abatere | Motiv | Remediere |
|---|---|---|---|
| **A1** | **Specificațiile sunt acceptate doar în JSON.** `SPEC_SCHEMA_v1.0.md` §1 spune „YAML sau JSON" | biblioteca de parsare YAML nu este instalată în venv-ul laboratorului | instalarea ei, sau publicarea unui șablon JSON. Până atunci, `SPEC_TEMPLATE_v1.0.yaml` este citibil de om, dar nu încărcabil de motor. YAML nu este parsat tăcut: produce oprire E3 explicită |
| **A2** | **Cererea de clarificare se scrie în `clarifications/` sau la `--out`, nu în bundle** | bundle-ul de rulare este livrabil F3 | se mută în bundle la F3 |
| **A3** | **E4 nu este ridicat în F2.** Hash-ul declarat se compară cu cel din registru, nu cu fișierul real | compararea cu fișierul real cere citirea lui — interzis în această fază | F4 |
| **A4** | **E5 acoperă doar coerența autorizare↔fereastră sigilată.** Verificarea și consumul token-ului CEO nu sunt implementate | protocolul de resursă sigilată este F8 | F8 |
| **A5** | **Reconfigurare UTF-8 a consolei în CLI**, neprevăzută în arhitectură | consola Windows implicită (cp1252) nu poate scrie diacriticele și doborâse procesul | păstrată; ieșirea nu are voie să oprească motorul |
| **A6** | **Decizie de proiectare nespecificată în arhitectură: etapa 2 nu rulează dacă etapa 1 a eșuat** | pe o structură invalidă, verificarea vocabularului produce erori derivate care îngreunează clarificarea | consemnată aici pentru ratificare |
| **A7** | **Garda de acces nu poate fi dezinstalată** din proces, odată importat pachetul `ve` | proprietate PEP 578, intenționată de designul Python | garda este inactivă implicit; se activează doar în context explicit |

---

## 7. Două goluri de registru descoperite prin implementare

Ambele sunt inofensive la validare, dar **blochează execuția** și trebuie rezolvate într-un registru v1.1 înainte de F5. Nu am modificat registrul aprobat.

**G1 — Nu există primitivă pentru seria brută OHLCV.** Registrul v1.0 conține indicatori derivați (`atr@v1`, `parkinson_volatility@v1`, …), dar nicio cale de a referi direct `high`, `low`, `close`, `open`, `volume`. Consecință: un eveniment elementar precum „maximul barei depășește un nivel" nu poate fi exprimat. Lipsește o intrare de tip `raw_series@v1 {source_id, field}`.

**G2 — Statisticile nu își pot primi parametrii.** Metodele primesc `statistic` ca `statistic_id` (un simplu identificator), dar statisticile din registru au ele însele parametri obligatorii — `mean@v1` cere `variable_ref`. În forma actuală nu există unde să fie transmis. Se rezolvă fie permițând `statistic` să fie un obiect `{id, params}`, fie legând statistica de o variabilă declarată.

Ambele au fost descoperite exact pentru că specificația de referință a fost scrisă strict în vocabularul aprobat, fără improvizații.

---

## 8. Stare

**Nu s-a implementat nicio metodă statistică. Nu s-a citit nicio dată de piață. Nu s-a construit nicio populație. Holdout-ul nu a fost atins. Niciun artefact din afara `validation_engine/` nu a fost creat sau modificat.**

**Validation Engine se oprește aici și așteaptă aprobarea CEO înainte de F3.**
