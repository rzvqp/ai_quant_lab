// DXY H1 replay-walk puller (mandate DATA-ACQ-DXY-H1-HISTORICAL-RATIFIED-001).
//
// Same mechanism as pull_replay.mjs (overlapping-window backward walk, provisional-cursor-bar fix,
// adaptive stall recovery, crash-safe flush, resume) but:
//   * --symbol   the chart symbol to walk (default OANDA:XAUUSD)   -> here ICEUS:DXY (official ICE DXY)
//   * --start    UPPER BOUND (ISO). If set, the realtime seed is SKIPPED and the walk begins at
//                --start and goes BACK to --floor. Nothing newer than --start is ever collected, so
//                the protected 2024+ region is never physically pulled into this file. The very first
//                replay-cursor (provisional) bar therefore lands at --start; keep --start a few days
//                INSIDE the protected zone (e.g. 2024-01-05) so that provisional bar is discarded and
//                every delivered <=2023-12-31 bar is a settled interior bar.
//
// No imputation, no interpolation, no gap filling -- missing bars stay missing. 6-col CSV
// (time,open,high,low,close,volume; epoch-UTC). DXY is a cash index: volume is structurally 0
// (NOT fabricated -- the feed supplies none). Usage:
//   node pull_dxy_h1.mjs --symbol ICEUS:DXY --tf 60 --start 2024-01-05 --floor 2011-07-26 --out /abs/RAW_DXY_H1.csv
import { evaluate, KNOWN_PATHS } from './src/connection.js';
import { setSymbol, setTimeframe } from './src/core/chart.js';
import fs from 'fs';
import { nextOverlapSeekMs, escalateSleep } from './replay_seek.mjs';

const RP = KNOWN_PATHS.replayApi;
const BARS = KNOWN_PATHS.mainSeriesBars;
const sleep = ms => new Promise(r => setTimeout(r, ms));
const iso = s => new Date(s * 1000).toISOString();

function arg(name, def) { const i = process.argv.indexOf('--' + name); return i >= 0 ? process.argv[i + 1] : def; }
const SYMBOL = arg('symbol', 'OANDA:XAUUSD');
const TF = arg('tf', '60');
const FLOOR_ISO = arg('floor', '2011-07-26');
const START_ISO = arg('start', '');   // upper bound; '' => seed from realtime (legacy behaviour)
const OUT = arg('out');
const MAX_ITERS = parseInt(arg('max-iters', '6000'), 10);
const STALL_LIMIT = parseInt(arg('stall', '6'), 10);
const STEP_SLEEP = parseInt(arg('sleep', '1900'), 10);
const MAX_SLEEP = parseInt(arg('max-sleep', String(Math.max(12000, STEP_SLEEP * 4))), 10);
const FLUSH_EVERY = parseInt(arg('flush', '25'), 10);
const OVERLAP = parseInt(arg('overlap', '5'), 10);
if (!OUT) { console.error('ERROR: --out <path> is required'); process.exit(2); }
const FLOOR = Math.floor(Date.parse(FLOOR_ISO + (FLOOR_ISO.length <= 10 ? 'T00:00:00Z' : '')) / 1000);
const START = START_ISO ? Math.floor(Date.parse(START_ISO + (START_ISO.length <= 10 ? 'T00:00:00Z' : '')) / 1000) : null;

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
async function dismissModal() {
  await evaluate(`(function(){var ds=Array.from(document.querySelectorAll('[role="dialog"]')).filter(function(d){return d.offsetParent!==null&&(d.innerText||'').indexOf('Continue your last replay')!==-1;});if(!ds.length)return false;var b=Array.from(ds[0].querySelectorAll('button')).find(function(x){return (x.innerText||'').trim()==='Start new';});if(b){b.click();return true;}return false;})()`);
}

