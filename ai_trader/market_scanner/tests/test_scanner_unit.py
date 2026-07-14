"""Unit tests for ai_trader.market_scanner.scanner.MarketScanner (method-level, not full replay)."""

import pytest

from ai_trader.market_scanner import (
    AdapterConfig,
    CalendarEvent,
    ImpactLevel,
    Mode,
    RawBar,
    RawTick,
    Requirements,
    ScannerNotConfiguredError,
    SymbolMeta,
    UnknownSymbolError,
    UnknownTimeframeError,
)
from ai_trader.market_scanner.config import ScannerConfig
from ai_trader.market_scanner.scanner import MarketScanner


def _symbol(name: str = "XAUUSD") -> SymbolMeta:
    return SymbolMeta(symbol=name, tick_size=0.1, point_value=1.0, price_precision=2)


def _m15_bar(ts_open: int, close: float = 100.0) -> RawBar:
    return RawBar(symbol="XAUUSD", timeframe="M15", ts_open=ts_open, ts_close=ts_open + 900,
                  open=close, high=close + 1, low=close - 1, close=close, volume=10.0, complete=True)


class TestConfigurationGuards:
    def test_methods_require_configure_first(self) -> None:
        scanner = MarketScanner()
        with pytest.raises(ScannerNotConfiguredError):
            scanner.build_context("XAUUSD", 900)
        with pytest.raises(ScannerNotConfiguredError):
            scanner.advance_clock(900)

    def test_unknown_symbol_raises(self) -> None:
        scanner = MarketScanner()
        scanner.configure([_symbol()], AdapterConfig(mode=Mode.REPLAY))
        with pytest.raises(UnknownSymbolError):
            scanner.build_context("NOTASYMBOL", 900)

    def test_health_before_configure_is_uninitialized(self) -> None:
        scanner = MarketScanner()
        h = scanner.health()
        assert h.state == "UNINITIALIZED"


class TestRegisterRequirements:
    def test_satisfiable_when_all_fields_known(self) -> None:
        scanner = MarketScanner()
        scanner.configure([_symbol()], AdapterConfig(mode=Mode.REPLAY))
        req = Requirements(
            timeframes=frozenset({"M15"}),
            fields_by_timeframe={"M15": frozenset({"m_atr", "m_rsi"})},
            lookback_by_timeframe={"M15": 20},
            symbols=frozenset({"XAUUSD"}),
        )
        report = scanner.register_requirements(req)
        assert report.satisfiable is True
        assert report.missing_fields == []
        assert report.missing_timeframes == []

    def test_unsatisfiable_when_field_unknown(self) -> None:
        scanner = MarketScanner()
        scanner.configure([_symbol()], AdapterConfig(mode=Mode.REPLAY))
        req = Requirements(
            timeframes=frozenset({"M15"}),
            fields_by_timeframe={"M15": frozenset({"totally_made_up_field"})},
            lookback_by_timeframe={"M15": 20},
            symbols=frozenset({"XAUUSD"}),
        )
        report = scanner.register_requirements(req)
        assert report.satisfiable is False
        assert "M15.totally_made_up_field" in report.missing_fields

    def test_unrecognised_timeframe_reported_missing(self) -> None:
        scanner = MarketScanner()
        scanner.configure([_symbol()], AdapterConfig(mode=Mode.REPLAY))
        req = Requirements(
            timeframes=frozenset({"M15", "M3"}),
            fields_by_timeframe={},
            lookback_by_timeframe={},
            symbols=frozenset({"XAUUSD"}),
        )
        report = scanner.register_requirements(req)
        assert "M3" in report.missing_timeframes


class TestVersionsAndProvidedFeatures:
    def test_versions_echo_config(self) -> None:
        config = ScannerConfig(scanner_version="9.9.9")
        scanner = MarketScanner(config)
        v = scanner.versions()
        assert v.scanner_version == "9.9.9"
        assert v.context_schema_version == config.context_schema_version

    def test_provided_features_include_full_m15_namespace(self) -> None:
        scanner = MarketScanner()
        provided = scanner.get_provided_features()
        assert "m_atr" in provided.fields_by_timeframe["M15"]
        # H4/H1/D1 context is folded into the M15 flat namespace under a prefix (features.py),
        # while each HTF's OWN TimeframeContext exposes only the unprefixed minimal snapshot.
        assert "h4_trend_up" in provided.fields_by_timeframe["M15"]
        assert provided.fields_by_timeframe["H4"] == frozenset({"trend_up", "volrank", "rsi"})


class TestWarmupStatus:
    def test_no_data_is_not_satisfied(self) -> None:
        scanner = MarketScanner()
        scanner.configure([_symbol()], AdapterConfig(mode=Mode.REPLAY))
        status = scanner.warmup_status("XAUUSD")
        assert status.satisfied is False


