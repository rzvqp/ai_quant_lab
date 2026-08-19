# STATISTICIAN — RĂSPUNS LA CONTROLUL SEMANTIC ÎNAINTE DE IMPLEMENTARE

**Document ID:** STAT-RANGE-V4-PRE-IMPL-CHALLENGE-v1.0 · **Data:** 2026-08-19
**Status:** `RANGE_V4_PRE_IMPLEMENTATION_SEMANTIC_CHALLENGE_READY_FOR_CEO_DECISION`
**VE rămâne în HOLD.** Nu am modificat specificația. Corecțiile necesare sunt DECLARATE la §15, separat de răspunsuri.

---

# RĂSPUNSUL LA ÎNTREBAREA DECISIVĂ (§14), PUS PRIMUL

## **NU.**

**VE nu poate implementa prototipul exclusiv din `v4.1` + deciziile CEO fără să inventeze.** Blocantele sunt de două feluri, iar cele semantice sunt mai grave decât cele numerice fiindcă **sunt găuri în contractul meu**, descoperite exact pentru că m-ai pus să demonstrez pe exemple în loc să citez.

```
BLOCANTE SEMANTICE — găuri în contract, nu parametri lipsă
S1  NU există regulă care să spună CE NIVEL primește o structură nou detectată.
    v4.1 zice „MESO = canalul sau sub-range-ul PRINCIPAL". „Principal" nu e definit nicăieri.
    Dacă la aceeași bară se califică două structuri, contractul nu spune care e MESO și care MICRO.
S2  NU există regulă de FORMARE A FRONTIERELOR sub noua ancoră. v4.1 listează
    `boundary_lower`/`boundary_upper` ca CÂMPURI, dar nu spune cum se CALCULEAZĂ.
    V2 folosea mediana swing-urilor pe 512 bare; V3 pe segment; V4 spune doar
    „fereastra ancorei <= durata obiectului" — o constrângere, nu un estimator.
S3  NU există rol pentru un episod TREND închis. D4 acoperă BALANCE → ACCUMULATION/DISTRIBUTION.
    Un TREND care se încheie primește ce `role`? Contractul tace.
S4  COLIZIUNE DE NUME pe `K_struct`. În v4.1 `K_struct` e o FEREASTRĂ ÎN BARE pentru ruperea
    opusă după sweep. Mandatul spune `K_struct=2` în contextul „al doilea swing exterior",
    adică un NUMĂR DE SWING-URI. Cele două citiri produc mașini diferite.

BLOCANTE NUMERICE — valori fără decizie și fără derivare
N1  d_macro     N2  d_meso     N3  d_micro     N4  K_reentry
N5  w_atr (de rederivat sub ancora nouă)        N6  tol_touch
N7  swing_k     N8  atr_window   (moștenite 2 și 14, NERATIFICATE sub V4)
```

**CEO a decis `N_accept = 3` și `K_struct = 2`. Rămân opt valori și patru reguli.** Conform §3 al mandatului tău — *„dacă VE ar trebui să inventeze chiar și un singur parametru semantic, declară specificația insuficientă și oprește autorizarea"* — **opresc autorizarea.**

Restul documentului arată, pe date reale, **unde anume** se rupe fiecare lucru.

---

# 1 — RANGE MACRO CU CANAL INTERN: `BLIND-019`

**Etichetat de CEO** (fereastră de 480 bare):

```
nivel 1   0-480   RANGE                       ← un singur segment pe toată fereastra
nivel 2   0- 48   CHANNEL_UP
          48-180  RANGE
         180-280  CHANNEL_DOWN
         280-345  CHANNEL_UP
         345-455  CHANNEL_DOWN
         468-480  RANGE
```

**Ce ar produce contractul, la bara 20 (în interiorul primului canal):**

| nivel | obiect | id | părinte | limite | stare |
|---|---|---|---|---|---|
| MACRO | `RANGE_MACRO` | 1 | NULL | 1254-1273 (din etichetă) | `RANGE_CONFIRMED` |
| MESO | `MESO_CHANNEL_UP` | 2 | **1** | ale canalului | activ |
| MICRO | — | — | — | — | **null** |

**Da, aceeași bară aparține tuturor nivelurilor ocupate.** Ieșirea la bara 20 e tripletul `(1, 2, null)`.

