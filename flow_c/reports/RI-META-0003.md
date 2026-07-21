─────────────────────────────────────────────
ESTIMATED ALPHA IMPACT:  🟡 MEDIUM
  (Întrebarea „concentrare↔fragilitate" e circulară — dar clarificarea + versiunea non-circulară
   „prezice flag-ul de fragilitate degradarea OOS?" au valoare Alpha reală, deși inferența e slabă.)
─────────────────────────────────────────────
FLOW C — META ANALYSIS (P2 / WP3, pivotat)
ID:              RI-META-0003
Data:            2026-07-21
Autor:           Research Intelligence (Alpha Intelligence Division)
Nivel epistemic: cunoaștere-observațională relațională (P2)
Încredere:       C1 (direcțional descriptiv; CI cluster include 0 = inconcludent la inferență).
─────────────────────────────────────────────
BAZA DE DOVEZI
  • Sursă:  results/FAMILY_RESULTS.parquet (reprodus bit-exact).
  • Verificare definiție (lecția val_exp, înainte de a construi teoria): code/run_full_campaign.py:36
      fragile := (n>0 AND exp>0 AND (t1>=0.5 OR wo1<=0))
  • Metodă: complete-case pe val_exp; median + CI bootstrap cluster-FAMILIE (10.000, seed 20260721);
            leave-S1-out (mandat WP1). Simplu (principiul simplității).
  • NON-fabricare: calcul direct pe corpul existent.
─────────────────────────────────────────────
PLAFON EPISTEMIC (P2): asociativ, NU cauzal, NU validat. Mecanismul = 🔒 P4.
─────────────────────────────────────────────

# 1. CONSTATARE STRUCTURALĂ: WP3-ul original este CIRCULAR

`fragile` este DEFINIT prin concentrare/robustețe: `t1≥0.5` SAU `wo1≤0`. Prin urmare întrebarea planificată „este concentrarea ASOCIATĂ cu fragilitatea?" este **tautologică** — asocierea există prin construcție, nu ca descoperire empirică. **Nu o rulez ca finding.** (Aceeași disciplină „verifică definiția întâi" ca la val_exp.)

# 2. PIVOT NON-CIRCULAR (în cadrul temei fragilității)

Întrebarea cu valoare Alpha reală: **prezice flag-ul de fragilitate (in-sample) degradarea OOS (`val_exp`)?**
- `fragile` e calculat pe in-sample (t1, wo1); `val_exp` e OOS (segment de validare, WP2) → **non-circular**.
- **Populație:** câștigători (hist_prof, unde `fragile` e definit), complete-case pe val_exp. Cluster=familie.
- **Estimand:** diferența de median val_exp (fragile − non-fragile) + rata OOS-pozitivă (share val_exp>0).

# 3. REZULTATE

Câștigători: 357 (133 fragile, 224 non-fragile). Cu val_exp: 247 (68 fragile, 179 non-fragile; 110 lipsă = low-trade S1).

| Grup | median val_exp | share val_exp>0 (OOS-pozitiv) | n |
|---|---|---|---|
| **fragile** (in-sample) | 0,053 | **63,2%** | 68 |
| **non-fragile** | 0,108 | **85,5%** | 179 |
| diferență (fragile−non) | **−0,054** | −22 pp | — |

- CI cluster-familie pentru diferența de median: **[−0,281; +0,004]** — **include 0** (marginal).
- **Leave-S1-out:** fragile median 0,019 vs non-fragile 0,131 (diff −0,112); OOS-pozitiv **50,0% vs 84,7%** → tiparul se **întărește** fără S1, nu dispare.

# 4. INTERPRETARE ȘI STĂRI DE EVIDENȚĂ

- **Direcțional:** câștigătorii marcați fragil in-sample au val_exp OOS mai mic și o rată OOS-pozitivă mult mai joasă (63% vs 86%; 50% vs 85% fără S1). Flag-ul de fragilitate **pare să urmărească degradarea OOS**.
- **Dar:** CI cluster-familie al diferenței de median **include 0** → la inferență, **NULL/INCONCLUSIVE**; gap-ul de rată OOS-pozitivă = **DESCRIPTIVE ASSOCIATION** direcțională, întărită de leave-S1-out.
- **DATA-LIMITED:** n mic (68 vs 179; 24 vs 72 fără S1), și `val_exp` e period-confounded (o singură fereastră, WP2). „De ce" = 🔒 P4.

# 5. REGISTRU DE TESTE
1. diff median val_exp (fragile−non) = −0,054, CI cluster [−0,281;+0,004] → INCONCLUSIVE (include 0).
2. share OOS-pozitiv: 63,2% vs 85,5% (descriptiv, direcțional).
3. leave-S1-out: diff −0,112; OOS-pozitiv 50% vs 84,7% (întărește direcția).
*Un singur estimand primar → FDR neaplicabil (decizie CEO 6).*

# 6. LIMITĂRI
- Confund de perioadă moștenit din WP2 (val_exp = o singură fereastră OOS).
- n mic la nivel de grup și de cluster (≤20 familii) → inferență slabă; CI larg.
- Missingness: 110 câștigători fără val_exp (low-trade S1).

# 7. INTERPRETĂRI INTERZISE
- ❌ „Concentrarea cauzează fragilitatea." (Circular — fragile e definit prin concentrare.)
- ❌ „Flag-ul de fragilitate prezice degradarea OOS" ca fapt stabilit. (Direcțional, dar CI include 0.)
- ❌ Orice mecanism cauzal (🔒 P4).

# 8. ÎNTREBĂRI ÎN COADĂ P4
- Flag-ul de fragilitate prezice degradarea pe MULTIPLE ferestre OOS (walk-forward), nu doar una? 🔒 P4/Alpha.

─────────────────────────────────────────────
# ALPHA INTELLIGENCE SUMMARY  (obligatoriu)

1. **Key finding.** (a) Flag-ul `fragile` este DEFINIȚIONAL (t1≥0.5 sau wo1≤0) — „concentrarea prezice fragilitatea" e circular, nu o descoperire. (b) Non-circular: câștigătorii fragili in-sample au o rată OOS-pozitivă mult mai mică (63% vs 86%; 50% vs 85% fără S1), dar diferența de median are CI care include 0.

2. **Operational consequence.** Dovada actuală este INSUFICIENTĂ pentru utilizare operațională: direcție interesantă, dar încredere scăzută, CI include 0, DATA-LIMITED. Flag-ul de fragilitate rămâne, cel mult, un **candidat de indicator de risc**.

3. **Recommended Alpha action.** Alpha ar trebui să: **NU** trateze „concentrare→fragilitate" ca relație empirică (e definiție); să considere flag-ul de fragilitate drept **„candidat de indicator de risc care necesită validare suplimentară"** — **NU** se recomandă deployment operațional încă; validare pe **walk-forward / ferestre multiple** înainte de orice utilizare (leagă de recomandarea WP2).

4. **Confidence.** C1 — direcțional descriptiv; inconcludent la inferența cluster (CI include 0); DATA-LIMITED.

5. **Changes Alpha's future Discovery process?** **Nu încă.** Semnalează un candidat de indicator de risc de urmărit și validat multi-fereastră; nu justifică nicio schimbare operațională în acest stadiu.

─────────────────────────────────────────────
*Sfârșitul RI-META-0003 (WP3, pivotat non-circular). Doar WP3. NU am executat WP4–WP5.*
─────────────────────────────────────────────
