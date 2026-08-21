# ÎNGHEȚAREA ETICHETELOR — `V4_4_1_FRESH_BLIND14`

**Divizia Statistician · mandat STAT-RANGE-V4_4_1-FRESH-BLIND14-FREEZE-001 · 2026-08-20**

```
V4_4_1_FRESH_BLIND14_LABELS_FROZEN
READY_FOR_RT_V4_4_VS_V4_4_1_INFERENCE_AND_SCORING
```

**Raportul nu conține niciun răspuns semantic** — doar identități, numărători și structură.

---

## 1 — CRONOLOGIA, DOVEDITĂ

```
PROTOCOL PRE-COMIS            4af8ea9
        ↓
UNIVERS ELIGIBIL VERIFICAT    73,2% consumat · ≥24 ferestre disjuncte disponibile, necesar 14
        ↓
14 FERESTRE SELECTATE         determinist, 14 trageri, zero respingeri
        ↓
SELECȚIE ÎNGHEȚATĂ            6a62243
        ↓
ETICHETARE OARBĂ CEO 14/14
        ↓
TRANSCRIERE VERIFICATĂ        identică 14/14 cu reafirmarea CEO
        ↓
PAYLOAD CANONIC → HASH → SIGILARE → INTEGRITATE VERIFICATĂ
        ↓
V4_4_1_FRESH_BLIND14_LABELS_FROZEN
```

**Niciun proces de detector înaintea punctului final de îngheț.**

## 2 — IDENTITĂȚI

| element | valoare |
|---|---|
| `labels_sha256` | `4112dbce7b49bd91fc7d0d073f266eea0d421f22b9799d18cc0aa4c63c28c508` |
| `session_log_sha256` | `577edf298b53b4b91f7b15de1fc401487a365f16b2e38c6206b7bd996b819784` |
| `selection_manifest_sha256` | `c8aa83baa3e283b4ff6ff774848b44dd94306101e0339089f71a30fcaa2bb7bc` |
| `window_payload_sha256` | `f66a87526fc752b31f98a1ae7dacccc5ffda000334c91d343f6a5172674d5164` |
| payload etichete | `payload-8838b8c521b5d26d.bin` (30.242 B, **OFF-GIT**) |
| seed | `RANGE_V4_4_1_FRESH_BLIND14\|4ed4eb4\|6adef91\|N14` |
| univers eligibil | corpus 197.094 · sursă `57f4ed95…` · amprentă `af3bf2f6…` |
| autoritate | V4.4.1 `4ed4eb4` (`config_id d7b6c067…`) · RT `6adef91` · V4.4 `3bb61cf` |

## 3 — AUDITUL TRANSCRIERII

★ **Am comparat mecanic transcrierea stocată cu reafirmarea ta din mandat, segment cu segment:
IDENTICĂ 14/14.** Zero divergențe de graniță, de clasă sau de ordine.

| verificare | rezultat | așteptat |
|---|---|---|
| ferestre complete | **14 / 14** | 14 |
| segmente MACRO RANGE | **26** | 26 ✓ |
| ferestre fără MACRO RANGE | **1** (`F441-011`) | 1 ✓ |
| control negativ natural | `F441-011`, **zero** segmente RANGE | ✓ |
| lungimi | **96: 5 · 288: 5 · 480: 4** | 5/5/4 ✓ |
| blocuri | B1: 5 · B2: 4 · B4: 5 | echilibrat pe blocurile eligibile |
| selecție = manifest înghețat | **identică**, aceeași ordine | ✓ |
| acoperire centrală | **14 / 14** completă, zero goluri, zero suprapuneri | ✓ |
| ontologie | doar clase ratificate; **nicio clasă nouă** | ✓ |

Cifrele **nu au fost forțate**: le-am recalculat independent din transcrierea canonică și abia apoi
le-am comparat cu cele așteptate. Ar fi diferit, m-aș fi oprit.

**Nu am recitit graficele.** Nu am rejudecat nicio graniță, n-am despărțit niciun RANGE lung, n-am
convertit niciun RANGE în CHANNEL din cauza driftului. Unde ai cerut explicit ca un RANGE să rămână
nefragmentat — notabil `F441-004` (trei structuri), `F441-008` `206–480`, `F441-012`, `F441-013`
`0–191`, `F441-014` `0–36` — instrucțiunea e păstrată literal în înregistrare.

