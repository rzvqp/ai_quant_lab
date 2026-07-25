# STATISTICIAN — OPERATIONAL DEFINITIONS v1.0
### Răspuns metodologic la clarificările solicitate de Validation Engine

**Document ID:** STAT-OPDEF-v1.0
**Data:** 2026-07-24 · **Autor:** Statistician
**Context:** Validation Engine a semnalat 3 ambiguități în protocolul DC-0004 înainte de a putea exprima complet specificația de execuție — exact clauza de oprire obligatorie (§1.7 din contractul Statistician↔Validation Engine). Acest document e răspunsul metodologic, fără implementare sau cod.

**Nu s-a modificat niciun Discovery Candidate, Addendum, Raport Red Team, Knowledge Base, Validation Engine, sau Capability Registry.**

---

## 1. Definiția oficială a "primei bare H1 a zilei"

**Regula:** ziua se ancorează la ora locală New York (America/New_York), NU la miezul nopții UTC. Motivul e structural, nu stilistic: "prior-day high" (nivelul D1 folosit de DC-0004) și convenția de rollover zilnic OANDA sunt deja legate de ora locală New York (17:00, ora tradițională de închidere/rollover pentru piața FX), nu de un ceas UTC fix. Dacă granița zilei ar fi definită diferit de granița folosită pentru a calcula "prior-day high," cele două concepte ar deveni reciproc inconsistente — un risc metodologic tăcut, nu un detaliu.

- **Granița zilei:** 17:00 America/New_York, echivalent 21:00 UTC în perioada EDT (DST activ, mijlocul lunii martie – începutul lunii noiembrie) și 22:00 UTC în perioada EST (restul anului).
- **"Prima bară H1 a zilei"** = bara H1 al cărei timp de deschidere este ≥ granița zilei și < granița zilei + 1 oră (adică prima bară disponibilă în acel interval orar), nu neapărat exact egală cu granița dacă lipsește o bară.
- **Tratamentul DST:** granița se calculează prin conversia orei locale New York în UTC pentru fiecare zi calendaristică specifică (regulile DST americane — a doua duminică din martie, prima duminică din noiembrie) — nu printr-o constantă UTC fixă. Verificare explicită: tranziția de DST are loc dimineața devreme, ora locală (ora 2:00 America/New_York) — deci NU se suprapune cu ancora de graniță (17:00) și nu creează ambiguitate de tip "ora repetată" în selecția primei bare.
- **Zile în care bara nu există** (weekend, sărbători, gap-uri): dacă nicio bară H1 nu are deschiderea în intervalul [graniță, graniță+1h), acea zi calendaristică e **exclusă din populație** — nu este numărată ca "zi fără eveniment." Această regulă trebuie preînregistrată explicit, altfel denominatorul testului se schimbă în funcție de cum sunt tratate zilele lipsă.

**Dependență deschisă, de semnalat înainte de blocarea specificației:** nu am acces la scripturile originale ale lui Alpha (obs0003/0008/0012/0013 — nu sunt printre cele 3 categorii oficiale de artefacte pe care le pot citi). Regula de mai sus e cea corectă din punct de vedere metodologic și consistentă cu convenția deja folosită informal în portofoliu, dar **trebuie confirmat** că testul original in-sample (care a produs p=0.021/0.029) a folosit aceeași convenție de graniță a zilei — altfel re-testul pe holdout n-ar mai fi o replicare a aceluiași test, ci un test diferit. Recomand ca cineva cu acces la acele scripturi să confirme acest lucru înainte ca Validation Engine să blocheze specificația.

## 2. K6 și K12 — aceeași familie de testare multiplă sau familii separate?

**Concluzie: aceeași familie.** Argumentare:

1. **Aceeași ipoteză, aceeași populație de evenimente.** K6 și K12 nu sunt două întrebări diferite — sunt două ferestre de măsurare ale aceluiași fenomen (reversia după sweep-reject), pe exact aceleași evenimente.
2. **Dependență statistică, nu independență.** K12 conține traiectoria de preț a lui K6 ca subset (primele 6 ore din cele 12) — cele două măsurători sunt puternic corelate, nu independente. Tratarea lor ca familii separate, fiecare cu propriul prag alpha=0.05, ar însemna în fapt **două șanse** de a găsi un rezultat "semnificativ" pornind de la aceeași populație — o multiplicitate ascunsă, în plus față de cea deja semnalată de Red Team pentru cele 6 celule sesiune×direcție.
3. **Corecția corectă nu e o simplă înmulțire.** Dacă K6 și K12 ar fi tratate ca 12 teste independente (6 celule × 2 orizonturi) și corectate Bonferroni simplu (alpha/12), corecția ar fi **prea conservatoare**, pentru că nu ține cont de corelația reală dintre K6 și K12 (nu sunt independente, sunt aninate). O corecție prin permutare (max-T pe cele 12 statistici de test, celulă×orizont) captează empiric această corelație și evită atât sub-corectarea, cât și supra-corectarea.

