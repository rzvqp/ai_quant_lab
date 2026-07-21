─────────────────────────────────────────────
ESTIMATED ALPHA IMPACT:  🟡 MEDIUM
  (Asimetrie direcțională robustă STABILITĂ; explicația OPEN — driftul de eșantion e ipoteza
   competitoare principală de investigat. Valoare Alpha = informație despre evaluarea direcțională.)
─────────────────────────────────────────────
FLOW C — META ANALYSIS (P2 / WP4, scope redus)
ID:              RI-META-0004
Data:            2026-07-21
Autor:           Research Intelligence (Alpha Intelligence Division)
Nivel epistemic: cunoaștere-observațională relațională (P2)
Încredere:       C2 pentru ASOCIERE (robustă: CI exclude 0, supraviețuiește leave-S1-out, apare și OOS).
─────────────────────────────────────────────
BAZA DE DOVEZI
  • Sursă:  results/FAMILY_RESULTS.parquet (reprodus bit-exact).
  • Metodă: hit-rate hist_prof pe side ∈{long,short} (`both` EXCLUS din primar — scope redus CEO);
            rate diff + CI bootstrap cluster-FAMILIE (10.000, seed 20260721); leave-S1-out (mandat WP1).
  • NON-fabricare: calcul direct pe corpul existent.
─────────────────────────────────────────────
PLAFON EPISTEMIC (P2): asociativ, NU cauzal, NU validat. Mecanismul = 🔒 P4.
─────────────────────────────────────────────

# 1. ÎNTREBAREA (WP4, scope redus)

Diferă rata de câștig (hist_prof) între long și short? (`both` = doar descriptiv, exclus din primar.)
**Populație:** long+short (n=1868; `both`=104 exclus). Unitate=ipoteză, cluster=familie.
**Estimand:** diferența de rată condiționată hit_prof(long) − hit_prof(short).

# 2. REZULTATE

| Side | hit-rate | winners/n |
|---|---|---|
| **long** | **0,290** | 271/934 |
| **short** | **0,092** | 86/934 |
| diferență (long−short) | **+0,198** | CI cluster-familie **[+0,120; +0,281]** (exclude 0) |

- **Leave-S1-out:** long 0,235 vs short 0,034 (diff +0,201) — **se menține puternic** fără S1.
- **Verificare OOS (median val_exp):** long **+0,017** vs short **−0,111** — avantajul long apare **și pe fereastra OOS**.
- **`both` (descriptiv, exclus):** 104 ipoteze, **0 câștigători**, toate în 4 familii zero-profit (S4,S7,S11,S15) → `both` e confundat cu familia; nu comparabil ca side liber.

# 3. INTERPRETARE ȘI STARE DE EVIDENȚĂ

- **CE E STABILIT:** o asimetrie direcțională robustă (long câștigă net mai des decât short, +20pp), care supraviețuiește leave-S1-out și apare și OOS. Stare: **STATISTICALLY SUPPORTED ASSOCIATION**.
- **CE NU E STABILIT:** cauza ei. **Driftul direcțional al eșantionului** (XAUUSD a urcat în fereastra de ~4 ani) este **IPOTEZA COMPETITOARE PRINCIPALĂ, care necesită investigație dedicată** (de-trending, testare pe regimuri cu drift diferit) — dar NU e stabilit ca mecanism dominant. Rămân pe masă și alte explicații (edge direcțional structural, asimetrie de construcție a strategiilor). Adjudecarea = 🔒 P4.

# 4. REGISTRU DE TESTE
1. rate diff (long−short) = +0,198, CI cluster [+0,120;+0,281] → SUPPORTED.
2. leave-S1-out diff = +0,201 → confirmă.
3. OOS median val_exp: long +0,017 vs short −0,111 (descriptiv, direcțional).
4. `both`: 0/104 câștigători, confundat cu familia (descriptiv).
*Un singur estimand primar → FDR neaplicabil.*

# 5. LIMITĂRI
- **Explicație OPEN:** driftul direcțional al eșantionului e IPOTEZA COMPETITOARE PRINCIPALĂ de investigat, NU un fapt stabilit; asimetria *ar putea* fi conflată cu deriva netă a instrumentului, dar asta cere investigație dedicată. Un singur eșantion, o singură direcție netă.
- `both` neinterpretabil ca side (confundat cu 4 familii zero-profit).
- OOS pe o singură fereastră (period-confounded, moștenit WP2).

# 6. INTERPRETĂRI INTERZISE
- ❌ „Strategiile long sunt inerent mai robuste / long e un edge real." (Cauza e OPEN; nu se poate afirma edge.)
- ❌ „Driftul explică fenomenul." (Drift = ipoteză competitoare principală, NEstabilită ca dominantă.)
- ❌ „Construcția both e inerent neprofitabilă." (`both` apare doar în 4 familii zero-profit — confundat cu familia.)
- ❌ Orice mecanism cauzal (🔒 P4).

# 7. ÎNTREBĂRI ÎN COADĂ P4
- Long-skew-ul supraviețuiește ajustării pentru driftul instrumentului / pe perioade cu drift diferit? 🔒 P4/Alpha.

─────────────────────────────────────────────
# ALPHA INTELLIGENCE SUMMARY  (obligatoriu)

1. **Key finding.** Asimetrie direcțională robustă STABILITĂ: hit-rate long 29% vs short 9% (diff +0,20, CI [+0,12;+0,28]); se menține fără S1 (23,5% vs 3,4%) și apare și OOS (long val_exp +0,02 vs short −0,11). Cauza rămâne OPEN.

2. **Operational consequence.** Un skew direcțional *ar putea* fi conflat cu deriva netă a instrumentului — driftul de eșantion e ipoteza competitoare principală, dar NEstabilită. Până la investigație dedicată, un skew direcțional NU poate fi citit ca edge robust.

3. **Considerations for Future Investigation.** *(Flow C informează, nu direcționează Discovery.)* Merită investigat: evaluarea direcțională față de un baseline de drift (buy-and-hold / drift-neutral); testarea pe perioade cu drift diferit; de-trending pentru a separa driftul de un eventual edge structural. `both` rămâne neinterpretabil ca side (confundat cu familia). Dacă/cum se folosesc = decizia Alpha.

4. **Confidence.** Asocierea: robustă (C2 — CI exclude 0, leave-S1-out, apare OOS). Explicația: OPEN (driftul = ipoteză competitoare principală, NEstabilită ca dominantă).

5. **Changes Alpha's future Discovery process?** Informativ — semnalează că evaluarea direcțională *poate fi* drift-confounded în acest dataset. Dacă asta modifică Discovery-ul = decizia Alpha; Flow C doar informează.

─────────────────────────────────────────────
*Sfârșitul RI-META-0004 (WP4, scope redus). Doar WP4. NU am executat WP5 (rămâne condiționat).*
─────────────────────────────────────────────
