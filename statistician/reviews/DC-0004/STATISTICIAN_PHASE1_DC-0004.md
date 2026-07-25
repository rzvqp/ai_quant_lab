# STATISTICIAN — PHASE 1 REPORT

**Report ID:** STAT-PHASE1-DC-0004-v1
**Discovery Candidate:** DC-0004 — "New-York-Session Prior-Day-High Sweep-Reject Is Followed By Reversion"
**DC freeze hash (as cited by Red Team):** `sha256:4560ba15e08226a9614097e1bd500db5a53d5095aa11ed02296876c64d665038` (current, post Library-Concept-Scan recompute)
**Phase:** Statistician Phase 1 — DESIGN AND TESTABILITY EVALUATION ONLY. No backtest executed. No new data collected. No market observed. No hypothesis validated.
**Date:** 2026-07-24 · **Reviewer:** Statistician
**Sources read (read-only, official artifacts only):**
- `ai_quant_lab-alpha-automation/discovery_candidates/DC-0004_ny_session_conditioned_sweep_reject/candidate_v1.md`, `metadata_v1.json` (no addenda exist — Red Team confirms "Addenda: none")
- `ai_quant_lab/red_team/reviews/DC-0004/REVIEW_DC-0004_v1.md`
- `ai_quant_lab/red_team/RED_TEAM_PHASE1_REPORT.md` — §0, F1–F9, §5 implicit assumptions, §6 DC-0004 entry, §7 item 6, §8 DC-0004 row.

**Explicitly NOT read:** Alpha or Red Team conversation/chat history; the underlying research-log documents cited by DC-0004 (`OBS-0001`, `OBS-0003`, `OBS-0008`, `OBS-0012`, `OBS-0013`, and their scripts) or Knowledge Base concepts it references (`K01`, `K04`, `K05`, `E017`). None of these are among the three authorized artifact categories. All facts about them used below (matched-null p-values, cell counts, Bonferroni threshold, sign-stability across halves) come exclusively from quotations already inside `candidate_v1.md` and `REVIEW_DC-0004_v1.md`.

**Nothing was modified.** DC-0004, the Red Team report/review, Knowledge Base, Alpha artifacts, and existing confidence/classifications are untouched.

---

## 1. Reconstrucția fidelă a ipotezei

Din `candidate_v1.md` §1, fără reformulare în strategie:

> Pe XAUUSD H1, prima bară a zilei al cărei maxim depășește maximul zilei precedente ("prior-day high") dar care închide înapoi sub acel nivel (un "sweep-reject" al prior-day high) este urmată de **reversie** — dar **doar când evenimentul are loc în sesiunea New York**. În alte sesiuni același eveniment nu arată reversie, iar pe partea Asia/Londra semnul este inversat.

Prezentat de Alpha explicit ca observație descriptivă, fără pretenție de cauzalitate ("No causal claim is made") și fără pretenție de edge ("Not validated, not an edge, not a strategy, no profitability claim").

## 2. Variabilele măsurate

- **Variabilă de expunere:** evenimentul sweep-reject al prior-day-high (prima bară H1 a zilei, high > prior-day-high ȘI close < prior-day-high), condiționat de sesiunea în care are loc (6 celule sesiune × direcție testate în OBS-0003).
- **Variabilă de rezultat:** continuation-excess măsurat la orizonturile K6 și K12 (ore după eveniment), calculat față de baseline-ul forward propriu al sesiunii NY (nu drift global).
- **Valori raportate:** K6 continuation-excess **−3.64**, CI95 [−6.90, −0.12] (exclude zero); K12 **−4.80**, CI95 [−8.88, +0.05]; P(continuation) = 0.36 la K6, 0.26 la K12; **n = 42**. NY-up-reject este singura celulă (din 6) care atinge semnificație nominală. Sign-stabil pe cele două jumătăți temporale (2023-24: −3.25, n=29; 2025: −4.65, n=13).

## 3. Definiția operațională existentă

Cea mai precisă din portofoliul citat de Red Team: nivel = prior-day high (D1); eveniment = prima bară H1 a zilei cu high>PDH și close<PDH; condiționare = sesiunea (Asia/Londra/NY × direcție = 6 celule); orizont = K6/K12 ore; baseline = forward baseline propriu al sesiunii NY; metodă = matched-null (scripturi `obs0003_session_reject.py`, `obs0008_ny_reject_null.py`, `obs0012_reject_allcells_null.py`, `obs0013_ny_stability.py`, deja rulate pe 16,623 bare H1, 2023-01-02→2025-10-23).

