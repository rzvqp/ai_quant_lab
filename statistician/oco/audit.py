import sys, json, math
sys.path.insert(0, '.')
import numpy as np, pandas as pd
from rep import (S, PDH, PDL, RISK, PDN, Hi, Lo, Cl, O, TS, YR, DOW, N, H, COST,
                 episode, run, stats, d, HOLDOUT)
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = run(2.0); ST = stats(BASE, "base 2R", quiet=True)
net = ST["net"]; ii = ST["ii"]; tr = ST["tr"]
yE = YR[S[ii]]; tsE = TS[S[ii]]
rk = np.array([r["risk"] for r in tr])

print("="*122); print("  §3  OCO EXECUTION AUDIT"); print("="*122)
amb = ST["amb"]; nt = ST["notrig"]
print(f"  total candidate episodes            : {len(S)}")
print(f"  no trigger within 24h               : {nt}  ({nt/len(S):.2%})")
print(f"  BOTH activations inside ONE M15 bar : {amb}  ({amb/len(S):.3%})  -> Alpha SKIPS these (conservative)")
print(f"  traded                              : {len(net)}")

# --- gap-through-the-activation: the fill assumption Alpha's spec does not handle
gap = []; gap_sz = []
for r in tr:
    j = r["trig_bar"]; dr = r["side"]; lvl = r["entry"]
    if (dr > 0 and O[j] > lvl) or (dr < 0 and O[j] < lvl):
        gap.append(r["i"]); gap_sz.append(abs(O[j] - lvl) / r["risk"])
gap = np.array(gap); gap_sz = np.array(gap_sz)
inmask = np.isin(ii, gap)
print(f"\n  ** GAP-THROUGH FILLS ** trigger bar OPENED beyond the activation level:")
print(f"     episodes {len(gap)} ({len(gap)/len(net):.2%}) -- Alpha fills at the LEVEL; a real stop order fills at the OPEN")
print(f"     slippage if filled at the open: median {np.median(gap_sz):.4f}R  mean {gap_sz.mean():.4f}R  p95 {np.quantile(gap_sz,0.95):.4f}R")
print(f"     day-of-week of gap fills: {dict(zip(*np.unique(DOW[S[gap]], return_counts=True)))} (0=Mon)")

def run_fillopen(mult, cost=COST):
    out=[]
    for i in range(len(S)):
        s, ua, da = S[i], PDH[i], PDL[i]; risk = ua-da; end=min(s+H, N-1); trig=None
        for j in range(s+1, end+1):
            up=Hi[j]>=ua; dn=Lo[j]<=da
            if up and dn: trig="skip"; break
            if up: trig=(j,+1,max(ua,O[j])); break         # gap -> fill at open
            if dn: trig=(j,-1,min(da,O[j])); break
        if trig is None or trig=="skip": continue
        j,dr,entry=trig; stop = da if dr>0 else ua; tgt = entry + dr*mult*risk
        res=None
        for k in range(j,end+1):
            ht=(Hi[k]>=tgt) if dr>0 else (Lo[k]<=tgt); hs=(Lo[k]<=stop) if dr>0 else (Hi[k]>=stop)
            if ht and hs: res=-abs(entry-stop)/risk; break
            if hs: res=-abs(entry-stop)/risk; break
            if ht: res=float(mult); break
        if res is None: res=dr*(Cl[end]-entry)/risk
        out.append(dict(status="traded", net=res-cost/risk, gross=res, i=i, risk=risk, side=dr))
    return out

fo = stats(run_fillopen(2.0), "2R fill-at-open", quiet=True)
print(f"     EXPECTANCY_WITH_WORST_CASE_ORDERING (gap fills at the open): {fo['net'].mean():+.4f} R "
      f"(base {net.mean():+.4f})  delta {fo['net'].mean()-net.mean():+.4f}")
noamb = net[~inmask]
print(f"     EXPECTANCY_WITH_AMBIGUOUS_EPISODES_REMOVED (gap-fill episodes dropped): {noamb.mean():+.4f} R (n={len(noamb)})")
print(f"     AMBIGUOUS_EPISODES = {amb} same-bar-both (already skipped) + {len(gap)} gap-through fills = {amb+len(gap)}")

# --- episode overlap
sp = np.diff(np.sort(S))
ov = (sp < H).sum()
print(f"\n  EPISODE INDEPENDENCE: consecutive daily anchors closer than {H} bars: {ov} of {len(S)-1} ({ov/(len(S)-1):.1%})")
print(f"     -> the 96-bar window from a Friday anchor reaches into Monday. Episodes are NOT fully")
print(f"        non-overlapping; week-clustered inference is used below rather than iid.")

