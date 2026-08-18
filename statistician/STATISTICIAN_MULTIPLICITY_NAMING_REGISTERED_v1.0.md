# STATISTICIAN — ÎNREGISTRAREA SEPARĂRII LEXICALE ȘI A REGULII DE MULTIPLICITATE

**Document ID:** STAT-MULTIPLICITY-NAMING-REGISTERED-v1.0 · **Data:** 2026-08-18 · **Autor:** Statistician
**Natură:** ÎNREGISTRARE de decizie CEO. Nu recalibrez, nu reinterpretez, nu extind.
**Neatinse, verificat:** registrul Alpha · `n_generated_total = 357` · tombstones · verdictele existente.

---

# PARTEA 1 — SEPARAREA, ÎNREGISTRATĂ

```
n_generated_total   contor MONOTON al configurațiilor GENERATE/evaluate de Alpha.
                    valoare 357, NEATINSĂ.  (fost `loop_state.m_total`)
                    unitate: configurație de candidat generată și expediată
                    p-value-uri produse: ZERO
m_inference         numărul ipotezelor care produc EFECTIV p-value și intră în corecția
                    inferențială.  valoare curentă 20 → 27 cu cele 7 familii RANGE
                    pre-înregistrate.  (fost „family m")
                    unitate: (politică, POPULAȚIE, estimand)
```

**Cartografierea către versiunile deja publicate, ca istoria să rămână lizibilă fără reeditare:**

```
„m = 16" (v2.7.43) · „m = 19" (v2.7.62) · „m = 20" (v2.7.71) · „m = 27/55" (v2.7.74)
    ⇒ toate se citesc ca `m_inference`
„m_total = 357" (loop_state, CANONICAL_SCREENING_REPORT)
    ⇒ se citește ca `n_generated_total`
Documentele anterioare NU se rescriu. Cartografierea de mai sus e canonică.
```

**Ambele contoare rămân MONOTONE, dar peste universuri diferite: `n_generated_total` peste ce s-a generat, `m_inference` peste ce s-a admis la inferență. Cele 44 de ipoteze `REGIME_UNREACHABLE` sunt în primul și NU în al doilea — separarea le rezolvă curat, fără caz special.**

---

# PARTEA 2 — REGULA, FĂCUTĂ EXECUTABILĂ

```
(a) cele 7 familii RANGE pre-înregistrate  ⇒  m_inference = 27
(b) grila de sensibilitate NU primește sloturi separate — DACĂ e raportată INTEGRAL ca
    sensibilitate
(c) dacă ORICE variantă e selectată retrospectiv după rezultat/PnL ⇒ TOATE variantele
    evaluate intră în m_inference, retroactiv
(d) rezultatele de screening rămân PROVISIONAL; promovarea confirmatorie cere OOS/forward
    INDEPENDENT
```

**Condiția din (b) e cea portantă, și o fac verificabilă: „INTEGRAL" înseamnă că se raportează TOATE variantele evaluate, nu o submulțime. Raportarea unei submulțimi ESTE selecție, deci declanșează (c). Mecanic: numărul de variante raportate trebuie să egaleze numărul de variante evaluate, iar ambele intră în `range_spec_id`.**

**Pentru (d), o precizare care decurge din ce am stabilit deja la v2.7.71: „OOS independent" nu e o proprietate a unei ferestre, ci a PERECHII (fereastră, candidat). Fereastra recentă e nevăzută de linia de screening wp5b (măsurat: zero bare) dar VĂZUTĂ de Flow-B. Iar holdout-ul e SIGILAT. Deci singura sursă de OOS cu adevărat independent, pentru candidații deja ecranați, e ACUMULAREA ÎNAINTE — Shadow. Nu o cer aici; o consemnez, fiindcă altfel „OOS independent" ar putea fi citit ca disponibil azi.**

---

# PARTEA 3 — O DISCREPANȚĂ DE NUMĂRARE, SEMNALATĂ FĂRĂ A FI APLICATĂ

**Enumerarea din propria mea specificație (`STATISTICIAN_RANGE_CAUSAL_SPEC_v1.0.md`, liniile 189-195), verbatim:**

