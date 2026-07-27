# DATA ACQUISITION — RAPORT FINAL

**Divizie:** Data Acquisition · **Instrument:** OANDA:XAUUSD (sursă unică)
**Status:** faza de achiziție ÎNCHISĂ · M15 + M5 CONECTATE · H1 în carantină · M1 amânat

---

## 1. Cele trei seturi (cu hash-uri)

| Set | Interval | Bare | Ani | sha256 | Verif. 0 | CHECK 1 (OHLC) |
|-----|----------|------|-----|--------|----------|----------------|
| **M15** v2 | 2011-07-26 16:30Z → 2026-07-27 16:15Z | 355.696 | 15,0 | `57f4ed9544993c8fbba28d9c1e3319f2e0665ef5db211fb09d9f4622222ccd37` | PASS (suprapunere) | 0 (excepția numită 2026-07-13) |
| **M5** | 2021-07-27 15:45Z → 2026-07-27 17:55Z | 354.669 | 5,0 | `cbb6eebe1a189ebb20972318a8d98a36bfa461d2cd030bbaa7ba5430cc9f3814` | PASS (dublă tragere) | 0 (agregat→M15, 118.202 bucket) |
| **H1** | 2006-03-20 00:00Z → 2026-07-27 17:00Z | 122.601 | 20,4 | `414adcbe02b8a66469a75c08428ab336267154c19b44fb2f569e252643b1078a` | PASS (dublă + cross) | 0 (agregat→H1, 88.567 bucket) |

Fișier vechi păstrat: `OANDA_XAUUSD_M15__SUPERSEDED_v1_2022-12-16_to_2026-07-13_R03terminal.csv`,
sha `8f865b87e9f88b764d9162d81b46b0a14c13e221f744b95b9e7627bf901955e1` (conține bara terminală greșită
2026-07-13 06:00, volum 8201 vs. corect 13464 — R-03).

## 2. Reparațiile puller-ului (4 fix-uri + documentație)

| Commit | Ce repară |
|--------|-----------|
| `5accefd` | **Seek/stall** — cere timestamp-ul exact, nu miezul nopții (`slice(0,10)`), care după `c839e91` (fail-closed) declanșa toast și oprea walk-ul ca „stale" |
| `0894191` | **Bara-cursor provizorie** — ferestre suprapuse, ca bara de la marginea dreaptă (provizorie) să cadă mereu pe o bară deja finală; + test-simulare |
| `228359b` | **Resume** — `Math.min` prin reduce, nu spread peste 300k+ chei (stack overflow) |
| `c5f7222` | **Recuperare adaptivă** — escaladează sleep-ul la stall (self-heal transient, oprire reală la podea); validat în producție pe H1 fără resume manual |
| `021ee8e` | **Documentație** — `pullers/README_MECHANISM.md`: proprietatea barei-cursor, mecanismul original (goluri+gapfill) vs. fix-ul cu suprapunere |

Teste: `pullers/replay_seek.test.mjs` 11/11 (inclusiv dovada mecanică că bara provizorie nu ajunge în fișier).

## 3. Cauza celor 196 nepotriviri (diagnostic, 3 teste convergente)

Bara de la cursorul de replay are close+volum **provizorii**. Cu ferestre adiacente + dedup first-seen
se salva la fiecare ~300 bare. TEST A: 195/196 nepotriviri exact la marginea dreaptă (57.800× vs.
interior). TEST B: recitire interior == existent 11/12. TEST C: 195 revizuiri minuscule + 1 bară
terminală provizorie a existentului. Fix = ferestre suprapuse. Corectate 1.051 bare pe M15.

## 4. Conectare (commit `ff64fca`)

- `data/market/OANDA_XAUUSD_M15.csv` → v2 curat. `data/market/OANDA_XAUUSD_M5.csv` → nou.
- Vechiul M15 redenumit cu sufix (nu suprascris).
- **Loader verificat** (`tests/test_loader_holdout_boundary.py`, 4/4): M15 încarcă cei 11 ani noi
  (min 2011-07-26); cutoff-ul 2025-10-23T09:15Z e limită exclusivă (17.792 bare de holdout excluse,
  `max_date_used=2025-10-23 09:00`); fail-closed pe config lipsă/gol; **M5 respins** de whitelist.

