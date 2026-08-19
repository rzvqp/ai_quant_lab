# STATISTICIAN — CONTRACT `range-hierarchical-v4.2`

**Document ID:** STAT-RANGE-HIERARCHICAL-CONTRACT-V4.2-v1.0 · **Data:** 2026-08-19
**Status:** `RANGE_HIERARCHICAL_SEMANTIC_SPEC_V4_2_READY_FOR_CEO_REVIEW`
**Supersedează:** `range-hierarchical-v4.1` @`fa2b1fb` · **VE rămâne în HOLD**

> **NU autorizez: VE prototype · wheel · Red Team PASS · Strategy Catalog · Alpha · AI Trader · LIVE_SHADOW · broker · tranzacții.**

```
verificat   challenge fe3f933 · contract v4.1 e70de6d/9baa654 · manifest v2.7.90 01de59e ·
            fingerprint a92ac35f979592f6118a87435de782f03830bf5e1d17a750aaf3e23bcab1d19f   ✔
detectorul NU a fost rerulat · niciun cod implementat · SEALED/OOS_ACCESS = 0
```

---

# 0 — RĂSPUNSUL LA CHALLENGE-UL REPETAT (§11), PUS PRIMUL

## **NU** — dar blocantul s-a mutat, iar mutarea contează.

```
ÎNCHISE de V4.2:   S1 · S2 · S3 · S4 — toate patru, cu formule, nu descrieri.
                   ★ CODUL e acum scriitibil fără ca VE să inventeze vreo REGULĂ SEMANTICĂ.
RĂMÂN:             ȘAPTE valori numerice. Prototipul nu poate fi RULAT, deci nici VERIFICAT.
```

**Distincția e reală, nu diplomatică:** la `v4.1` VE ar fi trebuit să inventeze *semantică* — cum se calculează o frontieră, ce nivel primește o structură. Acum nu mai trebuie. **Dar etapa 3 din propria ta stagializare (§10) — „identificarea valorilor pe construction" — vine ÎNAINTEA etapei 5 „prototip VE". Etapa 3 nu a rulat.** Deci răspunsul rămâne NU, prin propria ta ordine.

```
BLOCANTE RĂMASE
B1  d_macro          CONVENTION_CEO_REQUIRED
B2  d_internal       CONVENTION_CEO_REQUIRED
B3  w_atr            IDENTIFIABIL — regulă preînregistrată la §8, neaplicată
B4  tol_cluster      IDENTIFIABIL — idem
B5  K_reentry        IDENTIFIABIL — idem
B6  n_touch          MOȘTENIT 2, neratificat sub V4
B7  atr_window       MOȘTENIT 14, neratificat sub V4
```

**Nu autorizez prototipul.** Ce cer înainte: acceptarea celor trei reguli de selecție (§8) și două convenții CEO (`d_macro`, `d_internal`). Atunci etapa 3 se execută într-un commit separat care citește regulile din acesta — exact tiparul `4e69e22 → c29ac98`.

---

# 1 — DECIZIA CEO: DOUĂ NIVELURI

```
MACRO      RANGE_MACRO · TREND_UP · TREND_DOWN · TRANSITION_MACRO
INTERNAL   INT_SUBRANGE · INT_CHANNEL_UP · INT_CHANNEL_DOWN · INT_BALANCE
EVENIMENT  ortogonal, fără depth propriu, cu `applies_to_structure_id`

depth ∈ {0, 1} — enumerare ÎNCHISĂ. depth 2 NEREPREZENTABIL prin tip.
```

> **`MICRO` ELIMINAT din contractul implementabil. Motivul e al meu, măsurat: ZERO exemple pozitive etichetate, deci pică testul de nevacuitate. Rămâne în BACKLOG, condiționat de un corpus dedicat cu trei niveluri. Un al treilea nivel aparent se REFUZĂ cu `DEPTH_LIMIT_EXCEEDED` — nu se absoarbe în INTERNAL (ar falsifica limitele) și nu se convertește în eveniment (evenimentele n-au limite).**

