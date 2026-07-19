"""Encode/decode between Context Memory contracts and their canonical JSON representation -- Phase 7
Checkpoint 10. Reuses :mod:`ai_trader.context_memory.identities`'s own canonicalization functions for the
ENCODE direction (never duplicates that logic); this module adds the DECODE direction Checkpoint 9
deliberately left unimplemented ("canonical round-trip behavior, if deserialization is implemented" was
conditional there, and nothing needed it yet).

Only :class:`ContextSnapshot`, :class:`Observation`, and :class:`Outcome` are encoded/decoded as
independent, top-level, repository-persistable records (see ``repository.py``'s own module docstring for
why :class:`PresentEdgeReference` is deliberately NOT independently persisted -- it is always reachable
via its parent :class:`Observation`). :func:`decode_present_edge_reference` still exists here because
:class:`Observation`'s own decode needs it internally.

**Schema version enforcement**: every decode function checks the payload's own embedded
``context_memory_schema_version`` against this build's :data:`~ai_trader.context_memory.contracts.
CONTEXT_MEMORY_SCHEMA_VERSION` and raises :class:`UnsupportedSchemaVersionError` on any mismatch --
Checkpoint 10 §E's own explicit "unsupported schema versions" failure case. A record written under a
different schema version is never guessed at or partially decoded; a future checkpoint that needs to read
old-schema records will add an explicit migration path, not a silent fallback here.
"""

from __future__ import annotations

import functools
from collections.abc import Callable
from typing import Any, TypeVar

from ai_trader.context_memory.contracts import (
    CONTEXT_MEMORY_SCHEMA_VERSION,
    ContextSnapshot,
    Observation,
    ObservationId,
    Outcome,
    PresentEdgeReference,
    SchemaVersion,
)
from ai_trader.context_memory.enums import (
    ContextAgreementLevel,
    ContextDataQualityState,
    ContextEdgeStatus,
    ContextExpansionState,
    ContextLiquidityState,
    ContextMomentumState,
    ContextStructureState,
    ContextTrendDirection,
    ContextVolatilityRegime,
    HorizonUnit,
    OutcomeStatus,
    SourceType,
)
from ai_trader.context_memory.identities import (
    canonical_context_snapshot,
    canonical_observation,
    canonical_outcome,
    canonical_present_edge_reference,
)
from ai_trader.context_memory.validation import ContextMemoryValidationError


class UnsupportedSchemaVersionError(ContextMemoryValidationError):
    """A persisted record declares a ``context_memory_schema_version`` this build does not understand."""


def _decode_schema_version(data: dict[str, Any], field_name: str) -> SchemaVersion:
    return SchemaVersion(namespace=data["namespace"], version=data["version"])


def _decode_float(value: str | None) -> float | None:
    return None if value is None else float.fromhex(value)


def _check_record_type(payload: dict[str, Any], expected: str) -> None:
    actual = payload.get("record_type")
    if actual != expected:
        raise ContextMemoryValidationError(f"expected record_type={expected!r}, got {actual!r}")


_T = TypeVar("_T")


def _malformed_as_validation_error(decode_fn: Callable[[dict[str, Any]], _T]) -> Callable[[dict[str, Any]], _T]:
    """Wraps a ``decode_*`` function so a missing key / wrong-shaped value / unrecognized enum string
    (``KeyError``/``TypeError``/bare ``ValueError``) always surfaces as one consistent, catchable
    :class:`~ai_trader.context_memory.validation.ContextMemoryValidationError` -- "malformed record
    detection" (Checkpoint 10 §E), never a raw stdlib exception a caller has to know to anticipate.
    :class:`ContextMemoryValidationError` itself (including :class:`UnsupportedSchemaVersionError`) is
    never double-wrapped -- it already carries a clear, specific message."""

    @functools.wraps(decode_fn)
    def wrapper(payload: dict[str, Any]) -> _T:
        try:
            return decode_fn(payload)
        except ContextMemoryValidationError:
            raise
        except (KeyError, TypeError, ValueError) as exc:
            raise ContextMemoryValidationError(
                f"malformed {decode_fn.__name__.removeprefix('decode_')} payload: {exc}"
            ) from exc

    return wrapper


def _check_schema_version(payload: dict[str, Any]) -> None:
    raw = payload.get("context_memory_schema_version")
    if not isinstance(raw, dict) or raw.get("namespace") != CONTEXT_MEMORY_SCHEMA_VERSION.namespace:
        raise UnsupportedSchemaVersionError(f"missing or malformed context_memory_schema_version: {raw!r}")
    if raw.get("version") != CONTEXT_MEMORY_SCHEMA_VERSION.version:
        raise UnsupportedSchemaVersionError(
            f"unsupported context_memory_schema_version {raw!r} -- this build understands "
            f"{CONTEXT_MEMORY_SCHEMA_VERSION.version!r} only"
        )


