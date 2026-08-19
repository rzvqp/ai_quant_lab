# Componenta B — Runner pentru bare reale sigilate (inference / scoring separate)

Runner complet separat de componenta A (`../construction_reproduction/`), pt. rularea ULTERIOARĂ,
de către Red Team, a detectorului înghețat `f224e7d` pe barele reale sigilate — fără contaminare cu
etichetele CEO.

## Separarea obligatorie inference–scoring (mandat §4)

```
Etapa 1 (inference.py)          Etapa 2 (scoring.py)
  bare reale                      predicții deja înghețate (hash verificat)
  → detector înghețat (f224e7d)   + etichete
  → predicții brute                → metrici
  → hash + sigilare (read-only)
```

- `inference.py` **nu importă și nu poate primi** etichete CEO, mapping MACRO/INTERNAL, intervale
  de segmente, fișiere de scoring, output PnL.
- `scoring.py` **nu importă detectorul**, nu poate re-rula inference-ul, nu modifică predicțiile,
  nu recalculează limitele, nu modifică configurația, nu selectează ferestre după rezultate.
- Verificat STRUCTURAL, nu doar convențional — `tests/test_anti_leakage_ast.py` parsează sursa cu
  `ast` și verifică direct seturile de importuri + apelurile de funcții, pentru ambele module și
  pentru orice alt fișier din acest pachet.

## Schema input (derivată din API-ul real, v. `schemas.py`)

Bară (identică tipului real `ai_trader.live_signal_source.types.Bar`, consumat de
`RangeSemanticEngineV43.observe_closed_bar`/`replay_batch`):

```json
{"ts_open": 0, "ts_close": 900, "open": 100.0, "high": 100.5, "low": 99.5, "close": 100.2,
 "volume": null, "is_backfilled": false}
```

Fereastră: `{"window_id": "<opac, atribuit de Red Team>", "symbol": "...", "timeframe": "...",
"bar_interval_seconds": 900, "bars": [...]}`. Input complet: `{"windows": [...]}`.

Validare fail-closed (cod distinct per defect, v. `schemas.py`): câmp lipsă, timestamp lipsă, OHLC
lipsă/non-finit, `high<low`, open/close în afara `[low,high]`, ordine temporală greșită, bară
duplicată, timeframe invalid, fereastră goală, ID de fereastră duplicat, fișier corupt, date
parțiale.

## Schema output (`predictions.json`)

`prototype_commit`, `contract_version`, `config_id`, `code_fingerprint` (SHA-256 per fișier),
`config_fingerprint`, `input_bytes_hash`, `normalized_bars_hash`, per fereastră: `window_id`,
`records[]` (index RELATIV de bară, stare MACRO/INTERNAL, limite, `confirm_ts` relativ, rol,
evenimente cu `applies_to_structure_id`+reason codes), `macro_structures[]`/`internal_structures[]`
(inclusiv structura încă deschisă la finalul ferestrei — găsit+corectat, v. nota din `inference.py`).
**Fără** timestamp-uri calendaristice reale, căi locale, secrete, etichete CEO — verificat direct
(`tests/test_inference.py::test_zero_real_calendar_timestamp_in_output`).

## Sigilarea predicțiilor

`predictions.json` + `predictions.manifest.json` + `predictions.sha256`. După emitere,
`predictions.json` devine read-only (best-effort cross-platform); `scoring.py` refuză fail-closed
orice fișier al cărui hash nu se potrivește (`ScoringRefusedError(code="TAMPER_DETECTED")`) —
verificat direct: un singur bit modificat blochează scorarea
(`tests/test_tamper_and_determinism.py::test_one_bit_prediction_change_blocks_scorer`).

## Rulare

```bash
cd ve_n1_replay
python blind_runner/inference.py --input <bare.json> --output-dir <dir_predictii>
python blind_runner/scoring.py --predictions-dir <dir_predictii> --labels <etichete.json> --out scorecard.json
```

## Fixture-uri de dezvoltare

`dev_fixtures.py` — bare sintetice MECANICE (zigzag simplu, determinist), FĂRĂ nicio legătură cu
etichetele CEO sau cu cele 48 de ferestre din componenta A (deliberat izolat, ca să nu existe nicio
cale de scurgere între componente nici măcar în teste de dezvoltare). Nu reprezintă bare reale.
Folosite EXCLUSIV pt. a exercita instalația inference/scoring (I/O, hashing, validare, scorare) —
niciun rezultat calculat pe ele nu poartă vreo greutate de acuratețe.

## Ce NU e aici / nu se comite

Nicio bară OHLC reală, niciun timestamp real de fereastră, niciun secret, nicio cheie de escrow,
nicio dată SEALED/OOS.
