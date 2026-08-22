# XAUUSD — AUDIT DE ROBUSTEȚE `POST-E1-CLEAN-P2`

**Divizia Statistician · `STAT-XAUUSD-POST-E1-CLEAN-P2-ROBUSTNESS-001` · 2026-08-22**

```
POST_E1_CLEAN_P2_IDENTITY_AMBIGUOUS          (§1 -- nu endosez obiectul combinat)
POST_E1_CLEAN_P2_SIGNAL_WEAK                 (§32 -- verdictul pentru REGULA SIMPLA R1)
FRESH_POST_E1_SURVIVABILITY_EVIDENCE_REQUIRED
```

Reproducerea e **exactă**, inclusiv cifrele pe care scriptul comis **nu le mai produce** (§4.2).

**Efectul e mai robust decât sugerează propria prudență a lui Alpha pe câteva axe** — 4/4 blocuri
temporale, `odds ratio 4,7`, 34 de zile aproape necorelate, iar controlul pe distanță lasă `+0,213`
din `+0,369`. Dar `N` și istoria selecției sunt exact atât de subțiri pe cât a spus Alpha, iar
**identitatea candidatului nu e înghețată**.

Două suspiciuni pe care le-am adus din auditul precedent **se infirmă la măsurătoare**, și le raportez
ca atare (§3.2, §3.3).

`DEV-only. Zero CALIB, V1, 2025+. Nicio cercetare de execuție, nicio retunare, nicio variantă de salvare.`

---

## 1 — ★★ §1 IDENTITATEA CANDIDATULUI: **AMBIGUĂ**

Am căutat mecanic în tot depozitul. `POST-E1-CLEAN-P2` apare **exclusiv** în raportul `.md`, unde e
definit astfel (linia 80):

> *„EARLY-TRAP-E1 parent + at P2, R1 (`net downside>0 AND bearish P2 M5 body`) **or** the 8-feature P2
> logistic → predict CLEAN_REVERSAL"*

**Conjuncția „or" leagă două obiecte matematic diferite sub un singur nume.** Nu sunt aceeași mulțime:
la P2, R1 selectează `n = 34`, iar bucket-ul modelului (`p ≥ DISC-q0.6`) selectează `n = 20` pe CONF cu
`P(clean) = 0,650` față de `0,647` la R1. Numere apropiate, mulțimi diferite.

**Nu există niciun obiect de cod** numit `POST-E1-CLEAN-P2`: fără `SIGNAL_ID`, fără `SIGNAL_VERSION`,
fără `implementation_fingerprint()`, fără `evaluate()`.

**★ Contrastul e decisiv, fiindcă laboratorul știe deja să facă asta.** Părintele are exact ce lipsește
aici:

```
early_trap_e1_signal.py :  SIGNAL_ID = "EARLY-TRAP-E1" · SIGNAL_VERSION = "1.0.0"
                           implementation_fingerprint() = 33bec4498e72a05c486ec1763854edac17cc9da82556932d0f3257d62f6c2a16
                           self-check care asserteaza n_fires == 118
```

Acel artefact există fiindcă **auditul meu precedent (`de35453`) l-a cerut**. Aceeași disciplină nu a
fost aplicată noului candidat.

```
=> POST_E1_CLEAN_P2_IDENTITY_AMBIGUOUS   (varianta D din §1)
```

**Ce fac în consecință.** Refuz să endosez statistic *obiectul combinat* (§1). Dar §32 cere un verdict
pentru **REGULA SIMPLĂ**, iar §28 separă explicit `R1_SIMPLE_RULE` de `P2_MODEL_CONTEXT`. `R1` e
neambiguu — îi pot citi cele două condiții exact din cod. **Auditez R1 ca obiect de sine stătător** și
tratez modelul strict ca **context** (§10).

## 2 — §2 PĂRINTELE ÎNGHEȚAT: **VERIFICAT EXACT**

```
SIGNAL_ID = EARLY-TRAP-E1     SIGNAL_VERSION = 1.0.0
implementation_fingerprint = 33bec4498e72a05c486ec1763854edac17cc9da82556932d0f3257d62f6c2a16
n_parents = 329 · n_fires = 118 · n_unique_days = 118
episoade cu landmark-uri P1-P4 complete = 118 / 118 · zile unice printre ele = 118
blob early_trap_e1_signal.py:  edbc687 = 64b9fa988f96   ==   5471136 = 64b9fa988f96   (IDENTIC)
```

