# RED TEAM — N2 HANDOFF · independent verification of ve_tower 0.4.0
### RT-TOWER-0007 · **N2_HANDOFF_CONDITIONAL · N2_CHAIN_BINDING_REQUIRED**
**Date:** 2026-08-17 · **Auditor:** Red Team · **Artefact:** `ve_tower 0.4.0`, wheel `ve_tower-0.4.0-py3-none-any.whl` SHA-256 `fe9f8b14a55152c590e67fa21531fd744cfa0f625689590c36f51c33629a8852`, build `bd49884`, delivery `1362765`, inventory verdict `a5241fb`, repo `ai_quant_lab-wp5b`@`discovery-mk-matrix-v1`. AI Trader stays HOLD @ `54cf26e`. **No engine modified; no real market data; all runs on SYNTHETIC data; nothing changed outside `red_team/`.**

# VERDICT — **N2_HANDOFF_CONDITIONAL · N2_CHAIN_BINDING_REQUIRED**
N2 itself is **correct on every axis** — artefact identity exact, `bias_h1` byte-identical to the confirmed source, `run_n2` reproduces the ratified semantics with a **real** `output_fingerprint`, no probability, default-LONG impossible, identities data-bound, missing data fail-closed, 53/53 tests pass, isolated with zero forbidden imports, upgrade/rollback reproducible. It satisfies **every PASS condition except one**: the N2→N3/N4 link is **not contractually bound**. `run_n3`/`run_n4` accept **any** caller-supplied `n2_fingerprint` string with no means to prove it belongs to a `run_n2` response, and there is **no versioned in-artefact orchestrator** that runs `run_n2` and feeds `output_fingerprint` internally. Per the CEO's decisive rule this is exactly **N2_CHAIN_BINDING_REQUIRED** — not FAIL (N2 has no reproducible defect), not PASS (the full chain is not verifiably bound).

---

## §1 — ARTEFACT IDENTITY · PASS
- **Wheel SHA-256 `fe9f8b14…8852` exact**, 80396 bytes. **git-stored bytes == working wheel** (`git cat-file -p 1362765:ve_tower/release/…whl | sha256sum` == expected) → physical handoff, **no rebuild**.
- Commits all resolve: build `bd49884` ("expose N2 producer, verdict B, no re-vendor/no rewrite"), delivery `1362765` (HEAD, "commit real 0.4.0 wheel, physical handoff"), inventory `a5241fb` ("git-only inventory + verdict B N2_EXISTS_BUT_IS_NOT_PACKAGED").
- **METADATA** `Version: 0.4.0`, `Requires-Python: >=3.12`, `numpy>=1.24`, `pandas>=2.0`. Install in clean venv → **import exclusively from site-packages** (`ve_tower.__file__` under site-packages, not `ai_quant_lab`); `run_n2` served from the wheel's `n2.py`, not the repo.
- **Complete pin (all present, none missing):** package `0.4.0` · wheel `fe9f8b14…8852` · build/source `bd49884` · delivery/state `1362765` · N2 validated source `bias_h1`@`850815f` · N2 vendored blob `1638c7dd…cfa9` · N2 contract `tower-n2-request-v1` · N2 code_version = `bias_h1.SCHEMA_VERSION` (runtime-read, not invented) · N3/N4 contracts `tower-n3/n4-request-v2` · N3/N4 code `level3-v2.0-reanchored`/`level4-v2.0-w3` · deps `numpy>=1.24`/`pandas>=2.0` · ve_brain target `0.1.3`.

