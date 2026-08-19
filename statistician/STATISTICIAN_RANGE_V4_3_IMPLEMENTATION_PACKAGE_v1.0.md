# PACHET DE IMPLEMENTARE `range-hierarchical-v4.3`

**Divizia Statistician · mandat 3.105 · 2026-08-19**
**Status: `RANGE_V4_2_IMPLEMENTATION_PACKAGE_READY_FOR_RED_TEAM_STATIC_REVIEW`**
**`VE_CAN_IMPLEMENT_WITHOUT_INVENTION = TRUE`** — cu domeniul delimitat la §10.

Emis sub amendamentul CEO „închidere completă înainte de VE". Am corectat singur **17 probleme**,
fiecare declarată la §8. Nu am oprit lucrul pentru niciuna. Trei dintre ele erau defecte reale de
contract, nu chestiuni de redactare: `LIQUIDITY_SWEEP_REVERSAL` nu avea fereastră definită nicăieri
(C13), `DEPTH_LIMIT_EXCEEDED` era declarat dar nu putea fi emis niciodată, iar al treilea nivel — cel
eliminat explicit de CEO — se putea forma (C14), și conjuncția de confirmare exista doar ca proză,
deci VE ar fi trebuit să o compună singur (C15).

---

## 1 — CONTRACTUL CONSOLIDAT

`v4.3 = v4.2 (`5a9d5ec`) + cele 17 corecții`. Normele nemodificate rămân în documentul v4.2; aici e
doar ce s-a schimbat sau ce lipsea. **Definiția ierarhică, populația, etichetele CEO și configurația
fixată nu au fost atinse.**

### 1.1 Adâncimea

Exact **două** niveluri: `MACRO` (depth 0) și `INTERNAL` (depth 1). Un candidat conținut într-un
părinte `INTERNAL` **nu** primește `INTERNAL`; primește refuz cu `DEPTH_LIMIT_EXCEEDED`. Până la C14
regula era scrisă, dar nimic nu o impunea.

### 1.2 Conjuncția de confirmare — ordine de prioritate NORMATIVĂ

```
1. candidat absent / episod închis          -> BETWEEN_EPISODES
2. ATR indisponibil                         -> ATR_UNAVAILABLE            (fail-closed)
3. |membri| < n_touch pe oricare frontieră  -> ESTABLISHING_FEW_SWINGS
4. boundary_upper < boundary_lower          -> ZONES_INVERTED             (KILL)
5. separare <= 2 x w_atr x ATR_ref          -> ZONES_DEGENERATE           (KILL)
6. durată < d_macro | d_internal            -> TOO_SHORT_MACRO | _INTERNAL
7. altfel                                   -> OK_RANGE_MACRO | OK_RANGE_INTERNAL
```

**Ordinea nu e arbitrară și motivul e substanțial:** `TOO_SHORT_*` înseamnă *„încă nu"*. A raporta
*„încă nu"* despre un candidat deja **mort** ar fi o afirmație falsă. Deci stările de input lipsă și
stările KILL se evaluează înaintea porții de durată.

### 1.3 Degenerarea: KILL, nu DELAY

Lectura KILL rămâne normativă (mandatul 3.104, trei temeiuri). Consecință contractuală: `confirm_ts`
depinde **numai** de condiții independente de `w_atr`, deci circularitatea construcție↔observație e
ruptă prin tip, nu prin alegerea unei bare.

### 1.4 Canal intern vs sub-range — discriminator numeric (era „conform geometriei")

```
drift_normalizat = |panta_OLS(închideri)| x durată / ATR_ref
    > s_max  ->  INT_CHANNEL_UP / INT_CHANNEL_DOWN   (semnul pantei dă direcția)
   <= s_max  ->  INT_SUBRANGE
s_max = 2 x w_atr = 1,60   (derivat, niciodată stocat separat)
```

### 1.5 Reversal după sweep — fereastra, închisă FĂRĂ parametru nou