**Regula care împiedică dispariția macro-ului** e `I2` plus precedența de la §5.5: *un nivel inferior NU poate schimba unul superior; singura cale în sus e promovarea prin P1-P4*. Canalul de la bara 0 nu satisface `P1` — prețul nu părăsește limita macro — deci `PROMOTION_REFUSED_PRECONDITION_P1`, iar macro-ul rămâne `RANGE_CONFIRMED`.

> **Aici se vede exact ce a stricat V3: acolo `IS_CHANNEL` era motiv de RESPINGERE, deci canalul de la bara 0 ucidea range-ul. În V4 e o etichetă de nivel MESO și nu atinge macro-ul. Asta e reparația, și e verificabilă pe această fereastră.**

**Dar `S1` lovește deja aici:** de ce `CHANNEL_UP 0-48` e MESO și nu MICRO? Contractul nu spune. CEO l-a pus pe nivelul 2, dar CEO nu a etichetat niciodată un nivel 3 — deci nu am nicio dovadă care să distingă cele două.

---

# 2 — ÎNCEPUTUL RANGE-ULUI

```
candidat      la bara i, dacă există >= n_touch swing-uri confirmate pe FIECARE latură
              în fereastra de ancoră. Starea devine RANGE_FORMING.
start_ts      = ts-ul CELUI MAI VECHI swing folosit la construirea limitelor — deci
              RETROSPECTIV prin construcție. Nicio decizie nu se ia la start_ts.
confirm_ts    = bara la care toate condițiile sunt simultan adevărate: swing-uri suficiente
              ȘI durata >= d_macro ȘI zone disjuncte ȘI ATR disponibil.
              Starea devine RANGE_CONFIRMED. ACȚIONABIL abia aici.
înainte       sistemul vede RANGE_FORMING cu reason `ESTABLISHING_FEW_SWINGS` sau
              `TOO_SHORT_MACRO`, plus `not_yet_available` care spune ce lipsește.
```

## De ce nu repetă defectele

```
V2  poarta de durată nu putea EȘUA, fiindcă măsura vârsta celui mai vechi swing REȚINUT
    într-o fereastră de 512, iar pragul era 96. `TOO_SHORT` s-a emis de ZERO ori.
V3  poarta nu putea REUȘI, fiindcă ancora era legată de segment (segmente de max 80 bare)
    dar pragul rămăsese 96. `RANGE_CONFIRMED` s-a atins de ZERO ori în 13.824 bare.
V4  durata se măsoară de la `start_ts` AL OBIECTULUI, iar `C4` cere ca fereastra ancorei
    să nu depășească durata obiectului. Cele două nu mai pot diverge.
```

**Condiția care poate ȘI să treacă ȘI să eșueze — dovada pe corpus:** duratele segmentelor RANGE etichetate se întind pe `[4, 480]`, mediană 55. **Orice prag din intervalul deschis `(4, 480)` are, prin construcție, exemple de ambele feluri în corpus.** Asta e ceea ce nici V2 nici V3 nu puteau produce.

> **★ Dar exact aici e `N1`: nu pot numi pragul. Iar fără el, `T1` nu se poate rula, deci nici poarta nu se poate verifica înainte de implementare.**

---

# 3 — DURATA: CE POATE ȘI CE NU POATE VE

```
POATE IMPLEMENTA ACUM (fără să inventeze nimic)
   mașina de stări · cele trei niveluri cu depth enumerare închisă · invarianții I1-I5 ·
   schema obiectelor · schema snapshot cu refuz fail-closed · reason codes ·
   evenimentele ortogonale · precedența · interdicția rolurilor vii ·
   parametrii ca argumente OBLIGATORII FĂRĂ DEFAULT — exact cum a făcut deja la 0.4.x

NU POATE
   nu poate RULA · nu poate produce raportul de nevacuitate T1-T6 ·
   nu poate măsura nimic pe corpus · nu poate fi comparat cu etichetele

OBLIGATORII ÎNAINTE DE PRIMA RULARE
   d_macro · d_meso · d_micro · K_reentry · w_atr · tol_touch · swing_k · atr_window
   (N_accept = 3 și K_struct = 2 sunt decise, sub rezerva coliziunii de nume S4)

CUM SE ALEG FĂRĂ OPTIMIZARE DUPĂ REZULTAT
   prin protocolul din §6 al contractului: măsurătoare + regulă declarată ÎNAINTE,
   pe date care nu sunt și sursa validării. Nu prin căutare care maximizează potrivirea.

TREBUIE VE SĂ INVENTEZE VREUN NUMĂR?   DA, opt.  ⇒ SPECIFICAȚIE INSUFICIENTĂ.
```

