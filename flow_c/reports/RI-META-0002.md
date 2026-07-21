─────────────────────────────────────────────
ESTIMATED ALPHA IMPACT:  🔴 HIGH
  (val_exp = presupusa coloană de validare; comportamentul ei atinge direct capacitatea Alpha
   de a discerne edge-uri robuste. Regula permanentă CEO — impact estimat la început.)
─────────────────────────────────────────────
FLOW C — META ANALYSIS (P2 / WP2)
ID:              RI-META-0002
Data:            2026-07-21
Autor:           Research Intelligence (Alpha Intelligence Division)
Nivel epistemic: cunoaștere-observațională relațională (P2)
Încredere:       C2 pentru ASOCIERE (robustă: CI exclude 0, 19/20 familii, supraviețuiește leave-S1-out).
                 Semantica `val_exp` verificată (OOS temporal); confundul de perioadă = fapt structural.
─────────────────────────────────────────────
BAZA DE DOVEZI
  • Sursă:  results/FAMILY_RESULTS.parquet (reprodus bit-exact). Complete-case pe `val_exp`.
  • Metodă: diferență PERECHE d = val_exp − exp per ipoteză; median + CI bootstrap cluster-FAMILIE
            (10.000, seed 20260721); leave-S1-out (mandat WP1). Simplu, conform principiului simplității.
  • NON-fabricare: calcul direct pe corpul existent; nicio dată nouă.
─────────────────────────────────────────────
SEMANTICA `val_exp` — VERIFICATĂ (pas de clarificare atașat WP2)
  Sursă autoritativă: code/run_full_campaign.py (pipeline de generare a FAMILY_RESULTS), liniile 3-4, 24:
    d=MS.load(); a=int(n*0.6); b=int(n*0.8); res=d[:a]; val=d[a:b]   # holdout d[b:] SEALED
    mv=MS.backtest(val,h); val_exp = mv['R'].mean()  if len(mv)>=5 else NaN
  → `exp`      = expectancy (mean R) pe segmentul IN-SAMPLE = primele 60% temporale (res).
  → `val_exp`  = expectancy (mean R) pe segmentul de VALIDARE = următoarele 20% temporale (val),
                 un OOS temporal DISJUNCT de in-sample. Holdout-ul final (ultimele 20%) e SIGILAT.
  → `val_exp` NaN c"nd strategia are <5 trade-uri pe segmentul val (de aici lipsa; vezi §5).
  CONCLUZIE: `val_exp` NU e o coloană „stricată" — e un OOS temporal legitim. DAR `exp` și `val_exp`
  sunt pe FERESTRE DE TIMP DISJUNCTE → diferența lor conflează robustețea cu diferența de perioadă/regim.
PLAFON EPISTEMIC (P2): asociativ, NU cauzal, NU validat. Mecanismul „de ce OOS>IS" = 🔒 P4.
─────────────────────────────────────────────

# 1. ÎNTREBAREA RELAȚIONALĂ (WP2)

`val_exp` vs `exp` — care e diferența PERECHE per ipoteză (nu marginale)?
**Populație:** complete-case pe val_exp (n=1796; excluse 176, toate S1; S1 rămâne 976 în cc). Unitate=ipoteză, cluster=familie.
**Estimand primar:** median al diferenței pereche d = val_exp − exp, CI cluster-familie.

# 2. REZULTATE

### 2.1 Primar (corpus-wide, complete-case)
- **median(d) = +0,072**, 95% CI cluster-familie **[+0,061; +0,112]** → **exclude 0, pozitiv**. mean(d)=+0,083.
- **Semn: 77,3% dintre ipoteze au d>0** (val_exp > exp); doar 22,7% d<0.

### 2.2 Leave-S1-out (mandat WP1)
- median(d) fără S1 = **+0,095**, CI [+0,072; +0,118] — **mai puternic** fără S1 (S1-only median d = +0,056). NU e artefact S1.

### 2.3 Pervazivitate per-familie
- **19 din 20 familii au median d > 0** (excepție S14, −0,025). Efect consecvent, nu localizat.

### 2.4 Secundar exploratoriu (câștigători)
- Printre hist_prof (n=247 cc): median d = +0,028; d<0 la 42,9%. Gap-ul e mai MIC la câștigători, mai mare la masa neprofitabilă.

# 3. INTERPRETARE ȘI STARE DE EVIDENȚĂ