`LIQUIDITY_SWEEP_REVERSAL` era un cod declarat fără nicio regulă care să-l producă, iar `K_struct`
este **interzis explicit** de contract ca număr de swing-uri, deci nu putea servi drept fereastră.

```
după SWEEP_CONFIRMED, reversalul se confirmă la bara c ⟺
   c > reentry_bar
   ∧ episodul e încă viu la c            (altfel REVERSAL_WINDOW_EXPIRED)
   ∧ închiderea depășește ultimul swing confirmat OPUS, format ÎNAINTE de open_bar
       sweep jos (dir −1): close > swing_high_ref
       sweep sus (dir +1): close < swing_low_ref
referință absentă            -> REVERSAL_REFERENCE_UNAVAILABLE
referință confirmată DUPĂ open_bar -> ContractError FUTURE_TIMESTAMP_REFUSED  (lookahead)
```

**Fereastra este viața episodului.** Dacă episodul s-a încheiat, întrebarea despre reversal nu mai
are obiect. Asta închide golul fără a introduce a opta constantă liberă.

### 1.6 Identitate, rollback, restart

- ID-urile sunt monoton crescătoare; un ID **mort nu poate fi reutilizat** (`DEAD_ID_REUSE_REFUSED`).
- Level shift = **episod nou**, nu rescriere. Cel vechi rămâne integral (`id`, `start_ts`,
  `confirm_ts`, limite, rol) și e legat prin `predecessor_id`.
- `snapshot`/`restore` refuză fail-closed la nepotrivire de `contract_version` **sau** `config_id`,
  și transportă starea excursiei — nu doar limitele.
- Orice `ts > as_of` e refuzat (`FUTURE_TIMESTAMP_REFUSED`); bara curentă (`ts == as_of`) e admisă.

### 1.7 Rolurile — retrospective prin tip

`role_known_ts >= confirm_ts` și atribuirea pe un episod **deschis** e refuzată. Cele patru roluri
(`ACCUMULATION` / `DISTRIBUTION` / `TREND_EXHAUSTION` / `TREND_CONTINUATION` `_CONFIRMED`) sunt
constatări, **nu predicții**, conform deciziei CEO.

---

## 2 — CONFIGURAȚIA FINALĂ

```
contract_version = "range-hierarchical-v4.3"
config_id        = 24f72a60fcde42746d44f098558a745fac0f20b0141865bdbe0359f9cc3826da
```

`config_id` acoperă valorile scalare **plus** relațiile derivate **plus** proveniența ATR
(SHA-256 al wheel-ului). Două rulări cu același ATR nominal dar din altă sursă **nu** pot împărți
același `config_id`.

---

## 3 — TABELUL COMPLET AL PARAMETRILOR

| parametru | valoare | unitate | sursă | rol |
|---|---|---|---|---|
| `d_macro` | **29** | bare | decizie CEO | durata minimă a unui episod MACRO |
| `d_internal` | **12** | bare | decizie CEO | durata minimă a unui episod INTERNAL |
| `n_touch` | **2** | swing-uri | decizie CEO | membri minimi per frontieră |
| `K_reentry` | **22** | bare | decizie CEO | fereastra de reintrare care distinge sweep de breakout |
| `N_accept` | **3** | închideri consecutive | decizie CEO | acceptarea unui breakout |
| `K_struct` | **2** | **bare** stânga/dreapta | decizie CEO | raza fractalului; confirmare la `j + K_struct` |
| `n_external_swings` | **2** | **swing-uri** | decizie CEO | precondiția P3 a promovării |
| `atr_window` | **14** | bare | decizie CEO | fereastra ATR |
| `w_atr` | **0,80** | multiplu de ATR | măsurat 0,788051 → operațional, **fixat de CEO** | semilățimea zonei |
| `tol_cluster` | 1,60 | multiplu de ATR | **derivat** `= 2 x w_atr` | toleranța de apartenență la cluster |
| `s_max` | 1,60 | adimensional | **derivat** `= 2 x w_atr` | pragul canal vs sub-range |
| plafon de sanity `w_atr` | 1,3952 | multiplu de ATR | **recalculat sub ancora nouă** (C1) | test de sănătate, nu prag operațional |

