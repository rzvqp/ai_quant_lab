from __future__ import annotations

from pathlib import Path

from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.account_identity import (
    AccountIdentity,
    identities_match,
    load_persisted_account_identity,
    persist_account_identity,
    read_current_account_identity,
)
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.tests._fixtures import FakeMT5BridgeGateway


def test_reads_current_identity_fresh_every_call() -> None:
    gw = FakeMT5BridgeGateway()
    gw.account_info_result.login = 12345678
    identity = read_current_account_identity(gw, now=1000)
    assert identity is not None
    assert identity.login == 12345678
    assert identity.server == "FusionMarkets-Demo"
    assert identity.trade_mode == 0


def test_returns_none_when_account_info_unavailable() -> None:
    gw = FakeMT5BridgeGateway()
    gw.account_info_result = None
    assert read_current_account_identity(gw, now=1000) is None


def test_masked_never_exposes_full_login() -> None:
    identity = AccountIdentity(login=87654321, server="X-Demo", trade_mode=0, currency="EUR", recorded_at=0)
    masked = identity.masked()
    assert "87654321" not in json_str(masked)
    assert masked["login"] == "***21"


def json_str(d: dict[str, object]) -> str:
    import json

    return json.dumps(d)


def test_identities_match_requires_both_login_and_server() -> None:
    a = AccountIdentity(login=1, server="ServerA", trade_mode=0, currency="EUR", recorded_at=0)
    same = AccountIdentity(login=1, server="ServerA", trade_mode=0, currency="EUR", recorded_at=100)
    diff_login = AccountIdentity(login=2, server="ServerA", trade_mode=0, currency="EUR", recorded_at=0)
    diff_server = AccountIdentity(login=1, server="ServerB", trade_mode=0, currency="EUR", recorded_at=0)
    assert identities_match(a, same) is True
    assert identities_match(a, diff_login) is False
    assert identities_match(a, diff_server) is False


def test_persist_and_load_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "identity.json"
    identity = AccountIdentity(login=999, server="X-Demo", trade_mode=0, currency="USD", recorded_at=500)
    persist_account_identity(path, identity)
    loaded = load_persisted_account_identity(path)
    assert loaded == identity


def test_load_missing_file_returns_none(tmp_path: Path) -> None:
    assert load_persisted_account_identity(tmp_path / "nope.json") is None


def test_persist_overwrites_previous_identity_never_stale(tmp_path: Path) -> None:
    path = tmp_path / "identity.json"
    old = AccountIdentity(login=1, server="OldServer-Demo", trade_mode=0, currency="PLN", recorded_at=0)
    new = AccountIdentity(login=2, server="NewServer-Demo", trade_mode=0, currency="EUR", recorded_at=100)
    persist_account_identity(path, old)
    persist_account_identity(path, new)
    loaded = load_persisted_account_identity(path)
    assert loaded == new
    assert loaded != old
