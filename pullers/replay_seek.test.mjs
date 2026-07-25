// node --test pullers/replay_seek.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { nextSeekMs, legacyMidnightSeekMs } from './replay_seek.mjs';

// A real intraday oldest bar (not aligned to midnight): 2011-07-28T03:00:00Z.
// This is exactly the kind of bar the M15 floor walk lands on, where the old
// midnight-slice logic diverges from a valid bar instant.
const OLDEST = Math.floor(Date.parse('2011-07-28T03:00:00Z') / 1000);

test('nextSeekMs returns exactly one second before the oldest bar', () => {
  assert.equal(nextSeekMs(OLDEST), (OLDEST - 1) * 1000);
});

test('nextSeekMs is strictly BEFORE the oldest bar (forces a leftward fetch)', () => {
  assert.ok(nextSeekMs(OLDEST) < OLDEST * 1000);
});

test('nextSeekMs stays within the same bar neighborhood, not collapsed to midnight', () => {
  // The fixed target must be within one day of the real bar, never dragged back to 00:00:00Z.
  const seekSec = nextSeekMs(OLDEST) / 1000;
  assert.ok(OLDEST - seekSec <= 86400, 'seek should be near the oldest bar');
  assert.ok(seekSec > legacyMidnightSeekMs(OLDEST) / 1000, 'fixed seek must be later than day-midnight');
});

test('regression: legacy midnight seek differs from the oldest bar and would trip the toast', () => {
  // The legacy target lands on 2011-07-28T00:00:00Z, 3 hours before the real bar -> not a bar
  // instant -> "Data point unavailable" toast -> fail-closed throw in the hardened replay.start().
  const legacy = legacyMidnightSeekMs(OLDEST);
  assert.equal(legacy, Date.parse('2011-07-28T00:00:00Z'));
  assert.notEqual(legacy, OLDEST * 1000);
  assert.notEqual(legacy, nextSeekMs(OLDEST));
});

test('monotonic backward progress across successive steps', () => {
  // Simulate the map's oldest decreasing; each seek must be strictly earlier than the last.
  let oldest = OLDEST;
  let prevSeek = Infinity;
  for (let i = 0; i < 5; i++) {
    const seek = nextSeekMs(oldest);
    assert.ok(seek < prevSeek);
    prevSeek = seek;
    oldest -= 300 * 900; // ~300 M15 bars later
  }
});

test('nextSeekMs rejects non-finite input (fail-closed)', () => {
  assert.throws(() => nextSeekMs(undefined));
  assert.throws(() => nextSeekMs(NaN));
  assert.throws(() => nextSeekMs(Infinity));
});
