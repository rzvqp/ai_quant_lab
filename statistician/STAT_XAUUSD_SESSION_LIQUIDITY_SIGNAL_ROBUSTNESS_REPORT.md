# XAUUSD — AUDIT DE ROBUSTEȚE AL SEMNALULUI DE LICHIDITATE DE SESIUNE

**Divizia Statistician · `STAT-XAUUSD-SESSION-LIQUIDITY-SIGNAL-ROBUSTNESS-001` · 2026-08-22**

```
SESSION_LIQUIDITY_SIGNAL_WEAK
FRESH_SESSION_SIGNAL_EVIDENCE_REQUIRED
```

**Reproducerea e exactă.** Semnalul **există** și e temporal robust — pozitiv în 5/5 blocuri
cronologice și în toți cei 3 ani. Nu îl închid.

Dar trei măsurători îl reduc la altceva decât pare:

```
1. Corelatia intre "% din drum deja consumat" si P(atinge mid), pe cele 6 straturi = 0,982
2. La S4 distanta MEDIANA ramasa pana la mid este -4,8 pips  (pretul e DEJA sub tinta)
3. Testul PERECHE (acelasi episod, S1 fata de PROPRIUL sau S0): S1 adauga +0,008
```

Verdictul e `WEAK` pentru cuvântul din definiția ta: **LATE**. Semnalul e real, dar sosește după drum.

`DEV-only. Zero CALIB, zero V1, zero 2025+. Nicio redesenare de execuție, niciun stop nou, nicio țintă nouă.`

---

## 1 — §2 IDENTITATEA ARTEFACTULUI

| element | valoare din cod (`722a0e0`) |
|---|---|
| fișiere | `session_trap.py` blob `04a03f0dc877` · `session_trap2.py` blob `ea74e4a5572a`, ambele @ `722a0e0` · `m5_data.py` `1339e74a5e05` |
| TF | **M15**, agregat cauzal din M5-ul gated (`m5_data`) |
| **ASIA** | `00:00–07:00 UTC` **fix** (Tokyo 09–16 JST; Japonia nu are DST) |
| **LONDON** | `08:00–16:00` local `Europe/London`, prin `tz_convert` |
| **NEW YORK** | `08:00–17:00` local `America/New_York`, prin `tz_convert` |
| **OVERLAP** | `london & newyork` |
| Asia range | `hi = max(high)`, `lo = min(low)`, `mid = (hi+lo)/2` pe barele Asia; acceptat dacă `≥12` bare M15 |
| **sweep** | primul `i` cu `uh ≥ 7`, `high[i] > asia_hi`, în London **sau** NY — **unul singur pe zi** |
| **S1 return-inside** | primul `k > sweep` cu `close[k] < asia_hi`, în **≤ 8** bare M15 |
| **S2 bearish displacement** | `(open[k] − close[k]) > 1.0 × ATR14` și `close[k] < open[k]`, în ≤ 10 bare după S1 |
| **S3 failed reclaim** | `high[k] ≥ asia_hi` și `close[k] < asia_hi`, `k > ret` |
| **S4 structure break** | `close[k] < min(low[ret−5 … k−1])` și `close[k] < open[k]`, `k ≥ ret+1` |
| **S5** | primul displacement bearish după S3 |
| **outcome primar** | `hit_mid` = `low[k] ≤ asia_mid` **intrabar**, în ≤ 24 bare M15 de la `entry+1`, **și înainte de a atinge `sweep_hi + 0.1·ATR`** |
| split | pe **zi**, cronologic, `cut` la 60% din zilele-parinte |
| cost | `2,4` pips (doar în faza de execuție) |

**Firewall:** exclusiv `m5_data` → loaderul gated. Zero `read_csv`, zero N4, zero 2025+, zero CALIB.

