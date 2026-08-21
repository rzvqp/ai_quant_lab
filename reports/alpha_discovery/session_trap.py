"""ALPHA-XAUUSD-SESSION-LIQUIDITY-TRAP-SHORT-001. Asia-High liquidity-trap SHORT: Asia range -> sweep of
Asia High during London/NY -> failed breakout -> return into range -> bearish continuation. Session+time-of-day
+range-location+post-sweep-path conditioning (NEW vs generic swing-sweep). DST-correct sessions (Asia=fixed UTC,
Tokyo no DST; London/NY via tz_convert). Raw-signal-first, S0-S5 common-parent, disc/conf split, matched controls,
mean-reversion vs trend separated. M15 primary. Price-only, DEV-only. NO 2025+/CALIB/V1/N4/read_csv/exogenous."""
import sys, os, numpy as np, pandas as pd
SP=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,SP)
import m5_data as D
PIP=0.10
tfs,META=D.build()
M=tfs["M15"]
o=M["open"].to_numpy();h=M["high"].to_numpy();l=M["low"].to_numpy();c=M["close"].to_numpy()
atr=M["atr"].to_numpy(); dev=M["is_dev"].to_numpy()
dt=pd.to_datetime(M["time"].to_numpy(),unit="s",utc=True)
uh=dt.hour.to_numpy(); uday=dt.floor("D").astype("int64").to_numpy()   # utc calendar day key
lon_h=dt.tz_convert("Europe/London").hour.to_numpy()                    # DST-correct
ny_h=dt.tz_convert("America/New_York").hour.to_numpy()                  # DST-correct
n=len(o)
# ---- FROZEN SESSION DEFINITIONS (audited before testing) ----
# ASIA   = 00:00-07:00 UTC (Tokyo 09:00-16:00 JST; Japan has NO DST -> fixed UTC, DST-safe)
# LONDON = 08:00-16:00 Europe/London local (DST via tz)
# NEWYORK= 08:00-17:00 America/New_York local (DST via tz)
asia_win=(uh>=0)&(uh<7)
london=(lon_h>=8)&(lon_h<16)
newyork=(ny_h>=8)&(ny_h<17)
overlap=london&newyork
post_asia=(uh>=7)
print("=== SESSION/DST AUDIT ===")
print(f"M15 bars={n} DEV={dev.sum()} | Asia-win bars={asia_win.sum()} London={london.sum()} NY={newyork.sum()} overlap={overlap.sum()}")
# sanity: London DST offset varies, NY too; Asia fixed UTC
print(f"  London local-hour range at UTC07: {sorted(set(lon_h[(uh==7)]))[:3]}... (varies 7/8 by DST) ; NY offset varies -4/-5")

# ---- per-day Asia range (causal; complete at 07:00 UTC) ----
days=np.unique(uday)
asia={}  # day -> (hi,lo,mid,width_pips,nbars)
for d in days:
    m=(uday==d)&asia_win&np.isfinite(atr)
    if m.sum()<12: continue
    hi=h[m].max(); lo=l[m].min(); asia[d]=(hi,lo,(hi+lo)/2,(hi-lo)/PIP,int(m.sum()))
print(f"accepted Asia-range days={len(asia)} (>=12 M15 Asia bars) of {len(days)}")

def bear_disp(i): return i>0 and np.isfinite(atr[i]) and (o[i]-c[i])>1.0*atr[i] and c[i]<o[i]

# ---- sweep detection + S0..S5 sequence per day (parent = FIRST Asia-High sweep in London or NY) ----
recs=[]
di=np.where(post_asia)[0]
for d in days:
    if d not in asia: continue
    hi,lo,mid,wpip,_=asia[d]
    day_idx=np.where((uday==d)&post_asia&np.isfinite(atr))[0]
    if len(day_idx)<4: continue
    # find first sweep (high>asia_hi) in London or NY
    swept=None
    for i in day_idx:
        if h[i]>hi and (london[i] or newyork[i]):
            swept=i; break
    if swept is None: continue
    sess="OVERLAP" if overlap[swept] else ("LONDON" if london[swept] else "NY")
    # sweep excursion: max high until first close back inside range
    j=swept; sweep_hi=h[swept]; ret=None; closes_above=0; bars_above=0
    end=day_idx[day_idx>=swept]
    for k in end:
        if h[k]>sweep_hi: sweep_hi=h[k]
        if c[k]>hi: closes_above+=1
        if h[k]>hi: bars_above+=1
        if c[k]<hi and k>swept: ret=k; break            # S1 return inside range
        if k-swept>8: break
    dist_above=(sweep_hi-hi)/PIP
    # sequence events after return
    s2=s3=s4=s5=None
    if ret is not None:
        seg=[k for k in end if k>=ret and k-ret<=10]
        for k in seg:
            if s2 is None and bear_disp(k): s2=k
            if s3 is None and h[k]>=hi and c[k]<hi and k>ret: s3=k          # failed reclaim of Asia High
            if s4 is None and k>=ret+1 and c[k]<min(l[max(ret-5,0):k]) and c[k]<o[k]: s4=k  # structure break
        if s3 is not None:
            for k in seg:
                if k>s3 and bear_disp(k): s5=k; break
    recs.append(dict(d=d,sw=swept,sess=sess,hi=hi,lo=lo,mid=mid,wpip=wpip,sweep_hi=sweep_hi,dist=dist_above,
                     ret=ret,s2=s2,s3=s3,s4=s4,s5=s5,closes_above=closes_above,bars_above=bars_above,
                     t_utc=int(uh[swept]),t_lon=int(lon_h[swept]),dev=bool(dev[swept])))
