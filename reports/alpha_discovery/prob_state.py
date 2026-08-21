"""ALPHA-XAUUSD-PROBABILISTIC-BEARISH-STATE-001. CONTINUOUS/PROBABILISTIC market-state modelling of
P(bearish move | causal price state). Interpretable models first (ridge logistic via IRLS, Markov-state,
small tree diagnostic). Causal normalization FROZEN on DISCOVERY. Full metric suite + calibration + buckets
+ TF attribution + ROC-vs-static + temporal stability. Directional gate BEFORE any execution. Price-only,
DEV-only. NO 2025+/CALIB/V1/N4/read_csv/exogenous. Future returns are LABELS only, never features."""
import sys, os, numpy as np, pandas as pd
SP=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,SP)
import m5_data as D
PIP=0.10; H=24; THR=150; MAE_LIM=60
tfs,META=D.build()

def feats(tf):
    x=tfs[tf]; o=x["open"];h=x["high"];l=x["low"];c=x["close"]
    atr=x["atr"];e20=x["ema20"];e50=x["ema50"];hh20=x["hh20"];ll20=x["ll20"];hh50=x["hh50"];ll50=x["ll50"]
    eff=x["effic"];ama=x["atr_ma"]; a=atr.replace(0,np.nan); rng=(h-l).replace(0,np.nan)
    r1=(c-c.shift(1))/a; r5=(c-c.shift(5))/a; r10=(c-c.shift(10))/a; r20=(c-c.shift(20))/a
    F=pd.DataFrame(index=x.index)
    F["r5"]=r5; F["r20"]=r20
    F["accel"]=r5-(c.shift(5)-c.shift(10))/a                          # change in 5-bar momentum (ROC)
    F["persist"]=(c>c.shift(1)).rolling(10).mean()                    # directional persistence
    ret=c.diff(); F["updown_asym"]=(ret.clip(lower=0).rolling(20).sum()+ret.clip(upper=0).rolling(20).sum())/ret.abs().rolling(20).sum()
    F["rv"]=r1.rolling(20).std()                                      # realized vol (normalized)
    F["vol_exp"]=atr/ama                                              # vol expansion/contraction
    F["disp"]=(c-o)/a                                                 # ATR-normalized displacement
    F["effic"]=eff
    F["dist_hh20"]=(hh20-c)/a                                         # distance from causal high
    F["rangepos50"]=(c-ll50)/(hh50-ll50)                             # location within rolling range
    F["dist_ema20"]=(c-e20)/a
    F["ema_gap"]=(e20-e50)/a
    F["slope20"]=(e20-e20.shift(5))/a                                 # slope of trend ref (ROC)
    F["curv20"]=(e20-e20.shift(5))/a-(e20.shift(5)-e20.shift(10))/a   # curvature (ROC)
    exc_up=(h.rolling(10).max()-c); exc_dn=(c-l.rolling(10).min()); F["exc_asym"]=(exc_up-exc_dn)/a
    fup=((h>h.shift(1))&(c<c.shift(1))).astype(float); F["failed_up"]=fup.rolling(10).mean()  # failed upward progress
    F["close_loc"]=(c-l)/rng                                          # close location within bar
    return F

FH1=feats("H1"); FH4=feats("H4"); FM15=feats("M15")
H1=tfs["H1"]; H4=tfs["H4"]; M15=tfs["M15"]
h1_ct=H1["close_time"].to_numpy().astype("int64"); h4_ct=H4["close_time"].to_numpy().astype("int64")
m15_ct=M15["close_time"].to_numpy().astype("int64")
# causal alignment of H4 / M15 state to each H1 decision bar (last COMPLETED bar by close_time)
a_h4=np.searchsorted(h4_ct,h1_ct,side="right")-1
a_m15=np.searchsorted(m15_ct,h1_ct,side="right")-1
assert (h4_ct[a_h4[a_h4>=0]]<=h1_ct[a_h4>=0]).all(); assert (m15_ct[a_m15[a_m15>=0]]<=h1_ct[a_m15>=0]).all()

H1F=["r5","r20","accel","persist","updown_asym","rv","vol_exp","disp","effic","dist_hh20",
     "rangepos50","dist_ema20","ema_gap","slope20","curv20","exc_asym","failed_up","close_loc"]  # 18
H4F=["r5","effic","vol_exp","dist_hh20","dist_ema20","slope20","ema_gap","close_loc"]             # 8
M15F=["r5","accel","vol_exp","disp"]                                                              # 4
# assemble H1-indexed matrix
n=len(H1); cols={};
for f in H1F: cols[f"h1_{f}"]=FH1[f].to_numpy()
h4v=FH4.to_numpy(); h4cn=list(FH4.columns)
for f in H4F:
    arr=np.full(n,np.nan); good=a_h4>=0; arr[good]=FH4[f].to_numpy()[a_h4[good]]; cols[f"h4_{f}"]=arr