---

# 2 — S1 ÎNCHIS: REGULA DE ATRIBUIRE LA NIVEL

```
R1  MACRO      o structură CONFIRMATĂ fără părinte structural ACTIV la confirm_ts
R2  INTERNAL   TOATE patru, simultan:
                 a) start_ts >= start_ts al unui MACRO activ
                 b) [start_ts, end_ts] ⊆ [start_ts, end_ts] al părintelui
                 c) [boundary_lower, boundary_upper] ⊆ limitele MACRO,
                    SAU depășirea e un eveniment ÎNCĂ NECONFIRMAT
                 d) parent_structure_id = id-ul MACRO-ului
R3  altfel     LEVEL_ASSIGNMENT_UNRESOLVED — NU se ghicește nivelul.
               Se păstrează: interval, limite candidate, MACRO-urile candidate,
               și motivul exact al nerezolvării.
```

## 2.1 Suprapunere parțială fără containment — regula lipsă din `v4.1`

```
dacă intervalul se suprapune parțial cu un MACRO activ, dar NU e conținut:
   NU e INTERNAL (pică R2b)
   NU e MACRO cât timp MACRO-ul părinte e activ (ar încălca „cel mult unul activ pe nivel")
   → LEVEL_ASSIGNMENT_UNRESOLVED, reason PARTIAL_OVERLAP_NO_CONTAINMENT
   → structura se REEVALUEAZĂ la închiderea MACRO-ului: dacă atunci nu mai are părinte, devine MACRO
```

> **Un obiect INTERNAL NU poate închide, înlocui sau reclasifica părintele doar fiindcă e canal sau sub-range. Singura cale în sus e promovarea prin P1-P4 (§5).**

---

# 3 — S2 ÎNCHIS: ESTIMATORUL FRONTIEREI, CU FORMULĂ

## 3.1 Swing confirmat

```
swing high la bara j  ⟺  high[j] = max(high[j-K_struct .. j+K_struct])  ȘI  unic pe fereastră
confirm_ts(swing)     =  bara j + K_struct        ← NU bara j. Aici e zero-lookahead.
simetric pentru swing low.        K_struct = 2 (decizie CEO, §4)
```

## 3.2 Deschiderea clusterului

```
clusterul SUPERIOR se deschide la primul swing high confirmat după start_ts al candidatului.
   membri := [price(swing)]
   center := price(swing)
simetric pentru clusterul INFERIOR, cu swing low.
```

## 3.3 Adăugarea unui swing

```
un swing high confirmat la bara c se ADAUGĂ clusterului superior ⟺
      | price − center_curent |  <=  tol_cluster × ATR_ref
   atunci  membri ← membri ∪ {price}
           center ← MEDIAN(membri)          ← mediana, convenția deja ratificată
altfel REFUZAT, reason SWING_OUTSIDE_CLUSTER. Swingul refuzat NU se pierde:
       se înregistrează ca posibil început al unui episod ULTERIOR.
```

## 3.4 Zona

```
zona_superioară = [ center_sup − w_atr × ATR_ref ,  center_sup + w_atr × ATR_ref ]
zona_inferioară = [ center_inf − w_atr × ATR_ref ,  center_inf + w_atr × ATR_ref ]
boundary_upper  = center_sup      boundary_lower = center_inf
ATR_ref = ATR(atr_window) evaluat la confirm_ts al ULTIMULUI swing admis înainte de îngheț.
          Se FIXEAZĂ la îngheț. Cauzal prin construcție: toate intrările au index <= acea bară.
```

## 3.5 Confirmarea și înghețul

