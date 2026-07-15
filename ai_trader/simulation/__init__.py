"""AI Trader Simulation Framework v1 -- Phase 6.7.

Deterministic, no-broker replay of the composed live pipeline (Market Scanner -> Strategy Manager ->
Signal Engine -> Scoring Engine -> Risk Manager -> Execution Engine, unchanged) against historical
data, with the Execution Simulator standing in for the venue and the Portfolio Simulator standing in
for the account. See ``README.md``, ``SIMULATION_HANDOFF.md``, and ``IMPLEMENTATION_CHOICES.md`` in
this package for the frozen design and the documented gap-fill decisions.
"""

from __future__ import annotations
