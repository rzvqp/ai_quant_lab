# N1_REPLAY_VERSION_DRIFT_AUDIT

**Date**: 2026-08-21
**Scope**: `.alpha_n1_venv` currently holds `ve_n1_replay 0.2.0`; AI Trader's own pin
(`ai_trader/new_brain_live/n1_incremental/artifact_pin.py`) still names `0.1.1` (SHA-256
`2cff7e7be1f9401c10753f751a1189a512f5be39946dfada4260b9c5e1cd29ab`, delivery `e118c33`, RT PASS
`6230ee5`). Surfaced by `pytest` (`test_artifact_pin_matches_ceo_authorized_values`) failing closed
during the New Brain Architecture mandate's console-window regression (2026-08-21).

**STOP — later ratification of `0.2.0` exists, but explicitly does NOT cover AI Trader's use. This
audit does not change the environment; it reports evidence per the CEO's own directive.**

## 1. Provenance of the installed `0.2.0`

Read from `.alpha_n1_venv`'s own pip metadata (`ve_n1_replay-0.2.0.dist-info`), never guessed:

| field | value |
|---|---|
| installed | 2026-08-18 11:00:01 (local, UTC+3) |
| installer | `pip` |
| source | `file:///C:/Users/MEDION GAMING/ai_quant_lab-wp5b/ve_n1_replay/release/ve_n1_replay-0.2.0-py3-none-any.whl` |
| pip-recorded SHA-256 | `04b96a8b78b2d09bd8b54bd8044058282c6ab24bf2ac0f2aaec6c1f7a278786f` |
| build / delivery commit | `1dc355b` / `3577026` (`ai_quant_lab-wp5b`) |

## 2. Later ratification found — `RT-RANGE-0002`

`ai_quant_lab-wp5b` commit `898e1b9`: **`RT-RANGE-0002: ve_n1_replay 0.2.0 RANGE_STATE_HANDOFF_PASS`**
(2026-08-18 10:48:59, ~11 minutes before the install above — the install is this PASS being acted on).

Independently re-verified by Red Team (31/31 adversarial checks, 77 installed-wheel tests, mypy
`--strict`), re-hashed wheel matches exactly (`04b96a8b78b2…786f`, 82884 bytes — identical to what's
now installed). Decisive findings from that report:

- **§2, N1 parity (independently re-verified, not just claimed)**: 0.2.0's N1 output is
  **byte-identical** to 0.1.1 on trend_up/trend_down/uncertain/osc fixtures (`output_fingerprint`,
  `eval_identity_fp`, full digest all identical); evaluation-identity versions stay `v1`. All 15
  vendored `ai_trader` modules, all 5 detector modules, `_bootstrap.py`, and `incremental.py` are
  byte-identical to 0.1.1. The **only** new files are `range_engine.py`/`range_state.py` (additive);
  only `__init__.py`/`version.py` differ (surface + version metadata).
- **§10, LIVE_SHADOW**: explicitly confirms, at audit time, `.alpha_n1_venv` still held `0.1.1` ("0.2.0
  not yet installed — correct, this PASS had not been acted on") and the live AI Trader process
  (PIDs 22592/25992, HEAD `255eee6`) was the **old** runtime, predating 0.2.0 entirely.
- **Explicit scope, stated twice, unambiguously**: *"This PASS authorizes ONLY: Alpha may install 0.2.0
  in the Alpha environment and prepare the next combined discovery wave... It does NOT authorize
  AI-Trader deployment, final regression, cutover, set_authority, broker activation, or order_send."*

**No `RT-N1-000x` pass (the AI-Trader-integration track) exists beyond `RT-N1-0003`
(`f33e739`, integration review of AI Trader @ `9f0c13c`, which itself still names the `0.1.1` pin).**
`RT-RANGE-0002` is in the separate RANGE-research track (Alpha/Statistician/VE), scoped explicitly to
Alpha's own environment use, not to AI Trader's runtime.

## 3. The actual conflict

`.alpha_n1_venv` is a **shared** environment: Alpha Discovery's own research processes read/write it
under `RT-RANGE-0002`'s authorization (0.2.0, Alpha-env-only); AI Trader's isolated `worker_script.py`
subprocess (via `N1IncrementalClient`) also reads whatever is installed there, under the separate
`RT-N1-0002`/`RT-N1-0003` authorization (0.1.1 only). There is no version isolation between these two
legitimately-but-differently-scoped consumers of one venv — Alpha's authorized upgrade silently changed
what AI Trader's subprocess call would see.

## 4. Does AI Trader's runtime actually touch anything 0.2.0-specific?

No. `ai_trader/new_brain_live/n1_incremental/worker_script.py` imports only `n1r.Bar`,
`n1r.N1IncrementalReplayEngine`, `n1r.IncompatibleSnapshotError`, `n1r.N1ReplayError`,
`n1r.StaleStateError`, and version-identity attributes — the N1-only surface RT-RANGE-0002 §2
independently confirmed is byte-identical between 0.1.1 and 0.2.0. Nothing in `worker_script.py`
references `range_engine`/`range_state`/`RangeConfig`/any RANGE_STATE symbol. Mechanically, no
functional incompatibility is evident — but this is a source-level/logical inference, not itself an
AI-Trader-track Red Team re-validation of `N1IncrementalReplayEngine`'s runtime behavior specifically
under 0.2.0.

## 5. Restoration path (verified available, NOT executed)

The exact pinned 0.1.1 wheel is still physically present and hash-verified:
`ai_quant_lab-wp5b/ve_n1_replay/release/ve_n1_replay-0.1.1-py3-none-any.whl` →
`sha256 = 2cff7e7be1f9401c10753f751a1189a512f5be39946dfada4260b9c5e1cd29ab` — **matches the repository
pin exactly**. Restoration is mechanically possible whenever authorized.

## 6. Open question for the CEO

`RT-RANGE-0002` is later ratification of `0.2.0` — but it explicitly authorizes only Alpha's own
environment use and explicitly does NOT authorize AI-Trader deployment. Per the CEO's own directive
("if a later ratification exists, STOP and report before changing the environment"), this audit stops
here rather than deciding unilaterally whether "N1 byte-identical, Alpha-env-authorized" is sufficient
to also trust AI Trader's read of the same shared venv, or whether the repository pin must be
mechanically restored to 0.1.1 (or the two consumers given separate, non-shared environments) before
the New Brain mandate's N1-incremental path may be considered validated again.
