# STATISTICIAN — FIȘĂ DE DECIZIE: PARAMETRII `range-hierarchical-v4.2`

**Document ID:** STAT-RANGE-V4.2-PARAM-DECISION-SHEET-v1.0 · **Data:** 2026-08-19
**Status:** `RANGE_V4_2_PARAMETER_DECISION_SHEET_READY_FOR_CEO`
**VE rămâne în HOLD. V4.2 NU a fost modificat. NICIO regulă nu a fost aplicată.**

```
verificat   contract v4.2 5a9d5ec · manifest v2.7.91 498d5c3 ·
            fingerprint 19cb9548b99df869b5463e071fed96d26c7d92670c3040d2e22141d5f14d14d2   ✔
detectorul NU a fost rerulat · SEALED/OOS_ACCESS = 0
```

---

# 1 — CELE ȘAPTE VALORI

| # | parametru | definiție simplă | formulă | unitate | nivel | statut | sursă | interval permis | dacă e prea MIC | dacă e prea MARE |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `K_reentry` | câte bare are prețul la dispoziție ca să se întoarcă în zonă înainte ca absența să conteze | fereastră: reintrare la bara `b0+j`, `j <= K_reentry` | bare | EVENT | **IDENTIFIABIL** | durata sweep-urilor etichetate, n=66 | `[1, N_accept·(ceva) )`, practic `[1, 22]` observat | sweep-uri reale ratate — **exact defectul V3, unde plafonul de 2 bare tăia toate cele 66** | breakout-uri reale rămân „pending" prea mult; `BREAKOUT_PENDING` se acumulează |
| 2 | `w_atr` | jumătatea lățimii benzii din jurul centrului zonei | `zonă = centru ± w_atr · ATR_ref` | ×ATR | ambele | **IDENTIFIABIL** | benzile de limite scrise de CEO (ex. `1723-1725`) | `(0, 0.495)` — plafonul de disjuncție de la v2.7.79 | zonă prea îngustă: fitilele normale nu se înregistrează ca atingeri | zonele se apropie → `ZONES_DEGENERATE` mai des; la limită, un canal e admis ca range |
| 3 | `tol_cluster` | cât de departe poate fi un swing nou de centru ca să intre totuși în cluster | `\|price − centru\| <= tol_cluster · ATR_ref` | ×ATR | ambele | **IDENTIFIABIL** | idem, lățimea benzii | `(0, ?)`, constrâns `>= w_atr` (vezi §1.1) | clustere sărace: sub `n_touch` membri, episodul nu se confirmă | clustere care înghit swing-uri neînrudite → centru fals, frontieră fără sens |
| 4 | `d_macro` | durata minimă a unui episod MACRO | `durată >= d_macro` | bare | MACRO | **CONVENȚIE CEO** | duratele celor 88 MACRO | `(4, 480)` deschis | poarta nu poate EȘUA — **defectul V2** | poarta nu poate REUȘI — **defectul V3** |
| 5 | `d_internal` | durata minimă a unui episod INTERNAL | `durată >= d_internal` | bare | INTERNAL | **CONVENȚIE CEO** | duratele celor 12 INTERNAL | `(8, 132)` deschis, constrâns `< d_macro` | nivelul INTERNAL se umple cu zgomot | nivelul INTERNAL rămâne gol → ierarhie decorativă |
| 6 | `n_touch` | câți swing-uri confirmate trebuie să aibă un cluster ca să existe o frontieră | `\|membri\| >= n_touch` pe fiecare latură | număr | ambele | **CONVENȚIE CEO** (plafon structural 2) | moștenit din V2 | `[2, ∞)` — sub 2 nu există mediană de cluster | **imposibil**: 2 e podeaua structurală | episoade scurte nu se pot confirma niciodată; interacționează cu `d_macro` |
| 7 | `atr_window` | fereastra ATR-ului de referință | `ATR(atr_window)` | bare | ambele | **DECIZIE ARHITECTURALĂ EXTERNĂ** (vezi §5) | N1 / AI Trader, vendorizat | fix `14`, dacă CEO acceptă importul | ATR zgomotos → zone instabile între episoade | ATR lent → zone care nu urmăresc regimul |

