# STATISTICIAN — DECIZIE FORMALĂ: ABANDONAREA `block_bootstrap@v1` + RE-SPECIFICARE NOUĂ

**Document ID:** STAT-BLOCKBOOT-ABANDON-v1.0
**Data:** 2026-07-27 · **Autor:** Statistician
**Verificare de sursă:** `validation_engine/BLOCK_BOOTSTRAP_S_CALIBRATION_RECORD.md` citit direct — verdictul VE, tabelele S3/S4/S8, nota de fidelitate a reproducerii controalelor față de `docs/MONTE_CARLO_AUDIT.md` (0.57/5e-5 vs. 0.42/4e-4 — diferență de tragere/B, reconciliată explicit de VE, nu semnal de instabilitate a implementării).

---

## DECIZIE: ABANDON DEFINITIV al `block_bootstrap@v1` AȘA CUM E SPECIFICAT. Re-specificare autorizată sub un nume/domeniu nou, ca metodă separată, pornind UNVALIDATED.

## Raționament

`block_bootstrap@v1` (moving-block simplu, centrare la zero) trece S1 (contract) și S4 (putere) — dar EȘUEAZĂ exact testul care justifică existența metodei: S8, calibrarea sub null autocorelat. Nu marginal — anti-conservator direcțional, în regimul REALIST (n≈250, φ=0.4-0.6: FPR 7,7%-9,3% în loc de 5%), devenind nominal doar la n≥1.000, un regim în care metoda nu e folosită (S6: n=244; S1-rep: ~n=200).

**De ce nu e o reparație posibilă pe aceeași construcție:** VE confirmă explicit — nu e defect de implementare (reproduce fidel cele 2 controale sintetice originale din `MONTE_CARLO_AUDIT.md`), ci o proprietate reală de eșantion finit a moving-block bootstrap simplu: subestimează varianța pe termen lung când numărul de blocuri (n/L) e mic și autocorelația e prezentă. Aceasta e o proprietate STRUCTURALĂ a construcției alese (block bootstrap simplu, ne-studentizat), nu un bug de cod, nu un seed prost, nu un parametru de ajustat. Nu există o cale onestă să "reparăm" aceeași construcție ca să treacă S8 la n≈250 — literatura de specialitate rezolvă exact această problemă prin construcții DIFERITE (bootstrap studentizat — corectează bias-ul de estimare a varianței prin studentizare; bloc cu taper Politis-White — reduce efectele de margine, îmbunătățește calibrarea la eșantion mic; selecție automată de lungime de bloc — elimină parametrul liber `L` ales manual). Acestea sunt metode diferite, nu ajustări ale aceleiași estimări.

**Verdict:** `block_bootstrap@v1`, în forma actuală, trece de la `UNVALIDATED` la un statut TERMINAL — abandonat, nu reîncercat în această formă. (Notă de guvernanță: registrul, așa cum l-am citit, nu are încă un vocabular distinct pentru "abandonat permanent" față de "UNVALIDATED, în așteptare" — semnalez acest gol mic de vocabular pentru VE/CEO, nu îl rezolv unilateral eu.)

**Ce autorizez, ca lucru separat:** o RE-SPECIFICARE completă — o metodă NOUĂ (ex. `studentized_block_bootstrap@v1` sau `tapered_block_bootstrap_politis_white@v1`), înregistrată de la zero ca `UNVALIDATED`, cu propria ei baterie de acceptanță S1/S3/S4/S8 (sau echivalentul relevant), fără nicio moștenire de statut din `block_bootstrap@v1`. Nu specific eu acum construcția exactă (asta ar fi o sarcină separată, la cerere) — doar autorizez principiul: nevoia reală (test robust la autocorelație, valid la eșantion mic) rămâne, doar construcția trebuie să fie alta.

## E015-V1 — neschimbat

Confirmat, exact cum a precizat CEO: suspendarea lui E015-V1 e pe familia order-block (circularitate/dependență, `STATISTICIAN_ORDER_BLOCK_FAMILY_AUDIT_PROTOCOL_v1.0.md`), nu pe statutul metodei `block_bootstrap`. Această decizie de abandon nu schimbă, nu ridică, și nu agravează suspendarea E015-V1.

## `EMPIRICAL_PVALUE_SPEC.md` linia 21 — corectare recomandată, dar nu de mine

Confirmat, nu e caz D3: `EMPIRICAL_PVALUE_SPEC.md:21` ("INTERIM OFFICIAL, VALIDATED") și registrul (`UNVALIDATED`) folosesc DOUĂ bare diferite — bara veche a pipeline-ului (2 controale sintetice) vs. bara VE (bateria completă) — reconciliate deja de `PROJECT_AUDIT.md:23`. Nu e o contradicție de reparat ca fapt.

**Dar acum bateria completă arată că bara veche era greșită direcțional, nu doar provizorie** — "VALIDATED" în acel document, citit azi, riscă exact confuzia pe care o interzic peste tot în această sesiune: un cititor care nu cunoaște standardul vechi, mai lax, ar putea confunda "VALIDATED" din text cu `calibration_status: VALIDATED` din registru — și ar concluziona greșit că metoda e sigură de folosit. **Recomand corectarea, cu formularea exactă:**

> B. Block bootstrap of the trade-R series (SUPERSEDED — old-pipeline interim standard, 2 synthetic controls only; registry battery S1/S3/S4/S8 shows anti-conservative bias at realistic n≈250, see BLOCK_BOOTSTRAP_S_CALIBRATION_RECORD.md; do NOT read "VALIDATED" here as registry calibration_status; METHOD ABANDONED, see STATISTICIAN_BLOCK_BOOTSTRAP_ABANDONMENT_v1.0.md)

**Cine face corectarea:** documentul aparține arborelui vechiului pipeline, nu al meu, nici al VE — VE a semnalat problema tocmai pentru că nu editează unilateral artefacte din afara mandatului ei. Recomand ca proprietarul arborelui (Research Lab, care are deja acces de scriere pe `docs/` în acest repo și a executat munca D2/bracket conexă) să aplice corecția de mai sus, cu aprobarea CEO pentru rutare — eu nu editez fișierul, doar propun textul exact.

---

**Nu am executat nimic, nu am atins date. Statistician se oprește aici.**
