# STATISTICIAN — REGULI PRE-ÎNREGISTRATE PENTRU SETUL DE 11 ANI (M15) ȘI M5
### Scrise înainte ca fișierele să fie conectabile în orice loader

**Document ID:** STAT-11YR-PREREG-v1.1
**Data:** 2026-07-25 (v1.0) · **Amendat:** 2026-07-25 (v1.1, §2 — regula de proveniență a parametrilor împrumutați) · **Autor:** Statistician
**Statut:** Reguli, nu o alegere de dată. Comise înainte de a vedea harta de regimuri (verificarea 7 a Data Acquisition) și înainte ca fișierele M15 extins (2011-07-25 → 2022-12-16) și M5 (2021-07-22 → azi) să fie conectate în `edge_research/_common.py` sau orice alt loader.

**Precedentul pe care îl închid:** de trei ori în acest laborator, datele au fost accesibile înainte să existe o regulă — holdout-ul original, Setul B (loader fără cutoff), Setul B din nou (rulare pornită înainte de mesaj). De fiecare dată cauza a fost aceeași secvență greșită. Acest document există ca regula să existe ÎNAINTE de a treia oară deveni a patra.

---

## 1. Împărțirea celor 11 ani — regula, nu punctul de tăiere

**Tensiunea recunoscută:** sigilarea protejează confirmarea; diversitatea de regim (motivul pentru care aducem datele) cere ca ambele părți — descoperire și confirmare — să conțină fiecare tip de regim, nu doar unul.

**Regula:**

1. **Harta de regimuri trebuie produsă printr-o regulă mecanică, disclosed, nu prin etichetare subiectivă** — o clasificare fixă (ex. randament pe fereastră mobilă de N luni depășește ±X%), stabilită de Data Acquisition ÎNAINTE de a fi folosită pentru împărțire. Nicio hartă "din ochi".
2. **Împărțirea se face în INTERIORUL fiecărui segment de regim, nu printr-o singură dată globală de tăiere.** Pentru fiecare segment contiguu de regim identificat (bear 2011-2015, orice range/bull intermediar, etc.): primele **50%** din barele acelui segment (cronologic, pe număr de bare, nu pe zile calendaristice — consecvent cu convenția deja folosită la campania S1-S51, `d[:0.6n]` pe bare) merg la descoperire; ultimele 50% se sigilează pentru confirmare.
   - **De ce 50/50, nu 60/40 ca la S1-S51:** scopul explicit aici e "singurul set de confirmare curat care mai poate exista" — o raritate care justifică o pondere mai mare pentru partea sigilată decât la campania de strategii. Dacă harta arată segmente foarte scurte (ex. un regim de doar câteva luni) unde 50% ar lăsa prea puține bare pentru descoperire să fie utilă, ajustează spre 60/40 DOAR pentru acel segment specific, înainte de a vedea rezultate — nu retroactiv.
3. **Zonă de carantină (embargo) la fiecare graniță internă descoperire/confirmare** — minimum **960 de bare M15** (cel mai lung orizont folosit curent de orice ipoteză înghețată, `TRACK_HORIZON` din E015), rotunjit în sus la **1.000 de bare**, exclusă complet din AMBELE părți la graniță. Motivul: fără carantină, o ipoteză "descoperită" chiar lângă graniță ar putea fi informată de dependența serială care se scurge peste ea — exact tipul de scurgere pe care l-am identificat deja la E015/E010 în interiorul unei singure ferestre.
4. **Harta însăși nu raportează statistici cantitative fine pentru porțiunile care vor fi sigilate** — doar date de început/sfârșit și eticheta de direcție (bull/bear/range). Fapte macro deja publice (ex. "aurul a scăzut de la ~1900 la ~1050") nu constituie o contaminare — sunt cunoștințe de piață preexistente, nu statistici calculate din acest dataset specific — dar harta nu trebuie să adauge cifre noi, calculate special pentru acest exercițiu, despre porțiunea sigilată.

## 2. Statutul ipotezelor deja înghețate — DA, cu o distincție și o dependență

**Răspuns: DA, cei 11 ani sunt date nevăzute în sens statistic** pentru cele 40 V0 și pentru E015-V1 — **dar motivul corect nu e argumentul tău (a), ci un criteriu mai precis.**

