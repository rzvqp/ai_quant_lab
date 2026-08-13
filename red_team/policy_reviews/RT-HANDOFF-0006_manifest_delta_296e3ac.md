# RED TEAM — DELTA VERIFICATION · artifact manifest `fbc0f20..296e3ac`
### RT-HANDOFF-0006 · ve_brain 8-field pin manifest · does NOT reopen VE_HANDOFF_PASS
**Date:** 2026-08-13 · **Auditor:** Red Team · **Scope:** ONLY `git diff fbc0f20..296e3ac`. The six PASS rounds are not re-run. Verdict rule unchanged: reproducible decision-path defect → FAIL; documentary limitation without path impact → CONDITIONAL; all pass → PASS; no invented defects; the delta is documentary by nature — verify it, do not inflate it. **No engine modified; no real data.**

# VERDICT — **ARTIFACT_MANIFEST_PASS**
- **validated_core_commit = `fbc0f20`** (the artifact Red Team granted VE_HANDOFF_PASS; RT-HANDOFF-0005 / `46c462c`)
- **artifact_delivery_commit = `296e3ac`** (this delivery — adds the manifest emitter only)

The delta is clean: it touches only manifest files + a read-only export + docs; the entire decision-path core is **byte-identical** to `fbc0f20`; the new export has no side effects and cannot modify the sealed catalog. **This does NOT reopen VE_HANDOFF_PASS** — runtime behavior is unchanged. One documentary follow-on, already identified by the CEO, remains (in-manifest identity separation); it is verified on delivery, below.

## 1 · SCOPE — limited to the allowed set (verified)
`git diff --name-only fbc0f20 296e3ac` = exactly five paths, all under `ve_brain/`, all additive (+123 / −0):
| file | category (CEO's allowed list) |
|---|---|
| `ve_brain/ve_brain/manifest.py` | manifest emitter |
| `ve_brain/ARTIFACT_MANIFEST.json` | manifest JSON |
| `ve_brain/tests/test_manifest.py` | manifest tests |
| `ve_brain/ve_brain/__init__.py` (+2) | public export needed for reading |
| `ve_brain/HANDOFF_GATES.md` | handoff documentation |
No file outside `ve_brain/`.

## 2 · CORE UNTOUCHED — byte-identical (VE's claim, independently confirmed)
`git diff fbc0f20 296e3ac` on each core module returns **0 lines**: `version.py`, `_canonical_catalog.py`, `ev_engine.py`, `n6.py`, `regime_routing.py`, `contracts.py`, `fingerprint.py`, `strategy_contract.py`, `_ev_core.py`, `reason_codes.py`, `testing.py` — **all 11 byte-identical.** N1, the Router, EV, N6, the catalog, and the seal are unchanged. The eight manifest values are read from these live (byte-identical) constants; the delivered JSON equals the live emitter (`artifact_manifest() == ARTIFACT_MANIFEST.json` → True), so the manifest corresponds **exactly** to release `fbc0f20`. Values: `package_version=0.1.3 · source_commit=fbc0f20 · catalog_version=ve-canonical-catalog-v1 · catalog_hash=37b95393df85dc2b · measurement_contract_version=canonical-evaluator-v2.7.66-A2 · n1_contract_version=n1-additive-raw-axes-v1 · router_version=router-v1 · ev_engine_version=ev-core@bdd15e5+ev-adapter-v1`.

## 3 · THE NEW EXPORT — six required properties
- **does NOT change catalog initialization** ✓ — after importing `ve_brain` (which now imports `manifest`), `n6._SEALED_CATALOG.sealed` is True and `range_fade` still resolves to RANGE (blocked). No change.
- **exposes NO modification API** ✓ — the only new public names are `artifact_manifest` (a pure read; `artifact_manifest() == artifact_manifest()`), `ARTIFACT_SOURCE_COMMIT` (constant), `MANIFEST_FIELDS` (constant tuple). No setter, no register, no reset.
- **does NOT change N1 / Router / EV / N6** ✓ — those modules are byte-identical (§2).
- **no import side effects** ✓ — `manifest.py` only imports constants and defines one function + two constants; nothing executes at import beyond constant binding; the sealed catalog is untouched.
- **cannot modify the sealed catalog** ✓ — no path in the delta writes `_SEALED_CATALOG` / `_APPROVED_CATALOG_*`; the emitter is read-only.
- **reports identities unambiguously** — ⚠ **partial (documentary):** the manifest currently carries a **single `source_commit=fbc0f20`** field, which reports the *validated core* but not the *delivery commit* (`296e3ac`). A consumer comparing their installed git SHA (`296e3ac`) to `source_commit` (`fbc0f20`) sees a mismatch it cannot disambiguate from the manifest alone. This is the exact point the CEO flagged.

## 4 · THE IDENTITY SEPARATION — pending (CEO-scheduled follow-on)
The CEO identified that "the manifest used one field for two identities" and is delivering a correction separating **`validated_core_commit`** from **`artifact_delivery_commit`** plus a **`manifest_schema_version`**. Verified: **this separation is NOT in `296e3ac`** (`296e3ac` is the tip; grep for those three fields → none; single `source_commit`). Per the CEO ("verify the separation when it delivers it"), it is a distinct future delivery. I record the two identities here (`validated_core_commit=fbc0f20`, `artifact_delivery_commit=296e3ac`) and will verify the in-manifest separation + `manifest_schema_version` when VE delivers it. I do **not** block this delta on it — the delta is clean and impact-free, and the separation is an explicitly-scheduled follow-on, not a defect discovered here (inflating it would violate "verify it, do not inflate it").

## 5 · TESTS
VE's suite at `296e3ac` = **29 passed** (26 prior + 3 manifest tests), verified in the correct nested layout. The manifest tests are sound: exactly eight non-None fields, values from live constants, and `delivered JSON == live emitter` (no manual reconstruction / placeholders). (A transient failure in my first run was a flattened-extraction path artifact — the JSON landed in the package dir instead of the dist dir; corrected, all 29 pass.)

## VERDICT — **ARTIFACT_MANIFEST_PASS** · validated_core_commit=`fbc0f20` · artifact_delivery_commit=`296e3ac`
The delta is limited to the manifest emitter, JSON, tests, a read-only export, and docs; the decision-path core is byte-identical to the PASS'd `fbc0f20`; the new export is pure, side-effect-free, and cannot modify the sealed catalog. **VE_HANDOFF_PASS is not reopened and stands.** The one open item — separating `validated_core_commit` / `artifact_delivery_commit` and adding `manifest_schema_version` inside the manifest — is a documentary, decision-path-irrelevant follow-on the CEO already scheduled; I verify it on delivery.

## HANDOFF → CEO / VE
1. **ARTIFACT_MANIFEST_PASS** for `296e3ac`; VE_HANDOFF_PASS (`fbc0f20`) intact.
2. **Pending (documentary):** verify the in-manifest identity separation (`validated_core_commit=fbc0f20` / `artifact_delivery_commit=296e3ac` / `manifest_schema_version`) when VE delivers it.

Red Team modified no engine, ran no data on the market, changed nothing outside `red_team/`.
