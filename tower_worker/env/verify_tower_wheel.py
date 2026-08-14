"""SHA-256 pre-install verification for the eventual `ve_tower` wheel -- CEO mandate section 6: "Red Team
verifica SHA-ul... instalezi EXACT acel wheel."

Reuses `ai_trader.mandate2_readiness.wheel_verification.verify_wheel_hash` (the exact primitive already
built and tested for `ve_brain`'s own wheel -- it already takes `expected_sha256` as a parameter, so it
needs no `ve_tower`-specific fork). Run this with the MAIN repo's venv (not the tower venv -- this is an
admin/build-time check, not code the isolated worker itself ever runs), from the repo root, so the
`ai_trader` import resolves normally:

    venv\\Scripts\\python.exe tower_worker\\env\\verify_tower_wheel.py <path-to-wheel> <sha256> <size-bytes>

**`PINNED_TOWER_WHEEL_SHA256` is deliberately `None` today.** No repaired `ve_tower` wheel exists yet
(0.1.0 was rejected, `TOWER_HANDOFF_FAIL`). Once Red Team verifies a delivered wheel's hash, that value
(plus size and filename) goes here, exactly once, as the new pin -- never accepted from the command line
alone without also being written back into this file, so the pin itself stays under version control and
auditable, the same discipline `wheel_verification.py`'s own `PINNED_WHEEL_SHA256` already established for
`ve_brain`.
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

PINNED_TOWER_WHEEL_SHA256: str | None = None
PINNED_TOWER_WHEEL_SIZE_BYTES: int | None = None
PINNED_TOWER_WHEEL_FILENAME: str | None = None


def verify_tower_wheel(wheel_path: Path) -> None:
    """Fail-closed on two independent grounds: no pin recorded yet (nothing to compare against -- refuses
    rather than silently accepting anything), and the reused `verify_wheel_hash`'s own filename/size/hash
    checks once a pin exists."""
    if PINNED_TOWER_WHEEL_SHA256 is None:
        raise ArtifactHashMismatchError(
            "ARTIFACT_HASH_MISMATCH: no PINNED_TOWER_WHEEL_SHA256 recorded yet -- "
            "Red Team must verify and record the pin in this file before any install."
        )
    if wheel_path.name != PINNED_TOWER_WHEEL_FILENAME:
        raise ArtifactHashMismatchError(
            f"ARTIFACT_HASH_MISMATCH: filename {wheel_path.name!r} != expected {PINNED_TOWER_WHEEL_FILENAME!r}"
        )
    verify_wheel_hash(wheel_path, expected_sha256=PINNED_TOWER_WHEEL_SHA256)


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
