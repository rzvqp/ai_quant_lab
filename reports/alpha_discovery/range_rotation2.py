"""Phase 2: E0-E4 causal feature map for RANGE boundary attacks, A(clean) vs B+C, DISC/CONF, POSITION CONTROLS,
per family (U/upper->SHORT, L/lower->LONG). Failed-extension, inward-displacement, velocity, range geometry.
Consumes range_rotation (parent+4-class). NO execution/thresholds/classifier-unless-2-stable."""
import sys, os, numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import range_rotation as RR
h=RR.h;l=RR.l;c=RR.c;o=RR.o;uday=RR.uday;n=RR.n;PIP=RR.PIP;yr=RR.yr; bnd=RR.bnd
def auc(y,x):
    y=np.array(y);x=np.array(x,float);m=np.isfinite(x);y=y[m];x=x[m];n1=y.sum();n0=len(y)-n1
    if n1==0 or n0==0: return np.nan
    r=np.argsort(np.argsort(x))+1; return (r[y==1].sum()-n1*(n1+1)/2)/(n1*n0)
def rngb(i): return max(h[i]-l[i],1e-9)

def feats(r,k):
    i=r["i"]; side=r["side"]; up=r["up"]; lo=r["lo"]; mid=r["mid"]; sh=r["sweep_ext"]; e1=i+1
    seg=list(range(e1,e1+k))
    if not seg or seg[-1]>=n or any(uday[j]!=uday[i] for j in seg): return None
    hi=max(h[j] for j in seg); low=min(l[j] for j in seg); cl=c[seg[-1]]
    if side=="U":
        inward=(c[i]-cl)/PIP; adverse=(hi-c[i])/PIP; ext_beyond=(hi-sh)/PIP
        dist_to_mid=(cl-mid)/PIP; dist_from_bound=(cl-up)/PIP; failed_ext=float(hi<sh); closes_out=float(sum(c[j]>up for j in seg))
        resolved="newext" if hi>sh else ("mid" if low<=mid else "undecided")
    else:
        inward=(cl-c[i])/PIP; adverse=(c[i]-low)/PIP; ext_beyond=(sh-low)/PIP
        dist_to_mid=(mid-cl)/PIP; dist_from_bound=(lo-cl)/PIP; failed_ext=float(low>sh); closes_out=float(sum(c[j]<lo for j in seg))
        resolved="newext" if low<sh else ("mid" if hi>=mid else "undecided")
    return dict(inward_prog=inward,adverse=adverse,ext_beyond=ext_beyond,failed_ext=failed_ext,closes_out=closes_out,
                dist_to_mid=dist_to_mid,dist_from_bound=dist_from_bound,inout_ratio=inward/(adverse+1.0),
                last_body=(o[seg[-1]]-c[seg[-1]])/PIP*(1 if side=="U" else -1),resolved=resolved)

def e0feats(r):
    i=r["i"]; side=r["side"]; up=r["up"]; lo=r["lo"]; width=r["width"]; e0=i
    excursion=r["excursion"]
    # velocity into attack (causal)
    disp5=(c[i]-c[i-1])/PIP if i>=1 else np.nan; disp15=(c[i]-c[i-3])/PIP if i>=3 else np.nan
    path=sum(abs(c[j]-c[j-1]) for j in range(max(1,i-6),i+1)); net=abs(c[i]-c[max(0,i-6)]); eff=net/path if path>0 else np.nan
    # location within range at attack close, compression (recent range vs width)
    recent=np.mean([rngb(j) for j in range(max(0,i-6),i)]) if i>=6 else rngb(i)
    return dict(width=width,excursion=excursion,excursion_norm=excursion/width if width>0 else np.nan,
                upper_wick=(h[i]-max(o[i],c[i]))/rngb(i),close_loc=(c[i]-l[i])/rngb(i),
                disp5=disp5*(1 if side=="U" else -1),disp15=disp15*(1 if side=="U" else -1),approach_eff=eff,
                compression=recent/(width*PIP) if width>0 else np.nan)

