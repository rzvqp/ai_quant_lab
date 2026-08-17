"""Evaluation identity/provenance for N1 replay results (RT-N1-REPLAY-0001 section 2). Every field
here is either a REAL, verified constant read from the wrapped runtime (`ve_brain`, this repo's own
git history) or a hash computed over real observed data -- nothing here is invented or approximated.

**`WRAPPED_RUNTIME_COMMIT`**: the CEO's own directive names `eb97a80` explicitly as "detectorii și
configurațiile reale din runtime eb97a80". Verified (2026-08-17) that `ai_trader/new_brain_bridge/
raw_axes_builder.py`, `ai_trader/new_brain_bridge/bridge.py`, and `ai_trader/structural_observer/
vendor_bridge.py` have had ZERO commits touch them between `eb97a80` and this package's own delivery
commit (`git log --oneline eb97a80..HEAD -- <those 3 paths>` returned nothing) -- so citing `eb97a80`
as the pinned source commit for all three is exact, not approximate."""

from __future__ import annotations

import dataclasses
import hashlib

import ve_brain  # type: ignore[import-untyped]

from ai_trader.mandate2_readiness.wheel_verification import PINNED_WHEEL_SHA256

# -- pinned identity of the wrapped runtime (RawAxesBuilder + bridge.py's N1/Router recipe) --
WRAPPED_RUNTIME_COMMIT = "eb97a80"
RAW_AXES_BUILDER_BLOB_SHA1 = "d071c8cbd993cb9377b70af6b61e353d4c101966"
BRIDGE_PY_BLOB_SHA1 = "b4a301371e7c2f174064dc2d50129912f3d82a52"
VENDOR_BRIDGE_BLOB_SHA1 = "bb53680c2180a23366b9aa5a08130b4410ea6683"

# -- pinned identity of the ve_brain artifact N1/Router actually run inside --
VE_BRAIN_VERSION = ve_brain.VE_BRAIN_VERSION
VE_BRAIN_WHEEL_SHA256 = PINNED_WHEEL_SHA256
DETECTOR_SOURCE_COMMIT = ve_brain.version.SOURCE_COMMIT  # "dc28e4a" -- the N1/regime measurement source
N1_CONTRACT_VERSION = ve_brain.N1_CONTRACT_VERSION
ROUTER_VERSION = ve_brain.ROUTER_VERSION
RAW_AXIS_SCHEMA_VERSION = ve_brain.regime_routing.RAW_AXIS_SCHEMA_VERSION

# -- this package's own contract/schema version -- bump whenever N1ReplayResult's shape changes --
N1_REPLAY_SCHEMA_VERSION = "n1-replay-contract-v1"


def _fp(*parts: str) -> str:
    """Identical formula to `ai_trader.new_brain_bridge.bridge._fp` (sha256, pipe-joined, first 16 hex
    chars) -- a local copy of a generic hashing convention, not a reimplementation of any detector or
    routing algorithm. Kept local (rather than importing bridge.py's private `_fp`) so this package
    never imports anything from `new_brain_bridge` beyond `RawAxesBuilder` itself."""
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]


def detector_configuration_fingerprint() -> str:
    """Fingerprint of exactly the vendored detector source `RawAxesBuilder` calls
    (`ai_trader.structural_observer.vendor_bridge`) plus `RawAxesBuilder` itself -- both identified by
    their real git blob SHA-1 (`git hash-object`), not a re-hash of file bytes computed here (avoids
    this package silently drifting from git's own notion of "the file's content" if line endings or
    encoding differ at read time)."""
    return _fp(RAW_AXES_BUILDER_BLOB_SHA1, VENDOR_BRIDGE_BLOB_SHA1, BRIDGE_PY_BLOB_SHA1)


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class EvaluationIdentity:
    """The full provenance of one `N1ReplayEngine` instance's results. Two `EvaluationIdentity`
    values are equal if and only if every field that could change the DECISION (not merely metadata)
    is identical -- `fingerprint()` rolls all of them into one comparable string, and `IncompatibleSnapshotError`
    is raised by `restore()` whenever a snapshot's identity does not match the target engine's."""

    implementation_commit: str
    wrapped_runtime_commit: str
    ve_brain_version: str
    ve_brain_wheel_sha256: str
    detector_source_commit: str
    detector_configuration_fingerprint: str
    n1_contract_version: str
    router_version: str
    raw_axis_schema_version: str
    n1_replay_schema_version: str
    symbol: str
    timeframe: str
    bar_interval_seconds: int

    def fingerprint(self) -> str:
        return _fp(
            self.implementation_commit, self.wrapped_runtime_commit, self.ve_brain_version,
            self.ve_brain_wheel_sha256, self.detector_source_commit,
            self.detector_configuration_fingerprint, self.n1_contract_version, self.router_version,
            self.raw_axis_schema_version, self.n1_replay_schema_version, self.symbol, self.timeframe,
            str(self.bar_interval_seconds),
        )

    def matches(self, other: "EvaluationIdentity") -> bool:
        return self.fingerprint() == other.fingerprint()


def build_evaluation_identity(
    *, implementation_commit: str, symbol: str, timeframe: str, bar_interval_seconds: int,
) -> EvaluationIdentity:
    """`implementation_commit` is THIS package's own delivery commit -- supplied by the caller (never
    self-referential: a commit cannot embed its own hash, matching the established
    `artifact_manifest(delivery_commit)` convention elsewhere in this codebase). Everything else is a
    real constant read above, never a literal re-typed inline."""
    return EvaluationIdentity(
        implementation_commit=implementation_commit, wrapped_runtime_commit=WRAPPED_RUNTIME_COMMIT,
        ve_brain_version=VE_BRAIN_VERSION, ve_brain_wheel_sha256=VE_BRAIN_WHEEL_SHA256,
        detector_source_commit=DETECTOR_SOURCE_COMMIT,
        detector_configuration_fingerprint=detector_configuration_fingerprint(),
        n1_contract_version=N1_CONTRACT_VERSION, router_version=ROUTER_VERSION,
        raw_axis_schema_version=RAW_AXIS_SCHEMA_VERSION, n1_replay_schema_version=N1_REPLAY_SCHEMA_VERSION,
        symbol=symbol, timeframe=timeframe, bar_interval_seconds=bar_interval_seconds,
    )


def bars_content_hash(bars: tuple[object, ...], *, bar_to_parts) -> str:  # type: ignore[no-untyped-def]
    """Deterministic, content-addressed hash of an ordered bar sequence -- changes if and only if any
    bar's actual OHLCV content (not merely its count) changes. No existing helper in this codebase
    does this (confirmed by recon before writing this file) -- this is new, not a duplicate."""
    parts: list[str] = []
    for bar in bars:
        parts.extend(bar_to_parts(bar))
    return _fp(*parts)
