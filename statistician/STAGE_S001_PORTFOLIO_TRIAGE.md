# STATISTICIAN — STAGE S001: PORTFOLIO TRIAGE
### Clasificarea maturității statistice a întregului portofoliu de Discovery Candidates (Alpha #1)

**Report ID:** STAT-S001-TRIAGE-v1
**Data:** 2026-07-24 · **Autor:** Statistician
**Scop declarat de CEO:** clasificarea maturității statistice a portofoliului — NU validare statistică completă, NU evaluare a corectitudinii mecanismului, NU backtesting, NU recalcularea mecanismelor.

**Surse oficiale folosite:**
- `ai_quant_lab-alpha-automation/discovery_candidates/DISCOVERY_CANDIDATE_INDEX.md` (24 candidați, DC-0001…DC-0024, toți FROZEN)
- Toate cele 24 documente Discovery Candidate (`candidate_v1.md`) și toate Addenda existente
- `ai_quant_lab/red_team/RED_TEAM_PHASE1_REPORT.md` (audit complet, DC-0001…DC-0018)
- Toate cele 18 `REVIEW_DC-XXXX_v1.md` individuale (Red Team)
- `ai_quant_lab-alpha-automation/research_log/OBSERVATION_REGISTRY.md` (consultat pentru contextul orei 00:00-01:00 UTC, relevant pentru DC-0010/0012/0014, conform citărilor deja făcute de Red Team la F9/X6)

**Nu s-a folosit nicio cunoștință externă. Nu s-a modificat niciun artefact. Nu s-a recalculat niciun mecanism. Nu s-a produs nicio strategie. Nu s-a făcut backtesting.**

---

## 1. Executive Summary

Portofoliul conține **24 Discovery Candidates**, dintre care **18 au trecut prin Red Team Audit** (DC-0001…DC-0018) și **6 sunt încă în afara mandatului Statisticianului** (DC-0019…DC-0024) — create de Alpha după închiderea Phase 1 a Red Team, fără niciun review Red Team asociat.

Din cei 18 candidați auditați:
- **3** sunt deja **READY FOR STATISTICAL VALIDATION** — acestea sunt exact DC-0008, DC-0003, DC-0004, deja analizate integral și acceptate de CEO în Stage anterior (Phase 1 individual).
- **8** sunt **NEEDS MORE EVIDENCE** — ipoteze testabile, cu definiție operațională rezonabilă, dar cu evidență mult sub pragul necesar (n mic, fără denominator).
- **5** sunt **MONITORING** — evidență prea subțire/prea contaminată pentru a justifica resurse dedicate acum (adesea n=1, narațiuni compuse, sau conținut deja preluat de alt candidat).
- **2** (DC-0002, DC-0013) sunt **NOT YET STATISTICALLY ASSESSABLE** — populația/clasa de evenimente nu poate fi încă selectată, fiind condiționată de o definiție care nu există (DC-0002: "compresie" nedefinită; DC-0013: pragul de construcție al DC-0008 nedefinit).

Cei **6 candidați neauditați** (DC-0019…DC-0024) sunt clasificați provizoriu **NOT YET STATISTICALLY ASSESSABLE**, nu din lipsă de conținut, ci din lipsă de artefact obligatoriu (Raport Red Team) — arhitectura laboratorului cere trecerea prin Red Team înainte de Statistician. Notabil: toți cei 6 sunt instanțe n=1, iar cinci din șase sunt explicit auto-descrise de Alpha drept **recorduri/extreme ale eșantionului** ("cel mai mare", "cel mai lung", "un nou record") — exact tiparul de risc statistic (extremum de eșantion, nu o distribuție) deja identificat de Red Team la DC-0015.

**Cel mai important risc portofoliu-wide identificat în acest Stage:** 11 din cei 18 candidați auditați (Grupul I, construcție/microstructură) și acum, adăugând DC-0019-0024, un procent și mai mare din portofoliul total, depind de aceeași măsurătoare nefăcută încă — pragul de separare al DC-0008. Fără acest prag, o proporție mare a portofoliului rămâne fie NOT YET STATISTICALLY ASSESSABLE, fie MONITORING.

