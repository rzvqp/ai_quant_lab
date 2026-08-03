# VE — CAND-0001 PDH-PDL v2.0 (DEMO_BASELINE): verificarea mecanică a celor trei garduri + starea stratului de tranzacționare

**Document ID:** VE-CAND0001-DEMO-GATE-VERIF-v1.0 · **Data:** 2026-07-30 · **Autor:** Validation Engine
**Constrângeri:** NU ratific · NU modific criteriile · NU rulez pe date reale · GARD 2 neatins · NU modific testul static · NU implementez trimiterea de ordine.

**Surse citite integral:** `STATISTICIAN_CAND0001_DEMO_CRITERIA_v1.0.md` (STAT, manifest v2.7.34 `a11dde7`), `red_team/policy_reviews/RT-OPS-B-0001_PDH_PDL_v2.md`, `RT-OPS-A-0001_batch.md`, `POLICY_PDH_PDL_v2.md` (`1558397`, `alpha-automation-v1`), `CANDIDATE_QUEUE.md`, motorul `code/mstrat.py` (Engine-v2), stratul de execuție din `ai_quant_lab-research-main`.

---

## SARCINA 1 — cele trei garduri, verificate mecanic în Engine-v2

**Engine-v2 = `ai_quant_lab/code/mstrat.py::simulate` (liniile 43-83)** — singurul cod care implementează podeaua pre-înregistrată (`min_executable_risk`). RT-OPS-B linia 94 leagă poarta exact de acest motor: *„If the DEMO engine cannot be shown to enforce Engine-v2, the policy must not trade."*

| Gard | Cerință (criteriile DEMO) | Ce face Engine-v2 (citat cod) | Câmp de audit per-tranzacție? | Verdict |
|---|---|---|---|---|
| **S1** | ierarhie worst-case **STOP > TIME-STOP > TARGET** la **toate 3** coliziunile (stop∧țintă, stop∧time-stop, țintă∧time-stop); câmp `intrabar_ordering` | bucla `for j in range(ei,…)` cu `tfirst=False` verifică `hitS` apoi `hitT` (l.72-74) = **doar STOP>TARGET**. Time-stop-ul politicii = **închiderea zilei** (`day_index` boundary); Engine-v2 folosește un **timeout pe număr de bare** (`to`=48/ep, l.58/63), **nu** granița de zi. Pe bara de timeout, ținta câștigă (l.74) ÎNAINTE de ieșirea la close (l.75) → presupunerea optimistă „ținta prima" pe care RT a interzis-o. | **NU** (ieșirea = `{R,si,ei}`, l.82-83) | **NEIMPUS** (1 din 3 coliziuni; time-stop de zi nemodelat; audit absent) |
| **S2** | `min_executable_risk`=max(2×spread,5×tick,0,10×ATR); 1R pe distanța podită; **effective_spread = REAL observat**; audit `strategy_stop_distance`/`min_executable_risk`/`executable_stop_distance`/`floored` | formula **corectă** (l.53); podire + 1R pe `risk` podit (l.55, l.82) ✓. DAR `effective_spread = cfg['spread_ticks']×TICK` = **constantă MODELATĂ** (l.53), nu spread realizat. `strategy_stop_distance` e **suprascris** (l.55 reasignează `risk`/`stop`) → distanța pre-podire se pierde. | **NU** (niciunul din cele 4 câmpuri) | **PARȚIAL** (formulă+sizing OK; spread observat LIPSĂ; audit ABSENT) |
| **S3** | ținta scanată **strict de la `entry_idx+1`**; atingere anterioară în zi irelevantă; audit fereastră de scanare | bucla pornește la **`j=ei`** (bara de intrare), **nu** `ei+1` (l.63). O atingere pe bara de intrare e numărată (excepție îngustă: doar trade-uri podite cu `xi==ei` → INVALID_EXECUTION, l.80). | **NU** | **NEIMPUS ca specificat** (scanează de la `ei`, nu `ei+1`; audit absent) |

