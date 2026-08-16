# ve_tower — CHANGELOG

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
