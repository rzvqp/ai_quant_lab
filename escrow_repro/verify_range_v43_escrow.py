"""VERIFICATOR INDEPENDENT — reproduce cele 48 de ancore `bars_sha256` din escrow.

Punct de intrare unic. Exit code 0 numai la 48/48; nenul la ORICE nepotrivire.

    python escrow_repro/verify_range_v43_escrow.py \
        --payload <cale>/payload-b7e103a3d9b86f72.bin \
        --key     <cale>/escrow_key_v3.bin \
        --tool    <cale>/escrow_tool.py

Payload-ul, cheia si unealta stau IN AFARA checkout-urilor Git si se dau prin argument.
Nicio cale absoluta nu e codata in sursa.

★ OUTPUT: numai ID-uri abstracte, PASS/FAIL si hashuri deja autorizate pentru publicare.
  NICIODATA timestampuri, bare OHLC, mapping ID->fereastra, chei sau payload decriptat.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
import sys
from typing import Any

sys.path.insert(0, __file__.rsplit("escrow_repro", 1)[0] or ".")
sys.path.insert(0, __file__.rsplit("verify_range_v43_escrow.py", 1)[0] or ".")

from canonical_corpus import (  # noqa: E402
    BARS_SHA256_RECIPE_VERSION, CORPUS_SPEC, build_canonical_corpus,
    corpus_fingerprint, window_bars_sha256,
)

EXPECTED_CORPUS_FINGERPRINT = "af3bf2f6ffc35ba4c4f4c6da9963c06ff5c99c4952b5ab62d42218cc7b254cf3"
EXPECTED_PAYLOAD_SHA16 = "b7e103a3d9b86f72"          # = numele content-addressed
EXPECTED_N_WINDOWS = 48
EXPECTED_TOTAL_BARS = 13824
EXPECTED_LENGTH_HISTOGRAM = {96: 16, 288: 16, 480: 16}
EXPECTED_CORRECTED = {"BLIND-046": 288, "BLIND-047": 96, "BLIND-048": 480}


class VerifyError(RuntimeError):
    """Verificarea a esuat fail-closed."""


def _load_tool(path: str) -> Any:
    spec = importlib.util.spec_from_file_location("escrow_tool", path)
    if spec is None or spec.loader is None:
        raise VerifyError("ESCROW_TOOL_UNLOADABLE")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def open_mapping(payload_path: str, key_path: str, tool_path: str) -> list[dict[str, Any]]:
    """Deschide mapping-ul prin mecanismul autorizat. NU il scrie niciodata pe disc."""
    blob = io.open(payload_path, "rb").read()
    got = hashlib.sha256(blob).hexdigest()[:16]
    if got != EXPECTED_PAYLOAD_SHA16:
        raise VerifyError(f"PAYLOAD_SHA256_MISMATCH: {got} != {EXPECTED_PAYLOAD_SHA16}")
    tool = _load_tool(tool_path)
    plain = tool.open_(blob, io.open(key_path, "rb").read())   # HMAC invalid -> ridica
    doc = json.loads(plain)
    windows = doc["mapping_ID_to_window"]
    if not isinstance(windows, list):
        raise VerifyError("MAPPING_SHAPE_INVALID")
    return windows


def verify(payload_path: str, key_path: str, tool_path: str,
           *, quiet: bool = False) -> tuple[int, int, list[str]]:
    """Intoarce (potriviri, total, esecuri). Nu ridica la nepotrivire de ancora."""
    def say(msg: str) -> None:
        if not quiet:
            print(msg)

    say("=" * 74)
    say("VERIFICARE REPRODUCTIBILITATE ESCROW — RANGE V4.3")
    say("=" * 74)

    corpus = build_canonical_corpus()
    n_bars = len(corpus["time"])
    say(f"corpus canonic reconstruit : {n_bars} bare (asteptat {CORPUS_SPEC['expected_rows']})")
    fp = corpus_fingerprint(corpus)
    if fp != EXPECTED_CORPUS_FINGERPRINT:
        raise VerifyError(f"CORPUS_FINGERPRINT_MISMATCH: {fp}")
    say(f"amprenta corpus            : {fp}")
    say(f"reteta                     : {BARS_SHA256_RECIPE_VERSION}")

    windows = open_mapping(payload_path, key_path, tool_path)
    if len(windows) != EXPECTED_N_WINDOWS:
        raise VerifyError(f"WINDOW_COUNT_MISMATCH: {len(windows)}")
    ids = [w["id"] for w in windows]
    if len(set(ids)) != EXPECTED_N_WINDOWS:
        raise VerifyError("DUPLICATE_WINDOW_ID")

    hist: dict[int, int] = {}
    for w in windows:
        hist[w["L"]] = hist.get(w["L"], 0) + 1
    if hist != EXPECTED_LENGTH_HISTOGRAM:
        raise VerifyError(f"LENGTH_HISTOGRAM_MISMATCH: {hist}")
    total = sum(w["L"] for w in windows)
    if total != EXPECTED_TOTAL_BARS:
        raise VerifyError(f"TOTAL_BARS_MISMATCH: {total}")
    by_id = {w["id"]: w["L"] for w in windows}
    for wid, length in EXPECTED_CORRECTED.items():
        if by_id.get(wid) != length:
            raise VerifyError(f"CORRECTED_LENGTH_MISMATCH: {wid}")
    say(f"ferestre                   : {len(windows)}, ID-uri unice, "
        f"16x96 + 16x288 + 16x480 = {total} bare")
    say("corectii 046/047/048       : 288 / 96 / 480  OK")
    say("-" * 74)

    ok, failures = 0, []
    for w in windows:
        # fereastra RANDATA, interval semi-deschis
        got = window_bars_sha256(corpus, w["render_start"], w["render_end"])
        if got == w["bars_sha256"]:
            ok += 1
        else:
            failures.append(w["id"])            # numai ID-ul abstract
    say(f"ancore reproduse           : {ok}/{len(windows)}")
    if failures:
        say(f"ferestre NEREPRODUSE       : {', '.join(failures)}")
    say("=" * 74)
    say("REZULTAT: " + ("PASS 48/48" if ok == len(windows) and not failures else "FAIL"))
    return ok, len(windows), failures


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Verifica reproductibilitatea ancorelor escrow.")
    p.add_argument("--payload", required=True)
    p.add_argument("--key", required=True)
    p.add_argument("--tool", required=True)
    p.add_argument("--quiet", action="store_true")
    a = p.parse_args(argv)
    try:
        ok, total, failures = verify(a.payload, a.key, a.tool, quiet=a.quiet)
    except Exception as e:                       # fail-closed pe orice exceptie
        print(f"VERIFICARE ESUATA: {type(e).__name__}: {e}")
        return 2
    return 0 if (ok == total and not failures) else 1


if __name__ == "__main__":
    raise SystemExit(main())
