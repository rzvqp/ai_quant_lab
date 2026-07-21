# FLOW C — FAZA 0: FORMATELE STANDARD DE OUTPUT
### Specificație de format pentru cele 8 tipuri de output ale Research Intelligence
**Status:** ✅ PHASE 0 v1.0 — ÎNGHEȚAT (FROZEN) prin decizie CEO, 2026-07-21
**Bazat pe:** `MISSION_OF_RESEARCH_INTELLIGENCE.md` v1.0 (FROZEN)
**Rafinări aprobate integrate:** RR strict descriptiv (fără cross-axă) · HR = cunoaștere (fără experiment) · CE = cerere/guvernanță (fără mecanism). Vezi `PHASE_0_CONSISTENCY_AUDIT.md`.
**Nimic implementat. Niciun cod. Doar șabloane de document.**

> Formatele sunt congelate. Orice modificare ulterioară cere o nouă decizie CEO explicită și un bump de versiune.

---

## SCOPUL FAZEI 0

Înainte ca Flow C să producă orice output real (Faza 1), fixăm **forma** fiecărui tip de output. Un format standard garantează că fiecare produs Flow C:

- este **trasabil** la rezultate reale (interzice fabricarea),
- își declară **nivelul epistemic** (observație / informație / cunoaștere observațională / ipoteză) și **nu revendică niciodată validare**,
- spune explicit **ce l-ar falsifica** și **cât de sigur** este,
- se predă curat mai departe pe traseul de guvernanță când e cazul.

---

## ENVELOPE COMUN (obligatoriu la TOATE cele 8)

Orice output Flow C începe cu același antet. Fără el, documentul nu e valid.

```
─────────────────────────────────────────────
FLOW C — {TIP OUTPUT}
ID:              RI-{TIP}-{NNNN}
Data:            {YYYY-MM-DD}
Autor:           Research Intelligence
Nivel epistemic: [observație | informație | cunoaștere-observațională | ipoteză]
Încredere:       [scăzută | medie | ridicată]  + o frază de justificare
─────────────────────────────────────────────
BAZA DE DOVEZI (Evidence base) — OBLIGATORIU
  • Sursă:      {ce rezultate reale au fost observate — batch, familie, run-id, fișier}
  • Fereastră:  {ce interval / ce contexte acoperă}
  • NON-fabricare: confirm că fiecare afirmație de mai jos derivă din date reale produse.
─────────────────────────────────────────────
CE AR FALSIFICA ACEST OUTPUT:
  {condiția observabilă care ar demonta afirmația}
PLAFON EPISTEMIC:
  Acest document NU validează nimic. Validarea aparține exclusiv Alpha Discovery.
─────────────────────────────────────────────
```

**Regula de aur a envelope-ului:** dacă un câmp „Baza de dovezi" nu poate fi completat cu o sursă reală, output-ul nu se produce. Fără dovadă → fără document.

---

## 1. RESEARCH REPORT
**Întrebarea pe care o pune:** „Ce am văzut în acest corp de rezultate?"
**Rol:** nararea structurată, **descriptivă**, a ce s-a observat peste UN corpus de rezultate. Documentul „umbrelă" — cel mai general.
**Se produce când:** apare un batch nou de la Flow A, sau la o trecere periodică peste rezultatele existente.
**Nivel epistemic maxim:** cunoaștere-observațională.

```
1. Întrebarea de plecare        (ce am privit și de ce)
2. Corpul de dovezi             (ce rezultate, câte, ce fereastră — UN singur corpus)
3. Observații                   (fapte brute, listate, fiecare cu sursă)
4. Informații                   (observațiile puse în context, în interiorul aceluiași corpus)
5. Regularități găsite          (ce ține repetabil — cunoaștere observațională)
6. Ce NU explică raportul       (limite, zone neatinse)
7. Trimiteri                    (ce Hypothesis Reports / Research Questions nasc de aici)
```

> **REGULĂ DE GRANIȚĂ (CEO, rafinare aprobată) — descriptiv, niciodată corelativ.**
> Research Report rămâne **strict descriptiv**. NU are voie să coreleze axe independente (familii × regimuri, backtest × live, timeframe × timeframe). **În momentul în care apare raționament cross-axă, documentul NU mai este Research Report — devine Meta Analysis (§6).** Câmpul „Informații" (4) contextualizează doar în interiorul aceluiași corpus, nu între axe.

---

## 2. HYPOTHESIS REPORT
**Întrebarea pe care o pune:** „Ce credem că se întâmplă — și de ce?"
**Rol:** obiectul de cunoaștere al Flow C. O ipoteză cauzală falsificabilă + dovada care a motivat-o. Descrie mecanismul, **nu** experimentul.
**Se produce când:** o regularitate observată sugerează un **mecanism candidat**.
**Nivel epistemic maxim:** ipoteză. (Se oprește exact aici — vezi plafonul din misiune.)