## 2. Tabel complet — toate cele 24 Discovery Candidates

| ID | Evidence Count | Evidence Quality | Sampling Risk | Selection Bias Risk | Categorie |
|---|---|---|---|---|---|
| DC-0001 | n=2 confirmă + 1 contrast, vizual | Slabă — "cât de rapidă" judecat din ochi, fără măsurătoare | Ridicat — căutare vizuală țintită, fără scan sistematic, fără bază de referință | Ridicat — instanțe găsite prin căutare vizuală de bare-outlier | **NEEDS MORE EVIDENCE** |
| DC-0002 | n=4 (una pre-înregistrată) | Moderată — pre-înregistrarea C4 e un punct forte real | Ridicat — populația ("compresie") nedefinită, evenimentul nu poate fi încă selectat sistematic | Moderat — confound K05 long-beta numit de Alpha, nedecuplat | **NOT YET STATISTICALLY ASSESSABLE** |
| DC-0003 | n=2 micro-C + n=4 HTF-C, plus reutilizare disponibilă a OBS-0017 (n=384) | Bună pentru partea de expunere; testul decisiv reutilizează un dataset existent | Moderat — confuzie scale/lichiditate nedecuplată (ambele instanțe în tape asiatic subțire) | Moderat — n=2 discreționar pentru partea micro | **READY FOR STATISTICAL VALIDATION** *(deja analizat integral — vezi `reviews/DC-0003/`)* |
| DC-0004 | n=42 (matched-null deja rulat) | Cea mai bună din portofoliu — populație/eveniment/orizont/baseline complet specificate | Moderat — nu trece Bonferroni (6 celule), selecție post-hoc a celulei | Ridicat — celula aleasă după inspectarea a ~12 celule | **READY FOR STATISTICAL VALIDATION** *(deja analizat integral — vezi `reviews/DC-0004/`)* |
| DC-0005 | n=2 secvențe (una impură) | Slabă — prior de tip folk-knowledge ("a treia oară se rupe") | Ridicat — fără numărul de niveluri testate de 3 ori care nu au produs nimic ("aproape sigur majoritatea") | Ridicat — risc de confirmation bias explicit semnalat de Alpha | **NEEDS MORE EVIDENCE** |
| DC-0006 | ~5 instanțe, o singură sesiune | Foarte slabă — relația s-a inversat în 24h, deja contrazisă de alte dovezi din portofoliu (DC-0008/0013/0017 au extins pe volum extrem) | Ridicat — fără numărul de lumânări cu volum mare care AU extins | Ridicat — confundat cu efectul de scală (DC-0003) pe 3 din ~5 instanțe | **MONITORING** *(conținutul util e deja preluat de măsurătoarea DC-0008)* |
| DC-0007 | n=1 | Slabă (dar onest etichetată) — o singură instanță | Ridicat — la n=1, indistinguibil de zgomot intrabar ordinar | Moderat — descoperire discreționară | **NEEDS MORE EVIDENCE** |
| DC-0008 | ~6 instanțe discreționare | Cea mai operațională definiție de expunere din portofoliu (raport R), dar fără prag | Ridicat — fără denominator, fără scan sistematic | Ridicat — instanțe găsite prin stepping discreționar | **READY FOR STATISTICAL VALIDATION** *(deja analizat integral — vezi `reviews/DC-0008/`)* |
| DC-0009 | n=1 bandă (lifecycle bogat, 4 addenda) | Bună ca profunzime, dar tot n=1 nivel; Addendum D se auto-contrazice cu C | Ridicat — o singură bandă, variație de weekend-gap/sesiune necontrolată | Moderat — caz unic urmărit intensiv, nu populație | **NEEDS MORE EVIDENCE** |
| DC-0010 | n=1 deviație vs. baseline de 3 zile | Slabă — infirmată de propriul Addendum A (toată sesiunea a fost activă, nu doar ora) și de Observation Registry (instanțe ulterioare la aceeași oră, complet ordinare) | Foarte ridicat — baseline de 3 zile mult prea scurt; claim-ul specific de oră deja contrazis de materiale din lab | Ridicat | **MONITORING** *(întrebarea reziduală legitimă aparține primitivului Volatility, nu acestui candidat)* |
| DC-0011 | 3 instanțe (original + 2 addenda) | Moderată — rezultatul se repetă de 3 ori, dar toate confundate | Ridicat — toate cele 3 instanțe împart același confound (zi anormal de activă), fără instanțe pe zile ordinare | Ridicat | **NEEDS MORE EVIDENCE** |
| DC-0012 | n=1 (+ addendum = rezoluție, nu a 2-a instanță) | Cea mai curată definiție operațională din portofoliu (scan deja specificat de Alpha) | Moderat — scan sistematic e direct fezabil și ieftin | Scăzut-moderat — forma nu depinde de claim-ul de oră (deja infirmat) | **NEEDS MORE EVIDENCE** *(prioritate maximă în această categorie)* |
| DC-0013 | n=2 (original + addendum, aceeași încheiere) | Bună în nișa proprie, dar integral condiționată de pragul DC-0008 nedefinit | Ridicat — gatare externă; posibil efect de selecție ("fără reversal" poate fi survivorship) | Moderat-ridicat | **NOT YET STATISTICALLY ASSESSABLE** *(nu poate fi validat înainte ca măsurătoarea DC-0008 să definească clasa — cuvintele Red Team)* |
| DC-0014 | n=1 | Slabă — formă compusă din 3 părți (V + continuare + reversal) potrivită unei singure apariții, la o oră deja documentată ca inconsistentă | Ridicat — risc clasic de overfitting pe narațiune compusă | Ridicat | **MONITORING** *(Alpha însuși avertizează explicit să nu fie citit ca repetabil)* |
| DC-0015 | n=1 | Slabă — trăsătura distinctivă ("cea mai lungă serie observată") este un extremum de eșantion, nu o afirmație distribuțională | Ridicat — orice eșantion finit are un maxim; aceasta nu e o descoperire despre piață | Moderat | **MONITORING** *(conținutul e deja purtat de întrebarea de durată a DC-0008/0013)* |
| DC-0016 | n=2 la aceeași oră | Cea mai bine susținută sub-afirmație a familiei — forma de încheiere (marginal-high→reversal) recurentă, cu magnitudine explicit variabilă | Moderat — n=2 rămâne mic, dar trăsătura a fost pre-semnalată apoi confirmată | Moderat | **NEEDS MORE EVIDENCE** |
| DC-0017 | 3 instanțe (original + 2 addenda) | Bogată dar auto-infirmată — headline-ul ("hold") contrazis de propriile addenda de 2 ori | Ridicat | Moderat | **MONITORING** *(complet redundant cu propria serie de 12:30 UTC a DC-0008; headline-ul deja mort)* |
| DC-0018 | n=1 | Slabă — secvență compusă din 4 părți la o singură instanță | Ridicat | Ridicat — ambiguitate sweep vs. respingere nerezolvată | **NEEDS MORE EVIDENCE** *(întrebare comună cu DC-0011)* |
| DC-0019 | n=1 (dar există o bază de referință externă utilizabilă: OBS-0015, n=148, rată de umplere gap 93.2%) | Bine documentată ca instanță unică; contrastul cu 9 instanțe anterioare de weekend-gap e explicit | Ridicat — n=1 la magnitudinea nouă; dar populația de 148 gap-uri deja există pentru context | Moderat — instanță selectată tocmai pentru că a rupt tiparul (risc de selecție inerent oricărui "prim record") | **NOT YET STATISTICALLY ASSESSABLE** *(fără Raport Red Team — în afara mandatului curent; conținut promițător pentru re-testare împotriva OBS-0015 odată revizuit)* |
| DC-0020 | n=1 | Descriere atentă, verificare organică M5 inclusă | Ridicat — nou record de volum, extremum de eșantion | Ridicat | **NOT YET STATISTICALLY ASSESSABLE** *(fără Raport Red Team)* |
| DC-0021 | n=1 | Descriere atentă, două mecanisme cunoscute unite într-o secvență nouă | Ridicat — o singură secvențiere observată | Ridicat | **NOT YET STATISTICALLY ASSESSABLE** *(fără Raport Red Team)* |
| DC-0022 | n=1 | Descriere atentă; explicit auto-descrisă ca nou record de durată/magnitudine | Foarte ridicat — extremum explicit, "fiecare record anterior a fost depășit" | Ridicat | **NOT YET STATISTICALLY ASSESSABLE** *(fără Raport Red Team)* |
| DC-0023 | n=1 | Descriere atentă; a treia cea mai mare valoare de volum din tot replay-ul | Foarte ridicat — extremum + secvențiere n=1 imediat după DC-0022 | Ridicat | **NOT YET STATISTICALLY ASSESSABLE** *(fără Raport Red Team)* |
| DC-0024 | n=1 | Descriere atentă, cu o notă onestă de data-quality (o lumânare peste pragul de concentrare organică) | Foarte ridicat — nou record absolut de magnitudine | Ridicat | **NOT YET STATISTICALLY ASSESSABLE** *(fără Raport Red Team)* |

