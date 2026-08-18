# ve_n1_replay — CHANGELOG

## 0.3.1 — PIN de configurație V2: `w_atr=0,30` RATIFICAT, `s_max` DERIVAT structural (READY_FOR_RANGE_V2_BLIND_REVALIDATION)

**Modificare CHIRURGICALĂ, nu un patch semantic.** Statistician a rulat protocolul pre-înregistrat (`STAT-RANGE-V2-
PREREG-PROTOCOL-v1.0` @`4e69e22`, comis ÎNAINTE de orice atingere a datelor) și a fixat configurația finală
(`STAT-RANGE-V2-WATR-FINAL-v1.0` @`c29ac98`, manifest v2.7.81 @`2611d22`, fingerprint `432170ff…` verificat exact):
`w_atr = 0,30` (înlocuiește implicitul NERATIFICAT `0,25` al 0.3.0) și `s_max = 2 × w_atr = 0,60`, DERIVAT structural,
niciodată un parametru liber. Controlul de construcție `RC-CONSTRUCTION-CHANNEL-NEW-01` (S=3,3781, CHANNEL_UP)
respinge canalul ca range la un factor >2 peste orice `s_max` admisibil — pragul e o consecință a intervalului deja
publicat, nu o alegere. **0.3.0 rămâne NEMODIFICAT** (verificat: `git diff` gol), păstrat pentru audit.

- **`RangeConfigV2Pinned`** (nou, `range_state_v2_1.py`): `w_atr` e SINGURUL grad de libertate pe zonă (implicit
  `0,30`, suprascriptibil în teste controlate); `s_max`/`derived_s_max` sunt `@property` calculate ca `2 × w_atr` —
  NU există câmp `s_max` stocat sau setabil. Constructorul REFUZĂ `s_max` structural (`TypeError` — parametrul nu
  există). `from_dict()` (parserul) refuză explicit un câmp `s_max` primit din exterior, ridicând
  `LegacyConfigRejectedError(reason_code=LEGACY_S_MAX_REJECTED)` — UNICUL cod de motiv nou (restul rămân
  byte-identice cu 0.3.0). `provenance()` expune formula de derivare explicit, nu doar valoarea rezultată.
  `range_spec_id`/`config_hash`/`run_hash` recalculate (includ `w_atr` + regula de derivare + versiunea de
  producător `range-producer-0.3.1`) ⇒ rezultatele 0.3.0 devin automat NON-COMPARABILE PRIN TIP.
- **Gard structural/AST**: `0,15` (implicitul NERATIFICAT vechi) nu mai apare ca literal numeric NICĂIERI în
  `range_state_v2_1.py`/`range_engine_v2_1.py` — verificat prin scanare `ast` directă a fișierelor sursă de
  producție (nu doar prin testare comportamentală).
- **Reutilizare, NU reimplementare**: `RangeStateReplayEngineV2Pinned` (`range_engine_v2_1.py`) compune
  `N1IncrementalReplayEngine` (0.1.1, NEATINS, importat) + `RangeStateProducerV2` (0.3.0, NEATINS, importat) —
  `RangeConfigV2Pinned._to_runtime_config()` traduce configurația pin-uită într-un `RangeConfigV2` (0.3.0) real
  ÎNAINTE de a alimenta clasa neschimbată. Mediana-ancoră, atingerea pe interval, atingerea prin fitil, acumularea
  cauzală, BOS/CHoCH intern, mașina de stări, cele 11 evenimente, F7 `RANGE_MID_NO_ENTRY`, separarea structurală
  range/canal, zero-lookahead — TOATE rulează EXACT codul 0.3.0, dovedit structural (`isinstance(eng._range,
  RangeStateProducerV2)`), nu doar comportamental.
- **Snapshot/identitate**: `range-state-snapshot-v2-pinned` (nou) — restore REFUZĂ fail-closed orice snapshot 0.2.0
  SAU 0.3.0 (incl. configurații legacy cu `s_max=0,15` explicit testat), niciodată o migrare implicită.