```
TOTAL = 7. Recalculabil: 3 IDENTIFICABILE (1,2,3) + 3 CONVENȚIE CEO (4,5,6) + 1 EXTERN (7).
NU sunt incluse, fiindcă nu sunt parametri liberi:
   s_max        DERIVAT: s_max ≡ 2·w_atr — NU se stochează separat
   K_struct     DECIS (2)          n_external_swings  DECIS (2)      N_accept  DECIS (3)
```

## 1.1 O constrângere structurală pe care o semnalez acum

> **`tol_cluster >= w_atr` trebuie impus prin tip.** Dacă toleranța de apartenență ar fi mai mică decât semilățimea zonei, ar exista swing-uri care cad ÎN zonă dar sunt REFUZATE din cluster — o contradicție internă: frontiera ar exclude puncte pe care propria ei zonă le conține. **Nu era în v4.2. E o corecție necesară, declarată aici, neaplicată.**

---

# 2 — CELE TREI REGULI PREÎNREGISTRATE, NEAPLICATE

## R-A · `K_reentry`

```
1 măsurătoarea    durata fiecărui sweep etichetat = bare de la depășire până la reintrare
2 unitățile       cele 66 de evenimente SWEEP_UP/SWEEP_DOWN din cele 48 de ferestre
3 statistica      MAXIMUL observat, rotunjit în sus la următorul punct al rețelei (pas 2)
4 direcția        CONSERVATOR = mai MARE. Motiv: prea mic taie sweep-uri reale — defectul
                  demonstrat al V3, unde plafonul de 2 bare excludea TOATE cele 66.
                  Prea mare nu produce clasificări false: `N_accept = 3` închide independent
                  ipoteza de breakout, deci `K_reentry` mare doar întârzie decizia, nu o strică.
5 egalitate       imposibilă — maximul unei mulțimi finite e unic
6 fără punct      dacă mulțimea sweep-urilor ar fi goală → `NOT_IDENTIFIABLE`. Nu e cazul (n=66).
7 nu optimizează  nu se calculează niciun recall/precision/IoU/occupancy. Criteriul e
                  NON-EXCLUDEREA, o proprietate de acoperire, nu un scor de potrivire.
                  Nu există variantă alternativă între care să aleg.
8 ce ar putea da  un punct de rețea >= 22 (maximul observat). NU îl calculez aici.
```

## R-B · `w_atr`

```
1 măsurătoarea    lățimea benzii scrise de CEO pentru fiecare limită: „1723-1725" → 2 puncte
2 unitățile       toate limitele etichetate cu bandă, pe segmentele RANGE, ambele laturi
3 statistica      MEDIANA lui (lățime_bandă / 2) / ATR_ref, cu ATR_ref evaluat cauzal la
                  confirm_ts al episodului. Mediana e convenția DEJA ratificată pentru ancoră.
4 direcția        banda CEO e incertitudinea LUI asupra limitei. Jumătatea ei e semilățimea
                  naturală. Nu aleg nici mai mult, nici mai puțin.
5 egalitate       la număr PAR de observații, mediana = media celor două centrale (convenția v2.7.80)
6 fără punct      dacă rezultatul depășește plafonul de disjuncție 0,495 → `BLOCKED`,
                  fiindcă zonele s-ar suprapune prin construcție. Se raportează, nu se trunchiază.
7 nu optimizează  se citește ce a scris omul, nu se caută ce potrivește detectorul
8 ce ar putea da  orice valoare în (0, 0.495). NU o calculez aici.
```

## R-C · `tol_cluster`

```
1 măsurătoarea    aceeași bandă, dar ÎNTREAGĂ, nu jumătatea ei
2 unitățile       identice cu R-B
3 statistica      MEDIANA lui (lățime_bandă) / ATR_ref
4 direcția        banda ÎNTREAGĂ e dispersia pe care CEO o acceptă între swing-uri ale
                  ACELEIAȘI frontiere — exact definiția apartenenței la cluster
5 egalitate       ca la R-B
6 fără punct      dacă rezultatul ar ieși sub `w_atr`, se raportează CONTRADICȚIE (§1.1)
                  și se cere decizie. NU se ajustează tăcut.
7 nu optimizează  idem R-B
8 ce ar putea da  prin construcție ≈ 2× rezultatul lui R-B. NU îl calculez aici.
```

