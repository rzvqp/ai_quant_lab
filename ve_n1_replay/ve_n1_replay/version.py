"""ve_n1_replay — metadate + identitățile de sursă EXACTE + amprentele de integritate ale closure-ului vendat.

Artefact N1 replay INDEPENDENT de ai_trader: împachetează byte-identic modulele AI Trader @21ae632 + detectorii
@61cbd58c și consumă `ve_brain` 0.1.3 ca dependență externă pinuită. NU reutilizează detectorii ve_tower
(market_structure @61cbd58c = blob 52bb1eba…, DIFERIT de ve_tower).
"""

from __future__ import annotations

VE_N1_REPLAY_VERSION: str = "0.4.1"
N1_REPLAY_CONTRACT_VERSION: str = "n1-replay-request-v1"
SNAPSHOT_SCHEMA_VERSION: str = "n1-replay-snapshot-v1"
REASON_CODE_SCHEMA_VERSION: str = "n1-replay-reason-codes-v1"

# ── 0.1.1: remediere de performanță O(n²)→O(n)/mărginit-amortizat (motor N1 INCREMENTAL) ──
# Orizontul de istoric = maximul lookback-ului axelor MĂRGINITE (COMPRESSION_WINDOW), derivat din cod
# (N1_INCREMENTAL_HORIZON.md), NU ghicit. Legat în identitatea de ledger/snapshot, NU în evaluation_identity
# (care rămâne = 0.1.0 pentru ca rezultatul per-bară să fie byte-identic).
HISTORY_HORIZON: int = 460
HISTORY_HORIZON_VERSION: str = "n1-history-horizon-v1"
LEDGER_SCHEMA_VERSION: str = "n1-incremental-ledger-v1"
INCREMENTAL_SNAPSHOT_SCHEMA_VERSION: str = "n1-incremental-snapshot-v1"

# ── 0.2.0: producător ADITIV RANGE_STATE + evenimente longitudinale de range/breakout ──
# Implementează STAT-RANGE-RECONCILED-SPEC-v1.0 @aca7801 (manifest v2.7.75 @5063448, reachability RT @5e56396).
# RANGE_STATE e un STRAT NOU, separat: NU reutilizează/reinterpretează `StructBand.RANGE`, NU trece prin
# `applicable_regimes` (care nu poate produce RANGE — dovadă RT), NU atinge ve_brain/N3/N4/EV/N6.
# Rezultatele N1 (TREND_UP/DOWN/COMPRESSION/UNCERTAIN) rămân BYTE-IDENTICE cu 0.1.1 (motorul N1 e neatins).
#
# CELE ȘAPTE VERSIUNI CERUTE DE MANDAT — bump-uri la nivel de PACHET pentru suprafața de contract 0.2.0.
# Sunt DECLARAȚII ale pachetului, distincte de constantele runtime ale `ve_brain` (pe care nu le pot modifica
# și care rămân neschimbate în identitatea per-bară N1 ⇒ byte-identitate). Ele intră în identitatea RANGE.
PKG_N1_CONTRACT_VERSION: str = "n1-replay-request-v2"        # (1) n1_contract_version — suprafață extinsă cu RANGE
PKG_RAW_AXIS_SCHEMA_VERSION: str = "raw-axis-schema-v2"      # (2) raw_axis_schema_version — axă aditivă RANGE_STATE
PKG_ROUTER_VERSION: str = "router-v2"                        # (3) router_version — suprafață extinsă cu evenimente
RANGE_STATE_CONTRACT_VERSION: str = "range-state-v1"         # (4) range_state_contract_version
RANGE_EVENT_CONTRACT_VERSION: str = "range-events-v1"        # (5) range_event_contract_version (spec Partea C)
RANGE_SNAPSHOT_SCHEMA_VERSION: str = "range-state-snapshot-v1"   # (6) snapshot_schema_version (RANGE)
RANGE_LEDGER_SCHEMA_VERSION: str = "range-state-ledger-v1"       # (7) ledger_schema_version (RANGE)
# schema internă a stării RANGE (intră în range_spec_id, Partea B/F)
RANGE_STATE_SCHEMA_VERSION: str = "range-state-schema-v1"
RANGE_PRODUCER_VERSION: str = "range-producer-0.2.0"