**Părintele e neatins, byte-cu-byte.** Amprente ale artefactelor noi, măsurate: `post_e1_survive.py`
`3451fb93730b` · `post_e1_survive2.py` `8d099f860372`, ambele @ `5471136`.

---

## 3 — §3/§4/§5 CLASE, CONDIȚIONARE ȘI CAUZALITATE

### 3.1 Construcția claselor, recuperată din cod

```python
classify(e):  parcurge M15 de la e1+1, HORIZON = 32 bare, oprit la frontiera zilei UTC
              sweep_hi = max(high[sweep .. e1])
              daca high[j] > sweep_hi -> newhi = True
              daca low[j] <= asia_mid -> "A_clean" daca NOT newhi, altfel "B_newhi_then_mid"
              la epuizare: "C_newhi_never" daca newhi, altfel "D_none"
```

```
clase masurate: A_clean = 63 · B_newhi_then_mid = 36 · C_newhi_never = 19 · D_none = 0
CLEAN rate global = 0.534      DISC n = 70 · CONF n = 48
```

`D_none` **nu apare niciodată**: fiecare episod fie atinge mijlocul, fie face un nou maxim în orizont.

### 3.2 ★ Prima suspiciune pe care măsurătoarea o INFIRMĂ — conservatorismul intra-bară

`classify` marchează `newhi` **înainte** de a verifica `mid` în aceeași bară M15, deci o bară care le
face pe amândouă e clasificată `B`. Ordinea intra-bară e necunoscută la M15 — **deși M5 nativ există**.
Bănuiam că asta subestimează sistematic clasa A. **Măsurat:**

```
episoade in care PRIMA bara decisiva face AMANDOUA in aceeasi bara M15:  0 / 118  (0.0%)
```

**Convenția nu se activează niciodată.** Rămâne o infidelitate de proiectare (M5 era disponibil), dar
**efect zero**. O raportez fiindcă am căutat-o.

### 3.3 ★★ A doua suspiciune INFIRMATĂ — §4, condiționarea „încă nedecis"

`resolved` la `Pk` folosește **exclusiv barele M5 `P1..Pk`**:

```python
resolved = "newhi" if max(high[P1..Pk]) > sweep_hi else ("mid" if min(low[P1..Pk]) <= mid else "undecided")
```

Întrebarea din §4 e dacă a condiționa pe „încă nedecis" creează **immortal-time bias**: eticheta e
calculată global, de la `e1+1`, **înainte** de P2. Dacă vreun episod „undecided-at-P2" avea deja clasa
determinată înainte de finalul lui P2, condiționarea ar fi coliziune. **Măsurat:**

```
episoade 'undecided-at-P2' a caror clasa era DEJA determinata pe M15 inainte de finalul lui P2:  0 / 86
```

**Zero.** Pentru subsetul nedecis, eticheta e determinată **strict după P2**.

```
CONDITIONAREA = ANALIZA DE LANDMARK LEGITIMA
   nu immortal-time bias (nimic nu e deja rezolvat) · nu collider bias (filtrul foloseste doar bare <= Pk,
   e simetric fata de ambele rezultate, si nu conditioneaza pe nimic post-Pk)
```

### §5 Sincronizarea, verificată

```
P1 = prima bara M5 NATIVA cu time >= (e1_time + 900)   adica primul M5 complet dupa inchiderea M15 a lui E1
P2 = P1+1 · P3 = P1+2 · P4 = P1+3     contigue, trunchiate la frontiera zilei UTC
toate 118 episoadele au P1-P4 complete · fara bare partiale, fara M5 sintetic, fara interpolare
```

## 4 — §6 REPRODUCEREA: **EXACTĂ**

| | Alpha | reprodus | |
|---|---|---|---|
| P1 undecided `n` | ≈98 | **98** | ✓ |
| P2 undecided `n` | ≈86 | **86** | ✓ |
| P3 undecided `n` | ≈76 | **76** | ✓ |
| P4 undecided `n` | ≈56 | **56** | ✓ |
| P1 model DISC/CONF AUC | 0,643 / 0,660 | **0,643 / 0,660** | ✓ |
| P2 model DISC/CONF AUC | 0,786 / 0,774 | **0,786 / 0,774** | ✓ |
| P3 model DISC/CONF AUC | 0,802 / 0,898 | **0,802 / 0,898** | ✓ |
| P4 model DISC/CONF AUC | 0,710 / 0,804 | **0,710 / 0,804** | ✓ |
| R1 DISC lift | +0,217 | **+0,217** (`n=17`, `P=0,706`, bază `0,489`) | ✓ |
| R1 CONF lift | +0,237 | **+0,237** (`n=17`, `P=0,647`, bază `0,410`) | ✓ |

