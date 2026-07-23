# ALPHA — STARE SESIUNE (ultima actualizare 2026-07-22)

## Pozitie replay (punct de pornire pentru sesiunea urmatoare)
- Simbol: OANDA:XAUUSD
- Timeframe principal: **M15**
- Replay: **2025-08-19 22:15 UTC**, manual, autoplay OFF, pre-cutoff
- Cutoff holdout: 2025-10-23. La reluare: `replay_stop` INAINTE de re-seek (defect de stale-state),
  apoi verifica `replay_status` — pozitia persista corect intre reluari in aceeasi zi de lucru.
- `replay_step` sare automat peste weekend si peste pauza zilnica de rollover (21:00-22:00 UTC)
  intr-un singur step — comportament normal al instrumentului (piata inchisa), nu bug.
- Artefact tehnic cunoscut: ocazional primul `data_get_ohlcv` dupa un step intoarce OHLC identic
  + volum fractionar (stare de citire intermediara, nu bara reala) — re-interogheaza o data fara
  alt step, se rezolva mereu.

## METODOLOGIE (directiva CEO, 2026-07-22 — actualizata a doua oara, inlocuieste jurnalul bara-cu-bara)
Comporta-te ca un trader profesionist cu 20+ ani experienta care observa piata in timp real. NU
scopul e sa gasesti tranzactii, sa faci predictii, sau sa demonstrezi ca ai analizat fiecare
lumanare. Scopul e sa observi exact cum ar face un trader foarte experimentat.
- Timeframe principal de lucru: **M15**. Context 4H si 1H mentinut permanent.
- Avanseaza natural prin Replay FARA sa documentezi fiecare bara. Daca piata e normala, continua
  pur si simplu observarea, in tacere.
- Coboara pe 5M apoi 1M DOAR la un eveniment care merita investigat: schimbare de comportament,
  impuls neobisnuit, absorbtie, comprimare prelungita, expansiune neasteptata, reactie importanta
  intr-o zona relevanta, sau orice alt fenomen ce atrage atentia unui trader experimentat.
- In investigatie, intreaba-te: Ce se intampla cu adevarat? E obisnuit sau neobisnuit? Am mai
  vazut acest tipar? Merita urmarit in viitor?
- Dupa investigatie, DOAR doua rezultate posibile:
  1. Fenomenul justifica cercetare -> creeaza Discovery Candidate nou, documenteaza-l.
  2. Nu justifica un DC -> NU se pierde -> inregistreaza-l in `OBSERVATION_REGISTRY.md` ca
     observatie bruta pentru comparatii viitoare.
- Scrie DOAR cand: apare eveniment relevant / finalizezi o investigatie / creezi un DC / adaugi
  o intrare in Observation Registry / salvezi un checkpoint de sesiune. In rest, tacere completa —
  nicio explicatie lunga in timpul observatiei pure.

## ALPHA DISCOVERY OPTIMIZATION v2 (directiva CEO, 2026-07-23)
Rigoarea metodologiei de mai sus RAMANE NESCHIMBATA. Aceasta sectiune adauga un filtru INTERN
inainte de a decide sa cobori pe 5M/1M — nu reduce investigatiile importante, nu muta
responsabilitati catre Red Team. Optimizeaza DOAR decizia de a investiga, tintind raportul
informatie noua descoperita / timp de cercetare consumat.

Inainte de orice coborare pe M5/M1, raspunde la:
1. Este acest fenomen cu adevarat diferit de variatia normala?
2. Seamana cu ceva deja documentat in Discovery Candidates sau Observation Registry?
3. Exista suficiente motive sa cred ca poate produce informatie noua?

- NU -> continua observatia FARA investigatie.
- NU SUNT SIGUR -> urmareste inca 1-2 lumanari M15 inainte sa decizi.
- DA -> abia atunci coboara pe M5 si M1.

Memoria acumulata (DC-uri + Observation Registry + jurnal) este PRIMUL filtru. NU investiga automat
fiecare: impuls mare, volum mare, ora 00:00 UTC, ora 12:30 UTC, deschidere Londra, deschidere NY —
acestea sunt deja fenomene cunoscute si documentate (vezi DC-0008/DC-0010/DC-0012 si Observation
Registry). Investigheaza-le din nou DOAR daca observi ceva material diferit fata de instantele deja
documentate (ex: magnitudine mult peste orice instanta anterioara, o zona/context nou, un mecanism
de constructie care nu se potriveste niciunei forme deja catalogate).

## Jurnal de evenimente (2025-08-01 -> 2025-08-06, pre-cutoff)
- **08-01 03:40** — ruptura M15 (6.8pt, vol 3862) construita dintr-o SINGURA lumanare M1 (~60s,
  vol 459 vs baseline 163-219), restul minutelor la baseline. "Concentrare instantanee."
- **08-01 12:30** — puseu NFP (calendar: prima vineri a lunii, 12:30 UTC = ora standard NFP): M15
  39pt/vol 24005; pe M1, volum ridicat sustinut aproape fiecare minut ~15 min, 3 leg-uri, FARA
  concentrare intr-un minut — anatomie opusa fata de 03:40. -> **DC-0008** (contrast concentrare
  instantanee vs volum sustinut).
- **08-01 19:30** — a doua ruptura (3351->3361, vol 9844), anatomie M1 identica cu tipul
  "sustinut", DAR fara catalizator de calendar evident -> addendum A la DC-0008 (slabeste ipoteza
  "doar la stiri programate").
- **08-01 20:00 -> 08-03 22:00** (weekend) — consolidare post-NFP lunga, volum monoton descrescator
  la baseline; gap de weekend (+1.9pt) umplut aproape imediat -> confirma OBS-0015, nu e nou.
- **08-01 19:39 -> 08-04 07:15** — zona 3361.0-3363.6 testata de 7 ori peste 3 zile calendaristice
  (inclusiv weekend), respinsa mereu, ultima respingere (07:15) cea mai puternica din secventa
  -> **DC-0009** (banda de rezistenta multi-zi).
- **08-04 09:15-09:30** — inca 2 teste (8, 9) ale aceleiasi benzi, tot fara ruptura -> addendum B
  la DC-0009.
- **08-04 11:00** — ruptura finala a benzii dupa 9 teste (vol record 4201), confirmata de 3 bare
  de continuare fara retest -> addendum B (continuare) la DC-0009.
- **08-04 12:30** — primul retest dupa ruptura: scurta patrundere inapoi in banda, reclaim decisiv
  in 15 min -> addendum C la DC-0009 (rezistenta sparta = suport, prima confirmare).
- **08-05 09:30-10:00** — AL DOILEA retest al aceleiasi benzi: sparge decisiv SUB banda, ramane
  dedesubt, comportament OPUS primului retest -> addendum D la DC-0009 (contrazice addendum C:
  "rezistenta sparta -> suport" nu e proprietate durabila la retestari ulterioare).
- **08-05 11:45-13:00** — a treia interactie cu aceeasi banda: traversare curata, fara reactie
  vizibila — zona pare sa-si fi pierdut relevanta dupa a doua interactie esuata (context, fara
  addendum nou).
- **08-06 15:30** — miscare brusca jos (range 6.5pt, vol de varf 8593) cu recuperare partiala in
  aceeasi bara — posibil sweep rapid, neinvestigat pe M1, de urmarit daca se repeta.
- **08-07 00:00** — bara cu wick adanc (5.5pt) dar close aproape de maxim, vol 2x baseline;
  anatomie M1 = coborare treptata pe volum moderat + recuperare pe volum mult mai mic (nu sweep
  clasic) -> inregistrat in `OBSERVATION_REGISTRY.md`.
- **08-07 00:15-01:15** — volumul continua sa creasca in loc sa se stinga (H1 00:00-01:00: 30168
  vs baseline orar 4494-6393, ~5-7x), miscare directionala reala ~13pt sustinuta >1h, exact in ora
  stabilita direct (Aug 4-6) ca cea mai liniștita a zilei -> **DC-0010** (ruptura orei liniștite).

## Nota metodologica: 2 intrari in Observation Registry create in aceasta iteratie inainte de
promovarea la DC-0010 (pastrate ca notite brute, nu sterse).

- **08-07 01:15-05:00** — miscarea DC-0010 s-a stins treptat (varf 3386.175 la 01:15-01:30, apoi
  volum in declin), dar orele 02:00-05:00 s-au stabilizat la 11775-14883/ora — de 2-3x baseline-ul
  de 3 zile (4500-6400), NU o revenire completa la normal. Fara eveniment nou distinct.
- **08-07 05:00-06:00** — a doua ora cu volum de varf (32049, comparabil cu ora DC-0010 initiala),
  declin ordonat de 7.4pt fara mecanism nou (aceeasi constructie "sustinuta"). Sesiunea intreaga de
  azi pare sa ruleze mai fierbinte decat baseline-ul stabilit, nu doar ora 00:00-01:00 izolat ->
  **addendum A la DC-0010** (reformuleaza fenomenul de la "o ora anume" la "toata sesiunea").
- **08-07 06:30** — compresie M1 de 10 min urmata de ruptura curata in ultimele 5 min; tipar deja
  cunoscut (LINE-A compression), fara nimic nou de inregistrat.
- **08-07 07:00-08:00** — continuare puternica pana la 3397.58 (deschidere Londra), apoi
  **reversal masiv** la 08:00 (16.5pt, vol 16000): declin ordonat pe M1, volum uniform ~500-1500
  pe toate cele 15 minute — constructie "sustinuta" deja cunoscuta, fara mecanism nou. Doar
  schimbare de trend obisnuita la Londra, nu justifica DC/registry.

## Ce ramane neinvestigat / de urmarit
- Miscarile directionale sustinute de la NY open din 4, 5 si 6 august (13:00-15:00 UTC, volum mare
  descrescator) nu au fost coborate pe M1 pentru confirmarea anatomiei "sustinut" — doar profilul
  M15 se potriveste cu DC-0008.
- Sweep-ul rapid de la 08-06 15:30 UTC neinvestigat pe M1.

- **08-07 09:15-13:45** — consolidare Londra apoi impuls la deschiderea NY (13:30, vol 16485),
  volum variabil intre normal si ridicat, fara eveniment nou pana la 13:45.
- **08-07 14:08** — **sweep pe o singura lumanare M1** (10pt in 60s, 3384.8->3374.77, vol 2416
  ~1.5-3x vecinii), reclaim imediat urmatorul minut, apoi continuare la maxime NOI de sesiune
  (3390.31) in urmatoarele 6 minute — nu doar reclaim, ci depasire clara a nivelului pre-sweep
  -> **DC-0011** (sweep + reclaim + continuare peste pre-sweep, distinct de simplu reclaim-si-stall).

- **08-07 14:15-16:15** — dupa DC-0011, volatilitate ridicata inca 3 bare (18752, 14997, 11687)
  apoi normalizare treptata (9012->6493->5843->5892). Sesiunea "fierbinte" pare sa se fi consumat
  in sfarsit dupa impulsul de la 14:00. Fara eveniment nou.

- **08-07 16:15-18:15** — banda ~3384-3393, volum normal (3499-9882), fara eveniment nou.
  Sesiunea a revenit definitiv la comportament ordinar dupa dimineata volatila.

- **08-07 18:15-19:15** — banda linistita ~3387-3392, fara eveniment.
- **08-07 19:30-20:15** — impuls spre 3400 (round number), consolidare/magnet la cifra rotunda
  (3396.9-3401.9), spargere modesta la 20:15 (close 3401.34, vol descrescand) — confirma tiparul
  deja cunoscut (OBS-0010 round numbers), fara nimic nou.