> **★ Notă asupra outcome-ului (§7), pentru că schimbă interpretarea:** `hit_mid` **nu** e
> „P(prețul atinge mijlocul)". E `P(atinge mijlocul ÎNAINTE de a atinge sweep_hi + tampon, în 6 ore)`.
> Outcome-ul are un **stop încorporat**. Îl îngheț așa cum e, dar orice citire ca probabilitate pură de
> mișcare e greșită.

## 2 — REPRODUCERE: **EXACTĂ**

Am rulat `session_trap2.py` integral (importă `session_trap`). Toate cifrele se confirmă:

```
strat   DISC n  P(mid)  P(low) |  CONF n  P(mid)  P(low)
S0         197   0.462   0.228 |     131   0.397   0.221
S1         152   0.553   0.296 |     103   0.466   0.282
S2          86   0.779   0.465 |      50   0.760   0.540
S3          94   0.468   0.266 |      61   0.344   0.230
S4          58   0.948   0.586 |      34   0.912   0.676
S5          27   0.778   0.444 |      17   0.765   0.706
TRAP n=254 P(mid)=0.508  |  VALID BREAKOUT n=74 P(mid)=0.189   separare +0.319
329 sweep-uri parinte: LONDON 232 · NY 14 · OVERLAP 83
executie CONF (mid): S1 -0.281 · S2 -0.333 · S4 -0.288 · S5 -0.343
```

Nu emit `SESSION_LIQUIDITY_SIGNAL_REPRODUCTION_FAIL`.

### ★ 2.1 Ce apare în reproducere și nu în raportul Alpha

**Scara „monotonă" nu e monotonă.** `S3` (failed reclaim) dă `0,468 / 0,344` — **sub S1** (`0,553 / 0,466`).
`S5` (`0,778 / 0,765`) e sub `S4`. Secvența raportată **S0 → S1 → S2 → S4** e o **subsecvență aleasă**
dintr-un lanț de șase; `S3` și `S5` o rup. Vezi §11 pentru de ce.

### ★ 2.2 Un defect real, cosmetic, găsit în cod

`dt` are dtype `datetime64[s, UTC]` (pandas 2.x), deci `uday = dt.floor("D").astype("int64")` e în
**secunde**, nu nanosecunde. `session_trap.py` tipărește însă data de cut cu
`pd.to_datetime(cutday, unit='ns')` → afișează **1970-01-01**. **Logica splitului e corectă** (comparație
numerică `r["d"] < cutday`); doar eticheta tipărită e greșită. Semnalez fiindcă e o capcană pentru
oricine reia codul. *(Am căzut eu însămi în ea la prima trecere — vezi §14.)*

---

## 3 — §3 AUDIT DE SESIUNE / FUS ORAR / DST

```
offseturi observate pe tot DEV:   London - UTC in {0, +1}     NY - UTC in {-5, -4}
Asia = 00:00-07:00 UTC FIX -> imun la DST prin constructie (Japonia nu are DST)
```

**Teste explicite de frontieră DST** (zilele de tranziție sunt duminici; unde piața e închisă nu există
bare — le raportez ca atare, nu le ascund):

```
EU 2021-10-31 offset London = [0]    EU 2023-03-26 = [+1]    EU 2023-10-29 = [0]
US 2021-11-07 offset NY     = [-5]   US 2023-03-12 = [-4]    US 2023-11-05 = [-5]
EU 2021-03-28 / 2022-03-27 / 2022-10-30 : fara bare (duminica)
US 2021-03-14 / 2022-03-13 / 2022-11-06 : fara bare (duminica)
```

**DST-ul e tratat corect.**

### Cauzalitatea intervalului Asia

```
zile cu Asia-range acceptat = 564 ; bare Asia per zi: min = P25 = mediana = max = 28
=> pragul ">=12 bare" NU se activeaza NICIODATA; fereastra Asia e INTOTDEAUNA completa
toate barele de sweep au uh >= 7 ; bare de sweep in interiorul ferestrei Asia: 0
```

