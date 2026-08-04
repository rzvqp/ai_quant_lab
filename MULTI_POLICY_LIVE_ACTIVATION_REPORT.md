# Raport: Cablare Politici Multiple — construit, testat, ACTIVAT (CAND-0007, CAND-0019)

**Data:** 2026-08-04
**Status:** ACTIV. CAND-0007 și CAND-0019 pornite, PID 13268, confirmat viu. CAND-0009 rămâne
inactiv (construit, așteaptă re-screening cu orizontul de 14 bare). CAND-0001 (PID 29888)
neîntrerupt pe tot parcursul.

## Activare (după confirmarea ta)

1. Flag-uri de pauză setate în store-ul partajat: `CAND-0007=True`, `CAND-0019=True`,
   `CAND-0009` neatins (implicit `False`).
2. `entrypoint.py` lansat ca proces detașat (`Start-Process -WindowStyle Hidden`), PID **13268**,
   log de pornire curat, fără nimic in stderr, confirmat viu după warmup:
   `multi_policy_live: starting -- symbol=XAUUSD mt5_timeframe=15 bar_seconds=900
   poll_interval_seconds=30.0 policies=CAND-0007,CAND-0019(active) CAND-0009(built,inactive)`.
3. CAND-0001 (PID 29888) verificat viu înainte și după lansare — neatins.

## Ce raportez de-acum, per tranzacție închisă, per politică

Tichet, prețuri cerute/fill la ambele capete, spread observat, volum și risc efectiv,
câmpurile de audit ale motorului, rezoluția, costul realizat round-trip.

**Săptămânal, cumulativ, per politică ȘI agregat**, plus un contor separat pentru câte semnale
regula de excludere a blocat (deocamdată zero posibil, cât timp CAND-0009 rămâne inactiv).

## Ce am construit

Pachet nou, `ai_trader/multi_policy_live/` — `pdh_pdl_demo/` (CAND-0001) rămâne complet neatins,
încă rulează neîntrerupt (PID 29888, confirmat pe tot parcursul construcției).

| Politică | Fișier | STRATEGY_ID | MAGIC_NUMBER | Stare |
|---|---|---|---|---|
| CAND-0001 PDH-PDL | (existent, `pdh_pdl_demo/`) | S9001 | 100001 | activ, propriul proces |
| CAND-0007 Level×FVG | `recognition_level_fvg_confluence.py` | S9002 | 100002 | **gata de pornit** |
| CAND-0009 Level-Break-Drive | `recognition_level_break_drive.py` | S9003 | 100003 | **construit, INACTIV** |
| CAND-0019 DZ×Level | `recognition_dz_level_confluence.py` | S9004 | 100004 | **gata de pornit** |

## Lanțul complet

Un singur proces (`entrypoint.py`), un singur `LiveBarFeed` partajat (toate trei urmăresc aceleași
bare XAUUSD M15) → fiecare politică: recognition rule proprie → `PolicyOrchestrator` propriu
(clasă comună, instanțe independente — motorul `demo_gate_engine` e chemat din ACELAȘI import,
niciodată duplicat) → `send_after_dry_run_gate` (aceeași cale ca CAND-0001) → adaptor demo → MT5.
Motorul chemat post-hoc, o singură dată, după închidere.

Izolare per politică: jurnal de audit separat (fișier SQLite propriu), `try/except` cu
auto-degradare (o excepție într-o politică nu oprește pe celelalte, jurnalizată ca
`POLICY_ERROR_<etapă>`), flag de pauză persistat (implicit dezactivat pentru orice politică
neactivată explicit — de-asta CAND-0009 pornește deja oprit, fără cod suplimentar).

Circuit breaker: citit proaspăt, la fiecare tick, din fișierul de stare AL LUI CAND-0001 — o
suspendare din pierderi/drawdown oprește tot, nu doar politicile noi.

## Regula de excludere (CAND-0001 vs CAND-0009)

Implementată exact cum ai decis — excludere, nu prioritate. Constrângere onestă, semnalată: CAND-0001
rulează în propriul proces, neatins — cablarea nouă poate doar SĂ CITEASCĂ jurnalul lui deja scris
înainte ca CAND-0009 să trimită, nu poate opri simultan pe amândouă la o coincidență perfectă de bară.
În practică, acoperă cazul relevant (CAND-0001 aproape întotdeauna scrie înainte ca procesul nou,
cu polling la 30s, să ajungă la aceeași bară) — dar nu e o garanție matematică perfectă fără să ating
procesul lui CAND-0001, ceea ce n-a fost autorizat. Oricum, CAND-0009 rămâne oprit acum, deci
mecanismul e cablat dar neexercitat.

## Riscul — opțiunea D aplicată

Fiecare politică — propria ei `LivePdhPdlDepsFactory`, propriul `compute_sizing` la 0,5% implicit.
Niciun plafon nou, niciun bazin comun. Exact cum ai decis.

## Testare — cele 5 exemple de audit cerute

Toate din `tests/test_orchestration.py`, rulate pe `PolicyOrchestrator` (clasa comună folosită de
CAND-0007/0009/0019):

| Rezoluție | Rezultat verificat |
|---|---|
| **STOP** | `exit_reason="stop"`, `net_R<0` |
| **TARGET** | `exit_reason="target"`, `net_R>0` |
| **TIME_STOP** | `exit_reason="time_stop"`, ieșire la închiderea zilei |
| **INVALID_EXECUTION** | `exit_reason="invalid_execution"` (gap prin stopul flotat la intrare) |
| **NO_TRADE** | `exit_reason="no_trade"`, `net_R=None` |

Plus un test dedicat pentru hook-ul de sentinelă al lui CAND-0009 (`target_price_for_audit`) —
confirmă că motorul primește un target de nefolosit (dincolo de orice interval observat) și că
înregistrarea de audit marchează explicit `target_price_is_sentinel: true`, ca să nu fie confundat
cu un nivel real de nimeni care citește jurnalul mai târziu.

**Scenariile de confluență pentru CAND-0007 și CAND-0019 au fost verificate direct împotriva
detectoarelor reale** (`detect_fvgs`, `detect_fvg_reactions`, `detect_demand_zones`,
`detect_level_touches`) rulate separat, ÎNAINTE de a le transcrie în teste — nu deduse manual.

## Rezultate

- **46/46 teste** pachet nou, `mypy --strict` curat.
- **Verificare pe terminalul real**: `build_loop()` s-a conectat, un `tick()` a rulat cu succes,
  zero politici degradate.
- Rulare completă pe tot arborele `ai_trader/` pornită ca due-diligence suplimentar (în fundal,
  ~5 ore pe baza precedentului) — raportez separat dacă găsește ceva neașteptat.
- Commit `aa03244`, împins pe `trader/ai-trader-implementation`, hash verificat la remote.

## Ce NU am făcut

Nu am pornit procesul. Nu am activat flag-urile de pauză pentru CAND-0007/CAND-0019. CAND-0001
continuă exact cum era, neatins pe tot parcursul.

Aștept confirmarea ta înainte de a porni.
