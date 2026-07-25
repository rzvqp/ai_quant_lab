# CAPABILITY REGISTRY v1.1
### Vocabularul executabil al Validation Engine — catalogul publicat către Statistician

**Document ID:** VE-CAPREG-v1.1
**Data:** 2026-07-24 · **Autor:** Validation Engine · **Autoritate:** decizie CEO 2026-07-24 pe `REGISTRY_GAPS_G1_G2_ANALYSIS.md`
**Înlocuiește:** `CAPABILITY_REGISTRY_v1.0.md` (păstrat ca istoric, nemodificat)
**Statut:** **PUBLICAT — NEEXECUTABIL.** Nicio metodă nu are statusul `VALIDATED`, deci nicio specificație nu poate fi executată oficial. Statusurile se schimbă individual, prin fazele F5–F6.
**Forma normativă:** `capabilities.json` (sursa unică de adevăr pentru validarea etapa 2)

---

## 0. Ce s-a schimbat față de v1.0

Revizuirea acoperă **strict** golurile G1 și G2. Nicio metodă nu a fost adăugată, eliminată sau promovată; niciun status de calibrare nu s-a schimbat.

| # | Schimbare | Gol |
|---|---|---|
| 1 | Primitivă nouă de variabilă: **`raw_series@v1 {source_id, field}`** | G1 |
| 2 | Parametrul `statistic` al metodelor `matched_null@v1`, `block_bootstrap@v1`, `iid_bootstrap@v1`, `permutation_test@v1` trece de la domeniul `statistic_id` la **`statistic_call`**; `descriptive_measurement@v1.statistics` trece de la `list[statistic_id]` la `list[statistic_call]` | G2 |
| 3 | Două reguli noi în §0.1: forma apelului de statistică și semantica disponibilității pentru serii brute | G1, G2 |

`statistic_id` rămâne definit în gramatică, dar nu mai este folosit de nicio intrare din registru.

**Ordinea de livrare impusă și respectată:** gramatica (`ve/spec/domains.py`) → registrul v1.1 → specificația de referință.

---

## 1. La ce servește acest document

Contractul §2.9 interzice Validation Engine să aleagă metode, parametri sau praguri. Ca interdicția să fie executabilă și nu doar declarativă, există un catalog închis: **tot ce poate fi executat este listat aici; tot ce nu este listat aici oprește rularea (E3).**

Statisticianul scrie specificații exclusiv în vocabularul de mai jos. Când are nevoie de ceva ce nu există, cere extinderea registrului — nu o improvizație a motorului.

### 1.1 Regula parametrilor obligatorii

> **Registrul nu conține parametri opționali. Niciun parametru nu are valoare implicită.**

Un parametru cu default ar fi o alegere făcută de Validation Engine, interzisă de contractul §1.7. „Fără corecție" se declară explicit prin `none@v1`, nu prin omiterea secțiunii.

### 1.2 Forma apelului de statistică *(nou în v1.1)*

O statistică se invocă drept **declarație inline parametrizată**, în exact forma pe care schema o cere predicatelor:

```json
"statistic": { "id": "s_mean_excess_k6", "statistic": "mean@v1",
               "params": { "variable_ref": "cont_excess_k6" } }
```

Motivul este cauza de fond a lui G2: statisticile erau singura categorie cu parametri obligatorii fără loc de declarare în specificație. Fără această formă, motorul ar fi trebuit să **deducă** la execuție cărei variabile i se aplică statistica — exact ce interzice contractul.

### 1.3 Statusul de calibrare

| Status | Semnificație | Referibil într-o specificație oficială |
|---|---|---|
| `VALIDATED` | a trecut integral bateria sintetică de acceptare | DA |
| `UNVALIDATED` | neimplementat sau necalibrat | NU |
| `QUARANTINED` | implementat, dar a eșuat bateria | NU, până la re-validare |

