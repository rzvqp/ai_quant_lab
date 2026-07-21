# FLOW C — P1 COVERAGE PLAN
### Planul operațional de acoperire descriptivă până la P1 Completion
**Status:** DOCUMENT OPERAȚIONAL — pentru review CEO. NU e înghețat. NU se commit.
**Guvernat de (înghețate, nemodificate):** ANALYSIS_PROTOCOL v1.0 · ROADMAP · P1_COMPLETION_CRITERIA v1.0
**Ancorat în:** FAMILY_RESULTS.parquet (real) + RI-REPORT-0001 (livrat)

> Acest plan spune CE rapoarte descriptive urmează și DE CE, ca să atingem checklist-ul înghețat A.5 și Coverage Confidence = High. Nu produce rapoarte; le secvențiază.

---

## 1. ACOPERIRE DESCRIPTIVĂ CURENTĂ (ce acoperă deja RI-REPORT-0001)

RI-REPORT-0001 a livrat **harta la nivel de populație** a corpului (1972 ipoteze, S1–S20):
- **Funnel complet:** generated 1972 → valid 1800 → invalid 172 → hist_prof 357 → research_worthy 130; fragile 133. *(strat funnel: ACOPERIT)*
- **Compoziție per familie (agregat):** counts, hist_prof, research_worthy, fragile, exp_median, exp_max, pf_median pentru toate 20 familiile. *(profitabilitate + interval tipic exp/pf: ACOPERIT la nivel agregat)*
- **Side (marginal global):** 934 long / 934 short / 104 both. *(side global: ACOPERIT; side PER-FAMILIE: NU)*
- **Distribuția expectancy (populație):** medie −0,115, mediană −0,116, 18,1% exp>0, min −1,095, max 0,915.
- **Extreme:** S19/S14/S6 semnalate cu notă artefact-vs-semnal (S6 = artefact tiny-stop cunoscut). *(ACOPERIT)*
- **Goluri auto-logate (§6 al raportului):** `val_exp, t1, t3, t5, wo1` neatinse; fereastra calendaristică; nivel config/parametru.

**Verdict de stare:** Coverage Confidence ≈ **Medium** — matricea e umplută la nivel agregat, dar rămân celule-coloană goale, familia dominantă S1 netratată dedicat, eșecurile descrise superficial, side per-familie absent, și există un singur raport (checklist A.5 cere ≥2).

---

## 2. MATRICEA DE ACOPERIRE (stare curentă)

Legendă: ✅ acoperit · 🟡 parțial (doar agregat) · ⬜ gol · 🔒 se amână intenționat pentru P2

### 2a. Familii de edge (20) × legibilitate „normal"
| | profitabilitate | interval exp/pf | side per-familie | temporal (months/years) | adâncime distribuție |
|---|---|---|---|---|---|
| S1 (dominant, 1152) | ✅ | 🟡 | ⬜ | ⬜ | ⬜ (dedicat necesar) |
| S2–S20 profitabile (13) | ✅ | 🟡 | ⬜ | ⬜ | 🟡 |
| S4,S7,S10,S11,S12,S15 (zero-profit) | ✅ | 🟡 | ⬜ | ⬜ | ⬜ (rigoare egală necesară) |

### 2b. Dimensiuni de rezultat (coloane ~22)
| Coloană | Stare | Info-gain așteptat |
|---|---|---|
| n, exp, pf | 🟡 (agregat) | mediu |
| side, hist_prof, research_worthy, fragile | ✅ | — |
| **val_exp** (probabil expectancy de validare/OOS) | ⬜ | **RIDICAT** |
| **t1, t3, t5** (contribuția top-1/3/5 trades) | ⬜ | **RIDICAT** |
| **wo1** (expectancy fără cea mai bună tranzacție) | ⬜ | **RIDICAT** |
| **dd** (max drawdown) | ⬜ | ridicat |
| win, sumR | ⬜ | mediu |
| median, trim5 | 🟡 (menționate) | mediu |
| months, pos_months, years | 🟡 | mediu |

### 2c. Tipuri de outcome (straturi + regiuni de distribuție)
| Regiune | Stare |
|---|---|
| funnel: generated/valid/invalid/hist_prof/research_worthy/fragile | ✅ |
| câștigători (357) | 🟡 |
| perdanți / masa valid-neprofitabilă (~1443) | ⬜ (rigoare egală necesară) |
| fragili (133) | 🟡 (număr da, formă nu) |
| extreme-outlieri (S6/S14/S19) | ✅ |

### 2d. Goluri structurale (nedescriptibile din acest artefact)
- Nivel config/parametru intra-ipoteză (nu e în tabelul agregat).
- Fereastra calendaristică exactă (nu e auto-descrisă).
- Semantica exactă a `val_exp/t1/t3/t5/wo1` (de confirmat în primul raport planificat).
- Regim / dataset / TF multiplu — **inexistente în dovadă** → axe condiționale, logate ca limitare (nu blocaj).

---

## 3. IERARHIE DE PRIORITATE (după information gain)

