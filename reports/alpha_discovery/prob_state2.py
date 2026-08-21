"""Phase 2: settle outcome A vs B. (1) year-to-year generalization (train early->test later) for Q10;
(2) freeze DISC probability threshold -> execute the top high-confidence bearish bucket (S15/S23);
(3) execute the best baseline (recent-return momentum) as the executability ceiling. If neither the
model's high-confidence states nor the best ranking signal convert -> NO_PROBABILISTIC_BEARISH_SIGNAL."""
import sys, os, numpy as np, pandas as pd
SP=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,SP)
import prob_state as P
X=P.X; y=P.y; disc=P.disc; conf=P.conf; valid=P.valid; H1=P.H1; PIP=P.PIP; H=P.H
o=P.o;h=P.h;l=P.l;c=P.c;atr=P.atr; dev=P.dev
dt=pd.to_datetime(H1["time"].to_numpy(),unit="s",utc=True); yr=dt.year.to_numpy()
auc=P.auc; fit_logit=P.fit_logit; predict=P.predict

# ---------- (1) year-to-year generalization (H4+H1 feature set) ----------
cols=[f"h4_{f}" for f in P.H4F]+[f"h1_{f}" for f in P.H1F]; Xf=X[cols].to_numpy(); r20=X["h1_r20"].to_numpy()
def sub(yrs): return np.array([i for i in valid if yr[i] in yrs])
def train_test(tr,te):
    tri=sub(tr); tei=sub(te)
    mu=Xf[tri].mean(0); sd=Xf[tri].std(0)+1e-9
    w=fit_logit((Xf[tri]-mu)/sd, y[tri].astype(float), 2.0)
    pm=predict(w,(Xf[tei]-mu)/sd)
    return auc(y[tei],pm), auc(y[tei],-r20[tei]), len(tei), y[tei].mean()
print("=== YEAR-TO-YEAR GENERALIZATION (model AUC | momentum -r20 AUC | n | base) ===")
for tr,te in [((2021,),(2022,)),((2021,2022),(2023,)),((2021,),(2023,)),((2022,),(2021,))]:
    am,ab,nte,bs=train_test(set(tr),set(te))
    print(f"  train{tr}->test{te}: model AUC={am:.3f} | -r20 AUC={ab:.3f} | n={nte} base={bs:.3f}")

# ---------- (2)+(3) execution ----------
h1_sh=(pd.Series(h).rolling(5,center=True).max()==pd.Series(h)).to_numpy()  # local swing highs (causal-safe: used only <= i)
COST=2.4
def h1_stop(i,entry):
    hi=[h[j] for j in range(max(0,i-6),i+1) if h1_sh[j] and h[j]>entry]
    if hi: return max(hi)
    a=atr[i] if atr[i]==atr[i] else (entry*0.003)
    return entry+1.5*a
def execute(idx, rr):
    Rs=[]; yy=[]; cool=-1
    for i in sorted(idx):
        if i<=cool or not dev[i] or i+1>=len(o): continue
        entry=o[i+1]; stop=h1_stop(i,entry); risk=(stop-entry)/PIP
        if risk<=2: continue
        tgt=entry-rr*risk*PIP; R=None; xb=i+1
        for j in range(i+1,min(i+1+H,len(o))):
            xb=j
            if h[j]>=stop: R=-1.0; break
            if l[j]<=tgt: R=+rr; break
        if R is None: R=((entry-c[xb])/PIP)/risk
        Rs.append(R-COST/risk); yy.append(yr[i]); cool=xb
    Rs=np.array(Rs)
    if len(Rs)==0: return None
    s=np.sort(Rs)[::-1]; brem=lambda p:(s[int(len(s)*p):].mean() if int(len(s)*p)<len(s) else np.nan)
    yrs={int(t):round(float(Rs[np.array(yy)==t].mean()),3) for t in sorted(set(yy))}
    top10=s[:max(1,int(len(s)*.1))].sum(); tot=Rs.sum()
    return dict(n=len(Rs),wr=round(float((Rs>0).mean()),3),avg=round(float(Rs.mean()),3),med=round(float(np.median(Rs)),3),
                b5=round(float(brem(.05)),3),b10=round(float(brem(.10)),3),
                top10=round(float(top10/tot),3) if tot>0 else None,yy=yrs)

# high-confidence bucket: freeze DISC 95th/98th pct threshold of primary model probs
pdisc=P.prim.prob(disc); pconf=P.prim.prob(conf); pall=P.prim.prob(valid)
for q in (0.90,0.95,0.98):
    thr=np.quantile(pdisc,q)
    idx=[valid[k] for k in range(len(valid)) if pall[k]>=thr]
    conf_states=[i for i in idx if i in set(conf.tolist())]
    br=y[np.array(conf_states)].mean() if conf_states else np.nan
    print(f"\n=== HIGH-CONF BUCKET p>=DISC-q{q} (thr={thr:.3f}) | CONF n={len(conf_states)} actual bear-rate={br:.3f} (base {P.base_c:.3f}) ===")
    for rr in (1.5,2.0,3.0):
        r=execute(conf_states,rr)
        if r: print(f"   exec rr{rr}: n{r['n']} WR{r['wr']} avg{r['avg']:+.3f} med{r['med']:+.3f} b5{r['b5']:+.3f} b10{r['b10']:+.3f} top10%{r['top10']} yy{r['yy']}")

# best baseline executability: recent-return momentum short (r20 in DISC bottom 15%)
thr_m=np.quantile(r20[disc],0.15); mom_states=[i for i in valid if r20[i]<=thr_m and i in set(conf.tolist())]
print(f"\n=== MOMENTUM-SHORT (r20<=DISC-q15={thr_m:.3f}) CONF states n={len(mom_states)} bear-rate={y[np.array(mom_states)].mean():.3f} ===")
for rr in (1.5,2.0,3.0):
    r=execute(mom_states,rr)
    if r: print(f"   exec rr{rr}: n{r['n']} WR{r['wr']} avg{r['avg']:+.3f} med{r['med']:+.3f} b5{r['b5']:+.3f} b10{r['b10']:+.3f} top10%{r['top10']} yy{r['yy']}")
