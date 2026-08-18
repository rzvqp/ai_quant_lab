# STATISTICIAN — RECONCILIERE RANGE PE ETICHETE `CEO_ASSISTED` ȘI SPECIFICAȚIE SEMANTICĂ V3

**Document ID:** STAT-RANGE-SEMANTIC-SPEC-V3-v1.0 · **Data:** 2026-08-18 · **Autor:** Statistician
**Consumă:** `RANGE_HUMAN_LABEL_BATCH_01.pdf` (lot `2673227`) + `RANGE_HUMAN_LABEL_BATCH_01_CEO_ASSISTED_RESULTS.md`

## VERDICT TERMINAL

```
RANGE_SEMANTIC_SPEC_READY_FOR_VE
următorul proprietar: VE_RANGE_0.4.0_SEMANTIC_REDELIVERY
SEALED/OOS_ACCESS = 0 · zero PnL · zero profitabilitate · zero Strategy Catalog · zero Alpha
```

> **Domeniu de valabilitate, declarat înainte de orice cifră: STRUCTURA e gata; NUMERELE nu. Lotul e `CEO_ASSISTED` și nu poate identifica niciun parametru. Specificația V3 e completă ca mașină de stări, condiții, memorie și ceas; fiecare constantă numerică e marcată explicit `NEIDENTIFICAT` și cere un pas separat de identificare. Nu aleg niciun punct arbitrar.**

---

# 0 — REGULA DE ONESTITATE, APLICATĂ ÎNAINTE DE ORICE

```
proveniență           CEO_ASSISTED — asistentul a exprimat o opinie vizuală, CEO a confirmat/corectat
NU e blind            NU e independent · NU e OOS · NU e validare
utilizare permisă     EXCLUSIV construcție semantică și diagnostic
interdicție           nu se aleg parametri pe acest lot și apoi nu se validează aceiași parametri pe el
consemnare            proveniența `CEO_ASSISTED` rămâne în document ȘI în manifest, permanent
```

**Lotul rămâne `construction-only` PERMANENT.** Validarea cere un lot NOU, etichetat fără afișarea ieșirii detectorului.

---

# 1 — VERIFICĂRI

```
lot            2673227 (rezultat) · protocol 84be9ab + amendament a486c5d      ✔
manifest       0f1e501 v2.7.83 · fingerprint d23612f8…                          ✔ recalculat
artefact rulat ve_n1_replay 0.3.1, wheel 048ee2b4…, config PINUIT               ✔
               w_atr = 0.30 · s_max = 0.60 · fingerprint 432170ff… · citează 4e69e22 / c29ac98
```

## 1.1 Am verificat că etichetele au fost puse pe graficele reale

Etichetele CEO citează niveluri de preț. Le-am confruntat cu barele canonice ale ferestrelor:

```
HBL-01 1463-1478 vs real 1461.3-1479.0     HBL-17 1936-1973 vs real 1932.9-1973.8
HBL-04 1665-1678 vs 1635.8-1693.0          HBL-21 1864-1880 vs 1861.4-1918.7
HBL-12 1344-1352 vs 1321.9-1352.9          HBL-22 2376-2398 vs 2369.7-2425.5
HBL-14 1834-1838 vs 1830.1-1845.5          HBL-23 2020-2036 vs 2001.9-2047.7
HBL-15 1835-1847 vs 1812.6-1855.5          HBL-24 2307-2321 vs 2303.7-2378.6
HBL-16 1853-1862 vs 1761.0-1863.3
                                            11 / 11 cad ÎN INTERIOR
```

Mai mult, mai multe stau lipite de extremele reale (HBL-01: 1463 vs minim 1461,3; HBL-17: 1973 vs maxim 1973,8) — exact semnătura unei citiri de pe grafic. **Etichetele sunt reale. Premisa e verificată, nu acceptată.**

## 1.2 Ce a etichetat CEO

```
24 ferestre  →  5 RANGE pur · 2 CHANNEL pur · 17 MULTI-REGIME
66 segmente  →  27 de tip RANGE, în 21 din 24 de ferestre
```

---

# 2 — CE FACE DETECTORUL ACTUAL: LANȚUL DE PIERDERE

Rulat pe cele 24 de ferestre, cu 480 de bare de încălzire înainte de fiecare, exact ca în operare live:

```
   6912 bare evaluate
   1118 bare cu episod VIU                          16,17%   ← restul: ACCEPTED_BREAK / NO_STRUCTURE
    193 bare cu >= 2 atingeri pe AMBELE laturi       2,79%
     16 bare clasificate RANGE_STATE                 0,23%
```

```
UNAVAILABLE   5794  83,83%   din care ACCEPTED_BREAK 5298 (76,65%) · NO_STRUCTURE 496 (7,18%)
UNCLASSIFIED   929  13,44%
CHANNEL_UP     104   1,50%
CHANNEL_DOWN    69   1,00%
RANGE_STATE     16   0,23%
```

**Pe clase de fereastră, comparat cu ce vede CEO:**

| clasa CEO | ferestre | bare | RANGE_STATE | CANAL | INDISPONIBIL |
|---|---|---|---|---|---|
| RANGE pur | 5 | 1056 | **0 (0,00%)** | 32 (3,03%) | 81% |
| CHANNEL pur | 2 | 192 | 0 (0,00%) | **0 (0,00%)** | 85% |
| MULTI-REGIME | 17 | 5664 | 16 (0,28%) | 141 (2,49%) | 84% |

> **În cele CINCI ferestre pe care CEO le numește range fără ezitare, detectorul produce ZERO bare de range — și 32 de bare de CANAL. În cele DOUĂ ferestre de canal curat produce ZERO bare de canal. Nu e un detector înclinat spre canal: e un detector MUT pe 97% din bare, care ocazional numește canal exact acolo unde omul vede lateral.**

**Rată de omisiune a segmentelor: 37 din 66 (56%)** — tabelul complet, segment cu segment, în `HUMAN_LABEL_BATCH_01_SEGMENT_TABLE.md`.

---

# 3 — PATRU DEFECTE STRUCTURALE, FIECARE MĂSURAT

## 3.1 Ancora se calculează pe 512 bare, dar mărginește un range de 96

`range_window = 512` (`range_state_v2.py:151`). Ancorele sunt **mediana swing-urilor din ultimele 512 bare** ≈ 5,3 zile de tranzacționare. Range-ul minim cerut e `d_min = 96` bare ≈ o zi.

> **Fereastra pe care se calculează frontiera e de 5,3 ori mai LARGĂ decât durata minimă a lucrului pe care ar trebui să-l mărginească. Frontiera unui range de o zi e dominată de swing-uri din afara acelui range.**

Măsurat direct — ancorele detectorului față de limitele văzute de CEO:

```
HBL-21   CEO 1864-1880          detector 1920,8-1927,4     eroare 52,1 = 326% din lățimea CEO
HBL-12   CEO 1344-1352          detector 1324,3-1326,8     eroare 22,4 = 280%
HBL-04   CEO 1665-1678          detector 1694,2-1697,8     eroare 24,5 = 188%   (INTEGRAL deasupra)
HBL-17   CEO 1936-1973 (lat 37) detector 1945,4-1954,8 (lat 9,4)                 eroare  37%
HBL-24   CEO 2307-2321 (lat 14) detector 2308,5-2317,0 (lat 8,5)                 eroare  20%
```