★ `K_struct` (bare) și `n_external_swings` (swing-uri) sunt câmpuri **separate cu unități diferite**.
Confuzia lor este clasa de eroare pe care am prins-o de patru ori în acest dosar; contractul o
interzice explicit.

★ `tol_cluster` și `s_max` sunt **proprietăți calculate**, niciodată stocate (C2). Un câmp stocat ar
putea diverge de `w_atr` în tăcere.

---

## 4 — MATRICEA cerință → formulă → input → output → reason code → test

| # | cerință | formulă | input | output | reason code | test |
|---|---|---|---|---|---|---|
| 1 | swing confirmat | `high[j] = max(high[j−K..j+K])`, unic | OHLC | swing la `j+K_struct` | — | 14b |
| 2 | apartenență la cluster | `\|p − center\| <= tol_cluster x ATR_ref` | swing confirmat | membru adăugat | `SWING_OUTSIDE_CLUSTER` | 19h, 19i |
| 3 | centrul clusterului | `MEDIAN(membri)` | membri | `center` | — | 19h |
| 4 | zona | `center ± w_atr x ATR_ref` | `center`, `ATR_ref` | `boundary_*` | `ATR_UNAVAILABLE` | 10a, 10b |
| 5 | non-inversare | `boundary_upper >= boundary_lower` | zone | KILL | `ZONES_INVERTED` | 8a |
| 6 | non-degenerare | `separare > 2 x w_atr x ATR_ref` | zone | KILL | `ZONES_DEGENERATE` | 7a, 7b |
| 7 | membri suficienți | `\|membri\| >= n_touch` ambele | clustere | nedecis | `ESTABLISHING_FEW_SWINGS` | 9a, 9b |
| 8 | durata MACRO | `bar − start_ts >= d_macro` | timp | confirmare | `TOO_SHORT_MACRO` | 19b, 19c |
| 9 | durata INTERNAL | `bar − start_ts >= d_internal` | timp | confirmare | `TOO_SHORT_INTERNAL` | 19d, 19e |
| 10 | conjuncția completă | §1.2, prioritate fixă | candidat, bară | **un singur cod** | toate cele de mai sus | 19a–19g |
| 11 | nivel R1/R2/R3 | conținere în timp **și** în preț | candidat, părinte | `MACRO`/`INTERNAL` | `PARTIAL_OVERLAP_NO_CONTAINMENT`, `LEVEL_ASSIGNMENT_UNRESOLVED` | 1a, 3b, 13a, 13b |
| 12 | adâncime maximă | părinte `INTERNAL` ⇒ refuz | candidat, părinte | refuz | `DEPTH_LIMIT_EXCEEDED` | 18a–18c |
| 13 | canal vs sub-range | `\|panta\| x durată / ATR_ref` vs `s_max` | închideri | `INT_CHANNEL_*` / `INT_SUBRANGE` | — | 1b, 2a, 3a |
| 14 | excursie nedecisă | `închideri_afară < N_accept` ∧ în `K_reentry` | închideri | nedecis | `NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT` | 5a, 14b |
| 15 | sweep | reintrare la `dj <= K_reentry` | închideri | `SWEEP_CONFIRMED` | `SWEEP_CONFIRMED` | 4a, 4b, 14c |
| 16 | breakout acceptat | `N_accept` închideri **consecutive** | închideri | `BREAKOUT_ACCEPTED` | `BREAKOUT_ACCEPTED` | 5b |
| 17 | resetarea contorului | reintrarea readuce contorul la 0 | închideri | contor 0 | — | 5c |
| 18 | reversal după sweep | §1.5 | swing opus, close | reversal | `LIQUIDITY_SWEEP_REVERSAL`, `REVERSAL_WINDOW_EXPIRED`, `REVERSAL_REFERENCE_UNAVAILABLE` | 17a–17g |
| 19 | promovare | P1 ∧ P2 ∧ P3 ∧ P4, în ordine | stare | `IS_TREND_MACRO` | `PROMOTION_REFUSED_PRECONDITION_P1..P4` | 19j–19n |
| 20 | rol retrospectiv | `role_known_ts >= confirm_ts`, episod închis | episod închis | rol | `ROLE_ASSERTED_BEFORE_CONFIRMATION`, `ROLE_KNOWN_BEFORE_CONFIRM` | 14d–14f, 15a |
| 21 | identitate | ID mort nereutilizabil | registru | refuz | `DEAD_ID_REUSE_REFUSED` | 6c |
| 22 | level shift | episod nou + `predecessor_id` | episod închis | succesor | — | 6a, 6b, 16a, 16b |
| 23 | restart | `contract_version` **și** `config_id` | snapshot | restore sau refuz | `SNAPSHOT_CONTRACT_MISMATCH` | 12a–12c |
| 24 | zero-lookahead | `ts <= as_of` | orice timestamp | refuz | `FUTURE_TIMESTAMP_REFUSED` | 11a, 11b, 17f |
| 25 | între episoade | fără candidat viu | stare | stare neutră | `BETWEEN_EPISODES` | 19a, 19g |

