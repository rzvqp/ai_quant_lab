# VALIDATION ENGINE — BACKLOG
### Registrul permanent al datoriilor, abaterilor și punctelor deschise

**Document ID:** VE-BACKLOG
**Deschis:** 2026-07-24 · **Ultima actualizare:** 2026-07-24 (după F2.1 — registrul v1.1)
**Regulă:** acest document este **append-only pentru conținut**. O intrare nu se șterge niciodată; i se schimbă doar statusul, cu data și modul de rezolvare. Nimic nu se pierde, chiar dacă nu se rezolvă imediat.

**Statusuri:** `DESCHIS` · `ÎN DECIZIE` (livrat CEO, aștept hotărâre) · `PLANIFICAT` (decis, alocat unei faze) · `REZOLVAT` (cu data și dovada) · `ACCEPTAT` (rămâne permanent, prin decizie)

---

## 1. Abateri față de arhitectura aprobată (A1–A7)

Toate provin din faza F2 (`F2_REPORT.md` §6).

| ID | Abatere | Impact | Rezolvare | Status |
|---|---|---|---|---|
| **A1** | **Specificațiile sunt acceptate doar în JSON.** `SPEC_SCHEMA_v1.0.md` §1 promitea „YAML sau JSON" | `SPEC_TEMPLATE_v1.0.yaml` nu era încărcabil de motor | **CEO 2026-07-24: JSON-only, fără instalarea PyYAML.** Publicat `SPEC_TEMPLATE_v1.1.json`; `SPEC_SCHEMA_v1.0.md` §1 și §8 corectate; șablonul YAML retras; mesajul de oprire al loader-ului reformulat din limitare de mediu în decizie de politică. Teste: `test_documentation_no_longer_promises_yaml`, `test_no_yaml_template_remains`, `test_yaml_spec_is_refused_without_touching_data` | `REZOLVAT` 2026-07-24 |
| **A2** | **Cererea de clarificare se scrie în `clarifications/` sau la `--out`, nu în bundle-ul de rulare** | localizarea artefactului diferă de arhitectură §3.3 | F3 (bundle-ul de rulare) | `PLANIFICAT` |
| **A3** | **E4 nu este ridicat.** Hash-ul declarat se compară cu cel din registru, nu cu fișierul real | integritatea datelor nu este verificată la sursă; compararea reală cere citirea fișierului | F4 | `PLANIFICAT` |
| **A4** | **E5 acoperă doar coerența autorizare ↔ fereastră sigilată.** Verificarea, validarea și consumul token-ului CEO nu sunt implementate | protecția holdout-ului este parțială: prinde atingerea neautorizată prin fereastră, dar nu gestionează token-ul. Specificația de referință folosește un token evident fals (`FIXTURE-NOT-A-REAL-TOKEN`) tocmai pentru că nimic nu îl verifică încă | F8 | `PLANIFICAT` |
| **A5** | **Reconfigurare UTF-8 a consolei în CLI** | consola Windows implicită (cp1252) nu poate scrie diacriticele și doborâse procesul cu cod 3 | **CEO 2026-07-24: acceptat permanent.** Ieșirea nu are voie să oprească motorul | `ACCEPTAT` |
| **A6** | **Etapa 2 nu rulează dacă etapa 1 a eșuat** | pe o structură invalidă, verificarea vocabularului ar produce erori derivate care îngreunează clarificarea | **CEO 2026-07-24: acceptat permanent.** Test: `test_stage2_does_not_run_when_stage1_fails` | `ACCEPTAT` |
| **A7** | **Garda de acces nu poate fi dezinstalată** din proces, odată importat pachetul `ve` | proprietate PEP 578. Garda este inactivă implicit, se activează doar în context explicit | **CEO 2026-07-24: acceptat permanent, ca limitare documentată** | `ACCEPTAT` |

---

## 2. Goluri de registru

### 2.0 Rezolvate în registrul v1.2

