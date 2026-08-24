"""bfsd2_mine.py — emergent morphology mining + conditional outcomes (post-observation; outcomes touched ONLY here).
Reads bfsd2_stream.npz (agnostic symbol stream + canonical N1/N2). Morphology EMERGES as a recurring 3-gram of the observed
structural symbols (sym[T-2],sym[T-1],sym[T]) — NOT predefined. For each frequent morphology, estimates forward conditional
outcome P(up 1.5ATR before dn 1.5ATR within 48 bars), MFE/MAE, CONDITIONED BY N1 regime direction (regime specialists allowed;
era-stability NOT required — per-era n shown for transparency only). Baseline = unconditional / per-regime win rate; a morphology
is interesting only if it adds information vs baseline (§11). DISCOVERY ONLY — promising clusters -> preregister -> mechanize ->
full quant-falsification (§12/§13)."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
import cur_data as CD
K=48; TGT=1.5
def main():
    m=CD.load_m15(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy(); atr=m["atr"].to_numpy(); n=len(m)
    z=np.load(r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery\bfsd2_stream.npz",allow_pickle=True)
    sym=z["sym"].astype(str); n1dir=z["n1dir"].astype(str); yr=z["yr"]
    # --- forward outcome per bar (post-observation): win_up = up TGT*ATR before dn TGT*ATR within K ---
    win=np.full(n,np.nan)  # 1 up-first, 0 dn-first, nan unresolved/invalid
    for T in range(n):
        if not np.isfinite(atr[T]) or atr[T]<=0 or T+1>=n: continue
        tgt=TGT*atr[T]; seg_h=h[T+1:T+1+K]; seg_l=l[T+1:T+1+K]
        if len(seg_h)<8: continue
        uu=np.where(seg_h-c[T]>=tgt)[0]; dd=np.where(c[T]-seg_l>=tgt)[0]
        fu=uu[0] if len(uu) else 10**9; fd=dd[0] if len(dd) else 10**9
        if fu==fd==10**9: continue
        win[T]=1.0 if fu<fd else 0.0
    resolved=np.isfinite(win)
    base=np.nanmean(win[resolved]); print(f"bfsd2_mine: resolved={int(resolved.sum())} BASELINE P(up-first)={base:.3f} (null 0.5)")
    era=np.where(yr<=2018,"D",np.where(yr<=2022,"C","O"))
    # per-regime baseline
    print("Per-N1-regime baseline P(up-first):")
    for rg in sorted(set(n1dir)):
        mask=resolved&(n1dir==rg)
        if mask.sum()>=300: print(f"  N1dir={rg:10s} n={int(mask.sum()):6d} P={np.nanmean(win[mask]):.3f}")
    # --- emergent 3-gram morphologies ---
    tri=np.empty(n,object); tri[:]= "na"
    for T in range(2,n):
        if sym[T]=="na" or sym[T-1]=="na" or sym[T-2]=="na": continue
        tri[T]=sym[T-2]+" >> "+sym[T-1]+" >> "+sym[T]
    from collections import defaultdict
    idxby=defaultdict(list)
    for T in range(2,n):
        if tri[T]!="na" and resolved[T]: idxby[tri[T]].append(T)
    # rank by |P-base|, require n>=150
    rows=[]
    for k,v in idxby.items():
        if len(v)<150: continue
        vi=np.array(v); p=np.nanmean(win[vi])
        rows.append((k,len(v),p,p-base))
    rows.sort(key=lambda x:-abs(x[3]))
    print(f"\nEMERGENT 3-gram morphologies (n>=150), ranked by |P-baseline|  [P(up-first) | Δbase | n]:")
    for k,nn,p,d in rows[:22]:
        print(f"  {k:44s} n={nn:5d} P={p:.3f} Δ={d:+.3f}")
    # --- regime-specialist view: best morphology×regime cells (era-stability NOT required) ---
    print("\nREGIME SPECIALISTS: morphology × N1dir cells, n>=80, ranked by |P-base|:")
    cells=[]
    for k,v in idxby.items():
        if len(v)<200: continue
        vi=np.array(v)
        for rg in set(n1dir[vi]):
            sub=vi[n1dir[vi]==rg]
            if len(sub)<80: continue
            p=np.nanmean(win[sub])
            # per-era n for transparency
            ec={e:int(np.sum(era[sub]==e)) for e in ["D","C","O"]}
            cells.append((k,rg,len(sub),p,p-base,ec))
    cells.sort(key=lambda x:-abs(x[4]))
    for k,rg,nn,p,d,ec in cells[:22]:
        print(f"  [{rg:9s}] {k:40s} n={nn:4d} P={p:.3f} Δ={d:+.3f} era(D{ec['D']}/C{ec['C']}/O{ec['O']})")
    print("\nDISCOVERY ONLY — no edge claimed. A morphology×regime cell with material Δ and adequate n across ≥50-100 obs becomes a")
    print("PREREGISTERED hypothesis for §12 mechanize + §13 full quant-falsification. Regime specialists are valid (no era-stability req).")
if __name__=="__main__": main()
