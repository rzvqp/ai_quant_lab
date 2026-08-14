"""Isolated worker process hosting `ve_tower` (N3/N4) behind a versioned local IPC boundary.

CEO mandate, 2026-08-14: "TOWER WORKER IZOLAT. Forma same-process e PROHIBITA." This package never
imports `ai_trader`, is never installed into the AI Trader venv, and is always launched with its own
interpreter, its own venv, `-I` isolated mode, a cleared `PYTHONPATH`, and a working directory outside the
AI Trader repository -- see `env/launch_tower_worker.ps1` and `startup_audit.py`.

Produces N3 and N4 ONLY. Never a decision, never an order, never broker access.
"""

from __future__ import annotations
