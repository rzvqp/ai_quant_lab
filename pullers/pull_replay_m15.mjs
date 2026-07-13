import { evaluate, KNOWN_PATHS } from './src/connection.js';
import { setSymbol, setTimeframe } from './src/core/chart.js';
import * as replay from './src/core/replay.js';
import fs from 'fs';

const BARS=KNOWN_PATHS.mainSeriesBars; const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const OUT='C:/Users/MEDION~1/AppData/Local/Temp/claude/C--Users-MEDION-GAMING-tradingview-mcp/344b31d3-785f-43a4-b73b-d80a24bc18df/scratchpad/phaseb/alpha/data_market';
fs.mkdirSync(OUT,{recursive:true});
const SYM='OANDA:XAUUSD', TF='15';
const TARGET=Math.floor(new Date('2023-01-01T00:00:00Z').getTime()/1000);

async function readBars(){ return await evaluate(`(function(){var b=${BARS};if(!b||!b.lastIndex)return null;var s=b.firstIndex(),e=b.lastIndex(),r=[];for(var i=s;i<=e;i++){var v=b.valueAt(i);if(v)r.push([v[0],v[1],v[2],v[3],v[4],v[5]||0]);}return r;})()`); }

await setSymbol({symbol:SYM}); await setTimeframe({timeframe:TF}); await sleep(2500);
const map=new Map();
function add(bars){ let n=0; for(const b of bars){ if(!map.has(b[0])){ map.set(b[0],b); n++; } } return n; }

// seed with current live window
let cur=await readBars(); if(cur) add(cur);
let firstTs = cur ? cur[0][0] : Math.floor(Date.now()/1000);
console.log(`seed: ${map.size} bars, oldest ${new Date(firstTs*1000).toISOString()}`);

let iter=0, prevFirst=Infinity, stale=0;
while(firstTs>TARGET && iter<400){
  iter++;
  const dstr=new Date(firstTs*1000).toISOString().slice(0,10);
  let ok=false;
  for(let retry=0; retry<2 && !ok; retry++){
    try{
      await replay.start({date:dstr}); await sleep(1800);
      const bars=await readBars();
      if(!bars||!bars.length){ continue; }
      const wf=bars[0][0], wl=bars[bars.length-1][0];
      if(wf>=prevFirst){ stale++; } else { stale=0; }
      const added=add(bars);
      prevFirst=Math.min(prevFirst,wf);
      firstTs=wf;
      ok=true;
      if(iter%5===0||wf<=TARGET) console.log(`iter ${iter} replay@${dstr}: win ${new Date(wf*1000).toISOString().slice(0,10)}..${new Date(wl*1000).toISOString().slice(0,10)} +${added} total=${map.size}`);
    }catch(e){ /* retry */ }
  }
  try{ await replay.stop({}); await sleep(300); }catch(e){}
  if(!ok){ stale++; if(stale>4){ console.log('no progress / stale, stopping'); break; } firstTs -= 3*86400; }
  if(stale>6){ console.log('too many stale windows, stopping'); break; }
}
try{ await replay.stop({}); }catch(e){}

const arr=[...map.values()].sort((a,b)=>a[0]-b[0]);
fs.writeFileSync(`${OUT}/OANDA_XAUUSD_M15.csv`, ['time,open,high,low,close,volume',...arr.map(b=>b.join(','))].join('\n'));
console.log(`SAVED ${arr.length} M15 bars: ${new Date(arr[0][0]*1000).toISOString()} -> ${new Date(arr.at(-1)[0]*1000).toISOString()}`);
console.log('DONE'); process.exit(0);
