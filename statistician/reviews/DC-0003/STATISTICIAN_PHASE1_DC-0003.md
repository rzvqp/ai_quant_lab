# STATISTICIAN — PHASE 1 REPORT

**Report ID:** STAT-PHASE1-DC-0003-v1
**Discovery Candidate:** DC-0003 — "Scale Inversion — Micro-Scale Coils And Higher-Timeframe Compressions Resolve In Opposite Ways"
**DC freeze hash (as cited by Red Team):** `sha256:e56076c5c4fce6a296f77e996fe050f03ae6b27fc3b929819e8824033195ac7d` (current, post Library-Concept-Scan recompute)
**Phase:** Statistician Phase 1 — DESIGN AND TESTABILITY EVALUATION ONLY. No backtest executed. No new data collected. No market validation.
**Date:** 2026-07-24 · **Reviewer:** Statistician
**Sources read (read-only, official artifacts only):**
- `ai_quant_lab-alpha-automation/discovery_candidates/DC-0003_scale_inversion_of_break_behaviour/candidate_v1.md`, `metadata_v1.json` (no addenda exist — confirmed by directory listing, consistent with Red Team's "Addenda: none")
- `ai_quant_lab/red_team/reviews/DC-0003/REVIEW_DC-0003_v1.md`
- `ai_quant_lab/red_team/RED_TEAM_PHASE1_REPORT.md` — §0, F1–F9, X1–X6, O2/O8 (§4 O2), §5 implicit assumptions, §6 DC-0003 entry, §7 items 4/8, §8 DC-0003 row.

**Explicitly NOT read:** Alpha or Red Team conversation/chat history; `research_log/OBS-0017_swing_overshoot.md` itself (the underlying null-result document DC-0003 references as `source_artifacts`). OBS-0017 is not one of the three authorized artifact categories (Discovery Candidate / Addenda / Red Team Report); all facts about it used below (n=384 swing-high exceedances, break geometry uninformative, CI spans 0) are taken exclusively from quotations already present inside `candidate_v1.md` and `REVIEW_DC-0003_v1.md`. Any Discovery Candidate other than DC-0003 (incl. DC-0002, which this candidate subsumes) was not separately opened — only what the Red Team report quotes directly about it (F8/O2) is used.

**Nothing was modified.** DC-0003, the Red Team report/review, Knowledge Base, Alpha artifacts, and existing confidence/classifications are untouched.

---

## 1. Reconstrucția fidelă a ipotezei

Din `candidate_v1.md` §§1–3, fără reformulare în strategie:

> Compresia nu înseamnă același lucru la orice scară. Două clase se comportă opus: **HTF-C** (compresie H4 / multi-day consolidare după o extensie) se rezolvă printr-o expansie direcțională autentică (observată 4/4 — subiectul DC-0002). **micro-C** (coil M15 de ~5-10 candele într-un range, tipic în tape asiatic subțire) produce o spargere marginală dincolo de limita coil-ului, care eșuează imediat și se inversează (observată 2/2). Același cuvânt "breakout" descrie două evenimente opuse în funcție de dacă limita coil-ului se află în interiorul sau în afara amplitudinii de zgomot predominante (noise amplitude).

Ipoteza este prezentată de Alpha explicit ca observație descriptivă, nu ca edge sau strategie ("Not validated, not an edge, not a strategy, no profitability claim" — Handoff Statement).

## 2. Variabilele măsurate

- **Variabilă de expunere:** scara la care apare compresia, relativ la amplitudinea de zgomot predominantă — categorie propusă: micro (limita coil-ului în interiorul zgomotului) vs. HTF (limita în afara zgomotului).
- **Variabilă de rezultat:** felul în care se rezolvă spargerea — expansie direcțională susținută (HTF-C) vs. spargere marginală care eșuează imediat și se inversează (micro-C).
- **Variabile secundare notate în cele 2 instanțe micro-C:** range-ul coil-ului în scădere (1.51→0.62 pt și 1.55→0.62 pt), volumul în scădere apoi crescut pe spargere (656→343→813; ~210 flat→546), amplitudinea de preț "pinned" (1.3-1.5 pt).

## 3. Definiția operațională existentă

Pentru micro-C: un coil de ~5-10 candele M15, cu range descrescător și preț "pinned" într-o bandă îngustă, urmat de o spargere marginală care eșuează. Pentru HTF-C: compresia H4/multi-day (subiectul DC-0002), urmată de expansie. **Niciuna dintre cele două clase nu are un prag numeric fix** — "coil", "pinned", "compresie" rămân descriptive. Singura propunere de operaționalizare este chiar în candidatul frozen, §"Additional Notes": granița dintre clase se află probabil "acolo unde range-ul coil-ului trece de un anumit multiplu al ATR predominant" — dar multiplul respectiv nu este specificat, nu este testat, și este explicit etichetat ca întrebare deschisă pentru "whoever tests this."

## 4. Elemente lipsă pentru testare

| Element | Status |
|---|---|
| **Denominator** | Absent. n=2 micro-C, n=4 HTF-C (= DC-0002), toate discreționare (stepping manual). Niciun număr de coiluri/compresii trecute cu vederea care nu au produs modelul de rezolvare descris. |
| **Prag numeric (scale boundary)** | Absent. Multiplul de ATR propus în Additional Notes nu are valoare, nu este testat. |
| **Definiție operațională a "coil"/"compresie"** | Absentă: fără număr minim de candele, rată de contracție a range-ului, sau prag de volum fixat în avans. |
| **Separare scale vs. lichiditate** | Confundate: ambele instanțe micro-C sunt în tape asiatic subțire (trough-ul profilului orar de volatilitate) — Alpha însuși semnalează acest lucru ca alternativă nedecuplată. |
| **Orizont de "rezolvare"** | Neprecizat câte bare după spargere definesc "expansie susținută" vs. "eșec imediat". |
| **Separarea pe scară a setului OBS-0017** | Nulul existent (n=384) nu a fost încă re-analizat cu o variabilă de scară — aceasta este exact ceea ce candidatul propune, dar nu a fost făcută. |

## 5. Evaluarea independentă a criticilor Red Team

**Confirm:**
- **C3 (Alternative Explanation)** — confuzia scale/liquiditate este reală și verificabilă direct: ambele instanțe micro-C ocupă exact fereastra de lichiditate redusă (Asia thin tape) deja documentată în laborator ca trough al profilului orar de volatilitate (~4.3× peak/trough). La n=2, cele două variabile (scară mică, lichiditate scăzută) nu variază independent în eșantion — sunt perfect confundate.
- **Evaluarea Red Team** că acesta este cel mai ieftin test din portofoliu pentru că se bazează pe un dataset deja existent (OBS-0017, n=384), nu pe colectare nouă — confirmat: falsifier-ul propus ("re-run OBS-0017 with scale separation") nu necesită date noi de piață, doar o re-analiză a unui rezultat deja înregistrat.
- **F8/O2** (DC-0002 este cazul special HTF al DC-0003) — confirmat direct din textul candidatului: "The HTF-C half of this candidate is DC-0002's subject."

**Infirm parțial / extind:**
- Afirmația Red Team că "rezultatul negativ [al re-testării] este unambiguous" este acceptată doar condiționat: este adevărată NUMAI dacă separarea de scală introdusă în re-analiză este ea însăși predefinită înainte de a vedea rezultatele (pre-înregistrată), nu aleasă post-hoc pe același set de 384 pentru a maximiza separarea. Red Team nu semnalează explicit acest risc de "alegere de prag post-hoc" pentru DC-0003 (deși semnalează un risc structural similar — prag nedefinit — pentru DC-0008 la F3). Extind acest raționament aici ca observație proprie: fără pre-înregistrarea metodei de determinare a pragului/multiplului ATR, orice rezultat "pozitiv" obținut prin căutarea pragului care separă cel mai bine datele ar fi o formă de data snooping asupra celor 384 evenimente deja existente.

**Rămâne nedeterminat:**
- Dacă granița scale/HTF este o schimbare reală de regim (discontinuă) sau o funcție continuă a raportului range/ATR — Red Team nu discută explicit această posibilitate pentru DC-0003 (se concentrează pe costul redus al testului, nu pe forma funcțională a relației).

## 6. Cel mai puternic argument împotriva ipotezei

Confuzia scale-lichiditate: ambele cazuri micro-C au avut loc în aceeași fereastră de lichiditate redusă. Efectul observat (spargere marginală care eșuează) ar putea fi pur și simplu semnătura lichidității scăzute — spread-uri mai mari și execuție zgomotoasă produc "false breaks" indiferent de raportul range-coil/ATR — nu o proprietate de "scară" în sensul propus de candidat. La n=2, nu există nicio variație în eșantion care să separe cele două explicații; ele sunt indistinguibile din datele prezentate.

## 7. Cea mai puternică explicație alternativă

Explicația de lichiditate (deja numită de Alpha) este cea mai puternică alternativă: în regimul de lichiditate scăzută (trough-ul profilului orar de volatilitate, deja primitiv promovat în lab), orice graniță de preț îngustă poate fi depășită marginal prin zgomot de execuție/spread, independent de raportul dintre range-ul coil-ului și ATR predominant. Sub acest null, separarea "scale" observată în cele 2 instanțe ar fi doar un artefact al faptului că ambele s-au întâmplat să apară în aceeași fereastră orară subțire — testul decisiv trebuie să decupleze explicit cele două variabile.

## 8. Experimentul statistic cu puterea maximă de discriminare

Re-analiza directă a OBS-0017 (n=384 swing-high exceedances existente), NU o colectare nouă:

1. Pentru fiecare din cele 384 evenimente, se calculează o variabilă **continuă** de scară: `scale_ratio = range pre-spargere ÷ ATR local la momentul evenimentului` — nu o dihotomie fixă a priori.
2. Se modelează `outcome_spargere (continuare vs. eșec) ~ scale_ratio + regim_lichiditate + scale_ratio:regim_lichiditate`, cu termenul de interacțiune inclus explicit pentru a decupla scale de lichiditate — adresând direct §6-7.
3. Se testează dacă relația scale_ratio→outcome este semnificativă și dacă este monotonă/continuă sau are un punct de cotitură real (detectare changepoint / spline neliniar), analog logicii dip-test/GMM folosite pentru DC-0008, dar aplicată aici unei variabile de intrare continue, nu unei distribuții bimodale a expunerii.
4. Dacă efectul principal supraviețuiește controlului pentru lichiditate, pragul de separare (dacă unul real există) se derivă din date (ex. punctul de schimbare din modelul changepoint), nu se presupune din Additional Notes.

Acest design maximizează puterea de discriminare pentru că: (a) folosește un eșantion deja existent, cu ordine de mărime mai mare (n=384) decât cele 2 instanțe originale; (b) decuplează explicit scale de lichiditate, testul central pe care nici candidatul, nici Red Team nu l-au rulat; (c) nu presupune o dihotomie fixă, testând simultan dacă separarea e reală sau doar un continuum.

## 9. Datele necesare

- Setul OBS-0017 (384 swing-high exceedances) cu variabilele lui brute per eveniment — range pre-spargere, volum, rezultat (continuare/eșec) — nu doar concluzia agregată (CI spans 0).
- ATR local (sau altă măsură de amplitudine de zgomot) la momentul fiecărui eveniment, calculat strict din date anterioare evenimentului (fără leakage din viitor); dacă nu există deja în OBS-0017, trebuie reconstruit din seria de bare subiacentă.
- O variabilă de regim de lichiditate/sesiune per eveniment (oră UTC, sesiune Asia/Londra/NY) pentru termenul de interacțiune.

## 10. Dimensiunea minimă a eșantionului / metoda de estimare

Avantaj specific acestui candidat: eșantionul de testare (n=384) **există deja** și depășește confortabil pragurile tipice pentru un test de regresie/interacțiune cu putere rezonabilă pentru un efect de mărime moderată. Totuși, puterea reală depinde de câte din cele 384 evenimente cad efectiv în coada "scale mic" a distribuției (unde ipoteza prezice cel mai mult) — dacă distribuția lui scale_ratio e puternic dezechilibrată, sub-eșantionul relevant poate fi mult sub 384. Recomand o analiză de putere calculată pe distribuția reală a lui scale_ratio în cele 384 evenimente (nu presupusă), înainte de a interpreta orice rezultat nesemnificativ ca infirmare a ipotezei.

## 11. Testele statistice recomandate

**(a) Regresie/interacțiune:** `outcome ~ scale_ratio + regim_lichiditate + scale_ratio:regim_lichiditate` (logistică dacă outcome e binar, sau model liniar/ordinal dacă outcome e continuu).

**(b) Detectare changepoint/spline neliniar** pe `scale_ratio`, pentru a distinge un prag real de o relație continuă.

**(c) Sensibilitate la definiții:** re-rulare cu ATR calculat pe ferestre alternative (14/20/50 bare) și range pre-spargere măsurat pe orizonturi diferite (5/10 candele) — analiză de tip multiverse.

**(d) Testări multiple:** rezultatul acestui test este direct relevant și pentru DC-0002 (F8/O2 — DC-0002 e cazul special HTF al DC-0003); orice concluzie raportată simultan pentru ambii candidați trebuie corectată family-wise.

**(e) Temporal leakage:** ATR și scale_ratio calculate exclusiv din date anterioare momentului spargerii; orizontul de rezultat (outcome) pre-înregistrat și strict posterior evenimentului.

**(f) Outcome leakage:** trebuie confirmat dacă cele 384 evenimente din OBS-0017 au fost selectate printr-un scan sistematic (criteriu fix) sau discreționar — dacă selecția a fost condiționată în vreun fel de rezultatul cunoscut, riscul de leakage rămâne deschis; acest lucru nu poate fi verificat din artefactele oficiale primite (DC-0003 + Red Team) și trebuie clarificat înainte de a trata rezultatul re-analizei ca fiind curat.

**(g) Robustețe pe regimuri/perioade:** stratificare pe sesiune (Asia/Londra/NY) ca test central pentru decuplarea scale-lichiditate; replicare pe subperioade temporale disjuncte în cadrul celor 384 evenimente.

## 12. Criteriile preînregistrate de succes și eșec

- **Succes (candidat pentru validare condiționată):** relația `scale_ratio → outcome` este semnificativă, de sens constant (scale mai mic → rată de eșec a spargerii mai mare), **supraviețuiește** termenului de interacțiune cu regimul de lichiditate, și este stabilă la definiții alternative de ATR/fereastră și pe subperioade.
- **Eșec (STATISTICALLY REJECTED):** relația nu este semnificativă pe cele 384 evenimente (nulul OBS-0017 nu se descompune prin separare de scală — exact falsifier-ul propriu al candidatului) SAU efectul dispare după controlul pentru lichiditate (confirmând explicația alternativă de la §6-7 ca fiind cauza reală, nu scara).
- **Indeterminat:** numărul de evenimente cu adevărat "micro-scale" (coada distribuției) este prea mic pentru putere adecvată, sau rezultatele sunt instabile la definiții alternative de ATR/fereastră.

## 13. Verdictul final

**READY FOR STATISTICAL VALIDATION.**

Motivare independentă: partea de expunere (`scale_ratio` = range pre-spargere ÷ ATR) este complet operaționalizabilă din date brute, fără judecăți discreționare noi. Spre deosebire de multe alte candidate din portofoliu, acesta beneficiază de un dataset **deja existent** (OBS-0017, n=384) care poate fi re-analizat direct, fără o campanie nouă de colectare — motivul pentru care Red Team îl consideră "high-value, low-cost." Ajung la aceeași concluzie practică prin criterii proprii, nu prin deferență, cu o condiție suplimentară pe care Red Team nu a impus-o explicit (§5, §8): testul **trebuie** să includă termenul de interacțiune scale×lichiditate și pragul de separare (dacă există) trebuie derivat din date, nu ales post-hoc pentru a maximiza separarea — altfel rezultatul rămâne confundat exact cum sunt cele 2 instanțe originale.

Acest verdict nu este o confirmare a ipotezei — eșantionul original (n=2 micro-C) rămâne insuficient în sine; validitatea depinde integral de re-analiza celor 384 evenimente existente, care nu a fost încă efectuată.

## 14. Recomandarea pentru pasul următor

1. Nu executa încă re-rularea OBS-0017 — necesită autorizare CEO separată pentru Faza 2, chiar dacă este o re-analiză a unui rezultat deja existent în laborator, nu date noi de piață.
2. Recomand CEO să autorizeze Faza 2: re-analiza OBS-0017 cu variabila continuă `scale_ratio` + termen de interacțiune cu regimul de lichiditate, conform designului de la §8/§11, inclusiv confirmarea prealabilă a metodei de selecție a celor 384 evenimente (§11f).
3. Notă de secvențiere: rezultatul acestui test este direct relevant pentru DC-0002 (F8: DC-0002 e cazul special HTF al DC-0003) — dacă și când DC-0002 intră în Faza 1 separat, sau așteaptă rezultatul acestei re-analize, rămâne o decizie a CEO.

---

**Statistician nu a modificat DC-0003, raportul/review-ul Red Team, Knowledge Base, artefactele Alpha, sau clasificările/confidence existente.**

**Statistician se oprește aici și așteaptă aprobarea CEO înainte de următorul candidat.**