# constante de timeframe RATIFICATE (split_manifest: „D1 = 96 M15 bars"; H4 = 16). d_min PRIMAR = o zi M15.
BARS_PER_DAY_M15: int = 96
BARS_PER_WEEK_M15: int = 460     # obdz001.WEEK_BARS (= COMPRESSION_WINDOW); folosit DOAR de varianta de grilă „week"
BARS_PER_INTRADAY_SESSION_M15: int = 24    # 6 ore M15 — clasa INTRADAY_RANGE la 0.3.0 (Partea 6.3, aca7801/3aac2cc)

# ── 0.3.0: SPEC V2 semantică RANGE_STATE — remediu SEMANTIC_SPEC_DEFECT (NU un patch peste 0.2.0) ──
# Sursă normativă: Statistician STAT-RANGE-SEMANTIC-DIAGNOSIS-V2-v1.0 @3aac2cc, manifest v2.7.78 @18aa2a1
# (`18aa2a1` e COMMIT-ul manifestului, NU un "config hash" — Statistician a semnalat chiar ei eticheta greșită
# aplicată anterior lui aec8f07; nu o repet aici). Ruling: SEMANTIC_SPEC_DEFECT — cauza structurală (dovedită,
# nu doar măsurată): limita 0.2.0 = extremul unei mulțimi CRESCĂTOARE (monoton nedescrescătoare în lungimea
# ferestrei); a atinge d_min forța fereastra să crească; creșterea ridica limita; ridicarea limitei invalida
# RETROACTIV atingerile numărate față de limita veche. Cu cât fereastra era mai lungă, cu atât detectorul își
# ștergea singur dovezile — o definiție nesatisfiabilă, nu o eroare de implementare (RT a dat PASS; Alpha a
# reprodus identic de 2 ori/3 ere). 0.2.0 e PĂSTRAT NEMODIFICAT pentru audit — 0.3.0 e producător NOU, separat.
#
# Schimbarea centrală (repară exact cei doi factori măsurați, NU adaugă criterii noi):
#   anchor = MEDIANA extremelor swing-urilor confirmate de pe acea latură (NU maxim ⇒ NU monotonă în lungimea
#            ferestrei ⇒ nu se auto-invalidează; un singur spike nu mută limita — elimină factorul 71×)
#   boundary_zone = [anchor − w, anchor + w] (ZONĂ, nu linie)
#   touch = orice bară al cărei interval [low,high] intersectează boundary_zone (fitilul CONTEAZĂ, nu doar
#           close-ul; evaluat CAUZAL față de zona-așa-cum-era-atunci, acumulat monoton — NU se re-scanează
#           retroactiv contra unei zone noi — elimină factorul 160×)
# `w` (lățime de zonă) și `s_max` (prag de pantă pt. separarea range/canal) sunt declarate "PRE-ÎNREGISTRATĂ" în
# document dar FĂRĂ valoare numerică literală în text sau manifest (verificat, ambele surse). Nu le optimizez
# pe rezultate (interzis explicit de mandat) — valorile din `RangeConfigV2` de mai jos sunt PROPUSE DE VE, PE
# TEMEI STRUCTURAL, NERATIFICATE de Statistician; expuse ca parametri de configurare dinamici, niciodată hard-codați
# în producător. Vezi RANGE_STATE_V2_CONTRACT.md secțiunea „w și s_max — ambiguitate declarată".
RANGE_V2_STATISTICIAN_SOURCE_COMMIT: str = "3aac2cc"
RANGE_V2_STATISTICIAN_MANIFEST_COMMIT: str = "18aa2a1"          # manifest v2.7.78 — COMMIT, nu content_hash
RANGE_V2_STATISTICIAN_MANIFEST_VERSION: str = "v2.7.78"
RANGE_V2_RULING: str = "SEMANTIC_SPEC_DEFECT"

