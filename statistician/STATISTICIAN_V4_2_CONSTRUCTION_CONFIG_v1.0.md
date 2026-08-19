# STATISTICIAN — CONFIGURAȚIA DE CONSTRUCȚIE `range-hierarchical-v4.2`

**Document ID:** STAT-RANGE-V4.2-CONSTRUCTION-CONFIG-v1.0 · **Data:** 2026-08-19
**Citează:** fișa de decizie `4684e66` · manifest v2.7.92 `6ae0837`

## STATUS TERMINAL

```
RANGE_V4_2_PARAMETER_IDENTIFICATION_BLOCKED
```

**Motivul: propria mea condiție de blocare, preînregistrată la `4684e66`, s-a declanșat literal.** `w_atr` calculat = **0,788051**, iar regula R-B spune: *„dacă rezultatul depășește plafonul de disjuncție 0,495 → `BLOCKED`. Se raportează, nu se trunchiază."*

> **Nu trunchiez, nu reinterpretez, nu aleg 0,45. Livrez calculul complet ȘI măsurătoarea care arată de ce plafonul de 0,495 e el însuși un transplant expirat — apoi decizia e a ta. Îmi respect regula chiar când măsurătoarea sugerează că regula avea o premisă greșită, fiindcă altfel o condiție de blocare nu ar mai însemna nimic.**

**VE rămâne în HOLD.** Nu am modificat registrul Alpha, verdictele, tombstones, LIVE_SHADOW sau brokerul. `SEALED/OOS_ACCESS = 0`.

---

# 1 — NECIRCULARITATEA: REZOLVATĂ, DAR CERE O CLARIFICARE A CONTRACTULUI MEU

## 1.1 Circularitatea era reală

```
R-B cere ATR_ref la `confirm_ts`.
`confirm_ts` = bara la care ULTIMA condiție de confirmare devine adevărată (v4.2 §3.5).
Una dintre condiții e DISJUNCȚIA ZONELOR, care depinde de `w_atr`.
⇒ dacă disjuncția ÎNTÂRZIE confirmarea, atunci confirm_ts depinde de w_atr ⇒ CIRCULAR.
```

## 1.2 O ambiguitate în contractul meu, pe care o rezolv pe fond

```
§3.5  „confirm_ts = bara la care ULTIMA dintre aceste condiții devine adevărată"   → lectura DELAY
§3.6  „Unavailable, fail-closed. Un episod nu se poate confirma degenerat."         → lectura KILL
```

**Declar normativă lectura KILL, pe trei temeiuri independente de convenabilitate:**

```
1  În toată familia asta de contracte, `Unavailable` a însemnat mereu REFUZ — „producătorul nu
   poate vorbi" — niciodată „încă nu". „Încă nu" are propriul câmp: `not_yet_available`.
2  §3.6 spune explicit „se verifică ÎNAINTE de confirmare" — poartă de intrare, nu condiție care se coace.
3  ★ DECISIV: sub lectura DELAY contractul e INCOMPLET. Nu există regulă de oprire — separarea
   ancorelor se poate mișca în ambele direcții pe măsură ce clusterele cresc, deci „așteptăm
   disjuncția" nu are nici limită, nici criteriu de renunțare. Un contract cu o așteptare
   nemărginită nu e implementabil. KILL e singura lectură coerentă.
```

**Sub KILL:** `confirm_ts` e determinat exclusiv de condițiile independente de `w_atr` — swing-uri ≥ `n_touch` pe fiecare latură ȘI durata ≥ `d_macro`. **`ATR_ref` e calculabil. Nicio bară arbitrară nu a fost aleasă.**

```
confirm_ts := max( confirmarea celui de-al n_touch-lea swing high,
                   confirmarea celui de-al n_touch-lea swing low,
                   d_macro − 1 )
```

**Și nu există buclă de feedback la identificare:** populația peste care iau mediana e mulțimea segmentelor ETICHETATE de CEO, care e fixă. Nu e mulțimea episoadelor care supraviețuiesc detectorului.

