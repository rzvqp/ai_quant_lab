"""Reconstructia DETERMINISTA a corpusului canonic de 197.094 bare + reteta `bars_sha256`.

Remediaza `ESCROW-UNREPRODUCIBLE-ANCHOR` (Red Team RT-RANGE-0009, commit e504fcf).

NU citeste etichete. NU ruleaza detectorul. NU calculeaza metrici semantice.
NU publica timestampuri, bare sau mapping-ul ID->fereastra.
"""
from __future__ import annotations

import hashlib
from typing import Any

import numpy as np

# ─────────────────────── ancorele normative ale reconstructiei ───────────────────────

CORPUS_SPEC: dict[str, Any] = {
    # De ce ACEST repo: loaderul din `ai_quant_lab-wp5b` returneaza 130.491 bare pentru
    # ACELASI timeframe, fiindca manifestul lui declara 3 segmente de discovery, nu 4.
    # Divergenta e deja consemnata in manifestul Statisticianului; ramura de mai jos e
    # singura care produce cele PATRU blocuri oficiale.
    "repo_branch": "alpha-automation-v1",
    "loader_module": "edge_research/_common.py",
    "loader_entry": "load",
    "timeframe_key": "M15_v2",
    "split_id": "pre_holdout_2025-10-23T09-15-00Z_v1",
    "cutoff": "2025-10-23T09:15:00Z",
    "source_file": "data/market/OANDA_XAUUSD_M15.csv",
    "source_sha256": "57f4ed9544993c8fbba28d9c1e3319f2e0665ef5db211fb09d9f4622222ccd37",
    "expected_rows": 197094,
    "expected_segments": 4,
    "manifest_entry_fingerprint_M15_v2": "5d1cccabc3be9784ab8164ac79303774",
    "recipe_version": "canonical_corpus_v1",
}

# Intrarea `M15_v2` din manifest e BYTE-IDENTICA la v2.7.92 (6ae0837), v2.7.93 (96a7352)
# si v2.7.94 (14d4c22) — deci corpusul e invariant peste data sigilarii, iar
# reproductibilitatea NU depinde de o versiune de manifest scrisa dupa sigilare.
MANIFEST_VERSIONS_WITH_IDENTICAL_ENTRY = ("2.7.92", "2.7.93", "2.7.94")


class CorpusError(RuntimeError):
    """Reconstructia corpusului a esuat fail-closed."""


def build_canonical_corpus() -> dict[str, np.ndarray]:
    """Reconstruieste cele 197.094 bare canonice. Fail-closed la orice abatere."""
    import edge_research._common as common

    df, meta = common.load(
        CORPUS_SPEC["timeframe_key"],
        data_split_id=CORPUS_SPEC["split_id"],
        cutoff=CORPUS_SPEC["cutoff"],
    )
    if len(df) != CORPUS_SPEC["expected_rows"]:
        raise CorpusError(
            f"CORPUS_ROW_COUNT_MISMATCH: {len(df)} != {CORPUS_SPEC['expected_rows']}")
    if meta.get("n_discovery_segments") != CORPUS_SPEC["expected_segments"]:
        raise CorpusError(
            f"CORPUS_SEGMENT_COUNT_MISMATCH: {meta.get('n_discovery_segments')} "
            f"!= {CORPUS_SPEC['expected_segments']}")
    if meta.get("data_file_sha256") != CORPUS_SPEC["source_sha256"]:
        raise CorpusError("CORPUS_SOURCE_SHA256_MISMATCH")

    df = df.reset_index(drop=True)
    return {
        "time": df["time"].to_numpy(dtype="int64"),
        "open": df["open"].to_numpy(dtype="float64"),
        "high": df["high"].to_numpy(dtype="float64"),
        "low": df["low"].to_numpy(dtype="float64"),
        "close": df["close"].to_numpy(dtype="float64"),
    }


# ─────────────────────── reteta byte-exacta `bars_sha256` ───────────────────────

BARS_SHA256_RECIPE_VERSION = "bars_sha256_v1"


def bars_sha256(high: np.ndarray, low: np.ndarray,
                open_: np.ndarray, close: np.ndarray) -> str:
    """Reteta NORMATIVA, recuperata din unealta de sigilare si verificata 48/48.

    Ordinea campurilor e **H, L, O, C** — NU `OHLC`. Exact aceasta inversiune a facut ca
    toate conventiile de tip OHLC incercate de Red Team (~24) si de mine (~7.700) sa esueze.

    Serializare, byte cu byte:
      1. patru vectori separati, CONCATENATI in ordinea high, low, open, close
         (concatenare pe COLOANE, nu intretesere pe randuri);
      2. fiecare valoare inmultita cu 1e6 si convertita la `int64` — trunchiere spre zero,
         conventia `numpy.astype`, NU rotunjire;
      3. `ndarray.tobytes()` — 8 bytes per element, little-endian, ordine C;
      4. `sha256` peste fluxul de bytes rezultat, redat ca hex minuscul.

    Fara timestamp, fara volum, fara header, fara separatori, fara text.
    """
    if not (len(high) == len(low) == len(open_) == len(close)):
        raise CorpusError("BARS_LENGTH_MISMATCH")
    blob = np.concatenate([
        (high * 1e6).astype("int64"),
        (low * 1e6).astype("int64"),
        (open_ * 1e6).astype("int64"),
        (close * 1e6).astype("int64"),
    ])
    return hashlib.sha256(blob.tobytes()).hexdigest()


def window_bars_sha256(corpus: dict[str, np.ndarray], start: int, end: int) -> str:
    """Ancora unei ferestre.

    ★ Se aplica pe fereastra **RANDATA** `[render_start, render_end)` — cea cu context
    24 + 24 — NU pe fereastra canonica `[canonical_index_start, canonical_index_end)`.
    Ambiguitatea era declarata explicit deschisa de Red Team (§7.2); e transata aici
    empiric: fereastra randata da 48/48, cea canonica da 0/48.
    Intervalul e SEMI-DESCHIS: `start` inclus, `end` exclus.
    """
    return bars_sha256(corpus["high"][start:end], corpus["low"][start:end],
                       corpus["open"][start:end], corpus["close"][start:end])


def corpus_fingerprint(corpus: dict[str, np.ndarray]) -> str:
    """Amprenta intregului corpus canonic, sub ACEEASI conventie ca ancorele."""
    return bars_sha256(corpus["high"], corpus["low"], corpus["open"], corpus["close"])