---

# 4 — SWEEP VERSUS BREAKOUT, CU `N_accept = 3`

```
bara b0    prima închidere ÎN AFARA limitei
           → BOUNDARY_EXCURSION, closes_outside = 1
           → not_yet_available = SWEEP_VS_BREAKOUT
           ★ NU se emite nicio clasificare. Ambele ipoteze sunt deschise.

bara b1    a doua închidere în afară → closes_outside = 2, încă SWEEP_VS_BREAKOUT

bara b2    a treia închidere în afară → closes_outside = 3 = N_accept
           → BREAKOUT_ACCEPTED. confirm_ts = b2. Macro-ul se ÎNCHIDE, end_ts = b2.

reintrare ÎNAINTE de a treia închidere (la b0+j, j <= K_reentry, closes_outside < 3)
           → REENTRY_CONFIRMED la bara reintrării → SWEEP_CONFIRMED
           → macro-ul RĂMÂNE deschis. confirm_ts al sweep-ului = bara REINTRĂRII.

reintrare DUPĂ a treia închidere
           → prea târziu. Episodul e deja închis prin BREAKOUT_ACCEPTED.
           → reintrarea deschide un episod NOU, cu predecessor_id = episodul închis.
           NU învie episodul vechi.

BREAKOUT_PENDING   când fereastra K_reentry a expirat FĂRĂ reintrare, dar closes_outside < 3.
                   Ambele ipoteze rămân deschise; not_yet_available persistă.
```

## Poate un breakout acceptat să devină ulterior failed breakout?

**Nu, și asta e intenționat.**

```
`BREAKOUT_ACCEPTED` e o afirmație despre ce s-a ÎNTÂMPLAT până la b2, iar la b2 era adevărată.
Dacă prețul revine ulterior, asta e un EVENIMENT NOU asupra episodului NOU, nu o revizuire a celui vechi.
Episodul închis își păstrează end_ts, limitele și reason code-ul.
Ce se poate întâmpla: episodul succesor primește el `FAILED_BREAKOUT_*` ca eveniment,
iar legătura se citește prin predecessor_id.
A rescrie episodul vechi ar fi exact falsificarea de istoric interzisă la §3 din contract.
```

> **★ BLOCANT `N4` demonstrat concret: tot ce e mai sus depinde de `K_reentry`, care NU e decis. Fără el nu pot spune dacă o reintrare la bara b0+5 e „la timp" sau „prea târziu". Mașina e completă, ceasul îi lipsește.**

---

# 5 — PROMOVAREA LA TREND MACRO

**Întâi coliziunea de nume, fiindcă schimbă răspunsul:**

```
în v4.1  `K_struct` = FEREASTRĂ ÎN BARE pentru ruperea opusă după un sweep
în mandat `K_struct = 2` apare în contextul „al doilea swing exterior" = NUMĂR DE SWING-URI
```

**Răspund sub citirea „număr de swing-uri exterioare = 2", care coincide cu `n_continuation = 1 pereche` din contract. Dacă intenția era fereastra în bare, răspunsul de mai jos NU se aplică și cer decizia explicit (§15, C4).**

## Exemplu BULLISH — `BLIND-022`, structura etichetată

```
macro RANGE 0-260, limite ~1794-1811. La bara 260 prețul iese în sus.

b_break      prima închidere peste 1811                → BOUNDARY_EXCURSION
b_break+2    a treia închidere în afară (N_accept=3)   → BREAKOUT_ACCEPTED
                                                        macro 0-260 se ÎNCHIDE, end_ts scris
                                                        ★ ÎNCĂ NU e trend. P3 nesatisfăcută.
primul swing high confirmat peste maximul ruperii        → P3 parțial: 1 din 2
   ★ un singur extrem NU promovează. E un impuls, nu o structură.
     Un impuls se poate întoarce integral; o structură are nevoie de un al doilea punct
     care să arate că nivelul nou e SUSȚINUT.
al doilea extrem: swing low confirmat PESTE 1811         → P3 SATISFĂCUTĂ
   confirm_ts(promovare) = bara la care se confirmă AL DOILEA extrem
   → macro NOU: TREND_UP, predecessor_id = episodul RANGE închis
```