**P#1 — Coloanele de robustețe/concentrare (`val_exp, t1/t3/t5, wo1, dd`).** *Justificare:* sunt cel mai mare bloc gol ȘI poartă dimensiunea de CALITATE pe care harta de populație n-a putut-o vedea. Ele luminează descriptiv exact povestea fragilității (133/357 = 37% din câștigători sunt fragili) — concentrarea P&L (t1/t3/t5), robustețea (wo1), validarea (val_exp), riscul (dd). Breadth = tot corpul. **Cel mai mare info-gain.**

**P#2 — S1 (familia dominantă).** *Justificare:* checklist A.3.5 cere raport dedicat; S1 = 58% din corp și 73% din câștigători → orice „normal" al corpului e, statistic, normalul lui S1. A-l lăsa doar agregat = 58% din corp sub-descris.

**P#3 — Familiile de eșec + masa neprofitabilă.** *Justificare:* gardă anti-survivorship (A.4.2). Fără descrierea celor 6 zero-profit și a masei perdante cu rigoare egală, baza descriptivă e părtinitoare spre succes → orice P2 ar moșteni un base rate deghizat.

**P#4 — Completarea „normalului" per-familie (side split + temporal) pentru familiile mijlocii/mici.** *Justificare:* închide ultima celulă a legibilității per-familie (side per-familie, consistență temporală) pentru cele 13 familii non-S1 profitabile. Info-gain marginal, dar necesar pentru A.3.1.

---

## 4. SECVENȚA PLANIFICATĂ DE RAPOARTE

*(Fiecare rămâne strict descriptiv, un singur corpus, fără cross-axă. Relațiile derivate din aceste coloane sunt 🔒 P2 — vezi §6.)*

### RI-REPORT-0002 — Dimensiunea de robustețe & concentrare
- **Obiectiv:** descrie distribuțiile marginale ale `val_exp, t1, t3, t5, wo1, dd, win, median, trim5` peste corp; confirmă semantica lor.
- **Contribuție descriptivă:** umple cel mai mare bloc de celule-coloană gol; face legibilă dimensiunea de calitate/robustețe.
- **Celule completate:** 2b — toate coloanele ⬜ „ridicat/mediu"; regiunea „fragili (formă)".
- **Graniță:** descrie fiecare coloană *marginal*. Divergența `val_exp` vs `exp`, sau concentrarea vs flag-ul fragile, sunt RELAȚII → 🔒 P2.

### RI-REPORT-0003 — S1: forma internă a familiei dominante
- **Obiectiv:** hartă descriptivă dedicată a S1 (1152 ipoteze, 261 câștigători) — distribuție internă exp/pf/dd, side split intern, temporal.
- **Contribuție:** satisface A.3.5; face legibil în adâncime „normalul" a 58% din corp.
- **Celule completate:** 2a rândul S1 (toate coloanele 🟡/⬜ → ✅).
- **Graniță:** „S1 vs restul" = comparație cross-axă → 🔒 P2. Aici doar S1 în sine.

### RI-REPORT-0004 — Cunoaștere negativă: familiile de eșec & masa neprofitabilă
- **Obiectiv:** descrie cele 6 familii zero-profit (S4,S7,S10,S11,S12,S15) și masa valid-neprofitabilă cu **rigoare egală** cu a câștigătorilor — sunt uniform slabe sau near-miss? cum arată coada negativă?
- **Contribuție:** închide garda anti-survivorship (A.4.2); 6/6 zero-profit ca cunoaștere negativă.
- **Celule completate:** 2a rândul zero-profit; 2c „perdanți / masa neprofitabilă".
- **Graniță:** „de ce eșuează" = mecanism → 🔒 P4, interzis. Aici doar forma eșecului.

