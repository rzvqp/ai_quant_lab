# FLOW C — P2 EXECUTION PLAN
### Planul de execuție al analizei relaționale (P2 — Cartografiere relațională)
**Status:** ✅ v1.0 — ÎNGHEȚAT (FROZEN) prin decizie CEO, 2026-07-21 — planul oficial de execuție P2
**Guvernat de (înghețat):** ROADMAP (P2) · ANALYSIS_PROTOCOL v1.0 · P1_COMPLETION_CRITERIA (B.4 P2 Readiness)
**Aprobat de CEO:** 5 pachete (WP1–WP5) + ordinea artifact-first + §7 Relational Analysis Contract; cele 6 decizii statistice rezolvate (§9).
**P2 OFICIAL DESCHIS la commit. WP1 autorizat. WP2–WP5 NEautorizate până WP1 e complet și revizuit.**

---

## 0. PRECONDIȚII (P2 nu se deschide automat)

- **P1 e ÎNCHIS** (CEO 2026-07-21; Coverage Confidence = High, snapshot curent).
- **B.4 (P2 Readiness)** trebuie verificată înainte de execuție: P1 complet ✅ · coadă relațională reală ✅ (acumulată în §7 al fiecărui raport P1) · normal stabil ✅ · valoare relațională pozitivă ✅.
- **Deschiderea P2 rămâne o decizie CEO separată.** Acest document e doar planul; nu autorizează start.

---

## 1. PACHETE DE LUCRU RELAȚIONALE (din coada P1)

Fiecare pachet provine din observații amânate explicit în rapoartele P1. Fiecare corelează axe care în P1 au fost descrise doar marginal.

| WP | Titlu | Relația de examinat | Sursă (coadă P1) |
|---|---|---|---|
| **WP1** | Enumerare / mărime-familie ↔ profitabilitate | Rata hist_prof mai mare a S1 (22,7% vs 18,1%) e efect real sau artefact de lățime-de-căutare? Extreme mari la n mic (S19/S14). | RI-0001, RI-0003, RI-0005 |
| **WP2** | Validare vs in-sample | `val_exp` vs `exp` ca divergență per-ipoteză (NU marginale). Atenție: lipsă masivă localizată în S1 (populații neidentice). | RI-0002, RI-0003 |
| **WP3** | Concentrare ↔ fragilitate | `t1/t3/t5` și `wo1` vs flag-ul `fragile` / `exp`. ~37% profitabili fragili; ~31% cu wo1≤0. | RI-0002, RI-0003 |
| **WP4** | Side ↔ profitabilitate | Long-skew (271/86 la câștigători) + „both" exclusiv în familii zero-profit. | RI-0001, RI-0004, RI-0005 |
| **WP5** | Amprentă temporală ↔ outcome | Consistență temporală (pos_months/years) vs profitabilitate/robustețe. | RI-0005 |

*(research_worthy absent la S3/S13/S16/S18/S19 se tratează în interiorul WP1/WP3, nu ca pachet separat.)*

---

## 2. ORDINEA DE EXECUȚIE (artifact-first, valoare-maximă)

```
WP1 → WP2 → WP3 → WP4 → WP5
```

**Justificare (protocol §6.1 — artifact-first):**
- **WP1 primul.** Dacă setul de câștigători e în mare parte artefact de enumerare (S1 = 58% din corp, 1152 extrageri), atunci ORICE analiză relațională condiționată pe câștigători (WP3/WP4/WP5) e contaminată. WP1 e testul „setul nostru de câștigători e măcar real?" — fundația.
- **WP2 al doilea.** `val_exp` vs `exp` e cel mai apropiat lucru de robustețe out-of-sample → cea mai mare valoare de decizie după fundație.
- **WP3, WP4, WP5** urmează — relații condiționate pe câștigători, de rulat DUPĂ ce WP1 a clarificat dacă baza de câștigători e de încredere.

*Pachetele sunt în mare independente; ordinea reflectă PRIORITATE de valoare + regula artefact-first, nu dependență dură — cu excepția că WP1 precede logic pachetele condiționate pe câștigători.*

---

## 3. OUTPUT-URI AȘTEPTATE (per pachet)

Conform ROADMAP, P2 produce DOAR **Meta Analysis** și **Anomaly Report**. Mecanismele și handoff-ul spre Alpha aparțin P4.

