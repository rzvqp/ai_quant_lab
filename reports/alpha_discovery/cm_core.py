"""cm_core.py — CROSS_MARKET_RELATIVE_RESPONSE_FACTORY_V1 core. XAU-vs-DXY relative-response residual (causal), on the ratified DXY join.

Only governed cross-market series = ICE DXY H1 (3 slices b0 2011-13 / b1 2016-18 / y2123 2021-23; 2024+ protected). No NDX/risk proxy ->
family F (dual-confirmation) NOT testable. Relative response (the NEW variable, not the falsified simple DXY impulse):
  trailing beta W of XAU 1h return on DXY 1h return (backward only) ; EXPECTED = beta*DXY_move ; RESIDUAL = XAU_move - EXPECTED ;
  z-residual = RESIDUAL / trailing std(XAU_move). Positive z = XAU stronger than DXY implies; negative = weaker.
All causal (DXY known at decision via time+3600 contract). Entry = next H1 OPEN; conservative same-bar barrier; 2R; cost 0.419/risk.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import dxy_data as DX

COST=0.419; W=120

def prep():
    fr=DX.build(); out={}
    for era,m in fr.items():
        m=m.sort_values("time").reset_index(drop=True)
        o=m["open"].to_numpy(float); h=m["high"].to_numpy(float); l=m["low"].to_numpy(float); c=m["close"].to_numpy(float)
        t=m["time"].to_numpy(); n=len(c)
        xret1=c-np.r_[c[0],c[:-1]]; xret4=c-np.r_[ [c[0]]*4, c[:-4]]
        dret1=m["d_ret1_l0"].to_numpy(float); dret4=m["d_ret4_l0"].to_numpy(float)
        # trailing beta of xret1 on dret1 (rolling cov/var, shift 1 = strictly past)
        s=pd.Series(xret1); d=pd.Series(dret1)
        cov=s.rolling(W).cov(d).shift(1).to_numpy(); var=d.rolling(W).var().shift(1).to_numpy()
        beta=np.where(np.abs(var)>1e-9, cov/var, 0.0)
        vol1=pd.Series(xret1).rolling(W).std().shift(1).to_numpy(); vol4=pd.Series(xret4).rolling(W).std().shift(1).to_numpy()
        exp1=beta*dret1; exp4=beta*dret4
        res1=xret1-exp1; res4=xret4-exp4
        z1=np.where(vol1>1e-9,res1/vol1,np.nan); z4=np.where(vol4>1e-9,res4/vol4,np.nan)
        ez1=np.where(vol1>1e-9,exp1/vol1,np.nan); ez4=np.where(vol4>1e-9,exp4/vol4,np.nan)  # implied-move z
        az4=np.where(vol4>1e-9,xret4/vol4,np.nan)                                            # actual-move z
        tr=np.maximum.reduce([h-l,np.abs(h-np.r_[c[0],c[:-1]]),np.abs(l-np.r_[c[0],c[:-1]])])
        atr=pd.Series(tr).rolling(14).mean().shift(1).to_numpy()
        yr=pd.to_datetime(t,unit='s',utc=True).year.to_numpy(); hr=pd.to_datetime(t,unit='s',utc=True).hour.to_numpy()
        out[era]=dict(o=o,h=h,l=l,c=c,t=t,n=n,atr=atr,beta=beta,dret1=dret1,dret4=dret4,
                      res4=res4,z1=z1,z4=z4,ez1=ez1,ez4=ez4,az4=az4,vol4=vol4,yr=yr,hr=hr)
    return out

def resolve(E, k, side, tgtR=2.0, H=6):
    """Enter at H1 OPEN of bar k; stop=1*ATR; target=2R; conservative same-bar (both reachable -> stop). net-R after cost."""
    o=E["o"];h=E["h"];l=E["l"];c=E["c"];atr=E["atr"];n=E["n"]
    if k>=n or not np.isfinite(atr[k]) or atr[k]<=0: return None
    entry=o[k]; risk=atr[k]; stop=entry-side*risk; tgt=entry+side*2*risk*(tgtR/2.0)
    tgt=entry+side*tgtR*risk; end=min(k+H,n-1); res=None; mfe=-1e9
    for j in range(k,end+1):
        fav=(h[j]-entry)/risk if side>0 else (entry-l[j])/risk; mfe=max(mfe,fav)
        t_hit=(h[j]>=tgt) if side>0 else (l[j]<=tgt); s_hit=(l[j]<=stop) if side>0 else (h[j]>=stop)
        if t_hit and s_hit: res=-1.0; break
        if s_hit: res=-1.0; break
        if t_hit: res=tgtR; break
    if res is None: res=side*(c[end]-entry)/risk
    return dict(net=res-COST/risk, g=res, mfe=mfe, risk=risk, k=k)

def era_tag(era): return {"b0":"D","b1":"D","y2123":"O"}[era]   # b0/b1 = pre-2019 (D); y2123 = 2021-23 (C/O)
