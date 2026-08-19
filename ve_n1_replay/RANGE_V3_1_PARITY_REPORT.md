# RANGE V3.1 (0.4.1) — Raport de paritate decizională 0.4.0 ↔ 0.4.1

**Mandat §5**: comparație obligatorie 0.4.0 vs 0.4.1 pe aceleași intrări. Trebuie identice: stări; evenimente;
segment IDs; limitele range-ului; timestamp-uri de confirmare; reason codes; tranziții; verdicte sweep/breakout;
istoricul terminat; continuarea snapshot→restore; traseul HBL-20; toate ieșirile economice/semantice. Dacă
valoarea internă floating-point a pantei diferă doar din ordinea operațiilor: măsoară diferența; dovedește că
nu schimbă nicio clasificare; testează explicit valorile aflate imediat sub, la și imediat peste prag.

## 0. Ce s-a schimbat, ce nu

Singura schimbare e **modul de calcul al pantei** (`_Segment.slope()` → `_SegmentV31.slope()`): batch O(`d_min_bars`)
(reparcurgere completă a cozii `closes` la fiecare bară) → incremental O(1) (statistici suficiente `Sy`/`Sxy`
actualizate la fiecare `push_close`, `Sx`/`Sxx` în formă închisă din mărimea ferestrei). Aceeași definiție
matematică OLS, aceeași fereastră semantică (`d_min_bars`, neschimbată). Nimic altceva — stările, evenimentele,
segmentarea longitudinală, ancora, K/N, `ZONES_DEGENERATE`, `TOO_SHORT`, F7 — sunt REFOLOSITE prin import/
subclasare, nu reimplementate (vezi `range_semantic_v3_1.py`, header-ul modulului).

## 1. Paritate decizională completă — fixture oscilație (40 cicluri, 320 bare)

`tests/test_range_semantic_v3_1.py::test_full_decision_parity_0_4_0_vs_0_4_1_oscillation_fixture`

Fingerprint decizional per bară (`available, reason, segment_id, predecessor_id, transition_reason, lifecycle,
structural_start_ts, confirm_ts, bars_in_segment, anchor_lower, anchor_upper, range_mid, w, touches_upper,
touches_lower, pending_event, confirmed_event, reason_codes, events[].(kind,boundary,reason_codes)`) comparat
bară-cu-bară între `RangeSemanticEngineV3` și `RangeSemanticEngineV31`, configurație identică (`K=3,N=6,
w_atr=0.35,d_min_bars=20,n_touch=2,swing_k=2`):

- **0/320 bare cu mismatch pe fingerprint-ul decizional.**
- **Panta**: diferență absolută maximă măsurată = **0,0 exact** (nu doar sub toleranță) pe acest fixture —
  ordinea operațiilor (formă închisă `Sx`/`Sxx` + acumulare `Sy`/`Sxy`) coincide numeric cu batch-ul pe
  secvențele testate, nu doar decizional.
- **Istoricul segmentelor terminate** (`segment_id, predecessor_id, end_reason, structural_start_ts, confirm_ts,
  end_ts, bars_in_segment, anchor_lower, anchor_upper, reached_established`): identic, 12/12 segmente.

## 2. Traseul HBL-20 — reproducere numerică exactă, ambele versiuni

`tests/test_range_semantic_v3_1.py::test_full_decision_parity_0_4_0_vs_0_4_1_hbl20_trace`

Fixture sintetic construit din verificarea proprie deja publicată a Statisticianului (ancoră 3346,10/3333,06,
breach bara 52, sweep bara 56, markup bara 63), rulat bară-cu-bară prin `RangeSemanticProducerV3` ȘI
`RangeSemanticProducerV31` în paralel (`K=5,N=5,w_atr=0.02,d_min_bars=96`):

- **Log complet identic** (`lifecycle, segment_id, confirm_ts, reason_codes, events[].kind` la fiecare din cele
  71 de bare) — 0.4.0 == 0.4.1, bară cu bară.
- Sweep confirmat **EXACT la bara 56** în ambele versiuni (niciodată la bara 52 — breach-ul rămâne ambiguu
  până la reintrare, exact ca-n 0.4.0).
