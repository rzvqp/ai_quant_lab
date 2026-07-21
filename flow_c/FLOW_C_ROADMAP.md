# FLOW C — ROADMAP DE DEZVOLTARE
### Arhitectura evoluției Research Intelligence, de la starea curentă la departament științific matur
**Status:** PROPUNERE ARHITECTURALĂ — în așteptarea review-ului CEO (nu îngheța încă)
**Bazat pe (fără a le modifica):** MISSION v1.0 · PHASE_0_OUTPUT_FORMATS v1.0 · CONSISTENCY_AUDIT · ANALYSIS_PROTOCOL v1.0
**Nu e plan de implementare. Nu analizează rezultate Alpha. Nu generează Research Reports.**

---

## PRINCIPIUL CONDUCĂTOR (răspunsul la propria falsificare)

Cea mai puternică obiecție la orice roadmap fazat este: *„Protocolul spune că analiza e condusă de întrebare (§1). Un lanț rigid de faze contrazice libertatea condusă-de-întrebare."*

Rezolvare — și temelia întregii arhitecturi:

> **Fazele NU sunt un orar de sarcini și nu restricționează ce întrebări își pune Flow C. Sunt o scară de AUTORITATE CÂȘTIGATĂ.** Fiecare fază marchează momentul în care Flow C câștigă dreptul de a emite *de încredere* o clasă de output cu miză mai mare — culminând cu traversarea graniței de guvernanță spre Alpha Discovery (Candidate Experiment).

Curiozitatea condusă-de-întrebare operează liber *în interiorul frontierei curente de capabilitate*. Flow C poate **observa** un mecanism înainte de Faza 4 — dar nu-l poate **preda formal** lui A până nu și-a câștigat baza de încredere. Astfel roadmap-ul supraviețuiește propriei falsificări, dar în formă modificată: **fazele guvernează încrederea-de-handoff și autoritatea cross-graniță, nu curiozitatea internă.**

Aceasta se aliniază direct: cu spina de guvernanță (RI → Alpha → Validare → CEO → AI Trader) și cu scara de încredere §8 (C2/C3 se *câștigă* în timp).

---

## DERIVARE (de unde vin fazele)

Fazele nu sunt presupuse; sunt derivate din trei structuri deja înghețate:

1. **Cele 8 output-uri** (Faza 0) definesc spațiul de capabilități. Fiecare fază activează o clasă:
   descriptiv (Research Report) → relațional (Meta, Anomaly) → obiect (Strategy Diagnostic, Regime) → explicativ+handoff (Hypothesis, Candidate Experiment).
2. **Scara epistemică** (protocol §3): observație → informație → cunoaștere-obs. → ipoteză. Fazele urcă exact această scară, în ordine.
3. **Scara de încredere** (protocol §8): C1 → C2 → C3 se câștigă cumulativ. Un departament matur nu emite one-off-uri; menține un corp viu de cunoaștere a cărui încredere evoluează → impune o fază longitudinală.

Plus două fire transversale din misiune: **obiectul dublu de studiu** (piață + laborator) și **unknown-unknowns** (§6.1). Al doilea NU e o fază — este o capabilitate care se maturizează continuu (RI-REPORT-0001 a emis deja Research Questions candidate). Vezi „Fir transversal" mai jos.

---

## HARTA FAZELOR (privire de ansamblu)

| Fază | Capabilitate câștigată | Output-uri activate | Nivel epistemic atins |
|---|---|---|---|
| **P1 — Bază descriptivă** (curentă) | „vedem ce ESTE" | Research Report | cunoaștere-obs. |
| **P2 — Cartografiere relațională** | „vedem ce se LEAGĂ de ce" | Meta Analysis, Anomaly Report | cunoaștere-obs. |
| **P3 — Diagnostic țintit** | „vedem sănătatea unui OBIECT" | Strategy Diagnostic, Regime Analysis | inf. → ipoteză |
| **P4 — Handoff explicativ** | „propunem MECANISME și predăm lui A" | Hypothesis Report, Candidate Experiment | ipoteză (predată) |
| **P5 — Inteligență cross-flow** | „vedem backtest vs. live" | Meta Analysis (A×B), Anomaly Report | ipoteză |
| **P6 — Maturitate instituțională** | „întreținem un corp VIU de cunoaștere" | toate + auto-audit | evoluție de încredere |

**Fir transversal (P1→P6): Research Question** — capabilitatea de unknown-unknowns; se maturizează cu fiecare fază, nu are fază proprie.

---

## FAZELE (specificație pe 10 puncte)