| WP | Output primar | Output posibil |
|---|---|---|
| WP1 | Meta Analysis (mărime × hit-rate) | Anomaly Report (dacă hit-rate-ul S1 e artefact) |
| WP2 | Meta Analysis (val_exp × exp) | Anomaly Report (divergențe severe) |
| WP3 | Meta Analysis (concentrare × fragilitate) | — |
| WP4 | Meta Analysis (side × outcome) | Anomaly Report (both↔zero-profit) |
| WP5 | Meta Analysis (temporal × outcome) | — |

**Regulă:** orice mecanism care se conturează în P2 se **loghează pentru P4**, NU se produce ca Hypothesis Report în P2. Orice relație rămâne observațională (C1/C2 max, niciodată validată).

---

## 4. CRITERII DE OPRIRE (P2)

- **Coadă epuizată:** toate cele 5 pachete au produs Meta Analysis-ul lor.
- **Saturație relațională:** o rundă nouă nu mai scoate o relație cross-axă nevăzută.
- **Plafon epistemic (protocol §7):** în clipa în care o relație cere un experiment nou pe date proaspete → STOP, handoff spre P4/Alpha (nu se execută în P2).
- **Nevoie de mecanism:** când analiza cere „de ce" → STOP, se loghează pentru P4.
- **Halt-on-contradiction:** contradicție cu un fapt stabilit → oprire + semnalare.
- **Anti-perfecționism:** un Meta Analysis bine pus per pachet e livrabil complet; P2 nu rezolvă totul.

---

## 5. GRANIȚE DE GUVERNANȚĂ (P2)

- P2 **corelează** axe; NU **explică** (mecanism = P4) și NU **validează** (Alpha).
- FĂRĂ formulare de ipoteze în P2 (Hypothesis Report = P4). Mecanismele se loghează, nu se produc.
- FĂRĂ handoff la Alpha în P2 (Candidate Experiment = P4).
- FĂRĂ cross-flow A×B (backtest vs live = P5, gată de dovada Flow B).
- **Artifact-first obligatoriu** (protocol §6.1): la egalitate, „artefact de metodă" bate „semnal de piață".
- `val_exp` cu lipsă localizată în S1 se tratează onest (populații neidentice) — fără afirmații de pereche pe date incomplete.
- Coverage Confidence rămâne High doar cât timp snapshot-ul nu se schimbă; un batch nou revocă și poate redeschide P1 înaintea P2.

---

## 6. AUTO-FALSIFICARE A PLANULUI (scurt)

- **„Ordinea nu contează, pachetele-s independente."** Respins parțial: sunt independente ca date, dar WP1 (artefact-first) trebuie să preceadă pachetele condiționate pe câștigători — altfel riști să construiești relații pe un set de câștigători contaminat.
- **„WP2 ar trebui primul (validarea e cea mai importantă)."** Respins: validarea (val_exp) e ea însăși condiționată pe câștigători și pe o lipsă localizată în S1; are sens abia după ce WP1 clarifică statutul enumerării S1.
- **„5 pachete sunt prea multe."** Testat: fiecare provine dintr-o observație P1 distinctă și amânată; comasarea ar ascunde exact granițele pe care P1 le-a respectat. Păstrate.

---

---

## 7. RELATIONAL ANALYSIS CONTRACT (pre-înregistrare — refinare CEO)

Toate deciziile de mai jos sunt fixate **înainte de a observa orice rezultat analitic** (protocol §5.2, așteptare pre-declarată). Transformările NU se aleg după rezultate.

### Fundament structural comun (cunoscut din P1, nu observație de rezultat)
- Corp: 1972 ipoteze, 20 familii, **puternic dezechilibrat** (S1=1152). Ipotezele dintr-o familie sunt VARIANTE (config/dataset partajat, parametrizări repetate) → **NU sunt independente** (pseudo-replicare severă). **Unitatea inferențială primară = FAMILIA (20 clustere)**, nu ipoteza.
- `val_exp`: 1796 prezente / 176 lipsă, **toate lipsele în S1**.
- `fragile` e definit doar în interiorul hist_prof (357) → analizele cu `fragile` sunt within-profitable.
- `both` apare EXCLUSIV în familii zero-profit → `both` e **complet confundat cu familia** (nu comparabil ca side liber).
- **Default anti-post-hoc:** metode **rank-based / nonparametrice** ca standard (robuste la asimetrie extremă: dd max 2000, pf=∞, t* cu outlieri negativi), ca să NU alegem transformări după ce vedem datele.

