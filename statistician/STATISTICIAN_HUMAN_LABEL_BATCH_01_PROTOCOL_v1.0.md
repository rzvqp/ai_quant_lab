# STATISTICIAN — PROTOCOL PREÎNREGISTRAT: LOT DE ETICHETARE UMANĂ `HBL-01 … HBL-24`

**Document ID:** STAT-RANGE-HUMAN-LABEL-BATCH-01-PROTOCOL-v1.0 · **Data:** 2026-08-18 · **Autor:** Statistician
**Decizie CEO consumată:** VARIANTA 2 — generarea unui corpus vizual blind pentru etichetare umană.

> **★ ACEST DOCUMENT SE COMITE ȘI SE ÎMPINGE ÎNAINTE DE A CITI VREO BARĂ PENTRU SELECȚIE. Commit-ul lui e dovada de precedență. Orice rezultat publicat ulterior se raportează la ACEASTĂ versiune, într-un commit SEPARAT care o citează.**

**Status intermediar:** `RANGE_HUMAN_LABEL_PROTOCOL_PREREGISTERED`

---

# 0 — VERIFICARE GIT ȘI CONFIRMĂRI

```
RED TEAM      0e1a385  RT-RANGE-0003 (E78)                    2026-08-18 21:43:54 +0300  ✔
              LEDGER E78 prezent, STATE OPERATIONAL, next entry 79                        ✔
VE            aa01f41  build 0.3.1                            2026-08-18 21:17:59 +0300  ✔
              18d1aa1  delivery 0.3.1                         2026-08-18 21:18:15 +0300  ✔
              wheel SHA-256 048ee2b495112c9f90b39d65a7d6bd851764a46f1e32b0eda7c6ad2a42686cca ✔ re-hash direct
STATISTICIAN  5200647  ruling escrow + reason codes           2026-08-18 22:14:29 +0300  ✔
MANIFEST      451d400  v2.7.82                                2026-08-18 22:14:02 +0300  ✔
              fingerprint 7372ad1781e314399c55741c985a743a9418b203f4ba06e432f499362ca107aa ✔ recalculat
STATUS        RANGE_V2_BLIND_ESCROW_REPAIR_BLOCKED_NO_INDEPENDENT_SEMANTIC_GROUND_TRUTH_REMAINS ✔
```

```
RC-07 / RC-08 = SEMANTIC_ONLY_NOT_BLIND_ELIGIBLE                        ✔ (0 bare canonice, măsurat la v2.7.82)
detectorul 0.3.1 NU a fost rulat pe niciun corpus nou                    ✔
BLIND_OUTPUT_NOT_ACCESSED                                               ✔
SEALED/OOS_ACCESS = 0                                                   ✔
```

---

# 1 — POPULAȚIA ELIGIBILĂ

```
simbol / TF     OANDA:XAUUSD / M15, bare CANONICE, loaderul pre-holdout (197.094 bare)
blocuri         cele PATRU oficiale, exact cum sunt în manifest:
                  B1  2011-07-26 16:30 → 2013-09-27 16:45
                  B2  2016-01-11 09:00 → 2018-04-06 11:52
                  B3  2020-08-11 06:45 → 2021-09-05 12:15
                  B4  2022-12-16 10:45 → 2025-10-12 23:15
exclus           tot ce e în afara celor patru blocuri; embargo; SEALED; OOS
```

## 1.1 Ce se exclude, cu tampon de 96 bare de fiecare parte

```
RC-03  2016-12-20 → 2016-12-27      construcție
RC-04  2016-09-21 → 2016-10-31      construcție
RC-05  2022-12-16 → 2022-12-30      construcție
RC-06  ⊂ RC-05                      acoperit de excluderea RC-05
RC-01 · RC-02 · RC-07 · RC-08       0 bare canonice — regula se aplică oricum, prin construcție nu taie nimic
RC-CONSTRUCTION-CHANNEL-NEW-01      index canonic [192, 288)
```

## 1.2 Reguli tehnice de admisibilitate a unei ferestre

Fie `L` lungimea ferestrei și `C = 24` barele de context de fiecare parte. **Întinderea RANDATĂ** este `[s − C, s + L + C)`.

