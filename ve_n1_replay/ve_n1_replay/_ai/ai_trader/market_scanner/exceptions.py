"""Exception hierarchy for the Market Scanner.

All exceptions the scanner may raise derive from :class:`MarketScannerError` so callers can catch
the whole family with one `except` clause. Per ``MARKET_SCANNER_ARCHITECTURE.md`` §14 and
``MARKET_SCANNER_API.md`` §5, the scanner never fabricates a malformed or unvalidated
``MarketContext`` — a build failure raises :class:`ContextValidationError` internally instead of
emitting a bad object, and the caller is expected to treat that as "skip this symbol this cycle".
"""

from __future__ import annotations


class MarketScannerError(Exception):
    """Base class for every Market Scanner exception."""


class ScannerNotConfiguredError(MarketScannerError):
    """Raised when an operation requires :meth:`MarketScanner.configure` to have run first."""


class UnknownSymbolError(MarketScannerError):
    """Raised when a symbol not passed to :meth:`MarketScanner.configure` is referenced."""

    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        super().__init__(f"unknown symbol: {symbol!r} (not configured)")


class UnknownTimeframeError(MarketScannerError, ValueError):
    """Raised when a timeframe code is not one of the recognised canonical timeframes
    (:data:`~ai_trader.market_scanner.timeframes.TIMEFRAME_SECONDS`). Subclasses ``ValueError`` as
    well as :class:`MarketScannerError` so callers may catch either hierarchy."""

    def __init__(self, timeframe: str) -> None:
        self.timeframe = timeframe
        super().__init__(f"unknown timeframe: {timeframe!r} (not a recognised canonical timeframe)")


class InvalidBarError(MarketScannerError, ValueError):
    """Raised when a :class:`~ai_trader.market_scanner.types.RawBar` is structurally invalid
    (non-finite OHLC, high < low, open/close outside [low, high], negative volume, etc.) — at
    construction time, since :class:`~ai_trader.market_scanner.types.RawBar` is a frozen, always-
    validated value object. The scanner never accepts a bar it cannot make sense of; it never
    fabricates or repairs bad input. Subclasses ``ValueError`` as well as
    :class:`MarketScannerError` so callers may catch either hierarchy."""


class InvalidTickError(MarketScannerError, ValueError):
    """Raised when a :class:`~ai_trader.market_scanner.types.RawTick` is structurally invalid
    (e.g. bid > ask, non-finite price, no price at all) — at construction time. Subclasses
    ``ValueError`` as well as :class:`MarketScannerError` so callers may catch either hierarchy."""


class ContextValidationError(MarketScannerError):
    """Raised internally when an assembled ``MarketContext`` fails JSON Schema or semantic
    validation. Per the fail-safe policy, this context is NEVER emitted; the caller sees this
    exception (from :meth:`MarketScanner.build_context`) and must skip the symbol for this cycle."""

    def __init__(self, symbol: str, as_of: int, errors: list[str]) -> None:
        self.symbol = symbol
        self.as_of = as_of
        self.errors = errors
        joined = "; ".join(errors) if errors else "unknown validation failure"
        super().__init__(f"MarketContext for {symbol!r}@{as_of} failed validation: {joined}")


class SchemaLoadError(MarketScannerError):
    """Raised when the ``MARKET_CONTEXT_SCHEMA.json`` file cannot be located or parsed."""
