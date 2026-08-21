# HR-TU-pb-L — PREGĂTIREA VALIDĂRII INDEPENDENTE

**Divizia Statistician · `STAT-HR-TU-PB-L-INDEPENDENT-VALIDATION-PREP-001` · 2026-08-21**

```
HR_TU_PB_L_FRESH_VALIDATION_EVIDENCE_REQUIRED
```

**Protocolul NU e înghețat.** Nicio validare executată. Identitatea candidatului **este** înghețată,
regiunile candidate **sunt** identificate și hashuite, iar porțile **sunt** pre-înregistrate — dar
condiționat, fiindcă §7 le cerea doar dacă evidența e curată, și nu este.

Motivul e la §5 și e **material**: dovada propusă nu e nouă pentru divizia care a produs candidatul.

---

## 1 — IDENTITATEA CANDIDATULUI, RECUPERATĂ MECANIC

Recuperată din cod, nu din enunțul mandatului. Candidatul se întinde peste **două** commit-uri: stratul
de date + EDGE H1 vine din `2c8e3f4`, stratul de intrare/risc din `5c3b61a` (vârful, autoritatea numită
în mandat). Ambele sunt necesare pentru identitate; le îngheț pe amândouă.

| element | valoare recuperată |
|---|---|
| ID strategie | `HR-TU-pb-L-rr2` (`m5entry_htfrisk.py`) |
| amprentă implementare | `m5entry_htfrisk.py` blob `76b2e780e061` · `h1m5_campaign.py` blob `2e37116ba79e` · `m5_data.py` blob `1339e74a5e05` |
| amprentă configurație | `TRIG_WIN=36` · `MAXHOLD_M5=576` · `KSTRUCT=6` · `rr=2.0` · `PIP=0.10` · `TICK=0.01` · `RT.STRESS=0.24` |
| regim / direcție | `TREND_UP`, **LONG-only** (`up=True`) |
| **EDGE H1** | `edge_trend_pullback(up=True)`: bara H1 `i-1` a străpuns EMA20 în jos (`low[i-1] < ema20[i-1]`) **și** `close[i] > close[i-1]`, în regim `TREND_UP`. Nivel de referință = `high[i]` |
| regim `TREND_UP` | `ema20 > ema50` **și** `effic > 0.30` (eficiență direcțională pe 20), calculat pe H1 |
| **TRIGGER M5** | `kind="breakout"`: primul `j` din cele 36 de bare M5 după `close_time[i]` cu `m5h[j] > level`; intrare la **`m5o[j+1]`** |
| **SL — H1 structural** | `htf_stop_price`: `min(h1.low[i-6 … i]) − 0.10 × ATR14_H1[i]` |
| **TP — H1 economic** | `entry_ref + 2 × risk_ref`, cu `entry_ref = m5o[j_ref]` (prima bară M5 după închiderea H1 = deschiderea H1 următoare) și `risk_ref = abs(entry_ref − stop_px)` |
| hold maxim | **576 bare M5 = 48 h**; la epuizare, ieșire la `m5c` (a treia stare, v. §4.1) |
| serializare | fără suprapunere: intrare nouă doar dacă `m5t[ej] > lastB`, cu `lastB` = timpul barei `ej+576` |
| dependențe de sesiune | **NICIUNA** — nu există filtru de oră, de zi sau de sesiune |

**★ Ce NU e în identitate, deși mandatul îl presupune:** nu există „H4 context" și nu există „structură
M15" în acest candidat. H1 e singurul strat superior, iar el e **agregat cauzal din M5-ul gated**
(`m5_data.aggregate`), nu H1 nativ. Cheia H1 din manifest e sigilată (`AWAITING_REGIME_MAP`), deci H1
nativ nici nu era disponibil.

---

## 2 — §3 FIDELITATEA ARHITECTURII: **PASS**

Verificat linie cu linie, fiindcă mandatul cere STOP la nepotrivire semantică:

```
stop_px = htf_stop_price(i, up)        -> h1.low / ATR14_H1        => H1. NU M5.
tgt_px  = entry_ref + d*rr*risk_ref    -> ancorat in entry_ref     => H1. NU M5.
m5_entry_idx(...)                      -> DOAR indexul de intrare  => M5 = ENTRY ONLY.
```

