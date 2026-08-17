"""SHA-256 pre-install verification for the eventual `ve_tower` wheel -- CEO mandate section 6: "Red Team
verifica SHA-ul... instalezi EXACT acel wheel."

Reuses `ai_trader.mandate2_readiness.wheel_verification.verify_wheel_hash` (the exact primitive already
built and tested for `ve_brain`'s own wheel -- it already takes `expected_sha256` as a parameter, so it
needs no `ve_tower`-specific fork). Run this with the MAIN repo's venv (not the tower venv -- this is an
admin/build-time check, not code the isolated worker itself ever runs), from the repo root, so the
`ai_trader` import resolves normally:

    venv\\Scripts\\python.exe tower_worker\\env\\verify_tower_wheel.py <path-to-wheel> <sha256> <size-bytes>

**2026-08-14, `STAGED_INSTALL_AUTHORIZED`: pin closed.** `ve_tower` 0.3.0's real wheel bytes are committed
at `ai_quant_lab-wp5b` (`ve_tower/release/ve_tower-0.3.0-py3-none-any.whl`, commit `8078c99`, all four
remotes synced to `de7a56f`) -- independently re-hashed here before being written into this pin, matching
`HANDOFF_MANIFEST-0.3.0.json` and Red Team's `RT-TOWER-0006` (`TOWER_ARTIFACT_PASS`) exactly.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from ai_trader.mandate2_readiness.wheel_verification import (  # noqa: E402
    ArtifactHashMismatchError,
    verify_wheel_hash,
)

PINNED_TOWER_WHEEL_SHA256: str = "1abcd60d6e541468a38e68a8b57e4200178585df37b489ff59b0ac99693c28d8"
PINNED_TOWER_WHEEL_SIZE_BYTES: int = 86775
PINNED_TOWER_WHEEL_FILENAME: str = "ve_tower-0.5.2-py3-none-any.whl"
"""RT-TOWER-0010 remediation (2026-08-17, `TOWER_CHAIN_ATR_PASS`): independently re-hashed from the
committed file at `ai_quant_lab-wp5b`'s `ve_tower/release/ve_tower-0.5.2-py3-none-any.whl` (state delivery
commit `60bf71b`) -- matches `HANDOFF_MANIFEST-0.5.2.json`'s own `wheel_sha256`, the release directory's
own `SHA256SUMS.txt`, and this repo's own independent recomputation, all three agreeing. Size read
directly from the committed file (`os.path.getsize`), not copied from anywhere else. Superseded pins
remain in git history (`ve_tower-0.3.0-py3-none-any.whl` @ 77088 bytes, `ve_tower-0.4.0-py3-none-any.whl`,
`ve_tower-0.5.0-py3-none-any.whl` @ 84801 bytes, `ve_tower-0.5.1-py3-none-any.whl`) for rollback."""


def verify_tower_wheel(wheel_path: Path) -> None:
    """Fail-closed: filename, size, and SHA-256 must all match the pin above."""
    if wheel_path.name != PINNED_TOWER_WHEEL_FILENAME:
        raise ArtifactHashMismatchError(
            f"ARTIFACT_HASH_MISMATCH: filename {wheel_path.name!r} != expected {PINNED_TOWER_WHEEL_FILENAME!r}"
        )
    verify_wheel_hash(
        wheel_path, expected_sha256=PINNED_TOWER_WHEEL_SHA256, expected_size_bytes=PINNED_TOWER_WHEEL_SIZE_BYTES,
    )


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: verify_tower_wheel.py <path-to-wheel>", file=sys.stderr)
        return 2
    try:
        verify_tower_wheel(Path(argv[1]))
    except ArtifactHashMismatchError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"OK: {argv[1]} matches the pinned hash.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
