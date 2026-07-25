# INVENTAR DE EXECUTABILITATE — Pachetele S002 (DC-0008, DC-0003, DC-0004)
### Doar fapte. Ce metodă / ce sursă de date lipsește pentru fiecare pachet.

**Document ID:** VE-EXEC-INV-S002-v1.0
**Data:** 2026-07-25 · **Autor:** Validation Engine
**Cerut de:** CEO 2026-07-25 — inventar de fapte, NU plan de calibrare, NU estimare de efort, NU recomandare de ordine.
**Surse:** `capabilities.json` (`VE-CAPREG-v1.5`), `statistician/VALIDATION_ENGINE_HANDOFF_S002_v1.0.md` §§3-5, fixturile `tests/fixtures/reference_spec_dc0004.json` și `reference_spec_dc0008.json`. DC-0003 nu are fixtură — metodele sunt derivate din handoff §4.

**Legendă status metodă:** `VALIDATED` = executabilă oficial · `UNVALIDATED` = nereferabilă de o specificație oficială (regula `unvalidated_not_executable`).
**Surse de date în holdings-urile VE:** `OANDA_XAUUSD_{M15,H1,H4,D1}@v1`. **Absente:** M1, M5, orice agregare sub-bară (G6); orice dataset OBS-* nu e sursă înregistrată.

---

## Tabel-sinteză: metode distincte referite de cele trei pachete

| Metodă | Status | DC-0008 | DC-0003 | DC-0004 |
|---|---|---|---|---|
| `matched_null@v1` | **VALIDATED** | — | — | **verdict principal** |
| `bonferroni@v1` | UNVALIDATED | familie (alt. max-T) | condiționat (cu DC-0002) | corecție de familie |
| `multiverse@v1` | UNVALIDATED | sensibilitate | sensibilitate | robustețe (T3) |
| `regression_control@v1` | UNVALIDATED | outcome ~ R×vol | interacțiune | secundar (non-verdict) |
| `dip_test@v1` | UNVALIDATED | Strat 1 | — | — |
| `gaussian_mixture@v1` | UNVALIDATED | Strat 1 | — | — |
| `changepoint@v1` | UNVALIDATED | prag (fixtură) | segmentare Bai-Perron | — |
| `descriptive_measurement@v1` | UNVALIDATED | prag | — | — |
| `block_bootstrap@v1` | UNVALIDATED | stabilitate prag (§4.4) | — | — |
| `permutation_test@v1` | UNVALIDATED | max-T family-wise (§4.8) | — | — |
| `power_simulation@v1` | UNVALIDATED | putere (§4.9) | — | — |
| `placebo_control@v1` | UNVALIDATED | — | — | secundar (non-verdict) |

**Metode distincte referite în total: 12. `VALIDATED`: 1 (`matched_null@v1`). `UNVALIDATED`: 11.**

---

## PACHET 1 — DC-0008

### 1. Metode referite (din fixtură `reference_spec_dc0008.json` + handoff §4)

| Test / rol | Metodă | Status |
|---|---|---|
| T1 dip Hartigan | `dip_test@v1` | UNVALIDATED |
| T2 GMM 1v2 BIC | `gaussian_mixture@v1` | UNVALIDATED |
| T3 changepoint | `changepoint@v1` | UNVALIDATED |
| T4 măsurare prag | `descriptive_measurement@v1` | UNVALIDATED |
| T5 clasa prezice outcome (HAC) | `regression_control@v1` | UNVALIDATED |
| T6 multiverse | `multiverse@v1` | UNVALIDATED |
| T7 putere | `power_simulation@v1` | UNVALIDATED |
| corecție de familie | `bonferroni@v1` | UNVALIDATED |
| stabilitate prag, bootstrap în blocuri (handoff §4.4, absent din fixtură) | `block_bootstrap@v1` | UNVALIDATED |
| family-wise max-T prin permutare (handoff §4.8; fixtura folosește bonferroni ca formă) | `permutation_test@v1` | UNVALIDATED |
| comparație pe perechi potrivite / matching (handoff §4.6) | *nicio metodă dedicată în registru* (cea mai apropiată: statistica `difference_in_means@v1`) | — |

### 2. Variabile cerute și sursă de date

| Variabilă | Primitivă | Sursă | Există? |
|---|---|---|---|
| **R = vol max sub-lumânare M1/M5 ÷ vol M15** (expunerea reală, handoff §§1,3) | *nicio primitivă de agregare sub-bară în registru* | **M1/M5** | **NU (G6)** |
| `r_ratio_standin` (substituent de FORMĂ în fixtură, NU R) | `bar_range_ratio@v1` | M15@v1 | DA — dar **nu e R** |
| `vol_z` | `volume_zscore@v1` | M15@v1 | DA |
| `vol_hour` (regim volatilitate) | `hour_of_day_volatility_profile@v1` | M15@v1 | DA |
| `class_concentrated` | `indicator@v1` | (derivat) | DA (dacă R există) |
| `aftermath_k8` (N=8, blocat) | `forward_return@v1` | M15@v1 | DA |

### 3. Ce l-ar face executabil
- **Metode de validat:** `dip_test@v1`, `gaussian_mixture@v1`, `changepoint@v1`, `descriptive_measurement@v1`, `regression_control@v1`, `multiverse@v1`, `power_simulation@v1`, `bonferroni@v1`, `block_bootstrap@v1`, `permutation_test@v1` — **10 metode UNVALIDATED**.
- **Date lipsă:** sursă **M1/M5** + o primitivă de agregare sub-bară pentru R (**gol G6**). Fără ele, variabila centrală R e nematerializabilă; substituentul M15 din fixtură nu e R.