> **Cele trei reguli sunt scrise ÎNAINTE de aplicare, în acest document. Aplicarea lor e un commit SEPARAT care îl citează pe acesta — tiparul `4e69e22 → c29ac98`. Cer acceptarea lor înainte de a le rula o singură dată.**

---

# 3 — DISTRIBUȚIILE DE DURATĂ

## 3.1 Segmentele mapate `MACRO` (n = 88)

```
min 4 · p05 11,4 · p10 17,7 · p25 29,5 · MEDIANĂ 55,5 · p75 84,0 · p90 159,4 · p95 250,0 · max 480
```

| pe lungime | n | min | p25 | mediană | p75 | max | | pe bloc | n | min | mediană | max |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 96 | 25 | 4 | 17,0 | 22,0 | 40,0 | 96 | | B1 | 24 | 12 | 60,0 | 288 |
| 288 | 33 | 7 | 37,0 | 48,0 | 80,0 | 288 | | B2 | 22 | 4 | 59,0 | 480 |
| 480 | 30 | 26 | 60,0 | 77,0 | 143,8 | 480 | | B3 | 19 | 8 | 55,0 | 288 |
| | | | | | | | | B4 | 23 | 4 | 40,0 | 250 |

## 3.2 Segmentele mapate `INTERNAL` (n = 12)

```
min 8 · p05 10,2 · p10 12,6 · p25 21,0 · MEDIANĂ 30,5 · p75 56,5 · p90 88,0 · p95 108,9 · max 132
```

| pe lungime | n | min | mediană | max | | pe bloc | n | mediană |
|---|---|---|---|---|---|---|---|---|
| 96 | 5 | 8 | 26,0 | 52 | | B1 | 2 | 54,0 |
| 288 | 3 | 18 | 35,0 | 90 | | B2 | 3 | 22,0 |
| 480 | 4 | 12 | 60,0 | 132 | | B3 | 7 | 35,0 |
| | | | | | | **B4** | **0** | **— GOL** |

> **★ `INTERNAL` are n = 12, iar blocul B4 e GOL. Orice durată aleasă pe această bază stă pe douăsprezece observații, dintre care patru la lungimea 480. E o bază subțire, și o spun înainte să fie folosită.**

## 3.3 Cele 26 `LEVEL_ASSIGNMENT_UNRESOLVED` — raportate, NEUTILIZABILE

```
n 26 · min 16 · p05 20,5 · p10 25,0 · p25 42,0 · mediană 53,5 · p75 75,0 · p90 80,0 · max 95
```

**Nu intră în alegerea duratei**, fiindcă nu se știe cărui nivel aparțin. Le raportez ca să fie vizibil că distribuția lor seamănă cu a celor MACRO — deci excluderea lor nu e nici avantajoasă, nici dezavantajoasă sistematic.

---

# 4 — CONVENȚIILE POSIBILE

**Pragurile sunt generate din poziții de percentilă declarate ÎN AVANS — p10, p25, mediană — nu alese după consecință.**

## `d_macro`, pe cele 88

| variantă | prag | eligibile | excluse doar de durată | 96 | 288 | 480 | poate trece / eșua |
|---|---|---|---|---|---|---|---|
| PERMISIVĂ | **17** bare | 80/88 (90,9%) | 8 | 19/25 | 31/33 | 30/30 | da / da |
| ECHILIBRATĂ | **29** bare | 66/88 (75,0%) | 22 | 10/25 | 27/33 | 29/30 | da / da |
| CONSERVATOARE | **55** bare | 45/88 (51,1%) | 43 | 6/25 | 14/33 | 25/30 | da / da |

## `d_internal`, pe cele 12

| variantă | prag | eligibile | excluse doar de durată | 96 | 288 | 480 | poate trece / eșua |
|---|---|---|---|---|---|---|---|
| PERMISIVĂ | **12** bare | 11/12 (91,7%) | 1 | 4/5 | 3/3 | 4/4 | da / da |
| ECHILIBRATĂ | **21** bare | 9/12 (75,0%) | 3 | 4/5 | 2/3 | 3/4 | da / da |
| CONSERVATOARE | **30** bare | 6/12 (50,0%) | 6 | 1/5 | 2/3 | 3/4 | da / da |

