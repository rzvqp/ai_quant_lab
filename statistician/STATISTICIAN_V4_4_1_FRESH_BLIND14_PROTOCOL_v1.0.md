# PROTOCOL DE VALIDARE BLIND — `V4_4_1_FRESH_BLIND14`

**Divizia Statistician · mandat STAT-RANGE-V4_4_1-FRESH-BLIND14-PREP-001 · 2026-08-20**

```
V4_4_1_BLIND14_PROTOCOL_PRECOMMITTED
```

**Comis ÎNAINTE de orice selecție, randare sau etichetă.** Nu conține niciun rezultat semantic —
la momentul scrierii niciunul nu există.

---

## 1 — AUTORITATE, VERIFICATĂ DIN GIT

| element | verificat |
|---|---|
| implementare V4.4.1 | `4ed4eb4` · `config_id` începe cu `d7b6c067…` |
| audit RT | `6adef91` — `V4_4_1_IMPLEMENTATION_AUDIT_PASS_WITH_NONBLOCKING_NOTES` |
| autorizare | `V4_4_1_FRESH_BLIND_VALIDATION_AUTHORIZED_FOR_CEO_DECISION` (liniile 14–15) |
| referință V4.4 | `3bb61cf` |
| oglinzi | `local = remote` pe toate patru |

---

## 2 — PRIORITATEA DE COST A ERORII, DECLARATĂ DE CEO ÎNAINTE DE SELECȚIE

```
FALSE RANGE ESTE MAI PERICULOS DECÂT MISSED RANGE
```

Validarea e deliberat **averse la RANGE fals**, iar porțile primare sunt **asimetrice** din acest
motiv. Verdictul istoric FB14 rămâne neschimbat:
`V4_4_FRESH_BLIND14_GENERALIZATION_NOT_SUPPORTED`, sub regulile lui originale. Acesta e un
**experiment nou**, cu obiectiv declarat prospectiv.

---

## 3 — UNIVERSUL SURSĂ ȘI AUDITUL DE CAPACITATE (§4, executat ÎNAINTE de selecție)

Sursă identică celei ratificate: **OANDA:XAUUSD M15**, corpus canonic pre-holdout **197.094** bare,
loader `alpha-automation-v1` / `edge_research/_common.py`, cheia `M15_v2`, split
`pre_holdout_2025-10-23T09-15-00Z_v1`, fișier `57f4ed95…`, amprentă corpus `af3bf2f6…`.

| # | excludere (material consumat, marjă 480 bare) | bare |
|---|---|---|
| E1 | lotul 01 — 24 ferestre | 29.481 |
| E2/E3 | RC-01…RC-08 + controlul de construcție | 6.558 |
| E6 | lotul 02 — 48 ferestre | 51.365 |
| E7 | **MB3 — toate cele 48** (001…024 etichetate *și* 025…048 sigilate) | 43.337 |
| **E8 (NOU)** | **FB14 — cele 14 ferestre**, dovezi de diagnostic consumate | **13.511** |
| | **TOTAL** | **144.252 / 197.094 = 73,2%** |

**Rămân libere 52.842 de bare (26,8%).**

### Capacitatea proaspătă, măsurată

```
pozitii eligibile        L=96      L=288     L=480
  B1                   12.636     9.889     7.654
  B2                    8.002     5.218     3.145
  B3                        0         0         0     ← EPUIZAT (ca și la FB14)
  B4                   23.762    20.436    17.698

ferestre disjuncte plasabile:  B1 >= 8 · B2 >= 8 · B4 >= 8  ->  cel putin 24, necesar 14
```

★ **Poarta §4 TRECE.** Nu invoc `V4_4_1_FRESH_BLIND_INSUFFICIENT_FRESH_EVIDENCE` și **nu relaxez
nicio excludere**. `MB3-025…048` rămân `SEALED_FUTURE_EVIDENCE` — pentru excludere folosesc
**exclusiv coordonate non-semantice** din artefactele proprii de selecție; niciun payload de etichete
deschis, niciun grafic MB3 sau FB14 reprivit.

---

## 4 — ALOCARE (nemodificabilă după începerea selecției)

```
lungimi:  5 × 96  ·  5 × 288  ·  4 × 480   = 14
blocuri:  pe cele TREI eligibile, dupa CAPACITATE descrescatoare
          B4 (23.762) -> 5 · B1 (12.636) -> 5 · B2 (8.002) -> 4
```

Matricea bloc × lungime folosește **regula round-robin deja ratificată** (amendamentul 1 din
protocolul FB14, `7a2c93d`), tocmai ca lungimea să **nu** devină confundată cu blocul:

```
B4 {480: 2, 288: 1, 96: 2} = 5
B1 {480: 1, 288: 2, 96: 2} = 5
B2 {480: 1, 288: 2, 96: 1} = 4
sume pe lungime: 480 = 4 · 288 = 5 · 96 = 5
```

Fiecare lungime apare în **toate cele trei blocuri**. Regula e calculată exclusiv din cote și
capacități — nicio informație semantică nu intră în ea.

## 5 — SELECȚIE DETERMINISTĂ

```
seed_string = "RANGE_V4_4_1_FRESH_BLIND14|4ed4eb4|6adef91|N14"
```

Eligibilitate moștenită neschimbată: `C = 24`, `EDGE = 96`, `SEP = 96`, pauză internă maximă 60 h,
întinderea randată integral într-un singur bloc. Plasare: blocuri după capacitate, lungimi
descrescătoare, tragere uniformă din mulțimea încă fezabilă.

