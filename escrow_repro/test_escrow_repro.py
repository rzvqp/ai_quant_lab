"""Testele obligatorii (§7) pentru remedierea `ESCROW-UNREPRODUCIBLE-ANCHOR`.

Pozitive SI negative. Niciun test nu tipareste date sigilate.
Locatia escrow-ului (in afara Git) se da prin `ESCROW_DIR`; implicit `~/escrow_red_team`.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, REPO)
sys.path.insert(0, HERE)

from canonical_corpus import (  # noqa: E402
    CORPUS_SPEC, CorpusError, bars_sha256, build_canonical_corpus,
    corpus_fingerprint, window_bars_sha256,
)
import verify_range_v43_escrow as V  # noqa: E402

ESCROW_DIR = os.environ.get(
    "ESCROW_DIR", os.path.join(os.path.expanduser("~"), "escrow_red_team"))
PAYLOAD = os.path.join(ESCROW_DIR, "payload-b7e103a3d9b86f72.bin")
KEY = os.path.join(ESCROW_DIR, "escrow_key_v3.bin")
KEY_WRONG = os.path.join(ESCROW_DIR, "escrow_key.bin")
TOOL = os.path.join(ESCROW_DIR, "escrow_tool.py")


@pytest.fixture(scope="module")
def corpus() -> dict[str, np.ndarray]:
    return build_canonical_corpus()


@pytest.fixture(scope="module")
def windows() -> list[dict[str, object]]:
    return V.open_mapping(PAYLOAD, KEY, TOOL)


# ────────────────────────────── POZITIVE ──────────────────────────────

def test_01_48_din_48_ancore_reproduse(corpus, windows):
    ok = sum(1 for w in windows
             if window_bars_sha256(corpus, w["render_start"], w["render_end"])
             == w["bars_sha256"])
    assert ok == 48, f"reproduse doar {ok}/48"


def test_02_zero_lipsa_zero_suplimentare(windows):
    ids = [w["id"] for w in windows]
    assert len(ids) == 48 and len(set(ids)) == 48
    assert all("bars_sha256" in w and w["bars_sha256"] for w in windows)


def test_03_exact_13824_bare(windows):
    assert sum(w["L"] for w in windows) == 13824


def test_04_distributia_16x96_16x288_16x480(windows):
    hist: dict[int, int] = {}
    for w in windows:
        hist[w["L"]] = hist.get(w["L"], 0) + 1
    assert hist == {96: 16, 288: 16, 480: 16}


def test_05_corectiile_046_047_048(windows):
    by = {w["id"]: w["L"] for w in windows}
    assert by["BLIND-046"] == 288 and by["BLIND-047"] == 96 and by["BLIND-048"] == 480


def test_06_corpus_197094_si_amprenta(corpus):
    assert len(corpus["time"]) == CORPUS_SPEC["expected_rows"] == 197094
    assert corpus_fingerprint(corpus) == V.EXPECTED_CORPUS_FINGERPRINT


def test_07_determinism_doua_executii_consecutive():
    a = corpus_fingerprint(build_canonical_corpus())
    b = corpus_fingerprint(build_canonical_corpus())
    assert a == b == V.EXPECTED_CORPUS_FINGERPRINT


def _run(cwd: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    e = dict(os.environ)
    if env:
        e.update(env)
    return subprocess.run(
        [sys.executable, os.path.join(HERE, "verify_range_v43_escrow.py"),
         "--payload", PAYLOAD, "--key", KEY, "--tool", TOOL],
        capture_output=True, text=True, cwd=cwd, env=e)


def test_08_determinism_doua_directoare_curate():
    with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
        r1, r2 = _run(d1), _run(d2)
    assert r1.returncode == 0 and r2.returncode == 0
    assert "PASS 48/48" in r1.stdout and "PASS 48/48" in r2.stdout
    assert V.EXPECTED_CORPUS_FINGERPRINT in r1.stdout


def test_09_independenta_de_locale():
    with tempfile.TemporaryDirectory() as d:
        r = _run(d, {"LC_ALL": "tr_TR.UTF-8", "LANG": "tr_TR.UTF-8"})
    assert r.returncode == 0 and "PASS 48/48" in r.stdout


def test_10_independenta_de_calea_absoluta():
    with tempfile.TemporaryDirectory() as d:
        r = _run(d)
    assert r.returncode == 0
    assert d not in r.stdout


# ────────────────────────────── NEGATIVE ──────────────────────────────

def test_11_refuz_la_corpus_gresit(corpus, windows):
    w = windows[0]
    shifted = window_bars_sha256(corpus, w["render_start"] + 1, w["render_end"] + 1)
    assert shifted != w["bars_sha256"]


def test_12_refuz_la_schema_gresita():
    with pytest.raises(CorpusError):
        bars_sha256(np.array([1.0, 2.0]), np.array([1.0]), np.array([1.0]), np.array([1.0]))


def test_13_refuz_la_ordine_gresita_a_randurilor(corpus, windows):
    w = windows[0]
    a, b = w["render_start"], w["render_end"]
    rev = bars_sha256(corpus["high"][a:b][::-1], corpus["low"][a:b][::-1],
                      corpus["open"][a:b][::-1], corpus["close"][a:b][::-1])
    assert rev != w["bars_sha256"]


def test_14_refuz_la_ordine_gresita_a_coloanelor(corpus, windows):
    w = windows[0]
    a, b = w["render_start"], w["render_end"]
    ohlc = bars_sha256(corpus["open"][a:b], corpus["high"][a:b],
                       corpus["low"][a:b], corpus["close"][a:b])
    assert ohlc != w["bars_sha256"], "H,L,O,C si O,H,L,C nu trebuie sa coincida"


def test_15_refuz_la_modificarea_unei_singure_valori(corpus, windows):
    """O singura valoare schimbata cu UN TICK trebuie sa strice ancora.

    Un tick XAUUSD = 0,001, adica 1000 de unitati dupa scalarea 1e6 — de trei ordine de
    marime peste rezolutia retetei. Se verifica si campurile low/open/close, nu doar high.
    """
    w = windows[0]
    a, b = w["render_start"], w["render_end"]
    for field in ("high", "low", "open", "close"):
        arrs = {k: corpus[k][a:b].copy() for k in ("high", "low", "open", "close")}
        arrs[field][0] += 0.001                      # un tick
        got = bars_sha256(arrs["high"], arrs["low"], arrs["open"], arrs["close"])
        assert got != w["bars_sha256"], f"modificarea lui {field} a ramas invizibila"


def test_15b_podeaua_de_cuantizare_a_retetei(corpus, windows):
    """Limita REALA a retetei, masurata nu presupusa.

    Scalarea 1e6 urmata de trunchiere are rezolutie 1e-6 in pret, iar rotunjirea float64
    poate ABSORBI o perturbatie de exact 1e-6 (pe prima bara a ferestrei verificate asta se intampla). De la 2e-6 in
    sus detectia e ferma. Consemnat ca proprietate a ancorei, nu ca defect: marja fata de
    un tick real e de 1000x.
    """
    w = windows[0]
    a, b = w["render_start"], w["render_end"]
    base = corpus["high"][a:b]
    ref = bars_sha256(base, corpus["low"][a:b], corpus["open"][a:b], corpus["close"][a:b])
    hi = base.copy(); hi[0] += 2e-6
    got = bars_sha256(hi, corpus["low"][a:b], corpus["open"][a:b], corpus["close"][a:b])
    assert ref == w["bars_sha256"] and got != ref


def test_16_refuz_la_mutatia_unui_bit():
    blob = bytearray(io.open(PAYLOAD, "rb").read())
    blob[len(blob) // 2] ^= 0x01
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "payload-b7e103a3d9b86f72.bin")
        io.open(p, "wb").write(bytes(blob))
        with pytest.raises(Exception):
            V.open_mapping(p, KEY, TOOL)


def test_17_refuz_la_mapping_modificat(corpus, windows):
    tampered = [dict(w) for w in windows]
    orig = tampered[0]["bars_sha256"]
    tampered[0]["bars_sha256"] = "0" * 64
    ok = sum(1 for w in tampered
             if window_bars_sha256(corpus, w["render_start"], w["render_end"])
             == w["bars_sha256"])
    assert ok == 47 and orig != "0" * 64


def test_18_refuz_la_manifest_modificat():
    """Poarta REALA de manifest, invocata efectiv — nu doar aritmetica pe hash."""
    from edge_research.split_manifest import ManifestError, load_manifest, MANIFEST_PATH

    assert load_manifest(MANIFEST_PATH)["content_hash"]["value"]      # cel curat trece
    d = json.load(io.open(MANIFEST_PATH, encoding="utf-8"))
    d["version"] = "0.0.0-tampered"                                   # invalideaza content_hash
    with tempfile.TemporaryDirectory() as t:
        bad = os.path.join(t, "split_manifest.json")
        io.open(bad, "w", encoding="utf-8", newline=chr(10)).write(
            json.dumps(d, indent=2, ensure_ascii=False) + chr(10))
        with pytest.raises(ManifestError):
            load_manifest(bad)


def test_19_refuz_la_cheie_gresita():
    if not os.path.exists(KEY_WRONG):
        pytest.skip("a doua cheie nu e disponibila")
    with pytest.raises(Exception):
        V.open_mapping(PAYLOAD, KEY_WRONG, TOOL)


def test_20_reteta_e_fereastra_RANDATA_nu_L(corpus, windows):
    ok_L = sum(1 for w in windows
               if window_bars_sha256(corpus, w["canonical_index_start"],
                                     w["canonical_index_end"]) == w["bars_sha256"])
    assert ok_L == 0, "fereastra canonica NU trebuie sa reproduca ancorele"


def test_21_outputul_nu_contine_date_sigilate(windows):
    with tempfile.TemporaryDirectory() as d:
        r = _run(d)
    out = r.stdout
    for w in windows:
        assert str(w["start_utc"]) not in out
        assert str(w["end_utc"]) not in out
        assert str(w["canonical_index_start"]) not in out
        assert str(w["render_start"]) not in out
    for forbidden in ("start_utc", "end_utc", "canonical_index", "render_start"):
        assert forbidden not in out
