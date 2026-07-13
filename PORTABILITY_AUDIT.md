# PORTABILITY_AUDIT — 2026-07-13

Scope (CEO-approved): portability fix + reproducibility test ONLY. No methodology, no S1–S20 defs,
no thresholds, no holdout, no matched-null, no Portfolio Architect. Baseline never overwritten.

## 0. Checkpoint
- `ai_quant_lab/` was NOT a git repo → initialized one and committed the untouched state as rollback point.
- **Baseline commit (pre-fix):** `85857234bad5172634e9c2b603e873976a204470` (58 files).
- Added `.gitignore` (venv/, __pycache__/) so the venv and bytecode are not tracked.

## 1. Critical path fixed (class A — required by the S1–S20 campaign)
Only ONE module in the official campaign chain held a hardcoded Temp path:

`run_full_campaign.py → mstrat.py → s1.py → mtf.py`  — all data access goes through `mtf.D` (used as
`mstrat.M.D`, `s1.M.D`, and internally in `mtf.load_mtf`), always by string concatenation `D + r"\OANDA_XAUUSD_*.csv"`.

**`code/mtf.py` line 6** — before → after:
```
# before
D=r"C:\Users\MEDION~1\AppData\Local\Temp\claude\...\scratchpad\phaseb\alpha\data_market"
# after (portable, str-typed to preserve D+r"\..." concatenation; env override supported)
from pathlib import Path
import os as _os
D=_os.environ.get("AI_QUANT_DATA_DIR") or str(Path(__file__).resolve().parents[1]/"data"/"market")
```
- `parents[1]` because `mtf.py` lives in `<PROJECT_ROOT>/code/`.
- Kept as `str` (NOT a `Path`) — the code concatenates `D + r"\..."`; a `Path` would break it.
- Resolves at runtime to `C:\Users\MEDION GAMING\ai_quant_lab\data\market`.
- **cwd-independent** (derives from `__file__`, not the working directory).
- No new absolute Windows path hardcoded.

## 2. Secondary Temp paths — CLASSIFIED, class A only fixed
| file:line | constant | classification | action |
|---|---|---|---|
| `code/mtf.py:6` | `D` | **A — campaign** | **FIXED** |
| `code/resample_ny.py:4-5` | `D`,`N` | B — data rebuild only | deferred (debt) |
| `code/quality_and_resample.py:5` | `D` | B — data rebuild only | deferred (debt) |
| `code/run_prod.py:12` | `DATADIR` | B/D — standalone prod runner, not imported by campaign | deferred (debt) |
| `code/run_cycle.py:43` | inline | C — foundation GC only | deferred (debt) |
| `code/build_gc_bars.py:3-4` | `D2`,`OUTC` | C — foundation GC only (data2 not copied) | deferred (debt) |
| `foundation_gc/engine.py:12` | `OUT` | C — foundation GC only | deferred (debt) |
| `code/diag_mm.py:2`, `code/gapfind.py:2` | relative | D — diagnostics, relative paths (not Temp) | no change |

B/C/D are NOT on the official campaign path and were deliberately left unmodified per CEO scope.
Debt registered in PROJECT_AUDIT.md (D8) and NEXT_SESSION.md.

## 3. Data validation (runtime)
- Symbol XAUUSD; columns `time,open,high,low,close,volume`; `time` = int64 epoch seconds (UTC).
- Files opened at runtime are all under `...\ai_quant_lab\data\market\` (logged in ENGINE_RUNTIME_PATHS.json).
- Runtime bar counts: **M15=84152, H1=20832, H4=5450, D1=909**.
- **Discrepancy (documentation, benign):** docs say M15=84151. Actual file = 84152 (last line has no
  trailing newline → prior `wc -l` undercounted by one). Proven identical to the baseline data by the
  exact parquet reproduction AND by the sealed-holdout size (16831 = 84152−67321), which matches the
  original session's documented 16831. → docs off-by-one, not a data change. See REPRODUCIBILITY_AUDIT.

## 4. Environment
- No venv existed (original was in ephemeral Temp). Created `ai_quant_lab/venv` (Python 3.14.6).
- Installed `requirements.txt` (databento, pandas, numpy, sortedcontainers, zstandard) **+ pyarrow**
  (parquet engine — required to write/read FAMILY_RESULTS.parquet; missing from requirements.txt = debt D9).
- Installed versions are NEWER than the original run (pandas 3.0.3 / numpy 2.5.1 / pyarrow 25.0.0);
  reproduction was still bit-exact (see REPRODUCIBILITY_AUDIT).

## 5. Side-effect verification
- Disk changes after the whole run: `code/mtf.py` (fix), `.gitignore`, `results/reproduction_v2/*`,
  `venv/` (gitignored), `__pycache__/` (gitignored). Nothing written outside the project.
- Baseline `results/FAMILY_RESULTS.parquet` and `results/full.log` untouched (13:29 mtime preserved).
- No reads from Temp / System32 / old `tradingview-mcp` repo (0 such refs in the new log).
- Holdout: never opened (`research=50491 val=16830 holdout(SEALED)=16831`).

## Verdict: PORTABILITY FIX SUCCESSFUL — campaign runs autonomously from ai_quant_lab with no Temp dependency.
