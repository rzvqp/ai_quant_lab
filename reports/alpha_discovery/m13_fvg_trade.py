"""m13_fvg_trade.py — M13: (a) CAND-0003 exact DEMO tradeable resolution (§7): FVG-CE50 reaction -> trade polarity, stop=far
edge, target=near edge; (b) IFVG branch (detect_inverse_fvgs): inversion = polarity FLIP (continuation), info-first. Ratified
MK-03 detectors. Full gate. Data cur_data M15 2011-2026."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
import cur_data as CD, swing_base as sb, imbalance_mechanics as IM
from market_structure import Block
def build_blocks(t):
    gaps=np.where(np.diff(t)>72*3600)[0]; bs=[]; s=0
    for g in gaps: bs.append(Block(s,g+1)); s=g+1
    bs.append(Block(s,len(t))); return bs
def gate(m, idx, side, sl, rr, label):
    n=len(m); good=np.isfinite(sl)&(sl>0)&(idx<n-1); idx=idx[good]; sl=sl[good]
    if len(idx)<50: print(f"  {label}: N={len(idx)} thin"); return
    dd=sb.dedup_events(idx,8); p=np.isin(idx,dd); idx=idx[p]; sl=sl[p]
    tr=sb.simulate(m,idx,side,sl,rr=rr,horizon=96,scenario="STRESS"); r=tr["R"].to_numpy()
    yr=pd.Series(pd.to_datetime(tr["t_entry"],unit="s",utc=True)).dt.year.to_numpy()
    sr=np.sort(r); k10=max(1,len(r)//10); d=r[yr<=2018]; cf=r[(yr>=2019)&(yr<=2022)]; o=r[yr>=2023]
    sv=len(r)>=60 and d.mean()>0 and cf.mean()>0 and o.mean()>0 and sr[:-k10].mean()>0
    print(f"  {label}: N={len(r)} avgR={r.mean():+.4f} PF={sb._pf(r):.2f} best10rm={sr[:-k10].mean():+.4f} | DISC {d.mean():+.3f} CONF {cf.mean():+.3f} OOS {o.mean():+.3f} -> {'SURVIVOR' if sv else 'no'}")
def main():
    m=CD.load_m15(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy(); atr=m["atr"].to_numpy(); t=m["time"].to_numpy(); n=len(m)
    blocks=build_blocks(t); fvgs=IM.detect_fvgs(h,l,blocks); reacts=IM.detect_fvg_reactions(h,l,c,fvgs,blocks)
    BULL=IM.FVGKind.BULLISH; fvg_by=dict()
    for g in fvgs: fvg_by[g.formed_idx]=g
    # (a) CAND-0003 exact: enter at ce50_touch, polarity dir, stop=far edge, target=near edge
    iL=[];slL=[];rrL=[]; iS=[];slS=[];rrS=[]
    for r in reacts:
        i=r.ce50_touch_idx
        if i is None or i<0 or i>=n-1: continue
        g=fvg_by.get(r.formed_idx)
        if g is None: continue
        p=c[i]
        if r.kind==BULL:
            far=g.lower; near=g.upper; sl=p-far; tg=near-p
            flo=0.5*atr[i]; sl=max(sl,flo)
            if sl>0 and tg>0: iL.append(i); slL.append(sl); rrL.append(tg/sl)
        else:
            far=g.upper; near=g.lower; sl=far-p; tg=p-near
            flo=0.5*atr[i]; sl=max(sl,flo)
            if sl>0 and tg>0: iS.append(i); slS.append(sl); rrS.append(tg/sl)
    print(f"M13 (a) CAND-0003 exact FVG-CE50 reaction (stop=far edge, target=near edge): longs={len(iL)} shorts={len(iS)}")
    gate(m, np.array(iL), 1, np.array(slL), float(np.clip(np.median(rrL),0.3,3)), "BULL-FVG LONG ")
    gate(m, np.array(iS), -1, np.array(slS), float(np.clip(np.median(rrS),0.3,3)), "BEAR-FVG SHORT")
    # (b) IFVG branch: inversion = polarity flip -> continuation in the FLIPPED direction
    ifvgs=IM.detect_inverse_fvgs(h,l,c,fvgs,blocks)
    fmax=pd.Series(h).rolling(96).max().shift(-96).to_numpy(); fmin=pd.Series(l).rolling(96).min().shift(-96).to_numpy()
    up=(fmax-c)/atr; dn=(c-fmin)/atr; yr=m["dt"].dt.year.to_numpy()
    evB=[]; evb=[]
    for g in ifvgs:
        i=getattr(g,'confirmed_idx',None) or g.formed_idx
        if i is None or i>=n-1 or not np.isfinite(atr[i]) or atr[i]<=0: continue
        # inverted polarity: a BULL fvg inverted -> now bearish (short continuation), and vice-versa
        (evB if g.kind==BULL else evb).append(i)  # g.kind after inversion
    print(f"M13 (b) IFVG inversions={len(ifvgs)} (info: forward asym in flipped-polarity dir):")
    def row(idx,ln):
        idx=np.array(idx,int); idx=idx[idx<n-1]; ok=np.isfinite(up[idx])&np.isfinite(dn[idx]); idx=idx[ok]
        if len(idx)<150: return f"n={len(idx)}(thin)"
        a=np.median(up[idx])-np.median(dn[idx]) if ln>0 else np.median(dn[idx])-np.median(up[idx])
        return f"n={len(idx):5d} asym={a:+.2f}"
    for nm,ev,ln in [("IFVG kind=BULL",evB,1),("IFVG kind=BEAR",evb,-1)]:
        line=f"    {nm}: {row(ev,ln)}"
        for pl,ym in [("D",yr<=2018),("C",(yr>=2019)&(yr<=2022)),("O",yr>=2023)]:
            ii=[x for x in ev if ym[x]]; line+=f" | {pl} {row(ii,ln)}"
        print(line)
if __name__=="__main__": main()
