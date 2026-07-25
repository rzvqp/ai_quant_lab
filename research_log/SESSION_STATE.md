# ALPHA — STARE SESIUNE (ultima actualizare 2026-07-25)

## *** INCHIDERE OFICIALA — ALPHA 1 (2026-07-25) ***

Divizia Alpha ("Alpha 1") este **inchisa oficial** la cererea CEO. Aceasta este o inchidere
administrativa de stare — NU o noua investigatie, NU un nou DC/addendum, NU o promovare la
Knowledge Base. Detalii complete la finalul acestui document, sectiunea
"## Urmatorul punct de pornire" (ultimul checkpoint inainte de inchidere).

**Stare finala a portofoliului la inchidere:**
- **26 Discovery Candidates** (DC-0001 - DC-0026), toate FROZEN, hash verificat.
- **47 addenda** distribuite: DC-0013 (13, A-M), DC-0019 (5, A-E), DC-0023 (3, A-C), DC-0024 (4, A-D),
  DC-0025 (2, A-B), restul DC-urilor cu 0-1 addenda per HANDOFF_LOG.md.
- **18 intrari Observation Registry** (fenomene notate dar nepromovate la DC).
- Replay OANDA:XAUUSD M15: pozitie finala **2026-05-15 20:59:59 UTC** (current_date 1778878799),
  oprit explicit (`replay_stop` confirmat).
- Knowledge Base: **nemodificat**. Red Team: audit independent, NEasteptat/neanticipat de Alpha.
- Niciun DC promovat, nicio validare/invalidare facuta de Alpha (rol strict de observatie, conform
  mandatului).

**Follow-up administrativ la inchidere (2026-07-25, aceeasi zi, comanda CEO separata)** — replay
NEredeschis, niciun DC/addendum nou:
- Investigatia de reproducibilitate a hash-ului DC-0001 **inchisa** (concluzie: hash-ul inregistrat
  nu poate fi reprodus prin nicio metoda documentata; fisierul nu a fost atins de la freeze —
  confirmat via `git log --follow`, un singur commit; decizia de re-emitere ramane a CEO/Red Team).
  Detalii: `DC-0001_HASH_REPRODUCIBILITY_INVESTIGATION.md`.
- `DATA_QUALITY_OPEN_ITEM_2025-09-17_1800UTC.md` **inchis administrativ** (intrebarile substantiale
  raman nerezolvate empiric, predate mai departe; concluzia originala — artefact de date suspectat,
  NU eveniment de piata — ramane finala pentru Alpha 1).
- Contradictia DC-0001 vs OBS-0014 **reconciliata la nivel definitional** — vezi
  `DC0001_OBS0014_RECONCILIATION_NOTE.md` (timeframe M15 vs H1, definitie outlier diferita, orizont
  diferit; testul stiintific decisiv ramane deschis, in sarcina Red Team/Statistician, NU Alpha).
- Red Team **F2** (DC-0022 revendica record de familie 86.75pt, gresit fata de recordul curent al
  familiei -- DC-0024 Addendum D = **514.165pt**; DC-0013 Addendum H (180.53pt) era doar o valoare
  intermediara, deja depasita) **corectat** printr-o nota administrativa dedicata, fara a atinge
  textul inghetat: `DC-0022_.../CORRECTION_NOTE_2026-07-25.md` (nota revizuita 2026-07-25 dupa ce
  o versiune anterioara cita gresit doar valoarea 180.53pt).
- Red Team **F4** (DC-0013 citeste inca "One instance" desi are ~12 instante via 13 addenda) **corectat**
  similar: `DC-0013_.../CORRECTION_NOTE_2026-07-25.md`.
- `ALPHA_AUTONOMOUS_STATE.md` **rescris integral** — corecteaza `cycle_id`/"None frozen by Alpha"
  (care omitea cele 26 DC-uri ale Alpha 1) si adauga banner de inchidere pentru a preveni
  reluarea automata a replay-ului de catre orchestrator.
- Inventar administrativ nou: `NONPROMOTED_OBSERVATIONS_2026-01-29_to_2026-05-15.md` — compileaza
  cele doua intrari Observation Registry (17: 2026-01-29, 18: 2026-04-23) din acest interval,
  fara analiza noua.

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

## PROTOCOL DE OBSERVATIE v3 (directiva CEO, 2026-07-24 — SUPERSEDES partial METODOLOGIE de mai sus)
Standardizare a modului de observare, inlocuieste partial sectiunea METODOLOGIE (2026-07-22) de mai
sus in privinta timeframe-ului principal, a autoplay-ului si a caii de coborare in investigatie.
Ramane NESCHIMBAT: filtrul ALPHA DISCOVERY OPTIMIZATION v2 (cele 3 intrebari), regula celor doua
rezultate (DC sau Observation Registry), pragul ridicat pentru DC-uri, testul in 3 pasi pentru
noutate mecanism.

- **Timeframe principal de start: 1H** (nu M15). Context 4H mentinut permanent.
- **Autoplay ACTIVAT la 0.5x** (speed=2000ms per bara, conform mapping-ului tool-ului
  `replay_autoplay`: 1000ms=1x, 2000ms=0.5x) — inlocuieste regula anterioara "Nu activa autoplay".
  Piata se desfasoara natural pe 1H; NU opri pentru fiecare lumanare.
- Cand apare un fenomen ce merita investigat (deplasare puternica, absorbtie, compresie, reactie
  neobisnuita, schimbare de comportament, posibil mecanism nou etc.):
  1. **Pauza** autoplay-ul (`replay_autoplay` toggle OFF).
  2. **Noteaza timestamp-ul** exact (formula solida fata de baza 1761516000).
  3. **Coboara pe 5M** si analizeaza fenomenul in detaliu.
  4. Daca 5M nu e suficient pentru a intelege mecanismul, coboara pe **3M**.
- **3M este DOAR instrument de investigatie pentru un fenomen deja identificat pe timeframe
  superior — NU un punct de plecare.** Nu cauta mecanisme direct pe 3M; zgomotul de pe
  timeframe-uri mici nu genereaza mecanisme reale, doar modele false.
- Dupa investigatia pe 5M/3M, se aplica in continuare regula celor doua rezultate (DC nou sau
  Observation Registry) si testul in 3 pasi inainte de orice promovare la DC.
- Scopul ramane neschimbat: descoperirea de mecanisme reale ale pietei, nu modele generate de
  zgomotul din timeframe-uri mici.

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

## STARE: ACTIV — reconciliere handoff finalizata, commit administrativ creat, bucla reluata
Reconcilierea administrativa a HANDOFF_LOG.md (directiva CEO, 2026-07-23) e finalizata si
ACCEPTATA de CEO. Commit administrativ dedicat creat (`005f837`, doar HANDOFF_LOG.md,
SESSION_STATE.md, DC-0001_HASH_REPRODUCIBILITY_INVESTIGATION.md — fara DC-uri noi, fara config,
fara alte modificari preexistente). Niciun continut stiintific (DC-uri, addenda, verdicte,
confidence, observatii) nu a fost modificat in reconciliere. Discovery Loop reluat din checkpoint-ul
2025-09-17 16:00 UTC.

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

- **09-17 16:00-18:00** — grind ordinar 3682-3688, volum jos (2987-5232), fara mecanism nou.

- **09-17 18:00-19:00** — **suspiciune de artefact de date**: lumanara 18:00-18:15 UTC (ora FOMC)
  are un range de ~56.3pt (3651.33-3707.59) pe doar 12556 volum — disproportie clara fata de
  DC-0017/0018 (30-37k vol pentru range-uri comparabile). Verificat M1: volum aproape constant
  (~800-870/minut) pe toate cele 4 lumanari M15 din aceasta ora, inclusiv un wick de ~30pt intr-un
  singur minut fara nicio semnatura de volum distincta — tipar incompatibil cu date tick reale.
  -> **Fara DC/Observation Registry** (posibil artefact de sinteza/backfill al feed-ului, nu
  fenomen de piata). Deschis item separat: `DATA_QUALITY_OPEN_ITEM_2025-09-17_1800UTC.md`
  (research_log/), status OPEN, NU e Discovery Candidate.

- **09-17 19:00-19:15** — normalizare (vol 3192, range ingust), confirmand ca fereastra anterioara
  a fost o anomalie izolata.

- **09-17 19:15-20:45** — consolidare linistita 3657-3660, volum jos (1673-3377), fara mecanism nou.

- **09-17 20:45-22:15** — pauza zilnica de rollover (~76min, gap pret neglijabil), a 26-a instanta,
  tipar deja cunoscut. Continuare cu tranzactionare subtire (vol 1619-2686) pana la 00:00 UTC.

- **09-18 00:00-01:45** — instanta ordinara a ferestrei 00:00 UTC (vol 1619), apoi grind moderat
  3654-3671 cu un episod scurt de volum usor ridicat (vol 4890-7978, ~15pt) la ora 01:15-01:45 UTC
  — sub pragul familiei DC-0016 (15-30k+ vol), stabilizat rapid. Fara DC/addendum.

- **09-18 01:45-12:15** — grind ordinar sustinut 3633-3672, volum jos-moderat pe tot parcursul
  (1572-8890), fara mecanism nou.

- **09-18 12:30-12:45** — a 32-a instanta a ferestrei 12:30 UTC ordinara (vol 6719, in intervalul
  deja cunoscut). Fara investigatie.

- **09-18 12:45-14:15** — volatilitate moderat-ridicata la deschiderea NY (vol 6.5k-10.1k), grind
  choppy 3628-3663 fara constructie sustinuta clara, tipar deja documentat de "choppy NY-open".
  Fara DC/addendum nou.

- **09-18 14:15-18:00** — consolidare linistita 3639-3648, volum jos (1989-4491), fara mecanism
  nou. Verificat ora 18:00 UTC (unde 09-17 s-a gasit artefactul de date): astazi este complet
  ordinara (vol 2903, range normal) — confirma ca anomalia de ieri a fost izolata, nu un tipar
  recurent zilnic.

- **09-18 18:00-20:45** — consolidare linistita continuata 3640-3647, volum jos (586-3653), fara
  mecanism nou.

- **09-18 20:45-22:15** — pauza zilnica de rollover (~76min, gap pret neglijabil), a 27-a instanta,
  tipar deja cunoscut. Continuare cu tranzactionare subtire (vol 586-1806) pana la 00:00 UTC.

- **09-19 00:00-00:15** — instanta ordinara a ferestrei 00:00 UTC (vol 2602), in intervalul deja
  cunoscut, fara investigatie.

- **09-19 00:15-12:15** — grind ordinar sustinut 3632-3661, volum jos-moderat pe tot parcursul
  (1826-6556), inclusiv o miscare-V modesta la 01:30-02:00 UTC (~15pt, vol 4.7-6.6k, sub pragul
  familiei DC-0016) — fara mecanism nou.

- **09-19 12:30-12:45** — a 33-a instanta a ferestrei 12:30 UTC ordinara (vol 4405, in intervalul
  deja cunoscut). Fara investigatie.

- **09-19 12:45-16:00** — grind treptat NY-session 3644-3676, volum jos-moderat (2824-7363), fara
  constructie sustinuta clara (sub pragurile familiei DC-uri), fara mecanism nou.

- **09-19 16:00-20:45** — consolidare linistita 3668-3685, volum jos (1180-5297), fara mecanism nou.

- **09-19 20:45-21:00 -> gap de weekend**: vineri 09-19 21:00 UTC -> duminica 09-21 22:15 UTC (~49h
  intr-un singur pas), gap mic (3685->3687.4) recuperat rapid, a 5-a instanta, tipar deja cunoscut.

- **09-21 22:15 - 09-22 01:00** — tranzactionare subtire ordinara de duminica seara/Asia timpurie,
  volum 1372-4192, fara mecanism nou (inclusiv o instanta ordinara la ora 00:00 UTC, vol 3452).

- **09-22 01:00-01:45** — moderata revenire la ora 01:00 UTC (DC-0016 hour), ~7pt, vol 4.2k-7.3k,
  sub pragul familiei DC-0016; stabilizat rapid. Fara DC/addendum.

- **09-22 01:45-12:15** — grind ordinar sustinut 3686-3728, volum jos-moderat (1673-6791), fara
  mecanism nou (inclusiv un grind gradual 06:15-08:00 UTC de ~20pt pe volum moderat 5-6.8k, sub
  pragul familiei DC-uri).

- **09-22 12:30-12:45** — a 34-a instanta a ferestrei 12:30 UTC ordinara (vol 5826, in intervalul
  deja cunoscut). Fara investigatie.

- **09-22 12:45-16:15** — grind treptat NY-session 3715-3746, volum jos-moderat (3339-9438), fara
  constructie sustinuta clara (sub pragurile familiei DC-uri). Verificat 18:00 UTC (ora
  artefactului de 09-17): astazi ordinar (vol 4159), confirma din nou ca anomalia a fost izolata.

- **09-22 16:15-20:45** — consolidare linistita 3743-3748, volum jos (1163-4290), fara mecanism nou.

- **09-22 20:45-22:15** — pauza zilnica de rollover (~76min, gap pret neglijabil), a 28-a instanta,
  tipar deja cunoscut.

- **09-22 22:15 - 09-23 00:15** — tranzactionare subtire ordinara de seara Asia, volum 975-3317,
  fara mecanism nou (inclusiv instanta ordinara la ora 00:00 UTC, vol 2298).

- **09-23 00:15-07:15** — grind ordinar sustinut/consolidare 3737-3757, volum jos-moderat pe tot
  parcursul (1717-9384), tranzitie spre Londra fara reactie marcanta. Fara mecanism nou.

- **09-23 07:15-08:15** — grind ordinar 4 lumanari consecutive 3759->3791 (~36pt/~1h), volum ramas
  sub 6.3k pe toata durata (sub pragurile familiei DC-0013/15/16, 15-30k+); urmat de inversare/
  retragere pe volum similar, revenind spre 3782-3787. Se potriveste tiparului deja documentat de
  "grind gradual pe volum jos" (vezi 09-15/09-19/09-22). Fara DC/addendum nou.

- **09-23 08:15-12:15** — consolidare linistita 3777-3789, volum jos-moderat (3424-5963). Fara
  mecanism nou.

- **09-23 12:30-12:45** — a 35-a instanta a ferestrei 12:30 UTC ordinara (vol 6301, in intervalul
  deja cunoscut). Fara investigatie.

- **09-23 12:45-14:00** — banda ordinara 3779-3788, volum jos-moderat (4800-7773). Fara mecanism nou.

- **09-23 14:00-19:15** — deschidere si continuare NY choppy (vol pana la 9.4k), profil consistent
  cu deschiderile NY deja documentate; normalizare treptata spre seara (vol 3.8k-6.6k). Fara
  mecanism nou.

- **09-23 19:15-19:45** — declin de ~28.5pt (3780.64->3752.07) pe ~30min, volum M15 modest
  (7351/8690/6947) — sub pragurile familiei DC-0013+ dar peste variatia tipica pentru acest raport
  range/volum. Verificat pe M1: volum variaza organic intre ~198-806/minut, cu varfuri clare aliniate
  exact cu portiunile rapide ale miscarii (696-722 vs. baseline 198-360) — confirma date tick reale,
  NU semnatura de artefact (contrast cu DATA_QUALITY_OPEN_ITEM_2025-09-17). Rezolvat printr-o
  revenire in forma de V pana la 3766+ pe volum similar — se incadreaza in categoria deja exclusa
  "revenire V/coborare simpla fara continuare sustinuta". Fara DC/addendum nou.

- **09-23 19:45-21:00** — continuare revenire si normalizare, volum in scadere spre pauza de
  rollover (1717-6321). Fara mecanism nou.

- **09-23 21:00-22:15** — a 29-a pauza de rollover confirmata (jump 76min, 20:59->22:15).
  Redeschidere curata, fara gap notabil, volum scazut (1268-1408). Fara eveniment.

- **09-23 22:15 -> 09-24 00:15** — tranzactionare subtire ordinara de seara Asia, volum 585-2704,
  fara mecanism nou (inclusiv instanta ordinara la ora 00:00 UTC, vol 2236).

- **09-24 00:15-12:00** — grind ordinar linistit 3752-3778, volum jos pe tot parcursul
  (1667-5914), tranzitie spre Londra fara reactie marcanta. Fara mecanism nou.

- **09-24 12:30-12:45** — a 36-a instanta a ferestrei 12:30 UTC ordinara (vol 6473, in intervalul
  deja cunoscut). Fara investigatie.

- **09-24 12:45-14:00** — banda ordinara 3761-3772, volum jos-moderat (5374-5840). Fara mecanism nou.

- **09-24 14:00-19:45** — deschidere NY choppy (vol pana la 8.5k) urmata de un declin gradual
  sustinut pe multe ore (~3767->3717, ~50pt/~5h45m), volum ramas moderat pe tot parcursul
  (3-8.5k, niciodata concentrat sau exceptional) — constructie graduala pe volum jos, distincta de
  familia "expansiune sustinuta mare" (care necesita 15-30k+ vol fara pullback); se potriveste
  tiparului deja documentat de "grind gradual pe volum jos/declin NY". Fara DC/addendum nou.

- **09-24 19:45-21:00** — revenire partiala 3717->3736, volum in scadere spre pauza de rollover
  (1546-5535). Fara mecanism nou.

- **09-24 21:00-22:15** — a 30-a pauza de rollover confirmata (jump 76min, 20:58->22:20).
  Redeschidere curata, fara gap notabil, volum scazut (1719-2199). Fara eveniment.

- **09-24 22:15 -> 09-25 00:00** — tranzactionare subtire ordinara de seara Asia, volum 897-2776,
  fara mecanism nou (inclusiv instanta ordinara la ora 00:00 UTC, vol 2776).

- **09-25 00:00-08:30** — grind ordinar linistit 3729-3762, volum jos-moderat pe tot parcursul
  (1615-6524), inclusiv o revenire-V modesta la 11:45-12:00 (~16pt, vol 7104, sub pragul familiei
  DC-0016) si o alta la 08:30-09:00 (grind ascendent 3745->3761, vol 5.4-6.5k, sub prag). Tranzitie
  Londra fara reactie marcanta. Fara mecanism nou.

- **09-25 08:30-12:15** — consolidare linistita 3750-3761, volum jos-moderat (3055-5895). Fara
  mecanism nou.

- **09-25 12:30-12:45** — a 37-a instanta a ferestrei 12:30 UTC ordinara (vol 4576, in intervalul
  deja cunoscut). Fara investigatie.

- **09-25 12:45-19:15** — deschidere si continuare NY choppy (vol pana la 10.1k), grind
  bidirectional 3722-3757 fara constructie sustinuta clara, profil consistent cu deschiderile NY
  deja documentate; normalizare treptata spre seara (vol 3.6k-6.4k). Verificat 18:00 UTC (ora
  artefactului de 09-17): astazi ordinar, confirma din nou izolarea anomaliei. Fara mecanism nou.

- **09-25 19:15-21:00** — grind ordinar 3746-3758, volum in scadere spre pauza de rollover
  (1847-5957). Fara mecanism nou.

- **09-25 21:00-22:20** — a 31-a pauza de rollover confirmata (jump 76min, 20:58->22:20).
  Redeschidere curata, fara gap notabil, volum scazut (779-1878). Fara eveniment.

- **09-25 22:20 -> 09-26 00:00** — tranzactionare subtire ordinara de seara Asia, volum 1186-3296,
  fara mecanism nou (inclusiv instanta ordinara la ora 00:00 UTC, vol 2213).

- **09-26 00:00-08:00** — grind ordinar linistit 3735-3752, volum jos pe tot parcursul (1741-6701),
  inclusiv o instanta ordinara la ora 01:00 UTC (DC-0016 hour, vol 6701, sub prag). Tranzitie
  Londra fara reactie marcanta. Fara mecanism nou.

- **09-26 08:00-12:15** — consolidare linistita 3742-3755, volum jos-moderat (2548-5439). Fara
  mecanism nou.

- **09-26 12:30-12:45** — a 38-a instanta a ferestrei 12:30 UTC ordinara (vol 3639, in intervalul
  deja cunoscut). Fara investigatie.

- **09-26 12:45-18:00** — deschidere NY choppy (vol pana la 9.8k) urmata de un grind gradual
  ascendent 3752->3783 (~31pt/~2h15m) pe volum moderat (6-9.6k, niciodata concentrat), apoi
  consolidare treptata. Se potriveste tiparului deja documentat de "grind gradual pe volum jos" —
  distinct de familia "expansiune sustinuta mare" (15-30k+ vol, fara pullback). Verificat 18:00 UTC
  (ora artefactului de 09-17): astazi ordinar, confirma din nou izolarea anomaliei. Fara DC/addendum
  nou.

- **09-26 18:00-21:00** — banda linistita 3765-3783, volum jos (2056-4534), tranzactionare
  subtire spre inchiderea de vineri. Fara mecanism nou.

- **weekend 09-26 20:59 -> 09-28 22:20** — a 6-a instanta a gap-ului de weekend confirmata
  (jump ~49h), gap mic (3759.61->3756.04, ~-3.6pt), retras aproape imediat in prima bara
  (redeschidere pana la 3768.11) — consistent cu gap-urile de weekend deja documentate. Fara
  eveniment.

- **09-28 22:20 -> 09-29 00:00** — tranzactionare subtire ordinara de duminica seara, volum
  1264-3739, fara mecanism nou (inclusiv instanta ordinara la ora 00:00 UTC, vol 3739, prima zi a
  saptamanii noi).

- **09-29 00:00-01:45** — grind ordinar sustinut 3767->3789 (~22pt), volum crescand pana la ~10k
  (varf la 01:15-01:30 UTC, DC-0016 hour), apoi reversal partial la 3767-3775 pe volum in scadere
  (8.3k) — sub pragurile familiei DC-0016 (15-30k+, ~47pt); se potriveste tiparului deja documentat
  de "revenire modesta la ora 01:00 UTC". Fara DC/addendum nou.

- **09-29 01:45-11:15** — grind ordinar sustinut, treptat si distribuit pe multe ore (3767->3820,
  ~53pt/~9.5h), volum ramas moderat pe tot parcursul (3.2k-10k, niciodata concentrat, cu mai multe
  pauze/retrageri intermediare) — se potriveste tiparului deja documentat de "grind gradual pe
  volum jos", distinct de familia "expansiune sustinuta mare" (15-30k+ vol, fara pullback).
  Tranzitie Londra fara reactie marcanta. Fara DC/addendum nou.

- **09-29 11:15-12:15** — consolidare linistita 3817-3831, volum jos-moderat (4218-7360). Fara
  mecanism nou.

- **09-29 12:30-12:45** — a 39-a instanta a ferestrei 12:30 UTC ordinara (vol 7298, in intervalul
  deja cunoscut). Fara investigatie.

- **09-29 12:45-19:00** — deschidere NY choppy (vol pana la 9.3k), grind bidirectional 3809-3833
  fara constructie sustinuta clara, profil consistent cu deschiderile NY deja documentate;
  normalizare treptata (vol 3.3k-6.8k). Verificat 18:00 UTC (ora artefactului de 09-17): astazi
  ordinar, confirma din nou izolarea anomaliei. Fara mecanism nou.

- **09-29 19:00-21:00** — banda linistita 3822-3834, volum jos (2119-5921), tranzactionare
  subtire spre pauza de rollover. Fara mecanism nou.

- **09-29 21:00-22:20** — a 32-a pauza de rollover confirmata (jump 76min, 20:59->22:20).
  Redeschidere curata, fara gap notabil, volum scazut (1692-1812). Fara eveniment.

- **09-29 22:20 -> 09-30 00:00** — tranzactionare subtire ordinara de seara Asia, volum 1010-2545,
  fara mecanism nou (inclusiv instanta ordinara la ora 00:00 UTC, vol 2545).

- **09-30 00:00-07:00** — grind ordinar sustinut 3829->3872 (~43pt/~7h), volum jos-moderat pe tot
  parcursul (2.3k-6.6k), inclusiv o instanta ordinara la ora 01:00 UTC (vol 6.6k, sub prag).
  Tranzitie Londra fara reactie marcanta. Fara mecanism nou.

- **09-30 07:00-10:15** — declin gradual dar neobisnuit de amplu 3871.74->3793.19 (~78.5pt/~3h15m),
  volum ramas jos-moderat pe tot parcursul (5.4k-9.7k, niciodata concentrat, cu multiple pauze
  interne de consolidare la 3815-3822 si 3798-3806) — cea mai mare amplitudine totala observata
  pana acum pentru tiparul "grind gradual pe volum jos" (peste DC-0013 ~43pt si DC-0016 ~47pt ca
  puncte, dar sub pragul de volum al familiei, 15-30k+, si fara constructia fara-pullback ceruta).
  Notat distinct pentru comparatie viitoare, dar NU promovat la DC/addendum — construc'tia
  (multi-ora, multi-pauza, volum niciodata concentrat) ramane calitativ diferita de familia
  "expansiune sustinuta mare".

- **09-30 10:15-12:15** — stabilizare/revenire partiala 3793->3818, volum jos-moderat (4.3k-5.7k).
  Fara mecanism nou.

- **09-30 12:30-12:45** — a 40-a instanta a ferestrei 12:30 UTC ordinara (vol 6199, in intervalul
  deja cunoscut). Fara investigatie.

- **09-30 12:45-15:15** — continuare NY choppy, banda 3810-3830, volum moderat (5.7k-8.7k), profil
  consistent cu deschiderile NY deja documentate. Fara mecanism nou.

- **09-30 15:15-16:15** — impuls modest 3820->3852 (~32pt/~45min), volum sub prag (7.2k-9.6k, varf
  descrescand), urmat de reversal V la 3832.58 (~21.5pt) — se potriveste tiparului deja documentat
  de "impuls-apoi-reversal" la volum sub-prag. Fara DC/addendum nou.

- **09-30 16:15-21:00** — normalizare treptata, banda 3838-3862, volum jos-moderat (2.2k-6.4k).
  Verificat 18:00 UTC (ora artefactului de 09-17): astazi ordinar, confirma din nou izolarea
  anomaliei. Fara mecanism nou.

- **09-30 21:00-22:20** — a 33-a pauza de rollover confirmata (jump 76min, 20:59->22:20).
  Redeschidere curata, fara gap notabil, volum scazut (2236-2289). Fara eveniment.

- **09-30 22:20 -> 10-01 00:00** — tranzactionare subtire ordinara de seara Asia, volum 969-2402,
  fara mecanism nou (inclusiv instanta ordinara la ora 00:00 UTC, vol 1359).

- **10-01 00:00-07:30** — grind ordinar sustinut/consolidare 3858-3866, volum jos-moderat pe tot
  parcursul (1.4k-6.8k), inclusiv o instanta ordinara la ora 01:00 UTC (vol 2.8k, sub prag).
  Tranzitie Londra fara reactie marcanta. Fara mecanism nou.

- **10-01 07:30-09:15** — grind ordinar sustinut 3859->3895 (~36pt/~1h45m), volum jos-moderat
  (4.6k-7k, niciodata concentrat). Se potriveste tiparului deja documentat de "grind gradual pe
  volum jos". Fara DC/addendum nou.

- **10-01 09:15-12:15** — consolidare/retragere partiala 3882-3894, volum jos-moderat (3.5k-5.5k).
  Fara mecanism nou.

- **10-01 12:30-12:45** — a 41-a instanta a ferestrei 12:30 UTC ordinara (vol 4098, in intervalul
  deja cunoscut). Fara investigatie.

- **10-01 12:45-16:00** — deschidere NY choppy (vol pana la 10.7k), grind bidirectional 3855-3891
  fara constructie sustinuta clara, profil consistent cu deschiderile NY deja documentate.
  Fara mecanism nou.

- **10-01 16:00-21:00** — normalizare treptata, banda 3855-3871, volum jos-moderat (2.1k-6.9k).
  Verificat 18:00 UTC (ora artefactului de 09-17): astazi ordinar, confirma din nou izolarea
  anomaliei. Fara mecanism nou.

- **10-01 21:00-22:20** — a 34-a pauza de rollover confirmata (jump 76min, 20:58->22:20).
  Redeschidere curata, fara gap notabil, volum scazut (1802-2379). Fara eveniment.

- **10-01 22:20 -> 10-02 00:00** — tranzactionare subtire ordinara de seara Asia, volum 1209-3220,
  fara mecanism nou (inclusiv instanta ordinara la ora 00:00 UTC, vol 3220).

- **10-02 00:00-07:00** — grind ordinar linistit 3852-3874, volum jos pe tot parcursul (1.1k-5.2k),
  inclusiv o instanta ordinara la ora 01:00 UTC (vol 3.7k, sub prag). Tranzitie Londra fara reactie
  marcanta. Fara mecanism nou.

- **10-02 07:00-12:15** — grind ordinar linistit 3862-3886, volum jos-moderat (2.7k-5.5k). Fara
  mecanism nou.

- **10-02 12:30-12:45** — a 42-a instanta a ferestrei 12:30 UTC ordinara (vol 3979, in intervalul
  deja cunoscut). Fara investigatie.

- **10-02 12:45-15:00** — deschidere si continuare NY choppy (vol pana la 9.3k), grind bidirectional
  3880-3897 fara constructie sustinuta clara, profil consistent cu deschiderile NY deja documentate.
  Fara mecanism nou.

- **10-02 15:00-16:45** — **declin NY sustinut, cea mai mare amplitudine din familie**: 3896.79 ->
  3825.21 (~71.6pt) pe 6 lumanari consecutive fara pullback real (o singura pauza marginala
  +2.17pt), apoi stabilizare/consolidare 2 lumanari suplimentare — acelasi tipar de finalizare
  (consolidare, nu inversare abrupta) ca DC-0013 original si Addendum A. Volum ramas remarcabil de
  constant dar NOTABIL SUB pragul deja documentat al familiei (8.6k-11.4k pe lumanara vs 15-30k+ la
  DC-0013/Addendum A) — verificat pe M5: volum distribuit organic pe aproape fiecare sub-lumanara,
  crescand odata cu accelerarea pretului (NU semnatura de artefact). Aceasta e cea mai mare
  amplitudine observata in familie pana acum, la cel mai mic volum per-lumanara -> **Addendum B la
  DC-0013** (slabeste caracterizarea "volum mare per lumanara e obligatoriu" — sugereaza ca
  persistenta directionala sustinuta pe multe lumanari poate substitui volumul absolut ridicat).

- **10-02 16:45-17:15** — stabilizare confirmata dupa declin, banda 3826-3840, volum revenit la
  normal (7.1k-8.7k). Fara mecanism nou suplimentar.

- **10-02 17:15-21:00** — banda linistita 3838-3859, volum jos-moderat (2.8k-7.4k). Fara mecanism
  nou.