## Exemplu BEARISH — `BLIND-023` (secvență etichetată `STEPWISE_BEARISH_RANGE_BREAK`)

```
macro RANGE 0-16 → BREAKOUT_DOWN acceptat la bara ~20 → macro închis
lower low confirmat sub minimul ruperii                  → 1 din 2
lower high confirmat SUB limita inferioară a range-ului  → 2 din 2 → TREND_DOWN
```

## Ce se întâmplă cu range-ul anterior, și de ce nu există lookahead

```
range-ul anterior: ÎNCHIS, cu end_ts = bara acceptării, PĂSTRAT INTEGRAL. Nereclasificat.
lookahead: NU există, fiindcă fiecare confirmare se face pe un swing DEJA CONFIRMAT la bara i.
   Swing-ul se confirmă cu k bare la dreapta; `confirm_ts` e bara confirmării, nu bara extremului.
   Între extrem și confirmare, starea rămâne cea veche, cu `not_yet_available`.
```

---

# 6 — RANGE TERMINAT, PĂSTRAT ÎN ISTORIC

**Înainte de breakout (bara 200 din `BLIND-022`):**

```
structure_id 1 · depth 0 · parent NULL · state RANGE_CONFIRMED
start_ts b0 · confirm_ts b_conf · end_ts NULL
boundary 1794-1811 · reason_codes [OK_RANGE_MACRO] · role NULL · role_known_ts NULL
```

**După breakout acceptat (bara b2):**

```
structure_id 1        ← ACELAȘI
depth 0 · parent NULL ← neschimbate
start_ts b0           ← NESCHIMBAT
confirm_ts b_conf     ← NESCHIMBAT
end_ts b2             ← SCRIS
boundary 1794-1811    ← ORIGINALE, nemutate
state EPISODE_CLOSED
reason_codes [BREAKOUT_ACCEPTED_UP]
succesor: structure_id 2, predecessor_id = 1
role NULL până la confirmarea continuării; apoi ACCUMULATION_CONFIRMED + role_known_ts
```

**Dovada că nu e șters sau reclasificat:** `structure_id`, `start_ts`, `confirm_ts` și limitele sunt **imutabile prin contract**; singurele câmpuri care se scriu la închidere sunt `end_ts`, `state` și `reason_codes`. Tranziția `EPISODE_CLOSED → orice stare vie` e în lista INTERZISE (§5.4).

---

# 7 — TREI NIVELURI IMBRICATE

> **★ Nu pot arăta un exemplu real cu trei niveluri, fiindcă NU EXISTĂ NICIUNUL. Etichetele CEO au exact DOUĂ niveluri (`segments` și `internal_structures`), iar al doilea apare în 8 din 48 de ferestre. Un al treilea nivel nu a fost etichetat niciodată.**

Cel mai adânc caz real e `BLIND-012`: macro `RANGE 0-96`, intern `RANGE 0-52`. Sub contract ar fi `(MACRO RANGE, MESO_SUBRANGE, null)` — **două niveluri ocupate, al treilea gol.**

## Regula normativă pentru un al patrulea nivel aparent — o singură alegere

```
Structura care ar cere depth 3 se REFUZĂ, cu cod DEPTH_LIMIT_EXCEEDED, iar bara rămâne
descrisă de tripletul existent. NU se absoarbe în MICRO (ar falsifica limitele) și NU se
convertește în eveniment (evenimentele n-au limite, deci ar pierde informația).
```

**Motivul e testabilitatea: absorbția ar face imposibil de spus dacă MICRO e o structură reală sau un coș de gunoi.**

---

# 8 — `ACCUMULATION` FĂRĂ PRIVIRE ÎN VIITOR, PE HBL-20

