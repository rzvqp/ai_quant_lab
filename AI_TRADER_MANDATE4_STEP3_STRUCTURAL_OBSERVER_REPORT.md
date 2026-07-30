# AI Trader — Mandate 4, Step 3: Structural Detector Observer Wiring — Report

**Nature of this document**: implementation report for the CEO-authorized extension ("Dupa punte,
cableaza ca OBSERVATOR: market_structure, imbalance_mechanics, market_state, plus order_flow acum ca e
complet"), following Step 2's investigation and the CEO's own two corrections to it: the cross-repo
bridge target was specified explicitly, and `order_flow.py`'s formation criterion was confirmed
implemented (Step 2's `NotImplementedError` reading was stale).

## 1. The cross-repo bridge: git submodule, pinned

**Choice**: `vendor/alpha_automation_detectors`, a git submodule tracking
`ai_quant_lab-alpha-automation`'s `discovery-mk-matrix-v1` branch, pinned to
`61cbd58c3d5da19001b125b65d669ddad54a14c4` (84 files under `code/`).

**Justification** (the CEO asked me to choose and justify, among submodule/vendoring/install):
- **Vendoring (copying the source) rejected**: forks the code the instant it's copied. A future fix or
  further audit on the original repository would never propagate here, and the copy could silently
  diverge from what "frozen and independently audited" means — the exact property this code was
  described as having.
- **Package install rejected**: `code/` is a flat script directory with no packaging metadata
  (`setup.py`/`pyproject.toml`). Building one would mean modifying `ai_quant_lab-alpha-automation`
  itself — a repository this mandate does not authorize touching.
- **Submodule pin, chosen**: an exact commit becomes part of THIS repository's own git history — a
  cryptographic-strength provenance record. Any future update is a deliberate, auditable action (bumping
  the pointer to a new commit), never silent drift. Nothing is copied or forked; the original stays the
  single source of truth.

**Bridging mechanism**: the vendored modules use plain, non-namespaced imports (`from market_structure
import Block`), assuming `code/` itself is on `sys.path` — they are not an installable package in their
own repository either. `ai_trader/structural_observer/vendor_bridge.py` is the ONE file that performs
this `sys.path` insertion, with `# type: ignore[import-not-found]` on each import (mypy cannot resolve a
dynamically path-inserted module statically — the same convention already used for `RealMT5Gateway`'s own
`import MetaTrader5`). Nothing in the vendored code is modified; this package only reads from it.

## 2. Correction: `order_flow.py` is no longer blocked

Step 2 reported `detect_order_blocks` raising `NotImplementedError`. The CEO corrected this: the
formation criterion was implemented at `3fad03e` on `alpha-automation/discovery-mk-matrix-v1`, plus a fix
at `7d30f59` — both are ancestors of the pinned commit (confirmed via `git merge-base --is-ancestor`). A
fresh read of the file at the pinned commit confirms: impulse criterion (range > 1.5× ATR14 of the prior
bar AND body ≥ 0.5× range, reusing `market_state.atr14`) plus full-body engulfment of the opposite-
direction prior bar. `track_breaker`, `detect_mitigations`, and `detect_rejections` all take the resulting
`OrderBlock` as input and are fully implemented. `order_flow` is now wired alongside the other three.

## 3. What was built

`ai_trader/structural_observer/`:
- **`vendor_bridge.py`** — the `sys.path` bridge described above.
- **`types.py`** — `StructuralEventKind` (nine kinds: SWING, STRUCTURE_BREAK, FVG_FORMED, FVG_REACTION,
  REGIME, ORDER_BLOCK_FORMED/BREAKER/MITIGATION/REJECTION) and `StructuralObservation` (a single generic
  envelope — `symbol, as_of, kind, detail: dict[str, object]` — matching this codebase's own established
  convention of a generic envelope plus JSON-serialized detail, rather than one dataclass per event
  shape).
- **`journal.py`** — `StructuralObservationLog`, the same `SqliteStateStore` append-log engine and
  convention as `LiveSignalJournal` (Piesa 3).
- **`observer.py`** — `StructuralObserver(symbol, journal)`: `observe(bar)` accumulates OHLCV arrays in
  memory, builds one `Block(0, len(bars))` (single continuous block — CEO instruction, matching Step 2's
  own confirmed finding that block-boundary resets exist to protect offline research quarantine, not
  because live has a real boundary there), and re-runs every wired detector over the FULL array on every
  call, recording only NEWLY detected facts via per-fact dedup keys (`(idx, kind)` for swings/breaks,
  `formed_idx` for FVGs/OBs, `(formation_idx, event_idx)` for OB mitigation/rejection, a
  `formed_idx -> set of stage names` map for FVG reaction stages). REGIME (expansion/compression/session)
  is recorded for every bar unconditionally — it's a snapshot, not a discrete event, so there's nothing to
  dedup.
- **`observing_rule.py`** — `ObservingNullRecognitionRule`, the actual wiring point (Section 4).
- **`tests/`** — 19 tests: swing/break detection + dedup-on-regrowth, FVG formation + full 3-stage
  reaction lifecycle + dedup-on-regrowth, Order Block formation + mitigation + rejection + breaker + dedup,
  regime recorded every bar, a simulated-restart persistence test, an end-to-end producer integration
  test through `ObservingNullRecognitionRule`, and a 7-check static import-independence suite.

Every synthetic test input was verified empirically — run directly against the real vendored functions via
ad-hoc scripts — before being encoded into a pytest assertion, rather than hand-derived.

## 4. The actual wiring point: `ObservingNullRecognitionRule`, not `producer.py`

`CandidateSignalProducer.run_once()` already calls `self._rule.evaluate(bar)` for every newly closed bar
exactly once — `RecognitionRule` is already an INJECTED dependency (Piesa 2's own design, specifically so
alternate implementations can be substituted without touching the producer). I considered adding a second,
parallel `structural_observer` parameter directly to `producer.py` and rejected it: `live_signal_source`
currently has zero dependency on the vendor submodule, and a module-level import of `structural_observer`
from `producer.py` would force that dependency onto every user of `CandidateSignalProducer` at IMPORT
time — even one never given an observer — a real increase in that already-audited, execution-independent
package's fragility surface for no behavioral gain, since the identical effect is reachable through the
seam that already exists.

`ObservingNullRecognitionRule` implements the same `RecognitionRule` Protocol `NullRecognitionRule` does:
`evaluate(bar)` forwards the bar to a `StructuralObserver.observe()` call, then returns `None`
unconditionally — behaviorally identical to `NullRecognitionRule` from the producer's own point of view
("producatorul ramane cu NullRecognitionRule"). **This means zero existing files were modified by this
step** — confirmed by `git status --short`, which shows only new files (`.gitmodules`, the submodule, and
`ai_trader/structural_observer/` itself).

## 5. `liquidity_mechanics` / `institutional_levels`: still out of scope, re-confirmed

Both need a day/week-boundary derivation (a 17:00 New York DST-aware anchor) that exists only as
`resample_ny.py`, an offline, pandas-based, full-history batch script — not a live-callable, per-bar
function. The CEO's own latest message re-confirmed these "raman blocate pe derivarea zi/saptamana" and
instructed reporting the missing decision rather than inventing one. Nothing new investigated here beyond
Step 2's own finding; this section exists only to confirm the exclusion still stands and was not silently
dropped.

## 6. Disclosed limitations (not solved here)

- **In-memory-only bar history**: unlike the bar-feed watermark, the signal journal, or the equity
  high-water mark (all persisted since Mandate 2), this observer's own accumulated OHLCV arrays do not
  survive a process restart. Already-recorded observations remain in the (persisted)
  `StructuralObservationLog`; a restart means detectors needing a deep trailing window (`compression`'s
  460-bar requirement) read `None`/invalid again until enough bars re-accumulate. Not solved — the same
  class of gap Step 2 already flagged for `compression()` specifically, now a property of the whole
  observer.
- **Recompute-from-scratch performance**: every `observe()` call re-runs every detector over the FULL
  accumulated array (Step 2's own disclosed property of the vendored functions, now confirmed to apply to
  every wired detector). A months-long run needs a windowing/truncation strategy eventually; not built.
- **Not yet activated by any entrypoint**: this codebase has no real deployment script that constructs
  `CandidateSignalProducer`/`LiveSignalLoop` together for an actual live run — only tests do, for either
  class, today. Substituting `ObservingNullRecognitionRule` for a bare `NullRecognitionRule()` at whatever
  future entrypoint eventually assembles the live system is what would make structural observation run
  against real bars. That entrypoint is not a decision this mandate made, so this step makes the wiring
  *possible*, not yet *active*.

## 7. Validation

**Scope**: reduced, per the established rule — `structural_observer` is a brand-new, currently-unimported
package, and confirmed (`git status --short`) that zero existing files were modified. Ran the package
itself plus its direct dependencies (`live_signal_source`, `persistent_state`, `live_loop`) rather than
the full tree.

- `pytest ai_trader/structural_observer ai_trader/live_signal_source ai_trader/persistent_state
  ai_trader/live_loop` → **103 passed**, 0 failed.
- `mypy --strict` on the same four packages → **0 errors** (34 source files).
- Git-stash proof, twice (once before `observing_rule.py` was added, once after the package was
  complete): stashed the entire untracked `ai_trader/structural_observer/` directory, confirmed pytest
  genuinely fails (collection finds zero tests — the whole package, including the test files, is gone),
  restored, confirmed all tests pass again.

No modification to any existing, already-committed file. The 227 pre-existing mypy errors elsewhere in
the tree are unaffected and unchanged, as in every prior report.

## 8. Status

Item #7's loop is unchanged and already closed (Step 1). This extension adds pure, disclosed, additive
observation — no signals, no orders, `NullRecognitionRule`-equivalent behavior preserved exactly.
`liquidity_mechanics`/`institutional_levels` remain explicitly blocked, not worked around.

Not authorized to build anything further. Awaiting direction.
