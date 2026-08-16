"""FLOW B — HYPOTHESIS GENERATOR (toward 300). Parameterized signal builder + grid over the explorable
dimensions (entry · stop · exit), per causal family. Each grid cell = a DISTINCT pre-registered
hypothesis with a run_hash; semantic duplicates are de-duped by run_hash BEFORE running. RANGE excluded.

Regime is causal (edge_research.regime); trend strategies fire ONLY in eligible TREND episodes.
Exit is expressed in the canonical menu (rr / trailing / time) so the ratified evaluator runs them
identically. Logic is SEPARATE from the evaluator.
"""
from __future__ import annotations
import os, sys, hashlib, itertools
import numpy as np
for _c in [os.environ.get("RATIFIED_CODE_DIR"),
           r"C:\Users\MEDION~1\AppData\Local\Temp\claude\C--Users-MEDION-GAMING-tradingview-mcp\44ba92ba-04ad-40f2-a48e-0ee6a8aca893\scratchpad\ratified_code\code"]:
    if _c and os.path.isdir(_c):
        if _c not in sys.path:
            sys.path.insert(0, _c)
        break
from edge_research._screen import Trade
from edge_research.regime import UP, DOWN, compression_flags
from market_structure import BreakKind


def _entries(ctx, entry, regime):
    """Return (list of (signal_idx, side), eligibility_arr) for an entry type + causal regime."""
    o, h, l, c, reg = ctx.o, ctx.h, ctx.l, ctx.c, ctx.reg
    n = ctx.n; out = []
    if entry.startswith("pullback"):
        nb = int(entry[len("pullback"):])
        tgt = UP if regime == UP else DOWN
        elig = np.array([r == tgt for r in reg])
        for i in range(nb + 1, n - 1):
            if reg[i] != tgt:
                continue
            if tgt == UP:
                pull = all(h[i-1-k] < h[i-2-k] and l[i-1-k] < l[i-2-k] for k in range(nb - 1)) and c[i] > h[i-1]
                if pull:
                    out.append((i, "long"))
            else:
                pull = all(h[i-1-k] > h[i-2-k] and l[i-1-k] > l[i-2-k] for k in range(nb - 1)) and c[i] < l[i-1]
                if pull:
                    out.append((i, "short"))
        return out, elig
    if entry == "momentum":
        tgt = UP if regime == UP else DOWN
        elig = np.array([r == tgt for r in reg]); exp = ctx.exp
        for i in range(1, n - 1):
            if reg[i] == tgt and exp[i]:
                if tgt == UP and c[i] > o[i]:
                    out.append((i, "long"))
                elif tgt == DOWN and c[i] < o[i]:
                    out.append((i, "short"))
        return out, elig
    if entry == "continuation":
        # DISTINCT mechanism from pullback: buy a FRESH breakout of the recent high WITHIN an uptrend
        # (buy strength), not the dip. Lookahead-safe (rolling max of prior bars, shifted).
        import pandas as pd
        tgt = UP if regime == UP else DOWN
        elig = np.array([r == tgt for r in reg])
        H = pd.Series(h); L = pd.Series(l)
        rmax = H.rolling(20).max().shift(1).to_numpy(); rmin = L.rolling(20).min().shift(1).to_numpy()
        for i in range(21, n - 1):
            if reg[i] != tgt:
                continue
            if tgt == UP and np.isfinite(rmax[i]) and c[i] > rmax[i]:
                out.append((i, "long"))
            elif tgt == DOWN and np.isfinite(rmin[i]) and c[i] < rmin[i]:
                out.append((i, "short"))
        return out, elig
    if entry in ("bos", "bos_retest"):
        elig = np.zeros(n, dtype=bool)
        def be(idx):
            for bl in ctx.blocks:
                if bl.start <= idx < bl.end:
                    return bl.end
            return n
        for b in ctx.breaks():
            i = b.idx
            if not (0 < i < n - 1):
                continue
            elig[i] = True
            up = b.kind is BreakKind.BOS_BULL; dn = b.kind is BreakKind.BOS_BEAR
            if not (up or dn):
                continue
            if entry == "bos":
                out.append((i, "long" if up else "short"))
            else:
                lvl = b.reference_swing.price
                for j in range(i + 1, min(i + 1 + 20, be(i))):
                    if l[j] <= lvl <= h[j]:
                        elig[j] = True
                        out.append((j, "long" if up else "short")); break
        return out, elig
    if entry == "comp_break":
        comp = compression_flags(ctx.atr); exp = ctx.exp; elig = np.zeros(n, dtype=bool)
        for i in np.flatnonzero(exp):
            if not (0 < i < n - 1):
                continue
            j = i - 1; hh = -np.inf; ll = np.inf; steps = 0
            while j >= 0 and comp[j] and steps < 200:
                hh = max(hh, h[j]); ll = min(ll, l[j]); j -= 1; steps += 1
            if steps < 2 or hh <= ll:
                continue
            elig[i] = True
            if c[i] > o[i] and c[i] > hh:
                out.append((i, "long")); ctx._comp_edge[i] = ll
            elif c[i] < o[i] and c[i] < ll:
                out.append((i, "short")); ctx._comp_edge[i] = hh
        return out, elig
    return [], np.zeros(n, dtype=bool)


