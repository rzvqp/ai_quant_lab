# F5 — RAPORT DE ÎNCHIDERE
### `matched_null@v1`: reproducerea exactă a obs0012 (calibrare) + execuția oficială DC-0004

**Document ID:** VE-F5-REPORT-v1.0
**Data:** 2026-07-25 · **Autor:** Validation Engine
**Autoritate:** CEO 2026-07-25 — opțiunea A (separare strictă calibrare / execuție oficială).
**Statut:** livrat, în așteptarea aprobării. **DC-0004/registrul/vocabularul/motorul F4 neatinse. Holdout NEATINS. Toate rulările pe fereastra deschisă. Metoda rămâne `UNVALIDATED` (validarea = F6). F6 neînceput.**

---

## 1. Separarea strictă cerută

| | CALIBRARE (NON-OFFICIAL) | OFICIAL |
|---|---|---|
| Scop | reproduce fidel obs0012 (verifică implementarea) | rezultat in-sample cu parametrii DC-0004 |
| Modul | `ve/calibration/reproduce_obs0012.py` | `ve/run/matched_null_official.py` |
| B | 3000 | 200000 |
| seed | 7 literal, generator PARTAJAT | `derived_from_spec_hash`, per celulă (INDEPENDENT de ordine) |
| ordinea celulelor | ordinea obs0012 (artefact istoric) | irelevantă (independent de ordine) |
| marcaj bundle | `mode: CALIBRATION`, `official: false`, avertisment „NON-OFFICIAL" | `mode: OFFICIAL`, `official: true` |

Ambele folosesc **exclusiv intrările validate în F4** (evenimente, excess, pool) și metoda `matched_null@v1` (`ve/methods/matched_null.py`).

---

## 2. Reproducerea obs0012 — EXACTĂ

Harness-ul de calibrare replică algoritmul obs0012: un singur `default_rng(7)`, B=3000, tail=left, pool per sesiune, **consumat în ordinea de inserție a celulelor din obs0012**.

Ordinea reconstruită: `up/asia → down/ny → down/asia → up/london → up/ny → down/london`.

| Celulă | n | VE p | obs0012 p | Potrivire |
|---|---|---|---|---|
| up/asia | 135 | 0.9593 | 0.9593 | ✅ |
| down/ny | 47 | 0.4123 | 0.4123 | ✅ |
| down/asia | 114 | 0.3640 | 0.3640 | ✅ |
| up/london | 34 | 0.6570 | 0.6570 | ✅ |
| up/ny | 42 | 0.0253 | 0.0253 | ✅ |
| down/london | 40 | 0.3620 | 0.3620 | ✅ |

**Reproducere bit-exactă a tuturor celor 6 valori p raportate de obs0012**, la precizia scriptului (4 zecimale). Fără nicio ajustare prin încercări.

---

## 3. Execuția oficială DC-0004

Parametrii oficiali (B=200000, `seed_policy=derived_from_spec_hash` per celulă), pe intrările F4, ordinea declarată a specificației. Rezultat **provizoriu** (metoda e `UNVALIDATED` până la F6).

| Celulă | n | OFICIAL p | CI95 Monte-Carlo | obs0012 p |
|---|---|---|---|---|
| up/asia | 135 | 0.9538 | [0.9529, 0.9547] | 0.9593 |
| down/asia | 114 | 0.3497 | [0.3476, 0.3518] | 0.3640 |
| up/london | 34 | 0.6638 | [0.6618, 0.6659] | 0.6570 |
| down/london | 40 | 0.3561 | [0.3540, 0.3582] | 0.3620 |
| up/ny | 42 | 0.0214 | [0.0208, 0.0221] | 0.0253 |
| down/ny | 47 | 0.4108 | [0.4087, 0.4130] | 0.4123 |

Rezultatul oficial este mai precis (B=200000, CI95 strâns). **Nu se compară bit-exact cu obs0012** — ambele estimează aceeași p adevărată, obs cu B=3000 (zgomotos), oficialul cu B=200000 (precis).

---

## 4. Diferența calibrare vs. oficial — explicată EXCLUSIV de B și politica de seed

Cerința CEO: „confirmă că diferența este explicată exclusiv de B și politica de seed".

**Dovadă la nivel de cod:** ambele rulări apelează **aceeași funcție** `matched_null.run` cu **aceleași celule** (arrays `ex`/`pool` byte-identice, din aceeași materializare F4), diferind **doar** prin argumentele `B` și `seed`. Nu există altă cale de divergență prin construcție.