Nu emit `POST_E1_CLEAN_P2_REPRODUCTION_FAIL`.

### ★ 4.2 Dar scriptul comis **nu rulează până la capăt**

```
post_e1_survive2.py linia 72:  KeyError: 'remaining'
```

Blocul final — **exact cel care ar produce AUC-urile de model pe P1/P3** citate în raport — **crapă**
la prima iterație (`k=1`): `r["remaining"]` e setat doar pe populația undecided-at-**P2**, dar bucla
iterează peste undecided-at-**Pk**. **Deci cifrele `P3 0,802/0,898` și `P4 0,710/0,804` din raport nu
pot fi obținute executând artefactul comis.**

Le-am reprodus **eu**, reimplementând aceeași procedură (§9), și **se confirmă exact**. Deci cifrele
sunt corecte; **reproductibilitatea artefactului nu e.**

---

## 5 — ★★ §11/§12/§27 R1 PE PĂRINTELE COMUN

Populația = **undecided-at-P2**, `n = 86`, `P(clean) = 0,453`.

| | `n` | `P(clean)` | A / B / C | dist. rămasă |
|---|---|---|---|---|
| **părinte (toți undecided-at-P2)** | 86 | 0,453 | 39 / 31 / 16 | 25,6 p |
| `net_prog > 0` singur | 42 | 0,619 | 26 / 13 / 3 | 17,0 p |
| corp bearish P2 singur | 44 | 0,614 | 27 / 14 / 3 | 18,0 p |
| **R1 = ambele** | **34** | **0,676** | **23 / 9 / 2** | **16,3 p** |
| complement `NOT-R1` | 52 | 0,308 | 16 / 22 / 14 | 29,8 p |
| `net_prog>0` **dar NU** bearish | 8 | 0,375 | 3 / 4 / 1 | 27,5 p |
| bearish **dar NU** `net_prog>0` | 10 | 0,400 | 4 / 5 / 1 | 32,0 p |
| niciuna (derivat) | 34 | 0,265 | — | — |

```
lift fata de parinte   = +0.2230        lift fata de complement = +0.3688
risk ratio = 2.199                      ODDS RATIO = 4.705
```

**§27 — conjuncția contează.** Fiecare condiție singură dă `≈ 0,62`; **una fără cealaltă prăbușește
la `0,375` / `0,400`**, iar niciuna la `0,265`. Cele două nu sunt substituibile. Câștigul marginal al
conjuncției peste oricare condiție singură e modest (`+0,06`), dar structura e o scară curată.

## 6 — §20/§21 DESCOMPUNEREA CĂILOR ȘI REDUCEREA NOULUI MAXIM

```
                         P(clean)   P(new-high-FIRST)   P(mid EVENTUAL)   P(mid inainte de nou maxim)
R1                        0.676          0.324               0.941                 0.676
parinte undecided-at-P2   0.453          0.547               0.814                 0.453
EARLY-TRAP-E1 (118)       0.534          0.466               --                    0.534
```

**★ Afirmația științifică centrală (§21) se confirmă:**

```
P(new-high-first):  0.547  ->  0.324      reducere absoluta -0.223      reducere relativa -40.8%
```

Iar `P(mid eventual)` urcă de la `0,814` la `0,941`. **Reduce, nu elimină** — `32,4%` din episoadele
semnalate fac totuși un nou maxim întâi, exact cum a spus Alpha.

## 7 — ★★ §19 CONTROLUL PE DISTANȚĂ (analogul auditului pozițional de la E1)

R1 selectează episoade **deja mai avansate**:

```
distanta ramasa : R1 mediana 16.3p  vs  NOT-R1 29.8p
dist_to_sweep   : R1 mediana 13.9p  vs  NOT-R1  9.8p
% din drum consumat: R1 = 52.4%  vs  undecided-at-P2 = 30.6%
```

Stratificat pe **terțile**:

```
--- pe distanta ramasa ---
 t1 [ 3.4, 18.2): R1 n=22 P=0.727 | nonR1 n= 7 P=0.571 | dif +0.156
 t2 [18.2, 31.4): R1 n= 6 P=0.667 | nonR1 n=22 P=0.227 | dif +0.439
 t3 [31.4, 91.8): R1 n= 6 P=0.500 | nonR1 n=23 P=0.304 | dif +0.196
 => dif medie ponderata = +0.2129        (necontrolat +0.3688)

--- pe dist_to_sweep ---
 t1 [ 2.0,  9.3): R1 n= 8 P=0.500 | nonR1 n=21 P=0.095 | dif +0.405
 t2 [ 9.3, 17.2): R1 n=13 P=0.615 | nonR1 n=15 P=0.267 | dif +0.349
 t3 [17.2, 73.3): R1 n=13 P=0.846 | nonR1 n=16 P=0.625 | dif +0.221
 => dif medie ponderata = +0.3131        (necontrolat +0.3688)
```

**★ Rezultatul e net mai bun decât la `EARLY-TRAP-E1`.** Acolo, controlul pe distanță lăsa `+0,105`
din `+0,302` — **35%**. Aici lasă `+0,213` din `+0,369` — **58%** — și e **pozitiv în TOATE cele șase
straturi**, pe ambele axe de control. Efectul de poziție există, dar **nu explică majoritatea
separării**.

## 8 — §14 INCERTITUDINE CONȘTIENTĂ DE DEPENDENȚĂ

```
P(clean | R1) = 0.676   CI95 = [0.500 ; 0.824]      n = 34 episoade, 34 ZILE UNICE
lift vs parinte    = +0.2230   CI95 = [+0.0920 ; +0.3531]   nu contine 0
lift vs complement = +0.3688   CI95 = [+0.1652 ; +0.5713]   nu contine 0
```

**§13 — unitatea independentă:** `34 episoade = 34 zile unice` (o singură episodă pe zi, moștenit de la
părinte), iar orizontul se oprește la frontiera zilei ⇒ **fără suprapunere între zile**. Iar clusterizarea
temporală e **minimă**: doar **1 din 33** de perechi de zile R1 consecutive sunt calendaristic
adiacente. **`n_eff ≈ 34`** — nominalul și efectivul coincid. Acesta e un punct bun și îl consemnez.

## 9 — §15 TESTARE TEMPORALĂ (regulă fixă, blocuri cronologice de zile)

```
blk  interval             und n    base   R1 n  P(clean|R1)     lift   medRem
1    2021-07..2022-11        21   0.429      7      0.571     +0.143    19.6p
2    2022-11..2023-03        22   0.500      8      0.750     +0.250    15.7p
3    2023-03..2023-08        21   0.524     10      0.700     +0.176    15.2p
4    2023-08..2023-12        22   0.364      9      0.667     +0.303    14.8p

lift POZITIV IN 4/4 blocuri | medie +0.218 | sd 0.072
```

## 10 — ★ §16/§17 AN CU AN ȘI ONESTITATEA EȘANTIONULUI

```
2021: undecided n=14 base=0.429 | R1 n= 5  clean 3 / non-clean 2  P=0.600 lift=+0.171 CI95=[0.200 ; 1.000]
2022: undecided n=18 base=0.444 | R1 n= 5  clean 3 / non-clean 2  P=0.600 lift=+0.156 CI95=[0.200 ; 1.000]
2023: undecided n=54 base=0.463 | R1 n=24  clean 17 / non-clean 7 P=0.708 lift=+0.245 CI95=[0.500 ; 0.875]

TOTAL R1: n=34 | clean 23 | newhi-then-mid 9 | newhi-never 2 | DISC 17 / CONF 17
```

**★ Răspunsul explicit cerut la §16:** **2021 și 2022 sunt direcțional pozitivi dar statistic
NEINFORMATIVI.** Fiecare are **cinci** episoade, iar intervalul de încredere e `[0,200 ; 1,000]` — care
conține rata de bază, conține `0,5`, conține practic orice. **Numai 2023 e informativ** (`n = 24`, CI
`[0,500 ; 0,875]` exclude baza `0,463`).

**§17 — cât de multă evidență independentă susține de fapt candidatul:** `34` de episoade-zi, dintre
care **`24` (71%) sunt din 2023**. Rezultatul e **consistent cu un efect real promițător pe eșantion
mic**, nu cu un efect demonstrat pe trei ani.

## 11 — §18/§22 ECONOMIE ȘI COMPARAȚIE CU PĂRINTELE

