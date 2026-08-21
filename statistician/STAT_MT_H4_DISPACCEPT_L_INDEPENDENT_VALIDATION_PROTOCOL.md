# MT-H4-dispaccept-L — PREGĂTIREA VALIDĂRII INDEPENDENTE

**Divizia Statistician · `STAT-MT-H4-DISPACCEPT-L-INDEPENDENT-VALIDATION-PREP-001` · 2026-08-21**

```
MT_H4_DISPACCEPT_L_FRESH_VALIDATION_EVIDENCE_REQUIRED
```

**Protocolul NU e înghețat. Nicio validare executată. `V1` neconsumat.**

Acesta e cel mai solid candidat din serie. **Gate M se reproduce independent și TRECE — inclusiv
împotriva unei referințe mai dure pe care am construit-o eu.** Traiectoria trece. Cauzalitatea trece.

Trei lucruri însă nu trec, și le numesc exact:

```
MT_H4_DISPACCEPT_L_EARLIER_ENTRY = NON_CAUSAL / LOOKAHEAD
MT_H4_DISPACCEPT_L_FROZEN_POLICY_STATISTICALLY_INCONCLUSIVE   (t = 1,14 · IC include zero)
MT_H4_DISPACCEPT_L_ACCEPTANCE_SEMANTICS_MISNAMED
```

---

## 1 — §2 IDENTITATEA, ÎNGHEȚATĂ

**Ramură de harness**, ca predecesorii: `multitf_campaign.eval_tf(tf="H4", mech="dispaccept",
long=True, rr=1.5)`. Nu există obiect izolat de strategie. Auditul Gate M trăiește separat în
`gate_m_dispaccept.py`, care **reutilizează** `gate_m_audit.py`.

| element | valoare din cod |
|---|---|
| amprente | `multitf_campaign.py` `0989e1d4e6bc` · `gate_m_audit.py` `f8d3b342f6c1` · `gate_m_dispaccept.py` `744d376111e2` · `m5_data.py` `1339e74a5e05`, toate @ `e2e975c` |
| TF / direcție | **H4** (agregat cauzal din M5 gated, `nsub ≥ 24` din 48) · **LONG** |
| **displacement** (bara `d`) | **`close[d] − open[d] > 1.0 × ATR14_H4[d]`** |
| **„acceptance"** (bara `d+1`) | **`close[d+1] > close[d]`** — vezi §5, e denumire greșită |
| bara de semnal | `i = d+1` |
| intrare | **`open[d+2]`** |
| **SL** | `min(low[i−4 … i]) − 0.15 × ATR14_H4[i]`, cu `i = d+1` (swing de 5 bare terminat în bara de acceptare) |
| **TP** | `entry + 1.5 × risk` |
| RR | nominal **1,5** · **efectiv 1,500 exact** (ținta derivă din același `entry` și același `risk`) |
| hold maxim | 48 bare H4 = 8 zile, apoi ieșire la închidere |
| podea de stop | `max(5·tick, 0.10·ATR_H4)` — **activată în 0,0%** |
| cost | `tick 0,01` · STRESS round-trip **0,24** · BASE `0,05` |
| serializare | `mstrat.simulate`: `last = xi` (index de **ieșire**), `if ei <= last: continue` |
| dedup / cooldown | niciunul în plus |
| dependențe | fără regim, fără sesiune, fără TF superior |

**Firewall verificat pe lanțul Gate M:** zero `read_csv` pe `data/market`, zero N4, zero
`shadow_driver`, zero 2025+.

## 2 — §3 CRONOLOGIA CAUZALĂ, EXPLICITĂ

| moment | ce e cunoscut | ce se face |
|---|---|---|
| închiderea barei `d` | OHLC complet al lui `d`, `ATR14[d]` | se evaluează `c[d] − o[d] > 1.0·ATR[d]` |
| închiderea barei `d+1` | OHLC complet al lui `d+1` | se evaluează `c[d+1] > c[d]`; se calculează `stop = min(low[d−3 … d+1]) − 0.15·ATR[d+1]` |
| **deschiderea barei `d+2`** | prețul de deschidere | **INTRARE** la `o[d+2]`; `risk = |o[d+2] − stop|`; `target = o[d+2] + 1.5·risk` |
| barele `d+2 … d+49` | evoluție | se verifică **stop ÎNAINTE de țintă** în fiecare bară (conservator) |

