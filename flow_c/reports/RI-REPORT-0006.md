─────────────────────────────────────────────
ESTIMATED ALPHA IMPACT:  🟡 MEDIUM
  (Umple axa pe care se sprijină obiectivul strategic al laboratorului — winrate ridicat + RR mic —
   axă care lipsea complet din harta de acoperire P1. Pur descriptiv, fără inferență.)
─────────────────────────────────────────────
FLOW C — RESEARCH REPORT (addendum descriptiv, post-P1)
ID:              RI-REPORT-0006
Data:            2026-07-21
Autor:           Research Intelligence (Alpha Intelligence Division)
Nivel epistemic: cunoaștere-observațională (descriptiv, marginal)
Încredere:       fidelitate descriptivă ridicată (corpus reprodus bit-exact). Fără inferență.
─────────────────────────────────────────────
CONTEXT DE GUVERNANȚĂ
  P1 a fost închis (commit 42cd565) cu Coverage Confidence = High. Acest addendum adaugă o dimensiune
  descriptivă NOUĂ (axa win-rate × dependență-de-o-tranzacție) care lipsea din matricea A.5.
  Conform Coverage Confidence Lifecycle §2.1 (dimensiune descriptivă nouă → downgrade automat),
  Coverage Confidence se retrogradează High → în-re-review. Decizie CEO 2026-07-25: downgrade ACCEPTAT.
  Motiv (CEO): o hartă „High" căreia îi lipsește exact axa obiectivului strategic e o falsă siguranță.
─────────────────────────────────────────────
BAZA DE DOVEZI
  • Sursă:  results/FAMILY_RESULTS.parquet (reprodus bit-exact). Calcul direct, seed n/a (numărători).
  • Definiții: win = rată de câștig (coloana `win`). „Dependență de o singură tranzacție": operaționalizată
    prin `wo1` (expectancy fără cea mai bună tranzacție); `wo1>0` = supraviețuiește scoaterii celei mai bune.
  • NON-fabricare: fiecare cifră derivă din numărători directe pe corp.
─────────────────────────────────────────────
PLAFON EPISTEMIC: DESCRIPTIV, marginal. NU corelează axele ca relație (aia ar fi P2). NU infer, NU
  concluzionez, NU recomand. Doar distribuția.
─────────────────────────────────────────────

# 1. ÎNTREBAREA DE ACOPERIRE

Cum se distribuie corpul pe axa win-rate și pe axa dependenței-de-o-tranzacție (`wo1`) — marginal, fără a le corela ca relație? Axa lipsea din matricea P1 (corpul fusese descris prin expectancy, nu prin win-rate).

# 2. DISTRIBUȚIA (marginal + numărători joint descriptive)

| Populație | median win | win≥0,5 | wo1>0 (supraviețuiește) | win≥0,5 ȘI wo1>0 |
|---|---|---|---|---|
| Corpus (1972) | 0,363 | 258 (13%) | 248 (13%) | 107 |
| Câștigători hist_prof (357) | 0,443 | 147 (41%) | 248 (69%) | 107 |
| Research-worthy (130) | 0,442 | 38 (29%) | 110 (85%) | 36 |

*(Numărătorile joint sunt descriptive — câte ipoteze satisfac ambele condiții simultan — NU o relație inferată între axe.)*

# 3. FUNNEL DESCRIPTIV (pe axa obiectivului strategic)

```
1972 ipoteze
  → research_worthy: 130
    → win ≥ 0,50: 38
      → ȘI wo1 > 0 (nu depind de o tranzacție): 36
        → ȘI n ≥ 50 (eșantion decent): 21
```

# 4. AVERTISMENT (obligatoriu — NU e o descoperire)

Cele 21 (și 36) de ipoteze de mai sus sunt o **OBSERVAȚIE DE ACOPERIRE filtrată POST-HOC**, pe criterii alese DUPĂ vizualizarea datelor. **NU au valoare probatorie.** Pot deveni ipoteză DOAR prin: pre-înregistrare completă a criteriilor înainte de a atinge datele + p-engine validat + model de cost. Nu concluzionez nimic despre ele; doar consemnez distribuția.

# 5. CE NU FACE ACEST ADDENDUM
- Nu corelează win-rate cu dependența-de-tranzacție ca relație (= P2).
- Nu explică (= P4). Nu validează (= Alpha).
- Nu retrage și nu modifică rapoartele P1 închise.

─────────────────────────────────────────────
# ALPHA INTELLIGENCE SUMMARY (obligatoriu)

1. **Key finding.** Pe axa obiectivului strategic (winrate ridicat + independență de o tranzacție), corpul are: 38/130 research-worthy cu win≥0,5; 36 dintre ele supraviețuiesc scoaterii celei mai bune tranzacții; 21 au și n≥50. Median win printre profitabili = 0,443 (sub 50%).

2. **Operational consequence.** Axa pe care se sprijină obiectivul strategic al laboratorului există acum în harta de acoperire; anterior corpul era descris exclusiv prin expectancy. Coverage Confidence retrogradat de la High (re-review) — recunoaștere onestă că harta „High" era incompletă pe axa centrală.

3. **Considerations for Future Investigation.** *(Flow C informează, nu direcționează.)* Sub-mulțimea de 21/36 nu poate fi tratată ca rezultat fără pre-înregistrare + p-engine validat + model de cost. Dacă/cum se pre-înregistrează = decizia Alpha.

4. **Confidence.** Descriptiv, fidelitate ridicată (corpus reprodus); zero inferență.

5. **Changes Alpha's future Discovery process?** Informativ — expune că statistica primară înghețată (expectancy) nu filtrează pe win-rate deloc, iar obiectivul strategic e definit pe win-rate. Dacă asta schimbă screening-ul = decizia Alpha.

─────────────────────────────────────────────
*Sfârșitul RI-REPORT-0006. Addendum descriptiv; Coverage Confidence retrogradat High → re-review (CEO-accepted).*
─────────────────────────────────────────────
