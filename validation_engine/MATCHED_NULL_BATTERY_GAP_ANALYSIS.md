# ANALIZĂ DE GAP — bateria F6/F6.1/F6.2 vs. validarea matched-null Flow C
### Ce lipsește din calibrarea `matched_null@v1` înainte de promovare

**Document ID:** VE-MN-GAP-v1.0
**Data:** 2026-07-25 · **Autor:** Validation Engine
**Context:** CEO a ridicat interdicția de a citi implementarea Flow C. Am citit `docs/MATCHED_NULL_VALIDATION.md` + `code/{matched_null,mn_calibration,mn_power,mn_adversarial,drift_core,...}.py` de pe `flow-c-foundation` (fără merge, doar `git show`). **Nu am copiat cod.** Întrebarea CEO: ce din bateria lor lipsește din a mea și ar trebui adăugat.

---

## 0. Precizare esențială: obiecte diferite

Bateria Flow C validează **Test B pentru backtesturi de STRATEGIE** prin `mstrat.simulate` (intrări, ieșiri, stopuri, costuri, overlap). `matched_null@v1` al meu validează **celule de EVENIMENT DC** (sweep-reject → forward K6 → excess vs. pool per-sesiune). Multe dintre controalele lor sunt **specifice strategiei și NU se aplică** obiectului meu: reguli de ieșire (rr/time/trailing), tipuri de risc (atr/struct), frecvența de tranzacționare, overlap-ul, paritatea cu `MS.backtest`. Nu le import.

Filtrez la ce este **relevant pentru un test pe celule de eveniment**.

---

## 1. Ce am eu deja (F6/F6.1/F6.2)

| Element | Stare |
|---|---|
| Serii de PREȚ (nu R), scală reală | ✅ F6 (cauza eșecului istoric evitată) |
| Fidelitate = paritate pe date reale (reproduce 135/34/42/114/40/47 + obs0012 bit-exact) | ✅ analogul lor de paritate |
| Calibrare null (uniform, FPR@0.05, KS) | ✅ F6 |
| Curbă de putere (5 magnitudini) | ✅ F6 |
| Reproducibilitate pe seed | ✅ F6 |
| **Vol diferențiată pe sesiune** + cozi grele | ✅ F6.1 |
| **Drift real** (up/down/regime-shift), calibrat pe M15 | ✅ F6.2 |

**Contribuție proprie, absentă la ei:** design-ul meu folosește **excess = forward − baseline per-sesiune**, analogul structural al fix-ului lor (bootstrap pe raportul risk/ATR, nu absolut) — motivul pentru care F6.2 nu a eșuat sub drift.

> **CORECȚIE (2026-07-25), cerută de CEO — verificat în cod:** afirmasem că `matched_null@v1` este configurația **stratificată session×vol** pe care Flow C a amânat-o (§9 lim. 1). **Retrag jumătatea de volatilitate.** Verificat în `reproduce_obs0012.py` (pool per celulă = `sess == s`, doar sesiune) și `materialize.py` (baseline `strata=[session]`, doar sesiune): stratificarea este **exclusiv pe SESIUNE**, nu pe volatilitate. F6.1 a arătat **robustețe** la vol diferențiată pe sesiune (pool-ul de sesiune absoarbe vol-ul), dar aceasta NU e stratificare pe vol. Configurația lor amânată era session×**vol** (două dimensiuni); a mea e doar session. Complementaritatea revendicată se retrage.

---

## 2. Ce le lipsește din bateria mea — RELEVANT, DE ADĂUGAT

Bateria lor adversarială are 8 scenarii. Ordonate după relevanța pentru celule de eveniment:

| # | Scenariu Flow C | Am? | De ce contează pentru matched_null@v1 | Prioritate |
|---|---|---|---|---|
| **G-AR1** | **`range_ar1` (AR(1) = −0.3, reversie la medie în PREȚ)** | ❌ **NU** | Generatorul meu e random-walk (+drift). **Evenimentul sweep-reject ESTE un tipar de reversie** (sparge maximul, închide sub). Sub un preț cu reversie reală la medie, forward-ul evenimentului reversează genuin — dacă pooling-ul per-sesiune absoarbe asta (calibrat) sau selecția o biasează (fals-pozitiv) este întrebarea netestată. F6.2 a testat trendul; adversarul SIMETRIC (reversia) lipsește și e **mai relevant** pentru un test care caută reversie | 🔴 **MAXIMĂ** |
| **G-VOLCL** | **`vol_cluster` (clustering GARCH stocastic, persistență 0.92)** | ⚠️ parțial | Am vol diferențiată pe sesiune DETERMINISTĂ (F6.1), dar nu clustering STOCASTIC persistent. Un sweep-reject apare într-un moment volatil → volatilitate continuă → efect de varianță, netestat cu clustering stocastic | 🟠 mare |
| **G-GAPS** | **`heavy_gaps` (gap_rate 0.05, gap_size 5.0)** | ❌ NU | Nu modelez gap-uri. XAUUSD real are gap-ul zilnic 20:00→22:00 UTC (constatat la F4) + gap-uri de weekend. Gap-urile interacționează cu PDH/PDL și cu forward-ul | 🟠 mare |
| **G-CONC** | **`concentrated_year` / `concentrated_session` (evenimente concentrate în timp)** | ❌ NU | Nu testez robustețea când evenimentele se aglomerează într-un regim/perioadă (exact ce fac evenimentele reale — se aglomerează în regimuri de volatilitate) | 🟡 medie |

Controale (nu scenarii):

| # | Control Flow C | Am? | De adăugat |
|---|---|---|---|
| **G-FPR** | FPR la **0.01 și 0.10** (nu doar 0.05) + **split-half stability** | ⚠️ doar 0.05 | Ieftin, întărește afirmația de calibrare. Relevant: up/ny arată ~0.06 la 0.05; 0.01/0.10 ar caracteriza mai bine coada | 🟠 mare |
| **G-PLACEBO** | Pilot pe ipoteze reale + **control negativ** (pierzătorii primesc p mare) | ⚠️ parțial | Reproduc obs0012 pe date reale, dar NU am un **placebo**: matched_null pe un NIVEL ARBITRAR (non-PDH) pe date reale → trebuie să NU respingă. Exact placebo-ul cerut de Statistician la Phase 1 §10 pentru DC-0004 | 🟠 mare |

---

## 3. Ce NU trebuie importat (specific strategiei, irelevant)

Reguli de ieșire (rr/time/trailing), tipuri de stop (atr/struct), frecvența de tranzacționare, overlap-ul de trade-uri, paritatea cu `MS.backtest`. Obiectul meu nu are trade-uri, ieșiri sau stopuri — sunt celule de eveniment cu forward fix K6. Copierea lor ar fi zgomot.

---

## 4. Recomandare privind promovarea

`matched_null@v1` a trecut F6 (calibrare + putere), F6.1 (vol pe sesiune + cozi grele — **inclusiv configurația stratificată pe care Flow C a amânat-o**) și F6.2 (drift — fără eșec clar). Dar bateria adversarială Flow C, mai matură, arată **trei scenarii relevante încă netestate** pe obiectul meu:

**Înainte de promovarea la VALIDATED, recomand adăugarea:**
1. 🔴 **G-AR1 (reversie la medie în preț)** — adversarul simetric al driftului, cel mai relevant pentru un test de reversie. Neapărat.
2. 🟠 **G-FPR (praguri 0.01/0.10 + split-half)** — ieftin, caracterizează coada; up/ny are deja o înclinare ~0.06 de urmărit.
3. 🟠 **G-PLACEBO (nivel arbitrar pe date reale → nu respinge)** — controlul negativ pe date reale, cerut și de Statistician.

Opțional/ulterior: G-VOLCL (clustering stocastic), G-GAPS, G-CONC.

**Concluzia mea onestă:** promovarea NU ar trebui făcută încă. Nu pentru că metoda a eșuat — a trecut tot ce am rulat — ci pentru că bateria Flow C demonstrează că un adversar **de reversie** (G-AR1) este exact tipul de scenariu pe care un test de reversie trebuie să-l treacă înainte de a fi declarat calibrat, iar eu nu l-am rulat. Este un gap real, nu o precauție generică.

---

**Nu am copiat cod din Flow C. Am citit pentru a ști ce există. Recomand F6.3 (G-AR1 + G-FPR + G-PLACEBO) înainte de promovare.**