```
LUMANARE H4 INCOMPLETA         : NU  -- fiecare conditie foloseste doar bare inchise
INCHIDERE VIITOARE             : NU
HIGH/LOW VIITOR                : NU  -- stopul se calculeaza pe bare <= d+1
FILL FAVORABIL PE ACEEASI BARA : NU  -- intrarea e la deschiderea barei d+2, iar mersul incepe la d+2
```

**§3 = PASS.** Nicio scurgere în candidatul înghețat.

## 3 — §5 REPRODUCEREA CANDIDATULUI ÎNGHEȚAT: **EXACTĂ**

```
SERIALIZAT (politica inghetata)   GROSS +0.2056 · BASE +0.2038 · STRESS +0.1972
  n=41  WR 0.341  medR -0.070  PF 1.477  maxDD 3.91 R  pierdere max -1.019 R
  P25/P50/P75 R = -1.007 / -0.070 / +1.488
  avg castigator +1.252 (n=20) · avg perdant -0.807 (n=21)
  mix iesiri: 13 tinta / 15 stop / 13 TIMP (31,7%)   hold median 27 bare H4, max 49
  RR nominal 1,5 = RR efectiv 1,500 EXACT · podea 0,0%
  medSL 318,9 p ($31,89) · medTP 478,4 p · medMAE 220,4 p · medMFE 277,3 p
  sd 1,113 · se 0,174 · t = 1,14 · IC95 = [-0,143 ; +0,538]
```

`n = 41`, `WR = 0,341`, `STRESS = +0,1972` — **identic** cu ce a raportat Alpha. Zero dezacorduri.

### ★ 3.1 Prima constatare care schimbă lectura: **IC-ul politicii înghețate include zero**

`t = 1,14`. Politica pe care s-ar face validarea nu e distinsă statistic de zero **nici pe datele pe
care a fost descoperită**. Semnalul brut e mai puternic (§4), dar **obiectul de validat e politica.**

### ★ 3.2 A doua constatare: mediana tranzacției e **negativă** (`−0,070`), 20 câștiguri / 21 pierderi

## 4 — §6 REPRODUCEREA GATE M: **PASS, independent, și mai puternic decât a raportat Alpha**

Am re-implementat simulatorul per-semnal eu însămi (nu am importat `gate_m_audit`), verificând că
reproduce politica serializată prin motorul ratificat `mstrat.simulate`.

```
RAW per-semnal (trajectory-free = valoarea SEMNALULUI), STRESS
  M0  toate barele H4 LONG        n=2601  WR 0.333  avgR +0.0109  PF 1.019  b10rem -0.1533
  M1  dispaccept (INGHETAT)       n=  76  WR 0.368  avgR +0.2622  PF 1.679  b10rem +0.1330
  M2  ema20>ema50                 n=1467  WR 0.372  avgR +0.1056  PF 1.194  b10rem -0.0476
  EFF efficiency-L (comparatie)   n= 339  WR 0.351  avgR +0.0803  PF 1.153  b10rem -0.0730
BASE: M0 +0.0390 · M1 +0.2689 · M2 +0.1317
```

Toate cifrele lui Alpha (`+0,011 / +0,262 / +0,106`) **se reproduc**.

### ★ 4.1 Am testat o referință MAI DURĂ decât a folosit Alpha

`M2` al lui Alpha e doar `ema20 > ema50`. **Eticheta `TREND_UP` a proiectului e mai strictă:
`ema20 > ema50` ȘI `effic > 0.30`.** Am construit-o (`M2strict`) fiindcă e baremul corect:

```
                                        n      avgR      b10rem
M2strict  PROJECT TREND_UP             503   +0.0144   -0.1494
dispaccept INSIDE M2strict              33   +0.3620   +0.2390
M2strict NOT dispaccept                470   -0.0100   -0.1768     <- NEGATIV
  => INCREMENTAL fata de baseline: +0.3476   fata de complement: +0.3720

(pentru comparatie, cu M2 al lui Alpha: incremental +0.1715 · fata de complement +0.1774)
```

**Sub referința mai dură incrementul se DUBLEAZĂ**, iar complementul devine negativ. Am căutat un mod
de a slăbi concluzia și am găsit unul care o întărește. O raportez ca atare.

```
INCREMENTAL_ALPHA_OVER_H4_TREND_BETA_PASS   (confirmat independent, sub doua referinte)
```

