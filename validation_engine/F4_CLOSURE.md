# ÎNCHIDEREA OFICIALĂ A FAZEI F4
### Stratul de date, construirea populațiilor, materializarea variabilelor — cu DC-0004 reproducând EXACT experimentul in-sample

**Document ID:** VE-F4-CLOSURE-v1.0
**Data:** 2026-07-25 · **Autor:** Validation Engine
**Statut:** **ÎNCHIDERE F4 — pentru confirmarea CEO.** F5 NU este autorizat. Registrul, schema, vocabularul și motorul neatinse de corecțiile de specificație. Holdout NEATINS.

> F4 a livrat stratul de date + populație + variabile (raportat în `F4_REPORT.md`), apoi a trecut prin trei corecții de specificație (F4-1/F4-2/F4-3) până când **DC-0004 reproduce exact experimentul in-sample al scripturilor Alpha**, verificat împotriva obs0003/obs0008/obs0012.

---

## 1. Obiectivele F4 — îndeplinite

- **Strat de acces la date** cu verificarea hash-urilor, jurnalizare, loader streaming care se oprește la granița sigilată. ✅
- **Construirea populațiilor și cohortelor** — predicate (conjuncție G4), first_in_scope, cooldown, denominator per criteriu. ✅
- **Aplicarea eligibility** → familia realizată (câmpuri pre-rezultat). ✅
- **Materializarea variabilelor** — fără statistici. ✅
- **Integrare în bundle/manifest F3.** ✅
- **Holdout neatins**, dovadă verificabilă. ✅
- **DC-0004 reproduce EXACT experimentul in-sample.** ✅ (după F4-1/F4-2/F4-3)

---

## 2. Cele trei corecții de specificație (toate autorizate individual de CEO)

Fiecare descoperită prin materializarea F4 și confirmată împotriva scripturilor Alpha. **Niciuna nu a modificat motorul, registrul, schema sau vocabularul** — doar specificația oficială DC-0004.

| # | Discrepanța descoperită | Corecția | Confirmare |
|---|---|---|---|
| **F4-1** | PDH/PDL derivat din D1 (rollover 21:00/22:00), nu din H1 grupat pe zi UTC | `source_id` pdh/pdl D1→H1; D1 eliminat din `data` | familia empirică devine identică cu obs0012 |
| **F4-2** | Celulele marcau direcția prin `high>pdh`, nu prin evenimentul complet; 35 bare spargeau ambele direcții → supraestimare | celule = `in_session ∧ first_in_scope(high>pdh) ∧ close<pdh` | n per celulă **exact** 135/34/42/114/40/47; total 430 |
| **F4-3** | Baseline declara `exclude_event_bars: True`, dar Alpha include barele-eveniment | `exclude_event_bars: True→False` (aliniere la motor+Alpha, verificat în cod obs0008/0012) | excess per celulă **exact** obs0012 |

---

## 3. Confirmarea reproducerii EXACTE împotriva Alpha

Materializat pe fereastra deschisă completă (identică cu obs0012), **holdout neatins** (`max_ts_read = 2025-10-23T09:00:00Z < graniță`).