- **`val_exp` este SISTEMATIC MAI MARE decât `exp`** (pereche). Stare: **STATISTICALLY SUPPORTED ASSOCIATION** (CI exclude 0, 77% semn, 19/20 familii, supraviețuiește leave-S1-out). Observația în sine e acceptată de CEO.
- Cu semantica verificată: `val_exp` e OOS pe segmentul de validare (următoarele 20% temporale), `exp` e pe primele 60%. Deci OOS (fereastra ulterioară) e sistematic mai bun decât in-sample (fereastra anterioară) — **invers** față de shrinkage-ul tipic de overfitting.
- **Explicația rămâne OPEN** (formulare neutră, ceruta CEO): **semantic mismatch NU e cazul — coloana e un OOS legitim; dar cele două măsuri sunt pe ferestre de timp DISJUNCTE, deci diferența e CONFUNDATĂ cu perioada/regimul.** Cea mai parcimonioasă lectură descriptivă: fereastra de validare (un anumit 20% ulterior) a fost, în medie, mai favorabilă acestor strategii — NU o dovadă de robustețe. Care dintre perioadă/regim/robustețe domină = 🔒 P4.

# 4. REGISTRU DE TESTE
1. median paired d (corpus) = +0,072, CI[+0,061;+0,112] → SUPPORTED (pozitiv).
2. leave-S1-out median d = +0,095, CI[+0,072;+0,118] → confirmă.
3. semn d>0 = 0,773 (descriptiv).
4. per-familie: 19/20 median d>0 (descriptiv).
5. secundar câștigători median d=+0,028 (exploratoriu).
*Toate raportate; FDR neaplicabil pe un singur estimand primar direcțional (decizie CEO 6 — FDR doar pe primare; aici 1 primar).*

# 5. LIMITĂRI
- **Confund de perioadă (structural):** `exp` și `val_exp` sunt pe ferestre de timp disjuncte (primele 60% vs următoarele 20%) → un OOS pe o singură fereastră contiguă conflează robustețea cu condițiile acelei perioade. O singură fereastră de validare e un test de robustețe slab.
- **Missingness EXPLICAT:** cele 176 `val_exp` lipsă = strategii cu <5 trade-uri pe segmentul val (regula `len(mv)>=5`); toate în S1, consecvent cu frecvența mai joasă a S1 (n median 209, cea mai mică). Deci lipsa e un efect de trade-count-scăzut-în-val, nu un mister.
- Un singur corpus, un singur snapshot, o singură fereastră de validare.

# 6. INTERPRETĂRI INTERZISE
- ❌ „val_exp > exp dovedește că edge-urile sunt robuste/validate." (E confundat cu perioada; nu o confirmare de robustețe.)
- ❌ Orice afirmație cauzală despre DE CE OOS>IS (perioadă/regim/robustețe) — 🔒 P4.
- ❌ „val_exp e o coloană stricată / semantic mismatch." (Verificat: e un OOS temporal legitim.)

# 7. ÎNTREBĂRI ÎN COADĂ P4
- De ce e `val_exp` (OOS, 20% ulterior) sistematic > `exp` (60% anterior)? perioadă/regim vs robustețe reală? 🔒 P4.
- (REZOLVAT în §5, nu mai e P4: lipsa `val_exp` în S1 = <5 trade-uri în val.)

─────────────────────────────────────────────
# ALPHA INTELLIGENCE SUMMARY  (obligatoriu)

1. **Key finding.** `val_exp` (verificat: OOS temporal = mean R pe segmentul de validare 60–80%) este SISTEMATIC mai mare decât `exp` (in-sample, primele 60%) — gap median pereche +0,072R, la 77% din ipoteze, robust la 19/20 familii și fără S1. OOS > in-sample, invers față de shrinkage-ul tipic. Cauza rămâne OPEN.

2. **Operational consequence.** `exp` și `val_exp` sunt pe ferestre de timp DISJUNCTE → un OOS pe o singură fereastră contiguă conflează robustețea cu condițiile acelei perioade. Un gate de validare bazat pe o singură fereastră 60/20 e confundat cu regimul și poate induce în eroare (aici, în direcția „prea optimist").

3. **Recommended Alpha action.** Alpha ar trebui să: **RECONSIDERE** dependența de o singură fereastră de validare 60/20 — să prefere **walk-forward / ferestre multiple** ca să separe efectul de perioadă de robustețea reală; să **NU** citească „OOS>IS" ca dovadă de robustețe; să **noteze** că `val_exp` e nedefinit pentru strategiile cu <5 trade-uri în val (toate low-frequency S1) → orice gate pe `val_exp` are o gaură de acoperire acolo. *(Semantica e acum clară — recomandarea anterioară „investighează ce e val_exp" e închisă.)*

4. **Confidence.** Asocierea: robustă (C2 — CI exclude 0, 19/20 familii, supraviețuiește leave-S1-out). Confundul de perioadă e un fapt structural (nu incertitudine).

5. **Changes Alpha's future Discovery process?** **DA** — expune o limitare de METODĂ de validare (fereastră unică, period-confounded), nu o coloană stricată. Alpha ar câștiga din walk-forward / validare multi-fereastră înainte de a trata OOS ca robustețe.

─────────────────────────────────────────────
*Sfârșitul RI-META-0002 (WP2). Doar WP2. NU am executat WP3–WP5.*
─────────────────────────────────────────────
