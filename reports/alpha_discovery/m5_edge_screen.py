"""m5_edge_screen.py — MORE EDGES on the '4H/Daily context -> M5 entry (SL/TP)' architecture. Native M5 (2021+, single bull macro-era -> every
survivor is CURRENT-REGIME, needs prospective validation). Entry families are HTF-aligned M5 structural triggers; SL structural, TP = rr*risk.
Real cost BASE 0.05 / STRESS 0.24 round-trip. DECISIVE gate = the MATCHED-TIMING NULL (same month/dir/rr/risk, random entry timing) — because
sub-periods are all bull, only the null separates a real timing edge from HTF-long-beta. Ranks survivors that beat the null AND are STRESS-positive."""
import os, sys, numpy as np, pandas as pd
from numpy.random import default_rng
OUT=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"; sys.path.insert(0,OUT)
import m5_panel
P=m5_panel.build(); O=P["o"]; H=P["h"]; L=P["l"]; C=P["c"]; ATR=P["atr"]; T=P["t"]; n=P["n"]; yr=P["yr"]; sess=P["sess"]; hr=P["hr"]
h4t=P["h4t"]; d1t=P["d1t"]; ema20=P["ema20"]; orh=P["orh"]; orl=P["orl"]; bis=P["bis"]; rmax20=P["rmax20"]; rmin20=P["rmin20"]; pdh=P["pdh"]; pdl=P["pdl"]; pwh=P["pwh"]; pwl=P["pwl"]; psh=P["psh"]; psl=P["psl"]
month=pd.to_datetime(T,unit="s",utc=True).to_period("M").astype(str).to_numpy()
h4up=(h4t==1); h4dn=(h4t==0); d1up=(d1t==1); d1dn=(d1t==0); A=1.0*ATR
def xup(lvl):
    o=np.zeros(n,bool)
    for i in range(1,n):
        if np.isfinite(lvl[i]) and C[i-1]<=lvl[i]<C[i]: o[i]=True
    return o
def xdn(lvl):
    o=np.zeros(n,bool)
    for i in range(1,n):
        if np.isfinite(lvl[i]) and C[i-1]>=lvl[i]>C[i]: o[i]=True
    return o
def sim(el,es,risk,rr,cost,backstop=96):
    sig=np.where(el,1,np.where(es,-1,0)); tr=[]; ou=-1
    for i in range(60,n-2):
        s=sig[i]
        if s==0 or i<=ou: continue
        rk=risk[i]
        if not (rk>0) or not np.isfinite(rk): continue
        ei=i+1; entry=O[ei]; rr_risk=max(rk,2*cost,0.05); stop=entry-s*rr_risk; tgt=entry+s*rr*rr_risk
        end=min(ei+backstop,n-1); R=None; xi=end
        for k in range(ei,end+1):
            hs=(L[k]<=stop) if s>0 else (H[k]>=stop); ht=(H[k]>=tgt) if s>0 else (L[k]<=tgt)
            if hs and ht: R=-1.0; xi=k; break
            if hs: R=-1.0; xi=k; break
            if ht: R=float(rr); xi=k; break
        if R is None: R=s*(C[end]-entry)/rr_risk
        tr.append((i,s,R-cost/rr_risk,rr_risk)); ou=xi
    return pd.DataFrame(tr,columns=["i","dir","net","risk"]) if tr else None
def matched_null(tr,cost,reps=200,seed=7):
    if tr is None or len(tr)<120: return None
    real=float(tr.net.mean()); ii=tr.i.to_numpy(); dr=tr.dir.to_numpy(); rk=tr.risk.to_numpy(); rrv=2.0
    mb={}
    for i in range(60,n-100): mb.setdefault(month[i],[]).append(i)
    rng=default_rng(seed); nm=[]
    for _ in range(reps):
        rs=[]
        for a in range(len(ii)):
            cand=mb.get(month[ii[a]]);
            if not cand: continue
            j=int(rng.choice(cand)); s=int(dr[a]); risk=rk[a]; ei=j+1
            if ei>=n-1: continue
            entry=O[ei]; stop=entry-s*risk; tgt=entry+s*2.0*risk; end=min(ei+96,n-1); R=None
            for k in range(ei,end+1):
                hs=(L[k]<=stop) if s>0 else (H[k]>=stop); ht=(H[k]>=tgt) if s>0 else (L[k]<=tgt)
                if hs and ht: R=-1.0;break
                if hs: R=-1.0;break
                if ht: R=2.0;break
            if R is None: R=s*(C[end]-entry)/risk
            rs.append(R-cost/risk)
        if rs: nm.append(float(np.mean(rs)))
    nm=np.array(nm); return dict(real=round(real,4),null=round(float(nm.mean()),4),excess=round(real-float(nm.mean()),4),capt=round(100*float(nm.mean())/(real+1e-9),0),p=round(float((nm>=real).mean()),4))
