"""A minimal :class:`~ai_trader.strategy_manager.manager.MarketScannerLike` test double —
structurally satisfies the Protocol without needing a fully configured real
:class:`ai_trader.market_scanner.scanner.MarketScanner` (which requires symbols/adapter setup
unrelated to what these tests exercise)."""

from __future__ import annotations

from ai_trader.market_scanner.types import CompatibilityReport, ProvidedFeatures, Requirements, ScannerVersions


class FakeScanner:
    def __init__(
        self,
        fields_by_timeframe: dict[str, frozenset[str]] | None = None,
        feature_dictionary_version: str = "1.0.0",
        raise_on_handshake: bool = False,
    ) -> None:
        self._fields_by_timeframe = fields_by_timeframe or {
            "M15": frozenset({"m_atr", "m_rsi", "m_ema20", "m_ema50"}),
            "H1": frozenset({"h1_trend_up", "h1_rsi"}),
            "H4": frozenset({"h4_trend_up"}),
            "D1": frozenset({"d1_trend_up"}),
        }
        self._feature_dictionary_version = feature_dictionary_version
        self._raise_on_handshake = raise_on_handshake
        self.registered_requirements: list[Requirements] = []

    def get_provided_features(self) -> ProvidedFeatures:
        if self._raise_on_handshake:
            raise RuntimeError("simulated scanner handshake failure")
        return ProvidedFeatures(self._feature_dictionary_version, self._fields_by_timeframe)

    def versions(self) -> ScannerVersions:
        if self._raise_on_handshake:
            raise RuntimeError("simulated scanner handshake failure")
        return ScannerVersions("1.0.0", self._feature_dictionary_version, "1.0.0", "1.0.0")

    def register_requirements(self, req: Requirements) -> CompatibilityReport:
        self.registered_requirements.append(req)
        return CompatibilityReport(True, [], [], self._feature_dictionary_version)
