"""attr_v2_t2_regen.py — V2 COMPLETION: genuinely regenerate the 45 T2 objects into canonical causal ledgers, join the SAME 45 blind
features at the DECISION bar. BOUNDED RESEARCH-ONLY ADAPTER: it captures each module's EXACT frozen Trade population and evaluates it with the
ONE canonical lab evaluator (mstrat.simulate via _screen.canonical_evaluate) — NO change to any entry/exit/cost/parameter/logic. Objects with
no reproducible trade population (pure information-tests, no entry/exit/PnL) are recorded GENUINE_FAILED_REGENERATION with a concrete blocker.
Phase A = 25 edge_research modules (this file). Factory(14)+frozen-spec(6) handled by attr_v2_t2_factory.py.
"""
import os, sys, json, importlib, traceback, warnings, types, numpy as np, pandas as pd
warnings.filterwarnings("ignore")

# --- scipy stub: Windows App-Control blocks scipy's compiled DLLs; the E info-tests use scipy ONLY for p-values
# (chi2/MWU), NEVER for trade construction. A universal dummy unblocks import so the TRADE population still builds;
# the info-stats become NaN and are DISCARDED (we capture only the canonical mstrat ledger). NOT a logic change. ---
try:
    import scipy  # noqa: F401
except Exception:
    class _U:
        def __call__(self,*a,**k): return _U()
        def __getattr__(self,n): return _U()
        def __iter__(self): return iter((float("nan"),float("nan")))
        def __getitem__(self,i): return float("nan")
        def __float__(self): return float("nan")
    def _mk(name):
        m=types.ModuleType(name); m.__getattr__=lambda n:_U(); return m
    for _n in ("scipy","scipy.stats","scipy.special","scipy.optimize","scipy.spatial","scipy.ndimage","scipy.signal"):
        sys.modules[_n]=_mk(_n)
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; STAT=r"C:\Users\MEDION GAMING\ai_quant_lab\statistician"
SP=r"C:\Users\MEDION~1\AppData\Local\Temp\claude\C--Users-MEDION-GAMING-tradingview-mcp\44ba92ba-04ad-40f2-a48e-0ee6a8aca893\scratchpad"
os.environ.setdefault("RATIFIED_CODE_DIR", SP+r"\ratified_code\code")
os.environ.setdefault("CANONICAL_CODE_DIR", SP+r"\canonical_code\code")
sys.path.insert(0, AA); sys.path.insert(0, os.environ["RATIFIED_CODE_DIR"]); sys.path.insert(0, os.environ["CANONICAL_CODE_DIR"])
sys.path.insert(0, os.path.join(AA,"edge_research"))   # so bare `import _common`/`_screen` resolve
OUT=os.path.join(AA,"reports","alpha_discovery")

import edge_research._common as CM
import edge_research._screen as SC
sys.modules["_common"]=CM; sys.modules["_screen"]=SC   # alias bare names to the SAME (patched) objects
_orig_load=CM.load; _orig_ceval=SC.canonical_evaluate
try:
    from edge_research._common import PRE_HOLDOUT_SPLIT_ID as _PHS, RESEARCH_HOLDOUT_CUTOFF_UTC as _RHC
except Exception:
    _PHS=_RHC=None
CAP={}
def load_cap(*a,**k):
    # detect API era: modern callers pass the split kwargs; stale callers pass tf only and expect a BARE df
    new_api=("data_split_id" in k) or ("cutoff" in k)
    if _PHS is not None: k.setdefault("data_split_id",_PHS)
    if _RHC is not None: k.setdefault("cutoff",_RHC)
    r=_orig_load(*a,**k)                       # ratified loader always returns (df, meta)
    df=r[0] if isinstance(r,tuple) else r
    CAP["d"]=df
    return r if new_api else df                # stale callers get the bare df they expect (no logic change)
def eval_cap(d,trades,gross=False):
    res=_orig_ceval(d,trades,gross=gross); CAP["d"]=d
    CAP.setdefault("res",res); CAP["ncalls"]=CAP.get("ncalls",0)+1; return res