`walk()` parcurge bare M5, dar **doar ca rezoluție de execuție** (stop-first în bară, conservator):
pragurile pe care le testează sunt cele două prețuri H1. Nu există invalidare micro pe M5, nu există
stop M5, nu există țintă M5.

> **O nuanță reală, semnalată fiindcă schimbă interpretarea, nu verdictul:** SL și TP sunt calculate din
> `entry_ref` — prețul intrării **grosiere** (A), nu al intrării M5 (B). A și B partajează deci exact
> aceleași două prețuri absolute. E corect pentru experimentul de control (numai timing-ul diferă),
> **dar are o consecință economică pe care §8 o ratează** — v. §4.2.

---

## 3 — §4 IDENTITATEA EVIDENȚEI DE CERCETARE: **VERIFICATĂ**

Am rulat eu însumi stratul de date al candidatului (import izolat, fără bucla de campanie):

```
M5 livrate de poarta gated : 155.258 bare   2021-07-27 15:45:00Z .. 2024-06-20 00:40:00Z
H1 agregate                : 12.946 bare    (DEV 10.168 · CALIB 2.778)
DEV  (frozen)  121.949 bare  ohlc b30912e1...    CALIB (frozen)  33.309 bare  ohlc 3c170953...
```

Corespunde exact populațiilor pe care le-am înghețat la `b8d0447`. Verificat mecanic pe **întreg**
arborele `reports/alpha_discovery/`:

| cerință | rezultat |
|---|---|
| acces 2025+ | **0** — poarta livrează maximum `2024-06-20 00:40Z`; `m5_data` are și aserțiuni proprii de leak |
| N4 | **0** — zero referințe la `zone_confirmation` / `market_bus` / `confirmations` în lanțul candidatului |
| `shadow_driver` | **0** referințe |
| `read_csv` pe `data/market` în lanțul M5 | **0** — `m5_data.py` folosește exclusiv `edge_research._common.load` |

**Regula pe care am predat-o la `b8d0447` a fost respectată.**

> **Dar am găsit ce nu mi s-a cerut să caut, aplicând aceeași regulă pe TOT repo-ul, nu doar pe lanțul
> M5:** patru scripturi Alpha **citesc brut** `data/market` — `h1_protrend.py`, `econ_campaign.py`,
> `econ_profile_scan.py`, `deepen_econ.py`. Le-am verificat pe fiecare: **toate se plafonează la
> blocurile 0/1/2** (`≤ 2021-09`), niciunul nu atinge blocul 3. `hist_rereview.py` și `hist_wave2.py`
> se plafonează la `< 2018-05`. Deci **ocolirea porții există, dar nu a produs scurgere** pe această
> linie. O semnalez fiindcă e aceeași clasă de defect care a contaminat N4 — de data asta inertă.

---

## 4 — ★ TREI CORECȚII LA CIFRELE PROPRII ALE CANDIDATULUI

Am reprodus independent toate cifrele din mandat, re-executând funcțiile exacte ale candidatului pe
populația gated. **Toate se confirmă la ultima zecimală:** DEV `n=51`, `WR=0.510`, `avgR=+0.4506`,
`PF=1.926`, `medTP=166.5p`, CALIB `+0.2446`, RR1.5 `WR=0.627`. Nu contest niciun număr raportat.
Contest **ce înseamnă** trei dintre ele.

### 4.1 „RR = 1:2" descrie o paranteză cu DOUĂ ieșiri. Realitatea are TREI.

```
n=51  ->  tinta atinsa 26 (51,0%)   stop atins 18 (35,3%)   IESIRE PE TIMP 7 (13,7%)
```

Una din șapte tranzacții nu atinge nici stopul, nici ținta: iese la piață după 48 h. `WR = 51%` e
**rata de atingere a țintei**, nu rata de câștig; o parte din cele 49% rămase sunt ieșiri neutre, nu
pierderi de 1R. Raportarea din §8 trebuie să ceară descompunerea în trei, altfel „51% WR la 1:2" e
citit ca o paranteză pe care sistemul nu o are.

### 4.2 ★ RR-ul **executat** nu e 1:2. E ≈ 1:1,6.

Consecința nuanței din §2: SL și TP sunt fixate față de `entry_ref`, dar tranzacția se deschide la
`entry_b`. Iar M5-ul intră aproape întotdeauna **mai prost**:

