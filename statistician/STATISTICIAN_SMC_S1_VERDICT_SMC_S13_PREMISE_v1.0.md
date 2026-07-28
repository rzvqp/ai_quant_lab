# STATISTICIAN — VERDICTUL SMC_S1 ȘI PROBLEMA DE PREMISĂ SMC_S13

**Document ID:** STAT-SMC-S1-VERDICT-S13-PREMISE-v1.0
**Data:** 2026-07-28 · **Autor:** Statistician

**Verificare de sursă:** citit integral `code/lm001_s1_execution.py` (commit `0702958`) și **rulat direct** (worktree `ai_quant_lab-wp5b`, `discovery-mk-matrix-v1`) — cifrele tale reproduse EXACT: n_trades 9.247/7.181/4.614, winrate 0,473/0,4584/0,49, expectancy −0,16771/−0,18447/−0,22336, net_sumR −1.550,825/−1.324,705/−1.030,579, p_wp5 1,0/1,0/0,996. Verificat direct și cele două observații ale tale: cea mai bună tranzacție (netR=50,40) / suma pierderii absolute (3.906,109) = 1,29%, exact. Verificat aritmetica net+cost=gross la toate trei regimurile: −0,1677+0,24=0,0723; −0,1845+0,24=0,0555; −0,2234+0,24=0,0166 — toate confirmă cifrele tale. Verificat direct E004 (`EDGE_DISCOVERY_REGISTRY_v1.md`): „US Market Open First FVG" — același construct (fill de FVG) ca SMC_S13, nu o comparație forțată.

---

## SARCINA 1 — verdictul SMC_S1

**Populație confirmată:** 9.247+7.181+4.614 = 21.042 = 21.048−6 (excluse la marginea orizontului, Q2, deja stabilit).

**Cele două observații ale tale, verificate independent, ambele corecte:**
- **Pierderea e drag de cost, nu fragilitate** — confirmat: cea mai bună tranzacție din tot eșantionul (netR=50,40$) reprezintă doar 1,29% din pierderea absolută totală (3.906,11$). Nu există concentrare — media de −0,1856 R e distribuită pe toate cele 21.042 tranzacții, exact opusul tiparului deja documentat de colaps-la-eliminarea-celei-mai-bune-tranzacții (`NET_CONCENTRATION_INVENTORY`).
- **Edge-ul brut e mic, pozitiv, monoton descrescător** — verificat aritmetic: scăzând fracția de cost (24% din R median) din expectancy-ul net, rezultă +0,072 (bear) / +0,055 (bull) / +0,017 (corecție). Nu e o cifră aleasă — e o consecință mecanică a net+cost=gross, verificabilă de oricine repetă calculul.

**Decizie: DA, merită categorie proprie.** „Semnal fără edge" (rejecție completă, populația nu conține informație) și „edge sub pragul de executabilitate" (semnal real, mecanic dovedit prin descompunere, dar sub costul de execuție) sunt epistemic distincte — a le eticheta identic ar ascunde exact ce ai demonstrat: că strategia NU e zgomot, doar ne-monetizabilă la costul actual.

**Etichetă propusă, cu delimitare de scop (același tipar ca cele 47/22/E001-E002-E004):**

```
SMC_S1 (LM-001): REJECTED_NET_OF_COST

  Domeniu strict al respingerii:
  - se respinge H1: μ_netR > 0, la costul de execuție actual (0,40$ round-trip), pe cele trei
    regimuri M15_v2 discovery, cu construcția Open-R înghețată (stop = spike+2 pips, fără podea,
    filtru [10,1;65,0), orizont 20 bare, ieșire pură pe timp)
  - NU se respinge existența unui edge geometric brut — verificat mecanic, pozitiv, monoton
    descrescător bear->corecție (+0,072/+0,055/+0,017 R), consecință a net+cost=gross, nu a unei
    tranzacții sau unui subset favorizat
  - NU implică ca mecanismul de sweep-reject e fals — implică doar că, la acest cost, nu e
    tranzacționabil
  - se respinge DOAR pentru acest orizont (20 bare) și acest cost; o schimbare fie a costului de
    execuție, fie a construcției de risc, ar cere o re-testare, nu o extrapolare a acestui verdict
```

## SARCINA 2 — domeniul oracolului: confirmat PARȚIAL, cu limite scrise explicit

