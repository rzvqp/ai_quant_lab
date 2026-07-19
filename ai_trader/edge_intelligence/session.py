"""Session suitability evidence -- Phase 7 Checkpoint 6. Compares the current session (from
Market Intelligence's own ``SessionReading``) against a strategy's declared
``Contract.execution.sessions`` free-text field.
"""

from __future__ import annotations

from ai_trader.edge_intelligence.types import EdgeEvidenceItem, EvidenceContribution

DIMENSION = "session_suitability"

#: IMPLEMENTATION CHOICE: the only session tokens this layer recognizes inside a strategy's
#: free-text ``execution.sessions`` declaration. ``sessions`` is authored prose (e.g. "All
#: sessions", "London KZ 07-10 UTC | NY KZ 12-15 UTC", "Monday open only") with no controlled
#: vocabulary in the schema -- rather than build a fuzzy parser that risks silently misreading an
#: exotic phrasing (an undisclosed guess -- exactly what the CEO's "no AI guesses" directive
#: forbids), this layer only ever recognizes these exact known session names as substrings
#: (case-insensitive) and honestly reports UNKNOWN for everything else (e.g. "Monday open only",
#: "Fixed hours 00/07/08/13/14/20 UTC", "Weekday first bar" are all left UNKNOWN, never guessed).
_KNOWN_SESSION_TOKENS = ("ASIA", "LONDON", "NEW YORK", "NY", "OVERLAP")
_ALL_SESSIONS_MARKERS = ("all session", "any session")


def _mentioned_sessions(sessions_text: str) -> tuple[str, ...]:
    upper = sessions_text.upper()
    return tuple(token for token in _KNOWN_SESSION_TOKENS if token in upper)


def evaluate_session_suitability(sessions_declaration: str, current_session: str | None) -> EdgeEvidenceItem:
    lowered = sessions_declaration.lower()
    if any(marker in lowered for marker in _ALL_SESSIONS_MARKERS):
        return EdgeEvidenceItem(
            DIMENSION, EvidenceContribution.NEUTRAL,
            f"strategy declares sessions={sessions_declaration!r} -- no session constraint to evaluate",
        )

    mentioned = _mentioned_sessions(sessions_declaration)
    if not mentioned:
        return EdgeEvidenceItem(
            DIMENSION, EvidenceContribution.UNKNOWN,
            f"strategy declares sessions={sessions_declaration!r} -- not in a form this layer "
            f"recognizes (no known session token found)",
        )

    if current_session is None:
        return EdgeEvidenceItem(
            DIMENSION, EvidenceContribution.UNKNOWN,
            f"strategy restricts to session(s) {mentioned} but the current context has no known "
            f"session reading",
        )

    current_upper = current_session.upper()
    matches = any(token in current_upper or current_upper in token for token in mentioned)
    contribution = EvidenceContribution.SUPPORTS if matches else EvidenceContribution.CONTRADICTS
    return EdgeEvidenceItem(
        DIMENSION, contribution,
        f"strategy restricts to session(s) {mentioned}; current session is {current_session!r}",
    )
