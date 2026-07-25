from __future__ import annotations

from ai_trader.execution_engine.adapters.mt5_gateway import RealMT5Gateway
from ai_trader.mt5_demo_execution.gateway import MT5DemoGateway, RealMT5DemoGateway


def test_real_demo_gateway_is_a_real_gateway_subclass() -> None:
    assert issubclass(RealMT5DemoGateway, RealMT5Gateway)


def test_fake_demo_gateway_satisfies_the_protocol() -> None:
    from ai_trader.mt5_demo_execution.tests._fixtures import FakeMT5DemoGateway

    fake = FakeMT5DemoGateway()
    assert isinstance(fake, MT5DemoGateway)
