# STATISTICIAN — VERDICTUL FINAL OBDZ-001 (prima ipoteză compusă)

**Document ID:** STAT-OBDZ001-FINAL-VERDICT-v1.0
**Data:** 2026-07-29 · **Autor:** Statistician

**Verificare de sursă:** citit integral `code/obdz001.py` (comitul `1146124`) și `code/run_obdz001.py` (`0d40212`) — mecanica mașinii de stare, separarea anti-E010 (selecție/măsurare disjuncte prin construcție), și rularea corespund EXACT specificației ratificate `v2.7.11`. `mypy --strict` curat pe `obdz001.py`; `test_obdz001.py` 7/7. **Rulat direct** `code/run_obdz001.py` — TOATE cifrele din tabelul CEO reproduse exact: n=261/194/154; TP1=94/72/58; TP2=69/49/40; BE=20/22/16; SL=158/114/89; plasă=7/2/6; EOD=7/7/3; WR=0,3908/0,4021/0,4026; R mediu=1,71/1,09/1,80; expectancy_R=+0,0122/−0,0400/+0,0845; net_$=+9,26/−7,40/+26,06; best/sumR=0,686/−0,280/0,170; wo1=+1,00/−9,94/+10,81; p_WP5=0,501/0,826/0,186; CI95 identice. Orizontul realizat: mediană 1,0/2,0/2,0, medie 3,39/3,65/3,90, sub-10-bare 236/175/136 (90,4%/90,2%/88,3%) — toate confirmate exact.

---

## SARCINA 1 — verdictul formal

**OBDZ-001 se respinge LA ACEASTĂ PARAMETRIZARE. Mecanismul compus (bias H1/H4 + DemandZone cross-candle + OB nemitigat) NU e infirmat — rămâne NETESTAT ca semnal independent de risc.**

**Eticheta nouă, delimitată explicit (același precedent ca `REJECTED_NET_OF_COST`): `REJECTED_AT_DECLARED_PARAMETRIZATION`.**

```
Domeniu strict al respingerii:
- se respinge H1: μ_netR > 0 pentru construcția EXACTĂ SL=0,7×ATR / TP1=1,4×ATR / TP2=2,1×ATR /
  ieșire parțială 75/25, pe cele trei regimuri M15_v2 discovery (p=0,501/0,826/0,186, family=1)
- NU se respinge existența unei informații direcționale în semnalul compus însuși — pragurile
  SL/TP/parțial au fost DECLARATE ca alegere de proiectare (Mandatul 3.24), nu derivate din vreo
  proprietate statistică a semnalului; un rezultat nul pe o alegere declarată nu e o dovadă
  împotriva semnalului care o poartă
- constatarea mecanică (mai jos) arată CONCRET DE CE această parametrizare specifică eșuează:
  stopul e prea aproape față de amplitudinea unei bare tipice, deci semnalul moare pe stop înainte
  să aibă șansa să se joace — o problemă de CONSTRUCȚIE DE RISC, nu (neapărat) de conținutul
  informațional al declanșatorului
- se respinge DOAR pentru acest orizont/plasă/cost; o construcție de risc diferită (SL/TP mai
  late, cf. Sarcina 4) ar cere o RE-testare cu propria pre-înregistrare, nu o extrapolare a acestui
  verdict
```

## SARCINA 1b — asimetria bear/corecție, semnalată de CEO ca observație proprie: confirmată mecanic, nu schimbă verdictul

Verificat exact: bear best/sumR=0,686 (o SINGURĂ tranzacție = 69% din net), wo1 scade de la +3,19 la +1,00 — colapsul e aproape total, exact tiparul deja documentat la `NET_CONCENTRATION_INVENTORY`. Corecție: best/sumR=0,170 (17%), wo1 rămâne puternic pozitiv (+10,81 din +13,02) — genuin distribuit, nu un artefact de o tranzacție. **De acord: cele două celule pozitive NU sunt echivalente structural** — bear-ul e fragil (un singur eveniment norocos), corecția e un tipar distribuit pe 154 de tranzacții. **Nu schimbă verdictul de mai sus** (niciuna nu respinge H0 la niciun prag rezonabil), dar e o observație corectă de reținut dacă familia OBDZ e vreodată reluată: dacă un rezultat viitor arată edge la corecție, are un precedent structural mai solid decât unul la bear ar avea.

