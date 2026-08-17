# RED TEAM — TOWER CHAIN ATR · DELTA revalidation of ve_tower 0.5.1
### RT-TOWER-0009 · **TOWER_CHAIN_ATR_FAIL**
**Date:** 2026-08-17 · **Auditor:** Red Team · **Artefact:** `ve_tower 0.5.1`, wheel `ve_tower-0.5.1-py3-none-any.whl` SHA-256 `297aac5d5004b056c9785b8359be763cb7f9cf4056db865cd810040caa268807`, build `efc6e23`, delivery HEAD `73ec3c0`, wheel-commit `5f252dc`, sidecar `HANDOFF_MANIFEST-0.5.1.json`. Predecessor: **RT-TOWER-0008 N2_HANDOFF_PASS · N2_CHAIN_BINDING_PASS** (`d2f5a68`). AI Trader HOLD @ `ee92c8c`. **DELTA review — N2/chain-binding not reopened (no new binding defect).** No engine modified; SYNTHETIC data only; instrumentation observe-only; nothing changed outside `red_team/`.

# VERDICT — **TOWER_CHAIN_ATR_FAIL**
The primary defect **is fixed** — N4 now receives a real M15 1×ATR band (not `None`), reaches `confirmation_available=True`, and the chain reaches `ok_chain`. But a **single, reproducible provenance defect blocks PASS**: the **N3 `AtrProvenance.atr_value` does not equal the ATR value N3 actually consumed.** The chain reports `atr14(M15)[-1]` (the as_of bar), while `zone_map` internally consumes `atr14(M15)[i-1]` (= `[-2]`, its ratified non-lookahead band). §4 of the mandate makes this exact condition a FAIL ("*Dacă provenance spune o valoare diferită de ATR-ul efectiv consumat: TOWER_CHAIN_ATR_FAIL*"), and the PASS checklist item "*N3 provenance corespunde calculului său real*" is not satisfied.

---

## THE BLOCKING DEFECT (§4) — N3 provenance value ≠ ATR consumed by N3
Verified from the installed wheel by recovering the ATR `zone_map` actually froze into every N3 zone (`zone.band = 0.25 × a`, `a = atr14[i-1]` → `a = band/0.25`) and comparing to the reported `n3_atr_provenance.atr_value`. **Systematic across three independent synthetic M15 fixtures:**

| fixture | N3 provenance `atr_value` (reported) | ATR consumed by zone_map (`band/0.25`) | `atr14[-1]` | `atr14[-2]` | match |
|---|---|---|---|---|---|
| A (40 bars) | 3.071429 | 3.085714 | 3.071429 | 3.085714 | **NO** (Δ 0.014) |
| B (50 bars) | 4.072857 | 4.312857 | 4.072857 | 4.312857 | **NO** (Δ 0.240, ~6%) |
| C (60 bars) | 3.614286 | 3.628571 | 3.614286 | 3.628571 | **NO** (Δ 0.014) |

In every case the reported N3 value equals `atr14[-1]` and the consumed value equals `atr14[-2]`. `chain.py` computes `m15_atr = ms.atr14(...)` and records `n3_atr_provenance` with `value = m15_atr[-1]` (line 100/103–105), but `zone_map.build_zone_map` sets `i = n-1` and uses `a = atr14(...)[i-1]` (git `5888978`, line 191) for both `band` and `distance_atr`. `AtrProvenance.atr_value` is documented "*valoarea ATR folosită*" (the ATR value **used**) — so it claims to be the consumed value and is not. **VE's own test `test_atr_provenance_recorded_m15_for_n3_and_band_for_n4` only asserts N3 `timeframe`/`source_module`/`period`, never the value vs the consumed ATR — so the suite does not catch this.**

**Required fix (naming only):** N3's `AtrProvenance.atr_value` must report the ATR `zone_map` actually consumed — `atr14(M15)[i-1]` (= `m15_atr[-2]`) — matching zone_map's ratified `[i-1]` band convention. `zone_map` (ratified) must not change; the correction is in the chain's N3 provenance reporting. (N4's band/provenance are already consistent — see §5/§8.)

---

## EVERYTHING ELSE PASSES

**§1 Identity · PASS.** Wheel SHA `297aac5d…8807` exact; git-stored bytes == working wheel; build `efc6e23` ("compute ATR internally in the chain"), wheel-commit `5f252dc`, delivery HEAD `73ec3c0`. METADATA `0.5.1`. Sidecar describes the wheel exactly incl. the new `atr_source` block (`module=market_state`, `source_commit=a80d8a0…`, `function=atr14`, `period=14`, `true_range=max(h-l,|h-c_prev|,|l-c_prev|)`, `n3_timeframe=M15`, `n4_timeframe=M15_band_1xATR`), `state_delivery_commit=5f252dc` (authoritative), `vendored_source_identity=sha256:4c0dee…69e1c`, predecessor wheels 0.5.0/0.4.0. Clean-venv import from site-packages; `run_tower_chain` smoke-runs from the wheel. Complete pin present.

