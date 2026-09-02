"""attr_run.py — STRATEGY_OUTCOME_ATTRIBUTION_EDGE_RESCUE_V1. Mine the existing causal strategy graveyard for hidden conditional edge.
Master trade table across eligible M15 strategies (HTF x4, OBR-corrected + OB-exec x3, session x6) with common causal PRE-ENTRY features;
per-strategy + CROSS-STRATEGY meta-state attribution; winner/loser discrimination; injected positive control. Hypothesis generation only.
Uses ONLY corrected causal implementations (OBR = ob_exec EXEC-A true-limit, NOT the fill-artifact version). No promotion, no modification.
"""
import sys, numpy as np, pandas as pd, os
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import ob_core as OB, ob_exec as EX, htf_setups as HS, sess_core as SC, sess_scan as SS
OUT=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"

def feature_panel():
    m,H1,H4,P=OB.build()
    dt=m["dt"]; c=P["c"]; atr=P["atr"]; n=P["n"]
    F={}
    F["year"]=dt.dt.year.values; F["month"]=dt.dt.month.values; F["dow"]=dt.dt.dayofweek.values
    F["hour"]=dt.dt.hour.values; F["hb"]=(dt.dt.hour.values*2+(dt.dt.minute.values>=30).astype(int))  # 0..47 half-hour bucket
    hr=F["hour"]; F["sess"]=np.where(hr<8,"AS",np.where(hr<13,"LN",np.where(hr<20,"NY","LT")))
    F["atr"]=atr; F["atr_pct"]=pd.Series(atr).rolling(2000).rank(pct=True).shift(1).to_numpy()
    F["volb"]=np.where(F["atr_pct"]<0.33,"lo",np.where(F["atr_pct"]<0.67,"md","hi"))
    F["h1up"]=(P.get("ema80",m.get("ema80")) if False else None)  # placeholder
    ema80=m["close"].ewm(span=80,adjust=False).mean().to_numpy(); ema320=m["close"].ewm(span=320,adjust=False).mean().to_numpy()
    F["h1up"]=ema80>ema320
    ctx=H4["ctx"].values; h4i=m["h4i"].values; F["h4ctx"]=np.where(h4i>=0,ctx[np.clip(h4i,0,len(ctx)-1)],"NA")
    hi96=pd.Series(P["h"]).rolling(96).max().shift(1).to_numpy(); lo96=pd.Series(P["l"]).rolling(96).min().shift(1).to_numpy()
    F["rloc24"]=(c-lo96)/np.maximum(hi96-lo96,1e-9)
    F["retz"]=(c-pd.Series(c).shift(12).to_numpy())/np.maximum(atr,1e-9)
    return m,H1,H4,P,F

def gen_trades(m,H1,H4,P):
    """Return list of dicts: sid, ent(bar), side, net, mfe, mae. Only corrected causal implementations."""
    T=[]
    # HTF families (need HS.prep panel; same M15 indices)
    try:
        mp,H1p,H4p=HS.prep()
        for fam in ("PBK_TREND","RECLAIM","RANGE_FADE","TGT_BREAK"):
            for r in HS.evaluate(mp,HS.detect(mp,H1p,H4p,fam,htf_on=True)):
                T.append(dict(sid=f"HTF_{fam}",ent=int(r["ent"]),side=int(r["side"]),net=float(r["net_R"]),mfe=float(r["mfe_R"]),mae=float(r["mae_R"])))
    except Exception as e: print("HTF gen err",e)
    # OBR corrected (EXEC-A true resting limit) + OB executions B/C/D
    try:
        for mode,nm in (("A","OBR_A_limit"),("B","OBEXEC_B"),("C","OBEXEC_C"),("D","OBEXEC_D")):
            for r in EX.collect(P,m,mode):
                T.append(dict(sid=nm,ent=int(r["k"]),side=1,net=float(r["net"]),mfe=float(r.get("mfe_R",np.nan)),mae=np.nan))  # OBR bull-only
    except Exception as e: print("OBEXEC gen err",e)
    # session families (SC panel, same indices); resolve to net via SC.resolve_entry
    try:
        D=SC.build(); lon,ny=SS.per_date_idx(D)
        fams={"SESS_A":SS.trades_A(D,lon),"SESS_B":SS.trades_B(D,lon),"SESS_C":SS.trades_C(D,ny),
              "SESS_D":SS.trades_D(D,ny),"SESS_E":SS.trades_E(D,ny),"SESS_Fc":SS.trades_F(D,ny,"cont")}
        for nm,trs in fams.items():
            for eb,side,stop in trs:
                r=SC.resolve_entry(D,eb,side,stop,2.0)
                if r: T.append(dict(sid=nm,ent=int(r["k"]),side=int(side),net=float(r["net"]),mfe=float(r.get("mfe",np.nan)),mae=np.nan))
    except Exception as e: print("SESS gen err",e)
    return T

def attach(T,F,n):
    rows=[]
    for t in T:
        e=t["ent"]
        if e<0 or e>=n: continue
        d=dict(t);
        for k,v in F.items(): d[k]=v[e]
        d["align"]= "ALIGN" if ((t["side"]>0 and d["h4ctx"]=="TREND_UP") or (t["side"]<0 and d["h4ctx"]=="TREND_DOWN")) else ("COUNTER" if d["h4ctx"] in ("TREND_UP","TREND_DOWN") else "NEUT")
        rows.append(d)
    return pd.DataFrame(rows)

def expec(df, by):
    g=df.groupby(by)["net"]; return g.agg(N="count",exp="mean",wr=lambda x:(x>0).mean())