- **08-07 20:30-20:45** — retragere de la 3400, fara eveniment.
- **08-07 21:00-22:00** — a 4-a pauza de rollover confirmata. De data asta redeschiderea a fost
  **choppy/whipsaw** (range 18.4pt, vol 3569, fiecare minut M1 oscilant cu volum sub 400) — diferit
  de gap-urile curate din zilele anterioare -> inregistrat in `OBSERVATION_REGISTRY.md`.
- **08-07 22:00-22:45** — continuare choppy post-reopen, fara eveniment nou distinct.

- **08-07 22:45-23:59** — coada choppy post-rollover se stinge treptat, volum revenit la normal
  (973-2877) spre miezul noptii. Fara eveniment nou.
- **08-08 00:00-00:15** — **absorbtie clara**: volum 23718 (M15) / 650-2150 pe fiecare minut M1,
  dar range doar 4.75pt, fara trend — a doua zi consecutiva in care ora 00:00-01:00 UTC iese din
  baseline-ul stabilit (DC-0010 ieri a fost directional, azi e absorbtie pura) -> **DC-0012**.

- **08-08 00:30-01:15** — absorbtia s-a rezolvat imediat intr-un breakdown (00:30, 9pt, vol 22651)
  -> **addendum A la DC-0012**. Ora 00:00-01:00 UTC ramane extrem de activa 3 zile la rand acum
  (6 bare M15 consecutive cu vol 13456-23718 in aceasta a 3-a zi) — tipar recurent, nu izolat,
  intareste DC-0010/DC-0012 fara sa justifice inca un DC separat.

- **08-08 01:15-02:15** — banda ~3382-3390, volum ramas ridicat (9668-13584), fara sa revina la
  baseline-ul obisnuit de asia. Consolidare, fara eveniment nou.

- **08-08 02:15-03:15** — continuare, volum ramane robust ridicat (11977-17686) peste 3+ ore
  neintrerupt acum, urcare treptata 3383->3399. Reintareste (fara addendum nou) observatia deja
  facuta ca intreaga sesiune 08-08 ruleaza mai fierbinte decat baseline-ul stabilit.

- **08-08 03:15-04:30** — banda ~3390-3399, volum ramas ridicat dar usor descrescator
  (9510-13756), consolidare fara trend clar. Fara eveniment nou.

- **08-08 04:30-05:45** — volum ramas robust (12796-16989) peste 5+ ore neintrerupt acum (de la
  00:00). Aceasta e o depasire mult mai lunga si sustinuta a baseline-ului decat cea din 08-07
  (DC-0010) — posibil regim de volatilitate mai larg pentru aceasta zi/perioada, nu doar o ora
  izolata. Notat ca observatie de context, fara addendum nou (reintareste tema deja documentata).

- **08-08 05:30-08:30** — volum continua sa fluctueze intre foarte ridicat (18452-26494) si
  moderat (8158-11044), fara sa revina la baseline-ul de asia din 08-04/08-05/08-06. Acum peste
  8 ore neintrerupte de activitate peste normal (de la 00:00). Fara eveniment nou distinct.

- **08-08 08:45-10:15** — consolidare in jurul 3395-3401.5 (Londra), volum ramas ridicat
  (12484-20471), acum peste 10 ore neintrerupte de activitate peste baseline. Fara eveniment nou.

- **08-08 10:15-11:30** — declin lent Londra 3397->3382, apoi reviriment, volum ramas ridicat
  constant (14551-26266). Peste 11 ore de activitate anormala acum, fara semn de revenire la
  baseline. Fara eveniment nou distinct.

- **08-08 11:30-13:00** — nota tehnica: o bara (11:45-12:00) a fost sarita de instrument la un
  singur step (current_date a avansat direct 11:30->12:00), fara pierdere semnificativa de
  informatie (context deja stabilit). Volum ramas extrem de ridicat (22839-30129), pret volatil
  intre 3385-3402.6. Peste 12 ore de activitate anormala acum. Fara eveniment nou distinct.

- **08-08 12:45-17:45** — replay resetat tehnic intre ture (target CDP schimbat, replay oprit);
  repozitionat la 12:45 din checkpoint, fara pierdere de continut relevant. 12:45-17:00: activitate
  ridicata a continuat, apoi s-a domolit treptat spre normal (~7000-10000) — prima revenire clara
  la un nivel obisnuit dupa episodul extins inceput la 00:00. 17:59: al doilea sweep de un minut
  cu reclaim si extindere (19.4pt in 60s, urmat de range 27.4pt/vol 36149 pe bara urmatoare) ->
  **addendum A la DC-0011**.

- **08-08 18:15-21:00** — activitate ridicata a continuat inca ~2 ore (8500-19000), apoi a scazut
  progresiv spre nivelul cel mai jos observat pe toata durata episodului (1572 la 20:45) —
  posibilul sfarsit al perioadei extinse de activitate ridicata incepute la 00:00 (in esantionul
  local observat, nu confirmat ca revenire durabila).

- **08-08 21:00 -> 08-10 22:00** (weekend) — gap mic la redeschidere (+1.99pt), majoritar
  retras in prima bara; comportament similar cu observatii anterioare de gap de weekend
  (fara comparatie riguroasa facuta aici).
- **08-10 22:00 -> 08-11 00:30** — sesiune Asia foarte calma (volum sub 3000 aproape peste tot),
  un mic impuls izolat la 00:15 (vol 9544, range 5.2pt) fara continuare clara. Fara eveniment nou.

- **08-11 00:30-02:45** — un declin de 16.4pt la 01:00 (vol 17530, distribuit uniform pe M5,
  fara concentrare intr-un candle) urmat de consolidare 3369-3380, volum revenit spre moderat
  (4887-10705). Morfologie asemanatoare tipului deja documentat (constructie distribuita), fara
  element nou; nu s-a adaugat inregistrare noua.

- **08-11 02:45-04:30** — banda ~3374-3380, volum scazut (3294-5063). Fara eveniment.

- **08-11 04:30-06:15** — banda ~3372-3380, volum foarte scazut (2180-5991), cea mai calma
  fereastra observata in acest esantion local pentru sesiunea de dupa deschiderea saptamanii.
  Fara eveniment.

- **08-11 06:15-07:45** — declin lent 3374->3358.8 (tranzitia spre Londra), volum moderat
  (5743-11005), fara acceleratie sau reactie marcanta. Fara eveniment.

- **08-11 07:45-09:15** — continuare declin usor Londra, 3363->3356, volum moderat
  (5167-12147). Fara reactie marcanta la vreo zona. Fara eveniment.

- **08-11 09:15-10:45** — zig-zag in banda ~3353-3364, volum moderat (6098-8075). Fara eveniment.

- **08-11 10:45-12:15** — declin usor 3361->3350, apoi mica revenire, volum moderat
  (4183-9972). Fara eveniment.

- **08-11 12:15-13:45** — zig-zag in banda ~3344-3358 (tranzitie spre NY), volum moderat
  (9209-13203, usor peste fereastra anterioara). Fara reactie marcanta. Fara eveniment.

- **08-11 13:45-15:15** — declin treptat NY, 3358->3344, volum moderat (4524-12854). Fara
  reactie marcanta. Fara eveniment.

- **08-11 15:15-17:30** — consolidare stransa ~3342-3350.4, volum moderat (5303-9353). Fara
  eveniment.
- **08-11 17:30-17:45** — sweep sub podeaua consolidarii (3341.155), dar reclaim-ul distribuit
  pe ~5 lumanari M1 consecutive (volum material descrescator pe fiecare, nu o singura lumanare
  dominanta), apoi extindere peste plafonul pre-sweep pana la 3358.65 — acelasi rezultat ca
  DC-0011 (sweep + reclaim + extindere peste pre-sweep), dar constructie reclaim-ului sustinuta,
  nu concentrata intr-un minut -> **addendum B la DC-0011**.

- **08-11 17:45-19:30** — retragere usoara si consolidare dupa impulsul de la 17:30-17:45,
  banda ~3352-3359, volum in scadere spre normal (2933-7367). Fara eveniment.

- **08-11 19:30-21:00** — declin usor 3354->3343, volum in scadere spre normal (1803-7213). Fara
  eveniment.
- **08-11 21:00-22:00** — a 5-a pauza de rollover confirmata (jump 75min). Redeschidere curata,
  fara gap notabil, volum scazut (959). Fara eveniment.

- **08-11 22:15-23:45** — banda linistita ~3343-3349, volum foarte scazut (968-1557), Asia
  standard. Fara eveniment. Se apropie ora 00:00-01:00 UTC (08-12), fereastra deja marcata in
  esantionul local anterior ca punct de interes recurent (DC-0010/DC-0012) — de urmarit cu atentie
  la reluare, fara a presupune ca se va repeta.

- **08-11 23:45 -> 08-12 01:00** — ora 00:00-01:00 UTC (flagata anterior ca punct de interes)
  a rulat ORDINAR de data asta — volum 2330-3428, fara absorbtie, fara impuls directional
  (contrasteaza cu 08-07/08-08) -> inregistrat in `OBSERVATION_REGISTRY.md` ca instanta care
  contrazice, nu confirma, esantionul anterior.

- **08-12 01:00-02:15** — banda ~3346-3357, volum moderat (2088-4134). Fara eveniment.

- **08-12 02:15-03:30** — banda ~3350-3355, volum scazut-moderat (2225-3552). Fara eveniment.

- **08-12 03:30-04:45** — banda ~3348-3355, volum scazut (1523-2384), cea mai calma fereastra
  a acestei sesiuni asiatice. Fara eveniment.

- **08-12 04:45-06:00** — banda ~3350-3356, volum scazut (2048-3534). Fara eveniment.

- **08-12 06:00-07:15** — tranzitie spre Londra, zig-zag ~3342-3355, volum moderat
  (4052-7313), fara acceleratie sau reactie marcanta la vreo zona. Fara eveniment.

- **08-12 07:15-08:30** — Londra, zig-zag ~3348-3358, volum normal (2889-4129). Fara eveniment.

- **08-12 08:30-09:45** — Londra, banda ~3346-3352, volum scazut-moderat (2017-4153). Fara
  eveniment.

- **08-12 09:45-11:00** — declin usor 3348->3345, volum scazut-moderat (2054-3121). Fara
  eveniment.

- **08-12 11:00-12:00** — zig-zag 3336-3348, volum moderat (3195-6339), fara reactie marcanta.
  Fara eveniment.

- **08-12 12:00-12:30** — declin usor 3347->3339, volum moderat (4693-5084). Fara eveniment.
- **08-12 12:30-12:45** — ruptura 15.1pt/vol 17109; pe M1, deplasarea INTREAGA concentrata
  intr-un SINGUR minut (13.85pt in 60s, vol 2379), urmata de 14 min de oscilatie/consolidare la
  noul nivel (nici revenire, nici continuare) — aceeasi ora 12:30 UTC ca DC-0008 (NFP), dar zi
  diferita (marti, nu vineri) si constructie diferita (concentrata, nu sustinuta) -> **addendum B
  la DC-0008**.
- **08-12 12:45-13:30** — activitate ramasa ridicata (7896-12085) inca 3 bare dupa impuls, apoi
  normalizare treptata. Fara mecanism nou.

- **08-12 13:30-14:30** — deschidere NY, declin sustinut 3355->3335, volum ridicat pe tot
  intervalul (12104-20872), profil consistent cu deschiderile NY deja documentate anterior in
  esantion. Fara mecanism nou.

