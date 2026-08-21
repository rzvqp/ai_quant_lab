"""Phase 2: SE-aware strict directional gate on curated hierarchies + BOUNDED automated cross-TF scan
+ EXECUTION test (S17 gate -> S20/S21/S23) on the strongest directional hierarchies. Reuses nested_mtf_short
build. Completed-bar causal, DEV-only."""
import sys, os, numpy as np, pandas as pd
SP=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,SP)
import nested_mtf_short as N   # reuse all built arrays (import runs phase 1)
M15,H1,H4=N.M15,N.H1,N.H4; H1E,M15E,H4C=N.H1E,N.M15E,N.H4C; LAB=N.LAB
idx_h1,idx_h4=N.idx_h1,N.idx_h4; disc,conf=N.disc,N.conf; BASE_D,BASE_C=N.BASE_D,N.BASE_C; PIP=N.PIP
h1_recent=N.h1_recent
discS=set(disc.tolist()); confS=set(conf.tolist())

def full_mask(h4c,h1e,m15e,W=6):
    return (H4C[h4c][idx_h4] & (idx_h4>=0) & (idx_h1>=0) & h1_recent(h1e,W) & M15E[m15e])

def lift_split(mask):
    idx=np.where(mask)[0]
    d=[i for i in idx if i in discS]; c=[i for i in idx if i in confS]
    rd=np.mean([LAB[i] for i in d]) if d else np.nan; rc=np.mean([LAB[i] for i in c]) if c else np.nan
    sd=np.sqrt(BASE_D*(1-BASE_D)/len(d)) if d else np.nan; sc=np.sqrt(BASE_C*(1-BASE_C)/len(c)) if c else np.nan
    return (len(d),rd-BASE_D,sd,len(c),rc-BASE_C,sc)

# ---------- BOUNDED automated cross-TF scan (strict, SE-aware) ----------
CTX=["BULLISH_STATE","UPPER_RANGE","SWINGHIGH_INTERACT","OVEREXT_UP","FAILED_CONT","TRANSITION"]
H1EV=["FAILED_HH","BEAR_DISP","STRUCT_BREAK","FAILED_BULL_CONT","CLOSE_BELOW_LEVEL","HIGH_SWEEP","SECOND_BEAR","FAILED_RECLAIM"]
M15EV=["FAILED_RECLAIM","LOWER_HIGH","BEAR_DISP","MICRO_BREAKDOWN","SECOND_BEAR","COMPR_EXP_DOWN","BREAK_RETEST","FAILED_BULL_IMP"]
print(f"\n=== BOUNDED AUTOMATED CROSS-TF SCAN: {len(CTX)}x{len(H1EV)}x{len(M15EV)}={len(CTX)*len(H1EV)*len(M15EV)} hierarchies ===")
print("strict gate: nfD>=20 & nfC>=20 & DISC lift> +1SE & CONF lift> +1SE (both meaningfully bearish-predictive)")
survivors=[]; tested=0
for hc in CTX:
    for he in H1EV:
        for me in M15EV:
            tested+=1
            nd,ld,sd,nc,lc,sc=lift_split(full_mask(hc,he,me))
            if nd>=20 and nc>=20 and ld>sd and lc>sc:
                survivors.append((hc,he,me,nd,ld,sd,nc,lc,sc))
print(f"tested={tested}  survivors(strict, both splits > +1SE)={len(survivors)}")
for s in survivors:
    hc,he,me,nd,ld,sd,nc,lc,sc=s
    print(f"   {hc}->{he}->{me}: DISC n{nd} lift{ld:+.3f}(SE{sd:.3f}) | CONF n{nc} lift{lc:+.3f}(SE{sc:.3f})")
# how many would we expect by chance at a ~16% one-sided rate on both independent splits? ~ tested*0.16*0.16
print(f"   [expected false-positives by chance ~= {tested*0.16*0.16:.1f}]")

# ---------- EXECUTION test (S20/S21/S23) on the strongest directional hierarchies ----------
h1_sh=H1["sh"]; h1_h=H1["h"]; m15_o=M15["o"]; m15_h=M15["h"]; m15_l=M15["l"]; m15_c=M15["c"]; m15_atr=M15["atr"]
h1_atr=H1["atr"]; dev=M15["dev"]; n=M15["n"]; COST=2.4  # STRESS RT in project pips (0.24 price /0.10)
def h1_stop(i, entry):
    """H1 structural invalidation: highest completed H1 swing high above entry within last 8 H1 bars; else entry+1.5*H1atr."""
    k=idx_h1[i]
    if k<0: return entry+1.5*(h1_atr[k] if k>=0 and h1_atr[k]==h1_atr[k] else m15_atr[i]*3)
    hi=[h1_h[j] for j in range(max(0,k-7),k+1) if h1_sh[j] and h1_h[j]>entry]
    if hi: return max(hi)
    a=h1_atr[k] if h1_atr[k]==h1_atr[k] else m15_atr[i]*3
    return entry+1.5*a
def execute(mask, rr):
    idx=np.where(mask)[0]; Rs=[]; yrs=[]; cool=-1
    for i in idx:
        if i<=cool or not dev[i] or i+1>=n: continue
        entry=m15_o[i+1]; stop=h1_stop(i,entry); risk=(stop-entry)/PIP
        if risk<=2: continue
        tgt=entry-rr*risk*PIP; R=None; exitb=i+1
        for j in range(i+1, min(i+1+N.H_M15, n)):
            exitb=j
            if m15_h[j]>=stop: R=-1.0; break
            if m15_l[j]<=tgt: R=+rr; break
        if R is None: R=((entry-m15_c[exitb])/PIP)/risk
        R=R-COST/risk
        Rs.append(R); yrs.append(pd.to_datetime(M15["ot"][i],unit="s",utc=True).year); cool=exitb
    Rs=np.array(Rs)
    if len(Rs)==0: return None
    srt=np.sort(Rs)[::-1]
    def brem(p): k=int(len(Rs)*p); return srt[k:].mean() if k<len(Rs) else np.nan
    top10=srt[:max(1,int(len(Rs)*0.1))].sum(); tot=Rs.sum()
    yy={y:round(float(Rs[np.array(yrs)==y].mean()),3) for y in sorted(set(yrs))}
    return dict(n=len(Rs),wr=round(float((Rs>0).mean()),3),avg=round(float(Rs.mean()),3),
                med=round(float(np.median(Rs)),3),b5=round(float(brem(0.05)),3),b10=round(float(brem(0.10)),3),
                top10share=round(float(top10/tot),3) if tot>0 else None,yy=yy)
print("\n=== EXECUTION TEST (short next M15 open; H1 structural stop; STRESS cost) ===")
for hid,hc,he,me in [("N7 failcont-break","FAILED_CONT","STRUCT_BREAK","MICRO_BREAKDOWN"),
                     ("N4 swinghi-sweep","SWINGHIGH_INTERACT","HIGH_SWEEP","FAILED_RECLAIM"),
                     ("N8 twostage","BULLISH_STATE","SECOND_BEAR","SECOND_BEAR"),
                     ("N12 upper-closebl","UPPER_RANGE","CLOSE_BELOW_LEVEL","BEAR_DISP")]:
    m=full_mask(hc,he,me)
    for rr in (1.5,2.0,3.0):
        r=execute(m,rr)
        if r: print(f"  {hid:20s} rr{rr}: n{r['n']} WR{r['wr']} avg{r['avg']:+.3f} med{r['med']:+.3f} b5{r['b5']:+.3f} b10{r['b10']:+.3f} top10%{r['top10share']} yy{r['yy']}")
    print()