- Niciun breakout confirmat la/înainte de bara 63 (markup-ul singur nu poate confirma breakout — necesită N
  închideri consecutive) — identic în ambele.

## 3. Prag exact IS_CHANNEL — sub / la / peste

`tests/test_range_semantic_v3_1.py::test_channel_threshold_below_at_above_decision_parity_0_4_0_vs_0_4_1`

Pantă construită analitic ca `drift = |slope|*d_min_bars` să cadă imediat SUB, EXACT LA, și imediat PESTE
pragul `s_max*atr` (`d_min_bars=20, w_atr=0.35, atr=1.0` ⇒ `s_max*atr=0.70`):

| poziție | drift 0.4.0 | drift 0.4.1 | Δ drift | IS_CHANNEL 0.4.0 | IS_CHANNEL 0.4.1 |
|---|---|---|---|---|---|
| sub prag | calculat | calculat | < 1e-9 | egal | egal |
| exact la prag | calculat | calculat | < 1e-9 | egal | egal |
| peste prag | calculat | calculat | < 1e-9 | egal | egal |

Clasificarea `IS_CHANNEL` (`>` strict, conform 0.4.0) e **identică în toate cele trei poziții** — nicio
reclasificare cauzată de ordinea operațiilor flotante la pragul cel mai sensibil din spec.

## 4. Fingerprint de configurație — DELIBERAT diferit (nu o eroare de paritate)

`tests/test_range_semantic_v3_1.py::test_config_fingerprint_ties_to_new_implementation_identity`

`RangeConfigV31.range_spec_id()` != `RangeConfigV3.range_spec_id()` pentru parametri K/N/w_atr/d_min_bars
IDENTICI — prin construcție (`producer_version=RANGE_PRODUCER_VERSION_V3_1` în hash, în loc de
`RANGE_PRODUCER_VERSION_V3`). Mandatul §5 cere explicit legarea noii implementări de fingerprint-ul de
artifact/versiune — acesta e exact mecanismul, verificat direct.

## 5. Snapshot/restore — continuare identică, refuz fail-closed corect

- `test_snapshot_restart_before_window_fill` / `test_snapshot_restart_after_window_fill`: continuare
  identică (fingerprint + pantă) fie că restore-ul are loc ÎNAINTE, fie DUPĂ ce fereastra `closes` s-a
  umplut prima dată — cele două faze ale statisticilor incrementale (creștere vs. evict+append) au fost
  testate separat.
- `test_snapshot_restart_bit_identical` (5 combinații de chunk-uri): identic cu rularea neîntreruptă.
- `test_legacy_0_4_0_snapshot_refused`: un snapshot 0.4.0 (`RangeSnapshotV3`) e refuzat fail-closed de motorul
  0.4.1 — structura internă a segmentului s-a schimbat (câmpurile de statistici suficiente nu au corespondent
  în starea 0.4.0), motorul rămâne NESCHIMBAT la refuz (verificat).
- `test_legacy_0_2_0_0_3_0_0_3_1_snapshots_still_refused`: lista de refuz moștenită (0.2.0/0.3.0/0.3.1) rămâne
  validă prin 0.4.1.

## 5b. Găsit ȘI CORECTAT — `d_min_bars=0` (amendament CEO, hardening input-validation)

Verificare directă (nu doar raționament): `RangeConfigV3.__post_init__` (0.4.0, moștenit de `RangeConfigV31`)
validează `K>0, N>0, w_atr>0` dar NU validează `d_min_bars>0` — un gol PREEXISTENT, nu introdus de remedierea
§12. La `d_min_bars=0` (o configurație fără sens semantic — o fereastră de 0 bare):

- **0.4.0**: `deque(maxlen=0)` rămâne perpetuu goală; `slope()` vede `n=0<2` și întoarce `0.0` silențios.
- **0.4.1 (înainte de amendament)**: `push_close()` verifica `len(closes)==maxlen` (`0==0`, mereu adevărat)
  ÎNAINTE de append și indexa `closes[0]` pe o coadă goală → **`IndexError`** necontractual.

Confirmat inițial prin execuție directă, raportat transparent (nu livrat cu defectul deschis) — CEO a emis
un amendament explicit înainte de livrare, cerând refuz fail-closed contractual, nu doar documentare.

