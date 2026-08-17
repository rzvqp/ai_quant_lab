# ve_tower — CHANGELOG

## 0.5.2 — corecție PROVENANCE-ONLY a valorii ATR N3 (RT-TOWER-0009)

Verdict Red Team pe 0.5.1: **TOWER_CHAIN_ATR_FAIL**. Defectul funcțional (N4) e ÎNCHIS; singurul rest: N3
`AtrProvenance.atr_value` raporta `atr14(M15)[-1]`, dar `zone_map` ratificat CONSUMĂ `atr14(M15)[i-1]` cu `i = n-1`
(`zone_map.py:185,191`). Decizia N3 era CORECTĂ; doar proveniența era greșită. Delta **exclusiv de proveniență**:

- N3 `AtrProvenance.atr_value` = ATR-ul EFECTIV consumat = `atr14(M15)[i-1]`, `i = len(M15)-1` — legat de regula
  ratificată din zone_map (NU hardcodat orb `[-2]`). Cross-check: `atr_value == N3Level.band / BAND_ATR_MULT(0.25)`.
- Adăugat în `AtrProvenance`: `evaluation_index` (i), `consumed_atr_index` (N3: i-1 · N4: n-1),
  `consumed_bar_timestamp`.
- N4 rămâne `atr14(M15)[-1]` (banda M15 1×ATR). N3 și N4 au valori ATR DIFERITE prin construcție — corect, documentat.
- **Decizia N3/N4 NESCHIMBATĂ** față de 0.5.1: `run_n3` primește tot `atr=None` (zone_map calculează intern identic),
  `run_n4` primește ACEEAȘI bandă `atr14[-1]`. Doar `atr_value`/indicii de proveniență + `chain_fingerprint`-ul derivat
  din ei se schimbă. Regresie confirmată: N3 levels + N4 confirmation identice.
- Test decisiv comis (prinde vechiul bug pe 3 fixture-uri cu ATR variabil: `atr_value == level.band/0.25`, ≠ banda N4).
  Contracte de decizie neschimbate; module vendate byte-identice; ve_brain/N1/Router/EV/N6 neatinse; 0.5.1 păstrat.
  76 teste; mypy --strict clean.

## 0.5.1 — ATR calculat INTERN în orchestrator (remediere TOWER_CHAIN_ATR)

Defect reproductibil în 0.5.0: `run_tower_chain` chema `run_n3(atr=None)` și `run_n4(atr=None)`. N4 (cu atr=None)
cade determinist pe `atr_unavailable` ⇒ lanțul nu putea produce NICIODATĂ `confirmation_available=True`, deci nu
ajungea la EV/N6 ca oportunitate aprobată. Corectat FĂRĂ a atinge modulele vendate / contractele N2/N3/N4:

- **ATR canonic INTERN**: orchestratorul calculează ATR din barele primite cu primitiva RATIFICATĂ
  `market_state.atr14` (source `a80d8a0`, period **14**, TR = `max(h-l,|h-c₋₁|,|l-c₋₁|)`). Un singur detector, cel
  ratificat — NU un al doilea, NU ATR din AI Trader.