```
CONFIRMARE cere simultan:
   |membri_sup| >= n_touch   ȘI   |membri_inf| >= n_touch
   ȘI durata >= d_macro (sau d_internal, după nivel)
   ȘI zonele DISJUNCTE (§3.6)
   ȘI ATR disponibil
confirm_ts = bara la care ULTIMA dintre aceste condiții devine adevărată.
★ LA confirm_ts CLUSTERELE ÎNGHEAȚĂ. După îngheț NU se mai adaugă niciun membru,
  iar center și zonele NU se mai mișcă. NICIODATĂ.
```

## 3.6 Degenerare și inversare

```
ZONES_INVERTED     center_sup < center_inf                          → Unavailable, fail-closed
ZONES_DEGENERATE   center_sup − center_inf  <=  2 × w_atr × ATR_ref → Unavailable, fail-closed
Ambele se verifică ÎNAINTE de confirmare. Un episod nu se poate confirma degenerat.
```

## 3.7 După îngheț: extrema nouă NU mută frontiera

```
o extremă nouă în afara zonei, după îngheț, e tratată EXCLUSIV ca eveniment:
   închidere în afară              → BOUNDARY_EXCURSION, closes_outside = 1
   reintrare <= K_reentry          → SWEEP_CONFIRMED
   N_accept închideri consecutive  → BREAKOUT_ACCEPTED, episodul se ÎNCHIDE
LEVEL SHIFT: un breakout acceptat NU rescrie episodul vechi. Deschide unul NOU,
   cu clustere NOI și predecessor_id = episodul închis.
```

## 3.8 De ce estimatorul NU se auto-invalidează — demonstrația

```
DEFECTUL V1:  frontiera = MAXIM pe o mulțime CRESCĂTOARE. Creșterea ferestrei ridica frontiera,
              deci atingerile deja numărate deveneau retroactiv „în interior". Auto-invalidare.

V4.2:  (a) centrul e MEDIANA, nu maximul — non-monotonă: un membru nou o poate muta în ORICE
           direcție sau deloc, deci nu există drift sistematic într-o singură direcție;
       (b) ★ argumentul decisiv: MEMBRIA E CRITERIU DE PRE-CONFIRMARE, ATINGEREA E EVENIMENT
           POST-CONFIRMARE. Cele două nu se amestecă niciodată. Confirmarea cere
           |membri| >= n_touch — SWING-uri, nu atingeri. `BOUNDARY_TEST_*` se emite DOAR
           după confirm_ts, pe frontiere DEJA ÎNGHEȚATE.
       (c) deci nicio atingere numărată nu poate fi invalidată de o mișcare de frontieră:
           la momentul primei atingeri, frontiera e imutabilă prin contract.
```

> **Aici era circularitatea ascunsă în V1-V3: „atingerea" era folosită ȘI ca material de construcție, ȘI ca observație. V4.2 le separă prin tip. Asta e reparația care lipsea, și abia acum o pot numi.**

## 3.9 Exemplu care TRECE și exemplu care EȘUEAZĂ

```
TRECE     BLIND-019, macro RANGE 0-480, limite etichetate 1254-1260 / 1269-1273.
          Separarea centrelor ≈ 13 puncte; zonele rămân disjuncte la orice w_atr sub ~0,5×ATR.
          Clusterele au material abundent: 6 structuri interne, deci multe swing-uri.
EȘUEAZĂ   BLIND-041, două range-uri etichetate 1664-1667 și 1661-1664 — separare de 3 puncte,
          zone care se ating. `ZONES_DEGENERATE` se declanșează, fail-closed, episodul NU se confirmă.
          ★ Aceeași gardă s-a declanșat de 24 de ori pe corpus la V3, deci e demonstrat nevacuă.
```

---

# 4 — S4 ÎNCHIS: DOUĂ CÂMPURI DISTINCTE

| câmp | ce înseamnă | unitate | unde se folosește | test |
|---|---|---|---|---|
| `K_struct` | **bare** la stânga și la dreapta pentru confirmarea unui swing fractal | bare | §3.1, exclusiv | swingul se confirmă la `j + K_struct` |
| `n_external_swings` | **swing-uri** confirmate formate în exteriorul limitei rupte | număr | §5, promovare | promovarea la al 2-lea |

