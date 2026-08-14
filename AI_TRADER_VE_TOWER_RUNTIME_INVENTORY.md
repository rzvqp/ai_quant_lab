# AI Trader — Runtime Inventory for `ve_tower` (READ-ONLY, no install performed)

**Date**: 2026-08-14. **Context**: `ve_tower` wheel 0.1.0 was REJECTED (`TOWER_HANDOFF_FAIL`); VE is building
a new version. This report answers only "what environment would it land in" — no dependency was
installed, updated, or downgraded to produce it. All commands below were read-only or dry-run.

## 1-3. Interpreter, version, architecture

There is exactly **one** Python installation on this machine (`py -0p` lists a single entry):

```
C:\Users\MEDION GAMING\AppData\Local\Python\pythoncore-3.14-64\python.exe
Python 3.14.6 (tags/v3.14.6:c63aec6, Jun 10 2026, 10:26:10) [MSC v.1944 64 bit (AMD64)]
platform.machine() = AMD64
platform.platform() = Windows-11-10.0.26200-SP0
```

**This does not match either stated requirement.** `ve_brain` was declared Python 3.11; `ve_tower` is
declared Python 3.12. The actual runtime is **3.14.6** — newer than both. `ve_brain` already runs here
successfully (`verify_artifact_pin` PASSES against the real installed 0.1.3 wheel, prior mandate) because
it is stdlib-only and 3.11-targeted code is a subset of 3.14's language surface. **This is not proof
`ve_tower` will behave the same way** — if VE's build pins any 3.12-specific syntax, a compiled extension,
or a wheel tagged `cp312`-only, 3.14 will not satisfy it regardless of numpy/pandas presence (see §9).

**No Python 3.12 (or 3.11) interpreter exists anywhere on this machine.** Satisfying `ve_tower`'s stated
requirement literally would mean installing a second Python version — an environment change, not
performed here, and out of scope for a read-only inventory.

## 4. venv used by each of the 5 live processes

All five confirmed live, via `Get-CimInstance Win32_Process` against the actually-running PIDs:

| Process | Interpreter (from live command line) |
|---|---|
| `ai_trader.pdh_pdl_demo.entrypoint` | `...\ai_quant_lab-research-main\venv\Scripts\python.exe` |
| `ai_trader.multi_policy_live.entrypoint` | same |
| `ai_trader.live_observation.entrypoint` | same |
| `ai_trader.spread_collection.entrypoint` | same |
| `ai_trader.zone_observer.entrypoint` | same |

**All five share exactly one venv**: `C:\Users\MEDION GAMING\ai_quant_lab-research-main\venv`
(`pyvenv.cfg`: `home = ...pythoncore-3.14-64`, `include-system-site-packages = false`). There is no
per-process isolation today — a change to this venv's installed packages affects all five simultaneously,
and any of them restarting would re-import from the same `site-packages`.

## 5. numpy / pandas versions

Both are **already installed and already imported at live-process runtime today** (not merely present in
the venv unused — see §7):

```
numpy==2.5.1   ->  venv\Lib\site-packages\numpy\__init__.py
pandas==3.0.3  ->  venv\Lib\site-packages\pandas\__init__.py
```

