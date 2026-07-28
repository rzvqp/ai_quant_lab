#!/usr/bin/env python3
"""Mandate 2.7 -- generate derived HTF context (H1/H4/D1) from M15_v2 under the manifest's
context_derived_htf rule: an HTF bar exists ONLY IF its fixed calendar-aligned window falls entirely
within a SINGLE M15_v2 discovery block. No straddling, no truncation, no partial/flagged bars.

Anchoring matches the lab's code/resample_ny.py: H1 = UTC hour; H4/D1 = 17:00 America/New_York
(DST-aware). Output is the lab-native 7-column format (time,open,high,low,close,volume,sub) where `sub`
counts the constituent M15 bars. Reads coordinates verbatim from config/split_manifest.json.
Writes CSVs (LF) + prints hashes and the coverage/elimination accounting. Modifies no existing file.
"""
import argparse
import hashlib
import json
import os

import numpy as np
import pandas as pd  # type: ignore[import-untyped]

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "config", "split_manifest.json")


def sha256_lf(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=os.path.join(ROOT, "data", "market"))
    args = ap.parse_args()

    man = json.loads(open(MANIFEST, "rb").read())
    ctx = man["context_derived_htf"]
    src_fp = man["timeframes"]["M15_v2"]["file_path"]
    src_hash = ctx["source_file_sha256"]
    src_path = os.path.join(ROOT, src_fp)
    got = sha256_lf(src_path)
    assert got == src_hash, f"M15_v2 source hash mismatch: {got} != {src_hash}"
    blocks = [(b["start_epoch"], b["end_epoch"]) for b in ctx["m15_v2_discovery_blocks"]]
    print(f"source M15_v2 {src_fp} sha256 OK; discovery blocks: {len(blocks)}")

    m = pd.read_csv(src_path).drop_duplicates("time").sort_values("time").reset_index(drop=True)
    m["dt"] = pd.to_datetime(m["time"], unit="s", utc=True)

    # anchoring keys (identical convention to code/resample_ny.py)
    ny = m["dt"].dt.tz_convert("America/New_York").dt.tz_localize(None)
    shift = ny - pd.Timedelta(hours=17)

    def to_utc(naive_ny: pd.Series) -> pd.Series:
        return naive_ny.dt.tz_localize("America/New_York", ambiguous=True,
                                       nonexistent="shift_forward").dt.tz_convert("UTC")

    keys = {
        "H1": (m["dt"].dt.floor("1h"), 3600),
        "H4": (to_utc(shift.dt.floor("4h") + pd.Timedelta(hours=17)), 14400),
        "D1": (to_utc(shift.dt.floor("D") + pd.Timedelta(hours=17)), 86400),
    }

    def in_single_block(w_start: int, w_end: int, max_comp: int) -> bool:
        # the fixed calendar window AND all constituents must lie in ONE discovery block
        return any(s <= w_start and w_end <= e and max_comp < e for s, e in blocks)

    for tf, (key, bar_sec) in keys.items():
        g = m.assign(_k=key).groupby("_k")
        agg = pd.DataFrame(dict(
            open=g["open"].first(), high=g["high"].max(), low=g["low"].min(),
            close=g["close"].last(), volume=g["volume"].sum(), sub=g["close"].count(),
            max_comp=g["time"].max(),
        )).reset_index().rename(columns={"_k": "dt"}).sort_values("dt").reset_index(drop=True)
        agg["time"] = ((agg["dt"] - pd.Timestamp("1970-01-01", tz="UTC")) // pd.Timedelta(seconds=1)).astype("int64")
        n_without = len(agg)

        w_start = agg["time"].to_numpy()
        w_end = w_start + bar_sec
        max_comp = agg["max_comp"].to_numpy()
        keep = np.array([in_single_block(int(ws), int(we), int(mc))
                         for ws, we, mc in zip(w_start, w_end, max_comp)])
        kept = agg.loc[keep].reset_index(drop=True)
        n_with = len(kept)

        # elimination accounting: straddling a block edge vs fully outside any block
        straddle = 0
        outside = 0
        per_edge: dict[str, int] = {}
        for ws, we in zip(w_start[~keep], w_end[~keep]):
            hit = None
            for i, (s, e) in enumerate(blocks):
                if ws < e and we > s:  # window overlaps this block at all
                    if s > ws or e < we:  # ...but not fully contained -> straddles this edge
                        hit = f"block{i}_{'start' if s > ws else 'end'}"
                        break
            if hit:
                straddle += 1
                per_edge[hit] = per_edge.get(hit, 0) + 1
            else:
                outside += 1

        out = os.path.join(args.outdir, f"OANDA_XAUUSD_{tf}_from_M15_v2.csv")
        with open(out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("time,open,high,low,close,volume,sub\n")
            for _, r in kept.iterrows():
                fh.write(f"{int(r['time'])},{r['open']},{r['high']},{r['low']},{r['close']},{int(r['volume'])},{int(r['sub'])}\n")
        h = sha256_lf(out)

        print(f"\n==== {tf}_from_M15_v2 ====")
        print(f"  file      : {os.path.relpath(out, ROOT)}")
        print(f"  sha256    : {h}")
        print(f"  bars WITH rule    : {n_with}")
        print(f"  bars WITHOUT rule : {n_without}   (naive resample of full file)")
        print(f"  eliminated total  : {n_without - n_with}  = straddling {straddle} + fully-outside {outside}")
        print(f"  eliminated at each block edge (straddling): {dict(sorted(per_edge.items()))}")
        # coverage WITH GAPS -- the actual covered sub-intervals, not smoothed
        print("  coverage (per discovery block, delivered bars -- NOT continuous across blocks):")
        for i, (s, e) in enumerate(blocks):
            blk = kept[(kept["time"] >= s) & (kept["time"] < e)]
            if len(blk):
                a = pd.to_datetime(int(blk["time"].min()), unit="s", utc=True)
                b = pd.to_datetime(int(blk["time"].max()), unit="s", utc=True)
                print(f"     block{i}: {len(blk):5d} bars  {a:%Y-%m-%d %H:%M}Z .. {b:%Y-%m-%d %H:%M}Z")
            else:
                print(f"     block{i}:     0 bars")


if __name__ == "__main__":
    main()