**Setul de reason codes e ÎNCHIS: 29.** Testul 20 verifică mecanic ambele direcții — niciun cod
declarat-dar-neemisibil, niciun cod emis-dar-nedeclarat.

---

## 5 — MAPAREA SEGMENTELOR

`BLIND_BATCH_02_LEVEL_MAPPING.md`, neschimbat, 126 rânduri:

```
MACRO                        88   (77,2% din 114)
LEVEL_ASSIGNMENT_UNRESOLVED  26   (22,8%)
                            ---
nivel 1                     114   (partiție exactă)
INTERNAL (nivel 2)           12   (populație separată)
                            ---
total rânduri               126
```

Cele 26 `UNRESOLVED` **nu sunt un eșec al contractului**: sunt cazuri în care corpusul nu conține
informația necesară, iar contractul emite un cod definit în loc să inventeze un părinte. Regula a
fost aplicată mecanic; nu s-a inventat informație absentă.

---

## 6 — HARNESS-UL CONTRACTUAL

| fișier | linii | SHA-256 |
|---|---|---|
| `statistician/harness/range_v42_contract_harness.py` | 409 | `c917604bd42a0943d77d385523ececba149a3e78f76a4875ce94cf82a368c72d` |
| `statistician/harness/test_range_v42_adversarial.py` | 329 | `ecb4140e7f47d7b86cb29ef7d50e193a1375dddc2c5505aef7a65add2d277f40` |

```
mypy --strict  : Success, 0 erori
rezultat       : 79 PASS · 0 FAIL
```

Acoperă cele **16 cazuri adversariale** cerute, plus 4 grupe adăugate de mine (17 reversal,
18 adâncime, 19 conjuncție + promovare, 20 acoperirea codurilor), plus **12 teste de nevacuitate**.

**Ce NU este harness-ul:** nu e detectorul VE, nu e wheel, nu produce semnale, nu atinge SEALED/OOS,
nu calculează PnL. E implementarea de referință a deciziilor, ca VE să aibă un oracol executabil,
nu o descriere.

### Nevacuitate (§D) — fiecare poartă TRECE și EȘUEAZĂ

Douăsprezece porți verificate în ambele sensuri: durata MACRO, durata INTERNAL, degenerarea,
inversarea, sweep, breakout, apartenența la cluster, nivelul INTERNAL, nivelul UNRESOLVED,
clasificarea canal, rolul retrospectiv, reversalul, limita de adâncime. **Nicio condiție cu
`n_pass = 0` (moartă) sau `n_fail = 0` (vacuă).**