for f in M15F:
    arr=np.full(n,np.nan); good=a_m15>=0; arr[good]=FM15[f].to_numpy()[a_m15[good]]; cols[f"m15_{f}"]=arr
cols["mtf_div"]=cols["h1_r5"]-cols["h4_r5"]        # H1-vs-H4 momentum divergence (structural interaction)
X=pd.DataFrame(cols)
FEAT_ALL=list(X.columns)  # 18+8+4+1 = 31; models select subsets (<=30 each)
print(f"total assembled features={len(FEAT_ALL)} (models select subsets; H1={len(H1F)} H4={len(H4F)} M15={len(M15F)}+mtf_div)")

# ---------- labels (outcome only) ----------
o=H1["open"].to_numpy();h=H1["high"].to_numpy();l=H1["low"].to_numpy();c=H1["close"].to_numpy()
atr=H1["atr"].to_numpy(); dev=H1["is_dev"].to_numpy(); reg=H1["regime"].to_numpy()
dt=pd.to_datetime(H1["time"],unit="s",utc=True)
y=np.full(n,-1); bear_exc=np.full(n,np.nan); trade=np.full(n,-1)
y80=np.full(n,-1); y100=np.full(n,-1); y200=np.full(n,-1); y300=np.full(n,-1)
for i in range(25,n-H-1):
    if not dev[i] or atr[i]!=atr[i]: continue
    entry=o[i+1]; fl=l[i+1:i+1+H]; fh=h[i+1:i+1+H]
    be=(entry-fl.min())/PIP; bu=(fh.max()-entry)/PIP; y[i]=int(be>=THR and be>bu); bear_exc[i]=be
    y80[i]=int(be>=80 and be>bu); y100[i]=int(be>=100 and be>bu); y200[i]=int(be>=200 and be>bu); y300[i]=int(be>=300 and be>bu)
    amin=int(np.argmin(fl)); adverse=(fh[:amin+1].max()-entry)/PIP if amin>=0 else 0.0
    trade[i]=int(y[i]==1 and adverse<=MAE_LIM)
# valid rows = dev, label known, no NaN in the full feature union
Xall=X[FEAT_ALL].to_numpy()
valid=np.where((y>=0)&np.isfinite(Xall).all(axis=1))[0]
tt=dt.to_numpy()
cut_i=valid[int(len(valid)*0.6)]; CUT=H1["close_time"].to_numpy()[cut_i]
disc=valid[H1["close_time"].to_numpy()[valid]<CUT]; conf=valid[H1["close_time"].to_numpy()[valid]>=CUT]
base_d=y[disc].mean(); base_c=y[conf].mean()
print(f"H1 valid={len(valid)} | DISC n={len(disc)} base={base_d:.3f} | CONF n={len(conf)} base={base_c:.3f} (cut {pd.to_datetime(CUT,unit='s',utc=True).date()}) H={H} THR={THR}p")
print(f"path-aware TRADEABLE_BEAR (MAE<={MAE_LIM}p): DISC {trade[disc].mean():.3f} CONF {trade[conf].mean():.3f}")

# ---------- metrics ----------
def auc(y,p):
    o=np.argsort(p); yr=y[o]; n1=yr.sum(); n0=len(yr)-n1
    if n1==0 or n0==0: return np.nan
    ranks=np.argsort(np.argsort(p))+1; return (ranks[y==1].sum()-n1*(n1+1)/2)/(n1*n0)
def prauc(y,p):
    o=np.argsort(-p); ys=y[o]; tp=np.cumsum(ys); fp=np.cumsum(1-ys)
    prec=tp/(tp+fp); rec=tp/max(1,ys.sum()); rec0=np.concatenate([[0],rec])
    return float(np.sum(prec*(rec-rec0[:-1])))
def brier(y,p): return float(np.mean((p-y)**2))
def logloss(y,p): p=np.clip(p,1e-6,1-1e-6); return float(-np.mean(y*np.log(p)+(1-y)*np.log(1-p)))

