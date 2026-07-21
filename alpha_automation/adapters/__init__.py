"""Alpha reasoning adapters. Backend-agnostic: `stub` (deterministic, for dry-run/tests) and
`codex` (subprocess to the locally-installed `codex exec`). No external Python SDK is required.
"""

from .base import AlphaAdapter, AlphaContext, AlphaAdapterError, extract_json
from .stub import StubAdapter


def build_adapter(config):
    """Factory: construct the adapter named by config.adapter."""
    if config.adapter == "stub":
        return StubAdapter(config.seed)
    if config.adapter == "codex":
        from .codex_exec import CodexAdapter
        return CodexAdapter(config)
    raise ValueError(f"unknown adapter {config.adapter!r}")


__all__ = [
    "AlphaAdapter", "AlphaContext", "AlphaAdapterError", "extract_json",
    "StubAdapter", "build_adapter",
]
