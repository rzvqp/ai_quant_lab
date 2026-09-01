"""Post-freeze battery: OOS (inspected once), eras, matched controls, outlier + dependence robustness.
Definitions are frozen; nothing here changes a state or a target."""
import sys, json; sys.path.insert(0, '.')
from engine import *
from scan import S6, S12, S24, S48, D6, D12, D24, A2, B1, B2, B3, C3, C4, D4, D4sgn, E1, M, causal_pct

TOP = [
 ("F1-P500-48", S48, lambda s: B3(s), lambda s: M(s.tg["exc"] >= 500), "TAIL",      "5d/20d vol contraction -> P(|exc|>=500p), 48h"),
 ("B3-EXC-48",  S48, lambda s: B3(s), lambda s: s.tg["exc"],           "MAGNITUDE", "5d/20d vol contraction -> largest excursion, 48h"),
 ("E1-MAG-24",  S24, lambda s: E1(s), lambda s: s.mag(),               "MAGNITUDE", "low-range previous day -> |move|, 24h"),
 ("D4-MAG-6",   D6,  lambda s: D4(s), lambda s: s.mag(),               "MAGNITUDE", "Asia closed at edge of Asia range -> |move|, 6h"),
 ("E1-EXC-48",  S48, lambda s: E1(s), lambda s: s.tg["exc"],           "MAGNITUDE", "low-range previous day -> largest excursion, 48h"),
]

def crve_cov(y, x, cov, cl):
    """same CR1 estimator, with matched-control covariates added."""
    Z = [np.ones(len(y)), np.asarray(x, float)] + [np.asarray(c, float) for c in cov]
    Z = np.column_stack(Z)
    ok = np.isfinite(y) & np.isfinite(Z).all(1)
    y2, Z2, cl2 = y[ok], Z[ok], cl[ok]
    n = len(y2)
    if n < 80 or Z2[:, 1].sum() < 25: return None
    ZtZi = np.linalg.pinv(Z2.T @ Z2)
    b = ZtZi @ (Z2.T @ y2); u = y2 - Z2 @ b
    uni, inv = np.unique(cl2, return_inverse=True); G = len(uni)
    meat = np.zeros((Z2.shape[1],) * 2)
    for g in range(G):
        m = inv == g; s = Z2[m].T @ u[m]; meat += np.outer(s, s)
    V = ZtZi @ meat @ ZtZi * (G / max(G - 1, 1)) * ((n - 1) / max(n - Z2.shape[1], 1))
    se = math.sqrt(max(V[1, 1], 1e-18))
    return dict(n=int(n), lift=float(b[1]), se=se, z=float(b[1] / se))

print("=" * 116)
print("  POST-FREEZE BATTERY -- OOS inspected ONCE; definitions unchanged")
print("=" * 116)

