"""``MarketScanner`` — the public façade implementing ``MARKET_SCANNER_API.md`` exactly.

This is the ONLY class the AI Trader orchestrator (and the Data Source Adapter) talks to. It wires
together the Bar Store, Session/Calendar/Indicator engines, Timeframe Sync, Data Quality, and
Schema Validation into the documented, versioned, lookahead-safe ``MarketContext`` output. It is a
pure observer/normalizer: no signals, no scoring, no orders, no access to Research Lab artifacts
(``MARKET_SCANNER_ARCHITECTURE.md`` §14).
"""

from __future__ import annotations

import logging
from typing import Any

from ai_trader.market_scanner import data_quality
from ai_trader.market_scanner.bar_store import SymbolBarStore
from ai_trader.market_scanner.clock import ClockController, SymbolTimeframeClose
from ai_trader.market_scanner.config import DEFAULT_CONTEXT_TIMEFRAMES, ScannerConfig
from ai_trader.market_scanner.exceptions import (
    ContextValidationError,
    ScannerNotConfiguredError,
    UnknownSymbolError,
)
from ai_trader.market_scanner.features import M15_FEATURE_NAMES, FeatureProvider
from ai_trader.market_scanner.schema_validation import validate_context
from ai_trader.market_scanner.session import session_name_for_hour
from ai_trader.market_scanner.timeframe_sync import (
    build_timeframe_context,
    latest_lookahead_safe_bar,
    select_lookahead_safe_bars,
)
from ai_trader.market_scanner.timeframes import timeframe_seconds
from ai_trader.market_scanner.types import (
    CalendarEvent,
    CompatibilityReport,
    Mode,
    ProvidedFeatures,
    RawBar,
    RawTick,
    Requirements,
    ScannerHealth,
    ScannerVersions,
    SymbolMeta,
    WarmupStatus,
)

logger = logging.getLogger(__name__)

#: The minimal feature snapshot every H1/H4/D1 context-timeframe entry exposes on its OWN
#: ``TimeframeContext.features`` (mirrors exactly what the research engine's ``_htf_feat`` forwards
#: — see ``features.py`` module docstring).
_HTF_FEATURE_NAMES = frozenset({"trend_up", "volrank", "rsi"})


class AdapterConfig:
    """Selects and configures a Data Source Adapter (``MARKET_SCANNER_API.md`` §0/§1).

    A plain attribute holder, not a dataclass, so it can accept adapter-specific ``options``
    without coupling this module to any adapter implementation.
    """

    __slots__ = ("mode", "source_id", "options")

    def __init__(self, mode: Mode, source_id: str = "unspecified", **options: Any) -> None:
        self.mode = mode
        self.source_id = source_id
        self.options = options


