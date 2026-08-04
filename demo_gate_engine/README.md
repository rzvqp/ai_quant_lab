# DEMO gate-enforcement engine — CAND-0001 PDH-PDL v2.0

Motor DEMO **separat** care impune cele trei garduri Red Team cu câmpuri de audit per tranzacție. Construit de
Validation Engine (autorizat CEO 2026-07-30) după ce raportul `13c0f41` a arătat că `code/mstrat.py::simulate`
nu impune niciunul. **`mstrat.py` rămâne neatins** (motor de cercetare, folosit de rezultate emise). Acesta e
motorul de **execuție DEMO**, funcție pură de bare + spread OBSERVAT; fără MT5, fără trimitere de ordine.

## Cele trei garduri (criterii `c6305d5`, manifest v2.7.34 `a11dde7`)
- **S1** — ierarhie worst-case **STOP > TIME-STOP > TARGET** la toate trei coliziunile intrabar; time-stop-ul e
  al **ZILEI** (`day_end_idx`), nu timeout pe bare; pe bara-graniță STOP primează, iar țintă-pe-graniță devine
  TIME-STOP (ieșire la close), nu țintă. Audit: `intrabar_ordering`.
- **S2** — `min_executable_risk = max(2×effective_spread, 5×tick, 0,10×ATR)`; `executable_stop_distance =
  max(strategy, min_executable_risk)`; sizing 1R pe distanța corectată; `effective_spread` = spread REAL
  observat. Audit: `strategy_stop_distance` (NU se suprascrie), `min_executable_risk`, `executable_stop_distance`,
  `floored`.
- **S3** — țintă scanată strict de la `entry_idx+1`. Audit: `target_scan_start` / `target_scan_end`.

`INVALID_EXECUTION` îngust: gap prin stopul podit la intrare (doar tranzacții podite) sau risc zero/negativ.
Garda de intrare a politicii (next-open dincolo de țintă / stop structural) → `NO_TRADE`.

## API
`simulate_demo_trade(sig: DemoSignal, open_, high, low, close, tick_size) -> DemoTradeResult` (+ batch
`simulate_demo_trades`). Fiecare `DemoTradeResult` emite TOATE câmpurile de audit. `DemoSignal` primește
`effective_spread` și `cost` OBSERVATE (pe DEMO, din fill-uri reale) și `day_end_idx` (granița `day_index`).

## Teste
`test_pdh_pdl_demo_engine.py` — un test per gard care PICĂ fără el (prin contrast cu valoarea naivă ne-gardată)
și TRECE cu el, inclusiv cerința centrală S1 (bară stop∧țintă → STOP), simetria short, îngustimea
`INVALID_EXECUTION`, gărzile de intrare și completitudinea auditului. 13/13, `mypy --strict` curat.

## Handoff → AI Trader
Cablarea PDH/PDL la `mt5_demo_execution` (calea care a funcționat deja pe BTCUSD, `research-main`,
`a3ef1c7`): AI Trader alimentează `DemoSignal` din semnalul PDH/PDL frozen (`entry_idx`, `direction`,
`strategy_stop_price`=extrema barei de atingere, `target_price`=nivelul opus, `atr`, `day_end_idx`) și, la
fill, populează `effective_spread`/`cost` din valorile REALIZATE. Motorul decide rezultatul + auditul; ordinul
efectiv se trimite prin adaptorul demo existent. VE nu trimite ordine și nu atinge date reale.