```
K_struct = 2                (decizie CEO — bare, NU swing-uri)
n_external_swings = 2       (decizie CEO — swing-uri, NU bare)
★ INTERZIS ca K_struct să fie folosit drept număr de swing-uri. Sunt câmpuri separate,
  cu identități separate în fingerprint, și trebuie să rămână separate în snapshot.
```

---

# 5 — PROMOVAREA LA TREND MACRO

```
P1  prețul părăsește limita ÎNGHEȚATĂ a MACRO-ului
P2  BREAKOUT_ACCEPTED confirmat (N_accept = 3 închideri consecutive în afară)
P3  n_external_swings = 2 swing-uri CONFIRMATE, formate ÎNTREG în exteriorul limitei rupte
       TREND_UP:   swing high peste maximul ruperii, apoi swing low peste boundary_upper
       TREND_DOWN: swing low sub minimul ruperii, apoi swing high sub boundary_lower
P4  episodul RANGE anterior ÎNCHIS (end_ts scris) dar PĂSTRAT INTEGRAL

confirm_ts(promovare) = confirm_ts al AL DOILEA swing exterior
                      = bara j₂ + K_struct
★ NU la bara extremei. NU la primul swing. Un extrem e impuls; două sunt structură.
refuz: PROMOTION_REFUSED_PRECONDITION_<P1|P2|P3|P4>
```

---

# 6 — BREAKOUT ACCEPTANCE, `N_accept = 3`

```
b0  prima închidere în afara limitei ÎNGHEȚATE → BOUNDARY_EXCURSION, closes_outside = 1
                                                 NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT
b1  a doua închidere în afară                  → closes_outside = 2, încă nerezolvat
b2  a treia închidere CONSECUTIVĂ în afară     → BREAKOUT_ACCEPTED, end_ts = b2
★ REINTRARE înaintea celei de-a treia închideri → contorul se RESETEAZĂ la 0
   și, dacă reintrarea e în fereastra K_reentry → SWEEP_CONFIRMED, macro-ul SUPRAVIEȚUIEȘTE
```

## Ce se întâmplă dacă prețul revine DUPĂ un breakout acceptat

```
episodul acceptat NU se rescrie. `BREAKOUT_ACCEPTED` a fost adevărat la b2 și rămâne adevărat.
revenirea acționează asupra episodului SUCCESOR:
   dacă succesorul e un RANGE nou care conține vechea zonă → eveniment FAILED_BREAKOUT_* pe SUCCESOR
   legătura se citește prin predecessor_id
★ A rescrie episodul închis ar fi falsificare de istoric, interzisă prin contract.
```

---

# 7 — S3 ÎNCHIS: ROLURI RETROSPECTIVE, UNIFORM PENTRU RANGE ȘI TREND

```
stare vie, uniformă pe orice episod neterminat:  BALANCE
   ★ denumire NEUTRĂ UNICĂ. ACCUMULATION/DISTRIBUTION nu există ca stări vii.
   violare: ROLE_ASSERTED_BEFORE_CONFIRMATION, fail-closed.
```

## Schema completă, identică pentru RANGE și TREND

```
role              OPȚIONAL. NULL e o valoare VALIDĂ și EXPLICITĂ, nu o eroare.
role_known_ts     OBLIGATORIU dacă role ≠ NULL.   CONSTRÂNGERE: role_known_ts >= confirm_ts
                  ★ verificată prin tip; violarea = ROLE_KNOWN_BEFORE_CONFIRM, fail-closed
imutabile         structure_id · start_ts · confirm_ts · boundary_lower · boundary_upper · state
```