print("\n"+"="*122); print("  §4  IS EXPECTANCY ACTUALLY > 0?  (episode-level inference)"); print("="*122)
wk = (pd.to_datetime(tsE, unit='s', utc=True).isocalendar().year*100 +
      pd.to_datetime(tsE, unit='s', utc=True).isocalendar().week).to_numpy()
def cl_mean(y, cl):
    mu=y.mean(); n=len(y)
    g=pd.DataFrame({'c':cl,'y':y}).groupby('c')['y'].agg(['sum','count'])
    G=len(g); resid=g['sum'].to_numpy()-g['count'].to_numpy()*mu
    se=math.sqrt((resid**2).sum()/n**2*(G/(G-1)))
    return mu, se, G
for m in (1.0,1.5,2.0):
    y = stats(run(m), "", quiet=True)["net"]
    mu_i, se_i = y.mean(), y.std(ddof=1)/math.sqrt(len(y))
    mu_c, se_c, G = cl_mean(y, wk)
    print(f"  {m}R  mean {mu_c:+.4f}   iid se {se_i:.4f} (t {mu_i/se_i:+.2f})   "
          f"WEEK-CLUSTERED se {se_c:.4f} (t {mu_c/se_c:+.2f}, G={G})   CI95 [{mu_c-1.96*se_c:+.4f}, {mu_c+1.96*se_c:+.4f}]")
bs=[]
rng=np.random.default_rng(11); uw=np.unique(wk)
y2 = net
for _ in range(4000):
    pick=rng.choice(uw, len(uw), replace=True)
    v=np.concatenate([y2[wk==w] for w in pick]); bs.append(v.mean())
bs=np.array(bs)
print(f"  2R block bootstrap (4000 resamples of WEEKS): mean {bs.mean():+.4f}  "
      f"CI95 [{np.quantile(bs,.025):+.4f}, {np.quantile(bs,.975):+.4f}]  P(mean<=0) = {np.mean(bs<=0):.3f}")

print("\n"+"="*122); print("  §5  TAIL DEPENDENCE -- DECISIVE"); print("="*122)
srt=np.sort(net)[::-1]; tot=net.sum()
print(f"  net-R distribution: min {net.min():+.3f}  max {net.max():+.3f}  (wins are CAPPED at the {2.0}R target)")
print(f"  share of TOTAL PnL from the best k%:")
for p in (0.5,1,2,5,10):
    k=max(1,int(len(net)*p/100)); print(f"    top {p:4.1f}% ({k:3d} trades): {100*srt[:k].sum()/tot:6.1f}%")
print(f"  expectancy after REMOVING the best k%:")
for p in (1,2,3,5):
    k=int(len(net)*(1-p/100)); print(f"    drop-best-{p}% : {np.sort(net)[:k].mean():+.4f} R")
print(f"  winsorized at the 95th/5th pct: {np.clip(net, np.quantile(net,.05), np.quantile(net,.95)).mean():+.4f} R")
print(f"  median net-R: {np.median(net):+.4f}   trimmed(10%) mean: {np.sort(net)[int(.05*len(net)):int(.95*len(net))].mean():+.4f}")

print("\n  ** IS drop-best-5% A VALID TAIL DIAGNOSTIC FOR A CAPPED-PAYOFF STRATEGY? **")
print("  Simulation: a strategy with a KNOWN, GENUINE, BROAD +0.054R edge and this exact bounded payoff")
print("  (win = +2R capped, loss = -1R, WR set to reproduce the edge). No fat tail exists by construction.")
p_win = (0.054 + 1 + 0.026) / 3.0
sims=[]
for s_ in range(400):
    rg=np.random.default_rng(500+s_)
    w=rg.random(len(net))<p_win
    y=np.where(w, 2.0, -1.0) - 0.026
    k=int(len(y)*0.95); sims.append(np.sort(y)[:k].mean())
sims=np.array(sims)
print(f"    true edge by construction: {(np.where(np.random.default_rng(1).random(200000)<p_win,2.0,-1.0)-0.026).mean():+.4f} R")
print(f"    its drop-best-5% : mean {sims.mean():+.4f}  (negative in {100*np.mean(sims<0):.0f}% of 400 simulations)")
print(f"    -> a strategy with NO tail dependence whatsoever ALSO fails drop-best-5%.")
print(f"       Removing 5% of trades from a payoff capped at +2R removes ~5% x 2R = 0.10R per trade,")
print(f"       roughly TWICE the entire edge. The diagnostic is mechanically guaranteed to fail here.")