```
F1 BUY_LOW_ZONE_REJECTION · F2 SELL_HIGH_ZONE_REJECTION · F3 BREAKOUT_ACCEPTED ·
F4 BREAKOUT_RETEST · F5 FAILED_BREAKOUT · F6 LIQUIDITY_SWEEP_REVERSAL
F7 „interzis prin construcție: NICIO intrare în RANGE_MID — emis ca stare, auditat ca refuz"
```

> **F7 nu e o strategie — e o INTERDICȚIE. Nu generează tranzacții, deci nu produce niciodată un p-value. Sub definiția din decizie („ipotezele care produc EFECTIV p-value"), F7 nu ar aparține lui `m_inference`, iar numărul testabil e ȘASE, nu șapte.**

```
m_inference = 26  →  prag rang-1 0,001923 · MDE 0,0869
m_inference = 27  →  prag rang-1 0,001852 · MDE 0,0872      ← decizia CEO
diferența: 0,41% pe MDE.
```

**NU aplic 26. Motivul e de principiu, nu de mărime: 26 e mai PERMISIV decât 27, iar eu nu slăbesc unilateral un prag. Înregistrez 27 ca decis, semnalez discrepanța, și o las la CEO. Dacă rămâne 27, F7 e un slot consumat de o interdicție care nu poate fi testată — conservator, deci inofensiv pentru rata de descoperiri false, dar consemnat ca atare.**

---

# PARTEA 4 — COSTUL PRE-ÎNREGISTRĂRII, PREȚUIT

**Admiterea celor 7 acum e o UȘĂ CU UN SINGUR SENS: `m_inference` e monoton, deci pragul coborât nu se mai ridică pentru nimeni, niciodată — inclusiv dacă `RANGE_STATE` nu se construiește vreodată.**

```
m_inference 20 → 27 :  MDE 0,0844 → 0,0872  =  +3,4%
```

> **Costul e REAL și MIC. Îl prețuiesc explicit ca decizia să fie informată, nu ca s-o contest: 3,4% pe efectul minim detectabil, permanent, în schimbul închiderii definitive a portiței de selecție. La efectul observat al lui CAND-0037 (0,062), care e sub MDE la ambele valori, schimbarea nu mișcă niciun verdict.**

**Și reamintesc precondiția, neschimbată de această decizie: `RANGE_STATE` nu există (retras prin `bd60c7a`), iar F3/F4 rutează pe un breakout STATIC IMPOSIBIL (`5e56396`, confirmat empiric: 0 bare din 355.696). Pre-înregistrarea le REZERVĂ sloturile; nu le face rulabile. Până când producătorul VE există, ele rămân `ARCHIVE_INSUFFICIENT` prin construcție — nu eșec.**

---

# PARTEA 5 — CE RĂMÂNE DESCHIS

```
BLOCKING     niciunul introdus de această decizie.
MATERIAL     F7 e o interdicție, nu o ipoteză testabilă ⇒ numărul testabil e 6. Înregistrez 27
             (conservator, cum s-a decis) și cer arbitrajul. NU aplic 26 unilateral.
MATERIAL     „raportată INTEGRAL" devine verificabil: n_variante_raportate == n_variante_evaluate,
             ambele în `range_spec_id`. O submulțime raportată ESTE selecție și declanșează (c).
MATERIAL     „OOS/forward independent" e per PERECHE (fereastră, candidat). Holdout SIGILAT,
             fereastra recentă deja văzută de Flow-B ⇒ pentru candidații ecranați, singura sursă
             independentă e acumularea ÎNAINTE, prin Shadow.
LIMITATION   `m_inference = 27` e o ușă cu un singur sens: +3,4% pe MDE, permanent, chiar dacă
             `RANGE_STATE` nu se construiește niciodată.
NON-MATERIAL trecerea 20 → 27 nu schimbă niciun verdict actual: 0,062 < MDE la ambele.
```

**Neatinse și verificate: registrul Alpha · `n_generated_total = 357` · tombstones · verdictele existente. Specificația `aca7801` / manifest v2.7.75 `5063448` rămâne BAZĂ PENTRU IMPLEMENTAREA VE, NU ratificare a detectorului.**

---

**Manifest:** `config/split_manifest.json` v2.7.76, secțiunea `multiplicity_naming_registered_v2_7_76`.
