"""TvClient -- gated, logged Python facade over the TradingView research bridge.

Every research action goes through this client, which (1) authorizes the verb via the capability
gate, (2) executes it through the Node bridge (single or batch), and (3) logs the action linked
to the current investigation. Alpha never calls the bridge directly; the orchestrator translates
Alpha's structured follow-up requests into gated client calls.

The subprocess call is injectable (`run`) so the whole client is unit-testable without a live
TradingView instance.
"""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, List, Optional, Sequence, Tuple

from . import capabilities as caps

_BRIDGE = Path(__file__).resolve().parent / "bridge" / "tv_exec.mjs"


class TvError(RuntimeError):
    def __init__(self, verb: str, message: str, code: Optional[str] = None):
        self.verb = verb
        self.code = code
        super().__init__(f"tv verb {verb!r} failed: {message}" + (f" [{code}]" if code else ""))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _summarize_params(params: Optional[dict]) -> dict:
    """A compact, log-safe view of params (avoid dumping large Pine sources into the action log)."""
    if not params:
        return {}
    out = {}
    for k, v in params.items():
        if isinstance(v, str) and len(v) > 120:
            out[k] = f"<{len(v)} chars>"
        else:
            out[k] = v
    return out


class TvClient:
    def __init__(self, config, action_log: Optional[Callable[[dict], None]] = None,
                 run: Optional[Callable[[dict], dict]] = None):
        self.config = config
        self._action_log = action_log
        self._run = run or self._default_run
        self._pine_apply = bool(getattr(config, "tv_pine_apply", False))

    # ---------- subprocess ----------
    def _default_run(self, request: dict) -> dict:
        env = dict(os.environ, TV_MCP_DIR=self.config.tv_mcp_dir)
        proc = subprocess.run(
            ["node", str(_BRIDGE)],
            input=json.dumps(request), capture_output=True, text=True, env=env, timeout=180,
        )
        if proc.returncode != 0:
            raise TvError(request.get("verb", "batch"), f"bridge rc={proc.returncode}: {proc.stderr.strip()[:300]}")
        lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
        if not lines:
            raise TvError(request.get("verb", "batch"), "bridge produced no output")
        return json.loads(lines[-1])

    # ---------- logging ----------
    def _log(self, task_id: Optional[str], verb: str, params: Optional[dict], ok: bool,
             error: Optional[str] = None, code: Optional[str] = None) -> None:
        if not self._action_log:
            return
        self._action_log({
            "task_id": task_id,
            "verb": verb,
            "capability": caps.classify(verb),
            "mutating": caps.is_mutating(verb),
            "params": _summarize_params(params),
            "ok": ok,
            "error": error,
            "code": code,
            "ts": _now(),
        })

    # ---------- calls ----------
    def call(self, verb: str, params: Optional[dict] = None, *, task_id: Optional[str] = None) -> dict:
        caps.check(verb, pine_apply=self._pine_apply)  # authorize (raises CapabilityDenied)
        resp = self._run({"verb": verb, "params": params or {}})
        if not resp.get("ok"):
            err, code = resp.get("error", "unknown error"), resp.get("code")
            self._log(task_id, verb, params, ok=False, error=err, code=code)
            raise TvError(verb, err, code)
        self._log(task_id, verb, params, ok=True)
        return resp.get("result", {})

    def batch(self, ops: Sequence[Tuple[str, Optional[dict]]], *, task_id: Optional[str] = None,
              strict: bool = True) -> List[dict]:
        """Execute several verbs over one connection. Authorizes ALL verbs before executing any."""
        for verb, _ in ops:
            caps.check(verb, pine_apply=self._pine_apply)
        request = {"batch": [{"verb": v, "params": p or {}} for v, p in ops]}
        resp = self._run(request)
        results = resp.get("results", [])
        out: List[dict] = []
        for (verb, params), r in zip(ops, results):
            ok = bool(r.get("ok"))
            self._log(task_id, verb, params, ok=ok, error=r.get("error"), code=r.get("code"))
            if not ok and strict:
                raise TvError(verb, r.get("error", "unknown error"), r.get("code"))
            out.append(r)
        return out

    def try_call(self, verb: str, params: Optional[dict] = None, *, task_id: Optional[str] = None):
        """Best-effort call: returns result dict or None on failure (failure is logged, not raised)."""
        try:
            return self.call(verb, params, task_id=task_id)
        except (TvError, caps.CapabilityDenied):
            return None

    def health(self) -> bool:
        try:
            resp = self._run({"verb": "health", "params": {}})
            return bool(resp.get("ok"))
        except Exception:
            return False
