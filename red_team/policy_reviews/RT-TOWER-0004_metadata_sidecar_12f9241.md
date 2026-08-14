# RED TEAM — METADATA VERIFICATION · ve_tower 0.3.0 sidecar handoff manifest
### RT-TOWER-0004 · `HANDOFF_MANIFEST-0.3.0.json` @ `12f9241` (wheel + SHA unchanged)
**Date:** 2026-08-14 · **Auditor:** Red Team · **Task:** verify VE's sidecar manifest that completes AI Trader's pin (`vendored_source_identity` + N3/N4 contract versions were `None`). **No engine modified; no real data.** Verified against the wheel, commit `6daf2aa`, and independent `git rev-parse`.

# VERDICT — **TOWER_METADATA_PASS**
The sidecar manifest is fully verifiable. **The decisive requirement is met: `vendored_source_identity` is independently recomputable — I reproduced it from the 13 git blob identities using the manifest's own documented algorithm, exact match.** Every other field cross-checks against the wheel, `version.py` @ `6daf2aa`, and `git rev-parse`.

## Checks
- **`vendored_source_identity` — INDEPENDENTLY RECOMPUTED ✅.** The manifest documents the algorithm verbatim: *sort the 13 `(module_name, git_blob_sha1)` pairs by name; each line `"{name} {sha1}"`; join with `\n`; append a trailing `\n`; `"sha256:" + sha256(payload)`.* Recomputing it from the **git-verified** blobs → `sha256:4c0deecbec7afc74b1fc7f61898ad10e54b63d3b7c5cad63b80ee8c647a69e1c` == the manifest value. Not an emitter-only aggregate — reproducible by anyone with git.
- **13 blobs == `git rev-parse` ✅.** Every `vendored_blob_sha1[mod]` equals `git rev-parse <vendored_source_commit>:code/<mod>.py` (13/13), and all 13 are present in `version.py`'s `VENDORED_BLOB_SHA1`.
- **N3/N4 real constants ✅.** `n3_request/response = tower-n3-request-v2`, `n4_request/response = tower-n4-request-v2`, `n3_code_version = level3-v2.0-reanchored`, `n4_code_version = level4-v2.0-w3` — all match `version.py` @ `6daf2aa`. (The manifest correctly notes one contract version per node covers both request and response.)
- **Wheel + commit ✅.** `wheel_sha256 = 0c2581c068f3bd7d0c5beff1358af0aa906485d69ed74bf66c8a6d8d0c0120d2` matches the actual wheel; `ve_tower_package_version = 0.3.0`, `package_build_commit = 6daf2aa`, `state_delivery_commit = 0207ffa` (correctly kept separate).
- **`artifact_fingerprint = 1b33a5a853a0167e` ✅ (reproducible).** Its algorithm isn't restated in the manifest, but it equals ve_tower's own `fingerprint._artifact_identity()` = `sha256({ve_tower_version, vendored_source_commits})[:16]` (recomputed, exact match) — computable from the wheel's own code, not emitter-only; and it is **not** used in the pin/handshake verification (informational).

## EXACT VALUES → AI Trader (to close the pin)
```
vendored_source_identity = "sha256:4c0deecbec7afc74b1fc7f61898ad10e54b63d3b7c5cad63b80ee8c647a69e1c"
n3_contract_version      = "tower-n3-request-v2"
n4_contract_version      = "tower-n4-request-v2"
```
(already-verified pin, for completeness: `ve_tower_package_version=0.3.0`, `package_build_commit=6daf2aa`, `state_delivery_commit=0207ffa`, `wheel_sha256=0c2581c068f3bd7d0c5beff1358af0aa906485d69ed74bf66c8a6d8d0c0120d2`.)

## NEXT (after AI Trader closes the pin)
Re-execute the handshake tests against the completed pin: **fake server · old/stale-session worker · wrong wheel · wrong contract · other session · port occupied · cache bound + TTL · loopback enforcement.** AI Trader's remediation `88857ba` already appears to address my RT-TOWER-0003 findings (HMAC-SHA256 challenge-response → the fake-server defect I demonstrated can't produce a matching HMAC; per-response session binding → `STALE_SESSION`; bounded cache; OS-assigned port + occupied→startup-fail; mandatory loopback) — to be re-verified independently once the pin's three `None`s are filled with the values above. **If all pass → `TOWER_ARTIFACT_PASS · STAGED_INSTALL_AUTHORIZED`.** Alpha remains PAUSED; CAND-T05 frozen.

Red Team modified no engine, ran no data on the market, changed nothing outside `red_team/`.
