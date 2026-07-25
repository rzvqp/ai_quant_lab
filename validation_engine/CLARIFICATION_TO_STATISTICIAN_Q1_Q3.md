# CERERE DE CLARIFICARE CĂTRE STATISTICIAN
### Q1–Q3 · elemente ale designului DC-0004 care nu pot fi operaționalizate din artefactele oficiale

**Document ID:** VE-CLARIF-Q1Q3-v1.0
**Emitent:** Validation Engine · **Destinatar:** Statistician · **Prin:** CEO
**Data:** 2026-07-24
**Declanșator:** transcrierea designului DC-0004 în specificația de referință (`F2_1_REPORT.md` §4), cerută ca poartă de publicare a registrului
**Sursa citată:** `statistician/reviews/DC-0004/STATISTICIAN_PHASE1_DC-0004.md`, §2, §3, §11, §14

---

## 0. Regula acestui document

Validation Engine constată ce nu poate fi operaționalizat și cere valoarea de la Statistician.

> **Acest document nu conține valori recomandate, valori implicite propuse, reformulări ale designului sau completări prin inferență.** Contractul §1.7 interzice executantului să aleagă o valoare implicită, iar o sugestie ar fi o alegere deghizată.

Unde există mai multe lecturi posibile ale unui text, ele sunt enumerate **ca enunț al ambiguității**, fără ca vreuna să fie marcată ca mai probabilă sau preferabilă.

Specificația de referință folosită pentru testarea motorului conține, în locul acestor trei elemente, substituenți de inginerie **fără valoare normativă**. Valorile lor nu sunt reproduse aici, tocmai pentru a nu ancora răspunsul; sunt consemnate pentru audit în `VE_BACKLOG.md` §3. La primirea răspunsului, vor fi înlocuite integral.

Unde este util, sunt anexate **măsurători pe datele reale**. Sunt fapte verificabile despre seria de date, nu propuneri.

---

## Q1 — Definiția exactă a „primei bare H1 a zilei"

### Textul din sursă

§2 și §3 definesc evenimentul de expunere ca:

> „prima bară H1 a zilei, high > prior-day-high ȘI close < prior-day-high"

### De ce motorul nu poate rezolva

Formularea admite cel puțin două lecturi, care produc **populații diferite și denominatoare diferite**:

- **(a)** bara de deschidere a zilei, evaluată apoi pentru condiția de sweep-reject — o singură bară candidată pe zi;
- **(b)** prima bară din zi *care satisface* condiția de sweep-reject — toate barele zilei sunt candidate, se reține prima care se califică.

Sub (a), denominatorul este numărul de zile. Sub (b), este numărul de bare. Cele două nu sunt convertibile una în alta, iar rata evenimentului diferă în consecință.

Motorul nu are voie să aleagă între ele: alegerea determină populația, care este o decizie de proiectare statistică.

### Măsurători pe datele reale, relevante pentru răspuns

Pe `OANDA_XAUUSD_H1@v1` (20.832 bare, 2023-01-02 → 2026-07-13) și `OANDA_XAUUSD_D1@v1` (909 bare):

| Observație | Măsurătoare |
|---|---|
| Ora de start a barei D1 (sursa nivelului prior-day-high) | **21:00 UTC** la 596 de bare · **22:00 UTC** la 313 bare |
| Întrerupere zilnică sistematică în seria H1 | ultima bară 20:00 → următoarea 22:00 (**464 de cazuri**) · ultima bară 21:00 → următoarea 23:00 (**235 de cazuri**) |
| Întreruperi de weekend | 50 de ore, 165 de cazuri |
| Întreruperi zilnice mai lungi (probabil sesiuni scurtate) | 4 ore: 18:00 → 22:00 (12 cazuri) · 19:00 → 23:00 (10 cazuri) |

Consecințele factuale, fără interpretare:

1. **Granița zilei în seria D1 nu este miezul nopții UTC** și se deplasează între 21:00 și 22:00 UTC pe parcursul anului.
2. **Nu există o oră fixă la care „ziua începe" în seria H1.** Prima bară după întreruperea zilnică apare la 22:00 UTC în unele perioade și la 23:00 UTC în altele.
3. Există zile în care întreruperea este mai lungă decât una obișnuită, deci prima bară apare la o oră neobișnuită.

### Ce se cere

1. **Care dintre lecturile (a) sau (b)** — sau o a treia formulare — definește evenimentul.
2. **Ce delimitează „ziua"**: granița calendaristică UTC, granița barei D1 din care se derivă prior-day-high, sau altă graniță declarată numeric.
3. **Timezone-ul de referință** și dacă granița urmează sau nu schimbările sezoniere de oră.
4. **Regula pentru zilele în care nu există bară la ora așteptată**: se ia prima bară disponibilă indiferent de oră, se exclude ziua din populație, sau altă regulă.
5. **Regula pentru zilele cu întrerupere prelungită** (cele 22 de cazuri de mai sus): tratate identic cu punctul 4 sau separat.

