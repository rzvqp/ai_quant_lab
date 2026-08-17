# ve_n1_replay — CHANGELOG

## 0.1.1 — remediere de performanță O(n²)→O(n) (READY_FOR_N1_INCREMENTAL_REVALIDATION)

Motor N1 replay INCREMENTAL care remediază blocajul de performanță al 0.1.0 (un replay complet de 355.696 bare
era ~20+ zile din cauza `RawAxesBuilder.observe` care re-rula detect_swings/detect_breaks/expansion/compression
peste TOT istoricul crescând la fiecare bară — O(n²)+). Rezultatul per-bară rămâne **byte-identic** cu 0.1.0.

- **Orizont de dependență derivat din COD** (`N1_INCREMENTAL_HORIZON.md`), nu ghicit: axele MĂRGINITE
  (`is_compressed` ≤460 = COMPRESSION_WINDOW, `is_displacement` ≤15, `atr14` 14) vs axa NEMĂRGINITĂ
  (`structure`/`direction` = ultimul swing neconsumat, arbitrar de vechi). `HISTORY_HORIZON=460`,
  `HISTORY_HORIZON_VERSION="n1-history-horizon-v1"`.
- **`IncrementalRawAxesBuilder`** — interfață identică cu `RawAxesBuilder` (`.observe(bar)->ve_brain.RawAxes`),
  dar O(1)/mărginit amortizat: buffer rulant de 460 bare alimentează funcțiile RATIFICATE `expansion`/`compression`
  NEMODIFICATE (⇒ byte-identic pe axele mărginite); STARE INCREMENTALĂ (stive de swing-uri pe etichetă + mulțime
  consumată + `last_high`/`last_low` + ultimul break) reia EXACT `detect_swings`/`label_structure`/`detect_breaks`
  (tie-break strict D2, ordine bull-înainte-de-bear, re-armare din swing-uri neconsumate, `confirmed_idx < c`
  strict). **NU sliding window** pentru structure/direction, **NU trunchiere**.
- **`N1IncrementalReplayEngine(N1ReplayEngine)`** — schimbă DOAR `_axes_builder`; toate guard-urile, `_build_result`,
  identitatea și fingerprint-urile rămân vendate ⇒ `output_fingerprint` per-bară = 0.1.0. Snapshot/restore
  **INCREMENTAL** (mărginit): `N1IncrementalSnapshot` poartă doar starea incrementală + ultima bară + cursor +
  ultimul rezultat — restore O(HISTORY_HORIZON), NU re-rulează istoricul (dovadă: snapshot/restore < 1 ms la 355k).
- **`replay_batch`** — o SINGURĂ trecere forward O(n) ⇒ **ledger canonic** read-only (`N1IncrementalLedger`) pentru
  cele 355 de ipoteze; `ledger_key` = amprentă fail-closed peste identitatea evaluării ‖ orizont ‖ schema ledger ‖
  versiune ‖ identitatea datelor ‖ ultima bară (orice schimbare de identitate ⇒ cheie nouă ⇒ recompute).
- **Paritate DECISIVĂ** (`N1_INCREMENTAL_PARITY.md`, `tests/test_incremental.py`, 25 teste noi): byte-identic vs
  oracolul 0.1.0 pe RESULTAT (RawAxes: comp/disp/direction/structure) ȘI pe STARE INTERMEDIARĂ (swing-uri confirmate,
  etichete HH/HL/LH/LL, live_hh/ll/hl/lh, mulțimea consumată, ultimul break) la FIECARE bară; secvențe ADVERSARIALE
  (swing relevant mai vechi de 460/500 bare — paritate completă; >5000 bare — echivalență pe fereastra mărginită +
  persistența swing-ului nemărginit, fiindcă oracolul O(n²) e intractabil exact din cauza defectului remediat);
  chunk-size irelevant; restart între swing și break; zero-lookahead; două instanțe fără stare comună; invalidarea
  cheii de ledger; refuzuri fail-closed.
- **Benchmark** (`N1_INCREMENTAL_BENCHMARK.md`, `tools/benchmark_incremental.py`): până la 355.696 bare, măsurat
  wall/CPU/memory/bars-sec/scaling/ledger-size/snapshot-overhead pe serie sintetică deterministă de aceeași
  dimensiune (datele reale XAUUSD M15 sunt SIGILATE, interzise). Scalare ~liniară (O(n)); **SUB ținta de 4 ore**.
