# F6 — RAPORT: CALIBRAREA SINTETICĂ A `matched_null@v1`
### Verdict, curbă de putere, și dacă registrul poate ieși din PUBLISHED_NOT_EXECUTABLE

**Document ID:** VE-F6-REPORT-v1.0
**Data:** 2026-07-25 · **Autor:** Validation Engine
**Autoritate:** CEO 2026-07-25 — F6, prima metodă candidată la VALIDATED.
**Statut:** baterie rulată, **verdict PASS**. **Nimic promovat încă — registrul rămâne `PUBLISHED_NOT_EXECUTABLE`.** Prezint schimbarea de promovare gata de aplicat, în așteptarea ordinului CEO.

---

## 1. Designul care evită cauza eșecului istoric

Eșecul documentat al pilotului: R-uri sintetice brute (scală ±1) alimentate într-un null pe preț real (scală ±zeci $) → nepotrivire de scală → statistica observată minusculă față de null → p mereu ~1.

**Corecția (cerută de CEO):** seriile se generează ca **PREȚ**, nu ca R.
- Generator: random-walk additiv la scala XAUUSD (σ 1-bar = $5.4, wick = $1.7, preț ~2000), măsurat pe datele reale.
- Atât statistica observată, cât și nulul provin din **aceleași prețuri sintetice** → scală consistentă prin construcție.

**Dovada „aceeași cale ca datele reale" (fidelitate deterministă):** pipeline-ul sintetic (PDH/PDL pe zi UTC → sesiuni UTC → sweep-reject → forward K6 → baseline per sesiune → excess → `matched_null.run`), rulat pe **datele reale**, reproduce EXACT numărătorile de evenimente: **135/34/42/114/40/47**. Deci logica sintetică este identică cu cea reală; doar datele diferă.

---

## 2. Verdictul calibrării — PASS

Baterie: **120 serii de preț** sintetice (random-walk, null), B=2000, celula țintă `up/asia` (n≥25), o valoare p per serie. Înregistrare completă: `F6_CALIBRATION_RECORD.json`.

| Probă | Rezultat | Prag | Verdict |
|---|---|---|---|
| **Uniformitate (KS)** | D=0.060, **p=0.765** | p>0.05 = compatibil cu uniform | ✅ |
| **FPR = P(p<0.05)** | **0.042** (5/120), CI95 [0.018, 0.094] | CI conține 0.05 | ✅ |
| medie p / mediană | 0.490 / 0.486 | uniform ~0.5 | ✅ |
| **Reproducibilitate pe seed** | seed 777 → p identic la ambele rulări | identic | ✅ |

Sub null, distribuția p este **uniformă** și rata de fals-pozitiv este **≈5%**, exact ce cere un test bine calibrat. Nu am ajustat metoda — a trecut din prima.

---

## 3. Curba de putere

5 magnitudini de reversie injectate în preț (bump localizat, fără drift), 120 serii/magnitudine:

| δ (preț, $) | Rată de respingere P(p<0.05) | CI95 | |
|---|---|---|---|
| **0.0** | 0.042 | [0.018, 0.094] | FPR (null) |
| 1.0 | 0.117 | [0.073, 0.183] | |
| 2.0 | 0.267 | [0.194, 0.354] | |
| 4.0 | 0.708 | [0.622, 0.782] | |
| 8.0 | **1.000** | [0.969, 1.000] | putere maximă |

**Monotonă crescătoare**, de la FPR (~5% la δ=0) la putere completă (100% la δ=8$, ~0.6× din σ-ul forward K6). Metoda detectează efecte reale și cu putere care crește ordonat cu magnitudinea. δ=0 confirmă din nou FPR ≈ 5%.

---

## 4. Poate registrul ieși din `PUBLISHED_NOT_EXECUTABLE`? — DA, pentru `matched_null@v1`

**Da.** `matched_null@v1` îndeplinește toate criteriile bateriei sintetice cerute:
distribuție p uniformă sub null, FPR ≈ 5%, curbă de putere monotonă pe 5 magnitudini, reproducibilitate pe seed, serii de preț la scală reală prin aceeași cale.