PKG_N1_CONTRACT_VERSION_V2: str = "n1-replay-request-v2"        # neschimbat față de 0.2.0 — N1 rămâne neatins
PKG_RAW_AXIS_SCHEMA_VERSION_V2: str = "raw-axis-schema-v2"      # neschimbat față de 0.2.0
PKG_ROUTER_VERSION_V2: str = "router-v2"                        # neschimbat față de 0.2.0
RANGE_STATE_CONTRACT_VERSION_V2: str = "range-state-v2"                  # v1 → v2
RANGE_EVENT_CONTRACT_VERSION_V2: str = "range-events-v2"                 # v1 → v2 (touch pe interval; 11 evenimente)
RANGE_SNAPSHOT_SCHEMA_VERSION_V2: str = "range-state-snapshot-v2"        # v1 → v2
RANGE_LEDGER_SCHEMA_VERSION_V2: str = "range-state-ledger-v2"            # v1 → v2
RANGE_STATE_SCHEMA_VERSION_V2: str = "range-state-schema-v2"             # v1 → v2 (+boundary_zone/anchor/w/
                                                                          #   structure_events_inside/range_class/slope)
RANGE_STATE_MACHINE_VERSION_V2: str = "range-state-machine-v2"
RANGE_PRODUCER_VERSION_V2: str = "range-producer-0.3.0"
RANGE_REASON_CODE_SCHEMA_VERSION_V2: str = "range-reason-codes-v2"

# identitatea predecesorului 0.2.0 (pentru refuzul fail-closed la restore/migrare + raportul de compatibilitate)
PREDECESSOR_0_2_0_VERSION: str = "0.2.0"
PREDECESSOR_0_2_0_WHEEL_SHA256: str = "04b96a8b78b2d09bd8b54bd8044058282c6ab24bf2ac0f2aaec6c1f7a278786f"
PREDECESSOR_0_2_0_BUILD_COMMIT: str = "1dc355b"
PREDECESSOR_0_2_0_DELIVERY_COMMIT: str = "3577026"
PREDECESSOR_0_2_0_RANGE_STATE_HANDOFF_PASS_COMMIT: str = "898e1b9"   # RT-RANGE-0002
# baseline N1 — identic la 0.1.1, 0.2.0 și 0.3.0 (motorul N1 nu s-a schimbat niciodată din 0.1.1 încoace)
N1_BASELINE_VERSION: str = "0.1.1"
N1_BASELINE_INCREMENTAL_PASS_COMMIT: str = "6230ee5"                 # RT-N1-0002

# ── 0.3.1: PIN de configurație V2 — w_atr RATIFICAT, s_max DERIVAT structural (NU un patch semantic) ──
# Sursă normativă: Statistician STAT-RANGE-V2-PREREG-PROTOCOL-v1.0 @4e69e22 (precedență) →
# STAT-RANGE-V2-WATR-FINAL-v1.0 @c29ac98 (rezultat: w_atr=0.30, s_max=2×w_atr=0.60) → addendum @2dde05a
# (auto-corecție n_generated_total, NEAFECTEAZĂ 0.3.1) → manifest v2.7.80 @84a1a98 → v2.7.81 @2611d22
# (corectiv, fingerprint final). Control de construcție: RC-CONSTRUCTION-CHANNEL-NEW-01 (S=3,3781 >> s_max=0,60,
# canal respins ca range — insensibil la valoarea finală a lui w_atr, prag DERIVAT nu ales).
#
# `w_atr = 0.30` este UNICUL loc unde acest literal apare ca implicit de PRODUCȚIE în acest fișier — 0.3.0 folosea
# `w_atr=0.25`/`s_max=0.15` NERATIFICATE (păstrate NEATINSE în range_state_v2.py, pentru audit). `s_max` NU mai
# există ca literal sau câmp independent în 0.3.1 — e DERIVAT structural (`2 × w_atr`), niciodată stocat separat.
RANGE_V2_1_STATISTICIAN_PREREG_COMMIT: str = "4e69e22"
RANGE_V2_1_STATISTICIAN_RESULT_COMMIT: str = "c29ac98"
RANGE_V2_1_STATISTICIAN_ADDENDUM_COMMIT: str = "2dde05a"
RANGE_V2_1_MANIFEST_COMMIT: str = "2611d22"                # v2.7.81 (corectiv, final) — supersedes 84a1a98/v2.7.80
RANGE_V2_1_MANIFEST_VERSION: str = "v2.7.81"
RANGE_V2_1_MANIFEST_FINGERPRINT: str = (
    "432170ff5b6d0d20e125ea318d0293053f10ff0da8df9948bb470dde6d6501f6"
)   # verificat: content_hash.value din split_manifest.json @2611d22, MATCH exact
RANGE_V2_1_CONSTRUCTION_CONTROL_EPISODE_ID: str = "RC-CONSTRUCTION-CHANNEL-NEW-01"

