# FLOW C — FAZA 0: AUDIT DE CONSISTENȚĂ ȘI SUPRAPUNERE
### Verificarea că cele 8 output-uri au fiecare o misiune irepetabilă
**Status:** AUDIT — în așteptarea deciziei CEO (APPROVED / REQUIRES REFINEMENT)
**Nu redesenează misiunea. Nu creează tipuri noi. Nu atinge Flow A / Flow B.**

---

## STRUCTURA DESCOPERITĂ: patru perechi de vecini

Analiza de proximitate arată că cele 8 output-uri se grupează natural în **patru perechi mutuale**, fiecare pereche împărțind o „aer de familie" dar diferind pe **o singură axă**:

| Pereche | Axa care le separă |
|---|---|
| Research Report ↔ Meta Analysis | narare pe UN corpus vs. corelație PESTE axe |
| Hypothesis Report ↔ Candidate Experiment | ideea (de ce) vs. cererea de test (ce se rulează) |
| Anomaly Report ↔ Research Question | conflict între rezultate EXISTENTE vs. golul unde nu există rezultat |
| Strategy Diagnostic ↔ Regime Analysis | obiect = strategia (agentul) vs. obiect = regimul (mediul) |

Auditul de mai jos tratează fiecare output pe 7 puncte și îl confruntă cu vecinul lui cel mai apropiat.

---

## 1. RESEARCH REPORT

1. **Misiune unică:** narează, descriptiv, ce se vede peste UN corpus de rezultate, înainte ca observațiile să fie clasificate în ceva mai specific.
2. **Întrebarea exactă:** „Ce am văzut în acest corp de rezultate?"
3. **Are voie să conțină:** observații, informații, regularități observaționale pe un singur corpus/batch; trimiteri către output-uri specializate pe care le naște.
4. **Nu are voie să conțină:** corelații între axe independente (aia e Meta Analysis); mecanisme cauzale afirmate ca ipoteză de sine stătătoare (alea pleacă în Hypothesis Report); verdicte.
5. **Vecin cel mai apropiat:** Meta Analysis.
6. **De ce NU sunt duplicate:** Research Report este **descriptiv și mono-lentilă** („ce e în batch-ul ăsta"). Meta Analysis este **relațional și multi-axă** („ce ține peste TOATE axele și unde sursele nu sunt de acord"). Unul relatează, celălalt corelează.
7. **Când îl creezi pe ăsta, nu pe vecin:** a sosit batch-ul S21; vrei prima trecere descriptivă peste rezultatele lui, izolat → Research Report. (Dacă ai compara S21 cu S1–S20 → Meta Analysis.)

---

## 2. HYPOTHESIS REPORT

1. **Misiune unică:** formulează un mecanism cauzal falsificabil care explică un tipar observat — ideea, cu „de ce"-ul ei.
2. **Întrebarea exactă:** „De ce se întâmplă acest tipar?"
3. **Are voie să conțină:** enunțul ipotezei, mecanismul candidat, dovada observațională, predicții, testul de falsificare, alternative neexcluse.
4. **Nu are voie să conțină:** specificația operațională a testului (fereastră, criteriu de succes, cod) — aia e Candidate Experiment; și niciun verdict.
5. **Vecin cel mai apropiat:** Candidate Experiment.
6. **De ce NU sunt duplicate:** Hypothesis Report este un **obiect de cunoaștere** (produce înțelegere nouă: mecanismul). Candidate Experiment este un **obiect de cerere** (nu produce cunoaștere; împachetează o ipoteză existentă ca test). Un Hypothesis Report poate genera zero, unul sau mai multe Candidate Experiments.
7. **Când îl creezi pe ăsta, nu pe vecin:** tocmai ai înțeles *de ce* câștigătorii împart filtrul X și vrei să consemnezi mecanismul → Hypothesis Report. (Cererea concretă de test vine abia după.)

---

## 3. ANOMALY REPORT