## 4 — REGULA DE LOT ȘI JURNALUL

```
confidence          : o singură valoare distinctă pe tot lotul -> NOT_SPECIFIED
range episode state : o singură valoare distinctă pe tot lotul -> NOT_SPECIFIED
SEMANTIC_AMENDMENT_LOG = EMPTY
```

Decizia `OPTION_A` e consemnată ca rând propriu, luată **înainte de orice output de detector**; **fără
completare retroactivă**.

**`F441-008`: `TRANSCRIPTION_NOTE_NON_SEMANTIC`.** Formularea inițială („este aceeași fereastră") a
fost corectată de tine; **eticheta semantică nu s-a schimbat niciodată**, deci nu e amendament
semantic. Nota e păstrată pentru auditabilitate, fără efect asupra payload-ului. Am semnalat-o
neutru în timpul sesiunii, înainte de freeze — exact fereastra în care o corecție e încă permisă.

## 5 — SIGILAREA

```
ROUNDTRIP          PASS
BINDING            PASS
ONE_BIT_MUTATION   REJECTED
WRONG_KEY          REJECTED
```

Etichetele stau **în afara Git**; în depozit intră doar hashurile. Nicio cheie nu e comisă sau
transmisă.

## 6 — IZOLAREA DE DETECTOR ȘI PROTECȚIA DOVEZILOR

```
V4_4_EXECUTED = False · V4_4_1_EXECUTED = False
PREDICTIONS_EXIST = False · BLIND_SCORE_COMPUTED = False
detector încărcat în procesele de etichetare/freeze : False
artefacte de predicție sau scor pentru F441          : NICIUNUL
```

Nici V4.4 (`3bb61cf`), nici V4.4.1 (`4ed4eb4`) nu au fost importate, rulate sau consultate. Dovadă de
**mediu**, nu declarație.

```
FB14-001…014      NOT_REUSED       (excluse ca E8, dovezi de diagnostic consumate)
MB3-001…024       NOT_REUSED
MB3-025…048       SEALED / UNTOUCHED — nedecriptate, neinspectate, neetichetate
lot01 / lot02     NOT_REUSED
suprapunere a celor 14 ferestre cu material exclus : ZERO
separare minimă reală față de orice material exclus : 515 bare (cerut 480)
```

Pentru excludere am folosit **exclusiv coordonate non-semantice** din artefactele proprii de selecție.

## 7 — COMPARAȚIA, BLOCATĂ ȘI NESCHIMBATĂ

**V4.4 `3bb61cf` vs V4.4.1 `4ed4eb4`** (`config_id d7b6c067…`), pe exact aceleași 14 ferestre.
Prioritatea de cost declarată prospectiv de CEO rămâne: **RANGE fals e mai periculos decât RANGE
ratat**, deci **H1** (FP direcțional) și **H2** (FP total) sunt **porți DURE**; nicio creștere de
recall sau F1 nu compensează eșecul lor. H3 nedegradare TP, H4 nedegradare recall, H5 beneficiul
T-STALE.

★ **Regula care contează cel mai mult, nemodificată după vederea etichetelor:** dacă `H5` e
`NOT_TESTABLE` fiindcă niciun eveniment de blocare prin candidat stale nu apare natural, verdictul e
**`INCONCLUSIVE` chiar dacă H1–H4 trec**. Nu se adaugă ferestre și nu se inserează manual un caz.

Parametrii T-STALE rămân evaluați ca atare: `window 29 · min_rejections 4 · min_alternation 3`
(**FRAGIL**) `· min_age 12`.

**ENV A** (doar inferență, fără etichete) îngheață ambele seturi de predicții **înainte** de
deschiderea etichetelor; **ENV B** (doar scorare) nu importă și nu execută niciun detector.

---

Etichetele sunt **imutabile** de acum. Un defect de transcriere descoperit după freeze e **eveniment
de integritate**, nu reparație tăcută. Proprietar următor: **Red Team**,
`RT-RANGE-V4_4_1-FRESH-BLIND14-VALIDATION-001`.

*Niciun PASS nu autorizează Strategy Catalog, Alpha, AI Trader, LIVE_SHADOW, broker sau ordine.*