---

## PACHET 2 — DC-0003

*(Fără fixtură VE. Metode derivate din handoff §4; variabile din §5.)*

### 1. Metode referite

| Rol (handoff §4) | Metodă | Status |
|---|---|---|
| regresie cu interacțiune scale_ratio × regim_lichiditate, HAC (§4.2) | `regression_control@v1` | UNVALIDATED |
| test raport verosimilitate 1-segment vs 2-segmente, piecewise Bai-Perron (§4.3) | `changepoint@v1` (cea mai apropiată; segmentare) | UNVALIDATED |
| sensibilitate ATR/orizonturi (§4.4) | `multiverse@v1` | UNVALIDATED |
| corecție family-wise dacă raportat cu DC-0002 (§4.5) | `bonferroni@v1` (condiționat) | UNVALIDATED |

### 2. Variabile cerute și sursă de date

| Variabilă | Sursă | Există? |
|---|---|---|
| populația de **384 evenimente OBS-0017** (swing-high exceedances) + outcome (continuare/eșec) + range pre-spargere | **dataset OBS-0017** | **NU e sursă înregistrată în `capabilities.json`** |
| ATR local per eveniment | `atr@v1` din M15/H1@v1 | DA (primitivă + sursă există) |
| regim de lichiditate / sesiune | `session_label@v1` etc. | DA |

### 3. Ce l-ar face executabil
- **Metode de validat:** `regression_control@v1`, `changepoint@v1`, `multiverse@v1` (+ `bonferroni@v1` dacă raportat cu DC-0002) — **3 (–4) metode UNVALIDATED**.
- **Date lipsă:** datasetul **OBS-0017** (384 evenimente cu variabile brute + outcome) nu e o sursă de date înregistrată în registru. ATR-ul e derivabil din surse existente; populația de evenimente și outcome-urile nu.

---

## PACHET 3 — DC-0004

### 1. Metode referite (din fixtură `reference_spec_dc0004.json` + handoff §4)

| Test / rol | Metodă | Status |
|---|---|---|
| T1 matched-null K6 (**verdict decisiv**) | `matched_null@v1` | **VALIDATED** ✅ |
| T2 matched-null K12 (descriptiv) | `matched_null@v1` | **VALIDATED** ✅ |
| corecție Bonferroni empirică n≥25 (verdict principal) | `bonferroni@v1` | UNVALIDATED |
| T3 stabilitate / robustețe | `multiverse@v1` | UNVALIDATED |
| control de volatilitate (secundar, non-verdict, handoff §4.4) | `regression_control@v1` | UNVALIDATED |
| test placebo pe nivel arbitrar (secundar, non-verdict) | `placebo_control@v1` | UNVALIDATED |

### 2. Variabile cerute și sursă de date

| Variabilă | Primitivă | Sursă | Există? |
|---|---|---|---|
| bar_high / bar_low / bar_close | `raw_series@v1` | H1@v1 | DA |
| pdh / pdl | `prior_period_extreme@v1` | H1@v1 | DA |
| session | `session_label@v1` | (declarat) | DA |
| fwd_ret_k6 / fwd_ret_k12 | `forward_return@v1` | H1@v1 | DA |
| baseline_k6 / baseline_k12 | `baseline_forward_mean@v1` | H1@v1 | DA |
| cont_excess_k6 / k12 | `forward_excess@v1` | (derivat) | DA |

**Toate variabilele se materializează din `OANDA_XAUUSD_H1@v1` (EXISTĂ).** Fereastra populației = holdout post `2025-10-23T09:15:00Z` → **datele există în sursă dar sunt SIGILATE** (CEO-gated, single-shot; `sealed_registry` PROVISIONAL).

### 3. Ce l-ar face executabil
- **Metode de validat (verdict principal):** `bonferroni@v1` — **1 metodă UNVALIDATED**. `matched_null@v1` (metoda decisivă) e deja `VALIDATED`.
- **Metode de validat (robustețe + secundar, dacă cerute):** `multiverse@v1` (T3) + `regression_control@v1`, `placebo_control@v1` (non-verdict) — **încă 3**.
- **Date lipsă:** niciuna în sens de absență. Fereastra holdout există în sursă dar e **sigilată** — deblocarea cere token CEO + repetiție pe fereastra deschisă cu hash de spec identic (resursă single-shot).

---

## Fapte agregate

- **Metode distincte referite de cele trei pachete: 12. VALIDATED: 1. UNVALIDATED: 11.**
- **Metode UNVALIDATED per pachet:** DC-0008 = **10** · DC-0003 = **3–4** · DC-0004 = **1** (verdict principal) sau **4** (cu robustețe + secundar).
- **Sursa care are toate datele, fără achiziție:** DC-0004 (H1 există; holdout sigilat, nu absent).
- **Surse de date absente:** M1/M5 pentru R al DC-0008 (**G6**); dataset OBS-0017 pentru DC-0003 (neînregistrat).
- **Precedent de calibrare:** `matched_null@v1` a cerut 4 runde (F6/F6.1/F6.2/F6.3) pentru o singură metodă. Cele 11 metode `UNVALIDATED` nu au încă nicio rundă de calibrare.

**Notă de proces (fapt, nu recomandare):** G6 este marcat `DESCHIS` în `CAPABILITY_REGISTRY_v1.5.md` (linia 52). CEO a comunicat că Divizia Data Acquisition a confirmat podeaua M5 la 2021-07-22 (acoperă segmentul de research 2022-12-16→), deci G6 e rezolvabil prin achiziție; datele nu au trecut încă verificarea și nu sunt în holdings-urile VE la data acestui inventar.