---

## SARCINA 2 — de ce winrate 39-40% (peste pragul meu inițial de 35-37%) dă expectancy ~zero: pragul inițial era GREȘIT, recalculat pe structura REALĂ

**Cauza exactă, din defalcare:** câștigul mediu REAL nu e 2,25R (TP1→TP2 asumat) — doar 69-73% din cei care ating TP1 ajung și la TP2 (bear 69/94=73,4%; bull 49/72=68,1%; corecție 40/58=69,0%); restul se opresc la breakeven (1,5R) sau expiră după TP1 (variabil). Câștigul mediu REALIZAT e o combinație diluată, nu 2,25R fix.

**Recalculat direct din cifrele raportate** (pierderea medie ≈ 1R exact, verificat: fracția SL ≈ 1−winrate în toate cele trei regimuri — bear 60,5% vs 60,9% necesar, bull 58,8% vs 59,8%, corecție 57,8% vs 59,7% — reziduul mic provine din cele câteva tranzacții „plasă"/„EOD" care nu sunt exact −1R, neglijabil ca magnitudine):

```
                        BEAR      BULL     CORECȚIE
câștig mediu REAL (R)   1,59      1,39      1,69       (nu 2,25R asumat)
prag winrate CORECT    38,6%     41,9%     37,1%       (nu 35-37% asumat)
winrate observat       39,1%     40,2%     40,3%
diferență              +0,5pp    −1,7pp    +3,2pp
```

**Asta explică exact tabloul:** bear e marginal peste propriul prag corect (+0,5pp → expectancy ușor pozitivă, +0,0122R); bull e SUB propriul prag (−1,7pp → expectancy negativă, −0,0400R); corecție e confortabil peste (+3,2pp → expectancy clar pozitivă, +0,0845R). **Nu era un paradox — pragul meu inițial (35-37%) presupunea câștigul mediu greșit.** Cu structura reală, cele trei rezultate sunt exact ce te-ai aștepta, nu o anomalie.

**Precizare, nu ascunsă:** acest recalcul e o aproximare (tratează cele ~5-6% tranzacții „plasă"/„EOD" ca având valoare neglijabilă pe partea de pierdere) — suficient de precis pentru interpretare, dar NU înlocuiește testul formal (`mean(net_R)>0`), care rămâne criteriul de decizie, calculat direct pe fiecare tranzacție cu R-ul ei propriu.

---

## SARCINA 3 — domeniul oracolului: L≥H=20 e satisfăcut nominal, dar orizontul REALIZAT (1-2 bare) e mult sub H nominal — întrebare de domeniu, nedecisă, nu schimbă verdictul de azi

**Confirm observația ta, precis:** validarea `block_bootstrap@v1` (Mandatul 3.20) a fost calibrată pe presupunerea că ferestrele de măsurare se pot întinde până la H=20 bare, creând suprapunere reală între evenimente apropiate de această magnitudine. Aici, `L=28≥H=20` e satisfăcut PE HÂRTIE (orizontul NOMINAL/maxim posibil rămâne 20), dar orizontul EFECTIV REALIZAT e 1-2 bare median — mult mai scurt decât scenariul pentru care calibrarea a fost gândită ca worst-case.

**Direcția probabilă a erorii, dacă există una:** un nul calibrat pe o dependență presupusă mai LUNGĂ decât cea reală ar produce, în general, o varianță de reeșantionare MAI MARE decât cea corectă — adică testul ar fi MAI CONSERVATOR (mai greu de respins H0 în ORICE direcție), nu mai permisiv. Dacă asta e corect, p-value-urile reale (sub un nul recalibrat pe dependența EFECTIVĂ de 1-2 bare) ar fi probabil MAI MICI decât cele raportate, nu mai mari — ceea ce ar afecta cel mai mult celula de corecție (p=0,186, cea mai aproape de orice prag).

