# STATISTICIAN — REZULTAT: LOT BLIND INDEPENDENT `BLIND-001 … BLIND-048`

**Document ID:** STAT-RANGE-V3-BLIND-BATCH-02-RESULT-v1.0 · **Data:** 2026-08-19 · **Autor:** Statistician
**Execută:** protocolul `a47e942`, comis și împins **înainte** de a citi vreo bară.

## VERDICT TERMINAL

```
RANGE_V3_BLIND_LABEL_BATCH_READY_FOR_CEO
următorul proprietar: CEO, pentru etichetare independentă
DETECTOR_NOT_RUN · BLIND_OUTPUT_NOT_ACCESSED · SEALED/OOS_ACCESS = 0
```

---

# 1 — VERIFICĂRI ȘI O CONTRADICȚIE CURĂȚATĂ

```
STATISTICIAN V3  bf9f780                                                     ✔
MANIFEST v2.7.84 db098ed · cddaab381f0132eac025e9fcad3454d54fca78dc1abab6bc8b3cea05e5951233  ✔
VE 0.4.1         f9af357 build · 7dc2ff9 delivery                            ✔
   wheel SHA-256 39673910666e13708b1d4cb7266d1730bb1c9ceea4e0b021a1bf3cfa1f8281f4
                 extras din Git și re-hash-uit; se potrivește cu 39673910…81f4 din mandat  ✔
RED TEAM         10c2d46  RT-RANGE-0005 (E80)                                ✔
PROTOCOL         a47e942  2026-08-19 13:26:15 +0300, împins pe toate 4 oglinzile  ✔
```

> **Contradicție găsită și eliminată înainte de a scrie protocolul: `ve_n1_replay 0.3.1` și `ve_brain` rămăseseră INSTALATE din mandatul precedent, unde rularea detectorului era cerută pentru diagnostic. Le-am dezinstalat și am verificat că `find_spec` returnează `None` pentru ambele. `DETECTOR_NOT_RUN` trebuie să fie o proprietate a mediului, nu o promisiune.**

Testele VE 0.4.1 nu ating corpusul canonic — fixture-uri sintetice, între care `_hbl20_bars`, derivat din HBL-20. Acoperit integral de excluderea Batch 01.

---

# 2 — DIMENSIUNEA: DERIVATĂ, NU MOȘTENITĂ

```
ESTIMAND      p = recall pe segmente RANGE etichetate de om
              (ales fiindcă defectul dominant măsurat la v2.7.84 a fost OMISIUNEA — 37 din 66
               de segmente — nu clasificarea greșită. Se estimează ce a eșuat.)
IPOTEZE       Wald/Wilson 95% · p = 0,5 (varianță maximă) · semilățime țintă w = 0,15
              rata de segmente/fereastră: PRIOR SLAB din Batch 01 (asistat) 0,875 / 1,125 / 1,375
              segmentele din aceeași fereastră NU sunt strict independente ⇒ interval puțin
              prea îngust, declarat aici, nu descoperit ulterior
CALCUL        n_segmente = 1,96² × 0,25 / 0,15² = 42,7 → 43
              k = 3 → 36 ferestre → 40,5 segmente  ✗ SUB prag
              k = 4 → 48 ferestre → 54,0 segmente  ✓
FIXAT         N = 48 ferestre · 16 pe lungime · 12 pe bloc · 4 batch-uri × 12
```

**De ce `w = 0,15` și nu mai fin:** e o poartă semantică de primă trecere. O țintă mai strânsă ar cere o sarcină umană care riscă **oboseala de etichetare** — ea însăși o sursă de bias, și una pe care nu o pot corecta ulterior.

**Sensibilitate declarată:** dacă rata reală e cu 25% sub priorul asistat, cele 48 de ferestre dau 40,5 segmente ⇒ semilățime 0,155 în loc de 0,150. **Consecință minoră, și NU se compensează cu ferestre suplimentare.**

---

# 3 — SELECȚIA

```
SEED = SHA256("RANGE_V3_BLIND_LABEL_BATCH_02|10c2d46|f9af357|N48")
     = 82cffac4f7a18eb91fc33c7a29b7481ef6e2b105411d1be38f10d4d54bca6e8a
extrageri 96 (52 selecție + 44 amestecare) · acceptate 48 · refuzuri consemnate 4, toate R5
```

