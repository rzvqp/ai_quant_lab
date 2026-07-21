"""TradingView Research Environment (TVRE) -- Phase 2.5.

Turns TradingView Desktop into Alpha's active research workspace: read the chart, indicators
and custom Pine output, navigate symbols/timeframes/replay, add research indicators, author Pine
research tools, draw research objects, and capture screenshots -- all mediated by a strict
capability gate and logged/linked to the current investigation.

Per CEO decision 2026-07-22 the entire TradingView Desktop instance is dedicated to Alpha, so
there is no tab-isolation or workspace-restore requirement; however every important research
action remains logged and linked to its investigation, and the prohibited actions (trades,
broker, alerts, Strategy-Tester-as-evidence, parameter optimization) stay hard-denied.
"""