- **40 teste noi** (22 cazuri din mandat + 2 gard-uri AST + regresie structurală explicită 0.3.0→0.3.1),
  **162 teste total** (18+25+34+45+40), mypy `--strict` clean, empty-venv + rollback 0.3.1→0.3.0→0.1.1 verificate.
  Benchmark comparativ SCURT 0.3.0 vs 0.3.1 (nu rulare completă 355.696 — mandat: delta de configurație, același
  cod O(n) reutilizat neschimbat, deja dovedit la 0.3.0).
- `n_generated_total=363`/`m_inference=26`/tombstones/registrul Alpha/F1-F6 și cele 44
  `BLOCKED_PENDING_RANGE_SEMANTIC_FIX`/F7 `SAFETY_GUARD` NEATINSE. Fără SEALED/OOS, fără RC-07/RC-08, fără
  `range1.pdf`/`range2.pdf`. `RANGE_V2_BLIND_REVALIDATION` NU e auto-declarat — Red Team primește EXCLUSIV 0.3.1.

## 0.3.0 — RANGE_STATE SPEC V2: remediu SEMANTIC_SPEC_DEFECT (READY_FOR_RANGE_SEMANTIC_REVALIDATION)

**Contract NOU, NU un patch peste 0.2.0.** Statistician a diagnosticat 0.2.0 (`STAT-RANGE-SEMANTIC-DIAGNOSIS-V2-v1.0
@3aac2cc`, manifest v2.7.78 @18aa2a1) ca `SEMANTIC_SPEC_DEFECT`: limita = extremul unei mulțimi CRESCĂTOARE de
swing-uri confirmate ⇒ a atinge durata minimă forța fereastra să crească ⇒ creșterea ridica limita ⇒ ridicarea
limitei invalida RETROACTIV atingerile numărate contra limitei vechi — o definiție NESATISFIABILĂ, nu o eroare de
implementare (RT a dat PASS pe 0.2.0; Alpha a reprodus identic de 2 ori/3 ere). **0.2.0 rămâne NEMODIFICAT** (verificat:
`git diff` gol), păstrat pentru audit.

- **Schimbarea centrală**: `anchor` = MEDIANA extremelor swing-urilor confirmate pe o fereastră mărginită (NU maxim ⇒
  NU monotonă în lungimea ferestrei ⇒ nu se auto-invalidează); `boundary_zone=[anchor-w, anchor+w]` (ZONĂ, nu linie);
  `touch` = orice bară al cărei interval `[low,high]` intersectează zona LA MOMENTUL ACELEI BARE, acumulat ca un
  CONTOR MONOTON — niciodată re-scanat retroactiv contra unei zone ulterioare. **Dovedit direct vs 0.2.0** pe
  ACEEAȘI secvență adversarială: 0.2.0 pierde `touches_upper` 8→1 și nu mai reajunge CONFIRMED; 0.3.0 păstrează
  CONFIRMED și touches cresc monoton prin exact același eveniment.
- **BOS/CHoCH intern** NU invalidează — descriptor (`structure_events_inside`), reutilizează `IncrementalRawAxesBuilder`
  (0.1.1) ca instanță internă izolată, nicio reimplementare de detectori.
- **Separare range/canal**: `|slope|×d_min <= s_max×ATR` (formula EXACTĂ din spec — `d_min`, constanta FIXĂ, nu
  lungimea episodului, care ar fi crescut deriva nemărginit cu vârsta episodului — bug prins și corectat în timpul
  livrării). Panta = OLS pe fereastră trailing MĂRGINITĂ de `d_min_bars` close-uri (nu tot episodul — mai puțin
  zgomotoasă, coerentă cu `d_min` din formula de derivă, `O(d_min_bars)`/bară, NU O(n)).
- **Două clase de durată**: `RangeConfigV2.intraday()` (d_min=24) / `.multiday()` (d_min=96) — ipoteze SEPARATE dacă
  testate separat.
