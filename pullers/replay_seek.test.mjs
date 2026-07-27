// node --test pullers/replay_seek.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { nextSeekMs, legacyMidnightSeekMs, barSeconds, nextOverlapSeekMs, escalateSleep } from './replay_seek.mjs';

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

// ---- second-defect fix: overlapping windows drop the provisional cursor bar ----

test('barSeconds maps intraday resolutions', () => {
  assert.equal(barSeconds('15'), 900);
  assert.equal(barSeconds('60'), 3600);
  assert.equal(barSeconds(5), 300);
  assert.throws(() => barSeconds('W'));
});

test('nextOverlapSeekMs ends the window inside the collected region and requires overlap>=2', () => {
  const f = Math.floor(Date.parse('2015-03-10T07:30:00Z') / 1000);
  // window end is `overlap` bars newer than the frontier -> inside already-collected territory
  assert.equal(nextOverlapSeekMs(f, 5, '15'), (f + 5 * 900) * 1000);
  assert.ok(nextOverlapSeekMs(f, 5, '15') > f * 1000);
  assert.throws(() => nextOverlapSeekMs(f, 1, '15'));   // overlap of 1 is not enough
  assert.throws(() => nextOverlapSeekMs(NaN, 5, '15'));
});

// Mechanical proof that the provisional cursor bar never survives into the file.
// Simulates TradingView replay: selectDate(X) returns `winSize` bars ending at the bar <= X,
// where ONLY the rightmost bar carries a provisional value; all others are final. We run the
// puller's overlap walk (first-seen dedup) and assert every stored bar holds its FINAL value.
test('overlap walk: no provisional (rightmost) bar reaches the file', () => {
  const TF = '15', BS = 900, N = 4000, WIN = 300, OVERLAP = 5;
  const finalVal = t => t * 10;            // deterministic final close
  const provVal = t => t * 10 + 0.123;     // provisional differs
  function replayWindow(seekMs) {
    let ri = Math.floor(Math.floor(seekMs / 1000) / BS);
    ri = Math.min(N - 1, ri);
    if (ri < 0) return [];
    const lo = Math.max(0, ri - WIN + 1);
    const bars = [];
    for (let j = lo; j <= ri; j++) {
      const t = j * BS;
      bars.push([t, j === ri ? provVal(t) : finalVal(t)]); // rightmost = provisional
    }
    return bars;
  }
  const map = new Map();
  const add = bars => { for (const b of bars) if (!map.has(b[0])) map.set(b[0], b[1]); };

  // seed at the most recent bar
  add(replayWindow((N - 1) * BS * 1000));
  let frontier = Math.min(...map.keys());
  for (let i = 0; i < 100 && frontier > 0; i++) {
    const bars = replayWindow(nextOverlapSeekMs(frontier, OVERLAP, TF));
    add(bars);
    const wf = bars[0][0];
    if (wf < frontier) frontier = wf; else break;
  }

  // every bar except possibly the initial seed's rightmost must hold the FINAL value
  const seedRight = (N - 1) * BS;
  let provisionalKept = 0;
  for (const [t, v] of map) {
    if (t === seedRight) continue;
    if (v !== finalVal(t)) provisionalKept++;
  }
  assert.equal(provisionalKept, 0, 'a provisional cursor bar leaked into the file');
  // and coverage is gap-free across what we walked
  const times = [...map.keys()].sort((a, b) => a - b);
  let gaps = 0;
  for (let i = 1; i < times.length; i++) if (times[i] - times[i - 1] !== BS) gaps++;
  assert.equal(gaps, 0, 'overlap walk left a gap');
});

// ---- adaptive stall recovery ----

test('escalateSleep grows by factor and caps at maxMs', () => {
  const opt = { baseMs: 2000, maxMs: 8000, factor: 1.6 };
  assert.equal(escalateSleep(2000, opt), 3200);
  assert.equal(escalateSleep(3200, opt), 5120);
  assert.equal(escalateSleep(5120, opt), 8000);   // 8192 capped to 8000
  assert.equal(escalateSleep(8000, opt), 8000);   // stays pinned at max
  assert.throws(() => escalateSleep(2000, { baseMs: 0, maxMs: 8000 }));
  assert.throws(() => escalateSleep(2000, { baseMs: 5000, maxMs: 1000 }));
});

test('adaptive loop: a transient stall self-heals, a real floor still stops', () => {
  const BASE = 2000, MAX = 8000, LIMIT = 4;
  // model a "loader": returns progress=false until the sleep is >= readyAt, then true; a floor never readies.
  function runWalk(readyAt) {
    let sleep = BASE, stale = 0, steps = 0, healed = false;
    for (let i = 0; i < 50; i++) {
      steps++;
      const progressed = readyAt !== Infinity && sleep >= readyAt;
      if (progressed) { sleep = BASE; stale = 0; healed = true; return { stopped: false, healed, steps }; }
      if (sleep < MAX) sleep = escalateSleep(sleep, { baseMs: BASE, maxMs: MAX });
      else stale++;
      if (stale >= LIMIT) return { stopped: true, healed, steps };
    }
    return { stopped: false, healed, steps };
  }
  // transient: readies once sleep reaches 5120ms -> should heal, not stop
  const t = runWalk(5000);
  assert.equal(t.stopped, false);
  assert.equal(t.healed, true);
  // genuine floor: never readies -> escalates to max, then stalls out and stops
  const f = runWalk(Infinity);
  assert.equal(f.stopped, true);
  assert.equal(f.healed, false);
});
