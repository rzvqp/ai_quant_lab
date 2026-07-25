# CAPABILITY REGISTRY v1.0
### Vocabularul executabil al Validation Engine — catalogul publicat către Statistician

**Document ID:** VE-CAPREG-v1.0
**Data:** 2026-07-24 · **Autor:** Validation Engine
**Statut:** **PUBLICAT — NEEXECUTABIL.** Registrul definește vocabularul în care se scriu specificațiile. **Nicio metodă nu are încă statusul `VALIDATED`, deci nicio specificație nu poate fi executată oficial la această dată.** Statusurile se schimbă individual, prin fazele F5–F6.
**Documente guvernante:** `statistician/STATISTICIAN_VALIDATION_ENGINE_CONTRACT_v1.0.md` · `validation_engine/VALIDATION_ENGINE_ARCHITECTURE_v1.0.md`
**Forma mașină:** `capabilities.json` (sursa unică de adevăr pentru validarea etapa 2)

---

## 0. La ce servește acest document

Contractul §2.9 interzice Validation Engine să aleagă metode, parametri sau praguri. Ca interdicția să fie executabilă și nu doar declarativă, trebuie să existe un catalog închis: **tot ce poate fi executat este listat aici; tot ce nu este listat aici oprește rularea (eroare E3).**

Statisticianul scrie specificații exclusiv în vocabularul de mai jos. Când are nevoie de ceva ce nu există în registru, cere extinderea registrului — nu o improvizație a VE.

### 0.1 Regula parametrilor obligatorii

> **Registrul nu conține parametri opționali. Niciun parametru nu are valoare implicită.**

Un parametru cu default ar însemna o alegere făcută de Validation Engine, ceea ce contractul §1.7 interzice explicit. Acolo unde registrul menționează o „valoare convențională în laborator", aceasta este **informație factuală**, nu un default: specificația trebuie oricum să o scrie explicit, altfel rularea se oprește.

Aceeași regulă se aplică absenței unei corecții pentru testări multiple: „fără corecție" trebuie declarat explicit prin `none@v1`, nu obținut prin omiterea secțiunii.

### 0.2 Statusul de calibrare

| Status | Semnificație | Poate fi referit într-o specificație oficială |
|---|---|---|
| `VALIDATED` | A trecut integral bateria sintetică de acceptare | DA |
| `UNVALIDATED` | Neimplementat sau necalibrat | NU |
| `QUARANTINED` | Implementat, dar a eșuat bateria de acceptare | NU, până la re-validare |