**Niciun bar de sesiune ulterioară nu se scurge în Asia range, și invers.** §3 = **PASS**.

## 4 — §4 IDENTITATEA EVENIMENTULUI-PĂRINTE

```
329 inregistrari parinte  =  329 ZILE UTC UNICE     (bucla e `for d in days`, ia PRIMUL sweep -> parinte = ZIUA)
bare peste Asia High per episod: mediana 2, max 10
S1 = 255 · S2 = 140 · S3 = 156 · S4 = 92 · S5 = 46   -- toate SUB-MULTIMI ale acelorasi 329 de zile
perechi de zile-parinte CONSECUTIVE calendaristic: 196/328 = 59,8%
```

**Unitatea corectă de observație este ZIUA**, și codul o respectă deja: nu există dublă numărare de
bare din același episod. Acesta e un punct **bun** al implementării Alpha și îl consemnez.

## 5 — §5 DIMENSIUNEA EFECTIVĂ

Orizontul de outcome e 24 bare M15 = **6 ore** de la semnal → rămâne în aceeași zi, deci **nu există
suprapunere de ferestre între zile**. `n_eff ≈ n_zile` pentru fiecare strat luat separat.

**★ Dar straturile NU sunt patru eșantioane independente.** `S4 ⊂ S1 ⊂ S0` pe **aceleași** zile. A
compara `S4` (n=92) cu `S0` (n=329) ca și cum ar fi populații distincte e o comparație între o
submulțime selectată și întregul din care a fost selectată — vezi §12.

Iar 59,8% dintre zilele-părinte sunt **calendaristic consecutive**, deci episoadele sunt grupate
temporal: bootstrap-ul la nivel de zi (§13) e minimul necesar, nu o precauție.

---

## 6 — ★★ §10/§20/§21/§22 ANALIZA LA MOMENTUL DE REPER

Aici se explică totul. Pentru fiecare strat am măsurat, **la momentul în care semnalul devine
cunoscut**: distanța rămasă până la `mid`, și cât din drumul `sweep_hi → mid` fusese deja parcurs.

| strat | n | P(mid) | **dist. rămasă (pips)** | **% din drum consumat** | lag (bare M15) | risc (pips) | **RR implicit** |
|---|---|---|---|---|---|---|---|
| S0 | 328 | 0,436 | 39,2 | 34,5% | 0 | 21,9 | **1,79** |
| S1 | 255 | 0,518 | 26,1 | 46,7% | 1 | 26,6 | 0,98 |
| **S2** | 136 | **0,772** | **10,0** | **83,0%** | 4 | 50,0 | **0,20** |
| S3 | 155 | 0,419 | 29,1 | 43,2% | 4 | 24,1 | 1,21 |
| **S4** | 92 | **0,935** | **−4,8** | **108,8%** | 6 | 62,5 | **−0,08** |
| S5 | 44 | 0,773 | 1,9 | 96,2% | 7 | 50,7 | 0,04 |

```
Pearson( % din drum consumat , P(mid) )  pe cele 6 straturi  =  0,982
```

### 6.1 §20 — verdictul asupra lui S4

**La S4 distanța mediană rămasă până la mijloc este `−4,8` pips: prețul e DEJA sub țintă** în peste
jumătate din cazuri. `P(mid) = 0,935` nu e o predicție, e în mare parte **măsurarea a ceva deja
întâmplat**. Iar `S3` — care consumă doar 43,2% din drum — dă `0,419`, **sub S1**, exact cum prezice
dreapta de mai sus.

```
S4 = HIGH_DIRECTIONAL_CERTAINTY_BUT_LATE_INFORMATION      (confirmat numeric, nu prin intuitie)
```

### 6.2 §21 — verdictul asupra lui S2

`S2` e **cel mai bun compromis din familie**, și tot nu e bun: `83,0%` din drum consumat, `10,0` pips
rămași (**$1,00**) față de un risc median de `50,0` pips (**$5,00**) → **RR implicit `0,20`**.