## 5. Deschise / de decis (nu de mine)

1. **M5 NU e încărcabil** de `load()` — whitelist `{M15,H1,H4,D1}`. Pentru §9 trebuie extins whitelist-ul
   **+ cutoff-ul M5 din `b0d9e0c`**, care NU e în acest repo (e la Statistician). Nu l-am ghicit.
2. **Împărțirea pe 11 ani:** loader-ul sigilează doar holdout-ul terminal (2025-10-23). Dacă
   `STATISTICIAN_11YR_DATASET_PREREGISTRATION_RULES` (nu e în acest repo) sigilează vreo parte din
   2011-2022, Flow A trebuie să paseze cutoff-ul potrivit — de confirmat înainte ca Flow A să pornească.
3. **H1** rămâne în `acquisition_staging/`, neconectat, până publică Statisticianul protocolul 2006-2011.
   Îl mut imediat ce confirmă, fără altă aprobare.
4. **M1** amânat (1 an rulant).

## 5b. Mandat 2 — loader cu poartă-manifest (commit `f3c566a`)

- **Manifest** `config/split_manifest.json` adus verbatim din `6dc81a4` (NEmodificat). `content_hash`
  sha256 = `e6f7ec2db9f412e5f39194e0dbc4870e1f0e716be1dfd988edfb492b43b50103`, **verificat MATCH**.
  `.gitattributes` fixează fișierul la LF (altfel CRLF → hash mismatch → fail-closed, niciodată permisiv).
- **`edge_research/split_manifest.py`** (nou, strict-typed): reader fail-closed. Recalculează hash-ul
  (peste fișier cu `content_hash.value` golit); fișier lipsă / JSON invalid / hash greșit → `ManifestError`.
- **`edge_research/_common.py::load()`**: whitelist `{M15,M5,H1,H4,D1}`; acces permis DOAR pentru un
  timeframe cu status EXACT `VALIDATED` și `discovery_range` populat, DOAR în acea fereastră. Sub
  manifest v1.0.0 = **doar M15**; M5/H1 = AWAITING_REGIME_MAP (sigilate), H4/D1 = absente (sigilate).
  `discovery_end`-ul manifestului (cu embargo-ul nou de 1000 bare) **leagă** peste un cutoff mai permisiv:
  bound efectiv = min(cutoff apelant, discovery_end) = **2025-10-12T23:15Z** pentru M15.
- **Corecția 1:** H1 NU e conectat (AWAITING_REGIME_MAP) — rămâne în `acquisition_staging/`.
- **Corecția 2:** segmentarea pe 11 ani NU e implementată (fără spec). Cei 2011-2022 de pe disc sunt sub
  `discovery_start` → sigilați de poartă.
- **Validare:** `mypy --strict` curat (3 fișiere); `tests/test_loader_holdout_boundary.py` **10/10**
  (M5/H1 aruncă, H4/D1 aruncă, M15 doar în fereastra manifestului, hash greșit respins, manifest absent
  fail-closed). Blast radius intenționat: sigilarea D1 rupe calea D1 din `alpha_automation.DataAccess`
  (1 test); cele 2 picări wave1 sunt pre-existente (mstrat + pandas 3.0/numpy 2.x).
- **Segmentarea pe regimuri LIPSEȘTE** → **Research Lab rămâne blocat** până o publică Statisticianul.
  Flow A poate porni pe M15; decizia de deblocare e a CEO.

## 5c. Mandat 2.5 — hash-uri de fișier + verificare manifest↔disc (loader v4)

**Hash-uri SHA-256 calculate DIRECT din fișierele fizice LF-canonice (sursă DA, nu secondhand):**

| Intrare manifest | Fișier | SHA-256 |
|---|---|---|
| M15 (VALIDATED, legacy) | `data/market/OANDA_XAUUSD_M15__SUPERSEDED_v1_..._R03terminal.csv` | `c777cb9c6097287850b590b205ea4227b1a32ecb9255bdd611723f0364c64e86` |
| M15_v2 (AWAITING_DATA_FILE_HASH) | `data/market/OANDA_XAUUSD_M15.csv` | `57f4ed9544993c8fbba28d9c1e3319f2e0665ef5db211fb09d9f4622222ccd37` |
| M5 (AWAITING_REGIME_MAP_AND_DATA_FILE_HASH) | `data/market/OANDA_XAUUSD_M5.csv` | `cbb6eebe1a189ebb20972318a8d98a36bfa461d2cd030bbaa7ba5430cc9f3814` |
| H1 (AWAITING_REGIME_MAP_AND_DATA_FILE_HASH) | `acquisition_staging/OANDA_XAUUSD_H1.csv` (carantină) | `414adcbe02b8a66469a75c08428ab336267154c19b44fb2f569e252643b1078a` |

