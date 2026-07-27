# STATISTICIAN — VERDICT: R = pnl/risc PENTRU IPOTEZE CU STOP STRUCTURAL

**Document ID:** STAT-R-STRUCTURAL-VERDICT-v1.0
**Data:** 2026-07-27 · **Autor:** Statistician
**Întrebare formală (Research Lab, prin CEO):** e R = pnl/risc statistica potrivită pentru ipoteze cu stop structural, dat fiind că varianța explodează la risc→zero, iar rezoluția de date mai fină nu rezolvă asta?
**Context verificat independent:** WP-1..WP-4 executate (`code/d2_verify.py`, `results/reproduction_d2/d2_verify_summary.json` — hist_prof 357→426, `atr412_maxdiff=0.0`, confirmat); `docs/MIN_STOP_FLOOR_PREREG.md` citit direct.

---

## VERDICT PRINCIPAL

**Nu — R, așa cum e definit acum (nefloorat pe partea structurală), nu e statistica potrivită pentru ipotezele cu stop structural. E un defect de definiție a variabilei de rezultat, nu o problemă de suficiență a datelor. Confirm complet framing-ul Research Lab.**

## Raționament

Pentru stop **ATR-scaled** (`risc = k × ATR`), numitorul are o podea garantată prin construcție pre-înregistrată: `MIN_STOP_FLOOR_PREREG.md` fixează `min_executable_risk = max(k_spread·spread, k_tick·tick, k_atr·ATR)`, deci riscul nu poate coborî sub o valoare pozitivă fixă, indiferent de ce se întâmplă pe piață. Exact acest regim e cel pe care `matched_null@v1` a fost validat. Varianța lui R e mărginită acolo prin construcție.

Pentru stop **structural** (distanța de la intrare la un nivel de structură — swing, margine de order block, lichiditate), **nu există o podea analogă declarată**. Mai mult, distanța mică nu e un caz marginal rar — e frecvent chiar centrul definiției unor astfel de setup-uri ("intră când prețul e la/lângă marginea zonei"). Asta înseamnă că numitorul poate avea masă de probabilitate nenulă arbitrar de aproape de zero, prin însăși natura a ceea ce ipoteza selectează. R = pnl/risc devine un raport a două variabile dependente cu numitor ce se poate apropia de zero — condiția clasică pentru o distribuție cu cozi grele, varianță posibil infinită, medie posibil nedefinită (analog cazului Cauchy).

**Rezoluția mai fină (M5 vs M15) nu schimbă nimic aici.** M5 localizează mai precis NIVELUL structural — reduce eroarea de măsurare asupra numitorului adevărat. Dar nu schimbă faptul că numitorul adevărat însuși poate fi mic. O măsurătoare mai precisă a unei cantități care poate fi oricât de mică nu vindecă un raport care explodează — doar elimină zgomotul de rezoluție grosieră dintr-un numitor care rămâne, structural, permis să fie minuscul. Exact distincția pe care ai cerut-o: nu e o problemă de suficiență a datelor, e o proprietate a statisticii R însăși în acest regim.

## Consecință pentru cele ~1.560 ipoteze excluse

Nu sunt doar "netestate" — sunt **măsurate cu un instrument a cărui validitate în acest domeniu nu e stabilită, cu motiv activ de îndoială**. Recomand o etichetă distinctă (ex. `STRUCTURAL-R-UNVALIDATED`, nu pur și simplu "backlog"/"untested"), ca niciun rezultat R viitor pe ele să nu fie tratat implicit ca la fel de valid ca rezultatele ATR-scaled deja validate.

## Ce NU rezolv acum

Problema se mută, cum ai spus, la definirea variabilei de rezultat — domeniul meu. Nu improvizez o soluție aici. Căi candidate, de proiectat formal înainte de a atinge date (nu acum, ca livrabil separat):

1. **Podea structurală explicită**, analog `MIN_STOP_FLOOR_PREREG.md`, extinsă la cazul structural (prag sub care tranzacția e `INVALID EXECUTION`).
2. **Decuplarea numărătorii/numitorului** — pnl normalizat la o unitate fixă de volatilitate (ex. ATR la momentul intrării), nu la riscul structural propriu al tranzacției — elimină raportul care explodează, cu prețul schimbării a ceea ce statistica reprezintă.
3. **Statistică robustă/pe range** (ex. Wilcoxon pe pnl normalizat) care nu cere varianță finită a lui R.