---

# 2 — CALCULUL `w_atr`, APLICAT O SINGURĂ DATĂ

## 2.1 Ce am publicat înainte de a aplica

```
1 formula          w_atr = MEDIAN over all labelled bands of  (band_width / 2) / ATR_ref
2 populația        toate segmentele RANGE etichetate, nivel 1 ȘI nivel 2, cu BANDĂ numerică
                   pe AMBELE frontiere, din cele 45 de ferestre aliniate
3 excluderi        enumerate integral la §2.2
4 semilățimea      band_width / 2 — banda e incertitudinea CEO asupra frontierei; jumătatea ei
                   e semilățimea naturală a zonei centrate pe mijlocul benzii
5 ATR_ref          ATR(14) canonic vendorizat, la `confirm_ts` calculat ca la §1.2
6 timestamp        bara `confirm_ts`; toate intrările au index <= acea bară — CAUZAL
7 egalități        număr par ⇒ media celor două valori centrale (convenția v2.7.80)
8 precizie         valoarea brută se păstrează nerotunjită; operațională = cel mai mic punct
                   al rețelei cu pas 0,05 care e >= mediana
9 fără scor        formula nu conține recall, precision, IoU, occupancy sau PnL. Citește ce
                   a scris omul; nu caută ce potrivește detectorul.
```

## 2.2 Excluderile, cu motiv

| n | motiv |
|---|---|
| 78 | fără BANDĂ numerică pe ambele frontiere (CEO a scris o singură valoare sau niciuna) |
| 6 | durata sub `d_macro = 29` — segmentul nu poate confirma, deci nu are `confirm_ts` |
| 3 | eticheta superseded de addendum, iar addendumul nu conține benzi (`BLIND-046/047/048`) |
| 6 | `confirm_ts` cade în afara segmentului etichetat |
| **93** | **total excluse** |

**Rămân 25 de segmente × 2 frontiere = 50 de contribuții.**

## 2.3 Rezultatul

```
n = 50   min 0,2405   max 3,9258
MEDIANA NEROTUNJITĂ  =  0,788051
OPERAȚIONALĂ         =  0,80        (cel mai mic punct al rețelei pas 0,05 care e >= mediana)
tol_cluster derivat  =  1,60
```

**Contribuțiile individuale, toate 50, în `V4_2_W_ATR_AUDIT_TRAIL.md`.** Extreme, pentru orientare: minim `BLIND-013` 0,2405 · maxim `BLIND-019 lower` 3,9258 (bandă 6 puncte / ATR 0,7642).

---

# 3 — CONDIȚIA DE BLOCARE S-A DECLANȘAT

```
0,788051  >  0,495   ⇒  BLOCKED, conform R-B litera 6.
```

## 3.1 Dar am măsurat plafonul sub ANCORA NOUĂ, și e altul

Separarea frontierelor, direct din benzile etichetate de CEO — **necirculară, nu cere clustere**:

```
n = 25 segmente
min 2,790 ATR · p05 3,064 · p25 4,864 · MEDIANĂ 6,848 · max 18,456

plafon implicat:  w_atr < separare / 2
   pentru TOATE segmentele:  w_atr < 1,3952
   pentru 95%:               w_atr < 1,5318

la w_atr = 0,300 →  0/25 segmente etichetate ar fi degenerate
la w_atr = 0,495 →  0/25
la w_atr = 0,800 →  0/25
```

> **Plafonul de 0,495 vine de la v2.7.79, derivat sub ancora VECHE — mediană pe 512 bare, unde separarea la p05 era 0,99 ATR. Sub ancora legată de segment, separarea minimă e 2,79 ATR și mediana 6,85. Frontierele sunt acum acolo unde e range-ul, nu unde e mediana ultimelor cinci zile — iar asta se vede în cifre, nu în argument.**
>
> **Contractul v4.2 spune el însuși că `w_atr` ratificat sub ancora veche e INVALID sub cea nouă. Dacă valoarea e invalidă, plafonul derivat din ACEEAȘI ancoră veche e la fel de invalid. A-l aplica ar fi un TRANSPLANT DE UNITĂȚI — clasa de eroare pe care am prins-o de patru ori în acest dosar.**

