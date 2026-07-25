# STATISTICIAN — CRITERII DE CERTIFICARE A REZULTATELOR DE CAMPANIE
### Scrise ÎNAINTE ca rezultatul FDR să existe

**Document ID:** STAT-CAMPAIGN-CERT-CRITERIA-v1.0
**Data:** 2026-07-25 · **Autor:** Statistician
**Autoritate:** Contract Statistician↔Validation Engine v1.1, §5 (certificarea agregată a rezultatelor de campanie).
**Statut:** Precondiție operațională pentru §5. Comis **înainte** de orice p-value din campania FDR scopată (`ea36005`) — verificat direct: niciun fișier de rezultat (`SCOPED_FDR_RESULT*`, `scoped_fdr_research*`, `scoped_fdr_summary*`) nu există în niciun branch local sau remote la ora acestui commit. Scris acum, ca un contract, exact disciplina pe care o impun altora la pre-înregistrare — dacă aș scrie asta după ce văd rezultatul, criteriile ar fi modelate de el.

---

## 1. Ce verific la un rezultat POZITIV (unul sau mai multe supraviețuitori)

**Dovezi cerute înainte de certificare, toate, nu unele:**

1. **Fidelitate față de preînregistrare** — supraviețuitorul(ii) provin din populația exactă înghețată în `subset_prereg_enumeration.json` (412 id-uri), testați la exact pragul BH preînregistrat (0,05/412 = 1,2136×10⁻⁴), în configurația exact validată (unstratified + ATR-scaled). Orice abatere — populație extinsă/redusă, prag ajustat, configurație schimbată — anulează certificarea, indiferent de cifre (vezi §3).
2. **Rezoluție MC adecvată** — p-ul supraviețuitorului a fost confirmat la MC-3 (B≥1.000.000), cu intervalul Wilson **sub** pragul BH aplicabil rangului său, nu doar o estimare la B mic care se întâmplă să pară semnificativă. Un candidat cu CI care intersectează pragul rămâne UNRESOLVED — nu se certifică, nu se respinge.
3. **Segmentul de validare (OOS 20%) raportat separat și examinat** — nu cer ca validarea să treacă propriul ei BH (pre-înregistrarea nu cere asta, și aș introduce o poartă nedeclarată dacă aș cere-o acum). Cer însă ca rezultatul de validare să fie **raportat explicit alături de supraviețuitor, niciodată omis**, și ca o contradicție puternică (semn opus, p mare) să fie **numită direct în certificare**, nu îngropată. Un supraviețuitor cu validare puternic contrară primește certificare de tip "raportat, nu susținut de al doilea eșantion" — nu tăcere.
4. **Verificare de fragilitate cunoscută** — supraviețuitorul nu aparține unei construcții deja semnalată ca fragilă în lab (ex. tiny-stop/D2-adiacent, chiar dacă nominal ATR-stop — vezi pilotul 2026-07-13, S6-extreme). Dacă aparține, se certifică cu acest avertisment atașat explicit, nu implicit.
5. **Trasabilitate completă** — manifest de execuție, semințe RNG, hash-uri de date și cod, conform §8 din formatul deja cerut Validation Engine (extins acum la Research Lab prin Contract v1.1 §5).

**Ce m-ar face să refuz certificarea unui rezultat pozitiv:**
- Orice deviere de la populația/pragul/configurația înghețate, oricât de "mai bun" ar părea rezultatul rezultat din ea.
- Un candidat raportat drept "supraviețuitor" cât timp propriul CI intersectează pragul (încălcarea regulii proprii de UNRESOLVED din preînregistrare).
- Lipsa artefactelor de reproductibilitate (semințe, manifest).
- Orice dovadă de extindere a universului sau re-rulare după vederea rezultatelor.
- Folosirea configurației stratificate (nevalidată) pentru a obține sau confirma un supraviețuitor.

## 2. Ce verific la un rezultat NUL

**Un rezultat nul NU e certificabil ca informativ fără analiza de putere la pragul real deja finalizată și raportată alături de el** (`STATISTICIAN_POWER_ANALYSIS_SPEC_BH_THRESHOLD_v1.0.md`) — aceasta e precondiția pe care CEO tocmai a impus-o Research Lab, și o fac aici explicit parte din criteriile de certificare, nu doar o recomandare separată.

**Cum disting "nu există efect" de "nu am avut putere să-l văd":** prin mărimea minimă detectabilă (MDES) la putere convențională 80%, calculată la pragul real (1,2136×10⁻⁴), raportată pentru fiecare nivel de frecvență prezent în cele 412. Regula:

- **Dacă MDES la 80% putere e la sau sub intervalul de mărimi de efect plauzibile pentru acest corp** (stabilit de Research Lab/Alpha din rezultatele istorice de backtest, nu inventat de mine) → rezultatul nul e **certificabil ca informativ**: domeniul testat, la acest prag, nu conține un edge detectabil de mărime practic plauzibilă.
- **Dacă MDES la 80% putere depășește semnificativ mărimile plauzibile** → rezultatul nul e **certificat ca neinformativ / subalimentat** — nu distinge absența efectului de absența capacității de detecție, și nu poate fi folosit pentru a închide domeniul.
- **Prag pe care îl impun:** putere ≥80% la mărimea de efect plauzibilă e minimul pentru "informativ". Sub asta, indiferent de cât de aproape (ex. 60-79%), certific explicit ca "putere parțială — informativ doar pentru efecte mai mari decât [X]", nu ca null complet.

