"""Research-mode / holdout guard -- the load-bearing holdout control for TVRE.

Because Alpha now operates the live TradingView chart directly (which shows data past the
holdout cutoff), the holdout discipline is enforced here, fail-closed:

  replay_pre_cutoff : the only holdout-safe discovery mode. Enters TradingView Replay anchored at
                      the (pre-holdout) window start, and before ANY observation verifies replay
                      is started and the replay cursor is strictly < cutoff. A cursor at/after the
                      cutoff raises HoldoutViolation (never silently observed).
  live_observation  : observes current/live data (post-holdout) for discovery only. Every record
                      is tagged data_regime="live_post_holdout" and marked never-usable-as-
                      validation. No replay required.

Window selection already guarantees pre-holdout windows; this guard is the second, independent
check at observation time.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from .client import TvClient


class HoldoutViolation(RuntimeError):
    pass


def _parse(iso: str) -> datetime:
    return datetime.fromisoformat(iso)


def _to_dt(value) -> Optional[datetime]:
    """Replay status current_date may be unix seconds or an ISO string; normalize to aware dt."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        from datetime import timezone
        return datetime.fromtimestamp(float(value), tz=timezone.utc)
    try:
        return _parse(str(value))
    except ValueError:
        return None


class ResearchMode:
    def __init__(self, config, client: TvClient):
        self.config = config
        self.client = client
        self.mode = config.research_mode
        self.cutoff = _parse(config.holdout_cutoff)

    @property
    def data_regime(self) -> str:
        return "pre_holdout_replay" if self.mode == "replay_pre_cutoff" else "live_post_holdout"

    def prepare(self, window: dict, *, task_id: Optional[str] = None) -> dict:
        """Put the workspace into the correct mode for this window. Returns a provenance dict."""
        if self.mode == "live_observation":
            return {"mode": self.mode, "data_regime": self.data_regime,
                    "validation_eligible": False, "note": "live post-holdout observation; never validation"}

        # replay_pre_cutoff: anchor replay at the window start date (YYYY-MM-DD), then verify.
        start_date = window["start"][:10]
        # Defensive: the window must already be pre-holdout (selector guarantees it).
        if _parse(window["end"]) >= self.cutoff:
            raise HoldoutViolation(
                f"window end {window['end']} is at/after holdout cutoff {self.config.holdout_cutoff}")
        self.client.call("replay_start", {"date": start_date}, task_id=task_id)
        self.verify(task_id=task_id)
        return {"mode": self.mode, "data_regime": self.data_regime,
                "validation_eligible": False, "replay_anchor": start_date,
                "note": "pre-holdout replay observation"}

    def verify(self, *, task_id: Optional[str] = None) -> None:
        """Fail-closed check that the current replay cursor is strictly before the cutoff."""
        if self.mode != "replay_pre_cutoff":
            return
        status = self.client.call("replay_status", {}, task_id=task_id)
        if not status.get("is_replay_started"):
            raise HoldoutViolation("replay is not started -- refusing to observe live data in replay mode")
        cur = _to_dt(status.get("current_date"))
        if cur is None:
            raise HoldoutViolation("replay current_date unavailable -- cannot verify holdout safety (fail-closed)")
        if cur >= self.cutoff:
            raise HoldoutViolation(
                f"replay cursor {cur.isoformat()} is at/after holdout cutoff {self.config.holdout_cutoff}")

    def step_safely(self, *, task_id: Optional[str] = None) -> dict:
        """Advance one replay bar, then re-verify holdout safety before the caller observes."""
        if self.mode != "replay_pre_cutoff":
            raise HoldoutViolation("step_safely is only valid in replay_pre_cutoff mode")
        res = self.client.call("replay_step", {}, task_id=task_id)
        self.verify(task_id=task_id)
        return res
