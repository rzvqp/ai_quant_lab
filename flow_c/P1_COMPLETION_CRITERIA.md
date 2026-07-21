# FLOW C — P1 COMPLETION CRITERIA
### Când e completă descrierea corpului (P1) și când e justificată analiza relațională (P2)
**Status:** ✅ v1.0 — ÎNGHEȚAT (FROZEN) prin decizie CEO, 2026-07-21
**Autoritate:** derivat din ANALYSIS_PROTOCOL v1.0 + ROADMAP (P1 & poarta P2), fără a le modifica
**Ancorat în:** structura reală a corpului existent (RI-REPORT-0001; FAMILY_RESULTS.parquet)
**Include:** distincția P1 Completion vs P2 Readiness (Rev.1) · Coverage Confidence + Lifecycle §2.1 (Rev.2 + rafinare finală)

> Document înghețat. Orice modificare ulterioară cere o nouă decizie CEO explicită și un bump de versiune.

---

## 0. PREMISĂ DE REALITATE (constrânge tot restul)

P1 folosește **doar dovada Alpha existentă**. Structura ei reală, azi:
- **1 instrument / 1 timeframe / 1 dataset real de edge-uri** (XAUUSD, grilă M15; `FAMILY_RESULTS.parquet`). `reproduction_v2` = reproducere bit-exactă (nu dataset nou); `matched_null_validation` = null sintetic (nu edge-uri reale).
- **20 de familii** (S1–S20), **1972 ipoteze**, funnel `1972 → 1800 valide → 357 hist_prof → 130 research_worthy`, **133 fragile**, **6 familii zero-profit** (S4,S7,S10,S11,S12,S15).
- **~22 de coloane** metrice; RI-REPORT-0001 a lăsat explicit neatinse `val_exp, t1, t3, t5, wo1`.

**Consecință critică:** axele *regim / dataset / timeframe multiplu* **nu există** în dovada curentă. Nu pot fi criterii obligatorii (altfel P1 n-ar putea fi niciodată completă fără date noi, interzise). Sunt axe **condiționale** (Track A §2).

---

## 1. DOUĂ DECIZII DISTINCTE (Revizia 1)

Documentul separă explicit două întrebări **înrudite dar neidentice**:

| | Decizie | Întrebarea | Orientare |
|---|---|---|---|
| **A** | **P1 Completion** | „Am descris suficient corpul CURENT?" | spre trecut/prezent — harta e gata? |
| **B** | **P2 Readiness** | „Există material descriptiv suficient cât să JUSTIFICE analiza relațională?" | spre viitor — munca relațională merită și e ne-prematură? |

**De ce nu sunt identice — relație asimetrică, cuibărită:**

> **P2 Readiness ⊃ P1 Completion.** P1 Completion e o **precondiție necesară dar nu suficientă** pentru P2. P2 Readiness = P1 complet **PLUS** condiții suplimentare de justificare relațională.

- **P1 complet, dar P2 NEpregătit** (divergență reală): dacă tot corpul e descris complet, dar descrierile ies plate/omogene, fără nicio observație cross-axă amânată de urmărit — atunci a descrie mai mult nu ajută (P1 e gata), dar a lansa P2 e nejustificat (nu există suprafață relațională de vânat). Descriere completă ≠ muncă relațională justificată.
- **P2 „pare pregătit", dar P1 INcomplet**: dacă întrebări relaționale bogate apar din câteva rapoarte, dar unele familii rămân nedescrise — direcția e **blocată prin design**: P2 Readiness cere P1 Completion ca precondiție dură. Nu sari peste baza descriptivă oricât de tentante ar fi întrebările.

*(În corpul nostru real, RI-REPORT-0001 a amânat deja long-skew 271/86 și familie×outcome → suprafață relațională există. Dar criteriile trebuie să acopere și cazul general.)*

---

## 2. COVERAGE CONFIDENCE (Revizia 2 — concept nou)

**NU este scara epistemică C1/C2/C3.** Aceea măsoară *maturitatea de adevăr a unei concluzii*. **Coverage Confidence** măsoară cu totul altceva: **încrederea că harta descriptivă a corpului este suficient de completă** — o proprietate a *acoperirii*, nu a vreunei concluzii individuale.

> Axe ortogonale: un Research Report poate fi **C1** (interpretare speculativă) și totuși să ridice Coverage Confidence la **High** (a descris complet o regiune). Adevărul-de-concluzie și completitudinea-hărții sunt lucruri diferite.

### Niveluri: Low / Medium / High