| ID | Gol | Rezolvare | Status |
|---|---|---|---|
| **G3** | Nu exista primitivă care să transforme un predicat într-o variabilă-indicator | **`indicator@v1 {predicate}`**, aprobat CEO 2026-07-24. Variabilă 0/1, cu `availability` și `role`, sub garda de leakage. Regulă nouă obligatorie: disponibilitatea indicatorului ≥ max(disponibilitatea variabilelor din predicat), verificată recursiv; ciclurile de referință sunt respinse. Fără schemă nouă. Teste: `test_g3_*`, mutațiile M61–M67 | `REZOLVAT` 2026-07-24 |
| **G4** | Semantica listelor de predicate nu era definită | **Documentare normativă** în registru (conjuncție; `exclude` la orice potrivire; liste goale; denominator per criteriu). Fără schimbare de model. Teste de invariant: `test_g4_*` | `REZOLVAT` 2026-07-24 |
| **G5** | 13 parametri cu semantică de referință tipizați ca `string` | **Retipizare completă** + tipurile `test_ref` și `predicate_ref` în gramatică; unicitatea id-urilor de predicat extinsă la întreaga specificație. Fără schemă nouă. Teste: `test_g5_*`, mutațiile M68–M74 | `REZOLVAT` 2026-07-24 |

### 2.05 Goluri descoperite la porțile de acceptare v1.2/v1.3

