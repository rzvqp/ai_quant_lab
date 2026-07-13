import { evaluate, KNOWN_PATHS } from './src/connection.js';
import { setSymbol, setTimeframe, setVisibleRange } from './src/core/chart.js';
import fs from 'fs';

const BARS = KNOWN_PATHS.mainSeriesBars;
const OUT = 'C:/Users/MEDION~1/AppData/Local/Temp/claude/C--Users-MEDION-GAMING-tradingview-mcp/344b31d3-785f-43a4-b73b-d80a24bc18df/scratchpad/phaseb/alpha/data';
fs.mkdirSync(OUT, { recursive: true });

const SYMBOLS = ['OANDA:XAUUSD','OANDA:EURUSD','OANDA:GBPUSD','OANDA:USDJPY','OANDA:AUDUSD','OANDA:SPX500USD'];
const TF = 'D';
const FROM = Math.floor(new Date('2014-01-01').getTime()/1000);
const TO   = Math.floor(Date.now()/1000);
const sleep = ms => new Promise(r=>setTimeout(r,ms));

async function size(){ return await evaluate(`(function(){var b=${BARS};return b&&b.size?b.size():0;})()`); }
async function readBars(){
  return await evaluate(`(function(){var b=${BARS};if(!b||!b.lastIndex)return null;var s=b.firstIndex(),e=b.lastIndex(),r=[];for(var i=s;i<=e;i++){var v=b.valueAt(i);if(v)r.push([v[0],v[1],v[2],v[3],v[4],v[5]||0]);}return r;})()`);
}

for (const sym of SYMBOLS){
  try{
    await setSymbol({ symbol: sym });
    await setTimeframe({ timeframe: TF });
    await sleep(1500);
    // force-load history by widening the visible range, poll until bar count stabilizes
    let prev=-1, stable=0;
    for(let k=0;k<25;k++){
      try{ await setVisibleRange({ from: FROM, to: TO }); }catch(e){}
      await sleep(700);
      const n = await size();
      if(n===prev){ stable++; if(stable>=3) break; } else { stable=0; prev=n; }
    }
    const bars = await readBars();
    if(!bars || !bars.length){ console.log(`${sym}: NO BARS`); continue; }
    const rows = ['time,open,high,low,close,volume', ...bars.map(b=>b.join(','))];
    const name = sym.replace(':','_')+'.csv';
    fs.writeFileSync(`${OUT}/${name}`, rows.join('\n'));
    const d0=new Date(bars[0][0]*1000).toISOString().slice(0,10);
    const d1=new Date(bars[bars.length-1][0]*1000).toISOString().slice(0,10);
    console.log(`${sym}: ${bars.length} bars  ${d0} -> ${d1}  -> ${name}`);
  }catch(e){ console.log(`${sym}: ERROR ${e.message}`); }
}
console.log('DONE');
process.exit(0);
