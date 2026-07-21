#!/usr/bin/env node
/*
 * tv_exec.mjs -- generalized TradingView research bridge for Alpha Automation.
 *
 * Imports tradingview-mcp's OWN core modules (no reimplementation) and dispatches allowlisted
 * research "verbs" to them, returning JSON on stdout. Supports a single request or a batch (run
 * over one CDP connection to avoid per-call reconnect cost).
 *
 * The Python capability gate (tv/capabilities.py) authorizes verbs BEFORE they reach this bridge;
 * this bridge additionally refuses any verb not in DISPATCH (defence in depth). It never dispatches
 * trade/alert/broker/strategy-tester verbs -- they are simply absent from DISPATCH.
 *
 * tradingview-mcp location comes from TV_MCP_DIR (set by the Python client).
 *
 * Input  (stdin or argv[2], JSON):
 *   {"verb":"get_state","params":{}}
 *   {"batch":[{"verb":"set_symbol","params":{"symbol":"OANDA:XAUUSD"}}, {"verb":"get_state"}]}
 * Output (JSON line):
 *   single: {"ok":true,"verb":"get_state","result":{...}}   or {"ok":false,"verb":...,"error":"...","code":"..."}
 *   batch:  {"ok":true,"results":[{ok,verb,result|error,code}, ...]}
 */

import path from "path";
import { pathToFileURL } from "url";

function emit(obj) {
  process.stdout.write(JSON.stringify(obj) + "\n");
}

const TV = process.env.TV_MCP_DIR;
if (!TV) {
  emit({ ok: false, error: "TV_MCP_DIR not set" });
  process.exit(0);
}

async function importTv(...rel) {
  return import(pathToFileURL(path.join(TV, ...rel)).href);
}

async function readInput() {
  if (process.argv[2]) return process.argv[2];
  const chunks = [];
  for await (const c of process.stdin) chunks.push(c);
  return Buffer.concat(chunks).toString("utf-8");
}

async function main() {
  let core, tab, conn;
  try {
    core = await importTv("src", "core", "index.js");   // chart/data/replay/capture/drawing/indicators/pine
    tab = await importTv("src", "core", "tab.js");
    conn = await importTv("src", "connection.js");
  } catch (e) {
    emit({ ok: false, error: "cannot import tradingview-mcp modules: " + e.message });
    return;
  }

  const P = (params) => params || {};

  // verb -> async (params) => result. ONLY research-safe verbs. No trade/alert/broker/strategy verbs.
  const DISPATCH = {
    // health
    health: async () => { await conn.connect(); return await conn.getTargetInfo(); },
    // reads
    get_state: () => core.chart.getState({}),
    get_ohlcv: (p) => core.data.getOhlcv(P(p)),
    get_quote: (p) => core.data.getQuote(P(p)),
    get_study_values: () => core.data.getStudyValues(),
    get_indicator: (p) => core.data.getIndicator(P(p)),
    get_pine_lines: (p) => core.data.getPineLines(P(p)),
    get_pine_labels: (p) => core.data.getPineLabels(P(p)),
    get_pine_tables: (p) => core.data.getPineTables(P(p)),
    get_pine_boxes: (p) => core.data.getPineBoxes(P(p)),
    get_visible_range: () => core.chart.getVisibleRange({}),
    get_depth: () => core.data.getDepth(),
    list_drawings: () => core.drawing.listDrawings(),
    replay_status: () => core.replay.status({}),
    symbol_info: () => core.chart.symbolInfo({}),
    symbol_search: (p) => core.chart.symbolSearch(P(p)),
    tab_list: () => tab.list(),
    capture_screenshot: (p) => core.capture.captureScreenshot(P(p)),
    pine_get_source: () => core.pine.getSource(),
    pine_get_errors: () => core.pine.getErrors(),
    pine_analyze: (p) => core.pine.analyze(P(p)),
    pine_check: (p) => core.pine.check(P(p)),
    // navigate
    set_symbol: (p) => core.chart.setSymbol(P(p)),
    set_timeframe: (p) => core.chart.setTimeframe(P(p)),
    set_type: (p) => core.chart.setType(P(p)),
    set_visible_range: (p) => core.chart.setVisibleRange(P(p)),
    scroll_to_date: (p) => core.chart.scrollToDate(P(p)),
    replay_start: (p) => core.replay.start(P(p)),
    replay_step: () => core.replay.step({}),
    replay_stop: () => core.replay.stop({}),
    replay_autoplay: (p) => core.replay.autoplay(P(p)),
    tab_new: () => tab.newTab(),
    tab_switch: (p) => tab.switchTab(P(p)),
    tab_close: () => tab.closeTab(),
    // mutate
    add_indicator: (p) => core.chart.manageIndicator({ action: "add", ...P(p) }),
    remove_indicator: (p) => core.chart.manageIndicator({ action: "remove", ...P(p) }),
    set_indicator_inputs: (p) => core.indicators.setInputs(P(p)),
    toggle_indicator: (p) => core.indicators.toggleVisibility(P(p)),
    draw_shape: (p) => core.drawing.drawShape(P(p)),
    remove_drawing: (p) => core.drawing.removeOne(P(p)),
    clear_drawings: () => core.drawing.clearAll(),
    pine_set_source: (p) => core.pine.setSource(P(p)),
    pine_new: (p) => core.pine.newScript(P(p)),
    pine_open: (p) => core.pine.openScript(P(p)),
    // gated (may write to the account) -- present but only invoked when Python allows
    pine_compile: () => core.pine.compile(),
    pine_smart_compile: () => core.pine.smartCompile(),
    pine_save: () => core.pine.save(),
  };

  async function runOne(verb, params) {
    const fn = DISPATCH[verb];
    if (!fn) return { ok: false, verb, error: `unknown/forbidden verb: ${verb}`, code: "VERB_NOT_ALLOWED" };
    try {
      const result = await fn(params);
      return { ok: true, verb, result };
    } catch (e) {
      return { ok: false, verb, error: e && e.message ? e.message : String(e), code: e && e.code ? e.code : null };
    }
  }

  let req;
  try {
    req = JSON.parse((await readInput()).trim());
  } catch (e) {
    emit({ ok: false, error: "invalid JSON request: " + e.message });
    return;
  }

  try {
    if (Array.isArray(req.batch)) {
      const results = [];
      for (const item of req.batch) {
        results.push(await runOne(item.verb, item.params));
      }
      emit({ ok: true, results });
    } else {
      emit(await runOne(req.verb, req.params));
    }
  } catch (e) {
    emit({ ok: false, error: String(e && e.message ? e.message : e) });
  } finally {
    try { await conn.disconnect(); } catch (_) {}
  }
}

main().catch((e) => emit({ ok: false, error: String(e && e.message ? e.message : e) }));