| Nivel | Semnificație |
|---|---|
| **Low** | Harta e fragmentară — familii/coloane/straturi majore nedescrise; corpul încă „surprinde" descriptiv la fiecare trecere. |
| **Medium** | Majoritatea celulelor matricei de acoperire sunt pline, dar rămân goluri cunoscute și/sau ultimele treceri încă scot structură descriptivă nouă. |
| **High** | Toate celulele matricei pline sau logate explicit **ȘI** saturație descriptivă atinsă **ȘI** niciun gol nelogat. |

### Ce o CREȘTE
- Mai multe celule ale matricei de acoperire umplute (familii, coloane, straturi de funnel, side).
- Straturile de eșec descrise (nu doar câștigătorii) — reduce riscul de hartă părtinitoare.
- Familia dominantă (S1) tratată dedicat, nu doar agregat.
- **Saturație:** trecerile noi încetează să scoată structură descriptivă nevăzută anterior (semnal de randament descrescător, model: bazele cumulative ale laboratorului).
- **Logarea explicită a golurilor** — un gol *cunoscut* crește încrederea (convertește un unknown-unknown de acoperire într-un known-known), spre deosebire de unul ascuns.
- Provenanță verificată (corpus reprodus bit-exact).

### Ce o SCADE
- Descoperirea de familii/coloane/straturi nedescrise.
- O trecere nouă scoate structură descriptivă nevăzută → harta era mai puțin completă decât se credea.
- Detectarea de skew de survivorship (doar câștigători acoperiți).
- Goluri nelogate găsite.
- **Schimbarea bazei de dovezi** — sosirea unui batch nou de la Alpha coboară automat Coverage Confidence (harta nu mai acoperă materialul nou).

### Gardă anti-gaming (robustețe)
Saturația **singură** nu dă High: se poate „satura" descriind leneș. High cere **simultan** matrice obiectiv completă **ȘI** saturație din treceri genuine (unghiuri diverse). Saturație cu celule goale ≠ High.

### Prag de suficiență
- **P1 Completion (Track A) cere Coverage Confidence = High.** Medium sau Low blochează închiderea P1.
- Coverage Confidence e gauge-ul principal al Track A; nu e suficient singur pentru Track B (care cere în plus suprafață relațională — §Track B).

### 2.1 COVERAGE CONFIDENCE LIFECYCLE (rafinare finală CEO)

Coverage Confidence NU este o etichetă permanentă. Este o **proprietate evolutivă a corpului descriptiv**, ștampilată cu versiunea de dovadă pe care a fost câștigată; se degradează când dovada se schimbă.

**1. Evenimente care SCAD AUTOMAT Coverage Confidence** *(mecanic, fără review):*
- Sosirea unui batch / familii / dataset nou de la Alpha Discovery → harta nu mai acoperă materialul nou (mărimea scăderii ∝ cât material nou).
- Regenerarea sau modificarea corpului existent (chiar și o re-rulare) → drop până la re-verificarea acoperirii.
- Schimbare de schemă (apar coloane noi) → celule noi goale în matrice → drop.
- Descoperirea unui gol nelogat, sau a unui gol logat mai mare decât se credea → drop.

**2. Evenimente care POT crește Coverage Confidence** *(niciodată automat — cer muncă demonstrată + re-check de acoperire):*
- Rapoarte noi care umplu celule anterior goale/logate.
- Descrierea straturilor de eșec rămase.
- Re-demonstrarea saturației din treceri genuine, diverse.
- Logarea explicită a unui gol (convertește un unknown-unknown de acoperire într-un known-known).

**3. Downgrade automat vs. upgrade cu review** *(asimetrie fail-closed):*
- **Scăderile sunt AUTOMATE** — în clipa în care un trigger se declanșează, Coverage Confidence coboară fără a aștepta review. Direcția sigură: mai bine sub-declari acoperirea decât s-o supra-declari.
- **Creșterile CER REVIEW** — atingerea (sau recâștigarea) lui High nu e niciodată automată; cere un re-check explicit față de matrice + confirmarea saturației. Ușor de pierdut, trebuie câștigat ca să revii. *(Paralelă cu asimetria §8 din protocol — dar axă diferită: acoperire, nu adevăr.)*

**4. High nu e persistent — trebuie re-câștigat periodic:**
- High e valid DOAR față de snapshot-ul de dovadă pe care a fost câștigat. Orice schimbare a bazei (batch nou, regenerare, schemă) îl invalidează → trebuie re-câștigat.
- Chiar și fără schimbare, High se re-auditează la **gate-uri de creștere a corpului** (fiecare batch Alpha nou = re-câștigare obligatorie; model: bazele cumulative ale laboratorului cu re-audituri de prag), nu pe calendar.

