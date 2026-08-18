"""ve_n1_replay — metadate + identitățile de sursă EXACTE + amprentele de integritate ale closure-ului vendat.

Artefact N1 replay INDEPENDENT de ai_trader: împachetează byte-identic modulele AI Trader @21ae632 + detectorii
@61cbd58c și consumă `ve_brain` 0.1.3 ca dependență externă pinuită. NU reutilizează detectorii ve_tower
(market_structure @61cbd58c = blob 52bb1eba…, DIFERIT de ve_tower).
"""

from __future__ import annotations

VE_N1_REPLAY_VERSION: str = "0.3.0"
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
    }
