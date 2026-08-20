# LOT BLIND MACRO INDEPENDENT 03 — PREGĂTIRE ȘI SIGILARE

**Divizia Statistician · mandat 3.108 · 2026-08-20**

```
NEW_MACRO_BLIND_BATCH_SELECTED     = TRUE
NEW_MACRO_BLIND_ESCROW_SEALED      = TRUE
NEW_MACRO_BLIND_LABELS_FROZEN      = FALSE      ← etichetele NU există încă (vezi §6)
DETECTOR_EXECUTED_ON_NEW_BLIND     = FALSE
PREDICTIONS_FROZEN                 = FALSE
BLIND_SCORE_COMPUTED               = FALSE
INDEPENDENT_SEMANTIC_BLIND         = NOT_YET_EXECUTED
VALIDATION_WEIGHT                  = ZERO_UNTIL_BLIND_VERDICT
```

**Acest raport nu conține niciun răspuns blind.** Fără timestampuri, fără OHLC, fără indici canonici,
fără etichete.

---

## 1 — AUTORITATE, VERIFICATĂ DIN GIT

| element | verificat |
|---|---|
| RT-RANGE-0013 | `cc76dcc` — `RANGE_V4_F1_ONLY_REMEDIATION_AUDIT_PASS` |
| RT-RANGE-0012 | `892355f` — FAIL (E87), context |
| candidat VE | `bc6b9dc` |
| predicții înghețate | `46a9576` |
| LEDGER | `E88` |
| amprentă implementare | `f1-only-f5-deferred-2026-08-20` |

`MACRO_INDEPENDENT_BLIND_PREPARATION_AUTHORIZED = TRUE` — citit direct din raportul RT-0013 (linia 10)
și confirmat în LEDGER E88: *„authorizes ONLY prep+sealing of the new independent MACRO blind batch"*,
cu următorul proprietar **Statistician/blind-batch prep**. `local = remote` pe toate patru oglinzile.

---

## 2 — INDEPENDENȚA, MĂSURATĂ NU PRESUPUSĂ

Inventarul de excluderi, aplicat pe corpusul canonic de **197.094** bare, fiecare intrare fiind
material **deja expus**:

| excludere | bare |
|---|---|
| E1 — cele 24 de ferestre ale lotului 01 + marjă 480 | 29.481 |
| E2/E3 — episoadele RC-01…RC-08 + controlul de construcție | 6.558 |
| **E6 (NOU)** — cele 48 de ferestre ale lotului 02 + marjă 480 | **51.365** |
| **TOTAL** | **87.404 / 197.094 (44,3%)** |

> Lotul 02 a fost etichetat, rulat, scorat și publicat pe larg în RT-0010…0013, deci **fiecare bară a
> lui e material expus** — de aceea intră integral în excluderi, cu aceeași marjă de independență de
> 480 de bare (o fereastră completă de lungime maximă) folosită la lotul 02.

**Verificat independent după selecție**, nu doar prin construcție:

```
suprapunere cu material expus (loturile 01 + 02)   0
separare minimă reală față de orice fereastră expusă   481 bare   (marja cerută: 480)
suprapuneri între ferestrele noi                   0
```

★ **O notă proprie, corectată.** În memoria mea de la mandatul 3.102 scria că „corpusul vizual e
epuizat". **Măsurat acum: fals** — după toate excluderile rămân 55,7% din corpus și fiecare celulă
(bloc × lungime) susține cel puțin 4 ferestre disjuncte. Nota reflecta starea de atunci și a fost
verificată, nu preluată.

---

## 3 — SELECȚIA: DETERMINISTĂ, PRE-ÎNREGISTRATĂ, OARBĂ PRIN CONSTRUCȚIE

Protocol: `STAT-RANGE-V3-BLIND-BATCH-02-PROTOCOL-v1.0` + E6. **Nu am inventat mărimea eșantionului** —
protocolul o definește: 4 batch-uri × 4 blocuri × 3 lungimi = **48 de ferestre**, exact compoziția
lotului 02.