> **Consecință arhitecturală:** fiindcă P1 Completion cere Coverage Confidence = High, iar High se stinge la sosirea de dovadă nouă, **un P1 închis se poate REDESCHIDE** automat când Alpha produce un batch nou. P1 Completion este el însuși relativ la snapshot — nu un verdict definitiv.

---

# TRACK A — P1 COMPLETION
### „Am descris suficient corpul curent?"

## A.1 Acoperire suficientă
Matrice **{artefacte de dovadă} × {dimensiuni descriptive}**; suficient acoperit când fiecare celulă aplicabilă are ≥1 observație descriptivă cu provenanță, ≥C1, **incluzând straturile de eșec**.
Dimensiuni obligatorii: **familii** (toate 20, incl. cele 6 zero-profit) · **straturi de funnel** (generated/valid/invalid/hist_prof/research_worthy/fragile) · **side** (long/short; both=104 menționat) · **coloane** (toate ~22, fiecare tratată SAU marcată „non-informativă + motiv").

## A.2 Diversitate minimă
- **Obligatorie (există în dovadă):** toate 20 familiile (incl. cele 6 zero-profit ca cunoaștere negativă); traversarea distribuției de rezultat (câștigători / perdanți / fragili / extreme-outlieri S6·S14·S19 / masa valid-neprofitabilă) — gardă anti-survivorship.
- **Condiționată (doar dacă apare în dovadă):** regimuri / datasets / timeframe-uri multiple → dacă lipsesc, se **loghează ca limitare**, nu ca eșec.

## A.3 Criterii cantitative
1. **20/20 familii** cu „normal" legibil (profitabilitate + interval tipic exp/pf + split de side).
2. **6/6 familii zero-profit** acoperite ca cunoaștere negativă.
3. **≥22/22 coloane** tratate SAU marcate „non-informativă + motiv" (închide `val_exp/t1/t3/t5/wo1`).
4. **6/6 straturi de funnel** acoperite.
5. **S1 (dominantă, 58%/73%)** cu ≥1 raport descriptiv dedicat formei interne.
6. **≥2 Research Reports finalizate** (prag minim; metrica reală e matricea, nu numărul de rapoarte).
7. **0 goluri de acoperire nelogate.**

## A.4 Criterii calitative
1. Fiecare raport ≥C1 + provenanță + non-fabricare.
2. Eșecurile descrise cu aceeași rigoare ca succesele (simetrie, §5.7 protocol).
3. Extremele purtate cu notă preliminară artefact-vs-semnal, **fără** explicație (explicația e P4).
4. Zero scurgere cross-axă în oricare raport P1.
5. „Normalul" legibil per familie și metrică.
6. Toate golurile de acoperire logate explicit.

## A.5 CHECKLIST DE IEȘIRE — P1 COMPLETION
```
[ ] Coverage Confidence = High (matrice completă/logată + saturație genuină)
[ ] 20/20 familii cu „normal" legibil
[ ] 6/6 familii zero-profit acoperite ca cunoaștere negativă
[ ] 22/22 coloane tratate SAU marcate non-informativă+motiv (val_exp/t1/t3/t5/wo1 incluse)
[ ] 6/6 straturi de funnel acoperite
[ ] S1 are ≥1 raport descriptiv dedicat
[ ] ≥2 Research Reports finalizate, fiecare ≥C1 + provenanță + non-fabricare
[ ] eșecurile descrise cu aceeași rigoare ca succesele (simetrie)
[ ] extremele purtate cu notă artefact-vs-semnal, fără explicație
[ ] zero scurgere cross-axă
[ ] toate golurile logate explicit (inclusiv axele condiționale regim/dataset/TF)
```
Toate bifate → **P1 e complet**. (NU implică automat P2 — vezi Track B.)

---

# TRACK B — P2 READINESS
### „Există material descriptiv suficient cât să justifice analiza relațională?"

## B.1 Precondiție dură
- **P1 Completion (Track A) integral bifat.** Fără el, P2 Readiness e automat FALS, indiferent de cât de bogate par întrebările relaționale.

## B.2 Condiții suplimentare de justificare relațională
- **Suprafață relațională reală:** ≥2 rapoarte finalizate ale căror observații cross-axă amânate (ex. long-skew 271/86, familie×outcome) formează o **coadă concretă** de muncă relațională care așteaptă P2.
- **Normal stabil, nu doar complet:** „normalul" e destul de legibil și stabil încât să servească drept *bază de măsură* a devierilor relaționale (nu doar „descris o dată").
- **Valoare pozitivă:** juxtapunerea rapoartelor creează suprafață relațională (întrebări de tip axă×axă), nu doar o colecție de descrieri izolate.