```
în timpul range-ului (barele 0-51)
   MACRO = RANGE_CONFIRMED, MESO = MESO_BALANCE, role = NULL
   ★ NU spune „acumulare". Spune BALANCE.

la sweep down (bara 52, low 3330,25 sub 3333,06)
   BOUNDARY_EXCURSION, closes_outside creşte
   not_yet_available = SWEEP_VS_BREAKOUT
   ★ La bara 52 sistemul NU ştie dacă e sweep sau breakout. Nici omul nu ştia.

la reintrare (bara 56, close 3334,94 înapoi înăuntru)
   REENTRY_CONFIRMED → SWEEP_CONFIRMED. Macro-ul SUPRAVIEŢUIEŞTE.
   role încă NULL — direcţia ieşirii nu e cunoscută.

la ruperea bullish de structură (bara 63, close 3346,99 peste maximul acumulării)
   STRUCTURE_BREAK_UP. Începe verificarea P3.

ACCUMULATION_CONFIRMED
   apare la confirmarea CELUI DE-AL DOILEA extrem exterior (P3)
   role_known_ts = ACEA bară, undeva după 63. NICIODATĂ 0, niciodată 52, niciodată 63.

ce rămâne adevărat în istoric
   episodul BALANCE păstrează start_ts, confirm_ts, limitele şi not_yet_available de atunci.
   Rolul se ADAUGĂ, nu rescrie.
```

> **Dovada că live-ul nu putea şti: între barele 52 şi 56 ambele ipoteze erau deschise, iar contractul emite explicit `SWEEP_VS_BREAKOUT`. Un sistem care ar fi spus „acumulare" la bara 52 ar fi ghicit că preţul revine — exact previziunea pe care D4 o interzice.**

---

# 9 — RANGE ÎN INTERIORUL UNUI TREND MAI MARE

**Da, modelul o poate reprezenta:** `TREND_UP` la depth 0, `MESO_SUBRANGE` la depth 1, `MICRO_CHANNEL_*` la depth 2. Nimic din contract nu cere ca depth 0 să fie range.

**Dar corpusul nu o poate valida.** Șase ferestre poartă în câmpul `macro` un text de tipul `STEPWISE_TREND_UP_WITH_INTERNAL_RANGES` — **text liber, fără limite, fără indici de bară.** În aceleași ferestre, segmentele de pe nivelul 1 sunt o SECVENȚĂ de regimuri (`BLIND-034`: `CHANNEL_UP`, `CHANNEL_DOWN`, `CHANNEL_DOWN`, `TRANSITION`, `RANGE`), nu un macro cu copii.

> **★ Ce se pierde: exact ierarhia. Etichetele spun că trendul există, dar nu spun UNDE începe și unde se termină, deci nu pot servi ca adevăr pentru un obiect de nivel 0. Asta e informația lipsă, și e aceeași care blochează §11.**

---

# 10 — FRONTIERELE

> **★ AICI E GAURA `S2`, cea mai gravă. `v4.1` listează `boundary_lower` și `boundary_upper` ca CÂMPURI OBLIGATORII, dar NU SPUNE CUM SE CALCULEAZĂ. Constrângerea „fereastra ancorei <= durata obiectului" limitează DE UNDE se iau datele, nu CE se face cu ele.**

Ce e specificat, și ce nu:

```
SPECIFICAT     fereastra ancorei <= durata obiectului (C4)
               zone disjuncte, altfel ZONES_DEGENERATE fail-closed
               fitilul care intersectează zona E atingere; neintersecția NU e
               atingerile NU invalidează — sunt evenimentul care CONSTITUIE range-ul
NESPECIFICAT   ★ estimatorul limitei: mediană a swing-urilor? extremă? altceva?
               ★ dacă limitele se ÎNGHEAȚĂ la confirm_ts sau se actualizează
               ★ ce se întâmplă cu un extrem NOU în interiorul episodului
               ★ lățimea benzii (tol_touch) — parametru N6, nedecis
```

**De ce contează:** V1 a murit fiindcă limita era un maxim pe o mulțime CRESCĂTOARE, deci creșterea ferestrei ridica limita și invalida retroactiv atingerile deja numărate. **Dacă V4 nu spune dacă limitele îngheață, VE poate reintroduce exact acel defect fără să încalce nimic scris.**

Exemplu unde condiția de disjuncție TRECE: `BLIND-019`, macro 1254-1273 — separare ~19 puncte, zone clar disjuncte la orice lățime rezonabilă. Exemplu unde EȘUEAZĂ: la V3, garda `ZONES_DEGENERATE` s-a declanșat de 24 de ori pe corpus — deci poarta e demonstrat nevacuă, chiar dacă rar activă.

---

# 11 — CELE 114 SEGMENTE: NU POT FI ÎMPĂRȚITE

```
ce există în etichete
   nivel 1  `segments`             282 segmente, din care 114 RANGE
   nivel 2  `internal_structures`   34 segmente, din care  12 RANGE
   nivel 3  NU EXISTĂ în schemă
   nivelul 2 apare în 8 din 48 de ferestre
```

