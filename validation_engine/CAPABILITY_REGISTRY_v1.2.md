# CAPABILITY REGISTRY v1.2
### Vocabularul executabil al Validation Engine — catalogul publicat către Statistician

**Document ID:** VE-CAPREG-v1.2
**Data:** 2026-07-24 · **Autor:** Validation Engine · **Autoritate:** decizie CEO 2026-07-24 pe `REGISTRY_GAPS_G3_G4_G5_ANALYSIS.md`
**Înlocuiește:** `CAPABILITY_REGISTRY_v1.1.md` (păstrat ca istoric)
**Statut:** **PUBLICAT — NEEXECUTABIL.** Nicio metodă nu are statusul `VALIDATED`; nicio specificație nu poate fi executată oficial.
**Forma normativă:** `capabilities.json`

---

## 0. Ce s-a schimbat față de v1.1

Revizuirea acoperă **strict** golurile G3, G4 și G5. Nicio metodă de test/corecție nu a fost adăugată, eliminată sau promovată; niciun status de calibrare nu s-a schimbat. S-a adăugat o singură primitivă de variabilă.

| # | Schimbare | Gol |
|---|---|---|
| 1 | Primitivă nouă: **`indicator@v1 {predicate}`** — transformă un predicat într-o variabilă de expunere 0/1 | G3 |
| 2 | Regulă nouă de disponibilitate: indicatorul (și, generic, orice variabilă) nu poate fi disponibil mai devreme decât dependențele lui; verificat recursiv; ciclurile de referință sunt respinse | G3 |
| 3 | 13 parametri de referință retipizați din `string` în tipuri rezolvabile: 10 → `variable_ref`, 2 → `test_ref`, 1 → `predicate_ref` | G5 |
| 4 | Două tipuri noi de referință în gramatică: **`test_ref`** și **`predicate_ref`**; id-urile de predicat devin unice pe întreaga specificație | G5 |
| 5 | Semantica listelor de predicate, documentată normativ (conjuncție; `exclude` la orice potrivire; liste goale; denominator per criteriu) | G4 |

**Ordinea de livrare impusă și respectată:** gramatică (`test_ref`, `predicate_ref`) + validator → registru v1.2 → specificațiile de referință. G5 înaintea lui G3, pentru că indicatorul alimentează `regression_control@v1.exposure_ref`, retipizat prin G5.

**Nicio versiune nouă de schemă.** `SPEC_SCHEMA_v1.0.json` rămâne neatins — extinderea vocabularului nu cere schemă nouă.

---

## 1. Reguli (blocul `rules`)

Pe lângă regulile din v1.0/v1.1 (fără parametri opționali, vocabular închis, corecție explicită, status de calibrare, două etape, estimator de p, denominator), v1.2 adaugă:

- **`predicate_list_conjunction` (G4):** fiecare listă de predicate este o **conjuncție (ȘI logic)**. `population.include` selectează barele care satisfac TOATE predicatele; o bară este exclusă dacă potrivește ORICARE predicat din `population.exclude`; `cells[].predicates` este ȘI-ul elementelor. Logica ne-conjunctivă se scrie explicit cu `and@v1`/`or@v1`/`not@v1`.
- **`empty_predicate_lists` (G4):** `exclude: []` înseamnă „nicio excludere", declarat explicit. O celulă cu `predicates: []` înseamnă „toată populația" (teste nestratificate). `include` trebuie să fie nevidă (schema).
- **`per_criterion_denominator` (G4):** fiindcă fiecare predicat de includere are un id unic și lista este conjuncție, constructorul de populație raportează, per criteriu de includere, câte bare candidate a respins. Unicitatea globală a id-urilor de predicat este ce face denominatorul neambiguu.
- **`indicator_availability` (G3):** `indicator@v1` transformă un predicat într-o variabilă 0/1. Disponibilitatea lui nu poate fi mai devreme (mai negativă) decât disponibilitatea ORICĂREI variabile folosite în predicat, verificat recursiv. Generic: nicio variabilă nu poate declara o disponibilitate mai devreme decât dependențele ei.
- **`reference_types_resolved` (G5):** orice parametru cu semantică de referință (`variable_ref`, `test_ref`, `predicate_ref`, `data_source_id`, `statistic_call`) este rezolvat fail-closed la validare. O referință nerezolvată oprește cu E2 înainte de orice acces la date; niciodată amânată la execuție.

---

## 2. Surse de date, resurse sigilate

Neschimbate față de v1.1. Patru surse OANDA XAUUSD (M15/H1/H4/D1) cu hash-uri verificate; graniță sigilată unică `2025-10-23T09:15:00Z`, provizorie. Vezi `CAPABILITY_REGISTRY_v1.1.md` §2–§3 pentru detalii; valorile sunt identice în `capabilities.json`.

**Notă:** nu există sursă la timeframe mai fin de M15. Un candidat care are nevoie de agregare sub-bară (ex. raportul de volum M1/M5 al DC-0008) nu este exprimabil — gol **G6**, înregistrat în backlog, nerezolvat.

---

## 3. Primitive de variabile (V) — 16