### 7.1–7.4 Contract per pachet (Populație · Variabile · Estimand · Analiză primară)

| WP | Populație / unitate / nivel | Predictor → Outcome (tip) | Transf. pre-fixată | Estimand (primar) | Analiză primară |
|---|---|---|---|---|---|
| **WP1** | Toate 20 familiile; unitate=**familia** (n=20); corpus-wide | mărime familie `n_hyp` (continuu) → hit-rate familie (proporție) + exp_max familie | rank | Spearman ρ(mărime, hit-rate) și ρ(mărime, exp_max) la nivel de familie | Spearman ρ + CI bootstrap pe familii; permutation contrast extreme×mărime |
| **WP2** | Complete-case pe `val_exp` (n=1796; **exclus 176, toate S1**); unitate=ipoteză, cluster=familie | `val_exp` vs `exp` (pereche, continuu) | rank/pereche | **diferență pereche** val_exp−exp (Hodges-Lehmann median) | HL median al diferenței pereche, CI bootstrap cluster-familie |
| **WP3** | Doar hist_prof (n=357, unde `fragile` e definit); cluster=familie; within-profitable | concentrare `t5` (continuu) → `fragile` (binar) | rank | contrast effect-size t5: fragile vs non-fragile (rank-biserial) | diferență mediană t5 (fragile−non), CI bootstrap cluster |
| **WP4** | Toate; unitate=ipoteză, cluster=familie; corpus-wide. **`both` exclus din primar (confundat)** | side ∈{long,short} → `hist_prof` (binar) | — | **diferență de rată condiționată** hist_prof(long)−hist_prof(short) | rate diff cluster-aware; `both` doar notă descriptivă separată |
| **WP5** | Unde temporal prezent; unitate=ipoteză, cluster=familie | `pos_months` (continuu) → `exp` (continuu) | rank | Spearman ρ(pos_months, exp) | Spearman ρ, CI bootstrap cluster |

- **Analize secundare** (per-familie, alte outcome-uri, alte câmpuri temporale): etichetate EXPLICIT ca **exploratorii**, generatoare de întrebări, nu confirmatorii.
- **Un singur outcome primar per WP** (pre-ales mai sus) — fără outcome-shopping.

### 7.5 Politica de missingness
- **Complete-case** pe `val_exp` (WP2). Se raportează n exclus (176) și faptul că **toate lipsele sunt în S1** → complete-case-ul WP2 exclude o mare parte din S1 → populația pereche e **ne-dominată de S1**, fapt care se raportează explicit.
- **Nicio comparație marginală ne-perechată nu se interpretează ca relație pereche** (regula CEO). WP2 folosește DOAR perechi complete val_exp↔exp pe același rând.
- **Missingness-ul devine întrebare relațională separată:** „de ce `val_exp` lipsește exclusiv în S1?" — întrebare descriptivă înregistrată; *cauza* = 🔒 P4.

### 7.6 Controlul multiplicității
- Set de teste primare înregistrate: **5** (câte 1 per WP; WP1 are 2 estimand-uri → 6 primare). Control **FDR Benjamini-Hochberg** peste TOATE testele primare înregistrate.
- Analizele per-familie / subgrup / exploratorii: FDR separat SAU marcate strict generatoare-de-ipoteze; nu intră în verdictul primar.
- **TOATE relațiile testate se raportează** (inclusiv nule), nu doar cele „semnificative".

### 7.7 Regula effect-size
Pentru fiecare rezultat inferențial: **effect size · interval de incertitudine · n (și n clustere) · semnificație ajustată (FDR) · magnitudine practică.** Semnificația singură = insuficientă.
- **Prag de materialitate (provizoriu, cere sign-off CEO):** |Spearman ρ| < 0,10 sau diferență de rată < 5 puncte procentuale = „prea mic pentru a fi material informativ" → NULL/INCONCLUSIVE indiferent de p.

### 7.8 Controlul dependenței
- **Cluster = familia (20).** Analiză cluster-aware (bootstrap pe familii / agregare la nivel de familie). Efectiv n≈20 → inferența e slabă → **se înclină spre descriptiv + effect-size, nu spre p-values.**
- Pseudo-replicare recunoscută explicit: cele 1152 rânduri S1 **nu** sunt 1152 observații independente.
- Config/dataset partajat nu e complet observabil din artefact → conservator: familia ca cluster; unde independența nu se poate justifica → **retrogradare de încredere** (§7.9).

