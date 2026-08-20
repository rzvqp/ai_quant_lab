# PROTOCOL DE VALIDARE BLIND — `V4_4_FRESH_BLIND14`

**Divizia Statistician · mandat STAT-RANGE-V4_4-FRESH-BLIND14-PREP-001 · 2026-08-20**

```
V4_4_BLIND14_PROTOCOL_PRECOMMITTED
```

**Acest document e comis ÎNAINTE de orice selecție, de orice randare și de orice etichetă.**
Nu conține niciun rezultat semantic, fiindcă la momentul scrierii lui niciunul nu există.

---

## 1 — AUTORITATE, VERIFICATĂ DIN GIT

| element | verificat |
|---|---|
| audit RT V4.4 | `845a03c` — `V4_4_IMPLEMENTATION_AUDIT_PASS_WITH_NONBLOCKING_NOTES` |
| autorizare | `V4_4_FRESH_BLIND_VALIDATION_AUTHORIZED_FOR_CEO_DECISION` (liniile 13–14) |
| implementare V4.4 | `3bb61cf`, `config_id` începe cu `23d98c07…` |
| oglinzi | `local = remote` pe toate patru |

---

## 2 — UNIVERSUL SURSĂ

Identic cu cel ratificat: **OANDA:XAUUSD M15**, corpusul canonic pre-holdout de **197.094 bare**,
reconstruit determinist prin loaderul din `alpha-automation-v1`
(`edge_research/_common.py`, cheia `M15_v2`, split `pre_holdout_2025-10-23T09-15-00Z_v1`),
fișier sursă SHA-256 `57f4ed95…`, amprentă corpus `af3bf2f6…`.

Fără alt broker, fără date sintetice, fără resamplare, fără OHLC modificat.

---

## 3 — EXCLUDERI (dovada de prospețime)

Fiecare intrare e material **deja consumat**, exclus cu marjă de independență **480 de bare** de
fiecare parte:

| # | excludere | bare |
|---|---|---|
| E1 | cele 24 de ferestre ale lotului 01 | 29.481 |
| E2/E3 | episoadele RC-01…RC-08 + controlul de construcție | 6.558 |
| E6 | cele 48 de ferestre ale lotului 02 | 51.365 |
| **E7 (NOU)** | **toate cele 48 de ferestre MB3** — 001…024 etichetate *și* 025…048 sigilate | **43.337** |
| | **TOTAL** | **130.741 / 197.094 = 66,3%** |

**Rămân libere 66.353 de bare.**

> **De ce E7 acoperă și `MB3-025…048`:** deși nu au fost etichetate niciodată, ferestrele au fost
> **selectate și randate**, deci barele lor sunt material consumat. Le exclud pentru a garanta
> prospețimea, folosind **exclusiv coordonatele non-semantice** din propriul meu artefact de selecție.
> **Nu am deschis niciun payload de etichete, nu am privit niciun grafic MB3 și nu există etichete
> pentru 025…048.** `MB3-025…048` rămân `SEALED_FUTURE_EVIDENCE`.

Materialul sintetic de construcție/adversarial al V4.4 nu conține bare reale, deci nu intră în masca
de excludere.

---

## 4 — ★ ABATERE MATERIALĂ DE LA §7, DECLARATĂ ÎNAINTE DE SELECȚIE

Mandatul cere stratificare **4 / 4 / 3 / 3** pe patru blocuri, *„dacă există patru blocuri
eligibile"*, și cere explicit ca, dacă universul diferă, să documentez și să pre-înregistrez cea mai
apropiată stratificare echilibrată.

**Măsurat: blocul B3 este EPUIZAT — zero poziții eligibile la toate cele trei lungimi.**

```
pozitii eligibile        L=96      L=288     L=480
  B1                   17.036    14.102    11.675
  B2                   11.135     7.620     4.779
  B3                        0         0         0     ← EPUIZAT
  B4                   29.716    26.582    23.778
```

B3 e cel mai scurt bloc canonic (~25.245 bare) și a fost deja folosit de loturile 01, 02 și MB3.
Nu e o alegere; e o constatare.

**Stratificarea pre-înregistrată devine, pe trei blocuri eligibile: 5 / 4 / 5.**

Repartiția cotelor e determinată de **capacitate**, nu de conținut: blocul cu cele mai puține poziții
eligibile primește cota mai mică.

```
B2 (cel mai strâmt, 11.135)  ->  4 ferestre
B1 (17.036)                  ->  5 ferestre
B4 (29.716)                  ->  5 ferestre
```