- 43 teste (18 din 0.1.0 + 25 incrementale), mypy --strict clean pe modulele proprii, empty-venv verificat, rollback
  0.1.1↔0.1.0 (versiuni coexistă, upgrade = versiune nouă, NU suprascriere). ve_brain/N1/Router/EV neatinse;
  LIVE_SHADOW neatins; niciun acces la date SEALED; Alpha NErulat. `N1_INCREMENTAL_PASS` NU e auto-declarat —
  verdictul e al Red Team.

## 0.1.0 — artefact N1 replay standalone (READY_FOR_N1_HANDOFF_REVALIDATION)

Împachetează handoff-ul N1 replay al AI Trader (`21ae632`) ca artefact INDEPENDENT, instalabil de Alpha într-un venv
separat, fără repo-ul ai_trader și fără coliziune cu ve_tower.

- **Closure git-only** (vezi `N1_REPLAY_CLOSURE.md`): 14 module `ai_trader.*` runtime @`21ae632` + 5 detectori @
  submodul `61cbd58c` (`market_structure` blob `52bb1eba…` — DIFERIT de ve_tower, NU reutilizat) + `ve_brain` 0.1.3
  (wheel extern pinuit) + numpy. Coada incompletă a AI Trader REZOLVATĂ: `market_scanner.exceptions`,
  `imbalance_mechanics`, `order_flow`, `order_block_void`.
- **Byte-identitate** verificată SEPARAT pentru modulele AI Trader (@21ae632) și detectori (@61cbd58c) — git-blob SHA1
  în `version.py`, verificabile independent (`git rev-parse <commit>:<path>`). Modulele vendate NU sunt rescrise.
- **Bootstrap izolat + tranzacțional** (`_bootstrap.py`): încarcă modulele vendate sub numele lor reale
  (`ai_trader.*`, `market_structure`, …) în ordine topologică; coliziune cu un modul STRĂIN (ex. detector ve_tower
  preîncărcat) ⇒ `N1ReplayLoadCollisionError` fail-closed cu rollback complet (zero reziduuri, excepția originală,
  retry curat, sigur la concurență) — NICIODATĂ substituție silențioasă. NU atinge module host preexistente.
- **Suprafață publică păstrată**: `N1ReplayEngine` (initialize prin constructor · `observe_closed_bar` · `replay` ·
  `snapshot` · `restore` · `reset`) + `Bar`, tipurile, erorile, `EvaluationIdentity`. Ieșire: RawAxes ·
  applicable_regimes · router verdict (eligibility_decisions) · reason_codes · availability_status · input_data_identity
  · output_fingerprint · router_output_fingerprint · regime_axes_status · last_closed_bar · router_version ·
  detector_configuration_fingerprint · evaluation_identity.
- **INTERZIS, absent prin construcție**: MT5/broker/ve_tower/ai_trader la runtime-ul consumatorului · set_authority ·
  order_send · probability_inputs · fallback legacy · clasificator alternativ.
- **Paritate DECISIVĂ**: sursă @21ae632 (import direct al modulelor vendate) vs wheel instalat ⇒ IDENTICE
  (output_fingerprint, applicable_regimes, availability, router_output_fingerprint) pe TREND_UP (→{TREND_UP}/FULL),
  UNCERTAIN (→{UNCERTAIN}/PARTIAL), BOS_BULL. Testul MT5 al celor 12 bare reale journaled cere terminal MT5 + jurnalul
  LIVE_SHADOW (NEATINS) — de aceea paritatea folosește fixture-urile oficiale (VE decision (b): constantele de bare
  copiate ca DATE, nu algoritm).
- 18 teste (byte-integritate ai+detectori, izolare/coliziune fail-closed, suprafață+refuzuri, snapshot/restore,
  determinism, acoperire de regim, zero importuri interzise), din wheel instalat, cu repo-ul ai_trader ABSENT.
  mypy --strict clean pe modulele proprii. ve_brain/N1/Router/EV neatinse; LIVE_SHADOW neatins.

Rollback: `pip install ve_n1_replay==<prev>` (nicio versiune anterioară — 0.1.0 e prima). Upgrade viitor: versiune nouă,
NU suprascriere. `N1_HANDOFF_PASS` NU e auto-declarat — verdictul e al Red Team.