Motivul pentru care acest mecanism există este documentat în laborator: `docs/EMPIRICAL_PVALUE_SPEC.md` consemnează că implementarea matched-null existentă în `code/` este necalibrată („fails synthetic-null; MUST be fixed+re-validated before official use"). Statusul face imposibilă reintrarea accidentală în uz oficial a unei metode în această stare.

**La v1.0, toate metodele sunt `UNVALIDATED`**, pentru că nimic nu este încă implementat. Registrul este vocabular, nu capacitate.

### 0.3 Validarea în două etape

| Etapă | Instrument | Ce verifică |
|---|---|---|
| 1 | `SPEC_SCHEMA_v1.0.json` | **forma** specificației: secțiuni prezente, tipuri, structură, praguri numerice |
| 2 | `capabilities.json` (acest registru) | **vocabularul**: ID-uri existente, parametri obligatorii prezenți, domenii respectate, status de calibrare |

Consecință de design: metodele nu sunt duplicate în schemă. Registrul este sursa unică de adevăr pentru ce se poate executa, iar schema descrie doar forma. O extindere a registrului nu cere o versiune nouă de schemă.

---

## 1. Surse de date (DS)

Valorile de mai jos au fost calculate direct din fișiere la 2026-07-24 și sunt verificabile.

| ID | Fișier | Rânduri | Coloane | Acoperire (UTC) | SHA-256 |
|---|---|---|---|---|---|
| `OANDA_XAUUSD_M15@v1` | `data/market/OANDA_XAUUSD_M15.csv` | 84.152 | time, open, high, low, close, volume | 2022-12-16T10:45:00Z → 2026-07-13T06:00:00Z | `c777cb9c…c64e86` |
| `OANDA_XAUUSD_H1@v1` | `data/market/OANDA_XAUUSD_H1.csv` | 20.832 | + `sub` | 2023-01-02T23:00:00Z → 2026-07-13T05:00:00Z | `5ff7420a…868baa` |
| `OANDA_XAUUSD_H4@v1` | `data/market/OANDA_XAUUSD_H4.csv` | 5.450 | + `sub` | 2023-01-02T22:00:00Z → 2026-07-13T01:00:00Z | `9a6e1111…e743da` |
| `OANDA_XAUUSD_D1@v1` | `data/market/OANDA_XAUUSD_D1.csv` | 909 | + `sub` | 2023-01-02T22:00:00Z → 2026-07-09T21:00:00Z | `a5fc340c…8a4537` |

Hash-urile complete sunt în `capabilities.json`. Specificația trebuie să declare hash-ul sursei pe care o folosește; nepotrivirea oprește rularea (E4).

**Notă de neomogenitate, raportată ca atare, nu corectată:** M15 nu are coloana `sub` (celelalte trei o au) și începe cu ~2 săptămâni înainte de 2023-01-01, spre deosebire de H1/H4/D1. VE nu armonizează și nu completează datele.

---

## 2. Registrul de resurse sigilate (SEALED) — **PROVIZORIU, în așteptarea ratificării CEO (punct P4)**

Constatare verificată: **există o singură graniță sigilată, comună tuturor timeframe-urilor — `2025-10-23T09:15:00Z`.** Două derivări independente coincid:

- `code/run_full_campaign.py:3` împarte M15 la 60%/80% din 84.152 bare → holdout = 16.831 bare începând exact cu `2025-10-23T09:15:00Z`, identic cu `REPRODUCIBILITY_AUDIT.md`;
- DC-0004 citează „16.623 bare H1, 2023-01-02→2025-10-23" → exact numărul de bare H1 aflate înainte de aceeași graniță.

| Sursă | Fereastră deschisă | Bare deschise | Fereastră SIGILATĂ | Bare sigilate |
|---|---|---|---|---|
| M15 | … → 2025-10-23T09:00:00Z | 67.321 | 2025-10-23T09:15:00Z → … | 16.831 |
| H1 | … → 2025-10-23T09:00:00Z | 16.623 | 2025-10-23T10:00:00Z → … | 4.209 |
| H4 | … → 2025-10-23T09:00:00Z | 4.350 | 2025-10-23T13:00:00Z → … | 1.100 |
| D1 | … → 2025-10-22T21:00:00Z | 726 | 2025-10-23T21:00:00Z → … | 183 |

Regim de acces, conform arhitecturii §1.3: fereastra sigilată nu este încărcată în memorie, nu doar ignorată; deschiderea cere token CEO valid, o repetiție prealabilă reușită pe fereastră deschisă și resursă neconsumată; consumul este unic și irevocabil.

Acest tabel **nu creează** sigiliul — îl consemnează. Autoritatea asupra sigiliului rămâne deschisă până la ratificarea punctului P4.

---

## 3. Primitive de variabile (V)

Fiecare variabilă din specificație declară: `id`, `primitive`, `params`, `availability`, `role`. Rolurile admise: `exposure`, `outcome`, `control`, `stratifier`, `diagnostic`.

| ID | Scop | Parametri obligatorii |
|---|---|---|
| `lag@v1` | Deplasare temporală explicită a unei variabile | `variable_ref`, `bars` (≥1) |
| `atr@v1` | Average True Range | `source_id`, `period`, `method` (`wilder`\|`sma`) |
| `parkinson_volatility@v1` | Volatilitate log-range ln(H/L) — metrica primară a laboratorului | `source_id`, `window`, `output_form` (`variance`\|`stdev`) |
| `realized_volatility@v1` | Volatilitate realizată close-to-close | `source_id`, `window`, `return_basis`, `output_form` |
| `hour_of_day_volatility_profile@v1` | Profilul orar de volatilitate (primitivul promovat în lab) | `source_id`, `estimator`, `lookback_days`, `normalization`, `min_observations_per_hour` |
| `prior_period_extreme@v1` | Extremul unei perioade anterioare (PDH/PDL etc.) | `source_id`, `extreme`, `periods_back`, `availability_rule`, `availability_delay_seconds` |
| `forward_return@v1` | Randament forward pe orizont fix | `source_id`, `horizon_bars`, `basis`, `units` |
| `baseline_forward_mean@v1` | Baseline forward, stratificat | `source_id`, `horizon_bars`, `strata`, `estimation_window`, `exclude_event_bars` |
| `forward_excess@v1` | Excesul față de un baseline declarat | `forward_return_ref`, `baseline_ref` |
| `session_label@v1` | Etichetă de sesiune | `boundaries` (listă explicită `{name, start_utc, end_utc}`) |
| `bar_range_ratio@v1` | Raport între componente de bară (corp/umbre/range) | `source_id`, `numerator`, `denominator`, `window` |
| `volume_zscore@v1` | Volum normalizat | `source_id`, `window`, `min_periods` |
| `gap@v1` | Gap la deschidere | `source_id`, `gap_kind`, `units` |
| `rolling_quantile@v1` | Cuantilă mobilă a unei variabile | `variable_ref`, `window`, `q`, `min_periods` |

**`session_label@v1` nu conține nicio definiție de sesiune predefinită.** Nu există „NY", „Londra" sau „Asia" în VE. Granițele se declară numeric în specificație. Definiția sesiunii este o alegere de proiectare, deci aparține Statisticianului.

### 3.1 Disponibilitate și garda de leakage

Fiecare variabilă declară obligatoriu:

```yaml
availability: {anchor: event_time, offset_bars: -1, source_id: OANDA_XAUUSD_H1@v1}
```

Garda verifică **mecanic** regula declarată, nu o deduce:

- `exposure`, `control`, `stratifier` → `offset_bars` trebuie să fie ≤ 0 (strict anterioare sau contemporane evenimentului, conform declarației);
- `outcome` → `offset_bars` > 0 este permis, dar fereastra de rezultat trebuie să fie disjunctă de fereastra de clasificare;
- suprapunerea celor două ferestre declanșează tripwire-ul și oprește rularea (E6).

---

## 4. Predicate de populație (P)

Populația se construiește dintr-o **algebră generică închisă**. VE nu conține și nu va conține niciodată logică specifică unei ipoteze — nu există un predicat `sweep_reject` sau `liquidity_grab`. Astfel de evenimente se compun din primitivele de mai jos, iar compunerea aparține Statisticianului.

| ID | Scop | Parametri obligatorii |
|---|---|---|
| `compare@v1` | Comparație între variabile sau față de o constantă numerică | `left`, `op` (`<`,`<=`,`>`,`>=`,`==`,`!=`), `right` |
| `and@v1` / `or@v1` / `not@v1` | Compunere logică | `operands` |
| `bar_position@v1` | Poziția barei într-un ciclu | `scope` (`day`\|`session`\|`week`), `index`, `from` (`start`\|`end`) |
| `in_session@v1` | Apartenența la o sesiune declarată | `session_ref`, `names` |
| `in_window@v1` | Apartenența la o fereastră temporală | `start`, `end`, `bounds` |
| `crosses@v1` | Traversarea unui nivel | `series`, `level`, `direction`, `basis` |
| `sequence@v1` | Compunere ordonată pe bare consecutive | `steps`, `max_gap_bars` |
| `cooldown@v1` | Regulă de deduplicare a evenimentelor apropiate | `min_bars_between_events` |

`cooldown@v1` este obligatoriu în orice specificație de populație. Fără el, „câte evenimente distincte există" ar fi o decizie a VE. Dacă nu se dorește deduplicare, se declară explicit `min_bars_between_events: 0`.

### 4.1 Denominatorul

Constructorul de populație produce întotdeauna, alături de setul de evenimente, **numărul de bare candidate evaluate și numărul respins de fiecare criteriu în parte**. Este raportat automat, nu la cerere — este exact golul identificat ca universal în `STATISTICIAN_PHASE1_SUMMARY.md` §1 („absența universală a denominatorului").

---

## 5. Statistici (S)

Valori admise pentru parametrul `statistic` al metodelor de test.

| ID | Definiție | Parametri obligatorii |
|---|---|---|
| `mean@v1` | media aritmetică | `variable_ref` |
| `median@v1` | mediana | `variable_ref` |
| `trimmed_mean@v1` | media trunchiată simetric | `variable_ref`, `trim_pct` |
| `proportion@v1` | proporția instanțelor care satisfac un predicat | `variable_ref`, `predicate_ref` |
| `sum@v1` | suma | `variable_ref` |
| `count@v1` | numărul de instanțe | — |
| `difference_in_means@v1` | diferența de medii între două grupuri declarate | `variable_ref`, `group_ref`, `group_a`, `group_b` |

---

## 6. Metode de test (M)

Toate au, la v1.0, `calibration_status: UNVALIDATED`. Poarta de acceptare per metodă este indicată în ultima coloană (suitele din arhitectură §11 / plan F5–F6).

| ID | Scop | Parametri obligatorii | Poartă |
|---|---|---|---|
| `matched_null@v1` | Null cu potrivire structurală (timing aleator, invarianți păstrați declarativ) | `statistic`, `tail`, `B`, `preserve`, `resample_unit`, `min_n` | S1, S3, S4 |
| `block_bootstrap@v1` | Bootstrap pe blocuri contigue (păstrează autocorelația) | `statistic`, `block_length`, `tail`, `B`, `centering` | S1, S3, S4, S8 |
| `iid_bootstrap@v1` | Bootstrap iid — **diagnostic**, ignoră autocorelația | `statistic`, `tail`, `B`, `centering` | S1, S3, S8 |
| `permutation_test@v1` | Permutarea etichetelor | `statistic`, `tail`, `B`, `permute_label`, `strata` | S1, S3, S4 |
| `dip_test@v1` | Test de unimodalitate (Hartigan) | `variable_ref`, `B` | S1, S3 |
| `gaussian_mixture@v1` | Model de amestec, pentru separare propusă | `variable_ref`, `k_components`, `selection_criterion`, `n_init`, `max_iter`, `tol` | S1 |
| `changepoint@v1` | Detectare de discontinuitate | `variable_ref`, `algorithm`, `cost_model`, `penalty`, `min_segment` | S1 |
| `regression_control@v1` | Regresie cu controale explicite și termen de interacțiune | `outcome_ref`, `exposure_ref`, `controls`, `interaction`, `se_estimator`, `se_params` | S1, S3, S5 |
| `placebo_control@v1` | Control negativ / nivel placebo | `base_test_ref`, `placebo_definition`, `repeats` | S1, S5 |
| `multiverse@v1` | Analiză de sensibilitate pe definiții alternative | `base_test_ref`, `grid` | S1 |
| `power_simulation@v1` | Putere / dimensiune minimă de eșantion prin simulare | `effect_sizes`, `n_grid`, `alpha`, `B`, `generator` | S1, S4 |
| `descriptive_measurement@v1` | Măsurare fără test (ex. distribuția unui raport, pentru determinarea unui prag) | `variable_ref`, `statistics`, `quantiles` | S1 |

Note:

- `matched_null@v1` cere `preserve` — lista explicită a invarianților păstrați (ex. sesiune, direcție, număr de semnale, profil de risc). VE nu deduce ce trebuie păstrat; un null potrivit greșit este exact modul în care implementarea existentă a eșuat.
- `tail` nu are valoare implicită. `docs/EMPIRICAL_PVALUE_SPEC.md` folosește one-sided cu justificare scrisă; acea justificare aparține specificației, nu registrului.
- Toate metodele bazate pe reeșantionare raportează obligatoriu `k`, `B`, `p_hat = (k+1)/(B+1)`, CI Monte-Carlo și rezoluția MC. `p = 0` nu poate fi produs.
- `descriptive_measurement@v1` există pentru cazuri ca măsurătoarea de prag a DC-0008, care este o măsurare, nu un test. Nu produce valoare p.

---

## 7. Metode de corecție pentru testări multiple (C)

| ID | Parametri obligatorii | Ieșiri |
|---|---|---|
| `bonferroni@v1` | `alpha`, `family_members` | `p_adjusted`, `threshold_per_test`, `family_size` |
| `benjamini_hochberg@v1` | `alpha`, `family_members`, `variant` (`bh`\|`by`) | `p_adjusted`, `bh_thresholds`, `family_size` |
| `none@v1` | `justification_present` | — |

`family_members` este o **listă enumerată explicit** de teste/celule. VE nu deduce apartenența la familie și nu descoperă singur că un test face parte dintr-o familie mai mare. Definirea familiei este o decizie statistică și aparține Statisticianului (constituție §6, §8.4).

---

## 8. Ce nu conține registrul, deliberat

- **Definiții de sesiune** (NY/Londra/Asia) — se declară numeric în specificație.
- **Praguri implicite** de orice fel.
- **Evenimente specifice unei ipoteze** (sweep-reject, liquidity grab, compresie) — se compun din §4.
- **Metode de „auto-selecție"** a pragului, orizontului sau modelului.
- **Metrici de profitabilitate** (PF, Sharpe, drawdown, expectancy) ca statistici de verdict. Constituția §3 exclude evaluarea profitabilității din rolul statistic; dacă vor fi vreodată necesare ca diagnostic, se adaugă explicit, marcate ca atare.
- **Corecție implicită** — absența secțiunii nu înseamnă „fără corecție"; vezi `none@v1`.

---

## 9. Extinderea registrului

O cerere de extindere vine de la Statistician și conține: metoda dorită, motivul statistic, parametrii care trebuie să rămână în controlul specificației, și ieșirile așteptate. Extinderea produce o versiune nouă de registru (v1.1+), iar metoda nouă intră cu `UNVALIDATED` până trece bateria proprie de acceptare. **Nicio metodă nu devine executabilă pentru că este urgentă.**

---

## 10. Versionare

`capabilities.json` este forma normativă; acest document este forma citibilă. La divergență, fișierul JSON are prioritate. Orice modificare a listei de metode, a parametrilor obligatorii sau a domeniilor cere o versiune nouă de registru și o notă de decizie.

---

**Statusul registrului la v1.0: PUBLICAT — NEEXECUTABIL. Toate metodele sunt `UNVALIDATED`. Nicio specificație nu poate fi executată oficial până la finalizarea fazelor F5–F6.**

**Nu s-a scris niciun cod. Nu s-a executat nicio validare. Datele au fost citite exclusiv pentru calculul hash-urilor și al acoperirii declarate în §1–§2; nu au fost modificate.**