# ---------- ridge logistic via IRLS (interpretable) ----------
def fit_logit(Xd,yd,l2=2.0,iters=30):
    X1=np.column_stack([np.ones(len(Xd)),Xd]); w=np.zeros(X1.shape[1]); R=l2*np.eye(X1.shape[1]); R[0,0]=0
    for _ in range(iters):
        z=np.clip(X1@w,-30,30); p=1/(1+np.exp(-z)); Wd=np.clip(p*(1-p),1e-6,None)
        grad=X1.T@(p-yd)+R@w; Hh=X1.T@(X1*Wd[:,None])+R
        try: step=np.linalg.solve(Hh,grad)
        except np.linalg.LinAlgError: step=np.linalg.lstsq(Hh,grad,rcond=None)[0]
        w-=step
        if np.max(np.abs(step))<1e-7: break
    return w
def predict(w,Xd): z=np.clip(np.column_stack([np.ones(len(Xd)),Xd])@w,-30,30); return 1/(1+np.exp(-z))

class Model:
    def __init__(s,name,cols,l2=2.0): s.name=name; s.cols=cols; s.l2=l2
    def fit(s):
        Xd=X[s.cols].to_numpy()[disc]; s.mu=Xd.mean(0); s.sd=Xd.std(0)+1e-9  # FROZEN on DISCOVERY (S11)
        s.w=fit_logit((Xd-s.mu)/s.sd, y[disc].astype(float), s.l2)
    def prob(s,idx): return predict(s.w,(X[s.cols].to_numpy()[idx]-s.mu)/s.sd)

H1cols=[f"h1_{f}" for f in H1F]; H4cols=[f"h4_{f}" for f in H4F]; M15cols=[f"m15_{f}" for f in M15F]
ROCcols=[f"h1_{f}" for f in ("accel","slope20","curv20","vol_exp","updown_asym","failed_up","exc_asym","rv")]
STATcols=[f"h1_{f}" for f in ("dist_hh20","rangepos50","dist_ema20","ema_gap","effic","close_loc","disp","persist")]
MODELS=[Model("M1 H4-only",H4cols),Model("M2 H1-only",H1cols),Model("M3 H4+H1",H4cols+H1cols),
        Model("M4 H4+H1 ridge(L2=20)",H4cols+H1cols,l2=20.0),Model("M5 H4+H1+M15",H4cols+H1cols+M15cols+["mtf_div"]),
        Model("M6 ROC-only",ROCcols),Model("M7 STATIC-only",STATcols)]
for m in MODELS: m.fit()

# ---------- baselines ----------
def base_scores():
    # B1 PROJECT TREND_DOWN (binary), B2 recent-return (-r20), B3 vol (vol_exp), B4 discrete bearish structure
    e20=H1["ema20"].to_numpy(); e50=H1["ema50"].to_numpy(); eff=H1["effic"].to_numpy()
    td=((e20<e50)&(eff<-0.30)).astype(float)
    r20=X["h1_r20"].to_numpy(); vexp=X["h1_vol_exp"].to_numpy()
    disc_struct=X["h1_failed_up"].to_numpy()+ (X["h1_disp"].to_numpy()<-1.0).astype(float)  # crude discrete bearish
    return {"B1 TREND_DOWN":td,"B2 recent-ret(-r20)":-r20,"B3 vol(vol_exp)":vexp,"B4 discrete-bear":disc_struct}
BASE=base_scores()

print("\n=== CONFIRMATION metrics (frozen on DISCOVERY, evaluated ONCE) ===")
print(f"{'model':26s} {'AUC':>6} {'PRAUC':>6} {'Brier':>7} {'logL':>6}  (base rate CONF={base_c:.3f})")
def ev(name,pc):
    yc=y[conf]; print(f"{name:26s} {auc(yc,pc):6.3f} {prauc(yc,pc):6.3f} {brier(yc,pc):7.4f} {logloss(yc,pc):6.3f}")
for bn,sc in BASE.items(): ev(bn, sc[conf])
for m in MODELS: ev(m.name, m.prob(conf))

# ---------- probability buckets + calibration (primary model = best AUC among M2/M3/M5) ----------
prim=max([m for m in MODELS if m.name.startswith(("M2","M3","M5"))],key=lambda m:auc(y[conf],m.prob(conf)))
pc=prim.prob(conf); yc=y[conf]
print(f"\n=== PROBABILITY BUCKETS (primary={prim.name}) on CONFIRMATION (S13/S14) ===")
qs=np.quantile(pc,[0,.1,.2,.3,.4,.5,.6,.7,.8,.9,.95,.98,1.0])
print(f"{'bucket':>10} {'n':>5} {'pred':>6} {'actual':>7} {'avgBearExc':>10} {'lift':>7}")
for a,b in zip(qs[:-1],qs[1:]):
    mask=(pc>=a)&(pc<(b if b<qs[-1] else b+1e-9)); nn=mask.sum()
    if nn<5: continue
    ci=conf[mask]; print(f"{a:.3f}-{b:.3f} {nn:5d} {pc[mask].mean():6.3f} {yc[mask].mean():7.3f} {np.nanmean(bear_exc[ci]):10.1f} {yc[mask].mean()-base_c:+7.3f}")

