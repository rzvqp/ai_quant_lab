"""m5_scan.py — first-pass: raw-path + 2R baseline for the 5 M5 event-revealed families, by direction, with DEV/OOS + 100/200/300p reach.
DEV = 2021-07..2024-06 ; OOS = 2024-07..2026-07 (chronological). Reports net-R (price cost), WR, independent episodes, path skew.
"""
import sys, numpy as np
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import m5_core as MC, m5_families as MF

def evalfam(M, trades, exit_mode="2R"):
    rows=[]
    for tr in trades:
        k,side,stop=tr
        r=MC.resolve(M,k,side,stop,exit_mode)
        if r is None: continue
        r["yr"]=M["yr"][min(k,M["n"]-1)]; rows.append(r)
    return rows

def rep(M, rows, label):
    if len(rows)<40: print(f"{label:26s} N={len(rows)} small"); return
    net=np.array([r["net"] for r in rows]); g=np.array([r["g"] for r in rows]); k=np.array([r["k"] for r in rows])
    yr=np.array([r["yr"] for r in rows]); side=np.array([r["side"] for r in rows]); risk=np.array([r["risk"] for r in rows])
    ie=len(MC.dedup_episodes(k))
    t=M["t"]; ky=t[np.clip(k,0,M["n"]-1)]
    dev=ky< 1719792000   # 2024-07-01
    r100=np.mean([r["r100"] for r in rows]); r200=np.mean([r["r200"] for r in rows]); r300=np.mean([r["r300"] for r in rows])
    top1=np.sort(net)[-max(1,len(net)//100):].sum()/net.sum() if net.sum()>0 else float('nan')
    print(f"{label:26s} N={len(net):5d} ie={ie:4d} net={net.mean():+.3f} WR={(g>0).mean():.3f} "
          f"DEV={net[dev].mean():+.3f} OOS={net[~dev].mean():+.3f} | P100={r100:.3f} P200={r200:.3f} P300={r300:.3f} "
          f"stop={np.median(risk)/MC.PIP:.0f}p top1%={top1:.2f}")

def main():
    M=MC.load()
    print("=== 2R baseline, raw-path reach, DEV(2021-24H1)/OOS(2024H2-2026) ===")
    for name,fn in MF.FAMILIES.items():
        tr=fn(M); rows=evalfam(M,tr,"2R")
        rep(M,rows,f"{name}.ALL")
        rep(M,[r for r in rows if r["side"]>0],f"  {name}.LONG")
        rep(M,[r for r in rows if r["side"]<0],f"  {name}.SHORT")

if __name__=="__main__":
    main()