1. **Misiune unică:** consemnează un conflict între două rezultate care nu ar trebui să coexiste, dar coexistă.
2. **Întrebarea exactă:** „De ce se contrazic aceste două rezultate reale?"
3. **Are voie să conțină:** cele două fapte în conflict (ambele cu sursă), presupunerea tăcută afectată, verdictul preliminar piață-vs-artefact.
4. **Nu are voie să conțină:** explicația cauzală completă (aia devine Hypothesis Report); o întrebare fără rezultate de ambele părți (aia e Research Question).
5. **Vecin cel mai apropiat:** Research Question.
6. **De ce NU sunt duplicate:** Anomaly Report are **date pe ambele părți** — arată către un conflict în ce AVEM. Research Question arată către un **gol** — către ce NU avem, ce nu s-a testat niciodată. Anomalia e o coliziune; întrebarea e o absență.
7. **Când îl creezi pe ăsta, nu pe vecin:** S6 e profitabil în low-vol dar același mecanism pierde în S11 în aceeași condiție → ai două rezultate care se ciocnesc → Anomaly Report. (Dacă nimeni nu a testat vreodată condiția → Research Question.)

---

## 4. STRATEGY DIAGNOSTIC

1. **Misiune unică:** citește ce ne *învață* comportamentul unei strategii/familii — sănătate de ordinul doi, nu scorul.
2. **Întrebarea exactă:** „Ce ne spune această strategie despre celelalte?"
3. **Are voie să conțină:** comportament observat (citit de la Strategy Health), ce împarte cu câștigătorii/perdanții, semne premergătoare de degradare, lecția transferabilă.
4. **Nu are voie să conțină:** scoruri recalculate sau propuse; modificări de parametri; concluzii despre regimul de piață ca atare (aia e Regime Analysis).
5. **Vecin cel mai apropiat:** Regime Analysis.
6. **De ce NU sunt duplicate:** Strategy Diagnostic este **centrat pe agent** — subiectul e o strategie (un ID). Regime Analysis este **centrat pe mediu** — subiectul e o condiție de piață. Unul întreabă „ce e cu acest jucător", celălalt „ce e cu acest teren".
7. **Când îl creezi pe ăsta, nu pe vecin:** strategia S8 se degradează și vrei să vezi ce a precedat degradarea și dacă lecția se transferă la S9 → Strategy Diagnostic. (Dacă degradarea apare la TOATE strategiile într-o anumită condiție de piață → Regime Analysis.)

---

## 5. REGIME ANALYSIS

1. **Misiune unică:** propune existența unei condiții de piață (regim) — inclusiv una nouă — care explică gruparea rezultatelor.
2. **Întrebarea exactă:** „Există o stare de piață care structurează ce merge și ce nu?"
3. **Are voie să conțină:** regimul propus, semnătura lui observațională, ce se schimbă înăuntrul lui, dacă e nou vs. cunoscut, testul de falsificare.
4. **Nu are voie să conțină:** diagnostic al unei singure strategii (Strategy Diagnostic); afirmarea regimului ca fapt validat.
5. **Vecin cel mai apropiat:** Strategy Diagnostic.
6. **De ce NU sunt duplicate:** vezi §4.6 — mediu vs. agent. În plus, Regime Analysis urcă până la **ipoteză** (un regim propus e o ipoteză), pe când Strategy Diagnostic rămâne la cunoaștere-observațională despre un obiect concret.
7. **Când îl creezi pe ăsta, nu pe vecin:** observi că zeci de strategii diferite câștigă/pierd simultan la aceeași frontieră de volatilitate → sugerează un regim → Regime Analysis. (Dacă e o singură strategie care se comportă ciudat → Strategy Diagnostic.)

---

## 6. META ANALYSIS

1. **Misiune unică:** găsește ce e sistematic adevărat corelând PESTE axe (familii / regimuri / timeframe / A-vs-B) — mai ales divergențe backtest-vs-live.
2. **Întrebarea exactă:** „Ce ține transversal peste tot, și unde nu sunt de acord sursele?"
3. **Are voie să conțină:** axa de corelație, tiparul transversal, divergențele, explicația unificatoare candidată, ce unknown-unknown deschide.
4. **Nu are voie să conțină:** narare a unui singur corpus fără corelație cross-axă (Research Report); mecanism dezvoltat pe larg ca ipoteză de sine stătătoare (Hypothesis Report — Meta Analysis doar îl *semnalează*).
5. **Vecin cel mai apropiat:** Research Report.
6. **De ce NU sunt duplicate:** vezi §1.6 — relațional/multi-axă vs. descriptiv/mono-corpus. Meta Analysis nu poate exista fără cel puțin două axe puse în relație; Research Report nu are voie să pună axe în relație.
7. **Când îl creezi pe ăsta, nu pe vecin:** vrei să vezi dacă filtrul X ține atât în backtest cât și în shadow-live, peste 3 timeframe-uri → Meta Analysis. (O singură trecere peste un batch → Research Report.)

---

