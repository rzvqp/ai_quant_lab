# STATISTICIAN — `w_atr` FIXAT. CONFIGURAȚIE FINALĂ PENTRU `ve_n1_replay 0.3.1`

**Document ID:** STAT-RANGE-V2-WATR-FINAL-v1.0 · **Data:** 2026-08-18 · **Autor:** Statistician
**Status terminal:** **`RANGE_V2_NUMERIC_CONFIG_FINAL_READY_FOR_VE_0_3_1`**
**Comparație VE:** **`VE_DEFAULTS_DIFFER_FROM_FINAL_CONFIG`**
**Protocol executat:** `STAT-RANGE-V2-PREREG-PROTOCOL-v1.0`, commit **`4e69e22`**, `2026-08-18T20:24:20+03:00`
**BLIND_UNTOUCHED** · **SEALED/OOS_ACCESS = 0** · zero PnL · zero strategie · zero cost gate · zero p-value · zero Alpha · zero AI Trader · zero LIVE_SHADOW.

---

# 1 — DOVADA DE PRECEDENȚĂ

```
protocol comis   4e69e22   2026-08-18T20:24:20+03:00   ← ÎNAINTE de orice atingere a datelor
rezultat comis   acest document, commit SEPARAT, care citează 4e69e22
```

**Protocolul a fost scris, comis și împins înainte ca vreo bară din populația eligibilă să fie citită pentru selecție. Nu am revenit la §2 după ce am văzut rezultatul. O singură rulare, o singură selecție.**

**Verificat din Git înaintea lucrului:** `7c0987d` · manifest v2.7.79 `4fd6bdc` · fingerprint `55c08b32…` MATCH · `d307aec` · `22e1496` · wheel `34603375…` · defaulturi VE NERATIFICATE `w_atr=0.25`, `s_max=0.15` · `n_generated_total = 363`.
**CONFIRM: RC-07 și RC-08 nu au fost accesate — intervalele lor canonice rămân nerezolvate. CONFIRM: RC-06 nu a fost tratat ca blind independent (`RC-06 ⊂ RC-05`).**

---

# 2 — REZULTATUL SELECȚIEI DETERMINISTE

```
populație canonică      197.094 bare
excluse (RC-03/04/05/06 + tampon 96 bare)   4.577
ELIGIBILE               192.517
ferestre                nesuprapuse, L = 96, aliniate pe indexul canonic, ordine cronologică
selectată               PRIMA care satisface criteriul de canal
```

## `RC-CONSTRUCTION-CHANNEL-NEW-01`

```
episode_id           RC-CONSTRUCTION-CHANNEL-NEW-01
rol                  CONTROL NEGATIV DE CONSTRUCȚIE
                     NU blind · NU ipoteză · NU produce p-value · NU intră în Alpha ·
                     NU pentru PnL · NU modifică m_inference (26) · NU modifică n_generated_total (363)
index canonic        [192 , 288)          L = 96 bare
structural_start_ts  2011-07-28T17:30:00Z
confirm_ts           2011-07-29T17:45:00Z    (ultima bară ÎNCHISĂ a ferestrei)
sens                 CHANNEL_UP              slope = +0,123642 preț/bară
S = |slope|·L/ATR    3,3781                  (prag DERIVAT >= 2,0)
n_cross              6                       (prag >= 4, parametric liber)
ATR_ref              3,5137                  ATR(14) M15 la indexul 287
limitele episodului  high 1632,83  ·  low 1610,74
data_hash            ee962a714e3728867d70bd0b09a847cec0ff4eeb23c4a4a9fda4e8254037e41a
regula de selecție   prima fereastră nesuprapusă, ordine cronologică, cu S>=2,0 și n_cross>=4
```