W_ATR_CANONICAL: float = 0.30                              # RATIFICAT — Statistician @c29ac98
S_MAX_DERIVATION_MULTIPLIER: float = 2.0                    # s_max = S_MAX_DERIVATION_MULTIPLIER × w_atr
S_MAX_DERIVATION_FORMULA: str = "derived_s_max = 2 * w_atr"  # citat literal în provenance/fingerprint

RANGE_PRODUCER_VERSION_V2_1: str = "range-producer-0.3.1"
RANGE_SNAPSHOT_SCHEMA_VERSION_V2_1: str = "range-state-snapshot-v2-pinned"
RANGE_LEDGER_SCHEMA_VERSION_V2_1: str = "range-state-ledger-v2-pinned"
RANGE_CONFIG_SCHEMA_VERSION_V2_1: str = "range-config-schema-v2-pinned"

# identitatea predecesorului 0.3.0 (refuz fail-closed la restore/migrare + raport de compatibilitate)
PREDECESSOR_0_3_0_VERSION: str = "0.3.0"
PREDECESSOR_0_3_0_WHEEL_SHA256: str = "34603375de736de3d2b48d3471881a76d4107bcb48487100cf3af33f84ee63e0"
PREDECESSOR_0_3_0_BUILD_COMMIT: str = "d307aec"
PREDECESSOR_0_3_0_DELIVERY_COMMIT: str = "22e1496"

# UNICUL cod de motiv nou (mandat: "cu excepția unui cod nou strict necesar pentru refuzul configurației legacy")
LEGACY_S_MAX_REJECTED: str = "LEGACY_S_MAX_REJECTED"

# ── 0.4.0: RANGE SEMANTIC V3 — REDESIGN longitudinal (NU un patch, contract NOU range-semantic-v3.0) ──
# Sursă normativă: Statistician STAT-RANGE-SEMANTIC-SPEC-V3-v1.0 @`bf9f780`, manifest v2.7.84 @`db098ed`,
# fingerprint COMPLET verificat exact din manifest (content_hash.value):
#   cddaab381f0132eac025e9fcad3454d54fca78dc1abab6bc8b3cea05e5951233
# Consumă `RANGE_HUMAN_LABEL_BATCH_01.pdf` + `..._CEO_ASSISTED_RESULTS.md/.txt` — lot **CEO_ASSISTED**,
# **construction-only PERMANENT** (NU blind, NU independent, NU OOS, NU validare). Defecte V2 demonstrate:
# ancoră pe 512 bare vs d_min 96 (5,3×), ancore care se INVERSEAZĂ (ZONES_DEGENERATE absentă), poartă de
# durată care nu poate eșua (`bars_in_state` saturează la ~508), ACCEPTED_BREAK pe 76,65% din bare (aceeași
# CLASĂ de defect ca V1 — regula proprie distruge precondiția alteia), fără segmentare longitudinală
# (17/24 ferestre sunt multi-regim), sweep EMIS ca eveniment dar consumat de NICIO stare.
RANGE_V3_STATISTICIAN_SPEC_COMMIT: str = "bf9f780"
RANGE_V3_MANIFEST_COMMIT: str = "db098ed"
RANGE_V3_MANIFEST_VERSION: str = "v2.7.84"
RANGE_V3_MANIFEST_FINGERPRINT: str = (
    "cddaab381f0132eac025e9fcad3454d54fca78dc1abab6bc8b3cea05e5951233"
)   # verificat: content_hash.value din split_manifest.json @db098ed, MATCH exact
RANGE_V3_HBL_BATCH_PDF_SHA256: str = "8599660e73711b22d1d3f25095040107e4795b856e341faabfa735193c679a76"
RANGE_V3_HBL_PROVENANCE: str = "CEO_ASSISTED"     # NU blind, NU independent, NU OOS — construction-only PERMANENT

