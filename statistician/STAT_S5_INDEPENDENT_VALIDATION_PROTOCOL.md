# S5 — PREGĂTIREA VALIDĂRII INDEPENDENTE

**Divizia Statistician · mandat `STAT-ALPHA-S5-INDEPENDENT-VALIDATION-PREP-001` · 2026-08-21**

```
S5_INDEPENDENT_VALIDATION_EVIDENCE_NOT_CLEAN
FRESH_VALIDATION_EVIDENCE_REQUIRED
```

**Protocolul NU e înghețat.** Nu am pre-înregistrat praguri de acceptare și nu am executat nimic:
condiția din §26 s-a declanșat înainte de acel punct. `FINAL_HOLDOUT_ACCESS_COUNT = 0`.

---

## 1 — IDENTITATEA CANDIDATULUI, ÎNGHEȚATĂ ȘI NEAMBIGUĂ

Verificat direct din `661bb8f` (prezent în toate cele patru worktree-uri) și din registrul istoric.

| element | valoare |
|---|---|
| candidat | `S5` · ID istoric `C_2d587447` |
| familie / mecanism | `S5` · **opening-range momentum** |
| baseline înghețat | `S5_C_2d587447_HISTORICAL_BASELINE` |
| spec canonic | `S5{session=ny, mode=breakout, side=up, stop=or_opp, exit=rr3}` |
| ipoteză reprezentativă | `7472f3d412f2` |
| direcție | **LONG-only** — `direction=long`, `side=up`, declarat explicit „Long-only" în identitatea înghețată |
| intrare | next-bar open |
| stop | frontiera OPUSĂ a opening-range |
| exit | **RR3** |
| clasificare istorică | `B_research_candidate`, `shortlisted = True` |

**§3 — fără ambiguitate de direcție.** Alpha a înghețat formal LONG-only; nu e o alegere post-hoc a
mea. Nu emit `CANDIDATE_SPECIFICATION_AMBIGUITY`.

> **O fragilitate de proveniență, semnalată fără a schimba nimic:** în interiorul clusterului S5, spec-ul
> `mode=breakout` și `mode=retest` au **scoruri de robustețe identice** (1,388343 amândouă). Alegerea
> dintre ele a fost decisă de ordinea de sortare, nu de un criteriu. Spec-ul rămâne înghețat și
> neambiguu — semnalez doar că *breakout vs retest* nu a fost departajat de nicio dovadă.

---

## 2 — ★ AUDITUL DE NOUTATE A DOVEZILOR — `S5_VALIDATION_EVIDENCE_NOVELTY_AUDIT`

### 2.1 Ce declară cercetarea profundă (adevărat, dar insuficient)

`661bb8f` folosește DEVELOPMENT (`< 2018-05`) + CALIBRATION (`2020-01 → 2022-01`), plafonează datele
la `2022-01` și afirmă `VALIDATION_ACCESS_COUNT = 0`, `FINAL_HOLDOUT_ACCESS_COUNT = 0`. **Verificat în
cod:** `deep_research.py` taie setul la `CAL_B` și are `assert d["dt"].max() < VAL` cu
`VAL = 2022-12-01`. Pentru *acel program*, afirmația e corectă.

### 2.2 Ce arată auditul istoric — **contaminarea e reală**

S5 a existat înaintea programului curent. Programul istoric S1–S20 folosește un split **pozițional**:

```
alpha_lab.splits():  research = [0, 60%)   validation = [60%, 80%)   holdout = [80%, 100%]
knowledge_system.py:106     res = d.iloc[:a]      val = d.iloc[a:b]        a = 60%, b = 80%
knowledge_system.py:121     mv = MS.simulate(val, ...)['R']   ->   val_exp = mv.mean()
```

Calendaristic, **partiția VALIDATION istorică = `2020-07-21 → 2023-07-24`** (71.139 bare).

`val_exp` **nu** a fost doar raportat — a intrat în mașinăria de selecție:

```
knowledge_system.py:92
g['rob'] = g['stab'] + g['val_exp'].fillna(0).clip(-0.3, 0.3) + log10(g['n'])/3
           - g['t1'] - (g['dd']/25).clip(upper=1) - g['fragile']*0.5
```

Comentariul de deasupra spune el însuși: *„robustness rank … non-fragile, stable, low-t1, **+OOS**,
more n"*. Iar `build_strategy_library.py:83` pune o poartă pe `ve > 0` pentru nivelul de încredere.

Pentru S5: `rep_val_exp = 0.17885`, contribuind **+0,1788 (8,4%)** la `robustness_score = 2,1383`,
care a produs `shortlisted = True`. **16 din 17 candidați** au fost clasați folosind `val_exp`.