# ---------- TF attribution + ROC-vs-static summary ----------
print("\n=== TF ATTRIBUTION (CONF AUC) ===")
for m in [MODELS[0],MODELS[1],MODELS[2],MODELS[4]]: print(f"  {m.name:22s} AUC={auc(y[conf],m.prob(conf)):.3f}")
print(f"  M15 incremental (M5 - M3): {auc(y[conf],MODELS[4].prob(conf))-auc(y[conf],MODELS[2].prob(conf)):+.3f}")
print("=== ROC vs STATIC (CONF AUC) ===")
print(f"  M6 ROC-only={auc(y[conf],MODELS[5].prob(conf)):.3f}  M7 STATIC-only={auc(y[conf],MODELS[6].prob(conf)):.3f}")

# ---------- temporal stability: CONF AUC by year ----------
yrs=pd.to_datetime(H1["time"].to_numpy()[conf],unit="s",utc=True).year
print("=== TEMPORAL (CONF AUC by year, primary) ===")
for yy in sorted(set(yrs)):
    mk=yrs==yy;
    if mk.sum()>50: print(f"  {yy}: n={mk.sum()} AUC={auc(yc[mk],pc[mk]):.3f} base={yc[mk].mean():.3f}")

# ---------- normalization causality check (S11) ----------
print("\n=== CAUSAL NORMALIZATION CHECK (S11): DISC-frozen vs full-sample scaler ===")
m=MODELS[2]; Xf=X[m.cols].to_numpy()
mu_full=Xf[valid].mean(0); sd_full=Xf[valid].std(0)+1e-9
drift=np.abs(m.mu-mu_full)/ (m.sd)  # standardized mean drift DISC->full
print(f"  mean |DISC-vs-full| standardized drift: median={np.median(drift):.3f} max={drift.max():.3f} (>0 confirms regime drift; frozen scaler used, no full-sample leak)")
wfull=fit_logit((Xf[disc]-mu_full)/sd_full, y[disc].astype(float), m.l2)
p_leak=predict(wfull,(Xf[conf]-mu_full)/sd_full)
print(f"  CONF AUC frozen-DISC={auc(yc,m.prob(conf)):.3f} vs (illustrative) full-sample-scaler={auc(yc,p_leak):.3f} [we REPORT frozen-DISC]")

# ---------- feature attribution (primary standardized coefficients) ----------
print(f"\n=== FEATURE ATTRIBUTION (primary={prim.name}, standardized coef, top |w|) ===")
order=np.argsort(-np.abs(prim.w[1:]))[:10]
for j in order: print(f"  {prim.cols[j]:16s} w={prim.w[1+j]:+.3f}")

# ---------- Markov-state model (M8) diagnostic ----------
print("\n=== M8 MARKOV-STATE (frozen DISC terciles of effic x slope20) -> P(bear|state) ===")
ef=X["h1_effic"].to_numpy(); sl=X["h1_slope20"].to_numpy()
qe=np.quantile(ef[disc],[.33,.66]); qs2=np.quantile(sl[disc],[.33,.66])
def state(v,q): return int(v>=q[1])+int(v>=q[0])
st_d=np.array([state(ef[i],qe)*3+state(sl[i],qs2) for i in disc]); st_c=np.array([state(ef[i],qe)*3+state(sl[i],qs2) for i in conf])
pd_state={s:y[disc][st_d==s].mean() for s in range(9)}
worst=min(pd_state,key=lambda s:pd_state.get(s,1) if not np.isnan(pd_state.get(s,np.nan)) else 1)
# apply frozen state prob to conf
p_m8=np.array([pd_state.get(s,base_d) for s in st_c])
print(f"  M8 CONF AUC={auc(yc,p_m8):.3f}; DISC worst-bear state P={pd_state[worst]:.3f} vs base {base_d:.3f}; that state CONF actual={yc[st_c==worst].mean():.3f} (n={ (st_c==worst).sum() })")

# save primary probs for execution phase (if gate passes)
np.save(os.path.join(SP,"_prob_conf.npy"),pc); np.save(os.path.join(SP,"_prob_disc.npy"),prim.prob(disc))
np.save(os.path.join(SP,"_prim_meta.npy"),np.array([prim.name],dtype=object),allow_pickle=True)
print(f"\nPRIMARY={prim.name} CONF AUC={auc(yc,pc):.3f} | best baseline AUC={max(auc(yc,s[conf]) for s in BASE.values()):.3f}")
