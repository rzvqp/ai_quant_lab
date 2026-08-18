# STATISTICIAN — `m_inference` FINAL: 26, ȘI INVARIANTUL CARE PROTEJEAZĂ CORECȚIA

**Document ID:** STAT-M-INFERENCE-FINAL-v1.0 · **Data:** 2026-08-18 · **Autor:** Statistician
**Status livrat:** `RANGE_STATISTICAL_SPEC_FINAL_READY`
**Natură:** ÎNREGISTRARE de decizie CEO. Supersedă **NUMAI numărătoarea** din v2.7.76.
**Neatinse, verificate:** secțiunile B–F · registrul Alpha · `n_generated_total = 357` · tombstones · verdictele existente · clauza `n_raportate == n_evaluate` · regula selecției retrospective · interdicția SEALED.

---

# PARTEA 1 — VALOAREA FINALĂ ȘI PRAGURILE

```
n_generated_total = 357        NESCHIMBAT
m_inference       = 20 → 26    F1-F6 = ȘASE ipoteze testabile
F7 RANGE_MID_NO_ENTRY          INTERDICȚIE / guard de siguranță — NU ipoteză, NU produce p-value
```

```
BH-FDR:  pentru p ordonate p_(1) <= … <= p_(m), se resping primele k cu  p_(k) <= k · α / m
         α = 0,05 ,  m = 26
  prag rang-1  = 0,05/26 = 0,001923      prag rang-2 = 0,003846
  prag rang-3  = 0,005769                prag rang-6 = 0,011538
  MDE = z_{1−α/m} × SE = 2,8905 × 0,03006 = 0,0869      (SE = 0,4714/√246 = 0,03006)
```

**Costul real al celor ȘASE sloturi: MDE 0,0844 → 0,0869 = +3,0% permanent. Slotul F7, care NU se mai plătește, valora 0,0004 pe MDE — 0,4%. Îl consemnez ca să fie clar că nu corecția a schimbat ceva material, ci categorisirea.**

---

# PARTEA 2 — DE CE ASTA NU ÎNCALCĂ MONOTONIA. Argumentul, scris ca să nu devină precedent.

**v2.7.76 a înregistrat 27; v2.7.77 înregistrează 26. O scădere. Iar regula mea de familie e MONOTONĂ din v2.7.48. Contradicția e aparentă, dar trebuie desfăcută explicit, altfel cineva va cita cazul ca dovadă că monotonia e negociabilă.**

```
INVARIANTUL, restatat exact:
   o IPOTEZĂ admisă în `m_inference` nu iese NICIODATĂ.
   Motivul, neschimbat: scoaterea ei ar SLĂBI pragul pentru celelalte.
```

> **F7 nu a fost niciodată o ipoteză. A fost o INTRARE MISCATEGORISITĂ. Testul e verificabil din propria ei specificație, nu din rezultate: `RANGE_MID_NO_ENTRY` generează ZERO tranzacții PRIN CONSTRUCȚIE, deci nu poate produce un p-value sub nicio realizare a datelor. Nu a fost niciodată ELIGIBILĂ pentru admitere. A corecta TIPUL unei intrări nu e a SCOATE o ipoteză.**

**Și, decisiv pentru caracterul non-oportunist al corecției: nicio evaluare nu a rulat sub m=27. Nu s-a calculat niciun p-value, nu s-a comparat niciun prag, `RANGE_STATE` nici măcar nu există. Corecția precedă orice implementare sau evaluare RANGE — exact cum a formulat-o CEO.**

## Predicatul de reclasificare, îngustat ca să nu devină portiță

```
O intrare poate ieși din `m_inference` prin RECLASIFICARE DOAR DACĂ, CUMULATIV:
  (1) se demonstrează DIN PROPRIA EI SPECIFICAȚIE că generează ZERO tranzacții prin
      construcție — deci nu poate produce p-value sub nicio realizare a datelor; ȘI
  (2) reclasificarea se face ÎNAINTE de orice evaluare a ei sau a familiei în care stă; ȘI
  (3) se înregistrează în registrul de invarianți (Partea 3), nu se șterge.
DUPĂ prima evaluare, NICIODATĂ. Un rezultat observat nu poate motiva o reclasificare.
```

> **Fără (2), „reclasificare" ar deveni numele elegant al scoaterii din familie a oricărui candidat incomod. Cu (2), corecția e verificabilă mecanic: `RANGE_STATE` nu există, deci nicio evaluare nu putea exista.**