**Audit per-tranzacție (obligatoriu, nu opțional — criteriile DEMO):** `simulate()` întoarce `DataFrame{R, si, ei}` — **ZERO** din câmpurile mandatate (`intrabar_ordering`; `strategy_stop_distance`/`min_executable_risk`/`executable_stop_distance`/`floored`; fereastra de scanare a țintei; motivul ieșirii).

### POARTA RED TEAM — rezultat
Cele trei garduri **NU pot fi arătate ca impuse** în Engine-v2 cu câmpurile de audit cerute. Condiția RED TEAM, verbatim: *„Dacă motorul DEMO nu poate fi arătat ca impune cele trei garduri, politica NU tranzacționează."*

> ## → POARTĂ = BLOCAT. CAND-0001 PDH-PDL v2.0 NU tranzacționează pe DEMO în starea actuală.

### Ce îi trebuie fiecărui gard (concret; NU proiectez metoda de risc)
- **S1:** modelează time-stop-ul la închiderea zilei (`day_index` boundary, ca în politică) ca ieșire de rang întâi; rezolvă toate 3 coliziunile worst-case pe bara-graniță (STOP > TIME-STOP > TARGET); emite `intrabar_ordering`. INVALID_EXECUTION rămâne îngust.
- **S2:** pe DEMO, alimentează `effective_spread` = spread realizat observat (nu constanta `cfg`); păstrează și emite `strategy_stop_distance` (pre-podire), `min_executable_risk`, `executable_stop_distance`, `floored`.
- **S3:** pornește scanarea rezultatului la `entry_idx+1`; emite fereastra; o atingere anterioară a nivelului în aceeași zi e irelevantă.
- Emite `exit_reason` (stop/țintă/time-stop/INVALID_EXECUTION) per tranzacție.

**Notă:** Engine-v2 e un **simulator de backtest** (timeout pe bare, cost modelat). Un motor DEMO care satisface criteriile **nu există încă**. Nu l-am construit (mandat: verifică, nu implementa) și nu am rulat pe date reale.

---

## SARCINA 2 — starea stratului de tranzacționare (recunoaștere; NU am rulat/verificat o trimitere)

> ⚠ **Premisa mandatului e materialmente învechită.** O corectez, factual, nu o interpretez.

1. **Locație:** fișierele numite (`mt5_adapter.py`, `mt5_gateway.py`, `mt5_types.py`, `connection.py`) **NU sunt** în worktree-ul `alpha-automation` (unde stă CAND-0001). Sunt în **`ai_quant_lab-research-main`** (branch `ai-trader-implementation`), sub `ai_trader/execution_engine/adapters/`. `alpha-automation` are DOAR Protocolul abstract `broker_adapter.py`, fără cod MT5 concret.
2. **Scopul testului static:** `test_static_no_trading_calls.py` scanează **DOAR `adapters/*.py`** (glob ne-recursiv, `_PACKAGE_ROOT.glob("*.py")`, l.14/32; `tests/` exclus). Interzice prin substring `order_send`/`order_check`/`order_calc_*` + `getattr(`/`importlib`/`eval(`/`exec(` **într-un singur director**. **NU** scanează „tot codul de producție" — contrar formulării mandatului.
3. **Trimiterea de ordine EXISTĂ deja, ÎN AFARA scopului testului:** `ai_trader/mt5_demo_execution/` (adapter/gateway/request_builder/gating/safety) implementează `order_check`→`order_send` cu garduri fail-closed; `MT5DemoBrokerAdapter` subclasează adaptorul read-only și adaugă `submit_order`. Fiind **frate** cu `adapters/`, testul static nu-l examinează niciodată.
4. **Un ordin DEMO real a fost deja trimis** din calea aceea: **BTCUSD 0,01 lot, tichet broker 491745557, retcode 10009**, deschis+închis+verificat flat, autorizat CEO 2026-07-25, commit **`a3ef1c7`** (branch `ai-trader-implementation`). ⚠ **Instrument DIFERIT și pilot DIFERIT (linia AI-Trader), NU CAND-0001 PDH-PDL**, și **NU impune gardurile CAND-0001**. Nu am re-rulat/verificat independent trimiterea; raportat din artefacte + jurnal committate.

