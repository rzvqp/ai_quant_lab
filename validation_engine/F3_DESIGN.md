# F3 — DESIGN
### Infrastructura de audit și guvernanță: manifest, checksums, ledger, integritate, bundle

**Document ID:** VE-F3-DESIGN-v1.0
**Data:** 2026-07-25 · **Autor:** Validation Engine
**Statut:** DESIGN — implementat imediat după, în aceeași fază (arhitectura F3 era deja aprobată în §8; acest document o rafinează la nivel de module).
**Autoritate:** F3 autorizată de CEO 2026-07-25, cu limite obligatorii.

---

## 1. Domeniul F3 (limitele obligatorii)

**INCLUS:** infrastructură de audit + guvernanță · manifest (PRE + final) · checksums · ledger append-only · verificări de integritate · bundle-uri și artefacte.

**EXCLUS (obligatoriu):** acces la date · execuția metodelor · strat de date · logică statistică nouă · modificarea registrelor de capabilități (decât la un defect de infrastructură).

Consecința centrală: în F3, o „rulare" este o **rulare de audit** — validează specificația (F2, fără date) și **sigilează metadatele** într-un bundle reproductibil. Nu deschide nicio sursă de date și nu execută nicio metodă.

---

## 2. Verificarea impactului asupra arhitecturii

**Impact zero asupra arhitecturii aprobate.** F3 implementează exact componentele deja prevăzute în `VALIDATION_ENGINE_ARCHITECTURE_v1.0.md`:

| Element de arhitectură | Secțiune | Implementat în F3 |
|---|---|---|
| PRE-MANIFEST + MANIFEST | §5 fază 5/11, §8 | `ve/run/runner.py`, `ve/manifest/` |
| Checksums | §7, §11 | `ve/audit/checksums.py` |
| Ledger append-only | §3.5, §10 pct. 7 | `ve/audit/ledger.py` |
| Integritatea repo (external_writes) | §4.2, §11 | `ve/audit/repo_integrity.py` |
| Bundle write-once | §4.5, §7 | `ve/run/runner.py` (`mkdir(exist_ok=False)`) |
| Semințe derivate determinist | §10 pct. 1 | `ve/rng/streams.py` (doar hashing) |
| Captura mediului | §10 pct. 5 | `ve/manifest/environment.py` |
| Snapshot de cod | §10 pct. 4 | `ve/manifest/code_snapshot.py` |
| Comanda `verify` | §10 pct. 6 | `ve/verify/replay.py` |

Nicio interfață din arhitectură nu se schimbă. Contractul cu Statisticianul nu se atinge. Schema și registrul rămân neschimbate.

---

## 3. Arhitectura internă F3

```
ve/
  run/runner.py        Orchestratorul rulării de audit (fazele 0-5-11 + checksums/ledger)
  manifest/
    environment.py     versiuni Python/biblioteci, OS, mașină
    code_snapshot.py   commit git + arbore curat
  audit/
    access_audit.py    (F2) garda de acces la date — activă pe toată rularea
    checksums.py       SHA-256 per fișier + hash agregat de bundle + verify
    ledger.py          append-only JSONL + MD
    repo_integrity.py  instantaneu VE tree (exclude runs/), external_writes
  rng/streams.py       seed = sha256(spec_sha256 || test_id)[:8], pur derivat
  verify/replay.py     re-verificarea unui bundle existent
```

Direcția de dependență: `runner` depinde de `manifest`, `audit`, `rng`, `spec` (F2). Nucleul de audit nu conține logică statistică.

---

## 4. Fluxul rulării de audit

```
0. Intake         spec → spec_sha256, run_id, director de rulare (write-once)
   [instantaneu integritate ÎNAINTE — exclude runs/]
1-3. Validare     formă + vocabular (F2), SUB GARDA DE ACCES LA DATE (interdicție)
5. PRE-MANIFEST   scris înainte de orice altceva în bundle
   + SPEC_RECEIVED, VALIDATION, seeds (dacă PASSED), environment, log
   [instantaneu integritate DUPĂ → external_writes]
11. MANIFEST      final: mediu, cod, semințe, integritate repo, replay_command
+. CHECKSUMS      SHA-256 peste tot bundle-ul (ultimul fișier)
+. LEDGER         intrare append-only, indiferent de status
```

Rularea validării se face în interiorul `access_audit.recording(forbid_data=True)`: orice încercare de a deschide un fișier de date **abandonează operațiunea**. Manifestul publică `data.data_accesses` — dovada mecanică că a fost 0.

Specificațiile reale (DC-0004 etc.) se opresc la validare pe poarta de calibrare (E3), deci rularea de audit produce un bundle cu `status: HALTED` — comportamentul corect și așteptat. Bundle-ul este complet indiferent de status: **o rulare oprită produce tot un manifest complet**, exact criteriul de acceptare F3.

---

## 5. Formatul bundle-ului (write-once)

```
runs/VE-RUN-<ts>-<spec8>__<candidat>__audit/
├── PRE_MANIFEST.json     scris înaintea oricărei alte operații
├── MANIFEST.json         final
├── SPEC_RECEIVED.json    copie bit-identică a specificației
├── VALIDATION.json       status, coduri, erori, data_accesses
├── seeds.json            semințe derivate (doar dacă PASSED)
├── environment.json
├── logs/run.log
└── CHECKSUMS.sha256      peste toate fișierele de mai sus
```

Ledger-ul (`run_ledger.jsonl` + `RUN_LEDGER.md`) stă în rădăcina `validation_engine/`, nu în bundle — este cronologia tuturor rulărilor.

---

## 6. Comanda `verify`

Re-verifică un bundle existent, **fără date, fără execuție**:
1. re-calculează SHA-256 al fiecărui fișier și compară cu `CHECKSUMS.sha256` → `EXACT` / `MISMATCH` + diff;
2. confirmă coerența internă a manifestului (bundle prezent, câmpuri obligatorii);
3. raportează `external_writes` din manifest.

O modificare de un bit în orice fișier al bundle-ului este detectată (`MISMATCH`).

---

## 7. Determinism

`run_id` și `timestamp` sunt **injectabile** — în teste se pasează valori fixe, deci un bundle este bit-reproductibil; în CLI se derivă din timp. `verify` compară coerența internă (checksums), nu identitatea între rulări (care diferă prin timestamp/run_id, ca în `results/reproduction_v2/`). Semințele și hash-urile de conținut sunt complet deterministe.

---

## 8. Criterii de acceptare F3

1. O rulare de audit produce un **manifest complet** și un bundle valid.
2. `external_writes = 0` (nimic scris în afara directorului de rulare) — dovedit prin instantaneu înainte/după.
3. **Zero accesări de date** în timpul rulării — dovedit prin garda de acces.
4. `verify` întoarce `EXACT` pe un bundle intact și `MISMATCH` la orice alterare.
5. Ledger-ul este append-only — o a doua rulare adaugă, nu rescrie.
6. Bundle write-once — nu suprascrie un director existent.
7. Toate metodele rămân `UNVALIDATED`; registrul `PUBLISHED_NOT_EXECUTABLE`; schema neschimbată.

---

**Design gata. Implementarea urmează imediat, în limitele F3. Fără date, fără execuție de metode, fără logică statistică.**