### 7.9 Stări de evidență (clase de rezultat)
- **DESCRIPTIVE ASSOCIATION** — vizibilă descriptiv, fără pretenție inferențială.
- **STATISTICALLY SUPPORTED ASSOCIATION** — effect-size material + CI exclude nulul + supraviețuiește FDR + cluster-aware. *(Rămâne descriptiv-de-corp, NU edge validat.)*
- **FRAGILE ASSOCIATION** — depinde de câteva clustere/rânduri; cade la leave-one-cluster-out (ex. dispare fără S1).
- **ARTIFACT-SUSPECT** — mai bine explicată de artefact de metodă (enumerare, tiny-stop, missingness) decât de o relație de corp.
- **NULL / INCONCLUSIVE** — fără asociere materială / CI include nulul.
- **DATA-LIMITED** — neevaluabilă (missingness / clustere prea mici; ex. WP2 după excluderea S1).
- **Regulă:** nicio relație nu poate fi numită *explicativă* sau *cauzală* în P2.

### 7.10 Reguli de oprire și escaladare
Per WP, un pachet: (a) se oprește cu NULL; (b) se oprește DATA-LIMITED; (c) declanșează o problemă de calitate a corpului; (d) produce o întrebare pentru P4; (e) cere date noi (→ Alpha, nu se execută în P2); (f) invalidează pachete ulterioare.
- **Autoritate WP1 (mandat CEO):** dacă WP1 găsește contaminare materială de enumerare / pseudo-replicare, are **autoritatea de a opri sau reproiecta WP2–WP5** (ex. a le re-scopa cluster-aware sau a exclude/ajusta S1) înainte ca acestea să ruleze.

### 7.11 Contract de output (per WP)
Pentru fiecare WP: **nume raport** (RI-META-000X, sau RI-ANOM-000X unde apar contradicții) · tabele/figuri planificate · **registru complet de teste** (inclusiv nule) · limitări · **întrebări P4 în coadă** · **interpretări interzise** (listate explicit per raport).

---

## 8. CLARIFICARE DE GUVERNANȚĂ (mandat CEO)

P2 poate formula **întrebări relaționale înregistrate**. P2 NU poate formula sau valida mecanisme de piață.

| Permis (relațional) | Interzis (mecanism/cauzal) |
|---|---|
| „Concentrarea e ASOCIATĂ cu fragilitatea?" | „Concentrarea CAUZEAZĂ fragilitatea din cauza mecanismului X." |
| „Ipotezele both sunt CONCENTRATE în familii zero-profit." | „Construcția both e INERENT neprofitabilă." |
| „Rata hist_prof a S1 e mai mare — e asociată cu mărimea?" | „S1 e mai bun / privilegiat structural." |

Orice mecanism candidat care se conturează → **logat pentru P4**, nu produs în P2.

---

## 9. DECIZII STATISTICE — REZOLVATE DE CEO (2026-07-21)

1. **Praguri de materialitate:** **AMÂNATE.** Se raportează effect size + CI; CEO interpretează importanța practică ulterior. Nu se aplică un cutoff automat de materialitate.
2. **Motor inferențial:** **APROBAT.** Se prioritizează effect size + robustețe peste p-values acolo unde e potrivit. (CI bootstrap cluster-familie ca primar; fără dependență de motorul sub-validare.)
3. **Granularitatea clusterului:** **FAMILIA.** Fără creșterea complexității de clustering (nu familie×side, nu dataset/config).
4. **Semantica `val_exp`:** **APROBAT** ca „a doua măsură de expectancy" până la o definire formală.
5. **`both`:** **APROBAT.** Exclus din analiza primară; raportat separat dacă e util.
6. **FDR:** se aplică **DOAR** analizelor primare predefinite.

*Fără extindere de protocol suplimentară. Fără documente de guvernanță suplimentare. Obiectivul acum este execuția.*

---

*Sfârșitul planului de execuție P2 (Revizia 1, contract complet, decizii CEO rezolvate). Execution-ready. Nicio analiză relațională efectuată, niciun rezultat P2 produs. P2 rămâne ÎNCHIS până la autorizarea explicită a WP1.*
