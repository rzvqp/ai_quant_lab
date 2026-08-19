# Componenta A — Reproducerea istorică sintetică

```text
CEO_ASSISTED_SYNTHETIC_CONSTRUCTION_ONLY
CIRCULAR_LABEL_DERIVED_BARS
ZERO_VALIDATION_WEIGHT
```

Comite exact logica folosită pentru rularea de construcție deja raportată în
`../RANGE_V4_3_REAL_PROTOTYPE_DELIVERY_REPORT.md` (prototip înghețat `f224e7d`) — răspuns direct la
Red Team RT-RANGE-0007 §16 (`RANGE_V4_3_CONSTRUCTION_RESULT_NOT_REPRODUCED`: scripturile trăiau doar
local, necomise, deci cifrele VE nu puteau fi verificate independent).

**Scopul acestei componente e EXCLUSIV să reproducă cifrele VE deja raportate — NU să valideze
detectorul.** Barele sunt sintetizate MECANIC din aceleași etichete cu care sunt apoi comparate
(`fixtures/`, copii comise ale etichetelor deja publicate pe `statistician-foundation` — v.
`fixtures/FIXTURE_PROVENANCE.md`). Comparația e circulară prin construcție. Rezultatul NU e și nu
poate fi un BLIND PASS.

## Rulare

```bash
cd ve_n1_replay
python construction_reproduction/run_construction.py
python -m pytest construction_reproduction/tests/ -v
```

Scrie și comite `construction_run_results.json` (mandat §12: rezultatul sintetic reprodus e un
artefact obligatoriu) — deși e complet DERIVABIL determinist din codul + fixture-urile deja comise
(regenerabil oricând identic, v. `test_deterministic_rerun_byte_identical`), e comis explicit ca
dovadă directă a reproducerii, nu doar afirmată. Emite
`HISTORICAL_SYNTHETIC_RESULT_REPRODUCED`/`ZERO_VALIDATION_WEIGHT` sau
`HISTORICAL_SYNTHETIC_RESULT_NOT_REPRODUCED` (cu lista de nepotriviri).

## Fail-closed pe identitate

`run_construction.py` verifică, ÎNAINTE de a importa detectorul, că `range_semantic_v4_3.py`/
`range_engine_v4_3.py` sunt byte-identice cu fingerprint-urile citate în `f224e7d`, și că
`ConfigV43().config_id()` e cel înghețat. Dacă detectorul a fost modificat de atunci, scriptul
REFUZĂ să ruleze — nu produce tăcut numere dintr-un cod diferit.

## Ce NU e aici

Nicio bară OHLC reală. Barele reale ale celor 48 de ferestre rămân în escrow, în afara oricărui
checkout Git — verificat separat, documentat în
`../RANGE_V4_3_CONSTRUCTION_REPORT.md` §0. Comparația reală (detector pe bare reale, cu etichete
CEO folosite doar la scorare, niciodată la generarea barelor) e componenta B
(`../blind_runner/`), pentru rularea ulterioară, separată, autorizată de Red Team.