```
DEFECT DE VACUITATE: NICIUNA dintre cele șase variante nu produce „nu poate reuși" sau
„nu poate eșua". Toate au exemple de ambele feluri. Asta e diferența față de V2 și V3,
unde pragul stătea în AFARA distribuției observate.
```

**Consecința pe care o semnalez fără să recomand:** varianta CONSERVATOARE la `d_macro` lasă doar 6 din 25 de ferestre de 96 de bare cu vreun episod eligibil. **Nu spun că e rea** — spun că mută greutatea corpusului către ferestrele lungi, iar stratificarea pe lungimi devine dezechilibrată. Decizia e a ta.

---

# 5 — `atr_window`: POATE FI IMPORTAT?

## **DA.**

```
verificat în cod   `atr14` e o funcție VENDORIZATĂ din `ai_trader.market_state`,
                   expusă prin `raw_axes_builder.atr14()`, care returnează ATR-ul pe ULTIMA bară
                   acumulată și `None` pentru primele 14 bare (santinela proprie, tradusă la graniță)
cine o consumă     `range_engine_v2_1.py:157` și `range_engine_v3_1.py:94` — AMBELE prin
                   `self._n1._axes_builder.atr14()`, adică EXACT aceeași instanță ca N1
```

```
poate V4.2 să importe și să fixeze atr_window = 14?
   DA — ca DECIZIE ARHITECTURALĂ EXTERNĂ, nu ca alegere de parametru V4.
   Motivul e că nu se alege nimic: e convenția canonică deja consumată NESCHIMBAT de N1,
   de V2.1 și de V3.1. A o „re-identifica" ar însemna să creez o a doua definiție a ATR
   în laborator — exact fragmentarea pe care regula mea standing o interzice:
   o măsurătoare despre un modul ratificat trebuie să IMPORTE acel modul.

contradicție semantică?   NU.
   ATR e un input EXTERN mașinii de stări, nu o mărime derivată din semantica RANGE.
   V4.2 îl consumă; nu îl definește. Singura cerință e cauzalitatea, deja satisfăcută:
   valoarea e citită la bara curentă, din bare cu index <= i.

ce se schimbă        atr_window IESE din lista parametrilor liberi și intră în identitate
                     ca DEPENDENȚĂ EXTERNĂ, cu proveniență explicită.
                     config_id: trebuie să includă `atr_source` și `atr_provenance_commit`,
                     nu doar valoarea 14 — altfel două ATR-uri diferite ar da același config_id.
                     contract_version → v4.3 (schimbarea e de contract, nu de valoare).

testul de identitate  seria ATR produsă de V4 trebuie să fie BIT-IDENTICĂ cu
                      `n1._axes_builder.atr14()` pe aceleași bare, bară cu bară, inclusiv
                      `None` pe primele 14. O singură diferență ⇒ reimplementare mascată ⇒ REFUZ.
```

**Nu îl aplic. Îl prezint pentru decizie.**

---

# 6 — AL ȘAPTELEA PARAMETRU: `n_touch`

> **De ce n-a apărut în rezumat: pentru că l-am omis EU. `n_touch` era în tabelul din v4.2, rândul 6, cu statut `CONVENTION_CEO_REQUIRED` — dar în rezumatul din chat am enumerat doar șase nume. O sub-raportare a mea, nu o lipsă din contract. Cifra „șapte" era corectă; enumerarea nu.**

```
identificabil?         NU din etichete — CEO nu numără swing-uri per frontieră.
cere convenție CEO?    DA.
derivat structural?    PARȚIAL: are un PLAFON STRUCTURAL de 2, fiindcă sub doi membri
                       nu există mediană de cluster, deci nici frontieră. Podeaua e derivată;
                       valoarea peste podea nu e.
trebuie eliminat?      NU. Nu e derivabil din alt parametru, deci nu încalcă regula ta —
                       spre deosebire de `s_max`, care ESTE derivat (2·w_atr) și de aceea
                       NU se stochează separat.
```