print("\n"+"="*122); print("  §6  LOSERS / WHIPSAW STRUCTURE"); print("="*122)
both=0; opp_after=0; t_opp=[]
for r in tr:
    i=r["i"]; s=S[i]; end=min(s+H,N-1); j=r["trig_bar"]; dr=r["side"]
    other = PDL[i] if dr>0 else PDH[i]
    hit=None
    for k in range(j, end+1):
        if (dr>0 and Lo[k]<=other) or (dr<0 and Hi[k]>=other): hit=k; break
    if hit is not None: opp_after+=1; t_opp.append((hit-j)*0.25)
print(f"  first-side-only (opposite extreme never reached after entry) : {1-opp_after/len(tr):.3f}")
print(f"  opposite-side-after-trigger (i.e. stopped out)               : {opp_after/len(tr):.3f}")
print(f"  median hours from entry to the opposite extreme, when reached: {np.median(t_opp):.2f} h")
btt=np.array([r["bars_to_trig"] for r in tr])*0.25
print(f"  median hours from anchor to first activation                 : {np.median(btt):.2f} h")
mtm=np.array([r["mtm"] for r in tr]).astype(bool)
print(f"  unresolved at the 24h expiry (marked to market)              : {mtm.mean():.3f}  mean net there {net[mtm].mean():+.4f}")
print(f"  resolved by target                                           : {np.mean(np.array([r['gross'] for r in tr])==2.0):.3f}")
print(f"  resolved by stop                                             : {np.mean(np.array([r['gross'] for r in tr])==-1.0):.3f}")
cost_R = COST/rk
print(f"  cost drag: mean {cost_R.mean():.4f} R/trade  (median {np.median(cost_R):.4f}) vs net edge {net.mean():+.4f} R")
print(f"  gross expectancy {ST['gross'].mean():+.4f} R -> cost eats {100*cost_R.mean()/ST['gross'].mean():.0f}% of it")