## 3. Clasificarea pe cele patru categorii

**READY FOR STATISTICAL VALIDATION (3):** DC-0003, DC-0004, DC-0008 — deja analizate integral în Stage-ul individual anterior (Phase 1), verdict confirmat de CEO. Niciun element nou de la acest Stage nu schimbă acele verdicte.

**NEEDS MORE EVIDENCE (8):** DC-0001, DC-0005, DC-0007, DC-0009, DC-0011, DC-0012, DC-0016, DC-0018.

**MONITORING (5):** DC-0006, DC-0010, DC-0014, DC-0015, DC-0017.

**NOT YET STATISTICALLY ASSESSABLE (8):** DC-0002, DC-0013 (gate definițional intern portofoliului), DC-0019, DC-0020, DC-0021, DC-0022, DC-0023, DC-0024 (gate procedural — fără Raport Red Team).

## 4. Recomandarea ordinii în care ar trebui analizate statistic

**Deja finalizate (Phase 1 individual, nu se repetă):** DC-0008 → DC-0003 → DC-0004.

**Următorul val recomandat, în cadrul NEEDS MORE EVIDENCE**, ordonat după cost/leverage:

1. **DC-0012** — definiția cea mai curată din portofoliu, scan-ul e deja specificat de Alpha, cel mai ieftin de rulat, cel mai aproape de pragul de "ready."
2. **DC-0016** — n=2 cu o trăsătură recurentă deja pre-semnalată (forma de încheiere); extindere directă, ieftină.
3. **DC-0007** — scan simplu și ieftin (clustere de ≥3 minime egale + reclaim în aceeași lumânare).
4. **DC-0011 + DC-0018 împreună** — împart aceeași întrebare nerezolvată (sweep-reclaim vs. respingere pe zile ordinare vs. anormale); merită analizate ca pereche.
5. **DC-0009** — lifecycle bogat, dar necesită o populație de bande multiple, nu doar o bandă — efort mai mare.
6. **DC-0005** — necesită o populație mare de niveluri testate de 3 ori, risc de confirmare-bias — efort mare.
7. **DC-0001** — scan simplu de definit (viteză vs. bare vecine), dar necesită trecere sistematică prin tot setul de date — efort mare.