### Ce lipsește CONCRET pentru un ordin DEMO CAND-0001 PDH-PDL
**NU „ridicarea testului static".** Mecanismul de trimitere există (în celălalt worktree). Lipsesc, specific:
- **Motorul DEMO care impune gardurile** (cele 3 garduri neimpuse + audit din SARCINA 1) — fără el, per condiția RT, politica nu tranzacționează, indiferent de capacitatea de trimitere.
- **Legarea politicii CAND-0001** (PDH-PDL, `alpha-automation`) de un adaptor de broker: `alpha-automation` n-are MT5 concret; calea demo-execution e în `research-main`, agnostică la instrument, **necablată** la semnalul/sizing-ul CAND-0001.
- Rezerve operaționale (din recunoaștere; nu blochează o singură trimitere, dar reale): toggle AlgoTrading manual în UI; credențiale non-interactive codate dar neverificate; `MetaTrader5` lipsă din `requirements.txt`; trimiterea condusă de un script din rădăcină, nu o buclă automată; plafon de comentariu specific brokerului; cont în PLN, mapare de simbol literală.

### Ce ar trebui modificat, și unde (NU implementez — poartă CEO)
- Cablează `MT5DemoBrokerAdapter` (`research-main`) ca adaptor în orchestrator dintr-un punct de intrare live; SAU construiește echivalentul în `alpha-automation`.
- Adaugă `MetaTrader5` în `requirements.txt`.
- Populează `BrokerCredentials` (`connection.py`) pentru login non-interactiv, sau explicitează presupunerea terminalului pre-autentificat.
- Construiește motorul DEMO CAND-0001 care impune S1/S2/S3 + audit și îi dă ordinele adaptorului.
- **Niciuna nu cere atingerea testului static.**

### Ce riscuri introduce ridicarea testului static (ce protejează)
Păzește pachetul read-only `adapters/`: (1) îl ține read-only (fără `order_send`/`order_check`/margin-calc în `adapters/*.py`); (2) interzice dispatch dinamic (`getattr`/`importlib`/`eval`/`exec`) care ar strecura un apel pe lângă un grep; (3) interzice mutarea programatică a setărilor terminalului / AlgoTrading; (4) dovedește structural că `RealMT5Gateway`/`MT5ReadOnlyBrokerAdapter` nu expun metode de tranzacționare. Ridicarea îl pierde **pentru acel director**. **Corecție-cheie:** ridicarea **NU deblochează** DEMO-ul CAND-0001 (calea de trimitere e deja altundeva) → nu e nici necesară, nici suficientă pentru scopul acestui mandat. **NU l-am modificat**; ridicarea rămâne o poartă separată CEO, ca GARD 1/GARD 2.

---

## Constrângeri respectate
Nu am ratificat politica. Nu am modificat criteriile. Nicio rulare pe date reale. GARD 2 neatins (sigilatul niciodată citit). Testul static nemodificat; trimiterea de ordine neimplementată.

## HANDOFF → CEO
Decizii necesare: **(a)** poarta RT e acum **BLOCAT** — CAND-0001 nu tranzacționează până când Engine-v2 (sau un motor DEMO) nu impune demonstrabil cele trei garduri cu câmpurile de audit numite; **(b)** autorizarea (sau nu) a construirii acelui motor DEMO; **(c)** decizia de proveniență/cablare a stratului de tranzacționare (calea demo din `research-main` vs `alpha-automation`); **(d)** corecția premisei testului static (protejează un director, nu tot codul; trimiterea există deja în afara scopului lui).