Deci partiția VALIDATION a fost folosită istoric ca să **claseze**, să **preselecteze** și să
**încadreze în încredere** candidatul S5.

### 2.3 Contra-factual, măsurat — onest în ambele sensuri

Am recalculat totul **fără** termenul `val_exp`:

| | cu `val_exp` | fără `val_exp` |
|---|---|---|
| rangul S5 între 17 candidați | **1** | **1** |
| reprezentantul ales în clusterul S5 | `7472f3d412f2` (RR3) | `7472f3d412f2` (RR3) |

**Expunerea nu a schimbat nici clasamentul, nici spec-ul.** RR3 nu a fost ales de dovezile de
validare. Spun asta explicit fiindcă e adevărat și atenuează gravitatea.

**Dar nu restaurează orbirea.** Numărul a fost *citit* și *folosit*: dacă `val_exp` ar fi ieșit
negativ, `rob` scădea cu până la 0,3 și poarta de încredere retrograda candidatul. Un test al cărui
rezultat a fost deja consultat nu mai poate servi drept test independent, chiar dacă de data asta a
confirmat ce spuneau celelalte criterii.

### 2.4 Clasificarea

```
S5_VALIDATION_EVIDENCE_NOVELTY_AUDIT = CONSUMED
```

---

## 3 — ★ DE CE NU EXISTĂ O PARTIȚIE DE ÎNLOCUIRE ÎN LIMITELE AUTORIZATE

Partiția VALIDATION propusă de Alpha e `>= 2022-12-01`. Descompusă față de partiția istorică deja
consumată:

```
VALIDATION istorica consumata : 2020-07-21 -> 2023-07-24   (71.139 bare)
VALIDATION propusa            : 2022-12-01 -> 2026-07-27   (86.226 bare)

  A. CONSUMAT istoric (suprapunere)  2022-12-01 -> 2023-07-24   15.086 bare   17,5%
  B. HOLDOUT SIGILAT (dincolo)       2023-07-24 -> 2026-07-27   71.140 bare   82,5%

  bare NICI consumate, NICI sigilate:      0
```

**Fiecare bară a partiției propuse e ori deja consumată istoric, ori în holdout-ul sigilat.**
§6 interzice holdout-ul; §5 interzice validarea pe dovezi consumate. **Zero** bare rămân utilizabile.

Nu improvizez un substitut, nu redefinesc granițele și nu relaxez §6 ca să ajung la o partiție.

---

## 4 — CONTRACTUL DE EXECUȚIE (înregistrat, nu aplicat)

Rămâne cel ratificat, pentru mandatul viitor: `XAUUSD` · `min_tick = 0,01 USD` · intrare la
**next-bar open** · stop minim `max(2 × spread, 0,05 USD, 10% ATR)` · tratament bid-ask complet ·
BASE și STRESS ratificate · **STRESS round-trip 0,24** · fără execuție favorabilă pe aceeași bară.

## 5 — CE NU AM FĂCUT

Nu am pre-înregistrat praguri de acceptare (§9), fiindcă a fixa praguri pentru dovezi care nu există
ar fi o formalitate goală. Nu am executat S5, nu am generat niciun registru de tranzacții, nu am
calculat nicio metrică de validare, nu am atins holdout-ul, nu am comparat cu Candidate-001 și nu am
combinat niciun portofoliu. Valorile din §1 al mandatului (BASE +0,064, STRESS +0,032 etc.) rămân
**intrări istorice**, nu rezultate de acceptare.

---

## 6 — CE E NECESAR CA SĂ SE POATĂ CONTINUA

Decizia e a CEO; enumăr doar opțiunile care nu încalcă regulile deja ratificate:

1. **Dovezi cu adevărat noi** — date în afara celor 355.696 bare M15 actuale (perioadă nouă
   achiziționată, ori alt instrument/timeframe), niciodată atinse de programul S1–S20.
2. **Deblocarea explicită a unei felii din holdout** ca partiție de validare — decizie exclusiv CEO,
   cu preț epistemic clar: felia folosită încetează să mai fie holdout final, definitiv.
3. **Acceptarea explicită a validării pe dovezi consumate**, etichetată ca atare — *nu* validare
   independentă, cu greutate de validare corespunzător redusă.

Prima e singura care produce o validare independentă în sensul propriu.

---

**Proprietar următor: CEO.** Nu predau nimic către Red Team, fiindcă nu există protocol înghețat de
auditat. Nicio autorizare pentru Strategy Catalog, Alpha, AI Trader, Strategy Router, LIVE_SHADOW,
MT5, broker sau tranzacții.

*`FINAL_HOLDOUT_ACCESS_COUNT = 0` · S5 rămâne `DEEP_RESEARCH_PASS`, **nu** `VALIDATED_STRATEGY`.*