```
1. Enunțul ipotezei             (o singură frază falsificabilă: „X se întâmplă PENTRU CĂ Y")
2. Mecanism candidat            (de ce, nu doar ce — cauza propusă)
3. Dovada observațională        (tiparul din rezultate care a motivat-o + sursă)
4. Predicții                    (dacă ipoteza e adevărată, ce ar trebui să vedem în alt loc)
5. Condiție de falsificare      (CONCEPTUAL: ce observație ar demola ipoteza — NU un plan de test)
6. Alternative neexcluse        (ce alte explicații rămân pe masă)
7. Semnal de handoff            (doar: „această ipoteză merită un Candidate Experiment: da/nu")
```

> **REGULĂ DE GRANIȚĂ (CEO, rafinare aprobată) — cunoaștere, nu experiment.**
> Hypothesis Report descrie **„ce credem că se întâmplă?"**. NU are voie să definească experimentul: **fără criteriu de succes operațional, fără fereastră de date, fără plan de test.** Câmpul 5 este o condiție de falsificare *conceptuală* (ce ar contrazice ideea), nu un protocol. Câmpul 7 doar semnalează dacă merită un Candidate Experiment — nu îl scrie. Proiectarea testului aparține exclusiv §8 + Alpha Discovery.

---

## 3. ANOMALY REPORT
**Rol:** semnalează un rezultat care contrazice așteptarea sau alt rezultat. Materia primă a mecanismelor și a unknown-unknowns.
**Se produce când:** două rezultate nu ar trebui să coexiste, dar coexistă — sau un rezultat sfidează o presupunere implicită.
**Nivel epistemic maxim:** informație (anomalia e un fapt contextualizat; explicația ei devine un Hypothesis Report separat).

```
1. Anomalia                     (ce se abate și de la ce așteptare)
2. Cele două fapte în conflict  (A vs. B, ambele cu sursă)
3. Presupunerea tăcută afectată (ce credeam implicit și e pusă la îndoială)
4. Piață sau metodă?            (semnal real de piață vs. artefact al metodei — sau nedecis)
5. Ce ar rezolva anomalia       (ce ar trebui privit ca s-o înțelegem)
```
> §4 este obligatoriu: distincția piață-vs-artefact e muncă centrală de Flow C (precedent: artefactul de expectancy la stop-uri mici).

---

## 4. STRATEGY DIAGNOSTIC
**Rol:** citirea de sănătate-de-ordinul-doi a unei strategii/familii — nu scorul ei (ăla e al Strategy Health), ci *ce ne învață* comportamentul ei.
**Se produce când:** o strategie se degradează, se comportă atipic, sau e reprezentativă pentru o clasă.
**Nivel epistemic maxim:** informație → cunoaștere-observațională.

```
1. Subiect                      (strategia/familia + ID)
2. Comportament observat        (expectancy, drawdown, degradare — citite, nu recalculate)
3. Ce o face diferită           (ce împarte cu câștigătorii / perdanții)
4. Semne premergătoare          (dacă s-a degradat: ce a precedat degradarea)
5. Lecția transferabilă         (ce spune asta despre ALTE strategii)
```
> Interdicție: Strategy Diagnostic CITEȘTE valorile de la Strategy Health. Nu le recalculează, nu le modifică, nu propune scoruri noi.

---

## 5. REGIME ANALYSIS
**Rol:** ipoteze despre regimuri de piață — inclusiv regimuri **noi, neidentificate încă**.
**Se produce când:** rezultatele se grupează într-un mod care sugerează un regim latent.
**Nivel epistemic maxim:** ipoteză (un regim propus e o ipoteză până Flow A îl validează).

```
1. Regimul propus               (ce condiție de piață pare să definească un cluster)
2. Semnătura observațională     (cum se recunoaște în rezultate)
3. Ce se schimbă în interiorul lui (ce strategii merg/nu merg în acest regim)
4. Este nou?                    (regim deja cunoscut vs. candidat de regim nou)
5. Test de falsificare          (ce ar arăta că regimul nu există / e artefact)
```

---

## 6. META ANALYSIS
**Rol:** corelații cross-strategie / cross-regim / cross-timeframe / cross-flow. Aici apar cele mai valoroase ipoteze (divergențe backtest-vs-live).
**Se produce când:** întrebarea depășește o singură strategie sau un singur flux.
**Nivel epistemic maxim:** cunoaștere-observațională → ipoteză.

```
1. Axa de corelație             (peste ce se face agregarea: familii / regimuri / TF / A-vs-B)
2. Tiparul transversal          (ce e sistematic adevărat peste toate)
3. Divergențe                   (unde backtest ≠ live / unde fluxurile nu sunt de acord)
4. Explicație unificatoare candidată (mecanismul care ar lega totul — dacă există)
5. Ce unknown-unknown deschide  (ce întrebare nouă naște — leagă la §6.1 din misiune)
```

---

## 7. RESEARCH QUESTION
**Rol:** o întrebare bine pusă, încă fără ipoteză. Cea mai pură formă de „descoperire Flow C" (o întrebare mai bună / un unknown-unknown).
**Se produce când:** privind corpul întreg de rezultate, apare o întrebare pe care nicio ipoteză curentă nu o pune.
**Nivel epistemic maxim:** — (o întrebare nu are nivel de afirmație; nu revendică nimic).

