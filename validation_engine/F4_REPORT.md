# F4 — RAPORT DE ÎNCHIDERE
### Stratul de date, construirea populațiilor și materializarea variabilelor

**Document ID:** VE-F4-REPORT-v1.0
**Data:** 2026-07-25 · **Autor:** Validation Engine
**Autoritate:** F4 autorizată de CEO 2026-07-25, cu limite obligatorii.
**Statut:** livrat, în așteptarea aprobării. **Fără execuția metodelor. Fără p-values/efecte/corecții/interpretare. Fără calibrare. Holdout NEATINS. Registru neschimbat. F5 neînceput.**

---

## 1. Arhitectura stratului de date

```
ve/data/
  sealing.py         granița sigilată 2025-10-23T09:15:00Z; F4 refuză orice fereastră care o atinge
  integrity.py       SHA-256 al fișierului vs. hash declarat (spec) ȘI înregistrat (registru); E4 fail-closed
  access_journal.py  fiecare accesare: hash_read vs data_read + max_ts_read per sursă
  sources.py         loader STREAMING care se OPREȘTE la graniță — rândurile sigilate nu se parsează
  calendar.py        ziua = 00:00 UTC; sesiuni pe ore UTC fixe (Calea A)
ve/population/
  predicates.py      compare, and/or/not, in_session, bar_position, first_in_scope (conjuncție G4)
  builder.py         include(∧) − exclude(∨) − cooldown → evenimente + denominator per criteriu
  eligibility.py     member_eligibility {field∈[n,event_count]} → familia realizată (fără corecție)
ve/variables/
  materialize.py     raw_series, prior_period_extreme, session_label, forward_return,
                     baseline_forward_mean (per sesiune), forward_excess, volume_zscore
  leakage_guard.py   garda de disponibilitate la runtime (roluri non-viitoare: offset ≤ 0)
ve/run/materializer.py  orchestrator F4; extinde bundle-ul F3
ve/cli.py               + subcomanda `materialize`
```

**Materializarea nu execută metode.** Dacă singurele erori de validare sunt porți de calibrare pe metode (`UNVALIDATED`), materializarea continuă pe populație+variabile; orice altă eroare oprește fail-closed. Metodele rămân pentru F5.

---

## 2. Verificarea impactului arhitectural

**Zero** asupra interfețelor. F4 implementează straturile L1/L2 și fazele 4/6/7 din arhitectură; extinde bundle-ul F3 cu artefacte noi (POPULATION, REALIZED_FAMILY, MATERIALIZATION, ACCESS_JOURNAL), fără a schimba structura existentă. Contractul, schema, registrul, bundle-ul F3 rămân neatinse. Detalii în `F4_DESIGN.md` §3.

---

## 3. Contractul surselor și verificarea hash-urilor

Fiecare sursă declară `{source_id, sha256}`. F4:
1. **recalculează SHA-256** al fișierului întreg și compară cu hash-ul declarat (spec) **ȘI** cu cel înregistrat (registru); orice nepotrivire → **oprire fail-closed** (la F2 ca E2 vocabular, sau la F4 ca DataIntegrityError);
2. **verifică acoperirea** — fereastra fără bare → oprire;
3. verifică **monotonia, duplicatele, validitatea OHLC** la încărcare — orice anomalie → oprire.

Test direct: `resolve_and_verify` cu hash greșit ridică `DataIntegrityError`; materializarea cu hash declarat greșit se oprește.

---

## 4. Jurnalul de acces

`ACCESS_JOURNAL.json` înregistrează, per accesare: `source_id`, `path`, `kind` (`hash_read` = octeți pentru integritate / `data_read` = rânduri parsate), `rows_read`, `max_ts_read`, `stopped_at_boundary`. Manifestul publică `max_ts_read_by_source` și `sealed_window_touched`.

Distincția `hash_read` vs `data_read` este onestă: verificarea hash-ului citește octeții întregului fișier (necesar pentru integritate), dar **niciun rând sigilat nu este parsat ca dată** — dovada de non-utilizare este `max_ts_read` din citirile `data_read`.

---

## 5. Construirea populațiilor — demonstrație pe fereastra deschisă

