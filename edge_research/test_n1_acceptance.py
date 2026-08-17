"""N1 HANDOFF ACCEPTANCE SUITE — Alpha Discovery (Flow B).

These are CONTRACT tests for the canonical N1 producer (`RawAxesBuilder` -> `ve_brain.RawAxes` ->
`ve_brain.StrategyRouter`, owned by AI Trader, commit `a98a0a4`). They gate the moment Alpha is allowed
to consume the official producer for a canonical rerun. See `reports/N1_HANDOFF_INVENTORY.md`.

**DELIBERATELY BLOCKED.** Every behavioural test below is skipped with reason `BLOCKED_ON_N1_ARTIFACT`
until AI Trader delivers a *versioned replay/research artifact* exposing `observe(bar) -> RawAxes` (+
`applicable_regimes`, `StrategyRouter`) that Alpha can import WITHOUT reaching into `ai_trader.*` live
code. We do NOT:
  - recreate `RawAxesBuilder` (its logic is AI Trader's; a copy would fork and drift),
  - copy `structural_observer.vendor_bridge` (the detector pin `61cbd58` must stay single-sourced),
  - invent fixture outputs (the AUTHORITATIVE fixture expectations arrive WITH the artifact).

The artifact is discovered via the env var `ALPHA_N1_ARTIFACT` (an importable module name or a path the
handoff will define). Until it resolves, `_artifact()` returns None and the behavioural tests skip.

Two invariants (§13, §14) are ACTIVE now — they are Alpha-repo hygiene guards that must hold forever,
independent of the artifact: Alpha must never import `ai_trader.*`, and must never vendor a duplicate of
the frozen detectors. Those two run and must pass today.
"""
from __future__ import annotations

import os
import pathlib

import pytest

BLOCKED = "BLOCKED_ON_N1_ARTIFACT: awaiting AI Trader versioned replay artifact (see N1_HANDOFF_INVENTORY.md)"

# The identity Alpha will pin the delivered artifact against (from the corrected inventory). Any mismatch
# at handoff time is a REFUSAL, not a warning — encoded as the expected values §9-§11 will assert.
EXPECTED_N1_CONTRACT = "n1-additive-raw-axes-v1"
EXPECTED_ROUTER_VERSION = "router-v1"
EXPECTED_VE_BRAIN_VERSION = "0.1.3"
EXPECTED_VE_BRAIN_WHEEL_SHA = "edd208ad6c2c943b17a11759ece1fdf5ab2a7025779b191764c383ecce987d11"
EXPECTED_DETECTOR_PIN = "61cbd58c3d5da19001b125b65d669ddad54a14c4"


def _artifact():
    """Resolve the official N1 replay artifact, or None if not delivered yet. NEVER falls back to a
    hand-built substitute — absence means the suite stays blocked, by design."""
    name = os.environ.get("ALPHA_N1_ARTIFACT")
    if not name:
        return None
    try:
        import importlib
        return importlib.import_module(name)
    except Exception:
        return None


requires_n1 = pytest.mark.skipif(_artifact() is None, reason=BLOCKED)


# ─────────────────────────────────────────────────────────────────────────────────────────────────────
# BEHAVIOURAL CONTRACT — all BLOCKED_ON_N1_ARTIFACT until the artifact is delivered.
# Each test documents the property; the body uses ONLY the artifact's own API + its own authoritative
# fixtures (art.fixtures()), never Alpha-invented bars or expected outputs.
# ─────────────────────────────────────────────────────────────────────────────────────────────────────

@requires_n1
def test_01_same_bars_same_raw_axes_live_and_replay():
    """Same closed-bar sequence -> byte-identical RawAxes in live and replay modes."""
    art = _artifact()
    fx = art.fixtures()  # authoritative, ships WITH the artifact
    live = [art.observe_live(b) for b in fx.bars]
    replay = art.replay(fx.bars)
    assert live == replay == fx.expected_raw_axes


@requires_n1
def test_02_only_closed_bars_accepted():
    """A forming (un-closed) bar is rejected fail-closed, never silently normalized."""
    art = _artifact()
    with pytest.raises(art.BarNotClosedError):
        art.observe_live(art.fixtures().forming_bar)


@requires_n1
def test_03_zero_lookahead():
    """RawAxes at bar i is a function of bars <= i only. Truncating the tail cannot change earlier axes."""
    art = _artifact()
    fx = art.fixtures()
    full = art.replay(fx.bars)
    for i in range(1, len(fx.bars)):
        assert art.replay(fx.bars[:i]) == full[:i]


@requires_n1
def test_04_bar_order_validated():
    """Out-of-order (decreasing ts) bars are rejected fail-closed."""
    art = _artifact()
    with pytest.raises(art.BarOrderError):
        art.replay(art.fixtures().out_of_order_bars)


@requires_n1
def test_05_duplicate_bar_processed_once():
    """A duplicated bar (same ts) is idempotent — processed exactly once."""
    art = _artifact()
    fx = art.fixtures()
    assert art.replay(fx.bars_with_one_duplicate) == art.replay(fx.bars)


