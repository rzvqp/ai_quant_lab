# RECONCILIERE — DEFINIȚII OPERAȚIONALE
### Scripturile Alpha in-sample vs. definițiile propuse de Statistician: comparație, impact, recomandare de proces

**Document ID:** VE-RECON-DEF-v1.0
**Data:** 2026-07-24 · **Autor:** Validation Engine
**Statut:** **DOCUMENT DE RECONCILIERE — pentru decizia CEO.** Validation Engine **nu ia decizia**, nu modifică registrul, nu modifică specificațiile, nu începe F3.
**Surse:**
- scripturi: `ai_quant_lab-alpha-automation/research_log/scripts/{obs0003,obs0008,obs0012,obs0013}.py`, `_lab.py`, `edge_research/_common.py`
- definiții propuse: `ai_quant_lab/statistician/STATISTICIAN_OPERATIONAL_DEFINITIONS_v1.0.md`
- verificarea de bază: `SCRIPT_VERIFICATION_Q1_Q3.md`

> **Natura problemei.** Aceasta nu mai este o problemă de vocabular al Validation Engine. Este o problemă de **guvernanță**: laboratorul are, pentru aceleași trei concepte (graniță de zi, sesiuni, definiția evenimentului), **două definiții incompatibile** — una încorporată în codul care a produs rezultatul in-sample (p=0.021/0.029), alta propusă acum ca standard. Câtă vreme ambele coexistă, cuvântul „replicare pe holdout" nu are un sens unic.

---

## 1. Cele trei concepte în dispută

Toate cele patru scripturi (`obs0003/0008/0012/0013`) folosesc convenții **identice**, moștenite prin `from _lab import *` și `_common`. Nu există variație între ele; există o singură convenție in-sample, comparată mai jos cu o singură convenție propusă.

### 1.1 Granița zilei

| | Definiție | Dovadă |
|---|---|---|
| **Scripturi (in-sample)** | data calendaristică **UTC**, graniță la **00:00 UTC** | `_lab.add_prior_day`: `df["day"] = df["dt"].dt.date`; `dt` este UTC. „Prior-day high" = `daily.groupby("day").d_high.shift(1)`, pe aceeași zi UTC |
| **Statistician (propus)** | **17:00 America/New_York**, ajustat DST (21:00 UTC vara / 22:00 UTC iarna) | `OPDEF v1.0` §1 |

Diferență: **graniță complet diferită**, cu decalaj de 21–22 de ore față de miezul nopții UTC și cu variație sezonieră pe care versiunea in-sample nu o are.

### 1.2 Sesiunile

| | Definiție | Dovadă |
|---|---|---|
| **Scripturi (in-sample)** | **4 sesiuni**, cupe de oră **UTC fixă**, fără DST: asia 00–08, london 08–13, ny 13–21, **late 21–24** | `_common.py` linia 91: `np.select([hh<8, hh<13, hh<21], ["asia","london","ny"], default="late")`, `hh = dt.dt.hour` (UTC) |
| **Statistician (propus)** | **3 sesiuni**, ancorate local, DST: NY 12–21/13–22, Londra 07–15:30/08–16:30, Asia 00–06 | `OPDEF v1.0` §3 |