---

## 7 — ★★ §9/§15 AUDITUL CONTROLULUI POTRIVIT

### 7.1 Defectul, așa cum e construit

```python
trap = [r for r in recs if r["ret"] is not None]     # clasificare cunoscuta abia dupa <=8 bare
brk  = [r for r in recs if r["ret"] is None]
ps   = [outcome(r, r["sw"]) for r in rr]             # OUTCOME masurat DE LA BARA DE SWEEP
```

**Fereastra de clasificare (≤8 bare) e INTERIOARĂ ferestrei de outcome (24 bare), pentru ambele
grupuri.** Asta e exact ce interzice §9.

**Și e nested mecanic, nu doar procedural:**

```
din cele 74 "valid breakouts", 43 (58,1%) NU au inchis niciodata inauntru in fereastra de 24 de bare
     ->  P(mid) pentru ele = 0,023
a atinge Asia MID (care e SUB Asia HIGH) cere, practic, sa fi revenit deja inauntru
P(stopped): trap 0,591  vs  breakout 0,608   -- ambele grupuri sunt stopate la fel de des
```

Separarea `+0,319` e în bună măsură **definițională**.

### 7.2 Testul cauzal — și rezultatul e mai puternic, nu mai slab

Am reclasificat la `sw+8` (după ce fereastra de clasificare se închide) și am măsurat outcome-ul **de la
`sw+8` pentru ambele grupuri**:

```
TRAP      n=195  P(mid | de la sw+8) = 0,687
BREAKOUT  n= 74  P(mid | de la sw+8) = 0,176        separare CAUZALA = +0,512   (raportat: +0,319)
bootstrap la nivel de ZI: Alpha CI95 = [+0,207 ; +0,422]   CAUZAL CI95 = [+0,403 ; +0,616]  (nu contine 0)
```

**Separarea supraviețuiește și crește.** O raportez ca atare.

### 7.3 Dar nu e un test de informație — e un test de poziție

```
distanta mediana pana la Asia mid la sw+8:   TRAP  +26,3 pips   |   BREAKOUT  +83,5 pips
```

La momentul comparației cele două grupuri sunt la **distanțe complet diferite** de țintă. Grupul „trap"
e deja în interiorul intervalului; grupul „breakout" e sus, lângă stop. Întrebarea la care răspunde
`+0,512` nu e *„capcana prezice o scădere?"*, ci *„prețul e mai aproape de mijloc?"* — la care răspunsul
e cunoscut prin construcție.

---

## 8 — §11 TESTARE TEMPORALĂ (definiții deterministe; nimic de antrenat)

Cinci blocuri cronologice de zile-părinte, egale ca număr de zile.

```
blk  interval          S0 n/P      S1 n/P      S2 n/P      S4 n/P    liftS1   liftS2   liftS4
1    2021-07..2021-11  65/0.431   50/0.540   25/0.800   22/1.000   +0.109   +0.369   +0.569
2    2021-11..2022-12  66/0.515   47/0.660   30/0.800   16/0.938   +0.144   +0.285   +0.422
3    2022-12..2023-04  66/0.439   55/0.473   31/0.742   20/0.900   +0.033   +0.303   +0.461
4    2023-04..2023-08  66/0.470   54/0.500   25/0.720   18/1.000   +0.030   +0.250   +0.530
5    2023-08..2023-12  65/0.323   49/0.429   25/0.800   16/0.812   +0.105   +0.477   +0.489

lift S1: 5/5 pozitiv, medie +0.085 sd 0.050 -> t = 3.74
lift S2: 5/5 pozitiv, medie +0.337 sd 0.089 -> t = 8.41
lift S4: 5/5 pozitiv, medie +0.494 sd 0.058 -> t = 19.21
```

**Robustețea temporală e reală și e cel mai bun rezultat al acestui artefact.** Spre deosebire de coada
probabilistică (mandatul precedent), aici nimic nu se prăbușește la evaluare pe blocuri.

