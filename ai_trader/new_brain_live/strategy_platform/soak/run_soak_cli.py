"""CLI entrypoint for the section 36 soak harness -- run as its own OS process (`python -m ai_trader.
new_brain_live.strategy_platform.soak.run_soak_cli`), independent of any interactive session's lifetime,
so a real multi-hour run survives a terminal/conversation ending. Writes its own state under
`new_brain_live_state/strategy_platform_soak/` -- never touches `new_brain_live_state/xauusd_m15.db`
(the real LIVE_SHADOW database) or anything MT5-connected."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ai_trader.new_brain_live.strategy_platform.soak.harness import report_to_json, run_soak

_DEFAULT_STATE_DIR = Path(__file__).resolve().parents[4] / "new_brain_live_state" / "strategy_platform_soak"
_DEFAULT_REPORT_PATH = _DEFAULT_STATE_DIR / "soak_report.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Trader New Brain Architecture section-36 soak harness")
    parser.add_argument("--duration-seconds", type=float, default=6 * 3600.0)
    parser.add_argument("--cycle-interval-seconds", type=float, default=0.5)
    parser.add_argument("--state-dir", type=Path, default=_DEFAULT_STATE_DIR)
    parser.add_argument("--report-path", type=Path, default=_DEFAULT_REPORT_PATH)
    args = parser.parse_args()

    print(
        f"strategy_platform.soak: starting, duration_seconds={args.duration_seconds} "
        f"state_dir={args.state_dir}", flush=True,
    )
    report = run_soak(
        duration_seconds=args.duration_seconds, state_dir=args.state_dir,
        cycle_interval_seconds=args.cycle_interval_seconds,
    )
    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    args.report_path.write_text(report_to_json(report), encoding="utf-8")
    print(f"strategy_platform.soak: finished, report written to {args.report_path}", flush=True)
    print(report_to_json(report), flush=True)

    exit_code = 0 if (not report.exceptions and report.order_send_calls_total == 0) else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
