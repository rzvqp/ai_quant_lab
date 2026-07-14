"""Compatibility Checker (``STRATEGY_MANAGER_ARCHITECTURE.md`` §5).

Verifies, for one already schema-valid contract, that it is safe to expose: interface/runtime
version support, ``MarketContext`` field/timeframe availability against the Market Scanner's
declared feature dictionary, and the feature-dictionary MAJOR match. Never mutates anything; returns
a :class:`~ai_trader.strategy_manager.types.CompatibilityResult` the caller (the Loader/Manager
orchestration) attaches to the registry entry.
"""

from __future__ import annotations

from typing import Any, Protocol

from ai_trader.strategy_manager.config import SupportedVersions
from ai_trader.strategy_manager.contract import Contract
from ai_trader.strategy_manager.types import CompatibilityResult


class ProvidedFeaturesLike(Protocol):
    """Structural shape of ``MarketScanner.get_provided_features()``'s return value
    (:class:`ai_trader.market_scanner.types.ProvidedFeatures`) — a ``Protocol`` so this module
    never needs to import the Market Scanner package directly, keeping the two modules'
    compatibility layer decoupled and independently testable."""

    feature_dictionary_version: str
    fields_by_timeframe: dict[str, frozenset[str]]


def _major(semver: str) -> int:
    """Extract the MAJOR component of a ``MAJOR.MINOR.PATCH`` string. The contract schema already
    constrains this pattern (``^\\d+\\.\\d+\\.\\d+$``), so a well-formed input is assumed; this is
    only ever called on strings that already passed schema validation."""
    return int(semver.split(".", 1)[0])


def _field_present(contract: Contract, dotted_path: str) -> bool:
    """Whether the (optional) field at ``dotted_path`` is present (non-``None``) on ``contract`` —
    used for the deprecated-field check (architecture §5.5): a field marked deprecated in the
    current interface MINOR is accepted but flagged, never rejected outright."""
    obj: Any = contract
    for part in dotted_path.split("."):
        if obj is None:
            return False
        obj = getattr(obj, part, None)
    return obj is not None


def check(
    contract: Contract,
    provided_features: ProvidedFeaturesLike | None,
    supported: SupportedVersions,
    deprecated_field_paths: frozenset[str] = frozenset(),
) -> CompatibilityResult:
    """Run every compatibility check on ``contract`` (architecture §5, summarized rule: "accept iff
    ``schema_valid ∧ interface_major_ok ∧ runtime_major_ok ∧ all_required_fields_provided ∧
    all_required_timeframes_provided``").

    Args:
        contract: an already schema-validated, parsed contract.
        provided_features: the Market Scanner's declared feature dictionary
            (``get_provided_features()``), or ``None`` if the Manager has no scanner handshake yet
            (architecture §12: "if the Scanner handshake ... partially fails" — treated
            conservatively as MarketContext-incompatible, since compatibility cannot be honestly
            claimed without a scanner to check against; never silently assumed compatible).
        supported: the Manager's supported version window.
        deprecated_field_paths: dotted attribute paths the current interface MINOR marks deprecated.

    Returns:
        A :class:`CompatibilityResult`. ``schema_valid`` is always ``True`` here (the caller only
        invokes this on contracts that already passed schema validation); it is carried through so
        the result is self-describing.
    """
    reasons: list[str] = []
    deprecated: list[str] = []

    # Architecture §5.1 also describes a "MINOR <= supported" ceiling, but STRATEGY_REGISTRY_SCHEMA
    # .json's `supported` object (additionalProperties: false) tracks only MAJOR versions for
    # interface/runtime/feature-dictionary -- there is no supported-MINOR field to compare against
    # in the frozen schema. This is consistent with the contract schema itself const-pinning
    # `interface_version` to exactly "1.0.0" today (no released MINOR bump exists yet to reject).
    # MAJOR equality is therefore the only interface-version check with a real configuration
    # surface today; a future MINOR-ceiling config field can add that comparison without a
    # fabricated placeholder in the meantime.
    interface_major_ok = _major(contract.interface_version) == supported.interface_major
    interface_ok = interface_major_ok
    if not interface_major_ok:
        reasons.append(
            f"interface_version {contract.interface_version} MAJOR does not match supported "
            f"MAJOR {supported.interface_major}"
        )

    # Runtime API compatibility: the Strategy API's own version "tracks interface_version"
    # (STRATEGY_API_v1.md: "api_version: 1.0.0 (tracks interface_version)") -- the contract schema
    # has no separate api_version field, so runtime compatibility is the same MAJOR check under a
    # distinct name (architecture §5.4), kept separate so a future contract schema MINOR that adds
    # an independent api_version field only needs a change here, not at every call site.
    runtime_ok = interface_major_ok

    context_ok = True
    if provided_features is None:
        context_ok = False
        reasons.append("no Market Scanner handshake available -- MarketContext compatibility cannot be verified")
    else:
        major_ok = _major(provided_features.feature_dictionary_version) == supported.feature_dictionary_major
        if not major_ok:
            context_ok = False
            reasons.append(
                f"feature_dictionary_version {provided_features.feature_dictionary_version} MAJOR "
                f"does not match supported MAJOR {supported.feature_dictionary_major}"
            )
        for required in contract.semantics.required_data:
            tf_fields = provided_features.fields_by_timeframe.get(required.timeframe)
            if tf_fields is None:
                context_ok = False
                reasons.append(f"missing_timeframe:{required.timeframe}")
                continue
            for field_name in required.fields:
                if field_name not in tf_fields:
                    context_ok = False
                    reasons.append(f"missing_field:{required.timeframe}.{field_name}")

    for path in sorted(deprecated_field_paths):
        if _field_present(contract, path):
            deprecated.append(path)

    compatible = interface_ok and runtime_ok and context_ok
    return CompatibilityResult(
        compatible=compatible,
        schema_valid=True,
        interface_ok=interface_ok,
        runtime_ok=runtime_ok,
        context_ok=context_ok,
        deprecated_fields=deprecated,
        reasons=reasons,
    )
