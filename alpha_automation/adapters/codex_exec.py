"""Codex adapter -- invokes Alpha's reasoning via the locally-installed `codex exec` CLI.

This satisfies the CEO directive to reuse existing lab infrastructure for the execution path
rather than introducing an external Anthropic/OpenAI Python SDK: `codex` is already installed
locally. The adapter shells out to `codex exec`, passing the mission + question + data summary +
prior questions + a strict output contract on stdin, and reads a single JSON object back.

The subprocess call is injectable (`run` param) so the prompt-building and JSON-extraction paths
are unit-testable without invoking the real CLI. Live wiring (auth, model selection, sandbox
flags) is exercised in Phase 4, not here.
"""

from __future__ import annotations

import json
import subprocess
from typing import Callable, List, Optional

from .base import AlphaAdapter, AlphaContext, AlphaAdapterError
from .. import schemas

RunFn = Callable[[str, Optional[str], float], str]


def _default_run(prompt: str, model: Optional[str], timeout_s: float) -> str:
    cmd = ["codex", "exec"]
    if model:
        cmd += ["-m", model]
    # Read the prompt from stdin ('-'), keep the agent from touching the repo, ask for full-auto
    # non-interactive execution. These flags are conservative; Phase 4 finalizes them against the
    # installed codex version.
    cmd += ["-"]
    proc = subprocess.run(
        cmd,
        input=prompt,
        capture_output=True,
        text=True,
        timeout=timeout_s,
    )
    if proc.returncode != 0:
        raise AlphaAdapterError(
            f"codex exec failed (rc={proc.returncode}): {proc.stderr.strip()[:500]}")
    return proc.stdout


class CodexAdapter(AlphaAdapter):
    name = "codex"

    def __init__(self, config, run: Optional[RunFn] = None):
        self.config = config
        self.max_retries = config.adapter_max_retries
        self._run = run or _default_run
        self._model = config.codex_model
        self._timeout = config.codex_timeout_s

    def build_prompt(self, context: AlphaContext) -> str:
        schema = schemas.load_schema("alpha_response")
        prior = context.prior_questions[-40:]
        parts = [
            context.mission,
            "\n--- CURRENT PERSPECTIVE (research stance) ---",
            json.dumps(context.perspective, indent=2),
            "\n--- CURRENT INVESTIGATION QUESTION ---",
            f"task_id: {context.task_id}",
            context.task.get("question", ""),
            "\n--- MARKET WINDOW ---",
            json.dumps(context.window, indent=2, default=str),
            "\n--- MARKET DATA SUMMARY (descriptive; derived from the window) ---",
            json.dumps(context.data_summary, indent=2, default=str),
            "\n--- PREVIOUSLY ASKED QUESTIONS (avoid restating these) ---",
            json.dumps(prior, indent=2),
            "\n--- REQUIRED OUTPUT ---",
            "Respond with EXACTLY ONE JSON object and nothing else. It MUST validate against "
            "this JSON schema:",
            json.dumps(schema, indent=2),
            f'The "task_id" field MUST equal "{context.task_id}". Remember: most investigations '
            'are NEGATIVE, and that is the correct, expected result. Do not manufacture a '
            'candidate. Descriptive only -- no strategy, profit, validation, or causal claims.',
        ]
        return "\n".join(p for p in parts if p is not None)

    def _invoke(self, context: AlphaContext) -> str:
        prompt = self.build_prompt(context)
        return self._run(prompt, self._model, self._timeout)