## 7. RESEARCH QUESTION

1. **Misiune unică:** pune o întrebare bine formulată pe care nicio ipoteză curentă nu o pune — teritoriul unknown-unknowns.
2. **Întrebarea exactă:** „Ce nu știm nici măcar să ne întrebăm?"
3. **Are voie să conțină:** întrebarea (o propoziție), de ce era invizibilă, ce a scos-o la suprafață (absență / variabilă ignorată / contradicție tăcută), de ce contează, starea OPEN.
4. **Nu are voie să conțină:** o ipoteză (dacă ai deja un mecanism candidat, e Hypothesis Report); un conflict între rezultate existente (Anomaly Report).
5. **Vecin cel mai apropiat:** Anomaly Report.
6. **De ce NU sunt duplicate:** vezi §3.6 — gol vs. coliziune. Research Question nu poate cita două rezultate în conflict (dacă poate, e Anomaly); ea arată exact spre ce lipsește.
7. **Când îl creezi pe ăsta, nu pe vecin:** realizezi că nicio familie nu a folosit vreodată ora-din-zi ca axă, deși datele o conțin → nu ai rezultate de comparat, ai un gol → Research Question.

---

## 8. CANDIDATE EXPERIMENT

1. **Misiune unică:** este SINGURUL artefact care traversează formal granița de guvernanță și cere lui Alpha Discovery un test — spune CE se rulează și cum se judecă, niciodată CUM se implementează.
2. **Întrebarea exactă:** „Ce test concret ar decide această ipoteză?"
3. **Are voie să conțină:** link la ipoteza-sursă, ce de testat, criteriul de succes, date sugerate, riscuri de artefact, predarea.
4. **Nu are voie să conțină:** re-expunerea mecanismului (ăla trăiește în Hypothesis Report); cod de test; orice drept de follow-up asupra deciziei lui A.
5. **Vecin cel mai apropiat:** Hypothesis Report.
6. **De ce NU sunt duplicate:** Hypothesis Report **produce cunoaștere** (mecanismul). Candidate Experiment **nu produce cunoaștere deloc** — este pur logistică: transformă o ipoteză deja formulată într-o cerere operațională de test. Este singurul output cu funcție de guvernanță (cererea formală de experiment), nu de cunoaștere.
7. **Când îl creezi pe ăsta, nu pe vecin:** ai deja Hypothesis Report RI-HYP-0007 și vrei să-i ceri lui Alpha Discovery să-l testeze, cu un criteriu de succes clar → Candidate Experiment. (Cât timp încă lămurești *de ce*, rămâi în Hypothesis Report.)

---

## MATRICEA FINALĂ DE COMPARAȚIE

| Output | Scop primar | Trigger | Dovadă cerută | Nivel epistemic | Consumator final | Poate genera ipoteză? | Poate cere experiment A? | Poate deveni input de implementare? | Risc de duplicat |
|---|---|---|---|---|---|---|---|---|---|
| **Research Report** | Narare descriptivă a unui corpus | Batch nou / trecere periodică | Un corpus/batch real | obs. → cunoaștere-obs. | Intern / CEO | Da (naște HR) | Nu | Nu (doar via A) | **Mediu** (vs. Meta) |
| **Hypothesis Report** | Mecanism cauzal falsificabil | O regularitate cere un „de ce" | Tiparul observat + sursă | ipoteză | Alpha Discovery | Da (ESTE una) | Indirect (via CE) | Nu (doar via A) | **Mediu** (vs. CE) |
| **Anomaly Report** | Conflict între rezultate | Două rezultate se ciocnesc | Ambele fapte, cu sursă | informație | Intern / A | Nu (motivează una) | Nu | Nu (doar via A) | Scăzut (vs. RQ) |
| **Strategy Diagnostic** | Ce ne învață o strategie | Degradare / comportament atipic | Valori de la Strategy Health | inf. → cunoaștere-obs. | Intern / CEO | Da | Nu | Nu (doar via A) | Scăzut (vs. RA) |
| **Regime Analysis** | Propune un regim de piață | Rezultate grupate pe o condiție | Clusterul de rezultate | ipoteză | Alpha Discovery | Da (regim=ipoteză) | Indirect (via CE) | Nu (doar via A) | Scăzut (vs. SD) |
| **Meta Analysis** | Corelație cross-axă | Întrebare peste ≥2 axe | ≥2 axe puse în relație | cunoaștere-obs. → ipoteză | Intern / A / CEO | Da | Indirect (via CE) | Nu (doar via A) | **Mediu** (vs. RR) |
| **Research Question** | Întrebare neformulată (unknown-unknown) | Un gol devine vizibil | Absența/variabila ignorată, cu sursă | — (întrebare) | Open Research Questions | Nu | Nu | Nu (doar via A) | Scăzut (vs. AR) |
| **Candidate Experiment** | Cerere formală de test | O ipoteză e coaptă de testat | Link la HR-sursă | ipoteză (transportată) | Alpha Discovery | Nu (poartă una) | **Da (direct)** | Nu (doar via A) | **Ridicat** (vs. HR) |