- **Convenția de timeframe (justificată din git, raportată înainte de implementare)**: N3 ← `atr14(M15)`; N4 ← **banda
  M15 1×ATR** = `atr14(M15)[-1]`. `zone_confirmation` măsoară progresul contra benzii M15 (`zone_confirmation.py:22`
  „NU ATR M5"; `progress_reference="M15_band_1xATR"`; `market_bus.py:255,268` wire `atr=[m15_atr[-1]]*len(m5)`). A
  folosi ATR M5 pentru N4 ar schimba semantica modulului ratificat — INTERZIS. **RAPORT:** mandatul cerea „N4 ATR din
  M5"; sursa ratificată impune banda M15 — implementez ratificatul și justific din git.
- **Apelantul NU poate furniza** `atr`/`n3_atr`/`n4_atr`/atr fingerprint (nu există câmpuri; `parse_chain_request`
  respinge câmp necunoscut). ATR calculat din bare `<= as_of` (fără lookahead).
- **Fail-closed**: M15/M5 insuficiente/incomplete/neordonate/stale/NaN/Inf ⇒ `ATR_UNAVAILABLE`, nod indisponibil, reason
  explicit, zero fallback, zero `atr=0`.
- **Proveniență ATR** (`AtrProvenance`) în `ChainResponse` pentru N3 și N4 (source module/commit · function · timeframe
  · period · TR · as_of · last closed bar · source identity · atr value · availability · reason) și legată în
  `chain_fingerprint` (+ deja în `data_identity` a nodurilor prin bare). Schimbarea barelor/ATR ⇒ altă identitate.
- Contracte N2/N3/N4 NESCHIMBATE; module vendate byte-identice; ve_brain/N1/Router/EV/N6 neatinse; 0.5.0 păstrat.
  73 teste (decisivul: pe fixture valid, lanțul ajunge la N4 fără `atr_unavailable`). mypy --strict clean.

## 0.5.0 — ORCHESTRATOR de lanț `run_tower_chain` (remediere N2_CHAIN_BINDING, RT-TOWER-0007)

Verdict Red Team pe 0.4.0: **N2_HANDOFF_CONDITIONAL / N2_CHAIN_BINDING_REQUIRED**. N2 însuși e ACCEPTAT; singurul
defect: `run_n3`/`run_n4` acceptau ORICE `n2_fingerprint` de la apelant ("LONG", "", deadbeef…) — fingerprintul era
consumat, dar autenticitatea legăturii nu era impusă. Corectat FĂRĂ a atinge modulele vendate și FĂRĂ a suprascrie 0.4.0:

- **`run_tower_chain`** — orchestrator versionat ÎN artefact, SINGURA suprafață autorizată pentru live/replay/shadow.
  Rulează N2→N3→N4 INTERN și obține `n2_fingerprint`, `bias_available`, identitatea N3 EXCLUSIV din rezultatele
  funcțiilor executate în aceeași cursă. Contract `tower-chain-request-v1` / `tower-chain-response-v1`.
- **Injecția e imposibilă STRUCTURAL**: `ChainRequest` nu are câmp `n2_fingerprint`/`bias_available`/`N2Response`/
  `output_fingerprint`; `parse_chain_request` respinge orice câmp necunoscut (`UNKNOWN_REQUEST_FIELD`). Testul decisiv:
  o valoare inventată de apelant nu poate ajunge ca n2_fingerprint în run_n3.
- **`ChainResponse`**: N2/N3/N4 responses complete + `chain_fingerprint` (peste market_event_id · config fp · N2
  output_fingerprint · N3 node/event identity · N4 node/event identity · strategy_id · contract versions · artifact
  version) + `chain_status` + `terminal_reason_code`.
- **Cascadă fail-closed**: N2 indisponibil ⇒ `N2_UNAVAILABLE` (N3/N4 nu rulează); N3 indisponibil ⇒ `N3_UNAVAILABLE`;
  N4 indisponibil ⇒ `N4_UNAVAILABLE`; orice mismatch de identitate ⇒ `CHAIN_IDENTITY_MISMATCH`. Fără fallback, fără
  valori fabricate, fără default LONG.
- **`run_n2`/`run_n3`/`run_n4` = `UNBOUND_DIRECT_API`** (compat/research), INTERZISE pe calea de producție; nu sunt
  dovadă a traseului production-bound. `PRODUCTION_ENTRYPOINT="run_tower_chain"`, `TOWER_CHAIN_BINDING_VERSION=
  "tower-chain-binding-v1"` (expus în pin/manifest).
- **Contract N2/N3/N4 NESCHIMBAT** (tower-n2-request-v1 / v2). Module vendate byte-identice. ve_brain/N1/Router/EV/N6
  neatinse. 15 teste de lanț (binding, cascadă, identitate, chain_fingerprint, import-uri interzise, entrypoint unic);
  68 total.

## 0.4.0 — EXPUNE producătorul N2 (verdict B: N2_EXISTS_BUT_IS_NOT_PACKAGED)

N2 (bias direcțional H1) EXISTA ca implementare ratificată (`code/bias_h1.py` @850815f, spec
STAT-LEVEL2-BIAS-H1-SPEC-v1.0 @1b2933c + SPEC3 directional @404b6c8, manifest v2.7.61) și era deja VENDAT byte-identic
în ve_tower, dar NU era EXPUS ca producător versionat. 0.4.0 îl expune, FĂRĂ re-vendorizare și FĂRĂ rescriere semantică:

- **`run_n2`** peste `bias_h1.compute_bias` DEJA VENDAT (`_tower/bias_h1.py`, blob `1638c7dd…`, source `850815f`).
- Contract `tower-n2-request-v1` + `N2Response`: factori determiniști (`N2Factor`: structure/displacement/liquidity/
  momentum → LONG/SHORT/UNKNOWN), `availability`, reason codes, `n2_code_version` (= `SCHEMA_VERSION` citit din
  bias_h1), `data_identity`, `node_input_fingerprint`, **`output_fingerprint`** (identitatea IEȘIRII N2 pe care N3/N4 o
  primesc în locul lui bias_direction / default LONG), `market_event_id`, `event_fingerprint`, validitate/expirare.
- **Timeframe STRICT H1** (orice ≠ H1 ⇒ `invalid_timeframe`). Cascadă N1→N2 (`cascade_regime_all_axes_unavailable`).
  NaN/Inf REFUZ, sursă obligatorie, bare închise+ordonate, stale → indisponibil. `N2_UNAVAILABLE` fail-closed.
- **INTERZIS respectat**: fără default LONG (cascada ⇒ `factors=()`, `output_fingerprint=None`, NU un factor fabricat),
  fără wildcard/placeholder, fără fingerprint dintr-un string al apelantului. **N2 NU emite probabilitate**
  (`emits_probability=False` în modulul ratificat) — separat de `probability_inputs` pentru EV.
- **N3/N4 rămân v2, NEATINSE** (ve_tower 0.3.0 nu se suprascrie). AI Trader alimentează câmpul existent `n2_fingerprint`
  din N3/N4 cu `N2Response.output_fingerprint` REAL (nu "LONG"). Legarea/validarea explicită a n2_fingerprint în N3/N4
  = contract v3 viitor (schimbare de contract ⇒ handoff separat), nu inclusă aici.
- 15 teste N2 (determinism, single-OHLC→alt fingerprint, fără probabilitate, fără default LONG, timeframe strict,
  future/unordered/stale/NaN/sursă/contract refuzate, lanț N1→N2→N3→N4 cu fingerprint N2 real). 53 total.

## 0.3.0 — încărcare TRANZACȚIONALĂ (remediere TOWER_HANDOFF_CONDITIONAL)

Verdict Red Team pe 0.2.0: **TOWER_HANDOFF_CONDITIONAL** — identitatea/timeframe/substituirea/byte-integritatea sunt
ÎNCHISE, dar încărcătorul lăsa module PARȚIAL încărcate la o tentativă eșuată: coliziune la al 2-lea modul
(`market_state`) ⇒ fail-closed corect, DAR `level_output` (introdus de aceeași tentativă) rămânea în `sys.modules`.
Contractul N3/N4 rămâne **v2** (nemodificat); doar `_bootstrap` se schimbă. Corectat:

- **Încărcare tranzacțională**: `_load_sequence` urmărește EXACT modulele introduse de tentativă și, la ORICE eroare
  (coliziune la orice poziție SAU eroare în `exec_module`), le retrage pe TOATE (LIFO), restaurează exact starea
  preexistentă, lasă `_loaded=False` pentru un retry curat și RE-RIDICĂ **excepția originală** (cleanup-ul cu
  `pop(..., None)` nu aruncă ⇒ nu maschează eroarea/reason code inițial).
- **Proprietate**: ce era în `sys.modules` înainte de tentativă NU e al tower-ului — nu se șterge, nu se modifică;
  modulele host își păstrează IDENTITATEA (același obiect) înainte și după. Coliziunea nu suprascrie niciodată un modul
  străin (verificare înainte de înregistrare).
- **Teste** (`test_bootstrap.py`): coliziune la prima/a doua(cazul Red Team)/mijloc/ultima poziție · eroare în exec ·
  zero module noi după eșec · identitatea host neschimbată · retry pe încărcătorul real reușește după eliminarea
  coliziunii · import concurent determinist · excepția originală NU e mascată.

Notă de integrare (condiția a 2-a, la AI Trader): ve_tower rulează într-un PROCES + VENV SEPARAT; importul în procesul
principal e INTERZIS. Bootstrap-ul rulează deci într-un mediu curat — dar tranzacționalitatea rămâne obligatorie
(un worker care eșuează la pornire nu lasă reziduuri).

## 0.2.0 — remediere TOWER_HANDOFF_FAIL (schimbare MATERIALĂ de contract v1→v2)

Verdict Red Team pe 0.1.0: **TOWER_HANDOFF_FAIL** — N3 accepta M15/M5/orice, seturi diferite de bare puteau avea
aceeași amprentă, iar răspunsurile nu persistau identitatea datelor consumate. Corectat:

- **Timeframe STRICT la runtime**: N3 acceptă EXCLUSIV `M15`, N4 EXCLUSIV `M5`; orice altă valoare ⇒ `invalid_timeframe`
  (fail-closed). Constante `N3_EXPECTED_TIMEFRAME`/`N4_EXPECTED_TIMEFRAME`.
- **DOUĂ identități separate**: `event_fingerprint` rămâne COMUN N3/N4 (identitatea evenimentului, fără timeframe);
  ADĂUGAT per nod `data_identity` + `node_input_fingerprint`. N3 și N4 NU au același `node_input_fingerprint`.
- **data_identity** (persistată în request ȘI response): symbol · timeframe validat · source/feed identity ·
  prima bară · ultima bară închisă · bar count · as_of · **content hash canonic** al barelor · contract version
  (+ dataset/segment/manifest pentru replay/research). Fără sursă ⇒ `source_identity_missing`.
- **node_input_fingerprint** acoperă TOATE intrările care schimbă rezultatul (data identity, N1/N2 fingerprint,
  config, versiune; pentru N4 și level, side, strategy_id/version, W, și **legătura cu răspunsul N3**).
- **N4 legat EXPLICIT de răspunsul N3**: identitatea N3 (event + node fingerprint + provenanța nivelului) intră în
  `node_input_fingerprint`-ul N4; un răspuns N3 nepotrivit ⇒ `n3_link_mismatch`.
- **Hash canonic** (`canonical.py`): serializare deterministă documentată — timestamps normalizate, ordine fixă,
  reprezentare IEEE-754 exactă (nu `repr()`), **NaN/Inf REFUZ** (`non_finite_value`), tipuri distincte.
- **Byte-identitate corectată**: cele 13 module vendate sunt re-extrase DIRECT din git blob (`git cat-file blob`),
  deci **byte-identice cu blob-ul** (nu „content-identical după normalizare EOL"). `.gitattributes -text` păstrează
  asta la commit. `VENDORED_BLOB_SHA1` = identitatea verificabilă independent (`git rev-parse <commit>:code/<mod>.py`).
- **Bootstrap întărit**: lock (import concurent sigur) + cleanup complet la eroare la jumătatea încărcării
  (zero module parțial încărcate) + coliziune de nume fail-closed.

### Compatibilitate / upgrade / rollback
Contract `v2` (`tower-n3/n4-request-v2`). NON-comparabil cu `v1`. `SUPPORTED_N3/N4_CONTRACTS` listează versiunile
acceptate; o cerere `v1` pe artefactul 0.2.0 ⇒ `incompatible_contract` (fail-closed). Rollback = fixarea 0.1.0
(păstrat pentru audit); upgrade = adăugarea unei versiuni noi în mulțimile suportate.

## 0.1.0 — RESPINS (păstrat pentru audit)
Primul furnizor N3/N4. Wheel SHA-256 `e5457561604c2bd70ddca98a56b9a4c9ed8a60af95d9048237c768cef08b2db5`, contract
`v1`. Respins de Red Team (TOWER_HANDOFF_FAIL): fără timeframe strict, fără identitate de date per nod. NU se
suprascrie — rămâne în istoria git pentru audit.
