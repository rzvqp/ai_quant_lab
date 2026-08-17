# RED TEAM — TOWER CHAIN ATR · DELTA closure of ve_tower 0.5.2
### RT-TOWER-0010 · **TOWER_CHAIN_ATR_PASS**
**Date:** 2026-08-17 · **Auditor:** Red Team · **Artefact:** `ve_tower 0.5.2`, wheel `ve_tower-0.5.2-py3-none-any.whl` SHA-256 `1abcd60d5004…c28d8` (`1abcd60d6e541468a38e68a8b57e4200178585df37b489ff59b0ac99693c28d8`), build `b0cf2ea`, delivery HEAD `f7876ae`, wheel-commit `60bf71b`, sidecar `HANDOFF_MANIFEST-0.5.2.json`. Closes **RT-TOWER-0009 TOWER_CHAIN_ATR_FAIL** (`ecace9f`). AI Trader HOLD @ `ee92c8c`. **Provenance-only DELTA — N2/N4 not reopened.** No engine modified; SYNTHETIC data only; instrumentation observe-only; nothing changed outside `red_team/`.

# VERDICT — **TOWER_CHAIN_ATR_PASS**
The single RT-TOWER-0009 defect is **fixed exactly and only**. The N3 `AtrProvenance.atr_value` now reports the ATR `zone_map` actually consumes (`atr14(M15)[i-1]`), verified equal to `N3Level.band / 0.25` at full precision across three fixtures. The N3/N4 decision is byte-and-semantic identical to 0.5.1, the N4 fix and chain-binding guarantees are untouched, and a committed regression test now pins the old bug. All PASS conditions met.

---

## §1 — Artifact identity · PASS
Wheel SHA-256 `1abcd60d…c28d8` **exact**; **git-stored bytes == working wheel**. Build `b0cf2ea` ("correct N3 ATR provenance value, provenance-only, RT-TOWER-0009"); wheel-commit `60bf71b`; delivery HEAD `f7876ae`. METADATA `0.5.2`. Sidecar describes the wheel exactly: `state_delivery_commit=60bf71b`, updated `atr_source` block (`n3_consumed_index="i-1 (i=len(M15)-1)"`, `n4_band_index="-1"`, `n3_cross_check="atr_value == N3Level.band / 0.25"`), `vendored_source_identity=sha256:4c0dee…69e1c`, predecessor wheels 0.5.1/0.5.0. Clean-venv install → import only from site-packages.

## §2 — Delta provenance-only · PASS
Module diff 0.5.1→0.5.2: **DIFFER only** `chain.py` (ATR index derivation), `contracts.py` (`AtrProvenance` +`evaluation_index`/`consumed_atr_index`/`consumed_bar_timestamp`), `version.py`. **SAME (byte-identical):** all 13 vendored `_tower/*`, `n2.py`/`n3.py`/`n4.py`, `reason_codes.py`, `__init__.py`, `canonical.py`, `data_identity.py`, `fingerprint.py`, `_bootstrap.py`. **N2/N3/N4 contracts unchanged.** All 13 vendored blobs git-anchored to the installed wheel (13/13). ve_brain/N1/Router/EV/N6 absent → untouched. No economic change (the ATR value now reported is the one the ratified `zone_map` already used; no recomputation, no new detector).

## §3 — DECISIVE: N3 provenance == ATR consumed · PASS (full precision, 3 fixtures)
`chain.py` now derives `eval_i = n-1`, `n3_consumed_idx = eval_i-1`, `n3_val = atr14(M15)[n3_consumed_idx]` and records it. Verified from the installed wheel:

| fixture | i | `consumed_atr_index` | `atr_value` | `atr14[i-1]` | `N3Level.band/0.25` | `consumed_bar_ts` = `m15_time[i-1]` | old bug (`==atr14[-1]`) |
|---|---|---|---|---|---|---|---|
| A | 39 | 38 | 3.5700000000 | 3.5700000000 | 3.5700000000 | ✓ (T0+38·900) | **gone** (3.570 ≠ 3.588) |
| B | 49 | 48 | 4.3128571429 | 4.3128571429 | 4.3128571429 | ✓ | **gone** (4.313 ≠ 4.073) |
| C | 59 | 58 | 3.6285714286 | 3.6285714286 | 3.6285714286 | ✓ | **gone** (3.629 ≠ 3.614) |

