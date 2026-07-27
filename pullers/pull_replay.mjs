// Generalized replay-walk puller for OANDA:XAUUSD intraday history.
//
// Runs from the tradingview-mcp checkout (which provides ./src). Walks TradingView replay
// mode backward, window by window, accumulating de-duplicated bars, and writes a 6-column CSV
// (time,open,high,low,close,volume; epoch-UTC first column) matching the existing data/market
// files. No imputation, no interpolation, no gap filling -- missing bars stay missing.
//
// FIX 1 (seek/stall) vs the old pull_replay_m15.mjs: the walk no longer requests replay at
// calendar-day midnight (slice(0,10)), which trips the hardened fail-closed replay.start()
// (tradingview-mcp c839e91). Progress is measured from the bars actually read back, never from the
// replay cursor -- so a "Data point unavailable" toast cannot corrupt or halt the walk.
//
// FIX 2 (window-boundary provisional bar): the replay cursor (rightmost) bar carries a PROVISIONAL
// close+volume. With adjacent windows it was the only capture of its timestamp (~1 bad bar per 300,
// silently, across the whole file). The walk now OVERLAPS windows (nextOverlapSeekMs): each window
// ends a few bars inside the already-collected region, so its provisional rightmost bar lands on an
// already-final bar and first-seen dedup keeps the FINAL (interior) value. Validated against the
// existing lab file at 0 mismatches / 0 gaps on control slices. See ./replay_seek.mjs.
//
// Usage:
//   node pull_replay.mjs --tf 15 --floor 2011-07-20 --out /abs/path/OANDA_XAUUSD_M15.csv
//   node pull_replay.mjs --tf 60 --floor 2006-03-01 --out /abs/path/OANDA_XAUUSD_H1.csv
// Resume: if --out already exists it is loaded and the walk continues from its oldest bar.
import { evaluate, KNOWN_PATHS } from './src/connection.js';
import { setSymbol, setTimeframe } from './src/core/chart.js';
import fs from 'fs';
import { nextOverlapSeekMs } from './replay_seek.mjs';

const RP = KNOWN_PATHS.replayApi;
const BARS = KNOWN_PATHS.mainSeriesBars;
const sleep = ms => new Promise(r => setTimeout(r, ms));
const iso = s => new Date(s * 1000).toISOString();

// ---- args ----
function arg(name, def) { const i = process.argv.indexOf('--' + name); return i >= 0 ? process.argv[i + 1] : def; }
const TF = arg('tf', '15');
const FLOOR_ISO = arg('floor', '2011-07-20');
const OUT = arg('out');
const MAX_ITERS = parseInt(arg('max-iters', '4000'), 10);
const STALL_LIMIT = parseInt(arg('stall', '4'), 10);
const STEP_SLEEP = parseInt(arg('sleep', '1900'), 10);
const FLUSH_EVERY = parseInt(arg('flush', '25'), 10);
const OVERLAP = parseInt(arg('overlap', '5'), 10);   // window overlap in bars (>=2) — see FIX 2
if (!OUT) { console.error('ERROR: --out <path> is required'); process.exit(2); }
const FLOOR = Math.floor(Date.parse(FLOOR_ISO + (FLOOR_ISO.length <= 10 ? 'T00:00:00Z' : '')) / 1000);

// Read full OHLCV of every currently-loaded bar.
async function readBars() {
  return await evaluate(`(function(){var b=${BARS};if(!b||!b.lastIndex)return null;var s=b.firstIndex(),e=b.lastIndex(),r=[];for(var i=s;i<=e;i++){var v=b.valueAt(i);if(v)r.push([v[0],v[1],v[2],v[3],v[4],v[5]||0]);}return r;})()`);
}
async function readBarsRetry(tries = 4) {
  for (let t = 0; t < tries; t++) { const b = await readBars(); if (b && b.length) return b; await sleep(600); }
  return null;
}
async function selectDate(ms) {
  await evaluate(`(function(){try{window.TradingViewApi._replayApi.showReplayToolbar();}catch(e){}return true;})()`);
  await evaluate(`${RP}.selectDate(${ms})`);
}
// Dismiss a lingering "Continue your last replay?" modal if present.
async function dismissModal() {
  await evaluate(`(function(){var ds=Array.from(document.querySelectorAll('[role="dialog"]')).filter(function(d){return d.offsetParent!==null&&(d.innerText||'').indexOf('Continue your last replay')!==-1;});if(!ds.length)return false;var b=Array.from(ds[0].querySelectorAll('button')).find(function(x){return (x.innerText||'').trim()==='Start new';});if(b){b.click();return true;}return false;})()`);
}