def analyze(rows,name):
    if not rows: print(f"\n{name}: empty"); return
    rows=sorted(rows,key=lambda r:r["i"]); cut=rows[int(len(rows)*0.6)]["i"]
    for r in rows: r["split"]="DISC" if r["i"]<cut else "CONF"; r["E0"]=e0feats(r)
    lab=lambda r: 1 if r["cls"]=="A_clean" else (0 if r["cls"] in ("B_newext_then_rot","C_breakout") else -1)
    D=[r for r in rows if r["split"]=="DISC" and lab(r)>=0]; C=[r for r in rows if r["split"]=="CONF" and lab(r)>=0]
    print(f"\n=== {name}: E0 static features A(clean) vs B+C (DISC|CONF) + year AUC ===")
    for f in ("width","excursion","excursion_norm","upper_wick","close_loc","disp5","disp15","approach_eff","compression"):
        ad=auc([lab(r) for r in D],[r["E0"][f] for r in D]); ac=auc([lab(r) for r in C],[r["E0"][f] for r in C])
        ys=[auc([lab(r) for r in rows if yr[r["i"]]==y and lab(r)>=0],[r["E0"][f] for r in rows if yr[r["i"]]==y and lab(r)>=0]) for y in (2021,2022,2023)]
        st="STABLE" if (np.isfinite(ad) and np.isfinite(ac) and (ad-.5)*(ac-.5)>0 and abs(ad-.5)>.07 and abs(ac-.5)>.07) else ""
        print(f"  {f:14} DISC{ad:.2f} CONF{ac:.2f} yr{ys[0]:.2f}/{ys[1]:.2f}/{ys[2]:.2f} {st}")
    print(f"  --- E1-E4 path features (undecided-conditioned), A vs B+C, DISC|CONF, POSITION-adjusted ---")
    for k in (1,2,3,4):
        und=[r for r in rows if (fk:=feats(r,k)) and fk["resolved"]=="undecided" and lab(r)>=0]
        for r in und: r[f"F{k}"]=feats(r,k)
        d=[r for r in und if r["split"]=="DISC"]; cf=[r for r in und if r["split"]=="CONF"]
        rem=np.median([r[f"F{k}"]["dist_to_mid"] for r in und]) if und else np.nan
        print(f"    E{k}: undecided n={len(und)} (D{len(d)}/C{len(cf)}) medRemainToMid={rem:.1f}p")
        for f in ("inward_prog","ext_beyond","failed_ext","closes_out","inout_ratio","last_body"):
            ad=auc([lab(r) for r in d],[r[f"F{k}"][f] for r in d]); ac=auc([lab(r) for r in cf],[r[f"F{k}"][f] for r in cf])
            pos=np.array([r[f"F{k}"]["dist_from_bound"] for r in und]); ql=np.nanquantile(pos,[.33,.66]); padj=[]
            for a,b in ((-1e9,ql[0]),(ql[0],ql[1]),(ql[1],1e9)):
                sub=[r for r in und if a<=r[f"F{k}"]["dist_from_bound"]<b]
                if len(sub)>=8: padj.append(auc([lab(r) for r in sub],[r[f"F{k}"][f] for r in sub]))
            pa=np.nanmedian(padj) if padj else np.nan
            st="STABLE" if (np.isfinite(ad) and np.isfinite(ac) and (ad-.5)*(ac-.5)>0 and abs(ad-.5)>.07 and abs(ac-.5)>.07 and abs(pa-.5)>.05) else ""
            print(f"       {f:12} DISC{ad:.2f} CONF{ac:.2f} posadj{pa:.2f} {st}")
analyze(RR.rowsU,"FAMILY U / upper -> SHORT")
analyze(RR.rowsL,"FAMILY L / lower -> LONG")
