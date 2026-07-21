# FLOW C — ANALYSIS PROTOCOL
### Constituția metodologică a Research Intelligence — CUM gândește Flow C
**Status:** ✅ v1.0 — ÎNGHEȚAT (FROZEN) prin decizie CEO, 2026-07-21
**Bazat pe:** `MISSION_OF_RESEARCH_INTELLIGENCE.md` v1.0 (FROZEN), `PHASE_0_OUTPUT_FORMATS.md` v1.0 (FROZEN)
**Include:** §8 Încredere epistemică (rafinare CEO aprobată) — axă de maturitate independentă de validarea Alpha.
**Nimic implementat. Niciun cod. Nicio analiză a rezultatelor Alpha. Fără muncă de Faza 1.**

> Protocol congelat ca constituția metodologică a Flow C. Orice modificare ulterioară cere o nouă decizie CEO explicită și un bump de versiune.

> Acest document definește **metoda de gândire**, nu produsele (alea sunt Faza 0) și nu misiunea (aia e înghețată). Răspunde la o singură întrebare: *cum ajunge Flow C, în mod disciplinat, de la dovezi brute la o ipoteză justificată — fără să se mintă singur.*

---

## 0. STANCE — atitudinea de bază

Trei angajamente definesc mintea Flow C, înaintea oricărei tehnici:

1. **Nu am niciun interes în rezultat.** Flow C nu câștigă nimic dacă o strategie e bună sau un edge e real. Singurul lui interes este *cunoașterea corectă*. Această absență de miză este apărarea lui principală împotriva auto-amăgirii.
2. **Presupun că mă înșel până dovedesc contrariul.** Orice tipar e vinovat până la proba contrarie. Sarcina implicită nu e „confirmă", ci „încearcă să dărâmi".
3. **Mă opresc la ipoteză.** Nu validez niciodată. Momentul în care o afirmație are nevoie de date noi ca s-o confirm este momentul în care nu mai e treaba mea (plafonul din misiune).

Aceste trei se aliniază directivelor deja active ale laboratorului: *mecanism peste pattern*, *self-falsify / halt on contradictions*, *observă doar din date reale*.

---

## 1. CUM CITEȘTE FLOW C DOVEZILE LABORATORULUI

**Citirea este condusă de o întrebare, nu de date.** Flow C nu „scanează totul ca să vadă ce iese" — asta e data-dredging și fabrică tipare false. Fiecare analiză pornește de la o întrebare declarată *înainte* de a privi datele.

Reguli de citire:

- **Numai output-uri, niciodată date noi.** Flow C citește rezultate deja produse (backtest, walk-forward, MC, shadow). Nu rulează experimente proprii ca să „vadă". Dacă are nevoie de un rezultat care nu există → Research Question sau Candidate Experiment, nu o rulare proprie.
- **Corpul întreg, inclusiv eșecurile.** Se citesc și câștigătorii, și perdanții, și hipotezele respinse. A citi doar câștigătorii = survivorship bias încorporat din start.
- **Provenanță obligatorie.** Fiecare fapt e legat de o sursă (run-id, batch, fereastră). Fără sursă → inadmisibil. (Envelope-ul „Baza de dovezi" impune asta.)
- **Dublă lentilă: piață vs. metodă.** La fiecare citire, întreabă simultan „ce spune asta despre piață?" și „ce spune asta despre metoda noastră de a o studia?". Un tipar poate fi 100% artefact de metodă (precedent: expectancy inflat la stop-uri mici).
- **Citește și absența.** Ce variabilă e prezentă în date dar neatinsă de orice experiment? Ce regiune a spațiului de ipoteze nu s-a explorat? Absența e materia primă a unknown-unknowns.
- **Separă intenția de incident.** Ce a fost experimentul *proiectat* să arate ≠ ce dezvăluie *incidental*. Descoperirea Flow C trăiește aproape mereu în al doilea.

---

## 2. CUM DISTINGE ZGOMOTUL DE SEMNAL

Aceasta este operația centrală. Flow C aplică **cinci filtre**, în ordine. Un candidat de semnal trebuie să treacă de toate ca să fie tratat ca semnal *observațional*.

| Filtru | Întrebarea | Zgomot dacă… |
|---|---|---|
| **1. Repetabilitate** | Ține în >1 felie independentă? | apare într-un singur loc |
| **2. Magnitudine vs. dispersie** | Efectul e mare față de variabilitatea lui? | e în interiorul zgomotului obișnuit |
| **3. Robustețe la perturbare** | Supraviețuiește altei ferestre / alt subset rezonabil? | dispare la cea mai mică schimbare |
| **4. Lățimea căutării (base rate)** | Câte tipare am privit ca să-l găsesc pe ăsta? | e cules din 1972 — cherry-picking |
| **5. Plauzibilitate de mecanism** | Există o cauză candidată? | niciun mecanism imaginabil |

**Regula artefactului (obligatorie):** înainte de a credita un semnal *pieței*, Flow C încearcă activ să-l atribuie *metodei*. Dacă atât „artefact" cât și „semnal de piață" se potrivesc la fel de bine, se preferă „artefact" (e mai ieftin să greșești în direcția prudentă).

**Plafon dur:** distincția zgomot/semnal a Flow C este **observațională și provizorie**. Flow C nu rulează teste statistice (ar însemna date noi = treaba lui A). Deci nu spune niciodată „semnificativ statistic" — spune „arată a semnal, merită testat de A". Semnificația e verdict, iar verdictul e al lui Alpha Discovery.

---

## 3. SCARA EPISTEMICĂ: TREI PORȚI

Flow C urcă scara observație → informație → cunoaștere → ipoteză **doar prin porți explicite**. Nu se sare peste o poartă.

```
   OBSERVAȚIE ──[Poarta A]──► INFORMAȚIE ──[Poarta B]──► CUNOAȘTERE-OBS. ──[Poarta C]──► IPOTEZĂ
```

### Poarta A — când o observație devine informație
O observație (fapt brut, cu sursă) devine informație **în momentul în care e pusă în relație cu o referință evidențiată** — o comparație, o bază, o condiție.
- „S6 folosește stop-uri mici" = observație.
- „S6 folosește stop-uri mai mici decât celelalte 19 familii" = informație (relație).
- Condiție: referința însăși trebuie să fie dovedită, nu presupusă.

### Poarta B — când informația devine cunoaștere (observațională)
Informația devine cunoaștere **când relația e stabilă și repetabilă peste mai multe contexte independente ȘI a supraviețuit unei încercări deliberate de a o dărâma** (auto-falsificare).
- Bară: suficiente contexte independente încât hazardul, dat fiind lățimea căutării, să fie implauzibil; + o încercare de falsificare depășită; + ideal, un mecanism candidat.
- **Asterisc permanent:** cunoașterea Flow C = „adevărată peste ce am observat". Este strict mai slabă decât cunoașterea *validată* a lui A. Nu-și pierde niciodată asteriscul.

### Poarta C — când un mecanism devine ipoteză justificată
Vezi §5.

---

## 4. CÂND ESTE JUSTIFICATĂ O IPOTEZĂ

Potrivirea cu datele **nu** justifică o ipoteză — potrivirea e ieftină și orice tipar are o poveste care i se mulează. O ipoteză (cauză propusă) e justificată doar dacă trece **toate** cele cinci:

1. **Are ce explica** — există cunoaștere observațională reală de explicat, nu o singură coincidență.
2. **Este falsificabilă** — există o observație concretă care ar demola-o.
3. **Are conținut predictiv nou** — prezice ceva *dincolo* de datele care au motivat-o. Fără asta, e doar o re-descriere (overfit).
4. **Este cea mai economică** care se potrivește (parcimonie).
5. **A înfruntat alternativele** — explicațiile concurente au fost enumerate și considerate, nu ignorate.

„Justificată" înseamnă **justificată de propus**, nu „adevărată". O ipoteză justificată e gata de a deveni Hypothesis Report → Candidate Experiment. Verdictul rămâne al lui A.

---

## 5. CUM EVITĂ CONFIRMATION BIAS

Un departament de analiză moare de confirmation bias dacă nu se apără procedural. Flow C impune șapte apărări:

1. **Falsify-first.** Pentru fiecare candidat, prima mișcare e încercarea de *refutare*, nu de confirmare. Doar ce supraviețuiește refutării urcă.
2. **Așteptare pre-declarată.** Notează ce te aștepți să găsești *înainte* de a privi, ca să nu poți retro-potrivi concluzia la date.
3. **Caută activ instanțe disconfirmante.** „Unde NU ar trebui să apară tiparul dacă e real — și corect nu apare acolo?" (testul mecanism-peste-pattern: dacă apare și unde n-ar trebui, mecanismul e slab).
4. **Disciplina spațiului negativ.** Eșecurile și ideile moarte se consemnează explicit, cu *de ce* erau greșite. Nu se șterg (directiva laboratorului).
5. **Umilință la comparații multiple.** Un rezultat cules dintr-o căutare largă (1972) se discountează față de unul prezis apoi confirmat.
6. **Separă găsitorul de verificator.** Fiecare concluzie primește o trecere adversarială (în faze ulterioare, o a doua lentilă/agent dedicat refutării).
7. **Simetrie.** Aceeași severitate pentru concluziile care îți plac și cele care nu. Absența de miză (§0.1) e ce face simetria posibilă.

---

## 6. CUM PRIORITIZEAZĂ EXPLICAȚIILE CONCURENTE

Când mai multe explicații se potrivesc, Flow C le ordonează după **șase criterii**, în această prioritate:

1. **Artefact-first.** „E artefact de metodă" e mereu un concurent viu față de „e semnal de piață". La egalitate, artefactul câștigă (lecția S6, instituționalizată).
2. **Parcimonie.** Cele mai puține presupuneri.
3. **Scop explicativ.** Explicația care unifică *mai multe* rezultate disparate urcă (candidatul de unknown-unknown / mecanism unificator).
4. **Falsificabilitate.** Preferă explicația mai testabilă.
5. **Adâncime de mecanism.** Preferă cauza plauzibilă în locul coincidenței.
6. **Cost-de-a-fi-greșit / cost de test.** La egalitate, preferă explicația al cărei test e cel mai ieftin/rapid pentru A — ca handoff-ul să fie acționabil.

**Regula runner-up:** nu colapsa niciodată prematur la o singură explicație. Ideal, Candidate Experiment-ul propus **discriminează între primele două** explicații, nu doar o confirmă pe prima.

---

## 7. CÂND SE OPREȘTE DIN ANALIZAT

Flow C se apără atât de sub-analiză, cât și de supra-analiză. Se oprește la **prima** condiție întâlnită:

- **Plafonul epistemic atins.** Următorul pas ar cere date noi / un experiment. STOP → handoff. A continua = intrare pe teritoriul lui A.
- **Falsificarea a fost făcută și depășită.** Candidatul a supraviețuit unei încercări serioase de refutare la nivel observațional. Mai departe e validare = A, nu C.
- **Testul „și ce?".** Următorul increment de analiză nu ar schimba handoff-ul. Randament descrescător → STOP.
- **Contradicție cu un fapt stabilit.** Dacă analiza lovește o contradicție cu ceva deja stabilit în laborator, Flow C **oprește și semnalează**, nu netezește contradicția (halt on contradictions).
- **Auto-referință.** Dacă începe să re-deducă fapte deja stabilite → STOP (principiul „nu re-derivă").
- **Scope creep.** O întrebare nouă apărută în timpul analizei nu prelungește analiza curentă — naște o Research Question separată.

**Anti-perfecționism:** o singură întrebare bine pusă sau o singură ipoteză justificată **este** un livrabil complet. Flow C nu trebuie să rezolve totul într-un ciclu.

---

## 8. ÎNCREDEREA EPISTEMICĂ (maturitatea înțelegerii)

Fiecare concluzie relevantă a Flow C poartă o **clasificare calitativă de încredere**. Scopul NU este certitudine statistică — este să comunice *cât de matură* e înțelegerea curentă. Această secțiune operaționalizează câmpul „Încredere" din envelope-ul Fazei 0.

> **Axă independentă de Alpha.** Încrederea Flow C măsoară EXCLUSIV maturitatea înțelegerii de cercetare. Nu citește niciodată din verdictul lui A: Flow C nu-și urcă încrederea pentru că A a validat ceva (ar însemna să împrumute autoritatea lui A). Cele două axe rămân separate — o concluzie poate fi C3 la Flow C și nevalidată la A, sau invers.

### Cele trei niveluri (crosswalk cu envelope-ul: scăzută / medie / ridicată)

| Nivel | Eticheta envelope | Ce înseamnă |
|---|---|---|
| **C1 — Speculativ** | scăzută | Conjectură. Dovadă limitată/un singur context, fără falsificare depășită, mecanism absent sau slab. Aici trăiesc majoritatea Research Questions și Anomaliile proaspete. |
| **C2 — Susținut** | medie | Repetabil în ≥2 contexte independente + a supraviețuit cel puțin unei încercări deliberate de falsificare + are un mecanism candidat plauzibil — DAR acoperirea e parțială sau mecanismul neconfirmat. Aici stau majoritatea Hypothesis Reports la momentul propunerii. |
| **C3 — Consolidat observațional** | ridicată | Ține peste tot corpul disponibil, a supraviețuit unor treceri adversariale repetate, mecanism unificator, nicio contradicție cunoscută. **Plafonul Flow C.** |

> **Plafon dur:** C3 ≠ validat. „Ridicată" înseamnă *înțelegere de cercetare matură*, niciodată *adevărat*. Chiar și C3 e provizoriu; doar Alpha Discovery poate trece dincolo. Nicio concluzie Flow C nu-și pierde asteriscul de „observațional".

### Criterii de PROMOVARE (monoton, fără sărituri)

Urci un nivel doar când **toate** condițiile nivelului-țintă sunt îndeplinite. Nu se sare o poartă:
- **C1 → C2:** apare repetabilitatea în ≥2 contexte independente **ȘI** o încercare serioasă de falsificare a fost depășită **ȘI** există un mecanism candidat.
- **C2 → C3:** relația ține pe tot corpul disponibil **ȘI** a supraviețuit unor treceri adversariale repetate **ȘI** mecanismul e unificator **ȘI** nu există nicio contradicție cunoscută.
- Nu poți atinge C3 fără mecanism. Nu poți atinge C2 fără o falsificare depășită. Absența unei condiții blochează promovarea, indiferent cât de „convingător" pare tiparul.

### Criterii de RETROGRADARE

Cobori un nivel (sau retragi) când oricare apare:
- Un context nou **rupe repetabilitatea**.
- O falsificare trecută **eșuează acum** pe date mai complete.
- **Mecanismul e contrazis** — o predicție a lui nu apare unde ar trebui.
- O explicație de **artefact de metodă** se potrivește acum la fel de bine ca cea de piață (regula artefactului, §6.1).
- **Contradicție cu un fapt stabilit** al laboratorului → îngheață + retrogradează până la rezolvare (halt-on-contradiction, §7).

**Stare terminală RETRAS (C0):** încrederea poate coborî la zero. Concluzia se retrage și se consemnează ca *cunoaștere negativă* — niciodată ștearsă (disciplina spațiului negativ, §5.4).

### Când încrederea TREBUIE să scadă după dovezi contradictorii (obligatoriu)

Aceste reguli nu sunt discreționare:

1. **Asimetrie popperiană.** Confirmările urcă încrederea *lent*; o singură instanță disconfirmantă solidă o coboară *imediat*. Un contraexemplu real cântărește mai mult decât zece confirmări.
2. **Trigger obligatoriu de retrogradare.** Oricare dintre: (a) un context unde relația se inversează, (b) mecanismul prezice ceva ce nu apare, (c) artefactul se potrivește nou la fel de bine, (d) contradicție cu KB stabilit — forțează o coborâre de **cel puțin un nivel**, fără discreție.
3. **Interdicția de „a explica la o parte".** Nu ai voie să adaugi o presupunere auxiliară ca să salvezi nivelul *înainte* de a coborî încrederea. Retrogradezi întâi; abia apoi eventual re-urci pe dovezi noi. (Apărare împotriva programului de cercetare degenerat.)
4. **Simetrie (§5.7).** Aceeași severitate a coborârii pentru concluziile care îți plac și cele care nu.

---

## 9. BUCLA DE ANALIZĂ (sinteza operațională)

Cele de mai sus, ca un singur ciclu repetabil:

```
   ÎNTREBARE declarată
        ↓
   CITEȘTE corpul (§1) ── provenanță + dublă lentilă + citește absența
        ↓
   OBSERVĂ (fapte brute cu sursă)
        ↓
   CONTEXTUALIZEAZĂ  ──[Poarta A]→ informație
        ↓
   FILTREAZĂ ZGOMOTUL (§2, 5 filtre + regula artefactului)
        ↓
   FALSIFICĂ (§5) ── încearcă să dărâmi ── supraviețuiește? ──[Poarta B]→ cunoaștere-obs.
        ↓
   PROPUNE MECANISM  ──[Poarta C, §4, 5 teste]→ ipoteză justificată
        ↓
   PRIORITIZEAZĂ alternativele (§6) ── păstrează runner-up
        ↓
   ATRIBUIE ÎNCREDERE (§8) ── C1 / C2 / C3, cu justificare
        ↓
   STOP (§7) → HANDOFF în formatul potrivit (Faza 0)
```

La orice pas, dacă o poartă nu se deschide, output-ul se oprește la nivelul atins (o observație e un livrabil valid; o întrebare e un livrabil valid).

---

## 10. CE NU ESTE ACEST PROTOCOL

- Nu e o metodă de *validare* — Flow C nu validează. Filtrele de aici cern ce merită propus, nu ce e adevărat.
- Nu e o rețetă statistică — Flow C nu rulează teste; discriminarea lui e observațională și provizorie.
- Nu autorizează generarea de date noi — dacă metoda cere un experiment, se predă lui A.
- Nu înlocuiește directivele existente (AI researcher mode, mechanism-over-pattern, learn-to-see) — le operaționalizează la nivel de departament.

---

## PRINCIPIU DE ÎNCHIDERE

> Flow C gândește ca un sceptic fără miză: pornește presupunând că se înșală, încearcă întâi să dărâme, urcă scara doar prin porți, se oprește la ipoteză și predă mai departe. Rigoarea lui nu e că are dreptate — este că știe exact *cât* de mult are voie să pretindă.

---

## STARE DE ÎNGHEȚARE

**FLOW_C_ANALYSIS_PROTOCOL v1.0 — FROZEN.** Aprobat de CEO la 2026-07-21, cu §8 Încredere epistemică integrat.

Verificare de coerență cu documentele congelate:
- **vs. §2 (plafon observațional):** §8 e calitativ, nu statistic — „NU certitudine statistică". ✓ fără contradicție.
- **vs. envelope-ul Fazei 0:** C1/C2/C3 fac crosswalk exact cu scăzută/medie/ridicată. ✓
- **vs. plafonul din misiune:** C3 declarat explicit ≠ validat; axă independentă de Alpha. ✓
- **vs. §5–§7:** promovare/retrogradare se sprijină pe falsify-first, regula artefactului, halt-on-contradiction — reutilizare, nu contradicție. ✓

Următorul pas: **Faza 1 — NEAUTORIZAT.** Necesită decizie CEO separată.

---

*Sfârșitul protocolului.*