Their presence and successful import under 3.14.6 in this exact venv is itself evidence that *these two
specific pinned versions* have working `cp314` wheels. It is not evidence about what `ve_tower` itself
needs from them (version floor/ceiling in `ve_tower`'s own metadata is unknown until VE ships it).

## 6. Full dependency lock (`pip freeze`, venv, verbatim)

```
ast_serialize==0.6.0
attrs==26.1.0
colorama==0.4.6
coverage==7.15.1
fastjsonschema==2.21.2
iniconfig==2.3.0
jsonschema==4.26.0
jsonschema-specifications==2025.9.1
librt==0.13.0
metatrader5==5.0.5735
mypy==2.3.0
mypy_extensions==1.1.0
numpy==2.5.1
packaging==26.2
pandas==3.0.3
pathspec==1.1.1
pluggy==1.6.0
Pygments==2.20.0
pytest==9.1.1
python-dateutil==2.9.0.post0
referencing==0.37.0
rpds-py==2026.6.3
scipy==1.18.0
six==1.17.0
types-jsonschema==4.26.0.20260518
typing_extensions==4.16.0
tzdata==2026.3
ve_brain @ file:///.../ve_brain-0.1.3-py3-none-any.whl
```

`ve_tower` is confirmed **not installed** (`pip show ve_tower` -> "Package(s) not found"); no stray wheel
file for it exists anywhere in the repo tree. `pip` itself is `26.1.2`.

## 7. Who imports numpy / pandas, and is it actually on the live path

Two different questions, kept separate:

- **Direct imports inside `ai_trader/` production code (excluding tests)**: exactly one file,
  `ai_trader/strategy_health/scoring.py` (`numpy`). **Confirmed unreachable from any of the 5 live
  entrypoints** (`grep` across all five entrypoint packages: zero references; it only appears in
  `live_observation`'s own `test_import_independence.py` as a name in that test's *forbidden*-import
  list). No `ai_trader/` file imports `pandas` directly.
- **Transitively, via the vendored bare-name modules the 5 processes already load** (see §8): the
  vendored `vendor/alpha_automation_detectors/code/market_state.py` **does `import numpy` at module
  level**, and it is bare-imported by 4 of the 5 live processes today (`structural_observer` — part of
  `live_observation` — `multi_policy_live`, `pdh_pdl_demo`, `spread_collection`). **This means numpy is
  already loaded into the running process image of 4 of the 5 live processes right now**, independent of
  anything to do with `ve_tower`. None of the vendored bare modules these 5 processes actually import
  (`market_structure`, `market_state`, `institutional_levels`, `imbalance_mechanics`, `order_flow`,
  `interactions`, `pdh_pdl_demo_engine`, `session_levels`, `order_block_void`) import `pandas`.
  `vendor/alpha_automation_demo_gate/code/*.py` (the *other*, non-`demo_gate_engine` half of that
  submodule — research/backtest scripts, e.g. `mstrat.py`, `campaign.py`) imports both heavily, but
  **none of those files are on the import path of any of the 5 live entrypoints** — confirmed by
  restricting the reachability check to `demo_gate_engine/` (what the live bridges actually import from),
  which contains neither.

**Net finding**: pandas has zero live-process exposure today; numpy has real, already-proven live-process
exposure through the structural detectors, independent of `ve_tower`.

## 8. Module-name collision surface — CONFIRMED, and larger than the three named examples

Five separate `vendor_bridge.py` files (one per live process, `structural_observer` counting as
`live_observation`'s) each do `sys.path.insert(0, ...)` against one or more **vendored, flat-script,
non-namespaced code directories**, then import bare top-level names from them — by design (documented
in each file: "the vendored modules use PLAIN, non-namespaced imports... this file is the ONE place that
performs the `sys.path` insertion"). Because it's `insert(0, ...)`, these directories take priority over
every other `sys.path` entry, including `site-packages`, for the lifetime of the process.

**Bare names already live in `sys.modules` today, confirmed by process**:

| Bare name | Loaded by |
|---|---|
| `market_structure` | all 5 |
| `market_state` | `live_observation`, `multi_policy_live`, `pdh_pdl_demo`, `spread_collection` (4/5) |
| `institutional_levels` | `multi_policy_live`, `pdh_pdl_demo`, `spread_collection`, `zone_observer` (4/5) |
| `imbalance_mechanics` | `live_observation`, `multi_policy_live`, `zone_observer` |
| `order_flow` | `live_observation`, `multi_policy_live`, `zone_observer` |
| `interactions` | `multi_policy_live` |
| `pdh_pdl_demo_engine` | `multi_policy_live`, `pdh_pdl_demo` (from a *different* vendored dir: `alpha_automation_demo_gate/demo_gate_engine`) |
| `session_levels` | `zone_observer` (from a *third* vendored location: `vendor/alpha_automation_session_levels`, a single plain-tracked file, not a submodule) |
| `order_block_void` | `zone_observer` |

**The CEO's own three named examples — `market_state`, `market_structure`, `order_flow` — are not
hypothetical collision risks: all three are already bare top-level module names, already imported, in
sys.path position 0, in the live process image today.** If `ve_tower`'s bootstrap tries to import a bare
module sharing any of these 9 names, the outcome depends on import order and which `sys.path` entry is
scanned first — this repo's own vendor directories currently win that race inside these 5 processes,
because their own `vendor_bridge.py` runs (and inserts at position 0) before any `ve_tower` code would.
**This is a disclosed gap, not an exhaustive check**: I was given 3 example names, not VE's full list of
13. I cannot confirm or rule out collisions against the other ~10 names without that list — flagging this
explicitly rather than implying completeness. Beyond the vendored `code/` directory (89 flat `.py` files
total, listed in the repo, e.g. `campaign.py`, `mstrat.py`, `s1.py`, `families.py`, `resample_ny.py` and
more) sits at `sys.path[0]` too whenever any of the 5 processes run, meaning *any* of those 89 bare names
is a live collision candidate, not only the ones actively imported by name in a `vendor_bridge.py` today.

## 9. What installing the `ve_tower` wheel would modify

Not testable today (0.1.0 rejected, no wheel currently on this machine to `pip install --dry-run`
against), but structurally, in this single shared venv:

- `site-packages/ve_tower*` (new) and its `.dist-info` — additive, isolated to that directory itself.
- **Risk, not fact**: if `ve_tower`'s own declared metadata pins numpy/pandas ranges that don't include
  the currently-installed `2.5.1`/`3.0.3`, `pip` would either upgrade/downgrade them in this **shared**
  venv (silently affecting all 5 live processes' already-proven numpy import path, §7) or fail to resolve.
  Cannot be confirmed until VE's wheel states its own requirement pins.
- **Risk, not fact**: if `ve_tower` is not a pure-Python (`py3-none-any`) wheel like `ve_brain`, but
  instead tagged for a specific CPython ABI (e.g. `cp312`), it is **not installable at all** in this
  venv (`cp314`) — `pip` would refuse with a "no matching distribution" error, cleanly, before touching
  anything. This is the scenario the stated "Python 3.12" requirement suggests is plausible.
- No installation step, by itself, touches any of the 5 running processes' in-memory state — they would
  only pick up a change on their next restart (none is scheduled or performed here).

## 10. Rollback

Nothing to roll back — nothing was installed. If a future install attempt is approved and needs
reverting: `pip uninstall ve_tower` (removes only its own `site-packages` entry) plus, only if §9's risk
materialized, `pip install numpy==2.5.1 pandas==3.0.3` to restore the exact pins this report captured as
the last-known-good, already-proven-live state. No process restart occurred, so no process-level rollback
is needed regardless.

---

## If the environment cannot safely host both — options for Red Team to compare (not decided here)

Per instruction, I am not choosing a final form. Candidate shapes, each satisfying "no change to the 5
processes before approval":

1. **Separate process/venv for `ve_tower`** (its own Python 3.12 venv, once that interpreter is actually
   installed — not done today) — `new_brain_bridge` talks to it over a local, versioned IPC contract
   (the CEO's own ask) rather than importing it in-process. Isolates the numpy/pandas pin *and* the
   bare-module-name collision surface (§8) completely — `ve_tower`'s own `sys.path` never touches this
   venv's.
2. **Same venv, same process, but ONLY if VE's wheel proves `py3-none-any` and its numpy/pandas pins
   overlap `2.5.1`/`3.0.3`** — cheapest, but inherits the full §8 collision surface directly (no
   isolation at all) and re-couples `ve_tower`'s dependency footprint to the same shared venv all 5 live
   processes already depend on.
3. **Hybrid**: same venv, but `ve_tower` imported only inside `new_brain_bridge`'s own process boundary
   (not the 5 legacy processes) — narrows blast radius to the one component already gated behind
   `NEW_BRAIN_DECISION_AUTHORITY` (never activated), at the cost of still sharing `site-packages` with
   the 5 legacy processes for numpy/pandas version pins.

All three assume, per the CEO's own list: a versioned contract, a health check, fail-closed on
unavailability (mirrors `fail_safe.safe_evaluate_bar`'s existing pattern), and the same `EventIdentity`
carried across the boundary regardless of which shape wins.

---

Cele cinci procese: neschimbate. Autoritatea: NEACTIVATA. `LIVE_SHADOW`: nu porneste. Nimic instalat,
actualizat sau retrogradat pentru acest raport.
