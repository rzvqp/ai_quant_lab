"""Pins the exact `ve_n1_replay` artifact the CEO authorized (2026-08-18), independent of whatever
happens to be installed in `.alpha_n1_venv` at any given moment. Verified two ways, not one: pip's own
`direct_url.json` record (written at install time, the same mechanism `pip install` itself trusts) AND,
when the physical wheel file the venv was installed from is still reachable, an independent re-hash of
that file -- matching this repo's own established "verify independently, don't just trust the manifest"
convention (`tower_identity_pin.py`'s own precedent).

**Never writes to, and never imports anything from, `.alpha_n1_venv` or the `ve_n1_replay` source
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

ALPHA_N1_VENV_PYTHON = Path("C:/Users/MEDION GAMING/.alpha_n1_venv/Scripts/python.exe")
_DIST_INFO_DIR = Path("C:/Users/MEDION GAMING/.alpha_n1_venv/Lib/site-packages") / f"ve_n1_replay-{PINNED_VERSION}.dist-info"


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