## 4. Ipoteza nulă (H0)

Continuation-excess-ul observat la evenimentele sweep-reject-NY nu diferă sistematic de cel produs de un eșantion matched-null comparabil (aceeași sesiune/perioadă, fără condiționarea de eveniment) — sweep-reject-ul prior-day-high în sesiunea NY nu cară informație dincolo de ce ar produce o mostră aleatoare, potrivită, din acea sesiune.

## 5. Ipoteza alternativă (H1)

Sweep-reject-ul prior-day-high în sesiunea NY este urmat sistematic de reversie (continuation-excess negativ, semnificativ diferit de nulul potrivit), efect absent sau de semn opus în celelalte sesiuni.

## 6. Elementele lipsă pentru testare

| Element | Status |
|---|---|
| **Corecție testări multiple** | p=0.021 nu trece pragul Bonferroni (0.0083) pentru cele 6 celule testate — recunoscut de Alpha. |
| **Corecție pentru selecție** | Celula a fost aleasă DUPĂ inspectarea a ~12 celule în OBS-0003; p-ul matched-null nu este corectat pentru acest proces. |
| **Validare out-of-sample** | Holdout-ul rezervat (post 2025-10-23) nu a fost încă atins — CEO-gated, deliberat necheltuit. |
| **Robustețe pe jumătăți temporale** | Semn stabil, dar CI-urile per-jumătate (n=29 și n=13) includ ambele zero — semnificația nu se menține la nivel de jumătate. |
| **Decuplare sesiune vs. regim de volatilitate** | Nu există un test explicit care separă "efectul de sesiune NY" de "efectul regimului de volatilitate orară" — chiar candidatul notează doar posibilitatea reducerii, fără a o testa. |

## 7. Evaluarea independentă a criticilor Red Team

**Confirm:**
- **C3 (multiple testing/selecție)** — confirmat direct din text: 6 celule testate, p=0.021 nu trece Bonferroni (0.0083); celula a fost aleasă post-hoc dintr-un set de ~12 celule candidate din OBS-0003.
- **Clasificarea "Class A"** ca fiind candidatul cel mai bine specificat din portofoliu, cu un test decisiv deja identificat (holdout-ul rezervat) — confirmat independent, pe baza preciziei definiției (nivel, eveniment, sesiune, orizont, baseline) și a matched-null-ului deja rulat.
- **Nota Red Team** că trebuie să intre în validare "as a hypothesis, not as a result" — confirmat, exact din cauza efectului de selecție nedecorectat.

**Infirm parțial / extind:**
- Red Team notează posibila reducere la profilul orar de volatilitate ("Reducible to: the Volatility hour-of-day profile...") dar **nu o transformă într-o precondiție obligatorie** a testului de validare — doar o menționează ca observație. Propun (§9-11) ca acest control să fie o componentă **obligatorie**, nu opțională, a designului de validare — altfel un rezultat pozitiv pe holdout ar putea doar re-confirma un primitiv deja promovat, nu un fenomen nou de nivel.

**Rămâne nedeterminat:**
- Dacă efectul, chiar dacă se confirmă pe holdout, este atribuibil specific nivelului "prior-day-high" sau oricărui nivel de referință similar testat în aceeași fereastră orară NY (ex. un nivel arbitrar). Nici Red Team, nici Alpha nu propun un control de tip "nivel placebo" — rămâne o întrebare deschisă neabordată de niciuna dintre părți.

## 8. Cel mai puternic argument împotriva ipotezei

Combinația testare-multiplă + selecție: rezultatul semnificativ (p=0.021) provine dintr-o singură celulă aleasă DUPĂ observarea a 12 celule candidate, iar pragul corectat (Bonferroni 0.0083) nu este atins. Sub selecția "alege cea mai extremă din 12 teste", o valoare p nominală de 0.021 nu mai este o dovadă rară — este exact ce te-ai aștepta să găsești din întâmplare, testând atâtea celule ("garden of forking paths"). Acesta este, de altfel, motivul explicit invocat chiar în documentul frozen pentru care rezultatul in-sample "nu cară greutate evidențială" — un argument suficient, singur, pentru a nu trata starea actuală ca dovadă.

## 9. Cea mai plauzibilă explicație alternativă

Regimul de volatilitate orară — deja promovat ca primitiv în lab (profil ~4.3× peak/trough, vârf 13-14h UTC = fereastra NY). Dacă sesiunea NY are participare/lichiditate sistematic mai mare, orice eveniment de tip "prag depășit apoi respins" ar arăta reversie mai puternică acolo doar din cauza regimului de volatilitate, nu pentru că nivelul "prior-day-high" cară informație de memorie specifică. Candidatul însuși recunoaște explicit această reductibilitate posibilă.