| ID | Scop | Parametri obligatorii |
|---|---|---|
| **`indicator@v1`** *(nou, G3)* | **transformă un predicat într-o variabilă de expunere 0/1** | **`predicate`** |
| `raw_series@v1` | referință directă la un câmp al sursei | `source_id`, `field` |
| `lag@v1` | deplasare temporală | `variable_ref` *(G5: rezolvat)*, `bars` |
| `atr@v1` | Average True Range | `source_id`, `period`, `method` |
| `parkinson_volatility@v1` | volatilitate log-range (metrica primară) | `source_id`, `window`, `output_form` |
| `realized_volatility@v1` | volatilitate realizată | `source_id`, `window`, `return_basis`, `output_form` |
| `hour_of_day_volatility_profile@v1` | profilul orar de volatilitate | `source_id`, `estimator`, `lookback_days`, `normalization`, `min_observations_per_hour` |
| `prior_period_extreme@v1` | extremul unei perioade anterioare (PDH/PDL) | `source_id`, `extreme`, `periods_back`, `availability_rule`, `availability_delay_seconds` |
| `forward_return@v1` | randament forward pe orizont fix | `source_id`, `horizon_bars`, `basis`, `units` |
| `baseline_forward_mean@v1` | baseline forward stratificat | `source_id`, `horizon_bars`, `strata`, `estimation_window`, `exclude_event_bars` |
| `forward_excess@v1` | excesul față de un baseline | `forward_return_ref` *(G5)*, `baseline_ref` *(G5)* |
| `session_label@v1` | etichetă de sesiune (granițe declarate numeric) | `boundaries` |
| `bar_range_ratio@v1` | raport între componente de bară | `source_id`, `numerator`, `denominator`, `window` |
| `volume_zscore@v1` | volum normalizat | `source_id`, `window`, `min_periods` |
| `gap@v1` | gap la deschidere | `source_id`, `gap_kind`, `units` |
| `rolling_quantile@v1` | cuantilă mobilă | `variable_ref` *(G5)*, `window`, `q`, `min_periods` |

**`indicator@v1`** — semantică:
- produce 1 unde predicatul e adevărat, 0 altfel;
- se declară ca orice variabilă, cu `availability` și `role`, deci rămâne sub garda de leakage;
- disponibilitatea lui trebuie ≥ disponibilitatea oricărei variabile din predicat (regula `indicator_availability`);
- este destinat, tipic, parametrului `exposure_ref` al unei regresii de control, când expunerea este un eveniment discret (nu o variabilă continuă).

Aceasta este piesa care face exprimabilă regresia de control obligatorie din constituția §6 (control de regim ambiental cu termen de interacțiune) pentru orice candidat cu expunere-eveniment.

---

## 4. Predicate de populație (P) — 10

Neschimbate. Algebră generică închisă: `compare`, `and`/`or`/`not`, `bar_position`, `in_session`, `in_window`, `crosses`, `sequence`, `cooldown`. Vezi §5 din v1.1.

**Gol consemnat (G7):** nu există primitivă „prima apariție în domeniu" (`first-in-scope`). Un eveniment de tip „prima bară a zilei care depășește un nivel" (definiția in-sample a DC-0004) nu este exprimabil; predicatele selectează *toate* barele care satisfac o condiție, nu *prima*. Înregistrat în backlog, nerezolvat.

---

## 5. Statistici (S) — 7

Se invocă prin `statistic_call` `{id, statistic, params}` (v1.1). Parametrii `variable_ref`/`group_ref` sunt rezolvabili (v1.1). Neschimbate structural în v1.2.

---

## 6. Metode de test (M) — 12 · Corecții (C) — 3

Toate `UNVALIDATED`. Singura schimbare v1.2 este retipizarea parametrilor de referință (G5):

| Metodă | Parametru | v1.1 | v1.2 |
|---|---|---|---|
| `dip_test@v1`, `gaussian_mixture@v1`, `changepoint@v1`, `descriptive_measurement@v1` | `variable_ref` | `string` | `variable_ref` |
| `regression_control@v1` | `outcome_ref`, `exposure_ref` | `string` | `variable_ref` |
| `placebo_control@v1`, `multiverse@v1` | `base_test_ref` | `string` | `test_ref` |
| `proportion@v1` (statistică) | `predicate_ref` | `string` | `predicate_ref` |

Restul parametrilor și toate cele 15 statusuri de calibrare rămân neschimbate.

---

## 7. Ce nu conține registrul, deliberat

Neschimbat față de v1.1 (fără sesiuni predefinite, praguri implicite, evenimente specifice unei ipoteze, auto-selecție, metrici de profitabilitate, corecție implicită). Plus, consemnate ca goluri deschise: **G6** (agregare sub-bară / sursă M1-M5), **G7** (`first-in-scope`).

---

## 8. Poarta de publicare (decizie CEO 2026-07-24)

Înainte de publicarea oricărei versiuni de registru se scriu specificații complete pentru **designuri reale**. La v1.2, poarta a fost: DC-0004 exprimat **15/15** (inclusiv regresia de control) și o a doua specificație pentru **DC-0008** (formă diferită). A doua a descoperit G6; verificarea Q1–Q3 împotriva scripturilor in-sample a descoperit G7. Regula continuă să producă goluri reale la fiecare aplicare.

---

**Statusul registrului la v1.2: PUBLICAT — NEEXECUTABIL. Toate metodele sunt `UNVALIDATED`.**