```
distribuție   96 bare: 16   ·   288 bare: 16   ·   480 bare: 16
blocuri       B1: 12  ·  B2: 12  ·  B3: 12  ·  B4: 12
batch-uri     1: BLIND-001..012 · 2: 013..024 · 3: 025..036 · 4: 037..048
              FIECARE batch: 4 ferestre pe lungime, 3 pe bloc — echilibrat DE UNUL SINGUR
```

## 3.1 Defect de script, prins înainte de orice citire OHLC

> **Prima versiune a scriptului amesteca ID-urile GLOBAL. Asta ar fi rupt proprietatea din protocolul §2.4 — fiecare batch conține exact o fereastră pe celulă — fiindcă `BLIND-001…012` ar fi devenit o submulțime aleatoare, nu un batch echilibrat. Am corectat scriptul ca să amestece ÎN INTERIORUL fiecărui batch, așa cum cere protocolul deja comis. Nu e o schimbare de protocol: e aducerea scriptului în conformitate cu el, făcută înainte de a citi vreun preț. Consemnez și hash-ul listei produse de versiunea greșită, `f63dce843f3f457de4ffacb5708ddf730ec46d05567892a75e2a538314fd28ed`, ca să fie auditabil că nu am ales între două rezultate — ferestrele sunt IDENTICE în ambele, doar etichetele diferă.**

## 3.2 Poarta de fezabilitate, sub excluderile de independență

```
        L=96                L=288               L=480
B1   43.331 elig / max 186   41.795 / 102       40.259 /  69
B2   39.899 elig / max 172   37.795 /  93       36.034 /  63
B3   15.961 elig / max  70   14.341 /  37       12.964 /  25
B4   55.661 elig / max 239   53.357 / 129       51.295 /  88
                                            necesar: 4 pe celulă  →  trecut cu marjă largă
```

## 3.3 Refuzurile, consemnate

```
extragerea 29 · batch 3 · B2 · L=288 · start 103167 · R5
extragerea 32 · batch 3 · B3 · L=96  · start 110996 · R5
extragerea 34 · batch 3 · B3 · L=288 · start 129560 · R5
extragerea 47 · batch 4 · B3 · L=288 · start 129079 · R5
```

**Toate procedurale. Nicio fereastră nu a fost respinsă pentru aspect — criteriul de respingere e exclusiv R1-R5.**

---

# 4 — DOVADA DE INDEPENDENȚĂ

```
exclus   întinderile randate ale tuturor celor 24 de ferestre HBL-01…HBL-24
         RC-01 … RC-08 (cele cu bare canonice) · RC-CONSTRUCTION-CHANNEL-NEW-01 [192,288)
         fiecare cu MARJĂ DE 480 DE BARE de ambele părți — o fereastră întreagă de lungime maximă
total    36.039 din 197.094 bare excluse (18,3%)

VERIFICAT   ferestre noi care ating material exclus:      0
            perechi care încalcă separarea R5:            0
```

> **Marja e 480, nu 96 ca la Batch 01. Ce se cere aici e independență, nu doar non-suprapunere: o fereastră nouă nu doar că nu împarte nicio bară cu materialul de construcție — e separată de el prin cel puțin o fereastră completă.**

---

# 5 — DOVADA CĂ SELECȚIA N-A VĂZUT PREȚUL

```
lista celor 48 de ferestre, HASH-UITĂ ÎNAINTE de orice citire OHLC:
   d9f77eead2b17283dbdfae750778d2956541fbd00a33053c10249dc1a24442a6

scriptul de selecție citește DOAR d["time"]. `open/high/low/close` apar prima dată în scriptul de
randare, care se rulează DUPĂ ce lista e fixată și hash-uită.
ambele scripturi au raportat la runtime:  ve_n1_replay importat? False
în mediu: find_spec("ve_n1_replay") is None — pachetul nu e instalat, deci nu putea fi rulat
```

---

# 6 — RANDAREA ȘI ANTI-BIAS

```
ID-uri      BLIND-001 … BLIND-048, opace: nu conțin blocul, perioada, lungimea sau ordinea extragerii
ordine      amestecare Fisher-Yates deterministă în interiorul fiecărui batch, din ACELAȘI flux
axa timp    INDEX DE BARĂ RELATIV (0 … N). ZERO date calendaristice.
            E și unitatea în care formularul cere granițele de segment.
grafic      fundal negru · bullish turcoaz · bearish alb · același raport de aspect și aceeași marjă
            fereastra centrală delimitată cu linii verticale groase
            context 24+24 estompat, marcat CONTEXT · numărul de bare centrale afișat
absent      output de detector · etichete RANGE/TREND/CHANNEL · reason codes · PnL · swings ·
            ATR · limite automate · evenimente · orice sugestie
```

