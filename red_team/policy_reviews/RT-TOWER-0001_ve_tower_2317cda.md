# RED TEAM — TOWER HANDOFF · `ve_tower-0.1.0-py3-none-any.whl` (build `2317cda`)
### RT-TOWER-0001 · N3/N4 tower artifact · **TOWER_HANDOFF_FAIL**
**Date:** 2026-08-14 · **Auditor:** Red Team · **Task:** verify `ve_tower` (the N3/N4 tower, separate from ve_brain: numpy+pandas, Python ≥3.12) and emit TOWER_HANDOFF. **No engine modified; no real data.** Verified on the installed wheel (clean venv), imported source @`2317cda`, and independent comparison to the ratified commit blobs. Closed ve_brain attacks not re-run (this is a new artifact with vendored ratified code).

# VERDICT — **TOWER_HANDOFF_FAIL**
The wheel's identity, install, vendored code, bootstrap, contracts, no-lookahead, and unavailability handling are sound — but **point 13 is a reproducible, material integrity defect: data substitution is UNDETECTABLE.** The `timeframe` exclusion from `configuration_fingerprint` is correct for sharing N3/N4 event identity, but the CEO's six preconditions for accepting it are **all unmet**: N3/N4 do **not** validate their timeframe (M15/M5), and neither node persists its data identity (timeframe / bar range / last closed bar / dataset). So two events with the same `(market_event_id, symbol, as_of)` but **different bars** produce an **identical** fingerprint and carry **nothing** that distinguishes them. Per the CEO's own rule ("PASS only if there is no … undetectable data substitution") and the verdict rule (reproducible defect on the decision path → FAIL), this blocks handoff.

## POINT 13 (decisive) — undetectable data substitution · all 6 conditions fail, all 5 attacks succeed
Verified at source (`contracts.py`, `n3.py`, `n4.py`, `fingerprint.py`) and reproduced on the installed wheel:
| CEO condition | result |
|---|---|
| N3 validates it receives **M15** | ❌ `validate_n3_request` checks only `bool(req.timeframe)`; `run_n3` never compares to "M15" |
| N4 validates it receives **M5** | ❌ same — `bool(req.timeframe)` only |
| an N3 request labeled M5 is **refused** | ❌ **reproduced:** `run_n3(timeframe="M5")` → `ok_market_map`; `"BANANA"` → `ok_market_map` too |
| an N4 request labeled M15 is refused | ❌ same |
| each node **persists data identity** (timeframe · bar range · last closed bar · dataset) | ❌ `N3Response`/`N4Response` carry **none** of these (fields: contract/version/market_event_id/fingerprint/availability/map/levels/reason — no bar data) |
| a change of bars/range is **detectable** with identical `(id,symbol,as_of)` | ❌ **reproduced:** two different M15 bar-sets, same `(EVT1, XAU, 300)` → **identical `configuration_fingerprint`**, different maps, no distinguishing field |

**The five explicit attacks — all succeed:** (1) same id/symbol/as_of + other M15 bars → same fingerprint (undetectable); (2) same + other M5 bars → same fingerprint; (3) N3 fed M5 → **not refused**; (4) N4 fed M15 → not refused; (5) same event id reused for two datasets → same fingerprint. **`configuration_fingerprint = sha256(artifact ‖ market_event_id ‖ symbol ‖ as_of)`** binds to neither the bar data nor the timeframe.
**This is not "add timeframe to the shared fingerprint"** (that would break N3↔N4 shared identity, as the CEO notes). The fix is per-node: **N3 must validate `timeframe==M15` and N4 `timeframe==M5` (reject otherwise), and each response must persist its data identity** (timeframe + `time[0]`/`time[-1]` + last closed bar + a bar-data hash) so substitution is detectable while the shared event fingerprint stays constant.