def _stop(ctx, i, side, stype):
    o, h, l, atr = ctx.o, ctx.h, ctx.l, ctx.atr
    ref = o[min(i + 1, ctx.n - 1)]
    if stype == "swing":
        v = ctx.sl[i] if side == "long" else ctx.sh[i]
        return None if v != v else float(v)               # NaN check
    if stype == "bar":
        return float(l[i] if side == "long" else h[i])
    if stype == "range":
        v = getattr(ctx, "_comp_edge", {}).get(i)
        return None if v is None else float(v)
    if stype in ("atr1", "atr2"):
        k = 1.5 if stype == "atr1" else 2.5
        if not np.isfinite(atr[i]) or atr[i] <= 0:
            return None
        return float(ref - (1 if side == "long" else -1) * k * atr[i])
    return None


def gen_signals(ctx, spec):
    if not hasattr(ctx, "_comp_edge"):
        ctx._comp_edge = {}
    raw, elig = _entries(ctx, spec["entry"], spec["regime"])
    hold = spec["hold"]; ek = spec["exit_kind"]; ep = spec["exit_param"]
    trades = []
    for i, side in raw:
        st = _stop(ctx, i, side, spec["stop"])
        if st is None:
            continue
        ref = ctx.o[min(i + 1, ctx.n - 1)]
        if (side == "long" and st >= ref) or (side == "short" and st <= ref):
            continue
        trades.append(Trade(i, side, float(st), hold, exit_kind=ek, exit_param=ep))
    return trades, elig


GENERATOR_VERSION = "flowb_gen_v2"

# entry -> economic MECHANISM CLUSTER (pullback2/3/4 are the SAME cluster, not distinct mechanisms).
MECHANISM = {"pullback2": "pullback", "pullback3": "pullback", "pullback4": "pullback",
             "momentum": "momentum", "continuation": "continuation",
             "comp_break": "compression_breakout", "bos": "breakout_confirmation",
             "bos_retest": "breakout_retest"}
RATIONALE = {"pullback": "buy the retracement, resume the trend", "momentum": "enter on trend-direction impulse",
             "continuation": "buy a fresh breakout of the recent extreme within the trend",
             "compression_breakout": "range compresses then expands; trade the expansion",
             "breakout_confirmation": "structure break (body-BOS) confirms the transition",
             "breakout_retest": "structure break then a retest of the broken level"}
CLUSTER_BUDGET = 44          # max micro-variants per (family,regime,mechanism) cluster -> no monopoly


def cluster_of(family, regime, entry):
    return f"{family}|{regime}|{MECHANISM.get(entry, entry)}"


_HSF_FIELDS = ("regime", "entry", "stop", "hold", "exit_kind", "exit_param", "position_at_regime_end")


def hypothesis_semantic_fingerprint(spec):
    """HYPOTHESIS identity = the ECONOMIC LOGIC only (regime, signal/entry, stop, exit, holding,
    position_at_regime_end). Role: economic dedup, candidate identity, the m count. The SAME hypothesis
    re-run under a different evaluator/cost/router keeps THIS fingerprint and the SAME m."""
    return hashlib.md5(str(tuple((k, spec.get(k)) for k in _HSF_FIELDS)).encode()).hexdigest()[:12]