**Recomandare suplimentară, dincolo de întrebarea strict statistică:** înainte de a atinge holdout-ul, recomand desemnarea unui orizont **primar**, preînregistrat (de exemplu K6, fiind mai aproape de eveniment și mai puțin expus la regim/știri intervenite ulterior), cu celălalt (K12) raportat ca verificare secundară de consistență, nu ca al doilea test cu aceeași greutate evidențială. Documentul original DC-0004 prezintă cele două p-values unul lângă altul fără să desemneze unul ca principal — această ambiguitate trebuie rezolvată acum, înainte de execuție, nu după ce se văd rezultatele pe holdout.

## 3. Definițiile oficiale ale sesiunilor (granițe UTC + tratament DST)

Ca și la graniță zilei, sesiunile se ancorează la **ora locală a centrului financiar relevant**, nu la constante UTC fixe — pentru că variabila de interes ("sesiunea NY") reprezintă ciclul real de lichiditate al acelui centru, care se mișcă în UTC odată cu DST-ul local, nu invers.

| Sesiune | Oră locală | UTC (timp de vară local) | UTC (timp de iarnă local) |
|---|---|---|---|
| **New York** | 08:00–17:00 America/New_York | 12:00–21:00 UTC (EDT, mijl. martie–început nov.) | 13:00–22:00 UTC (EST, restul anului) |
| **Londra** | 08:00–16:30 Europe/London | 07:00–15:30 UTC (BST, sf. martie–sf. octombrie) | 08:00–16:30 UTC (GMT, restul anului) |
| **Asia (Tokyo)** | 09:00–15:00 Asia/Tokyo | 00:00–06:00 UTC, **fix pe tot anul** (Japonia nu are DST) |

**Notă importantă:** sesiunea Asia e singura stabilă în UTC pe tot parcursul anului, tocmai pentru că Japonia nu observă DST — o proprietate care simplifică orice candidat condiționat pe ora Asia (DC-0010, 0012, 0014) față de cei condiționați pe NY/Londra.

**Tratamentul suprapunerii Londra/NY** (~12:00-13:00 până la 15:30-16:30 UTC, fereastra de lichiditate maximă): pentru consistență cu analiza in-sample deja existentă (cele "6 celule sesiune×direcție" din DC-0004 presupun sesiuni **reciproc exclusive**, nu suprapuse), recomand păstrarea convenției de partiționare exclusivă — fiecare bară aparține exact unei singure sesiuni, pe baza orei ei UTC convertite din regula locală de mai sus — și NU introducerea unei categorii noi de "suprapunere" acum, pentru că asta ar schimba silențios definiția celulelor față de testul original.

**Tratamentul DST pentru sesiuni:** identic cu regula de la §1 — граnițele se calculează prin conversia orei locale (America/New_York, Europe/London) în UTC, pentru fiecare dată calendaristică specifică, folosind regulile istorice de DST ale fiecărei jurisdicții (care nu coincid mereu ca dată de tranziție — există ferestre scurte, de 1-2 săptămâni în martie și octombrie/noiembrie, unde SUA și UK sunt temporar pe reguli DST diferite).

**Aceeași dependență deschisă ca la §1:** convenția de mai sus e recomandarea metodologic corectă, dar trebuie confirmată contra convenției efectiv folosite în scripturile originale ale lui Alpha înainte ca Validation Engine să o blocheze ca definitivă — altfel riscăm exact tipul de discrepanță tăcută între definiția in-sample și cea din re-test pe care tot acest proces încearcă s-o prevină.

---

**Rezumat pentru Validation Engine:**
1. Ziua = ancorată la 17:00 America/New_York (nu miezul nopții UTC); zilele fără bară în fereastră sunt excluse din populație, nu numărate ca non-eveniment.
2. K6 și K12 = aceeași familie de testare; corecție prin permutare (nu Bonferroni simplu pe 12 teste independente); recomand un orizont primar preînregistrat (K6) și celălalt ca verificare secundară.
3. Sesiunile = ancorate la ora locală a centrului financiar (NY, Londra), convertite în UTC per dată calendaristică; Asia e fixă în UTC pe tot anul; sesiunile rămân reciproc exclusive, ca în analiza originală.

Toate trei depind de o confirmare pe care nu o pot face eu (acces la scripturile originale Alpha) — semnalez asta explicit, nu presupun că regula propusă coincide automat cu ce s-a folosit deja in-sample.