## 5 — §7 ATRIBUIREA COMPONENTELOR + §8 SEMANTICA

Populația-părinte comună = **evenimentele de displacement** `d` (`n = 141`; 75 acceptate = 53,2%,
66 respinse).

```
D0  baseline ema20>ema50                          n=1467  avgR +0.1056  b10rem -0.0476
D1  displacement singur, semnal d -> intrare d+1   n= 141  avgR +0.1254  b10rem -0.0277
D2  disp+ACCEPT (inghetat), semnal d+1 -> d+2      n=  75  avgR +0.2589  b10rem +0.1275
D2' disp+RESPINS, semnal d+1 -> d+2  (CONTROLUL)   n=  66  avgR -0.0729  b10rem -0.2291
```

**A. Displacement-ul singur adaugă aproape nimic:** `D1 − D0 = +0,0197`.

**★ B. Testul pe care Alpha nu l-a făcut, și care e cel decisiv.** `D2 vs D1` confundă condiția cu bara
de intrare. Comparația corectă e **accepted vs rejected, pe același părinte și la ACEEAȘI bară de
intrare `d+2`**:

```
acceptat d+2  +0.2589      respins d+2  -0.0729      =>  VALOAREA ACCEPTARII = +0.3318
```

Aceeași geometrie, aceeași bară de intrare, același părinte. **Acceptarea poartă tot alpha-ul**, iar
selecția e curat separată de efectul de timing. Concluzia lui Alpha e corectă și **acest test o face
mai tare decât a formulat-o el**.

### §8 — ce este de fapt „acceptance"

`close[d+1] > close[d]`. Nu există niciun nivel; nu e „acceptance" în sensul structural (preț acceptat
*deasupra unui nivel*). E, literal:

```
POST_DISPLACEMENT_SECOND_CLOSE_PERSISTENCE   (follow-through)
= bara de dupa un displacement bullish inchide peste inchiderea barei de displacement
```

**Numele candidatului trebuie să spună asta.** Recomand descrierea canonică
`H4 displacement + follow-through (a doua închidere), intrare la a treia bară`. Nu păstrez cuvântul
„acceptance" doar fiindcă l-a folosit Alpha.

## 6 — ★★ §4 OBSERVAȚIA DE „INTRARE MAI DEVREME": **NON-CAUZALĂ**

Alpha raportează diagnostic `+0,478` pentru o intrare cu o bară mai devreme, față de `+0,259`
înghețat, și îl numește „costul acceptării = −0,219". **Am reprodus cifrele și am găsit de ce sunt ce
sunt.**

```
constructia lui Alpha:  Dacc = { d : close[d+1] > close[d] }   apoi   INTRARE la open[d+1]
                        n=75  avgR +0.4782      (reprodus exact)

  criteriul  close[d+1] > close[d]  e cunoscut abia la INCHIDEREA barei d+1
  intrarea   open[d+1]              are loc INAINTE de acea inchidere
  ->  O BARA H4 INTREAGA DE LOOKAHEAD (4 ore)
```

Se selectează exact barele în care prețul a urcat în timpul lui `d+1` și apoi se intră la începutul
acelei bare. Nu e o strategie; e cunoașterea rezultatului.

**Alternativa cu adevărat cauzală** — „intră mai devreme" înseamnă a intra la `d+1` **pe fiecare**
displacement, fiindcă acceptarea nu poate fi știută încă:

```
D1 (cauzal, intrare d+1 pe toate cele 141)   avgR = +0.1254
frozen d+2 cu acceptare (n=75)               avgR = +0.2589
```

**Deci nu există niciun „cost al așteptării". Costul e negativ: așteptarea aduce `+0,1335`.**
Comparația lui Alpha era cu un reper inaccesibil.

```
EARLIER_ENTRY = NON_CAUSAL / LOOKAHEAD
```

**Nu** îl clasific `FUTURE_NEW_VERSION_RESEARCH_REQUIRED`, fiindcă nu e o strategie distinctă
implementabilă — e o măsurătoare invalidă. Candidatul înghețat rămâne neschimbat, iar §7 al raportului
Alpha (`acceptance cost`) trebuie **retras**, nu reținut ca îmbunătățire viitoare.

## 7 — §9 AUDITUL DE TRAIECTORIE: **PASS**, și metoda lui Alpha îl dezavantaja