**Invariant confirmat:** coloana „input de implementare" = **Nu** la toate 8. Niciun output nu devine acțiune direct; traseul rămâne RI → Alpha Discovery → Validare → CEO Approval → AI Trader.

---

## ÎNTREBAREA FINALĂ: care dispare cu cea mai mică pierdere de capabilitate?

> **Răspuns: Candidate Experiment.**

**Justificare.**

Din cele 8, **Candidate Experiment este singurul care nu produce cunoaștere nouă.** Toate celelalte șapte generează cel puțin o observație, o informație, o ipoteză sau o întrebare — un increment epistemic. Candidate Experiment nu adaugă nimic la înțelegere: **împachetează o ipoteză deja formulată în Hypothesis Report** într-o cerere operațională. Este logistică de handoff, nu producție de cunoaștere.

Iar Hypothesis Report **conține deja** un câmp de handoff și un test de falsificare propus. Cele trei elemente cu adevărat proprii ale Candidate Experiment — criteriul de succes, datele sugerate, riscurile de artefact — pot fi absorbite în acel câmp de handoff al HR fără pierdere de capabilitate **analitică**.

**Pierderea reală, care trebuie recunoscută onest:** Candidate Experiment este totuși singurul artefact cu o funcție de **guvernanță** proprie — cererea formală, cu graniță curată de predare, care traversează spre Alpha Discovery. Dacă dispare, această funcție trebuie re-găzduită explicit în câmpul de handoff al Hypothesis Report, iar disciplina „mă opresc aici" devine o regulă, nu un document.

Deci: dispariția lui costă **cea mai mică capabilitate de cunoaștere** (zero — nu produce cunoaștere), dar o capabilitate reală de **guvernanță** (cererea formală de experiment). Tocmai această asimetrie dictează recomandarea de mai jos.

---

## RECOMANDARE

> ## PHASE 0 REQUIRES REFINEMENT
> (rafinare chirurgicală, minimă — nu redesign)

Auditul confirmă că **șase din opt** output-uri au risc de duplicat scăzut și misiuni clar irepetabile. Dar bara pusă de CEO — *„fiecare tip trebuie să aibă un scop care nu poate fi îndeplinit de niciun altul"* — nu e încă atinsă în două locuri:

**Rafinarea 1 (obligatorie) — granița Hypothesis Report ↔ Candidate Experiment.**
Candidate Experiment produce zero cunoaștere și se suprapune peste câmpul de handoff al HR (risc: RIDICAT). Pentru a-i da un scop irepetabil, propun regula:
- **Hypothesis Report = cunoaștere (DE CE).** Nu conține criteriu de succes operațional, fereastră de date sau plan de test.
- **Candidate Experiment = cerere (CE se rulează + cum se judecă).** NU re-expune mecanismul; îl referențiază prin link. Este definit ca **singurul artefact de graniță** care poate cere direct un experiment.
- Cu această tăietură, cele două nu mai pot fi confundate: unul e obiect de cunoaștere, celălalt e obiect de cerere, și fiecare pierde câmpurile celuilalt.

**Rafinarea 2 (recomandată) — granița Research Report ↔ Meta Analysis.**
Adaug o singură regulă în ambele șabloane:
- **Research Report nu are voie să coreleze axe independente.** În momentul în care pui două axe în relație (familii × regimuri, backtest × live), documentul devine automat Meta Analysis. Un cuvânt de graniță elimină riscul mediu de duplicat.

Ambele rafinări sunt **doar reguli de delimitare adăugate în șabloanele existente** — nu tipuri noi, nu redesign, nu ating misiunea. Le pot aplica în `PHASE_0_OUTPUT_FORMATS.md` imediat ce le aprobi, apoi îngheț formatele.

*Aștept decizia CEO: aprob rafinările propuse (și îngheț), sau ceri altă delimitare?*