**Înlocuire tehnică:** doar pentru date corupte/lipsă — se trage următoarea poziție din același flux,
în aceeași celulă; fereastra respinsă și motivul rămân în jurnal. **Niciodată** pentru conținut.
Fără oprire timpurie, fără extindere adaptivă, fără eliminarea ferestrelor ambigue.

## 6 — ÎNGHEȚARE, RANDARE, SCHEMĂ

ID-uri neutre `F441-001` … `F441-014`. Manifest execution-safe (comis): doar `id`, `L`,
`n_rendered_bars`, `bars_sha256`; coordonatele stau **în afara Git**, sigilate.
Randare identică: axă = index de bară, fără date calendaristice, context 24+24 marcat.
**Zero** output V4.4, **zero** output V4.4.1, zero stări, markeri, evenimente sau scoruri.

Ontologie **neschimbată**: `RANGE · CHANNEL_UP · CHANNEL_DOWN · TREND_UP · TREND_DOWN · TRANSITION ·
AMBIGUOUS` (+ `UNAVAILABLE`). **Nicio ontologie nouă pentru V4.4.1.**
Regulă de lot, ca la FB14: `confidence = NOT_SPECIFIED`, `range episode status = NOT_SPECIFIED`;
niciunul nu se deduce. Jurnal append-only; amendamentele se adaugă, nu suprascriu.

---

## 7 — PORȚI PRIMARE, PRE-ÎNREGISTRATE ACUM (asimetrice prin decizie CEO)

| | ipoteză | criteriu | tip |
|---|---|---|---|
| **H1** | protecție FP direcțional | FP direcționale V4.4.1 **≤** V4.4 | **POARTĂ DURĂ** |
| **H2** | protecție FP total | FP MACRO total V4.4.1 **≤** V4.4 | **POARTĂ DURĂ** |
| H3 | nedegradare TP | TP RANGE genuin V4.4.1 **≥** V4.4 | |
| H4 | nedegradare recall | recall MACRO V4.4.1 **≥** V4.4 | |
| H5 | beneficiul T-STALE | unde apare natural cel puțin un eveniment de blocare prin candidat stale din clasa înghețată, V4.4.1 recuperează **cel puțin o** oportunitate RANGE genuină ratată de V4.4, **fără** a crește H1 sau H2 | |

**H1 sau H2 eșuat = respingere dură.** Diagnostice secundare (precizie, F1, IoU median, TP/FP/FN,
descompunerea FP direcționale, numărul de episoade, timpul de confirmare, metrici per lungime) sunt
importante, dar **o îmbunătățire mică de recall sau F1 NU compensează niciodată un eșec H1 sau H2**.
Nicio formulă ponderată nu poate fi inventată după rezultate.

### Regula de decizie, exactă

```
GENERALIZATION_SUPPORTED   <- H1 ∧ H2 ∧ H3 ∧ H4 = PASS, SI H5 = PASS daca e evaluabil
INCONCLUSIVE               <- H5 = NOT_TESTABLE (nu apare natural niciun eveniment stale),
                              CHIAR DACA H1-H4 trec — nu se poate dovedi eficacitatea corectiei
NOT_SUPPORTED              <- orice H1/H2/H3/H4 = FAIL, sau H5 = FAIL cand e evaluabil
```

Dacă H5 nu e testabil, **nu se adaugă ferestre** și **nu se inserează manual** un caz stale.

## 8 — PARAMETRI ÎNGHEȚAȚI (nu se variază în test)

```
STALE_WINDOW = 29 · STALE_MIN_REJECTIONS = 4 · STALE_MIN_ALTERNATION = 3 · STALE_MIN_AGE = 12
```

`STALE_MIN_ALTERNATION = 3` e **FRAGIL** prin calibrare, iar fereastra 29 are discriminare de
sensibilitate limitată. Ambele se evaluează **ca atare**, neatinse.

## 9 — EXECUȚIA ULTERIOARĂ, ÎN DOUĂ MEDII

**ENV A — doar inferență:** ferestrele înghețate, V4.4 (`3bb61cf`), V4.4.1 (`4ed4eb4`); **fără
etichete**. Produce și îngheață criptografic ambele seturi de predicții **înainte** de deschiderea
etichetelor. **ENV B — doar scorare:** etichete înghețate, predicții înghețate, scorer înghețat;
**fără** import sau execuție de detector.

Pentru fiecare declanșare T-STALE, Red Team raportează diagnostic: id candidat, vârstă, număr de
respingeri, alternanță, bara de declanșare, bara de start a înlocuitorului, dacă înlocuitorul se
confirmă ulterior, contextul semantic CEO. **Diagnostic, fără influență asupra predicțiilor sau
etichetelor.**

## 10 — CONTROALE NEGATIVE ȘI DOMENIU

Ferestrele direcționale apărute **natural** sunt deosebit de importante, fiindcă RANGE fals e riscul
principal. **Nu se selectează manual** controale direcționale; numărul lor se raportează **după**
înghețarea etichetelor. Fără reechilibrare semantică după selecție.

Statisticianul **nu** importă și **nu** rulează niciun detector. După înghețarea etichetelor: **STOP**;
proprietar următor Red Team. Niciun PASS nu autorizează Strategy Catalog, Alpha, AI Trader,
LIVE_SHADOW, broker sau ordine.