**§2 Delta · PASS (limited, no hidden semantic change).** DIFFER only `__init__.py`, `chain.py` (ATR compute), `contracts.py` (`AtrProvenance`, chain response ATR fields), `version.py`. **SAME (byte-identical):** all 13 vendored `_tower/*`, **`n2.py`/`n3.py`/`n4.py`**, `reason_codes.py`, `canonical.py`, `data_identity.py`, `fingerprint.py`, `_bootstrap.py`. N2/N3/N4 contracts unchanged. All 13 vendored blobs git-anchored to the installed wheel. ve_brain/N1/Router/EV/N6 absent → untouched.

**§3 Canonical ATR convention · PASS (git-verified).** `market_state.atr14@a80d8a0`: period 14, `TR=max(h-l,|h-c₋₁|,|l-c₋₁|)`, `rolling(14).mean()`, NaN warmup (first valid at index 14). `zone_confirmation@7f2694f`: `progress_reference="M15_band_1xATR"`, line 22 "*progres măsurat contra benzii M15 … NU ATR M5 — banda ratificată e 1×ATR M15*". **VE correctly followed the ratified semantics — N3 uses M15 ATR, N4 uses the M15 1×ATR band, NOT M5 ATR; this is not faulted.**

**§5 N4 ATR (the primary fix) · PASS.** Instrumented `run_tower_chain`: N4 receives `atr=[m15_last]×len(m5)` (a constant M15 band, len matches M5), **not `None`, not M5 ATR**; `m15_last == atr14(M15)[-1]`. On the valid fixture: `chain_status=ok_chain`, `n4.confirmation_available=True`, N4 reason `ok_confirmation` (no `atr_unavailable`). `confirmation_available` comes from the real `zone_confirmation`, not an orchestrator override.

**§6 No-lookahead / time alignment · PASS.** A future M15 bar (`time > as_of`) → `n3_unavailable` / `bars_not_closed_or_ordered` (refused, cannot change a prior decision). N4 uses the last causally-available M15 band even when M5 extends past the last M15 close (`n4 band == atr14(M15)[-1]`). Deterministic across repeated runs.

**§7 Fail-closed + ATR injection · PASS.** M15 insufficient for ATR14 → node unavailable (no fabricated ATR); M15 stale/unordered/NaN → refused; incompatible contract → refused. **ATR injection structurally impossible:** `atr`/`n3_atr`/`n4_atr`/`atr_value`/`atr_fingerprint`/`atr_available` all → `UnknownRequestFieldError` (parse) and `TypeError` (dataclass). Zero `atr=0`/`atr=None`-as-available, zero M5 fallback, zero caller-supplied ATR.

**§8 ATR provenance · PARTIAL.** N4 provenance value **equals** the consumed band (`atr14[-1]`), declares `M15_band_1xATR` (not M5), all fields present; `chain_fingerprint` independently recomputed (incl. ATR identity) → exact match; M15-bar change alters ATR + fingerprint. **N3 provenance value is the blocking defect above.**

**§9 Chain-binding regression (RT-TOWER-0007/0008) · PASS.** Caller `n2_fingerprint`/`bias_available` injection impossible (structural + `UnknownRequestFieldError`); N3 gets the real N2 `output_fingerprint`; substituted N3 → `CHAIN_IDENTITY_MISMATCH`; no default LONG; N2 emits no probability; `PRODUCTION_ENTRYPOINT=run_tower_chain`; `UNBOUND_DIRECT_API=(run_n2,run_n3,run_n4)`.

**§10 Tests & compatibility · PASS.** **73 tests, 0 failures** (matches VE). mypy `--strict` on the 12 top-level modules **clean (exit 0)** (independently re-run). Zero forbidden imports (no `market_intelligence`/`ai_trader`/`risk`/`execution`/`broker`). Upgrade 0.5.0→0.5.1 and rollback 0.5.1→0.5.0 reproducible (round-trip verified). AI Trader main venv untouched (separate sandbox tower venv used, restored to 0.5.0).

---

## CONSEQUENCE
**No PASS.** AI Trader stays HOLD @ `ee92c8c`; do **not** install 0.5.1; do **not** finalize the correlated run on this wheel. Fix the single N3 provenance-value defect (report the `[i-1]` ATR that `zone_map` consumes), add a committed test asserting `n3_atr_provenance.atr_value == the ATR zone_map used` (recoverable as `zone.band / band_mult`), re-deliver → Red Team re-runs this DELTA. **Standing constraints:** LIVE_SHADOW not started; authority not activated; broker DISABLED; Alpha `ALPHA_BLOCKED_CANONICAL_N1_HANDOFF`; CAND-T05 frozen. Red Team modified no engine, ran no real market data, changed nothing outside `red_team/`.