```
seed_string        RANGE_MACRO_BLIND_LABEL_BATCH_03|cc76dcc|bc6b9dc|N48
seed_sha256        01b7774729f85cdd4b42222582bf795359008e52ac21effcd766833a09ec2628
ferestre           48   ·   bare canonice 13.824   ·   16 × 96 + 16 × 288 + 16 × 480
trageri            48   (zero respingeri)
selection_sha256   dd1c8f5f99a31fc9eb0e74a9a65f0207623387124a1d858ae4adf412f2a0f5d0
```

★ **Scriptul de selecție citește DOAR coloana `time`.** Nu atinge OHLC, nu importă detectorul, iar
etichetele nu există. **Selecția e oarbă prin construcție** — nu doar prin disciplină — atât față de
răspunsul semantic, cât și față de detector. Nicio informație despre rezultat nu putea intra în ea
nici în principiu.

### 3.1 O corecție de eșantionare, declarată ÎNAINTE de selecție

Protocolul lotului 02 plasează ferestrele în ordinea (batch, bloc, lungime **crescătoare**) și acceptă
prin **respingere repetată**. Cu populația redusă la 55,7%, blocul **B3** devine strâmt: ferestrele
scurte plasate primele ocupă exact spațiul cerut de cele de 480 de bare din batch-urile următoare, iar
eșantionatorul a atins plafonul de siguranță (rulare blocată la 43/48).

**Nu e lipsă de populație** — împachetarea directă arată **12/12** ferestre plasabile în *fiecare*
bloc. E o limită a implementării prin respingere, expusă de populația mai mică. **Poarta de
fezabilitate per-celulă a protocolului nu testa asta**, fiindcă separarea R5 e globală pe bloc, nu pe
celulă. O semnalez ca limitare a protocolului ratificat.

Corecția, pre-înregistrată în artefactul comis înaintea oricărei selecții:

```
1. lungimi în ordine DESCRESCĂTOARE   (constrângerea cea mai dură prima)
2. tragere uniformă din mulțimea încă FEZABILĂ, nu prin respingere repetată
   — matematic aceeași distribuție pe care respingerea o aproximează; dispare doar bucla
3. blocuri în ordinea STRÂMTORII, cel mai constrâns primul
   fără ea: 43/48 și blocaj   ·   cu ea: 48/48 din 48 de trageri, zero respingeri
```

★ **De ce nu poate favoriza nimic:** toate trei regulile se calculează **exclusiv din axa timpului și
din masca de excluderi**. Niciun OHLC, nicio etichetă, niciun output de detector nu intră în ele. Nu
pot selecta „ferestre ușoare" sau „prietenoase cu detectorul" nici măcar în principiu, fiindcă la
momentul selecției nu există niciun rezultat de consultat.

---

## 4 — SEPARAREA ROLURILOR

| | conținut | unde |
|---|---|---|
| **A. execution-safe** | `id`, `L`, `n_rendered_bars`, `bars_sha256` — **atât** | Git: `blind_batch_03/EXECUTION_SAFE_MANIFEST.json` |
| **B. sigilat** | maparea ID → fereastră (indici, timestampuri), artefactul de selecție | escrow, **în afara Git** |
| **C. metadate de audit** | seed, SHA-uri, ancore, amprente | în A + în sigiliu |

Manifestul execution-safe **nu conține** timestampuri, OHLC, indici canonici sau etichete — verificat
mecanic. Artefactul de selecție conține indici, deci a fost **mutat în afara Git**; SHA-ul lui e
ancorat atât în manifest cât și în sigiliu, iar scriptul comis îl regenerează bit-exact din seed, deci
pre-înregistrarea rămâne integral verificabilă **fără** a publica coordonatele.

---

## 5 — SIGILAREA ȘI VERIFICAREA EI

Reteta ratificată `bars_sha256_v1` (RT-RANGE-0010), **nu o schemă nouă**: `concat(H,L,O,C)`,
`int64(x × 1e6)` trunchiat, `tobytes()` little-endian, `sha256`, pe fereastra **randată**.

