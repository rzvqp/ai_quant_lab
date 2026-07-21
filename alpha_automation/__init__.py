"""Alpha Automation v1.0 -- persistent Continuous Discovery orchestrator for the Alpha
research division of the AI Quant Lab.

This package turns Alpha (a falsification-first market-research process governed by
EDGE_RESEARCH_PROTOCOL.md) from a manually-prompted chat workflow into an autonomous,
restartable research loop.

Scientific boundary (unchanged from Alpha's charter): Alpha OBSERVES, COMPARES, QUESTIONS,
and produces DISCOVERY CANDIDATES only. It does NOT validate profitability, optimize
parameters, run strategy backtests as proof of edge, design strategies, or claim causality.

Phase 2 scope (this delivery): the minimum working orchestrator -- generate a research
perspective, select a task and a market window, obtain data (live TradingView primary,
local CSV fallback), invoke Alpha through a structured adapter, validate the response
against a schema, persist it, repeat for a bounded number of passes, and resume after
restart. Candidate freeze/hash/handoff (Phase 3) and continuous mode (Phase 4) are NOT
included here.
"""

__version__ = "1.0.0-phase2"

PACKAGE_NAME = "alpha_automation"