- **11 evenimente** (`range-events-v2`): RANGE_FORMING/ESTABLISHED/HIGH/LOW/MID, BREAKOUT_CANDIDATE,
  BREAKOUT_ACCEPTED_LONG/SHORT, BREAKOUT_RETEST, BREAKOUT_FAILED, LIQUIDITY_SWEEP. ACCEPTED_LONG/SHORT/FAILED mutual
  exclusive prin construcția mașinii; SWEEP structural disjunct — zero coliziuni pe aceeași bară (verificat).
- **F7 `RANGE_MID_NO_ENTRY` = SAFETY_GUARD** neschimbat semantic (amendament final @d0d08c1): refuz executabil,
  `n_guards` separat, auditabil, supraviețuiește snapshot/restart.
- **N1 (0.1.1) byte-identic** — motorul N1 neatins; `output_fingerprint` per-bară verificat identic cu o instanță
  `N1IncrementalReplayEngine` goală pe 4 fixture-uri. `pkg_n1_contract_version`/`pkg_raw_axis_schema_version`/
  `pkg_router_version` (declarate de pachet) rămân IDENTICE cu 0.2.0 (verificat).
- **9 versiuni de contract** publicate explicit (artifact/range-state-contract/schema/producer/event-contract/
  state-machine/snapshot-schema/ledger-schema/reason-codes) + identitatea N1-baseline + identitatea predecesorului
  0.2.0 (wheel SHA/build/delivery/RT-PASS commits) + sursa Statistician (3aac2cc/18aa2a1). Snapshot 0.2.0 restaurat
  într-un motor V2 (și invers) e REFUZAT fail-closed — nicio migrare implicită.
- **Ambiguitate declarată**: `w_atr`/`s_max` sunt „PRE-ÎNREGISTRATĂ" în spec dar FĂRĂ valoare numerică literală
  (verificat, absentă din document și manifest) — expuse ca parametri configurabili, valori implicite PROPUSE DE VE
  PE TEMEI STRUCTURAL, NERATIFICATE. Nicio dată reală de piață NU a fost încărcată pentru a le calibra (interzis
  explicit de mandat) — validarea empirică P1-P3 pe corpusul real rămâne sarcina Red Team pe subsetul BLIND.
- **45 teste noi** (28 cazuri din mandat + regresie directă vs 0.2.0 + reachability toate cele 11 evenimente +
  clasificare range/canal izolată de zgomotul motorului complet), **122 teste total** (18+25+34+45), mypy --strict
  clean, empty-venv + rollback 0.3.0→0.2.0→0.1.1 verificate. Benchmark incremental (fără regresie O(n²), până la
  355.696 bare). `RANGE_STATE_HANDOFF_PASS` NU e auto-declarat pentru V2 — verdictul e al Red Team (validare
  semantică BLIND pe RC-06/07/08, pe care VE nu le-a văzut).

## 0.2.0 — producător ADITIV RANGE_STATE + evenimente longitudinale (READY_FOR_RANGE_STATE_HANDOFF_REVALIDATION)

Adaugă un producător versionat pentru **RANGE_STATE** și **evenimente longitudinale de range/breakout**, conform
specului reconciliat final al Statisticianului **STAT-RANGE-RECONCILED-SPEC-v1.0 @`aca7801`** + amendamentul
**`m_inference` FINAL @`d0d08c1`** (manifest v2.7.77, hash `aec8f07`), pe baza reachability-ului **RT-RANGE-0001
@`5e56396`**. RANGE_STATE e un STRAT NOU, separat.

- **N1 NEATINS, byte-identic cu 0.1.1**: motorul incremental N1 nu se modifică; `RangeStateReplayEngine` îl COMPUNE și
  produce RANGE_STATE pe deasupra. `output_fingerprint` per-bară == 0.1.1 (testat). NU reutilizează/reinterpretează
  `StructBand.RANGE`, NU trece prin `applicable_regimes` (care nu poate produce RANGE — dovadă RT static + empiric:
  BREAKOUT_TRANSITION pe 0/355.696 bare), NU atinge ve_brain/N3/N4/EV/N6.