Toate cele 4 blob-uri git corespund acestor valori. Notă: hash-ul legacy e **c777cb9c** (forma LF-canonică);
valoarea 8f865b87 raportată anterior era artefactul CRLF al copiei de lucru (autocrlf) — corectat aici,
fișierele fixate LF prin `.gitattributes` pentru stabilitate.

**Manifest v2.1.0** (injectat de mine peste v2.0.0 `4e9cffd`): cele 4 `data_file_sha256` + `file_path`
per intrare; statusuri NESCHIMBATE (M15=VALIDATED, M15_v2=AWAITING_DATA_FILE_HASH, M5/H1=
AWAITING_REGIME_MAP_AND_DATA_FILE_HASH — promovarea e a Statisticianului). `content_hash` recalculat =
`99b9b385e76590f213ccbfd42285be4f075b5daf04abd57f31d085c09da7a57b` (metodă validată: UTF-8, LF, value golit).

**Loader v4** (`edge_research/_common.py`): DOUĂ condiții fail-closed — (1) content_hash manifest, (2)
sha256 fișier-de-date vs intrare. file_path rezolvat din manifest (M15→legacy, M15_v2→canonic, fără alias).
`mypy --strict` curat; teste **11/11**: M15 citește (ambele hash-uri), M15_v2 respins pe status deși hash
corespunde, M5/H1 respinse, **fișier modificat cu un byte respins pe nepotrivire de hash**.

## 5d. Mandat 2.6 — segmentare + carantină la runtime (loader v5)

Manifest **v2.2.0** (`4e1f550`, Statisticianul; hash-urile mele ratificate independent): M15_v2 și M5
promovate la VALIDATED cu hărți de regim; H1 rămâne AWAITING_REGIME_MAP. Loader-ul (`edge_research/`,
`split_manifest.segmentation_plan` + `_common.load`) livrează acum, la runtime, **exact reuniunea
segmentelor de descoperire**, cu benzile de carantină (embargo lider/intra/final, 1000 bare/parte la
M15_v2, 3000 la M5) și jumătățile sigilate excluse. Coordonatele vin verbatim din manifest, nu recalculate.

**Contabilitate (îmbucă tot fișierul, sumă = total):**

| TF | Total | Livrat (discovery) | Carantină | Sigilat |
|----|------:|-------------------:|----------:|--------:|
| M15_v2 | 355.696 | **130.491** | 7.215 | 217.990 |
| M5 | 354.669 | **162.899** | 22.458 | 169.312 |
| M15 (legacy) | 84.152 | 66.545 | 1.375 | 16.232 |

- Chei distincte fără alias (`M15`→legacy, `M15_v2`→canonic prin file_path). Cheie necunoscută/ambiguă →
  `IdentifierError` (tip distinct de eșecul de hash și de status).
- Cele 3 zone sigilate integral M15_v2 (feliuța pre-overlap, overlap_with_M15, post_M15_tail) — excluse.
- Verificarea dublă de hash (manifest + fișier-de-date) păstrată; fișier modificat cu un byte → respins.
- `mypy --strict` curat; teste **17/17** — inclusiv: bară din FIECARE bandă de carantină și din fiecare
  jumătate sigilată NU apare (dovada că segmentarea e reală), H1 aruncă, identificator ambiguu aruncă distinct.
- Commit `alpha-automation-v1`. H1 rămâne blocat; Research Lab blocat până la harta de regim H1.

## 6. Amplitudinea barei M5 — pragul minim de stop §9 (CHECK 6)

Mediană high-low (puncte): TOATE **1,400**, IQR [0,815–2,655], p90 4,995. Per sesiune: asia 1,220 ·
london 1,525 · ny 1,710 · late 0,735. Un stop sub ~1,4 face median-bar-ul M5 nedeterminat intrabar.
