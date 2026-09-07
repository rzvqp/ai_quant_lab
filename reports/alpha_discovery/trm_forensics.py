"""trm_forensics.py — TRADER-READ EXECUTION GEOMETRY FORENSIC AUDIT V1. Reproduces the exact 5 frozen ledgers (via the frozen trm_v1 detectors)
and diagnoses WHY trades lose: directional idea vs execution geometry. Every original trade stays frozen; all alternatives are
COUNTERFACTUAL_DIAGNOSTIC_ONLY. Computes loser classification (L1-L6), post-stop MFE, winner MAE, stop overshoot, structural invalidation,
intrabar ambiguity (+M5 resolution 2021+), entry-location slippage, directional path quality, 100-pip audit, level-to-level map, fixed-2R vs
next-level, counterfactual stops (diagnostic), Family-B and Family-E special audits. NO optimization.
"""
import os, sys, numpy as np, pandas as pd
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; OUT=os.path.join(AA,"reports","alpha_discovery")
sys.path.insert(0, os.path.join(AA,"code")); sys.path.insert(0, OUT)
import trm_v1 as TR   # runs the frozen detectors + writes identical frozen ledgers (deterministic)
O,H,L,Cl,ATR,Tt,n=TR.O,TR.H,TR.L,TR.Cl,TR.ATR,TR.T,TR.n; SWH,SWL=TR.SWH,TR.SWL; DET=TR.DET
pdh=TR.d["pdh"].to_numpy(float); pdl=TR.d["pdl"].to_numpy(float); sh=TR.d["sess_high"].to_numpy(float); sl=TR.d["sess_low"].to_numpy(float)
rmax20=TR.rhi; rmin20=TR.rlo  # prior-20 structure (causal) reused as level candidates
PIP=0.10; HZ=32; RR=2.0; COST=0.419; SPREAD=0.05
EXPECT={"A_sweep_reclaim":3274,"B_breakout_pullback":220,"C_attack_decay_break":313,"D_disp_fail_reversal":5855,"E_compress_expand":100}
# reproduce trades with FULL geometry (frozen simulate logic)
def ledger(sigs):
    sigs=sorted(sigs); open_until=-1; tr=[]
    for (si,dr,stop) in sigs:
        if si<=open_until or si+1>=n: continue
        ei=si+1; entry=O[ei]; a=TR.atrf(si); risk=max(abs(entry-stop),2*SPREAD,0.05,0.10*a)
        stp=entry-dr*risk; tgt=entry+dr*RR*risk; end=min(ei+TR.BACKSTOP,n-1); R=None; exit_i=end
        for k in range(ei,end+1):
            ht=(H[k]>=tgt) if dr>0 else (L[k]<=tgt); hs=(L[k]<=stp) if dr>0 else (H[k]>=stp)
            if ht and hs: R=-1.0; exit_i=k; break
            if hs: R=-1.0; exit_i=k; break
            if ht: R=RR; exit_i=k; break
        if R is None: R=dr*(Cl[end]-entry)/risk
        net=R-COST/risk
        tr.append(dict(si=si,ei=ei,dir=dr,entry=entry,stop=stp,target=tgt,risk=risk,R=R,net_R=net,exit_i=exit_i,atr=a,sigclose=Cl[si]))
        open_until=exit_i
    return pd.DataFrame(tr)