**Cerințe suplimentare pentru un nul certificabil:**
- Toate cele 412 trebuie să aibă un status rezolvat (respins/nu-respins la MC-3) — dacă un subset rămâne UNRESOLVED, rezultatul nu e "nul curat", e "nul printre cele rezolvate, X în așteptare printre cele nerezolvate" — se certifică cu acea nuanță, nu simplificat la zero.
- Nulul se certifică **exclusiv** pentru cele 412 (vezi §3) — niciodată extins la universul mai larg.

## 3. Ce NU certific niciodată, indiferent de rezultat — domeniul de valabilitate

- **Cele 1.532 ipoteze cu stop structural (regimul D2)** — complet în afara domeniului, netestate, indiferent de rezultatul celor 412. Un nul aici nu spune nimic despre ele.
- **Cele 12 ipoteze cu stop `ema`** — regim ambiguu, exclus, niciodată certificat.
- **Cele 16 ipoteze ATR-stop dar n<25** — ineligibile, fără p fabricat, niciodată certificate.
- **Configurația stratificată (session×vol)** — nevalidată; orice rezultat obținut sub ea, indiferent de semn, nu se certifică.
- **Orice atingere a holdout-ului sigilat** — dacă holdout-ul e vreodată accesat pentru această campanie, refuz certificarea a tot ce vine după acel punct, exact ca la DC-0004: o resursă arsă nu se poate re-arde curat.
- **Orice combinare a p-ului de research cu cel de validare într-un singur număr** — interzis explicit de preînregistrare (§5); dacă cineva o face, refuz certificarea rezultatului combinat.
- **Generalizarea dincolo de domeniul strict validat:** instrument XAUUSD/OANDA, motor `mstrat.simulate` v2, regim de stop exact 1,5×ATR, fereastra de cercetare (primele 60%, pre-holdout). Orice extrapolare la alt instrument, alt motor, alt multiplu de stop, sau la fereastra de validare/holdout ca și cum ar fi echivalentă cu cercetarea — nu se certifică.

## 4. Forma verdictului

**Vocabularul de 5 verdicte din Constituție (NOT TESTABLE / TESTABLE BUT INSUFFICIENT EVIDENCE / READY FOR STATISTICAL VALIDATION / STATISTICALLY REJECTED / STATISTICALLY ROBUST) NU se potrivește direct** — a fost proiectat pentru o ipoteză unică, narativă, descoperită discreționar, nu pentru un rezultat agregat peste un subset dintr-o gramatică combinatorie, cu propria despărțire research/validare și propria analiză de putere. Îl păstrez ca referință conceptuală, dar propun un vocabular distinct, pentru certificarea de campanie:

| Verdict de campanie | Corespondent conceptual DC | Când se aplică |
|---|---|---|
| **CAMPAIGN NULL — ADEQUATELY POWERED** | ≈ STATISTICALLY REJECTED | Zero supraviețuitori BH; MDES la 80% putere ≤ mărimile plauzibile; toate 412 rezolvate. |
| **CAMPAIGN NULL — UNDERPOWERED** | ≈ TESTABLE BUT INSUFFICIENT EVIDENCE | Zero supraviețuitori, dar MDES la 80% putere depășește ce e plauzibil — neinformativ. |
| **CAMPAIGN SURVIVOR — CERTIFIED** | ≈ STATISTICALLY ROBUST | Trece toate verificările de la §1. |
| **CAMPAIGN SURVIVOR — FLAGGED, NOT CERTIFIED** | (categorie nouă, fără corespondent direct) | Trece BH nominal dar eșuează una din verificările §1 (validare puternic contrară, rezoluție MC inadecvată, construcție fragilă cunoscută) — raportat, nu certificat ca dovadă. |
| **PROCEDURAL VIOLATION — NOT CERTIFIABLE** | (categorie nouă, fără corespondent direct) | Orice deviere de la populație/prag/configurație/segregare research-validare/holdout — refuz indiferent de cifre. |
| **UNRESOLVED** | (fără corespondent — la DC nu există echivalent explicit) | Subset rămas cu CI peste prag după MC-3; raportat ca atare, verdict amânat. |

Cele două categorii noi ("FLAGGED, NOT CERTIFIED" și "PROCEDURAL VIOLATION") nu au corespondent la nivel de DC pentru că natura mecanică, combinatorie a ipotezelor de campanie creează un risc pe care o ipoteză descoperită discreționar nu-l are în aceeași măsură: posibilitatea ca o abatere procedurală minoră (prag, configurație, populație) să treacă neobservată peste 412 teste simultane, mult mai ușor decât la un singur candidat analizat integral. Le tratez ca verdicte de sine stătătoare, nu ca note.

---

**Nu am modificat pre-înregistrarea, codul, sau rezultatele Research Lab. Acest document guvernează certificarea mea, nu execuția lor.**

**Statistician se oprește aici. Cele trei pachete (DC-0008, DC-0003, DC-0004) rămân în așteptare — nimic nu începe pe ele.**
