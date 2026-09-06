"""`STRUCTURAL_FINAL` resolution (design doc Section 19.11, itself citing "Section 11" for the
underlying confirmation/invalidation/bound rule).

**Disclosed citation defect (mechanically verified, not assumed):** Section 19.11, Section 9 (its
own horizon list), and Section 19.4 item 5 all cite "Section 11" as the place this
confirmation/invalidation/`UNRESOLVED_AT_H8` rule was "already-locked." The document's actual Section
11 is "Dedup Contract" and contains no such text anywhere -- confirmed by a full-document search for
every "## 11." heading (there is exactly one) and for "confirmation"/"invalidation" occurring
together (no other match). This is a real, repeated mislabeled cross-reference in the frozen
document, disclosed here rather than silently ignored -- but it does not invalidate the rule itself:
Section 19.11's own text states the rule verbatim, and Section 19 as a whole carries
`SCORECARD_DEFINITIONAL_LOCK = PASS`. The rule is implemented exactly as stated in 19.11, regardless
of its own citation's accuracy.

**The rule, verbatim from Section 19.11:** "confirmation = a same-direction `STRUCTURAL_BREAK` (or
continuation past the origin episode's own extreme) within the same `underlying_move_id`;
invalidation = price closes back through `move_origin_price` in the adverse direction; bound = `H8`
(32 M15 bars) -- `UNRESOLVED_AT_H8` if neither occurs by then."

**One disclosed interpretive step (not a new numeric threshold):** "the origin episode's own
extreme" is not itself defined field-by-field anywhere in the document. `reference_levels` is not
uniform across the 4 classes -- `STRUCTURAL_BREAK` in particular stores no high/low at all (only
`broken_level_type`/`broken_level_price`/`prior_bar_close`/`breaking_bar_close`), so no per-class
high/low field exists on every episode. `current_price` (`bar.close` at freeze time), by contrast, IS
present on every `EpisodeRecord` regardless of class, and is the natural "best point reached so far"
reading of "extreme" at the moment the episode itself froze. This module uses `current_price` for
that purpose -- a field-mapping choice, not a calibrated number, and disclosed prominently (matching
this delivery's own precedent for the session-reversal tie-break, Section 19.9) rather than silently
assumed.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ai_trader.apprenticeship_v2.general_observer.dedup import UNDERLYING_MOVE_WINDOW_SECONDS, row_move_origin_price

if TYPE_CHECKING:
    from ai_trader.apprenticeship_v2.mt5_read_only_source import ReadOnlyBar

STRUCTURAL_FINAL_WINDOW_SECONDS = UNDERLYING_MOVE_WINDOW_SECONDS  # H8 = 32 M15 bars -- reused, not reinvented


def compute_structural_resolution_state(
    episode_row: dict, m15_bars_since_episode: "list[ReadOnlyBar]", existing_general_episode_rows: list[dict],
) -> str:
    """Returns `"CONFIRMATION"` | `"INVALIDATION"` | `"UNRESOLVED_AT_H8"`. Pure function of its
    inputs -- no internal state, no caching -- so restart-safe by construction (a fresh call after a
    restart, given the same ledger rows and causal bars, reproduces the identical verdict).

    Invalidation and (extreme-based) confirmation are mutually exclusive on any single bar (a bar's
    close cannot simultaneously be beyond the favorable `current_price` and adverse to
    `move_origin_price`, since those sit on opposite sides of the episode's own position) -- so
    determining which occurred FIRST, chronologically, resolves any apparent ordering ambiguity
    without needing a priority rule beyond "earliest wins" (ties resolve to `INVALIDATION`, the more
    conservative outcome, consistent with this delivery's established fail-safe convention)."""
    frozen_ts = int(episode_row["frozen_at_bar_ts"])
    direction = episode_row.get("directional_hypothesis")
    move_id = episode_row.get("underlying_move_id")
    current_price = float(episode_row["current_price"])
    origin_price = row_move_origin_price(episode_row)
    window_end_ts = frozen_ts + STRUCTURAL_FINAL_WINDOW_SECONDS

    break_ts: int | None = None
    for row in existing_general_episode_rows:
        if (row.get("episode_type") == "STRUCTURAL_BREAK" and row.get("underlying_move_id") == move_id
                and row.get("directional_hypothesis") == direction):
            other_ts = int(row["frozen_at_bar_ts"])
            if frozen_ts < other_ts <= window_end_ts and (break_ts is None or other_ts < break_ts):
                break_ts = other_ts

    invalidation_ts: int | None = None
    continuation_ts: int | None = None
    for bar in m15_bars_since_episode:
        if not (frozen_ts < bar.ts_close <= window_end_ts):
            continue
        if direction == "BULLISH":
            if invalidation_ts is None and bar.close < origin_price:
                invalidation_ts = bar.ts_close
            if continuation_ts is None and bar.close > current_price:
                continuation_ts = bar.ts_close
        elif direction == "BEARISH":
            if invalidation_ts is None and bar.close > origin_price:
                invalidation_ts = bar.ts_close
            if continuation_ts is None and bar.close < current_price:
                continuation_ts = bar.ts_close

    confirmation_ts: int | None = None
    for candidate in (break_ts, continuation_ts):
        if candidate is not None and (confirmation_ts is None or candidate < confirmation_ts):
            confirmation_ts = candidate

    if invalidation_ts is None and confirmation_ts is None:
        return "UNRESOLVED_AT_H8"
    if invalidation_ts is None:
        return "CONFIRMATION"
    if confirmation_ts is None:
        return "INVALIDATION"
    return "INVALIDATION" if invalidation_ts <= confirmation_ts else "CONFIRMATION"


def due_structural_final_for_episode(
    episode_row: dict, m15_bars_since_episode: "list[ReadOnlyBar]", existing_general_episode_rows: list[dict],
) -> str | None:
    """Returns the resolved state (`"CONFIRMATION"` | `"INVALIDATION"` | `"UNRESOLVED_AT_H8"`) if
    `STRUCTURAL_FINAL` is due to be scored right now, else `None` if still pending (no early
    resolution has occurred yet AND the H8 window has not yet fully elapsed) -- mirrors
    `scorecard.due_horizons_for_episode`'s own "stays pending" semantics, never scoring early against
    a truncated window unless a genuine early resolution (confirmation/invalidation) has already
    occurred."""
    frozen_ts = int(episode_row["frozen_at_bar_ts"])
    window_end_ts = frozen_ts + STRUCTURAL_FINAL_WINDOW_SECONDS
    state = compute_structural_resolution_state(episode_row, m15_bars_since_episode, existing_general_episode_rows)
    if state != "UNRESOLVED_AT_H8":
        return state
    window_has_elapsed = any(frozen_ts < bar.ts_close and bar.ts_close >= window_end_ts for bar in m15_bars_since_episode)
    return "UNRESOLVED_AT_H8" if window_has_elapsed else None