- **08-12 14:30-15:30** — revenire 3335->3359, volum ramas moderat-ridicat (6841-12506), fara
  reactie marcanta la vreo zona anume. Fara mecanism nou.

- **08-12 15:30-16:45** — normalizare treptata dupa dimineata NY volatila, volum in scadere
  (5215-12015), banda ~3345-3358. Fara eveniment.

- **08-12 16:45-18:00** — banda linistita ~3346-3350, volum scazut (3209-5103). Fara eveniment.

- **08-12 18:00-19:15** — banda linistita ~3345-3350, volum scazut (3560-4364). Fara eveniment.

- **08-12 19:15-20:30** — banda linistita ~3346-3349, volum in scadere spre normal
  (1119-3491). Fara eveniment. Se apropie pauza de rollover (21:00-22:00 UTC).

- **08-12 20:30-21:00** — banda linistita, volum foarte scazut (768-1046). Fara eveniment.
- **08-12 21:00-22:00** — a 6-a pauza de rollover confirmata (jump 75min). Redeschidere curata,
  fara gap notabil, volum foarte scazut (353). Fara eveniment.

- **08-12 22:15-23:30** — banda linistita ~3350-3354, volum foarte scazut (351-710), Asia
  standard. Fara eveniment.

- **08-12 23:30 -> 08-13 01:00** — ora 00:00-01:00 UTC ordinara din nou (a doua zi consecutiva),
  volum 2919-3892, fara absorbtie, fara impuls. Esantion local acum 2-din-4 anomalos, 2-din-4
  ordinar la aceasta ora — nu s-a adaugat intrare noua in registry (acelasi rezultat deja notat).

- **08-13 01:00-02:15** — banda ~3343-3352, volum moderat (3553-4495). Fara eveniment.

- **08-13 02:15-03:30** — banda ~3349-3354, volum scazut-moderat (2177-3461). Fara eveniment.

- **08-13 03:30-04:45** — banda linistita ~3348-3352, volum foarte scazut (615-1758), cea mai
  calma fereastra a acestei sesiuni. Fara eveniment.

- **08-13 04:45-06:15** — mica scadere-revenire 3351->3346->3354 la 05:30-06:00 (vol de varf
  5338, ~3-5x local), fara acceleratie sustinuta sau reactie clara la o zona; tranzitie spre
  Londra. Fara mecanism distinct de investigat.

- **08-13 06:15-07:30** — Londra, urcare treptata 3354->3360, volum moderat (4052-5367). Fara
  eveniment.

- **08-13 07:30-08:45** — Londra, zig-zag ~3352-3360, volum moderat (3361-4702). Fara eveniment.

- **08-13 08:45-10:00** — Londra, urcare treptata 3359->3366, volum moderat (2496-5571). Fara
  eveniment.

- **08-13 10:00-11:15** — banda ~3361-3367, volum scazut-moderat (1774-3991). Fara eveniment.

- **08-13 11:15-12:15** — zig-zag ~3357-3363, volum moderat (4215-5775). Fara eveniment.
- **08-13 12:30-13:15** — fereastra 12:30 UTC (a treia instanta din esantion) ruleaza ORDINAR
  a treia oara: volum 6293-7975, fara concentrare, fara sustinere, fara reactie -> inregistrat
  in `OBSERVATION_REGISTRY.md` ca instanta care contrasteaza cu cele 2 anterioare (NFP-sustinut
  08-01, concentrat 08-12).

- **08-13 13:15-14:30** — deschidere NY, urcare 3357->3367, volum ridicat (5300-9854), profil
  consistent cu deschiderile NY deja documentate. Fara mecanism nou.

- **08-13 14:30-15:45** — declin usor 3365->3355, volum moderat (5058-7625). Fara eveniment.

- **08-13 15:45-17:00** — banda ~3357-3361, volum in scadere spre normal (2569-4621). Fara
  eveniment.

- **08-13 17:00-18:00** — banda ~3352-3359, volum scazut (2609-4656). Fara eveniment.

- **08-13 18:00-19:15** — banda linistita ~3350-3354, volum scazut (1399-3533). Fara eveniment.

- **08-13 19:15-20:30** — banda linistita ~3354-3359, volum in scadere spre foarte scazut
  (511-2560). Fara eveniment. Se apropie pauza de rollover.

- **08-13 20:30-21:00** — banda linistita, volum foarte scazut (341-505). Fara eveniment.
- **08-13 21:00-22:00** — a 7-a pauza de rollover confirmata (jump 75min). Redeschidere curata,
  fara gap notabil, volum foarte scazut (301). Fara eveniment.

- **08-13 22:15-23:30** — banda linistita ~3357-3361, volum scazut (254-1272), Asia standard.
  Fara eveniment.

- **08-13 23:30 -> 08-14 00:00** — Asia standard, fara eveniment.
- **08-14 00:00-01:15** — a patra instanta a orei 00:00-01:00 UTC: miscare directionala moderata
  3363->3375 (~12pt), volum 2-4x local (2552-4216), sub extremele anterioare (DC-0010/DC-0012).
  Esantion acum: 2 extreme (directional/absorbtie), 2 ordinare, 1 moderata -> inregistrat in
  `OBSERVATION_REGISTRY.md`, nicio caracterizare unica nu se sustine pentru aceasta ora.

- **08-14 01:15-02:15** — banda ~3365-3370, volum moderat (3195-3741). Fara eveniment.

- **08-14 02:15-03:30** — declin usor 3368->3358, volum moderat (2619-4992). Fara eveniment.

- **08-14 03:30-04:45** — banda linistita ~3357-3362, volum scazut (1828-3856). Fara eveniment.

- **08-14 04:45-06:00** — banda ~3356-3362, volum scazut (1501-3305). Fara eveniment.

- **08-14 06:00-07:00** — tranzitie spre Londra, zig-zag ~3356-3362, volum moderat
  (3355-5164). Fara eveniment.

- **08-14 07:00-08:15** — declin Londra 3362->3341 (~21pt), volum moderat (5043-7762). Pe M5,
  constructie distribuita uniform (1439-2204 pe fiecare candel, fara varf dominant) — morfologie
  deja cunoscuta, fara element nou. Nu s-a adaugat inregistrare noua.

- **08-14 08:15-09:30** — revenire partiala 3341->3356, volum moderat (3320-5230). Fara eveniment.

- **08-14 09:30-10:45** — banda ~3353-3359, volum scazut-moderat (3099-3394). Fara eveniment.

- **08-14 10:45-12:00** — banda ~3352-3357, volum scazut (1329-3703). Fara eveniment.

- **08-14 12:00-12:30** — banda ~3352-3358, volum moderat (3720-3928). Fara eveniment.
- **08-14 12:30-12:45** — a patra instanta 12:30 UTC din esantion: sweep de 11.4pt concentrat
  intr-un SINGUR minut (vol 14027 pe M15), urmat de recuperare partiala, choppy, FARA reclaim
  curat si FARA extindere peste nivelul pre-sweep -> **addendum C la DC-0008** (patru instante,
  patru rezultate diferite la aceeasi ora, fara caracterizare unica valabila).
- **08-14 12:45-13:00** — activitate ramasa ridicata (10355) dupa impuls, fara mecanism nou.

- **08-14 13:00-14:00** — deschidere NY, declin 3353->3344, volum ridicat (8321-11577), profil
  consistent cu deschiderile NY deja documentate. Fara mecanism nou.

- **08-14 14:00-15:00** — continuare declin NY 3344->3341, volum ramas ridicat dar in scadere
  treptata (7482-11457). Fara mecanism nou.

- **08-14 15:00-16:15** — normalizare treptata dupa dimineata NY volatila, volum in scadere
  (3493-8379), banda ~3333-3343. Fara eveniment.

- **08-14 16:15-17:30** — banda ~3330-3338, volum moderat (3868-6623). Fara eveniment.

- **08-14 17:30-18:45** — banda linistita ~3336-3339, volum scazut (2475-3741). Fara eveniment.

- **08-14 18:45-20:00** — banda linistita ~3338-3341, volum scazut (1095-2456). Fara eveniment.

- **08-14 20:00-21:00** — banda linistita, volum foarte scazut (632-1096). Fara eveniment.
- **08-14 21:00-22:00** — a 8-a pauza de rollover confirmata (jump 75min). Redeschidere curata,
  fara gap notabil, volum foarte scazut (361). Fara eveniment.

- **08-14 22:15-23:30** — banda linistita ~3332-3335, volum foarte scazut (503-1104), Asia
  standard. Fara eveniment.

- **08-14 23:30 -> 08-15 01:00** — ora 00:00-01:00 UTC ordinara din nou (a treia zi ordinara din
  esantion), volum 1429-2625, fara absorbtie, fara impuls. Fara intrare noua in registry (acelasi
  rezultat deja documentat).

- **08-15 01:00-02:15** — banda ~3333-3340, volum scazut-moderat (2167-3136). Fara eveniment.

- **08-15 02:15-03:30** — banda ~3336-3341, volum scazut (1253-1822). Fara eveniment.

- **08-15 03:30-04:45** — banda ~3340-3346, volum scazut (1088-1945). Fara eveniment.

- **08-15 04:45-06:00** — banda ~3342-3348, volum scazut (1162-2036). Fara eveniment.

- **08-15 06:00-07:15** — tranzitie spre Londra, banda ~3340-3344, volum scazut (1168-2382).
  Fara eveniment.

- **08-15 07:15-08:30** — Londra, zig-zag ~3339-3348, volum moderat (2402-3531). Fara eveniment.

- **08-15 08:30-09:45** — Londra, banda ~3338-3345, volum scazut-moderat (2169-2996). Fara
  eveniment.

- **08-15 09:45-11:00** — declin usor 3342->3338, volum scazut-moderat (1541-3091). Fara
  eveniment.

- **08-15 11:00-12:00** — zig-zag ~3337-3344, volum moderat (2182-3781). Fara eveniment.

- **08-15 12:00-12:30** — banda ~3336-3342, volum moderat (2751-5451). Fara eveniment.
- **08-15 12:30-12:45** — a cincea instanta 12:30 UTC din esantion: urcare 3333.6->3343.845
  (10.25pt, vol 9180), constructie SUSTINUTA (volum distribuit uniform pe toate cele 3 bare M5 si
  aproape toate cele 15 minute M1) -> **addendum D la DC-0008** (a doua zi de vineri cu constructie
  sustinuta, distinct de cele 3 instante zile-lucratoare cu concentrare/ordinar).
- **08-15 12:45-13:00** — activitate ramasa usor ridicata (5304), fara mecanism nou.

- **08-15 13:00-14:00** — deschidere NY, declin 3342->3335, volum ridicat (5451-7593), profil
  consistent cu deschiderile NY deja documentate. Fara mecanism nou.

- **08-15 14:00-15:15** — revenire 3335->3343, volum ramas moderat (3191-5548), fara reactie
  marcanta. Fara mecanism nou.

- **08-15 15:15-16:30** — declin usor 3343->3339, volum moderat (2585-3083). Fara eveniment.

- **08-15 16:30-17:45** — banda linistita ~3335-3339, volum in scadere (1229-3619). Fara
  eveniment.

- **08-15 17:45-19:00** — banda linistita ~3335-3338, volum scazut (606-1936). Fara eveniment.

- **08-15 19:00-20:15** — banda linistita ~3334-3339, volum scazut (1154-3696). Fara eveniment.
  Se apropie pauza de rollover.