**Pentru NOT YET STATISTICALLY ASSESSABLE:**
- **DC-0002** — recomand secvențiere împreună cu execuția Fazei 2 a DC-0003 (aceeași întrebare de scală); odată ce pragul de scală există, "compresia" H4 poate fi redefinită folosind același cadru.
- **DC-0013** — automat deblocat de execuția Fazei 2 a DC-0008; nu necesită o resursă separată, doar rezultatul acelei măsurători.
- **DC-0019…DC-0024** — recomand rutarea imediată către Red Team (aceștia sunt singurii candidați FROZEN din portofoliu fără niciun audit); între ei, **DC-0019 are cea mai mare valoare** pentru că poate fi testat direct împotriva unei baze de referință deja existente (OBS-0015, n=148), analog modului în care DC-0003 reutilizează OBS-0017 — recomand ca Red Team să-l prioritizeze pe acesta dacă alege să nu auditeze toți 6 deodată.

**Pentru MONITORING:** nicio resursă dedicată acum; se reevaluează dacă (a) apar noi instanțe naturale, sau (b) rezultatul măsurătorii DC-0008/primitivului Volatility rezolvă întrebarea reziduală fără cost suplimentar.

## 5. Riscuri metodologice observate

1. **Concentrare structurală de risc pe o singură măsurătoare nefăcută.** O proporție mare a portofoliului (Grupul I: DC-0008 + 0006/0010/0011/0013-0018, plus acum posibil câteva din DC-0019-024) depinde de același prag nedefinit (raportul R al DC-0008). Această măsurătoare unică este, de departe, cel mai mare punct de risc/leverage din tot portofoliul — nerezolvarea ei ține blocată o parte semnificativă a portofoliului în MONITORING sau NOT YET STATISTICALLY ASSESSABLE.

