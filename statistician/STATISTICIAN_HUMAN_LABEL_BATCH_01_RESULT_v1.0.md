# STATISTICIAN — REZULTAT: LOTUL DE ETICHETARE UMANĂ `HBL-01 … HBL-24`

**Document ID:** STAT-RANGE-HUMAN-LABEL-BATCH-01-RESULT-v1.0 · **Data:** 2026-08-18 · **Autor:** Statistician
**Execută:** protocolul `84be9ab` (v1.0) așa cum a fost amendat de `a486c5d` (v1.1) — ambele comise **înainte** de execuție.

## STATUS TERMINAL

```
RANGE_HUMAN_LABEL_BATCH_01_READY_FOR_CEO
următorul proprietar: CEO_HUMAN_RANGE_LABELING
DETECTOR_NOT_RUN · BLIND_OUTPUT_NOT_ACCESSED · SEALED/OOS_ACCESS = 0
```

---

# 1 — VERIFICARE GIT

```
RED TEAM      0e1a385  RT-RANGE-0003 (E78)                     2026-08-18 21:43:54 +0300  ✔
VE            aa01f41 build · 18d1aa1 delivery                                            ✔
              wheel 048ee2b495112c9f90b39d65a7d6bd851764a46f1e32b0eda7c6ad2a42686cca      ✔ re-hash direct
STATISTICIAN  5200647  ruling escrow + reason codes            2026-08-18 22:14:29 +0300  ✔
MANIFEST      451d400  v2.7.82 · fingerprint 7372ad17…                                    ✔ recalculat
PROTOCOL      84be9ab  v1.0                                    2026-08-18 22:26:35 +0300  ✔
              a486c5d  v1.1 amendament                         2026-08-18 22:30:58 +0300  ✔
```

`RC-07`/`RC-08` = `SEMANTIC_ONLY_NOT_BLIND_ELIGIBLE` ✔ · detectorul 0.3.1 nu a fost rulat pe niciun corpus nou ✔

---

# 2 — PRIMA EXECUȚIE A EȘUAT, ȘI DIN VINA MEA

Rulajul sub v1.0 a lovit plafonul de siguranță și a publicat `BLOCKED` la `B3 · L = 480`. Nu a fost ghinion:

```
toate cele 393 de porniri eligibile din B3 stăteau într-O SINGURĂ rulare continuă, lată de 392 bare
două ferestre de 480 cer porniri la >= 624 bare distanță   →   MAXIM 1 fereastră   →   INFEZABIL
```

**Cauza rădăcină: `R3` contrazicea propria intenție declarată.** Textul spunea *„un weekend obișnuit NU e o lipsă"*, iar pragul îl pusesem la 49h **deducând** calendarul (vineri 21:00 → duminică 22:00) în loc să-l măsor.

```
măsurat pe coloana `time`:  ultima bară a săptămânii se deschide la 20:45, nu la 21:00
pauza reală de weekend = 49,25h — și e valoarea MODALĂ: 343 din 414
```

> **Pragul meu respingea cel mai frecvent weekend din corpus. Eroare de exact o bară, apărută fiindcă am presupus calendarul în loc să-l citesc. A ZECEA eroare a mea prinsă de mine — din aceeași familie cu regula standing: *o măsurătoare despre un modul ratificat trebuie să IMPORTE acel modul*; aici, *o regulă despre calendarul pieței trebuie să CITEASCĂ calendarul*.**

**Pragul corectat nu e o alegere.** Distribuția e bimodală cu o bandă **complet goală**:

```
weekend           43,00h … 53,25h     414 pauze
   ── ZERO pauze între 53,25h și 73,00h ──
închidere lungă   73,00h … 76,50h      19 pauze  (sărbători)
gol de livrare    > 1000h                3 pauze  (golurile dintre blocuri)
```

Orice prag din bandă dă **aceeași** mulțime eligibilă. Fixat la 60h. **Seed-ul, ordinea, duratele, numărul și toate celelalte reguli au rămas byte-identice** — schimbarea seed-ului ar fi fost gestul suspect. Rezultatul v1.0 rămâne publicat, nu șters.

---

# 3 — SELECȚIA

```
SEED = SHA256("RANGE_HUMAN_LABEL_BATCH_01|0e1a385|CEO_VARIANTA_2")
     = 0d2106730ae29213188f375ff4905d2889cfcc34b45d734ab22d1dc9d8aa86ce
extrageri totale 28  ·  ferestre acceptate 24  ·  refuzuri consemnate 4 (toate R5, în B3 L=480)
distribuție 8 × 96 · 8 × 288 · 8 × 480      pe blocuri  B1 6 · B2 6 · B3 6 · B4 6
```

## Poarta de fezabilitate, sub `R3` corectat

```
        L=96              L=288             L=480
B1   215 disjuncte     119 disjuncte      82 disjuncte
B2   203               111                74
B3   104                57                39      ← era 1 sub pragul greșit
B4   272               150               103
```

## Dovada că extragerile provin din seed

Recalculat de la zero, independent de scriptul de selecție:

```
u64_1 = 11548941747766081574   →  al 41.600-lea element eligibil din bazinul de 51.494  →  HBL-01
u64_2 = 14528207936227397228   →  al  2.932-lea din 51.494                              →  HBL-02
u64_3 = 12211466196189503346   →  al 48.074-lea din 50.918                              →  HBL-03
u64_4 =  7310836764297114917   →  al 33.265-lea din 50.918                              →  HBL-04
u64_5 =  9645502672017995562   →  al 32.298-lea din 50.342                              →  HBL-05
u64_6 =   422425441426621703   →  al 12.643-lea din 50.342                              →  HBL-06
```

