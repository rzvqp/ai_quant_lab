"""cur_screen.py — CURRENT-REGIME re-screen harness (Phase 3). Runs a candidate's EXACT frozen definition on the
unified rebased M15 (2011-2026), restricts trades to CURRENT_LIKE_POPULATION_V1 periods, partitions by time
(DISC<=2021 / CONF 2022-24 / recent-OOS 2025-26), STRESS cost. Structurally-dissimilar (non-current-like) periods are
reported DIAGNOSTIC ONLY (not a veto, §4). A current-regime survivor = positive + robust across current-like DISC+CONF
(+OOS where N permits), with a causal OFF-switch (the frozen signature). No retuning (§8).
"""
import numpy as np, pandas as pd
import cur_data as CD, swing_base as sb
from batch_a import orb, _hr_day, _mk
from frontier_p import ny_pm_disp
_M=None; _LK=None
def _load():
    global _M,_LK
    if _M is None:
        _M=CD.load_m15()
        lk=pd.read_parquet("__cur_cache__/current_like_h4.parquet"); _LK=dict(zip(lk["time"].to_numpy().astype(np.int64), lk["like"].to_numpy()))
    return _M,_LK
def like_at(times):
    _,LK=_load(); h4=(np.asarray(times,np.int64)//14400)*14400
    return np.array([bool(LK.get(int(t),False)) for t in h4])

def rescreen(name, sigfn, side, rr, H, cool=8):
    m,_=_load(); idx,sl=sigfn(m); idx=np.asarray(idx); sl=np.asarray(sl,float)
    o=np.argsort(idx); idx=idx[o]; sl=sl[o]; dd=sb.dedup_events(idx,cool); p=np.isin(idx,dd); idx=idx[p]; sl=sl[p]
    ok=np.isfinite(sl)&(sl>0); idx=idx[ok]; sl=sl[ok]
    tr=sb.simulate(m,idx,side,sl,rr=rr,horizon=H,scenario="STRESS")
    if len(tr)==0: print(f"[{name}] no trades"); return
    te=tr["t_entry"].to_numpy(); r=tr["R"].to_numpy(); yr=pd.Series(pd.to_datetime(te,unit="s",utc=True)).dt.year.to_numpy()
    cl=like_at(te)
    def stat(msk):
        rr_=r[msk]; return (len(rr_), float(rr_.mean()) if len(rr_) else float('nan'))
    allc=cl; disc=cl&(yr<=2021); conf=cl&(yr>=2022)&(yr<=2024); oos=cl&(yr>=2025); noncur=~cl
    parts={"CUR-LIKE(all)":allc,"  DISC<=2021":disc,"  CONF 22-24":conf,"  OOS 25-26":oos,"DIAG non-cur":noncur}
    print(f"\n[{name}] side={'L' if side>0 else 'S'} rr{rr} totalN={len(tr)}")
    for k,msk in parts.items():
        n,a=stat(msk); print(f"    {k:16s}: n={n:5d} avgR={a:+.3f}")
    # verdict on current-like DISC+CONF
    _,da=stat(disc); _,ca=stat(conf); _,aa=stat(allc)
    surv = (disc.sum()>=25 and conf.sum()>=25 and da>0 and ca>0)
    print(f"    -> {'CURRENT_REGIME_SURVIVOR-candidate' if surv else 'not a current-regime survivor'} (DISC {da:+.3f}, CONF {ca:+.3f}, CUR-all {aa:+.3f})")

# --- candidate signal defs (exact frozen; §8 no retuning) ---
def comp_cont_L(fr, lo=13, hi=21):  # NY compression->long (the R26xR29 combo Q; retest under current-regime)
    from batch_a import _hr_day as HD
    hr,_,_=HD(fr); h=fr["high"]; l=fr["low"]; atr=fr["atr"].to_numpy(); atrm=fr["atr_ma"].to_numpy()
    bh=h.rolling(8).max().shift(1).to_numpy(); bl=l.rolling(8).min().shift(1).to_numpy()
    box=bh-bl; bm=pd.Series(box).rolling(50).mean().shift(1).to_numpy(); vr=atr/atrm
    comp=(box<0.7*bm)&(vr<0.9)&np.isfinite(bm)&(hr>=lo)&(hr<hi)
    return _mk(np.nan_to_num(comp.astype(float),nan=0).astype(bool),fr,bl,1)

if __name__=="__main__":
    print("CURRENT-REGIME RE-SCREEN (Phase 3/4). Exact frozen defs, STRESS, current-like partition. Non-cur=DIAGNOSTIC.")
    rescreen("ORB_NY_L (S5 anchor)", lambda f:orb(f,13,21,1), 1, 3.0, 48)
    rescreen("NYpm_disp_L(15-21) [Frontier P]", lambda f:ny_pm_disp(f,15,21), 1, 2.0, 48)
    rescreen("NYpm_comp_L(13-21) [Frontier Q]", lambda f:comp_cont_L(f,13,21), 1, 2.0, 48)
    print("\n--- PHASE 4 seed: REVERSION/FADE (cross-era-negative; hypothesized current-regime=corrective specialists) ---")
    from batch_a import mr_ext
    from batch_b import range_fade
    from frontier_l import rejection
    rescreen("MR_ext_L (2sigma SMA100)", lambda f:mr_ext(f,1), 1, 2.0, 48)
    rescreen("MR_ext_S (2sigma SMA100)", lambda f:mr_ext(f,-1), -1, 2.0, 48)
    rescreen("RANGE_fade_L", lambda f:range_fade(f,1), 1, 2.0, 48)
    rescreen("RANGE_fade_S", lambda f:range_fade(f,-1), -1, 2.0, 48)
    rescreen("REJECT_newhigh_S", lambda f:rejection(f,-1), -1, 2.0, 48)
    print("\n--- PHASE 4b: SHORT-CONTINUATION aligned with the current DOWN-correction (R4 trend-aligned) ---")
    from batch_b import sb_break
    def disp_dn(fr):  # down-displacement -> short continuation, stop = bar high
        o=fr["open"].to_numpy(); c=fr["close"].to_numpy(); h=fr["high"].to_numpy(); l=fr["low"].to_numpy(); atr=fr["atr"].to_numpy(); rng=h-l
        ev=((o-c)>0.7*atr)&(c<l+0.25*rng)&(rng>1.2*atr)
        return _mk(np.nan_to_num(ev.astype(float),nan=0).astype(bool),fr,h,-1)
    rescreen("SB_break_S (Donchian breakdown)", lambda f:sb_break(f,-1,12), -1, 2.0, 48)
    rescreen("SB_break_S_rr3", lambda f:sb_break(f,-1,12), -1, 3.0, 64)
    rescreen("DISP_dn_S (displacement-down)", disp_dn, -1, 2.0, 48)
    rescreen("DISP_dn_S_rr3", disp_dn, -1, 3.0, 64)
