"""range_extract.py — run the RATIFIED (unmodified) RANGE vNext read-only over each authorized M15 era-slice,
caching per-bar lifecycle events + state to __range_cache__/{era}.parquet. Gap-safe: each contiguous era gets a FRESH
engine (no state bridging across the 2014-2015 or era gaps). Aligned to the era sub-frame row order (+time for verify).
Events captured (boundary side kept for boundary events). Descriptors: macro_state, active_macro_count, regime,
boundary_upper/lower, confirm_ts, role. NO modification of ve_n1_replay; config_id guard asserted.
"""
import sys, os, time
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\ve_n1_replay")
_HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,_HERE)
import numpy as np, pandas as pd
from ve_n1_replay import Bar
from ve_n1_replay.version import RAW_AXES_BUILDER_IMPL_COMMIT as IC
from ve_n1_replay.range_engine_vnext import RangeSemanticEngineVNext
from ve_n1_replay.range_semantic_vnext import ConfigVNext, RANGE_HIERARCHICAL_VNEXT_NORMATIVE_CONFIG_ID
import swing_base as sb, hist_m15_data as m15d
CACHE=os.path.join(_HERE,"__range_cache__"); os.makedirs(CACHE,exist_ok=True)

BOOLS=["E_OK_MACRO","E_BO_up","E_BO_dn","E_SWEEP_up","E_SWEEP_dn","E_SWEEP_REV_up","E_SWEEP_REV_dn",
       "E_BIRTH","E_CONTIN","E_MERGED","E_ABANDON","E_SUPERSEDE","E_TREND","E_WEAKEN","E_WEAKEN_REC","E_CAND_PRESENT","E_CAND_PRESENT_any"]

def make_engine():
    assert ConfigVNext().config_id()==RANGE_HIERARCHICAL_VNEXT_NORMATIVE_CONFIG_ID, "RANGE vNext config_id MISMATCH"
    return RangeSemanticEngineVNext(symbol="XAUUSD",timeframe="15m",bar_interval_seconds=900,
        implementation_commit=IC, range_config=ConfigVNext(), acknowledge_construction_only=True)

def run_slice(sub, tag):
    hasv="volume" in sub.columns
    t=sub["time"].to_numpy(); o=sub["open"].to_numpy(); h=sub["high"].to_numpy(); l=sub["low"].to_numpy(); c=sub["close"].to_numpy()
    v=sub["volume"].to_numpy() if hasv else None; n=len(sub)
    cols={b:np.zeros(n,bool) for b in BOOLS}
    mstate=np.empty(n,object); ncand=np.zeros(n,int); regime=np.empty(n,object)
    bup=np.full(n,np.nan); blo=np.full(n,np.nan); confts=np.full(n,np.nan); role=np.empty(n,object)
    eng=make_engine(); t0=time.time()
    for k in range(n):
        bar=Bar(symbol="XAUUSD",ts_open=int(t[k]),ts_close=int(t[k])+900,open=float(o[k]),high=float(h[k]),
                low=float(l[k]),close=float(c[k]),volume=float(v[k]) if hasv else 100.0)
        _,res,events=eng.observe_closed_bar(bar)
        for e in events:
            kd=e.kind; bd=getattr(e,"boundary",None)
            if kd=="OK_RANGE_MACRO": cols["E_OK_MACRO"][k]=True
            elif kd=="BREAKOUT_ACCEPTED": (cols["E_BO_up"] if bd=="upper" else cols["E_BO_dn"])[k]=True
            elif kd=="SWEEP_CONFIRMED": (cols["E_SWEEP_up"] if bd=="upper" else cols["E_SWEEP_dn"])[k]=True
            elif kd=="LIQUIDITY_SWEEP_REVERSAL": (cols["E_SWEEP_REV_up"] if bd=="upper" else cols["E_SWEEP_REV_dn"])[k]=True
            elif kd=="EPISODE_REPLACEMENT": cols["E_BIRTH"][k]=True
            elif kd=="EPISODE_CONTINUATION": cols["E_CONTIN"][k]=True
            elif kd=="EPISODE_MERGED": cols["E_MERGED"][k]=True
            elif kd=="CANDIDATE_ABANDONED_PRICE_MOVED_ON": cols["E_ABANDON"][k]=True
            elif kd=="CANDIDATE_SUPERSEDED_BY_MERGE": cols["E_SUPERSEDE"][k]=True
            elif kd=="IS_TREND_MACRO": cols["E_TREND"][k]=True
            elif kd=="RANGE_WEAKENING": cols["E_WEAKEN"][k]=True
            elif kd=="WEAKENING_RECOVERED": cols["E_WEAKEN_REC"][k]=True
            elif kd=="RANGE_CANDIDATE_PRESENT": cols["E_CAND_PRESENT"][k]=True
        mstate[k]=res.macro_state; ncand[k]=res.active_macro_count; regime[k]=res.regime
        bup[k]=res.macro_boundary_upper if res.macro_boundary_upper is not None else np.nan
        blo[k]=res.macro_boundary_lower if res.macro_boundary_lower is not None else np.nan
        confts[k]=res.macro_confirm_ts if res.macro_confirm_ts is not None else np.nan
        role[k]=res.macro_role
    df=pd.DataFrame(cols); df["time"]=t; df["mstate"]=mstate; df["ncand"]=ncand; df["regime"]=regime
    df["bup"]=bup; df["blo"]=blo; df["confts"]=confts; df["role"]=role; df["bar_index"]=np.arange(n)
    df.to_parquet(os.path.join(CACHE,f"{tag}.parquet"))
    print(f"[{tag}] n={n} secs={time.time()-t0:.0f} events={int(sum(df[b].sum() for b in BOOLS))} OK_MACRO={int(df['E_OK_MACRO'].sum())} BO_up={int(df['E_BO_up'].sum())} BO_dn={int(df['E_BO_dn'].sum())} SWEEP_up={int(df['E_SWEEP_up'].sum())} SWEEP_dn={int(df['E_SWEEP_dn'].sum())} BIRTH={int(df['E_BIRTH'].sum())} maxcand={int(ncand.max())}",flush=True)

def main():
    hm=m15d.build(verbose=False)["M15"]; sm=sb.build_frames()["M15"]
    for tag,fr,mk in [("b0",hm,"is_b0"),("b1",hm,"is_b1"),("DEV",sm,"is_dev"),("CAL",sm,"is_cal")]:
        sub=fr[fr[mk].to_numpy()].reset_index(drop=True); run_slice(sub,tag)
    print("RANGE EXTRACT DONE")

if __name__=="__main__":
    main()
