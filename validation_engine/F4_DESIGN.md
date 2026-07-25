# F4 — DESIGN
### Stratul de date, construirea populațiilor și materializarea variabilelor

**Document ID:** VE-F4-DESIGN-v1.0
**Data:** 2026-07-25 · **Autor:** Validation Engine
**Statut:** DESIGN — pentru implementare imediat după. Autoritate: F4 autorizată de CEO 2026-07-25, cu limite obligatorii.

---

## 1. Domeniul F4 (limitele obligatorii)

**INCLUS:** stratul de acces la date · verificarea hash-urilor surselor · jurnalizarea fiecărei accesări · construirea populațiilor și cohortelor · aplicarea regulilor de scope/predicate/eligibility · materializarea variabilelor și indicatorilor · integrarea în bundle-ul/manifestul F3.

**EXCLUS (obligatoriu):** execuția metodelor statistice · p-values/efecte/corecții multiple/interpretare · calibrarea metodelor · **acces la holdout** · modificarea definițiilor normative blocate · rezolvarea automată a lui G6.

Fail-closed pe orice nepotrivire de hash/sursă/schemă/interval. O rulare oprită produce tot un bundle complet de audit (moștenit din F3).

---

## 2. Distincția cheie: materializare ≠ execuție de metode

O rulare de audit (F3) se oprește la validare pe poarta de calibrare (metodele sunt `UNVALIDATED`). **Materializarea (F4) nu execută metode** — construiește *intrările* metodelor (populația + variabilele + familia eligibilă). Prin urmare:

> Materializarea cere ca **populația, variabilele și sursele de date** să fie valide, dar **NU** cere ca metodele de test să fie `VALIDATED` — pentru că nu le rulează.