## 10. Riscurile metodologice suplimentare identificate de Statistician

- **Lipsa unui control "nivel placebo":** nu există un test paralel folosind un nivel de referință arbitrar (non-prior-day-high) în aceeași fereastră NY, pentru a izola dacă efectul e specific nivelului sau doar sesiunii/regimului de volatilitate — gol pe care nici Red Team, nici Alpha nu îl cer explicit.
- **Supra-ponderarea "sign-stability" ca dovadă:** "sign-stable across both halves" e prezentat ca un punct forte, dar cu n=29 și n=13 și CI-uri care includ zero în ambele jumătăți, stabilitatea semnului la eșantioane atât de mici e o dovadă slabă — sub null, semnul se poate păstra întâmplător cu probabilitate apropiată de 50%; acest argument nu ar trebui cântărit la fel de mult ca semnificația statistică propriu-zisă.
- **Riscul de a "cheltui" holdout-ul incomplet:** dacă testul pe holdout se rulează doar pe celula NY-up (câștigătoarea in-sample), fără a repeta explicit testul pe toate cele 6 celule și a reaplica corecția family-wise, holdout-ul ar putea părea să "confirme" un efect care e doar zgomot re-selectat.
- **Feed-ul broker (analog F6 din raportul Red Team, aplicat aici):** deși DC-0004 nu se bazează pe volum, nivelul "prior-day-high" derivă din prețurile OANDA proprii — diferențe de gap/preț față de alte feed-uri ar putea afecta definirea exactă a evenimentului; nemenționat explicit în DC-0004 sau în review-ul Red Team pentru acest candidat.

## 11. Experimentul statistic cu puterea maximă de discriminare

Test unic, pre-înregistrat, pe holdout-ul rezervat (post 2025-10-23):

1. **Re-rulare identică** a metodologiei OBS-0003/0008/0012/0013 (aceleași scripturi, definiție identică a evenimentului, orizonturi K6/K12, matched-null) pe **toate cele 6 celule** sesiune×direcție din fereastra holdout — nu doar pe celula NY-up.
2. **Corecție family-wise** (Bonferroni sau Benjamini-Hochberg) aplicată pe toate cele 6 celule din holdout, exact ca în eșantionul original.
3. **Control obligatoriu pentru regimul de volatilitate orară:** regresia continuation-excess pe evenimentul sweep-reject, controlând explicit pentru profilul orar de volatilitate (primitiv deja existent în lab); dacă efectul NY dispare după control, nulul de la §9 e confirmat.
4. **Test placebo (control suplimentar recomandat):** același test pe un nivel de referință arbitrar (non-prior-day-high) în aceeași fereastră NY, pentru a verifica specificitatea nivelului (§10).

Acest design maximizează puterea de discriminare pentru că testează simultan: (a) dacă efectul replică out-of-sample la pragul corectat family-wise (adresând C3), (b) dacă e specific nivelului sau doar regimului orar (adresând §9), folosind (c) singurul eșantion cu adevărat independent disponibil pentru acest candidat — holdout-ul, nefolosit până acum.

## 12. Datele necesare

- Seria H1 completă XAUUSD/OANDA pentru fereastra holdout (post 2025-10-23T09:15:00Z) — deja rezervată, nefolosită.
- Nivelurile D1 prior-day-high pentru aceeași fereastră.
- Aceleași scripturi/metodologie ca OBS-0003/0008/0012/0013, aplicate identic, fără modificări ad-hoc, pentru comparabilitate cu rezultatul in-sample.
- Variabila de regim orar de volatilitate (primitiv deja existent) pentru controlul de la pasul 3.

## 13. Dimensiunea minimă a eșantionului / metoda de estimare

Eșantionul in-sample avea n=42 la K6 (doar 13 în a doua jumătate temporală) — deja insuficient pentru semnificație robustă chiar înainte de corecția Bonferroni. Pentru holdout, dimensiunea fereastrei e fixă (nu poate fi aleasă), dar puterea așteptată trebuie calculată din rata de bază observată in-sample (~42 evenimente / ~2.8 ani ≈ 15/an). Dacă fereastra holdout oferă sub ~15-20 evenimente NY-up-reject noi, puterea de a confirma/infirma robust rămâne joasă și rezultatul trebuie interpretat ca atare — nu forțat într-un verdict tranșant doar pentru că holdout-ul a fost "cheltuit".

## 14. Testele statistice recomandate