Regula e calculată **exclusiv din axa timpului și din masca de excluderi** — niciun OHLC, nicio
etichetă, niciun output de detector nu intră în ea.

---

## 5 — ALOCAREA LUNGIMILOR (nemodificabilă)

```
96 bare  = 5 ferestre
288 bare = 5 ferestre
480 bare = 4 ferestre
TOTAL    = 14
```

### ★ AMENDAMENT 1 la §5 — corectat ÎNAINTE de orice selecție

Regula scrisă inițial („fiecare celulă primește maximul compatibil cu cotele rămase") s-a dovedit
**degenerată** când am verificat ce produce, înainte de a trage vreo fereastră:

```
B2 {480: 4, 288: 0, 96: 0}      fiecare lungime ar cădea INTEGRAL
B1 {480: 0, 288: 5, 96: 0}      într-un singur bloc, deci efectul de
B4 {480: 0, 288: 0, 96: 5}      lungime ar fi perfect CONFUNDAT cu blocul
```

Un astfel de plan face imposibilă separarea unui efect de lungime de un efect de perioadă — exact
comparația per-lungime 96/288/480 pe care §17 o cere. **Regula se înlocuiește**, tot determinist:

```
round-robin pe blocuri în ordinea CAPACITĂȚII DESCRESCĂTOARE (B4, B1, B2),
lungimi în ordine descrescătoare (480, 288, 96), pointer continuu între lungimi,
sărind blocurile a căror cotă s-a epuizat
```

Rezultat unic, recalculabil de oricine:

```
B4 {480: 2, 288: 1, 96: 2} = 5
B1 {480: 1, 288: 2, 96: 2} = 5
B2 {480: 1, 288: 2, 96: 1} = 4
sume pe lungime: 480 = 4 · 288 = 5 · 96 = 5
```

Fiecare lungime apare în **toate cele trei blocuri**. Amendamentul e făcut **înainte de orice
selecție, randare sau etichetă**, e calculat exclusiv din cote și capacități, și nu poate favoriza
niciun rezultat — la acest moment nu există niciun rezultat de consultat.

---

## 6 — SELECȚIE DETERMINISTĂ

```
seed_string = "RANGE_V4_4_FRESH_BLIND14|3bb61cf|845a03c|N14"
```

Flux SHA-256 identic cu cel ratificat. Reguli de eligibilitate moștenite neschimbate: context
`C = 24`, margine de bloc `EDGE = 96`, separare între ferestre `SEP = 96`, pauză internă maximă
60 h, întinderea randată integral într-un singur bloc canonic.

Plasare: **blocuri în ordinea strâmtorii, lungimi descrescătoare, tragere uniformă din mulțimea încă
fezabilă** — corecția de eșantionare deja pre-înregistrată și folosită la MB3.

**Regula de înlocuire tehnică:** dacă o fereastră selectată e invalidă tehnic (date corupte/lipsă),
se trage următoarea poziție din același flux, în aceeași celulă. Fereastra respinsă **și motivul**
rămân în jurnalul de audit. Înlocuirea e permisă **numai** pentru invaliditate tehnică, niciodată
pentru conținut.

Fără oprire timpurie. Fără extindere. Fără înlocuirea ferestrelor dificile. Fără eliminarea celor
ambigue.

---

## 7 — ÎNGHEȚAREA SELECȚIEI

ID-uri neutre `FB14-001` … `FB14-014`. Pentru fiecare fereastră se înregistrează: ID, sursă,
interval exact de bare, lungime, bloc, hash de date (rețeta ratificată `bars_sha256_v1`) și hashul
graficului randat.

Manifest **execution-safe** (comis): doar `id`, `L`, `n_rendered_bars`, `bars_sha256`.
Coordonatele stau **în afara Git**, sigilate. Se înregistrează `FRESH_BLIND14_SELECTION_FROZEN`.

---

## 8 — RANDARE

Identică cu procedura ratificată: axa orizontală = **index de bară**, fără date calendaristice;
context 24 + 24 estompat și marcat; fereastra centrală delimitată vizual.

**Zero** output V4.3, **zero** output V4.4, zero stări de detector, zero markeri de confirmare, zero
evenimente de model, zero metadate de predicție.

---

## 9 — SCHEMA SEMANTICĂ (neschimbată)

Se reutilizează **exact** schema deja ratificată: segmente ordonate cu
`RANGE · CHANNEL_UP · CHANNEL_DOWN · TREND_UP · TREND_DOWN · TRANSITION · AMBIGUOUS · UNAVAILABLE`,
`confidence HIGH/MEDIUM/LOW`, evenimente
`SWEEP_* · BREAKOUT_* · FAILED_BREAKOUT_* · NONE · AMBIGUOUS`, iar pentru RANGE limitele
`lower/upper/mid` plus caracterul și starea episodului.

**Nicio definiție nu se modifică pentru că există V4.4.** Ținta primară e **MACRO**.

## 10 — FLUX DE ETICHETARE ȘI AMENDAMENTE

`FB14-001` → `FB14-014`, una câte una, CEO vorbește primul, eu doar transcriu. Jurnal **append-only**;
o corecție înainte de freeze se adaugă ca **rând nou**, cu originalul păstrat intact. Toate cele 14
se completează; fără oprire pentru că lotul pare ușor sau greu.

## 11 — ÎNGHEȚAREA ETICHETELOR

Validare de schemă și de acoperire, serializare canonică, `labels_sha256`, sigilare, dovadă de
roundtrip și de respingere la alterare/cheie greșită. Se înregistrează
`FRESH_BLIND14_LABELS_FROZEN`. După freeze, etichetele sunt **imutabile** pentru această rulare.

---

## 12 — COMPARAȚIA, BLOCATĂ ACUM (înainte să existe vreo predicție)

**V4.3 înghețat vs V4.4 înghețat (`3bb61cf`, `config_id 23d98c07…`), pe EXACT aceleași 14 ferestre.**
Niciun cod nu se schimbă după ce încep predicțiile.

**Ipoteze primare:**

| | ipoteză | criteriu |
|---|---|---|
| H1 | reducerea FP direcționale | FP direcționale V4.4 **<** V4.3 |
| H2 | păstrarea TP | TP RANGE V4.4 **≥** V4.3 |
| H3 | recall nedegradat | recall MACRO V4.4 **≥** V4.3 |
| H4 | FP total nedegradat | FP MACRO total V4.4 **≤** V4.3 |
| H5 | calitate | nici precizia, nici F1 mai mici; **cel puțin una** în creștere, dacă e evaluabilă |

**Diagnostice secundare, non-adaptive:** precizie, recall, F1, IoU median, TP/FP/FN totale,
descompunerea FP direcționale pe clasă semantică, rezultate per lungime 96/288/480, timpul de
confirmare, numărul de episoade, cazurile de supra-segmentare, comportamentul pe GT `AMBIGUOUS`
conform politicii scorerului. **Nicio metrică nu se adaugă după rezultate.**

**Regula de neevaluabilitate:** dacă V4.3 produce zero FP direcționale pe tot lotul, `H1 = NOT_TESTABLE`;
dacă lotul nu conține structuri RANGE scorabile, afirmațiile de TP/recall = `NOT_TESTABLE`.
În acest caz verdictul poate fi `V4_4_FRESH_BLIND14_INCONCLUSIVE`. **Nu se adaugă ferestre după ce se
vede asta.**

**Dispoziții finale posibile:** `GENERALIZATION_SUPPORTED` · `GENERALIZATION_NOT_SUPPORTED` ·
`INCONCLUSIVE`; separat, `INTEGRITY_FAIL`. Un rezultat „susținut" cere trecerea porților primare
**exact așa cum sunt scrise aici**.

## 13 — EXECUȚIA ULTERIOARĂ, ÎN DOUĂ MEDII

**ENV A — doar inferență:** are acces la payload-ul ferestrelor, V4.3, V4.4 și configurații;
**nu** are acces la etichete. Produce și îngheață predicțiile ambelor detectoare, cu hashuri,
**înainte** de orice acces la etichete.
**ENV B — doar scorare:** are acces la etichetele înghețate, la predicțiile înghețate și la scorer;
**nu** execută și **nu** modifică detectoare. Fără scorare adaptivă în același proces.

## 14 — LIMITAREA CUNOSCUTĂ

Nu se selectează și nu se etichetează ferestre după prezența cazului
*canal blând / zigzag violent*. Dacă apare natural, e dovadă validă; dacă nu apare, **nu se
introduce artificial**. Acesta e un lot aleator de confirmare, nu o suită adversarială.

## 15 — DOMENIU

Statisticianul **nu** importă și **nu** rulează niciun detector în acest mandat. După înghețarea
etichetelor, **STOP**; proprietar următor: Red Team. Nici un eventual PASS pe 14 ferestre nu
autorizează Strategy Catalog, Alpha, AI Trader, LIVE_SHADOW, broker sau ordine.

*Statut epistemic: `FRESH_BLIND14_CONFIRMATION` · `VALIDATION_WEIGHT = ZERO` până la verdictul blind.*