- **10-02 21:00-22:20** — a 35-a pauza de rollover confirmata (jump 76min, 20:58->22:20).
  Redeschidere curata, fara gap notabil, volum scazut (1187-1694). Fara eveniment. (Notа: 10-02 e
  joi, deci aceasta e pauza zilnica obisnuita; inchiderea de vineri 10-03 21:00 UTC va fi gap-ul de
  weekend, nu pauza zilnica.)

- **10-02 22:20 -> 10-03 00:00** — tranzactionare subtire ordinara de seara Asia, volum 1045-2476,
  fara mecanism nou (inclusiv instanta ordinara la ora 00:00 UTC, vol 2324).

- **10-03 00:00-07:00** — grind ordinar linistit 3839-3860, volum jos pe tot parcursul (1.9k-4.9k),
  inclusiv o instanta ordinara la ora 01:00 UTC (vol 4.9k, sub prag). Tranzitie Londra fara reactie
  marcanta. Fara mecanism nou.

- **10-03 07:00-12:15** — grind ordinar linistit 3855-3868, volum jos-moderat (2.4k-4.7k). Fara
  mecanism nou.

- **10-03 12:30-12:45** — a 43-a instanta a ferestrei 12:30 UTC ordinara (vol 4400, in intervalul
  deja cunoscut). Fara investigatie.

- **10-03 12:45-16:45** — deschidere si continuare NY choppy (vol pana la 10.2k), grind bidirectional
  3862-3891 fara constructie sustinuta clara, profil consistent cu deschiderile NY deja documentate
  (inclusiv o revenire-V modesta la 15:30 UTC, ~20pt, vol ~9-10k, sub prag). Fara mecanism nou.

- **10-03 16:45-21:00** — banda linistita 3880-3889, volum jos-moderat (2.7k-6.7k). Verificat 18:00
  UTC (ora artefactului de 09-17): astazi ordinar, confirma din nou izolarea anomaliei. Fara
  mecanism nou.

- **weekend 10-03 20:59 -> 10-05 22:00** — a 7-a instanta a gap-ului de weekend confirmata (jump
  ~49.25h), gap mic (3886.50->3887.98, ~+1.5pt), in intervalul deja cunoscut. Fara eveniment.

- **10-05 22:00-22:45** — redeschidere Asia (Sunday), volum moderat (3.5k-4.7k), fara reactie
  marcanta. Fara mecanism nou.

- **10-05 22:45-00:00** — impuls modest la reluarea Asia de duminica (3893.68->3920.87, ~27pt/45min,
  vol pana la 8.4k), apoi stabilizare ~3910; instanta ordinara la ora 00:00 UTC (vol 7.7k). Sub
  pragul familiei DC-uri. Fara mecanism nou.

- **10-06 00:00-06:30** — grind ordinar sustinut, treptat pe multe ore (3899->3945, ~46pt/~5h),
  volum ramas jos-moderat pe tot parcursul (3.2k-6.4k, niciodata concentrat, cu pauze intermediare),
  apoi retragere partiala spre 3925-3932. Se potriveste tiparului deja documentat de "grind gradual
  pe volum jos". Tranzitie Londra fara reactie marcanta. Fara DC/addendum nou.

- **10-06 06:30-12:15** — grind ordinar Londra 3927-3950, volum jos-moderat (3.6k-7.3k), fara
  reactie marcanta la vreo zona. Fara mecanism nou.

- **10-06 12:30-12:45** — a 44-a instanta a ferestrei 12:30 UTC ordinara (vol 8045, in intervalul
  deja cunoscut). Fara investigatie.

- **10-06 12:45-16:15** — deschidere si continuare NY choppy (vol pana la 9.2k), grind ascendent
  gradual 3934-3964 fara constructie sustinuta clara, profil consistent cu deschiderile NY deja
  documentate. Fara mecanism nou.

- **10-06 16:15-17:45** — impuls la varf nou (3970.07) urmat de reversal modest (~24pt, vol ~8.9k)
  si stabilizare — se potriveste tiparului deja documentat de "reversal modest la varf nou, sub
  pragul DC-0018" (36798 vol). Fara DC/addendum nou.

- **10-06 17:45-21:00** — banda linistita 3952-3965, volum jos-moderat (2.7k-6.1k). Verificat 18:00
  UTC (ora artefactului de 09-17): astazi ordinar, confirma din nou izolarea anomaliei. Fara
  mecanism nou.

- **10-06 21:00-22:20** — a 36-a pauza de rollover confirmata (jump 76min, 20:58->22:20).
  Redeschidere cu volatilitate usor mai mare (14.1pt, vol 3509) dar in intervalul deja cunoscut.
  Fara eveniment.

- **10-06 22:20 -> 10-07 00:00** — tranzactionare subtire ordinara de seara Asia, volum 3.2k-5.3k,
  fara mecanism nou (inclusiv instanta ordinara la ora 00:00 UTC, vol 3355).

- **10-07 00:00-06:30** — grind ordinar linistit 3955-3977, volum jos-moderat pe tot parcursul
  (2.7k-6.6k), inclusiv o instanta ordinara la ora 01:00 UTC (vol 6.1k, sub prag) si un declin
  modest la 05:30 (~17pt, vol 5.1-5.6k, sub prag). Tranzitie Londra fara reactie marcanta. Fara
  mecanism nou.

- **10-07 06:30-12:15** — grind ordinar Londra 3941-3970, volum jos-moderat (3.0k-8.9k), fara
  reactie marcanta la vreo zona. Fara mecanism nou.

- **10-07 12:30-12:45** — a 45-a instanta a ferestrei 12:30 UTC ordinara (vol 5441, in intervalul
  deja cunoscut). Fara investigatie.

- **10-07 12:45-17:45** — deschidere NY si sesiune choppy prelungita (vol pana la 11k, niciodata
  peste prag), grind bidirectional 3961-3991 fara constructie sustinuta clara pe multe lumanari
  consecutive, profil consistent cu deschiderile/sesiunile NY deja documentate ca elevate dar
  choppy. Fara DC/addendum nou.

- **10-07 17:45-19:00** — banda linistita 3976-3987, volum jos-moderat (6.1k-7.1k). Verificat 18:00
  UTC (ora artefactului de 09-17): astazi ordinar, confirma din nou izolarea anomaliei. Fara
  mecanism nou.

- **10-07 19:00-21:00** — banda linistita 3978-3987, volum jos-moderat (2.4k-6.6k). Fara mecanism
  nou.

- **10-07 21:00-22:20** — a 37-a pauza de rollover confirmata (jump 76min, 20:58->22:20).
  Redeschidere curata, fara gap notabil, volum scazut (2023-2077). Fara eveniment.

- **10-07 22:20 -> 10-08 00:00** — tranzactionare subtire ordinara de seara Asia, volum 1.6k-2.6k,
  fara mecanism nou (inclusiv instanta ordinara la ora 00:00 UTC, vol 3778).

- **10-08 00:00-06:15** — grind ordinar sustinut, treptat pe multe ore (3990->4037, ~47pt/~6h),
  volum ramas jos-moderat pe tot parcursul (3.1k-6.9k, niciodata concentrat, cu pauze intermediare),
  inclusiv o instanta ordinara la ora 01:00 UTC (vol 6.9k, sub prag) si traversarea nivelului rotund
  4000 fara reactie marcanta (tipar deja documentat). Se potriveste tiparului deja documentat de
  "grind gradual pe volum jos". Tranzitie Londra fara reactie marcanta. Fara DC/addendum nou.

- **10-08 06:15-12:15** — grind ordinar Londra 4021-4049, volum jos-moderat (3.2k-7.2k), fara
  reactie marcanta la vreo zona. Fara mecanism nou.

- **10-08 12:30-12:45** — a 46-a instanta a ferestrei 12:30 UTC ordinara (vol 4585, in intervalul
  deja cunoscut). Fara investigatie.

- **10-08 12:45-17:15** — deschidere si continuare NY choppy (vol pana la 10.8k, niciodata peste
  prag), grind bidirectional 4026-4051 fara constructie sustinuta clara, profil consistent cu
  deschiderile/sesiunile NY deja documentate. Fara mecanism nou.

- **10-08 17:15-21:00** — banda linistita/choppy 4032-4059, volum jos-moderat (2.2k-8.6k). Fara
  mecanism nou.