**Singura întrebare deschisă: vrei mai mult de 2?** Un `n_touch = 3` cere frontiere mai bine sprijinite, dar interacționează direct cu `d_macro` — mai mulți swing-uri cer mai multe bare. **Cele două nu se pot alege independent**, și o spun acum, nu după.

---

# 7 — CE E DEJA FIXAT ȘI NU INTRĂ ÎN CELE ȘAPTE

| câmp | valoare | ce înseamnă | unitate |
|---|---|---|---|
| `N_accept` | **3** | închideri CONSECUTIVE în afara zonei înghețate pentru acceptarea ruperii | bare/închideri |
| `K_struct` | **2** | bare la stânga ȘI la dreapta pentru confirmarea unui swing fractal | bare |
| `n_external_swings` | **2** | swing-uri CONFIRMATE formate în exteriorul limitei rupte, pentru promovare | număr de swing-uri |

```
CONFIRM: sunt TREI noțiuni DISTINCTE, cu trei definiții, trei teste și trei câmpuri separate.
CONFIRM: identitatea configurației le păstrează SEPARAT — `config_id` hash-uiește fiecare câmp
         individual, deci `K_struct=2` și `n_external_swings=2` NU pot colapsa într-unul singur
         doar fiindcă au aceeași valoare numerică.
★ Coliziunea de nume de la v4.1 e închisă exact aici: valoarea comună 2 e o COINCIDENȚĂ,
  nu o identitate. Dacă vreodată una se schimbă, cealaltă nu se mișcă.
```

---

# 8 — RECONCILIEREA CELOR 114, FĂRĂ INTERPRETARE

```
cele 114 = segmentele RANGE de pe NIVELUL 1 al etichetelor (câmpul `segments`)

    88  MACRO
+   26  LEVEL_ASSIGNMENT_UNRESOLVED
= 114   ✓ PARTIȚIE EXACTĂ a celor 114. Fără dublă numărare. Fiecare segment are exact un statut.

cele 12 INTERNAL = segmente RANGE de pe NIVELUL 2 (câmpul `internal_structures`)
    NU sunt incluse în cele 114. Sunt o populație SEPARATĂ.
    NU au fost numărate simultan în altă categorie.

88 + 26 + 12 = 126 = TOATE segmentele RANGE de pe AMBELE niveluri
```

> **Răspuns direct la întrebare: `88 + 12 + 26 = 126` DEPĂȘEȘTE 114 fiindcă cele 12 nu fac parte din cei 114. Partiția celor 114 e `88 + 26`. Cele 12 se adaugă din a doua populație.**

---

# 9 — DECIZIILE CERUTE DE LA CEO

```
D1  Accepți cele TREI reguli preînregistrate (R-A, R-B, R-C)?  → deblochează etapa 3
D2  `d_macro`: PERMISIVĂ 17 · ECHILIBRATĂ 29 · CONSERVATOARE 55 — sau altă convenție semantică
    („un range macro e cel puțin o sesiune"), pe care o traduc eu în bare
D3  `d_internal`: PERMISIVĂ 12 · ECHILIBRATĂ 21 · CONSERVATOARE 30 — cu avertismentul că baza
    e de DOUĂSPREZECE observații și blocul B4 e gol
D4  `n_touch`: rămâne 2 (podeaua structurală) sau mai mult? Nu e independent de `d_macro`.
D5  `atr_window`: accepți importul lui `atr14` ca dependență externă, cu proveniență în
    `config_id` și contract → v4.3?
D6  Accepți corecția `tol_cluster >= w_atr` din §1.1? Fără ea, contractul e intern contradictoriu.
```

---

**Invariante verificate neatinse:** `n_generated_total = 363` · `m_inference = 26` · tombstones · registrul Alpha · verdictele existente · F1-F6 · F7 `SAFETY_GUARD` · LIVE_SHADOW · broker gate. V4.2 NU a fost modificat · nicio regulă aplicată · detectorul nererulat · `SEALED/OOS_ACCESS = 0`.

**Manifest:** v2.7.92. **VE rămâne în HOLD.**