Mecanismul există pentru că `docs/EMPIRICAL_PVALUE_SPEC.md` consemnează implementarea matched-null existentă în `code/` drept necalibrată. **La v1.1, toate metodele rămân `UNVALIDATED`.** Registrul este vocabular, nu capacitate.

### 1.4 Validarea în două etape

| Etapă | Instrument | Verifică |
|---|---|---|
| 1 | `SPEC_SCHEMA_v1.0.json` | forma: secțiuni, tipuri, structură, praguri numerice |
| 2 | `capabilities.json` | vocabularul: ID-uri, parametri obligatorii, domenii, status de calibrare, disponibilitate, ferestre sigilate |

Metodele nu sunt duplicate în schemă. O extindere de registru nu cere o versiune nouă de schemă — motiv pentru care v1.1 nu a atins `SPEC_SCHEMA_v1.0.json`.

---

## 2. Surse de date (DS)

Valori calculate direct din fișiere la 2026-07-24, neschimbate la v1.1.

| ID | Fișier | Rânduri | Coloane | Acoperire (UTC) | SHA-256 |
|---|---|---|---|---|---|
| `OANDA_XAUUSD_M15@v1` | `data/market/OANDA_XAUUSD_M15.csv` | 84.152 | time, open, high, low, close, volume | 2022-12-16T10:45Z → 2026-07-13T06:00Z | `c777cb9c…c64e86` |
| `OANDA_XAUUSD_H1@v1` | `data/market/OANDA_XAUUSD_H1.csv` | 20.832 | + `sub` | 2023-01-02T23:00Z → 2026-07-13T05:00Z | `5ff7420a…868baa` |
| `OANDA_XAUUSD_H4@v1` | `data/market/OANDA_XAUUSD_H4.csv` | 5.450 | + `sub` | 2023-01-02T22:00Z → 2026-07-13T01:00Z | `9a6e1111…e743da` |
| `OANDA_XAUUSD_D1@v1` | `data/market/OANDA_XAUUSD_D1.csv` | 909 | + `sub` | 2023-01-02T22:00Z → 2026-07-09T21:00Z | `a5fc340c…8a4537` |

**Neomogenitate raportată, nu corectată:** M15 nu are coloana `sub` pe care celelalte trei o au. Începând cu v1.1, această diferență devine operațională: `raw_series@v1` cu `field: "sub"` pe M15 se oprește cu E2, verificat mecanic față de coloanele declarate.

---

## 3. Registrul de resurse sigilate (SEALED)

Graniță unică, comună tuturor timeframe-urilor: **`2025-10-23T09:15:00Z`**, ratificată provizoriu de CEO (2026-07-24) ca graniță oficială de lucru. Protecția efectivă rămâne de demonstrat prin teste (F4/F8).

| Sursă | Fereastră deschisă | Bare deschise | Fereastră SIGILATĂ | Bare sigilate |
|---|---|---|---|---|
| M15 | … → 2025-10-23T09:00Z | 67.321 | 2025-10-23T09:15Z → … | 16.831 |
| H1 | … → 2025-10-23T09:00Z | 16.623 | 2025-10-23T10:00Z → … | 4.209 |
| H4 | … → 2025-10-23T09:00Z | 4.350 | 2025-10-23T13:00Z → … | 1.100 |
| D1 | … → 2025-10-22T21:00Z | 726 | 2025-10-23T21:00Z → … | 183 |

---

## 4. Primitive de variabile (V)

Fiecare variabilă declară `id`, `primitive`, `params`, `availability`, `role`. Roluri: `exposure`, `outcome`, `control`, `stratifier`, `diagnostic`.

