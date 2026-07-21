"""ResearchEnvironment -- wires the TVRE together and runs one investigation.

This is the entry point the runner uses when config.use_tv_research is on. For one investigation
it: builds the observation dossier (holdout-safe, provenance-logged), invokes Alpha with the
dossier + the allowed action menu + screenshots, and runs the bounded HYBRID follow-up loop --
Alpha may request a small number of additional observations, which are authorized by the
capability gate, executed by the gated client, appended to the dossier, and fed back for up to
`max_followup_rounds` rounds. Returns the final validated Alpha response plus data provenance.

Nothing here can place trades, touch alerts/broker, or read Strategy-Tester results: every action
passes through the capability gate, and denied follow-up requests are refused (recorded), not run.
"""

from __future__ import annotations

from typing import List, Optional

from .. import schemas
from ..adapters.base import AlphaContext
from . import capabilities as caps
from .client import TvClient, TvError
from .mode import ResearchMode
from .workspace import WorkspaceLog
from .dossier import DossierBuilder


class ResearchEnvironment:
    def __init__(self, config, client: TvClient, workspace: WorkspaceLog,
                 context_provider=None, logger=None):
        self.config = config
        self.client = client
        self.workspace = workspace
        self.mode = ResearchMode(config, client)
        self.dossier_builder = DossierBuilder(
            config, client, self.mode, workspace, context_provider=context_provider, logger=logger)
        self.log = logger

    def investigate(self, *, task: dict, window: dict, task_id: str, adapter, mission: str,
                    perspective: dict, prior_questions: List[str]) -> tuple:
        """Run one TVRE investigation. Returns (validated_response, provenance)."""
        dossier = self.dossier_builder.build(task, window, task_id)
        available = caps.allowed_verbs(getattr(self.config, "tv_pine_apply", False))

        followup_rounds = []
        response = self._invoke(adapter, task_id, mission, perspective, task, window,
                                dossier, prior_questions, available)

        rounds = 0
        while rounds < self.config.max_followup_rounds:
            requests = response.get("observation_requests") or []
            if not requests:
                break
            executed = self._execute_followups(requests[: self.config.max_followup_requests], task_id)
            followup_rounds.append(executed)
            dossier = {**dossier, "followups": followup_rounds}
            rounds += 1
            response = self._invoke(adapter, task_id, mission, perspective, task, window,
                                    dossier, prior_questions, available)

        provenance = {
            "data_source": "live_tv",
            "data_regime": dossier.get("data_regime"),
            "validation_eligible": dossier.get("validation_eligible", False),
            "timeframe": window["timeframe"],
            "instrument": self.config.instrument_live,
            "data_split_id": self.config.data_split_id,
            "holdout_cutoff": self.config.holdout_cutoff,
            "followup_rounds": len(followup_rounds),
        }
        return response, provenance

    def _invoke(self, adapter, task_id, mission, perspective, task, window, dossier,
                prior_questions, available) -> dict:
        context = AlphaContext(
            task_id=task_id, mission=mission, perspective=perspective, task=task, window=window,
            data_summary=dossier, prior_questions=prior_questions,
            available_actions=available, screenshots=list(dossier.get("screenshots", [])),
        )
        return adapter.investigate(context)

    def _execute_followups(self, requests: list, task_id: str) -> list:
        out = []
        schema = schemas.load_schema("tv_action_request")
        for req in requests:
            errs = schemas.validate(req, schema)
            if errs:
                out.append({"request": req, "ok": False, "denied": True, "reason": f"invalid request: {errs}"})
                continue
            verb, params, why = req["verb"], req.get("params", {}), req.get("why")
            try:
                caps.check(verb, pine_apply=getattr(self.config, "tv_pine_apply", False))
            except caps.CapabilityDenied as e:
                out.append({"verb": verb, "why": why, "ok": False, "denied": True, "reason": e.reason})
                if self.log:
                    self.log.warn("followup_denied", verb=verb, reason=e.reason)
                continue
            try:
                result = self.client.call(verb, params, task_id=task_id)
                out.append({"verb": verb, "why": why, "ok": True, "result": result})
            except TvError as e:
                out.append({"verb": verb, "why": why, "ok": False, "denied": False, "reason": str(e)})
        return out