class MarketScanner:
    """The Market Scanner. See ``MARKET_SCANNER_API.md`` for the full contract."""

    def __init__(self, config: ScannerConfig | None = None) -> None:
        self._config = config or ScannerConfig()
        self._symbol_meta: dict[str, SymbolMeta] = {}
        self._stores: dict[str, SymbolBarStore] = {}
        self._feature_providers: dict[str, FeatureProvider] = {}
        self._base_bar_index: dict[str, int] = {}
        self._last_base_result: dict[str, Any] = {}
        self._clock = ClockController()
        self._requirements: Requirements | None = None
        self._context_timeframes: frozenset[str] = frozenset(DEFAULT_CONTEXT_TIMEFRAMES)
        self._adapter_mode: Mode = Mode.REPLAY
        self._adapter_source_id: str = "unspecified"
        self._configured = False
        self._quote_by_symbol: dict[str, dict[str, Any]] = {}

    # ------------------------------------------------------------------ 1. configuration

    def configure(self, symbols: list[SymbolMeta], data_source: AdapterConfig) -> None:
        """Initialize per-symbol state and select the Data Source Adapter mode.

        Idempotent: calling this again fully resets the scanner's internal state (a fresh
        configuration means a fresh run — never a silent partial reset).
        """
        self._symbol_meta = {s.symbol: s for s in symbols}
        self._stores = {s.symbol: SymbolBarStore(s.symbol) for s in symbols}
        self._feature_providers = {}
        self._base_bar_index = {s.symbol: 0 for s in symbols}
        self._last_base_result = {}
        self._clock = ClockController()
        self._adapter_mode = data_source.mode
        self._adapter_source_id = data_source.source_id
        self._quote_by_symbol = {}
        self._configured = True
        logger.info(
            "MarketScanner configured: %d symbol(s), adapter mode=%s source=%s",
            len(self._symbol_meta), self._adapter_mode.value, self._adapter_source_id,
        )

    def register_requirements(self, req: Requirements) -> CompatibilityReport:
        """Register the aggregated Strategy Manager requirement; returns a compatibility report."""
        self._require_configured()
        provided = self.get_provided_features()
        missing_fields: list[str] = []
        for tf, fields in req.fields_by_timeframe.items():
            available = provided.fields_by_timeframe.get(tf, frozenset())
            for f in sorted(fields):
                if f not in available:
                    missing_fields.append(f"{tf}.{f}")
        missing_timeframes = [tf for tf in sorted(req.timeframes) if not self._is_recognised_timeframe(tf)]

        self._requirements = req
        new_context_timeframes = frozenset(tf for tf in req.timeframes if tf != self._config.base_timeframe)
        for symbol in self._symbol_meta:
            store = self._stores[symbol]
            already_ingesting = store.window(self._config.base_timeframe) is not None and len(
                store.window(self._config.base_timeframe).bars()  # type: ignore[union-attr]
            ) > 0
            if symbol not in self._feature_providers or not already_ingesting:
                self._feature_providers[symbol] = FeatureProvider(
                    new_context_timeframes, self._config.event_flag_window_seconds
                )
            else:
                logger.warning(
                    "register_requirements called after data was already ingested for %r; "
                    "keeping the existing FeatureProvider (its higher-timeframe set may not "
                    "reflect the newly registered requirements).",
                    symbol,
                )
        self._context_timeframes = new_context_timeframes

        satisfiable = not missing_fields and not missing_timeframes
        report = CompatibilityReport(
            satisfiable=satisfiable,
            missing_fields=missing_fields,
            missing_timeframes=missing_timeframes,
            feature_dictionary_version=self._config.feature_dictionary_version,
        )
        logger.info("register_requirements: satisfiable=%s missing_fields=%d missing_timeframes=%d",
                    satisfiable, len(missing_fields), len(missing_timeframes))
        return report

    def get_provided_features(self) -> ProvidedFeatures:
        """Declare exactly what this scanner build provides, for compatibility checks."""
        fields_by_timeframe: dict[str, frozenset[str]] = {self._config.base_timeframe: M15_FEATURE_NAMES}
        for tf in DEFAULT_CONTEXT_TIMEFRAMES:
            fields_by_timeframe[tf] = _HTF_FEATURE_NAMES if tf != "W1" else frozenset()
        return ProvidedFeatures(
            feature_dictionary_version=self._config.feature_dictionary_version,
            fields_by_timeframe=fields_by_timeframe,
        )

    # ------------------------------------------------------------------ 2. ingestion

    def ingest_bar(self, bar: RawBar) -> None:
        """Ingest a normalized bar for its (symbol, timeframe).

        Caller contract (architecture §9): for any timestamp, higher-timeframe bars closing at or
        before that timestamp must be ingested no later than the base-timeframe bar closing at
        that same timestamp, so ``pdh/pdl``-style features see the right "last available" bar.
        """
        self._require_configured()
        if bar.symbol not in self._symbol_meta:
            raise UnknownSymbolError(bar.symbol)
        store = self._stores[bar.symbol]
        window = store.ensure_timeframe(bar.timeframe, self._window_max_len(bar.timeframe))
        gap = window.ingest_bar(bar)
        if gap is not None:
            logger.debug("gap detected %s/%s: %s", bar.symbol, bar.timeframe, gap)

        if not bar.complete:
            return

        fp = self._ensure_feature_provider(bar.symbol)
        if bar.timeframe == self._config.base_timeframe:
            d1_window = store.window("D1")
            latest_d1 = latest_lookahead_safe_bar(d1_window, bar.ts_close)
            result = fp.on_base_close(bar, latest_d1)
            self._last_base_result[bar.symbol] = result
            self._base_bar_index[bar.symbol] = self._base_bar_index.get(bar.symbol, 0) + 1
        elif bar.timeframe in self._context_timeframes:
            fp.on_context_close(bar.timeframe, bar)

    def ingest_tick(self, tick: RawTick) -> None:
        """Fold a tick into the forming base-timeframe bar and the optional ``quote`` block."""
        self._require_configured()
        if tick.symbol not in self._symbol_meta:
            raise UnknownSymbolError(tick.symbol)
        store = self._stores[tick.symbol]
        base_tf = self._config.base_timeframe
        window = store.ensure_timeframe(base_tf, self._window_max_len(base_tf))
        price = tick.mid
        if price is not None:
            window.apply_tick(tick.ts, price, tick.volume)
        spread = (tick.ask - tick.bid) if (tick.bid is not None and tick.ask is not None) else None
        self._quote_by_symbol[tick.symbol] = {
            "ts": tick.ts, "bid": tick.bid, "ask": tick.ask, "spread": spread,
        }

    def ingest_calendar(self, evt: CalendarEvent) -> None:
        """Register an economic/holiday calendar event for every (or one) tracked symbol."""
        self._require_configured()
        targets = [evt.symbol] if evt.symbol is not None else list(self._symbol_meta)
        for symbol in targets:
            if symbol not in self._symbol_meta:
                raise UnknownSymbolError(symbol)
            self._ensure_feature_provider(symbol).calendar_engine.ingest_event(evt)

    def advance_clock(self, as_of: int) -> list[SymbolTimeframeClose]:
        """Move the canonical clock to ``as_of``; return every newly-closed (symbol, timeframe) bar."""
        self._require_configured()
        return self._clock.advance(as_of, self._stores)

    # ------------------------------------------------------------------ 3. context production

    def build_context(self, symbol: str, as_of: int) -> dict[str, Any]:
        """Assemble, validate, and return the ``MarketContext`` for ``symbol`` at ``as_of``."""
        self._require_configured()
        if symbol not in self._symbol_meta:
            raise UnknownSymbolError(symbol)

        store = self._stores[symbol]
        base_tf = self._config.base_timeframe
        base_window = store.window(base_tf)
        base_bars = select_lookahead_safe_bars(base_window, as_of, self._lookback_for(base_tf))

        last_result = self._last_base_result.get(symbol)
        if last_result is None:
            session_dict, calendar_dict = self._cold_session_calendar(as_of)
            m15_features: dict[str, Any] = dict.fromkeys(M15_FEATURE_NAMES)
        else:
            session_dict = last_result.session.to_schema_dict()
            calendar_dict = last_result.calendar.to_schema_dict()
            m15_features = last_result.features

        fp = self._feature_providers.get(symbol)
        timeframes: dict[str, Any] = {base_tf: build_timeframe_context(base_tf, base_bars, m15_features)}
        features_by_timeframe: dict[str, dict[str, Any]] = {base_tf: m15_features}
        for tf in sorted(self._context_timeframes):
            window = store.window(tf)
            bars = select_lookahead_safe_bars(window, as_of, self._lookback_for(tf))
            htf_feats = fp.htf_feature_snapshot(tf) if fp is not None else dict.fromkeys(_HTF_FEATURE_NAMES)
            timeframes[tf] = build_timeframe_context(tf, bars, htf_feats)
            features_by_timeframe[tf] = htf_feats

        windows_by_tf = {base_tf: base_window, **{tf: store.window(tf) for tf in self._context_timeframes}}
        dq, suff = data_quality.assess(as_of, self._config, windows_by_tf, features_by_timeframe, self._requirements)

        meta_symbol = self._symbol_meta[symbol]
        context: dict[str, Any] = {
            "meta": {
                "context_schema_version": self._config.context_schema_version,
                "feature_dictionary_version": self._config.feature_dictionary_version,
                "interface_version": self._config.interface_version,
                "scanner_version": self._config.scanner_version,
                "symbol": symbol,
                "base_timeframe": base_tf,
                "as_of": as_of,
                "generated_at": as_of,
                "mode": self._adapter_mode.value,
                "source": self._adapter_source_id,
            },
            "clock": {
                "as_of": as_of,
                "base_bar_index": self._base_bar_index.get(symbol, 0),
                "is_new_session": last_result.session.is_new_session if last_result else True,
                "is_new_day": last_result.calendar.is_new_day if last_result else True,
                "is_new_week": last_result.calendar.is_new_week if last_result else True,
                "is_month_boundary": last_result.calendar.is_month_boundary if last_result else True,
            },
            "symbol_meta": {
                "symbol": meta_symbol.symbol,
                "tick_size": meta_symbol.tick_size,
                "point_value": meta_symbol.point_value,
                "price_precision": meta_symbol.price_precision,
                "session_anchor": meta_symbol.session_anchor,
                "trading_hours": meta_symbol.trading_hours,
            },
            "session": session_dict,
            "calendar": calendar_dict,
            "timeframes": timeframes,
            "data_quality": dq,
            "sufficiency": suff,
        }
        quote = self._quote_by_symbol.get(symbol)
        if quote is not None:
            context["quote"] = quote

        errors = validate_context(context)
        if errors:
            logger.error("MarketContext validation failed for %s@%s: %s", symbol, as_of, errors)
            if self._config.strict_schema_validation:
                raise ContextValidationError(symbol, as_of, errors)
        return context

    def scan(self, as_of: int, symbols: list[str] | None = None) -> dict[str, dict[str, Any]]:
        """Build contexts for all tracked symbols (or ``symbols``) at ``as_of``."""
        self._require_configured()
        targets = symbols if symbols is not None else list(self._symbol_meta)
        batch: dict[str, dict[str, Any]] = {}
        for symbol in targets:
            try:
                batch[symbol] = self.build_context(symbol, as_of)
            except ContextValidationError:
                logger.error("skipping %s in this scan cycle (invalid context)", symbol)
        return batch

    def context_for(self, symbol: str, as_of: int) -> dict[str, Any]:
        """Alias for :meth:`build_context` (single-symbol callers)."""
        return self.build_context(symbol, as_of)

    # ------------------------------------------------------------------ 4. introspection & health

    def warmup_status(self, symbol: str) -> WarmupStatus:
        """Whether ``symbol``'s rolling windows/features have enough history to be non-null."""
        self._require_configured()
        if symbol not in self._symbol_meta:
            raise UnknownSymbolError(symbol)
        store = self._stores[symbol]
        tracked = (
            self._requirements.timeframes
            if self._requirements is not None
            else frozenset({self._config.base_timeframe}) | self._context_timeframes
        )
        by_tf: dict[str, bool] = {}
        bars_needed: dict[str, int] = {}
        for tf in sorted(tracked):
            window = store.window(tf)
            lookback = self._lookback_for(tf)
            have = len(window.bars()) if window is not None else 0
            has_close = window is not None and window.last_ingested_close is not None
            by_tf[tf] = has_close and have >= lookback
            bars_needed[tf] = max(0, lookback - have)
        satisfied = bool(by_tf) and all(by_tf.values())
        return WarmupStatus(satisfied=satisfied, by_timeframe=by_tf, bars_needed=bars_needed)

    def health(self) -> ScannerHealth:
        """Operational status of the scanner itself (reports only; takes no action)."""
        notes: list[str] = []
        gaps_open = 0
        staleness_by_symbol: dict[str, int] = {}
        sync_ok = True
        as_of = self._clock.as_of
        for symbol, store in self._stores.items():
            base_window = store.window(self._config.base_timeframe)
            gaps_open += len(base_window.gaps()) if base_window is not None else 0
            if as_of is not None and base_window is not None and base_window.last_ingested_close is not None:
                staleness_by_symbol[symbol] = max(0, int((as_of - base_window.last_ingested_close) * 1000))
            else:
                staleness_by_symbol[symbol] = data_quality.UNKNOWN_STALENESS_MS
                sync_ok = False
        state = "OK" if self._configured and sync_ok else ("DEGRADED" if self._configured else "UNINITIALIZED")
        if not self._configured:
            notes.append("configure() has not been called")
        return ScannerHealth(
            state=state,
            feeds=[self._adapter_source_id] if self._configured else [],
            sync_ok=sync_ok,
            gaps_open=gaps_open,
            staleness_ms_by_symbol=staleness_by_symbol,
            notes=notes,
        )

    def versions(self) -> ScannerVersions:
        """Echo the version lines for the Loader's end-to-end compatibility check."""
        return ScannerVersions(
            context_schema_version=self._config.context_schema_version,
            feature_dictionary_version=self._config.feature_dictionary_version,
            scanner_version=self._config.scanner_version,
            interface_version=self._config.interface_version,
        )

    # ------------------------------------------------------------------ internals

    def _require_configured(self) -> None:
        if not self._configured:
            raise ScannerNotConfiguredError("MarketScanner.configure(...) must be called first")

    def _ensure_feature_provider(self, symbol: str) -> FeatureProvider:
        fp = self._feature_providers.get(symbol)
        if fp is None:
            fp = FeatureProvider(self._context_timeframes, self._config.event_flag_window_seconds)
            self._feature_providers[symbol] = fp
        return fp

    def _lookback_for(self, timeframe: str) -> int:
        if self._requirements is not None:
            return self._requirements.lookback_by_timeframe.get(timeframe, self._config.history_buffer_bars)
        return self._config.history_buffer_bars

    def _window_max_len(self, timeframe: str) -> int:
        return max(self._lookback_for(timeframe), self._config.history_buffer_bars)

    @staticmethod
    def _is_recognised_timeframe(timeframe: str) -> bool:
        try:
            timeframe_seconds(timeframe)
            return True
        except ValueError:
            return False

    @staticmethod
    def _cold_session_calendar(as_of: int) -> tuple[dict[str, Any], dict[str, Any]]:
        """Schema-valid placeholder ``session``/``calendar`` objects before any base bar has
        closed for a symbol (pre-warmup). Never fabricates a price or a derived indicator — only
        the calendar facts directly computable from ``as_of`` itself."""
        from datetime import UTC, datetime

        dt = datetime.fromtimestamp(as_of, tz=UTC)
        name = session_name_for_hour(dt.hour)
        session_dict = {
            "name": name.value, "block_id": 0, "bar_in_session": 0, "session_open_ts": as_of,
            "session_high": None, "session_low": None,
            "opening_range": {"high": None, "low": None, "formed": False},
        }
        calendar_dict = {
            "date": dt.date().isoformat(), "dow": dt.weekday(), "dom": dt.day,
            "is_holiday": False, "is_weekend_gap": False, "dst_offset_seconds": 0,
            "event_flags": None,
        }
        return session_dict, calendar_dict