Standardul relevant nu e "a fost vreodată acest tip de concept informat, difuz, de istoricul pieței" — ăsta ar face imposibilă orice confirmare, vreodată, pe orice date istorice, pentru orice ipoteză despre piețe. Standardul care contează, consecvent cu tot ce am stabilit în această sesiune (DC-0004, B.3, E015-V1 însuși): **a fost PARAMETRUL NUMERIC SPECIFIC al ipotezei informat de un rezultat CALCULAT pe aceste date anume?** Codul pe care l-am citit deja (E010/E012/E015: praguri disclosed, neajustate — `DISP_MULT=1.5`, `REVISIT_HORIZON=480`, `REACTION_THRESHOLD=1.0`) arată exact tiparul corect — parametri fixați înainte, nu derivați din rezultate. Originea culturală/istorică difuză a conceptelor ICT nu atinge acest criteriu.

**Precizare importantă pentru E015-V1 specific:** contaminarea lui E015-V1 (stabilită anterior) a fost V0→Set A→V1 — un lanț care nu atinge deloc fereastra 2011-2022. De aceea cei 11 ani chiar rezolvă suspendarea lui, pentru prima dată — dar **doar testând definiția V1 exact așa cum e înghețată, fără nicio ajustare suplimentară acum, altfel se repetă exact tiparul care l-a contaminat prima dată.**

**Ce NU rezolvă cei 11 ani:** circularitatea structurală găsită în codul E010/E012 (`_profile.py`, suprapunerea fereastră-selecție/fereastră-rezultat) e un defect de COD, independent de care dataset rulează pe el. Rulat pe date noi, curate, cu ACELAȘI cod nereparat, aceeași circularitate reapare identic. "Date nevăzute" și "cod corect" sunt întrebări separate — rezolvarea uneia nu rezolvă cealaltă.

**Tratament pe categorie:**
- **Cele 24 V0 netestate:** merg direct la confirmare pe datele noi, sub rezerva verificării de operaționalizare de mai jos.
- **E015-V1:** testabil pe datele noi, cu definiția înghețată, fără ajustare.
- **B.1/B.2 (order block/FVG natural), dacă printre cele 40:** datele sunt curate, dar corecția de familie pe care am derivat-o deja (minimum 2 per E0xx, din selecția pe brațul de control) tot se aplică — "date nevăzute" nu anulează nevoia de corecție, sunt două întrebări diferite.
- **E028-INV:** nu am vizibilitate asupra lanțului lui specific de contaminare ("C-2", menționată anterior, dar nu detaliată). **Nu presupun că se transferă curat doar pentru că E015-V1 se transferă** — am nevoie de motivul exact al contaminării C-2 înainte să confirm sau resping pentru acest caz specific.

**Dependența pe care o cer, prin tine, de la Flow A:** pentru fiecare din cele 40 V0 (nu doar cele 3 pe care le-am verificat direct în cod), confirmarea trebuie să arate:
1. Prag numeric explicit, disclosed, pentru criteriul de detecție/clasificare.
2. Orizont fix, pre-declarat, pentru rezultat (nu "la un moment dat").
3. Populație/numitor declarat — regula exactă pentru ce constituie o instanță.
4. Prag de clasificare a reacției (continuare/reversal/stall) declarat, nu subiectiv.
5. Niciun parametru liber lăsat de ales la momentul confirmării.

Dacă vreunul din cele 37 pe care nu le-am văzut e narativ pe oricare din aceste 5 puncte, ACEA ipoteză specifică nu merge direct la confirmare — se operaționalizează întâi, separat, înainte de a atinge datele noi, ca să nu se repete exact tiparul "operaționalizare după ce vezi ce iese convenabil".

### [v1.1] Regula de proveniență pentru parametrii împrumutați din convențiile deja existente

**Întrebarea CEO care a declanșat asta:** dacă Flow A operaționalizează o ipoteză narativă preluând un prag deja folosit în alt script (ex. `REACTION_THRESHOLD=1.0×ATR`, `REVISIT_HORIZON=480`), fără să privească datele noi — e suficient ca protecție?

**Nu, nu ca regulă generală — dar nici insuficient universal. Depinde de proveniența cifrei împrumutate, iar protecția "fără să privească datele" nu verifică asta.** "A privi datele noi" e forma cea mai evidentă de contaminare; nu e singura. O convenție deja folosită poate fi ea însăși — subtil, fără căutare formală de parametri — informată de faptul că "a mers" pe fereastra 2022-2025, chiar dacă nimeni n-a rulat explicit o căutare de grilă.

**Testul pe care îl cer, per parametru împrumutat, înainte de a-l accepta:**