2. **Val nou de candidați construiți sistematic ca extreme de eșantion.** Cinci din cei șase candidați noi (DC-0020…DC-0024) sunt auto-descriși explicit de Alpha drept "noi recorduri" (volum, magnitudine, durată). Acesta este exact tiparul de risc deja identificat de Red Team la DC-0015 (extremum de eșantion, nu o afirmație distribuțională, garantat să fie depășit de următoarea observație). Fără o distribuție de populație din spate, acumularea de "recorduri" nu adaugă evidență — adaugă doar puncte pe coada aceleiași distribuții necunoscute. Recomand semnalarea explicită către CEO/Alpha a acestui tipar înainte ca mai mulți candidați de acest tip să fie creați.

3. **Gol procedural: 6 candidați FROZEN fără Raport Red Team.** 25% din portofoliul total (DC-0019…DC-0024) există în afara pipeline-ului oficial Alpha→Red Team→Statistician. Acesta este un risc de proces, nu doar statistic — arhitectura laboratorului presupune trecerea prin Red Team înainte ca Statisticianul să poată face o evaluare completă de testabilitate.

4. **Absența universală a denominatorului.** Confirmat la acest Stage pentru toate cele 18 candidate auditate (consistent cu Phase 1 Summary): nu există, pentru niciun candidat, un număr al evenimentelor comparabile trecute cu vederea. Aceasta rămâne limitarea dominantă a portofoliului.

5. **Redundanță nerezolvată în cadrul familiei de 12:30 UTC.** DC-0008 (Addenda B/C/D) și DC-0017 documentează parțial aceeași populație de evenimente (impulsuri mari la 12:30 UTC) fără a fi fost încă consolidate — orice evidență nouă colectată pentru unul ar trebui automat verificată și împotriva celuilalt, pentru a evita numărarea dublă a acaceleiași populații ca "evidență independentă."

## 6. Concluzii

Din 24 de Discovery Candidates, doar 3 (12.5%) sunt în prezent READY FOR STATISTICAL VALIDATION — și acestea au fost deja analizate integral. Majoritatea portofoliului (21 din 24) rămâne fie sub-probată (NEEDS MORE EVIDENCE, 8), fie prematur pentru resurse dedicate (MONITORING, 5), fie structural neevaluabilă până la rezolvarea unei precondiții — fie internă portofoliului (DC-0002, DC-0013 — gate de definiție), fie procedurală (DC-0019-0024 — gate de proces, lipsă Raport Red Team).

Cel mai mare pas unic de valoare pentru portofoliu ca întreg rămâne neschimbat față de sinteza Phase 1: **execuția măsurătorii de prag a DC-0008**, care ar debloca simultan DC-0013 și ar clarifica statutul mai multor candidați din MONITORING (DC-0006, DC-0015, DC-0017). Al doilea cel mai mare pas de valoare este procedural, nu statistic: **rutarea celor 6 candidați neauditați către Red Team**, în special DC-0019, care are deja o bază de referință utilizabilă (OBS-0015).

Acest Stage S001 este o clasificare de maturitate a evidenței, nu o judecată asupra corectitudinii niciunui mecanism — nicio concluzie de mai sus nu trebuie citită ca infirmare sau confirmare a vreunei ipoteze.

---

**Nu s-a modificat niciun Discovery Candidate, Addendum, Raport Red Team, sau Knowledge Base.**

**STATISTICIAN se oprește aici. Așteaptă aprobarea CEO pentru Stage S002.**