## 9 — §12 AN CU AN

```
2021 (82 zile) : S0 0.451 | S1 0.571 (+0.120) | S2 0.800 (+0.349) | S4 0.966 (+0.514)
2022 (54 zile) : S0 0.463 | S1 0.564 (+0.101) | S2 0.750 (+0.287) | S4 1.000 (+0.537)  [n(S4)=9]
2023 (193 zile): S0 0.422 | S1 0.484 (+0.062) | S2 0.766 (+0.344) | S4 0.907 (+0.486)
```

**Pozitiv în toți trei anii, pe toate cele trei straturi.** 2021 e parțial (începe 2021-07-27), 2022 are
doar 54 de zile-părinte, iar 2023 domină cu 193. Lift-ul S1 **scade monoton** pe ani
(`+0,120 → +0,101 → +0,062`).

## 10 — §13 SESIUNE (păstrate separate, cum ai cerut)

```
LONDON  232 zile | S0 0.411 | S1 0.452 | S2 0.717 | S4 0.912
NY       14 zile | S0 0.214 | S1 0.571 (n=7) | S2 1.000 (n=4) | S4 1.000 (n=2)
OVERLAP  83 zile | S0 0.542 | S1 0.717 | S2 0.875 | S4 1.000
```

**★ Efectul NU e omogen pe sesiuni.** `OVERLAP` e sistematic mai puternic decât `LONDON` la fiecare
strat. Iar în perioada de confirmare divergența e extremă: `S1 CONF` dă **LONDON n=80 → 0,362** vs
**OVERLAP n=22 → 0,864**. Cifra pooled `0,466` e o medie a două lucruri diferite.

**`NY` nu e o populație** (14 zile, `S4` pe `n=2`). Nu se poate afirma nimic despre ea.

## 11 — ★★ §6/§14 ATRIBUIRE PE PĂRINTE COMUN ȘI INCERTITUDINE LA NIVEL DE ZI

### 11.1 Intervale bootstrap pe episoade (unitatea de resamplare = **ziua-părinte**)

```
S0: n=328 P=0.436 CI95=[0.384,0.491]      S3: n=155 P=0.419 CI95=[0.342,0.497]
S1: n=255 P=0.518 CI95=[0.455,0.576]      S4: n= 92 P=0.935 CI95=[0.880,0.978]
S2: n=136 P=0.772 CI95=[0.699,0.838]      S5: n= 44 P=0.773 CI95=[0.636,0.886]
```

### 11.2 ★ Testul PERECHE — comparația pe care nimeni nu a făcut-o

Lift-urile din §8 compară o **submulțime selectată** (episoadele care ajung la S2/S4) cu **întreaga**
populație măsurată de la sweep. Comparația corectă e: pentru **exact aceleași episoade**, `P(mid)`
măsurat de la reperul S vs `P(mid)` măsurat de la **propriul lor** S0.

```
lift S1 vs PROPRIUL S0 (n=254):  +0.008   CI95 = [-0.012 ; +0.028]   CONTINE ZERO
lift S2 vs PROPRIUL S0 (n=135):  +0.104   CI95 = [+0.052 ; +0.163]
lift S4 vs PROPRIUL S0 (n= 91):  +0.121   CI95 = [+0.055 ; +0.198]
```

| | lift nepereche (§8) | **lift PERECHE** | factor |
|---|---|---|---|
| S1 | +0,085 | **+0,008** | ÷ 11 |
| S2 | +0,337 | **+0,104** | ÷ 3,2 |
| S4 | +0,494 | **+0,121** | ÷ 4,1 |

**`S1` — „return inside range", faptul central al raportului Alpha — nu adaugă NIMIC** odată comparat cu
propriile sale episoade. `S2` și `S4` adaugă real, dar **10–12 puncte procentuale, nu 34–49**.