# ---------------------------------------------------------------------------------------------------
# ContextSnapshot
# ---------------------------------------------------------------------------------------------------


def encode_context_snapshot(snapshot: ContextSnapshot) -> dict[str, Any]:
    return canonical_context_snapshot(snapshot)


@_malformed_as_validation_error
def decode_context_snapshot(payload: dict[str, Any]) -> ContextSnapshot:
    _check_record_type(payload, "context_memory.context_snapshot")
    _check_schema_version(payload)
    return ContextSnapshot(
        instrument=payload["instrument"],
        as_of=payload["as_of"],
        session_state=payload["session_state"],
        trend_m15=ContextTrendDirection(payload["trend_m15"]),
        trend_h1=ContextTrendDirection(payload["trend_h1"]),
        trend_h4=ContextTrendDirection(payload["trend_h4"]),
        trend_d1=ContextTrendDirection(payload["trend_d1"]),
        structure_state=ContextStructureState(payload["structure_state"]),
        momentum_m15=ContextMomentumState(payload["momentum_m15"]),
        momentum_h1=ContextMomentumState(payload["momentum_h1"]),
        momentum_h4=ContextMomentumState(payload["momentum_h4"]),
        momentum_d1=ContextMomentumState(payload["momentum_d1"]),
        volatility_regime=ContextVolatilityRegime(payload["volatility_regime"]),
        liquidity_state=ContextLiquidityState(payload["liquidity_state"]),
        expansion_state=ContextExpansionState(payload["expansion_state"]),
        multi_timeframe_agreement=ContextAgreementLevel(payload["multi_timeframe_agreement"]),
        context_confidence_score=_decode_float(payload["context_confidence_score"]),
        data_quality_state=ContextDataQualityState(payload["data_quality_state"]),
        market_intelligence_schema_version=_decode_schema_version(
            payload["market_intelligence_schema_version"], "market_intelligence_schema_version"
        ),
    )


# ---------------------------------------------------------------------------------------------------
# PresentEdgeReference (nested-only -- see module docstring)
# ---------------------------------------------------------------------------------------------------


def encode_present_edge_reference(ref: PresentEdgeReference) -> dict[str, Any]:
    return canonical_present_edge_reference(ref)


@_malformed_as_validation_error
def decode_present_edge_reference(payload: dict[str, Any]) -> PresentEdgeReference:
    _check_record_type(payload, "context_memory.present_edge_reference")
    _check_schema_version(payload)
    return PresentEdgeReference(
        strategy_id=payload["strategy_id"],
        contract_version=_decode_schema_version(payload["contract_version"], "contract_version"),
        edge_intelligence_schema_version=_decode_schema_version(
            payload["edge_intelligence_schema_version"], "edge_intelligence_schema_version"
        ),
        declared_status=ContextEdgeStatus(payload["declared_status"]),
    )


# ---------------------------------------------------------------------------------------------------
# Observation
# ---------------------------------------------------------------------------------------------------


def encode_observation(observation: Observation) -> dict[str, Any]:
    return canonical_observation(observation)


@_malformed_as_validation_error
def decode_observation(payload: dict[str, Any]) -> Observation:
    _check_record_type(payload, "context_memory.observation")
    _check_schema_version(payload)
    return Observation(
        context_snapshot=decode_context_snapshot(payload["context_snapshot"]),
        present_edges=tuple(decode_present_edge_reference(p) for p in payload["present_edges"]),
        edge_intelligence_schema_version=_decode_schema_version(
            payload["edge_intelligence_schema_version"], "edge_intelligence_schema_version"
        ),
        # provenance_note is deliberately excluded from the canonical payload (identities.py) and so is
        # never recoverable from a decoded record -- consistent with it never participating in identity.
    )


# ---------------------------------------------------------------------------------------------------
# Outcome
# ---------------------------------------------------------------------------------------------------


def encode_outcome(outcome: Outcome) -> dict[str, Any]:
    return canonical_outcome(outcome)


@_malformed_as_validation_error
def decode_outcome(payload: dict[str, Any]) -> Outcome:
    _check_record_type(payload, "context_memory.outcome")
    _check_schema_version(payload)
    return Outcome(
        observation_id=ObservationId(payload["observation_id"]),
        strategy_id=payload["strategy_id"],
        horizon=payload["horizon"],
        horizon_unit=HorizonUnit(payload["horizon_unit"]),
        outcome_definition_version=_decode_schema_version(
            payload["outcome_definition_version"], "outcome_definition_version"
        ),
        status=OutcomeStatus(payload["status"]),
        observation_as_of=payload["observation_as_of"],
        normalized_result=_decode_float(payload["normalized_result"]),
        resolution_as_of=payload["resolution_as_of"],
        cost_model_ref=payload["cost_model_ref"],
        source_type=SourceType(payload["source_type"]),
    )