---

# PARTEA 3 — REGISTRUL DE INVARIANȚI / GUARDS DE SIGURANȚĂ

**F7 nu dispare — își schimbă registrul. Unitate diferită, scop diferit, contor separat.**

```
REGISTRU                 SAFETY_GUARDS
unitate                  invariant / refuz executabil
scop                     a garanta că o acțiune interzisă NU se produce
NU intră în              `m_inference` · corecția BH · niciun prag inferențial
contor                   `n_guards` — separat, monoton, FĂRĂ efect asupra vreunui prag
prima intrare            F7 = RANGE_MID_NO_ENTRY

CE RĂMÂNE OBLIGATORIU pentru F7, neschimbat:
  · în CONTRACT — emis ca STARE explicită (`NO_ENTRY_BY_CONSTRUCTION`), nu ca absență;
    o absență nu se poate audita, o stare da
  · în testele VE — verificat ca REFUZ EXPLICIT: zero intrări în RANGE_MID, nu „nicio intrare
    observată"
  · în auditul Red Team — atacabil ca invariant
```

**Regula de promovare inversă, pre-declarată acum ca să nu fie negociată mai târziu: dacă vreodată F7 produce un test inferențial cu p-value propriu, primește ATUNCI o ipoteză pre-înregistrată NOUĂ, cu slot NOU. NICIODATĂ retroactiv, și niciodată prin reinterpretarea intrării de guard.**

---

# PARTEA 4 — CE SE SUPERSEDĂ, CHIRURGICAL

**Din v2.7.76 se supersedă NUMAI numărătoarea. Am verificat fiecare loc unde apare 27 (11 apariții) și le clasific:**

```
SUPERSEDAT   `lexical_separation.m_inference.value_with_range`   27 → 26
SUPERSEDAT   `rule_made_executable.a`  „cele 7 familii duc m_inference la 27" → ȘASE, la 26
SUPERSEDAT   `cost_of_pre_registration_priced.arithmetic`  „20→27, +3,4%" → „20→26, +3,0%"
PROMOVAT     `counting_discrepancy_raised_not_applied` — nu mai e discrepanță, e DECIZIA.
             Aritmetica ei (m=26 → 0,001923 / MDE 0,0869) devine cea în vigoare.
NESCHIMBAT   cartografierea istorică („m=27/55 (v2.7.74)" rămâne citit ca `m_inference` —
             e o referință la ce s-a scris ATUNCI, nu la valoarea curentă)
NESCHIMBAT   `n_generated_total = 357` · clauza `n_raportate == n_evaluate` · regula selecției
             retrospective · restatarea „OOS independent" ca proprietate a PERECHII ·
             precondiția `RANGE_STATE` inexistent și F3/F4 static imposibile
NESCHIMBAT   secțiunile B–F ale specificației (`aca7801`, v2.7.75)
```

---

# PARTEA 5 — DESCHIS, CLASIFICAT

```
BLOCKING     niciunul introdus de această corecție.
             Precondiția rămâne: `RANGE_STATE` nu există (`bd60c7a`); F3/F4 rutează pe un
             breakout STATIC IMPOSIBIL (`5e56396` + numărătoarea mea 0/355.696). Cele șase
             sloturi sunt REZERVATE, nu rulabile: `ARCHIVE_INSUFFICIENT` prin construcție.
MATERIAL     predicatul de reclasificare (Partea 2) e îngust prin proiectare. Orice viitoare
             cerere de reclasificare trebuie să treacă toate cele trei condiții, iar (2) —
             „înainte de orice evaluare" — e cea care o face neexploatabilă.
MATERIAL     `n_guards` e un contor NOU, dar NU un gate: nu atinge niciun prag. Prima intrare F7.
LIMITATION   cele șase sloturi sunt rezervate ÎNAINTE de rezultate și sunt PERMANENTE:
             +3,0% pe MDE, chiar dacă `RANGE_STATE` nu se construiește niciodată.
NON-MATERIAL corecția 27 → 26 nu schimbă niciun verdict: 0,062 < MDE la ambele (0,0872 / 0,0869).
```

**VE consumă ACEST manifest ca final. F7 rămâne implementat și testat ca REFUZ EXPLICIT, fără entry.**

---

**Manifest:** `config/split_manifest.json` v2.7.77, secțiunea `m_inference_final_v2_7_77`.
