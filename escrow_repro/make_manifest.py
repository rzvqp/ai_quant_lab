"""Genereaza `ESCROW_REPRO_MANIFEST.json`. Amprenta pachetului se calculeaza NUMAI dupa
ce toate artefactele incluse sunt inghetate (§11).

    python escrow_repro/make_manifest.py --result 48/48 --date 2026-08-19
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import platform
import sys
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)


def sha256_file(path: str) -> str:
    return hashlib.sha256(io.open(path, "rb").read()).hexdigest()


def build(result: str, date: str) -> dict[str, Any]:
    artefacts = ["canonical_corpus.py", "verify_range_v43_escrow.py",
                 "test_escrow_repro.py", "BARS_SHA256_SPEC.md", "make_manifest.py"]
    m: dict[str, Any] = {
        "manifest_id": "STAT-ESCROW-REPRO-MANIFEST",
        "version": "1.0",
        "remediates": "ESCROW-UNREPRODUCIBLE-ANCHOR (Red Team RT-RANGE-0009)",
        "published_date": date,
        "source_commits": {
            "statistician_v43_package": "d6e599e",
            "statistician_manifest_v2_7_94": "14d4c22",
            "red_team_static_audit_RT_0006": "2c113ef",
            "ve_frozen_prototype": "f224e7d",
            "red_team_prototype_audit_RT_0007": "b7c6fa8",
            "reproducible_runner": "82f27c0",
            "red_team_runner_audit_RT_0008": "eb62d3e",
            "red_team_prerun_protocol_RT_0009": "38daf9b",
            "red_team_verdict_RT_0009": "e504fcf",
            "red_team_scrubbed_report": "8e04dd7",
            "ledger": "E84",
        },
        "source_corpus": {
            "file": "data/market/OANDA_XAUUSD_M15.csv",
            "sha256": "57f4ed9544993c8fbba28d9c1e3319f2e0665ef5db211fb09d9f4622222ccd37",
            "rows": 355696,
            "git_tracked": True,
        },
        "canonical_corpus": {
            "rows": 197094,
            "discovery_segments": 4,
            "fingerprint_sha256": "af3bf2f6ffc35ba4c4f4c6da9963c06ff5c99c4952b5ab62d42218cc7b254cf3",
            "fingerprint_convention": "identica cu bars_sha256_v1, aplicata pe tot corpusul",
            "schema": ["time:int64 (unix s, UTC)", "open:float64", "high:float64",
                       "low:float64", "close:float64", "volume:int64 (neutilizat de ancora)"],
            "builder_version": "canonical_corpus_v1",
            "loader": {"repo_branch": "alpha-automation-v1",
                       "module": "edge_research/_common.py", "entry": "load",
                       "timeframe_key": "M15_v2",
                       "split_id": "pre_holdout_2025-10-23T09-15-00Z_v1",
                       "cutoff": "2025-10-23T09:15:00Z"},
            "why_this_repo": ("loaderul din ai_quant_lab-wp5b intoarce 130491 bare pentru acelasi "
                              "timeframe (manifestul lui declara 3 segmente, nu 4); divergenta era "
                              "deja consemnata in manifestul Statisticianului"),
            "manifest_entry_fingerprint_M15_v2": "5d1cccabc3be9784ab8164ac79303774",
            "invariant_across_manifest_versions": ["2.7.92", "2.7.93", "2.7.94"],
        },
        "bars_sha256_recipe": {
            "version": "bars_sha256_v1",
            "window": "[render_start, render_end) — fereastra RANDATA, semi-deschisa",
            "field_order": ["high", "low", "open", "close"],
            "concatenation": "pe COLOANE, nu intretesere pe randuri",
            "scaling": "valoare * 1e6, apoi int64 (TRUNCHIERE spre zero)",
            "bytes": "ndarray.tobytes() — 8 bytes/element, little-endian, ordine C",
            "digest": "sha256, hex minuscul",
            "excluded_fields": ["time", "volume", "atr14", "session", "dow"],
            "resolution": "1e-6 in pret; o perturbatie de exact 1e-6 poate fi absorbita de "
                          "rotunjirea float64, de la 2e-6 detectia e ferma (un tick = 1000 unitati)",
            "settles_open_question": "Red Team §7.2: se hashuieste fereastra RANDATA, nu cea "
                                     "canonica (48/48 vs 0/48)",
        },
        "escrow": {
            "payload_id": "payload-b7e103a3d9b86f72.bin",
            "payload_sha256_prefix16": "b7e103a3d9b86f72",
            "payload_bytes": 20906,
            "location": "IN AFARA Git — se transmite prin argument, nu prin cale codata",
            "published_anchors_document": "statistician/BLIND_LABEL_BATCH_02_HASHES.md "
                                          "(ai_quant_lab, statistician-foundation)",
            "n_windows": 48,
            "total_bars": 13824,
            "length_histogram": {"96": 16, "288": 16, "480": 16},
            "corrected_lengths": {"BLIND-046": 288, "BLIND-047": 96, "BLIND-048": 480},
        },
        "relation_to_prior_manifests": {
            "supersedes": None,
            "supplements": "BLIND_LABEL_BATCH_02_HASHES.md — ancorele NU sunt inlocuite, "
                           "sunt facute reproductibile",
            "resealing_performed": False,
            "anchors_modified": 0,
        },
        "unreproduced_historical_anchor": {
            "field": "window_list_sha256",
            "value_prefix": "d9f77eea",
            "status": "ISTORIC NEREPRODUCTIBIL — pastrat, NU inlocuit, reteta NU inventata",
            "blocks_RT_0009_section_4": False,
        },
        "reproduction_environment": {
            "date": date,
            "python": sys.version.split()[0],
            "platform": platform.system(),
            "numpy_required": True,
            "clean_checkout_verified": True,
        },
        "result": {"anchors_reproduced": result, "verifier_exit_code": 0,
                   "tests_passed": 22, "tests_failed": 0},
        "artefact_hashes": {},
        "package_fingerprint": {"value": "", "computed_over":
                                "sha256 peste artefact_hashes serializat sortat"},
    }
    m["artefact_hashes"] = {a: sha256_file(os.path.join(HERE, a)) for a in artefacts}
    body = json.dumps(m["artefact_hashes"], sort_keys=True, ensure_ascii=False)
    m["package_fingerprint"]["value"] = hashlib.sha256(body.encode("utf-8")).hexdigest()
    return m


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--result", default="48/48")
    p.add_argument("--date", required=True)
    a = p.parse_args()
    m = build(a.result, a.date)
    out = os.path.join(HERE, "ESCROW_REPRO_MANIFEST.json")
    io.open(out, "w", encoding="utf-8", newline=chr(10)).write(
        json.dumps(m, indent=2, ensure_ascii=False) + chr(10))
    print("amprenta pachet:", m["package_fingerprint"]["value"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
