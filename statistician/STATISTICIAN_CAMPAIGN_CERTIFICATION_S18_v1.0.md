# STATISTICIAN — CERTIFICARE DE CAMPANIE: SCOPED GLOBAL-FDR, SUPRAVIEȚUITOR S18
### Emisă conform criteriilor pre-înregistrate în `STATISTICIAN_CAMPAIGN_CERTIFICATION_CRITERIA_v1.0.md` (commit `844dc46`, scrise înainte ca rezultatul să existe)

**Document ID:** STAT-CAMPAIGN-CERT-S18-v1.0
**Data:** 2026-07-25 · **Autor:** Statistician
**Autoritate:** Contract Statistician↔Validation Engine v1.1, §5 (certificarea agregată a rezultatelor de campanie).
**Obiect certificat:** `docs/SCOPED_FDR_RESULT_v1.0.md`, supraviețuitorul unic `ce76669a3b2a` (S18, hour=13 UTC, side=down, stop=1.5×ATR, exit=time).
**Verificare independentă înainte de certificare:** am citit direct `SCOPED_FDR_RESULT_v1.0.md`, `NET_CONCENTRATION_INVENTORY_v1.0.md`, `STOP_FLOOR_DIAGNOSTIC_v1.0.md` — toate cifrele raportate mai jos sunt confirmate din artefacte, nu doar acceptate din rezumat.

---

## VERDICT

# CAMPAIGN SURVIVOR — FLAGGED, NOT CERTIFIED

`ce76669a3b2a` trece BH la pragul preînregistrat, cu rezoluție MC adecvată — dar eșuează suficiente verificări din §1 al criteriilor mele proprii încât nu poate fi certificat ca dovadă a unui efect real. Nu e o respingere a ipotezei "există un efect oră-13" ca obiect de cercetare viitoare — e o determinare că ACEST rezultat, așa cum stă acum, nu constituie dovadă certificabilă.

**Converg cu recomandarea Research Lab (FLAGGED-NOT-CERTIFIED), dar independent, pe propriul meu raționament** — exact disciplina pe care am aplicat-o față de Red Team pe tot parcursul acestei sesiuni: recomandarea altcuiva nu e adevăr, se verifică.

---

## Aplicarea criteriilor din §1 (rezultat pozitiv), punct cu punct

| Verificare | Rezultat | Verdict pe punct |
|---|---|---|
| Fidelitate populație/prag/configurație înghețate | m=412, prag 1,214×10⁻⁴, config unstratified+ATR-scaled — toate exact ca preînregistrat | ✅ trece |
| Rezoluție MC adecvată (nu UNRESOLVED) | MC-3, CI95 [5,28×10⁻⁵, 8,51×10⁻⁵] — întreg sub prag | ✅ trece |
| Segment de validare raportat separat, contradicție numită direct | p=0,078, obs +0,0226R (același semn, magnitudine mai mică, sub prag) — **nu confirmă**, dar nici nu contrazice frontal (nu e semn opus) | ⚠️ **nu confirmă la 0,05** — nu blochează singur, dar cântărește greu împreună cu restul |
| Verificare de construcție cunoscută ca fragilă (tiny-stop/D2) | Diagnostic stop-floor: 0% tranzacții lărgite, best-trade nelărgit, risc cerut de strategie (1,5×ATR) | ✅ trece — NU e artefact de podea |
| Trasabilitate completă (manifest, semințe, hash-uri) | Confirmat în tabelul §6 din `SCOPED_FDR_RESULT_v1.0.md` | ✅ trece |

**Până aici, ar putea părea aproape de certificare.** Dar criteriile mele proprii cer și verificarea de fragilitate/robustețe dincolo de tiny-stop — și aici apar motivele reale de refuz:

### Motivul decisiv 1 — semnul se inversează cu regula de ieșire, pe intrări identice

`STOP_FLOOR_DIAGNOSTIC` §7.5 (măsurătoarea pe ieșiri): aceleași 550 intrări, exit `time` dă +0,061R (supraviețuitorul); exit `rr2`, pe EXACT aceleași intrări, dă **−0,071R**, wo1 −0,075. Suprapunere de intrări: 100%. Diferența întreagă vine din regula de ieșire, nu din semnal.

Comparativ, `h20-long` (nu a trecut FDR) e **pozitiv sub AMBELE ieșiri** (+0,177 time, +0,107 rr2), robust la alegerea de ieșire.

