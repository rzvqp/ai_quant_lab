# STATISTICIAN — VERDICT: CELE 69 DE IPOTEZE (BRACKET WORST/BEST/EXCLUDERE)

**Document ID:** STAT-BRACKET69-VERDICT-v1.0
**Data:** 2026-07-27 · **Autor:** Statistician
**Verificare de sursă:** `docs/BRACKET_69_v1.0.md` (commit `7fa06e3`) citit direct — tabelul §"Rezultat", nota mecanică §31 ("best-case atinge TOATE barele ambigue; excludere atinge doar cele lărgite-same-bar — de-aceea nu sunt operații pe același set"), sanity checks (worst==baseline, excludere==reproduction_d2, supraviețuitor ATR identic).

---

## VERDICT — cele 22

**Etichetă: `CONVENTION-ARTIFACT`. Nu contează ca profitabilitate reală, sub nicio formă. Excluse permanent din orice pool de certificare/FDR.**

Statusul lor se inversează între worst (False) și best (True) FĂRĂ nicio schimbare a setului de tranzacții — doar prin schimbarea presupunerii de tie-break pentru bare identice, deja ambigue. Asta e exact regula pe care am scris-o deja: dacă verdictul calitativ se schimbă între cele două extreme la fel de rezonabile, cifra nu descrie ipoteza — descrie convenția de rezolvare a ambiguității. Verdictul e imediat, nu cere date suplimentare.

## VERDICT — cele 47

**Etichetă: `EXCLUSION-DEPENDENT — MECANISM NECLAR`. Nu resping ca artefact pur, dar NU certific ca profitabilitate reală. O a treia categorie, distinctă, cu un diagnostic suplimentar necesar înainte de verdict final.**

### De ce nu e un verdict imediat, dar nici o certificare

Cele 47 pierd bani sub AMBELE convenții depline (worst ȘI best) — inclusiv sub best-case, unde barele ambigue sunt scorate FAVORABIL (țintă câștigă). Devin profitabile DOAR când tranzacțiile marcate INVALID EXECUTION sunt eliminate din eșantion, nu scorate favorabil. Aceasta e o distincție importantă, pe care mecanismul semnalat de Research Lab (§31) o face posibilă: `target_first` (best-case) rezolvă favorabil ambiguitatea de tip "cine atinge primul, stop sau țintă, în aceeași bară" — dar `mark_invalid` (excludere) acoperă și celelalte două sub-cauze din regula pre-înregistrată (`MIN_STOP_FLOOR_PREREG.md:29-31`): gap peste podeaua de stop la intrare, și risc zero/negativ după flooring. Niciuna din acestea două nu e o "ambiguitate de tie-break" pe care `target_first` s-o poată rezolva favorabil — sunt execuții degenerate prin construcție, plauzibil scorate ca pierderi mari indiferent de convenția de tie-break.

**Inferența mea, semnalată explicit ca inferență, nu ca fapt verificat:** dacă scorarea favorabilă a ambiguității de tie-break (best-case) tot nu salvează aceste 47 de la pierdere, e plauzibil ca excluderea lor să fie dominată de cele două sub-cauze structurale (gap/risc-negativ), nu de simpla ambiguitate cui-a-atins-primul. Dacă adevărat, profitabilitatea lor nu vine din eliminarea unor tranzacții cu adevărat nemăsurabile (coin-flip), ci din ștergerea propriilor eșecuri de execuție cele mai severe — un semnal mult mai îngrijorător decât o simplă ambiguitate intrabar.

### Diagnosticul pe care îl cer, minim și punctual, înainte de verdict final

Pentru fiecare din cele 47: (1) defalcarea tranzacțiilor excluse pe sub-cauză (ambiguitate same-bar rezolvabilă vs. gap-peste-podea vs. risc negativ după flooring); (2) fracția de tranzacții excluse din totalul brut generat de acea ipoteză, comparată cu mediana corpului (`denominator_always_reported` — infrastructura există deja în registru, se aplică aici). **Dacă excluderea e dominată de gap/risc-negativ ȘI/SAU fracția exclusă e un outlier față de corp → verdict REJECTED, `CONVENTION-ARTIFACT` extins (aceeași etichetă ca cele 22, motiv diferit).** Dacă excluderea e dominată de ambiguitate same-bar genuină, la o fracție non-outlier → eligibile pentru scrutin evidențial normal (NU acceptare automată — doar nu mai sunt descalificate de acest defect specific).

## Consecință practică — promovarea `reproduction_d2` la canonic

**Autorizez promovarea METODOLOGIEI de măsurare `reproduction_d2` la canonic acum** — excluderea tranzacțiilor INVALID EXECUTION e convenția de măsurare corectă (deja stabilit în `STATISTICIAN_R_STATISTIC_STRUCTURAL_STOP_VERDICT_v1.0.md`, confirmat mecanic de `D2_CLOSURE_EXECUTION_v1.0.md` §WP-4b): elimină o părtinire pesimistă deterministă deja existentă, nu fabrică un rezultat. Aceasta e o decizie despre INSTRUMENTUL de măsurare, separată de certificarea oricărei ipoteze specifice — exact distincția aplicată consecvent toată sesiunea (proveniența parametrilor ≠ adevărul ipotezei; convenția barelor ambigue ≠ adevărul ipotezei).

**Condiție obligatorie pentru promovare:** documentul de tranziție (deja propus de Research Lab) trebuie să care explicit cele două etichete de mai sus pentru cele 69 — `CONVENTION-ARTIFACT` (22, permanent non-evidențial) și `EXCLUSION-DEPENDENT — MECANISM NECLAR` (47, în așteptarea diagnosticului). **Niciuna din cele 69 nu se numără în `hist_prof`/`research_worthy` pentru scopuri de certificare sau FDR global până la rezolvare.** Cele 357 originale rămân neafectate, cu statutul lor complet.

---

**Nu am modificat parquet-ul, nu am executat nimic. Statistician se oprește aici.**