**Remediu** (`RangeConfigV31.__post_init__`, `range_semantic_v3_1.py`): apelează întâi
`super().__post_init__()` (K/N/w_atr/`acknowledge_construction_only`/`K<=N` — EXACT neschimbate), APOI
respinge `d_min_bars` care nu e `int` STRICT (bool exclus explicit, deși `isinstance(True,int)` e adevărat în
Python), sau `int < 1`, cu `RangeSemanticContractErrorV3` (aceeași excepție deja folosită pt. K>N/K,N,w_atr
non-pozitive — niciun tip nou de excepție inventat). O configurație invalidă nu mai poate produce NICIODATĂ o
instanță `RangeConfigV31` — calea de crash devine STRUCTURAL INACCESIBILĂ (nu doar "prinsă" mai târziu în
`_SegmentV31`), fiindcă `RangeSemanticProducerV31`/`RangeSemanticEngineV31` cer un `RangeConfigV31` deja
construit ca argument obligatoriu.

**Verificat** (`tests/test_range_semantic_v3_1.py`, secțiunea "Amendament CEO", 15 teste noi):
- `-1, -100, 0, 1.0, 5.5, True, False, "96", None, 96.0` → toate respinse cu `RangeSemanticContractErrorV3`
  (explicit NU `IndexError` — testat direct).
- `d_min_bars=1` (limita validă minimă) → ACCEPTAT, funcțional corect (`push_close`/`slope()` OK, nu doar
  "nu crapă").
- Un `d_min_bars` invalid nu poate ajunge NICIODATĂ la `RangeSemanticEngineV31`/`RangeSemanticProducerV31`
  (expresia `RangeConfigV31(...)` aruncă înainte ca acestea să fie construite).
- O tentativă eșuată de configurație invalidă NU afectează o instanță VALIDĂ, independentă, deja în rulare
  (continuare identică cu o rulare de control fără nicio tentativă intercalată).
- **Configurațiile EXACTE ale celor două benchmark-uri** (`d_min_bars=96` canonic, `d_min_bars=200000`
  adversarial) rămân valide și NESCHIMBATE — verificat direct (construcție reușită, `range_spec_id()`
  identic) — hardening-ul e pur ADITIV, nu schimbă nimic pt. valori deja valide. **Cele două benchmark-uri
  în curs NU au fost repornite** — justificare: calea de execuție pt. configurații valide (inclusiv cele
  două rulări în curs) e neatinsă de acest amendament; singura schimbare e la GRANIȚA de construcție a
  configurației, pt. valori care oricum nu apar în niciuna din cele două rulări.

Suita completă crește la **320/320 PASS** (305 anterior + 15 noi), mypy `--strict` clean pe toate fișierele
atinse. Acesta e hardening de input-validation la graniță, NU o schimbare semantică RANGE — nimic din
paritatea documentată în §1-§4 de mai sus nu e afectat (toate configurațiile folosite acolo au `d_min_bars`
deja valid).

## 6. Concluzie

**Paritate decizională COMPLETĂ confirmată** pe fixture-ul de oscilație (320 bare), pe traseul HBL-20 (71 bare,
construction-only), și la pragul exact `IS_CHANNEL` (cel mai sensibil punct la reordonarea operațiilor
flotante). Diferența de fingerprint de configurație e DELIBERATĂ (leagă 0.4.1 de propria identitate), nu o
eroare de paritate. Nu s-a pretins byte-parity la nivel de implementare internă — s-a DEMONSTRAT decision-parity,
exact cum cere mandatul §5, cu măsurători explicite acolo unde ordinea flotantă ar fi putut introduce o
diferență (§3 de mai sus: Δ < 1e-9 în toate cele trei poziții testate). `d_min_bars=0` — găsit înainte de
livrare, raportat transparent, corectat prin amendament CEO cu refuz fail-closed contractual la granița de
configurație (§5b) — nu mai poate produce `IndexError`.

Vezi `tests/test_range_semantic_v3_1.py` pentru cele 83 de teste (20 iteme mandat §6 + paritate §5 + test
decisiv de performanță + 15 teste de hardening `d_min_bars`) — toate PASS, plus suita completă 320/320 (237
moștenite + 83 noi) în regresie completă.
