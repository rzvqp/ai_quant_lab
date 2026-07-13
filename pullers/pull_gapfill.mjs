import { evaluate, KNOWN_PATHS } from './src/connection.js';
import { setSymbol, setTimeframe } from './src/core/chart.js';
import * as replay from './src/core/replay.js';
import fs from 'fs';
const BARS=KNOWN_PATHS.mainSeriesBars; const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const AD='C:/Users/MEDION~1/AppData/Local/Temp/claude/C--Users-MEDION-GAMING-tradingview-mcp/344b31d3-785f-43a4-b73b-d80a24bc18df/scratchpad/phaseb/alpha';
const readBars=async()=>await evaluate(`(function(){var b=${BARS};if(!b||!b.lastIndex)return null;var s=b.firstIndex(),e=b.lastIndex(),r=[];for(var i=s;i<=e;i++){var v=b.valueAt(i);if(v)r.push([v[0],v[1],v[2],v[3],v[4],v[5]||0]);}return r;})()`);
// load existing M15
const map=new Map();
for(const line of fs.readFileSync(`${AD}/data_market/OANDA_XAUUSD_M15.csv`,'utf8').split('\n').slice(1)){
  if(!line.trim())continue; const p=line.split(','); map.set(+p[0],[+p[0],+p[1],+p[2],+p[3],+p[4],+p[5]]);
}
const gapDates=JSON.parse(fs.readFileSync(`${AD}/gap_dates.json`,'utf8'));
console.log(`existing M15=${map.size}, gaps to fill=${gapDates.length}`);
await setSymbol({symbol:'OANDA:XAUUSD'}); await setTimeframe({timeframe:'15'}); await sleep(1500);
let filled=0;
for(let gi=0; gi<gapDates.length; gi++){
  const d=new Date(gapDates[gi]); d.setUTCDate(d.getUTCDate()+2);
  const dstr=d.toISOString().slice(0,10);
  try{
    await replay.start({date:dstr}); await sleep(1600);
    const bars=await readBars();
    if(bars){ let a=0; for(const b of bars){ if(!map.has(b[0])){ map.set(b[0],b); a++; } } filled+=a; if(gi%15===0) console.log(`  [${gi}] fill@${dstr} +${a} total=${map.size}`); }
    await replay.stop({}); await sleep(200);
  }catch(e){ try{await replay.stop({});}catch(_){} }
}
const arr=[...map.values()].sort((a,b)=>a[0]-b[0]);
fs.writeFileSync(`${AD}/data_market/OANDA_XAUUSD_M15.csv`,['time,open,high,low,close,volume',...arr.map(b=>b.join(','))].join('\n'));
console.log(`FILLED +${filled} -> M15=${arr.length}`); process.exit(0);
