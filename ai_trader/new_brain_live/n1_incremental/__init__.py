"""N1 incremental hydration -- CEO directive 2026-08-18, following Red Team `RT-N1-0002:
N1_INCREMENTAL_PASS` (`6230ee5`) for `ve_n1_replay` 0.1.1 (delivery `e118c33`, wheel SHA-256
`2cff7e7be1f9401c10753f751a1189a512f5be39946dfada4260b9c5e1cd29ab`). Replaces `n1_hydration`'s bounded
460-bar snapshot (which `test_unbounded_structure_dependency_blocker.py` proved loses real, still-active
structure/direction on restart) with the Red-Team-cleared incremental engine, which persists the full
unbounded swing/break state.

**Isolation, not installation.** `ve_n1_replay` is never imported into the main AI Trader process or
venv -- it vendors its own copy of `ai_trader.n1_replay` under a bare namespace package, which would
collide with THIS repo's own real `ai_trader.n1_replay` if ever imported in the same interpreter
(confirmed empirically: `ai_trader` is not a real distribution in the isolated venv's `pip list`, it is
materialized as a side effect of `import ve_n1_replay` itself). `worker_script.py` is the ONLY file in
this package meant to run under the isolated venv's own interpreter, launched as a genuinely separate OS
process every call (`client.py`'s own `subprocess.run`, never an in-process import) -- so even if the two
`ai_trader.n1_replay` copies differ, they are never resident in the same `sys.modules` table at once.

**Environment split (CEO decision, AI Trader New Brain Architecture mandate, 2026-08-21,
`N1_ALPHA_AI_TRADER_RUNTIME_ISOLATION_COMPLETE`)**: this package's isolated venv is `.ai_trader_n1_venv`
-- AI-Trader-exclusive, holding only the pinned `0.1.1` artifact, never `.alpha_n1_venv` (Alpha
Discovery's own, separately-authorized environment, which legitimately runs `ve_n1_replay 0.2.0` under
`RT-RANGE-0002`). The two environments were originally the same physical venv, which caused a real,
audited version-drift incident (`N1_REPLAY_VERSION_DRIFT_AUDIT.md`) when Alpha's own authorized upgrade
silently changed what this package's subprocess call would see -- see `artifact_pin.py`'s own docstring
for the full identity/authorization story.

Status at delivery: built and tested against the real installed 0.1.1 artifact (not a mock), NOT wired
into `entrypoint.py`'s `main()`/`build_loop()` -- that wiring is the controlled cutover, gated on Red
Team's own integration review of THIS package, separate from the N1_INCREMENTAL_PASS review of the
artifact itself. `BROKER_ORDER_SUBMISSION` remains `DISABLED`; nothing here has a code path to a
decision, a risk gate, or a broker call -- same structural guarantee `n1_hydration` and `dual_clock`
already established, verified the same way (see `tests/test_import_independence.py` in this package)."""