## 3.2 De ce raportez totuși BLOCKED

**Fiindcă regula preînregistrată numește un număr, iar eu am văzut rezultatul.** Dacă aș declara acum plafonul nul și aș continua, aș fi relaxat propria condiție de blocare *după* ce am aflat că mă încurcă. Asta ar goli de sens orice condiție de blocare pe care o mai scriu.

**Decizia e a ta, cu ambele fapte pe masă.**

---

# 4 — `tol_cluster = 2 × w_atr`: CONFIRMAT MATEMATIC, NU PRESUPUS

```
R-B  mediana( semilățime / ATR )  =  0,788052
R-C  mediana( bandă      / ATR )  =  1,576103
raport                            =  2,0000000000
```

```
populația    IDENTICĂ — aceleași 50 de contribuții, aceleași segmente, aceleași benzi
statistica   IDENTICĂ — mediana
operandul    banda = 2 × semilățimea, prin definiție
mediana e ECHIVARIANTĂ LA SCARĂ pentru factori pozitivi: median(2x) = 2·median(x)
```

> **Deci `tol_cluster = 2 · w_atr` nu e o presupunere de comodă, ci o identitate care rezultă din faptul că cele două reguli împart populația și statistica. Contradicția pe care mi-ai cerut să o caut NU există. `tol_cluster` NU se stochează independent.**

Notez și că asta **închide corecția C6** din fișa anterioară: `tol_cluster >= w_atr` e satisfăcut automat, fiindcă `2·w_atr > w_atr` pentru `w_atr > 0`.

---

# 5 — ATR CANONIC: IDENTITATE PRIN CONSTRUCȚIE

```
funcția importată de mine   market_state.atr14
funcția folosită de builder market_state.atr14
ACEEAȘI REFERINȚĂ DE OBIECT: True          ← identitate prin construcție, nu prin comparație
serii bit-identice pe 600 bare: True
santinela pe primele 14 bare: 14/14 NaN, tradusă la None la graniță
hash serie finită (586 valori): ad0c83f6b0321f7d26fa1767d2460a44b65dad184fa66fa7b026d7d5c57da0bf
```

> **Corecție a unei verificări proprii: prima rulare a testului a raportat „bit-identice: False". Era artefactul comparației mele — `NaN != NaN` în Python. Cu o comparație conștientă de NaN: `True`. Nu era o diferență reală, dar puteam foarte ușor să public „False" și să declanșez o alarmă falsă.**

**Nicio reimplementare. Proveniența intră în `config_id`.**

---

# 6 — TESTELE DE CONSISTENȚĂ

| # | test | rezultat |
|---|---|---|
| 1 | `d_internal < d_macro` | 12 < 29 ✔ |
| 2 | poarta `d_macro` trece ȘI eșuează | trec 66/88, eșuează 22 ✔ |
| 2b | poarta `d_internal` trece ȘI eșuează | trec 11/12, eșuează 1 ✔ |
| 3 | `n_touch=2` permite ambele clustere | 25 de segmente au ≥2 swing-uri pe FIECARE latură ✔ |
| 4 | frontiere: exemple pozitive și negative | 50 contribuții vs 93 excluderi ✔ |
| 5 | `K_reentry=22` nu blochează `N_accept=3` | criterii pe axe INDEPENDENTE; 3 închideri se ating în 3 bare < 22 ✔ |
| 6 | `N_accept` / `K_struct` / `n_external_swings` distincte | 3 / 2 / 2 — trei câmpuri; ultimele două au aceeași VALOARE, sensuri diferite ✔ |
| 7 | `tol_cluster` derivat | `2·w_atr`, nestocat independent ✔ |
| 8 | `atr14` bit-identic cu sursa canonică | aceeași referință de obiect ✔ |
| 9 | nicio valoare aleasă după rezultat | `d_*`/`K_*` fixate de CEO ÎNAINTE; `w_atr` prin regula `@4684e66` ✔ |
| 10 | toate valorile intră în `config_id` | inclusiv sursa ATR și SHA-ul wheel-ului ✔ |