**De ce e CANAL și nu RANGE:** deriva cumulată e `S = 3,3781` ori ATR, adică prețul a parcurs în deriva netă de peste trei ori ATR-ul pe durata ferestrei — a PĂRĂSIT orice zonă de lățime admisibilă. Iar `n_cross = 6` arată că totuși OSCILEAZĂ în jurul dreptei, deci nu e un trend pur, ci un canal. Cele două împreună îl definesc.

**Clauza de rezervă rămâne activă:** dacă Red Team constată suprapunere cu RC-07/RC-08 (fie și o bară), se ia URMĂTOAREA fereastră în aceeași ordine, fără altă schimbare. Ordinea e fixată în protocol.

---

# 3 — DECIZIA NUMERICĂ `w_atr`

```
4.1  LIMITA INFERIOARĂ — validitatea atingerii prin fitil
     mediana overshoot-ului peste ancoră, pe barele de RESPINGERE, pooled pe cele trei pozitive
        RC-03  0,2559        RC-04  0,2949        RC-05  0,2596        (×ATR)
        POOLED  w_lower = 0,2823          n = 59.737 bare de respingere
4.2  LIMITA SUPERIOARĂ
     w_upper = min( 0,495 ,  S/2 = 1,6890 ) = 0,4950     ← disjuncția zonelor e cea care leagă
4.3  REGULA DE FIXARE
     cel mai MIC element din L05 = {0,10 … 0,45} care e >= w_lower
```

> # **`w_atr = 0,30`**
>
> **`s_max = 2 × w_atr = 0,60`**

## Verificarea de stabilitate (§4.4(d))

```
w_atr calculat pe FIECARE episod separat:  RC-03 → 0,30 · RC-04 → 0,30 · RC-05 → 0,30
deviația maximă față de valoarea pooled = 0,00 <= 0,05 (un pas de rețea)  ⇒  STABIL
Rezultatul NU depinde de un singur episod.
```

## Cele șapte condiții simultane cerute — toate verificate la `w_atr = 0,30`

```
                                        RC-03     RC-04     RC-05
pozitivele rămân recunoscute cauzal     100,0%    100,0%    100,0%      ✔
zonele NU devin degenerat suprapuse      0,00%     0,74%     0,26%      ✔
respingerile prin fitil rămân valide     55,3%     50,6%     54,9%      ✔  (peste mediană, prin construcție)
non-intersecția NU e atingere            prin definiție                 ✔
controlul de canal NU e clasificat range S = 3,3781 > s_max = 0,60      ✔  RESPINS
stabil la variații mici                  toate trei dau 0,30            ✔
niciun rezultat blind consumat           RC-07/RC-08 neatinse           ✔
```

**Analiza de sensibilitate e DESCRIPTIVĂ, nu selectivă: recunoașterea pozitivelor e insensibilă pe tot intervalul (99,9-100% de la 0,10 la 1,25), degenerarea crește monoton (0,3% la 0,25 → ~4% la 0,50 → ~30% la 1,00). NU am ales după ocupare, după numărul de evenimente, sau după „cea mai bună" valoare. Valoarea a ieșit din regula pre-înregistrată aplicată unei măsurători.**

---

# 4 — CONFIGURAȚIA CANONICĂ SERIALIZATĂ

