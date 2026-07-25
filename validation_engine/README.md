# VALIDATION ENGINE
### Componenta executivă a validării statistice din AI Quant Lab

Validation Engine (VE) **execută** protocoale statistice specificate de Statistician; nu proiectează, nu interpretează și nu emite verdicte. Separarea proiectare/execuție este fixată în contractul oficial (vezi mai jos).

> **Principiu de bază:** motorul se **oprește corect** înainte să calculeze ceva. Validarea fail-closed, protecția holdout-ului și auditul preced orice capacitate de calcul.

---

## Starea curentă

| Element | Stare |
|---|---|
| Registru de capabilități | **v1.4** — `PUBLISHED_NOT_EXECUTABLE` |
| Metode `VALIDATED` (executabile oficial) | **0 / 15** — toate `UNVALIDATED` |
| Schema specificației | `SPEC_SCHEMA_v1.0.json` (neschimbată din F1) |
| Faze livrate | F2 (validator) · F3 (audit) · F4 (date+populație) · F5 (`matched_null@v1`) |
| Fază curentă | **F5 închis** — următoarea: F6 (calibrare/validare metode) |
| Holdout | **NEATINS** (graniță `2025-10-23T09:15:00Z`); toate rulările pe fereastra deschisă |
| Teste | 400 passed |

Pipeline: `Alpha → Discovery Candidates → Red Team → STATISTICIAN → [Validation Engine] → Knowledge Base → AI Trader`. VE este un instrument subordonat Statisticianului, nu o etapă de pipeline.

---

## Documente oficiale

### Guvernanță și interfețe
| Document | Rol |
|---|---|
| `../statistician/STATISTICIAN_VALIDATION_ENGINE_CONTRACT_v1.0.md` | contractul proiectare↔execuție (autoritate) |
| `VALIDATION_ENGINE_ARCHITECTURE_v1.0.md` | arhitectura: ce intră/iese, comunicarea, responsabilități, ce nu face |
| `VE_BACKLOG.md` | registrul append-only al abaterilor (A1–A7), golurilor (G1–G8, F4-x), punctelor deschise |

### Vocabular și format de specificație
| Document | Rol |
|---|---|
| `capabilities.json` | forma normativă a registrului (sursa unică de adevăr) |
| `CAPABILITY_REGISTRY_v1.4.md` | catalogul citibil (v1.0–v1.3 păstrate ca istoric) |
| `SPEC_SCHEMA_v1.0.json` / `.md` | schema și explicația formatului de specificație |
| `SPEC_TEMPLATE_v1.4.json` | șablon de copiat |

### Rapoarte de fază (design → raport → închidere)
| Fază | Documente |
|---|---|
| F2 — validator + taxonomie erori | `F2_REPORT.md`, `F2_1_REPORT.md` (G1/G2), `F2_2_REPORT.md` (G3/G4/G5), `F2_3_REPORT.md` (G7), `F2_4_REPORT.md` (G8), `F2_CLOSURE.md` |
| F3 — infrastructură de audit | `F3_DESIGN.md`, `F3_REPORT.md` |
| F4 — strat de date + populație | `F4_DESIGN.md`, `F4_REPORT.md`, `F4_1_DC0004_FIX_REPORT.md`, `F4_2_DC0004_CELLFIX_REPORT.md`, `F4_CLOSURE.md` |
| F5 — `matched_null@v1` | `F5_DESIGN.md`, `F5_REPORT.md` |

### Analize și reconcilieri
| Document | Rol |
|---|---|
| `REGISTRY_GAPS_G1_G2_ANALYSIS.md`, `REGISTRY_GAPS_G3_G4_G5_ANALYSIS.md`, `REGISTRY_GAP_G8_DESIGN.md` | designul rezolvării golurilor de vocabular |
| `RECONCILIATION_DEFINITIONS_v1.0.md` | reconcilierea definițiilor Alpha vs. Statistician (a dus la Calea A pentru DC-0004) |
| `SCRIPT_VERIFICATION_Q1_Q3.md`, `CLARIFICATION_TO_STATISTICIAN_Q1_Q3.md` | verificarea împotriva scripturilor Alpha; întrebările Q1–Q3 |

---

## Cod (`ve/`)

```
ve/
  cli.py            validate | run | materialize | verify | capabilities
  spec/             loader, schema_validator (etapa 1), registry_validator (etapa 2), domains
  errors.py         taxonomia E1–E9
  clarification.py  cererea de clarificare (4 câmpuri, zero recomandări)
  audit/            access_audit (gardă PEP 578), checksums, ledger, repo_integrity
  manifest/         environment, code_snapshot
  rng/              streams (semințe derivate determinist)
  data/             sealing, integrity, access_journal, sources (loader streaming), calendar
  population/       predicates, builder (denominator per criteriu), eligibility
  variables/        materialize, leakage_guard
  methods/          matched_null@v1
  calibration/      reproduce_obs0012 (NON-OFFICIAL)
  run/              runner (audit F3), materializer (F4), matched_null_official, f5_run
  verify/           replay (re-verificarea unui bundle)
```

## Rulare (dezvoltare)

```bash
# din validation_engine/, cu venv-ul laboratorului:
../venv/Scripts/python.exe -m pytest tests -q          # 400 teste
../venv/Scripts/python.exe -m ve capabilities          # sumarul registrului
../venv/Scripts/python.exe -m ve validate <spec.json>  # validare fail-closed
```

**Testarea folosește exclusiv fereastra deschisă.** Holdout-ul (post `2025-10-23T09:15:00Z`) rămâne sigilat pentru F8.

---

## Reguli permanente

- Toate metodele rămân `UNVALIDATED` până la calibrarea sintetică (F6).
- Registrul rămâne `PUBLISHED_NOT_EXECUTABLE` până la promovarea unei metode.
- Schema JSON nu se modifică pentru extinderi de vocabular (invariant din F1).
- Holdout-ul nu se atinge înainte de F8; orice fereastră care îl atinge se oprește fail-closed.
- Fiecare gol/contradicție nou descoperit se consemnează în `VE_BACKLOG.md` și se oprește pentru decizie — nu se rezolvă automat.