- **10-08 21:00-22:00** — a 38-a pauza de rollover confirmata (jump 76min, 20:59->22:15).
  Redeschidere **choppy/whipsaw** (range 29.4pt, vol M15 4393) — verificat pe M1: volum organic
  crescand exact in minutul cu wick-ul cel mai adanc (642 vs. baseline 175-250), NU semnatura de
  artefact. A doua instanta a acestui tipar deja documentat (prima: 08-07 pauza #4, range 18.4pt,
  vol 3569) -> confirma tiparul, fara DC/addendum nou (memorie deja acopera "redeschidere
  choppy/whipsaw" ca varianta posibila a pauzei zilnice).

- **10-08 22:15 -> 10-09 00:00** — tranzactionare subtire, volum revenind la normal (2.5k-5.4k) dupa
  stabilizarea reopen-ului choppy, fara mecanism nou (inclusiv instanta ordinara la ora 00:00 UTC,
  vol 7489, sub prag).

- **10-09 00:00-01:45** — grind ordinar Asia 4011-4036 (vol 4.7k-9.9k), incluzand o revenire-V
  modesta la ora 01:00-01:30 UTC (~24pt, vol pana la 9.9k, sub pragul DC-0016). Fara DC/addendum
  nou.

- **10-09 01:45-04:00** — declin gradual 4036->4003 (~34pt/~1h) pe volum in scadere (5.9k-7.7k),
  apoi stabilizare/revenire spre 4028. Se potriveste tiparului deja documentat de "declin
  gradual/choppy pe volum jos". Fara DC/addendum nou.

- **10-09 04:00-09:00** — grind ordinar linistit 4022-4040, volum jos-moderat (2.8k-6.9k), tranzitie
  Londra fara reactie marcanta. Fara mecanism nou.

- **10-09 09:00-12:15** — grind ordinar Londra 4034-4047, volum jos (2.5k-5.0k), fara reactie
  marcanta la vreo zona. Fara mecanism nou.

- **10-09 12:30-12:45** — a 47-a instanta a ferestrei 12:30 UTC ordinara (vol 4183, in intervalul
  deja cunoscut). Fara investigatie.

- **10-09 12:45-15:15** — deschidere si continuare NY choppy (vol pana la 9.5k), grind gradual
  ascendent 4036-4058 fara constructie sustinuta clara, profil consistent cu deschiderile NY deja
  documentate. Fara mecanism nou.

- **10-09 15:15-16:30** — declin NY sustinut ~52pt (4056.78->4004.44) pe 6 lumanari, volum
  remarcabil de constant (9.4k-11.8k) — corespunde indeaproape semnaturii deja stabilite in
  DC-0013 Addendum B (magnitudine mare la volum moderat, 8.6-11.4k), fara sa depaseasca amploarea
  documentata acolo (~71.6pt) si fara dimensiune noua -> a treia instanta confirmatoare, notata in
  jurnal, fara addendum nou.

- **10-09 16:30-17:00** — stabilizare/consolidare 4016-4029, volum revenit spre normal (8.6k-9.7k).
  Fara mecanism nou suplimentar.

- **10-09 17:00-18:15** — banda choppy 4006-4022, volum moderat (6.8k-11k), fara constructie
  sustinuta clara. Fara mecanism nou.

- **10-09 18:15-19:45** — al doilea declin NY sustinut din aceeasi zi: ~68pt (4012.53->3944.77)
  pe 6 lumanari, volum remarcabil de constant (9.3k-11.5k) — semnatura aproape identica cu DC-0013
  Addendum B (~71.6pt, 8.6-11.4k) si cu declinul anterior din aceeasi zi (15:15-16:30, ~52pt,
  9.4-11.8k). A patra instanta confirmatoare a acestui tipar in total, si a doua in aceeasi zi
  calendaristica (10-09) — notat ca observatie de clustering intra-zi, fara a generaliza (esantion
  local, n=2 instante intr-o singura zi). Fara addendum nou (nu depaseste amploarea sau volumul
  deja documentat in Addendum B).

- **10-09 19:45-20:00** — stabilizare/revenire partiala 3950-3965, volum revenit spre normal
  (9.0k-9.3k). Fara mecanism nou suplimentar.

- **10-09 20:00-22:20** — banda linistita 3971-3982, volum jos (1.8k-7.1k). A 39-a pauza de
  rollover confirmata (jump 76min, 20:59->22:20). Redeschidere choppy/whipsaw (range 22.9pt, vol
  M15 3838) — verificat pe M1: volum organic (varf 602 exact la wick-ul cel mai adanc), a treia
  instanta a tiparului deja documentat (prima 08-07, a doua 10-08). Fara DC/addendum nou.

- **10-09 22:20 -> 10-10 00:00** — tranzactionare subtire, volum revenind spre normal (1.8k-4.3k)
  dupa stabilizarea reopen-ului choppy, fara mecanism nou (inclusiv instanta ordinara la ora 00:00
  UTC, vol 4328).

- **10-10 00:00-03:45** — grind ordinar linistit 3970-3995, volum jos-moderat pe tot parcursul
  (3.7k-7.6k), inclusiv o instanta ordinara la ora 01:00 UTC (vol 7.6k, sub prag) si un declin
  gradual modest la 01:15-02:15 (~24.5pt, vol 6.3k-7.5k, sub prag). Fara mecanism nou.

- **10-10 03:45-07:15** — grind ordinar linistit 3947-3978, volum jos-moderat (4.3k-6.9k), tranzitie
  Londra fara reactie marcanta. Fara mecanism nou.

- **10-10 07:15-12:15** — grind ordinar Londra 3952-4007, volum jos-moderat (4.2k-7.9k), inclusiv
  traversarea nivelului rotund 4000 fara reactie marcanta (tipar deja documentat). Fara mecanism
  nou.

- **10-10 12:30-12:45** — a 48-a instanta a ferestrei 12:30 UTC ordinara (vol 6080, in intervalul
  deja cunoscut). Fara investigatie.

- **10-10 12:45-15:00** — deschidere si continuare NY choppy (vol pana la 8.2k), grind bidirectional
  3979-3998 fara constructie sustinuta clara, profil consistent cu deschiderile NY deja documentate.
  Fara mecanism nou.

- **10-10 15:00-16:15** — declin NY sustinut ~27.2pt (3998.11->3970.93) pe 3 lumanari, volum
  remarcabil de constant (10.4k-10.7k) — a treia instanta a semnaturii "volum moderat 9-12k"
  documentata in DC-0013 Addendum B, dar cu o dimensiune genuin noua: acest declin cade in ACEEASI
  fereastra orara (15:00-16:30 UTC) ca prima instanta din 10-09, la o zi calendaristica distanta ->
  **Addendum C la DC-0013** (clustering pe fereastra orara specifica, n=2 pentru fereastra exacta,
  hedge explicit — insuficient pentru a stabili o regularitate, doar notat pentru comparatie
  viitoare). Rezolvat prin stabilizare/revenire partiala, nu inversare abrupta.

- **10-10 16:15-16:30** — stabilizare confirmata, banda 3980-3994, volum revenit spre normal
  (7.8k-8.7k). Fara mecanism nou suplimentar.

- **10-10 16:30-18:00** — swing NY bidirectional pe volum ridicat dar sub prag (8.6k-12.3k): rally
  ~42pt (3980.67->4022.83) urmat de reversal ~45.5pt (4022.83->3977.31), 8 lumanari, apoi
  stabilizare. Nu se potriveste curat cu tiparul declin-unidirectional din Addendum B/C (are un
  leg de rally comparabil inaintea declinului) — se incadreaza in categoria mai larga deja
  documentata de "sesiune NY choppy/volatilitate ridicata cu doua directii". Fara addendum nou.

- **10-10 18:00-18:45** — banda linistita 3975-3987, volum jos-moderat (8.6k-10.2k). Verificat
  18:00 UTC (ora artefactului de 09-17): astazi ordinar, confirma din nou izolarea anomaliei. Fara
  mecanism nou.

- **10-10 18:45-21:00** — banda linistita/choppy 3993-4021, volum jos-moderat (3.8k-8.8k). Fara
  mecanism nou.

- **weekend 10-10 20:59 -> 10-12 22:00** — a 8-a instanta a gap-ului de weekend confirmata (jump
  ~49.25h), gap ceva mai mare decat instantele minime anterioare (~-15.7pt, 4017.25->4001.57), dar
  retras rapid in prima lumanare (redeschidere pana la 4030.5, inchidere 4021.29) — consistent cu
  gap-urile de weekend deja documentate. Fara eveniment.

- **10-12 22:00-23:00** — redeschidere Asia (Sunday), volum moderat (3.5k-5.9k), fara reactie
  marcanta. Fara mecanism nou.

- **10-12 23:00 -> 10-13 09:15** — parcurs silentios ~10h15m (Asia tarzie -> ora 00:00-01:00 UTC ->
  Asia timpurie -> pre-Londra -> Londra deschidere). O usoara revenire modesta la ora ~01:00-01:45
  UTC (4024.68->4059.75, ~35pt, apoi retragere la 4043.76) — se incadreaza in categoria deja
  documentata "revenire modesta la ora DC-0016", fara addendum. Un mic rally-apoi-retragere la
  ~05:15-06:15 UTC (4056.83->4078.08, ~22pt, apoi retragere completa la 4059.54) — amploare/volum
  (max 6854) mult sub orice prag documentat, tipar ordinar. Restul intervalului: chop/grind linistit
  in banda 4059-4079, volum jos-moderat (1.4k-7.3k) tot parcursul, inclusiv la deschiderea Londrei
  (~07:00-08:00 UTC) fara reactie marcanta. Fara mecanism nou, fara artefact de date suspectat.

- **10-13 09:15 -> 19:15** — parcurs silentios 10h (Londra dimineata -> Londra/NY overlap ->
  NY dimineata/dupa-amiaza). Grind gradual, ordinar, in banda 4071-4117, volum jos-moderat pe tot
  parcursul (3.6k-9.9k, un singur varf izolat la 9862 la ~12:45 UTC insotit de o retragere obisnuita
  in aceeasi lumanare, fara continuare). Fereastra orara 15:00-16:30 UTC (clock-time clustering
  notat cu hedge in Addendum C la DC-0013) verificata explicit azi: NU s-a repetat — piata era in
  usoara revenire (rally net ~23pt spre 4116.99), nu declin, iar volumul a ramas 5.9k-6.8k, sub
  pragul de 9-12k documentat; consolidare/retragere ~13pt dupa aceea tot pe volum jos. Nicio noua
  instanta a tiparului, fara addendum, fara mecanism nou.

- **10-13 19:15 -> 23:30** — inchidere NY linistita, volum in scadere (7.1k -> 1.8k), grind ordinar
  4098-4113. Pauza de rollover zilnica confirmata a **40-a instanta** (~75min jump, 4110.51->4110.15,
  fara gap semnificativ, redeschidere organica, volum jos 2043 fara whipsaw). Fara mecanism nou.

- **10-13 23:30 -> 10-14 01:45** — mic rally la ora ~23:30-01:30 UTC (4115->4149.9, ~25pt max), volum
  crescand pana la 9202 dar fara sustinere (a urmat stagnare/consolidare la 4139-4140, volum scazut
  la 1.9k). Amploare/volum sub pragurile familiei DC-0014/DC-0016 (ora ~00:00-02:00 UTC) — se
  incadreaza in categoria deja documentata "variabilitate modesta la ora DC-0016", fara addendum.

- **10-14 01:45 -> 05:30** — grind gradual continuu Asia timpurie/pre-Londra, volum jos-moderat
  (4.3k-7.8k) tot parcursul, deriva lenta ascendenta 4137->4176 pe multe ore fara o singura
  lumanare dominanta — tipar de drift lent, distinct de constructiile "expansiune sustinuta" din
  familia DC-0013/14/15/16 (care implica displacement mare pe putine lumanari, nu drift lent
  multi-ora). Fara mecanism nou, fara artefact de date suspectat.

- **10-14 05:30-07:00** — declin sustinut la volum moderat, dar in ora Londrei timpurii/pre-open
  (05:30-06:45 UTC), NU sesiunea NY unde s-au observat toate instantele anterioare: 4179.78 ->
  4090.41 (~89.4pt), cea mai mare amplitudine din toata familia DC-0013 (depaseste Addendum B ~71.6),
  pe 5-6 lumanari, volum 9863-11816 (aceeasi banda 9-12k documentata in Addendum B/C), cu ceva mai
  mult chop intern bidirectional decat instantele NY curate. Verificat pe M5: volum distribuit
  (1842-4284), fara lumanare dominanta, creste in cea mai abrupta portiune — confirma organic, nu
  artefact. Rezolutie identica cu restul familiei: consolidare 4098-4113, nu inversare brusca.
  Dimensiune noua: prima instanta a acestei constructii in afara sesiunii NY -> **Addendum D la
  DC-0013**.

- **10-14 07:00-12:15** — grind ordinar Londra dimineata/pranz, banda 4116-4145, volum jos-moderat
  (4.7k-7.9k) tot parcursul. Fara mecanism nou.

- **10-14 12:15-14:30** — instanta ordinara a ferestrei 12:30 UTC (nu prima vineri a lunii, fara NFP):
  declin moderat ~30pt (4133.73->4103.6) pe volum 7.2k-8.8k (sub pragul 9-12k), urmat de regim de
  volum ridicat prelungit (~2h, 9.3k-11.1k) dar choppy/bidirectional fara constructie unidirectionala
  clara — se potriveste exact cu tiparul deja documentat in DC-0017 Addendum A (regim de volum
  prelungit dupa 12:30 UTC fara hold direct). Fara addendum nou.

- **10-14 14:30-16:30** — grind/chop ordinar 4126-4155, volum moderat (7.6k-9.8k). Fereastra
  15:00-16:30 UTC (clock-clustering, hedge n=2 in Addendum C) verificata a treia oara: nu s-a
  repetat din nou — piata a fost choppy/usor ascendenta, fara declin unidirectional pe volum
  9-12k. Fara mecanism nou.

- **10-14 16:30-19:45** — inchidere NY ordinara, grind/chop 4131-4155, volum moderat-descrescator
  (5.9k-9.8k). Un mic declin ~15.6pt la ~19:30-19:45 UTC, volum 8768, sub prag. Fara mecanism nou.

- **10-14 19:45-21:45** — banda linistita 4139-4146, volum in scadere spre inchidere. Pauza de
  rollover zilnica confirmata a **41-a instanta** (~75min jump, 4142.24->4143.66, fara gap
  semnificativ, reopen usor ascendent ~18.6pt pe volum jos 3070, fara whipsaw). Fara mecanism nou.

- **10-14 22:00 -> 10-15 02:15** — grind ordinar Asia, volum jos (1.2k-4.9k) tot parcursul, inclusiv
  fereastra 00:00 UTC (chop modest, sub prag). La ora ~01:00-01:45 UTC (fereastra DC-0016) o revenire
  modesta 4162.03->4186.73 (~24.7pt) pe volum 7.2k-9.6k, apoi pullback/stabilizare la 4176-4182 —
  amploare/volum sub pragurile familiei, se incadreaza in categoria deja documentata "variabilitate
  modesta la ora DC-0016". Fara addendum, fara mecanism nou.

- **10-15 02:15-05:30** — grind ordinar Asia, volum jos (1.6k-7.8k) tot parcursul, deriva usoara
  laterala/ascendenta 4172-4193. Fara mecanism nou.

- **10-15 05:30-07:00** — fereastra orara a Addendum D (05:30-06:45 UTC) verificata azi din nou: NU
  s-a repetat declinul de amploare mare — piata a fost ordinara/linistita (4184-4200, volum
  jos-moderat 3.8k-6.4k). Confirma n=1 pentru Addendum D, fara a doua instanta pana acum.

- **10-15 07:00-09:15** — grind ordinar Londra dimineata, deriva usoara ascendenta 4194-4217, volum
  jos (3.8k-5.2k). Fara mecanism nou.

- **10-15 09:15-10:15** — spike/wick brusc in jos (~40pt, 4203.76->4163.67) urmat de recuperare
  imediata in aceeasi lumanare (close 4190.23) si stabilizare, volum 9623 pe lumanara spike apoi
  scazut (1.6k) — tipar V-reversal/coborare simpla fara continuare sustinuta, categorie deja exclusa
  explicit din investigatie automata. Fara addendum, fara mecanism nou.

- **10-15 10:15-12:30** — grind ordinar Londra, banda 4180-4207, volum jos (2.9k-5.1k). Instanta
  ordinara a ferestrei 12:30 UTC: declin modest ~13.75pt pe volum 6.6k-9k, fara continuare
  sustinuta. Fara mecanism nou.

- **10-15 12:30-15:00** — regim de volum ridicat prelungit dupa 12:30 UTC (7.3k-9.6k, ~2h15m),
  choppy/bidirectional fara constructie unidirectionala clara — se potriveste tiparul deja
  documentat (DC-0017 Addendum A). Fara addendum nou.

- **10-15 15:00-16:30** — fereastra clock-clustering (Addendum C) verificata a patra oara: nu s-a
  repetat — declin modest ~16.8pt pe volum 8.6k (sub prag), apoi chop linistit. Ora 18:00 UTC
  (artefactul 09-17) verificata din nou: complet ordinara (volum 6.7k-7.8k, range normal) —
  confirma din nou izolarea anomaliei.

- **10-15 16:30-18:45** — grind/chop ordinar NY dupa-amiaza, banda 4183-4205, volum moderat
  (1.5k-9.3k). Fara mecanism nou.

- **10-15 18:45-21:45** — inchidere NY ordinara, grind 4199-4213, volum in scadere (2.9k-6.3k). Pauza
  de rollover zilnica confirmata a **42-a instanta** (~75min jump, 4208.21->4207.94, fara gap
  semnificativ, reopen ordinar pe volum jos 2762, fara whipsaw). Fara mecanism nou.

- **10-15 22:00 -> 10-16 02:15** — grind ordinar Asia, volum jos-moderat (2.2k-7.1k) tot parcursul,
  inclusiv fereastra 00:00 UTC (chop modest, sub prag), deriva usoara ascendenta 4205->4235. Fara
  mecanism nou.

- **10-16 02:15-05:30** — grind ordinar Asia, volum jos (2.6k-5.7k), deriva usoara laterala
  4224-4240. Fara mecanism nou.

- **10-16 05:30-07:00** — fereastra orara Addendum D reverificata a treia oara: NU s-a repetat
  declinul de amploare mare — in schimb un declin modest ~20.4pt (4224.08->4203.63) pe volum
  9.7k-7.6k urmat de recuperare completa in V (revenire la 4222.64 in aceeasi/urmatoarea lumanare)
  si stabilizare — tipar V-reversal/coborare simpla fara continuare sustinuta, categorie deja
  exclusa din investigatie automata. Confirma din nou n=1 pentru Addendum D.

- **10-16 07:00-08:30** — grind ordinar Londra dimineata, banda 4218-4234, volum jos (3.3k-5.9k).
  Fara mecanism nou.

- **10-16 08:30-12:30** — grind ordinar Londra dimineata/pranz, banda 4218-4247, volum jos
  (2.8k-5.2k). Instanta ordinara a ferestrei 12:30 UTC: rally-decline modest (~23.4pt), volum
  7-8.4k, sub prag. Fara mecanism nou.

- **10-16 12:30-15:00** — regim de volum ridicat prelungit dupa 12:30 UTC (7.1k-9.2k), choppy dar
  net ascendent — se potriveste tiparul deja documentat (DC-0017 Addendum A). Fara addendum nou.

- **10-16 15:00-16:30** — fereastra clock-clustering (Addendum C) verificata a cincea oara: nu s-a
  repetat — piata a fost in rally ordinar (4269->4292), fara declin. La marginea ferestrei
  (16:30-16:45) un swing bidirectional pe volum 9-11.8k (decline ~30pt urmat de recuperare completa
  si continuare la maxim nou 4295.18) — tipar deja exclus explicit (swing bidirectional fara
  constructie unidirectionala). Fara addendum nou.

- **10-16 16:45-17:45** — stabilizare/consolidare 4282-4296, volum in scadere. Fara mecanism nou.

- **10-16 17:45-20:59** — grind/chop ordinar NY dupa-amiaza/inchidere, banda 4273-4331, volum
  jos-moderat (2.8k-9.9k), fara constructie unidirectionala. Fara mecanism nou.

- **rollover 10-16 20:59-22:00** — pauza de rollover zilnica confirmata a **43-a instanta** (~75min
  jump, 4326.01->4332.07, gap mic). Redeschidere neobisnuit de volatila fata de instantele anterioare:
  rally ~54pt (4332.07->4379.95 pe 2 lumanari, volum 7022-7061) urmat de pullback ~36pt
  (4379.95->4343.53, volum 6692) — **a patra instanta confirmata a subtiparului "redeschidere
  choppy/whipsaw"** (dupa 08-07, 10-08, 10-09), cea mai mare amplitudine din acest subtipar pana
  acum. Verificat pe M5: volum distribuit (1889-2828), fara lumanare dominanta — organic, nu
  artefact. Se incadreaza in categoria deja documentata, fara addendum nou.

- **10-16 22:00-23:15** — stabilizare/chop 4341-4364, volum moderat (5.9k-6.3k). Fara mecanism nou.

- **10-16 23:15 -> 10-17 01:00** — grind ordinar Asia, banda 4341-4372, volum jos-moderat
  (3.7k-7.2k), inclusiv fereastra 00:00 UTC (ordinara). Fara mecanism nou.

- **10-17 00:45-02:30** — declin sustinut la volum moderat 9.5k-10.6k: 4371.58 -> 4278.43 (~93.15pt,
  3 lumanari, 00:45-01:30 UTC) — **cea mai mare amplitudine din toata familia DC-0013**, depaseste
  Addendum D. Verificat pe M5: volum distribuit (2072-3884), fara lumanare dominanta, creste in
  faza cea mai abrupta — confirma organic. Spre deosebire de toate instantele anterioare (care s-au
  incheiat prin consolidare), aceasta s-a rezolvat printr-o **recuperare sustinuta comparabila**:
  4278.43 -> 4344.64 (~66.2pt) pe 4 lumanari (01:30-02:30 UTC), acelasi volum moderat, apoi
  stabilizare 4336-4348 (volum sub prag). A treia sesiune distincta pentru aceasta constructie (dupa
  NY si Londra timpurie). Se suprapune partial pe ora DC-0014 (00:00-02:00 UTC) dar cu secventa
  inversata (declin apoi recuperare, nu rally-apoi-inversare) si amploare mult mai mare -> **Addendum
  E la DC-0013**.

- **10-17 03:00-05:30** — grind ordinar Asia, banda 4336-4378, volum jos-moderat (4.4k-7.3k). Fara
  mecanism nou.

- **10-17 05:30-06:45** — fereastra Addendum D reverificata a patra oara: nu s-a repetat — doar
  V-wick-uri ordinare (tipar deja exclus) pe volum 7.2k-9.2k, fara continuare sustinuta.

- **10-17 07:15-09:00** — declin moderat ~45.75pt (4357.39->4311.64) la deschiderea Londrei, volum
  8.5k-9.7k (in banda documentata), urmat de stabilizare/consolidare 4321-4350 — instanta
  confirmatoare a constructiei deja bine documentate (magnitudine sub recordurile B/D/E), fara
  dimensiune noua. Fara addendum.

- **10-17 09:00-11:15** — grind ordinar Londra, banda 4319-4348, volum jos-moderat (4.9k-8.6k). Fara
  mecanism nou.

- **10-17 11:15-13:00** — chop bidirectional pre-12:30 UTC pe volum ridicat (7.6k-10.4k), fara
  constructie unidirectionala clara (multiple swing-uri intre 4283-4322) — se incadreaza in
  categoria deja documentata "swing bidirectional/regim de volum ridicat". Fereastra 12:30 UTC
  ordinara. Fara addendum.

- **10-17 13:30-16:00** — declin sustinut 4317.91 -> 4216.94 (~100.97pt, 3 lumanari, 13:30-14:15
  UTC) pe volum 11930-12768 — **noul record de amploare al familiei DC-0013**, depaseste Addendum E,
  si prima instanta cu volum consistent PESTE banda 9-12k documentata anterior. Verificat pe M5:
  volum distribuit (3934-4373), fara lumanare dominanta — organic. Rezolutie: bounce partial ~49.4pt
  (la 4266.38) urmat de chop extins 4231-4260 (nu recuperare curata ca Addendum E, nici consolidare
  simpla ca A/B/D) — a treia sesiune distincta pentru amploare mare (NY pre-open/early-NY), a patra
  sesiune distincta pentru constructie in ansamblu -> **Addendum F la DC-0013**.

- **10-17 15:45-17:30** — a sasea instanta a constructiei "declin sustinut volum moderat-ridicat"
  (dupa consolidarea Addendum F): 4259.33 -> 4196.71 (~62.6pt) pe 8 lumanari (cea mai lunga durata
  din familie pana acum, dar amploare sub recordurile B/D/E/F), volum consistent 8.7k-11.5k, in
  aceeasi fereastra orara clock-clustering 15:00-16:30 UTC (Addendum C). Rezolutie: bounce partial
  si stabilizare ~4217-4245, volum revenind sub prag. Instanta confirmatoare, fara dimensiune noua
  (durata mai lunga e in variatia deja documentata). Fara addendum.

- **10-17 17:30-20:45** — inchidere NY linistita, grind 4212-4252, volum in scadere (2.9k-8.3k).
  Fara mecanism nou.

- **weekend 10-17 20:45 -> 10-19 22:00** — a **9-a instanta a gap-ului de weekend** confirmata (jump
  ~49.25h), gap aproape nul (~2.63pt, 4251.51->4248.88), redeschidere ordinara (range 4239.44-4274.79,
  volum 7005, fara whipsaw). Fara eveniment.

- **10-19 22:00 -> 10-20 05:15** — redeschidere Asia (Sunday), grind ordinar, volum jos-moderat
  (2.3k-10.4k) tot parcursul, inclusiv ferestrele 00:00 UTC si ora DC-0016 (01:00-01:15, revenire
  modesta ~35pt pe volum 7.8k-10.4k, sub prag). Fara mecanism nou.

- **10-20 05:15-06:45** — fereastra Addendum D reverificata a cincea oara: nu s-a repetat — declin
  modest ~37pt (4263.27->4226.29) pe volum 6.1k-8.5k (sub banda 9-12k documentata), apoi recuperare
  partiala. Fara addendum.

- **10-20 07:15-12:15** — grind ordinar Londra dimineata/pranz, banda 4245-4266, volum jos-moderat
  (4.3k-7.8k). Fara mecanism nou.

- **10-20 12:15-13:15** — impuls la ora 12:30 UTC intr-o zi ordinara (luni, NU prima vineri/NFP):
  4278.42 -> 4327.27 (~48.85pt), depaseste amploarea instantei NFP originale (~33.15pt) din DC-0017,
  dar pe volum mult mai mic (9.9k-10.6k vs 30975 original) — in banda "ordinara" deja documentata.
  Verificat pe M5: volum distribuit (1518-3706), creste in faza de accelerare — organic. Rezolutie:
  hold/consolidare 4313-4327 (nu inversare), identic cu constructia "impuls-apoi-hold" a DC-0017.
  Decupleaza volumul de amploare la aceasta fereastra orara -> **Addendum C la DC-0017**.

- **10-20 13:30-14:30** — declin modest ~27.9pt (4320.53->4292.62) in aceeasi fereastra ca Addendum
  F (13:30-14:15 UTC), volum 10.5k-11.6k (in banda), urmat de recuperare completa la 4334.59 (~42pt
  bounce) — magnitudine mult sub recordul F (~101pt), instanta ordinara confirmatoare. Fara addendum.

- **10-20 14:30-16:30** — grind ordinar NY, banda 4317-4351, volum moderat (5.5k-9.3k). Fereastra
  15:00-16:30 UTC (clock-clustering, Addendum C la DC-0013) verificata a sasea oara: nu s-a repetat.
  Fara mecanism nou.

- **10-20 16:30-19:15** — grind ordinar NY dupa-amiaza, banda 4337-4367, volum jos-moderat
  (4.4k-7.4k). Fara mecanism nou.

- **10-20 19:15-20:59** — inchidere NY, grind 4346-4381, volum jos-moderat (5.7k-8.2k). Fara
  mecanism nou.

- **rollover 10-20 20:59-22:00** — pauza de rollover zilnica confirmata a **44-a instanta** (~75min
  jump, 4356.4->4353.92, gap mic), reopen ordinar (~14.9pt rally, volum 4660, fara whipsaw). Fara
  mecanism nou.

- **10-20 22:00 -> 10-21 02:30** — grind ordinar Asia, volum jos-moderat (2.6k-5.8k) tot parcursul,
  inclusiv fereastra 00:00 UTC (ordinara). La ora ~01:00-01:45 UTC (fereastra DC-0016) un declin
  modest ~39.46pt (4372.24->4332.78) pe volum 7.5k-9.6k (majoritar sub prag), apoi stabilizare
  4339-4355 — sub recordurile familiei, instanta confirmatoare. Fara addendum.

- **10-21 02:30-05:30** — grind ordinar Asia, banda 4335-4351, volum jos (3.1k-7.2k). Fara mecanism
  nou.

- **10-21 05:30-06:45** — fereastra Addendum D reverificata a sasea oara: nu s-a repetat — declin
  modest ~18.3pt (4335.69->4317.41) pe volum 5.3k-8.5k (sub banda documentata), apoi stabilizare.
  Fara addendum.

- **10-21 06:45-07:30** — grind ordinar Londra dimineata, banda 4322-4344, volum jos-moderat
  (5.8k-7.6k). Fara mecanism nou.

- **10-21 07:30-09:00** — declin sustinut 4334.57 -> 4243.76 (~90.81pt, 4 lumanari, 07:30-08:30 UTC)
  pe volum 9997-11451 (in banda extinsa a familiei) — a treia cea mai mare amplitudine din familie.
  Verificat pe M5: volum distribuit (1827-3922), creste in faza cea mai abrupta — organic. Rezolutie:
  recuperare partiala ~30.35pt (o treime din declin), apoi stabilizare — a doua instanta a tiparului
  "recuperare partiala" din Addendum F. A cincea sesiune distincta (Londra mijlocul diminetii,
  07:30-08:30 UTC, diferita de fereastra Addendum D 05:30-06:45) -> **Addendum G la DC-0013**.

- **10-21 09:00-11:45** — grind ordinar Londra, banda 4249-4276, volum jos-moderat (6.2k-8.1k). Fara
  mecanism nou.

- **10-21 11:45-18:15** — episod extins, cel mai mare din toata familia: declin 4261.07 -> 4080.54
  (~180.53pt!) pe ~12 lumanari (11:45-14:45 UTC, 3h), volum sustinut 9.4k-12.7k. Verificat pe M5 pe
  portiunea cea mai abrupta (16:00-16:45 UTC region): volum distribuit (3773-4348), fara lumanare
  dominanta — organic. Spre deosebire de toate instantele anterioare, NU s-a rezolvat printr-o
  singura mișcare de recuperare/consolidare, ci prin **~3.5h suplimentare (14:45-18:15 UTC) de
  oscilatie extinsa** intre 4080-4267 (mai multe leg-uri de recuperare partiala si declin reinnoit),
  tot pe volum ridicat, inainte de stabilizare finala ~4111-4119. Episod total ~6.5h (~26 lumanari)
  — de peste 3 ori mai lung decat orice instanta anterioara. Se suprapune cu ferestrele 12:30 UTC,
  deschiderea NY, si clock-clustering 15:00-16:30 UTC -> **Addendum H la DC-0013** (cel mai
  semnificativ pana acum).

- **10-21 18:30-20:59** — inchidere NY linistita, grind 4090-4131, volum in scadere (2.9k-8.5k).
  Fara mecanism nou.

- **rollover 10-21 20:59-22:00** — pauza de rollover zilnica confirmata a **45-a instanta** (~75min
  jump, 4125->4125.13, fara gap, reopen ordinar, volum jos 4381, fara whipsaw). Fara mecanism nou.

- **10-21 22:00-23:45** — grind ordinar Asia, volum jos (2.8k-4k). Fara mecanism nou.

- **10-21 23:45 -> 10-22 01:45** — declin rapid si mare la ora 00:00 UTC: 4124.60 -> 4004.54
  (~120.06pt) in doar **2 lumanari (30 min)** — a doua cea mai mare amplitudine din familie (dupa
  Addendum H), cea mai rapida instanta mare din familie. Volum 11726/10659, in banda. Verificat pe
  M5: volum distribuit (1515-4138), creste in faza de accelerare — organic. Rezolutie: recuperare
  aproape completa (~116.27pt, ~97% retragere) pe 6 lumanari, volum revenind sub prag — cea mai
  completa recuperare din familie (depaseste Addendum E ~71%). Coincide cu ora DC-0014 (00:00-01:00
  UTC) -> **Addendum I la DC-0013**.

- **10-22 01:45-05:30** — grind ordinar Asia, banda 4103-4143, volum jos (4.1k-6.7k). Fara mecanism
  nou.

- **10-22 05:30-06:45** — fereastra Addendum D reverificata a saptea oara: nu s-a repetat — grind
  ordinar 4127-4147, volum 4.9k-6.9k (sub prag). Fara addendum.

- **10-22 06:45-07:45** — grind ordinar Londra, banda 4130-4162, volum jos-moderat (6.1k-10.1k).
  Fara mecanism nou.

- **10-22 07:45-10:00** — declin ~73.07pt (4135.83->4062.76) pe 7 lumanari (~1h45m), volum
  9.3k-10.8k (in banda), Londra mijlocul diminetii — aceeasi sesiune generala ca Addendum G dar
  amploare sub recordul acelei sesiuni (~90.81pt); rezolutie prin stabilizare simpla. Instanta
  confirmatoare, fara dimensiune noua. Fara addendum.

- **10-22 10:00-12:45** — declin ~75.75pt (4090.9->4015.17) pe volum 9k-10.5k, Londra
  mijloc-dimineata (10:30-11:30 UTC), urmat de chop extins ~1h30m suplimentar (4015-4050, volum
  8.6k-9.7k) inainte de stabilizare finala. Amploare/durata sub recordurile deja documentate (G
  ~90.81pt, H ~6.5h) — instanta confirmatoare, fara dimensiune noua. Fara addendum.

- **10-22 12:45-17:15** — regim de volum ridicat prelungit dupa 12:30 UTC (~4h30m, volum 8.6k-11.9k),
  choppy/bidirectional in cea mai mare parte, cu o scurta faza de declin ~61.4pt (14:15-15:00 UTC)
  urmata de recuperare — se potriveste tiparul deja documentat (DC-0017 Addendum A: regim extins,
  fara constructie unidirectionala sustinuta). Volum revine sub prag catre 17:00 UTC. Fara addendum
  nou.

- **10-22 17:15-20:59** — inchidere NY ordinara, grind 4044-4113, volum jos-moderat (2.6k-9k). Fara
  mecanism nou.

- **rollover 10-22 20:59-22:00** — pauza de rollover zilnica confirmata a **46-a instanta** (~75min
  jump, 4098.48->4095.54, fara gap semnificativ, reopen ordinar ~23pt range, volum jos 4688, fara
  whipsaw). Fara mecanism nou.

- **10-22 22:00-22:30** — redeschidere Asia (Sunday), volum jos (4k-4.7k), fara reactie marcanta.
  Fara mecanism nou.

- **10-22 22:30 -> 10-23 02:45** — grind ordinar Asia, volum jos (3.5k-8.9k) tot parcursul, inclusiv
  fereastra 00:00 UTC (ordinara, fara repetare a Addendum I) si ora DC-0016 (01:00-01:15, modesta,
  sub prag). Fara mecanism nou.

- **10-23 02:45-05:30** — grind ordinar Asia, banda 4079-4100, volum jos (2.8k-6.6k). Fara mecanism
  nou.

- **10-23 05:30-06:45** — fereastra Addendum D reverificata a opta oara: nu s-a repetat — rally
  modest ~27.77pt (4110.18->4137.95) pe volum 9k-9.8k (marginal in banda dar rally, nu declin),
  urmat de pullback ordinar. Fara addendum.

- **10-23 07:00-09:15** — grind ordinar Londra dimineata, banda 4091-4120, volum jos-moderat
  (4.6k-8k). Fara mecanism nou.

## FEREASTRA DE DISCOVERY REDESCHISA (CEO DECISION, 2026-07-24) — bucla Alpha reluata de la
checkpoint-ul 2025-10-23 09:15 UTC. Rol reconfirmat: motor exclusiv de observatie (fara validare,
comparatie, prioritizare, promovare KB). Metodologie/filtre/praguri neschimbate. Cadenta buclei
60s ramane in vigoare.

## FEREASTRA DE DISCOVERY INCHISA (istoric) — 2025-10-23 09:15 UTC (CEO DECISION: HARD STOP, acum inlocuita de redeschidere)
Replay-ul a ajuns exact la granita `holdout_cutoff` declarata in metadatele DC-0014 si DC-0017
(`pre_holdout_2025-10-23T09-15-00Z_v1`). CEO a confirmat explicit (2026-07-24): holdout_cutoff este
HARD STOP. Nicio lumanare ulterioara acestui punct nu a fost analizata, nicio dovada nu a fost
colectata dupa acest moment. Replay-ul (`replay_stop`) a fost oprit, sesiunea de cercetare este
formal inchisa. Fereastra completa acoperita: **2025-09-24 00:15 UTC -> 2025-10-23 09:15 UTC**
(~29 zile de piata, M15, fara sarituri, fara Fast Replay). Vezi raportul final de fereastra pentru
sinteza completa (addenda, recomandari Red Team, intrebari deschise, lectii metodologice).

Nu s-a promovat niciun Discovery Candidate. Nu s-a modificat Knowledge Base. Red Team NU a inceput.
Urmatoarea fereastra de replay NU a inceput. Bucla asteapta aprobarea CEO pentru etapa urmatoare.

- **10-23 09:15-12:30** — grind ordinar Londra, banda 4101-4125, volum jos-moderat (4.7k-7.6k).
  Fara mecanism nou.

- **10-23 12:30-14:45** — impuls ordinar la 12:30 UTC (rally 4109->4128, volum 8.3k-9.1k), urmat
  de regim de volum ridicat prelungit ~1h45m (9.1k-11k, choppy dar net ascendent) — se potriveste
  tiparul deja documentat (DC-0017 Addendum A). Volum revine sub prag catre 14:45 UTC. Fara
  mecanism nou.

- **10-23 14:45-18:45** — grind ordinar NY, banda 4125-4152, volum jos-moderat (3.9k-8.1k). Fereastra
  15:00-16:30 UTC (clock-clustering, Addendum C la DC-0013) verificata a saptea oara: nu s-a repetat.
  Ora 18:00 UTC (artefactul 09-17) reverificata: ordinara. Fara mecanism nou.

- **10-23 18:45-20:59** — inchidere NY ordinara, grind 4107-4140, volum jos-moderat (3.3k-6.1k).
  Fara mecanism nou.

- **rollover 10-23 20:59-22:00** — pauza de rollover zilnica confirmata a **47-a instanta** (~75min
  jump, 4126.07->4127.19, fara gap semnificativ, reopen ordinar, volum jos 3022, fara whipsaw).
  Fara mecanism nou.

- **10-23 22:00-22:30** — redeschidere Asia, volum jos (2.4k-3k), fara reactie marcanta. Fara
  mecanism nou.

- **10-23 22:30 -> 10-24 02:00** — grind ordinar Asia, volum jos (1.8k-6.4k) tot parcursul, inclusiv
  fereastra 00:00 UTC (ordinara, fara repetare a Addendum I) si ora DC-0016 (01:00-01:15, modesta
  ~15.35pt, sub prag). Fara mecanism nou.

- **10-24 02:00-05:15** — grind ordinar Asia, banda 4102-4126, volum jos (2.5k-6.4k). Fara mecanism
  nou.

- **10-24 05:15-06:45** — fereastra Addendum D reverificata a noua oara: nu s-a repetat — declin
  modest ~23.43pt (4104.98->4081.55) pe volum 7.4k-7.5k (sub banda documentata), apoi recuperare
  ordinara. Fara addendum.

- **10-24 06:45-07:30** — grind ordinar Londra dimineata, banda 4086-4098, volum jos-moderat
  (4.4k-5.6k). Fara mecanism nou.

- **10-24 07:30-10:15** — declin modest ~43.92pt (4091.37->4047.45) pe volum 5.6k-9k, Londra
  mijloc-dimineata (aceeasi sesiune ca Addendum G, dar mult sub recordul acelei sesiuni ~90.81pt),
  rezolvat prin recuperare/stabilizare ordinara. Restul intervalului: grind linistit 4054-4074,
  volum jos-moderat. Instanta confirmatoare, fara dimensiune noua. Fara addendum.

- **10-24 10:15-12:15** — grind ordinar Londra, banda 4044-4067, volum jos-moderat (4.3k-8.3k).
  Fara mecanism nou.

- **10-24 12:15-15:30** — impuls la 12:30 UTC intr-o zi ordinara (vineri, NU prima vineri/NFP):
  4061.27 -> 4135.02 (~73.75pt) — **noul record de amploare non-NFP pentru aceasta familie**,
  depaseste Addendum C (~48.85pt), pe volum 8.9k-10.9k (in banda documentata). Verificat pe M5:
  volum distribuit (2156-3802), fara lumanare dominanta — organic. Rezolutie: chop bidirectional
  extins (nu hold curat ca C, ci similar cu Addendum B), stabilizare ~4113-4128. -> **Addendum D la
  DC-0017**.

- **10-24 15:30-18:15** — grind ordinar NY, banda 4104-4137, volum jos-moderat (4.9k-8.1k).
  Fereastra 15:00-16:30 UTC verificata din nou (fara suprapunere cu impulsul de mai devreme): nu s-a
  repetat clock-clustering-ul. Ora 18:00 UTC reverificata: ordinara. Fara mecanism nou.

**[Notă tehnică]** Intre acest checkpoint și reluare, conexiunea MCP `tradingview` (port 9222) a
picat, a fost investigată o instrument-schimbare temporară la FOREXCOM:XAUUSD (respinsă — volum 0
pe toate barele, diferență structurală majoră, niciodată folosită pentru observație), și conexiunea
a fost recuperată prin auto-lansare TradingView Desktop (`shell:AppsFolder`, aplicație Windows
Store) cu `--remote-debugging-port=9222`. CEO a confirmat OANDA:XAUUSD ca sursă oficială finală.
Replay-ul a fost repoziționat exact la checkpoint-ul de mai jos prin 73 de pași `replay_step`
consecutivi de la `2025-10-24` (fără sărituri), verificat identic cu prețurile/volumul deja
observate înainte de întrerupere. Niciun Discovery Candidate sau Addendum nu a fost pierdut sau
modificat în acest interval.

- **10-24 18:15-21:45** — grind linistit de inchidere NY/tranzitie, banda 4098-4139, volum jos
  (4.3k-7.7k), rate de schimbare descrescatoare spre inchiderea de vineri. Fara mecanism nou.

- **weekend 10-24 21:45 -> 10-26 22:00** — **a 10-a instanta a gap-ului de weekend**, dar prima cu o
  rezolutie diferita: gap **~28.43pt** (4114.125->4085.70), noul record de amploare (depaseste
  fostul record ~15.7pt din 10-10->10-12 cu aproape 2x). Bara de redeschidere a atins intrabar
  4107.575 (la doar 6.55pt de umplere completa), parand initial sa urmeze tiparul deja cunoscut de
  retragere rapida — dar urmatoarele lumanare au inversat si au extins declinul **sub insusi
  pretul de deschidere al gap-ului**, continuand ~9 lumanari (pana la minim intrabar 4058.205 /
  inchidere 4064.665, ~00:15 UTC luni), pe volum 4.7k-8.5k (sub banda 9-12k a familiei DC-0013).
  Verificat pe M5: volum distribuit (1.1k-4.8k), fara lumanare dominanta — organic. Dupa
  stabilizare (3 lumanari), a inceput o recuperare (close 4090.195 pe volum 13384, cel mai mare din
  secventa), ajungand la maxim intrabar 4097.87, apoi oscilatie 4088-4098 — recuperare **partiala**
  (~30-33pt din ~50-56pt pierdute), nu completa. Prima instanta din cele 10 in care un gap de
  weekend nu doar esueaza sa se umple, ci se extinde sustinut in directia gap-ului -> **DC-0019
  nou** (promovat din Observation Registry).

- **10-26 22:00 -> 10-27 01:45** — vezi DC-0019 de mai sus pentru descrierea completa a secventei
  declin-stabilizare-recuperare. La finalul intervalului observat, pretul oscileaza 4088-4098,
  recuperare partiala in curs, fara continuare clara inca.

- **10-27 01:45-06:15** — recuperarea partiala din DC-0019 s-a dovedit nedurabila: pretul a cedat
  complet castigul si a extins declinul ~2h15m suplimentare (01:45-04:00 UTC) pana la un **nou
  minim marginal** (intrabar 4053.71, sub minimul initial 4058.205), pe volum similar-moderat
  (3.9k-7.4k), verificat organic pe M5. A urmat o a doua recuperare partiala (~04:00-05:00 UTC,
  pana la 4081.89), apoi stabilizare/consolidare stransa 4076-4085 pana la finalul intervalului
  (inchideri aproape plate). Eveniment multi-leg, nu o singura miscare curata -> **Addendum A la
  DC-0019**.

- **10-27 06:15-08:45** — grind linistit de consolidare, banda 4058-4084, volum jos-moderat
  (5.9k-11.7k). Fara mecanism nou.

- **10-27 08:45-09:15** — declin rapid 4058.885->4024.34 (~37.4pt in 2 lumanari) pe volum crescut
  (14.9k-15.1k), urmat de recuperare/stabilizare imediata (2 lumanari) inapoi la 4037-4048. Amploare
  sub recordurile documentate, volum spike scurt (nu sustinut). Instanta confirmatoare, fara
  addendum.

- **10-27 09:15-12:30** — grind ordinar Londra/pre-NY, banda 4015-4048, volum moderat (6.2k-14.9k).
  Ora 12:30 UTC verificata: lumanare ordinara (4034.74->4034.94, vol 12697), fara impuls. Fara
  mecanism nou.

- **10-27 13:30-15:15** — declin sustinut 4033.95->3971.445 (~55-62.5pt) pe **7 lumanari (~1h45m)**,
  fereastra NY pre-open/early-NY (aceeasi sesiune generala ca Addendum F), pe volum **19.5k-26.9k
  sustinut** — noul record de banda de volum sustinuta pentru familie, aproape dublu fata de
  recordul anterior (Addendum F, 11.9k-12.8k), apropiindu-se de scala NFP (30975) fara sa o atinga.
  Verificat pe M5: volum distribuit (6k-10k per sub-bara), fara lumanare dominanta — organic.
  Rezolutie: recuperare partiala (~15pt din ~62.5pt) pe 4 lumanari, volum scazand (19.5k->12.4k) ->
  **Addendum J la DC-0013**.

- **10-27 16:15-20:59** — recuperare/consolidare graduala dupa Addendum J, grind 3987-4010, volum
  moderat-descrescator (7.6k-15.8k), fara continuare clara catre nivelul pre-declin (~4033-4046).
  Fara mecanism nou.

- **rollover 10-27 20:59-22:15** — pauza de rollover zilnica confirmata (~75min jump, 3981.985->
  3990.015, gap mic +8.03pt), reopen ordinar (range 13.3pt, volum jos 2503, fara whipsaw). Fara
  mecanism nou.

- **10-27 22:15 -> 10-28 00:15** — grind ordinar Asia, volum jos (1.9k-5.9k), inclusiv fereastra
  00:00 UTC (ordinara, 13.7pt range, vol 5854, sub prag). Fara mecanism nou.

- **10-28 00:15-05:30** — grind ordinar Asia/Londra timpurie, banda 3953-4020, volum jos-moderat
  (3.1k-14.3k). Fereastra Addendum D reverificata a zecea oara (05:30 start): fara repetare imediata
  in primele bare. Fara mecanism nou.

- **10-28 05:30-09:00** — declin sustinut extins: 3980.1->3886.465 (~89-94pt dupa referinta, egaleaza
  practic recordul Addendum D ~89.37pt), dar pe **~14 lumanari (~3h30m)** — de peste 2x mai lung
  decat Addendum D (~1h15m), pe volum 6.8k-14k (mediu, ceva mai jos si mai variabil decat banda
  stransa 9.9k-11.8k a lui D). Traverseaza continuu fereastra Addendum D (05:30-06:45) si fereastra
  Addendum G (07:30+) ca o singura miscare neintrerupta — prima data cand aceste doua ferestre
  separate se dovedesc a fi un singur declin continuu. Verificat pe M5: volum distribuit (1.9k-5k),
  fara lumanare dominanta — organic. Rezolutie: consolidare/recuperare partiala (catre ~3910),
  acelasi tipar de final ca restul familiei -> **Addendum K la DC-0013**.

- **10-28 09:45-12:15** — grind ordinar Londra/pre-NY, banda 3897-3933, volum jos-moderat
  (8.8k-14.7k). Fara mecanism nou.

- **10-28 12:15-12:45** — ora 12:30 UTC verificata: lumanare modesta (3921.725->3916.2, ~10.7pt),
  vol 14784, fara impuls. Fara mecanism nou.

- **10-28 12:45-15:45** — regim de volum ridicat prelungit dupa 12:30 UTC (~3h, volum 13.2k-22.7k),
  choppy/bidirectional (3912-3960), fara constructie unidirectionala sustinuta — se potriveste
  tiparul deja documentat (DC-0017 Addendum A). Volum revine la baseline (9.6k) catre 15:45 UTC. Net
  rezultat: pret usor mai sus (3916->3958) dar prin chop extins, nu miscare curata. Fara addendum
  nou.

- **10-28 15:45-20:59** — grind linistit de inchidere NY, banda 3945-3970, volum jos-moderat
  (3.2k-15.2k). Fara mecanism nou.

- **rollover 10-28 20:59-22:15** — pauza de rollover zilnica confirmata (~75min jump), reopen
  **whipsaw pe volum subtire**: pe M1, o singura lumanare a oscilat ~44pt (3949.985->3907.925->
  3952.19) in ~2 minute pe doar 348-783 volum, apoi s-a stabilizat rapid — semnatura identica cu
  Observation Registry (intrarea #3, 2025-08-07 22:00 UTC): range mare, volum subtire, opusul unei
  miscari directionale genuine. Nu artefact de date nou, ci alta instanta a tiparului deja
  catalogat — fara entry noua in Registry, doar notat aici. Fara mecanism nou.

- **10-28 22:15-23:30** — normalizare dupa whipsaw, grind ordinar 3934-3950, volum jos-moderat
  (3.3k-6.1k). Fara mecanism nou.

- **10-28 23:30 -> 10-29 05:30** — grind ordinar Asia, banda 3943-3984, volum jos-moderat
  (2.5k-12.2k), inclusiv fereastra 00:00 UTC (ordinara, 10.1pt, vol 7385, sub prag). Fara mecanism
  nou.

- **10-29 05:30-07:15** — fereastra Addendum D reverificata a unsprezecea oara: de data aceasta
  rally usor (3957.975->3981.925), nu declin — nicio repetare a tiparului D/K. Volum jos-moderat
  (6.3k-8.9k). Fara mecanism nou.

- **10-29 07:15-12:15** — grind ordinar Londra/pre-NY, rally usor sustinut 3978->4029, volum
  jos-moderat (6k-14.7k). Fara mecanism nou.

- **10-29 12:15-13:15** — ora 12:30 UTC verificata: lumanare modesta (4028.45->4026.395, ~7.3pt),
  vol 15650, fara impuls. Volumul revine la normal imediat (9.4k-12.3k) — fara regimul extins
  prelungit vazut in alte zile. Fara mecanism nou.

- **10-29 13:15-17:45** — declin moderat 4025.79->3989.52 (~36.3pt intrabar) pe ~2h15m, volum
  variabil-ridicat (7.4k-22.9k, majoritar 13-19k) — se potriveste tiparul "regim extins NY"
  deja documentat, amploare/volum sub recordurile familiei (DC-0013). Rezolutie prin recuperare/
  stabilizare (3987-4001). Instanta confirmatoare, fara addendum.

- **10-29 17:45-18:00** — grind linistit, banda 3985-3998, volum jos (1.4k-4k). Fara mecanism nou.

- **10-29 18:00-20:30** — episod major: matura minim proaspat (3978.655) apoi puseu la maxim proaspat
  (4007.875, peste nivelul pre-miscare) in aceeasi lumanare, urmat de esec si inchidere aproape de
  minim (vol 28523). Declinul continua, apoi o lumanare (18:30-18:45) atinge **volum 37204 — noul
  record absolut de volum pe o singura lumanare din tot replay-ul** (depaseste DC-0018, 36798).
  Episodul nu se rezolva printr-o singura directie: bounce (3954->3970), apoi declin la un minim
  si mai jos (3927.86, sub minimul lumanarii de volum record), apoi bounce din nou, inainte ca
  volumul sa revina la normal (9034, apoi 6857) si pretul sa se stabilizeze 3937-3954. Amploare
  totala ~80pt (H4007.875-L3927.86), ~67pt de la nivelul pre-miscare. 8 lumanari consecutive la
  volum ridicat (15k-37k) pe ~2h15m. Verificat pe M5 pe lumanarea record: 6948/15895/14361,
  concentrare maxima 42.7% — identic cu pragul acceptat de DC-0018 ca organic. Ora 18:00 UTC are
  istoric de artefact suspectat (09-17), dar aceasta instanta e clar organica si de amploare mare,
  contrastand cu acea ingrijorare -> **DC-0020 nou**.

- **rollover 10-29 20:59-22:15** — pauza de rollover zilnica confirmata (~75min jump), reopen
  ordinar (gap mic -9pt, range 23.3pt, volum jos 4327). Fara mecanism nou.

- **10-29 22:15 -> 10-30 02:00** — grind ordinar Asia, volum jos-moderat (2.6k-10.9k), inclusiv
  fereastra 00:00 UTC (ordinara, 11.4pt, vol 6893, sub prag). Fara mecanism nou.

- **10-30 02:00-05:30** — grind ordinar Asia, banda 3915-3959, volum jos-moderat (4.8k-13k). Fara
  mecanism nou.

- **10-30 05:30-06:45** — fereastra Addendum D reverificata a douasprezecea oara: rally usor
  (3950.26->3971.115), nu declin — nicio repetare a tiparului D/K. Volum jos-moderat (8.2k-10.8k).
  Fara mecanism nou.

- **10-30 06:45-12:15** — grind ordinar Londra/pre-NY, banda 3958-4012, volum jos-moderat
  (5.9k-14.3k). Fara mecanism nou.

- **10-30 12:15-12:45** — ora 12:30 UTC verificata: lumanare modesta (3982.335->3970.98, ~14.9pt),
  vol 14408, fara impuls major. Fara mecanism nou.

- **10-30 12:45-15:30** — regim de volum ridicat prelungit dupa 12:30 UTC (~2h45m, volum
  12.5k-26.9k, aproape de recordul Addendum J), choppy/bidirectional (3961-4015, un puseu pana la
  4011 apoi retragere la 3987, stabilizare 3993-4004) — se potriveste tiparul deja documentat
  (DC-0017 Addendum A), fara constructie unidirectionala sustinuta desi volumul a fost neobisnuit de
  ridicat. Fara addendum nou (aceeasi categorie, nu o dimensiune noua).

- **10-30 15:30-18:00** — grind ordinar dupa-amiaza NY, banda 3991-4020, volum jos-moderat
  (3.7k-12.7k). Fara mecanism nou.

- **10-30 18:00-18:15** — ora 18:00 UTC reverificata (a doua instanta, dupa episodul extrem DC-0020
  de ieri): complet ordinara (9.63pt, vol 8812) — confirma hedge-ul explicit din DC-0020 ca n=2,
  fara pattern stabilit. Fara mecanism nou.

- **10-30 18:15-20:59** — grind ordinar inchidere NY, banda 4016-4028, volum jos-moderat
  (1.7k-17k). Fara mecanism nou.

- **rollover 10-30 20:59-22:15** — pauza de rollover zilnica confirmata (~75min jump), reopen
  ordinar (gap mic -3.06pt, volum jos 1871). Fara mecanism nou.

- **10-30 22:15 -> 10-31 04:00** — grind ordinar Asia, banda 3991-4046, volum jos-moderat
  (2.4k-12.1k), inclusiv fereastra 00:00 UTC (ordinara, 8.1pt, vol 6089, sub prag). Fara mecanism
  nou.

- **10-31 04:00-05:30** — grind ordinar Asia tarzie, banda 3989-4011, volum jos-moderat (4.4k-8k).
  Fara mecanism nou.

- **10-31 05:30-07:30** — fereastra Addendum D reverificata a treisprezecea oara: rally usor
  (4001.965->4016.86), nu declin — nicio repetare a tiparului D/K. Volum moderat (7.4k-12.2k). Fara
  mecanism nou.

- **10-31 07:30-12:15** — grind ordinar Londra/pre-NY, banda 3998-4027, volum jos-moderat
  (4.6k-10.7k). Fara mecanism nou.

- **10-31 12:15-12:45** — ora 12:30 UTC verificata: lumanare modesta (4012.58->4019.465, ~13.4pt),
  vol 11724, fara impuls major. Fara mecanism nou.

- **10-31 12:45-16:00** — regim de volum ridicat prelungit dupa 12:30 UTC, de data aceasta neobisnuit
  de lung (~3h15m, volum 13.3k-20.9k), choppy/bidirectional (4010-4036), fara constructie
  unidirectionala sustinuta — pretul net aproape neschimbat (4019->4021) desi volumul a ramas ridicat
  pe toata durata. Se potriveste tiparul deja documentat (DC-0017 Addendum A), doar durata este mai
  lunga decat instantele anterioare ale acestei categorii. Fara addendum nou.

- **10-31 16:00-18:00** — declin moderat 4021->3972.285 (~48.8pt) pe volum 13.8k-22k, urmat de
  stabilizare 3980-3990 — amploare/volum sub recordurile familiei, instanta confirmatoare. Fara
  addendum.

- **10-31 18:00-20:59** — grind linistit de inchidere NY, banda 3991-4010, volum jos-moderat
  (0.8k-8.3k). Fara mecanism nou.

- **weekend 10-31 20:59 -> 11-02 23:15** — a **12-a instanta a gap-ului de weekend** confirmata
  (jump ~50.25h), gap mic (4002.81->3995.47, ~-7.34pt), retras/normalizat rapid (redeschidere
  3990.91-3999.335, volum jos 1.9k-2.4k) — consistent cu tiparul original al primelor 9 instante,
  NU cu DC-0019 (confirma ca DC-0019 ramane un outlier, nu noul comportament tipic).

- **11-02 23:15 -> 11-03 02:45** — grind ordinar Asia/redeschidere duminica, banda 3963-4007, volum
  jos-moderat (3.5k-12.4k), inclusiv fereastra 00:00 UTC (ordinara). Fara mecanism nou.

- **11-03 02:45-06:00** — grind linistit Asia tarzie/Londra timpurie, banda 3997-4018, volum jos
  (2.5k-8.6k). Fereastra Addendum D (05:30 UTC) traversata fara repetare (grind linistit, nu
  declin). Fara mecanism nou.

- **11-03 06:00-10:00** — grind ordinar Londra dimineata, banda 3993-4028, volum jos-moderat
  (5.1k-11.1k), inclusiv un declin modest (~29pt, 4021->3993) confirmator, sub prag, urmat de
  stabilizare. Fara mecanism nou.

- **11-03 10:00-13:30** — grind ordinar Londra/pre-NY, banda 3994-4020, volum jos-moderat
  (5.7k-8.5k), inclusiv fereastra 12:30 UTC (rally usor, vol pana la 16k, fara impuls major). Fara
  mecanism nou.

- **11-03 13:30-16:30** — regim de volum ridicat prelungit (~3h, volum 9.5k-21k), choppy/
  bidirectional (4001-4031, puseu la 4030 apoi retragere la 4001, fara constructie unidirectionala
  sustinuta) — se potriveste tiparul deja documentat (DC-0017 Addendum A). Volum incepe sa
  normalizeze (15k) catre finalul intervalului. Fara addendum nou.

- **11-03 16:30-20:59** — grind linistit de inchidere NY, volum normalizat (4.2k-9.8k), banda
  3995-4012. Fara mecanism nou.

- **rollover 11-03 20:59-22:15** — pauza de rollover zilnica confirmata (~75min jump, dupa o
  perioada de lichiditate foarte subtire 1.1k-2k volum inainte de pauza), reopen ordinar (gap mic
  +3.51pt, dar range intern ~23.7pt pe volum jos 3252, stabilizare ulterioara). Fara mecanism nou.

- **11-03 22:30 -> 11-04 01:30** — grind ordinar Asia, banda 3979-3995, volum jos-moderat
  (2.9k-12.6k), inclusiv fereastra 00:00 UTC (ordinara, sub prag). Fara mecanism nou.

- **11-04 01:30-05:30** — grind ordinar Asia tarzie/Londra timpurie, banda 3975-3999, volum jos
  (2.6k-7.3k). Fara mecanism nou.

- **11-04 05:30-06:15** — fereastra Addendum D reverificata a paisprezecea oara: declin modest
  ~9pt (3992.06->3983.18), volum jos (2.6k-4.9k, sub banda documentata) — nicio repetare. Fara
  mecanism nou.

- **11-04 06:15-12:15** — grind ordinar Londra/pre-NY, banda 3966-4000, volum jos-moderat
  (3.9k-9.5k). Fara mecanism nou.

- **11-04 12:15-15:00** — ora 12:30 UTC verificata: lumanare ordinara (3996.165->3991.685, ~6.6pt,
  vol 4537, fara impuls). Grind ordinar NY dupa-amiaza, banda 3986-3999, volum jos-moderat
  (4.2k-8.6k). Fara mecanism nou.

- **11-04 15:00-20:00** — grind ordinar NY, banda 3983-4000, volum jos-moderat (3.9k-13.6k), choppy
  fara constructie unidirectionala sustinuta. Fara mecanism nou.

- **11-04 20:00-23:15** — declin moderat 3996->3928.685 (~67pt intrabar) pe volum ridicat
  (9.8k-23.6k), urmat de regim extins choppy/bidirectional (3928-3968, fara constructie
  unidirectionala sustinuta) — se potriveste tiparul deja documentat (DC-0017 Addendum A), de data
  aceasta la ora inchiderii NY, nu imediat dupa 12:30 UTC. Fara addendum nou.

- **11-04 23:15 -> 11-05 02:30** — normalizare volum si stabilizare, grind ordinar Asia, banda
  3932-3972, volum jos-moderat (4.2k-11.8k). Rollover-ul zilnic a trecut fara jump vizibil (a doua
  instanta cu acest comportament, dupa 11-03 -> 11-04) — notat ca variatie tehnica, nu mecanism de
  piata. Fara mecanism nou.

- **11-05 02:30-06:15** — grind ordinar Asia tarzie, banda 3931-3944, volum jos (0.9k-10.4k).
  Fereastra Addendum D (05:30 UTC) traversata fara repetare (grind linistit). Fara mecanism nou.

- **rollover si continuare** — pauza de rollover zilnica confirmata (~75min jump), reopen ordinar
  (gap mic +5.83pt, volum jos), urmata de grind ordinar Asia foarte linistit (volum 0.9k-3.5k) pana
  la current_date **1762302599**.

**[Nota tehnica — corectie etichetare orara]** Verificare directa a pozitiei curente fata de
referinta solida (`1761516000` = 2025-10-26 22:00:00 UTC, confirmata repetat pe parcursul
sesiunii) arata ca current_date 1762302599 corespunde exact la **2025-11-05 00:29:59 UTC**
(delta = 786599s = 9 zile, 2h29m59s), NU la ora aproximata prin urmarire incrementala manuala
folosita in etichetele scrise mai sus pentru intervalul aproximativ 10-30 -> 11-05 (care s-a
dovedit a fi deviat cu cateva ore, cel mai probabil in jurul zilelor 11-03/11-04 unde pauza de
rollover nu a produs un salt vizibil in observatiile mele si urmarirea manuala nu a fost
re-verificata). Secventa de preturi/volum observata si inregistrata este corecta si continua
(citita direct din tool la fiecare pas, nu estimata) — doar etichetele de ora/data din acel
interval pot fi decalate cu pana la ~8h fata de pozitia reala de replay. Nu s-a pierdut sau
suprapus nicio bara; nu a fost nevoie de nicio derulare inapoi sau salt inainte pentru a ajunge
aici. De acum inainte, orice eticheta de checkpoint va fi calculata exclusiv prin formula solida
(delta fata de baza confirmata), nu prin numarare incrementala.

- **11-05 00:30-03:30** — grind ordinar Asia, banda 3929-3956, volum jos-moderat (2.1k-11.9k). Fara
  mecanism nou.

- **11-05 03:30-05:15** — fereastra Addendum D (05:30 UTC) apropiata/traversata: rally usor
  (3953.36->3973.905), nu declin — nicio repetare. Volum jos (2.8k-4.8k). Fara mecanism nou.

- **11-05 05:15-08:30** — grind ordinar Londra timpurie, banda 3961-3987, volum jos-moderat
  (2.2k-8.5k). Fara mecanism nou.

- **11-05 08:30-10:45** — grind ordinar Londra dimineata, banda 3956-3986, volum jos (2.7k-5.3k).
  Fara mecanism nou.

- **11-05 10:45-12:45** — grind ordinar pre-NY, banda 3957-3970, volum jos (2.2k-7.3k). Ora 12:30
  UTC verificata: lumanare ordinara (3967.5->3964.585, ~5pt), vol 2515, fara impuls. Fara mecanism
  nou.

- **11-05 12:45-16:00** — grind ordinar NY, banda 3964-3985, cu un episod de volum ridicat
  prelungit (~1h30m, 11.9k-19.3k), choppy/bidirectional fara constructie unidirectionala sustinuta
  — se potriveste tiparul deja documentat (DC-0017 Addendum A). Volum normalizeaza catre finalul
  intervalului. Fara addendum nou.

- **11-05 16:00-17:45** — grind ordinar de inchidere NY, banda 3974-3990, volum jos-moderat
  (2.5k-8.7k). Fara mecanism nou.

- **11-05 17:45-20:00** — grind linistit de inchidere NY, banda 3978-3989, volum jos (2.4k-5.7k).
  Fara mecanism nou.

- **11-05 20:00-21:45** — grind foarte linistit spre finalul sesiunii NY, banda 3981-3990, volum
  foarte jos (0.6k-4.7k, scazand progresiv). Fara mecanism nou.

- **rollover 11-05 21:45-23:15** — pauza de rollover zilnica confirmata (~75min jump, dupa un
  interval de lichiditate extrem de subtire 0.5k-0.6k volum), reopen ordinar (gap mic -11.3pt,
  volum jos 3281). Fara mecanism nou.

- **11-05 23:15 -> 11-06 01:15** — grind ordinar Asia, banda 3964-3978, volum jos (1k-5.6k),
  inclusiv fereastra 00:00 UTC (ordinara, 4.9pt, vol 2298, sub prag). Fara mecanism nou.

- **11-06 01:15-03:30** — grind ordinar Asia tarzie, banda 3967-3986, volum jos (1.3k-4.6k). Fara
  mecanism nou.

- **11-06 03:30-05:30** — grind ordinar Asia tarzie/Londra timpurie, banda 3982-3990, volum foarte
  jos (0.6k-2.5k). Fara mecanism nou.

- **11-06 05:30-08:00** — fereastra Addendum D traversata (rally usor, nu declin — nicio repetare),
  urmata de grind ordinar Londra dimineata cu rally moderat 3984->4009, volum jos-moderat
  (1.3k-7.4k). Fara mecanism nou.

- **11-06 08:00-14:00** — grind ordinar Londra/pre-NY, rally continuu moderat 4005->4019.6 pe volum
  jos-moderat (3.9k-9.4k), o singura lumanare cu volum usor ridicat (14.5k, 07:00-07:15 UTC
  aproximativ) care s-a rezolvat prin continuare ordinara (nu esec/reversal) — verificat filtrul v2,
  fara mecanism nou. La 14:00 UTC a inceput episodul documentat ca DC-0021 (vezi mai jos).

- **11-06 17:00-20:45** — grind ordinar NY-dupa-amiaza, chop usor descendent apoi rally usor
  3979->3995 apoi retragere la 3980-3987, volum jos-moderat (6.1k-10.8k). Fara mecanism nou.

- **11-06 20:45-21:15** — puseu de volum tip absorbtie (25,601, deplasare minima ~5.5pt, verificat
  organic pe M5: 38.3% concentrare maxima, sub pragul 42.7%) urmat de o prabusire de volum abrupta
  si sustinuta (~92% intr-un singur pas, mentinuta o ora) in fereastra deja cunoscuta de lichiditate
  subtire dinaintea pauzei de rollover zilnic. Nu creeaza DC — forma de absorbtie are deja precedent
  (DC-0012), iar subtierea se rezolva in artefactul deja documentat de rollover; notat in Observation
  Registry (intrarea #9) doar pentru comparatie viitoare (cadere abrupta intr-un singur pas vs.
  decaderea graduala pe mai multe lumanari observata la coada fazei de absorbtie din DC-0021, in
  aceeasi zi de tranzactionare).

- **11-06 21:15-23:15** — pauza de rollover zilnic traversata (jump ~4500s, tipar deja documentat),
  urmata de reluare ordinara pe volum jos, fara mecanism nou.

- **11-06 23:15 -> 11-07 12:00** — grind ordinar prelungit Asia/Londra dimineata (~12h45m), chop
  intre ~3980-4014, volum jos-moderat aproape peste tot (0.8k-8k), o singura lumanare cu volum usor
  ridicat (8033) rezolvata prin continuare ordinara, un artefact cunoscut O=H=L=C/volum fractionar
  (re-verificat, rezolvat normal). Fara mecanism nou pe tot intervalul.

- **11-07 12:00-14:30** — grind ordinar Londra/pre-NY, chop 3992-4014, volum jos-moderat (2.6k-11k),
  fara mecanism nou. La 14:30 UTC a inceput episodul documentat ca Addendum A la DC-0021.

- **11-07 16:15-16:45** — puseu la maxim proaspat (4027.595, volum 14,453) urmat de esec/reversal
  in aceeasi zona si declin pe cateva lumanari (~5) pana la stabilizare, volum moderat (7.9k-11.4k,
  sub nivelul de record). Seamana cu mecanismul deja documentat DC-0018 (esec pe volum ridicat la
  maxim proaspat -> declin sustinut), la un nivel de volum mai mic decat recordul — nu a necesitat
  coborare pe M5/M1, tratat ca instanta ordinara/confirmatorie, fara DC/Registry nou.

- **11-07 16:45-22:00** — grind ordinar NY-dupa-amiaza/inchidere, chop 3994-4009, volum
  jos-moderat (0.4k-11.2k, un artefact O=H=L=C/volum fractionar re-verificat normal), subtiere
  treptata spre inchiderea de vineri. Fara mecanism nou.

- **11-07 ~22:00 -> 11-09 ~23:15** — gap de weekend (a 13-a-14-a instanta aproximativa, nenumarata
  exact) de amploare mica si ordinara (+4.4pt, close vineri 4001.275 -> open redeschidere 4005.675),
  volum redus tipic (2.3k-2.9k), fara esec de umplere sau extindere anormala — instanta complet
  ordinara, contrastand cu DC-0019 (recordul de amploare). Fara DC/Registry nou.

- **11-09 23:30 -> 11-10 01:00** — grind ordinar redeschidere Sunday/Asia, rally usor 4008->4020,
  volum jos (1k-5.5k). Fara mecanism nou.

- **11-10 01:00-02:45** — expansiune sustinuta early-Asia (~33.08pt, 4019.15->4053.47) pe 4 lumanari
  la volum ridicat (11.0k-13.4k), urmata de pauza/pullback pe volum in scadere (11.1k->6.4k->3.9k)
  si stabilizare. Seamana indeaproape cu mecanismul deja documentat DC-0016 (expansiune sustinuta
  early-Asia/pre-Londra) — instanta confirmatorie fara amploare-record sau stil de rezolutie nou,
  fara coborare pe M5/M1, fara DC/Registry nou.

- **11-10 02:45-07:45** — grind ordinar continuat, rally lent si sustinut 4044->4079 pe volum
  jos-moderat aproape peste tot (0.3k-7.0k), un artefact O=H=L=C/volum fractionar re-verificat
  normal. Fara mecanism nou.

- **11-10 07:45-13:00** — grind ordinar Londra/pre-NY prelungit, rally lent si sustinut 4075->4098,
  volum jos-moderat aproape peste tot (2.2k-9k). Fara mecanism nou.

- **11-10 13:00-14:45** — rally la maxim proaspat (4106), apoi declin sustinut in doua faze pe volum
  ridicat (faza 1: 11.3k-12.7k pe 3 lumanari, pauza, faza 2: puseu la 21,470 — aproape dublu fata
  de faza 1 — verificat organic pe M5, 40.9% concentrare maxima, sub pragul 42.7%), minim nou
  (4074.49), apoi recuperare pe volum in scadere graduala (14.6k->10.6k). Fiecare element in parte
  are precedent (DC-0018 esec-la-maxim-proaspat, DC-0013 declin sustinut, DC-0020 bidirectional cu
  puseu de volum) — nu justifica DC nou, notat in Observation Registry (intrarea #10) ca punct de
  comparatie pentru intrebarea daca a doua faza a unui declin in doi timpi tinde sa aiba volum mai
  mare decat prima.

- **11-10 15:30-21:00** — normalizare si grind ordinar NY-dupa-amiaza, rally lent 4084->4115, volum
  in general moderat cu decadere graduala (12.6k->1.1k spre final), fara mecanism nou.

- **11-10 21:00-21:30** — puseu de absorbtie (volum 11.3k-12.6k, deplasare minima ~7pt pe 3
  lumanari) urmat de o prabusire de volum la niveluri foarte subtiri (1137->574->547) inaintea
  pauzei de rollover — a doua instanta aproape identica cu Registry #9 (absorbtie -> prabusire de
  volum -> fereastra pre-rollover). Confirmatorie, fara artefact nou creat (aceeasi combinatie deja
  documentata).

- **11-10 21:30-23:15** — pauza de rollover zilnic traversata (jump ~4500s, tipar deja documentat),
  reluare ordinara. Fara mecanism nou.

- **11-10 23:15 -> 11-11 06:00** — grind ordinar prelungit Asia (~6h45m), rally lent 4120->4148 apoi
  usoara retragere 4148->4130, volum jos-moderat aproape peste tot (1.4k-7.1k). Fara mecanism nou.

- **11-11 06:00-12:45** — grind ordinar prelungit Londra dimineata (~6h45m), chop ingust 4125-4147,
  volum jos-moderat aproape peste tot (1.6k-7.0k). Fara mecanism nou.

- **11-11 12:45-14:30** — grind ordinar continuat, chop 4130-4147, volum jos-moderat (3.4k-7.5k).
  Fara mecanism nou.

- **11-11 14:30-16:15** — declin sustinut in doua faze (~49.6pt, 4146.885->4097.245 pe ~10 lumanari,
  ~1h45m): faza 1 cu volum in crestere graduala (3.4k->16.4k), apoi faza 2 cu un puseu ascutit la
  20,759 (aproape dublu fata de nivelul mediu al fazei 1) la minimul cel mai adanc, urmata de
  recuperare/stabilizare pe volum in scadere (16.3k->10.5k->7.0k). A doua instanta a tiparului deja
  notat in Observation Registry #10 (declin in doi timpi cu a doua faza avand volum semnificativ mai
  mare) — confirmatorie, fara coborare pe M5/M1, fara artefact nou creat.

- **11-11 16:15-21:45** — grind ordinar prelungit NY-dupa-amiaza/Asia (~5h30m), chop ingust
  4105-4133, volum jos aproape peste tot (0.5k-6.8k), subtiere treptata spre inchidere. Fara
  mecanism nou.

- **11-11 21:45-23:15** — pauza de rollover zilnic traversata (jump ~4500s, tipar deja documentat),
  reluare ordinara. Fara mecanism nou.

- **11-11 23:15 -> 11-12 05:15** — redeschidere Sunday/Asia ordinara (~6h), rally usor 4133->4145
  urmat de un declin sustinut moderat (~38pt, 4145->4103.635) pe volum moderat cu decadere graduala
  (13.9k->4.7k), stabilizare finala ~4107-4112. Fara escaladare in a doua faza (spre deosebire de
  Registry #10/#11) — instanta simpla, ordinara a familiei deja documentate DC-0013/DC-0021. Fara
  DC/Registry nou.

- **11-12 05:15-11:45** — grind ordinar prelungit Londra dimineata (~6h30m), rally lent si continuu
  4104->4131, volum jos-moderat aproape peste tot (2.0k-9.4k). Fara mecanism nou.

- **11-12 11:45-14:30** — grind ordinar continuat, chop 4120-4136, volum jos-moderat (2.0k-14.8k,
  un puseu izolat la 14803 rezolvat prin continuare ordinara). Fara mecanism nou. La 14:30 UTC a
  inceput episodul documentat ca DC-0022 (vezi mai jos).

- **11-12 20:00-22:45** — coada/normalizare dupa DC-0022, volum in scadere treptata (14.6k->1.7k),
  chop ingust 4191-4202, fara mecanism nou (rezolutie deja documentata: absorbtie/stabilizare
  post-expansiune, cf. DC-0012/DC-0021).

- **11-12 22:45-23:15** — pauza de rollover zilnic traversata (jump ~4500s, tipar deja documentat),
  reluare ordinara. Fara mecanism nou.

- **11-12 23:15 -> 11-13 07:00** — redeschidere Sunday/Asia ordinara urmata de grind Londra
  dimineata (~7h45m), rally usor 4188->4220 cu un declin sustinut moderat intermediar (~30pt,
  4209->4179.7, volum 7-13k, rezolutie prin recuperare — instanta ordinara a familiei deja
  documentate, fara escaladare in a doua faza), apoi continuare pana la noi maxime locale usoare
  (4219.5) pe volum moderat. Fara mecanism nou.

- **11-13 07:00-12:30** — grind ordinar prelungit Londra dimineata (~5h30m), rally moderat
  4210->4240 cu doua declinuri minore intermediare (~15-27pt, volum 8-11.7k, ambele rezolvate prin
  recuperare ordinara, fara escaladare), volum jos-moderat in rest (2.9k-6.3k). Fara mecanism nou.

- **11-13 21:30-22:15** — normalizare finala dupa DC-0023, volum jos (1.8k-2.6k). Fara mecanism nou.

- **11-13 22:15-22:45** — pauza de rollover zilnic traversata (jump ~4500s, tipar deja documentat),
  reluare ordinara pe volum jos. Fara mecanism nou.

- **11-13 22:45 -> 11-14 04:15** — redeschidere Sunday/Asia ordinara urmata de grind Londra
  dimineata (~5h30m), rally moderat 4179->4211 cu un declin/recuperare intermediar (~15pt, volum
  8-12.6k, instanta ordinara, fara escaladare), volum jos-moderat in rest (2.9k-8.9k). Fara mecanism
  nou.

- **11-14 04:15-10:00** — grind ordinar prelungit Londra dimineata (~5h45m), declin lent si
  sustinut 4200->4166 pe volum jos-moderat aproape peste tot (4.3k-12k), fara escaladare sau
  rezolutie record. Fara mecanism nou.

- **11-14 10:00-11:45** — grind ordinar continuat, chop 4150-4170, volum jos-moderat (6.0k-8.5k).
  Fara mecanism nou. La 11:45 UTC a inceput episodul documentat ca DC-0024 (vezi mai jos).

- **11-14 17:00-20:45** — grind ordinar continuat NY-dupa-amiaza/seara (~3h45m), chop 4075-4110,
  volum jos-moderat aproape peste tot (3.6k-9.6k). Fara mecanism nou. (CEO REVIEW ALPHA #1 primit si
  raspuns in aceasta fereastra — Red Team audit complet autorizat sa ruleze independent; bucla
  reluata per autorizare CEO explicita, fara reanaliza perioadelor deja inchise, fara modificare de
  artefacte/checkpoint-uri inghetate/metodologie.)

- **11-14 20:45-21:45** — grind ordinar final de vineri, volum jos (1.7k-2.5k). Fara mecanism nou.

- **11-14 21:45 -> 11-16 23:00** — gap de weekend ordinar de amploare mica (-7.55pt, close vineri
  4085.825 -> open redeschidere 4078.275), volum tipic (4.6k), fara esec de umplere sau extindere
  anormala — instanta complet ordinara. Fara DC/Registry nou.

- **11-16 23:00 -> 11-17 03:00** — redeschidere Sunday/Asia ordinara (~4h), rally moderat sustinut
  4078->4098 (~15pt) pe volum ridicat (10-13k) urmat de pullback (~13pt) pe volum in scadere
  (5.7k-7.9k) — instanta ordinara a familiei deja documentate (DC-0013/DC-0021), fara escaladare.
  Fara mecanism nou.

- **11-17 03:00-07:00** — grind ordinar prelungit Asia/Londra dimineata (~4h), declin lent-moderat
  4083->4049.76 (~33pt total, cu un declin intermediar de ~23pt pe volum 7.5k-9.1k, rezolvat prin
  stabilizare ordinara), volum jos-moderat in rest (2.4k-7.7k). Fara mecanism nou.

- **11-17 07:00-10:45** — grind ordinar continuat Londra dimineata (~3h45m), chop ingust 4066-4096,
  volum jos-moderat aproape peste tot (3.4k-6.3k). Fara mecanism nou.

- **11-17 10:45-15:15** — grind ordinar continuat, chop 4060-4092, volum jos-moderat (1.9k-7.6k).
  Fara mecanism nou.

- **11-17 15:15-17:00** — episod choppy moderat (~11 lumanari, ~29.6pt, 4082->4052.38) pe volum
  sustinut (8k-15.5k), fara escaladare peste pragurile deja documentate (DC-0012/DC-0017 Addendum A)
  — instanta ordinara/confirmatorie, rezolvata prin stabilizare pe volum in scadere (7.9k). Fara
  DC/Registry nou.

- **11-17 17:00-19:30** — grind ordinar continuat NY-dupa-amiaza, chop 4056-4081, volum jos-moderat
  (6.1k-10.9k). Fara mecanism nou.

- **11-17 19:30-21:30** — declin sustinut moderat (~51.7pt, 4058.77->4007.055 pe 3 lumanari, volum
  ridicat 17.3k-18.6k) urmat de recuperare (~38pt) pe volum in scadere graduala (9.3k->1.9k) —
  instanta ordinara/confirmatorie a familiei deja documentate (DC-0013/DC-0018/DC-0021), fara
  coborare pe M5/M1, fara escaladare peste pragurile record deja stabilite. Fara DC/Registry nou.

- **11-17 21:30-22:15** — normalizare finala, volum jos (1.6k-1.9k). Fara mecanism nou.

- **11-17 22:15-22:45** — pauza de rollover zilnic traversata (jump ~4500s, tipar deja documentat),
  reluare ordinara. Fara mecanism nou.

- **11-17 22:45 -> 11-18 04:15** — grind ordinar prelungit Asia/Londra dimineata (~5h30m), declin
  lent-moderat sustinut 4054->4009.725 (~44pt total, cu doua faze de volum usor ridicat 6-10.3k,
  rezolvate prin stabilizare ordinara, fara escaladare), volum jos-moderat in rest (2.7k-6.9k). Fara
  mecanism nou.

- **11-18 04:15-08:00** — grind ordinar prelungit Londra dimineata (~3h45m), chop ingust 4002-4025,
  volum jos-moderat aproape peste tot (3.5k-9.99k). Fara mecanism nou.

- **11-18 08:00-12:30** — grind ordinar continuat Londra dimineata (~4h30m), rally moderat
  4013->4050.5 apoi retragere usoara, volum jos-moderat aproape peste tot (2.9k-9.99k). Fara
  mecanism nou.

- **11-18 12:30-16:45** — episod multi-leg NY-dimineata (~4h, ~16 lumanari): rally sustinut
  (~4032->4081.9, volum 8.6k-18.8k) urmat de declin (~4081.9->4040.5, volum 11.5k-19.3k) apoi
  recuperare partiala (4040.5->4067), volum in scadere finala (5.8k). Aplicat testul in 3 pasi
  (directiva CEO): (1) mecanism nou? NU — aceeasi forma multi-leg/bidirectional deja documentata
  (DC-0012/DC-0017 Addendum A/DC-0020/DC-0023); (2) doar addendum? posibil, dar (3) nici macar nu
  atinge pragul de record (durata ~4h vs. 8h DC-0023, amploare ~50pt vs. 100-125pt DC-0023/DC-0024)
  — instanta pur confirmatorie, sub toate pragurile existente. Fara coborare pe M5/M1 (nu s-a
  justificat). Fara DC/Addendum/Registry nou, conform directivei CEO de prag ridicat.

- **11-18 16:45-20:30** — grind ordinar prelungit NY-dupa-amiaza (~3h45m), chop ingust 4059-4082,
  volum jos-moderat aproape peste tot (3.3k-11.3k). Fara mecanism nou.

- **11-18 20:30-22:45** — normalizare finala/subtiere pre-rollover, volum foarte jos (0.6k-1.7k).
  Fara mecanism nou.

- **11-18 22:45-23:15** — pauza de rollover zilnic traversata (jump ~4500s, tipar deja documentat),
  reluare ordinara. Fara mecanism nou.

- **11-18 23:15 -> 11-19 03:15** — redeschidere Sunday/Asia ordinara (~4h), chop ingust 4055-4081,
  volum jos-moderat aproape peste tot (1.7k-12.1k, un puseu izolat rezolvat prin continuare
  ordinara). Fara mecanism nou.

- **11-19 03:15-07:00** — grind ordinar prelungit Asia/Londra dimineata (~3h45m), rally lent
  4067->4098.7, volum jos-moderat aproape peste tot (1.9k-8.8k). Fara mecanism nou.

- **11-19 07:00-11:00** — grind ordinar Londra dimineata (~4h), chop urmat de rally moderat
  4088->4119.2 (~30pt, volum 10.6k-7k, instanta ordinara, fara escaladare), volum jos-moderat in
  rest (2.6k-6.7k). Fara mecanism nou.

- **11-19 11:00-14:15** — grind ordinar continuat, chop 4101-4120, un declin intermediar de ~14pt
  pe volum 8.6k-10.5k (rezolvat prin recuperare ordinara), volum jos-moderat in rest (3.9k-5.5k).
  Fara mecanism nou.

- **11-19 14:15-19:00** — episod choppy NY-dupa-amiaza (~4h45m, 20 lumanari): rally sustinut
  (4106->4132.985, volum 10k-19.5k) apoi declin prelungit (4132.985->4055.475, ~77.5pt, volum
  16k-19k) apoi recuperare partiala (4055.475->4087.5), volum in scadere finala (8k). Test in 3 pasi
  (directiva CEO), explicit: (1) mecanism nou? NU — forma rally-varf-declin-recuperare la volum
  sustinut e identica cu DC-0020/DC-0023; (2) addendum? nici macar atat — magnitudinea (77.5pt) si
  durata (~4h45m) sunt SUB pragurile deja stabilite de acele DC-uri (DC-0023: 100pt/8h) si volumul de
  varf (19,542) e sub jumatate fata de recordul DC-0020 (37,204); (3) record? nu, sub toate pragurile
  existente pe toate cele trei axe (durata/amploare/volum). Concluzie: nici DC, nici Addendum — pur
  confirmatorie. Nu s-a coborat pe M5/M1.

- **11-19 19:00-22:30** — coada/normalizare dupa episodul choppy anterior, volum in scadere
  treptata (12.7k->1.3k), chop ingust 4065-4085. Fara mecanism nou.

- **11-19 22:30-23:15** — pauza de rollover zilnic traversata (jump ~4500s, tipar deja documentat),
  reluare ordinara. Fara mecanism nou.

- **11-19 23:15 -> 11-20 01:45** — redeschidere Sunday/Asia ordinara (~2h30m), rally moderat
  4088->4110 apoi retragere usoara, volum jos-moderat (2.6k-8.7k). Fara mecanism nou.

- **11-20 01:45-03:15** — declin sustinut moderat (~59.7pt, 4098.565->4038.9 pe 3 lumanari, volum
  6.5k-14.2k) urmat de recuperare (~47pt) pe volum moderat (6.3k-9.9k) — instanta
  ordinara/confirmatorie a familiei deja documentate (DC-0013/DC-0018/DC-0021), sub toate pragurile
  existente pe durata/amploare/volum. Fara coborare pe M5/M1, fara DC/Addendum nou.

- **11-20 03:15-06:15** — grind ordinar prelungit Asia dimineata (~3h), chop ingust 4064-4080,
  volum jos-moderat aproape peste tot (2.8k-6.9k). Fara mecanism nou.

- **11-20 06:15-09:30** — grind ordinar continuat Londra dimineata (~3h15m), declin lent-moderat
  4076->4038.93 (~37pt) urmat de recuperare partiala, volum jos-moderat aproape peste tot
  (2.9k-8.3k). Fara mecanism nou.

- **11-20 09:30-13:30** — grind ordinar continuat (~4h), chop ingust-moderat 4055-4098, volum
  jos-moderat aproape peste tot (6.3k-9.4k), o singura lumanare izolata la 17,198 (13:00-13:15,
  fara continuare la volum comparabil imediat dupa). Fara mecanism nou.

- **11-20 13:30-18:00** — episod de volum sustinut ridicat pe **18 lumanari continue (~4h30m,
  13:30-18:00 UTC), volum ramas in banda 14k-26.4k aproape tot timpul, fara decadere pana spre
  finalul ferestrei**, miscare choppy/bidirectionala (minim 4043.58, maxim 4107.35, ~63.8pt range
  total), varf de volum 26,443 (13:45 UTC candle). Test in 3 pasi (directiva CEO), explicit:
  (1) mecanism nou? NU — sustinere de volum ridicat pe episod choppy multi-leg e exact tiparul deja
  documentat in DC-0023 (8h/32 lumanari) si DC-0012 (absorbtie fara deplasare neta); (2) addendum?
  nici macar atat — durata (4h30m), volumul de varf (26,443) si amploarea totala (~63.8pt) sunt toate
  sub pragurile deja stabilite de DC-0023 (8h/100.005pt/28,254) si sub recordurile DC-0020/DC-0018
  (37,204/36,798); nu aduce niciun unghi evidential nou, doar o instanta mai mica a aceluiasi
  fenomen; (3) record? nu, sub toate pragurile existente pe toate cele trei axe (durata/amploare/
  volum). Concluzie: nici DC, nici Addendum — pur confirmatorie. Fara coborare pe M5/M1 (filtrul v2
  a raspuns NU/nesigur repetat, rezolvat prin urmarire suplimentara pe M15, fara sa ceara M5).

- **11-20 18:00-20:15** — decadere treptata a volumului catre normal (26k->25k->21k->14-18k->11.7k),
  grind ordinar usor ascendent 4049->4084->4077, fara mecanism nou.

- **11-20 20:15-22:00** — grind ordinar linistit pe M15 (volum 4.4k-16.2k, chop ingust), fara
  mecanism nou.

## PROTOCOL DE OBSERVATIE v3 ADOPTAT (2026-07-24, in timpul acestei sesiuni)
La 2026-07-24, CEO a standardizat modul de observare (vezi sectiunea METODOLOGIE de mai jos in
fisier pentru textul complet al directivei): timeframe principal de start **1H**, **autoplay
ACTIVAT la 0.5x (2000ms/bara)**, pauza + coborare pe 5M (apoi 3M doar daca 5M insuficient) DOAR
la un fenomen ce merita investigat, 3M niciodata punct de plecare. Comutat chart la 60 (1H) si
autoplay pornit imediat dupa directiva; toata cercetarea de mai jos (de la 22:00 UTC 11-20 incolo)
ruleaza sub acest protocol nou.

**Lectie metodologica de executie (prima aplicare a protocolului v3)**: la identificarea
fenomenului de la 18:00-19:00 UTC 11-24 (vezi mai jos), am facut o eroare de secventiere — inainte
de a opri efectiv autoplay-ul, am mai facut o interogare OHLCV suplimentara pe 1H pentru context,
timp in care autoplay-ul a continuat sa ruleze (~2000ms/bara) si a avansat pozitia replay-ului cu
inca ~18h (de la current_date 1764007200 la 1764071999) inainte ca toggle-ul de oprire sa aiba
efect. NU e un incident metodologic major (datele istorice raman disponibile integral, investigatia
5M a putut fi facuta corect printr-o interogare OHLCV mai mare, count=240, care a acoperit fereastra
tinta), dar e o corectie de proces retinuta: **pasul 1 (Pauza) trebuie executat IMEDIAT la
identificarea fenomenului, inaintea oricarei interogari suplimentare de context** — nu dupa.
De asemenea, notez: **volumele pe 1H nu sunt direct comparabile cu pragurile calibrate pe M15**
(un candel de 1H agrega ~4 candele M15, deci volumele "normale"/"ridicate" pe 1H sunt mult mai mari
in termeni absoluti) — comparatiile de volum intre DC-urile M15 existente si observatii noi pe 1H
trebuie facute cu prudenta explicita, nu direct.

- **11-20 22:00 UTC -> 11-21 07:00 UTC** (1H, autoplay) — declin sustinut ~8h (4079->~4025 low),
  volum ramas ridicat pe scara 1H (10.9k-37.5k) aproape tot timpul; instanta ordinara/confirmatorie
  a familiei deja documentate (DC-0013/DC-0018/DC-0021), doar vazuta acum la rezolutie 1H pentru
  prima data. Fara DC/Addendum nou.
- **11-21 07:00-21:00 UTC** (Friday, 1H) — continuare choppy/volatila (grind intre ~4030-4140),
  volume orare mari (pana la 89,724) dar in linie cu asteptarile pentru agregare 1H pe sesiune
  NY-dupa-amiaza de vineri; nimic iese in evidenta ca mecanism nou.
- **Weekend gap** (Fri ~21:00 UTC 11-21 -> Sun ~23:00 UTC 11-23) traversat automat de autoplay
  (comportament deja documentat, identic cu `replay_step`), fara incident.
- **11-23 23:00 UTC -> 11-24 18:00 UTC** — redeschidere Sunday/Asia + Londra/NY-dimineata luni,
  grind ordinar choppy 4040-4075 apoi expansiune ascendenta graduala inceputa ~11:00 UTC catre
  ~4133; volum moderat (1H), fara mecanism nou pana la ora de mai jos.
- **11-24 18:00-19:00 UTC** — accelerare in cadrul trend-ului ascendent deja activ: candela 1H
  range 37.945pt (4088.085->4126.03), volum 42,154. Filtru aplicat: (1) diferit de variatia din
  jur (grind 5-15pt/ora)? da, vizibil; (2) seamana cu ceva documentat? partial (familia "impuls
  care isi tine castigul", DC-0011/DC-0017), dar prima observatie la rezolutie 1H; (3) motiv real
  de informatie noua? da — merita verificat organic pe 5M. Coborare pe 5M: 12 sub-candele,
  volum maxim per-candela 5,605 (din 42,154 total) = **13.3% concentrare maxima, mult sub pragul
  42.7%** — constructie organica clara, distribuita pe toata ora, cu doua puseuri de acceerare
  (in jur de minutul 15 si minutul 60 al orei). Test in 3 pasi (directiva CEO): (1) mecanism nou?
  NU — simpla intensificare temporara a unui trend deja in desfasurare, fara sweep/absorptie/
  reversal; (2) addendum? nu, nu se leaga clar printr-un mecanism nou de niciun DC existent —
  cel mult confirma ca acceerarile in trend se construiesc organic si la rezolutie 1H; (3) record?
  nu, volumul (42,154 pe 1H) e sub alte ore din aceeasi zi de vineri (89,724/77,215/59,739; desi
  comparatie 1H-vs-1H, nu record). Concluzie: **fara DC, fara Addendum** — pur confirmatorie,
  validare a mecanicii protocolului v3 (1H->5M functioneaza corect, datele raman organice la
  rezolutie fina).

## PROTOCOL DE OBSERVATIE — REVENIRE LA M15 MANUAL (directiva CEO, 2026-07-24, INLOCUIESTE v3)
CEO a decis revenirea la stepping manual pe M15 (autoplay OPRIT, chart mutat inapoi pe timeframe
15) — Protocolul v3 (1H + autoplay 0.5x) e ABANDONAT. Schimbari fata de metodologia originala
(2026-07-22): batch-uri de verificare MULT MAI MARI — 30-40 candele M15 per `replay_step` inainte
de fiecare verificare `data_get_ohlcv` (fata de 3-4 candele/verificare folosite anterior), pentru
acoperire mai rapida a perioadei. Cand un fenomen merita investigat: coboara pe **5M, apoi 1M**
(NU 3M — revenire la calea originala 5M->1M din metodologia 2026-07-22, nu 5M->3M din v3
abandonat). Ramane NESCHIMBAT: filtrul v2 (3 intrebari), regula celor doua rezultate, testul in
3 pasi pentru orice DC nou, pragul ridicat CEO pentru DC-uri.

Intre autoplay-ul v3 (oprit la current_date 1764071999, ~2025-11-25 12:00 UTC) si momentul acestei
directive, autoplay-ul a continuat sa ruleze nesupravegheat (asteptare intre wakeup-uri) pana la
current_date 1764230399. Fereastra **2025-11-25 ~06:30 UTC -> 2025-11-27 ~07:45 UTC (~49h)** a fost
revizuita retroactiv pe M15 (190 candele, `data_get_ohlcv count=240` dupa comutarea chart-ului
inapoi pe 15) inainte de a relua stepping manual, pentru a nu sari peste perioada nesupravegheata:
grind/chop ordinar intr-un interval larg ~4110-4172, cateva declinuri/rally-uri moderate (~30-40pt
fiecare) cu volum in benzile deja stabilite (2k-21k, niciun candel M15 aproape de pragurile
existente), doua traversari normale ale pauzei de rollover zilnic. Nimic nu a trecut filtrul v2.
Fara DC/Addendum nou, fara intrare noua in Observation Registry.

- **11-27 08:00-17:15 UTC** — grind ordinar strans in interval ~4148-4167, volum jos-moderat (2k-9k),
  compatibil cu lichiditate redusa de Thanksgiving SUA (2025-11-27). Fara mecanism nou.
- **11-27 17:15-19:30 UTC** — continuare grind ordinar, tranzitie spre lull-ul de mai jos.
- **11-27 19:30-21:45 UTC** — lull aproape complet (volum M15 sub 150 aproape peste tot), pauza de
  rollover traversata normal, apoi recuperare partiala a volumului (533-2,177) 23:00-00:15 UTC
  pe 11-28, tot sub baseline normal.
- **11-28 00:30 UTC** — spargere: vezi Addendum B la DC-0010 (documentat mai sus in Stare
  portofoliu) — puseu de viteza M1 (11.0pt/60s) urmat de whipsaw si revenire sustinuta care isi
  tine castigul pana la ~02:15 UTC (4180->~4193, fara reversal).

- **11-28 02:15-08:00 UTC** — grind ordinar, choppy 4155-4192, volum jos-moderat (0.5k-5.6k). Fara
  mecanism nou.
- **11-28 08:15-11:15 UTC** — vezi intrarea 11 din Observation Registry: semnatura de artefact de
  date (Black Friday, tape rar/gaps neregulate pe M1), NU fenomen de piata. Nici DC, nici Addendum.
- **11-28 11:15 UTC (dupa artefact) -> punctul curent** — tape normalizat, volum revenit in banda
  ordinara (20-2,000 pe M1 / cateva sute-cateva mii pe M15), grind fara mecanism nou.

- **11-28 10:45-19:45 UTC** — expansiune sustinuta NY (post-artefact), 4163->~4221 (~58pt/9h),
  volum ridicat in prima jumatate (9k-17k) apoi moderat; instanta ordinara a familiei deja
  documentate (DC-0013/DC-0022), sub toate pragurile. Fara mecanism nou.
- **Weekend gap** (Fri ~20:00 UTC 11-28 -> Sun ~23:15 UTC 11-30, ~51h) traversat automat, fara
  incident. Gap de 10.49pt (nesemnificativ fata de recordul DC-0019 de ~28.4pt), retestat aproape
  complet chiar in lumanarea de redeschidere.
- **11-30 23:15 UTC -> 12-01 08:45 UTC** — continuare expansiune sustinuta, 4217->~4245-4255 cu
  un varf local si retragere partiala (4255.56 -> 4234 -> recuperare la 4242-4250), volum 8k-17k;
  aceeasi familie deja documentata, sub toate pragurile. Fara mecanism nou.

- **12-01 08:45-14:30 UTC** — continuare grind/expansiune sustinuta 4242->~4262 varf local, volum
  moderat (8k-15k). Fara mecanism nou.
- **12-01 14:30-17:15 UTC** — puseu de declin pe o singura lumanare (28.2pt, vol 23,502) urmat de
  episod choppy multi-leg ~2h45m (volum 12k-20k, decadere treptata), stabilizare ~4230-4239.
  Instanta ordinara a familiei DC-0020/DC-0023, sub toate pragurile. Fara DC/Addendum.
- **12-01 17:15-22:00 UTC** — grind ordinar continuat, volum jos-moderat (1.6k-15.5k), pauza de
  rollover traversata normal.
- **12-02 00:00-01:00 UTC** — grind linistit Asia (volum 0.8k-7.6k). Fara mecanism nou.
- **12-02 01:00 UTC** — puseu de declin pe o singura lumanare (34.4pt, vol 17,212) dupa baseline
  linistit, urmat de recuperare ~29pt pe volum moderat descrescator (11k->4.4k). Instanta ordinara
  a familiei sweep-apoi-recuperare (DC-0018/19/20/21/24), sub toate pragurile. Fara DC/Addendum.

- **12-02 03:30-13:45 UTC** — drift lent descendent la volum jos (4221->~4181, ~40pt/9h), caracter
  ordinar de sesiune Asia/Londra-dimineata fara confirmare de volum. Fara mecanism nou.
- **12-02 13:45-15:45 UTC** — rally moderat (4204->4230.7, volum 10-13.5k) urmat de declin sustinut
  pe 6 lumanari (~1h30m, 66.9pt, volum ridicat si consistent 17-21k, fara decadere pana la minim).
  Instanta ordinara a familiei DC-0013/18/21, sub toate pragurile (durata/amploare/volum). Fara
  DC/Addendum.
- **12-02 15:45-21:15 UTC** — recuperare treptata si stabilizare 4164->~4210 pe volum
  moderat-descrescator (3k-11k). Fara mecanism nou.

- **12-02 21:15 UTC -> 12-03 14:15 UTC** — grind ordinar linistit Asia/Londra (4195-4227), pauza de
  rollover traversata normal, apoi rally moderat spre final (4211->4241 varf local, volum 10-17k)
  urmat de retragere partiala (4226.76). Fara mecanism nou pe tot parcursul.

- **12-03 14:15-18:15 UTC** — episod choppy la volum ridicat (varf 24,022), doua lumanari de declin
  brusc (~22pt si ~25pt), amploare totala ~45.7pt/~3h45m. Instanta ordinara a familiei DC-0020/
  DC-0023, sub toate pragurile (durata/amploare/volum). Fara DC/Addendum.
- **12-03 18:15-21:30 UTC** — stabilizare/grind ordinar 4195-4215, volum moderat-descrescator
  (2.2k-12k). Fara mecanism nou.

- **12-03 21:30 UTC -> 12-04 07:00 UTC** — pauza de rollover traversata normal, apoi grind ordinar
  linistit Asia (4181-4217), volum jos-moderat (0.7k-15.4k) aproape peste tot. Fara mecanism nou.

- **12-04 07:00-13:30 UTC** — grind ordinar linistit Londra-dimineata (4183-4207), volum
  jos-moderat (2.9k-13.6k) aproape peste tot. Fara mecanism nou.

- **12-04 13:30-19:45 UTC** — grind ordinar NY-dimineata (4187-4220), un scurt puseu de volum
  pe 2 lumanari (23.9k/25.4k, sub recordurile existente) fara amploare exceptionala, apoi
  continuare choppy ordinara pe volum jos-moderat (2.7k-16.6k). Fara mecanism nou.

- **12-04 19:45 UTC -> 12-05 03:00 UTC** — grind ordinar linistit NY-seara/Asia (4194-4210), pauza
  de rollover traversata normal, volum jos-moderat (0.5k-10.3k) aproape peste tot. Fara mecanism nou.

- **12-05 03:00-09:15 UTC** — grind ordinar linistit Asia (4203->4230 varf usor->4218), volum
  jos-moderat (3.1k-9.4k) aproape peste tot. Fara mecanism nou.

- **12-05 09:15-15:30 UTC** — grind ordinar/rally gradual (4215->4259.34 varf), volum jos-moderat
  (0.8k-18.9k). Fara mecanism nou.
- **12-05 16:00 UTC** — dupa varful de 4259.34, declin pe ~5 lumanari (~1h15m, 56.04pt total),
  cu majoritatea amplorii concentrata intr-o SINGURA lumanare M15 (16:00-16:15, range 40.34pt,
  vol 22,570). Coborare pe 5M: sub-candela de varf (16:10-16:15) are 10,938/22,570 = 48.5%
  concentrare — peste pragul 42.7%. Coborare pe 1M pentru acea fereastra de 5 minute: volumul se
  distribuie pe toate cele 5 minute (2643/2499/1969/1972/1855, max 24.2%) — constructie organica
  clara, NU artefact. Test in 3 pasi: (1) mecanism nou? NU — forma "rally la maxim proaspat urmat
  de declin" e deja DC-0018; (2) addendum? nici macar atat — DC-0024 are deja o lumanare unica cu
  range aproape identic (40.22pt), deci nu aduce un unghi nou fata de niciun DC existent; (3)
  record? NU pe nicio axa (volum 22,570 < 24,655; amploare 56pt < 100pt+; range/lumanare 40.34pt
  ≈ egal cu DC-0024, nu il depaseste). Concluzie: fara DC, fara Addendum — pur confirmatorie,
  coincide simultan cu doua DC-uri deja documentate fara sa adauge un unghi nou la niciunul.
- **12-05 16:15-18:00 UTC** — stabilizare/recuperare partiala (4203->4218), volum
  moderat-descrescator. Fara mecanism nou.

- **12-05 18:00-21:55 UTC** — declin gradual ordinar (4217->4198), volum jos-moderat (1.9k-12.4k).
  Fara mecanism nou.
- **Weekend gap** (Fri ~22:00 UTC 12-05 -> Sun ~23:15 UTC 12-07, ~49h15m) traversat automat, fara
  incident; gap nesemnificativ (~3.4pt).
- **12-07 23:15 UTC -> 12-08 01:15 UTC** — redeschidere Sunday/Asia ordinara, volum jos-moderat
  (0.6k-11.2k). Fara mecanism nou.

- **12-08 01:15-07:30 UTC** — grind ordinar linistit Asia (4197-4219), volum jos-moderat
  (3.3k-11.2k) aproape peste tot. Fara mecanism nou.

- **12-08 07:30-13:00 UTC** — grind ordinar linistit (4197-4217), volum jos-moderat (2.2k-9.4k).
  Fara mecanism nou.
- **12-08 13:00-14:45 UTC** — declin moderat pe volum ridicat (17.2pt, volum varf 18,202) urmat de
  recuperare partiala. Instanta ordinara, sub toate pragurile. Fara DC/Addendum.
- **12-08 15:00-15:45 UTC** — al doilea declin moderat pe volum ridicat (35.6pt, volum
  19.3k-21.7k pe 3-4 lumanari) urmat de recuperare partiala (4176->4193). Instanta ordinara a
  familiei DC-0013/18/21, sub toate pragurile. Fara DC/Addendum.

- **12-08 15:45-22:00 UTC** — continuare grind choppy ordinar NY-dupa-amiaza/seara (4176-4198),
  volum jos-moderat (0.9k-17.6k) fara escaladare sustinuta. Fara mecanism nou.

- **12-08 22:00 UTC -> 12-09 05:15 UTC** — pauza de rollover traversata normal, apoi grind ordinar
  linistit Asia (4183-4198), volum jos-moderat (0.7k-9.3k). Fara mecanism nou.

- **12-09 05:15-09:00 UTC** — declin gradual (4186->4174.9) urmat de recuperare choppy (4190),
  volum moderat (6.5k-13.3k). Fara mecanism nou.
- **12-09 09:00-11:30 UTC** — puseu de rally la deschiderea Londrei (11.7pt, vol 11,116) din
  baseline linistit, urmat de consolidare choppy 4202-4208. Instanta ordinara, sub toate
  pragurile. Fara DC/Addendum.

- **12-09 11:30-13:45 UTC** — grind ordinar linistit, volum jos-moderat. Fara mecanism nou.
- **12-09 13:45-17:30 UTC** — episod choppy la volum ridicat (~3h45m, varf 23,424, amploare
  totala 31.3pt: 4189.5-4220.785), fara direction clara, urmat de stabilizare. Instanta ordinara
  a familiei DC-0012/DC-0023, sub toate pragurile. Fara DC/Addendum.

- **12-09 16:45-23:59 UTC** — grind ordinar linistit NY-seara (4201-4222), pauza de rollover
  traversata normal, volum jos-moderat (0.9k-13.5k). Fara mecanism nou.

- **12-10 00:00-06:15 UTC** — grind ordinar linistit Asia (4201-4219), volum jos-moderat
  (1.5k-11.8k). Fara mecanism nou.

- **12-10 06:15-12:30 UTC** — declin gradual ordinar (4209->4195) urmat de stabilizare/grind
  (4187-4202), volum jos-moderat (2.9k-11.6k). Fara mecanism nou.

- **12-10 12:30-13:00 UTC** — grind ordinar linistit. Fara mecanism nou.
- **12-10 13:00-15:15 UTC** — episod choppy la volum ridicat (~2h15m, varf 20,639, amploare
  totala 18.1pt), urmat de stabilizare. Instanta ordinara a familiei DC-0012/DC-0023, sub toate
  pragurile. Fara DC/Addendum.

- **12-10 16:30-19:00 UTC** — grind ordinar linistit (4193-4205), volum jos-moderat. Fara
  mecanism nou.
- **12-10 19:00-20:30 UTC** — episod major: declin in doua faze pana la minim 4182.08, lumanara
  de volum maxim 34,319 (al 3-lea cel mai mare din tot replay-ul), verificata organic pe 5M (38.5%
  concentrare maxima). Vezi Addendum C la DC-0011 mai sus (Stare portofoliu) — aceeasi forma
  "sweep reclamat, extinde la maxime noi" ca DC-0011, la scara mult mai mare; revenire pana la
  maxim nou 4238.785 (~56.7pt round-trip de la minim).
- **12-10 20:30-20:45 UTC** — stabilizare dupa episod, volum descrescator. Fara mecanism nou.

- **12-10 20:45 UTC -> 12-11 04:00 UTC** — grind/mild rally (4221->4248) urmat de declin gradual
  (4248->4213-4217), pauza de rollover traversata normal, volum jos-moderat (1.5k-13.4k). Fara
  mecanism nou.

- **12-11 04:00-10:15 UTC** — grind ordinar linistit Asia (4204-4226), volum jos-moderat
  (2.1k-8.2k). Fara mecanism nou.

- **12-11 10:15-13:45 UTC** — grind ordinar linistit (4205-4226), volum jos-moderat. Fara
  mecanism nou.
- **12-11 13:45-16:30 UTC** — rally sustinut (4219->4261.585, ~42.5pt/2h45m), volum ridicat
  (7.8k-21k). Instanta ordinara a familiei DC-0013/15/22, sub toate pragurile. Fara DC/Addendum.

- **12-11 16:30-23:45 UTC** — continuare rally (4257->4285.89 varf), apoi stabilizare/pullback
  usor (4262-4283), pauza de rollover traversata normal, volum jos-moderat (0.7k-16.3k).
  Amploarea totala a rally-ului multi-ora (~4219->4285.89, ~67pt) ramane sub toate pragurile
  familiei DC-0013/15/22. Fara mecanism nou.

- **12-11 23:45 UTC -> 12-12 06:00 UTC** — grind ordinar linistit Asia (4264-4281), volum
  jos-moderat (1.7k-13.3k). Fara mecanism nou.

- **12-12 06:00-12:15 UTC** — grind/trend gradual ascendent (4278->4339.46, ~61pt/9h), cu mici
  retrageri care rup continuitatea stricta de lumanari consecutive (nu se califica drept o
  singura instanta a familiei DC-0013/15/22), volum ordinar 5.2k-12.8k (fara escaladare). Fara
  mecanism nou.

- **12-12 12:15-15:00 UTC** — continuare grind ascendent ordinar pana la 4353.555 varf, volum
  moderat. Fara mecanism nou.
- **12-12 15:15-17:00 UTC** — episod major: declin brusc de la 4353.555 pana la minim 4257.275
  (~96.28pt), 8 lumanari consecutive toate cu volum peste 17,000 (varf 35,082 — al 2-lea cel mai
  mare volum din tot replay-ul), verificat organic pe 5M pe cele 3 lumanari cele mai mari
  (36.8%/37.2%/34.2% concentrare, toate sub 42.7%). Vezi Addendum A la DC-0023 mai sus (Stare
  portofoliu) — acelasi mecanism, forma mult mai comprimata/intensa.
- **12-12 17:00-17:30 UTC** — stabilizare/recuperare partiala (4257->~4290), volum descrescator.
  Fara mecanism nou.

- **12-12 17:30-21:45 UTC** — grind ordinar linistit (4288-4304), volum jos-moderat. Fara
  mecanism nou.
- **Weekend gap** (Fri ~21:45 UTC 12-12 -> Sun ~23:00 UTC 12-14, ~49h15m) traversat automat, fara
  incident; gap nesemnificativ (~3.6pt).
- **12-14 23:00 UTC -> 12-15 00:30 UTC** — redeschidere Sunday/Asia ordinara, volum jos (1.4k-2.6k).
  Fara mecanism nou.

- **12-15 00:30-06:45 UTC** — grind ordinar linistit Asia (4302->4346), volum jos-moderat
  (1.4k-12.6k). Fara mecanism nou.

- **12-15 06:45-13:00 UTC** — grind ordinar linistit Londra-dimineata (4335-4350), volum
  jos-moderat (2.6k-9.6k). Fara mecanism nou.

- **12-15 13:00-17:00 UTC** — declin gradual NY-dimineata (4347->4285.5, ~61.7pt/4h), volum
  ridicat (13k-24k, sub pragurile de volum recente din sesiune), urmat de stabilizare/recuperare
  (4293-4310). Instanta ordinara a familiei DC-0013/18/21, sub toate pragurile. Fara DC/Addendum.

- **12-15 18:45-23:30 UTC** — grind ordinar linistit NY-seara (4299-4318), pauza de rollover
  traversata normal, volum jos-moderat (0.8k-16.1k). Fara mecanism nou.

- **12-15 23:30 UTC -> 12-16 05:15 UTC** — grind ordinar linistit Asia (4280-4318), un declin
  moderat izolat (~29pt, vol varf 11,911) urmat de stabilizare rapida — sub toate pragurile. Fara
  mecanism nou.

- **12-16 05:15-11:30 UTC** — grind ordinar linistit (4271-4292), volum jos-moderat (2.9k-9.4k).
  Fara mecanism nou.

- **12-16 11:30-15:00 UTC** — rally sustinut (4276->4335.185, ~59pt/3h30m), volum moderat-ridicat
  (2.4k-22.2k). Instanta ordinara a familiei DC-0013/15/22, sub toate pragurile. Fara DC/Addendum.
- **12-16 15:00-17:45 UTC** — declin ordinar consecutiv (4335.185->4291.41, ~43.8pt), volum
  ridicat (8.2k-18k), urmat de stabilizare. Sub toate pragurile. Fara mecanism nou.

- **12-16 17:45 UTC -> 12-17 00:45 UTC** — grind ordinar linistit NY-seara/Asia (4296-4316),
  pauza de rollover traversata normal, volum jos (0.6k-9.9k). Fara mecanism nou.

- **12-17 00:45-07:00 UTC** — grind ordinar linistit Asia (4311-4342), volum jos-moderat
  (2.5k-11.8k). Fara mecanism nou.

- **12-17 07:00-13:15 UTC** — grind ordinar linistit Londra-dimineata (4306-4331), volum
  jos-moderat (2.1k-12.4k). Fara mecanism nou.
- **12-17 13:15 UTC - 12-18 07:30 UTC** — volum crescut moderat (18k-27k, NU record) la
  deschiderea NY cash (~14:30 UTC), comportament normal de sesiune; apoi grind linistit
  Asia/Londra-noapte (4324-4346), volum 1.2k-13.4k, un jump de rollover zilnic (~4500s) fara
  anomalii. Fara mecanism nou.
- **12-18 07:30-13:30 UTC** — grind linistit Londra-dimineata/pre-NY (4308-4343), volum
  jos-moderat (2.1k-12.4k). Fara mecanism nou.
- **12-18 13:30-15:55 UTC — INVESTIGATIE (5M)** — rally 4321->4343.185 (fresh high, 13:30-13:55),
  reversal brusc 14:30-14:50 la low de sesiune 4308.67 (-32.6pt, volum moderat-crescut 7.5k-11.6k
  per 5M, NU record — max candela M15-echiv 28,380 vs recordul 37,204), recuperare pana la
  4337-4341.77 dar STAGNEAZA sub vechiul high (nu extinde la new high, spre deosebire de DC-0011).
  Test 3-parti aplicat: nu e mecanism nou, NU calificat ca Addendum DC-0011 (rezolutia diverge —
  stagnare, nu extindere), nu e record. **Logat ca Observation Registry intrarea 12**
  (counter-instance / contrast fata de DC-0011). Fara DC/Addendum creat.
- **12-18 16:00-17:00 UTC — CONTINUARE/CORECTIE la intrarea 12** — stagnarea era temporara: la
  16:00 UTC pretul sparge decisiv si urca la un nou high de 4374.655 (16:15 UTC, +31.47pt peste
  vechiul high 4343.185), volum sustinut/distribuit pe 4 candele M15 (20.5k-21.6k, NU concentrat).
  Apoi reversal brusc 16:15-17:00 UTC inapoi la 4322.55 (volum 26,660 pe candela de coborare),
  la ~14pt de low-ul original (4308.67), apoi stabilizare 4322-4341 fara extindere ulterioara.
  Deci reclaim-ul A extins la new high pana la urma (confirmand mecanismul DC-0011, doar cu
  intarziere de ore nu minute), dar apoi a fost complet reversat. Range total zi ~66pt. Testul
  3-parti reaplicat: tot nu e record, tot e o combinatie a doua piese deja documentate (extindere
  DC-0011-style + reversal ordinar), NU mecanism nou distinct. **Corectie/completare adaugata la
  intrarea 12 din Observation Registry** (text original nemodificat, doar completat dedesubt per
  conventia append-only). Ramane fara DC/Addendum.
- **12-18 17:00 UTC - 12-19 21:45 UTC** — grind linistit ordinar (4308-4349), volum jos-moderat
  (1.3k-24k, crestere normala la deschiderea NY ~14:30 UTC deja documentata), fara mecanism nou.
- **Weekend gap (a 11-a instanta)** — Vineri 12-19 close 21:45-22:00 UTC (4338.765) -> reopen
  Duminica (bar continuu la 12-21 23:15 UTC, open 4340.905): gap real bar-la-bar de doar **+2.14pt**
  — nesemnificativ, in totalitate in tiparul stabilit (gap total ~49.25h intre ultima bara si
  prima bara noua, consistent cu conventia documentata). Fara DC/Addendum/Registry — gap minor,
  fara nimic de investigat.
- **12-21 23:15 UTC - 12-22 08:15 UTC** — grind susținut dar ordinar in sus (4361->4420, ~59pt in
  ~6.5h), volum jos-moderat (2.0k-11.1k, NU record), fara mecanism nou — trend calm pe volum usor.
- **12-22 08:15 UTC - 12-23 07:00 UTC** — continuare ordinara a grind-ului (4406->4497 apoi
  pullback la 4471-4482), volum jos-moderat pe tot parcursul (1.6k-25.4k, un varf izolat 25,353
  NU record), un jump de rollover zilnic (~4500s) fara anomalii. Fara mecanism nou.
- **12-23 07:00-13:15 UTC** — grind ordinar in sus (4478->4497.635, fresh high), volum jos-moderat
  (4.7k-18.8k). Fara mecanism nou.
- **12-23 13:15-15:10 UTC — INVESTIGATIE (5M)** — decline in doua leg-uri de la fresh high
  4497.635: leg 1 (14:00-14:15) la 4456.205 (-41.4pt, vol M15 17,001+16,015), pauza ~20min
  (4463-4472), leg 2 (14:35-15:10) extinde la fresh low 4430.515 (-67.1pt total), vol M15
  25,682/21,970/31,090 (~1.6x fata de leg 1, varf 31,090 = al 4-lea cel mai mare din tot replay-ul).
  Verificare organica pe M5 a candelei de varf: 11,767/9,355/9,968, share maxim 37.8% (sub 42.7%,
  organic). Test 3-parti: nu e mecanism nou (familia DC-0013/0018/0020/0021 + precedent direct in
  intrarea Registry 2025-11-10), nu se califica ca Addendum (nu exista un DC specific pentru
  "doua leg-uri, al doilea escaladeaza"), nu e record (67.1pt si 31,090 sub recordurile existente).
  **Logat ca Observation Registry intrarea 13** (a doua instanta locala care sustine observatia
  "al doilea leg escaladeaza" din intrarea 2025-11-10). Fara DC/Addendum creat.
- **12-23 15:15 UTC - 12-24 13:45 UTC** — recuperare ordinara din low-ul 4430.515, grind lateral
  4466-4526, volum jos-moderat (1.5k-21.3k), o candela izolata cu range mare (~38pt, 4512->4474,
  vol 16,429 NU record, recuperare graduala ulterioara — nu trece filtrul, volum insuficient de
  mare fata de pragurile anterioare 25-31k), un jump de rollover zilnic (~4500s) fara anomalii.
  Fara mecanism nou.
- **12-24 13:45-18:45 UTC** — grind ordinar linistit (4478-4482), volum jos (3.9k). Fara mecanism
  nou.
- **Christmas closure gap (12-24 ~18:45 UTC -> 12-25 23:00 UTC) — INVESTIGATIE (M1)** — prima
  inchidere de mijloc-de-saptamana (holiday) din tot replay-ul, ~28.5h (spre deosebire de cele 11
  gap-uri de weekend deja documentate, ~49-50h). Reopen: gap +23.21pt (4479.415->4502.625, NU
  record), apoi supra-extindere tranzitorie pe volum foarte subtire in primele 2 minute pana la
  4536.74 (+57.3pt fata de close, doar 229 volum), apoi fade rapid inapoi la 4485-4494 in ~3
  minute. Verificat NU e artefact de date (tape M1 continuu, coerent, spre deosebire de Black
  Friday). Test 3-parti: mecanismul "reopen cu whipsaw range-mare/volum-subtire" e deja documentat
  (intrarea Registry 2025-08-07 rollover zilnic), doar la scara mai mare si la un tip de inchidere
  nou (holiday vs weekend/rollover); nu se califica ca Addendum (niciun DC specific pentru acest
  mecanism); gap-ul de 23.21pt nu e record. **Logat ca Observation Registry intrarea 14** (prima
  instanta de inchidere holiday + cea mai mare scara a whipsaw-ului de reopen deja recunoscut).
  Fara DC/Addendum creat.
- **12-26 01:15-15:30 UTC** — grind ordinar Asia/Londra (Boxing Day), range 4492-4534, volum
  jos-moderat (7.2k-26.9k). Fara mecanism nou.
- **12-26 15:30-21:59:59 UTC** — grind ordinar linistit (4521-4536), volum jos-moderat
  (3.2k-13.0k). Fara mecanism nou.
- **Weekend gap (a 12-a instanta)** — Vineri 12-26 close 21:59:59 UTC (4533.21) -> reopen Duminica
  12-28 23:00 UTC (open 4542.66): gap real bar-la-bar de **+9.45pt** — mic, nesemnificativ, in
  tiparul stabilit. Fara DC/Addendum/Registry.
- **12-28 23:15 UTC - 12-29 07:00 UTC** — decline moderat (4534->4471.325, cea mai mare candela
  singura ~42pt/vol 23,418 la 00:15 UTC), volum moderat-crescut (7.2k-27.1k, NU record), recuperare
  partiala intermediara la 4512-4520 apoi reluare declin. Amploare si volum in banda deja
  documentata a acestei sesiuni volatile — nu trece filtrul (NU record, tipar deja familiar).
  Fara mecanism nou.
- **12-29 07:00-13:15 UTC** — declin ordinar continuat (4488->4467.7), volum moderat (7.9k-27.7k).
  Fara mecanism nou.
- **12-29 13:15-14:20 UTC — INVESTIGATIE (5M)** — declin sustinut NY-open (4467.7->4386.365,
  -81.3pt in ~1h, 13 candele M5, volum 6.3k-10.4k/candela M5, echiv M15 22.4k-27.7k). Verificare
  organica pe cele 2 candele M15 cu volum maxim: 36.6% si 38.2% concentrare maxima (sub 42.7%,
  organic). Test 3-parti: mecanismul e exact familia DC-0013 deja saturata (11 addenda A-K); banda
  de volum se suprapune aproape complet cu recordul deja stabilit de Addendum J (19.5k-26.9k);
  amploarea (~81.3pt) e sub Addenda D/89.4/G/90.81/E/93.15/F/100.97/I/120.06/H/180.53; durata
  (~1h/13 candele) e neremarcabila. Niciun axa (amploare/volum/durata/sesiune/rezolutie) nu e
  record sau combinatie noua. **Logat ca Observation Registry intrarea 15** (instanta ordinara
  suplimentara, fara dimensiune noua). Fara DC/Addendum creat.
- **12-29 14:20-15:20 UTC — CONTINUARE/CORECTIE la intrarea 15** — declinul continua mult mai
  departe: de la high-ul 4467.7 (13:05 UTC) la low intrabar **4302.11** (15:20 UTC) — **165.59pt
  total** (nu 81.3pt), peste inca 4 candele M15 consecutive cu volum 34,453/29,809/28,227/28,172
  (toate organice pe M5, concentrare maxima 36.7-41.9%, sub 42.7%). Candela de varf (34,453) e a
  **treia cea mai mare din tot replay-ul** (depaseste marginal recordul anterior 34,319 din
  Addendum C la DC-0011). Amploarea (165.59pt) e acum a doua cea mai mare din familia DC-0013
  (dupa Addendum H/180.53). Data fiind imaginea completa, **Addendum L la DC-0013 creat**
  (`addendum_2026-07-24_l.md`, hash verificat 64-hex, adaugat in HANDOFF_LOG.md) pentru a capta
  amploarea si volumul aproape-de-record ratate de observatia initiala incompleta. Corectie
  adaugata la intrarea 15 din Observation Registry (text original nemodificat, doar completat
  dedesubt per conventia append-only).
- **12-29 21:30 UTC - 12-30 13:00 UTC** — grind ordinar continuat (4324-4402), volum moderat
  (2.3k-26.9k, un jump de rollover zilnic ~4500s fara anomalii). Fara mecanism nou.
- **12-30 13:00 UTC - 12-31 04:30 UTC** — grind NY/Asia continuat (4328-4404), volum moderat-crescut
  (1.6k-29.0k, in banda deja documentata recent, NU record), un jump de rollover zilnic (~4500s)
  fara anomalii. Fara mecanism nou.
- **12-31 04:30-18:45 UTC** — declin moderat (4343->4274, ~69pt/3 candele) urmat de grind lateral
  4303-4353, volum moderat (8.4k-28.9k, in banda deja documentata, NU record). Fara mecanism nou.
- **New Year holiday closure gap (12-31 ~22:00 UTC -> 01-01 22:00 UTC)** — a doua inchidere de
  mijloc-de-saptamana (holiday) din replay (~25.25h, dupa Christmas). Gap real bar-la-bar de doar
  **+3.8pt** (4322.61->4326.405) — mic, reopen ordonat (volum subtire->normal, FARA supra-extindere
  salbatica ca la Christmas). Fara DC/Addendum/Registry — complet ordinar.
- **01-01 22:00 UTC - 01-02 09:45 UTC** — grind ordinar linistit (4362-4398), volum moderat
  (4.0k-16.4k). Fara mecanism nou.
- **01-02 09:45-21:59:59 UTC** — declin moderat (4402->4315, ~87pt, vol de varf 29,090 in banda
  deja documentata, NU record). Fara mecanism nou.
- **Weekend gap (a 13-a instanta) — INVESTIGATIE (M5)** — Vineri 01-02 close 21:59:59 UTC
  (4332.065) -> reopen Duminica 01-04 23:00 UTC (open 4356.505): gap **+24.44pt** (al doilea cel
  mai mare gap din tot replay-ul, dupa recordul DC-0019/28.43pt). Gap NU s-a umplut — pretul a
  extins in continuare in aceeasi directie (sus) pana la un maxim intrabar de **4421.605**
  (~01:00-01:15 UTC luni), **89.54pt peste close-ul pre-gap** — depaseste chiar extensia finala a
  DC-0019 (~60.4pt). Verificare organica pe M5 a candelei de volum maxim (27,561): 10,101/9,289/
  8,171, share maxim 36.65% (sub 42.7%, organic). Dupa varf, stabilizare 4388-4421 fara al doilea
  leg de declin (spre deosebire de Addendum A la DC-0019). Test 3-parti: acelasi mecanism ca
  DC-0019 (gap mare, nu se umple, extinde in directia gap-ului) dar **prima instanta in directia
  SUS** (DC-0019 + Addendum A erau ambele in jos); nu e record pe gap (24.44 sub 28.43) dar extensia
  totala (89.54pt) E mai mare decat orice extensie DC-0019. **Addendum B la DC-0019 creat**
  (`addendum_2026-07-24_b.md`, hash verificat, adaugat in HANDOFF_LOG.md). Fara DC nou.
- **01-05 03:15-17:15 UTC** — grind NY/Londra continuat (4396-4456), volum moderat-crescut
  (4.2k-26.1k, in banda deja documentata, NU record). Fara mecanism nou.
- **01-05 17:15 UTC - 01-06 08:15 UTC** — grind ordinar continuat (4427-4474), volum moderat
  (969-20.1k), un jump de rollover zilnic (~4500s) fara anomalii. Fara mecanism nou.
- **01-06 08:15-23:15 UTC** — grind ordinar continuat (4442-4499), volum moderat-crescut
  (1.5k-25.7k, in banda deja documentata, NU record), un jump de rollover zilnic (~4500s) fara
  anomalii. Fara mecanism nou.
- **01-06 23:15 UTC - 01-07 13:15 UTC** — grind ordinar continuat (4428-4475), volum moderat
  (4.0k-24.7k, in banda deja documentata, NU record). Fara mecanism nou.
- **01-07 13:15 UTC - 01-08 04:15 UTC** — grind ordinar continuat (4423-4468), volum moderat
  (1.2k-23.1k, in banda deja documentata, NU record), un jump de rollover zilnic (~4500s) fara
  anomalii. Fara mecanism nou.
- **01-08 04:15-11:15 UTC** — grind ordinar continuat (4415-4440), volum moderat (4.1k-26.0k, in
  banda deja documentata, NU record). Fara mecanism nou.
- **01-08 11:15-18:15 UTC** — grind ordinar continuat (4407-4465), volum moderat-crescut
  (6.2k-28.7k, in banda deja documentata, NU record). Fara mecanism nou.
- **01-08 18:15 UTC - 01-09 09:15 UTC** — grind ordinar linistit continuat (4452-4478), volum
  moderat (1.9k-18.7k, in banda deja documentata, NU record), un jump de rollover zilnic (~4500s)
  fara anomalii. Fara mecanism nou.
- **01-09 09:15-21:59:59 UTC** — rally sustinut NY (4458->4517, ~55pt, vol pana la 29,103, in
  banda deja documentata, NU record), apoi grind lateral 4504-4511. Fara mecanism nou.
- **Weekend gap (a 14-a instanta)** — Vineri 01-09 close 21:59:59 UTC (4509.66) -> reopen Duminica
  01-11 22:00 UTC (open 4521.495): gap real bar-la-bar de **+11.84pt** — moderat, nesemnificativ,
  in tiparul stabilit. Fara DC/Addendum/Registry.
- **01-11 23:15 UTC - 01-12 00:15 UTC** — continuare rally dupa reopen (4521->4554), volum
  moderat (2.1k-9.8k). Fara mecanism nou.
- **01-12 00:15-07:15 UTC** — rally continuat (4553->4601.695, ~49pt), apoi grind lateral
  4562-4595, volum moderat-crescut (6.0k-28.6k, in banda deja documentata, NU record). Fara
  mecanism nou.
- **01-12 07:15-14:15 UTC** — grind/rally continuat (4578-4620), volum moderat-crescut
  (7.2k-22.9k, in banda deja documentata, NU record). Fara mecanism nou.
- **01-12 14:15-21:15 UTC** — rally/grind continuat (4585-4630), volum moderat-crescut
  (4.5k-28.5k, in banda deja documentata, NU record). Fara mecanism nou.
- **01-12 21:15 UTC - 01-13 05:15 UTC** — grind ordinar continuat (4575-4600), volum moderat
  (2.8k-21.1k, in banda deja documentata, NU record), un jump de rollover zilnic (~4500s) fara
  anomalii. Fara mecanism nou.
- **01-13 05:15-12:15 UTC** — grind ordinar linistit continuat (4573-4602), volum moderat
  (4.1k-17.6k, in banda deja documentata, NU record). Fara mecanism nou.
- **01-13 12:15-19:15 UTC** — rally la 4634.89 apoi declin la 4581.175 (~54pt swing), volum
  moderat-crescut (5.9k-30.4k, in banda deja documentata — max sub Addendum L/34,453, NU record).
  Fara mecanism nou.
- **01-13 19:15 UTC - 01-14 03:15 UTC** — grind ordinar continuat (4569-4624), volum moderat
  (1.9k-19.9k, in banda deja documentata, NU record), un jump de rollover zilnic (~4500s) fara
  anomalii. Fara mecanism nou.
- **01-14 03:15-10:15 UTC** — grind ordinar linistit continuat (4617-4640), volum moderat
  (4.2k-17.4k, in banda deja documentata, NU record). Fara mecanism nou.
- **01-14 10:15-17:15 UTC** — declin moderat (4641.74->4599.5, ~42.2pt) cu volum sustinut ridicat
  pe mai multe candele (varf 33,334, sub plafonul Addendum L/34,453, NU record), apoi grind
  4608-4626. Fara mecanism nou.
- **01-14 17:15 UTC - 01-15 01:15 UTC** — grind ordinar continuat (4602-4643), volum moderat
  (3.1k-19.8k, in banda deja documentata, NU record), un jump de rollover zilnic (~4500s) fara
  anomalii. Fara mecanism nou.
- **01-15 01:15-08:15 UTC** — declin moderat (4610.24->4581.065, ~29.2pt) cu volum sustinut ridicat
  (varf 32,294, sub plafonul Addendum L/34,453, NU record), apoi grind 4581-4614. Fara mecanism
  nou.
- **01-15 08:15-15:15 UTC** — grind ordinar continuat (4581-4623), volum moderat-crescut
  (6.1k-29.3k, in banda deja documentata, NU record). Fara mecanism nou.
- **01-15 15:15-23:45 UTC** — consolidare ordinara continuata (4600-4625), volum moderat
  (1.2k-22.6k, in banda deja documentata, NU record), un jump de rollover zilnic (~4500s) fara
  anomalii. Fara mecanism nou.
- **01-15 23:45 UTC - 01-16 07:30 UTC** — grind ordinar continuat cu declin moderat (4616.32->
  4591.37, ~25pt) apoi recuperare partiala, volum moderat (3.9k-20.9k, in banda deja documentata,
  NU record). Fara mecanism nou.
- **01-16 07:30-15:15 UTC** — grind ordinar continuat (4598-4616) cu o scurta scadere in volatilitate
  (4616->4582.67, ~34pt) urmata de recuperare la 4620.39, volum moderat-crescut (3.0k-21.1k, in banda
  deja documentata, NU record). Fara mecanism nou.
- **01-16 15:15-15:45 UTC — INVESTIGATIE, DC-0025 CREAT**: declin de tip "waterfall" pe DOAR 2
  lumanare M15 (30 minute), 4620.39->4536.49 (~83.9pt), a doua lumanare (15:30-15:45, 39,353) fiind
  NOU RECORD ALL-TIME de volum single-candle (depaseste DC-0020/37,204 cu +5.8%). Pe M5, volumul
  escaladeaza pe 4 sub-lumanare consecutive (6.4k->11.3k->13.6k->15.2k) exact pana la minimul
  episodului, apoi scade (13.0k->11.2k) — semnatura clara de climax organic, NU artefact
  (concentrare 43.5% / 38.7%, aproape de/sub pragul 42.7%). Testul in 3 pasi CEO aplicat: mecanism
  nou (2 lumanare vs. minim 4 al familiei DC-0013), nu e doar addendum la DC-0013 (viteza de
  realizare cu un ordin de marime mai mare), nu e doar un nou record al DC-0018/DC-0020 (structuri
  diferite — fara fresh-high-failure, fara 18:00 sweep-reclaim). DC-0025 creat si inghetat.
  NOTA METODOLOGICA: evenimentul a fost initial ratat mid-batch (pozitia replay a trecut si de gap-ul
  de weekend inainte de verificarea OHLCV M15); datele M15/M5 au ramas totusi accesibile (bufferul M5
  de ~300 lumanari, numarate de la pozitia curenta, tot acoperea evenimentul chiar si dupa gap).
- **01-16 15:45 UTC - 01-16 21:45 UTC (inchidere vineri)** — recuperare ~75% din declin (4536.49->
  4599.2 varf), apoi consolidare 4576-4599, inchidere saptamana la 4596.32. Fara mecanism nou dincolo
  de DC-0025.
- **Gap de weekend (01-16 21:45 UTC -> 01-18 23:00 UTC, ~49h05m) — INVESTIGATIE, ADDENDUM C LA
  DC-0019**: gap de **+53.46pt in sus** (4596.32->4649.78) — NOU RECORD ALL-TIME de magnitudine gap
  de weekend (orice directie), depasind recordul de baza al DC-0019 (28.425pt jos) cu ~88% si
  Addendum B (24.44pt sus) cu peste 100%. Gap-ul NU s-a retras deloc; pretul s-a extins pana la
  4690.94 (~94.62pt peste inchiderea pre-gap, NOU RECORD de extensie pe directia sus, depaseste
  Addendum B/89.54pt), apoi s-a stabilizat 4653-4682 fara retragere completa — acelasi mecanism DC-0019
  deja documentat, doar un nou record de magnitudine. Verificare M5 organica pe lumanara-varf de
  extensie (11,229, concentrare 37.7%) si pe lumanara-varf de volum a episodului (21,573, concentrare
  39.96%) — ambele organice. Addendum C la DC-0019 creat si inghetat.
- **01-18 23:00 UTC - 01-19 02:59:59 UTC** — grind ordinar continuat post-reopen (4653-4682), volum
  moderat (2.1k-21.6k, sub orice record), fara mecanism nou dincolo de Addendum C.
- **01-19 02:59:59-10:29:59 UTC** — grind ordinar continuat, foarte linistit (4658-4679), volum
  scazut-moderat (3.1k-11.3k, mult sub orice record). Fara mecanism nou.
- **01-19 10:29:59-18:14:59 UTC** — grind ordinar continuat, linistit (4659-4679), volum
  scazut-moderat (2.4k-12.6k, mult sub orice record). Fara mecanism nou.
- **01-19 18:14:59-19:30 UTC** — grind ordinar continuat (4670-4679), volum scazut (2.4k-4.2k).
- **GAP 01-19 19:30-23:00 UTC (3h45m) — OBSERVATION REGISTRY intrarea 16**: gol de timp de 3h45m,
  de ~3x mai lung decat pauza de rollover zilnic deja documentata (~4500s/75min), dar pret continuu
  (4670.295->4668.575, doar 1.72pt diferenta) si volum linistit la reluare (2,122) — NU dislocare de
  pret, NU eveniment de volatilitate. Test in 3 pasi: NU mecanism nou (aceeasi categorie deja
  documentata, doar durata mai mare), NU exista un DC-tinta pentru addendum (pauza de rollover nu a
  fost niciodata promovata la DC), record doar pe durata, fara record de pret/volum insotitor. Logat
  in Observation Registry (intrarea 16), NU DC/addendum.
- **01-19 23:00 UTC - 01-20 05:29:59 UTC** — grind ordinar continuat (4659-4682) apoi urcare
  moderata pana la 4701.615, volum scazut-moderat (2.1k-13.8k, mult sub orice record). Fara mecanism
  nou.
- **01-20 05:29:59-12:59:59 UTC** — urcare moderata continuata (4694->4737.57 varf), apoi consolidare
  4724-4733, volum moderat (5.2k-12.4k, mult sub orice record). Fara mecanism nou.
- **01-20 12:59:59-20:14:59 UTC** — urcare continuata cu pullback-uri normale (4715->4766 varf),
  volum moderat-crescut (4.9k-31.8k, in banda deja documentata, NU record). Fara mecanism nou.
- **01-20 20:14:59 UTC - 01-21 04:29:59 UTC** — consolidare linistita (4747-4787, volum 1.3k-10.7k)
  urmata de o urcare sustinuta incepand ~01:00 UTC (early Asia), 4784->4849.99, cu 4 candele
  consecutive la volum elevat (15.1k-19.2k, in banda deja documentata a familiei DC-0016, NU record).
  Un jump de rollover zilnic (~4500s) fara anomalii.
- **01-21 04:29:59-11:59:59 UTC — RALLY INCHIS, FARA MECANISM NOU**: rally-ul a continuat pana la un
  varf de 4888.545 (~06:15 UTC), apoi a inversat ~55.8pt pana la 4832.725 (~07:15 UTC), urmat de chop
  4834-4888 fara alta extensie. Deoarece traseul complet contine o inversare de amploare la mijloc
  (nu expansiune sustinuta fara reversal), NU se potriveste criteriul definitoriu al familiei
  DC-0013/15/16/22/24 ("no reversal"/expansiune curata). Volum maxim 14,670, mult sub orice record.
  Concluzie: activitate ordinara multi-faza de sesiune, NU DC/addendum.
- **01-21 11:59:59-19:14:59 UTC** — declin sustinut NY-session (14:00-17:30 UTC, ~78.3pt, 4880.935->
  4802.62) pe 14 candele consecutive cu volum ridicat (17k-33,954, varf 33,954 clasat ~6 all-time dar
  NU record), urmat de recuperare partiala (~60%, pana la ~4849-4850). Testul in 3 pasi: NU mecanism
  nou (potrivire exacta cu familia DC-0013 — sesiune NY, volum sustinut multi-candela, declin apoi
  recuperare partiala), amploarea/volumul/durata (14 candele) toate in bandele deja documentate ale
  familiei (Addendum K a avut tot 14 candele), NU record pe nicio axa. Concluzie: instanta ordinara
  suplimentara, NU addendum.
- **01-21 19:14:59 UTC - 01-22 03:29:59 UTC — INVESTIGATIE, ADDENDUM A LA DC-0025**: declin waterfall
  pe 3 candele M15 consecutive (19:15-20:00 UTC, ~99.09pt, 4854.165->4755.075), lumanara centrala
  (19:30-19:45, 41,995) fiind NOU RECORD ALL-TIME de volum (depaseste DC-0025/39,353 cu +6.7%).
  Verificat organic pe M5: lumanara-record 34.9% concentrare, a treia lumanara 38.1% (ambele sub
  42.7%); prima lumanara (17,702) are 60.5% concentrare dar cu volum substantial pe toate cele 3
  sub-lumanare si pret continuu — nu artefact, doar o acceleratie rapida. Recuperare ~85.6% (pana la
  4839.9) apoi consolidare 4772-4820. Test in 3 pasi: NU mecanism nou (exact mecanismul DC-0025, doar
  mai mare/mai lent cu o lumanare), addendum justificat (nou record all-time de volum si de amploare
  in cadrul familiei), NU DC nou. Addendum A la DC-0025 creat si inghetat.

- **01-22 03:29:59-10:44:59 UTC** — grind ordinar continuat (4790-4839), volum scazut-moderat
  (4.3k-11.1k, mult sub orice record). Fara mecanism nou.
- **01-22 10:44:59-17:59:59 UTC** — urcare sustinuta cu pullback-uri normale (4815->4906.47 varf),
  volum moderat-crescut (3.6k-25.4k, mult sub orice record). Fara mecanism nou.
- **01-22 17:59:59 UTC - 01-23 02:14:59 UTC** — grind ordinar continuat mai sus (4901->4967.52 varf)
  apoi chop 4936-4967, volum moderat-crescut (3.1k-22.8k, mult sub orice record). Un jump de rollover
  zilnic (~4500s) fara anomalii. Fara mecanism nou.
- **01-23 02:14:59-09:29:59 UTC** — chop ordinar continuat (4938-4967) apoi declin usor spre finalul
  batch-ului (pana la 4899.795), volum scazut-moderat (1.5k-16.1k, mult sub orice record). Fara
  mecanism nou.
- **01-23 09:29:59-16:44:59 UTC** — urcare sustinuta cu pullback-uri normale (4903->4988.44 varf),
  volum moderat-crescut (5.1k-22.4k, mult sub orice record). Fara mecanism nou.
- **01-23 16:44:59-21:59:59 UTC** — grind ordinar continuat (4958-4990), volum moderat (2.3k-16.3k,
  mult sub orice record). Fara mecanism nou.
- **Gap de weekend (01-23 21:59:59 UTC -> 01-25 23:14:59 UTC, ~49h15m)** — gap de +28.085pt in sus
  (4987.545->5015.63), NU s-a retras, s-a extins pana la 5052.26 (~64.7pt peste close-ul pre-gap).
  Test in 3 pasi: acelasi mecanism deja documentat (DC-0019), NU record pe nicio axa (gap 28.085pt <
  recordul 53.46pt si < recordul de baza 28.425pt; extensie 64.7pt < recordul 94.62pt) — instanta
  ordinara suplimentara, NU addendum.
- **01-25 23:14:59 UTC - 01-26 00:59:59 UTC** — continuare urcare post-reopen (5015->5052.26), volum
  moderat (7.7k-14.2k). Fara mecanism nou.
- **01-26 00:59:59-08:14:59 UTC** — chop ordinar continuat (5052-5111.51), volum moderat-crescut
  (7.6k-24.1k, mult sub orice record). Fara mecanism nou.
- **01-26 08:14:59-15:29:59 UTC** — chop ordinar continuat (5054-5098), volum moderat-crescut
  (6.9k-29.5k, in banda deja documentata, NU record). Fara mecanism nou.
- **01-26 15:29:59 UTC - 01-27 00:44:59 UTC — INVESTIGATIE, ADDENDUM M LA DC-0013**: declin NY-afternoon
  pe 15 candele consecutive (18:00-21:30 UTC, ~114.935pt, 5105.15->4990.215), lumanara-varf
  (19:15-19:30, 38,755) fiind NOU RECORD ALL-TIME #3 de volum (depaseste DC-0020/37,204 si
  DC-0018/36,798, sub doar Addendum A la DC-0025/41,995 si DC-0025/39,353). 4 din 15 candele au avut
  volum peste 33,000 — cea mai mare densitate de candele aproape-de-record dintr-un singur episod al
  familiei observata pana acum. Verificat organic pe M5 (37.2% concentrare maxima, sub 42.7%).
  Recuperare ~59% (pana la 5058.14) apoi consolidare. Test in 3 pasi: NU mecanism nou (exact
  mecanismul DC-0013), addendum justificat (nou record all-time de volum #3), NU DC nou. Addendum M
  la DC-0013 creat si inghetat. Un jump de rollover zilnic (~4500s) fara anomalii, gap ordinar.

- **01-27 00:44:59-08:59:59 UTC** — chop ordinar continuat (5013-5094), volum moderat-crescut
  (4.1k-28.6k, sub orice record). Fara mecanism nou.
- **01-27 08:59:59-16:14:59 UTC** — chop ordinar continuat, linistit (5055-5100), volum
  scazut-moderat (3.7k-23.5k, sub orice record). Fara mecanism nou.
- **01-27 16:14:59-23:29:59 UTC** — grind ordinar (5046-5103) urmat de un impuls rapid (2 candele
  M15 cu miscare >40pt fiecare) 5093->5190.51 varf (~91-97pt in ~2h), volum elevat (varf 37,228 —
  doar +24 peste DC-0020/37,204, o diferenta neglijabila/in zgomot, NU record semnificativ). Rezolutie:
  "hold gains" fara reversal, aceeasi forma ca DC-0017 dar la sesiune/ora diferita (NY afternoon, NU
  12:30 UTC NFP). Test in 3 pasi: NU mecanism nou (potrivire cu forma deja documentata), NU record
  semnificativ pe nicio axa (diferenta de volum e in limita zgomotului natural), NU addendum
  justificat. Concluzie: instanta ordinara, NU DC/addendum. Un jump de rollover zilnic (~4500s)
  fara anomalii.

- **01-28 00:59:59-08:14:59 UTC — RALLY SUSTINUT IN DESFASURARE**: urcare continua de la ~5157-5172
  pana la 5300.02 varf (~128-143pt in ~7h15m), doar pullback-uri minore (sub 15pt fiecare), volum
  moderat (8k-27k, mult sub orice record). Amploarea se apropie de recordul all-time DC-0024
  (125.685pt, in jos) dar in directia SUS. Rally-ul e INCA IN DESFASURARE la finalul batch-ului — de
  urmarit in continuare inainte de a decide daca merita filtrul v2 pe axa amploare/durata inainte de a
  inchide investigatia.

- **01-28 08:14:59-15:29:59 UTC — INVESTIGATIE, ADDENDUM A LA DC-0024 + ADDENDUM B LA DC-0025**:
  rally-ul sustinut s-a incheiat la un varf de 5311.665 (~154.665pt de la baza de consolidare 5157,
  deja logata) — NOU RECORD ALL-TIME DE AMPLOARE (depaseste recordul propriu al DC-0024/125.685pt cu
  +23%, prima data in directia SUS), pe ~32 candele/~8h. Rezolutia: NU o recuperare graduala ca la
  DC-0024, ci un REVERSAL abrupt — 2 candele M15 (15:00-15:30 UTC), 75.915pt in 30 min, cu o
  sub-miscare de ~58pt in doar 5 minute (M5). AMBELE candele au depasit recordul all-time anterior de
  volum (41,995): 42,339 si **42,808 (NOU RECORD ALL-TIME #1)**. Verificat organic pe M5: prima
  candela 42.68% concentrare (marginal SUB pragul 42.7%, notat onest ca limita), a doua candela 37.9%
  (clar organic). Test in 3 pasi (ambele): NU mecanism nou (amploarea = record al mecanismului deja
  documentat DC-0024; reversal-ul = mecanismul deja documentat DC-0025, doar mai rapid/mare), addenda
  justificate (recorduri all-time pe axe distincte), NU DC nou. Addendum A la DC-0024 + Addendum B la
  DC-0025 create si inghetate.

- **01-28 15:29:59-23:34:00 UTC** — grind ordinar continuat (5266->5502.145), volum moderat-crescut
  (15k-39.7k, sub orice record), un jump de rollover zilnic (~4500s) fara anomalii. Fara mecanism nou.
- **01-28 23:34:00-23:45:00 UTC — INVESTIGATIE, DC-0026 CREAT**: puseu parabolic extrem de rapid la
  redeschiderea de dupa rollover-ul zilnic (fereastra de lichiditate subtire): +100.08pt in ~6 minute
  (5502.145->5602.225), apoi reversal -77.1pt in ~4-5 minute (pana la 5525.125) — cea mai rapida
  viteza punct/minut din tot replay-ul (~2x mai rapida decat recordul anterior, Addendum B la
  DC-0025/~58pt in 5 min). Verificat organic pe M1 (nu doar M5): volum sanatos pe fiecare minut
  (900-4,100), pret continuu fara teleportare, concentrare maxima ~29% pe sub-minute — NU semnatura de
  artefact (contrast cu Black Friday, intrarea 11 Registry). NU record de volum (candelele raman mult
  sub recordul all-time 42,808). Rezolutie: NU stabilizare curata, ci chop volatil continuat
  (5444-5551) urmator. Test in 3 pasi: mecanism nou (viteza extrema + context de redeschidere
  rollover zilnic, nicio combinatie similara documentata), NU e doar addendum (DC-0001/DC-0010/DC-0025
  nu au aceeasi forma de "puseu-apoi-reversal complet in minute la redeschiderea zilnica"), NU doar
  record (axa noua e viteza, nu volum/amploare). DC-0026 creat si inghetat.

- **01-29 01:44:59-08:59:59 UTC** — chop volatil continuat (5473-5595), volum moderat (10k-25.8k,
  sub orice record). Fara mecanism nou.

- **01-29 08:59:59-14:15:00 UTC** — grind ordinar continuat (5497-5549.565), volum moderat
  (10k-16.9k, sub orice record). Fara mecanism nou.
- **01-29 14:15:00-16:14:59 UTC — INVESTIGATIE, OBSERVATION REGISTRY intrarea 17 (POSIBIL ARTEFACT DE
  DATE)**: declin sustinut real pe volum mare (13.8k-19.4k pe M5, agregand la 43,298/44,574/53,832/
  50,066 pe M15 — ar fi noi recorduri all-time daca luate ca atare). Pe M1, in interiorul candelei
  M15 15:15-15:30 UTC, DOUA minute consecutive (15:27-15:29 UTC) arata volum anormal de mic (748 si
  1,024) fata de range-ul lor (120.4pt si 56.5pt) — raport volum/punct de doar ~6-18 vs. bandă
  normală ~90-110 in aceeasi fereastra — semnatura de artefact "range mare, volum needobitor de mic"
  (diferita de Black Friday dar acelasi principiu). Minimul absolut (5097.215) si round-trip-ul
  intra-minut de 89.5pt cad exact in aceste minute compromise. Declinul GENUIN (bine sustinut pe volum
  pana la ~15:26 UTC) e estimat conservator la ~291-307pt (5549.565->~5242-5258), NU ~452pt/noile
  recorduri de volum, care raman nesuportate. Test in 3 pasi: NU aplicat pentru DC/addendum per
  instructiunea CEO — la semnatura de artefact, se logheaza in Registry si se continua, fara DC/
  addendum. Intrarea 17 adaugata la Observation Registry.

- **01-29 16:14:59 UTC - 01-30 00:29:59 UTC — INVESTIGATIE, ADDENDUM B LA DC-0023**: episod choppy
  sustinut cu volum persistent ridicat (16:15-21:00 UTC, ~4.5h, 19 candele, toate peste 23,000),
  lumanara-varf (16:15-16:30, **48,401**) fiind NOU RECORD ALL-TIME #1 de volum (depaseste recordul
  anterior 42,808 cu +13.1%, DC-0025 Addendum B trece pe locul 2). Verificat organic pe M5 (35.3%/
  35.9%/33.9% concentrare maxima pe cele 3 candele mari, toate sub 42.7%, distributie chiar mai
  uniforma decat multe recorduri anterioare). Pret choppy/multi-leg (5228-5451), fara displasare neta
  clara. Test in 3 pasi: NU mecanism nou (acelasi mecanism DC-0023/Addendum A), addendum justificat
  (nou record all-time de volum), NU DC nou. Addendum B la DC-0023 creat si inghetat. NOTA: acest
  episod e SEPARAT de declinul cu artefact deja logat (Registry 17) — nu se face nicio afirmatie
  despre amploarea acelui declin aici.

- **01-30 00:29:59-07:44:59 UTC** — declin choppy continuat cu volum ridicat (5436->5112), volum
  14.7k-44.9k (in banda deja documentata, sub recordul 48,401, NU record nou). Fara mecanism nou.
- **01-30 07:44:59-14:59:59 UTC** — episodul choppy/volum-ridicat CONTINUA (5181->4941), volum
  14.9k-49,448 (varf marginal peste recordul 48,401 din Addendum B la DC-0023, +2.2%, verificat
  organic pe M5 la 39.8% concentrare). Increment marginal in cadrul aceluiasi episod deja documentat
  si adendumat — NU addendum separat (consistent cu decizia anterioara pentru diferenta +0.06%
  37,228 vs 37,204). Fara mecanism nou.

- **01-30 14:59:59-22:00:00 UTC — INVESTIGATIE MAJORA, ADDENDUM C LA DC-0023 + ADDENDUM B LA
  DC-0024**: episodul choppy/volum-ridicat s-a intensificat DECISIV (14:30-18:35 UTC, ~4h05m):
  amploare **434.285pt (5113.795->4679.51) — NOU RECORD ALL-TIME ABSOLUT de magnitudine**, depaseste
  Addendum A la DC-0024 (154.665pt) cu +181% (aproape triplu!). Volum: lumanara-varf (15:00-15:15,
  **53,154**) fiind NOU RECORD ALL-TIME #1, depaseste Addendum B la DC-0023 (48,401) cu +9.8% — de
  data asta o diferenta DECISIVA, nu zgomot (spre deosebire de incrementul marginal +2.2% notat
  anterior). Alte 3 candele (52,558/50,809/50,599) depasesc de asemenea 48,401. Verificat organic pe
  M5 pe toate cele 4 candele mari (33.6-36.7% concentrare, sub 42.7%, distributie uniforma pe toate
  sub-lumanarele). CRITIC: lumanara M5 cu minimul absolut (4679.51) are un raport volum/punct de
  ~158 (13,149 vol/83.3pt range) — MULT PESTE banda normala (~90-110), opusul semnaturii de artefact
  gasite la declinul din 01-29 (Registry 17) — acest minim e pe deplin sustinut de volum, NU artefact.
  Recuperare ~58% (pana la ~4926.755) apoi consolidare. Test in 3 pasi (ambele): NU mecanism nou
  (amploarea = record al DC-0024, volumul = record al episodului DC-0023, ambele deja documentate),
  addenda justificate (recorduri all-time decisive pe axe distincte), NU DC nou. Addendum C la
  DC-0023 + Addendum B la DC-0024 create si inghetate. Gap de weekend (~4501-59:59 UTC 01-30 ->
  23:14:59 UTC 02-01, ~49h15m) urmator, ordinar.

- **02-01 23:14:59 UTC - 02-02 06:29:59 UTC** — declin volatil continuat (4728->4433), volum
  21.7k-47k (in banda deja documentata, sub recordul 53,154, NU record nou). Fara mecanism nou.

- **02-02 06:29:59-13:44:59 UTC — INVESTIGATIE, ADDENDUM C LA DC-0024**: minimul 4402.38 (deja
  notat ca finalul declinului anterior, fara record nou) a fost urmat de o revenire sustinuta,
  multi-leg, pana la un maxim de **4812.265** (~12:45 UTC) — amploare **409.885pt pe directia UP in
  ~6h15m (25 lumanari)**, **NOU RECORD ALL-TIME pe directia UP**, depaseste Addendum A la DC-0024
  (154.665pt) cu +165%. Ramane sub recordul absolut (434.285pt, Addendum B, directie DOWN). Fara
  volum-record (max 47,068, mult sub 53,154). Verificat organic pe M5 pe cele 3 candele cheie
  (37.2%/35.7%/42.1% concentrare, toate sub pragul 42.7%). Test in 3 pasi: NU mecanism nou (acelasi
  mecanism sustinut multi-leg ca baza + Addendum A/B), addendum justificat (record decisiv +165% pe
  axa UP), NU DC nou. Addendum C la DC-0024 creat si inghetat. Dupa maxim, retragere partiala pana la
  4686.02 (~13:15 UTC, ~31% din urcare) inainte de finalul batch-ului.

- **02-02 13:44:59 UTC - 02-10 15:29:59 UTC** — ~8 zile de piata parcurse fara mecanism nou. Continut:
  choppy/consolidare cu volum ordinar (majoritatea 5k-25k), un declin cu volum in escaladare pana la
  47,513 (5024.03->4789.655, 234.38pt, 02-04) — instanta suplimentara a mecanismului deja documentat
  DC-0023/DC-0024, sub ambele recorduri (53,154 volum / 409-434pt magnitudine), NU addendum. Un gap
  de weekend (02-06 ~21:44:59 UTC -> 02-08 ~14:14:59 UTC, verificat exact pe bare OHLCV = 177,300s =
  49.25h, cadenta standard) cu magnitudine modesta (+25.31pt, 4964.62->4989.93) — mult sub recordul
  DC-0019 (53.46pt), NU addendum. NOTA METODOLOGICA: valorile `current_date` intermediare intoarse de
  `replay_step` in timpul skip-ului de weekend NU sunt aliniate la granitele candelelor — verificarea
  reala a gap-ului s-a facut pe timestamp-urile bare din `data_get_ohlcv`, nu pe `current_date` brut.

- **02-10 15:29:59 UTC - 02-13 17:14:59 UTC** — ~3 zile de piata parcurse fara mecanism nou. Continut:
  choppy/consolidare cu volum ordinar (majoritatea 2k-26k), un declin moderat (5083.86->4878.50,
  205.35pt, 02-11/12) si o recuperare simetrica ulterioara — ambele in banda deja documentata, sub
  recordurile 53,154 volum / 409-434pt magnitudine, NU addendum. Fara gap de weekend in aceasta
  fereastra (doar pauze de rollover zilnic ~4500s, ordinare).

- **02-13 17:14:59 UTC - 02-18 14:29:59 UTC** — ~5 zile de piata parcurse fara mecanism nou. Continut:
  choppy/consolidare cu volum ordinar (majoritatea 2k-30k), un gap de weekend (02-13 ~21:something
  UTC -> 02-16, verificat exact pe bare OHLCV = 177,300s = 49.25h, cadenta standard) cu magnitudine
  modesta (-25.6pt), NU addendum; un gap mid-saptamana ~3h45m (verificat pe bare OHLCV, continuitate
  de pret ~5.3pt, volum redus) — instanta suplimentara a fenomenului deja documentat in Observation
  Registry intrarea 16, NU intrare noua necesara (fara informatie noua). Declinuri/recuperari
  moderate (max 112.35pt, 102.1pt) cu volum sub 30k — toate sub recordurile 53,154/409-434pt.

- **02-18 14:29:59 UTC - 02-20 10:29:59 UTC** — ~2 zile de piata extrem de linistite, fara mecanism
  nou. Volum ordinar scazut (majoritatea 1.5k-13k), range-uri modeste (max 61.07pt) — cea mai
  linistita fereastra din ultimele saptamani. Doar pauze de rollover zilnic ~4500s, ordinare.

- **02-20 10:29:59 UTC - 02-25 06:59:59 UTC** — ~5 zile de piata parcurse fara mecanism nou. Continut:
  choppy/consolidare cu volum ordinar (majoritatea 2k-22k), un gap de weekend (verificat exact pe
  bare OHLCV = 177,300s = 49.25h, cadenta standard) cu magnitudine neglijabila (+10.5pt), NU
  addendum. Declinuri/recuperari moderate (max 98.1pt) — toate sub recordurile 53,154/409-434pt.

- **02-25 06:59:59 UTC - 02-26 11:59:59 UTC** — ~1.2 zile de piata linistite, fara mecanism nou.
  Volum ordinar scazut (majoritatea 1.4k-21k), range-uri modeste (max 80.09pt). Doar pauze de
  rollover zilnic ~4500s, ordinare.

- **02-26 11:59:59 UTC - 02-28 16:59:59 UTC** — ~2.2 zile de piata linistite, fara mecanism nou.
  Volum ordinar (majoritatea 2.2k-18.8k), range-uri modeste (max 63.54pt). Doar pauze de rollover
  zilnic ~4500s, ordinare.

- **02-28 16:59:59 UTC - 03-01 14:59:59 UTC** — ~0.9 zile de piata linistite, fara mecanism nou.
  Volum ordinar (majoritatea 2.9k-28.4k), range-uri modeste (max 72.14pt). Doar pauze de rollover
  zilnic ~4500s, ordinare.

- **03-01 14:59:59 UTC - 03-02 05:59:59 UTC — INVESTIGATIE MAJORA, ADDENDUM D LA DC-0019**: gap de
  weekend standard ca durata (177,300s=49h15m, verificat pe bare OHLCV) dar EXCEPTIONAL ca
  magnitudine: Vineri 2026-02-27 21:45:00 UTC close 5278.51 -> Duminica 2026-03-01 23:00:00 UTC
  reopen 5368.53 = **+90.02pt — NOU RECORD ALL-TIME de magnitudine gap** (orice directie), depaseste
  Addendum C (53.46pt) cu +68.4%. Extensie ulterioara (~40min) pana la maxim 5394.005 (23:40 UTC) =
  **115.495pt peste close-ul pre-gap — NOU RECORD ALL-TIME de extensie**, depaseste Addendum C
  (94.62pt) cu +22.1%. Fara retragere (pattern consistent cu toata familia DC-0019). Verificat
  organic pe M5: candela de reopen (16,786 vol) are prima sub-candela de 5min cu doar 1 unitate de
  volum — semnatura standard de lichiditate subtire la reopen, deja documentata, NU artefact; candela
  de varf a extensiei (17,521 vol) are concentrare 50.6% (peste pragul 42.7%) dar raport volum/punct
  de 462.4 (mult peste banda normala ~90-110) — semnatura OPUSA artefactului de date, confirmand
  autenticitatea. Test in 3 pasi: NU mecanism nou (acelasi mecanism gap-fara-retragere ca baza +
  A/B/C), addenda justificate (recorduri decisive pe ambele axe), NU DC nou. Addendum D la DC-0019
  creat si inghetat.

- **03-02 05:59:59 UTC - 03-03 04:14:59 UTC** — ~0.93 zile de piata parcurse fara mecanism nou.
  Continut: choppy/consolidare cu volum ordinar (majoritatea 5k-23k), un declin moderat (156.76pt,
  volum max 22,953) — in banda deja documentata, sub recordurile 53,154/409-434pt.

- **03-03 04:14:59 UTC - 03-04 05:14:59 UTC** — declin sustinut, volum in escaladare pana la
  **50,079** (aproape de recordul 53,154, +/-5.7%, monitorizat indeaproape cu batch-uri mici) si
  magnitudine pana la ~379.6pt (aproape de recordurile 409-434pt) — declinul s-a oprit/consolidat
  FARA a depasi niciun record (nici volum, nici magnitudine). Instanta suplimentara a mecanismului
  deja documentat DC-0023/DC-0024, NU addendum. Recuperare ulterioara (107.61pt) fara mecanism nou.

- **03-04 05:14:59 UTC - 03-05 03:14:59 UTC** — ~0.92 zile de piata parcurse fara mecanism nou.
  Continut: choppy/consolidare cu volum ordinar (majoritatea 6.8k-19.7k), range-uri modeste (max
  97.63pt). Doar pauze de rollover zilnic ~4500s, ordinare.

- **03-05 03:14:59 UTC - 03-06 01:14:59 UTC** — ~0.92 zile de piata parcurse fara mecanism nou.
  Continut: choppy/consolidare cu volum ordinar (majoritatea 3.1k-28k), un declin moderat (117.32pt)
  — in banda deja documentata, sub recordurile 53,154/409-434pt.

- **03-06 01:14:59 UTC - 03-10 07:44:59 UTC** — ~4.27 zile de piata parcurse fara mecanism nou.
  Continut: choppy/consolidare cu volum ordinar (majoritatea 5k-40k, cateva varfuri monitorizate
  indeaproape dar sub recordul 53,154), un gap de weekend (48.25h, magnitudine neglijabila +0.45pt)
  si declinuri/recuperari moderate (max 143pt) — toate in banda deja documentata, sub recordurile
  53,154 volum / 409-434pt magnitudine.

- **03-10 07:44:59 UTC - 03-11 05:44:59 UTC** — ~0.92 zile de piata parcurse fara mecanism nou.
  Continut: choppy/consolidare cu volum ordinar (majoritatea 1.9k-38.3k), un candel cu volum
  elevat (38,302, sub recordul 53,154). Doar pauze de rollover zilnic ~4500s, ordinare.

- **03-11 05:44:59 UTC - 03-12 03:44:59 UTC** — ~0.92 zile de piata extrem de linistite, fara
  mecanism nou. Volum ordinar scazut (majoritatea 2.5k-19.3k), range-uri modeste (max 78.13pt). Doar
  pauze de rollover zilnic ~4500s, ordinare.

- **03-12 03:44:59 UTC - 03-11 17:44:59 UTC**: NOTA DE CORECTIE (append-only, textul anterior
  ramane neschimbat): checkpoint-ul anterior a etichetat gresit data calendaristica drept "2026-03-12
  03:44:59 UTC" pentru current_date 1773200699 — recalculul atent (Feb 2026 are 28 zile, deci Mar1 =
  ziua 126 fata de baza, Mar10 = ziua 135) arata ca eticheta corecta era **2026-03-11 03:44:59 UTC**.
  Eroarea a fost STRICT de etichetare calendaristica in narativ — pozitia reala de replay
  (current_date epoch 1773200699) a fost intotdeauna corecta si verificata direct prin
  `replay_status`, niciodata prin eticheta narativa. Nicio perioada nu a fost re-analizata sau sarita;
  NU necesita nicio actiune corectiva asupra portofoliului. De acum inainte, etichetele calendaristice
  vor folosi acest recalcul corectat. ~0.58 zile de piata parcurse intre cele doua checkpoint-uri, fara
  mecanism nou (choppy/consolidare cu volum ordinar, majoritatea 3.7k-14.7k, range-uri modeste sub
  48pt).

- **03-11 17:44:59 UTC - 03-12 08:44:59 UTC** — ~0.63 zile de piata parcurse fara mecanism nou.
  Continut: choppy/consolidare cu volum ordinar (majoritatea 3.8k-17.9k), range-uri modeste (max
  58.12pt). Doar pauze de rollover zilnic ~4500s, ordinare.

- **03-12 08:44:59 UTC - 03-12 23:44:59 UTC** — ~0.625 zile de piata parcurse fara mecanism nou.
  Continut: choppy/consolidare cu volum ordinar (majoritatea 1.5k-18.7k), un declin moderat (81.94pt,
  apoi inca 83.05pt) — in banda deja documentata, sub recordurile 53,154/409-434pt.

- **03-12 23:44:59 UTC - 03-13 13:44:59 UTC** — ~0.58 zile de piata parcurse fara mecanism nou.
  Continut: choppy/consolidare cu volum ordinar (majoritatea 5.2k-11.3k), range-uri modeste (max
  60.29pt). Doar pauze de rollover zilnic ~4500s, ordinare.

- **03-13 13:44:59 UTC - 03-16 11:44:59 UTC** — ~2.92 zile de piata parcurse fara mecanism nou.
  Continut: choppy/consolidare cu volum ordinar (majoritatea 2.3k-22k), un declin moderat (107.23pt),
  un gap de weekend (49.25h, magnitudine neglijabila -5.6pt) — toate in banda deja documentata, sub
  recordurile 53,154 volum / 409-434pt magnitudine.

- **03-16 11:44:59 UTC - 03-17 02:44:59 UTC** — ~0.63 zile de piata parcurse fara mecanism nou.
  Continut: choppy/consolidare cu volum ordinar (majoritatea 5.4k-16.4k), range-uri modeste (max
  63.91pt). Doar pauze de rollover zilnic ~4500s, ordinare.

- **03-17 02:44:59 UTC - 03-17 16:44:59 UTC** — ~0.58 zile de piata parcurse fara mecanism nou.
  Continut: choppy/consolidare cu volum ordinar (majoritatea 4.3k-19.7k), range-uri modeste (max
  57.87pt). Doar pauze de rollover zilnic ~4500s, ordinare.

- **03-17 16:44:59 UTC - 03-18 07:44:59 UTC** — ~0.625 zile de piata extrem de linistite, fara
  mecanism nou. Volum ordinar scazut (majoritatea 1.3k-7.1k), range-uri modeste (max 34.7pt). Doar
  pauze de rollover zilnic ~4500s, ordinare.

- **03-18 07:44:59 UTC - 03-19 01:14:59 UTC** — ~0.73 zile de piata parcurse fara mecanism nou.
  Continut: declin sustinut (175.5pt, volum max 33,743) urmat de consolidare/monitorizare atenta cu
  batch-uri mici (fara depasire de record), apoi inca un declin moderat (95.23pt) — toate in banda
  deja documentata, sub recordurile 53,154/409-434pt.

- **03-19 01:14:59 UTC - 03-19 14:29:59 UTC — INVESTIGATIE MAJORA, ADDENDUM D LA DC-0024**: declin
  sustinut multi-leg de la varf **5016.53** (2026-03-18 06:30:00 UTC) pana la minim **4502.365**
  (2026-03-19 13:00:00 UTC), ~30h30m — **514.165pt — NOU RECORD ALL-TIME de magnitudine (orice
  directie)**, depaseste Addendum B (434.285pt) cu +18.4%. Volum maxim in fereastra: 50,507 (candela
  ~2026-03-19 11:30 UTC), sub recordul 53,154 (-4.9%) — NU record nou de volum, doar de magnitudine.
  Verificat organic pe M5 pe candela minimului absolut (46,630 vol) — splitare 17,670/16,371/12,589
  (37.9% concentrare, sub pragul 42.7%). Varful (5016.53) a avut loc intr-o perioada deja verificata
  de consolidare linistita (volum 3.5k-7.5k), fara caracteristici anormale, NU necesita verificare M5
  separata. Test in 3 pasi: NU mecanism nou (acelasi mecanism declin multi-leg ca baza + A/B/C),
  addendum justificat (record decisiv +18.4%), NU DC nou. Addendum D la DC-0024 creat si inghetat.
  Recuperare partiala ulterioara (~147pt, ~29% din declin) pana la maxim ~4649.31, apoi fluctuatie
  4585-4650 — forma de rezolutie inca neclarificata la finalul batch-ului.

- **03-19 14:29:59 UTC - 03-20 05:29:59 UTC** — ~0.63 zile de piata parcurse fara mecanism nou.
  Continua recuperarea partiala post-Addendum D (DC-0024): range-uri moderate (max 111.02pt/101.82pt),
  volum in scadere/normalizare (majoritatea 2.7k-9.8k) — in banda deja documentata. Doar pauze de
  rollover zilnic ~4500s, ordinare.

- **03-20 05:29:59 UTC - 03-24 01:59:59 UTC** — ~3.86 zile de piata parcurse. Continut: choppy cu
  volum ordinar, un gap de weekend (49.25h, magnitudine modesta -25.24pt, confirmat exact pe bare
  OHLCV — nota: `current_date` intermediar din `replay_step` a aratat initial ~41.75h, discrepanta
  deja documentata ca artefact de citire, nu reala), apoi un declin+recuperare escalat (max ~437pt
  declin, ~394pt recuperare) cu volum ridicat repetat (pana la 50,907). O singura candela a atins
  **53,450 volum** — depaseste TEHNIC recordul anterior (53,154, DC-0023 Addendum C) dar cu doar
  +0.56%, ferm in banda "marginal/zgomot" stabilita anterior in acest replay (precedente: +0.06% si
  +2.2% ambele judecate ca zgomot, NU addendum) — NU addendum creat, doar notat aici. Nicio
  magnitudine sau alt volum nu a depasit recordurile all-time (514.165pt / 53,154 baseline). Fara
  mecanism nou.

- **03-24 01:59:59 UTC - 03-24 23:59:59 UTC** — ~0.92 zile de piata parcurse fara mecanism nou.
  Continut: choppy/consolidare cu volum ordinar (majoritatea 11k-44k, toate sub recordul 53,154),
  recuperare continuata (max 179.01pt) — in banda deja documentata. Doar pauze de rollover zilnic
  ~4500s, ordinare.

- **03-24 23:59:59 UTC - 03-25 13:59:59 UTC** — ~0.58 zile de piata parcurse fara mecanism nou.
  Continut: choppy/consolidare cu volum ordinar (majoritatea 5.7k-34.3k), range-uri modeste (max
  70.24pt). Doar pauze de rollover zilnic ~4500s, ordinare.

- **03-25 13:59:59 UTC - 03-26 04:59:59 UTC** — ~0.63 zile de piata parcurse fara mecanism nou.
  Continut: choppy/consolidare cu volum ordinar scazut (majoritatea 2k-14k), un declin moderat
  (92.85pt) — in banda deja documentata. Doar pauze de rollover zilnic ~4500s, ordinare.

- **03-26 04:59:59 UTC - 03-26 18:59:59 UTC** — ~0.58 zile de piata parcurse fara mecanism nou.
  Continut: declin continuat moderat (94.76pt, apoi 112.95pt), volum ordinar (majoritatea 13.9k-24k)
  — in banda deja documentata. Doar pauze de rollover zilnic ~4500s, ordinare.

- **03-26 18:59:59 UTC - 03-27 09:59:59 UTC** — ~0.63 zile de piata parcurse fara mecanism nou.
  Continut: choppy/consolidare cu volum ordinar scazut (majoritatea 7.6k-14k), range-uri modeste
  (max 89.25pt). Doar pauze de rollover zilnic ~4500s, ordinare.

- **03-27 09:59:59 UTC - 03-30 07:59:59 UTC** — ~2.92 zile de piata parcurse fara mecanism nou.
  Continut: choppy/consolidare cu volum ordinar (majoritatea 5k-29k), un gap de weekend (49.25h,
  magnitudine modesta +18.9pt, confirmat exact pe bare OHLCV) si declinuri/recuperari moderate (max
  151.05pt) — toate in banda deja documentata, sub recordurile 53,154/514.165pt.

- **03-30 07:59:59 UTC - 03-31 05:59:59 UTC** — ~0.92 zile de piata parcurse fara mecanism nou.
  Continut: choppy/consolidare cu volum ordinar (majoritatea 2.5k-32.4k), range-uri modeste (max
  136.6pt). Doar pauze de rollover zilnic ~4500s, ordinare.

- **03-31 05:59:59 UTC - 03-31 19:59:59 UTC** — ~0.58 zile de piata parcurse fara mecanism nou.
  Continut: choppy/consolidare cu volum ordinar (majoritatea 7.5k-21.6k), range-uri modeste (max
  117.83pt). Doar pauze de rollover zilnic ~4500s, ordinare.

- **03-31 19:59:59 UTC - 04-01 10:59:59 UTC** — ~0.63 zile de piata parcurse fara mecanism nou.
  Continut: choppy/consolidare cu volum ordinar scazut (majoritatea 5.3k-10.4k), range-uri modeste
  (max 80.62pt). Doar pauze de rollover zilnic ~4500s, ordinare.

## Urmatorul punct de pornire
Reia de la **2026-05-15 20:59:59 UTC pe M15, stepping manual** (current_date confirmat 1778878799,
verificat direct fata de baza 1761516000 = 2025-10-26 22:00:00 UTC: delta=17362799s, days=200
[200*86400=17280000], rest=82799s=22h59m59s, Apr1=ziua157, Apr30=ziua186 (Aprilie 30 zile), May1=
ziua187, deci ziua200=May14, +22h59m59s peste 22:00:00 = May15 20:59:59).
Autoplay ramane OPRIT; chart pe timeframe **15**. Foloseste batch-uri de 28-30 `replay_step` intre
verificari `data_get_ohlcv`; coboara pe 5M apoi 1M (NU 3M) doar la un fenomen ce trece filtrul v2.
ATENTIE OPERATIONALA: verifica `data_get_ohlcv` dupa batch-uri mai mici daca se suspecteaza un gap de
weekend/vacanta in fereastra, pentru a nu trece de un eveniment semnificativ inainte de verificare —
retine ca `current_date` din `replay_step` poate sari neuniform (inclusiv in doua salturi succesive)
in timpul skip-ului de weekend/rollover/vacanta, si ca la salturi mari OHLCV poate necesita 1-2 pasi
suplimentari pentru a "prinde din urma" fata de `current_date`; verificarea de gap se face STRICT pe
timestamp-urile bare din `data_get_ohlcv`, niciodata pe delta-ul brut intre doua `current_date`
succesive.
NOTA (de la ultimul checkpoint): Replay a avansat de la 2026-05-15 16:29:59 UTC la 2026-05-15
20:59:59 UTC (17 pasi manuali suplimentari) fara fenomene ce au trecut filtrul v2 — doar
volatilitate/volum normale de sesiune, sub toate pragurile de record (514.165pt magnitudine, 53,154
volum). Niciun gap de weekend in aceasta fereastra.
**SESIUNE OPRITA EXPLICIT LA CEREREA CEO (2026-07-25) — "Opreste-te aici, salveaza tot si intra in
stand by pana la urmatoarea comanda".** Bucla `/loop` a fost oprita (ScheduleWakeup stop:true).

**INCHIDERE OFICIALA ALPHA 1 (2026-07-25, comanda CEO ulterioara):** "Acum inchidem oficial Alpha 1.
Actualizeaza documentele de stare si fa commit. Nu implementa nimic nou." Replay TradingView oprit
explicit (`replay_stop` apelat si confirmat — chart revenit la realtime). Documentele de stare
(SESSION_STATE.md, DISCOVERY_CANDIDATE_INDEX.md, HANDOFF_LOG.md, OBSERVATION_REGISTRY.md) finalizate
si commise ca atare, fara nicio analiza/DC/addendum nou adaugat in cadrul acestei inchideri. Aceasta
este starea finala a diviziei Alpha 1 pana la o noua directiva CEO explicita de redeschidere.

Portofoliu final: **26 DC-uri**, **47 addenda** (DC-0013 are 13 A-M,
DC-0019 are 5 A-E, DC-0023 are 3 A-C, DC-0024 are 4 A-D, DC-0025 are 2 A-B), **18 intrari Observation
Registry**.
NOTA: fereastra 2025-11-28 ~08:15-11:15 UTC are calitate de date suspecta (vezi Observation
Registry intrarea 11) — deja verificata si notata, NU reanaliza. NOTA: fereastra 2026-01-29
15:27-15:29 UTC are calitate de date suspecta la nivel de tick (vezi Observation Registry intrarea
17) — declinul general e genuin dar minimul exact (5097.215) e nesuportat de volum, NU reanaliza.

## Stare portofoliu
26 Discovery Candidates: DC-0001 … DC-0026 (toate FROZEN, hash verificat, index + handoff la zi).
DC-0013 (creat 2026-07-23, prima aplicare a filtrului v2) — expansiune NY sustinuta pe 4 lumanari.
Are 5 addenda: A (2026-07-23, a doua instanta NY-session, 7 lumanari, aceeasi finalizare prin
consolidare), B (2026-07-24, a treia instanta NY-session, 6 lumanari, cea mai mare amplitudine din
familie (~71.6pt) dar la volum per-lumanara notabil sub pragul deja documentat — slabeste
caracterizarea "volum mare obligatoriu"), C (2026-07-24, a patra si a cincea instanta a semnaturii
"volum moderat 9-12k", cu dimensiune noua: clustering pe aceeasi fereastra orara 15:00-16:30 UTC in
2 zile calendaristice consecutive — hedge explicit, n=2, doar notat pentru comparatie viitoare),
D (2026-07-24, instanta din Londra timpurie 05:30-06:45 UTC, ~89.4pt — cea mai mare amplitudine din
toata familia la acel moment, prima instanta a acestei constructii in afara sesiunii NY, aceeasi
banda de volum 9-12k si aceeasi rezolutie prin consolidare, dar cu chop intern usor mai pronuntat)
E (2026-07-24, instanta din Asia timpurie 00:45-02:30 UTC pe 10-17, ~93.15pt declin — record de
amploare la acel moment, a treia sesiune distincta, dar cu o rezolutie noua: recuperare sustinuta
comparabila (~66.2pt) in loc de simpla consolidare; cross-referentiat cu DC-0014 din cauza suprapunerii
orare, dar secventa este inversata si amploarea mult mai mare), F (2026-07-24, instanta din
NY pre-open/early-NY 13:30-16:00 UTC pe 10-17, ~100.97pt declin — **noul record de amploare**,
prima instanta cu volum consistent peste banda 9-12k (11.9k-12.8k), a patra sesiune distincta, cu
o a treia rezolutie diferita: bounce partial (~49.4pt) urmat de chop extins, nici recuperare curata
nici consolidare simpla) G (2026-07-24, instanta din Londra mijlocul diminetii 07:30-09:00 UTC
pe 10-21, ~90.81pt declin — a treia cea mai mare amplitudine, a cincea sesiune distincta, cu
recuperare partiala (~30.35pt, o treime din declin) — a doua instanta a tiparului "recuperare
partiala" introdus de Addendum F) H (2026-07-24, cel mai semnificativ pana atunci: episod extins
11:45-18:15 UTC pe 10-21, declin record ~180.53pt (depaseste F cu peste 50%!) pe ~12 lumanari, apoi
~3.5h suplimentare de oscilatie extinsa intre mai multe leg-uri de recuperare partiala/declin
reinnoit, tot pe volum ridicat, inainte de stabilizare finala — episod total ~6.5h/~26 lumanari, de
peste 3 ori mai lung decat orice instanta anterioara; ridica intrebarea daca instantele foarte mari
sunt de fapt secvente de miscari mai mici, nu un eveniment atomic — n=1, hedge explicit) si I
(2026-07-24, declin ~120.06pt la ora 00:00 UTC pe 10-22, a doua cea mai mare amplitudine, comprimat
in doar 2 lumanari (cel mai rapid din familie la aceasta amploare), urmat de recuperare aproape
completa (~97% retragere, cea mai completa din familie) — coincide cu ora DC-0014) si J (2026-07-24,
instanta din NY pre-open/early-NY 13:30-15:15 UTC pe 10-27, ~55-62.5pt declin pe 7 lumanari — a doua
instanta (dupa F) unde noua dimensiune e banda de volum, nu amploarea/durata: 19.5k-26.9k sustinut,
aproape dublu fata de recordul anterior de volum (F, 11.9k-12.8k), apropiindu-se de scala NFP fara
sa o atinga; rezolutie prin recuperare partiala, ~15pt din declin) si K (2026-07-24, instanta din
aceeasi fereastra ca Addendum D (05:30 UTC) pe 10-28, care egaleaza practic recordul de amploare al
lui D (~89pt) dar pe ~14 lumanari (~3h30m) — de peste 2x mai lung decat D (~1h15m) — traversand
continuu si fereastra Addendum G (07:30+) ca o singura miscare; arata ca aceeasi amploare maxima se
poate atinge fie printr-un puseu scurt (D) fie printr-un declin lung/lent (K), la volum mediu ceva
mai jos).
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
sustinuta multi-minut identica cu DC-0008. Are 3 addenda: A (regimul de volum ridicat a durat de
fapt ~4h15m, nu 1h15m, cu deriva ascendenta usoara), B (a doua cea mai mare valoare de volum la
12:30 UTC, 25399 pe 09-11, dar rezolvata prin chop bidirectional extins, nu hold — amploarea singura
nu determina rezolutia) C (2026-07-24, instanta de luni ordinara — NU NFP — cu amploare mai mare
(~48.85pt) decat instanta NFP originala (~33.15pt) dar pe doar o treime din volum (9.9k-10.6k vs
30975) — decupleaza volumul de amploare la aceasta fereastra orara, rezolutie identica prin hold)
si D (2026-07-24, instanta de vineri ordinara — NU prima vineri/NFP — cu amploare noua record
(~73.75pt), depaseste Addendum C, pe volum 8.9k-10.9k, rezolvata prin chop bidirectional extins,
nu hold curat — a doua instanta non-NFP consecutiva cu record de amploare).
DC-0018 (creat 2026-07-23) — esec complet de breakout la varf nou (3674.695), pe cel mai mare volum
dintr-o singura lumanare din tot replay-ul (36798), urmat de declin sustinut pe 6 lumanari (~47.8pt,
~1h30m); constructie multi-minut sustinuta identica cu familia DC-0008/DC-0013/DC-0015 dar in
directie de coborare, precedata de un breakout esuat (distinct de toate DC-urile anterioare).
DC-0008 are 4 addenda (A-D), DC-0009 are 4 addenda (A-D), DC-0010 are 2 addenda (A-B), DC-0011 are 3
addenda (A-C), DC-0012 are 1 addendum (A), DC-0013 are 12 addenda (A-L), DC-0016 are 1 addendum (A),
DC-0017 are 4 addenda (A-D), DC-0019 are 3 addenda (A-C), DC-0021 are 1 addendum (A), DC-0023 are 3
addenda (A-C), DC-0024 are 2 addenda (A-B), DC-0025 are 2 addenda (A-B) — 43 addenda in total
(DC-0013 are 13, A-M), dovezi noi, fara schimbare de status/confidence (decizie ramane la Red
Team/Statistician).
Addendum B la DC-0019 (2026-07-24) — a 13-a instanta de gap de weekend, +24.44pt (al doilea cel
mai mare gap din replay, dupa recordul DC-0019/28.43pt), gap NU s-a umplut, pretul a extins in SUS
pana la 89.54pt peste close-ul pre-gap (depaseste extensia finala a DC-0019/~60.4pt), verificat
organic pe M5 (36.65% concentrare maxima, sub 42.7%). Prima instanta a mecanismului in directia
sus (DC-0019 si Addendum A erau ambele in jos) — slabeste ipoteza ca mecanismul e specific
directiei de coborare. Test in 3 pasi: NU mecanism nou (acelasi ca DC-0019, doar in sus), addendum
justificat (prima instanta in aceasta directie), NU record pe gap dar extensia totala e cea mai
mare din familie.
Addendum C la DC-0019 (2026-07-25) — a 14-a instanta de gap de weekend, **+53.46pt in sus, NOU
RECORD ALL-TIME de magnitudine gap (orice directie)**, depaseste recordul de baza DC-0019/28.425pt
cu ~88% si Addendum B/24.44pt cu peste 100%. Gap NU s-a retras deloc, pretul s-a extins pana la
94.62pt peste close-ul pre-gap (NOU RECORD de extensie pe directia sus, depaseste Addendum B/89.54pt),
apoi stabilizare 4653-4682 fara retragere completa. Verificat organic pe M5 (37.7% si 39.96%
concentrare maxima pe cele doua lumanari-cheie, sub 42.7%; prima lumanara de redeschidere are 60.1%
dar reflecta lichiditate subtire normala la instantul redeschiderii, nu artefact). Test in 3 pasi: NU
mecanism nou (acelasi ca DC-0019/Addendum B, doar magnitudine mai mare), addendum justificat (nou
record pe doua axe), NU DC nou.
Addendum L la DC-0013 (2026-07-24) — declin NY-open pe 12-29, 165.59pt (a doua cea mai mare
amploare din familie, dupa Addendum H/180.53), 4 candele M15 consecutive cu volum 34,453/29,809/
28,227/28,172 (varf 34,453 = a treia cea mai mare candela din tot replay-ul, depaseste marginal
Addendum C la DC-0011/34,319), toate verificate organic pe M5 (36.7-41.9% concentrare maxima, sub
42.7%). Initial logat incomplet ca Observation Registry intrarea 15 (observatie oprita la 81.3pt/
14:20 UTC); continuarea a relevat amploarea si volumul reale, motivand acest addendum. Test in 3
pasi: NU mecanism nou (familia DC-0013), addendum justificat (amploare/volum aproape-de-record pe
care intrarea Registry singura nu le capta), NU record absolut (sub Addendum H la amploare, sub
DC-0020/DC-0018 la volum) dar record marginal in cadrul propriei clasari (locul 3 la volum,
locul 2 la amploare in familie).
Addendum M la DC-0013 (2026-07-25) — declin NY-afternoon pe 15 candele (18:00-21:30 UTC pe 01-26,
114.935pt), lumanara-varf (38,755) fiind noul record all-time #3 de volum (depaseste DC-0020/37,204
si DC-0018/36,798), 4 din 15 candele peste 33,000 (cea mai mare densitate de candele
aproape-de-record dintr-un episod al familiei), verificat organic pe M5 (37.2% concentrare, sub
42.7%).
Addendum A la DC-0023 (2026-07-24) — acelasi mecanism (volum ridicat sustinut, candela aproape de
record) intr-o forma mult mai comprimata/intensa: 8 lumanari consecutive (15:15-17:00 UTC pe 12-12,
~1h45m) toate cu volum peste 17,000 (fata de podeaua 9,000 a episodului original de 8h), varf 35,082
(al doilea cel mai mare volum din tot replay-ul dupa DC-0020/37,204), verificat organic pe M5
(max 37.2% concentrare, sub 42.7%), amploare totala 96.28pt (sub recordurile DC-0023/100.005pt si
DC-0024/125.685pt). Test in 3 pasi: NU mecanism nou (acelasi ca DC-0023, doar comprimat), addendum
justificat (cifre aproape de recorduri dar sub ele), NU record pe nicio axa. Concluzie: Addendum,
NU DC nou.
Addendum C la DC-0011 (2026-07-24) — aceeasi forma "sweep reclamat, extinde la maxime noi" la
scara mult mai mare: episod 19:00-20:30 UTC pe 12-10, declin in doua faze (minim 4182.08), lumanara
de volum maxim (34,319 — al treilea cel mai mare din tot replay-ul dupa DC-0020/37,204 si
DC-0018/36,798) verificata organic pe M5 (38.5% concentrare maxima, sub pragul 42.7%), urmata de
revenire care depaseste nivelul pre-episod pana la un maxim nou (4238.785, ~56.7pt round-trip).
Test in 3 pasi: NU mecanism nou (mecanismul exact al DC-0011, la scara mai mare), addendum
justificat (potrivire foarte apropiata cu forma DC-0011), NU record (al treilea cel mai mare volum,
sub recordurile DC-0020/DC-0018; amploarea sub 100pt+). Concluzie: Addendum, NU DC nou.
Addendum B la DC-0010 (2026-07-24) — instanta mult mai extrema a mecanismului "ora linistita
sparta de expansiune de volum": lull aproape complet (volum M15 sub 150, ~2h15m) legat de un
catalizator calendaristic specific (Thanksgiving SUA, 2025-11-27), spart printr-un puseu de
viteza pe o singura lumanare M1 (11.0pt/60s, tipar identic DC-0001) urmat de whipsaw scurt si apoi
o revenire sustinuta care isi tine castigul ore intregi. Test in 3 pasi aplicat explicit: NU
mecanism nou (combina DC-0010 + DC-0001, deja documentate separat), addendum justificat de
dubiul real intre DC-0010/DC-0001, NU record (volum si amploare mult sub pragurile existente).
Concluzie: Addendum, NU DC nou.
DC-0020 (creat 2026-07-24, post-holdout — fereastra redeschisa) — ora 18:00 UTC pe 10-29: matura
minim proaspat, puseu esuat la maxim proaspat, apoi declin multi-leg bidirectional pe ~2h15m/8
lumanari la volum ridicat, incluzand **noul record absolut de volum din tot replay-ul (37204,
depaseste DC-0018/36798)**. Fara addenda inca.
DC-0019 (creat 2026-07-24, promovat din Observation Registry, post-holdout — fereastra redeschisa)
— gap de weekend record de amploare (~28.43pt, aproape 2x recordul anterior) care nu se umple, ci
se extinde sustinut ~9 lumanari (~2h) intr-un declin de ~50-56pt in sesiunea de redeschidere
Sunday/Asia timpurie, pe volum sub banda 9-12k a familiei DC-0013, urmat de recuperare partiala
(~30-33pt). Are 3 addenda: A (2026-07-24) — recuperarea initiala s-a dovedit nedurabila, declinul
s-a reluat ~2h15m suplimentare pana la un nou minim marginal (sub cel initial, noul record al
episodului, ~60.4pt/56.5pt de la close-ul pre-gap), urmat de o a doua recuperare partiala si
stabilizare — eveniment multi-leg (5+ faze), nu o singura miscare curata. B (2026-07-24) — prima
instanta a mecanismului in directia sus (+24.44pt, extensie 89.54pt). C (2026-07-25) — nou record
all-time de magnitudine gap (+53.46pt sus) si nou record de extensie sus (94.62pt), vezi detaliu mai
sus. D (2026-07-25) — nou record all-time de magnitudine gap (+90.02pt sus, depaseste C cu +68.4%)
si nou record de extensie (115.495pt, depaseste C cu +22.1%), verificat organic pe M5 (concentrare
50.6% dar raport volum/punct 462.4 — mult peste normal, opusul semnaturii de artefact). E (2026-07-25)
— prima instanta din acest replay a unei inchideri extinse de tip vacanta calendaristica (263,700s/
73h15m, fata de cadenta standard de 177,300s/49h15m), coincizand cu o data compatibila cu Vinerea
Mare 2026-04-03 (ipoteza plauzibila, hedged, neconfirmata explicit de vreun indicator/calendar); gap
in jos -38.495pt (NU record de magnitudine), acelasi mecanism de lichiditate subtire la redeschidere
(prima sub-lumanara M5 doar 101 volum) si esec de retracere completa (recuperare partiala la 4654.59,
sub close-ul pre-gap 4676.745), verificat organic pe M5 (sub-lumanara concentrata 373.8 vol/pt, mult
peste normal). Element nou: mecanismul de gap-la-redeschidere se confirma si sub o inchidere
calendaristic-extinsa, nu doar sub weekend-ul standard.
DC-0025 (creat 2026-07-25) — declin "waterfall" pe DOAR 2 lumanare M15 (30 min), 4620.39->4536.49
(~83.9pt), a doua lumanara fiind **noul record all-time de volum single-candle (39,353, depaseste
DC-0020/37,204 cu +5.8%)**, cu volum escaladand pe 4 sub-lumanare M5 consecutive pana la minimul
episodului (semnatura de climax organic, verificat pe M5, sub/aproape de pragul 42.7%), urmat de
recuperare ~75% (la 4599.2) apoi consolidare. Test in 3 pasi: mecanism nou (viteza de realizare cu un
ordin de marime mai mica decat minimul familiei DC-0013 de 4 lumanare), NU e doar addendum la
DC-0013/DC-0018/DC-0020 (structuri diferite), DC nou justificat. Are 1 addendum: A (2026-07-25) —
instanta si mai mare, pe 3 lumanare (45 min), ~99.09pt, lumanara centrala **nou record all-time de
volum (41,995, depaseste recordul propriu al DC-0025/39,353 cu +6.7%)**, recuperare ~85.6%, verificat
organic pe M5 (34.9%/38.1% concentrare pe cele doua lumanare mai relevante, prima lumanara 60.5% dar
cu volum substantial pe toate sub-lumanarele, nu artefact). B (2026-07-25) — reversal violent la
finalul unui rally record (vezi DC-0024 Addendum A), 2 lumanare (15:00-15:30 UTC pe 01-28), 75.915pt
in 30 min cu o sub-miscare de ~58pt in 5 min (M5), AMBELE lumanare depasesc recordul anterior (41,995):
42,339 si **42,808 (nou record all-time #1)**, verificat organic pe M5 (42.68%/37.9%, prima marginal
sub prag).
Observation Registry: 11 intrari (a 7-a: instanta 2025-08-26 00:00 UTC, promovata la DC-0014; a 8-a:
gap de weekend record 2025-10-24->10-26, promovata la DC-0019; a 9-a: puseu absorbtie 2025-11-06
20:45 UTC urmat de prabusire de volum in fereastra pre-rollover, nepromovata; a 10-a: declin in doua
faze 2025-11-10 13:00-14:45 UTC cu a doua faza aproape dubland volumul primei, nepromovata; a 11-a:
2025-11-28 ~08:15-11:15 UTC, semnatura de ARTEFACT DE DATE (nu observatie de piata) — tape rar
populat cu goluri neregulate, volume M1 1-38, pret sarind non-monoton intre niveluri distante pe
volum de 1-2 loturi; probabil legat de lichiditatea extrem de subtire de Black Friday; notat ca
avertisment de calitate a datelor pentru fereastra respectiva, nu ca fenomen de mecanism).
DC-0021 (creat 2026-07-24) — sesiunea NY-dimineata 14:00-16:45 UTC pe 11-06: declin sustinut pe 5
lumanari (volum in crestere graduala 13.9k->21.0k, minim nou 3978.245), urmat DIRECT, fara nicio
scadere de volum la tranzitie, de o faza de absorbtie pe 6 lumanari (banda ~3975-3991, deplasare
neta minima, volum ramas ridicat 16.1k-19.0k inca ~1h30m) inainte de normalizare finala. Combina
mecanismul DC-0013 (expansiune sustinuta) cu mecanismul DC-0012 (absorbtie fara deplasare) ca doua
faze secventiale ale unui singur eveniment continuu, fara decalaj de volum intre ele — element nou
fata de ambele familii documentate separat pana acum. Are 1 addendum: A (2026-07-24) — a doua
instanta a aceleiasi secvente, ziua urmatoare de tranzactionare, tot in fereastra NY-dimineata/
NY-open (14:30-16:15 UTC pe 11-07): declin de varf pe o singura lumanare (19,232, in loc de rampa
graduala), apoi absorbtie pe 4 lumanari la volum ramas ridicat (13.3k-15.6k), rezolvata insa printr-un
breakout bullish la un nou maxim local (opusul rezolutiei prin declin continuat din instanta
originala) — confirma mecanismul cu n=2, dar arata ca directia de rezolutie nu e fixata de mecanism.
DC-0022 (creat 2026-07-24) — sesiune NY-dupa-amiaza 14:30-19:45 UTC pe 11-12: expansiune sustinuta
pe **16 lumanari (exact 4 ore, record nou de durata**, depaseste DC-0015 la 11 lumanari/~2h45m),
amploare **86.75pt (record nou de amploare pentru familie**, depaseste DC-0016), volum ramas ridicat
15k-23k pe tot parcursul (fara decadere pana la reversal), verificat organic pe M5 pe cele doua
lumanari cu volum maxim (36.5% si 37.8% concentrare maxima, sub pragul 42.7%), urmat de un platou
scurt de 2 lumanari si apoi reversal (~17pt declin) cu volum in sfarsit in scadere. Fara addenda
inca.
DC-0023 (creat 2026-07-24) — imediat dupa DC-0022: episod choppy/multi-leg pe **8 ore continue
(13:00-21:00 UTC, 32 lumanari), volum ramas ridicat aproape tot timpul (9k-22.7k)**, amploare totala
**100.005pt** (record nou, depaseste DC-0022), continand o lumanare cu volum 28,254 — **al treilea
cel mai mare volum dintr-o singura lumanare din tot replay-ul** (dupa DC-0020/37204 si
DC-0018/36798), verificat organic pe M5 (42.2% concentrare maxima, chiar sub pragul 42.7%).
Secventa DC-0022 (expansiune curata record) urmata imediat de DC-0023 (choppy record) ridica
intrebarea daca cele doua sunt legate cauzal la scara mare (similar cu DC-0021, dar mult mai
amplu) — n=1, doar notat pentru comparatie viitoare. Are 2 addenda: A (2026-07-24) — instanta
comprimata/intensa (8 lumanari, 1h45m, prag 17k), varf 35,082 (locul 2 all-time la momentul respectiv).
B (2026-07-25) — instanta si mai intensa (19 lumanari, ~4.5h, prag 23k), varf **48,401 (nou record
all-time #1)**, verificat organic pe M5 (33.9-35.9% concentrare). C (2026-07-25) — episodul continua
si escaladeaza DECISIV (14:30-18:35 UTC pe 01-30), varf **53,154 (nou record all-time #1, +9.8% peste
Addendum B)**, 4 candele peste 48,401, verificat organic pe M5 (33.6-36.7%). Acelasi episod contine
si recordul de amploare (vezi DC-0024 Addendum B).
DC-0024 (creat 2026-07-24) — declin sustinut Londra-dimineata 11:45-16:30 UTC (19 lumanari,
4h45m): amploare **125.685pt (record nou absolut de magnitudine**, depaseste DC-0022/86.75pt si
DC-0023/100.005pt), volum ridicat aproape tot timpul (9.4k-19.9k), lumanara de varf a volumului
(24,655 — al patrulea cel mai mare din tot replay-ul) coincide cu minimul, verificata organic pe M5
(41.1%, sub pragul 42.7%). O a doua verificare (lumanara minimului secundar, 4014-14:15 UTC) a aratat
48.1% concentrare — peste pragul standard, notat transparent ca punct de atentie (posibil moment de
tip stop-cascade la minim, nu semnatura clara de artefact caci toate cele 3 sub-lumanari M5 au avut
volum si miscare reale). Urmat de recuperare partiala (~76pt, neincheiata la momentul inghetarii).
Are 2 addenda: A (2026-07-25) — rally sustinut (~8h, ~32 lumanari) 23:30 UTC 01-27 - 08:30 UTC
01-28, **noul record all-time de amploare (154.665pt, depaseste recordul propriu 125.685pt cu +23%,
prima data in SUS)**, rezolvat printr-un reversal violent (vezi DC-0025 Addendum B) in loc de
recuperare graduala. B (2026-07-25) — declin choppy-sustinut 14:30-18:35 UTC pe 01-30 (~4h05m),
**NOU RECORD ALL-TIME ABSOLUT de amploare (434.285pt, depaseste Addendum A cu +181%)**, verificat
organic pe M5 pe 4 candele-record (33.6-36.7% concentrare); minimul absolut are raport volum/punct
~158 — mult peste normal, opusul semnaturii de artefact de la declinul 01-29 (Registry 17), NU
artefact. Recuperare ~58%. Acelasi episod detine si recordul de volum (vezi DC-0023 Addendum C).
DC-0026 (creat 2026-07-25) — puseu parabolic extrem de rapid la redeschiderea de dupa rollover-ul
zilnic (fereastra subtire de lichiditate): +100.08pt in ~6 min, apoi reversal -77.1pt in ~4-5 min
(round-trip complet in ~10-11 min) — **cea mai rapida viteza punct/minut din tot replay-ul** (~2x
recordul anterior). Verificat organic pe M1 (nu doar M5, prima data in acest replay). Fara record de
volum (axa noua e viteza). Rezolutie: chop volatil continuat, nu stabilizare curata. Test in 3 pasi:
mecanism nou (nicio combinatie similara "puseu-apoi-reversal complet la redeschiderea rollover-ului
zilnic" documentata), NU e doar addendum la DC-0001/DC-0010/DC-0025 (forme diferite), NU doar
record. Fara addenda inca.
Fara datorii administrative deschise.