| episod | rol posibil | condiție |
|---|---|---|
| `RANGE_MACRO` închis | `ACCUMULATION_CONFIRMED` | ieșire bullish acceptată ȘI `n_external_swings` satisfăcut |
| `RANGE_MACRO` închis | `DISTRIBUTION_CONFIRMED` | simetric bearish |
| **`TREND_UP` închis** | `TREND_EXHAUSTION_CONFIRMED` | succesorul e `RANGE_MACRO` confirmat, nu un alt trend |
| **`TREND_UP` închis** | `TREND_CONTINUATION_CONFIRMED` | succesorul e tot `TREND_UP` |
| `TREND_DOWN` închis | idem, simetric | |
| orice episod | **`NULL`** | nimic nu s-a confirmat — **valid și frecvent** |

> **Rolul NU modifică starea istorică observată înainte de `role_known_ts`. Orice consumator care citește `role` trebuie să citească ȘI `role_known_ts`. Un jurnal care păstrează rolul și pierde momentul cunoașterii falsifică istoria.**

---

# 8 — CELE ȘAPTE VALORI RĂMASE

| nume | definiție | unitate | nivel | interval identificabil | sursa | regulă de selecție, PREÎNREGISTRATĂ | test nevacuitate | statut | fingerprint |
|---|---|---|---|---|---|---|---|---|---|
| `d_macro` | durata minimă a unui MACRO | bare | MACRO | `[4, 480]`, mediană 55, n=114 | duratele etichetate | **niciuna nefitată** — corpusul dă distribuția, nu punctul | T4 | **`CONVENTION_CEO_REQUIRED`** | da |
| `d_internal` | durata minimă a unui INTERNAL | bare | INTERNAL | sub-range `[8,132]` n=12; canal `[11,110]` n=22 | idem | **niciuna nefitată** | T2 | **`CONVENTION_CEO_REQUIRED`** | da |
| `K_reentry` | bare până la reintrare | bare | EVENT | `[4, 22]`, mediană 10, n=66 | durata sweep-urilor etichetate — **exact aceeași mărime** | **cea mai mică valoare din rețeaua pas 2 care NU exclude niciun sweep etichetat** = ceil(max observat) | T8 | **`IDENTIFIABIL`** | da |
| `w_atr` | semilățimea zonei | ×ATR | ambele | din benzile etichetate ale limitelor | CEO a scris limite ca benzi, ex. `1723-1725` | **mediana (lățimea benzii / 2) / ATR_ref, peste toate benzile etichetate** | T5/T6 | **`IDENTIFIABIL`** | da |
| `tol_cluster` | toleranța de apartenență la cluster | ×ATR | ambele | idem | idem | **mediana (lățimea benzii) / ATR_ref** — banda e chiar dispersia pe care CEO o acceptă între swing-uri | T5/T6 | **`IDENTIFIABIL`** | da |
| `n_touch` | membri minimi per cluster | număr | ambele | moștenit 2 | V2 | **plafon structural: 2** — sub 2 nu există mediană de cluster, deci nici frontieră | T5/T6 | **`CONVENTION_CEO_REQUIRED`** (moștenit, neratificat) | da |
| `atr_window` | fereastra ATR | bare | ambele | moștenit 14 | V1 | **niciuna** — nimic din etichete nu îl atinge | — | **`NOT_IDENTIFIABLE`** | da |

```
DECISE deja de CEO și NEDISCUTATE aici: K_struct = 2 · n_external_swings = 2 · N_accept = 3
```

## 8.1 De ce nu am aplicat regulile în acest document

**Regulile de mai sus sunt PREÎNREGISTRATE, nu executate.** Aplicarea lor e etapa 3 din §10 și se face într-un **commit separat care îl citează pe acesta** — exact tiparul care a protejat `w_atr` la `4e69e22 → c29ac98`. A propune o regulă și a o aplica în același document ar șterge tocmai dovada de precedență care face valoarea credibilă. **Cer acceptarea celor trei reguli înainte de a le rula o singură dată.**

## 8.2 Ce lipsește pentru cele neidentificabile