> **★ NU pot clasifica cele 114 în MACRO / MESO / MICRO și NU inventez împărțirea.**

**Informația care lipsește, exact:**

```
1  un câmp `depth` sau `level` per segment. În 40 de ferestre din 48 TOTUL e pe nivelul 1,
   fără nicio indicație dacă un segment e macro sau meso.
2  în ferestrele cu secvențe (BLIND-034: CHANNEL_UP → CHANNEL_DOWN → TRANSITION → RANGE),
   nivelul 1 e o SUCCESIUNE de regimuri. Nu se poate ști dacă `RANGE 230-480` e macro,
   sau meso în interiorul unui trend mai mare pe care eticheta îl afirmă doar în text liber.
3  niciun exemplu de nivel 3, deci MICRO nu are nici măcar un caz pozitiv.
```

**Ce se poate spune fără invenție:** cele 12 RANGE de pe nivelul 2 sunt sigur SUB un obiect de nivel 1, deci sunt cel puțin MESO. Cele 114 de pe nivelul 1 sunt **fie macro, fie meso, nedecidabil din etichete**.

---

# 12 — TESTUL DE NEVACUITATE: CE SE POATE ȘI CE NU

| poartă | exemplu POZITIV | exemplu NEGATIV | unități eligibile | observabil în output |
|---|---|---|---|---|
| confirmarea range | `BLIND-019` RANGE 0-480 | `BLIND-002` CHANNEL_DOWN 0-49 | 282 segmente nivel 1 | `state = RANGE_CONFIRMED` |
| durata | segmente de 480 bare | segmente de 4 bare | 114 RANGE, durate `[4,480]` | `TOO_SHORT_MACRO` |
| frontiere | `BLIND-019`, separare ~19 | `ZONES_DEGENERATE` s-a declanșat de 24 ori la V3 | toate barele cu episod | `ZONES_DEGENERATE` |
| sweep | 66 sweep-uri etichetate | 58 breakout-uri etichetate | 66 vs 58 | `SWEEP_CONFIRMED` |
| breakout acceptat | `BLIND-023` BREAKOUT_DOWN `ACCEPTED_VERY_STRONG` | 11 `FAILED_BREAKOUT` etichetate | 58 | `BREAKOUT_ACCEPTED` |
| promovare la trend | 6 ferestre cu macro TREND în text | 42 fără | **6 vs 42, dar fără limite** | `TREND_UP/DOWN` |
| nivel MACRO | 282 segmente | — | 282 | depth 0 nenul |
| nivel MESO | 34 segmente, 8 ferestre | 40 ferestre fără | 34 | depth 1 nenul |
| **nivel MICRO** | **NICIUNUL** | — | **0** | **imposibil de testat** |

> **★ `T6` EȘUEAZĂ ÎNAINTE DE IMPLEMENTARE pentru MICRO: zero exemple pozitive în corpus. Conform propriei mele reguli — *o condiție fără exemplu pozitiv și negativ nu intră în mandatul VE* — nivelul MICRO nu poate intra. Rămâne specificat, dar netestabil, iar asta trebuie spus înainte, nu descoperit după.**

**Și promovarea la trend e la limită:** cele 6 exemple sunt text liber fără limite de bară, deci nu pot servi ca adevăr temporal. Testabilă ca *existență*, netestabilă ca *moment*.

---

# 13 — CRITERIUL DE SUCCES, PREÎNREGISTRAT

