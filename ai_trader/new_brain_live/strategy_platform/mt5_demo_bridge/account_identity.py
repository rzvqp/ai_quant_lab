"""Current-account identity detection and persistence (mandate `AI-TRADER-MT5-NEW-ACCOUNT-READINESS-001`
sections 1, 3, 10). The CURRENT MT5 terminal state is always authoritative -- this module never caches
account identity across calls; `read_current_account_identity` re-reads `account_info()`/`terminal_info()`
fresh every time, exactly like every other DEMO-verification call site in this package already does.

`AccountIdentity.login` is a real account number, not a secret, but is still never printed/logged in
full anywhere outside this module's own local, gitignored persistence file -- every caller-facing
representation goes through `masked()`."""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.gateway_ext import MT5BridgeGateway


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class AccountIdentity:
    login: int
    server: str
    trade_mode: int
    currency: str
    recorded_at: int

    def masked(self) -> dict[str, object]:
        login_str = str(self.login)
        masked_login = f"***{login_str[-2:]}" if len(login_str) > 2 else "***"
        return {
            "login": masked_login, "server": self.server, "trade_mode": self.trade_mode,
            "currency": self.currency, "recorded_at": self.recorded_at,
        }


def read_current_account_identity(gateway: MT5BridgeGateway, *, now: int) -> AccountIdentity | None:
    """`None` if the account cannot be mechanically read at all -- never fabricated, never falls back to
    a cached/previous value."""
    info = gateway.account_info()
    if info is None:
        return None
    login = getattr(info, "login", None)
    server = getattr(info, "server", None)
    trade_mode = getattr(info, "trade_mode", None)
    currency = getattr(info, "currency", None)
    if login is None or server is None or trade_mode is None or currency is None:
        return None
    return AccountIdentity(login=int(login), server=str(server), trade_mode=int(trade_mode), currency=str(currency), recorded_at=now)


def identities_match(a: AccountIdentity, b: AccountIdentity) -> bool:
    """Login + server together are the real identity -- trade_mode/currency can legitimately be re-read
    identically without the account itself having changed, but a genuinely different account could
    coincidentally share one of those two, never both."""
    return a.login == b.login and a.server == b.server


def persist_account_identity(path: Path, identity: AccountIdentity) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(dataclasses.asdict(identity)), encoding="utf-8")
    tmp.replace(path)


def load_persisted_account_identity(path: Path) -> AccountIdentity | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return AccountIdentity(**data)
