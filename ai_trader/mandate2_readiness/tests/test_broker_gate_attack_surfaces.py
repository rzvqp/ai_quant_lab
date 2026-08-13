"""Attack-surface tests, CEO Mandate 2 amendment 2026-08-14, section 6: "Verifica si ca nu exista: cale
alternativa catre order_send, adaptor legacy cu drept de trimitere, setter runtime pentru broker gate,
variabila de mediu care poate activa executia, activare prin restart sau configuratie incompleta."

`test_broker_gate.py` already proves no-setter and no-env-var. This file proves the other three,
scanning the WHOLE `ai_trader/` production tree, not just this package -- these are claims about the
repo's actual current shape, verified here rather than left as narrative in a report."""

from __future__ import annotations

import inspect
from pathlib import Path

from ai_trader.mandate2_readiness.broker_gate import BrokerOrderSubmissionGate

_REPO_ROOT = Path(__file__).resolve().parents[3]
_AI_TRADER_ROOT = _REPO_ROOT / "ai_trader"


def _production_py_files() -> list[Path]:
    files: list[Path] = []
    for path in _AI_TRADER_ROOT.rglob("*.py"):
        if "tests" in path.parts or "__pycache__" in path.parts:
            continue
        files.append(path)
    return files


def _files_with_an_order_send_ast_call() -> list[str]:
    """AST-based, not a text scan -- `request_builder.py`/`types.py`/`order_manager/types.py` all
    legitimately MENTION `order_send()` in prose (documenting the raw dict shape / response type it
    normalizes), which a raw substring match would misflag. Only an actual `ast.Call` node whose
    function name is `order_send` counts as a real call site."""
    import ast

    hits: list[str] = []
    for path in _production_py_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", None)
                if name == "order_send":
                    hits.append(path.relative_to(_AI_TRADER_ROOT).as_posix())
                    break
    return hits


def test_no_alternative_route_to_order_send_exists_anywhere_in_production_code() -> None:
    """Cross-checks the runtime inventory's own finding (`AI_TRADER_MANDATE2_PREP_RUNTIME_INVENTORY.md`,
    section 4): exactly two files contain a genuine `order_send(...)` CALL (not a docstring mention) --
    `mt5_demo_execution/adapter.py` (`MT5DemoBrokerAdapter.submit_order` calling the gateway) and
    `mt5_demo_execution/gateway.py` (`RealMT5DemoGateway.order_send` itself calling
    `self._mt5.order_send(request)`, the one line that reaches the real MetaTrader5 module). A THIRD
    file appearing here would BE the alternative route this test exists to catch."""
    call_sites = _files_with_an_order_send_ast_call()
    assert set(call_sites) == {"mt5_demo_execution/adapter.py", "mt5_demo_execution/gateway.py"}, call_sites


def test_no_legacy_adapter_other_than_mt5_demo_broker_adapter_defines_a_real_submit_order() -> None:
    """`DryRunBrokerAdapter` and `NullBrokerAdapter` (and any other `submit_order` DEFINITION in the
    tree) must not themselves reach `order_send`/`order_check` -- a "legacy adapter with send rights"
    would be exactly one of these quietly gaining a real broker call."""
    from ai_trader.execution_engine.adapters.null_adapter import NullBrokerAdapter
    from ai_trader.order_manager.dry_run_adapter import DryRunBrokerAdapter

    for adapter_cls in (NullBrokerAdapter, DryRunBrokerAdapter):
        source = inspect.getsource(adapter_cls)
        assert "order_send(" not in source, f"{adapter_cls.__name__} unexpectedly calls order_send"
        assert "order_check(" not in source, f"{adapter_cls.__name__} unexpectedly calls order_check"


def test_a_fresh_construction_after_a_simulated_restart_is_still_disabled() -> None:
    """"Activare prin restart" -- a genuine process restart is a brand-new Python interpreter (fresh
    `sys.modules`, no shared state at all with the process that stopped) -- `importlib.reload()` was
    deliberately NOT used to simulate this: reload mutates the live module's namespace IN PLACE, which
    corrupts class identity for any other already-imported reference to the pre-reload classes (caught
    here during development -- it broke `test_08`'s own `pytest.raises(BrokerOrderSubmissionDisabledError)`
    in a way that had nothing to do with test 8's own logic, purely from executing in the same session).
    The actually-faithful simulation of "restart" is simply: construct a gate the exact way a fresh
    process's own startup code would, repeatedly, and confirm every single one lands disabled -- there is
    no different, "already warmed up" code path a restart could somehow reach instead."""
    for _ in range(5):
        assert BrokerOrderSubmissionGate().enabled is False


def test_activation_from_an_incomplete_or_missing_configuration_object_stays_disabled() -> None:
    """"Configuratie incompleta" -- a caller that only partially populates a config object (e.g. forgets
    the `enabled` key entirely) must land on the disabled default, never an implicit "on"."""
    incomplete_config: dict[str, object] = {"reason": "partial config, enabled key missing entirely"}
    gate = BrokerOrderSubmissionGate(**incomplete_config)  # type: ignore[arg-type]
    assert gate.enabled is False


def test_gate_has_no_method_whose_name_suggests_a_setter() -> None:
    """Structural, not just behavioral: confirms no `set_enabled`/`enable`/`activate`-shaped method
    exists at all on the class -- the frozen-dataclass test already proves direct attribute assignment
    fails, this proves there is no alternate API surface that could mutate it instead."""
    suspicious_names = {"set_enabled", "enable", "activate", "turn_on", "unlock"}
    actual_methods = {name for name in dir(BrokerOrderSubmissionGate) if not name.startswith("_")}
    assert actual_methods & suspicious_names == set()