---

## 7 — AUTO-AUDIT

**A. Aritmetică.** `88 + 26 = 114` ✓ · `114 + 12 = 126` ✓ · rânduri tabel `126 + 1 antet = 127` ✓ ·
`2 x 0,80 = 1,60` ✓ · procente `88/114 = 77,2%`, `26/114 = 22,8%`, sumă `100,0%` ✓.

**B. Unități.** Fiecare parametru poartă unitatea în tabel. `K_struct` (bare) și `n_external_swings`
(swing-uri) sunt separate prin câmpuri distincte. `w_atr`, `tol_cluster`, `s_max` sunt multipli de
ATR, nu prețuri. `normalized_drift` e adimensional prin construcție (`preț/bară x bare / preț`).

**C. Circularitate.** Ruptă prin tip: apartenența e PRE-confirmare, atingerea e POST-confirmare.
`confirm_ts` nu depinde de `w_atr` sub lectura KILL. Verificat că `evaluate_candidate` nu citește
niciun output al propriei confirmări.

**D. Completitudinea codurilor.** 29 declarate, 29 emisibile, 0 orfane în ambele direcții — verificat
mecanic, nu prin citire.

**E. Cazuri adversariale.** 16 cerute + 4 adăugate; toate trec.

**F. Consistență tabel ↔ contract ↔ harness.** `config_id` identic în toate trei. Denumirile
codurilor normalizate la forma completă (C16). Niciun câmp derivat stocat de două ori.

---

## 8 — CORECȚIILE APLICATE (17)

| # | problemă | corecție |
|---|---|---|
| C1 | plafonul de sanity `w_atr = 0,495` era **transplant de la ancora VECHE** | recalculat sub ancora nouă: **1,3952**; la 0,80 zero din 25 de segmente ar fi degenerate |
| C2 | `tol_cluster` și `s_max` puteau fi stocate și diverge de `w_atr` | proprietăți **calculate**, imposibil de stocat |
| C3 | §3.5 se citea DELAY, §3.6 KILL | KILL formalizat **în** conjuncția de confirmare |
| C4 | canal vs sub-range era „conform geometriei" — invenție lăsată VE | discriminator numeric `drift` vs `s_max` |
| C5 | `SLOPE_UNAVAILABLE` numea o stare inaccesibilă prin construcție | **retras** din setul de coduri |
| C6 | setul de coduri era deschis | **închis la 29**, cu test mecanic bidirecțional |
| C7 | un ID mort putea fi reutilizat | `DEAD_ID_REUSE_REFUSED` |
| C8 | timestamp din viitor era acceptat tacit | fail-closed; `ts == as_of` rămâne admis |
| C9 | `restore` accepta snapshot-uri străine; starea excursiei se pierdea | refuz pe `contract_version` **și** `config_id`; excursia inclusă |
| C10 | `config_id` era orb la sursa ATR | acoperă relațiile derivate + SHA-256 al wheel-ului |
| C11 | rollback/level shift nedefinit | episod vechi **imutabil** + `predecessor_id` |
| C12 | rolul se putea atribui pe episod deschis sau înaintea confirmării | `role_known_ts >= confirm_ts`, episod închis obligatoriu |
| **C13** | **`LIQUIDITY_SWEEP_REVERSAL` declarat fără nicio fereastră; `K_struct` interzis ca număr** | **fereastra = viața episodului; FĂRĂ parametru nou; +2 coduri** |
| **C14** | **`DEPTH_LIMIT_EXCEEDED` declarat dar NEEMIS: al treilea nivel se putea forma** | **adâncimea maximă IMPUSĂ, nu doar scrisă** |
| **C15** | **conjuncția de confirmare exista doar ca proză — VE ar fi compus-o singur** | **`evaluate_candidate()`, ordine de prioritate normativă, un singur cod** |
| C16 | contractul scria `PROMOTION_REFUSED_P1`, cod inexistent în set | normalizat la `PROMOTION_REFUSED_PRECONDITION_P1..P4` |
| C17 | codul de eșec era despărțit pe adâncime, cel de succes nu | adăugat `OK_RANGE_INTERNAL` |

