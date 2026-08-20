"""SIGILARE — `RANGE_MACRO_BLIND_LABEL_BATCH_03`.

Produce DOUA artefacte cu roluri separate:
  A. manifest EXECUTION-SAFE (comis in Git): ID abstract, lungime, ancora `bars_sha256`.
     NU contine timestampuri, NU contine OHLC, NU contine indici canonici.
  B. mapping SIGILAT (escrow, IN AFARA Git): ID -> fereastra, cu indici si timestampuri.

Ancorele folosesc reteta ratificata `bars_sha256_v1` (RT-RANGE-0010), NU o schema noua.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import sys
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "escrow_repro"))

from canonical_corpus import build_canonical_corpus, bars_sha256  # noqa: E402

ESCROW_DIR = os.environ.get("ESCROW_DIR",
                            os.path.join(os.path.expanduser("~"), "escrow_red_team"))


def main() -> int:
    sel = json.load(io.open(os.path.join(HERE, "selection_batch_03.json"), encoding="utf-8"))
    sel_txt = json.dumps(sel, indent=2, ensure_ascii=False) + chr(10)
    sel_sha = hashlib.sha256(sel_txt.encode("utf-8")).hexdigest()

    corpus = build_canonical_corpus()
    pub: list[dict[str, Any]] = []
    sealed: list[dict[str, Any]] = []
    for w in sel["windows"]:
        a, b = w["r_start"], w["r_end"]           # fereastra RANDATA, ca la lotul 02
        anchor = bars_sha256(corpus["high"][a:b], corpus["low"][a:b],
                             corpus["open"][a:b], corpus["close"][a:b])
        pub.append({"id": w["id"], "L": w["L"], "n_rendered_bars": b - a,
                    "bars_sha256": anchor})
        sealed.append({**w, "bars_sha256": anchor,
                       "start_utc": int(corpus["time"][w["start"]]),
                       "end_utc": int(corpus["time"][w["end"] - 1])})

    # ── A. manifest execution-safe ──────────────────────────────────────────────
    total = sum(p["L"] for p in pub)
    hist: dict[int, int] = {}
    for p in pub:
        hist[p["L"]] = hist.get(p["L"], 0) + 1
    man: dict[str, Any] = {
        "manifest_id": "STAT-MACRO-BLIND-BATCH-03-EXECUTION-SAFE",
        "batch_id": sel["batch_id"], "version": "1.0", "published_date": "2026-08-20",
        "authority": sel["authority"], "protocol": sel["protocol"],
        "seed_sha256": sel["seed_sha256"], "sampling_correction": sel["sampling_correction"],
        "selection_artifact_sha256": sel_sha,
        "n_windows": len(pub), "total_canonical_bars": total,
        "length_histogram": {str(k): v for k, v in sorted(hist.items())},
        "bars_sha256_recipe": "bars_sha256_v1 (RT-RANGE-0010, reprodusa 48/48)",
        "anchor_window": "[r_start, r_end) — fereastra RANDATA, context 24+24",
        "contains_no_timestamps": True, "contains_no_ohlc": True,
        "contains_no_canonical_indices": True, "contains_no_labels": True,
        "state": {"NEW_MACRO_BLIND_BATCH_SELECTED": True,
                  "NEW_MACRO_BLIND_LABELS_FROZEN": False,
                  "NEW_MACRO_BLIND_ESCROW_SEALED": True,
                  "DETECTOR_EXECUTED_ON_NEW_BLIND": False,
                  "PREDICTIONS_FROZEN": False,
                  "BLIND_SCORE_COMPUTED": False,
                  "INDEPENDENT_SEMANTIC_BLIND": "NOT_YET_EXECUTED"},
        "windows": pub,
    }
    man_txt = json.dumps(man, indent=2, ensure_ascii=False) + chr(10)
    io.open(os.path.join(HERE, "EXECUTION_SAFE_MANIFEST.json"), "w",
            encoding="utf-8", newline=chr(10)).write(man_txt)
    man_sha = hashlib.sha256(man_txt.encode("utf-8")).hexdigest()

    # ── B. mapping sigilat, IN AFARA Git ────────────────────────────────────────
    sys.path.insert(0, ESCROW_DIR)
    import escrow_tool as et                                    # noqa: PLC0415
    payload = {
        "escrow_id": "RANGE_MACRO_BLIND_LABEL_BATCH_03",
        "issued_by": "Statistician", "status": "SEALED_AWAITING_CEO_LABELS",
        "authority": sel["authority"], "seed_string": sel["seed_string"],
        "seed_sha256": sel["seed_sha256"], "selection_artifact_sha256": sel_sha,
        "execution_safe_manifest_sha256": man_sha,
        "n_windows": len(sealed), "mapping_ID_to_window": sealed,
        "labels_present": False,
        "prohibitions_at_seal_time": [
            "detectorul NU a fost rulat pe acest lot",
            "nu exista predictii pentru acest lot",
            "nu exista scor pentru acest lot",
            "etichetele NU exista inca — se produc de CEO, separat",
        ],
        "next_owner": "CEO (etichetare), apoi Red Team (executie oarba)",
    }
    blob = et.seal(json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                   io.open(os.path.join(ESCROW_DIR, "escrow_key_v3.bin"), "rb").read())
    pid = hashlib.sha256(blob).hexdigest()[:16]
    path = os.path.join(ESCROW_DIR, f"payload-{pid}.bin")
    io.open(path, "wb").write(blob)

    print(f"selection_sha256           : {sel_sha}")
    print(f"execution_safe_manifest_sha: {man_sha}")
    print(f"payload sigilat            : payload-{pid}.bin  ({len(blob)} bytes, OFF-GIT)")
    print(f"ferestre {len(pub)} | bare canonice {total} | histograma {man['length_histogram']}")

    # ── verificare independenta a sigiliului ────────────────────────────────────
    back = json.loads(et.open_(io.open(path, "rb").read(),
                               io.open(os.path.join(ESCROW_DIR, "escrow_key_v3.bin"), "rb").read()))
    assert back["mapping_ID_to_window"] == sealed, "roundtrip mapping"
    assert back["execution_safe_manifest_sha256"] == man_sha
    ok_anchor = sum(1 for p, s in zip(pub, back["mapping_ID_to_window"])
                    if p["bars_sha256"] == s["bars_sha256"])
    print(f"verificare sigiliu: roundtrip OK | ancore concordante {ok_anchor}/{len(pub)}")
    bad = bytearray(blob); bad[len(bad) // 2] ^= 0x01
    try:
        et.open_(bytes(bad), io.open(os.path.join(ESCROW_DIR, "escrow_key_v3.bin"), "rb").read())
        print("*** MUTATIA DE UN BIT NU A FOST REFUZATA ***")
        return 1
    except Exception:
        print("verificare sigiliu: mutatie de un bit REFUZATA (encrypt-then-MAC)")
    try:
        et.open_(blob, io.open(os.path.join(ESCROW_DIR, "escrow_key.bin"), "rb").read())
        print("*** CHEIA GRESITA NU A FOST REFUZATA ***")
        return 1
    except Exception:
        print("verificare sigiliu: cheie gresita REFUZATA")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
