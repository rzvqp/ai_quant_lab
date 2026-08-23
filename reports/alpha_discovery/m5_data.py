"""m5_data.py — CAUSAL M5 substrate (mandate NATIVE_M5_AUTHORIZED, 2026-08-23). Native OANDA XAUUSD M5 (2021-07-27..2026-07-27,
354,669 bars, sha256 cbb6eebe; verified monotonic/no-dupes/OHLC-valid/tick-volume). NO M15->M5 fabrication. Higher-TF state
(M15/H1/H4) aligned to each M5 bar by the STRICT NOMINAL-close contract (cur_data.causal_bucket_asof for H1/H4; identical
searchsorted(start+sec) logic for M15) -> an M5 bar at time T sees ONLY higher-TF buckets whose NOMINAL close (start+TF_sec)<=T
(last fully-closed bucket), never a forming one and never its own bucket even across gaps. Same _feat recipe. COVERAGE CAVEAT:
M5 only 2021-07-27+ (single macro-era); cross-era pre-2021 M5 impossible -> disclose on every finding; no era-independence claim."""
import numpy as np, pandas as pd
import cur_data as CD
M5PATH=r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\data\market\OANDA_XAUUSD_M5.csv"
SEC={"M15":900,"H1":3600,"H4":14400}
_M5=None; _HTF={}
def load_m5():
    global _M5
    if _M5 is None:
        d=pd.read_csv(M5PATH).drop_duplicates("time").sort_values("time").reset_index(drop=True)
        d["dt"]=pd.to_datetime(d["time"],unit="s",utc=True); d=CD._feat(d); d["close_time"]=d["time"].to_numpy()+300
        _M5=d
    return _M5
def _asof_nominal(t, starts, sec):
    starts=np.asarray(sorted(set(int(x) for x in starts)),np.int64); ct=starts+sec
    idx=np.searchsorted(ct,np.asarray(t,np.int64),side="right")-1
    out=np.full(len(t),-1,np.int64); ok=idx>=0; out[ok]=starts[idx[ok]]; return out
def htf_at_m5(m5, tf):
    if tf in _HTF: return _HTF[tf]
    m15=CD.load_m15(); x=(m15 if tf=="M15" else CD.agg(m15,tf)).copy()
    starts=x["time"].to_numpy().astype("int64"); t=m5["time"].to_numpy().astype("int64")
    ms = CD.causal_bucket_asof(t, starts, tf) if tf in ("H1","H4") else _asof_nominal(t, starts, SEC[tf])
    xi=x.set_index("time")[["open","high","low","close","atr","ema20","ema50","effic"]]
    j=xi.reindex(ms).reset_index(drop=True); j.columns=[f"{tf.lower()}_{c}" for c in j.columns]
    j[f"{tf.lower()}_start"]=ms
    _HTF[tf]=j; return j
if __name__=="__main__":
    m=load_m5(); print(f"M5: n={len(m)} {m['dt'].min()}..{m['dt'].max()} lastclose={m['close'].iloc[-1]:.1f}")
    t=m["time"].to_numpy().astype("int64")
    for tf in ("M15","H1","H4"):
        j=htf_at_m5(m,tf); ms=j[f"{tf.lower()}_start"].to_numpy(); sec=SEC[tf]; ok=ms>=0
        nomclose=ms[ok]+sec
        leak=int((nomclose>t[ok]).sum())                    # nominal close AFTER M5 bar = lookahead
        inside=int(((t[ok]>=ms[ok])&(t[ok]<ms[ok]+sec)).sum())  # M5 inside mapped nominal window
        print(f"  align {tf}: mapped {int(ok.sum())}/{len(m)} | nominal-close-leak={leak} | M5-inside-mapped={inside} -> {'CAUSAL-PASS' if leak==0 and inside==0 else 'LOOKAHEAD-FAIL'}")