> **Scurgere reziduală, declarată acum, nu descoperită ulterior: axa PREȚULUI rămâne reală, fiindcă formularul cere limitele aproximative ale range-ului. Nivelul absolut al aurului trădează aproximativ epoca. Nu îl ascund — un preț normalizat ar face răspunsurile greu de dat și greu de recuperat. Epoca nu spune nimic despre etichetă, iar blindul care contează aici e față de DETECTOR.**

---

# 7 — LIVRABILE ȘI HASH-URI

```
RANGE_V3_BLIND_BATCH_02_ALL.pdf       48 pagini
   e78eba2873779db4f897bdf7f926f062fedee78d90d68f7966a8b6e4a58eb62c
PART1  3df299472b6c749e…    PART2  d0c7561732623645…
PART3  4983256ce26477b4…    PART4  e56be4401720545e…

CEO_INSTRUCTIONS.md                    5c130ca55c8bf93bfb4eb8ebe2ac505e7efe5639383e967239e4fa1b206c5b67
RANGE_V3_BLIND_LABEL_RESPONSE_02.md    9d4b6906d92e277e5b3762e60ce3a15728a2da028a24b357877850c71ad4f14a
lista ferestrelor                      d9f77eead2b17283dbdfae750778d2956541fbd00a33053c10249dc1a24442a6
BLIND-001.png … BLIND-048.png          hash-uri individuale în HASHES.md
```

**Escrow — maparea `ID → (bloc, lungime, index, timestamp)`, sigilată înainte de etichetare:**

```
escrow_id            RT-BLIND-ESCROW-RANGE-V3-002
payload SHA-256      b7e103a3d9b86f7257debd0bc1d32da2d76f4031545ecd54e5487daf7ee3f1cb
plaintext SHA-256    5d986818ca867270d2bda5566f1bfdc2ac0cd3dd9654b1af6f15bbbc7c679f11
locație              ÎN AFARA oricărui checkout Git; `git rev-parse` eșuează în director
verificat            Red Team deschide (48 mapări) · un bit modificat → fail-closed
```

> **PDF-urile, PNG-urile și maparea NU intră în Git. În Git se publică doar documentația, protocolul și hash-urile — verificat că formularul, instrucțiunile și lista de hash-uri nu conțin nicio dată calendaristică.**

---

# 8 — CE NU S-A FĂCUT

```
NU s-a instalat și NU s-a rulat 0.4.1 sau orice altă versiune pe aceste ferestre
NU s-au comparat etichete cu detectorul · NU s-a calculat accuracy/recall · NU s-au ales parametri
NU s-a modificat SPEC V3 · NU Strategy Catalog · NU Alpha · NU AI Trader · NU LIVE_SHADOW · NU broker
```

**Mandatul se încheie aici.** Comparația cu detectorul e un mandat Red Team separat, **după** blocarea etichetelor.

---

# 9 — ELEMENTE DESCHISE

```
MATERIAL     Priorul de segmente/fereastră vine din Batch 01, care e CEO_ASSISTED. Dacă etichetarea
             independentă produce sistematic mai puține segmente, precizia finală va fi puțin sub
             țintă. Declarat înainte, nu compensat ulterior cu ferestre suplimentare.
MATERIAL     Segmentele din aceeași fereastră nu sunt strict independente; intervalul rezultat va fi
             puțin prea îngust. O corecție pe clustere se poate aplica la analiză, dacă CEO o cere.
LIMITARE     Axa prețului rămâne reală și trădează aproximativ epoca (§6). Blindul e față de detector.
LIMITARE     B3 e blocul cel mai sărac după excluderi (max 25 de ferestre disjuncte la L=480 față de
             69-88 în celelalte). Cerința de 4 e satisfăcută cu marjă, dar B3 va fi primul care
             blochează un eventual lot 3.
NON_MATERIAL Amestecarea consumă 44 de extrageri din același flux, după cele 52 de selecție.
```

---

**Invariante verificate neatinse:** `n_generated_total = 363` · `m_inference = 26` · tombstones · registrul Alpha · verdictele existente · F1-F6 `BLOCKED_PENDING_RANGE_SEMANTIC_FIX` · F7 `SAFETY_GUARD`. Zero PnL, zero strategie, zero broker, zero LIVE_SHADOW, zero rulare Alpha.

**Manifest:** v2.7.85.
