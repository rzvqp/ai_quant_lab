"""tsm_sweep.py — TEMPORAL_SEQUENCE_MINING_V1: scale/anchor invariance of the path-information negative.
Sweep L in {8,16,32,64} x anchor in {RANGE_EDGE, VOL_TRANSITION} x frame {up/down, continue}.
Apply the §12/§17 INFORMATION+STABILITY gate to every causal motif: a SURVIVOR needs |ALL|>=0.02 AND sign(DEV)==sign(OOS)==sign(ALL)
AND same sign across eras D,C,O. Report survivors (expected: none). Positive control (future return) must survive on up/down = power check.
"""
import sys, numpy as np
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import tsm_core as TC
from tsm_contrast import build_anchors, state_cell

def vol_transition_anchors(P):
    """Compression->expansion onset: comp<0.85 (compressed) then next bar's range expands > 1.5x atr_ma. Fresh events."""
    comp=P["comp"]; tr=P["tr"]; atr_ma=P["atr_ma"]; n=P["n"]
    exp=(tr>1.5*atr_ma); onset=np.zeros(n,bool)
    for i in range(2,n):
        if comp[i-1]<0.85 and exp[i]: onset[i]=True
    idx=np.where(onset)[0]; idx=idx[(idx>400)&(idx<n-64)]
    # dedup consecutive
    out=[]; last=-10
    for t in idx:
        if t-last>3: out.append(t); last=t
    return np.array(out)

def within_cell_spread(cells, feat, opos, mask):
    hi_n=hi_p=lo_n=lo_p=0
    for cel in np.unique(cells[mask]):
        m=mask&(cells==cel)
        if m.sum()<20: continue
        fv=feat[m]; ov=opos[m]; med=np.median(fv); hi=fv>med; lo=fv<=med
        if hi.sum()<5 or lo.sum()<5: continue
        hi_p+=ov[hi].sum(); hi_n+=hi.sum(); lo_p+=ov[lo].sum(); lo_n+=lo.sum()
    if hi_n<50 or lo_n<50: return np.nan
    return hi_p/hi_n - lo_p/lo_n

def run(P, idx, L, tag):
    n=P["n"]; yr=P["yr"]; c=P["c"]
    pf=TC.path_features(P, idx, L)
    lab,_,_,_=TC.triple_barrier(P, idx, b=1.5, H=32)
    keep=np.array([i for i,f in enumerate(pf) if f is not None and np.isfinite(f["net"])])
    idx2=idx[keep]; pf=[pf[i] for i in keep]; lab=lab[keep]
    netL=np.array([f["net"] for f in pf]); pdir=np.sign(netL); pdir[pdir==0]=1
    resolved=(lab!=0); up=(lab>0).astype(int)
    cont=(np.where(((pdir>0)&(lab>0))|((pdir<0)&(lab<0)),1,0)).astype(int)
    F={k:np.array([f[k] for f in pf],float) for k in ["eff","sc","energy_late","argH","argL","pull","rc","net_r"]}
    F["_POSCTRL_fut3"]=np.array([(c[min(t+3,n-1)]-c[t]) for t in idx2],float)
    era=np.array([P["era"](t) for t in idx2]); dev=(yr[idx2]<=2019); oos=~dev
    cells=np.array([hash(state_cell(P,t,pdir[k])) for k,t in enumerate(idx2)])
    ie=len(TC.independent_episodes(idx2,32))
    survivors=[]
    for fname,feat in F.items():
        for frame,opos in [("up/down",up),("continue",cont)]:
            dA=within_cell_spread(cells,feat,opos,resolved)
            dD=within_cell_spread(cells,feat,opos,resolved&dev)
            dO=within_cell_spread(cells,feat,opos,resolved&oos)
            dd=within_cell_spread(cells,feat,opos,resolved&(era=="D"))
            dc=within_cell_spread(cells,feat,opos,resolved&(era=="C"))
            do=within_cell_spread(cells,feat,opos,resolved&(era=="O"))
            vals=[dA,dD,dO,dd,dc,do]
            if any(not np.isfinite(v) for v in vals): continue
            stable = (abs(dA)>=0.02) and (np.sign(dD)==np.sign(dA)==np.sign(dO)) and (np.sign(dd)==np.sign(dc)==np.sign(do)==np.sign(dA))
            if stable and not fname.startswith("_POSCTRL"):
                survivors.append((fname,frame,dA,dD,dO,dd,dc,do))
    pc=within_cell_spread(cells,F["_POSCTRL_fut3"],up,resolved)
    print(f"[{tag} L={L:2d}] anchors={len(idx2)} indep_ep={ie} POSCTRL(up/down)={pc:+.3f} CAUSAL_SURVIVORS={len(survivors)}")
    for s in survivors:
        print(f"      SURVIVOR {s[0]:14s} {s[1]:9s} ALL{s[2]:+.3f} DEV{s[3]:+.3f} OOS{s[4]:+.3f} D{s[5]:+.3f} C{s[6]:+.3f} O{s[7]:+.3f}")
    return len(survivors), pc

def main():
    P=TC.load_panel()
    anchors={"RANGE_EDGE":build_anchors(P), "VOL_TRANS":vol_transition_anchors(P)}
    for aname,idx in anchors.items():
        print(f"\n### anchor={aname} raw={len(idx)}")
        for L in [8,16,32,64]:
            run(P, idx, L, aname)

if __name__=="__main__":
    main()
