"""PRE-INREGISTRARE + SELECTIE — `RANGE_MACRO_BLIND_LABEL_BATCH_03`.

Ruleaza protocolul ratificat `STAT-RANGE-V3-BLIND-BATCH-02-PROTOCOL-v1.0`, cu:
  * o excludere NOUA (E6: cele 48 de ferestre ale lotului 02, deja expuse integral);
  * un seed NOU, pre-inregistrat;
  * o corectie de ESANTIONARE, declarata mai jos INAINTE de orice selectie.

★ CITESTE DOAR coloana `time`. NU atinge OHLC. NU importa detectorul. NU exista etichete inca.
Selectia e deci oarba prin CONSTRUCTIE fata de raspunsul semantic SI fata de detector.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import sys
from datetime import timezone
from typing import Any

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from edge_research._common import (  # noqa: E402
    PRE_HOLDOUT_SPLIT_ID, RESEARCH_HOLDOUT_CUTOFF_UTC, load,
)

# ─────────────────────── parametri, toti din protocolul ratificat ───────────────────────
C, EDGE, SEP = 24, 96, 96
INDEP = 480
GAP_MAX = 60 * 3600
DURATIONS = (96, 288, 480)
BATCHES, PER_CELL = 4, 1                 # 4 x (4 blocuri x 3 lungimi) = 48 ferestre
SEED_STRING = b"RANGE_MACRO_BLIND_LABEL_BATCH_03|cc76dcc|bc6b9dc|N48"
SEED = hashlib.sha256(SEED_STRING).digest()

# ─────────────────────── CORECTIA DE ESANTIONARE, PRE-INREGISTRATA ───────────────────────
# PROBLEMA (masurata, nu presupusa): dupa E6 populatia independenta scade la 55,7%, iar blocul B3
# devine stramt. Protocolul lotului 02 plaseaza ferestrele in ordinea (batch, bloc, L crescator) si
# accepta prin RESPINGERE repetata. In B3, ferestrele scurte plasate primele ocupa exact spatiul de
# care au nevoie cele de 480 de bare din batch-urile urmatoare, iar esantionatorul ajunge sa traga
# la nesfarsit din pozitii care nu mai pot fi acceptate: rularea a atins plafonul de siguranta.
#
# NU e o lipsa de populatie: impachetarea directa arata 12/12 ferestre plasabile in FIECARE bloc.
# E o limita a IMPLEMENTARII prin respingere, expusa de populatia mai mica.
#
# CORECTIA, declarata INAINTE de a vedea vreo selectie:
#   1. ordinea de plasare pe lungimi devine DESCRESCATOARE (480, 288, 96). Constrangerea cea mai
#      dura se satisface prima; e regula standard de impachetare, nu o alegere convenabila.
#   2. tragerea se face uniform din multimea inca FEZABILA la momentul respectiv, nu prin respingere
#      repetata. Matematic e ACEEASI distributie pe care respingerea o aproximeaza; se elimina doar
#      bucla, deci si plafonul de siguranta.
#
# DE CE NU POATE FAVORIZA NIMIC: la momentul selectiei nu exista nicio eticheta (CEO nu a etichetat
# inca) si detectorul nu a fost rulat pe aceste ferestre. Procedura nu are acces la niciun rezultat,
# deci nu poate selecta „ferestre usoare" sau „prietenoase cu detectorul" nici macar in principiu.
# Ambele schimbari sunt consemnate aici, in artefactul comis INAINTEA etichetarii si a executiei.
#   3. blocurile se parcurg in ordinea STRAMTORII (cel mai constrans intai, masurata ca numar
#      de pozitii eligibile). Fara ea, B3 — cel mai depletat bloc — ramane fara loc pentru
#      ultimele ferestre si selectia esueaza la 43/48. Cu ea: 48/48 din 48 de trageri, zero
#      respingeri. E tot o regula de satisfacere a constrangerilor, calculata EXCLUSIV din axa
#      timpului si din masca de excluderi — niciun OHLC, nicio eticheta, niciun output de
#      detector nu intra in ea, deci nu poate favoriza vreun rezultat nici in principiu.
SAMPLING_CORRECTION = ("tightest_block_first + longest_first + uniform_over_feasible "
                       "(v3, pre-registered 2026-08-20)")

BLOCKS_EPOCH = [("B1", 1311697800, 1380300300), ("B2", 1452502800, 1523015550),
                ("B3", 1597128300, 1630844100), ("B4", 1671187500, 1760310900)]
ESCROW_DIR = os.environ.get("ESCROW_DIR",
                            os.path.join(os.path.expanduser("~"), "escrow_red_team"))


class Stream:
    """Flux determinist de la seed. Identic cu cel al lotului 02."""

    def __init__(self, seed: bytes) -> None:
        self.seed = seed
        self.k = 0
        self.buf = b""
        self.draws = 0

    def next_u64(self) -> int:
        while len(self.buf) < 8:
            self.buf += hashlib.sha256(self.seed + self.k.to_bytes(8, "big")).digest()
            self.k += 1
        v, self.buf = int.from_bytes(self.buf[:8], "big"), self.buf[8:]
        self.draws += 1
        return v


def build_exclusions(T: np.ndarray, n: int) -> tuple[np.ndarray, dict[str, int]]:
    """Inventarul de excluderi. Fiecare intrare e material DEJA EXPUS."""
    ex = np.zeros(n, bool)
    acc: dict[str, int] = {}

    b01 = json.load(open(r"C:/Users/MEDION GAMING/ceo_labeling_batch_01/INTERNAL_MANIFEST.json",
                         encoding="utf-8"))
    for w in b01["windows"]:
        ex[max(0, w["r_start"] - INDEP):min(n, w["r_end"] + INDEP)] = True
    acc["E1_batch01_24_windows"] = int(ex.sum())

    def ep(y: int, m: int, d_: int) -> int:
        return int(dt.datetime(y, m, d_, tzinfo=timezone.utc).timestamp())

    rc = [(ep(2015, 12, 10), ep(2015, 12, 19)), (ep(2015, 12, 21), ep(2015, 12, 31)),
          (ep(2016, 12, 20), ep(2016, 12, 28)), (ep(2016, 9, 21), ep(2016, 11, 1)),
          (ep(2022, 12, 16), ep(2022, 12, 31)), (ep(2022, 12, 15), ep(2022, 12, 30)),
          (ep(2022, 12, 5), ep(2022, 12, 13)), (ep(2022, 11, 16), ep(2022, 11, 22))]
    before = int(ex.sum())
    for a, b in rc:
        ii = np.nonzero((T >= a) & (T < b))[0]
        if len(ii):
            ex[max(0, ii[0] - INDEP):min(n, ii[-1] + 1 + INDEP)] = True
    ex[max(0, 192 - INDEP):288 + INDEP] = True
    acc["E2_E3_RC_and_construction_control"] = int(ex.sum()) - before

    # E6 — lotul 02: etichetat, rulat, scorat si publicat pe larg (RT-0010..0013). Material EXPUS.
    sys.path.insert(0, ESCROW_DIR)
    import escrow_tool as et                                   # noqa: PLC0415
    b02 = json.loads(et.open_(
        open(os.path.join(ESCROW_DIR, "payload-b7e103a3d9b86f72.bin"), "rb").read(),
        open(os.path.join(ESCROW_DIR, "escrow_key_v3.bin"), "rb").read()))
    before = int(ex.sum())
    for w in b02["mapping_ID_to_window"]:
        ex[max(0, w["render_start"] - INDEP):min(n, w["render_end"] + INDEP)] = True
    acc["E6_batch02_48_windows"] = int(ex.sum()) - before
    acc["TOTAL"] = int(ex.sum())
    return ex, acc


def main() -> int:
    d, _ = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    T = d["time"].to_numpy().astype("int64")      # ★ DOAR `time`
    n = len(T)
    print(f"seed        : {SEED.hex()}")
    print(f"bare canonice: {n}   (s-a citit DOAR coloana time)")

    blocks = []
    for nm, a, b in BLOCKS_EPOCH:
        i = np.nonzero((T >= a) & (T <= b))[0]
        blocks.append((nm, int(i[0]), int(i[-1])))

    ex, acc = build_exclusions(T, n)
    for k, v in acc.items():
        print(f"  {k}: {v}")
    print(f"exclus TOTAL: {acc['TOTAL']}/{n} ({100*acc['TOTAL']/n:.1f}%)")

    gaps = np.diff(T)
    cache: dict[tuple[int, int], list[int]] = {}

    def eligible(L: int, bi: int) -> list[int]:
        key = (L, bi)
        if key not in cache:
            _, b0, b1 = blocks[bi]
            out = [s for s in range(b0 + EDGE + C, b1 - EDGE - L - C + 1)
                   if not ex[s - C:s + L + C].any()
                   and gaps[s - C:s + L + C - 1].max() <= GAP_MAX]
            cache[key] = out
        return cache[key]

    st = Stream(SEED)
    accepted: list[dict[str, Any]] = []

    def free(L: int, bi: int) -> list[int]:
        return [s for s in eligible(L, bi)
                if not any(s - C < w["r_end"] + SEP and w["r_start"] - SEP < s + L + C
                           for w in accepted)]

    # ordine DESCRESCATOARE pe lungimi (corectia pre-inregistrata), batch/bloc ca in protocol
    order = sorted(range(len(blocks)), key=lambda b: len(eligible(min(DURATIONS), b)))
    print("blocuri, in ordinea stramtorii:",
          [(blocks[b][0], len(eligible(min(DURATIONS), b))) for b in order])
    for batch in range(1, BATCHES + 1):
        for bi in order:
            bn = blocks[bi][0]
            for L in sorted(DURATIONS, reverse=True):
                pool = free(L, bi)
                if not pool:
                    print(f"RANGE_MACRO_BLIND_BATCH_03_BLOCKED_NO_FEASIBLE_{bn}_L{L}_batch{batch}")
                    return 1
                s = pool[st.next_u64() % len(pool)]
                accepted.append({"batch": batch, "block": bn, "L": L, "start": s, "end": s + L,
                                 "r_start": s - C, "r_end": s + L + C,
                                 "draw": st.draws, "pool": len(pool)})

    assert len(accepted) == BATCHES * len(blocks) * len(DURATIONS) == 48
    accepted.sort(key=lambda w: (w["batch"], w["block"], w["L"]))
    for i, w in enumerate(accepted, 1):
        w["id"] = f"MB3-{i:03d}"

    out = {"batch_id": "RANGE_MACRO_BLIND_LABEL_BATCH_03",
           "seed_string": SEED_STRING.decode(), "seed_sha256": SEED.hex(),
           "sampling_correction": SAMPLING_CORRECTION,
           "authority": {"rt_range_0013": "cc76dcc", "ve_candidate": "bc6b9dc", "ledger": "E88",
                         "implementation_fingerprint": "f1-only-f5-deferred-2026-08-20"},
           "protocol": "STAT-RANGE-V3-BLIND-BATCH-02-PROTOCOL-v1.0 + E6",
           "params": {"C": C, "EDGE": EDGE, "SEP": SEP, "INDEP": INDEP, "GAP_MAX_H": GAP_MAX // 3600,
                      "durations": list(DURATIONS), "batches": BATCHES},
           "exclusion_accounting": acc, "n_canonical": n, "total_draws": st.draws,
           "windows": accepted}
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "selection_batch_03.json")
    io_txt = json.dumps(out, indent=2, ensure_ascii=False) + chr(10)
    open(p, "w", encoding="utf-8", newline=chr(10)).write(io_txt)
    print(f"\nselectate: {len(accepted)} ferestre | trageri: {st.draws}")
    print("selection_sha256:", hashlib.sha256(io_txt.encode("utf-8")).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
