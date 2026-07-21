# MISSION OF RESEARCH INTELLIGENCE
### Flow C — Documentul fundamental de misiune
**Status:** ✅ OFICIAL — ÎNGHEȚAT (FROZEN) prin decizie CEO, 2026-07-21
**Nimic implementat. Niciun cod. Document de misiune, guvernanță și epistemologie.**

> Acest document este congelat ca misiunea oficială a Flow C. Orice modificare ulterioară cere o nouă decizie CEO explicită și o notă de versiune.

---

## 0. TRIADA — de ce trei fluxuri, nu două

Laboratorul are deja două fluxuri care se închid într-o buclă aparent completă:

| Flux | Întrebare | Direcție | Natură |
|---|---|---|---|
| **A — Alpha Discovery** | „Cum găsim și validăm edge-uri?" | Înainte: ipoteză → test → verdict | **Generativă** |
| **B — AI Trader** | „Cum executăm determinist edge-uri validate?" | Înainte: cunoaștere → acțiune | **Deterministă** |

Ambele lucrează **înainte** și **local**: A ia o ipoteză o dată, o testează, o închide. B ia o cunoaștere validată o dată, o execută.

Ce lipsește nu e un al treilea generator. Lipsește un cititor.

| Flux | Întrebare | Direcție | Natură |
|---|---|---|---|
| **C — Research Intelligence** | „Ce înseamnă, împreună, tot ce am produs — și ce întrebare nouă ne pune?" | **Înapoi și transversal**: rezultate → tipar → mecanism candidat → întrebare | **Interpretativă** |

Flow C nu adaugă o a treia mână care produce. Adaugă **ochiul care privește înapoi peste tot ce au produs celelalte două** și întreabă ce nu am înțeles încă.

---

## 1. Care este problema pe care nici Alpha Discovery, nici AI Trader nu o rezolvă?

**Laboratorul produce mult mai multe date decât convertește în înțelegere.**

- Fiecare backtest, walk-forward, Monte Carlo, fiecare familie testată (S1–S20, 1972 ipoteze) lasă în urmă un **corp masiv de rezultate**. Alpha Discovery îl folosește pentru un singur scop: verdictul „acest edge e real sau nu". După verdict, restul informației — de ce a eșuat, ce au în comun eșecurile, ce tipar leagă câștigătorii — rămâne **necitit**.
- AI Trader produce continuu **divergențe** între backtest și comportament live (shadow evidence). El le loghează ca să execute corect. Nu are ca *sarcină* să întrebe ce ne spune tiparul acestor divergențe despre piață.

Niciunul dintre cele două nu are în fișa postului să citească **transversal, peste toate rezultatele deodată**, inclusiv peste eșecuri, ca să extragă cunoaștere de ordinul doi.

> **Problema orfană a laboratorului:** cunoașterea de ordinul doi — tiparele-despre-tipare, mecanismele care explică multe rezultate disparate simultan, cunoașterea negativă (ce eșuează sistematic) — **nu e treaba nimănui.** Se pierde ca „gaz de eșapament" al cercetării.

Flow C există pentru a captura exact acest gaz de eșapament și a-l transforma înapoi în combustibil.

### 1.1 — Obiectul dublu de studiu: piața ȘI laboratorul (adăugire CEO)

Flow C nu studiază doar piața. Studiază **două obiecte în același timp:**

1. **Piața** — indirect, prin răspunsurile pe care ea le-a dat deja *prin* rezultatele laboratorului.
2. **Laboratorul însuși** — direct: cum caută, ce ratează, unde se contrazice, ce tipare de eșec repetă, de ce anumite regiuni ale spațiului de ipoteze rămân neexplorate.

A doua față e la fel de importantă ca prima. Un tipar în rezultatele noastre poate spune tot atât despre **metoda noastră de cercetare** cât despre piață — iar a distinge între cele două (semnal de piață vs. artefact de metodă) este muncă centrală de Flow C. *(Precedent: artefactul de expectancy la stop-uri mici era un defect de metodă, nu un edge de piață.)*

