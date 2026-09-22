"""L2 ere calendaristice (panou cu context istoric ratificat) + L3 null potrivit LONG + coada + cost."""
import os, sys, math, json
import numpy as np, pandas as pd
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
AA = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"
sys.path.insert(0, os.path.join(AA, "code"))
import mstrat, mstrat_ext as ME, htf_context_historical as HH
from alpha_lab import CFG
mstrat.TICK = 0.01
if hasattr(ME, "TICK"): ME.TICK = 0.01
def cfg_for(rt):
    c = dict(CFG); c["spread_ticks"] = rt / (2 * mstrat.TICK); c["slip_ticks"] = 0.0; return c
CB, CS = cfg_for(0.05), cfg_for(0.24)

d = mstrat.load()
T = d["time"].to_numpy(); yr = pd.to_datetime(T, unit="s", utc=True).year.to_numpy()
mon = (pd.to_datetime(T, unit="s", utc=True).year * 12 + pd.to_datetime(T, unit="s", utc=True).month).to_numpy()
def clt(r, cl):
    n = len(r); mu = r.mean()
    g = pd.DataFrame({"c": cl, "r": r}).groupby("c")["r"].agg(["sum", "count"]); G = len(g)
    resid = g["sum"].to_numpy() - g["count"].to_numpy() * mu
    se = math.sqrt(max((resid ** 2).sum() / n ** 2 * (G / max(G - 1, 1)), 1e-18))
    return mu, se, (mu / se if se > 0 else 0.0), G

SPEC = {}
for N in range(1, 52):
    for mod in (mstrat, ME):
        g = getattr(mod, f"s{N}_grammar", None); s = getattr(mod, f"s{N}_setups", None)
        if not (g and s): continue
        for h in g():
            if h["id"] in ("85dfa65a9ce1", "047d776a1bcb", "601e20753a4a"):
                SPEC[h["id"]] = (f"S{N}", h, s)
        break

print("=" * 116); print("  L2 — ERE CALENDARISTICE pe panoul cu CONTEXT ISTORIC RATIFICAT"); print("=" * 116)
dh = HH.load_mstrat_historical()
th = dh["time"].to_numpy(); yrh = pd.to_datetime(th, unit="s", utc=True).year.to_numpy()
monh = (pd.to_datetime(th, unit="s", utc=True).year * 12 + pd.to_datetime(th, unit="s", utc=True).month).to_numpy()
print(f"  panou istoric: {len(dh)} bare; acoperire context: "
      + ", ".join(f"{c}={dh[c].notna().mean():.3f}" for c in ("pdh", "h4_trend_up", "h1_trend_up")))
print(f"  NB: aceeasi definitie de strategie, panou cu acoperire mai buna a contextului (ratificat).")
print(f"      NU e o modificare a candidatului — e un test de robustete pe o sursa alternativa ratificata.\n")
ERAS = [(2011, 2014), (2014, 2017), (2017, 2020), (2020, 2023), (2023, 2027)]
HIST = {}
for hid, (fam, h, sfn) in SPEC.items():
    tb = mstrat.simulate(dh, sfn(dh, h), CB)
    r = tb.R.to_numpy(); ei = tb.ei.to_numpy(); ya = yrh[ei]
    HIST[hid] = (tb, ya)
    mu, se, t, G = clt(r, monh[ei])
    print(f"  {fam:4} {hid}: N={len(r):5d}  mean={mu:+.4f}  t_clust={t:+.2f}")
    line = []
    for a, b in ERAS:
        m = (ya >= a) & (ya < b)
        line.append(f"{a}-{b-1}: " + (f"{r[m].mean():+.3f}(n{int(m.sum()):4d})" if m.sum() >= 30 else f"   n/a(n{int(m.sum()):4d})"))
    print(f"       " + " | ".join(line))
    ok = [(a, b) for a, b in ERAS if ((ya >= a) & (ya < b)).sum() >= 30]
    pos = sum(1 for a, b in ok if r[(ya >= a) & (ya < b)].mean() > 0)
    print(f"       ere calendaristice cu N>=30: {len(ok)}  dintre care pozitive: {pos}")

print("\n" + "=" * 116); print("  L3 — NULL POTRIVIT LONG (aceeasi luna, aceeasi directie, aceeasi geometrie de risc, acelasi rr3)"); print("=" * 116)
o = d["open"].values
B = 400
rng = np.random.default_rng(11)
for hid, (fam, h, sfn) in SPEC.items():
    su = sfn(d, h)
    real = mstrat.simulate(d, su, CB)
    rr = real.R.to_numpy(); ei = real.ei.to_numpy()
    risks = np.array([abs(o[e] - s["stop"]) for e, s in
                      zip(ei, sorted([x for x in su if x["ei"] in set(ei.tolist())], key=lambda z: z["ei"])[:len(ei)])])
    # pool de bare candidate = barele din aceeasi luna in care strategia chiar a fost activa
    act = np.unique(mon[ei])
    pool = {m: np.where(mon == m)[0] for m in act}
    nulls = []
    for b in range(B):
        syn = []
        for e, rk in zip(ei, risks):
            cand = pool[mon[e]]
            bb = int(rng.choice(cand))
            if bb + 1 >= len(d) - 1 or bb < 1: continue
            syn.append(dict(si=bb, ei=bb + 1, dir=1, stop=o[bb + 1] - rk, exit_kind="rr", exit_param=3.0))
        tn = mstrat.simulate(d, syn, CB)
        if len(tn) >= 50: nulls.append(float(tn.R.mean()))
    nulls = np.array(nulls)
    mu, se, t, G = clt(rr, mon[ei])
    pct = float((nulls >= rr.mean()).mean())
    print(f"  {fam:4} {hid}: real mean={rr.mean():+.4f} (t_clust {t:+.2f}, {G} luni)")
    print(f"       null LONG potrivit: media {nulls.mean():+.4f}  sd {nulls.std():.4f}  "
          f"p5={np.quantile(nulls,.05):+.4f} p95={np.quantile(nulls,.95):+.4f}  ({len(nulls)} replici)")
    print(f"       p empiric (P(null >= real)) = {pct:.4f}   exces peste null = {rr.mean()-nulls.mean():+.4f} R")

print("\n" + "=" * 116); print("  COADA / OUTLIERI  si  SENSIBILITATE LA COST"); print("=" * 116)
for hid, (fam, h, sfn) in SPEC.items():
    su = sfn(d, h); tb = mstrat.simulate(d, su, CB); r = np.sort(tb.R.to_numpy())[::-1]; n = len(r)
    tot = r.sum()
    cont = {f"top{p}%": round(float(r[:max(1, int(n * p / 100))].sum() / tot), 3) for p in (1, 2, 5, 10)}
    drops = {f"drop{p}%": round(float(r[max(1, int(n * p / 100)):].mean()), 4) for p in (1, 2, 3, 5, 10)}
    wins = np.clip(tb.R.to_numpy(), np.quantile(tb.R, .05), np.quantile(tb.R, .95)).mean()
    print(f"\n  {fam:4} {hid}:  contributie {cont}")
    print(f"       expectanta dupa eliminare {drops}")
    print(f"       winsorizat 5/95: {wins:+.4f}   (brut {tb.R.mean():+.4f})")
    line = []
    for rt in (0.05, 0.16, 0.24, 0.50, 1.00, 2.00):
        tt = mstrat.simulate(d, su, cfg_for(rt))
        line.append(f"{rt:.2f}$->{tt.R.mean():+.4f}")
    print(f"       cost round-turn: " + "  ".join(line))