---

## Q2 — Apartenența celor două orizonturi la familia de testare multiplă

### Textul din sursă

§14(b):

> „Corecție family-wise (Bonferroni/BH) aplicată pe cele 6 celule din holdout."

§11 pasul 1 cere re-rularea metodologiei **pe toate cele 6 celule** sesiune × direcție, iar §3 raportează rezultatul la **două orizonturi**, K6 și K12.

### De ce motorul nu poate rezolva

Sursa numește șase celule, dar designul produce douăsprezece valori p (6 celule × 2 orizonturi). Textul nu spune dacă:

- cele două orizonturi formează **o singură familie** de 12 teste;
- formează **două familii separate** de câte 6, corectate independent;
- **un singur orizont** este primar și intră în familie, celălalt fiind raportat ca diagnostic în afara corecției.

Pragul corectat diferă în fiecare caz, deci criteriul de succes preînregistrat de la §15 se schimbă odată cu alegerea. Aceasta este o decizie statistică de preînregistrare — constituția §8.4 cere ca planul de corecție să fie declarat în avans.

`multiple_testing.family_members` din specificație se enumeră explicit; motorul nu deduce apartenența la o familie și nu are voie să presupună o convenție.

### Ce se cere

1. **Compoziția exactă a familiei**: enumerarea țintelor care intră sub aceeași corecție.
2. Dacă rezultă **mai multe familii**, care sunt ele și ce metodă de corecție se aplică fiecăreia.
3. Dacă un orizont este **primar** iar celălalt diagnostic, care este care și dacă cel diagnostic rămâne complet în afara corecției.
4. Dacă ieșirile testului **placebo** (§11 pas 4) și ale analizei **multiverse** (§14(e)) intră în aceeași familie sau sunt tratate separat.
5. Metoda de corecție declarată pentru fiecare familie (`bonferroni@v1` sau `benjamini_hochberg@v1`, cu varianta `bh`/`by`) și pragul `alpha`.

---

## Q3 — Granițele UTC exacte ale sesiunilor

### Textul din sursă

§2, §3 și §11 condiționează întregul design pe sesiune, folosind etichetele **Asia**, **Londra**, **New York**, în șase celule sesiune × direcție. Granițele numerice ale acestor sesiuni **nu apar în niciunul dintre artefactele oficiale citite** (documentul Discovery Candidate, review-ul Red Team, raportul Statistician Phase 1).

### De ce motorul nu poate rezolva

Registrul nu conține și nu va conține definiții de sesiune predefinite (`CAPABILITY_REGISTRY_v1.1.md` §4): „NY", „Londra" și „Asia" nu există în motor, pentru că delimitarea sesiunilor este o alegere de proiectare. `session_label@v1` cere granițele declarate numeric în specificație.

Alegerea nu este neutră pentru acest design: explicația alternativă principală identificată chiar de Statistician (§9 — profilul orar de volatilitate, vârf 13–14h UTC) se suprapune parțial peste fereastra NY, iar unde se pune granița schimbă compoziția celulei.

### Ce se cere

1. **Granițele numerice** ale fiecărei sesiuni, ca ore UTC de început și de sfârșit.
2. Dacă granițele sunt **fixe în UTC pe tot parcursul anului** sau urmează schimbările sezoniere de oră ale piețelor de referință.
3. Dacă cele trei sesiuni trebuie să **acopere integral cele 24 de ore** sau dacă există intervale neatribuite; în al doilea caz, cum se tratează barele care cad în afara oricărei sesiuni — excluse din populație sau atribuite unei categorii declarate.
4. Dacă sesiunile se pot **suprapune** și, dacă da, care este regula de atribuire pentru o bară aflată în două sesiuni.
5. Care **marcaj temporal al barei** determină apartenența la sesiune — momentul de început al barei H1 sau alt reper declarat.
6. Cum se atribuie barele din zona întreruperii zilnice documentate la Q1 (22:00–23:00 UTC).

---

## 1. Ce se întâmplă după răspuns

Răspunsurile se transcriu literal în specificația de referință, înlocuind substituenții de inginerie. Nu se aplică nicio adaptare, interpretare sau extindere.

Dacă un răspuns rămâne parțial — de exemplu granițele de sesiune fără regula pentru orele neatribuite — motorul se oprește din nou pe elementul rămas incomplet. Nu completează diferența.

Cele trei întrebări nu blochează nicio decizie de arhitectură și nu blochează analiza G3–G5. Blochează exclusiv statutul de „design real complet exprimat" al specificației de referință.

---

**Nu s-a modificat niciun Discovery Candidate, Addendum, raport Red Team, raport Statistician, Knowledge Base sau artefact Alpha. Datele au fost citite exclusiv pentru numărătorile factuale din Q1; nu au fost modificate.**