**Un efect de timing real n-ar trebui să dispară — și să-și schimbe semnul — doar pentru că alegi o altă regulă de ieșire rezonabilă pe aceleași intrări.** Asta e exact genul de fragilitate pe care criteriile mele cer să fie numită explicit, nu îngropată — și pe care o extind acum, formal, ca parte a verificării de "construcție cunoscută ca fragilă": nu doar tiny-stop, ci și non-robustețe la alegeri de modelare rezonabile pe date identice.

### Motivul decisiv 2 — concentrare pe net de 47,4% dintr-o singură tranzacție

`NET_CONCENTRATION_INVENTORY` §6: net1 = 0,474 — aproape jumătate din tot profitul net al supraviețuitorului vine dintr-o singură tranzacție (+15,88R). Confirmat, prin diagnosticul de stop-floor, că NU e artefact de podea — tranzacția e reală, pe risc cerut de strategie. Dar realitatea tranzacției nu schimbă faptul că e o bază evidențială extrem de subțire pentru o pretenție de "abilitate de timing la nivel de populație".

**Notă obligatorie, pe care o consemnez explicit fiindcă tu ai semnalat-o prima:** eticheta `fragile=False` a supraviețuitorului **nu poate fi folosită ca argument în favoarea lui** — e calculată pe profit brut, iar inventarul de concentrare arată că rateaza sistematic fragilitatea reală (117 din 357 ipoteze etichetate "nefragile" au peste 30% din net dintr-o tranzacție). Cifra care contează e net1=0,474, nu eticheta.

### Motivul decisiv 3 — eșec OOS, în tiparul deja cunoscut al laboratorului

p=0,078 nu confirmă la 0,05. Consistent cu tiparul deja documentat în acest laborator ("edge-urile de research pică OOS"). Nu e, singur, un motiv de respingere definitivă a ipotezei ca obiect de cercetare — dar combinat cu motivele 1 și 2, elimină orice bază pentru certificare acum.

---

## Ce NU schimbă acest verdict

- **D2 rămâne exact unde era** — supraviețuitorul e ortogonal regimului structural (stop 1,5×ATR, nicio legătură cu stopurile structurale), confirmat independent și de diagnosticul de stop-floor. Acest rezultat nu susține și nu infirmă închiderea lui D2.
- **Nu e un verdict STATISTICALLY REJECTED asupra ipotezei "efect oră-13"** ca întrebare de cercetare — e o determinare că ACEST test, cu ACEASTĂ execuție, nu produce dovadă certificabilă. Rămâne deschisă unei viitoare investigații mai bine specificate (ex. testată direct pentru robustețe la regula de ieșire, ÎNAINTE de a rula, nu după).

## Findinguri consemnate, nu rezolvate aici

**Contradicție de criterii a laboratorului însuși:** supraviețuitorul trece FDR global dar `research_worthy=False` (dd=33,4R > pragul de 25R din Discovery Screen V1). Două criterii oficiale, verdicte opuse pe același obiect. Consemnat ca finding de integritate, nu rezolvat — nu e în mandatul acestei certificări.

**Cele 6 ipoteze S18 cu p mic sunt 3 semnale × 2 ieșiri, nu 6 teste independente** (suprapunere de intrări 100% în toate cele 3 perechi, confirmat în §7.5). Nu schimbă certificarea de azi — supraviețuitorul trece la 6,8×10⁻⁵, cu marjă suficientă față de prag chiar dacă m-ul efectiv ar fi mai mic decât 412 din cauza acestei redundanțe. **Dar e un finding metodologic de sine stătător, relevant pentru orice re-analiză viitoare a corpului S1-S51** — dacă familii întregi conțin perechi semnal×ieșire pe intrări identice, numărătoarea lui m=412 tratează teste corelate ca independente, undeva în corp, chiar dacă nu schimbă rezultatul acestui supraviețuitor specific. Semnalez pentru referință viitoare, nu ca acțiune acum.

## Ce ar fi fost necesar pentru CERTIFIED (orientativ, nu o promisiune de rezultat)

Confirmare OOS la prag rezonabil; robustețe la cel puțin cele două reguli de ieșire deja disponibile (time și rr2); și o bază evidențială care nu depinde de o singură tranzacție pentru jumătate din profit. Niciuna din cele trei nu se susține azi.

---

**Nu am modificat rezultatul, parquet-ul, sau holdout-ul (SEALED, neatins). Certificarea e o determinare, nu o execuție.**

**Statistician se oprește aici.**