Fluxul e contor-mod SHA-256, nu PRNG-ul vreunui limbaj, deci oricine îl poate reproduce.

## Refuzurile, consemnate

```
extragerea 17 · B3 L=480 start 110105 · R5
extragerea 19 · B3 L=480 start 125399 · R5
extragerea 20 · B3 L=480 start 109306 · R5
extragerea 21 · B3 L=480 start 124829 · R5
```

Fiecare refuz a consumat următoarea valoare din flux, exact cum cere protocolul. **Nicio fereastră nu a fost respinsă pentru aspect.**

---

# 4 — DOVADA CĂ DETECTORUL NU A FOST IMPORTAT SAU RULAT

```
grep în ambele scripturi după `ve_n1_replay` / `range_state` / `RANGE_STATE`:
   o SINGURĂ potrivire în fiecare — chiar linia de verificare care tipărește rezultatul
   ambele rulaje au raportat:  ve_n1_replay importat? False
în mediul de execuție:  importlib.util.find_spec("ve_n1_replay") is None
   → pachetul nu e nici măcar instalat, deci nu putea fi rulat
```

**Selecția a citit exclusiv coloana `time`.** `open/high/low/close` s-au atins abia la randare, după ce toate cele 24 de ferestre erau deja fixate — deci nicio fereastră nu putea fi aleasă după cum arată prețul.

---

# 5 — LIVRABILE

```
RANGE_HUMAN_LABEL_BATCH_01.pdf        24 pagini, o fereastră pe pagină, 1800 × 1125
   SHA-256  8599660e73711b22d1d3f25095040107e4795b856e341faabfa735193c679a76
HBL-01.png … HBL-24.png               24 imagini, hash-uri în HASHES.md
RANGE_HUMAN_LABEL_RESPONSE_01.md      formularul CEO — fără nicio dată calendaristică
INTERNAL_MANIFEST.json                intervalele exacte + hash OHLC per fereastră — NEPUBLICAT
HASHES.md                             toate hash-urile, recalculabile
```

> **PDF-ul și PNG-urile afișează axa temporală, deci dezvăluie intervalele. De aceea întregul pachet stă în `C:\Users\MEDION GAMING\ceo_labeling_batch_01\`, ÎN AFARA oricărui checkout git (`git rev-parse` eșuează acolo). În repo se publică doar acest document, hash-urile și formularul — niciunul nu conține vreo dată.**

## Cum arată graficele

```
fundal negru · bullish turcoaz · bearish alb · 1800 × 1125 pentru toate · marjă 5% peste extreme
axa prețului la dreapta · axa timpului cu dată ȘI oră, în UTC · antet OANDA:XAUUSD · M15 · ID
24 bare context înainte și 24 după, ESTOMPATE, delimitate cu o linie discretă și etichetate CONTEXT
ZERO indicatori · ZERO medii · ZERO trendline · ZERO dreptunghiuri · ZERO etichete RANGE
ZERO output de detector · ZERO sugestie de clasificare
```

Am reparat o singură problemă de lizibilitate după prima randare: etichetele de pe axa timpului se suprapuneau acolo unde un weekend aduce două limite de zi aproape una de alta. Rezolvată cu o distanță minimă de 120 px între etichete.

---

# 6 — CE URMEAZĂ, ȘI CE NU

```
Aștept etichetele CEO. Atât.
NU transform etichetele în expected outputs · NU rulez detectorul · NU arăt ferestrele lui VE
NU public intervalele în repo-urile VE/Alpha · NU sugerez nicio clasificare
NU deschid RC-07/RC-08 · ZERO SEALED/OOS
```

**Pragul pentru un al doilea lot:** ≥ 2 `RANGE`, ≥ 1 `CHANNEL_UP`, ≥ 1 `CHANNEL_DOWN`. Dacă lipsesc clase, **raportez și cer decizie** — nu extrag ferestre suplimentare până iese distribuția dorită, fiindcă asta ar fi exact selecția pe rezultat pe care protocolul există ca să o excludă.

---

# 7 — ELEMENTE DESCHISE

```
MATERIAL     Lotul e util doar dacă etichetele ies suficient de decise. `AMBIGUOUS` e un răspuns
             legitim și e declarat ca atare în formular — o etichetă nesigură dată ca sigură ar
             strica exact testul pentru care există lotul.
MATERIAL     Selecția e UNIFORMĂ pe indici eligibili, deci distribuția claselor va reflecta
             frecvența lor naturală. Dacă range-urile sunt rare, un lot de 24 poate să nu conțină
             două. Asta nu e un defect al lotului — e informație despre piață, și e exact motivul
             pentru care pragul de la §6 se raportează în loc să fie forțat.
LIMITARE     Ferestrele de 480 de bare traversează cel puțin un weekend prin construcție (o
             săptămână de tranzacționare are ~460 bare). Discontinuitatea e vizibilă în grafic.
NON_MATERIAL Barele de context pot depăși marginal limitele blocului doar dacă R2 ar fi încălcat —
             nu se poate întâmpla, R2 cere 96 bare marjă, iar contextul are 24.
```

---

**Invariante verificate neatinse:** `n_generated_total = 363` · `m_inference = 26` · tombstones · registrul Alpha · verdictele existente · F1-F6 și cele 44 `BLOCKED_PENDING_RANGE_SEMANTIC_FIX` · F7 `SAFETY_GUARD`. Alpha, VE detector, AI Trader, regresia AI Trader, LIVE_SHADOW cutover: **nepornite**. Brokerul și autoritatea: **neatinse**.

**Manifest:** v2.7.83.