Aceasta este **prima** metodă care se califică pentru `VALIDATED`. Recomand promovarea.

### 4.1 Schimbarea exactă propusă (gata de aplicat, în așteptarea ordinului)
Registru **v1.5** (`capabilities.json`):
```
- test_methods["matched_null@v1"].calibration_status: "UNVALIDATED" -> "VALIDATED"
+ test_methods["matched_null@v1"].calibration_record: {
    battery: "F6 synthetic price calibration", verdict: "PASS",
    null_ks_p: 0.765, fpr: 0.042, power_monotone: true, record: "F6_CALIBRATION_RECORD.json" }
- status: "PUBLISHED_NOT_EXECUTABLE" -> "PUBLISHED_PARTIALLY_EXECUTABLE (1/15 VALIDATED)"
```

### 4.2 Ce NU se deblochează prin această promovare
- Restul de **14 metode rămân `UNVALIDATED`** (fiecare cere propria baterie).
- **DC-0004 tot NU devine executabil oficial** — se oprește în continuare pe `bonferroni@v1` și `multiverse@v1`, care rămân `UNVALIDATED`. Deci promovarea lui `matched_null@v1` **nu** produce nicio execuție oficială accidentală.
- Holdout-ul rămâne intact; F8 rămâne singurul care îl atinge.

### 4.3 De ce nu am aplicat-o autonom
CEO a cerut să **raportez** „dacă registrul poate ieși", iar promovarea la VALIDATED este cea mai consecventă schimbare de guvernanță din tot ciclul VE (prima metodă executabilă). O prezint gata de aplicat și aștept ordinul explicit de promovare — consistent cu tiparul de ratificare al laboratorului și cu regula „nimic promovat până la verdict" (verdictul e acum PASS).

---

## 5. Constrângeri respectate

| Cerință | Stare |
|---|---|
| ≥100 serii de PREȚ null, prin aceeași cale | ✅ 120 serii; fidelitate = numărători reale exacte |
| Distribuție p uniformă, P(p<0.05)≈5% | ✅ KS p=0.765; FPR=0.042 |
| 3–5 magnitudini → curbă de putere | ✅ 5 magnitudini, monotonă |
| FPR + reproducibilitate pe seed | ✅ FPR=0.042; seed identic → p identic |
| Serii ca preț, nu ca R (scală corectă) | ✅ random-walk XAUUSD, statistică+null din aceleași prețuri |
| Holdout neatins | ✅ bateria e 100% sintetică; datele reale doar pentru fidelitate (fereastra deschisă); hash-urile surselor neschimbate |
| Nimic promovat; registru NOT_EXECUTABLE până la verdict | ✅ neatins; promovarea propusă, nu aplicată |
| Dacă pică → raportează, nu ajusta metoda | N/A — a trecut din prima, fără ajustări |

---

## 6. Fișiere

**Create:** `ve/calibration/synthetic_matched_null.py` (generator de preț + pipeline + baterie), `tests/test_f6_calibration.py`, `F6_CALIBRATION_RECORD.json`, `F6_REPORT.md`.
**Neatins:** registrul (`capabilities.json`), schema, DC-0004, motorul, cele 4 surse de date.
**Teste:** 405 passed (400 + 5 F6).

---

## 7. Concluzie

`matched_null@v1` **calibrează**: sub null, distribuția p este uniformă cu FPR ≈ 5%; sub edge injectat, puterea crește monoton până la 100%; rezultatele sunt reproducibile pe seed; iar seriile sunt preț la scală reală, prin exact aceeași cale ca datele reale (fidelitate dovedită prin reproducerea numărătorilor reale).

**Verdict: PASS.** Registrul **poate** ieși din `PUBLISHED_NOT_EXECUTABLE` pentru această metodă. Promovarea la `VALIDATED` (registru v1.5, status `PARTIALLY_EXECUTABLE`) este gata de aplicat și o recomand, dar **nu am aplicat-o** — aștept ordinul explicit de promovare al CEO.

**Validation Engine se oprește și așteaptă decizia de promovare.**
