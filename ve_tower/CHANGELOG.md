# ve_tower — CHANGELOG

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