**Răspunsul la §6 („care eveniment adaugă informație care generalizează?"):**

```
S1 return-inside          -> +0.008   NU adauga informatie
S2 bearish displacement   -> +0.104   ADAUGA, dar tarziu (83% din drum consumat)
S4 structure break        -> +0.121   ADAUGA, dar PREA tarziu (pretul e deja sub tinta)
```

## 12 — §23 CARACTERIZAREA DRUMULUI DUPĂ S2 (diagnostic)

```
n=136  P(mid)=0.772   ★ P(face un nou maxim peste sweep_hi) = 0.507
MFE median 33,2 p · MAE median 26,0 p · timp median pana la mid = 1 bara M15
distanta ramasa la mid: P25 -6,6 · P50 10,0 · P75 23,2 pips
risc (stop = sweep_hi + tampon): P25 34,1 · P50 50,0 · P75 71,2 pips
RR implicit spre mid: median 0,20 | RR >= 1 in 11,8% | RR >= 1,5 in 4,4%
recompensa ramasa mediana = $1,00   (10 pips = 1 USD)
```

**Peste jumătate din episoade fac un nou maxim peste sweep-high după S2.** Asta explică fără rest de ce
execuția e negativă: stopul structural e exact acolo. **Și timpul median până la mijloc e 1 bară M15** —
mijlocul se atinge aproape instantaneu, fiindcă e deja aproape.

## 13 — §24 ROBUSTEȚE PE REGIM (M15 nu are etichetă de regim; am aliniat cauzal la H1)

```
S2:  RANGE n=76 P=0.750 | TREND_UP n=29 P=0.793 | REGIME_INDEP n=19 P=0.842 | TREND_DOWN n=9 P=0.889 | TRANSITION n=3 P=0.333
S4:  RANGE n=50 P=0.920 | TREND_UP n=17 P=1.000 | REGIME_INDEP n=14 P=0.929 | TREND_DOWN n=7 P=1.000 | TRANSITION n=4 P=0.750
```

**Semnalul supraviețuiește în `TREND_UP`** (`S2` n=29 → 0,793), ceea ce e strategic relevant pentru un
portofoliu SHORT. Nu cere `TREND_DOWN`. Punct favorabil.

## 14 — §16/§17/§18/§19 SELECȚIE, MULTIPLICITATE ȘI DIAGNOSTICE POST-HOC

**Spațiul de căutare, enumerat din cod:**

```
6 straturi (S0..S5) x 2 tinte (MID / LOW) x 2 split (DISC/CONF)          = 24 celule directionale
+ 3 sesiuni x 2 split la S1                                              =  6
+ bucket-uri: latime Asia (4) + magnitudine sweep (4) + ora Londra (4)   = 12
```

Testele sunt puternic dependente (straturile sunt **imbricate**), deci **nu aplic Bonferroni**. Dar
semnalez lucrul decisiv: **secvența raportată `S0→S1→S2→S4` e o subsecvență aleasă dintr-un lanț de
șase**, iar cele două noduri omise (`S3`, `S5`) sunt tocmai cele care rup monotonia. Selecția
subsecvenței monotone e o alegere post-hoc, chiar dacă toate șase au fost tipărite.

**§17 lățimea Asia · §18 ora din zi · §19 magnitudinea sweep-ului** — toate trei sunt calculate în
`session_trap2.py` **pe TOT DEV, fără split DISC/CONF**:

```
latime Asia   [0,50) -0.351 | [50,80) -0.240 | [80,120) -0.195 | [120,+) +0.126 (n=17)
magnitudine   [0,10) -0.330 | [10,25) -0.186 | [25,60) -0.018 | [60,+) -0.136     <- NEmonoton
ora Londra    [7,9) -0.045 | [9,11) -0.354 | [11,13) -0.494 | [13,17) -0.217      <- toate negative
```

```
POST_HOC_DIAGNOSTIC   pentru toate trei  (nepredeclarate, neconfirmate pe un split retinut)
SWEEP_MAGNITUDE_NOT_SUPPORTED_AS_DISCRIMINATOR   -- nemonoton si negativ in toate bucket-urile
```

Bucket-ul „Asia range larg" e **un singur bucket cu n=17**, pozitiv, descoperit pe toate datele. **Nu îl
promovez.** Ora din zi: „cel mai puțin rău" nu e un rezultat.

> **Auto-corecție, prinsă în timpul auditului.** La prima trecere am raportat intern „0/328 zile-părinte
> consecutive", concluzionând că episoadele sunt separate temporal. Era greșit: căzusem exact în capcana
> de la §2.2 — am împărțit cheia de zi (în **secunde**) la nanosecunde pe zi. Cifra corectă e
> **196/328 = 59,8% consecutive**, adică exact concluzia opusă. Corectat înainte de publicare.

---

## 15 — §25 SEMNAL vs EXECUȚIE, separate

```
SIGNAL ROBUSTNESS  : real, temporal robust, dar TARZIU si mult mai mic decat raportat  (§8, §11)
CURRENT EXECUTION  : UNSOLVED -- reprodus diagnostic, negativ pe CONFIRMARE la toate straturile
                     (S1 -0.281 · S2 -0.333 · S4 -0.288 · S5 -0.343)
```

**Nu tratez execuția negativă drept dovadă împotriva semnalului** — și, simetric, **nu tratez
`P(mid) = 0,93` drept alpha executabil**. §12 arată de ce sunt compatibile: `RR` implicit `0,20` și
`P(nou maxim) = 0,507`.

## 16 — §28 VERDICT

```
SESSION_LIQUIDITY_SIGNAL_WEAK
```

Motivat punct cu punct față de definițiile tale:

- **Nu e `NOT_SUPPORTED`.** Efectul nu dispare și nu se inversează: `5/5` blocuri cronologice pozitive,
  toți cei 3 ani pozitivi, iar lift-ul **pereche** al lui `S2` (`+0,104`) și `S4` (`+0,121`) are
  intervale bootstrap la nivel de zi care **exclud zero**. Supraviețuiește și în `TREND_UP`. Nu e
  explicat integral de dependență sau selecție.
- **Nu e `SUPPORTED`.** Controlul potrivit e, prin construcție, un test de **poziție**, nu de
  informație (§7.3). Lift-urile raportate sunt umflate de 3–11× față de comparația pereche (§11.2).
  `S1` — faptul central al raportului — adaugă **+0,008**. Iar cele două straturi care adaugă ceva real
  sosesc după ce **83%** și, respectiv, **109%** din drum e consumat.
- **Este `WEAK`, pe cuvântul din propria ta definiție: LATE.** *„directionally interesting effect
  remains but evidence is too concentrated, **late**, dependent, or small for execution research."*
  Recompensa mediană rămasă la `S2` e **$1,00** față de un risc de **$5,00**, iar `RR ≥ 1` apare în
  `11,8%` din cazuri.

## 17 — §30 STATUT DE ELIGIBILITATE

```
FRESH_SESSION_SIGNAL_EVIDENCE_REQUIRED
```

**Dar spun clar ce ar rezolva și ce NU ar rezolva evidența nouă.**

Mai multe date **nu vor rezolva** problema principală. Lateness-ul nu e o chestiune de eșantion — e o
**proprietate structurală** a definițiilor: `S2` și `S4` sunt definite prin evenimente care se produc
*în timpul* mișcării pe care o prezic. Cu `n` de zece ori mai mare, `S4` va avea în continuare distanța
mediană rămasă negativă.

**Ce ar rezolva** e un **reper mai devreme** — un eveniment observabil la S0 sau S1 care să separe
episoadele care vor ajunge la S2 de cele care nu. Aceea e o **întrebare de cercetare nouă**, nu o
variantă a acesteia, și **nu o proiectez aici** (§26 interzice orice semnal nou).

**Ce recomand concret, fără a consuma nicio dovadă:**

1. **Retragerea formulării „P(reach Asia midpoint)".** Metrica are un stop încorporat (§1) și trebuie
   numită `P(atinge mid înainte de sweep_hi + tampon, în 6 ore)`.
2. **Retragerea afirmației despre `S1`.** Lift-ul pereche e `+0,008`; „return-inside" nu e semnalul.
3. **Repararea controlului potrivit**: clasificare la `sw+8`, outcome de la `sw+8`, **și potrivire pe
   distanța până la țintă** — altfel comparația rămâne un test de poziție.
4. **Separarea permanentă a sesiunilor.** `OVERLAP` și `LONDON` nu sunt aceeași populație
   (`0,864` vs `0,362` pe confirmare); `NY` nu e o populație.

**Nu identific un semnal preferat pentru cercetare de execuție** (§29 se aplică doar la `SUPPORTED`).
Dacă CEO decide totuși să continue, singurul candidat rezonabil ar fi **`S2`**, cu limitarea scrisă că
oferă `$1,00` mediană împotriva unui risc de `$5,00`.

## 18 — LIMITĂRI ALE PROPRIULUI MEU AUDIT

1. Testul pereche (§11.2) compară `P(mid)` de la reper cu `P(mid)` de la sweep **pe aceleași episoade**,
   dar cele două măsurători au **ferestre de 24 de bare decalate**; o parte din diferență e efect de
   fereastră, nu de informație. E conservator în direcția corectă (subestimează, nu supraestimează
   lift-ul), dar nu e un experiment curat.
2. Blocurile temporale sunt **egale ca număr de zile**, nu ca durată calendaristică; blocul 2 acoperă
   13 luni, blocul 5 doar 4.
3. Nu am rulat un test de permutare pentru multiplicitate; am argumentat de ce (§14) dar nu am demonstrat.
4. `S4` pe `2022` are `n = 9`; cifra de `1,000` de acolo nu are conținut.
5. Nu am investigat de ce `OVERLAP` e sistematic mai puternic decât `LONDON` — poate fi volum, poate fi
   ora, poate fi artefact de eșantion. E o întrebare deschisă, nu un rezultat.

---

```
SESSION_LIQUIDITY_SIGNAL_WEAK
FRESH_SESSION_SIGNAL_EVIDENCE_REQUIRED
REPRODUCTION = EXACT  ·  DST_AUDIT = PASS  ·  ASIA_RANGE_CAUSALITY = PASS
PARENT_UNIT = ZIUA (329 zile unice, o inregistrare pe zi -- implementare corecta)
corelatie(% drum consumat, P(mid)) pe 6 straturi = 0,982
S4: distanta mediana ramasa = -4,8 pips  ->  HIGH_DIRECTIONAL_CERTAINTY_BUT_LATE_INFORMATION
S2: 83% din drum consumat, $1,00 ramas vs $5,00 risc, RR>=1 in 11,8%
lift PERECHE: S1 +0.008 (CI contine 0) · S2 +0.104 · S4 +0.121   (nepereche: +0.085 / +0.337 / +0.494)
matched control: fereastra de clasificare INTERIOARA celei de outcome; versiunea cauzala separa +0.512
                 dar grupurile sunt la 26,3 vs 83,5 pips de tinta -> test de POZITIE, nu de informatie
temporal: 5/5 blocuri pozitive, 3/3 ani pozitivi  ·  supravietuieste in TREND_UP
SWEEP_MAGNITUDE_NOT_SUPPORTED_AS_DISCRIMINATOR  ·  latime/ora = POST_HOC_DIAGNOSTIC
CURRENT_EXECUTION = UNSOLVED (reprodus, negativ pe CONF la toate straturile)
```

*Niciun candidat creat. Nicio redesenare de execuție. Fără CALIB, V1, 2025+ sau holdout final.
Fără promovare, fără AI Trader, fără broker, fără live.*