```
A) TRAIECTORII VALIDE (start mai tarziu; politica implementabila cronologic), 45 offseturi
   min +0.1800 · p05 +0.1934 · MEDIANA +0.3095 · medie +0.3142 · p95 +0.4797 · max +0.5371
   % negative = 0,0%      canonica +0.1972 la PERCENTILA 8,9  (aproape de minim -> conservatoare)

B) varianta lui Alpha (ordine ALEATOARE de procesare), 200 de rulari
   min -1.0141 · p05 -0.8757 · mediana +0.4894 · p95 +1.4881 · % negative = 20,5%
   canonica la percentila 30,5

C) RAW SIGNAL +0.2622   vs   SERIALIZED POLICY +0.1972    ->  serializarea COSTA, nu ajuta
```

**Amendament metodologic.** Varianta (B) amestecă *ordinea de procesare* a semnalelor, apoi aplică
`ei > last`. Asta nu e o traiectorie de tranzacționare: nu poți sări o tranzacție din ianuarie fiindcă
vei lua una din martie. De acolo vine `p05 = −0,88` pe care Alpha îl citează drept avertisment.
**Sub traiectorii valide nu există niciun rezultat negativ.**

**Semnalul rămâne pozitiv independent de traiectorie** (`+0,2622` fără nicio cale) — cerința §9 e
satisfăcută, iar `TRAJECTORY_ROBUST` se confirmă cu o metodă mai curată decât cea folosită.

## 8 — §10 AUDITUL DE COADĂ: **divergență semnal / politică**

```
                        top1    top2    top4    top8     medR    b1rem    b5rem   b10rem
RAW  M1 (n=76)          9,0%   16,5%   31,5%   61,5%   +0,327   +0.2419  +0.2075 +0.1330
SER  M1 (n=41)         22,1%   40,6%   77,5%  151,4%   -0,070   +0.1575  +0.1232 +0.0491
```

- **Semnalul e BROAD_BASED** — top 4 din 76 = 31,5%, mediană pozitivă, `b10rem +0,133`. Justificat.
- **Politica serializată NU este.** `top 4 din 41 = 77,5%`; `top 8 = 151,4%`, adică **celelalte 33 de
  tranzacții sunt net negative**. `b10rem` scade la `+0,0491`.

`BROAD_BASED_ALPHA` e **justificat pentru semnal, NU pentru politica înghețată**. Nu emit
`TAIL_CONCENTRATION_DISQUALIFYING` (motivul structural rămâne: `rr` fix la 1,5 plafonează R-ul, max
observat `+1,786`), dar poarta de concentrare trebuie să se aplice **politicii**, nu semnalului.

## 9 — §11 ROBUSTEȚE TEMPORALĂ: o corecție necesară

```
RAW M1     2021: n=15  +0,423     2022: n=13  +0,017     2023: n=48  +0,278
SERIALIZAT 2021: n= 9  +0,060     2022: n= 8  -0,130     2023: n=24  +0,358
baseline M0        -0,085 ... (2021)   M2  -0,021 (2021)   M2strict  -0,356 (2021)
baseline M2        2021 -0,021 · 2022 +0,269 · 2023 +0,101
```

**Ce se susține, și e remarcabil:** în 2021 — anul în care `M0`, `M2`, `M2strict` și `efficiency-L`
**pierd toate** — semnalul dă `+0,423`. Asta e argumentul cel mai bun împotriva ipotezei „beta pe
bull", și îl susțin.

**★ Ce trebuie corectat:** afirmația „pozitiv în TOȚI cei trei ani" e adevărată doar pentru **semnalul
brut**, iar `2022 = +0,017` e practic zero pe 13 semnale. **Pe politica înghețată — obiectul care s-ar
valida — 2022 este NEGATIV (`−0,130`).** Formularea din commit trebuie precizată.

**Și o observație pe care o semnalez fără să blochez:** în 2022 baseline-ul `M2` dă `+0,269`, adică
**mai mult decât candidatul** (`+0,017` raw, `−0,130` serializat). Incrementul nu e stabil pe ani;
e concentrat în 2021 și 2023.

## 10 — §12 GEOMETRIA ECONOMICĂ