**Nu schimbă verdictul de azi:** este o întrebare de DOMENIU, nedecisă acum, nu o eroare de rezultat — cere o recalibrare dedicată (analog WP-5' original, dar cu generatorul de nul potrivit la distribuția REALĂ a orizontului realizat, nu la H nominal) înainte de a fi de încredere în ORICE direcție. **Regulă asimetrică, aceeași ca la LM-001:** un rezultat NEGATIV (bear, bull) rămâne robust la această nesiguranță (un nul prea conservator ar fi lucrat ÎMPOTRIVA găsirii unui fals-pozitiv, deci direcția sigură). Corecția (p=0,186, singura celulă unde direcția e ambele pozitivă ȘI relativ apropiată) NU e la fel de robustă — dacă familia OBDZ e reluată vreodată, această recalibrare ar trebui făcută înainte ca orice rezultat de-acolo să fie citat ca dovadă, nu doar presupusă favorabilă.

**Răspuns direct la ultima observație:** da, p=0,186 e calitativ diferit de 0,501/0,826 (un nul mai puțin covârșitor) — dar rămâne confortabil departe de orice prag rezonabil de respingere (~0,05 sau mai strict sub orice corecție de testare multiplă), nu o „aproape-semnificație". Diferența de grad e reală și demnă de notat descriptiv, dar nu schimbă concluzia formală — niciuna din cele trei celule nu respinge H0.

---

## SARCINA 4 — direcția următoare: recomand DIAGNOSTIC înainte de o nouă parametrizare, nu o ghicire directă

**De acord cu diagnosticul mecanic al CEO** (verificat aritmetic): SL=0,7×ATR e sub o singură bară de amplitudine medie — orice bară obișnuită, mișcată integral advers, ar depăși stopul. Un SL de 1,5×ATR cu TP1 la 3,0×ATR ar păstra RR=1:2, dar ar cere o mișcare adversă de peste o bară medie pentru a fi lovit — mecanic plauzibil să reducă rata de stop-out, cu prețul unei pierderi mai mari în dolari per stop și al unei ținte TP1 mai greu de atins (aceleași două forțe opuse, magnitudinea netă necunoscută fără măsurătoare).

**Recomandare de proces, nu un răspuns direct da/nu:** dacă se urmărește, NU se ghicește o a doua pereche de multipli direct — se reutilizează disciplina deja stabilită la `SMC_S1_v2` (Mandatul 5.12/Measurement A): o măsurătoare DIAGNOSTICĂ dedicată (distribuția reală a excursiei adverse/favorabile după declanșatorul OBDZ, înainte de invalidare) cu un prag de decizie PRE-ÎNREGISTRAT înainte ca vreo cifră să existe — nu o a doua alegere liberă de SL/TP testată direct pe aceleași date.

**Familia de corecție, dacă se procedează: family=2 cu OBDZ-001**, exact precedentul SMC_S1/SMC_S1_v2 — aceeași descoperire consumată a doua oară pentru o ipoteză aproape identică (același semnal de intrare, doar scalarea riscului diferă), cu declarație explicită obligatorie. **Fixată ÎNAINTE de orice nouă rulare**, cum a cerut CEO.

**Dacă se decide să NU se continue:** motivul corect nu e „p e prea mare" generic — e că niciuna din cele trei celule nu se apropie de un prag de respingere plauzibil (0,501/0,826/0,186 vs ~0,05), și diagnosticul mecanic (stop prea strâns) oferă deja o explicație completă și verificabilă a rezultatului nul, fără reziduu neexplicat care ar justifica investigație suplimentară doar din curiozitate statistică.

---

## Ce NU s-a făcut

Sigilatul neatins — toată rularea a fost pe cele 130.491 bare de descoperire M15_v2. Rezultatul e CANDIDAT (in-sample), nu confirmare — nici măcar pozitiv statistic la niciun regim, cum a subliniat CEO. Nimic din acest document nu autorizează o nouă rulare a familiei OBDZ — Sarcina 4 rămâne o recomandare de proces, nu o autorizare.

---

**Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.12 (commit `58799fa`, `alpha-automation-v1`) — mypy --strict curat, content_hash reverificat independent (blank-and-rehash), pytest 139/143 trecute (aceleași 4 eșecuri pre-existente).**