```
1. Întrebarea                   (o singură propoziție, cât mai precisă)
2. De ce nu era pusă până acum  (ce a făcut-o invizibilă)
3. Ce a scos-o la suprafață     (absență / variabilă ignorată / contradicție tăcută — cu sursă)
4. De ce contează              (ce s-ar schimba în cercetare dacă am răspunde)
5. Stare                        (OPEN — nu se auto-promovează în RQ oficial; alimentează directiva Open Research Questions)
```
> Aliniat directivei existente: întrebările rămân OPEN; Flow C nu le auto-promovează.

---

## 8. CANDIDATE EXPERIMENT
**Întrebarea pe care o pune:** „Cum ar trebui Alpha să testeze această ipoteză?"
**Rol:** artefactul de **guvernanță** — SINGURUL care traversează formal granița către Alpha Discovery și cere un test. Scop primar: predarea formală, nu producția de cunoaștere.
**Se produce când:** o ipoteză (din §2) e coaptă pentru testare de către Flow A.
**Nivel epistemic maxim:** ipoteză (transportată din HR; verdictul e al lui A).

```
1. Ipoteza-sursă                (DOAR link la Hypothesis Report RI-HYP-NNNN — mecanismul trăiește acolo)
2. Ce ar trebui testat          (întrebarea experimentală operațională, nu codul)
3. Criteriu de succes propus    (ce rezultat ar confirma / infirma — la nivel conceptual)
4. Date sugerate                (ce fereastră / instrument ar fi relevant — sugestie, nu comandă)
5. Riscuri de artefact          (capcane metodologice de evitat — ex: rezoluție de fill, look-ahead)
6. PREDARE                      (Flow C se oprește aici. Alpha Discovery decide independent dacă/cum testează.)
```

> **REGULĂ DE GRANIȚĂ (CEO, rafinare aprobată) — cerere, nu cunoaștere.**
> Candidate Experiment descrie **„cum ar trebui Alpha să testeze?"**. NU are voie să **re-expună mecanismul** — acela există doar în Hypothesis Report și e adus aici prin link (câmpul 1). Nu produce cunoaștere nouă; este pură cerere operațională. Interdicție dură: fără cod de test, nu rulează nimic, fără drept de follow-up asupra deciziei lui A.

---

## MATRICE DE SINTEZĂ

| # | Output | Nivel epistemic max | Destinatar principal | Poate deveni acțiune? |
|---|---|---|---|---|
| 1 | Research Report | cunoaștere-observațională | intern Flow C / CEO | nu |
| 2 | Hypothesis Report | ipoteză | Alpha Discovery | nu (doar via A) |
| 3 | Anomaly Report | informație | intern / A | nu |
| 4 | Strategy Diagnostic | cunoaștere-observațională | intern / CEO | nu |
| 5 | Regime Analysis | ipoteză | Alpha Discovery | nu (doar via A) |
| 6 | Meta Analysis | ipoteză | intern / A / CEO | nu |
| 7 | Research Question | — (întrebare) | Open Research Questions | nu |
| 8 | Candidate Experiment | ipoteză | Alpha Discovery | nu (A decide) |

**Invariant peste toate:** ultima coloană e „nu" fără excepție. Niciun output Flow C nu devine acțiune direct — traseul rămâne RI → Alpha Discovery → Validare → CEO Approval → AI Trader.

---

## CONVENȚII DE NUMEROTARE ȘI STOCARE (propunere)

```
flow_c/
  MISSION_OF_RESEARCH_INTELLIGENCE.md      (FROZEN v1.0)
  PHASE_0_OUTPUT_FORMATS.md                (acest document)
  reports/
    RI-REPORT-0001.md
    RI-HYP-0001.md
    RI-ANOM-0001.md
    RI-DIAG-0001.md
    RI-REGIME-0001.md
    RI-META-0001.md
    RI-RQ-0001.md
    RI-EXP-0001.md
  INDEX.md                                 (registru al tuturor output-urilor RI)
```

---

## STARE DE ÎNGHEȚARE

**PHASE 0 v1.0 — FROZEN.** Aprobat de CEO la 2026-07-21, cu cele trei rafinări de graniță integrate (RR↔MA, HR↔CE ×2).

Self-review final de suprapunere — cele patru perechi de vecini:
- **RR ↔ MA:** RR interzis explicit să coreleze cross-axă → devine MA. ✓ separate.
- **HR ↔ CE:** HR = „ce credem că se întâmplă" (mecanism, fără plan de test); CE = „cum testează Alpha" (cerere, fără mecanism, doar link). Seturi de câmpuri disjuncte. ✓ separate.
- **AR ↔ RQ:** AR cere două rezultate reale în conflict; RQ arată spre o absență. ✓ separate.
- **SD ↔ RA:** SD centrat pe agent (strategie); RA centrat pe mediu (regim). ✓ separate.

Nicio suprapunere reziduală. Cele 8 formate au fiecare un scop irepetabil.

Următorul pas autorizat: **Faza 1** — prima observație pasivă peste rezultatele S1–S20 + primul Research Report ca test al formatului. **Necesită autorizare CEO separată înainte de start.**