- **08-15 20:15-21:00** — banda linistita, volum foarte scazut (518-1100). Fara eveniment.
- **08-15 21:00 -> 08-17 22:00** (weekend) — gap mic la redeschidere (~0.5pt), majoritar retras in
  prima bara; comportament similar cu gap-urile de weekend anterioare.

- **08-17 22:15-23:45** — deschidere Asia (Sunday), declin usor 3335->3328 cu range-uri ceva mai
  largi (pana la 7.3pt) dar volum ramas scazut tot timpul (155-1932) — compatibil cu lichiditate
  subtire de redeschidere, nu semnaleaza un eveniment distinct. Fara element nou de investigat.

- **08-17 23:45 -> 08-18 01:00** — a 6-a instanta a orei 00:00-01:00 UTC: miscare directionala
  moderata 3327->3341 (~14pt) in primele 30 min, volum 2-5x local (3248-5238), apoi consolidare -
  morfologie deja documentata (asemanatoare cu instanta moderata din 08-14), fara element nou;
  nu s-a adaugat inregistrare noua.

- **08-18 01:00-02:15** — banda ~3339-3347, volum moderat (3109-5355). Fara eveniment.

- **08-18 02:15-03:30** — banda ~3342-3347, volum scazut (963-2745). Fara eveniment.

- **08-18 03:30-04:45** — urcare usoara 3346->3355, volum scazut-moderat (1741-3304). Fara
  eveniment.

- **08-18 04:45-06:00** — declin usor 3358->3349, volum moderat (2349-4156). Fara eveniment.

- **08-18 06:00-07:15** — tranzitie spre Londra, banda ~3346-3354, volum moderat (2542-3892).
  Fara eveniment.

- **08-18 07:15-08:30** — Londra, declin usor 3353->3346, volum moderat (2955-4209). Fara
  eveniment.

- **08-18 08:30-09:45** — banda ~3346-3351, volum scazut-moderat (2059-3580). Fara eveniment.

- **08-18 09:45-11:00** — banda ~3346-3350, volum scazut-moderat (1919-3826). Fara eveniment.

- **08-18 11:00-12:00** — banda ~3344-3349, volum scazut (1660-3308). Fara eveniment.

- **08-18 12:00-12:30** — banda ~3345-3348, volum moderat (3542-4254). Fara eveniment.
- **08-18 12:30-13:00** — a 6-a instanta 12:30 UTC din esantion, ruleaza ORDINAR (vol 4760-4981,
  fara concentrare, fara sustinere) — acelasi rezultat deja documentat, fara intrare noua.
- **08-18 13:00-13:15** — deschidere NY, volum 7206, profil consistent cu deschiderile NY deja
  documentate. Fara eveniment.

- **08-18 13:15-14:15** — continuare NY, declin 3341->3336, volum ridicat (6176-9360), profil
  consistent cu deschiderile NY deja documentate. Fara mecanism nou.

- **08-18 14:15-15:15** — banda ~3332-3339, volum ramas moderat-ridicat (4823-6900). Fara
  eveniment.

- **08-18 15:15-16:30** — normalizare treptata, banda ~3332-3336, volum in scadere (2246-4072).
  Fara eveniment.

- **08-18 16:30-17:45** — banda linistita ~3331-3335, volum scazut (2078-3591). Fara eveniment.

- **08-18 17:45-19:00** — banda linistita ~3331-3334, volum scazut (1316-2329). Fara eveniment.

- **08-18 19:00-20:15** — banda linistita ~3330-3334, volum in scadere (610-2165). Fara eveniment.
  Se apropie pauza de rollover.

- **08-18 20:15-21:00** — banda linistita, volum foarte scazut (263-406). Fara eveniment.
- **08-18 21:00-22:00** — a 9-a pauza de rollover confirmata (jump 75min). Redeschidere curata,
  fara gap notabil, volum foarte scazut (492). Fara eveniment.

- **08-18 22:15-23:30** — banda linistita ~3331-3335, volum foarte scazut (201-627), Asia
  standard. Fara eveniment.

- **08-18 23:30 -> 08-19 00:30** — a 7-a instanta a orei 00:00-01:00 UTC: declin scurt spre
  3326.3 apoi urcare sustinuta pana la 3339 (~13pt), volum distribuit uniform pe toate cele 15
  minute M1 (98-614, fara concentrare), morfologie deja cunoscuta (sustinuta/distribuita) -
  fara element nou, nu s-a adaugat inregistrare noua.

- **08-19 00:30-01:45** — banda ~3330-3336, volum scazut-moderat (1576-3695). Fara eveniment.

- **08-19 01:45-03:00** — banda ~3329-3338, volum scazut (1318-2744). Fara eveniment.

- **08-19 03:00-04:15** — declin usor 3341->3337, volum scazut-moderat (1161-3674). Fara
  eveniment.

- **08-19 04:15-05:30** — banda linistita ~3334-3340, volum scazut (1094-2089). Fara eveniment.

- **08-19 05:30-06:45** — tranzitie spre Londra, banda ~3334-3340, volum scazut-moderat
  (1081-2417). Fara eveniment.

- **08-19 06:45-08:00** — Londra, zig-zag ~3334-3342, volum moderat (1871-2931). Fara eveniment.

- **08-19 08:00-09:15** — banda ~3336-3339, volum scazut-moderat (625-2715). Fara eveniment.

- **08-19 09:15-10:30** — urcare usoara 3337->3345, volum scazut-moderat (1051-2117). Fara
  eveniment.

- **08-19 10:30-11:45** — banda ~3339-3345, volum scazut (805-1727). Fara eveniment.

- **08-19 11:45-12:30** — declin usor 3341->3336, volum moderat (2629-2742). Fara eveniment.
- **08-19 12:30-13:00** — inca o instanta 12:30 UTC ordinara (vol 2542-3479, fara concentrare,
  fara sustinere) — acelasi rezultat deja documentat, fara intrare noua.
- **08-19 13:00-13:15** — deschidere NY, volum 2160, profil ordinar. Fara eveniment.

- **08-19 13:15-14:15** — deschidere NY, zig-zag 3326->3339, volum ridicat (4217-7172), profil
  consistent cu deschiderile NY deja documentate. Fara mecanism nou.

- **08-19 14:15-15:30** — continuare NY, declin 3335->3323 (~12pt), volum ridicat (2186-7606),
  profil consistent cu deschiderile/continuarile NY deja documentate. Fara mecanism nou.

- **08-19 15:30-16:45** — declin usor continuat 3324->3319, volum moderat (2026-3486). Fara
  eveniment.

- **08-19 16:45-18:00** — banda ~3315-3320, volum scazut-moderat (2408-3460). Fara eveniment.

- **08-19 18:00-19:15** — banda linistita ~3316-3320, volum scazut (733-2151). Fara eveniment.

- **08-19 19:15-20:30** — banda linistita ~3315-3318, volum in scadere (773-2674). Fara eveniment.
  Se apropie pauza de rollover.

- **08-19 20:30-21:00** — banda linistita, volum foarte scazut (286-856). Fara eveniment.
- **08-19 21:00-22:00** — a 10-a pauza de rollover confirmata (jump 75min). Redeschidere curata,
  fara gap notabil, volum foarte scazut (297). Fara eveniment.

- **08-19 22:15 -> 08-20 00:00** — banda linistita 3312-3317, volum scazut-moderat (301-2375).
  Fara eveniment.
- **08-20 00:00-01:00** — a 8-a instanta a ferestrei 00:00-01:00 UTC, complet ordinara (volume
  2375/2314/1766/2559, fara outlier). Se potriveste unui tipar deja documentat (majoritatea
  instantelor din esantion sunt ordinare) -> nu justifica intrare noua in Observation Registry,
  doar nota de jurnal.
- **08-20 01:00-02:00** — miscare directionala moderata usoara in sus apoi retragere partiala
  (3312->3317->3315), volum moderat (3129-4138). Variatie ordinara, fara mecanism nou.
- **08-20 02:00-03:00** — banda linistita 3312-3317, volum scazut-moderat (2099-2725). Fara
  eveniment.

- **08-20 03:00-05:15** — banda linistita 3314-3321, volum scazut-moderat (263-2731). Fara
  eveniment.

- **08-20 05:15-07:45** — urcare treptata 3318->3327, volum moderat (1147-4446), variatie ordinara
  fara concentrare intr-un minut. Fara eveniment.

- **08-20 07:45-09:45** — deschidere Londra si continuare, banda 3321-3327, volum moderat
  (561-3001), fara concentrare intr-un minut, fara impuls neobisnuit. Fara eveniment.

- **08-20 09:45-11:30** — banda ordinara 3323-3331, volum moderat (1625-3263), urcare treptata
  fara concentrare. Fara eveniment.

- **08-20 11:30-13:15** — a 6-a instanta a ferestrei 12:30 UTC (12:30-12:45, vol 6507, doar usor
  peste bara precedenta 5728, fara concentrare — verificat pe M5: 2656/1751/2100, distribuit).
  Se citeste ca o continuare ordinara a urcarii deja in desfasurare, nu ca puseu distinct. Se
  potriveste tiparului deja documentat (instante ordinare) -> doar nota de jurnal. Restul benzii
  3329-3344, volum moderat-ridicat (3452-6507), urcare treptata generala. Fara alt eveniment.

- **08-20 13:15-14:30** — deschidere NY, zig-zag 3340->3348->3340->3345, volum ridicat
  (3660-6734), profil consistent cu deschiderile NY deja documentate. Fara mecanism nou.

- **08-20 14:30-15:45** — continuare NY, urcare la 3350 apoi retragere 3350->3340, volum
  moderat-ridicat (2794-7185), profil consistent cu variatiile NY deja documentate. Fara mecanism
  nou.

- **08-20 15:45-16:45** — banda ordinara 3339-3346, volum scazut-moderat (2422-3427). Fara
  eveniment.

- **08-20 16:45-17:45** — banda foarte ingusta 3344-3346, volum scazut (2109-2694). Fara
  eveniment.

- **08-20 17:45-18:45** — banda ordinara 3344-3348, volum scazut-moderat (2279-4321). Fara
  eveniment.

- **08-20 18:45-19:45** — banda ordinara 3345-3349, volum scazut-moderat (1817-2532). Fara
  eveniment. Se apropie pauza de rollover.

- **08-20 19:45-21:00** — banda linistita 3347-3349, volum in scadere (137-3707). Fara eveniment.
- **08-20 21:00-22:00** — a 11-a pauza de rollover confirmata (jump 75min). Redeschidere cu gap mic
  (~2.7pt), volum scazut (565). Fara eveniment.

- **08-20 22:15-23:15** — banda linistita 3347-3351, volum foarte scazut (408-1548). Fara
  eveniment.

- **08-20 23:15 -> 08-21 00:00** — banda linistita 3346-3348, volum foarte scazut (199-798). Fara
  eveniment.
- **08-21 00:00-01:00** — a 9-a instanta a ferestrei 00:00-01:00 UTC, complet ordinara (volume
  1142/997/1297/2278, fara outlier). Se potriveste tiparului deja documentat -> doar nota de jurnal.

- **08-21 01:00-02:00** — banda ordinara 3340-3346, volum scazut-moderat (1918-2992). Fara
  eveniment.

- **08-21 02:00-03:00** — banda linistita 3340-3345, volum scazut (1256-2267). Fara eveniment.

- **08-21 03:00-04:00** — banda linistita 3339-3345, volum scazut (544-1630). Fara eveniment.

- **08-21 04:00-05:00** — declin usor 3340->3338, volum foarte scazut (461-1356). Fara eveniment.

- **08-21 05:00-06:00** — banda linistita 3337-3340, volum scazut (1016-2259). Fara eveniment.

