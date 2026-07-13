import { evaluate, KNOWN_PATHS } from './src/connection.js';
import { setSymbol, setTimeframe, setVisibleRange } from './src/core/chart.js';
import fs from 'fs';
const BARS=KNOWN_PATHS.mainSeriesBars; const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const OUT='C:/Users/MEDION~1/AppData/Local/Temp/claude/C--Users-MEDION-GAMING-tradingview-mcp/344b31d3-785f-43a4-b73b-d80a24bc18df/scratchpad/phaseb/alpha/data_native';
fs.mkdirSync(OUT,{recursive:true});
const FROM=Math.floor(new Date('2022-06-01').getTime()/1000), TO=Math.floor(Date.now()/1000);
const size=async()=>await evaluate(`(function(){var b=${BARS};return b&&b.size?b.size():0;})()`);
const readBars=async()=>await evaluate(`(function(){var b=${BARS};if(!b||!b.lastIndex)return null;var s=b.firstIndex(),e=b.lastIndex(),r=[];for(var i=s;i<=e;i++){var v=b.valueAt(i);if(v)r.push([v[0],v[1],v[2],v[3],v[4],v[5]||0]);}return r;})()`);
await setSymbol({symbol:'OANDA:XAUUSD'}); await sleep(1500);
for(const [tf,name] of [['60','H1'],['240','H4'],['D','D1']]){
  await setTimeframe({timeframe:tf}); await sleep(1500);
  let prev=-1,st=0; for(let k=0;k<25;k++){ try{await setVisibleRange({from:FROM,to:TO});}catch(e){} await sleep(650); const n=await size(); if(n===prev){st++; if(st>=3)break;} else {st=0;prev=n;} }
  const bars=await readBars();
  fs.writeFileSync(`${OUT}/OANDA_XAUUSD_${name}.csv`,['time,open,high,low,close,volume',...bars.map(b=>b.join(','))].join('\n'));
  console.log(`${name}: ${bars.length} bars ${new Date(bars[0][0]*1000).toISOString()} -> ${new Date(bars.at(-1)[0]*1000).toISOString()}`);
}
console.log('DONE'); process.exit(0);