# NOUĂ suprafață de contract (9 versiuni — spațiu de nume PROPRIU, NU reutilizează/reinterpretează v2/StructBand)
RANGE_SEMANTIC_CONTRACT_VERSION_V3: str = "range-semantic-v3.0"
RANGE_STATE_MACHINE_VERSION_V3: str = "range-state-machine-v3.0"
RANGE_EVENT_CONTRACT_VERSION_V3: str = "range-events-v3.0"
RANGE_SNAPSHOT_SCHEMA_VERSION_V3: str = "range-state-snapshot-v3.0"
RANGE_LEDGER_SCHEMA_VERSION_V3: str = "range-state-ledger-v3.0"
RANGE_REASON_CODE_CONTRACT_VERSION_V3: str = "range-reason-codes-v3.0"
RANGE_CONFIG_SCHEMA_VERSION_V3: str = "range-config-schema-v3.0"
RANGE_EVALUATION_IDENTITY_VERSION_V3: str = "range-evaluation-identity-v3.0"
RANGE_PRODUCER_VERSION_V3: str = "range-producer-0.4.0"

# ── Parametrii V3 — statutul lor EXACT din spec (§6.4 @bf9f780), NIMIC ascuns ──
# d_min ȘI n_touch rămân MOȘTENITE (spec: NU marcate NEIDENTIFICAT — doar fereastra ancorei și w_atr trebuie
# reidentificate sub noua geometrie). K (reintrare sweep) și N (închideri de acceptare) sunt NEIDENTIFICATE
# — NU au valoare implicită ascunsă; `RangeConfigV3` le cere EXPLICIT, fără default, și refuză construcția
# fără confirmarea explicită `acknowledge_construction_only=True` (suprafața de producție REFUZĂ configurația
# neratificată prin construcție, nu doar prin documentație). `w_atr` (deci `s_max=2×w_atr`) NU se transportă
# automat din 0.3.1 — ancora s-a schimbat (segment-locală, nu fereastră de 512 bare), deci valoarea 0,30
# ratificată SUB ancora veche NU e validă sub ancora nouă și trebuie reidentificată — la fel NEIDENTIFICAT.
RANGE_V3_D_MIN_INHERITED: bool = True             # d_min_bars (96/24) — inherited, per spec
RANGE_V3_N_TOUCH_INHERITED: bool = True           # n_touch — inherited, per spec
RANGE_V3_K_STATUS: str = "NEIDENTIFICAT"          # fereastra de reintrare pt. sweep — interval plauzibil (1, d_min/4]
RANGE_V3_N_ACCEPTANCE_STATUS: str = "NEIDENTIFICAT — moștenit provizoriu n_acceptance=2 (marcaj explicit, nu ratificare)"
RANGE_V3_W_ATR_STATUS: str = "NEIDENTIFICAT — trebuie REIDENTIFICAT sub noua ancoră segment-locală (0.3.1: 0.30 NU se transportă)"
RANGE_V3_ANCHOR_WINDOW_RULE: str = (
    "swing-uri acumulate DIN structural_start AL SEGMENTULUI CURENT, nemărginit în viața segmentului "
    "(mărginit natural: un segment nou pornește gol la fiecare tranziție) — NU fereastra fixă de 512 bare "
    "din 0.3.x. Aceasta operaționalizează regula declarată 'fereastra ancorei nu poate depăși durata "
    "segmentului' FĂRĂ a introduce un al patrulea parametru numeric neidentificat."
)

# identitatea predecesorului 0.3.1 (refuz fail-closed la restore/migrare + raport de compatibilitate)
PREDECESSOR_0_3_1_VERSION: str = "0.3.1"
PREDECESSOR_0_3_1_WHEEL_SHA256: str = "048ee2b495112c9f90b39d65a7d6bd851764a46f1e32b0eda7c6ad2a42686cca"
PREDECESSOR_0_3_1_BUILD_COMMIT: str = "aa01f41"
PREDECESSOR_0_3_1_DELIVERY_COMMIT: str = "18d1aa1"