Diferențe: **număr diferit** (4 vs 3, script-ul are „late"); **granițe diferite** pentru fiecare sesiune; **ancorare diferită** (UTC fix vs local cu DST).

### 1.3 Definiția evenimentului

| | Definiție | Dovadă |
|---|---|---|
| **Scripturi (in-sample)** | **prima bară a zilei UTC care depășește nivelul** (`next(i for i in idx if high>ph)`), verificată apoi pentru reject (`close<ph`). Dacă prima depășire nu respinge, ziua nu are eveniment — chiar dacă o bară ulterioară ar respinge | `obs0003/0008/0012/0013`, blocul de selecție |
| **Statistician (propus)** | „prima bară H1 a zilei" — lectură nefixată în OPDEF (a: bara de deschidere / b: prima care satisface) | `OPDEF v1.0` §1 |

Diferență: script-ul folosește **„prima depășire a zilei"** — o a treia variantă, distinctă de ambele lecturi din clarificare, și **neexprimabilă** în vocabularul actual (gol G7).

---

## 2. Diferențe secundare descoperite, relevante pentru replicare

Nu au fost întrebate explicit (Q1–Q3), dar afectează direct ce înseamnă „același test":

| # | Aspect | Scripturi (in-sample) | Statistician (propus) |
|---|---|---|---|
| S1 | **Mărimea familiei Bonferroni** | **empirică**: `cells = [(d,s) if len≥25]`, `thr = 0.05/len(cells)` — depinde de câte celule (din 4 sesiuni × 2 direcții = până la 8) ating n≥25, potențial inclusiv „late" | fixă la **6 celule** (3 sesiuni × 2 direcții), `alpha/6`; ulterior recomandă permutare max-T |
| S2 | **Orizontul testului decisiv corectat** | **K6 singur** (`obs0012`, K=6); K12 doar raportat descriptiv în 0003/0008 | K6 și K12 **aceeași familie**, K6 primar |
| S3 | **Baseline** | 0003: **drift global**; 0008/0012/0013: **media forward a sesiunii proprii** | forward propriu al sesiunii |
| S4 | **Pragul de includere a celulei** | **n ≥ 25** rejecturi pe celulă | n ≥ 15 (min_n al design-ului) |
| S5 | **Matched null** | reeșantionare din barele aceleiași sesiuni, **3000** trageri, `seed=7`, coada stângă (one-sided reversie) | matched-null, două-cozi în raportul Phase 1 |
| S6 | **Split de stabilitate** | `2025-01-01` (obs0013) | — |

S1 și S2 sunt cele mai grave dintre cele secundare: **schimbă direct pragul de decizie** (mărimea familiei) și **care orizont contează** — adică exact criteriul preînregistrat de succes.

---

## 3. Impactul fiecărei diferențe asupra replicabilității

Întrebarea de fond: dacă re-testul pe holdout folosește definițiile Statisticianului, mai este el o replicare a testului care a produs p=0.021?

| Diferență | Ce se schimbă concret | Severitate pentru replicare |
|---|---|---|
| **Granița zilei** (§1.1) | Schimbă complet ce este „prior-day high" și ce bară este „prima a zilei". PDH calculat pe zi UTC ≠ PDH pe zi NY. Populația de evenimente se schimbă la bază | 🔴 **Critică** — redefinește nivelul și evenimentul simultan |
| **Sesiuni: număr** (§1.2) | 3 vs 4 celule de sesiune. „late" (21–24 UTC) dispare sau se contopește. Barele din 21–24 UTC sunt reatribuite | 🔴 **Critică** — schimbă apartenența la celule și mărimea familiei |
| **Sesiuni: granițe** (§1.2) | Fereastra NY 13–21 (script) vs 12–21/13–22 (Statistician). Bare la 12:00 și 21:00–22:00 UTC își schimbă sesiunea. Fereastra NY in-sample nu include ora 12:00 UTC; cea propusă o include (vara) | 🔴 **Critică** — celula NY-up, chiar câștigătoarea, își schimbă compoziția |
| **Sesiuni: DST** (§1.2) | Ancorarea locală mută granițele cu ±1h de două ori pe an; versiunea in-sample e fixă. Barele din ferestrele de tranziție se reatribuie sezonier | 🟠 **Mare** — introduce o variație pe care testul original nu o avea |
| **Definiția evenimentului** (§1.3) | „prima depășire" (script) vs „bara de deschidere" sau „prima care satisface reject". Populații diferite, denominatoare diferite | 🔴 **Critică** + **neexprimabilă** (G7) |
| **Mărimea familiei** (S1) | Prag corectat `0.05/len(cells)` empiric vs `0.05/6` fix. Dacă „late" atinge n≥25, familia in-sample e mai mare → prag mai strict. Criteriul de succes se schimbă | 🟠 **Mare** — schimbă pragul de decizie |
| **Orizontul decisiv** (S2) | In-sample, corecția Bonferroni s-a aplicat pe K6 singur; propunerea leagă K6+K12. Numărul de teste corectate diferă | 🟠 **Mare** — schimbă criteriul preînregistrat |
| **Baseline** (S3) | obs0003 global vs propus per-sesiune. Escaladarea (0008+) e deja per-sesiune, deci impact parțial | 🟡 **Moderată** |
| **min_n** (S4) | 25 (script) vs 15 (design). Celule marginale intră/ies | 🟡 **Moderată** |
| **Two-sided vs one-sided** (S5) | In-sample coada stângă (reversie); Phase 1 vorbește two-sided. p-ul se dublează la one→two | 🟠 **Mare** — schimbă direct valoarea p |

**Concluzie de replicabilitate:** cinci diferențe critice și patru mari. Nu este o discrepanță de detaliu care s-ar putea neglija. **Sub definițiile Statisticianului, populația de evenimente, compoziția celulelor, mărimea familiei, orizontul corectat și lateralitatea testului diferă toate față de in-sample.** Un rezultat obținut astfel nu poate fi numit „replicarea" testului care a produs p=0.021 — este un test nou, care nu moștenește dovada in-sample ca justificare.

---

## 4. Cele două căi de guvernanță, cu consecințele lor

Există exact două poziții coerente. Ambele sunt legitime; se exclud reciproc.

### Calea A — REPLICARE STRICTĂ
Definiția oficială = **exact convenția in-sample** (zi UTC, 4 sesiuni fixe UTC, eveniment „prima depășire", familie empirică n≥25, K6 decisiv, baseline per-sesiune, one-sided, seed=7).

- **Avantaj:** re-testul pe holdout este o replicare autentică; rezultatul in-sample (p=0.021) rămâne dovada de bază pe care holdout-ul o confirmă sau infirmă.
- **Cost:** îngheață și eventualele defecte metodologice ale convenției in-sample (graniță UTC arbitrară, „late" nemotivat, baseline inconsistent între 0003 și 0008).
- **Dependență pentru Validation Engine:** necesită rezolvarea **G7** (`first-in-scope`) înainte ca specificația oficială să poată fi exprimată — evenimentul „prima depășire" nu e exprimabil azi.

### Calea B — RE-SPECIFICARE ÎMBUNĂTĂȚITĂ
Definiția oficială = **definițiile Statisticianului** (ancorare locală, DST, 3 sesiuni, permutare max-T), mai corecte metodologic.

- **Avantaj:** convenție conceptual mai solidă (sesiunea = ciclul real de lichiditate al centrului financiar, nu o cupă UTC arbitrară).
- **Cost decisiv:** holdout-ul devine un test **nou**. Rezultatul in-sample p=0.021 **nu îl mai justifică**, pentru că a fost măsurat sub altă definiție. A cheltui holdout-ul (resursă irepetabilă, CEO-gated) pe o ipoteză a cărei susținere in-sample nu a fost niciodată măsurată sub noua definiție ar fi o risipă a resursei.
- **Consecință procedurală obligatorie:** înainte de a atinge holdout-ul, testul in-sample trebuie **re-rulat sub noile definiții** pe datele ne-sigilate, ca să se restabilească baza de dovezi. Dacă efectul dispare sub noua definiție, holdout-ul nu ar trebui cheltuit deloc.

---

## 5. Recomandarea mea privind procesul (nu decizia)

Nu recomand care definiție este „corectă" — este o alegere de guvernanță care aparține CEO și de proiectare statistică ce aparține Statisticianului. Recomand **procesul** prin care laboratorul ar trebui să ajungă la o singură definiție oficială:

1. **Fixați o singură definiție oficială pentru toate cele trei concepte, într-un artefact unic** (graniță de zi, sesiuni, eveniment), și tratați-le ca un pachet — nu se pot amesteca (ex. zi NY cu sesiuni UTC), pentru că PDH și apartenența la sesiune trebuie derivate din aceeași ancoră.

2. **Declarați explicit ce înseamnă „replicare" pentru acest candidat** — Calea A sau Calea B din §4 — și scrieți consecința aleasă lângă decizie, astfel încât nimeni să nu citească ulterior holdout-ul ca „confirmare in-sample" dacă s-a ales B.

3. **Dacă alegeți Calea B, re-rulați in-sample sub noua definiție înainte de holdout** (pe date ne-sigilate), și tratați acel rezultat ca noua bază de dovezi. Holdout-ul se atinge doar dacă baza re-măsurată justifică cheltuirea lui.

4. **Nu atingeți holdout-ul până când definiția nu e înghețată și aprobată** — este o resursă irepetabilă; orice ambiguitate de definiție cheltuită pe ea nu mai poate fi recuperată (constituție Statistician §8.7; `NEXT_SESSION.md`).

5. **Rezolvați diferențele secundare S1–S5 în același pachet**, nu separat — mărimea familiei și orizontul decisiv (S1, S2) schimbă criteriul preînregistrat de succes la fel de mult ca definițiile primare, iar lateralitatea (S5) schimbă direct valoarea p.

6. **Abia după înghețarea definiției oficiale**, Validation Engine o poate bloca în registru/specificație ca normă, iar dependența tehnică devine clară: Calea A cere prioritizarea G7; Calea B nu, dacă evenimentul se redefinește ca „bara de deschidere".

7. **Semnalați către Alpha** că viitoarele experimente ar trebui să emită definițiile operaționale (graniță, sesiuni, eveniment) ca artefact explicit, versionat, alături de rezultat — exact pentru ca acest tip de discrepanță tăcută să nu se mai repete la următorul candidat. Convențiile in-sample au trebuit reconstruite din cod (`_lab`/`_common`), nu citite dintr-o declarație.

---

## 6. Ce nu am făcut

- **Nu am ales** între Calea A și Calea B, nici între vreo definiție.
- **Nu am modificat** registrul, specificațiile, fixturile sau codul.
- **Nu am blocat** nicio convenție ca normă oficială — fixturile rămân nenormative pe graniță/sesiuni/eveniment.
- **Nu am început F3.**
- **Nu am atins** holdout-ul și nicio dată de piață; scripturile Alpha au fost citite ca text-sursă, nu executate.

---

**Validation Engine a produs documentul de reconciliere cerut și se oprește. Decizia asupra convențiilor oficiale ale laboratorului aparține CEO și Statisticianului.**