Rulare de materializare pe fixtura DEV (replicare sweep-reject, **fereastra deschisă** 2023-06 → 2025-06, `authorization.required=false`):

```
status: MATERIALIZED | n_events: 295 | sealed_touched: False | external_writes: 0
n per celulă: asia_up 96, asia_dn 84, london_up 27, london_dn 35,
              ny_up 32, ny_dn 33, late_up 6, late_dn 6
familie realizată (n≥25): m = 6  →  cele două celule 'late' (n=6) EXCLUSE
methods_executed: 0
```

Aceasta demonstrează, integrat:
- **populația** — `first_in_scope(day)` (prima bară a zilei UTC care depășește nivelul), 4 sesiuni UTC, cooldown, denominator per criteriu;
- **variabilele** — raw_series, `prior_period_extreme` (PDH = max high al zilei UTC anterioare, din H1), forward_return, baseline per sesiune, forward_excess;
- **familia empirică n≥25** — exact mecanismul din `obs0012`: celulele cu suport sub prag ('late', n=6) sunt excluse, m=6. Funcțional la F4, fără nicio corecție statistică.

---

## 6. Comportamentul la date lipsă, duplicate, gap-uri, timezone

| Situație | Comportament | Verificare |
|---|---|---|
| **Timestamp duplicat / ne-monoton** | oprire fail-closed (integritate) | loader `DataLoadError` |
| **OHLC invalid** | oprire fail-closed | loader `DataLoadError` |
| **Fereastră neacoperită / populație sub min_n** | oprire fail-closed (E6) | `test_uncovered_window_halts` |
| **Gap** (weekend, ore lipsă) | permis — se operează pe barele prezente; **nu se completează, nu se interpolează** | design §5.3 |
| **Bară lipsă la poziția așteptată** | fără fabricare | design §5.3 |
| **Timezone** | totul UTC (epoch); ziua = 00:00 UTC; sesiuni pe ore UTC fixe; **fără DST** (Calea A) | `ve/data/calendar.py` |

---

## 7. Rezultatele testelor

```
../venv/Scripts/python.exe -m pytest tests -q
389 passed in 7.78s
```

| Suită | Teste |
|---|---|
| F2 (validator, mutații, acces, clarificare, referință) | 360 |
| F3 (audit) | 16 |
| **F4 (`test_f4_materialize.py`)** | **13** |

Testele F4 acoperă: construirea populației, familia empirică n≥25 (celule cu suport mic excluse), materializarea variabilelor fără statistici, **holdout neatins**, oprirea specificației care țintește holdout, oprirea loader-ului la graniță, fail-closed pe hash/fereastră neacoperită, zero metode executate, zero p-values în ieșiri, invarianții F2 păstrați, external_writes zero.

---

## 8. Dovada că nu a fost executată nicio metodă statistică

- `manifest.execution.methods_executed == 0` în fiecare rulare.
- Materializatorul **nu importă și nu apelează** niciuna dintre cele 12 metode de test / 3 de corecție. `ve/run/materializer.py` depinde doar de `data/`, `population/`, `variables/`, `spec/` (F2), `audit/`, `manifest/`.
- Ieșirile F4 (POPULATION, REALIZED_FAMILY, MATERIALIZATION, MANIFEST, ACCESS_JOURNAL) **nu conțin** `p_value`, `p_hat`, `significant`, praguri corectate (test `test_no_pvalue_anywhere_in_bundle`).
- Familia realizată este o **numărare de populație** (n per celulă), nu o corecție — pragul Bonferroni rămâne pentru F5.
- Registru `PUBLISHED_NOT_EXECUTABLE`; 15/15 metode `UNVALIDATED` (neschimbat).

---

## 9. Dovada că holdout-ul nu a fost accesat

| Dovadă | Valoare |
|---|---|
| Granița sigilată | `2025-10-23T09:15:00Z` (epoch 1761210900) |
| `max_ts_read` H1 (materializare DEV) | `2025-10-23T09:00:00Z` — **strict înainte de graniță** |
| `sealed_window_touched` | **False** în manifest și în jurnalul de acces |
| Loader la graniță | se oprește; `test_loader_stops_at_boundary`: exact 16.623 bare deschise H1 |
| Specificație care țintește holdout | **oprită** — F4 refuză fereastra sigilată indiferent de autorizare (`test_spec_targeting_holdout_halts`) |
| **Hash-urile celor 4 fișiere de piață (holdout inclus)** | **identice** cu cele de la F1 — fișierele nu au fost modificate |