# ── 0.4.1: PERFORMANCE DELTA FIX — remediu §12 RT-RANGE-0004, NU un patch semantic ──
# Sursă normativă: Red Team RT-RANGE-0004 @`87cad2c` (ledger entry E79), verdict RANGE_V3_SEMANTIC_FAIL pe
# `ve_n1_replay 0.4.0` (build `dead38d`, delivery `034b919`). SINGURUL defect material: `RangeConfigV3`
# accepta `d_min_bars` nemărginit (ex. 200000), iar `_Segment.slope()` (0.4.0) re-parcurgea întreaga coadă
# `closes` la FIECARE bară — O(d_min_bars)/bară, măsurat 20,1× cost pt. 20× d_min, extrapolat ~8,9h la
# d_min_bars=200000 (>> garanția de 4h declarată la 355.696 bare). Restul semanticii V3 (14 stări, segmentare,
# ancoră, K/N, HBL-20) a trecut INDEPENDENT verificat de Red Team — NEATINS aici (domeniu STRICT performanță).
# Variantă aleasă: **A — pantă OLS incrementală** (statistici suficiente, NU o resortare/reparcurgere completă
# per bară) — NU s-a introdus niciun plafon arbitrar pt. `d_min_bars` (spec `bf9f780` e tăcută asupra unui
# asemenea plafon; mandatul interzice explicit alegerea arbitrară a unui număr doar ca benchmarkul să treacă;
# Varianta B (plafon) a rămas NEUTILIZATĂ, fiindcă nicio sursă normativă nu publică un asemenea maxim).
RANGE_V3_1_RED_TEAM_COMMIT: str = "87cad2c"
RANGE_V3_1_RED_TEAM_ENTRY: str = "E79"
RANGE_V3_1_RED_TEAM_VERDICT: str = "RANGE_V3_SEMANTIC_FAIL"
RANGE_V3_1_RED_TEAM_DEFECT_SECTION: str = "§12"
RANGE_V3_1_FIX_VARIANT: str = "A — incremental OLS slope via sufficient statistics, no d_min_bars cap"

# spațiu de nume PROPRIU pt. 0.4.1 (0.4.0 rămâne BYTE-NEATINS — vezi range_semantic_v3.py, NEMODIFICAT)
RANGE_PRODUCER_VERSION_V3_1: str = "range-producer-0.4.1"
RANGE_SNAPSHOT_SCHEMA_VERSION_V3_1: str = "range-state-snapshot-v3.1"   # structura internă a segmentului s-a schimbat
# NESCHIMBATE față de 0.4.0 (semantica NU s-a schimbat — doar implementarea pantei):
# range_semantic_contract_version, range_state_machine_version, range_event_contract_version,
# range_config_schema_version, range_reason_code_contract_version, range_evaluation_identity_version
# rămân EXACT RANGE_SEMANTIC_CONTRACT_VERSION_V3 etc. (0.4.0) — cele 14 stări/evenimente, K/N, geometria,
# reason codes NU s-au schimbat, deci NU au un nou identificator de contract.

# identitatea predecesorului 0.4.0 (refuz fail-closed la restore/migrare + raport de compatibilitate)
PREDECESSOR_0_4_0_VERSION: str = "0.4.0"
PREDECESSOR_0_4_0_WHEEL_SHA256: str = "c79f5fcab202a72c6548a470e7702b6917685dc782c67f5f4dfe4ed0af363699"
PREDECESSOR_0_4_0_BUILD_COMMIT: str = "dead38d"
PREDECESSOR_0_4_0_DELIVERY_COMMIT: str = "034b919"

# ── PROTOTIP `range-hierarchical-v4.3` (mandat CEO, NU o versiune a pachetului -- VE_N1_REPLAY_VERSION rămâne
# 0.4.1, NEATINS; niciun wheel, nicio atingere release/SHA256SUMS). Provenance-only -- constantele operaționale
# proprii (contract_version, config_id normativ) trăiesc direct în range_semantic_v4_3.py, nu aici, ca să nu
# implice o identitate de PACHET pt. ceva ce mandatul interzice explicit să fie livrat ca atare. ──
RANGE_V4_3_STATISTICIAN_PACKAGE_COMMIT: str = "d6e599e"
RANGE_V4_3_STATISTICIAN_MANIFEST_COMMIT: str = "14d4c22"
RANGE_V4_3_STATISTICIAN_MANIFEST_VERSION: str = "v2.7.94"
RANGE_V4_3_STATISTICIAN_MANIFEST_FINGERPRINT: str = (
    "a5d69e2d0150d7ca2cf750df49f65cfc55b91fa89d13568fa42f81a48f4ee565")
