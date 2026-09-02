"""P007 Q4 episode reconstruction from the FROZEN detector + ledger labels. No model fitting yet."""
import sys, os, re, io, json, csv
import numpy as np, pandas as pd
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
RM = r"C:\Users\MEDION GAMING\ai_quant_lab-research-main"
sys.path.insert(0, RM); os.chdir(RM)
from ai_trader.csv_causal_replay.sealed_reader import SealedReader, SealedReaderConfig
from ai_trader.csv_causal_replay.tests.test_p007_detector import XAUUSD_M15_SYMBOL, M15_BAR_INTERVAL_SECONDS, Q4_START_TS
from ai_trader.csv_causal_replay.p007_detector import replay_p007_detection

from pathlib import Path
FIX = Path(os.path.join(RM, "ai_trader", "csv_causal_replay", "fixtures", "data", "Q4_SEALED_1_5932.csv"))
cfg = SealedReaderConfig(symbol=XAUUSD_M15_SYMBOL, bar_interval_seconds=M15_BAR_INTERVAL_SECONDS,
                         q4_start_ts=Q4_START_TS, max_q4_bar_index=5932)
with SealedReader(FIX, config=cfg) as _r:
    rows = list(_r.iter_rows())
q4 = [r for r in rows if getattr(r, "q4_bar_index", None) is not None]
print(f"  sealed reader: {len(rows)} rows, {len(q4)} Q4 bars (warm-up {len(rows)-len(q4)})")
ev = replay_p007_detection(iter(rows))
trg = [e for e in ev if e.event_type == "TRIGGER"]
res = [e for e in ev if e.event_type == "RESOLUTION"]
print(f"  frozen detector: {len(trg)} TRIGGERs, {len(res)} RESOLUTIONs")

# ledger trigger bars
s = io.open(os.path.join(RM, "docs", "trader_apprenticeship", "AI_TRADER_Q4_PATTERN_LEDGER.md"), encoding="utf-8").read()
blocks = re.split(r"\n## (Q4-P007-\d{3})\n", s)
ents = [(blocks[i], blocks[i + 1]) for i in range(1, len(blocks), 2)]
lg = []
for eid, body in ents:
    m = re.search(r"STATUS\s+(SUPPORT|REJECTED)", body) or re.search(r"CLASSIFICATION\s*:?\s*\*{0,2}(SUPPORT|REJECTED)", body) or re.search(r"\b(SUPPORT|REJECTED)\b", body)
    tb = re.search(r"TRIGGER_BAR\s+(\d+)", body)
    rb = re.search(r"RESOLUTION_BAR\s+(\d+)", body)
    tb2 = re.search(r"[Bb]ar (\d{2,5})", body)
    lg.append(dict(id=eid, label=m.group(1) if m else None,
                   trigger_bar=int(tb.group(1)) if tb else (int(tb2.group(1)) if tb2 else None),
                   resolution_bar=int(rb.group(1)) if rb else None))
L = pd.DataFrame(lg)
print(f"\n  ledger: {len(L)} entries, labels {L.label.value_counts().to_dict()}")
print(f"  explicit TRIGGER_BAR field present : {int(L.trigger_bar.notna().sum())}/{len(L)}")
print(f"  explicit RESOLUTION_BAR field      : {int(L.resolution_bar.notna().sum())}/{len(L)}")

tb_det = np.array([e.bar_index for e in trg])
tb_led = L.trigger_bar.dropna().astype(int).to_numpy()
inter = np.intersect1d(tb_det, tb_led)
print(f"\n  detector trigger bars matching a ledger trigger bar EXACTLY : {len(inter)} of {len(tb_led)} ledger / {len(tb_det)} detector")
# nearest-match tolerance
near = sum(1 for b in tb_led if np.min(np.abs(tb_det - b)) <= 2)
print(f"  ledger trigger bars within +/-2 bars of a detector trigger  : {near} of {len(tb_led)}")
json.dump(dict(n_trg=len(trg), n_res=len(res), n_ledger=len(L),
               exact=int(len(inter)), near=int(near)), open(r"C:\Users\MEDION~1\AppData\Local\Temp\p7\build.json", "w"))
L.to_csv(r"C:\Users\MEDION~1\AppData\Local\Temp\p7\ledger.csv", index=False)
pd.DataFrame([dict(bar=e.bar_index, ts=e.bar_ts_open, close=e.close, ema=e.h1_ema50, kind=e.event_type)
              for e in ev]).to_csv(r"C:\Users\MEDION~1\AppData\Local\Temp\p7\events.csv", index=False)
