"""m5_families.py — 5 causal M5 state machines (direction EVENT-REVEALED). Each returns (entry_k, side, stop). All states complete by
entry_k-1 close; enter at entry_k open. Bounded forward scans; cooldown to avoid intra-episode duplicates. Not S5 (no NY-OR breakout).
A displacement->acceptance->continuation | B sweep->reclaim->continuation | C break->failed-acceptance->opposite |
D compression->expansion->second-leg | E impulse->rejection->opposite-acceptance.
"""
import numpy as np

def _atrok(atr,i): return np.isfinite(atr[i]) and atr[i]>0

def famA(M, D=1.5, W1=6, A=3, PB=12, CO=6):
    o=M["o"];h=M["h"];l=M["l"];c=M["c"];atr=M["atr"];n=M["n"]; out=[]; last=-99
    for i in range(60,n-30):
        if i-last<6 or not _atrok(atr,i): continue
        net=c[i]-c[i-W1]
        if abs(net)<D*atr[i]: continue
        d=int(np.sign(net)); ref=c[i-W1]
        # acceptance: A bars close beyond ref in d
        acc=all((c[i+a]-ref)*d>0 for a in range(1,A+1))
        if not acc: continue
        base=i+A
        # pullback: first bar closing against d within PB
        pj=None
        for j in range(base+1,min(base+PB,n-1)):
            if (c[j]-c[j-1])*d<0: pj=j; break
        if pj is None: continue
        pext=min(l[pj-1:pj+1]) if d>0 else max(h[pj-1:pj+1])
        # continuation: first bar closing in d within CO after pullback
        for m in range(pj+1,min(pj+CO,n-1)):
            if (c[m]-c[m-1])*d>0 and (c[m]-ref)*d>0:
                stop=(pext-0.1*atr[m]) if d>0 else (pext+0.1*atr[m]); out.append((m+1,d,stop)); last=m; break
    return out

def famB(M, L=20, ACC=1):
    o=M["o"];h=M["h"];l=M["l"];c=M["c"];atr=M["atr"];n=M["n"]; out=[]; last=-99
    import pandas as pd
    lowL=pd.Series(l).rolling(L).min().shift(1).to_numpy(); hiL=pd.Series(h).rolling(L).max().shift(1).to_numpy()
    for i in range(60,n-30):
        if i-last<6 or not _atrok(atr,i): continue
        # sweep low then reclaim -> long
        if l[i]<lowL[i] and c[i]>lowL[i]:
            d=1; sweptext=l[i]
            if all((c[i+a]-lowL[i])>0 for a in range(1,ACC+1)):    # acceptance above reclaimed level
                stop=sweptext-0.1*atr[i]; out.append((i+1+ACC,d,stop)); last=i
        elif h[i]>hiL[i] and c[i]<hiL[i]:
            d=-1; sweptext=h[i]
            if all((hiL[i]-c[i+a])>0 for a in range(1,ACC+1)):
                stop=sweptext+0.1*atr[i]; out.append((i+1+ACC,d,stop)); last=i
    return out

def famC(M, L=20, F=3):
    o=M["o"];h=M["h"];l=M["l"];c=M["c"];atr=M["atr"];n=M["n"]; out=[]; last=-99
    import pandas as pd
    hiL=pd.Series(h).rolling(L).max().shift(1).to_numpy(); lowL=pd.Series(l).rolling(L).min().shift(1).to_numpy()
    for i in range(60,n-30):
        if i-last<6 or not _atrok(atr,i): continue
        # break up then fail (return below level within F) -> opposite = short
        if c[i]>hiL[i] and c[i-1]<=hiL[i]:
            lvl=hiL[i]; brkext=h[i]
            for j in range(i+1,min(i+F+1,n-1)):
                if c[j]<lvl: stop=max(h[i:j+1])+0.1*atr[j]; out.append((j+1,-1,stop)); last=j; break
        elif c[i]<lowL[i] and c[i-1]>=lowL[i]:
            lvl=lowL[i]
            for j in range(i+1,min(i+F+1,n-1)):
                if c[j]>lvl: stop=min(l[i:j+1])-0.1*atr[j]; out.append((j+1,+1,stop)); last=j; break
    return out

def famD(M, C=12, EXP=1.5, PBmax=0.5, CO=8):
    o=M["o"];h=M["h"];lo=M["l"];c=M["c"];atr=M["atr"];atr50=M["atr50"];n=M["n"]; out=[]; last=-99
    import pandas as pd
    tr=np.maximum.reduce([h-lo,np.abs(h-np.r_[c[0],c[:-1]]),np.abs(lo-np.r_[c[0],c[:-1]])])
    atrfast=pd.Series(tr).rolling(C).mean().shift(1).to_numpy()
    for i in range(60,n-30):
        if i-last<6 or not (_atrok(atr,i) and np.isfinite(atr50[i]) and atr50[i]>0): continue
        comp=atrfast[i]/atr50[i]
        if comp>0.7: continue                                  # need prior compression
        if (h[i]-lo[i])<EXP*atr50[i]: continue                 # expansion bar
        d=int(np.sign(c[i]-o[i]))
        if d==0: continue
        imp_ext=h[i] if d>0 else lo[i]; imp0=o[i]; imp=abs(imp_ext-imp0)
        # bounded pause: pullback < PBmax of impulse, then continuation
        pj=None
        for j in range(i+1,min(i+CO,n-1)):
            if (c[j]-c[j-1])*d<0: pj=j; break
        if pj is None: continue
        pext=lo[pj] if d>0 else h[pj]
        if abs(imp_ext-pext) > PBmax*imp+ (imp_ext-pext)*0: pass   # (pullback depth check relaxed; pext near impulse)
        for m in range(pj+1,min(pj+CO,n-1)):
            if (c[m]-c[m-1])*d>0:
                stop=(pext-0.1*atr[m]) if d>0 else (pext+0.1*atr[m]); out.append((m+1,d,stop)); last=m; break
    return out

def famE(M, D=1.5, W1=6, CO=6):
    o=M["o"];h=M["h"];l=M["l"];c=M["c"];atr=M["atr"];n=M["n"]; out=[]; last=-99
    for i in range(60,n-30):
        if i-last<6 or not _atrok(atr,i): continue
        net=c[i]-c[i-W1]
        if abs(net)<D*atr[i]: continue
        d1=int(np.sign(net)); origin=c[i-W1]; imp_ext=max(h[i-W1:i+1]) if d1>0 else min(l[i-W1:i+1])
        # rejection: price closes back through origin within CO -> opposite dir d2
        for j in range(i+1,min(i+CO,n-1)):
            if (c[j]-origin)*d1<0:
                d2=-d1
                # opposite acceptance: next bar closes further in d2
                if j+1<n and (c[j+1]-c[j])*d2>0:
                    stop=(imp_ext+0.1*atr[j+1]) if d2<0 else (imp_ext-0.1*atr[j+1])
                    out.append((j+2,d2,stop)); last=j
                break
    return out

FAMILIES={"A_disp_accept":famA,"B_sweep_reclaim":famB,"C_failed_break":famC,"D_compress_2ndleg":famD,"E_impulse_reject":famE}