## STARE: ACTIV — reluat cu filtru v2 (2026-07-23)
CEO a aprobat reluarea. Filtrul de investigatie v2 (vezi sectiunea de mai jos) este acum activ.
Ultima pozitie confirmata in replay la reluare: **2025-08-21 05:59:59 UTC** (checkpoint 06:00 UTC).

- **08-21 06:00-07:00** — banda ordinara 3334-3340, volum scazut-moderat (1651-3508), fara
  deviatie materiala fata de variatia normala (filtru v2: NU justifica investigatie). Fara eveniment.

- **08-21 07:00-08:00** — banda ordinara 3335-3341, volum scazut (1723-2432). Fara eveniment.

- **08-21 08:00-09:00** — deschidere Londra ordinara, banda 3337-3341, volum scazut (1214-2708),
  fara deviatie materiala (filtru v2: NU justifica investigatie). Fara eveniment.

- **08-21 09:00-13:15** — banda ordinara 3325-3345, volum scazut-moderat (984-5914). Un declin de
  ~14pt in 3 bare (11:30-12:15) cu volum usor ridicat a fost verificat pe M5: distributie
  uniforma, revenire graduala de la minim — se potriveste tiparului deja documentat
  (declin-pe-volum/recuperare-graduala), fara mecanism nou. Fereastra 12:30 UTC (a 7-a instanta)
  a rulat ordinar (vol 7636, ~1.7x baseline, sub pragul instantelor notabile) — filtrul v2 nu a
  justificat investigatie.
- **08-21 13:15-16:45** — deschidere si continuare NY, zig-zag 3336-3348, volum ridicat dar in
  intervalul deja cunoscut pentru sesiunea NY (3035-11961), fara mecanism nou.

- **08-21 16:45 -> 08-22 01:00** — banda linistita 3336-3342, volum scazut pe tot parcursul
  (225-2771). A 12-a pauza de rollover confirmata (jump 75min, 20:59->22:14), redeschidere curata,
  gap mic, volum foarte scazut — tipar deja cunoscut, fara mecanism nou. Fereastra 00:00-01:00 UTC
  (a 10-a instanta) a rulat complet ordinar (544/864/2312/1261, fara outlier) — se potriveste
  esantionului deja documentat. Fara evenimente care sa justifice investigatie dupa filtrul v2.

- **08-22 01:00-07:00** — banda linistita 3326-3340, volum scazut pe tot parcursul (958-2984),
  fara nicio deviatie care sa justifice investigatie dupa filtrul v2. Tranzitia spre Londra (06:00)
  a trecut fara reactie marcanta.

- **08-22 07:00-14:00** — banda ordinara 3321-3335, volum scazut-moderat (958-7581), tranzitia
  Londra si fereastra 12:30 UTC (a 8-a instanta, vol 6913, ~1.4x, ordinara) fara nimic ce sa
  justifice investigatie dupa filtrul v2.
- **08-22 14:00 UTC** — expansiune direct'ionala mare, sustinuta pe 4 lumanari M15 consecutive
  (3333.97 -> 3376.77, ~43pt), fara nicio inversare, volum sustinut si distribuit pe minut
  (verificat M5/M1: fara concentrare intr-un minut). Una din cele mai mari miscari sustinute din
  tot replay-ul -> **DC-0013 creat** (contrast fata de DC-0008 prin persistenta multi-lumanare,
  contrast fata de DC-0011 prin absenta oricarui sweep/reclaim).
- **08-22 14:45-16:30** — consolidare/retragere partiala dupa DC-0013 (3368-3378), volum in
  scadere (2793-10464), fara mecanism nou.

- **08-22 16:30-21:00** — consolidare/banda ordinara 3368-3376, volum scazut-moderat (677-4915),
  fara mecanism nou. Vineri, deci inchiderea de la 21:00 UTC este gap-ul de weekend, nu pauza
  zilnica obisnuita.
- **weekend 08-22 21:00 -> 08-24 22:15** — gap de weekend confirmat (jump ~49h), redeschidere cu
  gap mic (~2.5pt), volum scazut, consistent cu gap-urile de weekend deja documentate. Fara
  eveniment.
- **08-24 22:15-23:00** — redeschidere Asia obisnuita, volum foarte scazut (280-543). Fara
  eveniment.

- **08-24 23:00 -> 08-25 04:00** — banda linistita 3359-3371, volum scazut pe tot parcursul
  (369-2797). A 11-a instanta a ferestrei 00:00-01:00 UTC (prima instanta de luni) a rulat complet
  ordinar, fara outlier. Fara evenimente care sa justifice investigatie dupa filtrul v2.

- **08-25 04:00-08:00** — banda linistita 3363-3370, volum scazut (556-1906), tranzitia Londra
  fara reactie marcanta. Fara evenimente care sa justifice investigatie dupa filtrul v2.

- **08-25 08:00-13:00** — banda ordinara 3362-3371, volum scazut (820-2916). Fereastra 12:30 UTC
  (a 12-a instanta, vol 2916, ~2x, ordinara) fara nimic ce sa justifice investigatie dupa filtrul
  v2.

- **08-25 13:00-15:30** — deschidere si continuare NY, zig-zag 3362-3376, volum ridicat dar in
  intervalul deja cunoscut (1990-6100), fara mecanism nou (fara nimic comparabil cu DC-0013).

- **08-25 15:30-21:00** — banda linistita 3364-3376, volum scazut-moderat (740-3038). A 13-a pauza
  de rollover confirmata (jump 75min, 20:59->22:00). Redeschidere curata, gap mic (~0.9pt), volum
  foarte scazut (290) — tipar deja cunoscut, fara mecanism nou. Fara evenimente care sa justifice
  investigatie dupa filtrul v2.

- **08-25 22:15 -> 08-26 00:00** — banda linistita 3358-3365, volum scazut (198-3733), incluzand
  un declin-recuperare pe volum usor crescut (~12pt) care se potriveste tiparului deja documentat.
  Fara eveniment separat.
- **08-26 00:00-01:00** — revenire in forma de V intr-o singura lumanare (declin pe volum redus la
  un minim proaspat, apoi recuperare sustinuta pe volum distribuit, 19.7pt) urmata de o extindere
  sustinuta pe inca 3 lumanari (pana la ~35.4pt total de la minim) si apoi o inversare. Verificat
  M5/M1: fara concentrare intr-un minut. -> **DC-0014 creat** (promovat dintr-o intrare initiala in
  Observation Registry, dupa ce amploarea completa a devenit clara; comparat cu DC-0013 ca a doua
  expansiune sustinuta mare, dar cu inversare in loc de consolidare).
- **08-26 01:00-02:30** — consolidare dupa DC-0014 (3371-3379), volum in scadere (1542-8158). Fara
  eveniment.

- **08-26 02:30-07:45** — banda ordinara 3367-3379, volum scazut-moderat (1084-4400), incluzand un
  declin-recuperare de ~11pt (06:15-07:00) care se potriveste tiparului deja documentat. Tranzitia
  Londra fara reactie marcanta. Fara evenimente care sa justifice investigatie dupa filtrul v2.

- **08-26 07:45-12:45** — banda ordinara 3367-3380, volum moderat (1538-5418). Fereastra 12:30 UTC
  (a 13-a instanta, vol 5219, similar cu bara precedenta, ordinara) fara nimic ce sa justifice
  investigatie dupa filtrul v2.

- **08-26 12:45-15:00** — deschidere si continuare NY, zig-zag 3370-3380, volum ridicat dar in
  intervalul deja cunoscut (5420-10477), fara mecanism nou.

- **08-26 15:00-17:00** — continuare NY, urcare treptata 3379-3389, volum moderat (3495-5532),
  fara mecanism nou.

- **08-26 17:00-18:45** — banda ordinara 3380-3386, volum scazut-moderat (2381-3668). Fara
  eveniment.

- **08-26 18:45-21:00** — banda linistita 3384-3394, volum scazut-moderat (453-4820). A 14-a pauza
  de rollover confirmata (jump 75min, 20:59->22:14). Redeschidere curata, gap mic (~4pt), volum
  scazut (1242) — tipar deja cunoscut, fara mecanism nou.

- **08-26 22:15 -> 08-27 00:00** — banda linistita 3388-3393, volum foarte scazut (324-576). Fara
  eveniment.
- **08-27 00:00-01:00** — a 14-a instanta a ferestrei 00:00-01:00 UTC, ordinara (1243/2114/2254/
  2995, fara outlier). Se potriveste esantionului deja documentat -> doar nota de jurnal.

- **08-27 01:00-03:00** — banda ordinara 3382-3390, volum scazut-moderat (930-4763). Fara
  eveniment.

- **08-27 03:00-05:00** — declin lent 3384-3375, volum scazut-moderat (1279-3053), fara mecanism
  nou.

- **08-27 05:00-07:00** — banda ordinara 3374-3382, volum scazut-moderat (1892-3137), tranzitia
  Londra fara reactie marcanta.

- **08-27 07:00-08:30** — banda ordinara 3374-3385, volum scazut-moderat (3000-4767). Fara
  eveniment.

- **08-27 08:30-11:00** — declin lent 3384-3375, volum scazut-moderat (1461-4687), fara mecanism
  nou.

- **08-27 11:00-13:00** — banda ordinara 3374-3383, volum moderat (2523-6873). Fereastra 12:30 UTC
  (a 15-a instanta, vol 6873, ~1.4x, ordinara) fara nimic ce sa justifice investigatie dupa filtrul
  v2.

- **08-27 13:00-14:45** — deschidere si continuare NY, zig-zag 3375-3384, volum ridicat dar in
  intervalul deja cunoscut (3750-10285), fara mecanism nou.

- **08-27 14:45-16:00** — continuare NY, urcare 3383-3390, volum moderat (2216-5382), fara
  mecanism nou.

- **08-27 16:00-17:30** — continuare NY, urcare 3388-3398, volum moderat (3629-7310), fara
  mecanism nou.

- **08-27 17:30-18:45** — banda ordinara 3392-3397, volum scazut-moderat (2172-4375). Fara
  eveniment.

- **08-27 18:45-21:00** — banda linistita 3393-3398, volum scazut-moderat (766-3744). A 15-a pauza
  de rollover confirmata (jump 75min, 20:59->22:14). Redeschidere curata, gap mic (~0.7pt), volum
  scazut (851) — tipar deja cunoscut, fara mecanism nou.

- **08-27 22:15 -> 08-28 00:00** — banda linistita 3394-3399, volum foarte scazut (187-1413). Fara
  eveniment.
- **08-28 00:00-01:00** — a 16-a instanta a ferestrei 00:00-01:00 UTC, ordinara (2011/1677/1399/
  1585, fara outlier). Se potriveste esantionului deja documentat -> doar nota de jurnal.

- **08-28 00:45-02:00** — declin sustinut pe 5 lumanari (~12pt, 3398->3385.5), volum elevat dar
  moderat (3829-6313), acum in consolidare. Se potriveste tiparului deja documentat de declin
  sustinut multi-lumanare — nu justifica investigatie M5 dupa filtrul v2.

- **08-28 02:00-03:30** — revenire treptata 3385-3392, volum scazut-moderat (2420-5307), fara
  mecanism nou.

- **08-28 03:30-05:00** — banda linistita 3388-3392, volum scazut (942-2073). Fara eveniment.

- **08-28 05:00-06:30** — banda ordinara 3387-3392, volum scazut-moderat (930-3654), tranzitia
  Londra fara reactie marcanta.