| Nivel | Validation Engine | Alpha (obs) | Potrivire |
|---|---|---|---|
| **Event count per celulă** | 135/34/42/114/40/47 | obs0012 | ✅ exact |
| **Total interacțiuni reject** | 430 | obs0003 („430") | ✅ exact |
| **Familia eligibilă (n≥25)** | asia/london/ny × up/dn, m=6 | obs0012 (6 celule) | ✅ exact |
| **Celule excluse** | late_up, late_dn (n=9) | late (sub prag) | ✅ exact |
| **Prag Bonferroni** | 0.05/6 = 0.0083 | obs0012 (0.0083) | ✅ exact |
| **Baseline per sesiune (K6)** | 0.5122/0.2172/1.4535/1.0498 | formula obs (recalc, 1e-9) | ✅ exact |
| **Excess per celulă** | −3.64/1.29/1.75/−1.04/−0.46/−0.36 | obs0012 (coloana excess) | ✅ exact |

**Nicio diferență rămasă între DC-0004 și experimentul original la nivelul F4** (date, populație, variabile, baseline, familie, excess).

*Notă:* verificarea excess-ului per celulă a fost un **diagnostic** de reproducere, nu un livrabil F4 — bundle-ul F4 conține numărători (n, denominator), nu medii/efecte. Ultimul pas al obs (matched-null cu 3000 reeșantionări, seed=7, coada stângă → valoarea p) este **F5** (execuția metodei); intrarea lui (excess) este confirmată.

---

## 4. Arhitectura finală (rezumat)

Straturile F4, neschimbate de corecțiile de specificație:
```
ve/data/       sealing, integrity (hash fail-closed), access_journal, sources (streaming, stop la graniță), calendar (00:00 UTC, sesiuni UTC)
ve/population/ predicates (conjuncție), builder (denominator per criteriu), eligibility (familia realizată)
ve/variables/  materialize (raw_series, prior_period_extreme H1-UTC-zi, session_label, forward_return, baseline per sesiune, forward_excess), leakage_guard
ve/run/        materializer (validare → date → populație → variabile → eligibilitate → bundle; NU execută metode)
```

Bundle F4 = bundle F3 + `ACCESS_JOURNAL.json`, `POPULATION.json`, `REALIZED_FAMILY.json`, `MATERIALIZATION.json`.

---

## 5. Dovada că nu a fost executată nicio metodă / holdout neatins

| Dovadă | Valoare |
|---|---|
| `methods_executed` | 0 |
| Ieșiri F4 fără p-values/efecte | verificat lexical |
| `max_ts_read` (H1) | 2025-10-23T09:00:00Z < graniță 09:15 |
| `sealed_window_touched` | False |
| Hash-urile celor 4 surse de piață (holdout inclus) | **identice** cu F1 |
| Metode `VALIDATED` | 0 / 15 |
| Registru | `PUBLISHED_NOT_EXECUTABLE` |

---

## 6. Goluri/datorii rămase după F4

| ID | Natură | Status |
|---|---|---|
| **G6** | sursă M1/M5 + agregare sub-bară (expunerea R a DC-0008) | `DESCHIS`, în afara fazei |
| **F4-4** | `baseline_forward_mean@v1` nu implementează `exclude_event_bars` (îl ignoră) | `CONSEMNAT`, **non-blocant** — DC-0004 folosește `False` = comportamentul motorului = Alpha; ar deveni defect doar la un protocol viitor cu `True` |
| **P1** | evaluarea mecanică a criteriilor (înainte de F7) | `DESCHIS` |

Niciunul nu blochează reproducerea DC-0004 sau F5.

---

## 7. Fișiere modificate în ciclul de corecții

**Specificație/fixturi (autorizate):** `tests/fixtures/reference_spec_dc0004.json` (PDH→H1, celule eveniment-complet, baseline False), `tests/fixtures/dev_spec_open_window.json` (fixtura de confirmare aliniată la obs0012).
**Documente:** `F4_1_DC0004_FIX_REPORT.md`, `F4_2_DC0004_CELLFIX_REPORT.md`, `F4_CLOSURE.md`, `VE_BACKLOG.md`.
**Neatins (hash verificat):** motorul (`materialize.py` `842fa301…`, `materializer.py` `ce118faa…`), registrul (`capabilities.json` `fb78b935…`), schema (`f1ba7009…`), validatorul, cele 4 surse de date.

**Teste:** 389 passed.

---

## 8. Condițiile pentru autorizarea F5

F5 (execuția metodelor statistice) devine posibilă odată ce:
1. **CEO confirmă că reproducerea DC-0004 la nivel F4 este acceptată** (populație/familie/baseline/excess = Alpha exact).
2. Domeniul F5 este confirmat: execuția metodelor pe fereastra **deschisă** (matched-null, dip test etc.); holdout rămâne pentru F8.
3. Prima metodă de calibrat rămâne `matched_null@v1` — reproducerea valorii p a obs0012 (seed=7, 3000 reeșantionări, coada stângă) va fi criteriul de reproducere la F5.
4. Invarianții F2 se mențin până la momentul în care F6 acordă `VALIDATED` unei metode.

---

## 9. Concluzie

F4 este complet. Stratul de date construiește populații și variabile pe fereastra deschisă, cu holdout-ul dovedit neatins și nicio metodă executată. Cele trei discrepanțe descoperite prin materializare au fost corectate (exclusiv în specificație, cu autorizare individuală), iar **DC-0004 reproduce acum EXACT experimentul in-sample al scripturilor Alpha** — la nivel de populație, familie, baseline și excess. Ultimul nivel (valoarea p a matched-null) aparține F5, iar intrarea lui este confirmată identică cu Alpha.

**F4 este închis. Nicio metodă executabilă. Holdout neatins. F5 nu a fost început.**

**Validation Engine se oprește și așteaptă aprobarea CEO pentru autorizarea F5.**
