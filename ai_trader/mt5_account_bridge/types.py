"""Types owned by `mt5_account_bridge`."""

from __future__ import annotations


class AccountDataUnavailableError(Exception):
    """Raised by `MT5AccountBridge` whenever account/symbol data cannot be read completely -- never
    swallowed into a stale or fabricated value. Same rationale as `mt5_pnl_source.types.
    PortfolioDataUnavailableError`, applied to account/instrument data: a value that cannot currently be
    read must never be served as though it were the current one -- whether that means defaulting to 0.0
    (Risk Audit #1) or returning a cached copy from an earlier read (this package's own "no caching"
    constraint) -- both are the same permissive-default failure mode under a different name."""