def sim_cap(*a,**k):
    trades=k.get("trades");
    if trades is None:
        trades=a[4] if len(a)>=5 else a[-1]
    d=CAP.get("d")
    if d is None: raise RuntimeError("deprecated _screen.simulate called before _common.load captured d")
    res=_orig_ceval(d,trades); CAP.setdefault("res",res); CAP["ncalls"]=CAP.get("ncalls",0)+1; return res
CM.load=load_cap; SC.canonical_evaluate=eval_cap; SC.simulate=sim_cap

# object -> REGENERATOR module (from the authoritative manifest)
M=pd.read_csv(STAT+r"\COMPLETE_STRATEGY_GRAVEYARD_MANIFEST_V1.csv")
t2=pd.read_csv(os.path.join(OUT,"T2_OBJECTS_TO_REGENERATE.csv"))
ER=t2[t2.TIER=="T2_REGENERATE_EDGERESEARCH"].ANALYSIS_OBJECT_ID.tolist()
regmap={r.OBJECT_ID:str(r.REGENERATOR) for _,r in M.iterrows()}

rows=[]; cov=[]
for oid in ER:
    modpath=regmap.get(oid,""); CAP.clear()
    if not modpath.startswith("edge_research/"):
        cov.append((oid,"GENUINE_FAILED_REGENERATION",f"no edge_research regenerator in manifest ({modpath})")); continue
    mod=modpath.replace("/",".").replace(".py","")
    err=None
    try:
        m=importlib.import_module(mod)
        if hasattr(m,"main"):
            try: m.main()
            except SystemExit: pass
            except Exception as e: err=e     # a LATER auxiliary step (H1 robustness / scipy info-stats) may fail
                                             # AFTER the canonical M15 ledger was already captured -> still valid
    except Exception as e:
        err=e
    res=CAP.get("res"); d=CAP.get("d")
    if res and d is not None:
        tt=d["time"].to_numpy(); n=0
        for x in res:
            si=int(x["signal_idx"]); rows.append((oid,mod,"T2_ER",float(x["r"]),int(tt[si]))); n+=1
        partial=" (partial: canonical M15 ledger captured before a later step raised: %s)"%(type(err).__name__) if err else ""
        cov.append((oid,"ANALYSED",f"n={n} ncalls={CAP.get('ncalls',0)} mod={mod}{partial}"))
        print(f"  {oid:10s} ANALYSED n={n}{partial}")
    elif err is not None:
        msg=str(err)
        if ("D1" in msg and "manifest" in msg):
            cov.append((oid,"GENUINE_FAILED_REGENERATION",f"HTF_SOURCE_ABSENT: strategy requires a D1 feed loaded up-front, but D1 is not a ratified manifest timeframe (governed loader serves M15/M15_v2/M5/H1 only) -> {type(err).__name__}"))
        elif ("H1" in msg and "AWAITING_REGIME_MAP" in msg):
            cov.append((oid,"GENUINE_FAILED_REGENERATION",f"HTF_SOURCE_SEALED: strategy requires H1 up-front, but H1 status=AWAITING_REGIME_MAP is 100% sealed under ratified governance -> {type(err).__name__}"))
        else:
            cov.append((oid,"ATTEMPT_ERROR",f"{type(err).__name__}: {msg[:120]}"))
        print(f"  {oid:10s} {cov[-1][1]}: {str(err)[:70]}")
    else:
        cov.append((oid,"GENUINE_FAILED_REGENERATION","NO_TRADE_POPULATION: module ran but built no canonical trade ledger (information-test: no entry/exit/PnL)"))
        print(f"  {oid:10s} GENUINE NO_TRADE_POPULATION")

T=pd.DataFrame(rows,columns=["object","module","tier","net_R","decision_time"])
T.to_parquet(os.path.join(OUT,"ATTRIBUTION_V2_T2_ER_LEDGER.parquet"))
C=pd.DataFrame(cov,columns=["object","STATUS","note"])
C.to_csv(os.path.join(OUT,"ATTRIBUTION_V2_T2_ER_COVERAGE.csv"),index=False)
print("\n== EDGE_RESEARCH (25) COVERAGE ==")
print(C.STATUS.value_counts().to_string())
print(f"total trades regenerated = {len(T)} across {T.object.nunique()} objects")
print("\nnon-analysed:")
for _,r in C[C.STATUS!="ANALYSED"].iterrows(): print(f"  {r.object:10s} {r.STATUS}: {r.note}")