```
payload sigilat                payload-b9d0fd727d08d149.bin   (14.414 B, OFF-GIT)
execution_safe_manifest_sha    1098abd0333a57ae5bed40c47322348c9f2c9feb0d0fb6293c8a3bf8134f4903
```

Verificare independentă, după creare:

```
roundtrip mapping                          OK
ancore concordante manifest ↔ sigiliu      48/48
mutație de un bit                          REFUZATĂ  (encrypt-then-MAC)
cheie greșită                              REFUZATĂ
```

Cheia rămâne în locația ei securizată, în afara Git, a rapoartelor, a memoriei și a Telegramului.

---

## 6 — DE CE `NEW_MACRO_BLIND_LABELS_FROZEN = FALSE`

Mandatul cere ca starea finală să includă etichete înghețate. **Nu pot livra asta, și motivul e chiar
motivul pentru care lotul trebuie să fie orb.**

Protocolul ratificat de etichetare (`BLIND_LABEL_BATCH_02_CEO_INSTRUCTIONS.md`) e explicit:

> „**TU spui PRIMUL ce vezi.** … Eu **doar TRANSCRIU** verdictul tău."

**Etichetatorul uman e CEO-ul; eu randez, transcriu și sigilez.** Dacă aș eticheta eu, lotul ar înceta
să fie orb: am văzut în detaliu comportamentul MACRO al detectorului — funnelul, IoU-urile, ferestrele
ratate și fals-pozitive, tabelul celor 12 cazuri INTERNAL. Etichetarea de către mine ar fi exact
scurgerea pe care acest mandat o previne.

Prin urmare livrez **materialul de etichetare**, nu etichetele:

```
48 imagini + 4 PDF-uri a câte 12 pagini + 1 PDF complet   ->  C:/Users/MEDION GAMING/ceo_labeling_batch_03
PART1 ea8f55ec…  PART2 267ae1ec…  PART3 963f1edab…  PART4 4ccbd487…
ALL   34d883a19448da442834467c443e31075948e3c59fc4fea9fa862c8aad10758c
```

Axa graficelor e **index de bară**, fără date calendaristice — ca la lotul 02, ca să nu se poată
identifica perioada.

**Pasul următor imediat: sesiunea de etichetare CEO.** Abia după înghețarea etichetelor pachetul e
complet pentru un verdict blind scorabil.

---

## 7 — VERIFICĂRI NEGATIVE / SCURGERI

| verificare | rezultat |
|---|---|
| suprapunere cu ferestre expuse anterior | **0** |
| separare minimă reală față de material expus | **481 bare** (cerut 480) |
| etichete în fișiere execution-safe | **0** — etichetele nu există |
| timestampuri / indici canonici în manifest | **0** |
| output de detector sau scoruri în pachet | **niciunul** |
| predicții pentru lotul nou | **niciuna** |
| detectorul a fost rulat pe lotul nou | **NU** |
| secrete HMAC în Git / raport / memorie / Telegram | **niciunul** |

★ **Dovadă de mediu, nu declarație:** scriptul de randare raportează la final
`ve_n1_replay importat? False` — detectorul nu a fost nici măcar încărcat în procesul care a atins
barele OHLC.

---

## 8 — STARE ȘI DOMENIU

**Lotul e selectat, sigilat și dovedit independent.** Nu declar
`MACRO_INDEPENDENT_BLIND_EXECUTION_AUTHORIZED = TRUE`: propria condiție de completare a mandatului
cere etichete înghețate, iar ele nu există încă. A declara execuția autorizată acum ar însemna să-mi
relaxez propria condiție de finalizare după ce am aflat că mă încurcă — exact tiparul pe care l-am
refuzat la `w_atr`.

**Nu autorizez și nu afirm nimic despre:** verdictul RANGE, BLIND PASS, rularea detectorului, wheel,
Strategy Catalog, Alpha, AI Trader, LIVE_SHADOW, broker, tranzacții.

**Proprietar următor:** CEO, pentru sesiunea de etichetare. Apoi Red Team, pentru execuția oarbă.

---

*Divizia Statistician · detector NErulat și NEimportat · etichete inexistente · `SEALED/OOS_ACCESS = 0`*