Holdout-ul (16.831 bare M15 / 4.209 H1 post-graniță) nu a fost **încărcat ca dată** în nicio populație sau variabilă. Rândurile sigilate nu sunt parsate de loader (oprire la graniță).

---

## 10. Gol nou descoperit — CONSEMNAT, NEREZOLVAT

Conform instrucțiunii („gol/contradicție → înregistrează și oprește-te; nu rezolva automat"):

**F4-1 — sursa PDH în specificația oficială DC-0004 contrazice convenția in-sample.** DC-0004 (Calea A) calculează PDH/PDL din sursa **D1**, dar `_lab.add_prior_day` (in-sample) calculează PDH din **H1 grupat pe zi calendaristică UTC**. D1 e ancorat la rollover-ul de broker (21:00/22:00 UTC), misaliniat față de ziua UTC — la materializare, concentrează artificial evenimentele în sesiunea „late".

- **NU este gol de vocabular:** `prior_period_extreme@v1` cu `source_id=H1` exprimă corect convenția (verificat — fixtura DEV cu H1 dă distribuție corectă pe sesiuni, m=6).
- **Este o eroare de autorizare a sursei** în specificația oficială DC-0004 (D1 în loc de H1 la pdh/pdl).
- **Specificația oficială DC-0004 NU a fost modificată.** Corecția `source_id` D1→H1 necesită aprobare separată (înregistrat în `VE_BACKLOG.md` §2.06 ca F4-1).

Aceasta este exact tipul de discrepanță pe care materializarea F4 e menită să o scoată la lumină — vizibilă doar rulând construcția populației, nu citind specificația.

---

## 11. Fișiere

**Create:** `ve/data/{__init__,sealing,integrity,access_journal,sources,calendar}.py`, `ve/population/{__init__,predicates,builder,eligibility}.py`, `ve/variables/{__init__,materialize,leakage_guard}.py`, `ve/run/materializer.py`, `tests/test_f4_materialize.py`, `tests/fixtures/dev_spec_open_window.json`, `F4_DESIGN.md`, `F4_REPORT.md`.
**Modificate:** `ve/cli.py` (+`materialize`), `VE_BACKLOG.md` (S2/S3/S4 rezolvate; F4-1 consemnat).
**Neatins, verificat prin hash:** `capabilities.json`, `SPEC_SCHEMA_v1.0.json`, modulele F2/F3, contractul, arhitectura, **cele 4 surse de date** (holdout inclus).

---

## 12. Confirmări finale

| Cerință F4 | Stare |
|---|---|
| Strat de acces la date + verificarea hash-urilor | ✅ |
| Jurnalizarea fiecărei accesări | ✅ `ACCESS_JOURNAL.json` |
| Construirea populațiilor + eligibility | ✅ n=295, familia n≥25 funcțională |
| Materializarea variabilelor și indicatorilor | ✅ fără statistici |
| Integrare în bundle/manifest F3 | ✅ |
| Fără execuția metodelor / p-values / corecții / interpretare | ✅ `methods_executed=0` |
| Fără calibrare | ✅ 15/15 `UNVALIDATED` |
| Fără acces la holdout | ✅ `max_ts < graniță`, `sealed_window_touched=False` |
| Fără modificarea definițiilor normative | ✅ registru/schema identice |
| G6 nerezolvat automat | ✅ neatins |
| Orice nepotrivire → fail-closed | ✅ hash/fereastră/anomalie |
| Rulare oprită → bundle complet | ✅ |
| Gol nou → consemnat, oprit | ✅ F4-1 |

---

**Validation Engine se oprește aici. F4 este complet; stratul de date construiește populații și variabile pe fereastra deschisă, cu holdout-ul dovedit neatins și nicio metodă executată. Aștept aprobarea CEO înainte de F5.**
