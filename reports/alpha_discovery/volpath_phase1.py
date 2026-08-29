"""volpath_phase1.py — VOLPATH Phase-1 PATH GEOMETRY DISCOVERY (information-first, no strategy). Per VOLPATH_PROTOCOL.md (frozen).
Qualifying event = mature compression endpoint (comp_dur>=12, deduped >=H apart). Freeze ref=close[T], atr, range[rLo,rHi], mid.
Measure the forward H=48-bar path geometry (A timing, B two-sided excursion, C path ordering, D midpoint recross, E first-break quality,
F double-sided break, G range consumption, H alternation). Barriers k in {0.5,1,1.5,2} ATR (frozen family). Aggregate overall + by era +
session + compression severity. NO strategy, NO barrier chosen post-hoc. cur_data M15 UTC."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import cur_data as CD
import session_tz as STZ
H=48; KS=[0.5,1.0,1.5,2.0]
def main():
    m=CD.load_m15(); o=m["open"].to_numpy(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy()
    atr=m["atr"].to_numpy(); atr_ma=m["atr_ma"].to_numpy(); n=len(m); yr=m["dt"].dt.year.to_numpy(); hr=m["dt"].dt.hour.to_numpy()
    comp=(atr<atr_ma).astype(int); cd=np.zeros(n,int)
    for i in range(1,n): cd[i]=cd[i-1]+1 if comp[i] else 0
    def sess(i):
        H_=hr[i]; return "AS" if H_<8 else ("LN" if H_<13 else ("NY" if H_<20 else "AS"))
    def era(i): return "D" if yr[i]<=2018 else ("C" if yr[i]<=2022 else "O")
    # qualifying deduped events
    ev=[]; last=-10**9
    for T in range(60, n-H-2):
        if cd[T]>=12 and np.isfinite(atr[T]) and atr[T]>0 and T-last>=H:
            ev.append(T); last=T
    recs=[]
    for T in ev:
        a=atr[T]; ref=c[T]; W=min(cd[T],40); rHi=np.max(h[T-W+1:T+1]); rLo=np.min(l[T-W+1:T+1]); mid=0.5*(rHi+rLo)
        segh=h[T+1:T+1+H]; segl=l[T+1:T+1+H]; segc=c[T+1:T+1+H]
        up_ex=(segh-ref)/a; dn_ex=(ref-segl)/a
        max_up=np.max(up_ex); max_dn=np.max(dn_ex)
        r=dict(era=era(T), sess=sess(T), sev=atr[T]/atr_ma[T] if atr_ma[T]>0 else np.nan, max_up=max_up, max_dn=max_dn)
        # B two-sided reach + C ordering per k
        for k in KS:
            fu=np.where(up_ex>=k)[0]; fd=np.where(dn_ex>=k)[0]
            pu=len(fu)>0; pd_=len(fd)>0; r[f"P_up{k}"]=pu; r[f"P_dn{k}"]=pd_; r[f"P_both{k}"]=pu and pd_
            iu=fu[0] if pu else 10**9; idn=fd[0] if pd_ else 10**9
            r[f"ord{k}"]=("UP" if iu<idn-1 else ("DN" if idn<iu-1 else ("BOTH" if (pu and pd_) else "NEITHER"))) if (pu or pd_) else "NEITHER"
        # A timing: bars to first 0.5/1/1.5/2 either-side, bars to max excursion
        for k in KS:
            f=np.where((up_ex>=k)|(dn_ex>=k))[0]; r[f"t{k}"]=(int(f[0])+1) if len(f) else -1
        r["t_maxup"]=int(np.argmax(up_ex))+1; r["t_maxdn"]=int(np.argmax(dn_ex))+1
        # D midpoint recross: sign of (close-mid) over path; count sign changes after first 0.5ATR move
        s=np.sign(segc-mid); moved=np.where(np.abs(segc-mid)>=0.5*a)[0]
        if len(moved):
            st=moved[0]; sub=s[st:]; sub=sub[sub!=0]
            rec=int(np.sum(sub[1:]!=sub[:-1])) if len(sub)>1 else 0
            r["recross"]=rec
            # time to first recross after st
            first=-1
            for j in range(st+1,len(s)):
                if s[j]!=0 and s[j]!=s[st]: first=j-st; break
            r["t_recross1"]=first
        else: r["recross"]=0; r["t_recross1"]=-1
        # E first break of compression range + follow-through + classification
        fb=None
        for j in range(H):
            if segh[j]>=rHi: fb=(j,1,rHi); break
            if segl[j]<=rLo: fb=(j,-1,rLo); break
        if fb:
            j,bdir,lvl=fb; r["fb_dir"]=bdir; r["fb_bar"]=j+1
            after_c=segc[j:]; after_h=segh[j:]; after_l=segl[j:]
            # follow-through: extend +0.5ATR beyond lvl in bdir at 1/2/4 bars
            def ft(kk):
                if j+kk>=H: return np.nan
                return float(((segc[j+kk]-lvl)*bdir)/a)  # close beyond break level in bdir, ATR
            r["ft1"]=ft(1); r["ft2"]=ft(2); r["ft4"]=ft(4)
            # MFE/MAE after break in ATR (in break dir)
            if bdir>0: r["fb_mfe"]=float((np.max(after_h)-lvl)/a); r["fb_mae"]=float((lvl-np.min(after_l))/a)
            else: r["fb_mfe"]=float((lvl-np.min(after_l))/a); r["fb_mae"]=float((np.max(after_h)-lvl)/a)
            # classify: continues (+1ATR beyond before recross) / reverses (hit opposite boundary) / double_break / whipsaw
            oppo = rLo if bdir>0 else rHi
            ext=np.where(((after_c-lvl)*bdir)>=1.0*a)[0]; recross_in=np.where(((after_c-lvl)*bdir)<0)[0]
            opp_break = (np.min(after_l)<=rLo) if bdir>0 else (np.max(after_h)>=rHi)
            fe=ext[0] if len(ext) else 10**9; fr=recross_in[0] if len(recross_in) else 10**9
            if opp_break and fr<10**9: r["fb_class"]="DOUBLE_BREAK"
            elif fe<fr: r["fb_class"]="CONTINUES"
            elif fr<10**9: r["fb_class"]="WHIPSAW"
            else: r["fb_class"]="NEITHER"
        else: r["fb_dir"]=0; r["fb_class"]="NO_BREAK"
        # G range consumption: fraction of dominant total excursion reached within first 1/2/4/8 bars
        dom = max(max_up, max_dn); domex = up_ex if max_up>=max_dn else dn_ex
        for w in [1,2,4,8]:
            r[f"cons{w}"]= float(np.max(domex[:w])/dom) if dom>0 and w<=H else np.nan
        recs.append(r)
    df=pd.DataFrame(recs); N=len(df)
    print(f"VOLPATH Phase-1: qualifying deduped compression events = {N} (comp_dur>=12, H={H}b). ref=close@endpoint, barriers {KS} ATR.")
    print(f"\n[B/C] TWO-SIDED reach + ordering (H1: symmetric? / H3-H4: one vs two-sided):")
    for k in KS:
        print(f"  k={k}ATR: P(up)={df[f'P_up{k}'].mean():.3f} P(dn)={df[f'P_dn{k}'].mean():.3f} P(BOTH)={df[f'P_both{k}'].mean():.3f} | "
              f"ord UP={np.mean(df[f'ord{k}']=='UP'):.2f} DN={np.mean(df[f'ord{k}']=='DN'):.2f} BOTH={np.mean(df[f'ord{k}']=='BOTH'):.2f} NEITHER={np.mean(df[f'ord{k}']=='NEITHER'):.2f}")
    print(f"\n[A] TIMING (median bars to first excursion / to max):")
    for k in KS:
        v=df[df[f't{k}']>0][f't{k}']; print(f"  first {k}ATR: medBars={v.median():.0f} (reached {len(v)}/{N})")
    print(f"  median bars to max-up={df['t_maxup'].median():.0f}, to max-dn={df['t_maxdn'].median():.0f}")
    print(f"\n[D] MIDPOINT RECROSS (H5 whipsaw): mean recross count={df['recross'].mean():.2f} median={df['recross'].median():.0f} | "
          f"P(0 recross=clean)={np.mean(df['recross']==0):.3f} P(>=2)={np.mean(df['recross']>=2):.3f} medT-to-1st-recross={df[df['t_recross1']>0]['t_recross1'].median():.0f}b")
    print(f"\n[E/F] FIRST BREAK quality (H2) + double-break (F): break rate={np.mean(df['fb_dir']!=0):.3f}")
    fbdf=df[df['fb_dir']!=0]
    for cl in ["CONTINUES","WHIPSAW","DOUBLE_BREAK","NEITHER"]:
        print(f"  {cl:12s}: {np.mean(fbdf['fb_class']==cl):.3f}")
    print(f"  first-break follow-through (ATR beyond level, median): ft1={fbdf['ft1'].median():.2f} ft2={fbdf['ft2'].median():.2f} ft4={fbdf['ft4'].median():.2f} | fb_MFE={fbdf['fb_mfe'].median():.2f} fb_MAE={fbdf['fb_mae'].median():.2f}")
    print(f"\n[G] RANGE CONSUMPTION (H7/H8: does first impulse consume expansion?): median fraction of dominant excursion by bar w:")
    for w in [1,2,4,8]: print(f"  first {w}b: {df[f'cons{w}'].median():.3f}")
    print(f"\n[CONTEXT] P(BOTH 1.0ATR) & recross by SESSION / ERA / severity-tercile (H6):")
    for col,vals in [("sess",["AS","LN","NY"]),("era",["D","C","O"])]:
        print(f"  by {col}: "+" ".join(f"{v}[P(both1)={df[df[col]==v]['P_both1.0'].mean():.2f} rec={df[df[col]==v]['recross'].mean():.1f} cont={np.mean(df[(df[col]==v)&(df['fb_dir']!=0)]['fb_class']=='CONTINUES'):.2f}]" for v in vals))
    sv=df['sev'].dropna(); q=np.nanquantile(sv,[0.33,0.66])
    for nm,msk in [("lowComp(sev hi)",df['sev']>=q[1]),("midComp",(df['sev']>=q[0])&(df['sev']<q[1])),("extremeComp(sev lo)",df['sev']<q[0])]:
        d=df[msk]; print(f"  sev {nm:20s}: P(both1)={d['P_both1.0'].mean():.2f} recross={d['recross'].mean():.2f} cont={np.mean(d[d['fb_dir']!=0]['fb_class']=='CONTINUES'):.2f} cons1={d['cons1'].median():.2f}")
    df.to_json(r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery\volpath_events.jsonl",orient="records",lines=True)
    print(f"\nwrote volpath_events.jsonl ({N} events). Phase-1 information only; hard gate assessed in VOLPATH_PHASE1_REPORT.md.")
if __name__=="__main__": main()