- **08-28 06:30-07:45** — banda ordinara 3393-3397, volum moderat (3429-3895). Fara eveniment.

- **08-28 07:45-09:15** — urcare treptata 3394-3401, volum moderat (2569-4182), fara mecanism nou.

- **08-28 09:15-10:45** — banda ordinara 3394-3401, volum moderat (1535-6057). Fara eveniment care
  sa justifice investigatie dupa filtrul v2.

- **08-28 10:45-12:30** — urcare treptata 3396-3408, volum moderat-ridicat (2222-8536), fara
  mecanism nou.
- **08-28 12:30-13:00** — a 16-a instanta a ferestrei 12:30 UTC: declin sustinut pe 2 lumanari
  (~10.4pt, vol 13058+11067). Verificat M5: volum distribuit uniform pe toate cele 6 lumanari
  (3581-4648), fara concentrare — se potriveste tiparului deja documentat de declin sustinut, fara
  element nou de investigat.
- **08-28 13:00-13:30** — revenire 3397->3405, volum ridicat dar in intervalul deja cunoscut
  (8604-9334), fara mecanism nou.

- **08-28 13:30-14:30** — deschidere si continuare NY, urcare 3404-3412, volum ridicat dar in
  intervalul deja cunoscut (8440-14441), fara mecanism nou.

- **08-28 14:30-15:45** — continuare NY, urcare la 3413 apoi retragere la 3405, volum moderat-ridicat
  (4310-8102), fara mecanism nou.

- **08-28 15:45-16:45** — urcare treptata 3406-3417, volum moderat (3445-5599), fara mecanism nou.

- **08-28 16:45-18:00** — banda ordinara 3414-3419, volum moderat (4132-5512), fara mecanism nou.

- **08-28 18:00-19:15** — banda ordinara 3417-3420, volum scazut-moderat (3118-5302). Fara
  eveniment.

- **08-28 19:15-21:00** — banda linistita 3416-3423, volum scazut-moderat (597-10741, un varf
  izolat fara continuare). A 16-a pauza de rollover confirmata (jump 75min, 20:59->22:14).
  Redeschidere curata, fara gap notabil, volum scazut (841) — tipar deja cunoscut, fara mecanism
  nou.

- **08-28 22:15 -> 08-29 00:00** — banda linistita 3413-3417, volum foarte scazut (279-656). Fara
  eveniment.
- **08-29 00:00-01:00** — a 17-a instanta a ferestrei 00:00-01:00 UTC, ordinara (1176/3107/2661/
  1985, fara outlier). Se potriveste esantionului deja documentat -> doar nota de jurnal.

- **08-29 00:45-02:00** — declin lent 3414-3410, volum moderat (3245-6005), fara mecanism nou.

- **08-29 02:00-03:00** — banda ordinara 3409-3414, volum scazut-moderat (1963-4367). Fara
  eveniment.

- **08-29 03:00-04:00** — banda ordinara 3409-3414, volum scazut (438-3587). Fara eveniment.

- **08-29 04:00-05:00** — banda linistita 3407-3411, volum scazut (1536-2305). Fara eveniment.

- **08-29 05:00-06:00** — banda ordinara 3407-3411, volum scazut (1627-2550). Fara eveniment.

- **08-29 06:00-07:00** — tranzitia Londra ordinara, banda 3407-3413, volum scazut (1650-3114).
  Fara eveniment.

- **08-29 07:00-08:00** — banda ordinara 3406-3413, volum moderat (3285-5398). Fara eveniment.

- **08-29 08:00-09:00** — banda ordinara 3409-3415, volum moderat (3931-6940). Fara eveniment.

- **08-29 09:00-10:00** — declin lent 3410-3407, volum moderat (4482-5210), fara mecanism nou.

- **08-29 10:00-11:00** — banda ordinara 3404-3409, volum scazut-moderat (2772-5051). Fara
  eveniment.

- **08-29 11:00-12:30** — urcare treptata 3404-3411, volum moderat (2694-7434), fara mecanism nou.
- **08-29 12:30-13:00** — a 18-a instanta a ferestrei 12:30 UTC, ordinara (vol 6211, ~1x baseline).
  Continuare urcare 3408->3417, volum ridicat dar in intervalul deja cunoscut (9002-11151), fara
  mecanism nou.

- **08-29 13:00-15:45** — expansiune direct'ionala sustinuta pe 11 lumanari M15 consecutive
  (3416.51 -> 3447.79, ~31.3pt, ~2h45m), fara pullback semnificativ pana la final. Volum ridicat pe
  tot parcursul (6626-19061), verificat M5 pe cele 2 lumanari cu volum maxim: distributie uniforma,
  fara concentrare. Aceasta e cea mai lunga miscare sustinuta unidirectionala din tot replay-ul
  (mai lunga decat DC-0013 si DC-0014). -> **DC-0015 creat** (comparat cu DC-0013/DC-0014 ca a
  treia instanta a familiei "expansiune sustinuta mare", cu durata cea mai lunga).
- **08-29 15:45-16:45** — consolidare dupa DC-0015 (3442-3448), volum normalizat (6202-9751). Fara
  eveniment.

- **08-29 16:45-17:45** — consolidare 3444-3450, volum moderat (5881-8222), fara mecanism nou.

- **08-29 17:45-20:00** — consolidare/urcare usoara 3441-3452, volum normal (5199-8668), fara
  mecanism nou. La 19:45-20:00 o lumanare cu volum 17575 (~2-3x baseline) urmata imediat de
  inversare aproape completa (vol 6226) — tipar deja documentat (DC-0006, volum extrem care nu se
  extinde), fara investigatie.

- **08-29 20:00-21:00** — consolidare joasa pe volum 1691-2569, fara mecanism nou. -> **gap de
  weekend**: vineri 08-29 21:00 UTC -> duminica 08-31 22:15 UTC (~49h intr-un singur pas), gap mic
  (3447.4->3445.4) recuperat rapid, tipar deja cunoscut.

- **08-31 22:15 - 09-01 00:45** — tranzactionare subtire tipica de duminica seara/Asia timpurie,
  volum 650-6350, fara mecanism nou (inclusiv o lumanare la ~01:00 UTC cu vol 6345, in intervalul
  deja documentat pentru aceasta ora).

- **09-01 01:00-02:45** — expansiune directionala sustinuta pe ~6-7 lumanari M15 (3439.03 ->
  3486.26, ~47.2pt, ~1h45m), cea mai mare miscare punctuala din familia "expansiune sustinuta mare"
  de pana acum. Volum ridicat pe tot parcursul (5795-15884), verificat M5 pe cele 2 lumanari cu
  volum maxim: distributie uniforma (ex. 3968/6579/5337), fara concentrare — construc'tie identica
  cu DC-0008/DC-0013/DC-0014/DC-0015. Se incheie cu o lumanare de inversare abrupta la varf marginal
  nou (vol 13863), urmata de consolidare pe volum in scadere (7766). -> **DC-0016 creat** (a patra
  instanta a familiei, la o noua fereastra orara — Asia timpurie/pre-Londra — si cea mai mare
  amplitudine observata pana acum).

- **09-01 02:45-15:45** — consolidare/grind ordinar in banda 3467-3490, volum jos-moderat pe tot
  parcursul (2271-9828); a 19-a instanta a ferestrei 12:30 UTC ordinara (vol 4514, in intervalul
  deja cunoscut). Fara mecanism nou, fara declansare filtru v2 pe tot intervalul.

- **09-01 15:45-23:45** — consolidare joasa, volum foarte scazut (312.5-3225, un citire stale
  O=H=L=C corectata silentios prin re-interogare). Un salt de pas unic 18:30->22:15 UTC (~3h45m,
  gap pret neglijabil ~0.45pt) — aceeasi categorie ca pauzele zilnice deja documentate, doar mai
  lung; fara mecanism nou de piata.

- **09-01 23:45-00:15** (00:00 UTC) — instanta ordinara a ferestrei 00:00 UTC (vol 7514, ~3-6x
  baseline imediat anterior), in intervalul deja cunoscut, fara investigatie.

- **09-02 01:00-02:15** — expansiune directionala pe 3 lumanari M15 (3479.21 -> 3508.79, ~29.6pt,
  ~45min), volum in crestere (10371-20353), aceeasi fereastra orara ca DC-0016 (01:00-02:45 UTC),
  la exact 24h distanta. Se incheie cu inversare ampla in aceeasi lumanare de volum maxim (varf
  3508.79 -> close 3493.94), urmata de consolidare pe volum in scadere (14470->5814). Verificat M5
  pe lumanarea cu volum maxim (20353): distributie uniforma (7278/6713/6362), fara concentrare —
  construc'tie identica cu familia deja documentata. -> **Addendum A la DC-0016** (a doua instanta
  la aceeasi ora, amploare mai mica ~63% si durata mai scurta, dar acelasi tipar de final).

- **09-02 02:15-11:45** — consolidare/grind ordinar in banda 3470-3499, volum jos-moderat pe tot
  parcursul (2002-13216), inclusiv o coborare treptata 3499->3470 (07:45-08:00 UTC, vol 13216,
  stabilizata rapid) fara mecanism nou.

- **09-02 11:45-12:30** — urcare treptata spre a 20-a instanta a ferestrei 12:30 UTC (vol 12961,
  interval 3474-3488.6), in intervalul deja cunoscut, fara investigatie.

- **09-02 12:45-13:30** — consolidare post-12:30, volum normalizat (8519-12032), fara mecanism nou.

- **09-02 13:30-15:15** — expansiune directionala sustinuta pe 7 lumanari M15 (~3485.4 -> 3516.91,
  ~31.5-37.9pt, ~1h45m) chiar la deschiderea sesiunii NY, volum ridicat pe tot parcursul
  (15297-23646, fara un varf dominant ca la DC-0013 original). Se incheie cu consolidare treptata
  (volum in scadere 9276->10694), nu inversare abrupta. Verificat M5 pe lumanarea cu volum maxim
  (23646): distributie uniforma (7697/7631/8318), fara concentrare. -> **Addendum A la DC-0013**
  (a doua instanta NY-session, durata mai lunga -7 lumanari vs 4- dar aceeasi finalizare prin
  consolidare, nu inversare).

- **09-02 15:15-20:45** — continuare grind treptat 3514->3540, volum moderat (5472-10854), fara
  mecanism nou (prelungire naturala a expansiunii NY deja notate in Addendum A/DC-0013).

- **09-02 20:45-22:15** — pauza zilnica de rollover (~75min, gap pret neglijabil), a 17-a instanta,
  tipar deja cunoscut. Continuare cu tranzactionare subtire Asia (vol 862-4384) pana la 00:15 UTC.

- **09-03 00:15-00:30** — o lumanare cu volum 12524 (varf 3547.33) urmata imediat de respingere si
  inchidere cu ~10pt sub varf, apoi volum in scadere (6963) fara continuare — tipar deja documentat
  (volum extrem ce nu se extinde, DC-0006-like), in fereastra orara 00:00 UTC deja cunoscuta. Fara
  investigatie.

- **09-03 00:30-02:15** — consolidare choppy 3531-3546, volum moderat (5523-11740), fara tendinta
  clara, fara mecanism nou.

- **09-03 02:15-12:30** — consolidare/grind ordinar in banda 3526-3551, volum jos-moderat pe tot
  parcursul (3336-9435); a 21-a instanta a ferestrei 12:30 UTC ordinara (vol 9435, in intervalul
  deja cunoscut). Fara mecanism nou, fara declansare filtru v2 pe tot intervalul.