Regula de decizie a materializatorului: rulează validarea F2; dacă **singurele** erori rămase sunt porți de calibrare pe metode (`tests/*/method`, `multiple_testing/method`, reason = „UNVALIDATED"), materializarea **continuă** pe populație+variabile. Orice altă eroare (structură, vocabular, hash, fereastră sigilată, leakage) **oprește** fail-closed. Execuția metodelor rămâne blocată pentru F5.

---

## 3. Verificarea impactului asupra arhitecturii

F4 implementează stratul de date prevăzut în arhitectură §3 (L1 DATE, L2 CONSTRUCȚIE) și fluxul fazelor 4/6/7. **Impact zero asupra interfețelor**: contractul, schema, registrul, bundle-ul F3 rămân neschimbate. F4 *extinde* bundle-ul cu artefacte noi (populație, familie realizată, jurnal de acces), nu modifică structura existentă.

O singură clarificare de comportament, consemnată: **garda de acces trece din regim de INTERDICȚIE (F3) în regim de ÎNREGISTRARE pentru fereastra deschisă**, păstrând INTERDICȚIA pentru holdout. Aceasta era deja prevăzută în arhitectură §1.3 („fereastra sigilată nu este încărcată").

---

## 4. Arhitectura internă F4

```
ve/data/
  sealing.py        registrul de ferestre sigilate + granița 00:00... = 2025-10-23T09:15:00Z
  integrity.py      SHA-256 al fișierului vs. hash declarat (spec) și înregistrat (registru)
  access_journal.py fiecare accesare: cale, scop, rânduri citite, max_ts_read
  sources.py        loader STREAMING care se OPREȘTE la granița sigilată (holdout neîncărcat)
  calendar.py       granița zilei = 00:00 UTC; etichetare de sesiune pe ore UTC fixe
ve/population/
  predicates.py     compare, and/or/not, in_session, bar_position, first_in_scope, crosses, sequence, cooldown
  builder.py        include(∧)/exclude(∨) + cooldown → evenimente + denominator per criteriu
  eligibility.py    aplică member_eligibility {field∈[n,denominator,event_count]} → familia realizată
ve/variables/
  primitives.py     raw_series, prior_period_extreme, forward_return, baseline_forward_mean,
                    forward_excess, session_label, hour_of_day_volatility_profile, volume_zscore, indicator, ...
  leakage_guard.py  verificare la runtime: nicio valoare nu folosește bare cu ts > ts_eveniment + offset declarat
  materialize.py    dispatch primitive → valori, sub garda de disponibilitate
ve/run/
  materializer.py   orchestrator F4: validare → date → populație → variabile → eligibilitate → bundle
  cli.py            + subcomanda `materialize`
```

---

## 5. Stratul de date — contract și protecția holdout-ului

### 5.1 Contractul surselor
Fiecare sursă declară în specificație `{source_id, sha256}`. F4:
1. **verifică integritatea** — recalculează SHA-256 al fișierului întreg și compară cu hash-ul declarat (spec) ȘI cu cel înregistrat (registru); orice nepotrivire → **E4 halt**;
2. **verifică acoperirea** — fereastra cerută trebuie să existe în date; altfel → E4 halt;
3. **încarcă STREAMING doar fereastra deschisă** — citește rânduri în ordine crescătoare a timpului și se **oprește** la primul rând cu `ts ≥ granița sigilată`. Rândurile sigilate **nu sunt parsate în memorie**.

### 5.2 Protecția holdout-ului (F4 nu-l atinge)
- **F4 refuză orice fereastră care se suprapune peste granița sigilată** — indiferent de autorizare. Protocolul de holdout (token, rehearsal, consum unic) este **F8**, nu F4.
- Loader-ul se oprește la graniță; jurnalul de acces înregistrează `max_ts_read` per sursă.
- **Dovada verificabilă**: `max_ts_read < 2025-10-23T09:15:00Z` pentru fiecare sursă, publicată în manifest. Rândurile sigilate nu intră în nicio populație sau variabilă.
- Notă onestă: verificarea hash-ului citește *octeții* întregului fișier (necesar pentru integritate), dar **niciun rând sigilat nu este parsat ca dată** — cele două operații sunt separate în jurnal (`hash_read` vs `data_read`), iar dovada de non-utilizare este `max_ts_read`.

### 5.3 Comportamentul la anomalii de date
| Anomalie | Comportament |
|---|---|
| **Timestamp duplicat** | E4 halt (integritate) — nu se deduplică tăcut |
| **Timp ne-monoton** | E4 halt |
| **OHLC invalid** (high<low etc.) | E4 halt |
| **Fereastră neacoperită** de date | E4 halt |
| **Gap** (weekend, ore lipsă) | permis — se operează pe barele prezente; **nu se completează, nu se interpolează** |
| **Bară lipsă la o poziție așteptată** | fără fabricare — populația folosește barele reale prezente |
| **Timezone** | totul în UTC (epoch); ziua = 00:00 UTC; sesiuni pe ore UTC fixe (Calea A) — fără conversie locală |

---

## 6. Construirea populației

1. **Materializează variabilele** referite de predicate (raw_series, pdh/pdl, session, …), sub garda de disponibilitate.
2. **Evaluează `include`** ca **conjuncție** (G4): o bară intră dacă satisface TOATE predicatele. `first_in_scope(day, …)` selectează prima bară a zilei (00:00 UTC) care satisface predicatul intern.
3. **Evaluează `exclude`** — o bară e scoasă dacă potrivește ORICARE predicat de excludere.
4. **Aplică `cooldown`** — deduplică evenimente la mai puțin de `min_bars_between_events`.
5. **Raportează denominatorul per criteriu** — câte bare candidate a respins fiecare predicat de includere.
6. **Rezultat:** setul de evenimente + denominatorul, fără nicio statistică.

## 7. Aplicarea eligibility (familia realizată)

Materializatorul calculează `n` per celulă (numărul de evenimente în fiecare celulă a testului), apoi aplică `member_eligibility {field, op, value}` — dar **doar pe câmpuri pre-rezultat** (`n`, `denominator`, `event_count`). Rezultatul: **familia realizată** = celulele eligibile + `m`. Aceasta NU este o corecție statistică (pragul Bonferroni e F5) — este o operație de numărare a populației. R3 rămâne impusă: eligibilitatea nu poate referi niciun rezultat.

## 8. Materializarea variabilelor

Fiecare variabilă declarată e calculată la valorile ei per bară de eveniment, sub **garda de disponibilitate la runtime**: o valoare nu poate folosi bare cu timestamp în afara ferestrei permise de `availability.offset_bars`. Rezultatul materializării este un rezumat (per variabilă: câte valori, formă de bază — **fără** medii, teste sau interpretare) + valorile brute salvate în bundle.

---

## 9. Integrarea în bundle (extinde F3)

Bundle-ul de materializare adaugă, la structura F3:
```
├── ACCESS_JOURNAL.json    fiecare accesare de fișier + max_ts_read per sursă
├── POPULATION.json        n evenimente, denominator per criteriu, fereastră
├── REALIZED_FAMILY.json   celule eligibile, m, per-celulă n
├── MATERIALIZATION.json   per variabilă: count, formă (fără statistici)
└── (F3: PRE_MANIFEST, MANIFEST, SPEC_RECEIVED, VALIDATION, seeds, environment, CHECKSUMS, logs)
```
Manifestul F3 primește o secțiune nouă `data` completată: hash-uri **calculate** (nu doar declarate), `max_ts_read` per sursă, `sealed_window_touched: false`, `methods_executed: 0`.

---

## 10. Criterii de acceptare F4

1. Materializare pe fereastra deschisă → populație + variabile + familie realizată, **fără execuție de metode** (`methods_executed = 0`).
2. **Holdout neatins** — `max_ts_read < 2025-10-23T09:15:00Z` pentru fiecare sursă; `sealed_window_touched = false`; o specificație cu fereastră peste graniță → **halt** (F4 nu deschide holdout-ul).
3. **Hash fail-closed** — nepotrivire de hash → E4 halt + bundle de audit.
4. **Fiecare accesare jurnalizată** — `ACCESS_JOURNAL.json` complet și verificabil.
5. Anomalii (duplicat, ne-monoton, OHLC invalid, fereastră neacoperită) → halt fail-closed.
6. O rulare oprită produce tot un bundle complet.
7. Zero p-values/efecte/corecții/interpretare oriunde în ieșiri.
8. Toate metodele rămân `UNVALIDATED`; registru `PUBLISHED_NOT_EXECUTABLE`; schema neschimbată.
9. Testarea folosește **exclusiv fereastra deschisă**; holdout dovedit neatins în raport.

---

**Design gata. Implementarea urmează, strict în limitele F4. Fără execuția metodelor, fără p-values, fără holdout.**