const map = new Map();
function add(bars, upper) {
  let n = 0;
  for (const b of bars) { if (upper != null && b[0] > upper) continue; if (!map.has(b[0])) { map.set(b[0], b); n++; } }
  return n;
}
function flush() {
  const arr = [...map.values()].sort((a, b) => a[0] - b[0]);
  const body = ['time,open,high,low,close,volume', ...arr.map(b => b.join(','))].join('\n');
  fs.writeFileSync(OUT + '.tmp', body);
  fs.renameSync(OUT + '.tmp', OUT);
  return arr;
}

if (fs.existsSync(OUT)) {
  for (const line of fs.readFileSync(OUT, 'utf8').split('\n').slice(1)) {
    if (!line.trim()) continue; const p = line.split(',');
    map.set(+p[0], [+p[0], +p[1], +p[2], +p[3], +p[4], +p[5]]);
  }
  console.log(`resume: loaded ${map.size} existing bars from ${OUT}`);
}

await setSymbol({ symbol: SYMBOL });
await setTimeframe({ timeframe: TF });
await sleep(2500);
await dismissModal();

function minKey(m) { let lo = Infinity; for (const k of m.keys()) if (k < lo) lo = k; return lo; }
let oldest;
if (START != null) {
  // UPPER-BOUND mode: begin the walk at --start, never collect anything newer.
  oldest = map.size ? Math.min(minKey(map), START) : START;
  console.log(`upper-bound mode: start=${iso(START)} (realtime seed skipped; nothing newer than start is collected)`);
} else {
  let seed = await readBarsRetry();
  if (seed) {
    const barSec = (nextOverlapSeekMs(0, 2, TF) / 1000) / 2;
    const nowSec = Math.floor(Date.now() / 1000);
    const newestT = seed.at(-1)[0];
    if (newestT + barSec > nowSec) { seed = seed.slice(0, -1); console.log(`dropped still-forming bar ${iso(newestT)}`); }
    console.log(`realtime seed: +${add(seed)} bars, newest ${iso(seed.at(-1)[0])}`);
  }
  oldest = map.size ? minKey(map) : (seed ? seed[0][0] : Math.floor(Date.parse('2026-01-01T00:00:00Z') / 1000));
}

await selectDate(nextOverlapSeekMs(oldest, OVERLAP, TF));
await sleep(2500);
{ const b = await readBarsRetry(); if (b) { add(b, START); oldest = Math.min(oldest, minKey(map)); } }
console.log(`SYMBOL=${SYMBOL} TF=${TF} floor=${iso(FLOOR)} overlap=${OVERLAP} start oldest=${iso(oldest)} total=${map.size}`);

let stale = 0, reachedFloor = false, curSleep = STEP_SLEEP;
for (let i = 1; i <= MAX_ITERS && oldest > FLOOR; i++) {
  await selectDate(nextOverlapSeekMs(oldest, OVERLAP, TF));
  await sleep(curSleep);
  const bars = await readBarsRetry();
  const wf = bars ? bars[0][0] : oldest;
  const added = bars ? add(bars, START) : 0;
  if (bars && wf < oldest) {
    oldest = wf; stale = 0; curSleep = STEP_SLEEP;
  } else if (curSleep < MAX_SLEEP) {
    curSleep = escalateSleep(curSleep, { baseMs: STEP_SLEEP, maxMs: MAX_SLEEP });
  } else {
    stale++;
  }
  if (i % 5 === 0) console.log(`iter ${i}: oldest=${iso(oldest)} +${added} total=${map.size} stale=${stale} sleep=${curSleep}`);
  if (i % FLUSH_EVERY === 0) flush();
  if (stale >= STALL_LIMIT) { console.log(`FLOOR reached — oldest stable at ${iso(oldest)} (sleep pinned at ${curSleep}ms)`); reachedFloor = true; break; }
}

try { await evaluate(`${RP}.stopReplay()`); } catch (e) {}
const arr = flush();
console.log(`SAVED ${arr.length} bars: ${iso(arr[0][0])} -> ${iso(arr.at(-1)[0])}`);
console.log(`reachedFloor=${reachedFloor} targetFloor=${iso(FLOOR)} deepest=${iso(oldest)}`);
console.log('DONE'); process.exit(0);
