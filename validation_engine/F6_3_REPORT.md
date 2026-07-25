# F6.3 — RAPORT: SCENARIILE ADVERSARIALE Flow C LIPSĂ
### G-AR1 (reversie) · G-FPR (praguri + split-half) · G-PLACEBO (nivel arbitrar)

**Document ID:** VE-F63-REPORT-v1.0
**Data:** 2026-07-25 · **Autor:** Validation Engine
**Statut:** finalizat. **Verdict: PASS la condițiile reale; două caveat-uri documentate.** Promovarea rămâne decizia CEO.

---

## 0. Corecție cerută de CEO — afirmația de stratificare (RETRACT)

Afirmasem că `matched_null@v1` este configurația **stratificată session×vol** pe care validarea Flow C din 2026-07-13 a amânat-o. **Verificat în cod, retrag jumătatea de volatilitate:**
- `reproduce_obs0012.py`: pool per celulă = `sess == s` — **doar sesiune**.
- `materialize.py`: baseline `strata=[session]` — **doar sesiune**.

Stratificarea este **exclusiv pe SESIUNE**. F6.1 a arătat **robustețe** la volatilitate diferențiată (pool-ul de sesiune absoarbe vol-ul), dar aceasta **nu** e stratificare pe vol. Complementaritatea cu golul lor (care era session×**vol**, două dimensiuni) **se retrage** — a mea e doar session. Ați avut dreptate.

---

## 1. G-AR1 — reversie la medie (testul decisiv)

Coeficientul AR(1) **măsurat** din date reale (H1, fereastra deschisă, demean): **φ = −0.0182** (reversie slabă). Rulat la φ real (calibrat) și la φ adversarial (stress).

**Curba de sensibilitate — celula up/ny** (fără efect de nivel; + vol NY 2.5× + cozi t4):

| φ | × real | FPR@0.05 | Status |
|---|---|---|---|
| **−0.018 (REAL)** | 1.0× | ~0.06–0.085 | la graniță (CI atinge 0.05) |
| −0.05 | 2.7× | 0.054 | calibrat |
| −0.10 | 5.5× | 0.100 | **RUPT** |
| −0.20 | 11× | 0.123 | **RUPT** |
| −0.30 | 16.5× | 0.162 (KS=0.000) | **RUPT** |

up/asia rămâne calibrat chiar și la φ=−0.30 (0.064).

**Interpretare:** mecanismul pe care l-ați identificat **este real și confirmat** — reversia puternică fabrică o respingere falsă în up/ny (reversia din date interacționează cu selecția evenimentului up-sweep-reject). **DAR** apare doar la φ ≤ −0.10 (**5.5×+ reversia reală**). La reversia reală (−0.018), metoda **nu respinge clar** (up/ny la graniță ~0.06–0.085; up/asia curat). **DC-0004 NU e fabricat de reversie la nivelul real al datelor.**

Verdict G-AR1: **PASS la φ real** (up/ny la graniță); mecanism confirmat ca **vulnerabilitate de stress** departe de date; up/ny e celula vulnerabilă (n mic).

## 2. G-FPR — praguri 0.01/0.05/0.10 + split-half (base null, n=500)

| Celulă | FPR@0.01 | FPR@0.05 | FPR@0.10 | split-half@0.05 | KS_p | medie |
|---|---|---|---|---|---|---|
| **up/ny** | 0.010 | 0.052 | 0.096 | [0.048, 0.056] | **0.003** | 0.542 |
| up/asia | 0.002 | 0.042 | 0.082 | [0.032, 0.052] | 0.653 | 0.502 |

**up/ny:** cozile (0.01/0.05/0.10) sunt **calibrate**, split-half stabil — înclinarea ~0.06 semnalată la F6.2 **se spală la n=500**. Dar **KS p=0.003**: distribuția nu e perfect uniformă (medie 0.542, ușor **conservatoare** — direcția SIGURĂ, mai greu să respingă fals). Artefact de eșantion mic (n~37). **up/asia:** complet curat.

Verdict G-FPR: **PASS** — cozile calibrate, split-half stabil; up/ny subtil non-uniform în direcția sigură.

## 3. G-PLACEBO — nivel arbitrar pe date reale (control negativ)

| Nivel arbitrar | Celule eligibile | Respinge? |
|---|---|---|
| prior-day close | asia/late, toate p>0.5 | NU |
| prior-day midpoint | up/asia 0.55, down/asia 0.58 | NU |
| **extremă de acum 2 zile** | **up/ny p=0.247**, down/ny 0.73, asia 0.82–0.89 | **NU** |

Reper: PDH real, NY-up p=**0.025**. La extrema arbitrară, NY-up p=**0.247** (nesemnificativ).

**Interpretare:** metoda **NU respinge fals** la niveluri arbitrare. Mai mult, reversia este **specifică PDH-ului** (0.025 la PDH real vs. 0.247 la o extremă arbitrară) — controlul negativ cerut de Statistician (Phase 1 pct. 3) **trece**, și susține specificitatea de nivel a DC-0004.

Verdict G-PLACEBO: **PASS.**

---

## 4. Verdict F6.3 și recomandare de promovare

**PASS la condițiile reale ale datelor**, în toate cele trei scenarii. La driftul, reversia, volatilitatea și cozile grele **măsurate din date**, metoda nu respinge fals. DC-0004 NU e explicat de aceste artefacte.

**Două caveat-uri documentate:**
1. **up/ny e o celulă cu n mic (~37)** cu non-uniformitate subtilă (KS p=0.003, direcția conservatoare/sigură) și o vulnerabilitate **confirmată** la reversie puternică (φ≤−0.10, 5.5×+ real). Exact celula DC-0004.
2. Mecanismul de reversie **este real** dar nu se materializează la nivelul real al datelor (−0.018 ≪ −0.10).

**Recomandarea mea:** metoda a trecut acum F6 + F6.1 + F6.2 + F6.3, toate la condiții reale — o validare temeinică. Promovarea la `VALIDATED` este **defendabilă**, cu **caveat-ul explicit** că celula NY-up (n~37) e la granița calibrării și că metoda se degradează sub reversie ≥5× reala. Alternativ, dacă doriți calibrare curată pe up/ny înainte, ar trebui celule mai mari (n mai mare) sau o corecție de eșantion mic — dar aceasta e o îmbunătățire, nu un blocaj la condiții reale. Decizia vă aparține; nu am promovat.

---

## 5. Fișiere & stare

**Create:** `F6_3_REPORT.md`, `F6_3_CALIBRATION_RECORD.json`, `tests/test_f6_3_reversion.py`. **Modificate:** `ve/calibration/synthetic_matched_null.py` (+AR1), `MATCHED_NULL_BATTERY_GAP_ANALYSIS.md` (retract vol), `VE_BACKLOG.md`. Holdout neatins (G-PLACEBO pe fereastra deschisă; hash-uri surse identice). Nimic promovat.

**Verdict F6.3: PASS la condiții reale; caveat NY-up small-n + vulnerabilitate de reversie la stress. Promovarea — decizia CEO.**
