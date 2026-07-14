"""Market Scanner v1 — the AI Trader's first module.

Public API surface (``MARKET_SCANNER_API.md``). Only these names are exported; internal modules
(``bar_store``, ``session``, ``calendar_engine``, ``indicators``, ``features``, ``timeframe_sync``,
``data_quality``, ``clock``, ``schema_validation``) are implementation details and may change
without notice. Per the separation law, nothing in this package imports Research Lab code
(``code/``, ``results/``, ``knowledge/experiments/``, ``knowledge/ontology/``) at runtime.
"""

from ai_trader.market_scanner.adapters import DataSourceAdapter, ReplayAdapter
from ai_trader.market_scanner.clock import SymbolTimeframeClose
from ai_trader.market_scanner.config import ScannerConfig
from ai_trader.market_scanner.exceptions import (
    ContextValidationError,
    InvalidBarError,
    InvalidTickError,
    MarketScannerError,
    SchemaLoadError,
    ScannerNotConfiguredError,
    UnknownSymbolError,
    UnknownTimeframeError,
)
from ai_trader.market_scanner.scanner import AdapterConfig, MarketScanner
from ai_trader.market_scanner.types import (
    CalendarEvent,
    CompatibilityReport,
    DataQualityLevel,
    ImpactLevel,
    Mode,
    ProvidedFeatures,
    RawBar,
    RawTick,
    Requirements,
    ScannerHealth,
    ScannerVersions,
    SessionName,
    SufficiencyLevel,
    SymbolMeta,
    TimeframeRequirement,
    WarmupStatus,
)

__all__ = [
    "MarketScanner",
    "AdapterConfig",
    "ScannerConfig",
    "DataSourceAdapter",
    "ReplayAdapter",
    "SymbolMeta",
    "RawBar",
    "RawTick",
    "CalendarEvent",
    "Requirements",
    "TimeframeRequirement",
    "CompatibilityReport",
    "WarmupStatus",
    "ScannerHealth",
    "ProvidedFeatures",
    "ScannerVersions",
    "SymbolTimeframeClose",
    "Mode",
    "ImpactLevel",
    "DataQualityLevel",
    "SufficiencyLevel",
    "SessionName",
    "MarketScannerError",
    "ScannerNotConfiguredError",
    "UnknownSymbolError",
    "UnknownTimeframeError",
    "InvalidBarError",
    "InvalidTickError",
    "ContextValidationError",
    "SchemaLoadError",
]
