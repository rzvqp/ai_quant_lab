"""Adapter base -- the structured Alpha I/O contract and validation.

An adapter takes an AlphaContext (mission + perspective + task + window + data summary + prior
questions) and returns a schema-valid, boundary-clean AlphaResponse dict. Parsing arbitrary
conversational prose is forbidden: the response must be a single JSON object. `investigate()`
handles bounded re-requests on validation failure so a malformed or boundary-violating response
is never persisted.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, List, Optional

from .. import schemas
from .. import boundaries


class AlphaAdapterError(RuntimeError):
    pass


@dataclass
class AlphaContext:
    task_id: str
    mission: str
    perspective: dict
    task: dict
    window: Optional[dict]
    data_summary: dict
    prior_questions: List[str] = field(default_factory=list)


def extract_json(text: str) -> dict:
    """Extract the first balanced top-level JSON object from `text`. Tolerates surrounding prose."""
    if text is None:
        raise AlphaAdapterError("no output to parse")
    # Fast path: whole string is JSON.
    stripped = text.strip()
    try:
        obj = json.loads(stripped)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass
    # Scan for the first balanced {...} block.
    depth = 0
    start = -1
    in_str = False
    esc = False
    for i, ch in enumerate(text):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start >= 0:
                candidate = text[start:i + 1]
                try:
                    obj = json.loads(candidate)
                    if isinstance(obj, dict):
                        return obj
                except json.JSONDecodeError:
                    start = -1
                    continue
    raise AlphaAdapterError("no JSON object found in adapter output")


def validate_response(obj: dict, expected_task_id: str) -> List[str]:
    """Return a list of problems with an Alpha response (empty == acceptable)."""
    problems: List[str] = []
    problems.extend(schemas.validate(obj, schemas.load_schema("alpha_response")))
    if obj.get("task_id") != expected_task_id:
        problems.append(f"task_id mismatch: expected {expected_task_id!r}, got {obj.get('task_id')!r}")
    hits = boundaries.scan_response(obj)
    if hits:
        problems.append(f"scientific-boundary breach -- forbidden language: {hits}")
    return problems


class AlphaAdapter:
    """Base adapter. Subclasses implement `_invoke(context) -> (dict | str)`."""

    name = "base"
    max_retries = 2

    def _invoke(self, context: AlphaContext) -> Any:  # pragma: no cover - abstract
        raise NotImplementedError

    def investigate(self, context: AlphaContext) -> dict:
        last_problems: List[str] = []
        attempts = self.max_retries + 1
        for attempt in range(attempts):
            raw = self._invoke(context)
            try:
                obj = raw if isinstance(raw, dict) else extract_json(raw)
            except AlphaAdapterError as e:
                last_problems = [str(e)]
                continue
            problems = validate_response(obj, context.task_id)
            if not problems:
                return obj
            last_problems = problems
        raise AlphaAdapterError(
            f"adapter {self.name!r} failed to produce a valid response after {attempts} "
            f"attempt(s): {last_problems}")
