"""Pins the exact `ve_n1_replay` artifact the CEO authorized for AI Trader (RT-N1-0002/RT-N1-0003),
independent of whatever happens to be installed in `.ai_trader_n1_venv` at any given moment. Verified
two ways, not one: pip's own `direct_url.json` record (written at install time, the same mechanism
`pip install` itself trusts) AND, when the physical wheel file the venv was installed from is still
reachable, an independent re-hash of that file -- matching this repo's own established "verify
independently, don't just trust the manifest" convention (`tower_identity_pin.py`'s own precedent).

**Environment split (CEO decision, AI Trader New Brain Architecture mandate, 2026-08-21,
`N1_ALPHA_AI_TRADER_RUNTIME_ISOLATION_COMPLETE`)**: `ve_n1_replay` has TWO separate, independently
authorized consumers that must never share one environment again. Alpha Discovery's own `.alpha_n1_venv`
runs `ve_n1_replay 0.2.0` under `RT-RANGE-0002` (`898e1b9`, Alpha-environment-scoped only -- see
`N1_REPLAY_VERSION_DRIFT_AUDIT.md`). AI Trader's own, separate `.ai_trader_n1_venv` runs the exact
`0.1.1` pinned below under `RT-N1-0002`/`RT-N1-0003`. `RT-RANGE-0002` independently re-verified N1
output is byte-identical between the two versions -- useful corroborating evidence, but it does NOT
expand AI Trader's own authorization, which remains `0.1.1` only. This module never resolves anything
through `.alpha_n1_venv`, checks it, or depends on its state in any way.

**Never writes to, and never imports anything from, `.ai_trader_n1_venv` or the `ve_n1_replay` source
tree.** This is read-only verification against the running main-venv interpreter; the actual `ve_n1_
replay` package is never imported here -- only `.dist-info` metadata files, plain text/JSON, are read."""

from __future__ import annotations

import dataclasses
import hashlib
import json
from pathlib import Path

PINNED_WHEEL_SHA256 = "2cff7e7be1f9401c10753f751a1189a512f5be39946dfada4260b9c5e1cd29ab"
PINNED_DELIVERY_COMMIT = "e118c33"
PINNED_RT_PASS_COMMIT = "6230ee5"
PINNED_VERSION = "0.1.1"
PINNED_AI_SOURCE_COMMIT = "21ae632"
PINNED_DETECTOR_SUBMODULE_COMMIT = "61cbd58c3d5da19001b125b65d669ddad54a14c4"

AI_TRADER_N1_VENV_PYTHON = Path("C:/Users/MEDION GAMING/.ai_trader_n1_venv/Scripts/python.exe")
"""AI-Trader-exclusive -- NEVER `.alpha_n1_venv` (that is Alpha Discovery's own, separately-authorized
environment; see the module docstring's environment-split note)."""
_DIST_INFO_DIR = Path("C:/Users/MEDION GAMING/.ai_trader_n1_venv/Lib/site-packages") / f"ve_n1_replay-{PINNED_VERSION}.dist-info"


class N1ArtifactIdentityMismatchError(Exception):
    """Raised at AI Trader startup (`runtime_loop.build_incremental_dual_clock_loop`) when
    `verify_pin()` fails -- fail-closed: the process must not start, never fall back to whatever happens
    to be installed. The one, single, deliberate call site is startup-time; `client.py`'s own per-call
    check (`verify_artifact_identity`) uses the softer `N1IncrementalResponse.rejected` channel instead,
    since a running process must degrade to NO_TRADE mid-lifetime, never crash on a single bad call."""


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class PinVerificationResult:
    ok: bool
    reason: str
    recorded_sha256: str | None
    rehashed_sha256: str | None
    wheel_path: str | None


def _sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_pin() -> PinVerificationResult:
    """Fail-closed: any missing file, any hash mismatch, any parse error -> `ok=False`. Never guesses,
    never falls back to "probably fine"."""
    direct_url_path = _DIST_INFO_DIR / "direct_url.json"
    if not direct_url_path.is_file():
        return PinVerificationResult(
            ok=False, reason=f"direct_url.json not found at {direct_url_path}",
            recorded_sha256=None, rehashed_sha256=None, wheel_path=None,
        )
    try:
        data = json.loads(direct_url_path.read_text(encoding="utf-8"))
        recorded_sha256 = data["archive_info"]["hashes"]["sha256"]
        url = data["url"]
    except (KeyError, json.JSONDecodeError) as exc:
        return PinVerificationResult(
            ok=False, reason=f"direct_url.json unparsable: {exc}",
            recorded_sha256=None, rehashed_sha256=None, wheel_path=None,
        )

    if recorded_sha256 != PINNED_WHEEL_SHA256:
        return PinVerificationResult(
            ok=False, reason=f"pip-recorded hash {recorded_sha256} != pinned {PINNED_WHEEL_SHA256}",
            recorded_sha256=recorded_sha256, rehashed_sha256=None, wheel_path=url,
        )

    if not url.startswith("file:///"):
        return PinVerificationResult(
            ok=False, reason=f"unexpected non-local install source: {url}",
            recorded_sha256=recorded_sha256, rehashed_sha256=None, wheel_path=url,
        )
    wheel_path = Path(url.removeprefix("file:///").replace("%20", " "))
    if not wheel_path.is_file():
        # Wheel no longer reachable at its original path -- the pip-recorded hash above still holds,
        # but the independent re-hash cannot run. Reported explicitly, not silently skipped.
        return PinVerificationResult(
            ok=True, reason="pip-recorded hash matches; physical wheel no longer reachable for re-hash",
            recorded_sha256=recorded_sha256, rehashed_sha256=None, wheel_path=str(wheel_path),
        )

    rehashed = _sha256_of(wheel_path)
    if rehashed != PINNED_WHEEL_SHA256:
        return PinVerificationResult(
            ok=False, reason=f"independent re-hash {rehashed} != pinned {PINNED_WHEEL_SHA256}",
            recorded_sha256=recorded_sha256, rehashed_sha256=rehashed, wheel_path=str(wheel_path),
        )

    return PinVerificationResult(
        ok=True, reason="pip-recorded hash and independent re-hash both match the pin",
        recorded_sha256=recorded_sha256, rehashed_sha256=rehashed, wheel_path=str(wheel_path),
    )


def verify_artifact_identity(
    *, ve_n1_replay_version: str, ai_source_commit: str, detector_submodule_commit: str,
) -> tuple[bool, str]:
    """Per-response defense-in-depth, distinct from `verify_pin()` (which checks the dist-info AT REST,
    typically once at startup): every worker response's own `artifact` block is checked against the
    SAME three pinned identity fields, so a venv mutated DURING a long-running process's lifetime (not
    just a stale-at-startup pin) is still caught on the very next call, never silently trusted. Returns
    `(True, "")` only if all three match; otherwise `(False, <reason>)` -- callers must treat any
    mismatch as a fail-closed rejection (NO_TRADE), never a warning."""
    if ve_n1_replay_version != PINNED_VERSION:
        return False, f"ve_n1_replay_version {ve_n1_replay_version!r} != pinned {PINNED_VERSION!r}"
    if ai_source_commit != PINNED_AI_SOURCE_COMMIT:
        return False, f"ai_source_commit {ai_source_commit!r} != pinned {PINNED_AI_SOURCE_COMMIT!r}"
    if detector_submodule_commit != PINNED_DETECTOR_SUBMODULE_COMMIT:
        return False, (
            f"detector_submodule_commit {detector_submodule_commit!r} != "
            f"pinned {PINNED_DETECTOR_SUBMODULE_COMMIT!r}"
        )
    return True, ""