| obiect | `n` | `P(clean)` | `P(newhi-first)` | dist. rămasă | latență |
|---|---|---|---|---|---|
| `EARLY-TRAP-E1` (toți) | 118 | 0,534 | 0,466 | 21,6 p † | E1 (0 min) |
| undecided-at-P2 | 86 | 0,453 | 0,547 | 25,6 p | P2 (10 min) |
| **`POST-E1 R1`** | **34** | **0,676** | **0,324** | **16,3 p** | **P2 (10 min)** |

† *Re-măsurat în convenția ACESTUI artefact* — `(close[E1] − asia_mid)/PIP` pe toate cele 118 — nu preluat din auditul precedent: **21,6 p**, `%consumat = 35,0%`. Coincide cu cifra din `de35453`, dar am verificat-o aici în loc s-o transport dintr-un alt artefact.

**★ O corecție de accent la raportul Alpha.** Raportul citează `~29–31%` din drum consumat la P2 — dar
acela e **populația undecided**. Pentru **subsetul R1**, `%consumat` median este **52,4%**, nu 31%.
Raportul menționează separat că subsetul de mare încredere păstrează `~16p`, ceea ce e corect — dar
titlul „~31% consumat" nu se aplică candidatului însuși. **R1 e mai târziu decât sugerează titlul**,
deși rămân `16,3` pips de mișcare.

## 12 — ★ §23/§24/§25 P1 / P2 / P3 / P4

```
Pk   und n  DISC n  CONF n  CONF clean/non  DISC AUC  CONF AUC   medRem  R1 n   R1 P(clean)
P1      98      53      45          18/27      0.643     0.660    24.4p    46      0.609
P2      86      47      39          16/23      0.786     0.774    25.6p    34      0.676
P3      76      42      34          15/19      0.802     0.898    25.5p    23      0.783
P4      56      30      26          12/14      0.710     0.804    28.0p    21      0.714
```

### ★ 12.1 §23 — a fost P2 ales pentru că rezultatele lui arătau atrăgător?

Codul are `K = 2` hardcodat, cu comentariul *„best timeliness/discrimination balance"*. **Cifrele nu
susțin acel comentariu:** `P3` are AUC **mai mare** pe ambele split-uri (`0,802/0,898` vs
`0,786/0,774`), `R1 P(clean)` **mai mare** (`0,783` vs `0,676`) și distanță rămasă **practic identică**
(`25,5p` vs `25,6p`). Pe criteriile declarate, **P3 domină P2**.

Singurul avantaj real al lui P2 e **eșantionul**: `86` vs `76` undecided, `34` vs `23` episoade R1.

```
=> P2 e DEFENSABIL, dar pe temei de MARIME A ESANTIONULUI, nu pe „echilibrul timeliness/discriminare"
   pe care il invoca codul. Justificarea declarata e gresita; alegerea nu e.
```

### ★ 12.2 §24 — scepticism față de `P3 CONF AUC = 0,898`

```
CONF n = 34   (15 clean / 19 non-clean)
DISC 0.802  ->  CONF 0.898     -- CRESTE la iesirea din esantion
```

Un model potrivit pe DISC care obține **AUC mai mare pe CONF decât pe DISC** e semnul unui **CONF
norocos**, nu al unui landmark mai bun: un model regularizat nu poate „generaliza mai bine decât s-a
antrenat" decât prin variație de eșantion. Cu `15 vs 19` clase pe CONF, o singură pereche de ranguri
mută AUC-ul cu ~0,003, iar câteva perechi îl mută cu 0,05. **Nu promovez P3.**

### 12.3 §25 — atriția la P4

`P4` păstrează doar `56` din `118` episoade (`47,5%`). Populația e **selectată prin supraviețuire**:
sunt exact episoadele care nu s-au rezolvat în 20 de minute. Nu creez candidat; consemnez că
`DISC 0,710` (sub P2 și P3) sugerează că la P4 **informația scade**, nu crește.

## 13 — §26 ATRIBUIRE UNIVARIATĂ (DISC → CONF, la P2)