**Ce se confirmă:** mecanismul de SUPRAPUNERE (ce a fost calibrat la WP-5') se păstrează identic — R-normalizarea și direcția sunt scalari PER-EVENIMENT, independenți de șocurile viitoare care creează suprapunerea; nu schimbă CARE evenimente împart șocuri, doar cum se convertește suma în R. Mecanismul de dependență rămâne cel validat.

**Ce NU s-a testat explicit, semnalat corect de VE:** bateria WP-5' a folosit o serie de rezultate cu variație relativ OMOGENĂ (sumă de șocuri, aceeași unitate pentru tot segmentul). `net_R` introduce heteroschedasticitate reală (R_i variază 1,21$-6,50$ per tranzacție) și schimbări de semn (direcție) NEtestate explicit ca atare în baterie. Asta e un gol metodologic genuin, nu doar o formalitate.

**De ce nu schimbă verdictul de azi:** rezultatul e o NE-respingere COVÂRȘITOARE (p≈1,0/1,0/0,996 — foarte departe de orice prag de decizie), nu o respingere la limită sensibilă la o mică eroare de calibrare. O eventuală polarizare anti-conservatoare (riscul teoretic al metodei) ar face testul MAI PREDISPUS să găsească fals-pozitive (edge unde nu există), nu mai predispus să ASCUNDĂ un edge negativ real — deci un eventual defect rezidual de calibrare ar lucra ÎN DIRECȚIA OPUSĂ concluziei de azi, întărind-o, nu slăbind-o.

**n per regim, verificat cu date deja existente, nu presupunere nouă:** cele trei n de regim (4.614/7.181/9.247) se încadrează în intervalul deja TESTAT prin stratificarea pe sesiune din aceeași baterie WP-5' (Mandatul 3.20): asia n=5.915, london n=5.635, ny n=8.386, late n=1.118 — toate au ieșit nominale. n-ul cel mai mic dintre regimuri (corecție, 4.614) e comparabil cu ny (8.386) și peste late (1.118) — deja acoperit empiric, nu o extrapolare.

**Regulă permanentă, pentru rezultate viitoare din același pipeline:** un rezultat NEGATIV (ca acesta) rămâne robust la acest gol metodologic. **Un rezultat POZITIV din același pipeline NU ar fi la fel de robust** — ar necesita închiderea explicită a golului de heteroschedasticitate (o extensie a bateriei WP-5' cu R_i/direcție reale, nu doar sume omogene) înainte de a fi acceptat ca dovadă. Scris acum, ca regulă de aplicat automat, nu de redecis la fiecare rezultat viitor.

## SARCINA 3 — SMC_S13: premisa e greșită, o formulare validă există

**De acord integral cu diagnosticul.** Verificat direct: E004 („US Market Open First FVG" — același construct FVG-fill) a stabilit deja rata de bază de 85% (banda pre-înregistrată (0,512;0,886), eticheta `OBSERVED_NOT_DISTINCTIVE`, deja ratificată). „85% rată de umplere" NU e un edge descoperit — e rata de bază a ORICĂRUI gap comparabil, stabilită tocmai pentru a preveni această citire. Mai grav, verificat aritmetic (z≈−8,75, consistent cu z=8,8 citat): gap-urile E004 se umplu MAI RAR (71,48%) decât linia de bază, direcție OPUSĂ oricărei pretenții de „exploatare a ratei masive". Ordinul primit citează literal rezultatul controlului ca ipoteză.

**Ce e corect în design, confirmat:** stopul propus (2 pips dincolo de marginea B1, jumătate de gap + amplitudinea B1) e structural mai larg decât cel care a produs pierderea la S1 (14,7 pips median) — cost/R ar scădea semnificativ. Intuiția arhitecturii de risc e bună; justificarea din ordin (rata de 85%) e greșită.

**Cele trei variante:**
1. **Respinsă** — o subpopulație de FVG-uri care se umplu semnificativ MAI des de 85%: E004 e cel mai apropiat precedent testat, și arată exact opusul.
2. **Notă, nu rezolvată acum** — continuare vs. respingere la CE-50: o întrebare genuin diferită, care NU se bazează pe rata de umplere deloc — rămâne o direcție viitoare posibilă, separată, neformulată aici.
3. **Aleasă.** Economia execuției: la rata de bază (nu se pretinde alta), dacă R-ul geometric e favorabil și costul mic relativ la el, expectancy-ul poate fi pozitiv — o afirmație despre GEOMETRIE, nu despre predictibilitate.

**Formularea explicită a ipotezei (varianta 3), cu declarația cerută:**
```
SMC_S13 NU pretinde că FVG-urile se umplu mai des decât rata de bază (85%, deja stabilită la E004).
Ipoteza testează dacă, LA rata de bază necontestată, geometria stopului (spike+2 pips pe amplitudinea
B1) produce net_R > 0 după cost — o întrebare de economie a execuției, nu de predictibilitate a
evenimentului de umplere.
```

## DOUĂ PROBLEME TEHNICE ALE FORMULĂRII

**Problema A — ordinul limită la CE-50, rezolvată prin ÎNLOCUIRE, nu prin regulă de umplere:** decid să NU păstrez ordinul limită. Restul cadrului Open-R (S1-S17) folosește deja next-open la piață exact pentru a evita incertitudinea de umplere pe M15 — inconsecvent să introduc o excepție doar pentru S13. **Intrare: next-open de piață, la bara imediat următoare atingerii de CE-50** (fitil, punctul de consumare D7 deja stabilit la MK-03), nu ordin limită la CE-50 însuși. Elimină problema, nu o gestionează.

**Problema B — orizontul de 12 bare, EROARE de implementare, nu decizie nouă:** confirmat — la Mandatul 3.18 am specificat explicit **SMC_S13 în GRUPA A (20 bare)**, un declanșator PUNCTUAL (atingere CE-50), nu de sesiune. „12 bare" (durata sesiunii `late`) nu a fost niciodată decizia mea pentru S13 — pare o eroare de implementare, aplicând regula Grupei B (durata sesiunii declanșatorului) unei familii care aparține Grupei A. **Reconfirm: orizontul SMC_S13 rămâne 20 bare, Grupa A** — cere corecție în implementare, nu o derivare nouă.

## S10 — rămâne deschis, consemnat, nerezolvat acum

Confirmat: kickback-ul Research Lab (substituția BOS-ca-displacement decuplează magnitudinea de structură — „nu e aproximare, e substituție de ipoteză") e notat, nu rezolvat în acest document. Rămâne pe agenda unui mandat viitor.

---

**Publicat pe `statistician-foundation`. Manifestul se incrementează la v2.7.6, cum a fost instruit, acum că decizia pe SMC_S13 e luată. Holdout SEALED.**
