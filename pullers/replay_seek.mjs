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

// Bar length in seconds for the intraday resolutions we pull.
export function barSeconds(tf) {
  const m = { '1': 60, '5': 300, '15': 900, '30': 1800, '60': 3600, '240': 14400 };
  const s = m[String(tf)];
  if (!s) throw new Error(`barSeconds: unsupported timeframe ${tf}`);
  return s;
}

// SECOND-DEFECT FIX (window-boundary provisional bar).
//
// The replay cursor bar (the newest/rightmost bar of the loaded window) carries a PROVISIONAL
// close+volume. With adjacent, non-overlapping windows + first-seen dedup, that provisional bar
// is the only capture of its timestamp and is saved verbatim (~1 bar per 300, silently, across
// the whole file). The original lab pipeline avoided this by leaving boundary GAPS and back-filling
// them as interior bars (pull_gapfill.mjs); this reproduces the proven property directly in one
// pass: OVERLAP the windows so each window's provisional rightmost bar lands inside the
// already-collected region, where first-seen dedup keeps the earlier FINAL (interior) value.
//
// Given the oldest bar collected so far, return the selectDate() argument (ms) whose window ends
// `overlapBars` bars INTO the collected region (so it re-covers the previous boundary) while still
// fetching ~(windowSize - overlapBars) genuinely older bars to the left. overlapBars >= 2.
export function nextOverlapSeekMs(frontierSec, overlapBars, tf) {
  if (!Number.isFinite(frontierSec)) {
    throw new Error(`nextOverlapSeekMs: frontierSec must be finite, got ${frontierSec}`);
  }
  if (!(overlapBars >= 2)) {
    throw new Error(`nextOverlapSeekMs: overlapBars must be >= 2, got ${overlapBars}`);
  }
  return (frontierSec + overlapBars * barSeconds(tf)) * 1000;
}

// Adaptive stall recovery. Deep-history windows sometimes load slower than the per-step sleep,
// producing a TRANSIENT no-progress step that, with a fixed sleep, would prematurely trip the stall
// limit (observed on the M15 and M5 pulls, each requiring a manual resume with a longer sleep). Instead
// of a manual resume, escalate the sleep on each no-progress step (giving TV more time) and reset it on
// progress. A genuine floor keeps failing even at maxMs, so the caller only counts toward the stall
// limit once the sleep is already pinned at maxMs — a slow load self-heals, a real floor still stops.
export function escalateSleep(currentMs, { baseMs, maxMs, factor = 1.6 } = {}) {
  if (!(baseMs > 0) || !(maxMs >= baseMs)) {
    throw new Error(`escalateSleep: need 0 < baseMs <= maxMs, got baseMs=${baseMs} maxMs=${maxMs}`);
  }
  return Math.min(Math.round(currentMs * factor), maxMs);
}
