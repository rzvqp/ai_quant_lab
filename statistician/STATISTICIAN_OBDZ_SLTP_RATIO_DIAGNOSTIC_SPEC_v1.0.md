# STATISTICIAN — SPECIFICAȚIA DIAGNOSTICULUI DE RAPORT SL/TP PENTRU OBDZ

**Document ID:** STAT-OBDZ-SLTP-RATIO-DIAGNOSTIC-SPEC-v1.0
**Data:** 2026-07-29 · **Autor:** Statistician

Acest document e o SPECIFICAȚIE — nimic nu se rulează aici. Diagnosticul rămâne de executat de VE, DUPĂ publicare, exact cum au fost și celelalte specificații (LM-001, SMC_S1_v2).

**Verificare de sursă, înainte de orice decizie:** am recalculat W și pragul de rentabilitate **direct din valorile brute per-tranzacție** `net_R` (nu din agregatele raportate, pentru precizie maximă) — am scris un script de verificare temporar (șters după, necomis), rulând `detect_obdz001_signals`+`evaluate_obdz001` (mașina înghețată) și separând câștigătorii de pierzători direct:

```
regim       WR       mean_win(R)   mean_loss(R)   prag rentabilitate
bear      0,3908       1,8184         −1,1464            38,67%
bull      0,4021       1,6884         −1,2022            41,59%
corecție  0,4026       1,8499         −1,1052            37,40%
```

**Pragurile de rentabilitate CONFIRMĂ exact cifrele tale** (38,6%/41,7%/37,4% vs 38,67%/41,59%/37,40% — diferențe sub 0,1pp, în limita rotunjirii). **Coloana „W" pe care ai citat-o (1,89/1,84/1,97) nu se potrivește exact cu `mean_win` calculat direct din date (1,82/1,69/1,85)** — probabil o convenție diferită de definire a lui W în derivarea ta, pe care nu am putut-o reconstitui exact. Nu contează practic: **pragul (cifra decizională) e confirmat independent, la sursă, cu precizie sub-0,1pp** — asta era verificarea care conta. Confirm și explicația ta: bull are pragul cel mai mare pentru că are ATR-ul median cel mai mic (deci cost/R cel mai mare) — corect, verificat.

---

## MĂSURĂTOAREA A' — distribuția reală a excursiei adverse (MAE), derivată nu aleasă

**Populația: cele 275/223/156 declanșatoare compuse BRUTE (pasul 3 din numărătoare — bias aliniat + intersecție cross-candle DemandZone×OB), NU cele 261/194/154 deja filtrate de podeaua de ATR.** Motiv, identic cu Măsurătoarea A de la SMC_S1_v2: **podeaua de ATR însăși depinde de multiplicatorul SL** (`ATR_min = 3×cost/SL_MULT` — cu SL mai larg, podeaua scade, admițând mai multe declanșatoare) — aplicarea filtrului VECHI (derivat pentru SL=0,7) înainte de a măsura geometria pentru candidați NOI ar fi circulară.

**Definiția geometrică:** pentru fiecare din cele 275/223/156 declanșatoare (bara `t`, intrare `t+1`), măsor **Excursia Maximă Adversă (MAE)** — distanța maximă, în multipli de `ATR14[t]`, cu care prețul se mișcă ÎMPOTRIVA direcției intrării, pe fereastra `[t+1, t+1+92]` (92 bare = ziua empirică deja stabilită, Mandatul 3.18/3.19 — reutilizată verbatim, nu o cifră nouă; suficient de generoasă față de plasa curentă de 20 de bare, fără să fie nesfârșită). **Fereastra de măsurare e SEPARATĂ de plasa de tranzacționare** (care rămâne 20 bare/EOD pentru diagnostic, cf. mai jos) — Măsurătoarea A' caracterizează COMPORTAMENTUL PIEȚEI după declanșator, nu regula de ieșire.

**Raportare:** percentilele p25/p50/p75/p90 ale distribuției MAE-în-ATR, agregat și per regim, PLUS multiplicatorul original 0,7 ca ancoră de referință — exact structura de 5 puncte de la SMC_S1_v2.