---

# 7 — CONFIGURAȚIA COMPLETĂ ȘI `config_id`

| parametru | valoare | statut |
|---|---|---|
| `d_macro` | **29** | fixat CEO |
| `d_internal` | **12** | fixat CEO |
| `n_touch` | **2** | fixat CEO (podea structurală) |
| `K_reentry` | **22** | fixat CEO |
| `N_accept` | **3** | fixat CEO |
| `K_struct` | **2** | fixat CEO — RAZA fractalului |
| `n_external_swings` | **2** | fixat CEO — NUMĂR de swing-uri |
| `atr_window` | **14** | import canonic |
| `w_atr` | **0,80** (brut 0,788051) | **CALCULAT — dar BLOCAT de R-B litera 6** |
| `tol_cluster` | **1,60** | DERIVAT `2·w_atr`, nestocat |
| `s_max` | `2·w_atr` | DERIVAT, nestocat |

```
atr_source                    ai_trader.structural_observer.vendor_bridge.atr14
atr_provenance_wheel_sha256   39673910666e13708b1d4cb7266d1730bb1c9ceea4e0b021a1bf3cfa1f8281f4
contract_version              range-hierarchical-v4.2

config_id = 81b05f9cd3678fc13991feaada5e8eea13274eccec1f6b754fa6c15323570594
```

> **`config_id` e PROVIZORIU: e calculat cu `w_atr = 0,80`, valoare care e blocată. Dacă decizi altfel, `config_id` se schimbă și trebuie recalculat.**

---

# 8 — CE ÎȚI CER

```
D-A  Plafonul de 0,495 e un transplant din ancora VECHE. Îl declari NUL sub v4.2 și accepți
     w_atr = 0,80 (brut 0,788051), cu plafonul nou măsurat 1,3952? → DEBLOCHEAZĂ configurația.
D-B  Sau menții regula literal, iar eu re-execut R-B cu plafonul corectat DECLARAT ÎNAINTE,
     într-un commit nou? Rezultatul numeric va fi același; se schimbă doar dovada de precedență.
D-C  Confirmi lectura KILL pentru degenerare (§1.2)? Fără ea, `w_atr` e necalculabil prin circularitate.
```

**Recomandarea mea, spusă o dată: `D-B`.** Rezultatul e identic, dar precedența rămâne curată — regula corectată se declară înainte de a fi rulată, chiar dacă știu deja ce va da. Cu `D-A` obții aceeași cifră mai repede, dar cu o condiție de blocare relaxată după ce a fost văzut rezultatul, iar asta slăbește toate regulile viitoare.

---

# 9 — CE RĂMÂNE DESCHIS

```
BLOCANT     w_atr blocat de propria regulă. Decizie D-A sau D-B.
MATERIAL    baza lui w_atr e de 50 de contribuții din 25 de segmente — 78 de segmente etichetate
            NU au bandă numerică pe ambele frontiere. E o bază subțire, spusă înainte de folosire.
MATERIAL    dispersia contribuțiilor e mare: 0,24 … 3,93. Mediana e robustă, dar coada superioară
            (BLIND-019, ATR 0,76) arată că benzile CEO nu scalează uniform cu volatilitatea.
LIMITARE    lectura KILL e o clarificare a contractului meu, nu o modificare a lui. Nu am editat v4.2.
```

---

**Invariante verificate neatinse:** `n_generated_total = 363` · `m_inference = 26` · tombstones · registrul Alpha · verdictele existente · F1-F6 · F7 `SAFETY_GUARD` · LIVE_SHADOW · broker gate. Prototipul NU a fost rulat · `SEALED/OOS_ACCESS = 0`.

**Manifest:** v2.7.93. **VE rămâne în HOLD.**
