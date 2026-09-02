"""sess_diag.py — direction split + matched-control (§14 SESSION_INCREMENTAL_INFORMATION) on the two break-even families A and D.
Control = same-direction entry at the same session decision, WITHOUT the session condition (unconditional session-open exposure = beta).
If the conditioned family does not beat its unconditional control cross-era, the session condition adds no tradeable information.
"""
import sys, numpy as np
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import sess_core as SC
from sess_scan import per_date_idx, trades_A, trades_D

def stats(D,trades):
    rows=[]
    for eb,side,stop in trades:
        r=SC.resolve_entry(D,eb,side,stop,2.0)
        if r: r["y"]=D["yr"][eb]; r["side"]=side; rows.append(r)
    return rows

def rep(D,rows,label):
    if len(rows)<25: print(f"{label:40s} N={len(rows)} small"); return
    net=np.array([r["net"] for r in rows]); g=np.array([r["g"] for r in rows]); y=np.array([r["y"] for r in rows])
    era=np.array([SC.era_of(v) for v in y])
    def me(x): return net[era==x].mean() if (era==x).sum()>0 else float('nan')
    pos=sum(1 for yy in sorted(set(y)) if net[y==yy].mean()>0); tot=len(set(y))
    print(f"{label:40s} N={len(net):4d} net={net.mean():+.3f} WR={(g>0).mean():.3f} D={me('D'):+.3f} C={me('C'):+.3f} O={me('O'):+.3f} yrs+={pos}/{tot}")

# control: unconditional NY-open long/short (beta) with matched stop logic (London low/high)
def control_D(D,ny,side):
    o=D["o"];S=D["S"]; out=[]
    for d,idxs in ny.items():
        r=S.get(d,{})
        if "LH" not in r or not idxs: continue
        ns=idxs[0]; stop=r["LL"] if side>0 else r["LH"]
        out.append((ns,side,stop))
    return out
# control: unconditional London-open long/short with matched stop (Asia low/high)
def control_A(D,lon,side):
    o=D["o"];S=D["S"]; out=[]
    for d,idxs in lon.items():
        r=S.get(d,{})
        if "AH" not in r or not idxs: continue
        st=idxs[0]; stop=r["AL"] if side>0 else r["AH"]
        out.append((st,side,stop))
    return out

def main():
    D=SC.build(); lon,ny=per_date_idx(D)
    A=stats(D,trades_A(D,lon)); Dd=stats(D,trades_D(D,ny))
    print("== FAMILY A (Asia->London expansion) by direction + matched control ==")
    rep(D,[r for r in A if r["side"]>0],"A.LONG (break Asia high)")
    rep(D,stats(D,control_A(D,lon,+1)),"A.CONTROL uncond London LONG")
    rep(D,[r for r in A if r["side"]<0],"A.SHORT (break Asia low)")
    rep(D,stats(D,control_A(D,lon,-1)),"A.CONTROL uncond London SHORT")
    print("== FAMILY D (London trend->NY continuation) by direction + matched control ==")
    rep(D,[r for r in Dd if r["side"]>0],"D.LONG (London up -> NY long)")
    rep(D,stats(D,control_D(D,ny,+1)),"D.CONTROL uncond NY LONG")
    rep(D,[r for r in Dd if r["side"]<0],"D.SHORT (London down -> NY short)")
    rep(D,stats(D,control_D(D,ny,-1)),"D.CONTROL uncond NY SHORT")

if __name__=="__main__":
    main()