> **Scop unic, formulat complet:** Flow C transformă **întreaga dovadă a laboratorului — despre piață și despre sine — în cunoaștere care schimbă direcția viitoare de cercetare.** Dacă o analiză Flow C nu schimbă unde va căuta laboratorul mâine, nu și-a atins scopul.

---

## 2. Care este întrebarea fundamentală la care răspunde Flow C?

Alpha Discovery întreabă: *„Cum găsim edge-uri?"* — generativ, un caz o dată.
AI Trader întreabă: *„Cum executăm edge-uri?"* — determinist.

Research Intelligence întreabă:

> ## „Ce nu înțelegem încă despre piață — judecând după tiparul propriilor noastre rezultate?"

Sau, echivalent operațional:

> „De ce arată rezultatele noastre așa cum arată, ce mecanism le-ar putea explica pe toate deodată, și ce întrebare nouă naște acest tipar?"

Este o întrebare **interpretativă**, nu generativă. Nu caută răspunsuri noi de la piață direct — citește răspunsurile pe care piața le-a dat deja *prin* rezultatele laboratorului, și le interpretează.

---

## 3. Ce tip de cunoaștere produce Flow C?

Nu „rapoarte". Rapoartele sunt doar recipientul.

Flow C produce **cunoaștere de ordinul doi** — cunoaștere *despre* propria producție de cunoaștere a laboratorului. Concret, patru forme:

1. **Regularități structurale** — ce e sistematic adevărat peste rezultate, deși niciun experiment individual nu a fost proiectat să dezvăluie asta. *(ex: „câștigătorii au în comun filtrul X, indiferent de familie")*
2. **Anomalii** — locurile unde rezultatele contrazic așteptarea sau se contrazic între ele. *(ex: „S6 are expectancy 2× mediana doar sub un anumit prag de stop")*
3. **Mecanisme candidat** — ipoteze cauzale falsificabile pentru un tipar observat. Nu „ce se întâmplă", ci „de ce s-ar putea întâmpla". *(ex: „expectancy-ul inflat la stop-uri mici e artefact de rezoluție a modelului de fill, nu edge")*
4. **Cunoaștere negativă** — ce eșuează în mod repetat. Un drum mort documentat e cunoaștere: împiedică laboratorul să-l reia.

Toate patru sunt subordonate principiului deja adoptat al laboratorului — **mecanism peste tipar**. Flow C este vânătorul de mecanisme la nivel meta: tiparul e simptomul, mecanismul candidat e produsul.

---

## 4. Observație vs. informație vs. cunoaștere vs. ipoteză — și unde se oprește Flow C

Scara epistemică pe care operează Flow C, de la brut la structurat:

| Nivel | Definiție | Exemplu |
|---|---|---|
| **Observație** | Un fapt brut, direct citibil din rezultate. Fără context, fără relație. | „Familia S6 folosește stop-uri mici." |
| **Informație** | Observația plasată în context și făcută comparabilă. Observație + relație. | „S6 arată expectancy 2× mediana, DAR numai în regim low-vol." |
| **Cunoaștere (observațională)** | O relație stabilă, repetabilă, care ține peste contexte în corpul observat. | „Expectancy-ul inflat apare în ORICE familie cu stop sub pragul X — nu e specific S6." |
| **Ipoteză** | O *cauză* propusă pentru cunoaștere, falsificabilă, încă netestată. | „Apare pentru că modelul de fill nu captează slippage-ul la stop-uri sub granularitatea barei." |

**Unde se oprește responsabilitatea Flow C:**

Flow C poate urca scara până la **ipoteză inclusiv** — poate ajunge chiar la *cunoaștere observațională* (un tipar care ține peste tot ce a observat).

Dar există un plafon dur, care definește granița:

> **Cunoașterea observațională a Flow C ≠ cunoașterea validată a Flow A.**
> Cunoașterea Flow C descrie ce *pare* adevărat peste rezultatele deja produse. Este epistemic mai slabă. În momentul în care o afirmație are nevoie de **un experiment nou pe date proaspete/live** pentru a-i confirma mecanismul cauzal, ea **iese din mâna Flow C.**

Produsul terminal al Flow C este o **ipoteză falsificabilă, bine pusă, împachetată împreună cu dovada observațională care a motivat-o** — gata de a fi testată de Alpha Discovery. Flow C nu trece niciodată pragul de la „pare adevărat în ce am observat" la „este adevărat".

---

## 5. Ce NU trebuie să facă NICIODATĂ Flow C — limite absolute

1. **Nu validează niciodată.** Validarea este monopolul exclusiv al Alpha Discovery. Flow C produce ipoteze, nu verdicte.
2. **Nu scrie în niciun component de producție** — Strategy Health, Scoring Engine, Risk Manager, Portfolio Architect, Alpha Discovery, AI Trader. Drept de citire, zero drept de scriere.
3. **Nu generează cod de producție** și nu optimizează parametri sau threshold-uri.
4. **Nu activează și nu dezactivează** nicio strategie.
5. **Nu comunică niciodată direct cu Flow B.** Orice cunoaștere ajunge la AI Trader doar pe traseul complet: RI → Alpha Discovery → Validare → CEO Approval → AI Trader.
6. **Nu-și tratează propria ipoteză ca adevăr** și nu se auto-promovează. Presupunerea implicită e că Flow C se poate înșela.
7. **Nu fabrică observații.** Observă exclusiv din rezultate reale, deja produse. Zero date inventate. *(în linia directivei de laborator: observă doar din date reale, niciodată fabricat.)*
8. **Nu creează date experimentale noi.** Flow C *citește* output-uri existente; nu-și rulează propriile backtest-uri ca să-și „demonstreze" ipoteza. Dacă e nevoie de un test nou, Flow C scrie un **Candidate Experiment** pentru Alpha Discovery — nu îl execută el.

Regula de graniță care le rezumă pe toate: **dacă un pas cere fie testare pe date proaspete, fie atingerea unui parametru live — nu mai e Flow C.** Flow C se oprește la „ipoteză formulată + dovadă observațională" și pasează mai departe.

---

## 6. Ce înseamnă o „descoperire" (discovery) pentru Flow C?

Pentru Alpha Discovery, o descoperire = un edge validat.
Pentru Research Intelligence, definiția e fundamental diferită:

> **O descoperire Flow C = o întrebare nouă, bine pusă, pe care laboratorul nu știa că trebuie să și-o pună — sau o regularitate până acum invizibilă în propriile rezultate, care reîncadrează ce merită testat în continuare.**

Mai precis, Flow C a „descoperit" ceva când scoate la suprafață un **tipar-peste-rezultate + un mecanism candidat** care:
- (a) nu a fost ținta niciunui experiment individual,
- (b) este falsificabil,
- (c) **schimbă ce ar trebui să testeze Alpha Discovery în continuare.**

Criteriul de succes al unei descoperiri Flow C **nu este dacă e adevărată** (asta o decide A), ci **dacă redirecționează cercetarea.** Cea mai valoroasă formă: o ipoteză unificatoare care explică dintr-o dată multe rezultate împrăștiate.

> Flow C nu descoperă răspunsuri. Descoperă **întrebări mai bune.**

### 6.1 — Rolul special: descoperirea „unknown unknowns" (adăugire CEO)

Există trei categorii de necunoscut în laborator:

| Categorie | Cine o acoperă |
|---|---|
| **Known knowns** — ce știm și știm că știm (cunoaștere validată) | Alpha Discovery |
| **Known unknowns** — întrebări pe care le punem deja (ipoteze deschise, Open Research Questions) | Alpha Discovery + directivele existente |
| **Unknown unknowns** — întrebări pe care **nicio ipoteză curentă nu le pune** | **DOAR Flow C** |

Alpha Discovery, prin construcție, poate testa doar ipoteze **deja formulate** — nu poate căuta ce nu știe să caute. AI Trader execută ce e deja validat. Zona întrebărilor neformulate — a lucrurilor pe care nu știm încă nici măcar să ne întrebăm — este **teritoriul propriu al Flow C** și motivul cel mai profund pentru existența lui.

Mecanismul prin care Flow C le scoate la suprafață:
- **Ce e absent** — regiuni ale spațiului de ipoteze pe care nimeni nu le-a atins, vizibile abia când privești corpul întreg de rezultate.
- **Ce e sistematic ignorat** — variabile prezente în date pe care niciun experiment nu le-a folosit ca axă.
- **Contradicții tăcute** — două rezultate care nu ar trebui să coexiste, dar coexistă, semnalând o presupunere ascunsă și greșită.
- **Explicații unificatoare surpriză** — un mecanism care leagă rezultate pe care nimeni nu le credea înrudite, deschizând o clasă întreagă de întrebări noi.

> Un unknown unknown descoperit de Flow C nu este un răspuns și nici măcar o ipoteză validabilă imediat — este **conștientizarea că exista o întrebare pe care laboratorul o rata în întregime.** Aceasta e cea mai valoroasă formă de descoperire Flow C, tocmai pentru că nimeni altcineva din laborator nu o poate produce.

---

## 7. Produsul final al unui ciclu complet — în termeni de valoare

Nu „un document". Documentul e ambalajul. Valoarea adusă laboratorului este:

> **Un increment de înțelegere care direcționează următorul ciclu de Alpha Discovery — reducerea incertitudinii laboratorului despre *unde* să caute în continuare.**

Cu alte cuvinte, produsul unui ciclu Flow C **crește rata de conversie a cercetării din întâmplare în intenție.** În loc ca Alpha Discovery să enumere brut spațiul de ipoteze (1972 de căutări), Flow C îi spune *în ce regiune a spațiului* arată deja dovada acumulată. A caută **cu țintă**, nu prin epuizare.

Valoarea are două componente măsurabile:
1. **Direcție** — următorul batch al Flow A este mai bine țintit *datorită* Flow C. (Test: dacă rata de hit a lui A crește după ce consumă output-ul C.)
2. **Memorie instituțională a eșecului** — cunoașterea negativă curatoriată care împiedică relansarea drumurilor moarte. *(în linia directivei laboratorului: nu șterge intrările vechi; renunță la ideile greșite dar păstrează de ce erau greșite.)*

> Rezumat într-o frază: **produsul final al Flow C este ca Alpha Discovery să caute cu intenție, nu la întâmplare.**

---

## POZIȚIONARE FAȚĂ DE DIRECTIVELE EXISTENTE

Laboratorul are deja directive de *raportare* și *practică individuală*: Research Journal, Open Research Questions, AI Researcher Mode, Telegram Notifications. Acestea sunt **proceduri pe care un agent le urmează în interiorul oricărui context**.

Flow C este diferit: e un **departament** a cărui unică sarcină e cunoașterea de ordinul doi, operând pe **agregat**, nu în interiorul unui context. Flow C **consumă** aceste directive ca input (jurnalele și întrebările deschise sunt materie primă), le **instituționalizează și le scalează**, dar **nu le înlocuiește și nu se suprapune** peste responsabilitatea lor.

---

## PRINCIPIU DE ÎNCHIDERE

> Flow C nu are întotdeauna dreptate. Flow C produce ipoteze și explicații. Flow C **nu validează niciodată.** Validarea rămâne exclusiv responsabilitatea Alpha Discovery.

---

## STARE DE ÎNGHEȚARE

**DOCUMENT ÎNGHEȚAT (FROZEN) — misiunea oficială a Flow C.**
Aprobat de CEO la 2026-07-21, cu cele două adăugiri cerute integrate (§1.1 obiectul dublu de studiu, §6.1 unknown unknowns).

Versiune: `MISSION v1.0 — FROZEN`. Orice modificare ulterioară necesită decizie CEO explicită și bump de versiune.
Următorul pas autorizat: **Faza 0 — Fundație** (definirea formatelor standard pentru cele 8 tipuri de output). Fără cod, fără atingerea Flow A / Flow B.
