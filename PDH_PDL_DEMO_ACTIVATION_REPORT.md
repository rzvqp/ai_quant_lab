# PDH-PDL v2.0 DEMO Activation Report

**Data:** 2026-08-04
**Status:** ACTIV — proces continuu, neatendat, pornit cu succes.

## Ce s-a facut in acest pas

1. Verificare de conectivitate (read-only, `pdh_pdl_connectivity_check.py`) rulata pe terminalul MT5
   real, INAINTE de orice lansare. Foloseste exact clasele de productie (`RealMT5DemoGateway`,
   `RealMT5HistoryGateway`, `MT5DemoBrokerAdapter`, `verify_safety_guards`), nu apeluri proprii.
2. Toate verificarile au trecut — vezi tabelul de mai jos.
3. `entrypoint.py` lansat ca proces detasat (`Start-Process -WindowStyle Hidden`), PID **29888**,
   confirmat inca activ dupa warmup. Log de pornire curat, fara erori in stderr.

## Rezultatul verificarii de conectivitate

| Verificare | Rezultat |
|---|---|
| `RealMT5DemoGateway.initialize()` | OK |
| `RealMT5HistoryGateway.initialize()` | OK |
| `MT5DemoBrokerAdapter.connect()` | acceptat |
| Cont DEMO | confirmat |
| Server = FusionMarkets-Demo | confirmat |
| AlgoTrading activ | confirmat |
| Piata deschisa (XAUUSD) | confirmat |
| `symbol_info` (tick_value/tick_size/contract_size) | citite: 3.74134 / 0.01 / 100.0 |
| `point_value` per unitate derivat | 3.74134 (= tick_value/tick_size/contract_size) |
| `history_deals_get` accesibil | OK |
| `positions_get` accesibil | OK |
| Pozitie PDH-PDL "stale" sub MAGIC_NUMBER=100001 | 0 (curat, fara conflict la pornire) |
| Stare circuit breaker | READY, fara reason_code |

Toate verificarile: **PASSED**. Lansarea a continuat conform instructiunii — nicio verificare nu a picat,
deci nu a fost nevoie de oprire.

## Ce ruleaza acum

- **Politica:** CAND-0001 PDH-PDL v2.0, INGHETATA (frozen la commit-ul semnalat de tine, `1558397`,
  in submodulul vendor).
- **Lant:** `PdhPdlRecognitionRule` (Part A: PDH/PDL + first-touch, ratificat) → S2 (floor de risc, live,
  din tick-ul curent) → `send_after_dry_run_gate` (dry-run apoi demo) → `MT5DemoBrokerAdapter` → MT5.
  Motorul `demo_gate_engine` (S1/S3) chemat **post-hoc, o singura data**, dupa inchiderea pozitiei —
  niciodata ca input de decizie live.
- **Simbol:** XAUUSD. **Cont:** DEMO FusionMarkets. **Risc:** 0,5% din `compute_sizing`, NEocolit —
  volumul calculat normal, nu hardcodat (spre deosebire de testul de instalatie anterior).
- **Timeframe:** M15. **Interval de polling:** 30s intre verificari de bare noi.
- **State store:** `pdh_pdl_live_state/xauusd_m15.db` (SQLite — watermark bar feed, jurnal semnale,
  jurnal audit PDH-PDL, ledger-e/jurnale de ordine dry-run si demo, high-water-mark portofoliu). Nou,
  separat complet de `live_observation_state/` — nicio suprapunere de fisiere sau conexiuni.
- **Observarea live (Mandatul 5)** continua neschimbata, in paralel, propriul ei proces.

## Ce raportez de-acum

- **Per tranzactie inchisa:** tichet, preturi cerute/fill la ambele capete, spread observat la trimitere,
  volum + risc efectiv (%), toate campurile de audit ale motorului (`exit_reason`, `net_R`,
  `strategy_stop_distance`, `executable_stop_distance`, `floored`, etc.), rezolvarea (STOP/TARGET/
  TIME_STOP), costul realizat round-trip.
- **Saptamanal, cumulativ:** numar tranzactii, winrate, expectancy in dolari, distributia costului
  realizat fata de 0,20 modelat, refuzuri de garduri (S1/S2/S3 sau risc/RiskConfig) cu motivul.

Niciun rezultat din aceasta rulare nu constituie validare statistica si nu promoveaza nimic — este
DEMO_BASELINE, exact cum ai specificat.

## Constrangeri respectate

- Politica INGHETATA, neatinsa.
- Motorul niciodata ocolit; NO_TRADE si INVALID_EXECUTION se respecta necontestat.
- `compute_sizing` ruleaza normal (nu ocolit, spre deosebire de testul de instalatie).
- Nimic din acest pas nu a modificat `demo_gate_engine`, `mstrat.py`, sau politica insasi — verificat
  static prin testele existente ale pachetului (`test_mstrat_is_never_referenced`,
  `test_demo_gate_engine_is_never_reimplemented`).

## Cablare pentru politici multiple — inca neinceput

Instructiunea "construieste cablarea ca sa poata primi politici multiple, dar nu le activa acum" este
notata ca urmatorul pas de arhitectura, dupa ce Alpha corecteaza orizontul la CAND-0009/0019 si dupa
re-screening. Nu a fost inceput in acest pas — voi reveni cu un design inainte de a construi, ca sa il
confirmi.

## Commit-uri acestui pas

- `b1ceb3a` — factory de dependinte reale, tick/fill readers, entrypoint (compute_sizing normal), 61/61
  teste, mypy strict curat.
- `e08bd20` — script de verificare conectivitate + `.gitignore` pentru starea de runtime.

Ambele impinse pe `trader/ai-trader-implementation`, hash verificat la remote.