```
d_macro, d_internal   lipsește o CONVENȚIE, nu o măsurătoare. Corpusul dă distribuția;
                      orice punct din ea e fie o optimizare (interzisă), fie arbitrar.
                      Ce ar debloca: CEO declară semantica pragului — de exemplu
                      „un range macro e cel puțin o sesiune" — iar eu îl traduc în bare.
n_touch               moștenit 2. Plafonul structural E 2 (sub 2 nu există mediană),
                      deci singura întrebare e dacă CEO vrea mai mult. Decizie, nu măsurătoare.
atr_window            nimic din etichetele CEO nu privește ATR-ul. Ar cere fie o convenție,
                      fie un corpus adnotat cu volatilitate — care nu există.
```

---

# 9 — MAPAREA CELOR 114 SEGMENTE

**Regula §2 aplicată MECANIC. Nu am inventat informație absentă.**

```
   MACRO                          88   (77,2% din 114)
   LEVEL_ASSIGNMENT_UNRESOLVED    26   (22,8%)
   INTERNAL                       12   ← de pe nivelul 2, numărate SEPARAT de cele 114
```

| pe lungime | MACRO | UNRESOLVED | | pe bloc | MACRO | UNRESOLVED |
|---|---|---|---|---|---|---|
| 96 | 25 | 3 | | B1 | 24 | 4 |
| 288 | 33 | 7 | | B2 | 22 | 7 |
| 480 | 30 | 16 | | B3 | 19 | 5 |
| | | | | B4 | 23 | 10 |

## Regulile care justifică fiecare atribuire

```
R1a  MACRO, HIGH      segmentul CONȚINE structuri de nivel 2 → e demonstrat părinte.
                      8 ferestre: BLIND-009/011/012/019/020/022/034/037
R1b  MACRO, MEDIUM    fereastra nu afirmă niciun regim care să o cuprindă → niciun părinte candidat
R3   UNRESOLVED       fereastra AFIRMĂ un regim spanning în câmpul `macro`, dar în TEXT LIBER,
                      fără limite de bară → există părinte CANDIDAT, containment-ul nedecidabil.
                      8 ferestre: BLIND-023/029/031/032/035/038/039/044
R2   INTERNAL, HIGH   segment de nivel 2, conținut temporal într-un segment de nivel 1
```

**Informația lipsă, pentru cele 26 `UNRESOLVED`:** limitele de bară ale regimului afirmat în text liber. **Ambiguitatea:** un `RANGE` de nivel 1 dintr-o fereastră marcată `STEPWISE_TREND_UP` e fie MACRO, fie INTERNAL în interiorul trendului — nedecidabil fără acele limite.

**Exemple:** MACRO pozitiv `BLIND-019#L1-1` (0-480, conține 6 interne) · MACRO negativ — `BLIND-002` `CHANNEL_DOWN` 0-49, nu e RANGE · INTERNAL pozitiv `BLIND-012#L2-1` (0-52 în 0-96) · INTERNAL negativ — cele 40 de ferestre fără nivel 2 · UNRESOLVED pozitiv `BLIND-035` (macro = `STEPWISE_TREND_UP_WITH_INTERNAL_RANGES`).

**Tabelul complet, segment cu segment, în `BLIND_BATCH_02_LEVEL_MAPPING.md`.**

---

# 10 — TESTELE DE NEVACUITATE