| ID | Gol | Cum a fost descoperit | Impact | Status |
|---|---|---|---|---|
| **G6** | **Nu există sursă la timeframe mai fin (M1/M5) și nicio primitivă de agregare sub-bară.** | scrierea specificației de referință DC-0008 | Blochează variabila de expunere reală a DC-0008 (raportul R). Restul mașinăriei DC-0008 e exprimabilă; fixtura folosește substituent nenormativ | `DESCHIS` (CEO: „Nu rezolva G6 în acest pas") |
| **G7** | Nu exista primitivă „prima apariție în domeniu" (`first-in-scope`) | verificarea împotriva scripturilor Alpha | evenimentul in-sample al DC-0004 = „prima bară a zilei care depășește nivelul" | **`REZOLVAT`** 2026-07-24 prin registrul v1.3: `first_in_scope@v1 {scope, predicate}`, lookahead-safe; scope `day` = 00:00 UTC (Calea A). Validator: `_iter_predicates` recursează în predicatul singular. Teste: `test_g7_*`, mutațiile M75–M78 |
| **G8** | Familia de corecție cu apartenență dependentă de date nu era exprimabilă | exprimarea Căii A pentru DC-0004 | **`REZOLVAT`** 2026-07-25 prin registrul v1.4 (varianta V1, `REGISTRY_GAP_G8_DESIGN.md`): `member_eligibility {field, op, value}` la `bonferroni@v1`/`benjamini_hochberg@v1`, cu lista albă `[n, denominator, event_count]`. **Regula de aur R3 impusă prin vocabular:** un câmp de rezultat (p/statistică/efect) nu poate fi nici măcar numit → familia nu poate depinde sintactic de rezultat. Validatorul verifică structura + lista albă, NU calculează familia (execuție F5+). Familie vidă → oprire (E6 runtime). Teste: `test_g8_*`, mutațiile M79–M87 |
| **seed** | `seed=7` literal nu e exprimabil — schema fixează `seed_policy` la `derived_from_spec_hash` | exprimarea Căii A (item 8) | — | **`REZOLVAT` (CEO 2026-07-24): NU se introduce excepție. Rămâne politica generală `derived_from_spec_hash`.** Pentru holdout, seed-ul literal e imaterial (alt eșantion). Convenția Calea A #8 este suprascrisă de politica de reproductibilitate |

### 2.06 Descoperit la materializarea F4 — CONSEMNAT, NEREZOLVAT

| ID | Constatare | Cum a fost descoperit | Impact | Status |
|---|---|---|---|---|
| **F4-1** | Specificația oficială DC-0004 calcula PDH/PDL din D1 (ancorat la rollover 21:00/22:00), dar in-sample folosește H1 grupat pe zi UTC (`add_prior_day`) | materializarea F4 (distribuție anormală pe sesiuni) | Contradicție cu convenția Calea A | **`REZOLVAT`** 2026-07-25 — modificare autorizată de CEO: `source_id` pdh/pdl D1→H1; D1 eliminat din `data`. Verificat: cu H1, celulele familiei se potrivesc obs0012. Doar specificația a fost modificată; vocabular/registru/validator/motor neatinse |
| **F4-2** | Celulele DC-0004 marcau direcția prin `compare(high>pdh)` în loc de evenimentul complet; 35 bare spargeau ambele direcții → supraestimare | confirmarea F4 împotriva obs0012 | A doua discrepanță | **`REZOLVAT`** 2026-07-25 — modificare autorizată CEO: celule = `in_session(s) ∧ first_in_scope(high>pdh) ∧ close<pdh`. Verificat: n per celulă = **exact** 135/34/42/114/40/47; total interacțiuni = 430 (= obs0003); m=6. Doar specificația+fixturile; motor/registru/validator neatinse |
| **F4-3** | Specificația DC-0004 declara `baseline exclude_event_bars: True`, dar obs0008/0012 includ barele-eveniment în baseline (`sess_idx[s]` = toate barele) | confirmarea F4 (comparație baseline) | A treia discrepanță | **`REZOLVAT`** 2026-07-25 — modificare autorizată CEO. Verificat explicit în cod (obs0008 l.24-26, obs0012 l.25,33): baseline peste TOATE barele sesiunii, inclusiv evenimente. Confirmat numeric: motorul reproduce EXACT formula Alpha (4 sesiuni identice la 1e-9). Preferință CEO: aliniere SPEC la motor+Alpha → `exclude_event_bars: True→False`. Motorul NU a fost modificat (reproduce deja Alpha). Excess per celulă acum = obs0012 EXACT (-3.64/1.29/1.75/-1.04/-0.46/-0.36) |
| **F4-4** | **Latent (motor):** `baseline_forward_mean@v1` nu implementează parametrul `exclude_event_bars` — îl acceptă dar îl ignoră (include mereu toate barele) | rezolvarea F4-3 | **Non-blocant pentru DC-0004** (spec = False = include-toate = comportamentul motorului = Alpha). Ar deveni un defect DOAR dacă o specificație viitoare setează `True` și așteaptă excluderea. Nu s-a modificat motorul (CEO: „nu modifica motorul dacă reproduce deja Alpha") | `CONSEMNAT` — de rezolvat dacă vreun protocol viitor cere `exclude_event_bars: True` |

### 2.1 Rezolvate în registrul v1.1

| ID | Gol | Rezolvare | Status |
|---|---|---|---|
| **G1** | Nu exista primitivă pentru seria brută OHLCV; clasa evenimentelor „comparație preț ↔ nivel" nu era exprimabilă | **Opțiunea G1-b**, aprobată CEO 2026-07-24: `raw_series@v1 {source_id, field}`. Seria brută se declară ca orice variabilă, cu `availability` și `role`, deci rămâne sub garda de leakage. `field` este validat față de coloanele declarate ale sursei. Teste: `test_g1_raw_series_exists_and_is_field_constrained`, mutațiile M58–M60 | `REZOLVAT` 2026-07-24 |
| **G2** | Statisticile nu își puteau primi parametrii; motorul ar fi trebuit să deducă la execuție cărei variabile se aplică o statistică | **Opțiunea G2-b**, aprobată CEO 2026-07-24: apel parametrizat `{id, statistic, params}`, în forma predicatelor. Completare descoperită prin mutația M56: în catalogul de statistici, `variable_ref` și `group_ref` au trecut de la domeniul `string` la tipul de referință rezolvabil `variable_ref` — altfel o statistică putea numi o variabilă niciodată declarată. Teste: `test_g2_*`, mutațiile M54–M57 | `REZOLVAT` 2026-07-24 |
| **G-ord** | Ordinea de livrare impusă de auto-verificarea fail-closed a gramaticii | Respectată: gramatică (`statistic_call` în `ve/spec/domains.py`) → registru v1.1 → specificație de referință | `REZOLVAT` 2026-07-24 |

### 2.2 Descoperite la scrierea specificației de referință — NEREZOLVATE

Toate trei au ieșit la suprafață aplicând poarta de publicare cerută de CEO: *o specificație completă pentru un design real, înainte de publicare*. Niciuna nu a fost rezolvată în această revizuire, care a fost strict limitată la G1 și G2.

| ID | Gol | Impact | Rezolvare | Status |
|---|---|---|---|---|
| **G3** | **Nu există primitivă care să transforme un predicat într-o variabilă-indicator.** Consecință: un test care contrastează evenimente cu non-evenimente nu își poate declara `exposure_ref` | **Blochează regresia de control obligatorie**, declarată obligatorie de constituție §6 pentru o clasă largă de candidați. Verificat: necesară pentru 2 din 3 designuri livrate (DC-0004 expunere-eveniment, DC-0008 apartenență la clasă); DC-0003 nu are nevoie (expunere continuă). **Capacitate generică, nu specifică DC-0004** | recomandare `indicator@v1 {predicate}` — registru v1.2, fără schemă nouă. Vezi `REGISTRY_GAPS_G3_G4_G5_ANALYSIS.md` §2 | `ÎN DECIZIE` |
| **G4** | **Semantica listelor de predicate nu este scrisă nicăieri.** `population.include`, `population.exclude` și `cells[].predicates` sunt liste; conjuncția este presupusă, nu documentată | astăzi inofensiv (validarea nu evaluează predicate); devine periculos la F4, unde constructorul de populație ar fixa semantica prin implementare, nu prin decizie | recomandare: documentare normativă în registru + fixturi de conformitate la F4. Vezi analiza §3 | `ÎN DECIZIE` |
| **G5** | **13 parametri cu semantică de referință sunt tipizați ca `string`** — 10 referă variabile, 2 referă teste (`base_test_ref`), 1 referă un predicat (`proportion@v1.predicate_ref`) | o referință nerezolvată trece validarea și devine problemă abia la execuție — aceeași clasă de defect ca G2. Cazul cel mai grav este `regression_control@v1.exposure_ref`, exact parametrul pe care G3 urmează să îl alimenteze | recomandare: retipizare completă + tipurile `test_ref` și `predicate_ref` în gramatică. **Trebuie rezolvat înaintea lui G3.** Vezi analiza §4–§5 | `ÎN DECIZIE` |

---

## 3. Întrebări deschise către Statistician

Ridicate la transcrierea designului DC-0004 în specificația de referință. **Sunt decizii statistice, deci nu pot fi luate de Validation Engine.** Fixtura a fost nevoită să aleagă o variantă pentru a fi completă; alegerile sunt marcate ca atare și nu au valoare normativă.

**Cerere emisă 2026-07-24:** `CLARIFICATION_TO_STATISTICIAN_Q1_Q3.md`. Documentul nu reproduce substituenții din fixtură, pentru a nu ancora răspunsul; ei rămân consemnați mai jos exclusiv pentru audit și **nu au valoare normativă**.

Statisticianul a răspuns (`STATISTICIAN_OPERATIONAL_DEFINITIONS_v1.0.md`, 2026-07-24). Verificarea împotriva scripturilor Alpha in-sample (`SCRIPT_VERIFICATION_Q1_Q3.md`) a arătat că **răspunsurile propuse contrazic convențiile efective in-sample**. Q1–Q3 rămân **DESCHISE** până la reconciliere.

| ID | Întrebare | Răspuns Statistician (propus) | Convenție in-sample (scripturi) | Status |
|---|---|---|---|---|
| **Q1** | Definiția „primei bare a zilei"; granița zilei | ziua ancorată la 17:00 New York, DST | ziua = data calendaristică UTC; eveniment = prima bară care depășește nivelul | **`REZOLVAT — Calea A` (CEO 2026-07-24): 00:00 UTC + prima depășire** |
| **Q2** | K6/K12 aceeași familie? | aceeași familie; K6 primar | ambele calculate; 0013 doar K6 | **`REZOLVAT — Calea A`: K6 decisiv, K12 secundar** |
| **Q3** | Granițele de sesiune | 3 sesiuni ancorate local, DST | 4 sesiuni UTC fixe (+ late) | **`REZOLVAT — Calea A`: 4 sesiuni fixe UTC** |

**DECIZIE DE GUVERNANȚĂ (CEO 2026-07-24):** pentru DC-0004 s-a ales **Calea A — Replicare Strictă** (`RECONCILIATION_DEFINITIONS_v1.0.md`). Convențiile in-sample sunt acum OFICIALE pentru DC-0004: graniță de zi 00:00 UTC, 4 sesiuni fixe UTC (asia/london/ny/late), eveniment = prima depășire, K6 decisiv, baseline per sesiune, one-sided, familie Bonferroni empirică n≥25, seed=7. Definițiile din `STATISTICIAN_OPERATIONAL_DEFINITIONS_v1.0.md` **NU se aplică** acestui re-test (posibilă direcție viitoare, cu re-baseline și protocol separat). Specificația oficială DC-0004 (`tests/fixtures/reference_spec_dc0004.json`, Calea A) validează structural cu 4×E3 (calibrare), dar **NU e completă**: blocată de G8 (familia empirică) și de tensiunea seed.

---

## 4. Puncte de arhitectură rămase deschise (P1–P5)

| ID | Punct | Stare actuală | Decis la | Status |
|---|---|---|---|---|
| **P1** | Evaluează VE mecanic criteriile preînregistrate (`true/false`)? | **blocat activ**: `return.criteria_evaluation` este respins de schemă (mutația M23) | înainte de F7 | `DESCHIS` |
| **P2** | Implementare statistică independentă vs. reutilizarea `code/` | nu se importă nimic din `code/`; se reutilizează doar convenția de localizare a datelor | F5 | `DESCHIS` |
| **P3** | Domeniul Capability Registry | v1.1 publicat ca vocabular; toate metodele `UNVALIDATED` | F5–F6 | `DESCHIS` |
| **P4** | Cine deține sigiliul holdout-ului | granița `2025-10-23T09:15:00Z` ratificată provizoriu ca graniță oficială de lucru (CEO, 2026-07-24); protecția efectivă rămâne de demonstrat prin teste | F8 | `PARȚIAL DECIS` |
| **P5** | Limba artefactelor | chei mașină în engleză, guvernanță și clarificări în română | — | `ACCEPTAT` implicit, reversibil |

---

## 5. Datorie de scop amânată deliberat

| ID | Element | Fază |
|---|---|---|
| **S1** | Metodele statistice (12 de test + 3 de corecție), fiecare cu bateria proprie de calibrare | **PARȚIAL F5/F6/F6.1** — `matched_null@v1` implementat + calibrat: F6 (uniform sub null, curbă de putere, reproducibilitate — `F6_CALIBRATION_RECORD.json`) + F6.1 (robust la vol pe sesiune + cozi grele; testul decisiv „NY vol mare fără efect de nivel → nu respinge", FPR=0.050 — `F6_1_CALIBRATION_RECORD.json`). **Verdict PASS**, dar rămâne `UNVALIDATED` — promovarea la VALIDATED e propusă, în așteptarea ratificării CEO (registrul referit era `CANDIDATE_STATUS_REGISTER_v1.1.md` — eroare de citare CEO, citit; nu lipseau cerințe F6.1). F6.2 (drift real up/down/regime-shift, calibrat pe M15 — niciun eșec clar; reîncadrat de CEO din poartă în acoperire) executat, `F6_2_CALIBRATION_RECORD.json`. Analiză de gap vs. bateria Flow C (`MATCHED_NULL_BATTERY_GAP_ANALYSIS.md`): F6.3 executat (G-AR1/G-FPR/G-PLACEBO): PASS la condiții reale. Caveat: NY-up e celulă n mic (~37) la granița calibrării, cu vulnerabilitate confirmată la reversie ≥5× reala (nu se materializează la φ real −0.018); reversia e specifică PDH (placebo NY-up 0.247 vs PDH 0.025). Corecție: afirmația de stratificare pe VOL retrasă (stratificare doar pe sesiune). Măsurătoare finală (autorizată de CEO, o singură): φ AR(1) condițional pe populația reală NY-up (42 evenimente) = **−0.018 la K6** (= globalul, neamplificat), −0.058 la K12 (~3× global); CI-uri largi care nu exclud pragul −0.10 (n=42 limitează precizia). **PROMOVAT la `VALIDATED` de CEO 2026-07-25** (registru v1.5, `VE-CAPREG-v1.5`, status `PARTIALLY_EXECUTABLE` 1/15), cu 4 caveat-uri obligatorii ca CÂMPURI în `capabilities.json` (domeniu K6; NY-up n mic; vulnerabilitate reversie φ≤−0.10; configurație session-only/ATR-scaled, fără stratificare vol). Raționament CEO: imprecizia φ e risc specific DC-0004 (tipar de reversie), nu al metodei — DC-0008/DC-0003 nu-l ating; DC-0004 deja plafonat. KS p=0.003 acceptat (cozi calibrate, corp conservator = direcție sigură). Restul de 14 metode: `UNVALIDATED`, la cerere |
| **S2** | Population builder + denominatorul per criteriu | **`REZOLVAT` F4** 2026-07-25 (`ve/population/builder.py`) |
| **S3** | Construcția variabilelor + garda de leakage la runtime | **`REZOLVAT` F4** (`ve/variables/`) — primitivele DC-0004; alte primitive la cerere |
| **S4** | Stratul de date, sigilarea pe fereastră la nivel de loader, jurnalul de acces la date | **`REZOLVAT` F4** (`ve/data/`) |
| **S5** | Manifest, PRE-MANIFEST, checksums, bundle write-once, ledger append-only | **`REZOLVAT` F3** 2026-07-25 (`ve/run/runner.py`, `ve/manifest/`, `ve/audit/{checksums,ledger,repo_integrity}.py`) |
| **S6** | Subcomenzile `run` (audit) și `verify` livrate la F3; `rehearse` rămâne F8 | **PARȚIAL** — `run`/`verify` F3; `rehearse` F8 |
| **S7** | Protocolul de resursă sigilată (repetiție + token + consum unic) | F8 |

---

## 6. Poarta permanentă de publicare a registrului

**Decizie CEO 2026-07-24:** înainte de publicarea oricărei versiuni de registru se scrie cel puțin **o specificație completă bazată pe un design real**.

Prima aplicare a regulii a produs imediat trei rezultate: G3, G4 și G5, plus completarea lui G2 (referințe nerezolvabile). Regula se dovedește, la prima folosire, mai productivă decât recitirea catalogului.

---

## 7. Istoricul modificărilor de status

| Data | Intrare | Schimbare |
|---|---|---|
| 2026-07-24 | A1–A7 | create la închiderea F2 |
| 2026-07-24 | G1, G2, G-ord | create la închiderea F2; analiză livrată CEO |
| 2026-07-24 | P1–P5 | preluate din arhitectură; P4 marcat `PARȚIAL DECIS` |
| 2026-07-24 | S1–S7 | create ca datorie de scop |
| 2026-07-24 | A1, A5, A6, A7 | decizii CEO: A1 `REZOLVAT` (JSON-only), A5/A6/A7 `ACCEPTAT` permanent |
| 2026-07-24 | G1, G2, G-ord | `REZOLVAT` prin registrul v1.1 |
| 2026-07-24 | G3, G4, G5 | create la scrierea specificației de referință |
| 2026-07-24 | Q1–Q3 | create: întrebări statistice ridicate de transcrierea designului DC-0004 |
| 2026-07-24 | G3, G4, G5 | `DESCHIS` → `ÎN DECIZIE`; analiză livrată (`REGISTRY_GAPS_G3_G4_G5_ANALYSIS.md`); G3 confirmat ca **capacitate generică**, nu specifică DC-0004; ordine impusă G5 → G3 → G4 |
| 2026-07-24 | Q1–Q3 | `CERERE EMISĂ` (`CLARIFICATION_TO_STATISTICIAN_Q1_Q3.md`), fără valori sugerate |

---

**Nicio intrare nu se închide fără dovadă. O intrare `REZOLVAT` indică faza, data și testul sau artefactul care demonstrează rezolvarea.**