## §2 — N2 PROVENANCE · PASS (git-verified, not VE's declaration)
- **`_tower/bias_h1.py` byte-identical to `code/bias_h1.py`@`850815f`**: `git rev-parse 850815f:code/bias_h1.py` = `git hash-object <wheel bias_h1>` = declared `1638c7dd…cfa9`; raw sha256 identical. **Not re-vendored, not rewritten.**
- **`run_n2` is a thin adapter** over the vendored producer: calls `bias_h1.compute_bias(...)` (the ratified function) and `level_output.is_available`; `n2_code_version = bias_h1.SCHEMA_VERSION` read at runtime.
- **All 13 vendored blobs byte-identical** to ratified heads (independent `git rev-parse` == wheel `git hash-object` == `VENDORED_BLOB_SHA1`, 13/13). N1 `regime_classifier`@`62c447e`, N3 `zone_map`@`5888978`, N4 `zone_confirmation`@`7f2694f` all untouched.
- **N3/N4 ratified modules + adapters unchanged vs 0.3.0**: `zone_map.py`, `zone_confirmation.py`, `n3.py`, `n4.py`, `canonical.py`, `data_identity.py`, `fingerprint.py`, `_bootstrap.py` all **byte-identical** between the 0.3.0 and 0.4.0 wheels; only `contracts.py` differs (additive N2 types). ve_brain / Router / EV / N6 are a separate artefact, absent from this wheel — untouched.

## §3 — N2 SEMANTICS · PASS
- Emits **deterministic directional H1 factors**: `structure_run_h1`, `displacement_h1`, `liquidity_above`, `momentum`→`Unavailable` (permanent, outside the required set). Direction enum `{LONG='long', SHORT='short', UNKNOWN='unknown'}`.
- **Emits NO** probability / `probability_inputs` / EV / TRADE / NO_TRADE / order / position — verified on the `N2Response` field set. `emits_probability=False` confirmed from `bias.schema_payload()`.
- `direction_share_long`/`direction_share_short` remain **descriptive**, not probability.

## §4 — RUNTIME CONTRACT · PASS
`N2Request`/`N2Response`, contract `tower-n2-request-v1`, **strict H1**, closed+ordered bars only, `market_event_id`/`configuration`-fingerprint preserved, `source_identity` mandatory, freshness (`max_staleness_s`→`DATA_STALE`), `data_identity`, `node_input_fingerprint`, `output_fingerprint`, `n2_code_version`, reason codes, `as_of_index`/`valid_until_index`. Missing/stale/incompatible → **`N2_UNAVAILABLE`** via specific reason codes, **no fabricated values**.

## §5 — ATTACKS (16/16, from the installed wheel, synthetic data) · PASS
1 same bars → same result+fingerprint ✓ · 2 one OHLC change → different `data_identity`+`output_fingerprint` ✓ · 3 future bar after `as_of` → `bars_not_closed_or_ordered` ✓ · 4 timeframe≠H1 → `invalid_timeframe` ✓ · 5 unordered → `bars_not_closed_or_ordered` ✓ · 6 incomplete → `schema_validation_failed`/`incomplete_window` ✓ · 7 stale → `data_stale` ✓ · 8 NaN → `non_finite_value` ✓ · 9 Inf → `non_finite_value` ✓ · 10 missing `source_identity` → `source_identity_missing` ✓ · 11 incompatible contract → `incompatible_contract` ✓ · 12 N1/regime axes unavailable → `cascade_regime_all_axes_unavailable` ✓ · 13 no direction → `unknown`, **never default LONG** (flat series → all factors `unknown`, `output_fingerprint=None` on full cascade) ✓ · 14 restart → identical `output_fingerprint` across two separate processes ✓ · 15 `output_fingerprint` bound to data+factors, **independent of caller `market_event_id`** (not a caller-string) ✓ · 16 no probability emitted ✓.