def main():
    m,H1,H4,P,F=feature_panel(); n=P["n"]
    T=gen_trades(m,H1,H4,P)
    df=attach(T,F,n)
    print(f"TOTAL valid causal trades={len(df)}  strategies={df['sid'].nunique()}")
    df.to_csv(os.path.join(OUT,"STRATEGY_ATTRIBUTION_MASTER_TABLE.csv"),index=False)
    # POSITIVE CONTROL: synthetic strategy where high-vol=+0.3, low-vol=-0.3
    rng=np.random.RandomState(1); nsim=6000; ebs=rng.choice(np.where(np.isfinite(F["atr_pct"]))[0],nsim)
    sim=[];
    for e in ebs:
        vp=F["atr_pct"][e]; base=0.3 if vp>0.67 else (-0.3 if vp<0.33 else 0.0); sim.append(dict(sid="POSCTRL",ent=int(e),side=1,net=base+rng.normal(0,0.5),mfe=np.nan,mae=np.nan))
    sdf=attach(sim,F,n); pc=sdf.groupby("volb")["net"].mean()
    pc_ok = pc.get("hi",0)-pc.get("lo",0) > 0.3
    print(f"POSITIVE_CONTROL volb exp: lo={pc.get('lo',float('nan')):+.3f} md={pc.get('md',float('nan')):+.3f} hi={pc.get('hi',float('nan')):+.3f} -> {'PASS' if pc_ok else 'FAIL'}")
    # ===== per-strategy summary + LONG/SHORT + key effects =====
    print("\n== PER-STRATEGY (net exp; L/S split; best session/vol/align/dow) ==")
    recs=[]
    for sid,g in df.groupby("sid"):
        L=g[g.side>0]["net"]; S=g[g.side<0]["net"]
        bs=g.groupby("sess")["net"].mean(); bv=g.groupby("volb")["net"].mean(); ba=g.groupby("align")["net"].mean(); bd=g.groupby("dow")["net"].mean()
        rec=dict(sid=sid,N=len(g),exp=g["net"].mean(),wr=(g["net"]>0).mean(),
                 Lexp=L.mean() if len(L) else np.nan,LN=len(L),Sexp=S.mean() if len(S) else np.nan,SN=len(S),
                 best_sess=bs.idxmax() if len(bs) else "-",best_sess_exp=bs.max() if len(bs) else np.nan,
                 best_vol=bv.idxmax() if len(bv) else "-",align_exp=ba.get("ALIGN",np.nan),counter_exp=ba.get("COUNTER",np.nan),
                 best_dow=bd.idxmax() if len(bd) else -1)
        recs.append(rec)
        print(f"  {sid:14s} N={len(g):5d} exp={rec['exp']:+.3f} | L={rec['Lexp']:+.3f}(n{rec['LN']}) S={rec['Sexp']:+.3f}(n{rec['SN']}) | "
              f"bestSess={rec['best_sess']}({rec['best_sess_exp']:+.2f}) bestVol={rec['best_vol']} ALIGN={rec['align_exp']:+.2f} COUNTER={rec['counter_exp']:+.2f} bestDoW={rec['best_dow']}")
    pd.DataFrame(recs).to_csv(os.path.join(OUT,"STRATEGY_RESCUE_HYPOTHESIS_REGISTER.csv"),index=False)
    # matrices
    df.pivot_table(index="sid",columns="hb",values="net",aggfunc="mean").to_csv(os.path.join(OUT,"STRATEGY_TIME_BUCKET_MATRIX.csv"))
    df.pivot_table(index="sid",columns="dow",values="net",aggfunc="mean").to_csv(os.path.join(OUT,"STRATEGY_WEEKDAY_MATRIX.csv"))
    df.pivot_table(index="sid",columns="sess",values="net",aggfunc="mean").to_csv(os.path.join(OUT,"STRATEGY_SESSION_MATRIX.csv"))
    # ===== CROSS-STRATEGY META-STATE =====
    print("\n== CROSS-STRATEGY META-STATE: fraction of strategies with positive exp per state (pooled exp) ==")
    def meta(col, vals=None):
        sids=df["sid"].unique();
        for v in (vals if vals is not None else sorted(df[col].dropna().unique())):
            sub=df[df[col]==v]; per=[(sub[sub.sid==s]["net"].mean()) for s in sids if (sub.sid==s).sum()>=50]
            per=[x for x in per if np.isfinite(x)]
            if len(per)<3: continue
            fpos=np.mean([x>0 for x in per])
            print(f"  {col}={str(v):10s} pooled_exp={sub['net'].mean():+.3f} strat+={fpos:.2f} ({sum(x>0 for x in per)}/{len(per)}) N={len(sub)}")
    meta("sess"); meta("volb",["lo","md","hi"]); meta("align",["ALIGN","COUNTER","NEUT"])
    print("  -- side --")
    for sd,nm in ((1,"LONG"),(-1,"SHORT")):
        sub=df[df.side==sd]; sids=df["sid"].unique(); per=[sub[sub.sid==s]["net"].mean() for s in sids if (sub.sid==s).sum()>=50]; per=[x for x in per if np.isfinite(x)]
        if per: print(f"  side={nm:5s} pooled_exp={sub['net'].mean():+.3f} strat+={np.mean([x>0 for x in per]):.2f} ({sum(x>0 for x in per)}/{len(per)})")
    # ===== winner/loser pre-entry (pooled correlation of net with features) =====
    print("\n== POOLED winner/loser: mean net by key pre-entry bucket (all strategies) ==")
    for col,vals in (("sess",None),("volb",["lo","md","hi"]),("align",["ALIGN","COUNTER","NEUT"])):
        e=expec(df,col); print(f"  {col}:", {str(k):round(v,3) for k,v in e["exp"].items()})

if __name__=="__main__":
    main()
