"""m5_f4.py — Frontier M5-4 (info-first, causal): M15 COMPRESSION-BREAKOUT (direction self-supplied by the break, era-robust)
+ M5 DISPLACEMENT confirmation. Setup: M15 coil (20-bar range < 0.6x trailing) then M15 close breaks the coil high (long) or low
(short). M5 question: does an M5 DISPLACEMENT bar (|m5 c-o| >= 1.0*m5 ATR in the break direction) within Wr bars separate real
continuation from fakeout? CAUSAL/no-circularity: entry at the M5-displacement bar; outcome forward from there; BASE = enter at
M15 breakout bar, outcome forward from there. P(target-first, 1.5*M15-ATR) BASE vs M5-DISP, partitioned. 2021-2026 disclosed."""
import numpy as np, pandas as pd
import cur_data as CD, m5_data as M5D
Wr=24; H=288
def up1st(hi,lo,i,p,a,H,n,side):
    tgt=p+side*1.5*a; stp=p-side*1.5*a; end=min(i+1+H,n)
    for j in range(i+1,end):
        ht=(hi[j]>=tgt) if side>0 else (lo[j]<=tgt); hs=(lo[j]<=stp) if side>0 else (hi[j]>=stp)
        if ht and hs: return 0
        if ht: return 1
        if hs: return 0
    return -9
def main():
    m5=M5D.load_m5(); M15=M5D.htf_at_m5(m5,"M15")
    hi=m5["high"].to_numpy(); lo=m5["low"].to_numpy(); c5=m5["close"].to_numpy(); o5=m5["open"].to_numpy(); a5=m5["atr"].to_numpy(); n=len(m5)
    m15atr=M15["m15_atr"].to_numpy()
    m15=CD.load_m15(); H4h=pd.Series(m15["high"].to_numpy()).rolling(20).max().shift(1); H4l=pd.Series(m15["low"].to_numpy()).rolling(20).min().shift(1)
    wid=(H4h-H4l); medw=wid.rolling(160).median().shift(1); coil=(wid<0.6*medw)
    mf=m15[["time"]].copy(); mf["ch"]=H4h.to_numpy(); mf["cl"]=H4l.to_numpy(); mf["coil"]=coil.to_numpy().astype(float)
    j=pd.merge_asof(pd.DataFrame({"time":m5["time"].to_numpy()}).sort_values("time"),mf.sort_values("time").rename(columns={"time":"mt"}),left_on="time",right_on="mt",direction="backward").sort_index()
    CH=j["ch"].to_numpy(); CL=j["cl"].to_numpy(); CO=j["coil"].to_numpy()
    up_brk=(CO==1)&(c5>CH)&(np.r_[False,~(c5[:-1]>CH[:-1])])&np.isfinite(m15atr)&(m15atr>0)
    dn_brk=(CO==1)&(c5<CL)&(np.r_[False,~(c5[:-1]<CL[:-1])])&np.isfinite(m15atr)&(m15atr>0)
    yr=m5["dt"].dt.year.to_numpy()
    base=[]; disp=[]
    for side,brk in [(1,up_brk),(-1,dn_brk)]:
        for i in np.where(brk)[0]:
            if i>=n-2: continue
            a=m15atr[i]
            if not(np.isfinite(a) and a>0): continue
            base.append((up1st(hi,lo,i,c5[i],a,H,n,side),yr[i]))
            end=min(i+1+Wr,n); tj=-1
            for k in range(i+1,end):
                disp_ok=np.isfinite(a5[k]) and a5[k]>0 and (abs(c5[k]-o5[k])>=1.0*a5[k]) and (np.sign(c5[k]-o5[k])==side)
                if disp_ok: tj=k; break
            if tj>=0 and tj<n-1: disp.append((up1st(hi,lo,tj,c5[tj],a,H,n,side),yr[tj]))
    base=np.array(base); disp=np.array(disp)
    def p1(s): 
        v=s[:,0][(s[:,0]==0)|(s[:,0]==1)]; return (float((v==1).mean()) if len(v) else float('nan')), len(s)
    pb,nb=p1(base); pd_,nd=p1(disp)
    print(f"FRONTIER M5-4 (causal): M15 coil-breakout + M5 displacement. breakouts={nb} M5-disp-confirmed={nd}")
    print(f"  P(target-first): BASE(breakout bar)={pb:.3f}(n{nb})  M5-DISP(displacement bar)={pd_:.3f}(n{nd})")
    for lab,ym in [("DISC<=2023",lambda y:y<=2023),("CONF 2024",lambda y:y==2024),("OOS 2025-26",lambda y:y>=2025)]:
        b2=base[ym(base[:,1])]; d2=disp[ym(disp[:,1])]; pb2,_=p1(b2); pd2,_=p1(d2)
        print(f"    {lab}: BASE={pb2:.3f}  M5-DISP={pd2:.3f}  delta={pd2-pb2:+.3f}")
if __name__=="__main__": main()