- **Șapte bump-uri de contract** (la nivel de PACHET, în identitatea RANGE; identitatea per-bară N1 rămâne neschimbată):
  `n1_contract_version`→`n1-replay-request-v2`, `raw_axis_schema_version`→`raw-axis-schema-v2`,
  `router_version`→`router-v2`, `range_state_contract_version`=`range-state-v1`,
  `range_event_contract_version`=`range-events-v1`, `snapshot_schema_version`=`range-state-snapshot-v1`,
  `ledger_schema_version`=`range-state-ledger-v1`.
- **Producător RANGE_STATE (`range_state.py`)**: stare INCREMENTALĂ (nu recalcul pe fereastră) — limite upper/lower din
  swing-uri CONFIRMATE (fractali strict D2, byte-identic cu `detect_swings`), `boundary_validity`
  PROVISIONAL/CONFIRMED/EXTENDED/VIOLATED, `data_readiness` WARMUP/READY/DEGRADED (fail-closed),
  `consolidation_state` NONE/FORMING/ESTABLISHED/DECAYING, `structural_start_ts` (retrospectiv) vs
  `actionable_start_ts=confirm_ts` (>= structural + k bare), ER=|Δclose_net|/Σ|Δclose|, width=(H-L)/ATR,
  RANGE_MID explicit, invalidare doar pe dovezi (ACCEPTED_BREAK/MAX_DURATION/INPUT_UNAVAILABLE, niciodată retroactiv),
  reason codes, `range_spec_id` (sha256 peste definiția ordonată) + `run_hash`=sha256(config_hash‖data_identity‖spec_id).
  Zero lookahead.
- **Mașină de stări longitudinală (`range-events-v1`)**: 8 evenimente (LOW/HIGH_REJECTION, MID, BREAKOUT_CANDIDATE,
  BREAKOUT_ACCEPTED, BREAKOUT_RETEST, FAILED_BREAKOUT, LIQUIDITY_SWEEP_REVERSAL). BREAKOUT_ACCEPTED și FAILED_BREAKOUT
  sunt tranziții MUTUAL EXCLUSIVE prin mașină (nu prin filtrare) ⇒ populații disjuncte (repară PRDS). SWEEP reutilizează
  semnătura D6 (wick dincolo + close înăuntru, aceeași bară). Fără trendline breakout (nicio primitivă canonică).
- **Precedență**: `TREND_PAUSE ⊆ RANGE_STATE`, `RANGE_STATE_OVER_TREND_PAUSE` (în `range_spec_id`); direcția N1 devine
  atributul `trend_context` păstrat. Ledger cu MATRICE DE OCUPANȚĂ.
- **F7 `RANGE_MID_NO_ENTRY` = SAFETY_GUARD** (amendament final): NU strategie, NU ipoteză, NU produce p-value/MDE/prag
  (`m_inference`=26). REFUZ EXECUTABIL: RANGE_MID emis explicit cu `safety_guard`, `entry_decision` întoarce refuz (zero
  entry/candidate/p-value/broker), contorizat separat `n_guards` în registrul `SAFETY_GUARDS`, prezent în audit —
  niciodată dedus din absență; supraviețuiește snapshot/restart.
- **Snapshot/restore RANGE combinat, mărginit** (`range-state-snapshot-v1`): snapshot N1 incremental + starea RANGE
  (limite/swing-uri/stare/tranziții/candidat/invalidare/confirm_ts/reason codes/identitate), restaurare bit-identică;
  fail-closed la nepotrivire de identitate/versiune/`range_spec_id`.
- **77 teste** (18 N1 + 25 incremental + 34 range: N1 byte-identic, paritate stream swing vs `detect_swings`, actionable
  numai după confirm_ts, warmup≠range, F7 SAFETY_GUARD, toate cele 8 evenimente reachable, accepted XOR failed, retest,
  sweep, invalidare, zero-lookahead, chunk invariance, snapshot/restart în FIECARE stare, două instanțe, run_hash,
  fără MT5/broker/order_send/set_authority/probability_inputs). mypy --strict clean; empty-venv + rollback 0.1.1↔0.2.0
  verificate. Benchmark incremental (RANGE, până la 355.696 bare, sub 4h, ~O(n)). `RANGE_STATE_HANDOFF_PASS` NU e
  auto-declarat — verdictul e al Red Team.

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