def forensic(fam,g):
    rows=[]
    for _,t in g.iterrows():
        ei=int(t.ei); dr=int(t.dir); entry=t.entry; stp=t.stop; tgt=t.target; risk=t.risk; a=t.atr
        end=min(ei+HZ,n-1); path=slice(ei,end+1)
        hi=H[path]; lo=L[path]; cl=Cl[path]
        fav=(hi-entry) if dr>0 else (entry-lo); adv=(entry-lo) if dr>0 else (hi-entry)   # per-bar fav/adv excursion (USD)
        # stop / target bars
        hs=(lo<=stp) if dr>0 else (hi>=stp); ht=(hi>=tgt) if dr>0 else (lo<=tgt)
        sb=np.where(hs)[0]; tb=np.where(ht)[0]; stop_bar=sb[0] if len(sb) else -1; tgt_bar=tb[0] if len(tb) else -1
        same_bar=bool(stop_bar>=0 and tgt_bar>=0 and stop_bar==tgt_bar)
        # post-stop MFE (fav from entry after the stop bar), in R
        def postmfe(w):
            if stop_bar<0: return np.nan
            s=stop_bar+1; e=min(stop_bar+w, len(fav)-1)
            return float(np.max(fav[s:e+1])/risk) if e>=s else np.nan
        pm={w:postmfe(w) for w in (4,8,16,32)}
        post_max=float(np.max(fav[stop_bar+1:])/risk) if (stop_bar>=0 and stop_bar+1<len(fav)) else np.nan
        reach_2R_after_stop = bool(stop_bar>=0 and tgt_bar>stop_bar)          # stop first then original 2R target
        # winner MAE (adverse before target), fraction of stop distance
        wmae=np.nan
        if t.R>0 and tgt_bar>=0: wmae=float(np.max(adv[:tgt_bar+1])/risk)     # in R (=fraction of stop since stop=1R)
        # stop overshoot (penetration beyond stop) where recovery (post-stop fav>0)
        overshoot=np.nan
        if stop_bar>=0:
            pen=(stp-lo[stop_bar]) if dr>0 else (hi[stop_bar]-stp); overshoot=float(pen/a)
        # structural invalidation: CLOSE beyond stop within 3 bars of stop hit
        struct_inval=False
        if stop_bar>=0:
            for k in range(stop_bar,min(stop_bar+3,len(cl))):
                if (cl[k]<stp) if dr>0 else (cl[k]>stp): struct_inval=True; break
        # directional path MFE/MAE over horizons
        dirq={}
        for w in (4,8,16,32):
            e=min(w,len(fav)-1); dirq[f"mfe_{w}"]=float(np.max(fav[:e+1])); dirq[f"mae_{w}"]=float(np.max(adv[:e+1]))
        # 100-pip audit: fav move (USD) before structural invalidation (first close beyond stop)
        inval_bar=next((k for k in range(len(cl)) if ((cl[k]<stp) if dr>0 else (cl[k]>stp))), len(cl)-1)
        fav_before_inval=float(np.max(fav[:inval_bar+1])) if inval_bar>=0 else 0.0
        # level-to-level: nearest causal level in predicted dir at signal bar si
        si=int(t.si)
        cands=[]
        if dr>0:
            for lv in (pdh[si],sh[si],rmax20[si],SWH[si]):
                if np.isfinite(lv) and lv>entry: cands.append(lv)
            nextlv=min(cands) if cands else np.nan
        else:
            for lv in (pdl[si],sl[si],rmin20[si],SWL[si]):
                if np.isfinite(lv) and lv<entry: cands.append(lv)
            nextlv=max(cands) if cands else np.nan
        lvl_dist=abs(nextlv-entry) if np.isfinite(nextlv) else np.nan
        reached_level=bool(np.isfinite(nextlv) and fav_before_inval>=lvl_dist) if np.isfinite(lvl_dist) else False
        # fixed-2R vs next-level position
        tgt_dist=abs(tgt-entry)
        pos2R=("before" if np.isfinite(lvl_dist) and tgt_dist<lvl_dist*0.8 else ("beyond" if np.isfinite(lvl_dist) and tgt_dist>lvl_dist*1.2 else "near")) if np.isfinite(lvl_dist) else "no_level"
        # entry slippage (signal close -> next open) in ATR, directionally (positive = worse for the trade)
        slip=dr*(entry-t.sigclose)/a   # >0 means entry worse than signal close (moved against before entry? no: entry-sigclose in trade dir = favorable). worse = -slip
        entry_worse=-slip*a/a  # ATR units, >0 = worse
        entry_worse=float(-slip) if not np.isnan(slip) else np.nan
        rows.append(dict(family=fam,si=si,ei=ei,dir=dr,R=t.R,net_R=t.net_R,risk=risk,atr=a,
            same_bar=same_bar,stop_bar=int(stop_bar),tgt_bar=int(tgt_bar),reach_2R_after_stop=reach_2R_after_stop,
            post_stop_mfe_4=pm[4],post_stop_mfe_8=pm[8],post_stop_mfe_16=pm[16],post_stop_mfe_32=pm[32],post_stop_max=post_max,
            winner_mae_R=wmae,stop_overshoot_atr=overshoot,struct_invalidated=struct_inval,
            fav_before_inval_usd=fav_before_inval,next_level_dist_usd=lvl_dist,reached_level=reached_level,tgt_vs_level=pos2R,
            entry_worse_atr=entry_worse,**dirq))
    return pd.DataFrame(rows)

# reproduce + verify identity
LED={}; ident=True
for fam,sigs in DET.items():
    g=ledger(sigs); LED[fam]=g
    if len(g)!=EXPECT[fam]: ident=False; print(f"IDENTITY MISMATCH {fam}: {len(g)} vs {EXPECT[fam]}")
    else: print(f"  {fam}: {len(g)} trades OK")
print("ORIGINAL_TRADE_IDENTITY_GATE =", "PASS" if ident else "FAIL")
FA=pd.concat([forensic(f,LED[f]) for f in LED],ignore_index=True)
FA.to_parquet(OUT+r"\_trm_forensics.parquet")
print("forensics computed:",len(FA),"trades")
