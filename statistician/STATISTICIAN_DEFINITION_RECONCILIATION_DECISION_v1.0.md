# STATISTICIAN — DECIZIE DE RECONCILIERE A DEFINIȚIILOR
### Răspuns la `RECONCILIATION_DEFINITIONS_v1.0.md` (Validation Engine)

**Document ID:** STAT-RECON-DECISION-v1.0
**Data:** 2026-07-24 · **Autor:** Statistician
**Statut:** Decizie metodologică, nu opinie. Se aplică specific validării DC-0004 pe holdout. Nu modifică Validation Engine, Capability Registry, sau vreun cod/implementare.

---

## Decizia

**Pentru re-testul pe holdout-ul DC-0004: adopt Calea A — REPLICARE STRICTĂ a convenției in-sample.**

Definițiile oficiale ale acestui candidat rămân **identice** cu cele încorporate în scripturile care au produs p=0.021/0.029. Definițiile pe care le-am propus în `OPDEF v1.0` **nu se substituie** convenției in-sample pentru acest test. Motivele sunt statistice, nu de conservatorism metodologic — le explic mai jos, împreună cu ce cred că ar trebui să se întâmple, separat, cu propunerile mele.

---

## De ce Calea A, nu Calea B

**Argumentul central:** DC-0004 a ajuns la verdictul READY FOR STATISTICAL VALIDATION *pentru că* există deja un rezultat empiric specific (p=0.021/0.029), produs de o procedură specifică, iar holdout-ul rezervat există tocmai ca test decisiv *pentru acel rezultat*. Valoarea evidențială a holdout-ului nu vine din faptul că testează "aceeași idee generală" — vine din faptul că testează *exact procedura* care a produs dovada inițială. Dacă schimb definițiile acum, holdout-ul nu mai confirmă sau infirmă DC-0004 — testează o ipoteză nouă, pentru care nu există nicio dovadă in-sample (pentru că p=0.021 a fost calculat sub altă definiție, nu sub a mea).

**Avantaje Calea A:**
- Holdout-ul rămâne o replicare autentică — singurul lucru care justifică statistic cheltuirea unei resurse irepetabile.
- Lanțul evidențial (observație → in-sample → OOS) rămâne intact și interpretabil.
- Nu necesită re-stabilirea unei baze de dovezi noi înainte de a atinge holdout-ul.

**Dezavantaje Calea A (le recunosc deschis, nu le ascund):**
- Îngheață posibile slăbiciuni reale ale convenției in-sample — inclusiv una pe care o consider genuin problematică: regula "prima depășire, verifică dacă TOT ea respinge" (§ mai jos) poate **subnumăra** evenimente reale (o zi în care a doua bară respinge, nu prima, e clasificată "fără eveniment", deși fenomenul de interes chiar a avut loc).
- Granița UTC a zilei și sesiunile fixe, fără DST, sunt convenții mai simple decât cele pe care le-aș fi recomandat de la zero — dar simplitatea lor, dacă introduce zgomot, ar acționa *împotriva* găsirii unui efect real, nu în favoarea lui. Asta reduce urgența schimbării, nu o elimină.

**De ce NU Calea B acum:**
- Cere, prin propria ei logică (§4 din documentul VE), re-rularea in-sample sub noile definiții *înainte* de a considera holdout-ul — adică nu e "hai să testăm mai bine", e "hai să reconstruim de la zero baza de dovezi". Asta transformă "validarea DC-0004" în "un nou proiect de descoperire", cu un cost și un risc mult mai mari decât execuția Stage S002 planificată.
- Cheltuirea holdout-ului pe o ipoteză a cărei susținere in-sample n-a fost niciodată măsurată sub noua definiție ar fi exact risipa de resursă irepetabilă pe care am semnalat-o deja ca risc major (§17 Constituție).
- Aș încălca propriul principiu pe care l-am aplicat riguros față de Alpha și Red Team pe tot parcursul acestui angajament: nu schimbi definiția unui test *după* ce dovada a fost deja produsă sub altă definiție, oricât de bine intenționată ar fi schimbarea — e aceeași familie de risc ca alegerea unui prag post-hoc pentru a maximiza separarea (semnalat la DC-0003).

**Impact asupra validității statistice, rezumat:** sub Calea B, cele 5 diferențe critice (graniță zi, număr sesiuni, granițe sesiuni, definiție eveniment) plus cele 4 majore (mărime familie, orizont decisiv, baseline, lateralitate) schimbă simultan populația, compoziția celulelor, pragul de corecție și valoarea p însăși. Nu e o discrepanță marginală — sub Calea B, rezultatul obținut n-ar avea nicio legătură demonstrabilă cu p=0.021. Sub Calea A, holdout-ul testează exact ce a fost promis când DC-0004 a intrat în READY FOR STATISTICAL VALIDATION.