```
RR nominal 1,5  =  RR efectiv median 1,500  =  mediu 1,500 (exact, prin constructie)
RAW : SL median 302,4 p ($30,24) · TP median 453,6 p ($45,36) · P25/P50/P75 TP = 368 / 454 / 573
      %TP >=70 = 100 · >=80 = 100 · >=100 = 100 · >=150 = 100 · >=200 = 98,7 · >=300 = 82,9 · >=400 = 64,5
SER : SL median 318,9 p ($31,89) · TP median 478,4 p · >=300 = 87,8% · >=400 = 65,9%
```

**Cel mai mare obiectiv economic din program** și **fără tautologie** — nu există filtru de spațiu
minim; ținta rezultă din stopul structural H4. Observație de dimensionare: **riscul median e ~$31 per
tranzacție**, adică 319 pips de proiect; e o strategie de swing pe ~4,5 zile mediană.

## 11 — §13 CALIBRAREA

```
semnale CALIB: 22    serializat: n=13
serializat  GROSS +0.2306 · BASE +0.2290 · STRESS +0.2230 · WR 0.462 · PF 1.478 · medR -0.012
            sd 1,253 · se 0,347 · t = 0,64 · IC95 = [-0,458 ; +0,904]
            top 2 din 13 = 103,2% din profit  ->  celelalte 11 sunt net negative
raw n=22    +0.4909 · WR 0.545 · medR +1.491 · b10rem +0.3905
```

```
CALIB_ADEQUACY = INSUFFICIENT
```

`t = 0,64`, IC include zero, `se = 0,347` e de 1,5× media estimată. Nu reinterpretez CALIB ca validare
independentă și, la acest `n`, nici ca sprijin.

## 12 — §14 AUDITUL DE NOUTATE

**`MECHANICAL_DATA_CONSUMPTION` — ABSENT.** Poarta gated se oprește fizic la `2024-06-20 00:40Z`;
`N4 = 0`, `read_csv = 0`, `2025+ = 0`, `shadow_driver = 0` pe tot lanțul, inclusiv `gate_m_*`.
Pragurile `1.0·ATR` și `RR 1.5` sunt constante declarate, fără grid.

