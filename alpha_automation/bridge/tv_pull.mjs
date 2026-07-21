#!/usr/bin/env node
/*
 * tv_pull.mjs -- live TradingView Desktop data bridge for Alpha Automation.
 *
 * Reuses tradingview-mcp's OWN connection/chart modules (no reimplementation) to pull a window
 * of bars from the live chart via CDP, exactly as the repo's pull_*.mjs scripts do. Prints a
 * single JSON line to stdout.
 *
 * The tradingview-mcp repo location is passed via the TV_MCP_DIR env var (set by the Python
 * DataAccess layer). This keeps the two repos decoupled.
 *
 * Usage:
 *   node tv_pull.mjs --health
 *   node tv_pull.mjs --symbol OANDA:XAUUSD --tf 60 --from <unix> --to <unix>
 *
 * Output (health):  {"ok":true}                                  or {"ok":false,"error":"..."}
 * Output (pull):    {"ok":true,"source":"live_tv","bars":[[t,o,h,l,c,v],...]}  or {"ok":false,...}
 */

import path from "path";
import { pathToFileURL } from "url";

function arg(name, def = null) {
  const i = process.argv.indexOf(name);
  return i >= 0 && i + 1 < process.argv.length ? process.argv[i + 1] : def;
}
const has = (name) => process.argv.includes(name);

function emit(obj) {
  process.stdout.write(JSON.stringify(obj) + "\n");
}

const TV = process.env.TV_MCP_DIR;
if (!TV) {
  emit({ ok: false, error: "TV_MCP_DIR not set" });
  process.exit(0);
}

async function importTv(rel) {
  const url = pathToFileURL(path.join(TV, ...rel)).href;
  return import(url);
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function main() {
  let conn, chart;
  try {
    conn = await importTv(["src", "connection.js"]);
    chart = await importTv(["src", "core", "chart.js"]);
  } catch (e) {
    emit({ ok: false, error: "cannot import tradingview-mcp modules: " + e.message });
    return;
  }

  // Health check: can we connect to the live chart at all?
  if (has("--health")) {
    try {
      await conn.connect();
      emit({ ok: true });
    } catch (e) {
      emit({ ok: false, error: e.message });
    } finally {
      try { await conn.disconnect(); } catch (_) {}
    }
    return;
  }

  const symbol = arg("--symbol");
  const tf = arg("--tf");
  const from = parseInt(arg("--from"), 10);
  const to = parseInt(arg("--to"), 10);
  if (!symbol || !tf || !Number.isFinite(from) || !Number.isFinite(to)) {
    emit({ ok: false, error: "missing/invalid --symbol/--tf/--from/--to" });
    return;
  }

  const BARS = conn.KNOWN_PATHS.mainSeriesBars;
  const size = () =>
    conn.evaluate(`(function(){var b=${BARS};return b&&b.size?b.size():0;})()`);
  const readBars = () =>
    conn.evaluate(
      `(function(){var b=${BARS};if(!b||!b.lastIndex)return null;` +
        `var s=b.firstIndex(),e=b.lastIndex(),r=[];` +
        `for(var i=s;i<=e;i++){var v=b.valueAt(i);if(v)r.push([v[0],v[1],v[2],v[3],v[4],v[5]||0]);}` +
        `return r;})()`
    );

  try {
    await conn.connect();
    await chart.setSymbol({ symbol });
    await chart.setTimeframe({ timeframe: tf });
    await sleep(1200);
    // Force history load by widening the visible range to cover [from,to]; poll until stable.
    let prev = -1, stable = 0;
    for (let k = 0; k < 25; k++) {
      try { await chart.setVisibleRange({ from, to }); } catch (_) {}
      await sleep(600);
      const n = await size();
      if (n === prev) { stable++; if (stable >= 3) break; } else { stable = 0; prev = n; }
    }
    const all = (await readBars()) || [];
    const bars = all.filter((b) => b[0] >= from && b[0] <= to);
    emit({ ok: true, source: "live_tv", bars });
  } catch (e) {
    emit({ ok: false, error: e.message });
  } finally {
    try { await conn.disconnect(); } catch (_) {}
  }
}

main().catch((e) => emit({ ok: false, error: String(e && e.message ? e.message : e) }));
