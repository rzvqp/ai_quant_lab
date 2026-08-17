"""N1 replay fail-closed error hierarchy. Every one of these is a REFUSAL, never a silent
degradation and never a best-effort guess -- matching the CEO's own directive ("refuz") for every
scenario listed in RT-N1-REPLAY-0001 section 3."""

from __future__ import annotations


class N1ReplayError(Exception):
    """Base class for every fail-closed refusal this package raises."""


class BarNotClosedError(N1ReplayError):
    """The bar's `ts_close` has not yet passed the engine's clock -- this is a forming bar, never
    observable (mirrors `LiveBarFeed.poll()`'s own `ts_close > now: continue` discipline, but as a
    hard refusal here rather than a silent skip, since a replay caller handing over an unclosed bar
    is a caller bug, not routine feed behavior)."""


class OutOfOrderBarError(N1ReplayError):
    """The bar's `ts_open` is before the last-observed bar's `ts_open` (and is not an exact
    duplicate -- see `DuplicateBarError`). `RawAxesBuilder` accumulates history in the order it is
    fed; feeding bars out of order would silently corrupt every downstream detector."""


class FutureBarError(N1ReplayError):
    """The bar's `ts_close` is beyond the replay horizon (`as_of`) the caller explicitly bounded this
    call to -- distinct from `BarNotClosedError` (a wall-clock check): this is a batch-level guard so
    a bounded `replay(bars, as_of=...)` call can never silently process bars beyond what was asked
    for, even if the wall clock would otherwise permit it."""


class DuplicateBarError(N1ReplayError):
    """The bar has the same `ts_open` as the last-observed bar but different content (open/high/low/
    close/volume) -- an ambiguous, conflicting duplicate for an already-observed slot. An EXACT
    duplicate (identical content) is not an error -- see `N1ReplayEngine.observe_closed_bar`'s
    deterministic dedup path, which returns the prior cached result unchanged."""


class NonFiniteAxesInputError(N1ReplayError):
    """The bar carries a NaN or Infinite OHLC/volume value. Refused before it ever reaches
    `RawAxesBuilder` -- a non-finite input would silently propagate into every downstream detector
    (swings, structure, expansion, compression) as `NaN`/`inf` comparisons that Python does not raise
    on, producing a plausible-looking but meaningless `RawAxes` reading."""


class StaleStateError(N1ReplayError):
    """Too much wall-clock time has passed since the last observed bar for this engine instance to be
    trusted as still representing "the current state" without an explicit fresh `observe_closed_bar`
    or `restore`. Mirrors `live_signal_source.types.StaleProbeError`'s own "wait, don't silently
    trust" philosophy, applied to replay state rather than a feed probe."""


class IncompatibleSnapshotError(N1ReplayError):
    """A `restore()` target snapshot's pinned identity (contract version, router version, detector
    configuration fingerprint, ve_brain version, symbol, timeframe, or bar interval) does not
    byte-for-byte match this engine's own current identity. Restoration is refused BEFORE any state
    is mutated -- the engine is left exactly as it was before the call."""
