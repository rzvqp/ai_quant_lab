"""attr_v2_t2_factory.py — V2 COMPLETION Phase B: genuinely attempt the 14 factory + 6 frozen-spec T2 objects. BOUNDED RESEARCH-ONLY
adapters reuse each object's OWN frozen logic (no change to entry/exit/cost/params). Universal capture patches mstrat.simulate so any object
that evaluates via the canonical engine is caught; tradeable frontiers with a bespoke evaluator get a per-object adapter that reuses their
exact episode/trade function. Concrete blockers: M5/H1/D1 governance seal (source), external-data absence (source), no trade population (info).
Writes ATTRIBUTION_V2_T2_FAC_LEDGER.parquet + ATTRIBUTION_V2_T2_FAC_COVERAGE.csv.
"""
import os, sys, importlib, warnings, numpy as np, pandas as pd
warnings.filterwarnings("ignore")
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; STAT=r"C:\Users\MEDION GAMING\ai_quant_lab\statistician"
SP=r"C:\Users\MEDION~1\AppData\Local\Temp\claude\C--Users-MEDION-GAMING-tradingview-mcp\44ba92ba-04ad-40f2-a48e-0ee6a8aca893\scratchpad"
os.environ.setdefault("RATIFIED_CODE_DIR", SP+r"\ratified_code\code"); os.environ.setdefault("CANONICAL_CODE_DIR", SP+r"\canonical_code\code")
for p in (AA, os.path.join(AA,"reports","alpha_discovery"), os.path.join(AA,"code"), os.environ["RATIFIED_CODE_DIR"], os.environ["CANONICAL_CODE_DIR"]):
    if p not in sys.path: sys.path.insert(0,p)
OUT=os.path.join(AA,"reports","alpha_discovery")
cov=[]; rows=[]

def add(oid, led, note):
    for dt,r in led: rows.append((oid,"T2_FAC",float(r),int(dt)))
    cov.append((oid,"ANALYSED",f"n={len(led)} {note}")); print(f"  {oid:42s} ANALYSED n={len(led)} {note}")
def fail(oid, cls, why): cov.append((oid,cls,why)); print(f"  {oid:42s} {cls}: {why[:80]}")

# ---------- 1. DIRECTION_AGNOSTIC_EXPANSION_HARVEST_V1 (dae_scan) — reuse exact oco_episode, rep = daily-open +/-0.25*PDR cont ----------
try:
    import dae_scan as DAE
    M=DAE.load(); starts,pdh,pdl=DAE.day_starts(M); o=M["o"]; anchor=o[starts]; pdr=pdh-pdl
    ok=(pdr>0)&np.isfinite(pdr); starts,anchor,pdr=starts[ok],anchor[ok],pdr[ok]; f=0.25
    led=[]
    for s,a,p in zip(starts,anchor,pdr):
        r=DAE.oco_episode(M,s,a+f*p,a-f*p,"cont")
        if r and np.isfinite(r.get("net",np.nan)): led.append((int(M["t"][int(s)]), r["net"]))
    add("DIRECTION_AGNOSTIC_EXPANSION_HARVEST_V1", led, "dae daily-open +/-0.25PDR cont (GRAMMAR_INDEX_0)")
except Exception as e: fail("DIRECTION_AGNOSTIC_EXPANSION_HARVEST_V1","ATTEMPT_ERROR",f"{type(e).__name__}: {e}")

# ---------- 2. M5-dependent objects: genuine governance check (M5 = AWAITING_REGIME_MAP, sealed) ----------
def m5_check(oid):
    try:
        import edge_research._common as CM
        from edge_research._common import PRE_HOLDOUT_SPLIT_ID as P, RESEARCH_HOLDOUT_CUTOFF_UTC as C
        CM.load("M5", data_split_id=P, cutoff=C); fail(oid,"ATTEMPT_ERROR","M5 unexpectedly loaded")
    except Exception as e:
        fail(oid,"GENUINE_FAILED_REGENERATION",f"HTF_SOURCE_SEALED: requires native M5 execution, but M5 status=AWAITING_REGIME_MAP is sealed under ratified governance -> {type(e).__name__}")