```json
{
  "range_state_schema_version": "range-state-v2",
  "event_contract_version": "range-events-v2",
  "w_atr": 0.30,
  "w_atr_semantics": "SEMI-WIDTH in ATR units; total zone width = 2 * w_atr * ATR_ref",
  "zone_upper": "[anchor_up - w_atr*ATR_ref , anchor_up + w_atr*ATR_ref]",
  "zone_lower": "[anchor_dn - w_atr*ATR_ref , anchor_dn + w_atr*ATR_ref]",
  "anchor_up": "MEDIAN(high of confirmed swing highs in window)",
  "anchor_dn": "MEDIAN(low of confirmed swing lows in window)",
  "median_even_count": "mean of the two central values",
  "touch": "bar interval [low,high] INTERSECTS the zone; wick rejection IS a touch; non-intersection is NOT",
  "symmetry": "same w_atr for upper and lower",
  "atr_period": 14,
  "atr_timeframe": "15m",
  "atr_index": "evaluation bar i (CLOSED)",
  "atr_as_of": "confirm_ts = bar i; all inputs index <= i",
  "atr_unavailable": "Unavailable(reason=ATR_UNAVAILABLE); never assumed, never default, never zero",
  "s_max": 0.60,
  "s_max_derivation": "s_max IDENTICALLY 2 * w_atr - COMPUTED, never stored as an independent literal",
  "slope": "OLS on close, x = 0..d_min-1 (BAR INDICES, not calendar time)",
  "slope_window": "the exact d_min CLOSED bars ending at evaluation bar i",
  "S": "|slope| * d_min / ATR_ref  [dimensionless]",
  "n_touch": 2,
  "d_min_bars": {"INTRADAY_RANGE": 24, "MULTIDAY_RANGE": 96},
  "n_acceptance": 2,
  "swing_k": 2,
  "precedence_rule": "RANGE_STATE_OVER_TREND_PAUSE",
  "timeframe": "15m",
  "reason_codes": ["OK_RANGE","FEW_TOUCHES","TOO_SHORT","WARMUP","ATR_UNAVAILABLE",
                   "BOUNDARY_EXTENDED","ACCEPTED_BREAK","MAX_DURATION",
                   "CHANNEL_UP_SLOPE","CHANNEL_DOWN_SLOPE","SLOPE_UNAVAILABLE",
                   "NO_ENTRY_BY_CONSTRUCTION","ZONES_DEGENERATE"]
}
```

```
PRAGURI DE PANTĂ    S <= s_max               → RANGE admis pe axa pantei
                    S >  s_max ȘI slope > 0  → CHANNEL_UP      reason CHANNEL_UP_SLOPE
                    S >  s_max ȘI slope < 0  → CHANNEL_DOWN    reason CHANNEL_DOWN_SLOPE
                    ATR indisponibil          → Unavailable     reason SLOPE_UNAVAILABLE
GARDĂ NOUĂ          2*w_atr*ATR_ref >= (anchor_up − anchor_dn) → Unavailable, reason ZONES_DEGENERATE
                    (zonele s-ar suprapune; măsurat sub 1% la w=0,30, dar fail-closed prin tip)
```

---

# 5 — COMPARAȚIA CU DEFAULTURILE VE 0.3.0

```
                    VE 0.3.0        FINAL          diferență
w_atr               0,25            0,30           +0,05 (un pas de rețea)
s_max               0,15            0,60           factor 4×
cuplarea w ↔ s      ABSENTĂ         OBLIGATORIE    structurală
```

> # **`VE_DEFAULTS_DIFFER_FROM_FINAL_CONFIG`**
>
> **Diferă pe ambele valori și, mai important, STRUCTURAL: în 0.3.0 `s_max` e o constantă liberă; aici nu e parametru deloc, ci `2·w_atr` calculat. Chiar dacă `w_atr` ar fi coincis, `s_max` derivat ar fi fost 0,50 la 0,25 — nu 0,15. Valoarea VE era admisibilă dar nederivată, exact cuplarea absentă care a produs defectul V1.**

**Consemnez și că `w_atr = 0,25` al VE se afla ÎN intervalul admisibil și la un singur pas de rețea de valoarea derivată. Propunerea VE era rezonabilă; ce lipsea era derivarea, nu bunul-simț.**

---

# 6 — INSTRUCȚIUNEA EXACTĂ PENTRU `ve_n1_replay 0.3.1`