---

## Recunoaștere directă a erorii din OPDEF v1.0

Nu apăr propunerile inițiale doar pentru că le-am scris. Documentul de reconciliere arată clar că am greșit pe două puncte concrete:

1. **Granița zilei** — am presupus ancorare la ora locală New York, bazat pe convenția obișnuită din industria FX, **fără să verific** convenția reală a pipeline-ului (care e, de fapt, zi calendaristică UTC simplă — `dt.dt.date`). Presupunerea mea era plauzibilă în abstract, dar nefondată empiric pentru acest lab.
2. **Definiția evenimentului** — am oferit două variante posibile ("bara de deschidere" / "prima care satisface reject"), dar niciuna nu corespunde definiției reale din cod ("prima bară care depășește nivelul; verifică dacă tot ea respinge; dacă nu, ziua n-are eveniment"). Nu am anticipat această a treia variantă.

Am semnalat corect, în documentul original, dependența de verificare împotriva scripturilor Alpha — dar nu pot pretinde că propunerile ar fi fost corecte "cu excepția verificării". Au fost, pe aceste două puncte, pur și simplu greșite.

---

## Rezolvarea golurilor pentru execuția Calea A (răspuns pentru Validation Engine)

Pentru ca specificația să poată fi blocată:

- **G7 (definiția evenimentului):** eveniment = prima bară H1 a zilei (zi UTC) al cărei `high` depășește prior-day-high; se verifică EXCLUSIV acea bară pentru `close < prior-day-high`. Dacă acea bară nu respinge, ziua nu are eveniment în populație — indiferent dacă o bară ulterioară ar respinge independent. Aceasta e limitarea cunoscută a convenției originale, purtată mai departe neschimbată sub Calea A.
- **Graniță zi:** 00:00 UTC, zi calendaristică simplă (`dt.dt.date`), fără DST.
- **Sesiuni:** 4 categorii, cupe UTC fixe, fără DST — asia [00,08), london [08,13), ny [13,21), late [21,24).
- **S1 (mărime familie):** empirică — toate celulele (sesiune, direcție) cu n≥25 intră în familie; pragul Bonferroni = 0.05/(numărul de celule care ating acest n, determinat din date, nu fixat la 6 în avans).
- **S2 (orizont decisiv):** **K6 singur** e orizontul corectat/decisiv. K12 rămâne raportat descriptiv, fără pretenție de semnificație corectată — exact ca în scripturile originale. (Recomandarea mea anterioară, "K6+K12 aceeași familie", rămâne valabilă ca *bune practici pentru candidați viitori*, dar nu se aplică retroactiv aici, pentru consecvență cu procedura care a produs p=0.021.)
- **S3 (baseline):** forward-ul propriu al sesiunii (nu drift global) — confirmat și de documentul DC-0004 însuși ("measured against the NY session's own forward baseline"), consistent cu obs0008/0012/0013.
- **S4 (min_n):** 25, nu 15.
- **S5 (lateralitate):** one-sided (coada stângă, testând specific reversia), 3000 reeșantionări, seed=7 — exact ca în scripturi.

---

## Recomandare separată, orientată spre viitor (nu se aplică la DC-0004)

Nu resping definițiile propuse în OPDEF ca fiind greșite conceptual — cred că ancorarea locală/DST și evenimentul reformulat pentru a nu subnumăra rejecturile târzii sunt îmbunătățiri reale. Dar acestea trebuie tratate ca o **întrebare de cercetare metodologică separată**, cu propria ei re-baseline pe date ne-sigilate, nu ca o substituție tăcută într-un test deja aflat la pasul de validare. Recomand CEO să autorizeze această comparație ca exercițiu independent, cu rezultat propriu, înainte ca vreun candidat viitor să adopte noile convenții ca standard — și recomand, separat, ca Alpha să emită viitoarele definiții operaționale (graniță, sesiuni, eveniment) ca artefact explicit, versionat, alături de rezultat, exact cum propune Validation Engine la punctul 7 al documentului de reconciliere.

---

**Nu am modificat Validation Engine, Capability Registry, sau vreun cod. Aceasta e o decizie metodologică și un set de definiții blocate pentru execuție, nu o implementare.**

**Statistician se oprește aici și așteaptă confirmarea CEO înainte ca Validation Engine să blocheze specificația.**
