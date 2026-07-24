"""`MT5Gateway` -- the ONLY interface `mt5_adapter.py` is allowed to depend on, and (via `RealMT5Gateway`)
the ONLY file in this entire codebase that imports the real `MetaTrader5` package. This single choke
point is what makes the CEO's own mandatory static control provable BY CONSTRUCTION, not merely by grep:
`MT5Gateway` (the Protocol) and `RealMT5Gateway` (its concrete implementation) declare and wrap EXACTLY
the CEO's own authorized read-only operation list -- no order-submission or order-modification call is
merely unused here; no such method is defined by this module or capable of being exposed at all.

Unit tests never import this module's own `RealMT5Gateway` -- they inject a fake implementing the same
`MT5Gateway` Protocol (`tests/_fixtures.py::FakeMT5Gateway`), so the entire adapter/base/foundation test
suite runs with NO dependency on a real MT5 terminal or even the `MetaTrader5` package being importable.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class MT5Gateway(Protocol):
    """Exactly the CEO's own authorized read-only MT5 operation list. Every method mirrors the real
    `MetaTrader5` module's own function signature/return shape (namedtuples for `terminal_info`/
    `account_info`/`symbol_info`/`symbol_info_tick`, or `None` on failure -- `mt5.last_error()` reports
    why). No order/position-modifying method is declared here, full stop."""

    def initialize(
        self, path: str | None = None, login: int | None = None, password: str | None = None,
        server: str | None = None,
    ) -> bool: ...

    def shutdown(self) -> None: ...

    def terminal_info(self) -> Any | None: ...

    def account_info(self) -> Any | None: ...

    def symbols_get(self) -> tuple[Any, ...] | None: ...

    def symbol_info(self, symbol: str) -> Any | None: ...

    def symbol_select(self, symbol: str, enable: bool = True) -> bool: ...

    def symbol_info_tick(self, symbol: str) -> Any | None: ...

    def copy_rates_from(self, symbol: str, timeframe: int, date_from: int, count: int) -> Any | None: ...

    def copy_rates_range(self, symbol: str, timeframe: int, date_from: int, date_to: int) -> Any | None: ...

    def copy_ticks_from(self, symbol: str, date_from: int, count: int, flags: int) -> Any | None: ...

    def copy_ticks_range(self, symbol: str, date_from: int, date_to: int, flags: int) -> Any | None: ...

    def positions_get(self, symbol: str | None = None) -> tuple[Any, ...] | None: ...

    def orders_get(self, symbol: str | None = None) -> tuple[Any, ...] | None: ...

    def last_error(self) -> tuple[int, str]: ...


class RealMT5Gateway:
    """Thin, literal wrapper over the real `MetaTrader5` package -- every method is a one-line
    passthrough, nothing more. This is the ONLY file in this codebase importing `MetaTrader5`."""

    def __init__(self) -> None:
        import MetaTrader5 as mt5  # type: ignore[import-untyped]  # local import: this class is the
        # sole production consumer; MetaTrader5 ships no py.typed marker/stubs, hence the suppression.

        self._mt5 = mt5

    def initialize(
        self, path: str | None = None, login: int | None = None, password: str | None = None,
        server: str | None = None,
    ) -> bool:
        kwargs: dict[str, object] = {}
        if path is not None:
            kwargs["path"] = path
        if login is not None:
            kwargs["login"] = login
        if password is not None:
            kwargs["password"] = password
        if server is not None:
            kwargs["server"] = server
        return bool(self._mt5.initialize(**kwargs))

    def shutdown(self) -> None:
        self._mt5.shutdown()

    def terminal_info(self) -> Any | None:
        return self._mt5.terminal_info()

    def account_info(self) -> Any | None:
        return self._mt5.account_info()

    def symbols_get(self) -> tuple[Any, ...] | None:
        return self._mt5.symbols_get()  # type: ignore[no-any-return]

    def symbol_info(self, symbol: str) -> Any | None:
        return self._mt5.symbol_info(symbol)

    def symbol_select(self, symbol: str, enable: bool = True) -> bool:
        return bool(self._mt5.symbol_select(symbol, enable))

    def symbol_info_tick(self, symbol: str) -> Any | None:
        return self._mt5.symbol_info_tick(symbol)

    def copy_rates_from(self, symbol: str, timeframe: int, date_from: int, count: int) -> Any | None:
        return self._mt5.copy_rates_from(symbol, timeframe, date_from, count)

    def copy_rates_range(self, symbol: str, timeframe: int, date_from: int, date_to: int) -> Any | None:
        return self._mt5.copy_rates_range(symbol, timeframe, date_from, date_to)

    def copy_ticks_from(self, symbol: str, date_from: int, count: int, flags: int) -> Any | None:
        return self._mt5.copy_ticks_from(symbol, date_from, count, flags)

    def copy_ticks_range(self, symbol: str, date_from: int, date_to: int, flags: int) -> Any | None:
        return self._mt5.copy_ticks_range(symbol, date_from, date_to, flags)

    def positions_get(self, symbol: str | None = None) -> tuple[Any, ...] | None:
        return self._mt5.positions_get(symbol=symbol) if symbol is not None else self._mt5.positions_get()  # type: ignore[no-any-return]

    def orders_get(self, symbol: str | None = None) -> tuple[Any, ...] | None:
        return self._mt5.orders_get(symbol=symbol) if symbol is not None else self._mt5.orders_get()  # type: ignore[no-any-return]

    def last_error(self) -> tuple[int, str]:
        return self._mt5.last_error()  # type: ignore[no-any-return]