class TestIngestTickAndQuote:
    def test_tick_populates_quote_block(self) -> None:
        scanner = MarketScanner()
        scanner.configure([_symbol()], AdapterConfig(mode=Mode.REPLAY))
        scanner.ingest_bar(_m15_bar(0))
        scanner.advance_clock(900)
        scanner.ingest_tick(RawTick(symbol="XAUUSD", ts=901, bid=100.0, ask=100.2))
        ctx = scanner.build_context("XAUUSD", 900)
        assert ctx["quote"] == {"ts": 901, "bid": 100.0, "ask": 100.2, "spread": pytest.approx(0.2)}

    def test_tick_on_unknown_symbol_raises(self) -> None:
        scanner = MarketScanner()
        scanner.configure([_symbol()], AdapterConfig(mode=Mode.REPLAY))
        with pytest.raises(UnknownSymbolError):
            scanner.ingest_tick(RawTick(symbol="NOPE", ts=1, last=100.0))

    def test_tick_updates_forming_base_bar_features_do_not_leak_early(self) -> None:
        scanner = MarketScanner()
        scanner.configure([_symbol()], AdapterConfig(mode=Mode.REPLAY))
        scanner.ingest_tick(RawTick(symbol="XAUUSD", ts=10, last=100.0))
        # a forming bar must never appear in the (complete-bars-only) window
        assert scanner._stores["XAUUSD"].window("M15").bars() == []  # noqa: SLF001


class TestIngestCalendar:
    def test_calendar_event_reaches_all_symbols_by_default(self) -> None:
        scanner = MarketScanner()
        scanner.configure([_symbol("XAUUSD"), _symbol("EURUSD")], AdapterConfig(mode=Mode.REPLAY))
        scanner.ingest_calendar(CalendarEvent(ts=1000, impact=ImpactLevel.HIGH, kind="nfp"))
        for symbol in ("XAUUSD", "EURUSD"):
            fp = scanner._feature_providers[symbol]  # noqa: SLF001
            assert len(fp.calendar_engine._events) == 1  # noqa: SLF001

    def test_calendar_event_targeted_to_one_symbol(self) -> None:
        scanner = MarketScanner()
        scanner.configure([_symbol("XAUUSD"), _symbol("EURUSD")], AdapterConfig(mode=Mode.REPLAY))
        scanner.ingest_calendar(CalendarEvent(ts=1000, impact=ImpactLevel.HIGH, kind="nfp", symbol="XAUUSD"))
        assert len(scanner._feature_providers["XAUUSD"].calendar_engine._events) == 1  # noqa: SLF001
        assert "EURUSD" not in scanner._feature_providers  # noqa: SLF001

    def test_calendar_event_unknown_symbol_raises(self) -> None:
        scanner = MarketScanner()
        scanner.configure([_symbol()], AdapterConfig(mode=Mode.REPLAY))
        with pytest.raises(UnknownSymbolError):
            scanner.ingest_calendar(CalendarEvent(ts=1000, impact=ImpactLevel.LOW, symbol="NOPE"))


class TestScanAndAlias:
    def test_scan_builds_batch_for_all_symbols(self) -> None:
        scanner = MarketScanner()
        scanner.configure([_symbol("XAUUSD"), _symbol("EURUSD")], AdapterConfig(mode=Mode.REPLAY))
        for sym in ("XAUUSD", "EURUSD"):
            scanner.ingest_bar(_m15_bar(0))  # harmless: XAUUSD twice is fine, just proves API shape
        scanner.ingest_bar(RawBar(symbol="EURUSD", timeframe="M15", ts_open=0, ts_close=900,
                                   open=1.1, high=1.2, low=1.0, close=1.15, volume=10, complete=True))
        scanner.advance_clock(900)
        batch = scanner.scan(900)
        assert set(batch) == {"XAUUSD", "EURUSD"}

    def test_scan_subset_of_symbols(self) -> None:
        scanner = MarketScanner()
        scanner.configure([_symbol("XAUUSD"), _symbol("EURUSD")], AdapterConfig(mode=Mode.REPLAY))
        scanner.advance_clock(900)
        batch = scanner.scan(900, symbols=["XAUUSD"])
        assert set(batch) == {"XAUUSD"}

    def test_context_for_is_alias_of_build_context(self) -> None:
        scanner = MarketScanner()
        scanner.configure([_symbol()], AdapterConfig(mode=Mode.REPLAY))
        scanner.ingest_bar(_m15_bar(0))
        scanner.advance_clock(900)
        assert scanner.context_for("XAUUSD", 900) == scanner.build_context("XAUUSD", 900)


class TestHealthWithData:
    def test_health_ok_after_ingest(self) -> None:
        scanner = MarketScanner()
        scanner.configure([_symbol()], AdapterConfig(mode=Mode.REPLAY))
        scanner.ingest_bar(_m15_bar(0))
        scanner.advance_clock(900)
        h = scanner.health()
        assert h.state == "OK"
        assert h.sync_ok is True
        assert h.staleness_ms_by_symbol["XAUUSD"] == 0


class TestUnrecognisedTimeframe:
    def test_ingest_bar_unrecognised_timeframe_raises(self) -> None:
        scanner = MarketScanner()
        scanner.configure([_symbol()], AdapterConfig(mode=Mode.REPLAY))
        bad = RawBar(symbol="XAUUSD", timeframe="M3", ts_open=0, ts_close=180,
                     open=1, high=2, low=0.5, close=1.5, volume=1, complete=True)
        with pytest.raises(UnknownTimeframeError):
            scanner.ingest_bar(bad)