- **09-03 12:45-14:45** — volatilitate ridicata dar choppy (nu directionala sustinuta), volum
  8.3k-18.1k, pret oscilind repetat intre ~3549-3566 fara progres net semnificativ; caracter deja
  documentat de volatilitate NY-session ordinara (fara pullback-free construction ca in familia
  DC-0013/15/16). Fara declansare filtru v2.

- **09-03 14:45-20:45** — grind treptat 3564->3578, volum normalizat (5688-9548, un varf izolat de
  15632 pe o singura lumanare stabilizata rapid), fara mecanism nou.

- **09-03 20:45-22:15** — pauza zilnica de rollover (~75min, gap pret neglijabil), a 18-a instanta,
  tipar deja cunoscut. Continuare cu tranzactionare subtire (vol 1063-3972) pana la 00:00 UTC.

- **09-04 00:00-00:15** — instanta ordinara a ferestrei 00:00 UTC (vol 6002), in intervalul deja
  cunoscut, fara investigatie.

- **09-04 00:15-02:45** — consolidare ordinara 3543-3562, volum jos-moderat (1063-10791), fara
  mecanism nou.

- **09-04 02:45-03:30** — coborare 2 lumanari (3538.4->3511.8, ~26.6pt, vol 12303/12025) urmata de
  o singura lumanare de revenire V (3514.6->3530.7, ~15.6pt, vol 11511), apoi stabilizare imediata
  (vol 3838, fara continuare sustinuta). Tipar V generic, dar spre deosebire de DC-0014 nu s-a
  transformat intr-o expansiune sustinuta multi-lumanari -> fara DC/addendum, doar notat in jurnal.

- **09-04 03:30-12:30** — consolidare/grind ordinar in banda 3524-3553, volum jos-moderat pe tot
  parcursul (1551-10085); a 22-a instanta a ferestrei 12:30 UTC ordinara (vol 9607, in intervalul
  deja cunoscut). Fara mecanism nou.

- **09-04 12:45-14:15** — volatilitate ridicata choppy la deschiderea NY (vol 8.6k-19k), coborare
  neta ~23.5pt (3558.9->3535.4 in ~1h) apoi stagnare/revenire fara continuare sustinuta — a doua
  instanta a acestui tipar "choppy NY-open, fara constructie pullback-free" (prima: 09-03
  12:45-14:45), acum confirmat de doua ori ca fiind caracter ordinar, nu familia de expansiuni
  sustinute. Fara DC/addendum.

- **09-04 14:15-20:45** — consolidare/grind treptat 3542-3556, volum jos-moderat (3070-6874), fara
  mecanism nou.

- **09-04 20:45-22:15** — pauza zilnica de rollover (~75min, gap pret neglijabil), a 19-a instanta,
  tipar deja cunoscut. Continuare cu tranzactionare subtire (vol 811-3516) pana la 00:00 UTC.

- **09-05 00:00-00:15** — instanta ordinara a ferestrei 00:00 UTC (vol 6583), in intervalul deja
  cunoscut, fara investigatie.

- **09-05 00:15-12:15** — consolidare/grind ordinar in banda 3544-3561, volum jos-moderat pe tot
  parcursul (2007-8083), fara mecanism nou.

- **09-05 12:15-12:30** — pre-eveniment ordinar (vol 9882), apoi **12:30-12:45: impuls de amploare
  NFP** (O3555.235 H3587.04 L3553.89 C3583.63, ~33.15pt, vol 30975) — cu mult peste toate cele 22
  instante anterioare ale ferestrei 12:30 UTC. Verificat M1: volum distribuit pe toate cele 15
  minute (1161-3099, fara minut dominant), construc'tie identica cu DC-0008. Urmat de 4 lumanari
  suplimentare cu volum ridicat (22921, 19012, 16151, 20627) care mentin nivelul de pret (3572-3587)
  fara sa inverseze si fara sa extinda dramatic. -> **DC-0017 creat** (data = prima vineri a lunii,
  consistenta cu NFP; tipar "impuls apoi mentinere", distinct de familia expansiune-sustinuta-mare
  DC-0013/15/16 care se construieste treptat).

- **09-05 13:45-16:45** — continuare volum ridicat post-NFP (21722->8932, decadere treptata pe 13
  lumanari, ~3h), pretul NU consolideaza plat ci deriva usor mai sus (varf marginal nou 3600.2 pe la
  16:30) inainte de a se normaliza aproape complet spre 16:45-17:00 (vol ~7-10k). -> **Addendum A la
  DC-0017** (durata reala a regimului de volum ridicat ~4h15m, nu doar cele 4 lumanari initiale;
  pretul a continuat sa urce usor in coada, nu doar a mentinut nivelul).

- **09-05 17:00-21:00** — normalizare completa, volum jos-moderat (1478-15619, un singur varf
  izolat de 15619 stabilizat imediat), fara mecanism nou. -> **gap de weekend**: vineri 09-05 21:00
  UTC -> duminica 09-07 22:15 UTC (~49h intr-un singur pas), gap mic (3586.5->3591.6) recuperat
  rapid in prima lumanare, a treia instanta, tipar deja cunoscut.

- **09-07 22:15 - 09-08 01:00** — tranzactionare subtire ordinara de duminica seara/Asia timpurie,
  volum 1602-9154, fara mecanism nou.

- **09-08 01:00-01:45** — coborare moderata 3 lumanari (3597.2->3584.9, ~12.3pt, vol 17487/12398)
  la aceeasi ora ca familia DC-0016, dar directie opusa (coborare, nu urcare) si amploare mult mai
  mica (~12pt vs 30-47pt); stabilizare rapida (vol 9717). Nu se potriveste constructiei DC-0016
  (magnitudine insuficienta) -> fara DC/addendum, doar notat.

- **09-08 01:45-12:30** — grind ordinar sustinut 3579-3622, volum jos-moderat pe tot parcursul
  (2342-8569); a 24-a instanta a ferestrei 12:30 UTC ordinara (vol 7280, in intervalul deja
  cunoscut). Fara mecanism nou.