## WHAT IS SOUND (so the FAIL is precise)
- **Point 1 — SHA-256 + size:** `e5457561604c2bd70ddca98a56b9a4c9ed8a60af95d9048237c768cef08b2db5`, 71,313 bytes — **exact match**; `SHA256SUMS.txt` agrees.
- **Point 2/3 — content + clean install:** wheel content == `2317cda`; fresh venv `pip install` pulls **numpy 2.5.2 + pandas 3.0.5**, `ve_tower 0.1.0`; N3 produces a real map and N4 a real confirmation from the wheel.
- **Point 4 — vendored integrity: CONTENT-identical to the ratified heads (documentary caveat).** 10/13 modules are **byte-identical** to their ratified commit blobs; 3 (`order_flow`, `imbalance_mechanics`, `institutional_levels`) differ **only in line endings** (CRLF vs LF) — **content-identical** after EOL normalization, benign for execution. `zone_map@5888978`, `zone_confirmation@7f2694f` confirmed (the CEO's corrected heads). **Caveat (documentary):** VE's claim "byte-identical to ratified heads" is inaccurate for those 3, and `test_vendored_modules_content_integrity` checks against the **self-baked** `VENDORED_CONTENT_SHA256` (the wheel's own hash), **not** the git commits — so it structurally cannot catch this; my independent commit-blob comparison did. No decision-path impact.
- **Point 5/14 — bootstrap fail-closed:** `TowerLoadCollisionError` on a foreign pre-occupied bare name (`test_collision_is_fail_closed` passes in-repo); a failed `exec_module` pops the half-loaded module. **Residual (point 14):** the loader registers **13 bare names** (`market_state`, `order_flow`, `session_levels`, `market_structure`, `regime_classifier`, `bias_h1`, …) in the **global** `sys.modules` — a contamination surface if the host process uses any of those top-level names (fail-closed if the host loads first; ve_tower shadows if it loads first). Needs the AI Trader-env check (point 12).
- **Point 6 — contracts:** runtime schema validation; `SUPPORTED_N3/N4_CONTRACTS`; `assert_n*_compatible` + `INCOMPATIBLE_CONTRACT` (an unsupported contract_version → `INCOMPATIBLE_CONTRACT`, fail-closed).
- **Point 8 — no lookahead:** a bar with `time > as_of` → `bars_not_closed_or_ordered` (reproduced). Strict-ascending, all `≤ as_of`.
- **Point 9 — explicit unavailability:** unordered bars / stale / incompatible / N1-N2 cascade / N3→N4 cascade / invalid side → **reason codes, never fabricated values** (reproduced several).
- **Point 10 — independence:** no `market_intelligence`/`ai_trader` import in the vendored modules (VE test passes in-repo); no duplicate MK detector (vendored, not re-implemented).
- **Point 11 — test matrix:** 6 foundation + 17 contract; negative fixtures present.

## OPEN / NOT FULLY VERIFIED
- **Point 12 — AI Trader runtime compatibility:** could **not** inspect (no AI Trader venv found under `ai_quant_lab-alpha-automation`). `ve_tower` `requires-python ≥3.12` + `numpy≥1.24, pandas≥2.0` — a **different profile** from `ve_brain` (Python 3.11, stdlib-only). The two artifacts **cannot share one interpreter**; the tower must run in a **separate 3.12+ process/venv**. Before any TOWER_HANDOFF_PASS: confirm the target env's Python and that installing numpy 2.5.2 / pandas 3.0.5 does **not** upgrade/downgrade deps used by the 5 live processes (dry-run, no live modification).
- **Point 15 — documentary reconciliation (for the next stage, non-blocking now):** AI Trader's "22/25 real" vs its four listed blocks (`04, 05, 09, 20b`) — the denominator needs the exact register and whether `20b` is a distinct subtest; plus the 6 skipped + 4 warnings in the full suite. Not anonymized before `PASS_FOR_LIVE_SHADOW`.

## VERDICT — **TOWER_HANDOFF_FAIL**
The tower computes correctly and fail-closes on lookahead/stale/incompatible/cascade — but it **cannot detect data substitution**: N3/N4 do not validate their timeframe and do not persist data identity, and the shared fingerprint ignores bar data. That is a reproducible integrity defect on the decision path and one of the CEO's explicit PASS-blockers. **Handoff is refused.**

## HANDOFF → CEO / VE
1. **Blocking (point 13):** N3 validate `timeframe==M15` / N4 `timeframe==M5` (reject otherwise with a distinct reason); persist per-node data identity (timeframe + bar range + last closed bar + a bar-data hash) so substitution is detectable while the shared event fingerprint stays constant. Re-run the five attacks.
2. **Documentary (point 4):** make `test_vendored_modules_content_integrity` compare against the **ratified git blobs**, not the self-baked hash; normalize EOL so "byte-identical" is literally true (or restate the claim as "content-identical").
3. **Point 12 (before PASS):** verify install in the real AI Trader env (separate 3.12+ venv), no dependency conflict with the 5 live processes; confirm no bare-name `sys.modules` collision with host top-level modules.
4. Re-submit; I re-run the five substitution attacks + points 12/14 + the full matrix. Alpha remains PAUSED; CAND-T05 frozen.

Red Team modified no engine, ran no data on the market, changed nothing outside `red_team/`.