### P1 — BAZĂ DESCRIPTIVĂ *(în curs; un ciclu validat)*
1. **Scop.** Stabilește harta descriptivă a întregii dovezi Alpha existente — „normalul" față de care orice deviere viitoare capătă sens.
2. **Obiectiv științific.** Capabilitatea de a produce *de încredere* Research Reports peste tot corpul, nu doar un exemplar.
3. **Inputuri.** Rezultatele existente Alpha Discovery (FAMILY_RESULTS și artefacte reproduse); coloanele încă neatinse (val_exp, t1/t3/t5, wo1).
4. **Outputuri permise.** Research Report (+ Research Questions transversale).
5. **Criterii de intrare.** Fundația v1.0 validată (îndeplinit).
6. **Criterii de ieșire.** Corpul are o acoperire descriptivă suficientă încât „normalul" per familie/side/metrică e cunoscut; nicio zonă majoră de metrică nedescrisă.
7. **Deliverables.** Un set de Research Reports care acoperă corpul; INDEX actualizat.
8. **Granițe.** FĂRĂ corelație cross-axă (→ P2), FĂRĂ mecanisme, FĂRĂ diagnostic de obiect.
9. **Dependențe.** Doar fundația.
10. **Riscuri dacă e sărită.** Fără „normal", filtrul de repetabilitate (§2.1) nu are referință → imposibil de distins semnal de zgomot în toate fazele următoare. Catastrofal.