**Și lățimea e sistematic prea mică**: mediana swing-urilor stă în MIJLOCUL distribuției, nu la marginea range-ului. Exact mecanismul pe care l-am semnalat la v2.7.79 („ancora mediană stă în MIJLOCUL distribuției de swing-uri, nu la o extremă") — atunci am văzut că asta anulează puterea de discriminare a pozitivelor; acum se vede a doua consecință: **face frontiera trivial de depășit.**

## 3.2 `anchor_upper` poate ajunge SUB `anchor_lower`

```
HBL-01: detector anchor_lower = 1442,2 · anchor_upper = 1435,7  →  lățime NEGATIVĂ, −6,4
```

**Ancorele se inversează, și nimic nu oprește asta.** Garda `ZONES_DEGENERATE`, ratificată la v2.7.80 și raportată LIPSĂ de mine la v2.7.82, e exact garda care ar fi prins acest caz — și încă e absentă. Măsurat pe barele disponibile, separarea ancorelor scade sub o lățime de zonă pe **0,82%** dintre ele.

## 3.3 Cerința de durată nu poate să nu fie satisfăcută

```
bars_in_state pe cele 1118 bare disponibile:  min 487 · mediană 512 · max 599
sub d_min = 96:  0 bare  (0,00%)
codul TOO_SHORT: emis de 0 ori în 6912 bare
```

`_bars_in_state()` măsoară vârsta **celui mai vechi swing REȚINUT**, nu vârsta episodului de range; iar reținerea e plafonată la `range_window = 512`, adică de 5,3 ori `d_min`.

**Corectez o ipoteză proprie:** am presupus întâi un contor nemărginit și am testat-o — la warmup 200/480/1500/3000 valoarea a dat 197/469/508/508, deci **saturează**: contorul e mărginit, nu nemărginit. Mecanismul pe care îl propusesem era greșit. Concluzia rezistă însă în formă corectată și e mai simplă: **plafonul stă cu mult DEASUPRA pragului, deci poarta nu poate refuza nimic.** *O cerință care nu poate eșua nu e o cerință* — aceeași lecție ca la R10.

## 3.4 Acceptarea ruperii distruge episodul înainte să poată exista

```
din 5794 bare indisponibile, 5298 (76,65% din TOATE barele) poartă ACCEPTED_BREAK
```

Cu `n_acceptance = 2`, două închideri dincolo de zonă acceptă ruperea și invalidează episodul. Dar zona e centrată pe **mediana** swing-urilor: prin construcție, aproximativ jumătate dintre swing-urile high stau DEASUPRA ancorei superioare. Două închideri deasupra medianei + 0,30·ATR e un eveniment **absolut obișnuit**.

> **Detectorul își invalidează propriul episod de trei ori mai des decât îl ține în viață. Iar dintre barele care totuși supraviețuiesc ȘI acumulează două atingeri pe fiecare latură (193), 173 — adică 90% — sunt respinse pe axa PANTEI ca fiind canal. Range-ul e strivit din două direcții simultan.**

**Aceasta e aceeași CLASĂ de defect ca la V1**, pe care am diagnosticat-o `SEMANTIC_SPEC_DEFECT`: o definiție a cărei proprie regulă distruge precondiția de care are nevoie cealaltă regulă. V1 invalida retroactiv atingerile; V2 invalidează episodul. **Reparația din V2 a mutat defectul, nu l-a eliminat.**

---

# 4 — RĂSPUNSUL LA ÎNTREBAREA PRINCIPALĂ

> **Raritatea RANGE NU e o proprietate a XAUUSD M15.**

Argumentul nu e retoric, e aritmetic. CEO identifică segmente de range în **21 din 24** de ferestre selectate uniform, fără detector. Detectorul dă **0,23%** din bare. Cele două afirmații nu pot fi ambele despre piață.

**Descompunerea cauzală, cu ponderi măsurate:**

```
CAUZĂ 1  definiție prea strictă prin ACCEPTARE           83,83% din bare pierdute înainte de orice test
         (ancoră mediană + n_acceptance = 2 ⇒ ruperea e acceptată banal)
CAUZĂ 2  scara greșită a ancorei (512 vs 96)             frontiera nu e frontiera range-ului local
CAUZĂ 3  lipsa segmentării longitudinale                 17 din 24 ferestre sunt MULTI-REGIME;
         detectorul are o singură stare pe fereastră și nicio noțiune de secvență
CAUZĂ 4  range confundat cu canal                        90% dintre barele care trec testul de atingeri
                                                          sunt respinse ca IS_CHANNEL
CAUZĂ 5  poarta de durată inoperantă                     nu contribuie la raritate; e o cerință moartă
```

**Deci: o COMBINAȚIE**, dominată de cauza 1, cu cauza 2 ca rădăcină comună a cauzelor 1 și 4 — o ancoră calculată pe scara greșită produce și rupturi false, și pante false.

**Nu raportez niciun procent-țintă.** Cele 70% sunt o ipoteză a CEO, nu un criteriu. Proporția se raportează **abia după** ce definiția e fixată semantic și validată pe un lot nou — altfel aș regla o definiție ca să nimerească un număr, ceea ce e exact eroarea pe care întreg dosarul o evită.

---

# 5 — HBL-20: TIPARUL, DEFINIT CAUZAL

**Confirmat de CEO:** `RANGE/ACUMULARE → MANIPULARE/SWEEP_DOWN → EXPANSIUNE/MARKUP_UP → RANGE nou`.
Fereastra: 2025-08-15 09:00 → 2025-08-18 09:45 UTC, 96 bare, interval 3323,68–3358,49.

```
FAZA 1  ACUMULARE        barele 0-31    3333,06 - 3346,10   lățime 13,04
FAZA 2  SWEEP_DOWN
        prima bară sub minimul acumulării   bara 52   2025-08-17 23:00   low 3330,25 < 3333,06
        REINTRARE, primul close înapoi peste 3333,06:  bara 56   2025-08-18 00:00   close 3334,94
        confirm_ts = bara 56.   ⚠ Pe bara 52 informația „acesta e un sweep" NU EXISTA.
FAZA 3  MARKUP_UP
        primul close peste maximul acumulării 3346,10:  bara 63   2025-08-18 01:45   close 3346,99
        maxim ulterior 3358,49
```

## Ce separă un SWEEP de un BREAKOUT autentic

```
SWEEP_DOWN   depășire a frontierei inferioare  URMATĂ de reintrare cu ÎNCHIDERE în interior,
             în cel mult K bare.   Se confirmă la REINTRARE, nu la depășire.
BREAKOUT     depășire URMATĂ de acceptare (N închideri în afară) FĂRĂ reintrare în K bare.
             Se confirmă la a N-a închidere.
```

> **Cele două ipoteze sunt DESCHISE SIMULTAN între bara 52 și bara 56. Pe bara 52 nu se poate decide, și orice specificație care pretinde altceva introduce lookahead. `K` și `N` sunt NEIDENTIFICATE de acest lot.**

**Ce NU fac:** niciun PnL, nicio afirmație de profitabilitate, nicio intrare în Strategy Catalog, nicio modificare a lui `m_inference` (26) sau `n_generated_total` (363). Rămâne **candidat semantic**.

---

# 6 — SPECIFICAȚIA V3

```
contract_version   range-semantic-v3.0        (V2 = range-state-v2, NEATINS)
regulă             NU se reutilizează `StructBand.RANGE`; NU se schimbă sensul enumurilor vechi.
                   V3 introduce enumuri NOI, într-un spațiu de nume propriu.
```

## 6.1 Cele trei schimbări arhitecturale care fac diferența

```
S1  SEGMENTARE LONGITUDINALĂ. O fereastră NU are o stare; are o SECVENȚĂ de segmente cu
    tranziții explicite. 17 din 24 de ferestre sunt multi-regim — o etichetă per fereastră
    pierde exact informația căutată.
S2  ACCEPTAREA SE SEPARĂ DE INVALIDARE. Astăzi o rupere acceptată ȘTERGE episodul. În V3
    ruperea acceptată ÎNCHEIE segmentul și DESCHIDE următorul, păstrând identitatea secvenței.
    Un range care se termină nu e un range care n-a existat.
S3  ANCORA SE CALCULEAZĂ PE SEGMENTUL CANDIDAT, nu pe o fereastră fixă de 512 bare.
    Fereastra ancorei nu poate depăși durata segmentului pe care îl descrie.
```

## 6.2 Stările și evenimentele

Pentru fiecare: **inputuri · condiție · memorie longitudinală · `confirm_ts` · zero-lookahead · reason codes · snapshot · invalidarea identității · ieșire · ce NU era încă disponibil.**

```
RANGE_ESTABLISHING
  inputuri      swing-uri confirmate (k), ATR(14) cauzal, close-uri
  condiție      >= 2 swing high ȘI >= 2 swing low în segmentul candidat, ancore din ELE
  memorie       segmentul candidat, de la primul swing reținut al segmentului — NU 512 bare fixe
  confirm_ts    bara la care se confirmă al doilea swing de pe latura a doua
  zero-lookahead ancorele folosesc DOAR swing-uri deja confirmate la bara i
  reason        ESTABLISHING_FEW_SWINGS · ATR_UNAVAILABLE
  ieșire        → RANGE_ESTABLISHED | RANGE_FAILED | CHANNEL_*
  nedisponibil  dacă range-ul va ține — nu se poate ști încă

RANGE_ESTABLISHED
  condiție      atingeri >= n_touch pe FIECARE latură ȘI durata segmentului >= d_min
                ȘI panta normalizată <= s_max ȘI zonele DISJUNCTE
  ★ durata se măsoară de la `structural_start` AL SEGMENTULUI. Fereastra ancorei
    nu are voie să depășească durata segmentului: altfel poarta e moartă (§3.3).
  ★ GARDĂ OBLIGATORIE: anchor_upper > anchor_lower ȘI 2·w·ATR < (anchor_upper − anchor_lower)
    → altfel `ZONES_DEGENERATE`, fail-closed prin TIP. Inversarea din §3.2 trebuie
    NEREPREZENTABILĂ, nu doar detectată.
  reason        OK_RANGE · FEW_TOUCHES · TOO_SHORT · IS_CHANNEL · ZONES_DEGENERATE

RANGE_MID · BOUNDARY_TEST_UPPER · BOUNDARY_TEST_LOWER
  condiție      bara INTERSECTEAZĂ zona respectivă; fitilul e atingere, neintersecția nu e
  confirm_ts    bara însăși (închisă)
  BOUNDARY_TEST_* NU invalidează. E evenimentul care CONSTITUIE range-ul, nu care îl strică.

LIQUIDITY_SWEEP_UP / LIQUIDITY_SWEEP_DOWN
  condiție      depășirea zonei URMATĂ de close ÎNAPOI în interior în <= K bare
  memorie       bara depășirii + numărătoarea până la reintrare
  confirm_ts    bara REINTRĂRII, niciodată bara depășirii
  zero-lookahead între depășire și reintrare starea rămâne AMBIGUĂ prin contract:
                se emite BOUNDARY_BREACH_PENDING, nu o clasificare
  invalidare    NU invalidează range-ul — îl CONFIRMĂ
  nedisponibil  pe bara depășirii nu se poate distinge sweep de breakout (dovedit la §5)

BREAKOUT_ACCEPTANCE_UP / _DOWN
  condiție      N închideri consecutive în afara zonei FĂRĂ reintrare în K bare
  confirm_ts    a N-a închidere
  ★ ÎNCHEIE segmentul de range; NU șterge identitatea. Segmentul trece în istoric cu
    starea TERMINATED_BY_BREAKOUT, iar succesorul primește `predecessor_id`.
  ieșire        → CHANNEL_* | RANGE_ESTABLISHING (range nou) | TRANSITION

RANGE_FAILED
  condiție      segmentul candidat pierde precondiția înainte de ESTABLISHED
  ieșire        → TRANSITION

CHANNEL_UP / CHANNEL_DOWN
  condiție      pantă normalizată > s_max, cu semnul pantei
  ★ direcția e OBLIGATORIE și nenulă ori de câte ori se emite clasa (contract v2.1, păstrat)
  ★ `slope == 0` trebuie tratat explicit, nu lăsat pe ramura `else`

TRANSITION / UNAVAILABLE
  ★ TRANSITION e o stare de PLIN DREPT, nu absența uneia. Astăzi 83,83% din bare cad în
    „indisponibil" fiindcă nu există unde altundeva să cadă. TRANSITION acoperă intervalul
    dintre două segmente identificate; UNAVAILABLE rămâne EXCLUSIV pentru input lipsă.
  reason        ATR_UNAVAILABLE (input) vs BETWEEN_SEGMENTS (structural) — NU se confundă
```

## 6.3 Reguli transversale

```
CEAS          fiecare stare are `structural_start_ts` (când a început în retrospectivă)
              și `confirm_ts` (când s-a putut ști). Nicio decizie nu se ia la structural_start.
SNAPSHOT      snapshot/restore bit-identic pe: segmentul curent, istoricul de segmente,
              swing-urile reținute, contoarele de atingeri, starea pending a breșei.
              Refuz fail-closed la orice snapshot de altă versiune de contract.
IDENTITATE    `segment_id` stabil; ruperea acceptată NU minte un id nou pentru același range;
              un segment NOU primește `predecessor_id` și `transition_reason`.
AUDIT         se înregistrează PERECHEA (reason_code, însoțitor). Un jurnal care păstrează
              IS_CHANNEL și pierde `structure_class` colapsează două stări în una (v2.1).
```

## 6.4 Parametrii — toți NEIDENTIFICAȚI de acest lot

```
K   fereastra de reintrare pentru sweep        NEIDENTIFICAT — interval plauzibil (1, d_min/4]
N   închideri pentru acceptare                 NEIDENTIFICAT — moștenit provizoriu n_acceptance = 2
w_atr                                          RATIFICAT 0,30 — dar sub o ancoră DIFERITĂ;
                                               ★ trebuie REIDENTIFICAT când ancora se schimbă
s_max = 2·w_atr                                cuplarea rămâne, valoarea urmează w_atr
d_min                                          96 (MULTIDAY) / 24 (INTRADAY), moștenit
fereastra ancorei                              ★ NU 512. Se leagă de durata segmentului.
                                               Regula exactă: NEIDENTIFICATĂ.
```

> **Lotul `CEO_ASSISTED` NU poate identifica niciunul dintre acestea, și nu voi alege un punct. Identificarea cere un protocol separat, pe date care nu sunt și sursa etichetelor. Raportez intervalul, nu punctul — la fel ca la `w_atr` înainte de controlul negativ.**

---

# 7 — CONTRADICȚII FAȚĂ DE CONTRACTUL ACTUAL

```
C1  `range_window = 512` NU e în configurația canonică ratificată la v2.7.80. E un parametru
    NEDECLARAT care determină ancorele și face poarta de durată inoperantă. Contradicție directă.
C2  `d_min_bars` e ratificat ca durata range-ului; implementarea măsoară vârsta celui mai vechi
    swing reținut. Nu e același lucru, și diferența e de 5,3×.
C3  Garda `ZONES_DEGENERATE` rămâne ABSENTĂ (semnalată la v2.7.82). §3.2 arată consecința reală:
    ancore INVERSATE, lățime negativă, fără nicio oprire.
C4  Ruperea acceptată ȘTERGE episodul. Contractul semantic cere ca un range terminat să rămână
    un range care a existat. Contradicție de model, nu de parametru.
C5  Nu există stare de SWEEP. `LIQUIDITY_SWEEP` există ca EVENIMENT (105 emisii) dar nicio stare
    o consumă — deci nu poate fi nici testat, nici falsificat.
C6  Nu există TRANSITION. Tot ce nu e clasificat cade în „indisponibil", amestecând input lipsă
    cu structură absentă — exact confuzia pe care contractul v2.1 o interzice la reason codes.
```

---

# 8 — CE RĂMÂNE BLOCAT

```
F1-F6                 BLOCKED_PENDING_RANGE_SEMANTIC_FIX — nemodificat
F7                    SAFETY_GUARD — nu strategie, nu ipoteză
m_inference = 26 · n_generated_total = 363 · tombstones · registrul Alpha · verdictele existente
HBL-20                candidat semantic. NU în Strategy Catalog. Zero PnL, zero profitabilitate.
lotul HBL             construction-only PERMANENT
0.3.1                 Red Team NU e autorizat pe el; nici pe 0.3.0
```

## Ordinea obligatorie, reafirmată

```
Statistician spec → VE artifact → Red Team code/semantic PASS → LOT BLIND NOU →
Red Team blind PASS → VE Strategy Catalog → Red Team PASS → Alpha discovery → AI Trader
```

**Lotul blind nou se definește ÎNAINTE de rulare** și se etichetează **fără** afișarea ieșirii detectorului. Regula lui de selecție e deja preînregistrată la `84be9ab`/`a486c5d` și se reutilizează cu un seed nou, declarat înainte.

---

# 9 — ELEMENTE DESCHISE

```
BLOCANT      Niciun parametru V3 nu e identificat de acest lot. Identificarea cere date care
             nu sunt și sursa etichetelor — altfel se alege și se validează pe același material.
BLOCANT      Ancora nouă schimbă sensul lui `w_atr = 0,30`: valoarea a fost derivată sub ancora
             mediană pe 512 bare. Cu o ancoră legată de segment, derivarea TREBUIE refăcută.
MATERIAL     Lotul e CEO_ASSISTED. Un asistent a propus, CEO a confirmat — deci etichetele pot
             purta o parte din prejudecata propunerii. Nu pot cuantifica acea parte.
MATERIAL     Segmentele CEO nu au timestamp-uri. Potrivirea per segment e la nivel de FEREASTRĂ
             („detectorul a produs vreodată starea X aici"), nu la nivel de bară. „Început prea
             târziu / închis prea devreme" NU se pot măsura fără granițe de segment.
LIMITARE     Încălzirea de 480 de bare e o alegere de harness. Am verificat sensibilitatea:
             la 200/480/1500/3000 rezultatul saturează, deci concluziile nu depind de ea.
NON_MATERIAL Cele 16 bare RANGE_STATE apar în 2 ferestre (HBL-18: 4, HBL-24: 12).
```

---

**Invariante verificate neatinse:** `n_generated_total = 363` · `m_inference = 26` · tombstones · registrul Alpha · verdictele existente · F1-F6 și cele 44 · F7 `SAFETY_GUARD`. Alpha, AI Trader, regresia, LIVE_SHADOW, brokerul: **neatinse**. `SEALED/OOS_ACCESS = 0`.

**Manifest:** v2.7.84.