**Notă obligatorie, aplicabilă oricărei căi alese:** orice constantă împrumutată din cazul ATR (ex. `k_atr=0.10`) pentru podeaua structurală trebuie să treacă testul de proveniență §2 din `STATISTICIAN_11YR_DATASET_PREREGISTRATION_RULES_v1.0.md` (v1.1) — acele constante au fost ele însele calibrate pe diagnosticul ATR, nu pe cazul structural, deci reutilizarea lor tăcută ar repeta exact problema pe care regula aceea o interzice.

---

# ANEXĂ — TRATAMENTUL CELOR 69 DE IPOTEZE NOI (357→426, excludere INVALID EXECUTION)

**Verificat independent:** `code/mstrat.py` (comentariu WP-1, regulă identică la `simulate` și funcția de paritate), `docs/MIN_STOP_FLOOR_PREREG.md:29-31` (o tranzacție e `INVALID EXECUTION` doar dacă nu poate fi executată deloc — gap peste podea, risc ≤0 după flooring, sau fill ambiguu intra-bară pe care modelul worst-case nu-l poate rezolva), `results/reproduction_d2/d2_verify_summary.json` (`hist_prof_base=357` sub convenția veche stop-câștigă-la-ambiguitate, `hist_prof_new=426` după excludere, delta = 69).

## Verdict pe sub-întrebare

**Excluderea e tratamentul primar corect, dar nu suficient singură. Nu propun înlocuirea ei cu raportare separată — propun raportare separată CA VERIFICARE OBLIGATORIE suplimentară, nu ca alternativă.**

Excluderea e superioară convenției vechi (stop câștigă mereu la ambiguitate) pentru că nu inventează un rezultat: bara e genuin nerezolvabilă din OHLC, iar convenția veche impunea o presupunere sistematic pesimistă, nu una neutră. Regula a fost pre-înregistrată ÎNAINTE de acest rezultat (`MIN_STOP_FLOOR_PREREG.md:38`: "Do NOT tune k after seeing..."), deci nu e o alegere post-hoc care favorizează rezultatul.

Dar excluderea totală e corectă DOAR dacă barele ambigue sunt reprezentative pentru populația testată — dacă barele de mare volatilitate (mai predispuse să atingă și stopul și ținta în aceeași bară) diferă sistematic de restul, excluderea schimbă compoziția populației testate într-un mod neverificat, nu doar elimină o părtinire.

## Ce cer, exact ca disciplina canary-check din regula de proveniență

Pentru cele 69 (și orice ipoteză viitoare a cărei stare `hist_prof` depinde de acest tratament): raportare obligatorie sub **ambele extreme deterministe** — stop-câștigă-întotdeauna (worst-case) și țintă-câștigă-întotdeauna (best-case) — alături de numărul primar (excludere). Infrastructura pentru fracția exclusă per ipoteză deja există în registru (`denominator_always_reported`) — se aplică aici, nu se inventează.

**Verificare factuală care susține exact această distincție:** cele 357 originale au fost `hist_prof` chiar sub convenția veche, integral pesimistă (worst-case) — deci sunt deja robuste la cel mai defavorabil tratament posibil al ambiguității, nu au nevoie de eticheta de mai jos. Cele 69 noi, prin definiție, devin `hist_prof` DOAR sub excludere — nu supraviețuiesc worst-case. Acestea primesc eticheta **"stare hist_prof condiționată de tratamentul barelor ambigue"** și nu intră în niciun pool de certificare/FDR până nu trec verificarea de stabilitate calitativă sub cele trei tratamente (excludere / worst-case / best-case). Dacă verdictul calitativ (supraviețuire BH, semn, ordin de mărime) rămâne stabil pe acest interval, tratamentul nu era decisiv. Dacă se schimbă, baza evidențială a acelei ipoteze e un artefact al convenției de rezolvare a ambiguității, nu un efect real — se semnalează, nu se certifică.

**Nu am modificat parquet-ul, nu am executat nimic. Statistician se oprește aici.**