```
feature              P1 D/C     P2 D/C     P3 D/C     stabil DISC->CONF?
net_prog           0.67/0.64  0.74/0.74  0.78/0.83   DA, si e componenta lui R1
last_bear_body     0.67/0.64  0.73/0.70  0.68/0.75   DA, si e componenta lui R1
downside_prog      0.64/0.56  0.69/0.68  0.67/0.84   DA
ratio_dn_up        0.60/0.60  0.68/0.68  0.67/0.77   DA
dist_to_sweep      0.60/0.86  0.69/0.87  0.71/0.88   ★ INSTABIL -- CONF mult peste DISC
consec_lower_close 0.53/0.52  0.70/0.63  0.69/0.68   partial
last_close_loc     0.32/0.37  0.32/0.28  0.38/0.28   informativ INVERS, stabil
```

**★ `dist_to_sweep` e cazul de urmărit:** `DISC 0,60–0,71` dar `CONF 0,86–0,88` la toate landmark-urile.
O diferență de `+0,17…+0,26` între descoperire și confirmare, în **favoarea** confirmării, e un semn de
instabilitate de eșantion mic, nu de putere. **Și e exact feature-ul pe care se bazează `R2`** — regula
care dă `CONF n = 4, P = 1,000`. **Consemnez, nu construiesc nimic pe el.**

Cele două componente ale lui `R1` (`net_prog`, `last_bear_body`) sunt, la P2, **cele mai puternice două
features univariate pe DISC** (`0,74` și `0,73`) și rămân stabile pe CONF. **R1 e justificabil pe
DISCOVERY singură.**

## 14 — §7 CRONOLOGIA SELECȚIEI

```
LANDMARK P2 : CONFIRMATION_SELECTED
              `K=2` e hardcodat DUPA ce tabelul univariat a tiparit P1/P2/P3 pe DISC **si CONF**.
REGULA R1   : DISCOVERY_JUSTIFIABLE  (componentele sunt top-2 pe DISC)
              dar EVALUATA pe CONF alaturi de R2 si R3, si retinuta dintre trei.
FEATURES model: 8 din 12, alese dupa tabelul univariat DISC+CONF -> CONFIRMATION_SELECTED
PRAG model  : q0.6 pe DISC (corect), dar bucket-ul evaluat pe CONF.
```

**Penalizarea evidențială, cuantificată:** dintre cele trei reguli tipărite, `R2` are lift DISC mai mare
(`+0,280`) dar `CONF n = 4`; `R3` are `+0,177/+0,161`. `R1` e reținută fiindcă e singura cu lift bun
**și** `n` rezonabil pe ambele split-uri. **Asta e o alegere informată de CONF.** Efectul practic e
însă limitat: `R1 ⊂ R3`, iar `R3` — regula cea mai simplă posibilă, fără nicio alegere — dă tot lift
pozitiv pe ambele split-uri. **Semnalul nu depinde de a fi ales `R1` în locul lui `R3`.**

## 15 — §8 MULTIPLICITATE

```
4 landmark-uri (P1..P4)
x 12 features univariate, fiecare tiparit pe DISC SI CONF   = 96 celule de AUC afisate
+ 3 reguli (R1/R2/R3) x 2 split-uri                          =  6
+ 1 model (8 din 12 features) + 1 prag                       =  2
+ diagnostice de sesiune / an
```

**Nu aplic Bonferroni**: landmark-urile sunt **imbricate** (undecided-at-P3 ⊂ undecided-at-P2 ⊂ P1),
features-urile sunt puternic corelate (`net_prog`, `downside_prog`, `ratio_dn_up` măsoară aceeași
mișcare), iar `R1 ⊂ R3`. Numărul efectiv de teste independente e de ordinul **4–6**, nu 96.

**Rămâne P2/R1 material neobișnuit după conștientizarea selecției?** `odds ratio 4,705` cu
`CI [+0,165 ; +0,571]` pe diferența față de complement, **pozitiv în 4/4 blocuri temporale și în toate
cele 6 straturi de control pe distanță** — da, rămâne neobișnuit. Multiplicitatea nu e obiecția
principală aici; **`N` este**.

## 16 — §28 MODELUL DE 8 FEATURES (strict CONTEXT)

```
features: net_prog · dist_to_sweep · downside_prog · ratio_dn_up · last_bear_body ·
          consec_lower_close · dist_to_e1hi · failed_extend      (8 din cele 12 evaluate)
antrenare: ridge logistic IRLS, l2 = 3.0, mu/sd INGHETATE pe DISC   (corect)
prag: q0.6 pe probabilitatile DISC  (corect)   -> bucket evaluat pe CONF: n=20, P(clean)=0.650, ~17p
DISC AUC 0.786 -> CONF AUC 0.774   (degradare mica, sanatoasa)
```