OUT = {}
for hid, S, mk, tf, cls, desc in TOP:
    x = mk(S); y = tf(S); t = TS[S.idx]
    dev = t < DEV_END_TS; oos = ~dev
    yr = YEAR[S.idx]
    print(f"\n{'='*116}\n  {hid}   [{cls}]   {desc}\n{'='*116}")
    rd = crve(y[dev], x[dev], MON[S.idx][dev])
    ro = crve(y[oos], x[oos], MON[S.idx][oos])
    ra = crve(y, x, MON[S.idx])
    for nm, r in (("DEV  (2011-2018)", rd), ("OOS  (2019-2025)", ro), ("FULL (2011-2025)", ra)):
        if r: print(f"    {nm:20} n_cond {r['n_cond']:5d}  base {r['base']:9.3f}  cond {r['cond']:9.3f}"
                    f"  lift {r['lift']:+9.3f}  z {r['z']:+6.2f}")
        else: print(f"    {nm:20} not estimable")
    sign_ok = (rd and ro and np.sign(rd['lift']) == np.sign(ro['lift']))
    print(f"    OOS SIGN AGREES WITH DEV : {'YES' if sign_ok else 'NO'}")

    # ---- pre/post 2021
    pre = t < pd.Timestamp("2021-01-01T00:00:00+00:00").timestamp()
    r1 = crve(y[pre], x[pre], MON[S.idx][pre]); r2 = crve(y[~pre], x[~pre], MON[S.idx][~pre])
    print(f"    PRE_2021  (2011-2020) : " + (f"n_cond {r1['n_cond']:4d}  lift {r1['lift']:+9.3f}  z {r1['z']:+6.2f}" if r1 else "n/a"))
    print(f"    POST_2021 (2021-2025) : " + (f"n_cond {r2['n_cond']:4d}  lift {r2['lift']:+9.3f}  z {r2['z']:+6.2f}" if r2 else "n/a"))

    # ---- era blocks
    eras = [(2011, 2013), (2013, 2016), (2016, 2019), (2019, 2021), (2021, 2023), (2023, 2026)]
    line = []
    for a, b in eras:
        m = (yr >= a) & (yr < b)
        r = crve(y[m], x[m], MON[S.idx][m])
        line.append(f"{a}-{b}: " + (f"{r['lift']:+8.2f}(n{r['n_cond']:3d})" if r else "   n/a    "))
    print("    ERA BLOCKS  " + " | ".join(line))
    neg = sum(1 for a, b in eras if (lambda r: r and r['lift'] < 0)(crve(y[(yr>=a)&(yr<b)], x[(yr>=a)&(yr<b)], MON[S.idx][(yr>=a)&(yr<b)])))
    est = sum(1 for a, b in eras if crve(y[(yr>=a)&(yr<b)], x[(yr>=a)&(yr<b)], MON[S.idx][(yr>=a)&(yr<b)]))
    print(f"    era sign consistency (negative): {neg}/{est}")

    # ---- matched controls (time-of-day exact by construction; add the rest as covariates)
    cov = [causal_pct(atr20d[S.idx]), causal_pct((np.abs(ret24) / atr20d)[S.idx]), S.clp,
           causal_pct(vol20[S.idx])]
    rc = crve_cov(y, x, cov, MON[S.idx])
    if rc:
        shrink = 100 * (1 - abs(rc['lift']) / max(abs(ra['lift']), 1e-9))
        print(f"    MATCHED CONTROL (+ trailing vol, recent-move size, range position, 20d vol):")
        print(f"        raw lift {ra['lift']:+9.3f} (z {ra['z']:+5.2f})  ->  controlled {rc['lift']:+9.3f} "
              f"(z {rc['z']:+5.2f})   effect absorbed: {shrink:5.1f}%")
        print(f"        ADDS INFORMATION BEYOND CONTROLS: {'YES' if abs(rc['z'])>1.96 else 'NO'}")
    OUT[hid] = dict(dev=rd, oos=ro, full=ra, pre2021=r1, post2021=r2, controlled=rc, sign_ok=bool(sign_ok))

    # ---- outlier robustness (continuous targets only)
    if cls != "TAIL":
        yy = y[np.isfinite(y)]
        srt = np.sort(yy)[::-1]
        tot = yy.sum()
        print(f"    OUTLIERS: top-1% of episodes carry {100*srt[:max(1,len(yy)//100)].sum()/tot:.1f}% of total |move|; "
              f"top-5% carry {100*srt[:max(1,len(yy)//20)].sum()/tot:.1f}%")
        thr = np.nanquantile(y, 0.99)
        m = y < thr
        rdrop = crve(y[m], x[m], MON[S.idx][m])
        if rdrop: print(f"    DROP-BEST-1%: lift {rdrop['lift']:+9.3f}  z {rdrop['z']:+6.2f}  "
                        f"-> {'HOLDS' if abs(rdrop['z'])>1.96 and np.sign(rdrop['lift'])==np.sign(ra['lift']) else 'WEAKENS'}")
        thr5 = np.nanquantile(y, 0.95); m5 = y < thr5
        r5 = crve(y[m5], x[m5], MON[S.idx][m5])
        if r5: print(f"    DROP-BEST-5%: lift {r5['lift']:+9.3f}  z {r5['z']:+6.2f}")

    # ---- dependence robustness: double the stride (strictly stronger non-overlap)
    hb = S.h
    hour = 8 if hid.startswith("D") else 0
    st2 = 4 if hb == 192 else 2
    S2 = type(S)(hour, hb, st2)
    x2 = mk(S2); y2 = tf(S2)
    r2s = crve(y2, x2, MON[S2.idx])
    if r2s: print(f"    DEPENDENCE (stride x2 -> {len(S2.idx)} episodes): lift {r2s['lift']:+9.3f}  z {r2s['z']:+6.2f}")

json.dump(OUT, open("post.json", "w"), indent=1, default=float)

# ---------------- class-level summary for the CEO questions
print("\n" + "=" * 116)
print("  TARGET-CLASS SUMMARY ACROSS ALL 60 DEV HYPOTHESES")
print("=" * 116)
sc = json.load(open("dev_scan.json"))
for cls in ("DIRECTION", "MAGNITUDE", "TIMING", "TAIL"):
    zs = [abs(r["dev"]["z"]) for r in sc if r["target_class"] == cls and r["dev"]]
    if zs:
        print(f"  {cls:<11} tests {len(zs):3d}   best |z| {max(zs):5.2f}   mean |z| {np.mean(zs):5.2f}   "
              f"count |z|>2 : {sum(1 for z in zs if z>2)}   >3.02 (Bonf m=60): {sum(1 for z in zs if z>3.02)}")
for br in "ABCDEF":
    zs = [abs(r["dev"]["z"]) for r in sc if r["branch"] == br and r["dev"]]
    print(f"  branch {br}: tests {len(zs):2d}  best |z| {max(zs):5.2f}")