## §6 — N2 → N3/N4 BINDING · **THE DECISIVE POINT — NOT ENFORCED**
1. **`run_n2` produces a real `output_fingerprint`** = `canonical_hash({node_input_fingerprint, factors, direction_shares})` — bound to actual N2 output + data identity. ✓
2–8. **`run_n3`/`run_n4` accept ANY caller-supplied `n2_fingerprint` string.** Empirically, from the installed wheel, `run_n3` returns `market_map_available=True` for the real fp, for `"LONG"`, for `"placeholder-n2-fp"`, for `""`, and for a **fabricated 64-hex** (`"deadbeef"×8`). The string only alters `node_input_fingerprint` by inclusion; **`run_n3` has no `N2Response` to verify against**, performs **no N2-membership check**, and **never calls `run_n2`**. There is **no in-artefact orchestrator** composing N2→N3→N4 (`run_n2` is referenced only by `__init__` export). The cascade (`bias_available=False` → `cascade_level1_or_level2_unavailable`) is driven by a **caller-supplied boolean**, not by any proof that N2 actually ran. **N3/N4 remain contract v2.**
- **The artefact's own chain test confirms the gap, not the binding:** `test_full_n1_to_n4_uses_real_n2_fingerprint` feeds the real fp *and* `"some-other-n2-fp"`, asserting only that `node_input_fingerprint` **differs** — i.e. N3 *consumes* the fingerprint. **Both produce a valid market map.** It proves consumption, not rejection.
> **Conclusion (CEO's exact criterion):** since `run_n3`/`run_n4` accept any `n2_fingerprint` without any way to demonstrate it belongs to a `run_n2` response, **the link is a caller convention, not a contractual guarantee.** → **N2_CHAIN_BINDING_REQUIRED.**

## §7 — TEST MATRIX · PASS on count/quality; required negative test **ABSENT**
- **53 tests, 0 failures** (matches VE's 53). **15 N2 tests** in `test_n2.py` (matches). Fixture **N1→N2→N3→N4 exists and uses the real `run_n2` `output_fingerprint`** into `N3Request`. Tests exercise the real producers on synthetic data (no self-referential-constant-only tests).
- **Missing (reported explicitly, not assumed):** there is **NO negative test** asserting `run_n3`/`run_n4` **rejects** a modified/foreign `n2_fingerprint`. The lines that pass `"some-other-n2-fp"` assert only that the node fingerprint changes — a **consumption** check, not a **rejection** check. Under the v2 contract, such a rejection test **cannot** exist.
- **mypy strict on 11 modules: NOT independently re-run** (VE's static-typing claim; low-risk, not verified here).

## §8 — COMPATIBILITY & ROLLBACK · PASS
- **0.4.0 runs in the separate tower venv** (numpy 2.5.1 / pandas 3.0.3). **Upgrade 0.3.0→0.4.0 reproducible**; **rollback 0.4.0→0.3.0 reproducible** (`run_n2` gone at 0.3.0).
- **Old worker (0.3.0) has no `run_n2`** → cannot accidentally accept the new N2 contract; incompatible contract → fail-closed (`incompatible_contract`).
- **Zero forbidden imports** in the wheel: no `market_intelligence`, `risk_manager`, `execution_adapter`, `broker`, `order_send`, or `import ai_trader` (the single `market_intelligence` hit is a docstring stating it is NOT imported). No Risk/Execution/broker access. AI Trader's main venv untouched (this work used the separate sandbox venv; AI Trader stays HOLD @ `54cf26e`).

---

## REQUIRED REMEDIATION (CEO-permitted, either one) → to reach N2_HANDOFF_PASS
**(a)** N3/N4 **v3 contracts** that RECEIVE and VALIDATE the N2 response identity — `run_n3`/`run_n4` recompute/verify the `run_n2` `output_fingerprint` (or consume the full `N2Response`) and **reject a mismatch**; OR **(b)** a **versioned in-artefact orchestrator** that runs `run_n2` and passes `output_fingerprint` to N3/N4 internally, with **no caller substitution possible**. The mechanism must be **versioned, tested (including a negative substitution-rejection test), and re-verified** by Red Team before the final correlated path. **Not acceptable:** the promise that "AI Trader will pass the correct value."

## POST-PASS SEQUENCE (only after a future PASS)
AI Trader installs the verified wheel **only** in the tower venv → updates pin+handshake for 0.4.0 → worker runs real N2 → removes `bias_direction="LONG"` and any synthetic fingerprint → resumes from `54cf26e` → builds the single correlated path → runs the full regression → delivers `READY_FOR_LIVE_SHADOW_REVIEW_CANDIDATE_V2_CORRELATED`.

## STANDING CONSTRAINTS (reaffirmed)
LIVE_SHADOW **NEPORNIT**. Authority **NEACTIVATĂ**. Broker **DISABLED**. Alpha **`ALPHA_BLOCKED_CANONICAL_N1_HANDOFF`**; CAND-T05 frozen. Red Team modified no engine, ran no real market data, changed nothing outside `red_team/`.