| # | condiție | trece | eșuează | populație | câmp output | reason code |
|---|---|---|---|---|---|---|
| T1 | MACRO populat | 88 segmente | — | 114 | `depth = 0` | `OK_RANGE_MACRO` |
| T2 | INTERNAL populat | 12 segmente, 8 ferestre | 40 ferestre fără | 34 nivel 2 | `depth = 1` | — |
| T3 | `LEVEL_ASSIGNMENT_UNRESOLVED` accesibil | **26 segmente** | 88 rezolvate | 114 | `level` | `PARTIAL_OVERLAP_NO_CONTAINMENT` |
| T4 | confirmarea range | `BLIND-019` 480 bare | `BLIND-002` canal 0-49 | 282 | `RANGE_CONFIRMED` | `TOO_SHORT_MACRO` |
| T5 | cluster superior | `BLIND-019` | `BLIND-041`, bandă 3 puncte | toate episoadele | `boundary_upper` | `SWING_OUTSIDE_CLUSTER` |
| T6 | cluster inferior | idem | idem | idem | `boundary_lower` | idem |
| T7 | zone degenerate | `BLIND-041` separare 3 pct | `BLIND-019` separare 13 | 24 declanșări la V3 | `Unavailable` | `ZONES_DEGENERATE` |
| T8 | sweep | 66 etichetate | 58 breakout-uri | 124 evenimente | `SWEEP_CONFIRMED` | — |
| T9 | breakout acceptat | 58 etichetate | 11 failed | 69 | `BREAKOUT_ACCEPTED` | — |
| T10 | promovare la trend | 8 ferestre cu trend în text | 40 fără | 48 | `TREND_UP/DOWN` | `PROMOTION_REFUSED_*` |
| T11 | rol retrospectiv | HBL-20 → `ACCUMULATION_CONFIRMED` | episoade fără rol | toate | `role` | — |
| T12 | canal intern cu MACRO păstrat | `BLIND-019` bara 20 | — | 8 ferestre | `depth 0` neschimbat | `PROMOTION_REFUSED_P1` |

```
★ T10 rămâne SLAB: cele 8 exemple pozitive sunt text liber, fără limite de bară. Testabil ca
  EXISTENȚĂ, netestabil ca MOMENT. Îl las în contract cu această limitare declarată, nu ascunsă.
★ MICRO nu apare: zero exemple → în BACKLOG, nu în contractul VE. Propria mea regulă.
```

---

# 11 — PROTOCOLUL DE CONSTRUCȚIE ȘI ÎNGHEȚ

```
1 contract final (ACEST document)          2 protocol numeric preînregistrat (§8, LIVRAT)
3 identificarea valorilor pe construction  4 configurație fixată
5 prototip VE                              6 verificare pe construction
7 înghețare cod/config/fingerprint         8 lot nou blind
9 Red Team
★ Suntem la finalul etapei 2. Etapa 3 cere acceptarea regulilor + 2 convenții CEO.

orice schimbare după îngheț → POST_FREEZE_CONFIG_DRIFT, invalidează verdictul blind
config_id = hash peste toți parametrii + contract_version, înregistrat la fiecare rulare
corpusul rămâne CEO_ASSISTED_CONSTRUCTION_ONLY · 70% NU e țintă · PnL INTERZIS
```

---

# 12 — MATRICEA DE IMPLEMENTABILITATE

**Livrată PARȚIAL, fiindcă răspunsul e NU. Rândurile blocate sunt marcate, nu omise.**