# ---- families: (name, long_sig, short_sig, risk) parametrised by HTF context ctx in {h4,h4d1} ----
insess=(sess=="london")|(sess=="ny")
def families(ctx):
    up = h4up & (d1up if ctx=="h4d1" else True); dn = h4dn & (d1dn if ctx=="h4d1" else True)
    orisk=np.where((orh-orl)>0,orh-orl,np.nan)
    F=[]
    F.append((f"M5_ORB_{ctx}", insess&(bis>=12)&(bis<=48)&xup(orh)&up, insess&(bis>=12)&(bis<=48)&xdn(orl)&dn, orisk))
    F.append((f"M5_ema20pb_{ctx}", up&(L<=ema20)&(C>ema20), dn&(H>=ema20)&(C<ema20), A))
    F.append((f"M5_don20_{ctx}", xup(rmax20)&up, xdn(rmin20)&dn, A))
    F.append((f"M5_pdh_{ctx}", xup(pdh)&up, xdn(pdl)&dn, A))
    disp=(H-L)>1.5*ATR
    F.append((f"M5_disp_{ctx}", disp&(C>O)&up, disp&(C<O)&dn, A))
    F.append((f"M5_sweepReclaim_{ctx}", up&(L<psl)&(C>psl), dn&(H>psh)&(C<psh), A))
    F.append((f"M5_pwh_{ctx}", xup(pwh)&up, xdn(pwl)&dn, A))
    return F
rows=[]; survivors=[]
for ctx in ("h4","h4d1"):
    for name,el,es,risk in families(ctx):
        for rr in (2.0,3.0):
            tb=sim(el,es,risk,rr,0.025); ts=sim(el,es,risk,rr,0.12)
            if tb is None or ts is None or len(ts)<150: continue
            rb=tb.net.to_numpy(); rs=ts.net.to_numpy(); y=yr[ts.i.to_numpy()]
            pf=rs[rs>0].sum()/(abs(rs[rs<=0].sum())+1e-9)
            p1=rs[y<=2022].mean(); p2=rs[(y>=2023)&(y<=2024)].mean(); p3=rs[y>=2025].mean()
            S=np.sort(rs)[::-1]; k5=max(1,int(len(rs)*0.05)); db5=(rs.sum()-S[:k5].sum())/(len(rs)-k5)
            row=dict(fam=f"{name}/rr{int(rr)}",N=len(ts),tpy=round(len(ts)/5,0),WR=round(float((rs>0).mean()),3),BASE=round(float(rb.mean()),4),STRESS=round(float(rs.mean()),4),PF=round(pf,3),
                     p1=round(float(p1),3),p2=round(float(p2),3),p3=round(float(p3),3),db5=round(float(db5),4))
            gate = (row["BASE"]>0) and (row["STRESS"]>0) and (row["PF"]>=1.15) and (row["N"]>=150) and (min(p1,p2,p3)>-0.05)
            row["GATE"]=bool(gate); rows.append(row)
            if gate: survivors.append((row["fam"],ts))
R=pd.DataFrame(rows).sort_values("STRESS",ascending=False); R.to_csv(OUT+r"\M5_EDGE_SCREEN.csv",index=False)
pd.set_option("display.width",220,"display.max_columns",30)
print(f"screened {len(rows)} M5 configs | STRESS-positive+PF gate survivors = {len(survivors)}")
print(R[R.GATE].to_string(index=False) if R.GATE.any() else R.head(12).to_string(index=False))
print("\n=== MATCHED-TIMING NULL on gate survivors (the decisive test) ===")
for fam,tb in survivors:
    m=matched_null(tb,0.12,reps=200)
    if m is None: continue
    v="EDGE (beats null)" if (m["p"]<0.05 and m["excess"]>0 and m["real"]>0) else "HTF-long-beta (fails null)"
    print(f"{fam:24s} real={m['real']:+.4f} null={m['null']:+.4f} excess={m['excess']:+.4f} null_capt={m['capt']:.0f}% p={m['p']:.4f} -> {v}")