```
entry_edge:  medie -15,7 pips   mediana -10,1 pips   MAI PROST decat A in 92,2% din cazuri
risc propriu / risc parinte:    mediana 1,120
SL median:   83,3 pips in unitati-parinte   ->   102,0 pips in unitati REALE
REWARD:RISK REALIZAT:           mediana 1,679    medie 1,598      (nominal 1:2)
```

Motivul e mecanic și inevitabil: stopul e fix, deci o intrare mai proastă **mărește** riscul asumat și
**micșorează** recompensa rămasă. Riscul real per tranzacție e cu ~12% mai mare decât numitorul folosit.

Alpha a măsurat corect efectul și l-a raportat separat (`B_ownRR_avgR`), dar l-a lăsat în subsol, iar
§8 cere raportarea „RR = 1:2". **Cifrele oneste, în unități de risc efectiv asumat:**

| metrică | unități-părinte (raportat) | **unități proprii (corect)** |
|---|---|---|
| avg R | +0,4506 | **+0,4191** |
| best-10%-eliminat | +0,283 | **+0,2407** |
| SL median | 83,3 p | **102,0 p** |
| maxDD | 4,62 R | **3,13 R** |
| cea mai mare pierdere | — | **−1,084 R** |

Diferența nu răstoarnă semnul, dar validarea trebuie să raporteze **unitățile proprii ca primar**: e
singurul număr pe care un cont îl trăiește.

### 4.3 „Pozitiv în toți cei 3 ani DEV" e adevărat și aproape gol de conținut

```
2021: n=13  +0,077        2022: n= 9  +0,653        2023: n=29  +0,500
```

2021 e practic plat, pe 13 tranzacții; distribuția anuală e 13/9/29. „Trei ani pozitivi" sugerează trei
observații independente — sunt trei sub-eșantioane foarte inegale dintr-un total de 51.

### 4.4 Am urmărit o anomalie și am constatat că NU e defect

`CALIB avgR = 0,2446` e **identic la patru zecimale** pentru rr1.5 și rr2, deși `WR` diferă
(0,462 vs 0,385). Am reprodus per-tranzacție ca să văd dacă e un bug de stare partajată. **Nu este.**
E aritmetică exactă: trecând de la 1,5 la 2, fiecare tranzacție care atinge ambele ținte câștigă
**exact +0,5 R**, iar tranzacția care atinge 1,5 și apoi se întoarce în stop pierde **exact −2,5 R**.
Aici: 5 × (+0,5) = 2,5 = 1 × (−2,5). Coincidență structurală, nu eroare.

**Dar constatarea de fond e mai gravă decât ar fi fost un bug:** întreg rezultatul CALIB `+0,2446` stă
pe **13 tranzacții**, iar o singură tranzacție care basculează anulează câștigul a cinci altora. Iar
`CALIB_A` (intrarea grosieră) la rr2 este **negativ, −0,0191**. Concluzia „M5 îmbunătățește" pe CALIB
se sprijină pe 13 versus 17 tranzacții. Nu e evidență; e zgomot cu virgulă.

### 4.5 Ce se confirmă fără rezervă

Candidatul **nu** e micro-scalping, și asta cerea directiva economică: `%TP ≥ 70p = 88,2%`,
`≥ 80p = 84,3%`, `≥ 100p = 70,6%`, TP median 166,5 pips (~156 pips față de intrarea reală) =
**~15,6 USD** la convenția `10 pips = 1,00 USD`. Corecția HTF a rezolvat real nepotrivirea semantică
de care CEO a fost diagnostician. Acest punct îl susțin integral.

---

## 5 — ★ AUDITUL DE NOUTATE SPECIFIC CANDIDATULUI

Mandatul cere explicit să determin dacă consumul cunoscut al lui N4 e **relevant sau irelevant** pentru
acest candidat, și interzice să presupun răspunsul. L-am determinat mecanic — și am găsit că întrebarea
pusă nu e cea periculoasă.

### 5.1 N4 — **IRELEVANT**, demonstrat

| | N4 (`zone_confirmation`) | HR-TU-pb-L |
|---|---|---|
| construct | penetrarea unei zone N3 + `persistence` (fracția închiderilor dincolo) + `progress/ATR-M15` | `m5h[j] > high[i]` al barei de semnal H1 |
| ceas | `W_DEFAULT = 3` bare M5 | `TRIG_WIN = 36` bare M5 |
| praguri | `0.2240 / 0.8378 / 0.0000 / 0.6667` | niciunul dintre ele |
| import | — | **zero** referințe |