**Oferă informație peste R1?** Marginal și neconcludent: bucket-ul modelului dă `0,650` pe `n = 20`
CONF, iar `R1` dă `0,647` pe `n = 17` CONF. **Practic identice**, cu mulțimi diferite. Modelul include
`dist_to_sweep`, feature-ul instabil de la §13.

```
P2_MODEL_CONTEXT = NU_ADAUGA_INFORMATIE_DEMONSTRABILA_PESTE_R1
(nu contaminează verdictul pentru regula simplă, conform §28)
```

## 17 — §29 SESIUNE (diagnostic, cu prudență)

```
LONDON : undecided n=76 base=0.447 | R1 n=30 P=0.633
OVERLAP: undecided n= 8 base=0.500 | R1 n= 3 P=1.000
NY     : undecided n= 2 base=0.500 | R1 n= 1 P=1.000
```

**Populația e efectiv London-only.** `OVERLAP` și `NY` au `3` și `1` episoade R1 — fără conținut. Nu se
poate afirma nimic despre heterogenitate de sesiune, și **nu se creează niciun filtru** (§29).

## 18 — LIMITĂRI ALE PROPRIULUI MEU AUDIT

1. Controlul pe distanță (§7) folosește **terțile pe o singură dimensiune** deodată. Un control comun
   (distanță × dist_to_sweep) ar fi mai riguros, dar cu `n = 34` celulele ar avea 2–4 observații.
2. Terțilele 2 și 3 de distanță rămasă au `R1 n = 6` fiecare — diferențele `+0,439` și `+0,196` de
   acolo sunt fragile; media ponderată e purtată de terțila 1 (`n = 22`).
3. Blocurile temporale sunt **egale ca număr de zile**, nu ca durată: blocul 1 acoperă 16 luni,
   blocul 4 doar 4.
4. Am reprodus AUC-urile de model P1–P4 **reimplementând** procedura din `post_e1_survive2.py`, fiindcă
   blocul original crapă. Reproduc exact cifrele raportate, dar dacă Alpha a folosit o variantă subtil
   diferită care dă aceleași patru perechi de numere, nu aș putea distinge.
5. Nu am testat sensibilitatea lui `R1` la perturbări (prag nenul pe corpul bearish, `net_prog > ε`) —
   §30/§32 interzic orice variantă.
6. `HORIZON = 32` bare M15 și trunchierea la frontiera zilei UTC sunt moștenite; nu le-am modificat,
   dar înseamnă că `P(mid eventual)` e condiționat de acel orizont.

---

## 19 — §32 VERDICT PENTRU REGULA SIMPLĂ

```
POST_E1_CLEAN_P2_SIGNAL_WEAK
```

Verificat punct cu punct față de definiția `SUPPORTED`:

| condiție §32 | verificare |
|---|---|
| regula exactă **se reproduce** | **DA** — `+0,217` DISC / `+0,237` CONF, exact |
| **istoria selecției e acceptabilă** | **PARȚIAL** — `R1` e justificabil pe DISC, dar **landmark-ul P2 e ales informat de CONF**, iar identitatea candidatului nu e înghețată (§1) |
| lift supraviețuiește **părinte comun / dependență / temporal** | **DA** — `+0,223` CI `[+0,092 ; +0,353]`; `34` zile aproape necorelate; **4/4** blocuri |
| `P(new-high-first)` **material redusă** | **DA** — `0,547 → 0,324`, `−40,8%` relativ |
| **rămâne distanță economică utilă** | **DA** — `16,3 p` mediană, deși `52,4%` din drum consumat |

**De ce nu `SUPPORTED`:** trei motive, în ordinea greutății.

1. **`N`.** `34` episoade totale, din care **24 (71%) în 2023**. `2021` și `2022` au **cinci** episoade
   fiecare, cu `CI = [0,200 ; 1,000]` — **neinformative**, nu doar mici. Efectul e demonstrat pe **un
   singur an**.
2. **Identitatea nu e înghețată** (§1). Nu se poate acorda `READY_FOR_CANONICAL_FREEZE` unui obiect
   definit printr-un „sau" între o regulă și un model, fără artefact de cod și fără amprentă.
3. **Landmark-ul e ales informat de CONF**, iar `P3` — care domină `P2` pe criteriile declarate — a
   fost respins printr-o justificare pe care cifrele nu o susțin.

