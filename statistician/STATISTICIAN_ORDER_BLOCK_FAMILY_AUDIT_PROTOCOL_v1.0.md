# STATISTICIAN — PROTOCOL DE AUDIT: FAMILIA "ORDER BLOCK REVIZITAT" (E010/E013/E015/E016)

**Document ID:** STAT-OBFAMILY-AUDIT-v1.0
**Data:** 2026-07-27 · **Autor:** Statistician
**Autoritate:** scris ÎNAINTE de a autoriza E013/E016 să atingă setul de confirmare de 11 ani, la cererea explicită a CEO. **CEO nu autorizează testarea până la răspunsul la (b) și (c) — acest document e acel răspuns.**

**Notă de transparență obligatorie:** nu am putut localiza textul V0 verbatim al E010/E013/E015/E016 în acest checkout (căutare largă `.md/.json/.py`, inclusiv `CANDIDATE_STATUS_REGISTER_v1.6.md` — fără rezultat; probabil trăiesc în spațiul de lucru al Flow A, neatins din acest folder). Raționamentul de mai jos se bazează pe caracterizarea ta ("aceeași zonă de order block atinsă din nou, diferind doar în momentul ciclului") — o iau ca fapt raportat, nu ca fapt verificat direct de mine, exact regimul aplicat și în alte cazuri din această sesiune când o altă divizie a produs constatarea.

---

## (a) Tratament de familie sau patru teste independente?

**Familie, cu corecție comună — nu patru sloturi independente în corpul global.**

Dacă toate patru citesc din aceeași construcție de bază (o zonă de order block + un eveniment de revizitare), diferind doar în care moment al ciclului de viață al zonei îl capturează drept intrare, atunci nu sunt patru idei de piață distincte — sunt patru operaționalizări ale UNEI singure idei candidate ("revizitarea unei zone de order block prezice o reacție"), tăiate în puncte diferite. Testarea tuturor patru și raportarea celei mai bune ar fi exact "multiple looks la un singur semnal" — genul de multiplicitate ne-numărată pe care am semnalat-o deja la S18 §"6 ipoteze = 3 semnale × 2 ieșiri, nu 6 teste independente". Corecția (Bonferroni/BH) presupune independență sau cel puțin numărătoare corectă a testelor efective; patru variante puternic corelate tratate ca patru unități m independente subminează exact ipoteza pe care se bazează pragul.

## (b) E013/E016 moștenesc automat suspiciunile lui E010/E015?

**Nu automat — nici "da, descalificate din start", nici "nu, complet independente, decide rezultatul". Moștenirea depinde de mecanica specifică a definiției, care trebuie VERIFICATĂ înainte de date, nu presupusă și nu lăsată să se decidă din rezultat.**

Motivul pentru care nu poate fi lăsat "să decidă rezultatul": dacă E013/E016 au exact același defect care a scos E010 (circularitate definițională — criteriul de selecție a populației și criteriul de măsurare a rezultatului citesc din același reper de preț), ORICE rezultat calculat pe cei 11 ani ar fi o confirmare tautologică, nu o descoperire — dar un p mic obținut așa ar ARĂTA ca o confirmare reală pe date nevăzute. Exact riscul pe care l-ai numit: consumarea ultimului set curat de confirmare pe o non-întrebare. Defectul lui E010 e o proprietate a definiției lui specifice, nu a obiectului "zonă de order block" în sine — deci nu se transferă prin asociere, ci prin mecanică demonstrabil comună.

## (c) Ce verific ÎNAINTE de a le lăsa să atingă datele noi

Niciuna din E013/E016 nu atinge datele de 11 ani până nu trece toate cele trei verificări de mai jos, raportate înapoi la mine:

**1. Verificare de circularitate (moștenire posibilă de la E010).** Pentru fiecare din E013 și E016, scrie explicit: (i) criteriul exact care definește/selectează populația (ce face o zonă/bară eligibilă ca instanță a ipotezei) și (ii) criteriul exact care măsoară rezultatul (ce contează drept reacție/succes). Verifică dacă (i) și (ii) citesc din același nivel de preț, aceeași fereastră sau același eveniment de bază — dacă da, "semnalul" și "confirmarea" sunt două unghiuri asupra aceluiași fapt, defectul care a anulat E010. Trece doar dacă (i) și (ii) sunt demonstrabil independente (repere diferite, nu doar formulare diferită a aceluiași fapt).

**2. Verificare de suprapunere a intrărilor (aceeași metodă ca S18 §7.5).** Calculează suprapunerea pairwise a seturilor de bare/zone-intrare între E010, E013, E015, E016. Raportează fracția de suprapunere brut, fără prag ascuns. Suprapunere mare cu E010 sau E015 e dovadă directă de populație comună — alimentează direct cerința (a) de corecție comună și marchează rezultatul ca variantă corelată, nu ca replicare independentă.

**3. Verificare de măsurători repetate pe aceeași zonă fizică (moștenire posibilă de la E015).** Verifică dacă aceeași zonă de order block poate genera mai multe "oportunități de tranzacție" numărate separat (revizitată pe bare diferite, fiecare contată ca observație proprie). Dacă da, dimensiunea efectivă a eșantionului trebuie calculată ținând cont de această clusterizare (conceptul deja stabilit în laborator — N efectiv sub clusterizare) înainte ca orice p calculat pe cei 11 ani să fie luat ca atare.

**4. Pre-angajament de corecție de familie.** Înainte de rulare: E010/E013/E015/E016 sunt pre-înregistrate ca O familie cu un singur buget de semnificație, nu patru sloturi independente — indiferent de rezultatele verificărilor 1-3.

**Doar variantele care trec 1 și 3 (și au 2 raportat, indiferent de rezultat) pot atinge datele de 11 ani.** Orice eșec la 1 sau 3 înseamnă operaționalizare/re-specificare separată ÎNAINTE de a atinge date noi — aceeași regulă deja scrisă pentru ipotezele narative în `STATISTICIAN_11YR_DATASET_PREREGISTRATION_RULES_v1.0.md`, aplicată acum explicit acestei familii.

**Nu autorizez testarea lui E013/E016 până când verificările 1-3 sunt executate și raportate. Statistician se oprește aici.**