Zero parametri partajați, zero constructe partajate, zero dependență de cod. Terțilele N4 nu pot
propaga selecție către acest candidat fiindcă nu intră nicăieri în el.

```
N4_CONSUMPTION_RELEVANCE_TO_HR_TU_PB_L = IRRELEVANT
```

### 5.2 ★ Ce e relevant: **propria divizie a consumat deja tot intervalul propus**

Aplicând întrebarea corect — *„a influențat evidența propusă cercetarea acestei divizii?"* — am
inventariat artefactele committed din `edge_research/`. Fiecare studiu de edge Flow A își înregistrează
propriul `date_range`:

```
E005 E006 E008 E009 E010 E011 E012 E013/E016 E014 E015 E017 E025 E026 E027 E028 E029 E032
      date_range = 2022-12-16 10:45Z  ->  2025-10-23 09:00Z          (>= 17 studii)
E025 E026 E028 E029 E032 (rularile originale)
      date_range = 2022-12-16 10:45Z  ->  2026-07-13 06:00Z
```

**Flow A este „Alpha Discovery Laboratory"** — aceeași divizie care a produs HR-TU-pb-L (`_common.py`
o numește astfel în propriul docstring). Deci intervalul propus ca dovadă independentă a fost deja
exploatat, la rezoluție M15, de cel puțin 17 ipoteze de edge distincte ale aceleiași divizii.

**Iar adiacența nu e nominală.** `E028 — Fibonacci OTE`, ipoteză înghețată verbatim:

> *„zona de retragere «optimal trade entry» 61,8%–79% a unei mișcări impulsive oferă o intrare de
> **continuare** favorabilă statistic"*

Aceea e, ca familie de mecanism, exact HR-TU-pb-L: **retragere într-un trend, intrare pe continuare.**
Operaționalizarea diferă (nivel Fibonacci vs străpungere de EMA20; M15 vs H1→M5), dar familia a fost
căutată pe fix acest interval. La fel `E032` (premium/discount față de echilibru), `E009` (retest
CHoCH), `E012`, `E015` — toate intrări pe retragere/retest.

**Nu pot demonstra o influență directă**, și nu o afirm: HR-TU-pb-L a fost selectat pe metrici DEV
calculate exclusiv sub poartă, iar niciun output E0xx nu intră în codul lui. Dar cerința §5 nu e
„demonstrează influența" — e „determină dacă evidența a influențat proiectarea". Canalul mecanic e
**absent**; canalul de cunoaștere al analistului e **prezent și nefalsificabil**.

### 5.3 Holdout-ul terminal — **CONSUMAT prin decizie CEO deja înregistrată**

`PROJECT_STATE_v2.md §8.23`, verdict factual confirmat de CEO: perioada
**`2025-10-23 09:15Z → 2026-07-13 06:00Z`** *„nu mai poate fi considerată SIGILATĂ sau nevăzută la
nivel de proiect"*; holdout-ul terminal e **CONSUMAT / INVALIDAT**. Cinci analize au avut observații
concrete înăuntru, care au intrat în statisticile raportate.

### 5.4 Clasificarea, pe regiuni

```
V1  2024-07-10 -> 2025-10-23   PARTIALLY_CONSUMED   (>=17 studii Flow A la M15, acelasi calendar; N4 la M5 brut)
V2  2025-10-23 -> 2026-02-17   CONSUMED             (holdout terminal invalidat, verdict CEO)
V3  2026-03-10 -> 2026-06-20   CONSUMED             (integral in fereastra invalidata)
V4  2026-07-13 -> 2026-07-27   CLEAN                (nimic in afara de N4 -- dar v. §7: 2.904 bare)
```

---

## 6 — §6 REGIUNEA ELIGIBILĂ, DERIVATĂ MECANIC

Am derivat-o din manifestul ratificat, nu din formularea mandatului. **Splitul M5 nu e cronologic** —
e `50_50_stratified_by_regime_segment` cu embargo 3.000 de bare, deci jumătățile discovery/sealed sunt
**întrețesute**, nu „înainte/după".

