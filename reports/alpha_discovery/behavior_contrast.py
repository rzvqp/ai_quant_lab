"""behavior_contrast.py — ALPHA_DISCOVERY_FACTORY_V2: GOLD_BEHAVIOR_ATLAS + CONTRAST_MINER (the central engine).
Detect a well-populated structural EVENT family (break of a prior-20-bar swing extreme = STRUCTURAL_BREAK), label the outcome
(WINNER = reach +2R before −1R with a structural stop, direction=break), and mine EX-ANTE discriminators (measured with bars<=break,
NO outcome as input): break_depth, break_velocity, prior_test_count(level freshness), htf_align(H1/H4 nested-EMA), session(DST-correct),
location(premium/discount), vol_state, and TARGET_SPACE (room to the 100-bar extreme beyond / to PDH-PDL). For each discriminator report
win-rate + NET-R (STRESS 0.24) by bin, cross-era D/C/O. Goal: find a context where the SAME break becomes ASYMMETRIC (a real ex-ante
discriminator), not a description of winners. cur_data M15 UTC. No mining (fixed feature set, reported for all bins)."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import cur_data as CD
import session_tz as STZ
COST=0.24; H=48
def main():
    m=CD.load_m15(); o=m["open"].to_numpy(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy()
    atr=m["atr"].to_numpy(); atr_ma=m["atr_ma"].to_numpy(); n=len(m); yr=m["dt"].dt.year.to_numpy(); hr=m["dt"].dt.hour.to_numpy()
    e20=m["ema20"].to_numpy(); e50=m["ema50"].to_numpy(); e200=pd.Series(c).ewm(span=200,adjust=False).mean().to_numpy()
    p20H=pd.Series(h).rolling(20).max().shift(1).to_numpy(); p20L=pd.Series(l).rolling(20).min().shift(1).to_numpy()
    hi100=pd.Series(h).rolling(100).max().shift(1).to_numpy(); lo100=pd.Series(l).rolling(100).min().shift(1).to_numpy()
    body=np.abs(c-o)
    def sess(i):
        H_=hr[i]; return "AS" if H_<8 else ("LN" if H_<13 else ("NY" if H_<20 else "AS"))
    def era(i): return "D" if yr[i]<=2018 else ("C" if yr[i]<=2022 else "O")
    # structural break events (fresh break of prior-20 extreme), deduped
    rows=[]; last=-10**9
    for T in range(120, n-H-2):
        if not np.isfinite(atr[T]) or atr[T]<=0 or not np.isfinite(p20H[T]) or not np.isfinite(hi100[T]): continue
        up=c[T]>p20H[T]; dn=c[T]<p20L[T]
        if not(up or dn) or T-last<6: continue
        dirn=1 if up else -1; lvl=p20H[T] if up else p20L[T]; a=atr[T]
        # OUTCOME (label only): 2R before 1R, stop=opposite side of the break structure (prior-20 opposite extreme)
        stop=(p20L[T]-0.1*a) if dirn>0 else (p20H[T]+0.1*a); risk=abs(c[T]-stop)
        if risk<=0.1*a: last=T; continue
        ei=T+1; entry=o[ei] if ei<n else c[T]; tgt=entry+2*risk*dirn
        segl=l[ei:ei+H]; segh=h[ei:ei+H]
        if dirn>0: fs=np.where(segl<=stop)[0]; ft=np.where(segh>=tgt)[0]
        else: fs=np.where(segh>=stop)[0]; ft=np.where(segl<=tgt)[0]
        fstop=fs[0] if len(fs) else 10**9; ftgt=ft[0] if len(ft) else 10**9
        if fstop==ftgt==10**9: last=T; continue
        R=2.0 if ftgt<fstop else -1.0
        # EX-ANTE features (bars<=T only)
        depth=(c[T]-lvl)*dirn/a                                   # how far close is beyond the level
        vel=body[T]/a                                            # break bar impulse
        htf=1 if ((dirn>0 and e20[T]>e50[T] and c[T]>e200[T]) or (dirn<0 and e20[T]<e50[T] and c[T]<e200[T])) else 0  # HTF align
        loc=(c[T]-lo100[T])/(hi100[T]-lo100[T]) if hi100[T]>lo100[T] else 0.5
        vol=a/atr_ma[T] if atr_ma[T]>0 else 1.0
        # target space: room to the 100-bar extreme in the break direction (price-discovery if ~0 room beyond)
        tspace=((hi100[T]-c[T]) if dirn>0 else (c[T]-lo100[T]))/a
        # prior test count: times the level zone was touched in the prior 20 bars (freshness)
        zone_lo=lvl-0.15*a; zone_hi=lvl+0.15*a
        tests=int(np.sum((h[T-20:T]>=zone_lo)&(l[T-20:T]<=zone_hi)))
        rows.append(dict(era=era(T),sess=sess(T),dirn=dirn,R=R,depth=depth,vel=vel,htf=htf,loc=loc,vol=vol,tspace=tspace,tests=tests))
    df=pd.DataFrame(rows); N=len(df)
    base=np.mean(df['R']-COST)
    print(f"CONTRAST MINER — STRUCTURAL_BREAK family: N={N} events. BASE netR={base:+.3f} winrate={np.mean(df['R']>0):.3f} (2R:1R null 0.333)")
    print("  (a break that just fails to net after costs = the known result; seek an EX-ANTE bin that is materially + cross-era)")
    def contrast(name, series, bins, labels):
        print(f"\n  discriminator: {name}")
        for lab,(lo,hi) in zip(labels,bins):
            d=df[(series>=lo)&(series<hi)]
            if len(d)<150: print(f"    {lab:16s}: n={len(d)} thin"); continue
            net=np.mean(d['R']-COST); wr=np.mean(d['R']>0)
            eras=" ".join(f"{e}={np.mean(d[d.era==e]['R']-COST):+.2f}" for e in ["D","C","O"])
            print(f"    {lab:16s}: n={len(d):4d} netR={net:+.3f} WR={wr:.3f} | era {eras}")
    contrast("TARGET_SPACE (room to 100b extreme, ATR)", df['tspace'], [(0,1),(1,3),(3,6),(6,100)], ["<1(discovery)","1-3","3-6",">6(room)"])
    contrast("PRIOR_TEST_COUNT (level freshness)", df['tests'], [(0,1),(1,3),(3,6),(6,100)], ["0(fresh)","1-2","3-5",">=6(stale)"])
    contrast("BREAK_VELOCITY (break bar body/ATR)", df['vel'], [(0,0.5),(0.5,1),(1,1.5),(1.5,100)], ["<0.5(creep)","0.5-1","1-1.5",">1.5(impulse)"])
    contrast("BREAK_DEPTH (close beyond level, ATR)", df['depth'], [(0,0.2),(0.2,0.5),(0.5,1),(1,100)], ["<0.2","0.2-0.5","0.5-1",">1"])
    contrast("LOCATION (premium/discount)", df['loc'], [(0,0.34),(0.34,0.66),(0.66,1.01)], ["discount","mid","premium"])
    print("\n  HTF_ALIGN: "+" ".join(f"align={a}:netR={np.mean(df[df.htf==a]['R']-COST):+.3f}(n{len(df[df.htf==a])})" for a in [0,1]))
    print("  SESSION: "+" ".join(f"{s}:netR={np.mean(df[df.sess==s]['R']-COST):+.3f}(n{len(df[df.sess==s])})" for s in ["AS","LN","NY"]))
    print("  DIRECTION: "+" ".join(f"{'UP' if d>0 else 'DN'}:netR={np.mean(df[df.dirn==d]['R']-COST):+.3f}(n{len(df[df.dirn==d])})" for d in [1,-1]))
    # 2-way: best single discriminator x direction, cross-era (guarded, small)
    df.to_json(r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery\contrast_events.jsonl",orient="records",lines=True)
    print(f"\nwrote contrast_events.jsonl (N={N}). A bin with netR materially >0 AND cross-era-stable = ex-ante discriminator candidate.")
if __name__=="__main__": main()