**Set de candidați SL: p25/p50/p75/p90 ale distribuției MAE + 0,7 (ancoră)** — 5 puncte DERIVATE din comportamentul real al pieței după declanșator, nu alese liber. **TP1/TP2 NU se derivă separat — se fixează la 2×SL_candidat / 3×SL_candidat**, păstrând EXACT progresia 1×/2×/3× deja stabilită (Mandatul 3.24) pentru fiecare candidat — asta izolează CURAT întrebarea „contează raportul" de o a doua întrebare nelegată („ar trebui schimbat și RR-ul însuși").

**Dacă nu s-ar fi putut deriva:** ai lăsat opțiunea declarării explicite ca alternativă — nu e necesară aici, pentru că Măsurătoarea A' oferă o derivare directă, la fel de solidă ca cea de la SMC_S1_v2. Sugestia ta (1,0/1,5/2,0) rămâne un candidat PLAUZIBIL, dar nu-l aleg direct — dacă percentilele măsurate ies apropiate de aceste valori, e o confirmare independentă, nu o coincidență forțată.

## Podeaua de eligibilitate — RE-DERIVATĂ per candidat SL, nu fixă

**Punct tehnic obligatoriu, necerut explicit dar necesar:** podeaua de ATR (`ATR_min = 3×cost/SL_MULT`) depinde de `SL_MULT`. Pentru fiecare candidat, podeaua se RECALCULEAZĂ cu aceeași formulă (saturație 3×cost), NU se reutilizează $0,857 fix. Populația eligibilă efectivă (după podea) va fi ușor MAI MARE la SL-uri mai late (podeaua scade) — raportată explicit la fiecare candidat, nu ascunsă.

---

## CELE TREI PUNCTE DE TRATAT

### 1. Orizontul: FIX la 20 bare/EOD pentru diagnostic, fracția de expirare raportată obligatoriu

**Plasa de tranzacționare (`min(entry+20, EOD)`) rămâne NESCHIMBATĂ pentru toate cele 5 candidate SL** — condiție de control, ca să izolăm CURAT „contează raportul" de „a contat și mai mult timp". Nu se re-derivă orizontul aici.

**Diagnostic obligatoriu, la fiecare candidat×regim:** fracția de tranzacții care expiră FĂRĂ rezoluție (nici TP, nici SL) — `timeout_plasa`+`timeout_EOD`, separat de restul. Dacă la SL-uri late această fracție crește substanțial (semn că 20 de bare devine insuficient pentru un stop mai lat), se RAPORTEAZĂ ca limitare cunoscută a ACESTUI diagnostic, nu se corectează pe ascuns prin lărgirea orizontului în același test (ar reintroduce exact confuzia pe care o evităm).

### 2. Structura de payoff: conversia TP1→TP2, obligatorie la fiecare celulă, nu doar expectancy

**Raportare obligatorie, la fiecare din cele 5×3 celule (SL×regim):** defalcarea COMPLETĂ pe motive de ieșire (SL/TP1→TP2/TP1→breakeven/TP1→timeout/niciodată-TP1→timeout), PLUS rata de conversie TP1→TP2 explicit calculată (`reach_TP2/reach_TP1`) — nu doar expectancy_R/expectancy_$. Motivul, exact cum ai spus: rata de conversie (68-73% acum) e o funcție a cât de departe e TP2 relativ la volatilitatea reziduală după TP1 — un SL mai lat înseamnă ținte mai depărtate, deci probabil o rată mai mică; asta trebuie VĂZUT, nu dedus din expectancy singur.

### 3. Pragul de decizie, scris ACUM, înainte de orice cifră — DOLARII sunt variabila de decizie

Reutilizez EXACT structura și regula SMC_S1_v2:

```
ÎNCHIS DEFINITIV pentru familia OBDZ (linia de raport SL/TP):
  expectancy net în DOLARI <= 0 la TOATE cele 5 candidate SL, în TOATE cele 3 regimuri.

MERITĂ IPOTEZĂ NOUĂ (OBDZ-002, family=2 cu OBDZ-001):
  expectancy net în DOLARI > 0 la CEL PUȚIN 2 din cele 3 candidate SL mai late (p75, p90),
  în CEL PUȚIN 2 din cele 3 regimuri — un TIPAR în partea largă a distribuției MAE, nu un
  punct izolat.

NICIUNA DIN CELE DOUĂ (tipar amestecat, un punct izolat, sau pozitiv într-un singur regim):
  TESTABLE BUT INSUFFICIENT EVIDENCE — nu se declară nici închidere, nici ipoteză nouă.
```

**Regula deja stabilită, reaplicată identic: DOLARII, nu R, sunt variabila de decizie.** Un stop de 2-3× mai lat va arăta aproape automat mai bine în R (cost/R scade), dar fiecare pierdere e proporțional mai mare în bani reali. **Fiecare celulă raportează AMBELE (expectancy_R ȘI expectancy_$), cu DOLARII decisivi pentru pragurile de mai sus** — o îmbunătățire de R fără îmbunătățire de dolari NU trece bara „merită ipoteză nouă".

---

## DIAGNOSTIC, nu FITTING — declarat acum, nu la vedere cifrelor

**Întrebarea pusă: „rezultatul depinde de raport, sau e nul peste tot?" — NU „care raport dă cel mai bun rezultat?"** Repet distincția, exact pentru că tentația e mai mare aici (există deja o celulă pozitivă și distribuită, la corecție) — pragul de mai sus e scris ACUM, înainte ca vreo cifră din Măsurătoarea A' sau din re-rulare să existe, tocmai ca să nu poată fi citit ulterior ca justificând continuarea indiferent de rezultat. Diferența nu e în cod (aceeași mașină de stare, `obdz001.py`, rulează pentru fiecare candidat) — e în faptul că pragul de decizie a fost FIXAT înainte de execuție, nu ales după ce arată bine.

---

## Familia de corecție: CONFIRM — diagnosticul însuși NU intră în familie

**Confirm interpretarea ta.** Măsurătoarea A' + re-rularea pe cele 5 candidate SL e un DIAGNOSTIC (o măsurătoare + o regulă de decizie pre-înregistrată), NU un test de ipoteză cu propriul H0/H1/verdict — exact precedentul SMC_S1_v2, a cărui Măsurătoare A nu a fost numărată ca test separat. **Family rămâne 1 (OBDZ-001, deja închis) până când, și DOAR dacă, diagnosticul produce o ipoteză nouă formal pre-înregistrată** — abia atunci family devine 2 (OBDZ-001 + succesorul), cu pragul de semnificație îngustat corespunzător, exact cum ai confirmat.

---

## Recalibrarea oracolului pentru corecție: DUPĂ diagnostic, nu înainte — motivat

**Recomand explicit: AȘTEAPTĂ.** Motivul e secvențial, nu o amânare arbitrară: dacă diagnosticul duce la o ipoteză nouă (SL mai lat), acea ipoteză va avea propria distribuție de orizont REALIZAT (probabil mult mai lungă decât 1-2 bare, dat fiind un stop mai lat) — orice recalibrare făcută ACUM (potrivită pe orizontul realizat de 1-2 bare al construcției CURENTE) ar deveni OBSOLETĂ imediat, trebuind refăcută pentru noua distribuție oricum. Dacă, în schimb, diagnosticul arată nul peste tot (linia se închide definitiv), recalibrarea celulei de corecție devine, practic, irelevantă pentru orice decizie — linia e închisă indiferent dacă p=0,186 „real" ar fi 0,10 sau 0,25 sub un nul mai bine calibrat. **În ambele cazuri, recalibrarea acum ar fi efort irosit sau muncă ce trebuie refăcută.** Singurul scenariu în care ar merita ACUM ar fi dacă cineva vrea să știe, din curiozitate pur științifică, dacă celula de corecție merită investigată INDEPENDENT de linia SL/TP — nu e cazul aici, dat fiind diagnosticul e deja comandat.

---

**Nimic rulat în acest document. Publicat pe `statistician-foundation`; manifestul se incrementează.**