| ID | Scop | Parametri obligatorii |
|---|---|---|
| **`raw_series@v1`** *(nou)* | **referință directă la un câmp al sursei** | **`source_id`, `field` ∈ {open, high, low, close, volume, sub}** |
| `lag@v1` | deplasare temporală explicită | `variable_ref`, `bars` |
| `atr@v1` | Average True Range | `source_id`, `period`, `method` |
| `parkinson_volatility@v1` | volatilitate log-range ln(H/L) — metrica primară a laboratorului | `source_id`, `window`, `output_form` |
| `realized_volatility@v1` | volatilitate realizată | `source_id`, `window`, `return_basis`, `output_form` |
| `hour_of_day_volatility_profile@v1` | profilul orar de volatilitate | `source_id`, `estimator`, `lookback_days`, `normalization`, `min_observations_per_hour` |
| `prior_period_extreme@v1` | extremul unei perioade anterioare (PDH/PDL) | `source_id`, `extreme`, `periods_back`, `availability_rule`, `availability_delay_seconds` |
| `forward_return@v1` | randament forward pe orizont fix | `source_id`, `horizon_bars`, `basis`, `units` |
| `baseline_forward_mean@v1` | baseline forward, stratificat | `source_id`, `horizon_bars`, `strata`, `estimation_window`, `exclude_event_bars` |
| `forward_excess@v1` | excesul față de un baseline declarat | `forward_return_ref`, `baseline_ref` |
| `session_label@v1` | etichetă de sesiune | `boundaries` (listă explicită) |
| `bar_range_ratio@v1` | raport între componente de bară | `source_id`, `numerator`, `denominator`, `window` |
| `volume_zscore@v1` | volum normalizat | `source_id`, `window`, `min_periods` |
| `gap@v1` | gap la deschidere | `source_id`, `gap_kind`, `units` |
| `rolling_quantile@v1` | cuantilă mobilă | `variable_ref`, `window`, `q`, `min_periods` |

**`session_label@v1` nu conține nicio definiție de sesiune predefinită.** „NY", „Londra", „Asia" nu există în motor; granițele se declară numeric.

### 4.1 Disponibilitate și garda de leakage

```yaml
availability: {anchor: event_time, offset_bars: -1, source_id: <sursă>}
```

- `exposure`, `control`, `stratifier` → `offset_bars ≤ 0`;
- `outcome` → offset pozitiv permis, cu fereastra de rezultat disjunctă de cea de clasificare.

**Semantica pentru `raw_series@v1`:** `offset_bars` **selectează bara** a cărei valoare se ia (0 = bara evenimentului). La primitivele calculate, precum `atr@v1`, offsetul înseamnă „calculat pe date până la acea bară". Diferența este declarată explicit, nu lăsată la intuiție.

Seriile brute nu creează un spațiu de nume paralel: se declară ca orice altă variabilă, deci **garda de leakage se aplică nemodificat**. Acesta a fost motivul respingerii variantelor cu nume magice de coloană în predicate.

---

## 5. Predicate de populație (P)

Algebră generică închisă. Motorul nu conține și nu va conține logică specifică unei ipoteze — nu există `sweep_reject` sau `liquidity_grab`; astfel de evenimente se compun.

| ID | Parametri obligatorii |
|---|---|
| `compare@v1` | `left`, `op`, `right` |
| `and@v1` / `or@v1` / `not@v1` | `operands` |
| `bar_position@v1` | `scope`, `index`, `from` |
| `in_session@v1` | `session_ref`, `names` |
| `in_window@v1` | `start`, `end`, `bounds` |
| `crosses@v1` | `series`, `level`, `direction`, `basis` |
| `sequence@v1` | `steps`, `max_gap_bars` |
| `cooldown@v1` | `min_bars_between_events` |

`cooldown@v1` este obligatoriu în orice specificație de populație; 0 se declară explicit. Constructorul de populație raportează întotdeauna **denominatorul per criteriu**.

---

## 6. Statistici (S)

Se invocă prin `statistic_call` (§1.2), niciodată prin identificator gol.

| ID | Parametri obligatorii |
|---|---|
| `mean@v1` | `variable_ref` |
| `median@v1` | `variable_ref` |
| `trimmed_mean@v1` | `variable_ref`, `trim_pct` |
| `proportion@v1` | `variable_ref`, `predicate_ref` |
| `sum@v1` | `variable_ref` |
| `count@v1` | — |
| `difference_in_means@v1` | `variable_ref`, `group_ref`, `group_a`, `group_b` |