`evaluation_index == i == len(M15)-1`; `consumed_atr_index == i-1`; `atr_value == atr14[i-1] == N3Level.band/0.25` (Δ < 1e-12); `consumed_bar_timestamp == m15_time[i-1]`. **Old-bug reproduction:** `atr_value` no longer equals `atr14[-1]` on any fixture. The committed test `test_n3_provenance_equals_atr_consumed_by_zone_map_three_fixtures` asserts `atr_value == lvl.band/0.25` across three amplitudes (line 181) — it would have failed on 0.5.1 (which reported `atr14[-1]`) and passes on 0.5.2; `test_provenance_indices_bound_to_ratified_rule` pins `evaluation_index=39`, `consumed_atr_index=38`, the timestamps.

## §4 — N4 unchanged · PASS
Instrumented: N4 ATR = `atr14(M15)[-1]` (`n4_band_idx=n-1`), `progress_reference="M15_band_1xATR"`, **not M5, not None**; valid fixture → `ok_chain`, `confirmation_available=True`, reason `ok_confirmation` (no `atr_unavailable`), produced by the real `zone_confirmation`. N4 `consumed_atr_index = n-1`. **The N3(`i-1`) vs N4(`i`) ATR difference is correct by construction** and now explicitly declared in both provenances.

## §5 — Decision identical 0.5.1 ↔ 0.5.2 · PASS
Same three fixtures, run under both installed wheels: **`chain_status`, `terminal_reason_code`, N2 factors, N3 market map (zone_id/anchor/band/rank), N3 levels, N4 `confirmation_available`+reason codes are byte-identical.** Only `n3_atr_provenance` (corrected value + new index fields) and the derived `chain_fingerprint` change — exactly what §5 permits, nothing else.

## §6 — Chain-binding regression · PASS
Caller injection of `n2_fingerprint`/`bias_available`/`atr`/`n3_atr`/`n4_atr`/`atr_value` → `UnknownRequestFieldError` (structural). N2→N3 and N3→N4 internal binding intact; substituted N3 → `chain_identity_mismatch`; no default LONG; N2 emits no probability; `PRODUCTION_ENTRYPOINT=run_tower_chain`; `UNBOUND_DIRECT_API=(run_n2,run_n3,run_n4)`; future M15 bar (>as_of) refused (no-lookahead); M15 stale → fail-closed; deterministic.

## §7 — Tests & compatibility · PASS
**76 tests, 0 failures** (matches VE; +3 vs 0.5.1: the provenance-consumed, index-binding, and N4/decision-regression tests). mypy `--strict` on the 12 top-level modules **clean (exit 0)** (re-run). Zero forbidden imports (no `market_intelligence`/`ai_trader`/`risk`/`execution`/`broker`). Upgrade 0.5.1→0.5.2 and rollback 0.5.2→0.5.1 reproducible (round-trip verified). AI Trader main venv untouched (separate sandbox tower venv).

---

## AUTHORIZATION (automatic on PASS)
AI Trader may now, in sequence: resume from `ee92c8c`; install **exactly** `ve_tower-0.5.2-py3-none-any.whl` (`1abcd60d…c28d8`) **only** in the tower venv; update the pin + handshake; finalize the single correlated run; run the full regression; deliver `READY_FOR_LIVE_SHADOW_REVIEW_CANDIDATE_V2_CORRELATED` — the next, separate review (RT-MANDATE2 track).

## STANDING CONSTRAINTS (reaffirmed)
**Do NOT start LIVE_SHADOW. Do NOT activate authority. Broker stays DISABLED. Alpha stays `ALPHA_BLOCKED_CANONICAL_N1_HANDOFF`. CAND-T05 frozen.** Red Team modified no engine, ran no real market data, changed nothing outside `red_team/`.
