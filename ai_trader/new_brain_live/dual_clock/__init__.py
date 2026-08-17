"""M5 dual-clock (RT-TIME-0001 section B, CEO directive 2026-08-17). N1/Router stay M15-paced
(`ContextRefreshLoop`, `upstream_context.py`); N4/EV/N6/Risk/Shadow trigger independently on every
closed M5 bar (`M5DecisionLoop`). Every tower call goes through the real `run_tower_chain` via
`bridge.query_tower_chain` -- never `run_n2`/`run_n3`/`run_n4` directly, never a fabricated or reused
N2/N3 substitute.

Status at delivery: built and tested, NOT wired into `entrypoint.py`'s `main()`/`build_loop()` yet --
that wiring is the controlled cutover, gated on Red Team review, per the CEO's own explicit ordering.
`BROKER_ORDER_SUBMISSION` remains `DISABLED` throughout; nothing in this package can reach it otherwise
(AST-guard-proven, `tests/test_ast_guard.py`)."""