---

## 7. Metode de test (M)

Toate au `calibration_status: UNVALIDATED`.

| ID | Parametri obligatorii | Poartă |
|---|---|---|
| `matched_null@v1` | `statistic` *(statistic_call)*, `tail`, `B`, `preserve`, `resample_unit`, `min_n` | S1, S3, S4 |
| `block_bootstrap@v1` | `statistic` *(statistic_call)*, `block_length`, `tail`, `B`, `centering` | S1, S3, S4, S8 |
| `iid_bootstrap@v1` | `statistic` *(statistic_call)*, `tail`, `B`, `centering` | S1, S3, S8 |
| `permutation_test@v1` | `statistic` *(statistic_call)*, `tail`, `B`, `permute_label`, `strata` | S1, S3, S4 |
| `dip_test@v1` | `variable_ref`, `B` | S1, S3 |
| `gaussian_mixture@v1` | `variable_ref`, `k_components`, `selection_criterion`, `n_init`, `max_iter`, `tol` | S1 |
| `changepoint@v1` | `variable_ref`, `algorithm`, `cost_model`, `penalty`, `min_segment` | S1 |
| `regression_control@v1` | `outcome_ref`, `exposure_ref`, `controls`, `interaction`, `se_estimator`, `se_params` | S1, S3, S5 |
| `placebo_control@v1` | `base_test_ref`, `placebo_definition`, `repeats` | S1, S5 |
| `multiverse@v1` | `base_test_ref`, `grid` | S1 |
| `power_simulation@v1` | `effect_sizes`, `n_grid`, `alpha`, `B`, `generator` | S1, S4 |
| `descriptive_measurement@v1` | `variable_ref`, `statistics` *(list[statistic_call])*, `quantiles` | S1 |

`matched_null@v1` cere `preserve` — lista explicită a invarianților păstrați. Motorul nu deduce ce trebuie păstrat; un null potrivit greșit este exact modul în care implementarea existentă a eșuat.

---

## 8. Metode de corecție (C)

| ID | Parametri obligatorii |
|---|---|
| `bonferroni@v1` | `alpha`, `family_members` |
| `benjamini_hochberg@v1` | `alpha`, `family_members`, `variant` |
| `none@v1` | `justification_present` |

`family_members` se enumeră explicit. Motorul nu deduce apartenența la o familie.

---

## 9. Ce nu conține registrul, deliberat

Definiții de sesiune · praguri implicite · evenimente specifice unei ipoteze · metode de auto-selecție a pragului/orizontului/modelului · metrici de profitabilitate ca statistici de verdict · corecție implicită.

**Rămas neacoperit după v1.1, consemnat în backlog:** nu există primitivă care să transforme un predicat într-o variabilă-indicator (gol **G3**). Consecință: un test care contrastează evenimente cu non-evenimente — de exemplu regresia de control obligatorie din designul DC-0004 — nu își poate declara variabila de expunere. Vezi `VE_BACKLOG.md`.

---

## 10. Extinderea registrului

O cerere de extindere vine de la Statistician cu: metoda dorită, motivul statistic, parametrii care trebuie să rămână în controlul specificației, ieșirile așteptate. Metoda nouă intră cu `UNVALIDATED`. **Nicio metodă nu devine executabilă pentru că este urgentă.**

**Poartă de publicare (decizie CEO 2026-07-24):** înainte de publicarea oricărei versiuni de registru se scrie cel puțin **o specificație completă bazată pe un design real**. Un catalog nu se auditează citindu-l, ci încercând să scrii cu el — G1, G2 și acum G3 au fost descoperite exact așa.

---

**Statusul registrului la v1.1: PUBLICAT — NEEXECUTABIL. Toate metodele sunt `UNVALIDATED`.**