```
S1 correction  discovery 2021-07-27..2022-02-27   41.801 | embargo 4.140 | SEALED 2022-03-20..2022-10-21  42.300
S2 bull        discovery 2022-11-11..2024-06-20  113.458 | embargo 4.075 | SEALED 2024-07-10..2026-02-17 113.674
S3 correction  discovery 2026-03-10..2026-04-20    7.642 | embargo 4.107 | SEALED 2026-05-10..2026-06-20   8.202
tail           2026-06-30..2026-07-27  TOO_SHORT_FULLY_SEALED
```

Poarta a oprit Alpha la `2024-06-20` din două motive independente: acolo se termină discovery-ul S2,
**și** discovery-ul S3 începe după cutoff-ul de holdout `2025-10-23`.

**Identitatea regiunilor candidate** — hashuri calculate într-un proces care a tipărit **exclusiv
digestul**; nicio valoare OHLC nu a fost afișată, rezumată sau inspectată:

| regiune | interval | bare | `ohlc_sha256` (32) | `timeline` (16) |
|---|---|---|---|---|
| **V1** | `2024-07-10 20:45Z → 2025-10-23 09:15Z` | **91.445** | `a2ca328f40101954b42c08b9f9512ac2` | `7cec35f571a29cfd` |
| **V2** | `2025-10-23 09:15Z → 2026-02-17 11:45Z` | **22.229** | `c4d32d911eab0212ebd4b8f783283dc5` | `4cf3aac73b5eeae0` |
| **V3** | `2026-03-10 07:45Z → 2026-06-20 13:45Z` | **19.950** | `1496b35eafc59ac10fcfd4295aa39e15` | `6e56819fc7560010` |
| **V4** | `2026-07-13 06:00Z → 2026-07-27 17:55Z` | **2.904** | `a130b9a9ce2f812d9d175b08cd432a5a` | `9caa2e1a08d669ec` |

---

## 7 — ★ DOUĂ PROBLEME CARE AR BLOCA **CHIAR DACĂ** EVIDENȚA AR FI CURATĂ

Le separ deliberat de §5: nu depind de cine ce a consumat.

### 7.1 Regiunea propusă e un **regim omogen, potrivit direcției candidatului**

Eticheta e în manifestul ratificat, publică, la vedere:

> `"2022-10 -> 2026-02 bull (+223.3%) -- full"`

`V1` și `V2` sunt **integral** în interiorul acelui segment. HR-TU-pb-L este **LONG-only, continuare de
trend**. A valida un urmăritor de trend exclusiv long pe o fereastră despre care manifestul însuși
declară că e un bull de +223,3% nu e un test independent — e un test aliniat.

Și nu e nevoie să fi privit vreo bară ca să știi asta: **eticheta de regim e metadata ratificată**.
Oricine alege această fereastră a ales, prin construcție, un regim favorabil.

Singurul segment care ar testa candidatul advers — `S3`, etichetat *„2026-02 → 2026-06 correction
(−24,1%)"* — este **integral** în fereastra invalidată. Regimul care contează e exact cel indisponibil.

### 7.2 Volumul de dovezi e insuficient pentru mărimea selecției

Rata măsurată pe DEV: 51 tranzacții / 121.949 bare M5 = **1 la 2.391 de bare**.

```
V1        91.445 bare  ->  ~38 tranzactii
V1+V2    113.674 bare  ->  ~48 tranzactii
V3        19.950 bare  ->   ~8 tranzactii
V4         2.904 bare  ->   ~1 tranzactie
```

Iar candidatul e **cel mai bun din 84 de ipoteze** testate pe același DEV: 64 în `h1m5_campaign`
(2 direcții × 4 RR × 8 familii) plus 20 în `m5entry_htfrisk`. Un câștigător din 84 pe `n=51` are o
așteptare de contracție severă. Pentru comparație, pragul de adecvare pe care l-am pre-înregistrat
pentru S5/S20 a fost `n ≥ 100`; V1 oferă ~38, iar V4 oferă ~1.

**`V4` — singura regiune curată — e cu două ordine de mărime prea mică.** Asta e concluzia operativă:
curățenia și suficiența nu coexistă în nicio regiune disponibilă.

---

## 8 — §7 PORȚI PRE-ÎNREGISTRATE (contingent, NU protocol înghețat)

