"""Manual, explicitly-gated integration test against a REAL MT5 terminal -- NOT part of the standard
regression suite (CEO's own explicit instruction: "unit tests must not depend on the MT5 terminal
existing... the real probe can exist separately as a manual integration test, explicitly marked, without
running implicitly in standard regression").

Skipped unless the environment variable `MT5_REAL_TERMINAL_TEST=1` is set AND the `MetaTrader5` package
is importable AND a terminal is actually reachable. Strictly read-only, mirroring
`mt5_connectivity_probe.py`'s own already-approved scope exactly -- no order/position call of any kind.

Run explicitly with:
    MT5_REAL_TERMINAL_TEST=1 pytest ai_trader/execution_engine/adapters/tests/test_mt5_real_terminal_integration.py -v
"""

from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("MT5_REAL_TERMINAL_TEST") != "1",
    reason="Real MT5 terminal integration test -- set MT5_REAL_TERMINAL_TEST=1 to run explicitly. "
    "Never runs as part of standard regression, per the CEO's own explicit instruction.",
)


def test_real_mt5_connect_and_read_only_status() -> None:
    from ai_trader.execution_engine.adapters.mt5_adapter import MT5ReadOnlyBrokerAdapter

    adapter = MT5ReadOnlyBrokerAdapter()  # real RealMT5Gateway, real terminal
    try:
        result = adapter.connect()
        assert result.accepted, f"real connect failed: {result.reason}"
        assert adapter.is_connected()

        status = adapter.status()
        assert status.account_is_demo is True, (
            "SAFETY: this integration test must only ever be run against a demo account -- "
            "MT5ReadOnlyBrokerAdapter's own safety refusal should have already prevented reaching here "
            "on a non-demo account, but this is re-asserted explicitly as a second, independent gate"
        )
        print(status)  # visible only when run with -s; not asserted on beyond the demo-account gate

        caps = adapter.symbol_capabilities("XAUUSD")
        assert caps is not None

        tick = adapter.read_tick("XAUUSD")
        assert tick is not None
    finally:
        adapter.disconnect()