**(a)** Matched-null re-test identic celui in-sample, pe toate cele 6 celule din holdout (nu doar NY-up).
**(b)** Corecție family-wise (Bonferroni/BH) aplicată pe cele 6 celule din holdout.
**(c)** Regresie de control pentru profilul orar de volatilitate (§9/§11 pas 3).
**(d)** Test placebo pe nivel arbitrar (§10/§11 pas 4).
**(e) Sensibilitate la definiție:** re-rulare cu orizonturi alternative (K4/K8) și cu praguri alternative de "sweep" (ex. depășire minimă peste PDH), pentru a verifica dacă rezultatul depinde de alegeri specifice de parametri.
**(f) Temporal leakage:** confirmare că niciun element al definirii evenimentului sau al nulului potrivit nu folosește date din fereastra de rezultat (K6/K12) — risc structural redus, dar de reconfirmat pe scripturile reutilizate.
**(g) Outcome leakage:** confirmare că evenimentele din holdout sunt selectate prin exact același criteriu fix (high>PDH și close<PDH pe prima bară a zilei), fără ajustări discreționare după observarea rezultatelor lor.
**(h) Robustețe pe sub-perioade** ale holdout-ului (dacă fereastra permite măcar 2 subperioade), testând stabilitatea semnului, analog robusteții deja cerute in-sample.

## 15. Criteriile preînregistrate de succes și eșec

- **Succes (STATISTICALLY ROBUST — eligibil pentru promovare la Knowledge Base):** efectul NY-up-reject replică pe holdout la pragul corectat family-wise (peste toate cele 6 celule), cu semn negativ (reversie) consistent cu in-sample, **ȘI** supraviețuiește controlului pentru profilul orar de volatilitate (§11 pas 3).
- **Eșec (STATISTICALLY REJECTED):** efectul nu replică pe holdout la pragul corectat (nesemnificativ sau semn schimbat), **SAU** dispare complet după controlul pentru volatilitatea orară (confirmă explicația alternativă de la §9 ca fiind cauza reală).
- **Indeterminat (rămâne TESTABLE BUT INSUFFICIENT EVIDENCE):** numărul de evenimente NY-up-reject disponibile în fereastra holdout e sub pragul de putere calculat la §13, sau rezultatele sunt instabile/contradictorii între testul principal și controlul de volatilitate.

## 16. Verdictul final

**READY FOR STATISTICAL VALIDATION.**

Motivare independentă: DC-0004 este singurul candidat din portofoliu cu o populație complet definită (nivel, eveniment, sesiune, orizont, baseline), deja testat printr-un matched-null pre-înregistrat, cu un test decisiv deja identificat și rezervat (holdout-ul post 2025-10-23) — nefolosit până acum. Ajung la aceeași concluzie practică ca Red Team, dar independent, cu **două condiții suplimentare proprii**: (1) testul pe holdout trebuie rulat pe toate cele 6 celule cu corecție family-wise repetată, nu doar pe celula câștigătoare in-sample, altfel selecția se repetă identic; (2) controlul pentru profilul orar de volatilitate trebuie să fie parte **obligatorie**, nu doar notă de context — altfel un rezultat pozitiv pe holdout ar putea confirma doar regimul de volatilitate deja cunoscut, nu un fenomen nou de nivel.

Acest verdict **nu** este o confirmare a ipotezei — p-ul in-sample (0.021) nu trece corecția pentru testări multiple/selecție, iar holdout-ul, singurul test cu adevărat independent, nu a fost încă rulat.

## 17. Recomandarea pentru pasul următor

1. **Nu cheltui încă holdout-ul.** Este o resursă CEO-gated, deliberat necheltuită; execuția testului de la §11-15 necesită autorizare CEO explicită și separată, dat fiind caracterul ireversibil al resursei (odată cheltuit, holdout-ul nu mai poate servi drept test independent pentru acest candidat).
2. Recomand ca designul complet (toate cele 6 celule + corecție family-wise + control de volatilitate + test placebo) să fie fixat și aprobat **înainte** de orice atingere a datelor din holdout, pentru a preveni o nouă rundă de selecție.
3. Odată autorizată Faza 2, aceasta ar trebui tratată ca eveniment unic, irepetabil pentru acest candidat — nu se recomandă încercări repetate pe holdout dacă primul rezultat nu convine.

---

**Statistician nu a modificat DC-0004, raportul/review-ul Red Team, Knowledge Base, artefactele Alpha, sau clasificările/confidence existente.**

**Statistician se oprește aici și așteaptă aprobarea CEO înainte de următorul candidat.**