**`ANALYST_KNOWLEDGE_CONSUMPTION` — PREZENT**, pentru exact familiile enumerate la §14: `≥17` studii
de edge Flow A committed au `date_range 2022-12-16 → 2025-10-23` (cinci merg la `2026-07-13`), iar
Flow A **este** Alpha Discovery Laboratory. Direct relevante: **`E028` Fibonacci OTE** („intrare de
**continuare**"), **`E011`** failed 3-drive, **`E026`** ADR exhaustion (persistență a mișcării),
`E012` inverted FVG. `2025-10-23 → 2026-07-13` rămâne **CONSUMAT** prin breach-ul holdout-ului terminal
(`PROJECT_STATE_v2 §8.23`).

## 13 — §15/§16 EVIDENȚĂ ȘI SUFICIENȚĂ

Rata măsurată a politicii înghețate: **41 / 2.652 bare H4 DEV = 1 la 64,7** (CALIB: 13/725 = 1 la 55,8
— coerent). Numărătoare **exclusiv pe coloana `time`**, fără a inspecta niciun rezultat.

| regiune | interval | bare H4 | **N așteptat** | status |
|---|---|---|---|---|
| **V1** | `2024-07-10 → 2025-10-23` | 1.988 | **30,7** | `PARTIALLY_CONSUMED` |
| **V2** | `2025-10-23 → 2026-02-17` | 482 | 7,5 | `CONSUMED` |
| **V3** | `2026-03-10 → 2026-06-20` | 434 | 6,7 | `CONSUMED` |
| **V4** | `2026-07-13 → 2026-07-27` | 64 | **1,0** | `CLEAN` |

*(Amprentele `ohlc_sha256` sunt înghețate la `6d4430a` §6.)*

```
N >= 30  : atins MARGINAL, doar in V1 (30,7) -- si V1 NU e curat
N >= 50  : nicaieri            necesar ~3.234 bare H4 = ~1,5 ani de M5 nou
N >= 100 : nicaieri            necesar ~6.468 bare H4 = ~3,0 ani
```

**Nicio regiune nu e simultan `CLEAN` și `SUFFICIENT`.** `V4` — singura curată — dă **o** tranzacție.

★ Și chiar dacă `V1` ar fi curat: cu ~31 de tranzacții și o eroare standard de ordinul `1,11/√31 ≈ 0,20`,
un test acolo nu ar putea distinge `+0,20` de `0`. **Puterea, nu curățenia, e constrângerea binding.**

## 14 — §17 REDUNDANȚĂ ÎN FAMILIA H4

```
                                 n     |cap|   %din M1   Jaccard   avgR propriu (raw)
MT-H4-momentum-L (3 inchideri)  315      48      63,2%     0,140      +0,2360
MT-H4-efficiency-L (effic>0.4)  339      30      39,5%     0,078      +0,0803
MT-H4-structure-L               219      20      26,3%     0,073      +0,1396
MT-H4-pullback-L                340      14      18,4%     0,035      +0,2573
TR breakout+displacement         69      11      14,5%     0,082      +0,3592
                          M1 dispaccept  76                            +0,2622
```

**★ Cea mai apropiată rudă NU e niciunul dintre candidații comparați de Alpha, ci `MT-H4-momentum-L`:
63,2% din semnalele lui `M1` sunt și semnale de momentum**, iar momentum-L are un `avgR` propriu de
`+0,2360`, aproape de `+0,2622` al candidatului. Alpha nu a făcut această comparație.

```
MT_H4_DISPACCEPT_L_MECHANISM_CLASS = RELATED_BUT_DISTINCT
   (ruda cea mai apropiata: MT-H4-momentum-L, 63,2% acoperire -- NU efficiency-L, NU familia breakout)
```

**Nu e `DUPLICATE`** (36,8% din semnale sunt exclusiv ale lui, Jaccard 0,140) și nu e
`PARAMETRIC_VARIANT` (condiții diferite ca formă). Dar suprapunerea cu momentum-L trebuie declarată
în orice afirmație de complementaritate.

## 15 — ★ §18 RELAȚIA CU `breakout + displacement`: **populație genuin distinctă**

Comparație obligatorie, cerută explicit după auditul meu al lui `TR-H4-rng2trend_disponly-L`:

```
semnale comune M1 & breakout+displacement:  11 din 76 = 14,5%   Jaccard 0,082
M1 EXCLUZAND breakout+displacement:  n=65  raw avgR = +0.2435   (fata de +0.2622 pe tot M1)
suprapunerea comuna:                 n=11  raw avgR = +0.3728
suprapunere pe aceeasi ZI:           Jaccard 0,467
```

**Verdict:** `MT-H4-dispaccept-L` **nu** este „breakout+displacement + filtru de continuare întârziat".
Doar 14,5% din semnalele lui sunt semnale de breakout+displacement, iar eliminarea completă a
suprapunerii lasă `+0,2435` pe `n = 65` — edge-ul supraviețuiește.

**Dar semnalez o limitare pe care Alpha nu ar fi găsit-o:** la nivel de **zi**, suprapunerea e
**0,467**. Populațiile de semnal sunt distincte, dar cele două mecanisme ar fi **în piață simultan
aproape în jumătate din zilele lor**. Pentru orice afirmație de portofoliu, aceea e cifra relevantă,
nu Jaccard-ul pe bare.

## 16 — §19 PORȚI PRE-ÎNREGISTRATE (contingent, NU protocol înghețat)

Fixate acum, fără a fi văzut niciun rezultat în `V1–V4`.

```
MT_H4_DISPACCEPT_L_GATES_PREREGISTERED_CONTINGENT
```

| # | poartă | prag |
|---|---|---|
| A | fidelitate de specificație | `c[d]−o[d] > 1.0·ATR[d]` · `c[d+1] > c[d]` · intrare `o[d+2]` · SL swing 5 bare `−0.15·ATR[d+1]` · TP `entry+1.5·risk` · hold 48 · `nsub≥24` · blocaj o-poziție-o-dată. Orice abatere ⇒ **STOP** |
| B | N minim | `n ≥ 30` → altfel `INCONCLUSIVE`. `n < 100` ⇒ etichetă permanentă `LOW_POWER` |
| C | BASE | `> 0` la round-trip `0,05` |
| D | STRESS | `> 0` la round-trip **`0,24`** |
| **E** | **increment peste baseline potrivit pe regim** | **`avgR(candidat) > avgR(toate barele H4 LONG cu `ema20>ema50` din aceeași fereastră, aceeași geometrie)`.** Se raportează și față de `PROJECT TREND_UP` (`ema20>ema50 ȘI effic>0.30`) |
| F | robustețe cronologică | treimi fixate pe **bare H4**: ≥2/3 pozitive, niciuna sub `−0,10` |
| G | `best-1%-removed` | `> 0` (valid la `n ≥ 100`) |
| H | `best-5%-removed` | `> 0` |
| I | concentrarea profitului | **top 10% ≤ 60% din profit, măsurat pe POLITICA serializată** (DEV: 77,5% la top 4 ⇒ **poarta ar PICA pe DEV** — o consemnez ca prag ferm, nu retro-croit) |
| J | maxDD | `≤ 10 R` (DEV 3,91 R) |
| K | pierdere individuală maximă | `≤ 1,5 R` (DEV −1,019 R) |
| L | fidelitate RR efectiv | `1,500 ± 0,01` pe **fiecare** tranzacție |
| M | geometrie economică | `%TP ≥ 300` să rămână `≥ 60%` (DEV 87,8%) |
| **N** | **invarianță la traiectorie** | ≥45 traiectorii **valide** (start decalat cronologic), **≥90% pozitive**, canonica între P05 și P95. **Interzis explicit: amestecarea ordinii de procesare** (§7) |
| **O** | **fidelitate semantică de mecanism** | descrierea trebuie să spună **`displacement + follow-through (a doua închidere)`**, nu „acceptance". Și: `avgR(accepted d+2) > avgR(rejected d+2)` pe aceeași fereastră — testul matched din §5 |

Niciun prag nu se mișcă după rezultate.

## 17 — RĂSPUNSURI LA §1

| | |
|---|---|
| reproductibil mecanic | **DA**, exact |
| valid cauzal | **DA** pentru candidatul înghețat; **NU** pentru varianta „intrare mai devreme" |
| genuin incremental peste beta H4 | **DA** — `+0,1715` vs `ema20>ema50`, **`+0,3476`** vs `PROJECT TREND_UP`, complement negativ |
| tail robust | **DA pentru semnal** (top 4 = 31,5%); **NU pentru politică** (top 4 = 77,5%) |
| robust la traiectorie | **DA** — 0% negative pe traiectorii valide, canonica la percentila 8,9 |
| credibil temporal | **PARȚIAL** — semnalul e pozitiv în 2021 unde toate baseline-urile pierd, dar 2022 e `+0,017` raw și **`−0,130` serializat** |
| suficient specificat | **PARȚIAL** — ramură de harness; `nsub≥24` și blocajul de serializare trebuie să intre explicit în spec |
| eligibil pentru validare independentă | **NU** |
| dovezi proaspete și suficiente | **NU** — `V1` `PARTIALLY_CONSUMED` cu `N ≈ 31`; `V4` curat cu `N ≈ 1` |

## 18 — CE AR DEBLOCA

1. **Retragerea §7 din raportul Alpha** (`acceptance cost −0,219`). E o măsurătoare non-cauzală, iar
   lăsată în picioare va genera o „versiune îmbunătățită" construită pe lookahead. Costă zero.
2. **Redenumirea mecanismului** în `displacement + follow-through`, ca descrierea să corespundă
   codului. Costă zero.
3. **Poarta I, măsurată acum pe DEV.** Concentrarea politicii (top 4 = 77,5%) e singurul rezultat care
   contrazice profilul altfel sănătos al semnalului. Merită înțeleasă înainte de a cheltui dovezi.
4. **Acumulare prospectivă**: `n ≥ 50` cere ~1,5 ani de M5 nou — cel mai scurt orizont dintre toți
   candidații auditați, fiindcă frecvența e mai mare.

**Recomand (1) + (2) + (3), toate gratuite și imediate.** Nu recomand cheltuirea lui `V1`: la ~31 de
tranzacții, cu `se ≈ 0,20`, testul nu poate distinge `+0,20` de zero — iar `V1` e oricum
`PARTIALLY_CONSUMED`. **Acesta e însă primul candidat pentru care acumularea prospectivă are un
orizont rezonabil**, și e cel mai bun argument pentru a-l păstra viu.

## 19 — PREDARE CĂTRE RED TEAM

Gata de atacat: identitatea și cronologia explicită (§1–§2), reproducerea exactă (§3), **reproducerea
independentă a Gate M plus referința mai dură pe care am construit-o (§4)**, **testul matched
accepted-vs-rejected la aceeași bară de intrare (§5)**, **demonstrația de lookahead (§6)**, amendamentul
metodologic la testul de traiectorie (§7), divergența semnal/politică pe coadă și temporal (§8–§9),
redundanța cu `momentum-L` (§14), relația cu breakout+displacement inclusiv suprapunerea zilnică 0,467
(§15), porțile A–O (§16).

**★ AUTO-CORECȚIE, A TREIA OARĂ — regula se generalizează.** În prima redactare am scris `best-1%-removed = +0.2394` pentru semnalul brut. **Nu îl calculasem.** Măsurat: **`+0.2419`**. La ultimele două mandate am prins aceeași eroare pe amprente de blob (`32e69ab`, `6f8c922`) și îmi impusesem regula pentru *amprente*. Era prea îngustă: eroarea nu e despre hash-uri, e despre **orice număr**. Regula devine: **niciun număr nu intră într-un document înainte ca măsurătoarea care îl produce să fi rulat și să fi fost citită.** Toate celelalte cifre din acest raport provin din ieșirile rulate și citate mai sus.

**Auto-atac 1:** §4.1 folosește `PROJECT TREND_UP` ca referință „mai dură", dar acea definiție s-a
dovedit *mai slabă* ca beta (`+0,0144` față de `+0,1056`). Un adversar poate spune că am ales referința
față de care incrementul arată cel mai bine. Contra: am raportat **ambele**, iar `M2` al lui Alpha
rămâne referința mai conservatoare — și incrementul e pozitiv sub amândouă.

**Auto-atac 2:** §5 măsoară valoarea acceptării ca `accepted − rejected` la aceeași bară de intrare.
Asta e o comparație între două subseturi ale părintelui, nu un experiment randomizat; selecția rămâne
condiționată pe evoluția barei `d+1`, care e *și* parte din informația care prezice bara `d+2`. Nu am
un design care să separe „acceptarea prezice" de „acceptarea e deja o parte din mișcare".

**Auto-atac 3:** toate concluziile de coadă și de traiectorie se sprijină pe `n = 41` (politică) sau
`n = 76` (semnal). Sunt eșantioane mici, iar candidatul e cel mai bun din **56 de ID-uri** ale campaniei
multi-TF. `t = 2,07` (semnal) nu supraviețuiește unei corecții Bonferroni pe 56 (`t ≈ 3,2`).

---

```
MT_H4_DISPACCEPT_L_FRESH_VALIDATION_EVIDENCE_REQUIRED
MT_H4_DISPACCEPT_L_IMPLEMENTATION_AUDIT_PASS
MT_H4_DISPACCEPT_L_CAUSALITY_PASS  (candidatul inghetat)
MT_H4_DISPACCEPT_L_GATE_M_REPRODUCED_INDEPENDENTLY_PASS
INCREMENTAL_ALPHA_OVER_H4_TREND_BETA_PASS  (+0.1715 vs ema-cross · +0.3476 vs PROJECT TREND_UP)
MT_H4_DISPACCEPT_L_TRAJECTORY_ROBUST  (0% negative pe traiectorii VALIDE)
MT_H4_DISPACCEPT_L_SIGNAL_BROAD_BASED  /  FROZEN_POLICY_TAIL_CONCENTRATED (top4 = 77,5%)
MT_H4_DISPACCEPT_L_FROZEN_POLICY_STATISTICALLY_INCONCLUSIVE  (t = 1,14 · IC [-0,143 ; +0,538])
MT_H4_DISPACCEPT_L_EARLIER_ENTRY = NON_CAUSAL / LOOKAHEAD  (o bara H4 intreaga)
MT_H4_DISPACCEPT_L_ACCEPTANCE_SEMANTICS_MISNAMED -> POST_DISPLACEMENT_SECOND_CLOSE_PERSISTENCE
CALIB_ADEQUACY = INSUFFICIENT  (serializat n=13, t=0,64)
MECHANISM_CLASS = RELATED_BUT_DISTINCT  (ruda cea mai apropiata MT-H4-momentum-L, 63,2%)
NOT_A_BREAKOUT_DISPLACEMENT_VARIANT  (14,5% suprapunere de semnal; dar 0,467 pe ZILE)
GATES_PREREGISTERED_CONTINGENT (A-O)
```

*Fără execuție de validare. Fără consum de `V1`. Fără retuning Alpha. Fără versiune nouă de intrare.
Fără AI Trader, Catalog, broker, live.*