## B.3 Condiții care INTERZIC deschiderea P2 (oricare blochează)
- P1 Completion neîndeplinit (orice căsuță A.5 goală).
- Familia dominantă (S1) descrisă doar agregat.
- Eșecurile sub-descrise față de succese (survivorship în bază).
- **Un singur raport** existent (o trecere descriptivă nu poate fundamenta faza relațională).
- Vreo scurgere cross-axă deja prezentă în rapoartele P1 (granița n-a fost respectată).
- Coadă relațională inexistentă (nimic de vânat → P2 prematur/nejustificat).

## B.4 CHECKLIST DE IEȘIRE — P2 READINESS
```
[ ] TOATE căsuțele din A.5 (P1 Completion) sunt bifate           ← precondiție dură
[ ] ≥2 rapoarte ale căror observații amânate formează o coadă relațională reală
[ ] „normalul" e stabil + legibil ca bază de măsură a devierilor
[ ] juxtapunerea rapoartelor produce întrebări axă×axă (valoare relațională pozitivă)
[ ] nicio condiție interzicătoare din B.3 activă
```
Toate bifate → **P2 e eligibil de deschidere, sub decizie CEO separată.** (Eligibilitate, nu autoprogramare.)

---

## RISCURI (comune ambelor track-uri)

**De a părăsi P1 prea devreme (Track A slab):**
- Normal incomplet → corelații P2 pe nisip; artefacte cross-axă (long-skew) luate drept semnal → confirmation bias amplificat.
- Survivorship încorporat → „ce împart câștigătorii" din P2 = base rate deghizat.
- Coloane neexplorate (`val_exp` posibil OOS) → P2 ratează exact axa care contează.

**De a rămâne în P1 prea mult (Track B ignorat deși satisfăcut):**
- Paralizie descriptivă (protocol §7, „și ce?").
- Cost de oportunitate: P2 relațional / P5 divergență backtest-vs-live amânate.
- Deriva spre ipoteză (granularitate excesivă → ipotezare implicită, interzis în P1).
- Limitare de date, nu de descriere: baza mono-instrument nu crește prin mai multă descriere.

---

## AUTO-FALSIFICARE (criterii + concepte noi)

**Distincția A/B — e reală sau artificială?** Testată prin cazuri de divergență (§1): P1-complet-dar-P2-nepregătit (descrieri plate, fără coadă relațională) e un caz real și posibil → distincția NU e artificială. Direcția inversă (P2 fără P1) e blocată prin precondiție dură → asimetria e corectă.

**Coverage Confidence — prea slab?** Saturația singură ar fi putut fi „jucată" prin descriere leneșă → **întărit** cu garda anti-gaming (matrice obiectiv completă ȘI saturație genuină). Logarea golurilor *crește* încrederea (convertește necunoscutul în cunoscut) — contra-intuitiv dar corect: o hartă care își știe găurile e mai de încredere decât una care le ascunde.

**Coverage Confidence vs C1/C2/C3 — confundabile?** Explicit ortogonalizate: un raport C1 poate da Coverage High. Măsoară completitudine-de-hartă, nu adevăr-de-concluzie.

**Prea puternic (moștenit din Revizia 1, păstrat):** axele regim/dataset/TF rămân condiționale; „acoperire per coloană", nu „raport per coloană".

**Echilibru:** satisfăcibile pe dovada existentă, dar nu trivial; A și B au praguri diferite, ceea ce previne colapsarea celor două decizii într-una.

---

## STARE DE ÎNGHEȚARE

**P1_COMPLETION_CRITERIA v1.0 — FROZEN.** Aprobat de CEO la 2026-07-21, cu rafinarea finală (§2.1 Coverage Confidence Lifecycle) integrată.
Distincție oficială adoptată: P1 Completion („am descris corpul?") ≠ P2 Readiness („e justificat relaționalul?"), relație asimetrică cuibărită. Coverage Confidence = concept arhitectural oficial, ortogonal C1/C2/C3, proprietate evolutivă (nu etichetă permanentă), fail-closed (scădere automată / creștere cu review), re-câștigat la fiecare batch nou.
Următorul pas: prima sarcină de implementare P1 — necesită decizie CEO separată.

---

*Sfârșitul documentului.*