recs=[r for r in recs if r["dev"]]
print(f"\n=== RAW ASIA-HIGH SWEEP CATALOG (DEV) ===")
print(f"parent sweeps={len(recs)} | LONDON={sum(r['sess']=='LONDON' for r in recs)} NY={sum(r['sess']=='NY' for r in recs)} OVERLAP={sum(r['sess']=='OVERLAP' for r in recs)}")
print(f"  returned inside range (S1)={sum(r['ret'] is not None for r in recs)} | median dist above={np.median([r['dist'] for r in recs]):.1f}p | median Asia width={np.median([r['wpip'] for r in recs]):.1f}p")

# ---- forward outcome from a short entry (stop=sweep_hi+buffer; targets Asia mid / Asia low) ----
def outcome(r, entry_i):
    if entry_i is None or entry_i+1>=n: return None
    e=o[entry_i+1]; stop=r["sweep_hi"]+0.1*(atr[entry_i] if np.isfinite(atr[entry_i]) else 1.0)
    risk=(stop-e)/PIP
    if risk<=2: return None
    endday=np.where((uday==r["d"])&(uh<21)&np.isfinite(atr))[0]; endday=endday[endday>entry_i]
    hor=[k for k in range(entry_i+1,min(entry_i+1+24,n))]
    hit_mid=hit_low=stopped=None; mae=0; mfe=0
    for k in hor:
        mae=max(mae,(h[k]-e)/PIP); mfe=max(mfe,(e-l[k])/PIP)
        if h[k]>=stop: stopped=k; break
        if hit_mid is None and l[k]<=r["mid"]: hit_mid=k
        if hit_low is None and l[k]<=r["lo"]: hit_low=k
        if hit_low is not None: break
    return dict(e=e,stop=stop,risk=risk,hit_mid=hit_mid is not None,hit_low=hit_low is not None,
                stopped=stopped is not None,mae=mae,mfe=mfe,
                R_mid=((e-r["mid"])/PIP)/risk if hit_mid is not None else (-1.0 if stopped is not None else ((e-c[hor[-1]])/PIP)/risk),
                R_low=(((e-r["lo"])/PIP)/risk) if hit_low is not None else (-1.0 if stopped is not None else ((e-c[hor[-1]])/PIP)/risk))

# entry index per layer (raw-signal-first): S1 entry after return; S2 after bear disp; S3 after failed reclaim; S4 after break; S5 after 2nd impulse
def layer_entry(r,layer): return {"S1":r["ret"],"S2":r["s2"],"S3":r["s3"],"S4":r["s4"],"S5":r["s5"]}[layer]

# discovery/confirmation split by day (chronological)
dd=sorted(set(r["d"] for r in recs)); cutday=dd[int(len(dd)*0.6)]
def split(r): return "D" if r["d"]<cutday else "C"
print(f"\n=== DISCOVERY/CONFIRMATION (cut {pd.to_datetime(cutday,unit='ns',utc=True).date()}) ===")
print(f"DISC sweeps={sum(split(r)=='D' for r in recs)} CONF sweeps={sum(split(r)=='C' for r in recs)}")

# ---- S0..S5 common-parent attribution: P(reach Asia mid) and P(reach Asia low) ----
def layer_stats(layer, sess=None, split_tag=None):
    rr=[r for r in recs if (sess is None or r["sess"]==sess) and (split_tag is None or split(r)==split_tag)]
    if layer=="S0": ents=[(r,r["sw"]) for r in rr]
    else: ents=[(r,layer_entry(r,layer)) for r in rr if layer_entry(r,layer) is not None]
    outs=[(r,outcome(r,ei)) for r,ei in ents]; outs=[(r,ov) for r,ov in outs if ov is not None]
    if not outs: return (0,np.nan,np.nan)
    pmid=np.mean([ov["hit_mid"] for _,ov in outs]); plow=np.mean([ov["hit_low"] for _,ov in outs])
    return (len(outs),pmid,plow)

print("\n=== S0->S5 COMMON-PARENT ATTRIBUTION: P(reach Asia MID) | P(reach Asia LOW) ===")
print(f"{'layer':6} {'DISC n':>7} {'P(mid)':>7} {'P(low)':>7} | {'CONF n':>7} {'P(mid)':>7} {'P(low)':>7}")
for layer in ("S0","S1","S2","S3","S4","S5"):
    nd,pmd,pld=layer_stats(layer,None,"D"); nc,pmc,plc=layer_stats(layer,None,"C")
    print(f"{layer:6} {nd:7d} {pmd:7.3f} {pld:7.3f} | {nc:7d} {pmc:7.3f} {plc:7.3f}")

print("\n=== SESSION SPLIT (S1 base tradeable): P(mid)|P(low) DISC||CONF ===")
for sess in ("LONDON","NY","OVERLAP"):
    nd,pmd,pld=layer_stats("S1",sess,"D"); nc,pmc,plc=layer_stats("S1",sess,"C")
    print(f"  {sess:8}: DISC n{nd} mid{pmd:.3f} low{pld:.3f} | CONF n{nc} mid{pmc:.3f} low{plc:.3f}")