```
1. `w_atr = 0.30`, ratificat prin acest document.
2. `s_max` NU se stochează. Se CALCULEAZĂ ca `2 * w_atr` în cod. Cuplarea trebuie să fie
   NEREPREZENTABILĂ ca doi parametri liberi — dacă un cititor poate seta `s_max` independent,
   contractul e încălcat.
3. Panta: OLS pe `close`, `x` = INDICI DE BARĂ 0..d_min−1, `S = |slope|*d_min/ATR_ref`,
   `ATR_ref` = ATR(14) M15 la bara de evaluare — ACEEAȘI citire cauzală ca zona, nu o a doua.
4. Gardă `ZONES_DEGENERATE` (§4), fail-closed prin tip.
5. Citează ACEST commit Statistician ca sursă normativă, plus protocolul `4e69e22`.
6. `range_spec_id` RECALCULAT ⇒ rezultatele 0.3.0 devin NON-COMPARABILE PRIN TIP, automat.
7. Sidecar manifest actualizat. **0.3.0 NU se suprascrie** — rămâne pentru audit.
8. Restul logicii BYTE-IDENTIC față de 0.3.0, în afara celor de mai sus.
9. Red Team primește EXCLUSIV 0.3.1 pin-uit. **NU autorizez Red Team pe 0.3.0.**
```

---

# 7 — PROTOCOLUL RED TEAM, CU RC-07/RC-08 PĂSTRATE BLIND

```
1. RT primește NUMAI `ve_n1_replay 0.3.1` pin-uit, cu `w_atr = 0,30` și `s_max` calculat.
2. RT verifică ÎNTÂI non-suprapunerea `RC-CONSTRUCTION-CHANNEL-NEW-01` ([192,288),
   2011-07-28/29) cu RC-07 și RC-08. RT deține intervalele; eu nu. Dacă există suprapunere,
   se aplică clauza de rezervă din protocol: următoarea fereastră în aceeași ordine.
3. RT rulează pe RC-07 și RC-08 — episoade pe care VE NU le-a văzut și pe care eu nu le-am atins.
4. Testul DECISIV rămâne P2: un detector care marchează un canal drept range a EȘUAT,
   indiferent de ocupare.
5. RT verifică independent zero-lookahead și snapshot bit-identic.
6. Intervalele blind NU se dezvăluie către VE, nici înainte, nici după.
7. Nicio ratificare fără RT PASS și aprobare CEO. Nu ratific detectorul.
```

---

# 8 — DESCHIS, CLASIFICAT

```
BLOCKING     niciunul.
MATERIAL     `RC-CONSTRUCTION-CHANNEL-NEW-01` are L = 96 bare (o zi). Controlul negativ e din
             clasa MULTIDAY; clasa INTRADAY (d_min=24) NU are control negativ propriu.
             Consemnat ca limitare de acoperire, nu ca blocaj: `s_max` e derivat, deci se
             transferă automat între clase.
MATERIAL     verificarea de non-suprapunere cu RC-07/RC-08 e DELEGATĂ Red Team; până la
             confirmarea lor, selecția e provizorie prin clauza de rezervă.
LIMITATION   `w_lower` e o MEDIANĂ: prin construcție ~50% dintre respingerile prin fitil au
             overshoot mai mare decât zona și NU se înregistrează. Aceasta e definiția lui
             „respingerea TIPICĂ se înregistrează", nu un defect — dar se consemnează, fiindcă
             o cerință de acoperire mai mare ar cere o cuantilă mai mare și deci un `w` mai mare,
             care e direcția RISCANTĂ pentru misclasificarea canalelor.
NON-MATERIAL `w_atr` VE (0,25) era în interval, la un pas de rețea de valoarea derivată.
```

**Invariante verificate neatinse: `n_generated_total = 363` · `m_inference = 26` · tombstones · registrul Alpha · verdictele existente · F1-F6 și cele 44 `BLOCKED_PENDING_RANGE_SEMANTIC_FIX` · F7 `SAFETY_GUARD`.**

---

**Manifest:** `config/split_manifest.json` v2.7.80, secțiunea `range_v2_watr_final_v2_7_80`.