# kept as an alias so existing dedup callers keep working; identity role is the HSF.
run_hash = hypothesis_semantic_fingerprint


def evaluation_run_hash(hsf, run_context):
    """RUN identity = the exact EVALUATION (HSF + data_identity + evaluator/engine + measurement contract
    + N1 contract + router + eligibility + cost model + snapshot identities + classifier + impl commit).
    Role: comparability + reproduction. Changing evaluator/cost/router/data => NEW run_hash, SAME hsf/m if
    the economic logic is unchanged. NOT reducible to the economic config."""
    payload = dict(hsf=hsf, **{k: run_context.get(k) for k in sorted(run_context)})
    return hashlib.sha256(str(sorted(payload.items())).encode()).hexdigest()[:16]


def semantic_fingerprint(family, regime, entry, direction):
    """Economic logic only (mechanism cluster + direction), NO microparameters -> semantic-duplicate check."""
    return hashlib.md5(f"{cluster_of(family, regime, entry)}|{direction}".encode()).hexdigest()[:10]


# ── the CATALOG: cluster-budgeted declarative hypotheses across the authorized mechanisms ──
EXITS = [("time", 20.0, "time20"), ("time", 40.0, "time40"), ("time", 60.0, "time60"),
         ("rr", 2.0, "rr2"), ("rr", 3.0, "rr3"), ("rr", 1.5, "rr1_5"), ("trailing", None, "trail")]
STOPS_TREND = ["swing", "bar", "atr1", "atr2", "atr3"]
STOPS_BREAK = ["swing", "bar", "atr2", "atr3"]


def build_grid():
    specs = []
    seen = set()
    cluster_count = {}
    def add(family, regime, entry, direction, stop, hold, ek, ep, exlabel):
        cl = cluster_of(family, regime, entry)
        if cluster_count.get(cl, 0) >= CLUSTER_BUDGET:
            return  # cluster budget reached -> move on (no pullback monopoly)
        spec = dict(family=family, regime=regime, entry=entry, stop=stop, hold=int(hold), exit_kind=ek,
                    exit_param=(float(ep) if ep is not None else None),
                    position_at_regime_end="HOLD_UNTIL_STRATEGY_EXIT")
        rh = hypothesis_semantic_fingerprint(spec)
        if rh in seen:
            return
        seen.add(rh); cluster_count[cl] = cluster_count.get(cl, 0) + 1
        specs.append(dict(cell=f"{family} × {entry}", run_hash=rh, hypothesis_semantic_fingerprint=rh,
                          exit_label=exlabel,
                          mechanism_cluster=cl, generator_version=GENERATOR_VERSION,
                          economic_rationale=RATIONALE.get(MECHANISM.get(entry, entry), ""),
                          direction=direction, parameter_neighborhood=dict(stop=stop, exit=exlabel, hold=int(hold)),
                          **spec))
    for reg, fam in [(UP, "TREND_UP"), (DOWN, "TREND_DOWN")]:
        d = "long" if reg == UP else "short"
        for entry in ["pullback2", "pullback3", "pullback4", "momentum", "continuation"]:
            for stop in STOPS_TREND:
                for ek, ep, xl in EXITS:
                    hold = int(ep) if ek == "time" else 40
                    add(fam, reg, entry, d, stop, hold, ek, ep, xl)
    for stop in ["range"] + STOPS_BREAK:
        for ek, ep, xl in EXITS:
            hold = int(ep) if ek == "time" else 40
            add("COMPRESSION", "COMPRESSION", "comp_break", "break", stop, hold, ek, ep, xl)
    for entry in ["bos", "bos_retest"]:
        for stop in STOPS_BREAK:
            for ek, ep, xl in EXITS:
                hold = int(ep) if ek == "time" else 40
                add("BREAKOUT_TRANSITION", "BREAKOUT_TRANSITION", entry, "break", stop, hold, ek, ep, xl)
    return specs


if __name__ == "__main__":
    g = build_grid()
    print(f"grid: {len(g)} distinct hypotheses")
    from collections import Counter
    print(Counter(s["family"] for s in g))