```
R1  întinderea RANDATĂ stă INTEGRAL într-un singur bloc canonic
R2  MARGINE DE BLOC: întinderea randată stă la cel puțin 96 bare de ambele capete ale blocului
    (așa se elimină „marginile incomplete ale blocurilor")
R3  FĂRĂ LIPSURI INTERNE: niciun interval între bare consecutive din întinderea randată nu depășește
    49 de ore. 49h e ÎNCHIDEREA NORMALĂ DE WEEKEND (vineri 21:00 UTC → duminică 22:00 UTC), citită
    din chiar corpusul canonic. Un weekend obișnuit NU e o lipsă; orice pauză mai lungă (sărbători,
    hiat de livrare) ESTE și descalifică fereastra.
R4  întinderea randată nu atinge niciun interval exclus de la §1.1, nici tamponul lui de 96 bare
R5  NESUPRAPUNERE: întinderea randată a oricăror două ferestre selectate e disjunctă ȘI separată
    prin cel puțin 96 bare
```

---

# 2 — SEED-UL ȘI GENERATORUL PSEUDOALEATOR

```
SEED = SHA256( "RANGE_HUMAN_LABEL_BATCH_01|0e1a385|CEO_VARIANTA_2" )     — șirul EXACT, ASCII, fără terminator
```

Fluxul de numere e **contor-mod SHA-256**, ca oricine să-l poată reproduce fără a depinde de implementarea PRNG a vreunui limbaj:

```
bloc_k   = SHA256( SEED ‖ uint64_big_endian(k) )        k = 0, 1, 2, …
fluxul   = concatenarea blocurilor, citită în felii de 8 octeți
extragerea j-a  u_j = uint64_big_endian( felia j )
candidat        s   = ELIGIBLE[ u_j mod len(ELIGIBLE) ]
```

`ELIGIBLE` = lista SORTATĂ CRESCĂTOR a indicilor canonici `s` care satisfac R1-R4 pentru lungimea `L` curentă. Sortarea o face reproductibilă.

---

# 3 — ALGORITMUL DE SELECȚIE, EXACT

```
ORDINEA e FIXATĂ AICI și e singura sursă a numerotării HBL:
    pentru bloc in (B1, B2, B3, B4):              # ordine cronologică
        pentru L in (96, 288, 480):               # ordine crescătoare
            pentru repetare in (1, 2):            # două ferestre
                extrage următorul candidat din flux
                dacă încalcă R1-R5 → REFUZĂ, consemnează motivul, consumă
                   URMĂTOAREA valoare din flux, repetă
                altfel → ACCEPTĂ, atribuie următorul ID HBL

rezultat: 24 ferestre = 8 × 96 + 8 × 288 + 8 × 480, câte 6 pe bloc
ID-uri: HBL-01 … HBL-24, în ORDINEA SELECȚIEI, niciodată reordonate după aspect
```

## 3.1 Ce NU are voie să atingă selecția

```
RANGE_STATE · N1 · Router · detector de pantă · detector de breakout · PnL · strategie ·
etichete istorice · ATR · swing-uri · volatilitate · randament · orice output de detector
```

> **Selecția citește DOAR `time`. Nu citește `open`, `high`, `low`, `close` decât la RANDARE, după ce toate cele 24 de ferestre sunt deja fixate. O fereastră nu poate fi respinsă fiindcă „nu arată interesant" — criteriul de respingere e exclusiv tehnic (R1-R5) și e enumerat mai sus.**

## 3.2 Plafon de siguranță

```
Dacă fluxul consumă 10.000 de extrageri fără a completa cele 24 de ferestre:
    RANGE_HUMAN_LABEL_BATCH_BUILD_BLOCKED_INSUFFICIENT_ELIGIBLE_WINDOWS
Nu se relaxează nicio regulă ca să iasă numărul. Nu se schimbă seed-ul.
```

---

# 4 — RANDAREA

```
Un grafic candlestick standardizat per fereastră, IDENTIC ca stil:
   fundal negru · lumânări bullish turcoaz · lumânări bearish albe
   același raport de aspect · aceeași regulă de margine (5% sus/jos peste extremele randate)
   ZERO indicatori · ZERO medii mobile · ZERO trendline · ZERO dreptunghiuri
   ZERO etichete RANGE · ZERO output de detector · ZERO sugestie de clasificare
```

