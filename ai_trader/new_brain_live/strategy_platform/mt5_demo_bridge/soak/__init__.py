"""S5 MT5 DEMO unattended operational soak (mandate `AI-TRADER-S5-MT5-DEMO-UNATTENDED-SOAK-001`).
Orchestrates the already-built `mt5_demo_bridge` execution path continuously, with restart
reconciliation, position lifecycle tracking, a persisted safety-stop monitor, checkpoints, and health
snapshots -- see `soak_loop.py`'s own module docstring for the full design."""
