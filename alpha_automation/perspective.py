"""Perspective Generator -- deterministic rotation of the WHOLE research stance.

CEO refinement #3: this is a distinct component from the Research Task Selector. Its job is
NOT to pick another market window or another question; it is to intentionally vary the entire
research perspective -- the lens, the analytical style, the framing, and the volatility-regime
bias -- so the loop does not converge on a single style of investigation.

Mechanism: each axis advances at a different (co-prime-ish) stride per pass, so the combined
stance cycles through the space without any single axis repeating consecutively. Per-axis
offsets are seeded from the run's master seed (variety across runs, reproducibility within a
run). If the generated stance collides with one of the last K stances (from research memory),
the generator deterministically steps forward until the stance differs on at least the lens
AND the framing -- guaranteeing non-convergence without sacrificing determinism.
"""

from __future__ import annotations

from typing import List, Sequence, Tuple

from . import seeds
from . import schemas

LENSES = [
    "time", "behaviour", "sequence", "structure", "volatility",
    "cross_timeframe", "regime", "anomaly", "falsification",
]
STYLES = ["descriptive_scan", "comparative_contrast", "conditional_slicing",
          "sequence_tracing", "distributional"]
FRAMINGS = ["neutral_observation", "adversarial_falsification", "anomaly_hunt", "regime_conditioned"]
REGIMES = ["any", "low_vol", "high_vol", "trending", "ranging"]

# Per-axis advance strides. Chosen so each axis walks its full cycle and neighbours differ.
_STRIDE = {"lens": 1, "style": 2, "framing": 1, "regime": 3}

StanceTuple = Tuple[str, str, str]  # (lens, style, framing)


class PerspectiveGenerator:
    def __init__(self, master_seed: int):
        self.master_seed = int(master_seed)
        # Stable per-run offsets so different runs explore the space from different phases.
        self._off = {
            axis: seeds.sub_seed(self.master_seed, 0, f"persp_off_{axis}") % len(vals)
            for axis, vals in (
                ("lens", LENSES), ("style", STYLES), ("framing", FRAMINGS), ("regime", REGIMES)
            )
        }

    def _raw_stance(self, step: int) -> dict:
        lens = LENSES[(self._off["lens"] + step * _STRIDE["lens"]) % len(LENSES)]
        style = STYLES[(self._off["style"] + step * _STRIDE["style"]) % len(STYLES)]
        framing = FRAMINGS[(self._off["framing"] + step * _STRIDE["framing"]) % len(FRAMINGS)]
        regime = REGIMES[(self._off["regime"] + step * _STRIDE["regime"]) % len(REGIMES)]
        return {"lens": lens, "style": style, "framing": framing, "regime": regime}

    def generate(self, pass_no: int, recent_stances: Sequence[StanceTuple] = ()) -> dict:
        """Produce the Perspective for `pass_no`, avoiding the given recent stances.

        `recent_stances` is a sequence of (lens, style, framing) tuples (most recent last).
        Returns a schema-valid Perspective dict.
        """
        recent = set(tuple(s) for s in recent_stances)
        step = pass_no
        # Deterministically walk forward until the stance differs on lens AND framing from all
        # recent stances (bounded so we never loop forever; the space is small).
        for _ in range(len(LENSES) * len(FRAMINGS) + 1):
            raw = self._raw_stance(step)
            stance: StanceTuple = (raw["lens"], raw["style"], raw["framing"])
            collides = any(
                (raw["lens"] == r[0] and raw["framing"] == r[2]) for r in recent
            )
            if not collides:
                break
            step += 1
        tf_scope = "cross_tf" if raw["lens"] in ("cross_timeframe",) else "single_tf"
        persp = {
            "perspective_id": f"P{pass_no:04d}",
            "lens": raw["lens"],
            "analytical_style": raw["style"],
            "framing": raw["framing"],
            "regime_bias": raw["regime"],
            "timeframe_scope": tf_scope,
            "rationale": (
                f"Rotated stance for pass {pass_no}: examine the market through a "
                f"{raw['lens']} lens using a {raw['style']} style, framed as "
                f"{raw['framing']}, biased to {raw['regime']} regime. Rotation avoids "
                f"converging on a single investigation style."
            ),
        }
        errs = schemas.validate(persp, schemas.load_schema("perspective"))
        if errs:  # pragma: no cover - internal invariant
            raise AssertionError(f"generated invalid perspective: {errs}")
        return persp

    @staticmethod
    def stance_of(persp: dict) -> StanceTuple:
        return (persp["lens"], persp["analytical_style"], persp["framing"])
