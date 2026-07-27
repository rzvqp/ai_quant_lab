# STATISTICIAN — RESPINGEREA EXCEPȚIEI PENTRU `block_bootstrap@v1` (E015-V1)

**Document ID:** STAT-BLOCKBOOT-DENIAL-v1.0
**Data:** 2026-07-27 · **Autor:** Statistician
**Obiect:** cererea CEO de a evalua dacă executarea `block_bootstrap@v1` (UNVALIDATED) pentru E015-V1 e legitimă pe motivul că rolul lui aici e de **corecție** (reduce o afirmație), nu de **susținere** (o sporește), spre deosebire de DC-0008.

---

## VERDICT

**Argumentul nu se susține ca excepție categorică. E015-V1 rămâne SUSPENDAT. Executarea nu e legitimă pe nicio cale — nici Validation Engine sub Contract, nici Flow A informal.**

## Verificare independentă a faptelor înainte de verdict

- `PROJECT_AUDIT.md:23`: *"Block bootstrap (Test A robustness): well-calibrated on 2 synthetic controls; METHOD UNDER VALIDATION (needs full battery)."* — confirmat citind fișierul direct.
- `validation_engine/capabilities.json` (VE-CAPREG-v1.6): `block_bootstrap@v1.calibration_status = "UNVALIDATED"`, `acceptance_suites: [S1, S3, S4, S8]`. Regula registrului: `"unvalidated_not_executable": "A method whose calibration_status is not VALIDATED cannot be referenced by an official specification."` — confirmat citind fișierul direct.
- Precedentul DC-0008 (`validation_engine/clarifications/CLARIFICATION_DC-0008_G6_and_unvalidated_methods.md`, punctul 2): VE a refuzat execuția tocmai pe baza acestei reguli, formulată fără nicio condiționare de direcție a rezultatului — regula nu spune "cu excepția metodelor care doar corectează în jos".

## De ce argumentul CEO nu se susține

Argumentul cere ca "UNVALIDATED" să implice totuși o proprietate cunoscută: că eroarea de calibrare, oricare ar fi ea, nu poate merge decât într-o singură direcție (spre a mări p, niciodată spre a-l micșora artificial). Aceasta e exact ceea ce **"needs full battery"** înseamnă că NU știm încă.

1. **"Corectează doar în jos" e o presupunere despre direcția erorii de calibrare, nu o proprietate demonstrată a implementării.** Dacă `block_length` e prost ales pentru regimul specific al lui E015 (autocorelație, dimensiune eșantion, structura cozilor — niciuna verificată de cele 2 controale sintetice trecute până acum), rezultatul plauzibil al unei subcorectări este un p care rămâne artificial de mic — adică exact "confirmarea" pe care argumentul o declară imposibilă. Metoda nu trebuie să fabrice un rezultat pozitiv "din nimic" pentru ca eroarea să fie periculoasă în sensul cerut aici; îi e suficient să nu reducă suficient un p deja umflat.
2. **"2 controale sintetice trecute" nu stabilește o garanție de conservatorism universal** — stabilește doar că metoda s-a comportat corect în acele 2 regimuri. Bateria S1/S3/S4/S8 există exact pentru regimurile ne-testate încă, care ar putea include structura specifică relevantă pentru E015.
3. **O "dizolvare" falsă e tot o eroare cu cost, nu un rezultat sigur din oficiu.** Dacă metoda supra-corectează (ex. `block_length` prea mare, pierdere de putere), poate ucide pe nedrept ultima ipoteză vie a programului de edge-uri pe baza unei corecții defecte — o pierdere reală, doar de tip opus. Argumentul "poate doar să facă rău într-o direcție sigură" ignoră acest cost.
4. **Regula registrului e formulată la nivel de metodă, nu la nivel de scop declarat al execuției.** Ea nu distinge "execuție care susține" de "execuție care corectează" — distincția aceasta nu există în text și introducerea ei acum ar fi o excepție creată ad-hoc, exact tipul de gaură pe care disciplina de pre-înregistrare a acestui laborator o interzice.

## Portița — închisă, indiferent de cine execută

Flow A nu e semnatar al Contractului Statistician↔Validation Engine, deci regula `unvalidated_not_executable` nu i se aplică formal pe acea cale. Dar regula există la nivelul **registrului de capabilități** (`VE-CAPREG`), nu la nivelul contractului unei singure divizii — ea guvernează ce metode pot produce dovadă oficială în acest laborator, indiferent cine apasă butonul de execuție. Recomand formalizarea explicită a acestui punct (extinderea `unvalidated_not_executable` ca regulă de guvernanță la nivel de laborator, nu doar de Contract Statistician↔VE), astfel încât nicio divizie viitoare să nu poată executa o metodă UNVALIDATED doar pentru că nu e semnatară a contractului care o interzice pe altă cale. Aceasta închide exact gaura pe care ai semnalat-o, fără să depind de cine e sub ce contract.

## Ce rămâne valabil

- **E015-V1 rămâne SUSPENDAT** — nicio recalculare nu se execută până când `block_bootstrap@v1` trece bateria S1/S3/S4/S8 și devine VALIDATED (același drum ca `matched_null@v1` și `bonferroni@v1`).
- **Recomand un al doilea program de tip F6** pentru validarea `block_bootstrap@v1`, dacă laboratorul dorește să deblocheze E015-V1 — aceasta e o decizie de prioritizare a CEO, nu ceva ce autorizez sau execut eu.
- Nu am modificat nicio specificație, nu am executat nimic. **Statistician se oprește aici.**
