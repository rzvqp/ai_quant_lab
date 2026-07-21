"""Deterministic seed derivation -- pure stdlib.

Every research pass derives its own seed deterministically from the run's master seed and
the pass number, so a run is fully reproducible and a resumed run reproduces the exact same
perspective/task/window choices for a given pass. No wall-clock or OS entropy is used here.
"""

from __future__ import annotations

import hashlib
import random


def pass_seed(master_seed: int, pass_no: int) -> int:
    """Derive a stable 63-bit integer seed for a given pass from the master seed.

    Deterministic: (master_seed, pass_no) -> same integer, every time, on every machine.
    """
    raw = f"{int(master_seed)}:{int(pass_no)}".encode("utf-8")
    digest = hashlib.sha256(raw).digest()
    # 8 bytes -> unsigned 64-bit, masked to 63 bits so it is always a positive int.
    return int.from_bytes(digest[:8], "big") & ((1 << 63) - 1)


def rng_for(master_seed: int, pass_no: int) -> random.Random:
    """A seeded random.Random for a pass. Isolated instance -- never touches global RNG state."""
    return random.Random(pass_seed(master_seed, pass_no))


def sub_seed(master_seed: int, pass_no: int, label: str) -> int:
    """A labelled sub-seed so independent selectors within one pass do not share an RNG stream."""
    raw = f"{int(master_seed)}:{int(pass_no)}:{label}".encode("utf-8")
    return int.from_bytes(hashlib.sha256(raw).digest()[:8], "big") & ((1 << 63) - 1)


def rng_labelled(master_seed: int, pass_no: int, label: str) -> random.Random:
    return random.Random(sub_seed(master_seed, pass_no, label))