**Dovadă empirică (descompunere pe up/ny):**
- obs0012 (B=3000, seed=7): p = 0.0253
- Control (B=200000, seed=7): p = 0.02166 → izolează efectul **B** (mai precis)
- Oficial (B=200000, seed derivat per celulă): p = 0.02143 → efectul **seed** peste control: |diff| = 0.0005 (nivel Monte-Carlo)

**Eliminarea celui de-al treilea factor (ordinea):** inițial, execuția oficială în ordinea spec cu generator partajat introducea un al treilea factor de diferență — ordinea celulelor. Conform deciziei CEO („ordinea celulelor și consumul RNG sunt detalii de implementare istorică, nu proprietăți științifice"), execuția oficială folosește **semințe independente per celulă**, deci este **independentă de ordine** (verificat: ordine directă == ordine inversă → p identice). Astfel diferența oficial vs obs rămâne **strict B + seed**, fără contribuția ordinii.

---

## 5. Rezultatele testelor

```
../venv/Scripts/python.exe -m pytest tests -q
400 passed in 48.75s
```

| Suită | Teste |
|---|---|
| F2/F3/F4 | 389 |
| **F5 (`test_f5_matched_null.py`)** | **11** |

Testele F5 acoperă: cele două moduri de seeding (partajat determinist / per-celulă independent de ordine), sensul cozii, **reproducerea exactă a obs0012** (cele 6 valori + ordinea celulelor), parametrii execuției oficiale + holdout neatins, diferența oficial-obs în limite MC, marcajul clar CALIBRATION/OFFICIAL în manifest, și că metoda rămâne `UNVALIDATED`.

---

## 6. Dovezi de guvernanță

| Cerință | Stare |
|---|---|
| Holdout neatins (toate rulările pe fereastra deschisă) | ✅ `sealed_window_touched=False`; `max_ts_read=2025-10-23T09:00Z < graniță`; hash-urile celor 4 surse identice cu F1 |
| DC-0004 nemodificat | ✅ hash spec neschimbat de F5 |
| Registru/vocabular nemodificate | ✅ `capabilities.json` `fb78b935…` |
| Motor F4 nemodificat | ✅ `materialize.py`/`materializer.py` hash-uri identice |
| Intrări F4 neschimbate | ✅ aceeași materializare |
| Calibrarea NU e folosită ca execuție oficială | ✅ bundle-uri separate, `mode`/`official` în manifest |
| Rezultatul calibrării nu e publicat ca rezultat oficial | ✅ avertisment „NON-OFFICIAL" în manifest |
| Metoda rămâne `UNVALIDATED` | ✅ 0 metode `VALIDATED`; `PUBLISHED_NOT_EXECUTABLE` |
| Ordinea/consumul RNG consemnate ca detalii de implementare | ✅ §4; oficialul e independent de ordine |

---

## 7. Fișiere

**Create:** `ve/methods/{__init__,matched_null}.py`, `ve/calibration/{__init__,reproduce_obs0012}.py`, `ve/run/{matched_null_official,f5_run}.py`, `tests/test_f5_matched_null.py`, `F5_DESIGN.md`, `F5_REPORT.md`.
**Modificate:** `VE_BACKLOG.md` (S1 parțial).
**Neatins (hash verificat):** DC-0004, registrul, schema, vocabularul, motorul de materializare F4, cele 4 surse de date (holdout inclus).

---

## 8. Concluzie

`matched_null@v1` reproduce **bit-exact** experimentul obs0012 (calibrare), demonstrând că implementarea este fidelă protocolului Alpha. Execuția oficială (B=200000, seed derivat per celulă) produce un rezultat in-sample mai precis, independent de ordine, iar diferența față de obs este explicată **exclusiv** de B și de politica de seed — confirmat atât la nivel de cod (aceeași funcție, aceleași intrări), cât și empiric (descompunerea B/seed). Nicio altă diferență nu a apărut.

Metoda rămâne `UNVALIDATED`: promovarea la `VALIDATED` (prin bateria sintetică de calibrare — distribuție uniformă sub null, curbă de putere) este obiectivul **F6**.

**F5 este complet. Holdout neatins. Metoda neexecutabilă oficial (UNVALIDATED). F6 neînceput.**

**Validation Engine se oprește și așteaptă aprobarea CEO înainte de F6.**