§7 le cerea doar dacă evidența e curată. Le scriu totuși — **și explic de ce aici, spre deosebire de
S5, nu e o formalitate goală**: la S5 nu exista nicio partiție de evaluat, deci pragurile nu aveau
obiect. Aici regiunile există, sunt hashuite, iar eu **nu am văzut niciun rezultat în ele**. Momentul
prezent e singurul în care pragurile pot fi fixate onest. Dacă CEO deblochează ulterior, ele sunt deja
bătute în cui și nu mai pot fi ajustate după rezultate.

```
HR_TU_PB_L_GATES_PREREGISTERED_CONTINGENT_ON_CEO_EVIDENCE_RULING
```

Toate în **unități de risc propriu** (§4.2). Toate necesare; oricare picată ⇒ FAIL.

| # | poartă | prag |
|---|---|---|
| A | adecvarea eșantionului | `n ≥ 30`. Sub 30 ⇒ `INCONCLUSIVE`, **niciodată** PASS sau FAIL. `n < 100` ⇒ verdictul poartă permanent eticheta `LOW_POWER` |
| B | expectanță BASE | `avg R_own > 0` la round-trip `0,05` |
| C | expectanță STRESS | `avg R_own > 0` la round-trip **`0,24`** |
| D | stabilitate temporală | trei treimi **cronologice**, fixate acum prin numărul de bare, nu de tranzacții: ≥ 2 din 3 pozitive, niciuna sub `−0,10` |
| E | robustețea cozii | `best-10%-eliminat > 0`. Supraviețuirea doar prin winsorizare = **FAIL de coadă**, nu PASS |
| F | robustețea intrării | trigger întârziat cu **1 bară M5** (intrare la `j+2` în loc de `j+1`) ⇒ `avg R_own > 0` |
| G | drawdown maxim | `≤ 10 R` (DEV a dat 3,13 R; pragul lasă 3× marjă) |
| H | pierderea individuală maximă | `≤ 1,5 R_own` (DEV: −1,084 R) |
| I | fidelitate de specificație | SL exclusiv H1-structural, TP exclusiv `entry_ref + 2 × risk_ref`, M5 **numai** pentru index de intrare. Orice abatere ⇒ STOP, nu FAIL |
| J | non-degenerarea ieșirii pe timp | ieșiri pe timp `≤ 30%` din tranzacții. Peste, „RR 1:2" nu mai descrie sistemul |

Niciun prag nu se mișcă după rezultate. Nicio metrică nu se adaugă pentru că arată bine.

## 9 — §8 SPECIFICAȚIA DE RAPORTARE, CORECTATĂ

Se raportează **ambele coloane**, unități-părinte și unități proprii, cu cele proprii ca primar:

```
WR = rata de atingere a TINTEI, plus descompunerea completa: tinta / stop / iesire-pe-timp
RR: nominal 1:2  SI  realizat (mediana + medie)     -- DEV a dat 1,679 / 1,598, NU 2,0
PF · avg R (BASE) · avg R (STRESS) · maxDD · pierderea maxima
SL median in pips PROPRII (DEV: 102,0) si in unitati-parinte (83,3)
TP median in pips  ·  %TP >= 70  ·  >= 80  ·  >= 100     (10 pips = 1,00 USD; 80 pips = 8,00 USD)
```

## 10 — §9 VARIANTA SECUNDARĂ, DOAR ÎNREGISTRATĂ

```
HR-TU-pb-L-rr1.5 = PROFILE_A_ADJACENT_RESEARCH_VARIANT
```

`WR` de cercetare **62,7%** — reprodus independent, `0.627`, se confirmă. **Nu** intră în această
validare. Candidat primar = **rr2 exclusiv**, ca să nu se creeze multiplicitate inutilă.

## 11 — §10 DOVADA DE ACCES

```
FINAL_HOLDOUT_ACCESS_COUNT = 0
VALIDATION_EXECUTION_COUNT  = 0
```

Nu am rulat candidatul pe V1/V2/V3/V4 și nu am inspectat niciun rezultat acolo. Am citit din fișierul
brut **exclusiv coloana `time`** pentru recensământul din §6 — tehnică deja folosită și ratificată la
selecția loturilor blind — plus hashurile de identitate, calculate cu digestul ca unic output.
**Deliberat nu am citit verdictele E028/E032/E009/E015**, deși sunt publicate: mi-ar fi introdus în
raționamentul de proiectare rezultate măsurate chiar pe regiunea candidată. Am folosit doar ipotezele
lor înghețate, care sunt metadate de mecanism.