**O eroare proprie, prinsă de propriul instrument în aceeași rulare:** aplicând C17 am adăugat un
comentariu `# C17` la mijlocul liniei, care a comentat restul ei și a scos tăcut `TOO_SHORT_MACRO`
și `TOO_SHORT_INTERNAL` din setul închis. Testul 20 a semnalat-o imediat (`|REASONS| = 27`, nu 29).
Nu a ajuns în nicio cifră publicată — de aceea **nu** intră în numărătoarea celor 13 erori publicate
ale dosarului. O consemnez fiindcă e dovada că testul de acoperire își face treaba: exact clasa C14,
prinsă mecanic în loc de citită.

---

## 9 — BLOCAJE REALE RĂMASE

**Niciunul pentru implementare.** Următoarele sunt **limitări de evidență**, cu efect asupra a ce se
poate AFIRMA, nu asupra a ce se poate construi:

1. **Baza empirică a lui `w_atr` e subțire** — 50 de contribuții din 25 de segmente; **78 de segmente
   nu au bandă numerică pe ambele frontiere**; dispersia 0,24–3,93 arată că benzile CEO nu scalează
   uniform cu volatilitatea. Valoarea e utilizabilă; nu e ratificată statistic.
2. **Precedență cu pată, declarată deschis** — plafonul corect (1,3952) a fost derivat **după** ce
   văzusem rezultatul 0,788. Ce salvează precedența e că `w_atr = 0,80` a fost fixat prin **decizie
   CEO**, independent de plafonul meu; blocajul meu din 3.104 e ridicat de acea decizie, nu de o
   relaxare a propriei reguli după ce am aflat că mă încurcă.
3. **Detectorul nu a fost rulat niciodată sub v4.2/v4.3.** Nu există nicio rată empirică. Orice
   afirmație despre raritatea sau calitatea RANGE sub acest contract ar fi, azi, nefondată.
4. **Cele 26 `UNRESOLVED` (22,8%)** rămân nerezolvabile din corpusul actual. E o limitare a
   corpusului, nu a contractului.
5. **Corpusul vizual e epuizat** — escrow-ul blind rămâne BLOCAT (mandatul 3.102). Nu există episod
   aflat simultan în populația canonică și nevăzut de VE.

---

## 10 — VERDICT

```
VE_CAN_IMPLEMENT_WITHOUT_INVENTION = TRUE
```

**Domeniu, strict.** Verdictul spune că **fiecare regulă de decizie și fiecare constantă necesare
implementării există, sunt numerice, sunt testate în ambele sensuri și au un oracol executabil.**
Ce a mai rămas pentru VE e orchestrarea per-bară, nu inventarea unei reguli.

**Verdictul NU spune** că semantica RANGE e validată, că detectorul va produce ceva, că `w_atr = 0,80`
e ratificat statistic, sau că vreun rezultat e utilizabil în strategie.

**Nu autorizez:** wheel, Strategy Catalog, Alpha, AI Trader, LIVE_SHADOW, broker, tranzacții, acces
SEALED/OOS, PnL, sau vreo modificare a definiției ierarhice, a populației, a etichetelor CEO ori a
configurației fixate.

**Autorizez exact atât:** implementarea `range-hierarchical-v4.3` de către VE, sub `config_id`
`24f72a60…`, verificată contra harness-ului de la §6, urmată de **revizuire statică Red Team**.

---

*Divizia Statistician · `SEALED/OOS_ACCESS = 0` · detectorul dezinstalat · invariante neatinse*
