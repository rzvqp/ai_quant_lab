// Pure seek-target logic for the replay-walk pullers.
//
// BUG (pre-fix): the pullers walked backward by requesting replay at the CALENDAR-DAY
// midnight of the current oldest bar, computed as `new Date(oldest*1000).toISOString().slice(0,10)`.
// After tradingview-mcp commit c839e91 hardened replay.start() to be fail-closed, a midnight
// request is almost never an exact bar instant, so TradingView shows its "Data point unavailable"
// toast and substitutes a nearby point; the hardened wrapper then THROWS. The puller's try/catch
// swallowed the throw and counted the step as "stale", so the walk halted long before the real
// history floor.
//
// FIX: request the exact instant ONE SECOND BEFORE the current oldest loaded bar. That is strictly
// earlier than any loaded bar (so TradingView must fetch older history to the left) and it is derived
// from a real bar timestamp rather than an arbitrary calendar midnight. Progress is then measured by
// the bars actually read back (dedup by timestamp), never by trusting the replay cursor -- so a toast,
// if one appears, is irrelevant to correctness.

/**
 * Replay selectDate() argument (ms since epoch) for the next backward step.
 * @param {number} oldestBarSec  epoch seconds of the oldest bar currently loaded
 * @returns {number} ms since epoch, strictly before the oldest bar
 */
export function nextSeekMs(oldestBarSec) {
  if (!Number.isFinite(oldestBarSec)) {
    throw new Error(`nextSeekMs: oldestBarSec must be a finite number, got ${oldestBarSec}`);
  }
  return (oldestBarSec - 1) * 1000;
}

/**
 * The buggy legacy behavior, retained ONLY so the test can demonstrate the regression.
 * Do not use in production code.
 * @param {number} oldestBarSec
 * @returns {number} ms since epoch at calendar-day midnight (UTC) of the oldest bar
 */
export function legacyMidnightSeekMs(oldestBarSec) {
  const dstr = new Date(oldestBarSec * 1000).toISOString().slice(0, 10);
  return new Date(dstr + 'T00:00:00Z').getTime();
}