const map = new Map();
function add(bars) { let n = 0; for (const b of bars) { if (!map.has(b[0])) { map.set(b[0], b); n++; } } return n; }
function flush() {
  const arr = [...map.values()].sort((a, b) => a[0] - b[0]);
  const body = ['time,open,high,low,close,volume', ...arr.map(b => b.join(','))].join('\n');
  fs.writeFileSync(OUT + '.tmp', body);
  fs.renameSync(OUT + '.tmp', OUT);
  return arr;
}

// ---- resume ----
if (fs.existsSync(OUT)) {
  for (const line of fs.readFileSync(OUT, 'utf8').split('\n').slice(1)) {
    if (!line.trim()) continue; const p = line.split(',');
    map.set(+p[0], [+p[0], +p[1], +p[2], +p[3], +p[4], +p[5]]);
  }
  console.log(`resume: loaded ${map.size} existing bars from ${OUT}`);
}

await setSymbol({ symbol: 'OANDA:XAUUSD' });
await setTimeframe({ timeframe: TF });
await sleep(2500);
await dismissModal();

// Seed: capture the realtime right-edge window first (most recent bars), then enter replay.
// Guard: if the market is open, the newest realtime bar is still FORMING (provisional). Drop it so
// the file's terminal bar is always a settled bar — the same provisional-bar rule as the interior fix.
let seed = await readBarsRetry();
if (seed) {
  const barSec = (nextOverlapSeekMs(0, 2, TF) / 1000) / 2; // = barSeconds(TF)
  const nowSec = Math.floor(Date.now() / 1000);
  const newestT = seed.at(-1)[0];
  if (newestT + barSec > nowSec) { seed = seed.slice(0, -1); console.log(`dropped still-forming bar ${iso(newestT)}`); }
  console.log(`realtime seed: +${add(seed)} bars, newest ${iso(seed.at(-1)[0])}`);
}
let oldest = map.size ? Math.min(...map.keys()) : (seed ? seed[0][0] : Math.floor(Date.parse('2026-01-01T00:00:00Z') / 1000));

// Enter replay with an overlapping window: it ends OVERLAP bars inside the realtime-collected
// region (so its provisional rightmost bar is already-collected) and fetches older bars to the left.
await selectDate(nextOverlapSeekMs(oldest, OVERLAP, TF));
await sleep(2500);
{ const b = await readBarsRetry(); if (b) { add(b); oldest = Math.min(oldest, b[0][0]); } }
console.log(`TF=${TF} floor=${iso(FLOOR)} overlap=${OVERLAP} start oldest=${iso(oldest)} total=${map.size}`);

let stale = 0, reachedFloor = false;
for (let i = 1; i <= MAX_ITERS && oldest > FLOOR; i++) {
  await selectDate(nextOverlapSeekMs(oldest, OVERLAP, TF));
  await sleep(STEP_SLEEP);
  const bars = await readBarsRetry();
  if (!bars) { stale++; if (stale >= STALL_LIMIT) { console.log(`no bars ${stale}x -> stop`); break; } continue; }
  const wf = bars[0][0];
  const added = add(bars);
  if (wf < oldest) { oldest = wf; stale = 0; }
  else { stale++; }
  if (i % 5 === 0) console.log(`iter ${i}: oldest=${iso(oldest)} +${added} total=${map.size} stale=${stale}`);
  if (i % FLUSH_EVERY === 0) flush();
  if (stale >= STALL_LIMIT) { console.log(`FLOOR reached — oldest stable at ${iso(oldest)}`); reachedFloor = true; break; }
}

try { await evaluate(`${RP}.stopReplay()`); } catch (e) {}
const arr = flush();
console.log(`SAVED ${arr.length} bars: ${iso(arr[0][0])} -> ${iso(arr.at(-1)[0])}`);
console.log(`reachedFloor=${reachedFloor} targetFloor=${iso(FLOOR)} deepest=${iso(oldest)}`);
console.log('DONE'); process.exit(0);