### RI-REPORT-0005 — Completarea legibilității per-familie (non-S1)
- **Obiectiv:** side split per-familie + consistență temporală (months/pos_months/years) pentru cele 13 familii non-S1 profitabile.
- **Contribuție:** închide A.3.1 (20/20 „normal" legibil incl. side per-familie).
- **Celule completate:** 2a coloanele „side per-familie" + „temporal" pentru S2–S20.
- **Graniță:** orice tipar side×profitabilitate între familii = 🔒 P2.

---

## 5. EVOLUȚIA COVERAGE CONFIDENCE (estimare per raport)

| După | Coverage Confidence | De ce |
|---|---|---|
| RI-REPORT-0001 (acum) | **Medium** | hartă agregată; coloane-cheie goale; S1 nededicat; eșecuri superficiale; 1 raport |
| + RI-REPORT-0002 | **Medium** (în urcare) | cel mai mare bloc-coloană umplut, dar S1/eșecuri/side-per-familie încă deschise |
| + RI-REPORT-0003 | **Medium-High** | familia dominantă (58%) dedicată; rămân eșecuri + per-familie side |
| + RI-REPORT-0004 | **Medium-High** | gardă anti-survivorship închisă; rămâne per-familie side/temporal |
| + RI-REPORT-0005 | **High (candidat)** | toate celulele pline/logate — **DAR** High se declară doar după re-check de saturație + audit A.5 integral |

> **Regulă de porție (din §2.1 Lifecycle, înghețat):** High NU e automat după 0005 — cere upgrade *cu review*: verificarea că ultimul raport n-a mai scos structură descriptivă nevăzută (saturație genuină) + toate căsuțele A.5 bifate. Și e relativ la snapshot: un batch Alpha nou l-ar coborî automat și ar redeschide P1.

---

## 6. RISCURI

**Ce rămâne necunoscut (chiar la P1 complet):**
- Structura config/parametru din interiorul fiecărei ipoteze (absentă din artefactul agregat).
- Fereastra calendaristică exactă și eventuale regimuri temporale (nedescriptibile din coloane).
- Semantica exactă a `val_exp/t1/t3/t5/wo1` până la confirmarea în RI-REPORT-0002.

**Ce NU poate fi descris încă (limitare de dovadă, nu de efort):**
- Regimuri de piață / datasets / timeframe-uri multiple — inexistente în dovadă (axe condiționale, logate). Mai multă descriere NU le poate crea; doar Alpha (date noi) le poate.
- Comportament live/shadow (Flow B) — nu e obiect de P1.

**Ce trebuie să aștepte INTENȚIONAT P2 (nu scurgeri în P1):**
- TOATE relațiile cross-axă: side×outcome (long-skew 271/86), familie×outcome, `val_exp` vs `exp` ca divergență, concentrare (t1/t3/t5) vs flag `fragile`, S1 vs restul.
- P1 descrie fiecare axă *marginal*; corelarea lor e P2. Aceasta e granița pe care fiecare raport din §4 o respectă explicit.
- Mecanismele („de ce") — 🔒 P4.

---

## 7. PLAN REVISION RULES (rafinare operațională CEO)

Planul e **stabil implicit**. Reordonarea e permisă doar de un trigger *de acoperire* (info-gain sau fezabilitate), niciodată de un trigger despre relații, mecanisme sau „interesant" — acelea aparțin fazelor/cozii de mai târziu.

### 7.1 Condiții în care secvența POATE fi reordonată
- **Info-gain schimbat de o descoperire de acoperire:** o coloană planificată se dovedește goală/constantă/non-informativă (scade în prioritate → se loghează „non-informativă + motiv") SAU o celulă cotată jos ascunde structură nedescriptată majoră (poate urca).
- **Dependență descoperită:** un raport ulterior are nevoie de ceva ce unul anterior nu a livrat → resecvențiere ca să deblocheze.
- **Eveniment de Lifecycle (§2.1, înghețat):** batch Alpha nou / regenerare / schimbare de schemă → Coverage Confidence scade automat și planul **trebuie** re-prioritizat ca să acopere întâi materialul nou.
- **Gol blocant:** un artefact necesar unui raport planificat lipsește/e corupt.

### 7.2 Descoperiri SUFICIENTE pentru a schimba prioritățile
- O coloană/celulă planificată e goală, constantă sau non-informativă.
- O celulă dezvăluie mult mai multă structură nedescriptată decât cota ei de info-gain.
- Schimbarea bazei de dovezi (batch/regenerare/schemă) — re-prioritizare **obligatorie**.
- Un gol structural care blochează un raport ulterior.

### 7.3 Descoperiri care NU sunt suficiente (garda principală)
- **Un tipar cross-axă tentant** observat în timpul descrierii (ex. long-skew pare convingător) → **NU** reordonează. E 🔒 P2: se loghează în coada relațională, secvența rămâne neschimbată. *(Cel mai tentant motiv de deviere e exact cel care trebuie rezistat — e muncă P2 deghizată în urgență.)*
- **O idee de ipoteză** care se formează → NU (🔒 P4, interzis).
- **O anomalie descriptibilă în raportul curent** → se descrie pe loc (notă), nu se reordonează.
- Preferință de comoditate/estetică.

### 7.4 Guvernanță a reordonării
- Reordonarea **intra-secvență** (schimbarea ordinii, coborârea unei coloane moarte la „non-informativă") e operațională, la discreția Flow C, dar **logată** (traseu de audit în acest document).
- Orice schimbare care ar altera *definiția* P1 Completion (A.5), ar extinde scopul dincolo de descriptiv, sau ar deschide P2 → necesită **decizie CEO**, nu e operațională.

---

## NOTĂ DE PLANIFICARE

Secvența 0002→0005 e proiectată să bifeze integral checklist-ul A.5 (P1 Completion). Ea NU atinge B.4 (P2 Readiness) — coada relațională se acumulează pasiv (granițele 🔒 din fiecare raport), dar deschiderea P2 rămâne o decizie CEO separată după ce P1 e închis.

*Sfârșitul planului de acoperire. Livrat pentru review CEO. Nu am produs rapoarte, nu am deschis P2, nu am modificat documente înghețate. Aștept aprobarea planului înainte de a genera RI-REPORT-0002.*