### P2 — CARTOGRAFIERE RELAȚIONALĂ
1. **Scop.** Trecerea de la „ce este" la „ce se leagă de ce" — exact observațiile pe care P1 le amână (ex. long-skew 271/86, familie×outcome din RI-REPORT-0001).
2. **Obiectiv științific.** Capabilitatea de corelație cross-axă disciplinată + detecția de anomalii.
3. **Inputuri.** Baza descriptivă P1 + corpul brut, pe ≥2 axe (familie, side, metrică, timp).
4. **Outputuri permise.** Meta Analysis, Anomaly Report (+ Research Questions).
5. **Criterii de intrare.** P1 la criteriul de ieșire (există un „normal").
6. **Criterii de ieșire.** Relațiile transversale majore din corp sunt cartografiate; anomaliile evidente sunt consemnate cu verdict preliminar piață-vs-artefact.
7. **Deliverables.** Meta Analyses pe axele majore; Anomaly Reports pentru contradicțiile găsite.
8. **Granițe.** FĂRĂ diagnostic de strategie individuală (→ P3), FĂRĂ mecanism dezvoltat ca ipoteză de sine stătătoare (→ P4), FĂRĂ handoff la A.
9. **Dependențe.** P1.
10. **Riscuri dacă e sărită.** Salt direct la diagnostic/explicație fără temelie relațională → artefacte cross-axă confundate cu semnal (capcana long-skew) → confirmation bias amplificat.

### P3 — DIAGNOSTIC ȚINTIT
1. **Scop.** Vederea sănătății de ordinul doi a obiectelor concrete: strategii care se degradează, regimuri care structurează rezultatele.
2. **Obiectiv științific.** Capabilitatea de diagnostic obiect-nivel (agent) și de propunere de regim (mediu).
3. **Inputuri.** Baza descriptivă + relațională; felii per-strategie / per-regim; valorile de la Strategy Health (citite, nu recalculate).
4. **Outputuri permise.** Strategy Diagnostic, Regime Analysis (+ RQ). *(Regime Analysis urcă la ipoteză — prima atingere a plafonului explicativ.)*
5. **Criterii de intrare.** P2 la ieșire (există „normalul relațional" față de care se măsoară degradarea).
6. **Criterii de ieșire.** Strategiile atipice/degradante au diagnostice; clusterele care sugerează regimuri au analize cu test de falsificare propus.
7. **Deliverables.** Strategy Diagnostics pentru cazurile reprezentative/degradante; Regime Analyses pentru clusterele candidate.
8. **Granițe.** FĂRĂ scoruri recalculate, FĂRĂ modificarea Strategy Health, FĂRĂ handoff la A (mecanismul complet e P4).
9. **Dependențe.** P1, P2.
10. **Riscuri dacă e sărită.** Fără „normal" de obiect, degradarea e invizibilă → misiunea „detectează degradarea înainte să apară" eșuează.

### P4 — HANDOFF EXPLICATIV *(prima traversare a graniței de guvernanță)*
1. **Scop.** Transformarea cunoașterii acumulate în mecanisme falsificabile și predarea lor lui Alpha Discovery — rațiunea de a fi a departamentului (misiune §7: „A caută cu intenție").
2. **Obiectiv științific.** Capabilitatea de a produce Hypothesis Reports justificate (§4, 5 teste) și Candidate Experiments (cerere de guvernanță).
3. **Inputuri.** Toate anomaliile, diagnosticele și pattern-urile relaționale din P2/P3.
4. **Outputuri permise.** Hypothesis Report, Candidate Experiment (+ RQ).
5. **Criterii de intrare.** P2 și P3 la ieșire; există candidați care au trecut filtrele de zgomot (§2) și au supraviețuit unei falsificări (→ eligibili C2).
6. **Criterii de ieșire.** Există un flux funcțional și disciplinat de handoff către A; primul Candidate Experiment predat conform traseului de guvernanță.
7. **Deliverables.** Hypothesis Reports; Candidate Experiments; înregistrări de predare în INDEX.
8. **Granițe.** FĂRĂ validare (rămâne a lui A), FĂRĂ cod de test, FĂRĂ drept de follow-up asupra deciziei lui A, FĂRĂ comunicare cu Flow B.
9. **Dependențe.** P2, P3. *(NU depinde de P5.)*
10. **Riscuri dacă e sărită.** Flow C produce cunoaștere care nu ajunge niciodată la A → departament inert → misiunea (valoarea = A caută cu intenție) e ratată complet.

### P5 — INTELIGENȚĂ CROSS-FLOW *(gată extern de Flow B)*
1. **Scop.** Cele mai valoroase ipoteze din misiune (§3): divergențele backtest-vs-live.
2. **Obiectiv științific.** Capabilitatea de a corela dovada lui A (backtest) cu dovada lui B (shadow/live).
3. **Inputuri.** Shadow evidence / comportament live de la Flow B **+** baza relațională P2.
4. **Outputuri permise.** Meta Analysis (A×B), Anomaly Report, Hypothesis Report (+ RQ).
5. **Criterii de intrare.** P2 la ieșire **ȘI** Flow B emite dovadă shadow/live utilizabilă. *(Ramură, nu succesiune — vezi Evaluare.)*
6. **Criterii de ieșire.** Divergențele majore backtest-vs-live sunt cartografiate cu verdict preliminar; ipotezele născute din divergență intră în fluxul P4.
7. **Deliverables.** Meta Analyses cross-flow; Anomaly Reports de divergență.
8. **Granițe.** FĂRĂ comunicare directă cu B (doar consumă dovada lui, nu-i trimite nimic), FĂRĂ validare.
9. **Dependențe.** P2 (minim). NU depinde de P3/P4 pentru a începe.
10. **Riscuri dacă e sărită.** Cel mai periculos mod de eșec (merge în backtest, cade în live) rămâne nedetectat → ipotezele cu cea mai mare valoare nu se produc niciodată.

### P6 — MATURITATE INSTITUȚIONALĂ
1. **Scop.** Flow C devine un departament permanent cu un corp VIU de cunoaștere a cărui încredere (§8) evoluează, integrat cu directivele laboratorului.
2. **Obiectiv științific.** Capabilitatea longitudinală: urmărirea concluziilor în timp (promovare/retrogradare C1↔C3), auto-audit adversarial, vânătoare sistematică de unknown-unknowns.
3. **Inputuri.** Toate output-urile anterioare + batch-uri noi continue + contradicții nou apărute.
4. **Outputuri permise.** Toate cele 8 + un registru longitudinal de încredere + auto-audituri.
5. **Criterii de intrare.** Componenta „registru longitudinal" se activează devreme (la ieșirea din P1 există concluzii de urmărit); componenta „re-audit de prag" necesită volum (vezi Evaluare — split).
6. **Criterii de ieșire.** Fără ieșire — este starea staționară matură; are în schimb gate-uri de re-audit periodice (model: bazele cumulative ale laboratorului, praguri 50/75/100).
7. **Deliverables.** Registrul de încredere; auto-audituri periodice; Meta Analyses de tip „ce lipsește" (completeness critic, protocol §... / misiune §6.1).
8. **Granițe.** FĂRĂ a lăsa auto-auditul să valideze (auto-auditul cerne, nu confirmă); FĂRĂ modificarea propriei fundații fără decizie CEO.
9. **Dependențe.** P1 (pentru registru); P2–P4 (pentru un corp bogat de auditat).
10. **Riscuri dacă e sărită.** Output-uri one-off, încrederea nu evoluează niciodată, concluziile fie osifică fie sunt re-derivate, unknown-unknowns nevânate → departamentul rămâne un generator de rapoarte, nu un departament științific. Contrazice natura temporală a §8.

---

## EVALUARE ȘI AUTO-FALSIFICARE

Pentru fiecare fază: necesară? redundantă? de comasat? de scindat? maximizează ordinea valoarea?

| Fază | Necesară? | Redundantă? | Comasare? | Scindare? | Verdict ordonare |
|---|---|---|---|---|---|
| **P1** | Da — ancora „normalului" | Nu | Nu | Nu | Trebuie prima (toate depind de „normal") |
| **P2** | Da — poartă spre orice non-descriptiv | Nu | *Tentant* cu P3 — vezi mai jos | Nu | După P1 |
| **P3** | Da — misiunea cere detecție de degradare | Nu | *Tentant* cu P2 — respins mai jos | Nu | După P2 (are nevoie de normal relațional) |
| **P4** | Da — rațiunea de a fi (handoff la A) | Nu | Nu | Nu | După P2+P3 |
| **P5** | Da — valoarea maximă (misiune §3) | Nu | Nu | Nu | **Ramură după P2**, nu succesiune (vezi jos) |
| **P6** | Da — natura temporală a §8 | Nu | Nu | **Da — scindare** (vezi jos) | Registru devreme; re-audit târziu |

**Falsificarea 1 — „Comasează P2 și P3 într-o singură fază analitică."**
Argument pro: ambele sunt „dincolo de descriptiv". *Respins:* P2 e breadth (cross-axă, agregat), P3 e depth (obiect, țintit); auditul de consistență le-a stabilit deja ca output-uri distincte. Mai important, P3 are nevoie de „normalul relațional" produs de P2 pentru a măsura degradarea — deci sunt secvențiale, nu simultane. Comasarea ar șterge exact dependența care le ordonează. **Rămân separate.**

**Falsificarea 2 — „P5 trebuie să fie ultima (după P4), fiind cea mai avansată."**
*Respins parțial → refinare:* calitatea lui P5 depinde de skill-ul relațional (P2), NU de P3/P4. Iar valoarea lui P5 (divergențe backtest-vs-live) e cea mai mare din misiune. Deci dacă Flow B emite deja dovadă, **P5 este o RAMURĂ care pornește imediat după P2, în paralel cu P3/P4** — a o forța după P4 ar amâna cea mai valoroasă capabilitate fără motiv de dependență. Roadmap-ul NU e liniar; e un DAG.

**Falsificarea 3 — „P6 e doar «steady state», nu o fază reală."**
*Respins → scindare:* P6 conține două capabilități cu maturitate diferită. (a) *Registrul longitudinal de încredere* trebuie să se activeze DEVREME (la prima concluzie, sfârșitul P1) — altfel promovarea/retrogradarea §8 nu are unde trăi. (b) *Re-auditul de prag + completeness critic* e genuin terminal (are nevoie de volum). Deci P6 se scindează: componenta (a) e transversală și pornește la ieșirea din P1; componenta (b) rămâne finală. Aceasta e un răspuns direct la „could it be split?".

**Falsificarea 4 (cea mai dură) — „Întregul roadmap contrazice analiza condusă-de-întrebare."**
Deja rezolvată în Principiul Conducător: fazele guvernează *autoritatea de handoff*, nu curiozitatea internă. Flow C poate observa orice în orice fază; câștigă doar treptat dreptul de a *preda* clase de output cu miză crescândă. Fără această reîncadrare roadmap-ul ar fi fost fals; cu ea, supraviețuiește.

**Este o arhitectură mai bună disponibilă?** Am testat varianta minimală în 4 faze (Descrie / Relaționează+Diagnostichează / Explică+Predă / Cross-flow+Instituție). Respinsă: comasează dependențe reale (P2→P3 normal relațional; P5 ca ramură; split-ul P6) pe care versiunea minimală le-ar ascunde, reducând capacitatea de gating. Versiunea de 6 faze + DAG **maximizează valoarea științifică prin gating precis al autorității**, nu prin număr de faze.

---

## ARHITECTURA FINALĂ (DAG, nu lanț liniar)

```
P1 Bază descriptivă
   │
   ├──────────────► P2 Cartografiere relațională
   │                   │
   │                   ├──► P3 Diagnostic țintit ──┐
   │                   │                            ├──► P4 Handoff explicativ ──► (spre Alpha Discovery)
   │                   ├──► P5 Cross-flow* ─────────┘         │
   │                   │    (*gată de dovada Flow B)          │
   │                   │                                      │
   └──► [P6a Registru longitudinal de încredere] ────────────┴──► [P6b Re-audit de prag + completeness]
        (se activează la ieșirea din P1, transversal)              (terminal, necesită volum)

Fir transversal P1→P6: Research Question (unknown-unknowns), fără fază proprie.
```

**Rezumat al refinărilor produse de auto-falsificare:**
1. Fazele = scară de autoritate câștigată, nu orar (răspuns la Falsificarea 4).
2. P5 e ramură după P2 (paralel cu P3/P4), nu succesor al P4 (Falsificarea 2).
3. P6 scindat: registru longitudinal devreme (P6a) + re-audit terminal (P6b) (Falsificarea 3).
4. P2 și P3 rămân separate — dependența de „normal relațional" le ordonează (Falsificarea 1).

---

*Sfârșitul roadmap-ului. Livrat și mă opresc, conform mandatului. Nu am modificat niciun document înghețat, nu am generat Research Reports, nu am analizat rezultate Alpha, nu am făcut plan de implementare. Aștept review-ul CEO înainte de orice îngheț.*