RANGE_V4_3_RED_TEAM_COMMIT: str = "2c113ef"
RANGE_V4_3_RED_TEAM_ENTRY: str = "E81"
RANGE_V4_3_RED_TEAM_AUDIT: str = "RT-RANGE-0006"
RANGE_V4_3_RED_TEAM_VERDICT: str = "RANGE_V4_IMPLEMENTATION_PACKAGE_STATIC_PASS"
RANGE_V4_3_HARNESS_PATH: str = "statistician/harness/range_v42_contract_harness.py"
RANGE_V4_3_HARNESS_SHA256: str = "c917604bd42a0943d77d385523ececba149a3e78f76a4875ce94cf82a368c72d"
RANGE_V4_3_HARNESS_TESTS_PATH: str = "statistician/harness/test_range_v42_adversarial.py"
RANGE_V4_3_HARNESS_TESTS_SHA256: str = "ecb4140e7f47d7b86cb29ef7d50e193a1375dddc2c5505aef7a65add2d277f40"
# numele fișierului harness conține "v42" din motive ISTORICE (v4.3 = v4.2 + 17 corecții, statistician nu a
# izolat un fișier nou) -- normativ e contract_version="range-hierarchical-v4.3" (singular, RT §2). VE nu
# implementează v4.2 -- toate simbolurile VE poartă v4_3/V43, niciodată v42/V42.

# sursele EXACTE
AI_SOURCE_REPO: str = "ai_quant_lab-wp5b"
AI_SOURCE_BRANCH: str = "discovery-mk-matrix-v1"
AI_SOURCE_COMMIT: str = "21ae632"                                   # handoff-ul AI Trader
DETECTOR_SOURCE_REPO: str = "ai_quant_lab-alpha-automation"
DETECTOR_SUBMODULE_COMMIT: str = "61cbd58c3d5da19001b125b65d669ddad54a14c4"   # submodul pinuit (NU ve_tower)

# dependența externă
VE_BRAIN_VERSION: str = "0.1.3"
VE_BRAIN_WHEEL_SHA256: str = "edd208ad6c2c943b17a11759ece1fdf5ab2a7025779b191764c383ecce987d11"

# GIT-BLOB SHA1 — verificabile INDEPENDENT de Red Team (git rev-parse <commit>:<path>). Byte-identitate SEPARATĂ
# pentru modulele AI Trader (@21ae632) și detectori (@61cbd58c).
VENDORED_AI_BLOB_SHA1: dict[str, str] = {
    "n1_replay/__init__.py": "5e3d1d9520f883a2b2a86d4ecec71422db66bfa9",
    "n1_replay/engine.py": "f2df0402907c7eb689ba6b53937a6eee055f216f",
    "n1_replay/errors.py": "2eff7d3371f0d376c79c5b575f52228f098c83b6",
    "n1_replay/identity.py": "08611d44ab6dba40094051734de546789f6e40b0",
    "n1_replay/types.py": "c58d40016736e5bc35df08714f0cbfc288dc2e58",
    "n1_replay/fixtures/__init__.py": "2f481def8b9be154e8861fcf3d16898d0488774d",
    "n1_replay/fixtures/canonical_bars.py": "4c13daf4864b7e4c3143d2fe02d236ab8cee0a26",
    "live_signal_source/types.py": "fc5d534e95d2973f5b6e66dade8119ee81fef774",
    "signal_engine/types.py": "16fba869be2205cad66f2117a0a799e5e6447fc2",
    "market_scanner/types.py": "09ef62241a16e24bd52f31705af00658cd887e35",
    "market_scanner/exceptions.py": "729eb8f80782b4df577c2d58914471c846ac9899",
    "strategy_manager/contract.py": "30bb43f3e0a715dbde9416d307e9d2da795720fe",
    "mandate2_readiness/wheel_verification.py": "99066d6386f3e830408deab11265439860c36b6b",
    "new_brain_bridge/raw_axes_builder.py": "d071c8cbd993cb9377b70af6b61e353d4c101966",
    "structural_observer/vendor_bridge.py": "bb53680c2180a23366b9aa5a08130b4410ea6683",
}
VENDORED_DETECTOR_BLOB_SHA1: dict[str, str] = {
    "market_structure.py": "52bb1eba76d1dee96fae3ed5f5e434c53612176a",   # DIFERIT de ve_tower (d734ac9a)
    "market_state.py": "3f88f8c88988d2b74caf70c199907cf0871c3019",
    "imbalance_mechanics.py": "aa1c6d36d6395a1266b17848296a4c74631ab7c1",
    "order_flow.py": "23b0470086efa24f7b50048e973ecc90fa4a8cb7",
    "order_block_void.py": "2b0f3f37154c4df475e1e7ef0fa782d6f808de9b",
}