**De ce nu `NOT_SUPPORTED`:** efectul **nu dispare sub controale**. `58%` din separare supraviețuiește
controlului pe distanță și e **pozitiv în toate cele 6 straturi**; `4/4` blocuri temporale; `odds ratio
4,7`; conjuncția e genuin necesară; iar condiționarea la landmark s-a dovedit **legitimă**, nu un
artefact.

## 20 — §33 URMĂTORUL PAS

```
FRESH_POST_E1_SURVIVABILITY_EVIDENCE_REQUIRED
```

**Ce ar rezolva, și ce nu.** Spre deosebire de semnalul de lichiditate de sesiune (unde problema era
*structurală* — lateness — și date noi nu ar fi ajutat), **aici problema e pur de eșantion**. Rata e
`34` episoade R1 la `118` părinți pe ~2,4 ani, adică `~14` pe an. Pentru ca `2021`-`2022` să devină
informative ar trebui **ordinul a 25–30 de episoade R1 per an**, deci evidență nouă, nu o re-analiză.

**Trei condiții pe care le atașez, toate gratuite:**

1. **Îngheață `R1` ca artefact de cod**, exact ca `early_trap_e1_signal.py`: `SIGNAL_ID`,
   `SIGNAL_VERSION`, `implementation_fingerprint()`, self-check care asertează `n = 34` la P2 pe
   părintele `33bec449…`. **Fără asta nu există candidat, doar o propoziție.**
2. **Retrage disjuncția.** `POST-E1-CLEAN-P2` trebuie să fie **ori** regula, **ori** modelul — nu
   „R1 sau modelul". Recomand **regula**: e transparentă, justificabilă pe DISC, și modelul nu adaugă
   informație demonstrabilă peste ea (§16).
3. **Repară scriptul comis** (`KeyError` la linia 72) și corectează justificarea lui `K=2`: motivul
   real e mărimea eșantionului, nu „echilibrul timeliness/discriminare".

**Nu recomand** trecerea la `P3` (AUC mai mare dar `CONF n = 34` și degradare inversă), nici la `R2`
(`CONF n = 4`), nici vreo variantă de salvare.

---

```
POST_E1_CLEAN_P2_IDENTITY_AMBIGUOUS   (varianta D -- "R1 SAU modelul", fara obiect de cod)
POST_E1_CLEAN_P2_SIGNAL_WEAK          (verdict pentru REGULA SIMPLA R1)
FRESH_POST_E1_SURVIVABILITY_EVIDENCE_REQUIRED
REPRODUCTION = EXACT (10/10 cifre, inclusiv cele pe care scriptul comis nu le mai produce)
PARINTE VERIFICAT: fingerprint 33bec449... · 118 fires · 118 zile · blob IDENTIC edbc687 == 5471136
CONDITIONAREA LA LANDMARK = LEGITIMA  (0/86 deja rezolvate inainte de P2; 0/118 ambiguitate intra-bara)
R1: n=34 (34 zile unice, 1/33 consecutive) · P(clean) 0.676 vs parinte 0.453 vs complement 0.308
    lift +0.223 CI [+0.092,+0.353] · OR 4.705 · P(newhi-first) 0.547 -> 0.324 (-40.8% relativ)
CONTROL PE DISTANTA: +0.213 din +0.369 supravietuieste (58%), pozitiv in TOATE cele 6 straturi
TEMPORAL: 4/4 blocuri pozitive, medie +0.218
2021 n=5 CI [0.200,1.000] · 2022 n=5 CI [0.200,1.000]  -> NEINFORMATIVE ; doar 2023 (n=24) informativ
P3 domina P2 pe criteriile declarate, dar CONF AUC 0.898 pe n=34 cu degradare INVERSA -> nu il promovez
dist_to_sweep INSTABIL (DISC 0.60-0.71 vs CONF 0.86-0.88) -- si e baza lui R2 (CONF n=4)
P2_MODEL_CONTEXT = nu adauga informatie demonstrabila peste R1
DEFECT: post_e1_survive2.py CRAPA la linia 72 (KeyError 'remaining') -- blocul P1/P3/P4 nu ruleaza
```

*Niciun candidat promovat, nicio cercetare de execuție, nicio retunare, nicio variantă de salvare.
`EARLY-TRAP-E1` neatins. Fără CALIB, V1, 2025+ sau holdout final. Fără AI Trader, broker, live.*