- **09-08 12:45-16:00** — volatilitate ridicata choppy la deschiderea NY (vol 8.5k-19k, 3620->3646
  cu retrageri repetate, nu o construc'tie fara pullback), a treia instanta a acestui tipar deja
  documentat (dupa 09-03 si 09-04) -> confirmare suplimentara, fara DC/addendum nou.

- **09-08 16:00-18:45** — normalizare si consolidare 3632-3641, volum jos-moderat (3775-7735), fara
  mecanism nou.

- **09-08 18:45-20:45** — consolidare linistita 3632-3638, volum jos (1359-5748), fara mecanism nou.

- **09-08 20:45-22:15** — pauza zilnica de rollover (~75min, gap pret neglijabil), a 20-a instanta,
  tipar deja cunoscut. Continuare cu tranzactionare subtire (vol 781-2475) pana la 00:00 UTC.

- **09-09 00:00-00:15** — instanta ordinara a ferestrei 00:00 UTC (vol 3170), in intervalul deja
  cunoscut, fara investigatie.

- **09-09 00:15-06:00** — grind ordinar sustinut 3636-3659, volum jos-moderat (2549-9962), fara
  mecanism nou.

- **09-09 06:00-06:30** — coborare 2 lumanari (3659.4->3636.6, ~22.8pt, vol 15088/10962) urmata de
  revenire in V pe o singura lumanare (close 3649.9), apoi stabilizare (vol 7107) fara continuare
  sustinuta — tipar generic deja documentat (vezi 09-08 01:00), amploare/durata insuficiente pentru
  familia DC-0016. Fara DC/addendum.

- **09-09 06:30-12:30** — consolidare/grind ordinar in banda 3641-3656, volum jos-moderat pe tot
  parcursul (2517-9900); a 25-a instanta a ferestrei 12:30 UTC ordinara (vol 12788, in intervalul
  deja cunoscut). Fara mecanism nou.

- **09-09 12:45-14:00** — volatilitate ridicata la deschiderea NY (vol 8.8k-17.4k), urcare treptata
  3646.8->3668.3, ~5 lumanari fara pullback major -> **14:00-14:15: candela extrema** (O3665.95
  H3674.695 L3642.18 C3651.75, vol 36798 — cel mai mare volum dintr-o singura lumanare din tot
  replay-ul, depasind DC-0017). Verificat M1: spike la varf nou 3674.695 in primele ~3 min, apoi
  inversare abrupta la 3642.18 in ~8-9 min, apoi stabilizare 3648-3652; volum distribuit pe toate
  cele 15 minute, fara concentrare.

- **09-09 14:15-15:45** — declin sustinut pe volum ridicat continuu (23103, 23884, 15184, 16260,
  18652, 12212), varf 3674.695 -> minim 3626.915 (~47.8pt in ~1h30m). Verificat M5 pe lumanarea cu
  minimul: distributie uniforma (7964/4799/5889), fara concentrare — construc'tie identica cu
  DC-0008/DC-0013/DC-0015 dar in directie de coborare. -> **DC-0018 creat** (esec complet de
  breakout la varf nou proaspat, pe volum record, urmat de declin sustinut multi-lumanari —
  constructie distincta de toate familiile anterioare).

- **09-09 15:45-16:15** — normalizare treptata (vol 11074, 9208), fara mecanism nou.

- **09-09 16:15-20:45** — consolidare/grind treptat 3628-3649, volum jos-moderat (1613-9712), fara
  mecanism nou.

- **09-09 20:45-22:15** — pauza zilnica de rollover (~75min, gap pret neglijabil), a 21-a instanta,
  tipar deja cunoscut. Continuare cu tranzactionare subtire (vol 1606-3112) pana la 00:00 UTC.

- **09-10 00:00-00:15** — instanta ordinara a ferestrei 00:00 UTC (vol 6322), in intervalul deja
  cunoscut, fara investigatie.

- **09-10 00:15-12:15** — grind ordinar sustinut 3620-3657, volum jos-moderat pe tot parcursul
  (1362-11922), fara mecanism nou.

- **09-10 12:30-13:00** — a 26-a instanta a ferestrei 12:30 UTC, usor elevata (vol 19858, interval
  3642.6-3657.6, ~15pt) apoi in scadere (14823, 11984) si stabilizare rapida — magnitudine sub
  pragul NFP/DC-0017, tipar ordinar deja documentat. Fara investigatie.

- **09-10 13:00-15:30** — volatilitate choppy la deschiderea NY (vol 4.9k-15.9k, oscilatii repetate
  3638-3656), a patra instanta a tiparului deja documentat (choppy NY-open) -> confirmare
  suplimentara, fara DC/addendum nou.

- **09-10 15:30-20:45** — consolidare/grind ordinar 3635-3648, volum jos-moderat (961-8392), fara
  mecanism nou.

- **09-10 20:45-22:15** — pauza zilnica de rollover (~75min, gap mic ~3.9pt recuperat rapid), a
  22-a instanta, tipar deja cunoscut. Continuare cu tranzactionare subtire (vol 619-1372) pana la
  00:00 UTC.

- **09-11 00:00-00:15** — instanta ordinara a ferestrei 00:00 UTC (vol 2794), in intervalul deja
  cunoscut, fara investigatie.

- **09-11 00:15-12:15** — grind ordinar sustinut 3612-3648, volum jos-moderat (1455-8656), fara
  mecanism nou.

- **09-11 12:30-15:00** — a 27-a instanta a ferestrei 12:30 UTC, de amploare notabila (vol 25399,
  interval 3612.8-3644.1, ~31.25pt — a doua cea mai mare valoare de volum la aceasta fereastra dupa
  DC-0017/NFP), dar rezolvata complet diferit: chop bidirectional pe 9 lumanari (~2h15m), fara
  directie neta, inchizand aproape de nivelul de deschidere. Volum in scadere neuniforma
  (20001->9659). -> **Addendum B la DC-0017** (a doua cea mai mare valoare de volum la 12:30 UTC,
  dar fara mentinere/hold ca la NFP — chop extins, amploarea singura nu determina rezolutia).

- **09-11 15:00-20:45** — consolidare/grind ordinar 3630-3642, volum jos-moderat (1844-9895), fara
  mecanism nou.

- **09-11 20:45-22:15** — pauza zilnica de rollover (~75min, gap pret neglijabil), a 23-a instanta,
  tipar deja cunoscut. Continuare cu tranzactionare subtire (vol 249-1564) pana la 00:00 UTC.

- **09-12 00:00-00:15** — instanta ordinara a ferestrei 00:00 UTC (vol 2710), in intervalul deja
  cunoscut, fara investigatie.

- **09-12 00:15-12:15** — grind ordinar sustinut 3630-3656, volum jos-moderat (1177-10081), fara
  mecanism nou.

- **09-12 12:30-12:45** — a 28-a instanta a ferestrei 12:30 UTC ordinara (vol 12102, in intervalul
  deja cunoscut). Fara investigatie.

- **09-12 12:45-16:30** — volatilitate moderat-ridicata la deschiderea NY (vol 6.3k-14.2k), grind
  choppy 3638-3654 fara constructie sustinuta clara, in linia caracterului deja documentat de
  "choppy NY-open". Fara DC/addendum nou.

- **09-12 16:30-20:45** — consolidare linistita 3641-3651, volum jos (1078-4380), fara mecanism nou.

- **09-12 20:45-21:00 -> gap de weekend**: vineri 09-12 21:00 UTC -> duminica 09-14 22:15 UTC (~49h
  intr-un singur pas), gap mic (3643.1->3644.6) recuperat rapid, a 4-a instanta, tipar deja
  cunoscut.

- **09-14 22:15 - 09-15 00:15** — tranzactionare subtire ordinara de duminica seara, volum
  584-3155, fara mecanism nou (inclusiv o instanta ordinara la ora 00:00 UTC, vol 3155).

- **09-15 00:15-12:30** — grind ordinar sustinut 3626-3646, volum jos-moderat pe tot parcursul
  (905-10681); a 29-a instanta a ferestrei 12:30 UTC ordinara (vol 8983, in intervalul deja
  cunoscut). Fara mecanism nou.

- **09-15 12:45-18:15** — grind treptat choppy pe toata sesiunea NY (vol 5.3k-16.4k, oscilant, nu
  monoton), pret deriva net ascendent 3644.9->3685.7 (~41pt pe ~5h15m) dar cu retrageri repetate
  (nu constructie fara-pullback ca familia DC-0013/15/16 — volum mai moderat, ~6-16k vs 15-30k+ la
  instantele deja documentate). Se incheie in consolidare (vol normalizat ~5-7k). Fara DC/addendum
  nou — caracter ordinar de grind NY, deja acoperit conceptual de tiparul "choppy NY-open".

- **09-15 18:15-20:45** — consolidare linistita 3676-3682, volum jos (1126-7542), fara mecanism nou.

- **09-15 20:45-22:15** — pauza zilnica de rollover (~75min, gap pret neglijabil), a 24-a instanta,
  tipar deja cunoscut. Continuare cu tranzactionare subtire (vol 466-2975) pana la 00:00 UTC.

- **09-16 00:00-00:15** — instanta ordinara a ferestrei 00:00 UTC (vol 4991), in intervalul deja
  cunoscut, fara investigatie.

- **09-16 00:15-12:15** — grind ordinar sustinut 3674-3699, volum jos-moderat pe tot parcursul
  (1250-9201), fara mecanism nou.

- **09-16 12:30-12:45** — a 30-a instanta a ferestrei 12:30 UTC ordinara (vol 12452, in intervalul
  deja cunoscut). Fara investigatie.

- **09-16 12:45-16:15** — volatilitate choppy la deschiderea NY (vol 6.9k-19.7k), varf 3703.24
  (~14:15) apoi declin cu revenire ~23pt pe cateva lumanari (nu constructie fara-pullback,
  magnitudine sub pragul DC-0018 vol/amploare); normalizare spre 16:00 (vol ~7-8k). Tipar deja
  documentat de "choppy NY-open". Fara DC/addendum nou.

- **09-16 16:15-20:45** — consolidare linistita 3686-3694, volum jos (610-8118), fara mecanism nou.

- **09-16 20:45-22:15** — pauza zilnica de rollover (~75min, gap pret neglijabil), a 25-a instanta,
  tipar deja cunoscut. Continuare cu tranzactionare subtire (vol 147-1668) pana la 00:00 UTC.

- **09-17 00:00-00:15** — instanta ordinara a ferestrei 00:00 UTC (vol 2824), in intervalul deja
  cunoscut, fara investigatie.

- **09-17 00:15-01:45** — coborare moderata pe volum crescand (5934-12377), varf 3695->minim 3676
  (~19pt/~1h30m), apoi stabilizare choppy fara continuare sustinuta — sub pragul DC-0018
  (volum/amploare mult mai mic), matches tipar deja documentat de volatilitate choppy overnight.
  Fara DC/addendum.

- **09-17 01:45-12:15** — grind ordinar sustinut 3660-3684, volum jos-moderat (504-8987), fara
  mecanism nou.

- **09-17 12:30-12:45** — a 31-a instanta a ferestrei 12:30 UTC ordinara (vol 4538, in intervalul
  deja cunoscut). Fara investigatie.

- **09-17 12:45-16:00** — volatilitate moderat-ridicata la deschiderea NY (vol 3.1k-15.2k), grind
  choppy 3672-3687 fara constructie sustinuta clara, in linia caracterului deja documentat de
  "choppy NY-open". Fara DC/addendum nou.

## STARE: OPRIT — RECONCILIERE HANDOFF FINALIZATA (directiva CEO, 2026-07-23)
Discovery Loop oprit la checkpoint sigur (2025-09-17 16:00 UTC) pentru reconcilierea
administrativa a HANDOFF_LOG.md (vezi raportul de reconciliere livrat in chat). Niciun continut
stiintific (DC-uri, addenda, verdicte, confidence, observatii) nu a fost modificat.

Rezultat reconciliere: 18/18 Discovery Candidates FROZEN au acum linie oficiala in HANDOFF_LOG.md
(5 lipseau: DC-0008..DC-0012, backfilled azi cu data istorica de freeze 2026-07-22); 16/16 fisiere
addendum de pe disc sunt acum logate individual (0 logate anterior); fara duplicate; fara intrari
orfane; index si folders 18/18 aliniate.

Declaratia "index + handoff la zi" este acum adevarata si verificabila (vezi HANDOFF_LOG.md,
sectiunea "Ultima reconciliere administrativa").

Declaratia "fara datorii administrative deschise" NU mai poate fi facuta neconditionat: reconcilierea
a descoperit ca hash-ul inregistrat pentru DC-0001 (sha256:1f1b3d399f2e9613b18d1d4ecaede8d7e3b0dec085ab709482b4d2c3f40cf75c,
identic in candidate_v1.md, metadata_v1.json si HANDOFF_LOG.md intre ele) NU se reproduce printr-o
recalculare independenta a fisierului curent de pe disc (recalculare da sha256:7d6282b2ae29400f3b654a8d9b4a1578a7d8d97edc884595f6879bf90de5438e,
testat cu mai multe variante de normalizare CRLF/placeholder). Hash-ul NU a fost modificat.

**CEO a acceptat raportul de reconciliere (2026-07-23)** si a dispus deschiderea unui item separat,
distinct de structura Discovery Candidate: `DC-0001_HASH_REPRODUCIBILITY_INVESTIGATION.md`
(discovery_candidates/), status OPEN, ramane deschis pana la o investigatie dedicata. Nu este un
Discovery Candidate si nu apare in DISCOVERY_CANDIDATE_INDEX.md.

Un commit administrativ dedicat (doar HANDOFF_LOG.md, SESSION_STATE.md,
DC-0001_HASH_REPRODUCIBILITY_INVESTIGATION.md — fara DC-uri noi, fara config, fara alte modificari
preexistente) urmeaza sa fie creat separat, conform directivei CEO.

## Urmatorul punct de pornire
Reia de la **2025-09-17 16:00 UTC pe M15** (dupa commit-ul administrativ si aprobarea finala CEO
pentru reluarea buclei).

## Stare portofoliu
18 Discovery Candidates: DC-0001 … DC-0018 (toate FROZEN, hash verificat, index + handoff la zi).
DC-0013 (creat 2026-07-23, prima aplicare a filtrului v2) — expansiune NY sustinuta pe 4 lumanari.
Are 1 addendum (A, 2026-07-23): a doua instanta NY-session, 7 lumanari, aceeasi finalizare prin
consolidare.
DC-0014 (creat 2026-07-23, promovat din Observation Registry) — revenire V + expansiune sustinuta
la ora 00:00-01:00 UTC, apoi inversare; comparabil ca amploare cu DC-0013.
DC-0015 (creat 2026-07-23) — expansiune NY sustinuta pe 11 lumanari (~2h45m), cea mai lunga
miscare unidirectionala din familia "expansiune sustinuta mare" (DC-0013/DC-0014/DC-0015).
DC-0016 (creat 2026-07-23) — expansiune Asia timpurie/pre-Londra (01:00-02:45 UTC) pe ~6-7
lumanari, cea mai mare amplitudine (~47.2pt) din familie pana acum, incheiata cu inversare abrupta
la varf marginal nou (tipar similar cu finalul DC-0014). Are 1 addendum (A, 2026-07-23): a doua
instanta la aceeasi ora, 24h mai tarziu, amploare/durata mai mici dar acelasi tipar de final.
DC-0017 (creat 2026-07-23) — impuls de amploare NFP la 12:30 UTC (prima vineri a lunii, vol 30975,
~33.15pt), mentinut pe 4 lumanari suplimentare fara inversare/extindere dramatica; construc'tie
sustinuta multi-minut identica cu DC-0008. Are 2 addenda: A (regimul de volum ridicat a durat de
fapt ~4h15m, nu 1h15m, cu deriva ascendenta usoara) si B (a doua cea mai mare valoare de volum la
12:30 UTC, 25399 pe 09-11, dar rezolvata prin chop bidirectional extins, nu hold — amploarea singura
nu determina rezolutia).
DC-0018 (creat 2026-07-23) — esec complet de breakout la varf nou (3674.695), pe cel mai mare volum
dintr-o singura lumanare din tot replay-ul (36798), urmat de declin sustinut pe 6 lumanari (~47.8pt,
~1h30m); constructie multi-minut sustinuta identica cu familia DC-0008/DC-0013/DC-0015 dar in
directie de coborare, precedata de un breakout esuat (distinct de toate DC-urile anterioare).
DC-0008 are 4 addenda (A-D), DC-0009 are 4 addenda (A-D), DC-0010 are 1 addendum (A), DC-0011 are 2
addenda (A-B), DC-0012 are 1 addendum (A), DC-0013 are 1 addendum (A), DC-0016 are 1 addendum (A),
DC-0017 are 2 addenda (A-B) — 16 addenda in total, dovezi noi, fara schimbare de status/confidence
(decizie ramane la Red Team/Statistician).
Observation Registry: 7 intrari (a 7-a: instanta 2025-08-26 00:00 UTC, promovata la DC-0014).
Fara datorii administrative deschise.