Re-execuția din §4 a atins **numai** DEV+CALIB, prin poarta gated — care fizic nu poate întoarce bare
de după `2024-06-20`. Nu e o promisiune, e o proprietate a loaderului.

## 12 — ★ CONFLICT DE ALOCARE, SEMNALAT

`V1` se suprapune calendaristic (`2024-07-10 → 2025-10-12`) cu populația curată de **52.572 bare M15**
pe care am înghețat-o la `ed49c2c` ca evidență de validare independentă pentru **S5 și S20**, predată
Red Team. Timeframe diferit, mecanisme diferite — dar **aceeași istorie de preț**. Dacă se folosește și
aici, aceleași ~15 luni devin dovada „independentă" pentru trei candidați. Nu contaminează proiectarea
lui HR-TU-pb-L; consumă însă aceeași rezervă de două ori. Decizie CEO.

## 13 — CE AR DEBLOCA

Enumăr doar variante care nu rescriu tăcut regulile:

1. **Acumulare prospectivă de M5.** Fișierul se oprește la `2026-07-27`. Date noi, dincolo de el, sunt
   curate prin construcție și necontaminate de N4, de E0xx și de breach. E singura cale către
   `CLEAN + adecvat`. Cost: timp calendaristic. La rata măsurată, `n ≥ 30` cere ~17 luni de M5 nou;
   `n ≥ 100` cere ~4,7 ani. **Cifra asta e argumentul cel mai tare pentru a nu risipi V1.**
2. **Acceptarea explicită a lui `V1` ca `PARTIALLY_CONSUMED`**, cu limitarea scrisă: verdictul nu poate
   fi numit independent, ci `OUT_OF_SAMPLE_SAME_DIVISION`, cu etichetele `LOW_POWER` (~38 tranzacții) și
   `REGIME_ALIGNED` (bull +223,3%, candidat long-only). Rapid, dar cumpără mai puțin decât pare.
3. **Un al doilea instrument sau alt simbol** pe care mecanismul să fie testat — nu rezolvă noutatea
   temporală, dar testează dacă mecanismul e mecanism, nu potrivire.
4. **Reducerea multiplicității înainte de a cheltui dovezi:** candidatul e cel mai bun din 84. O
   re-selecție pre-înregistrată pe DEV, cu penalizare de multiplicitate explicită, ar spune dacă rr2
   supraviețuiește propriei familii înainte să consume o partiție.

Recomand **(1) combinat cu (4)**: nu cheltui `V1` acum. Puterea pe care o cumperi (~38 tranzacții pe un
regim aliniat) nu justifică pierderea definitivă a singurei rezerve mari rămase.

---

## 14 — PREDARE CĂTRE RED TEAM

Ce e gata de atacat, deși protocolul nu e înghețat: identitatea candidatului (§1), verdictul de
fidelitate arhitecturală (§2), reproducerea independentă și cele trei corecții (§4), auditul de noutate
cu inventarul `date_range` (§5), derivarea regiunilor cu hashuri (§6), porțile contingente (§8).

Ținta principală de atac, formulată de mine împotriva mea: **§5.2 e o inferență, nu o demonstrație.**
Am arătat că 17+ studii ale aceleiași divizii au consumat calendarul propus și că E028 e adiacent ca
familie de mecanism — **nu** am demonstrat că vreunul a influențat proiectarea lui HR-TU-pb-L. Cine
susține că influența e nulă trebuie să explice de ce canalul de cunoaștere al analistului nu contează;
cine susține că e fatală trebuie să arate canalul. Am raportat exact ce am putut măsura.

---

```
HR_TU_PB_L_FRESH_VALIDATION_EVIDENCE_REQUIRED
HR_TU_PB_L_CANDIDATE_IDENTITY_FROZEN
HR_TU_PB_L_ARCHITECTURE_FIDELITY_PASS
N4_CONSUMPTION_RELEVANCE_TO_HR_TU_PB_L = IRRELEVANT
HR_TU_PB_L_GATES_PREREGISTERED_CONTINGENT_ON_CEO_EVIDENCE_RULING
```

*Fără execuție de validare. Fără acces Alpha la V1–V4. Fără AI Trader, Strategy Catalog, LIVE_SHADOW,
broker sau tranzacții. Cel mai înalt statut al candidatului rămâne `research candidate`.*