| cerință | regulă/formulă | input | output | reason code | test | poz. | neg. |
|---|---|---|---|---|---|---|---|
| swing confirmat | `max(high[j±K])`, confirm la `j+K` | high/low | swing | — | T5 | oricare | — |
| cluster superior | §3.3, `\|p−center\| ≤ tol·ATR` | swing-uri | `boundary_upper` | `SWING_OUTSIDE_CLUSTER` | T5 | `BLIND-019` | `BLIND-041` |
| centrul zonei | `MEDIAN(membri)` | membri | `center` | — | T5 | — | — |
| zonă | `center ± w_atr·ATR_ref` | center, ATR | zonă | — | T5 | **★ `w_atr` LIPSĂ** | |
| degenerare | `sup−inf ≤ 2·w_atr·ATR` | centre | `Unavailable` | `ZONES_DEGENERATE` | T7 | `BLIND-041` | `BLIND-019` |
| îngheț | la `confirm_ts` | — | clustere imutabile | — | T4 | — | — |
| confirmare | `\|membri\|≥n_touch ∧ durată≥d_macro ∧ disjuncte` | — | `RANGE_CONFIRMED` | `TOO_SHORT_MACRO` | T4 | `BLIND-019` | **★ `d_macro` LIPSĂ** |
| atribuire nivel | R1/R2/R3 §2 | ierarhie | `depth` | `LEVEL_ASSIGNMENT_UNRESOLVED` | T1-T3 | 88 | 26 |
| sweep | reintrare ≤ `K_reentry` | închideri | `SWEEP_CONFIRMED` | — | T8 | HBL-20 b56 | **★ `K_reentry` LIPSĂ** |
| breakout | 3 închideri consecutive | închideri | `BREAKOUT_ACCEPTED` | — | T9 | `BLIND-023` | 11 failed |
| promovare | P1-P4, `n_external_swings=2` | swing-uri | `TREND_*` | `PROMOTION_REFUSED_*` | T10 | 8 text liber | 40 |
| rol | `role_known_ts ≥ confirm_ts` | episod închis | `role` | `ROLE_KNOWN_BEFORE_CONFIRM` | T11 | HBL-20 | fără rol |

---

# 13 — SNAPSHOT, IDENTITATE, INCOMPATIBILITĂȚI

```
contract_version  range-hierarchical-v4.2      structure_schema  range-structure-v4.2
snapshot_schema   range-snapshot-v4.2          identity_version  range-identity-v4.2
config_id         hash peste TOȚI parametrii + contract_version

SNAPSHOT   macro_active + macro_history · internal_active + internal_history (cu parent_structure_id)
           clusters {membri, center, frozen: bool, ATR_ref} pentru fiecare episod activ
           excursion_state {open_bar, direction, closes_outside, reentry_seen, applies_to}
           swing_buffer cu fereastra de reținere DECLARATĂ · id_counters monotone
           roles_assigned [(structure_id, role, role_known_ts)]
           contract_version + config_id OBLIGATORII

★ restaurarea cu alt contract_version SAU alt config_id → SNAPSHOT_CONTRACT_MISMATCH, fail-closed.
  Restaurarea tăcută a V1/V2/V3/v4.0/v4.1 e INTERZISĂ.

INCOMPATIBIL cu: V1 max+close · V2 ancoră fixă 512 · V3 segment unic · V3 K≤N ·
                 V3 IS_CHANNEL=respingere · v4.0 ACCUMULATION stare vie · v4.1 trei niveluri
Fingerprint RECALCULAT; rezultatele anterioare NECOMPARABILE PRIN TIP.
```

---

# 14 — CE RĂMÂNE DESCHIS

```
BLOCANT     d_macro și d_internal cer o CONVENȚIE CEO — corpusul dă distribuția, nu punctul.
BLOCANT     w_atr, tol_cluster, K_reentry au reguli preînregistrate NEAPLICATE (etapa 3).
BLOCANT     n_touch (moștenit 2) și atr_window (moștenit 14) nu sunt ratificate sub V4.
MATERIAL    26 din 114 segmente rămân UNRESOLVED. Se rezolvă doar cu limite de bară pentru
            regimurile afirmate în text liber — o adnotare, nu o inferență.
MATERIAL    T10 e testabil ca existență, nu ca moment.
LIMITARE    MICRO în backlog. Rămâne netestabil până există un corpus cu trei niveluri.
LIMITARE    Corpusul e CEO_ASSISTED: poate arăta că stările sunt VII, niciodată că sunt CORECTE.
```

---

**Invariante verificate neatinse:** `n_generated_total = 363` · `m_inference = 26` · tombstones · registrul Alpha · verdictele existente · F1-F6 · F7 `SAFETY_GUARD` · LIVE_SHADOW · broker gate. Detectorul NU a fost rerulat, niciun cod nu a fost implementat, `SEALED/OOS_ACCESS = 0`.

**Manifest:** v2.7.91. **VE rămâne în HOLD.**