Fiecare grafic afișează: `OANDA:XAUUSD`, `M15`, ID-ul ferestrei, axa timpului cu dată și oră, **fusul orar `UTC`**, axa prețului, toate lumânările ferestrei, plus **24 bare context înainte și 24 după** acolo unde populația permite.

```
Barele de CONTEXT se marchează DISCRET (estompate + o bandă etichetată „CONTEXT" la capete).
CEO clasifică NUMAI fereastra centrală.
Numele fișierului conține DOAR ID-ul. Perioada rămâne în manifestul intern.
```

---

# 5 — LIVRABILE

```
RANGE_HUMAN_LABEL_BATCH_01.pdf          o fereastră pe pagină, lizibil
HBL-01.png … HBL-24.png                 24 imagini individuale
RANGE_HUMAN_LABEL_RESPONSE_01.md        formularul CEO (fără date calendaristice)
manifest intern content-addressed       intervale exacte + hash OHLC per fereastră
SHA-256 pentru fiecare imagine · pentru PDF · pentru barele fiecărei ferestre
```

> **PDF-ul și PNG-urile ARATĂ axa temporală, deci dezvăluie intervalele. De aceea PDF-ul, PNG-urile și manifestul intern se păstrează ÎN AFARA repo-urilor citite de VE/Alpha, lângă escrow-ul Red Team. În repo se publică DOAR hash-urile și formularul, care nu conține nicio dată.**

---

# 6 — FORMULARUL CEO

Pentru fiecare `HBL-xx`, exact o clasificare principală din `RANGE · CHANNEL_UP · CHANNEL_DOWN · TREND · AMBIGUOUS`.

```
dacă RANGE      început aprox · sfârșit aprox · limită superioară aprox · limită inferioară aprox ·
                breakout ∈ {UP, DOWN, FAILED, SWEEP, NONE} · încredere ∈ {HIGH, MEDIUM, LOW}
dacă CHANNEL    început aprox · sfârșit aprox · direcție · încredere
dacă AMBIGUOUS  fereastra NU va produce verdict semantic PASS/FAIL și NU va fi forțată într-o clasă
```

---

# 7 — REGULA PENTRU UN AL DOILEA LOT

```
NU se generează automat lotul 2. După etichetarea tuturor celor 24 se verifică pragul:
    ≥ 2 RANGE · ≥ 1 CHANNEL_UP · ≥ 1 CHANNEL_DOWN
Dacă lipsesc clase: se RAPORTEAZĂ și se cere decizie nouă.
NU se extrag ferestre suplimentare până iese distribuția dorită — asta ar fi exact selecția pe
rezultat pe care întregul protocol există ca să o excludă.
```

---

# 8 — PROTECȚIA BLIND ÎN ACEASTĂ ETAPĂ

```
NU se transformă încă etichetele în expected outputs   NU se rulează detectorul
NU se arată ferestrele lui VE                          NU se publică intervalele în repo-urile VE/Alpha
NU se comunică nicio clasificare sugerată              NU se deschid RC-07/RC-08
ZERO SEALED/OOS · ZERO Alpha · ZERO PnL · ZERO cost gate · ZERO p-value · ZERO AI Trader ·
ZERO regresie AI Trader · ZERO LIVE_SHADOW cutover · ZERO broker · ZERO order_send
```

**Invariante neatinse:** `n_generated_total = 363` · `m_inference = 26` · tombstones · registrul Alpha · verdictele existente · F1-F6 și cele 44 `BLOCKED_PENDING_RANGE_SEMANTIC_FIX` · F7 `SAFETY_GUARD`.

---

# 9 — ORDINEA DE EXECUȚIE, OBLIGATORIE

```
1. ACEST document se comite și se împinge; hash local = remote se verifică.   ← dovada de precedență
2. Abia apoi se citesc timestamp-urile și se execută selecția (§1-§3).
3. Abia apoi se citesc OHLC-urile și se randează (§4).
4. Rezultatul se publică într-un commit SEPARAT care îl citează pe acesta.
Dacă §3.2 lovește plafonul, se publică BLOCKED. Nu se revine la §2 cu reguli schimbate.
```

**Status terminal așteptat:** `RANGE_HUMAN_LABEL_BATCH_01_READY_FOR_CEO` · **următorul proprietar:** `CEO_HUMAN_RANGE_LABELING`.