1. **E o convenție generică de normalizare/rotunjire** (1,0×ATR ca "o unitate de volatilitate locală"; "N zile de tranzacționare" ca orizont calendaristic; 50%/61,8% ca procent standard) **care ar fi fost alegerea naturală indiferent de ce fereastră de piață s-ar fi examinat vreodată** → acceptabilă pentru reutilizare.
2. **Sau a fost vreodată cifra specifică calculată, comparată, sau aleasă pe baza oricărui rezultat cuantificat rulat pe 2022-2025** (backtest, hit-rate, orice) — chiar informal, chiar fără a fi numit "optimizare" → **nu e acceptabilă fără o sursă independentă** (ex. o convenție deja publicată în literatura ICT, care predatează acest proiect) — sau ipoteza rezultată se marchează explicit cu rezerva că parametrizarea ei păstrează o dependență reziduală de fereastra adiacentă confirmării.
3. **Pentru cazuri la limită:** cere o justificare explicită, independentă de orice calcul pe 2022-2025 ("e o definiție standard de analiză tehnică, folosită independent de instrument/fereastră" — nu "așa a mers la E010").

**Verificare suplimentară obligatorie, nu opțională:** pentru orice parametru împrumutat conform punctului 1, cere raportarea rezultatului sub **1-2 alternative la fel de generice** (ex. 0,75×ATR și 1,25×ATR în loc de doar 1,0×ATR). Dacă rezultatul rămâne calitativ stabil pe acest interval, alegerea specifică nu era load-bearing. Dacă rezultatul se schimbă calitativ între aceste alternative la fel de rezonabile, cifra "generică" ascunde de fapt o potrivire fină, chiar dacă neintenționată.

**Cerință de disclosure:** fiecare parametru împrumutat trebuie să vină cu proveniența lui explicită scrisă ("1,0×ATR, reutilizat din `_profile.py`, justificat ca unitate generică de volatilitate, niciodată calculat sau comparat împotriva vreunui rezultat de backtest specific") — nu reutilizare tăcută.

## 3. Pragul M5 — regula de nedeterminare

**Regula, în două straturi:**

1. **Per-tranzacție:** dacă bara decisivă (cea în care s-ar declanșa ieșirea) conține ATÂT nivelul de stop CÂT ȘI nivelul de țintă în intervalul ei [low, high], rezultatul acelei tranzacții e **NEDETERMINAT** — nu se numără nici ca win, nici ca loss. Rata de excludere se raportează explicit (nu se ascunde).
2. **Per-ipoteză (poarta de rezolvabilitate):** calculează fracția de tranzacții nedeterminate din tot eșantionul acelei ipoteze la M5. **Dacă fracția depășește 25%**, ipoteza se marchează **NOT-RESOLVABLE-AT-M5** — subeșantionul rămas ("norocos", fără ambiguitate) nu mai e reprezentativ, iar o rată de câștig calculată doar pe el ar fi părtinitoare, nu doar incompletă.

**Prag de pre-screening, din distribuția pe care o livrează Data Acquisition (mediană + IQR per sesiune):**
- Dacă distanța stop-ului **depășește percentila 75 (Q3)** a amplitudinii high-low pe sesiunea relevantă → în general rezolvabilă; se rulează testul per-tranzacție de mai sus ca verificare, nu ca presupunere.
- Dacă distanța stop-ului **e sub percentila 25 (Q1)** → marchează **NOT-RESOLVABLE-AT-M5** direct, fără a rula testul complet — la această scară, majoritatea barelor ar cuprinde singure toată distanța de stop.
- Între Q1 și Q3 → rulează testul per-tranzacție; decizia finală o dă fracția de 25% de mai sus, nu presupunerea inițială.

**Ce se întâmplă cu ipotezele NOT-RESOLVABLE-AT-M5:** **nu se exclud definitiv** — se marchează explicit ca atare, ca un status informativ (analog UNRESOLVED), și rămân eligibile pentru testare la o rezoluție mai grosieră (M15, inclusiv noii 11 ani M15 extinși) unde distanța de stop e confortabil rezolvabilă față de amplitudinea barei. Nu se forțează un rezultat dintr-un subeșantion părtinitor doar pentru că există date.

## Context — problema de măsurare pe brut vs. net (notat, nu rezolvat aici)

Consemnat: metricile de fragilitate t1/t3/t5 calculate pe profit brut, nu net, înseamnă că orice sistem cu flux brut mare și marjă subțire va apărea artificial nefragil. Voi citi orice caracterizare anterioară de fragilitate — inclusiv cea a Flow C — cu această rezervă explicită, până când Research Lab livrează distribuția recalculată pe net. Nu încerc s-o repar aici.

---

**Nu s-a modificat niciun artefact Flow A, Data Acquisition, sau Research Lab. Acest document e regula, nu execuția ei.**

**E015-V1 rămâne suspendat. Certificarea S18 rămâne în coadă. Nimic pe DC-0003/DC-0004.**

**Statistician se oprește aici, în așteptarea hărții de regimuri și a confirmării de operaționalizare pentru cele 37 V0 nevăzute.**