```
CE MĂSURĂM        recall + precision pe segmente nivel 1 · recall separat pe nivel 2 ·
                  IoU · eroarea limitelor (mediană şi p90, în bare) ·
                  stratificat pe 96/288/480 şi pe B1-B4 · matrice RANGE/CHANNEL/TREND ·
                  precizie temporală sweep/breakout · raportul n_pass/n_fail pentru FIECARE poartă

ÎMBUNĂTĂŢIRE REALĂ   recall pe segmente RANGE nivel 1 STRICT > 0 cu IoU median > 0,
                     ŞI fiecare poartă din §12 demonstrat nevacuă.
                     Pragul de la zero e scăzut deliberat: V3 a dat ZERO. Prima întrebare
                     nu e „cât de bine", ci „funcţionează deloc".

OPRIRE OBLIGATORIE   orice poartă cu n_pass = 0 sau n_fail = 0 · orice nivel gol ·
                     orice lookahead detectat · snapshot/restart nereproductibil bit-identic

ÎNGHEŢARE PERMISĂ    toate porţile nevacue ŞI zero lookahead ŞI snapshot bit-identic
                     ŞI parametrii aleşi prin protocolul preînregistrat, nu prin căutare

CUM EVITĂM ALEGEREA CELEI MAI BUNE VARIANTE
   se rulează O SINGURĂ configuraţie, fixată înainte prin protocol. Dacă se rulează mai multe,
   TOATE se raportează, iar alegerea NU se face după rezultat. `config_id` se înregistrează la
   fiecare rulare, iar poarta `POST_FREEZE_CONFIG_DRIFT` marchează orice abatere.

DOAR INFORMATIVE   sensibilitatea la d_macro, la w_atr, la K_reentry — se raportează descriptiv,
                   NU se folosesc pentru alegere.

INTERZIS   procentul de 70% ca ţintă · orice PnL · orice metrică economică
```

---

# 14 — MATRICEA `cerință → regulă → câmp → test → exemple`

**Nu o livrez completă, fiindcă răspunsul la §14 e NU.** O matrice completă ar sugera că totul e calculabil din datele disponibile, ceea ce ar fi fals pentru rândurile blocate. Livrez partea calculabilă și marchez restul:

| cerință | regulă | câmp output | test | poz. | neg. |
|---|---|---|---|---|---|
| range macro nu moare la canal intern | precedență §5.5 + I2 | `depth 0` neschimbat | T1 | `BLIND-019` | `BLIND-002` |
| breakout închide fără să șteargă | `end_ts` scris, id imutabil | `EPISODE_CLOSED` | T4 | `BLIND-022` | — |
| sweep confirmat la reintrare | reintrare ≤ `K_reentry` | `SWEEP_CONFIRMED` | T2 | HBL-20 b56 | **★ `K_reentry` LIPSĂ** |
| breakout acceptat | 3 închideri (`N_accept=3`) | `BREAKOUT_ACCEPTED` | T4 | `BLIND-023` | 11 failed |
| promovare la trend | P1-P4 | `TREND_UP/DOWN` | T4 | 6 text liber | **★ fără limite** |
| rol retrospectiv | `role_known_ts ≠ start_ts` | `role` | T5 | HBL-20 | episoade fără rol |
| nivel MESO | `parent_structure_id` | `depth 1` | T6 | 34 segmente | 40 ferestre |
| **nivel MICRO** | — | `depth 2` | T6 | **★ ZERO** | — |
| **frontiere** | **★ NESPECIFICAT (S2)** | `boundary_*` | — | — | — |
| **atribuire de nivel** | **★ NESPECIFICAT (S1)** | `depth` | — | — | — |

---

# 15 — CORECȚIILE NECESARE, DECLARATE ȘI NEAPLICATE

**Nu am modificat `v4.1`.** Următoarele cer decizie și ar produce `v4.2`:

```
C1 (S2)  estimatorul frontierelor + regula de îngheţare. FĂRĂ ea, VE poate reintroduce
         defectul V1 fără să încalce nimic scris. ★ CEA MAI GRAVĂ.
C2 (S1)  regula de atribuire a nivelului: ce face un obiect MESO şi nu MICRO.
C3 (S3)  ce `role` primeşte un episod TREND închis.
C4 (S4)  dezambiguizarea lui `K_struct`: fereastră în bare SAU număr de swing-uri.
C5 (T6)  nivelul MICRO rămâne specificat dar NETESTABIL. Decizie: intră în prototip
         nevalidat, sau se amână până există etichete pe trei niveluri?
C6       cele opt valori numerice, prin protocolul preînregistrat.
```

**Recomandarea mea:** nu porni prototipul. `C1` singură e suficientă — o implementare fără estimator de frontieră ar fi VE alegând semantica în locul meu, exact inversarea de roluri pe care contractul nostru o interzice.

---

**Invariante verificate neatinse:** `n_generated_total = 363` · `m_inference = 26` · tombstones · registrul Alpha · verdictele existente · F1-F6 · F7 `SAFETY_GUARD` · LIVE_SHADOW · broker gate. Detectorul NU a fost rerulat, parametrii nu au fost modificați, niciun cod nu a fost implementat, `SEALED/OOS_ACCESS = 0`.

**Manifest:** v2.7.90. **VE rămâne în HOLD.**