@requires_n1
def test_06_restart_preserves_needed_state():
    """State snapshot/restore reproduces the exact post-restart RawAxes (accumulation survives restart)."""
    art = _artifact()
    fx = art.fixtures()
    mid = len(fx.bars) // 2
    b = art.builder(fx.symbol)
    for bar in fx.bars[:mid]:
        b.observe(bar)
    resumed = art.builder_from_state(b.snapshot())
    tail = [resumed.observe(bar) for bar in fx.bars[mid:]]
    assert tail == art.replay(fx.bars)[mid:]


@requires_n1
def test_07_stale_data_fails_closed():
    """Data older than the contract's max staleness -> UNAVAILABLE / fail-closed, never a stale RawAxes."""
    art = _artifact()
    res = art.observe_with_clock(art.fixtures().stale_bar, now=art.fixtures().much_later_ts)
    assert res.unavailable and res.reason == "DATA_STALE"


@requires_n1
def test_08_incompatible_contract_fails_closed():
    """A RawAxes schema the client wasn't built against -> fail-closed refusal."""
    art = _artifact()
    with pytest.raises(art.ContractIncompatibleError):
        art.assert_contract("some-future-raw-axes-vNEXT")


@requires_n1
def test_09_different_detector_pin_is_refused():
    """A detector-submodule commit != the pinned 61cbd58 -> refuse to run."""
    art = _artifact()
    assert art.detector_pin() == EXPECTED_DETECTOR_PIN
    with pytest.raises(art.DetectorPinMismatch):
        art.assert_detector_pin("0000000000000000000000000000000000000000")


@requires_n1
def test_10_different_n1_version_is_refused():
    """N1 contract version != n1-additive-raw-axes-v1 -> refuse."""
    art = _artifact()
    assert art.n1_contract_version() == EXPECTED_N1_CONTRACT
    with pytest.raises(art.N1VersionMismatch):
        art.assert_n1_version("n1-additive-raw-axes-v2")


@requires_n1
def test_11_different_configuration_fingerprint_is_refused():
    """A configuration fingerprint (detector pin + windows + break-map) that differs -> refuse."""
    art = _artifact()
    good = art.configuration_fingerprint()
    with pytest.raises(art.ConfigurationFingerprintMismatch):
        art.assert_configuration_fingerprint(good[::-1])


@requires_n1
def test_12_identical_raw_axes_same_applicable_regimes():
    """Identical RawAxes -> StrategyRouter yields identical applicable_regimes (router determinism)."""
    art = _artifact()
    fx = art.fixtures()
    for axes in fx.expected_raw_axes:
        assert art.applicable_regimes(axes) == art.applicable_regimes(axes)
    assert art.applicable_regimes(fx.trend_up_axes) == frozenset({art.TREND_UP})


# ─────────────────────────────────────────────────────────────────────────────────────────────────────
# ALPHA-REPO HYGIENE — ACTIVE NOW (must hold forever, artifact or not).
# ─────────────────────────────────────────────────────────────────────────────────────────────────────

def _alpha_py_files():
    root = pathlib.Path(__file__).resolve().parent
    return [p for p in root.rglob("*.py") if p.name != "test_n1_acceptance.py"]


def test_13_zero_local_path_import_from_ai_trader():
    """Alpha must NEVER import ai_trader.* nor path-insert the AI Trader repo. The canonical producer is
    consumed ONLY through the future versioned artifact, never by reaching into the live repo."""
    offenders = []
    for p in _alpha_py_files():
        txt = p.read_text(encoding="utf-8", errors="ignore")
        for ln, line in enumerate(txt.splitlines(), 1):
            s = line.strip()
            if s.startswith("#"):
                continue
            if "import ai_trader" in s or "from ai_trader" in s:
                offenders.append(f"{p.name}:{ln}: {s}")
            if "ai_quant_lab-research-main" in s and ("sys.path" in s or "insert" in s or "append" in s):
                offenders.append(f"{p.name}:{ln}: local-path insert into AI Trader repo")
    assert not offenders, "forbidden AI Trader imports/path-inserts:\n" + "\n".join(offenders)


def test_14_zero_duplicate_detector_in_alpha():
    """Alpha must NOT vendor a second copy of the frozen structural detectors (single-source the pin).
    A duplicated detector would silently diverge from 61cbd58 — exactly what the submodule pin prevents."""
    root = pathlib.Path(__file__).resolve().parent
    forbidden_copies = [
        p for p in root.rglob("vendor_bridge.py")
    ] + [
        p for p in root.rglob("*.py")
        if p.name in {"market_structure.py", "market_state.py"}
        and "def detect_swings" in p.read_text(encoding="utf-8", errors="ignore")
    ]
    assert not forbidden_copies, (
        "duplicate detector source found in Alpha (must consume via the pinned artifact, not a copy): "
        + ", ".join(str(p) for p in forbidden_copies)
    )
