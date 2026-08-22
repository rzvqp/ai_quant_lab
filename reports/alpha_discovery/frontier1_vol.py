"""F1-VOL-EXP — volatility compression -> directional expansion, SWING horizon, H4 signal / D1 context.
Cheap path-first screen (mechanism magnitude) BEFORE strategy conversion. Both sides independent.
Firewall via swing_base (gated M5 only). DEV selection; CALIB reported separately as robustness.
"""
import numpy as np, pandas as pd
import swing_base as sb

W = 20          # compression box window (H4 bars ~ 3.3 days)
HORS = [42, 60] # swing horizons in H4 bars (~7d, ~10d)

def signals(h4):
    h = h4["high"].to_numpy(); l = h4["low"].to_numpy(); c = h4["close"].to_numpy()
    atr = h4["atr"].to_numpy(); atr_ma = h4["atr_ma"].to_numpy()
    box_high = pd.Series(h).rolling(W).max().shift(1).to_numpy()
    box_low  = pd.Series(l).rolling(W).min().shift(1).to_numpy()
    box_range = box_high - box_low
    box_ma = pd.Series(box_range).rolling(50).mean().shift(1).to_numpy()
    comp_vol = atr < atr_ma
    narrow = box_range < box_ma
    comp = comp_vol & narrow & np.isfinite(box_range) & np.isfinite(atr)
    up = comp & (c > box_high)      # release up
    dn = comp & (c < box_low)       # release down
    return dict(box_high=box_high, box_low=box_low, up=up, dn=dn)

def run_side(h4, sig, side, dev_mask, d1_up_aligned):
    o = h4["open"].to_numpy()
    if side > 0:
        raw = np.where(sig["up"])[0]
        risk_at = lambda i: (o[i+1] - sig["box_low"][i]) if i+1 < len(o) else np.nan
    else:
        raw = np.where(sig["dn"])[0]
        risk_at = lambda i: (sig["box_high"][i] - o[i+1]) if i+1 < len(o) else np.nan
    # DEV signal bars only (selection); dedup one event per box window
    raw = np.array([i for i in raw if i+1 < len(h4) and dev_mask[i]])
    ev = sb.dedup_events(raw, cooldown=W)
    risk = np.array([risk_at(i) for i in ev])
    ok = np.isfinite(risk) & (risk > 0)
    ev, risk = ev[ok], risk[ok]
    if len(ev) == 0:
        print(f"  side={'L' if side>0 else 'S'}: 0 events"); return
    # D1-aligned subset (context, not pre-filter for the screen)
    al = d1_up_aligned[ev] if side > 0 else (~d1_up_aligned[ev])
    for tag, sel in (("ALL", np.ones(len(ev), bool)), ("D1aligned", al)):
        e2, r2 = ev[sel], risk[sel]
        if len(e2) < 8:
            print(f"  side={'L' if side>0 else 'S'} [{tag}]: N={len(e2)} (too few)"); continue
        # CHEAP SCREEN: path magnitude with far target (never hit) over horizon
        for H in HORS:
            scr = sb.simulate(h4, e2, side, r2, rr=10.0, horizon=H, scenario="STRESS")
            af = float((scr["mae_R"] >= 1.0).mean())
            # favorable-before-adverse proxy = WR at rr with structural stop
            print(f"  {'L' if side>0 else 'S'} [{tag}] H={H}: N={len(scr)} "
                  f"medMFE={scr['mfe_R'].median():.2f}R medMAE={scr['mae_R'].median():.2f}R "
                  f"advFirst(MAE>=1R)={af:.2f} medSL={scr['sl_pips'].median():.0f}p")
        # CONVERSION path quality: WR/avgR at real RR (STRESS)
        for rr in (1.5, 2.0, 3.0):
            tr = sb.simulate(h4, e2, side, r2, rr=rr, horizon=HORS[-1], scenario="STRESS")
            m = sb.metrics(tr, h4, rr)
            dc = sb.disc_conf(tr, h4, rr)
            py = " ".join(f"{y}:{v[0]:+.2f}(n{v[1]})" for y,v in sorted(m["per_year"].items()))
            dctxt = (f"DISC{dc['disc_avgR']:+.2f}(n{dc['disc_N']}) CONF{dc['conf_avgR']:+.2f}(n{dc['conf_N']})"
                     if dc else "DISC/CONF n/a")
            print(f"     rr={rr}: N={m['N']} WRt={m['WR_target']:.2f} avgR={m['avgR']:+.3f} "
                  f"PF={m['PF']:.2f} best10={m['best10']:+.3f} maxDD={m['maxDD_R']:.1f} | {dctxt} | {py}")

def main():
    tfs = sb.build_frames()
    h4, d1 = tfs["H4"], tfs["D1"]
    sig = signals(h4)
    dev_mask = h4["is_dev"].to_numpy()
    # D1 context aligned to H4 (last completed D1 EMA20>EMA50 => up-trend context)
    d1["d1_up"] = (d1["ema20"] > d1["ema50"]).astype(float)
    h4c = sb.align_context(h4, d1, ["d1_up"], "_d1")
    d1_up_aligned = (h4c["d1_up_d1"].to_numpy() > 0.5)
    print(f"F1-VOL-EXP  H4 DEV bars={int(dev_mask.sum())}  compression events: up={int((sig['up']&dev_mask).sum())} dn={int((sig['dn']&dev_mask).sum())}")
    print("LONG (up-release):")
    run_side(h4, sig, +1, dev_mask, d1_up_aligned)
    print("SHORT (down-release):")
    run_side(h4, sig, -1, dev_mask, d1_up_aligned)

if __name__ == "__main__":
    main()