RAW_AXES_BUILDER_IMPL_COMMIT: str = AI_SOURCE_COMMIT   # commitul implementării RawAxesBuilder (parte din identitate)


def build_info() -> dict[str, object]:
    return {
        "ve_n1_replay_version": VE_N1_REPLAY_VERSION, "n1_replay_contract_version": N1_REPLAY_CONTRACT_VERSION,
        "ai_source_commit": AI_SOURCE_COMMIT, "detector_submodule_commit": DETECTOR_SUBMODULE_COMMIT,
        "ve_brain_version": VE_BRAIN_VERSION, "ve_brain_wheel_sha256": VE_BRAIN_WHEEL_SHA256,
        "snapshot_schema_version": SNAPSHOT_SCHEMA_VERSION, "reason_code_schema_version": REASON_CODE_SCHEMA_VERSION,
        "history_horizon": HISTORY_HORIZON, "history_horizon_version": HISTORY_HORIZON_VERSION,
        "ledger_schema_version": LEDGER_SCHEMA_VERSION,
        "incremental_snapshot_schema_version": INCREMENTAL_SNAPSHOT_SCHEMA_VERSION,
        "range_state_contract_version_v2": RANGE_STATE_CONTRACT_VERSION_V2,
        "range_event_contract_version_v2": RANGE_EVENT_CONTRACT_VERSION_V2,
        "range_state_schema_version_v2": RANGE_STATE_SCHEMA_VERSION_V2,
        "range_state_machine_version_v2": RANGE_STATE_MACHINE_VERSION_V2,
        "range_snapshot_schema_version_v2": RANGE_SNAPSHOT_SCHEMA_VERSION_V2,
        "range_ledger_schema_version_v2": RANGE_LEDGER_SCHEMA_VERSION_V2,
        "range_producer_version_v2": RANGE_PRODUCER_VERSION_V2,
        "range_v2_statistician_source_commit": RANGE_V2_STATISTICIAN_SOURCE_COMMIT,
        "range_v2_statistician_manifest_commit": RANGE_V2_STATISTICIAN_MANIFEST_COMMIT,
        "w_atr_canonical": W_ATR_CANONICAL, "s_max_derivation_formula": S_MAX_DERIVATION_FORMULA,
        "range_producer_version_v2_1": RANGE_PRODUCER_VERSION_V2_1,
        "range_snapshot_schema_version_v2_1": RANGE_SNAPSHOT_SCHEMA_VERSION_V2_1,
        "range_ledger_schema_version_v2_1": RANGE_LEDGER_SCHEMA_VERSION_V2_1,
        "range_v2_1_statistician_prereg_commit": RANGE_V2_1_STATISTICIAN_PREREG_COMMIT,
        "range_v2_1_statistician_result_commit": RANGE_V2_1_STATISTICIAN_RESULT_COMMIT,
        "range_v2_1_manifest_commit": RANGE_V2_1_MANIFEST_COMMIT,
        "range_v2_1_manifest_fingerprint": RANGE_V2_1_MANIFEST_FINGERPRINT,
        "range_semantic_contract_version_v3": RANGE_SEMANTIC_CONTRACT_VERSION_V3,
        "range_producer_version_v3": RANGE_PRODUCER_VERSION_V3,
        "range_v3_statistician_spec_commit": RANGE_V3_STATISTICIAN_SPEC_COMMIT,
        "range_v3_manifest_commit": RANGE_V3_MANIFEST_COMMIT,
        "range_v3_manifest_fingerprint": RANGE_V3_MANIFEST_FINGERPRINT,
        "range_v3_hbl_provenance": RANGE_V3_HBL_PROVENANCE,
        "range_producer_version_v3_1": RANGE_PRODUCER_VERSION_V3_1,
        "range_snapshot_schema_version_v3_1": RANGE_SNAPSHOT_SCHEMA_VERSION_V3_1,
        "range_v3_1_red_team_commit": RANGE_V3_1_RED_TEAM_COMMIT,
        "range_v3_1_red_team_verdict": RANGE_V3_1_RED_TEAM_VERDICT,
        "range_v3_1_fix_variant": RANGE_V3_1_FIX_VARIANT,
    }