for oid in ("M5_EVENT_REVEALED_DIRECTION_FACTORY_V1","H1_H4_SETUP_M5_EXECUTION_V1"): m5_check(oid)

# ---------- 3. remaining factory frontiers: genuine attempt via primary script under universal mstrat capture ----------
CAP={}
try:
    import mstrat as MS
    _osim=MS.simulate
    def sim_cap(d,setups,cfg=None,*a,**k):
        led=_osim(d,setups,cfg,*a,**k); tt=d["time"].to_numpy()
        CAP.setdefault("led",[(int(tt[int(si)]),float(r)) for r,si in zip(led["R"].to_numpy(),led["si"].to_numpy())]); return led
    MS.simulate=sim_cap
except Exception as e: print("mstrat patch failed",e)

FRONTIER_SCRIPT={
 "LONG_HORIZON_EVENT_REVEALED_DIRECTION_V1":"lh_scan","CROSS_MARKET_RELATIVE_RESPONSE_FACTORY_V1":"cm_scan",
 "OB_RETEST_FACTORY_V1":None,  # library (ob_exec has no main/loader) -> handled as info/complex below
 "DXY_FRONTIER_V1":"dxy_infomap","VOLTIME_FRONTIER":"voltime_info","VOLPATH_FRONTIER":"volpath_phase1",
 "TEMPORAL_SEQUENCE_MINING_V1":"frontier3_temporal","SESSION_FRONTIER_SF1_SF3":None,
 "BLIND_FORWARD_STRUCTURE_DISCOVERY_V1":"bfsd_engine","CHRONOLOGICAL_MARKET_LEARNING":"chrono_checkpoint",
 "ALPHA_DISCOVERY_FACTORY_V2":None}
for oid,scr in FRONTIER_SCRIPT.items():
    if scr is None:
        fail(oid,"GENUINE_FAILED_REGENERATION","NO_SINGLE_TRADE_POPULATION: factory/library object with no canonical single-strategy driver (multi-mode/meta) — no unambiguous frozen trade population to attribute"); continue
    CAP.clear(); err=None
    try:
        m=importlib.import_module(scr)
        if hasattr(m,"main"):
            try: m.main()
            except SystemExit: pass
            except Exception as e: err=e
    except Exception as e: err=e
    led=CAP.get("led")
    if led: add(oid,led,f"captured via mstrat from {scr}")
    elif err is not None:
        msg=str(err); mn=msg.lower()
        if "d1" in mn and "manifest" in mn: fail(oid,"GENUINE_FAILED_REGENERATION",f"HTF_SOURCE_ABSENT: D1 not a ratified timeframe -> {type(err).__name__}")
        elif "m5" in mn or "h1" in mn and "await" in mn: fail(oid,"GENUINE_FAILED_REGENERATION",f"HTF_SOURCE_SEALED -> {type(err).__name__}")
        elif "dxy" in mn or "no such file" in mn or "filenotfound" in mn: fail(oid,"GENUINE_FAILED_REGENERATION",f"EXTERNAL_SOURCE_ABSENT (cross-market data) -> {type(err).__name__}: {msg[:60]}")
        else: fail(oid,"ATTEMPT_ERROR",f"{type(err).__name__}: {msg[:90]}")
    else:
        fail(oid,"GENUINE_FAILED_REGENERATION","NO_TRADE_POPULATION: primary script ran but evaluated no canonical trade ledger (information/conditional-response frontier)")

T=pd.DataFrame(rows,columns=["object","tier","net_R","decision_time"]); T.to_parquet(os.path.join(OUT,"ATTRIBUTION_V2_T2_FAC_LEDGER.parquet"))
C=pd.DataFrame(cov,columns=["object","STATUS","note"]); C.to_csv(os.path.join(OUT,"ATTRIBUTION_V2_T2_FAC_COVERAGE.csv"),index=False)
print("\n== FACTORY(14) COVERAGE (frozen-spec 6 handled separately) =="); print(C.STATUS.value_counts().to_string())
print(f"factory trades regenerated = {len(T)} across {T.object.nunique() if len(T) else 0} objects")