print("\n"+"="*122); print("  §8  TEMPORAL STABILITY"); print("="*122)
print(f"  {'block':<14}{'N':>6}{'net':>9}{'WR':>8}{'PF':>8}{'top1%PnL':>10}{'week-clust t':>14}")
for a,b in ((2011,2014),(2014,2017),(2017,2020),(2020,2023),(2023,2027)):
    m=(yE>=a)&(yE<b); y=net[m]
    if len(y)<50: continue
    w=y>0; pf=y[w].sum()/abs(y[~w].sum()); t1=np.sort(y)[-max(1,len(y)//100):].sum()/y.sum()
    mu,se,_=cl_mean(y, wk[m])
    print(f"  {a}-{b-1:<9}{len(y):>6}{y.mean():>+9.4f}{w.mean():>8.3f}{pf:>8.3f}{t1:>10.2f}{mu/se:>+14.2f}")

print("\n"+"="*122); print("  §9  MATCHED CONTROLS -- same episodes, same levels, same risk, direction NOT market-selected")
print("="*122)
def forced(side_fn, label, mult=2.0, seed=7):
    rg=np.random.default_rng(seed); out=[]
    for pos,i in enumerate(ii):
        s=S[i]; ua,da=PDH[i],PDL[i]; risk=ua-da; end=min(s+H,N-1)
        dr=side_fn(rg,i)
        entry = ua if dr>0 else da
        stop  = da if dr>0 else ua
        tgt   = entry + dr*mult*risk
        # enter at the SAME trigger time as the market-selected trade, on the chosen side's level
        j=None
        for k in range(s+1,end+1):
            if (dr>0 and Hi[k]>=ua) or (dr<0 and Lo[k]<=da): j=k; break
        if j is None: continue
        res=None
        for k in range(j,end+1):
            ht=(Hi[k]>=tgt) if dr>0 else (Lo[k]<=tgt); hs=(Lo[k]<=stop) if dr>0 else (Hi[k]>=stop)
            if ht and hs: res=-1.0; break
            if hs: res=-1.0; break
            if ht: res=float(mult); break
        if res is None: res=dr*(Cl[end]-entry)/risk
        out.append(res-COST/risk)
    y=np.array(out)
    print(f"  {label:34s} N={len(y):5d}  net={y.mean():+.4f}  WR={(y>0).mean():.3f}")
    return y
mk = forced(lambda rg,i: 1 if rg.random()<0.5 else -1, "random direction (matched)")
al = forced(lambda rg,i: 1, "always LONG at prior-day high")
ash= forced(lambda rg,i: -1, "always SHORT at prior-day low")
print(f"  market-selected (the candidate)     N={len(net):5d}  net={net.mean():+.4f}  WR={(net>0).mean():.3f}")
diff = net.mean()-mk.mean()
mu_d, se_d, _ = cl_mean(net, wk)
print(f"\n  MARKET_SELECTION_INCREMENTAL_VALUE = {diff:+.4f} R over matched random direction")
bs2=[]
for _ in range(4000):
    pick=rng.choice(uw,len(uw),replace=True)
    a_=np.concatenate([net[wk==w] for w in pick])
    bs2.append(a_.mean())
print(f"  (candidate CI95 [{np.quantile(bs2,.025):+.4f},{np.quantile(bs2,.975):+.4f}]; random control mean {mk.mean():+.4f})")

print("\n"+"="*122); print("  §10  COST ROBUSTNESS"); print("="*122)
for lbl,cst in (("BASE  0.419",0.419),("STRESS 0.838 (2x)",0.838)):
    y=stats(run(2.0,cost=cst),"",quiet=True)["net"]
    print(f"  {lbl:22s} net 2R = {y.mean():+.4f} R")
g2 = ST["gross"].mean()
be = g2/np.mean(1.0/rk)
print(f"  gross 2R expectancy {g2:+.4f} R.  Break-even cost solves mean(gross) = cost*mean(1/risk):")
print(f"    BREAK_EVEN_COST = {be:.3f} price units/trade  ({be/0.419:.2f}x BASE, {be/0.838:.2f}x STRESS)")
print(f"    additional adverse execution that erases the edge: {be-0.419:.3f} price units = {(be-0.419)/0.10:.1f} pips/trade")

print("\n"+"="*122); print("  §11  ECONOMIC SIGNIFICANCE"); print("="*122)
yrs=np.unique(yE); ann=[]
print(f"  {'year':<7}{'trades':>8}{'net R':>10}{'WR':>8}")
for y_ in yrs:
    m=yE==y_; ann.append(net[m].sum())
    print(f"  {y_:<7}{m.sum():>8}{net[m].sum():>+10.2f}{(net[m]>0).mean():>8.3f}")
ann=np.array(ann)
print(f"\n  trades/year (full years)      : {np.mean([ (yE==y_).sum() for y_ in yrs[1:-1]]):.0f}")
print(f"  net R/year  median            : {np.median(ann[1:-1]):+.2f}   mean {ann[1:-1].mean():+.2f}")
print(f"  worst year {ann.min():+.2f}   best year {ann.max():+.2f}   negative years {int((ann<0).sum())}/{len(ann)}")
eq=np.cumsum(net); dd=np.maximum.accumulate(eq)-eq
print(f"  max drawdown in R             : {dd.max():.2f} R   (total profit {eq[-1]:+.2f} R over {len(net)} trades)")
ls=0; mx=0
for v in net:
    ls = ls+1 if v<0 else 0; mx=max(mx,ls)
print(f"  longest losing sequence       : {mx} consecutive losing trades")
print(f"  MaxDD / annual R              : {dd.max()/max(np.median(ann[1:-1]),1e-9):.1f}x  <- years of median profit to recover a max drawdown")
print(f"\n  ** WHAT IS 1R HERE? ** median risk {np.median(rk):.1f} USD = {np.median(rk)/0.10:.0f} pips.")
print(f"     +0.054R per trade = {0.054*np.median(rk)/0.10:.1f} pips per trade at the median risk unit.")
print(f"     Alpha's cost of 0.419 USD = 4.2 pips. Edge/cost ratio = {0.054*np.median(rk)/0.419:.2f}x")

print("\n"+"="*122); print("  GOVERNANCE: RESEARCH HOLDOUT"); print("="*122)
inho = tsE >= HOLDOUT.timestamp()
print(f"  RESEARCH_HOLDOUT_CUTOFF_UTC = {HOLDOUT}  (edge_research/_common.py:43)")
print(f"  Alpha's loader (cur_data.load_m15) applies NO truncation -> data runs to {d.dt.max()}")
print(f"  episodes inside the protected holdout : {int(inho.sum())} of {len(net)} ({inho.mean():.2%})")
print(f"  expectancy on holdout episodes        : {net[inho].mean():+.4f} R" if inho.sum() else "")
print(f"  expectancy EXCLUDING the holdout      : {net[~inho].mean():+.4f} R  (n={int((~inho).sum())})")
