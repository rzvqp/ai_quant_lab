# STATISTICIAN — RATIFICAREA CELOR ȘAPTE DECIZII + PRE-ÎNREGISTRAREA LINIEI STRUCTURALE (Mandat 3.9)

**Document ID:** STAT-MKTSTRUCT-RATIF-PREREG-v1.0
**Data:** 2026-07-28 · **Autor:** Statistician
**Statut:** proiectare/ratificare, nu execuție. Modulele `market_structure.py`/`liquidity_mechanics.py` sunt drafturi de referință, testate doar sintetic, nu în repo — nu le-am citit direct (nu există să le citesc), lucrez pe descrierea celor șapte decizii din mandat. Validation Engine implementează după ratificare; altă divizie verifică conformitatea per `CROSS_VERIFICATION_SPEC`; execuția vine abia după ambele.

---

## PARTEA 1 — RATIFICAREA CELOR ȘAPTE DECIZII

### Corecția de citire — confirmată, nu doar acceptată

8 structuri **în total** (4 blocuri × 2 tipuri de swing), nu 8 per graniță. Diferența schimbă concluzia: 8 per graniță ar fi însemnat 24-32 pierdute, iar costul lui D3 ar fi părut prohibitiv artificial. Confirm citirea ta ca fiind corectă; ordinul pe care l-am primit purta eroarea.

### D1 — Lookahead. RATIFICAT.
Fractal k=2, `confirmed_idx = idx + k`, ruperile folosesc doar swing-uri cu `confirmed_idx < c`. E singura construcție lookahead-safe posibilă pentru un fractal — nu există alternativă de ratificat împotriva ei.

### D2 — Departajare (inegalitate strictă pe ambele laturi). RATIFICAT.
Verificat sintetic corect (vârf unic → 1 swing; platou → 0). **Alternativa (strict stânga, non-strict dreapta) rămâne nemenționată ca implementare, corect** — dacă vreodată se dorește, cere propria ei rulare sintetică de verificare înainte de a înlocui D2, nu o schimbare tacită.

### D4 — Bazinele nu supraviețuiesc unui gol între blocuri. RATIFICAT.
Consecvent cu D3 — dacă bazinul nu poate exista fără o referință care nu traversează carantina, el nu poate nici supraviețui peste ea.

### D5 — Maparea M5→M15 neimplementată. RATIFICAT, cu scop explicit.
**Consecință pentru pre-înregistrare (Partea 2):** linia structurală, așa cum e specificată acum, se testează **exclusiv pe blocurile de descoperire M15_v2** — NU pe M5 — până când (dacă vreodată) o mapare de structură cross-rezoluție funcțională e construită. Nu extind scopul dincolo de ce e implementat.

### D6 — Wick-sweep, integral pe bara curentă. RATIFICAT.
`low[c] < bazin ȘI close[c] > bazin` (simetric pentru rezistență) — fără lookahead, verificabil mecanic pe o singură bară.

### D7 — Bazinul maturat se consumă. RATIFICAT.
**Alternativa (re-armare) rămâne nemenționată ca implementare** — aceeași notă ca la D2: dacă se dorește vreodată, cere propria rulare de verificare, nu o schimbare tacită peste D7 deja ratificat.

### D3 — Reset la graniță de bloc. PRINCIPIU RATIFICAT. Acceptabilitatea de cost — NERATIFICATĂ, în așteptarea măsurătorii.

**Ce ratific acum:** principiul — resetarea la fiecare graniță de bloc, cu primul swing de fiecare tip rămânând `UNCLASSIFIED` — e singura construcție corectă dată arhitectura de carantină deja stabilită (`config/split_manifest.json`). Împrumutarea unei referințe din blocul anterior ar traversa exact banda de carantină pe care restul acestui manifest o protejează. Nu există o alternativă mai sigură de ratificat împotriva ei.

**Ce NU ratific încă:** dacă acest cost e ACCEPTABIL. Estimarea ta e sintetică (16 bare, ambele swing-uri rămân `UNCLASSIFIED`, deci zero bazine) — un exemplu prea mic pentru a spune ceva despre densitatea reală de swing-uri pe blocurile de descoperire reale. **Nu ratific D3 pe cifra ta, exact cum ai cerut.**

**Măsurătoarea cerută, specificată precis, executabilă fără alte clarificări:**

Pentru fiecare bloc de descoperire (M15_v2, segmentele 1-3 din `STATISTICIAN_H1_PREREGISTRATION_PROTOCOL_v1.0.md`/manifest, plus intervalul moștenit de la M15 — NU segmentul 2022-2026, exclus ca `SAME-WINDOW-RESAMPLED`), rulează detectorul k=2 (D1/D2) și raportează:
1. Numărul total de swing-uri detectate (high + low, separat).
2. Câte rămân `UNCLASSIFIED` (ar trebui să fie exact 2 per bloc — primul de fiecare tip — cu excepția blocurilor cu zero swing-uri de un tip).
3. **Fereastra oarbă**: numărul de bare de la începutul barelor de descoperire ale blocului până la prima structură CLASIFICATĂ (primul swing, de orice tip, care NU e primul-de-tip) — raportată atât ca număr absolut de bare, CÂT ȘI ca procent din numărul de bare de descoperire al acelui bloc (blocurile diferă enorm ca mărime — un număr absolut singur ar înșela).

**Prag de decizie, fixat acum, înainte de rezultat:**
- Fereastră oarbă ≤ **1%** din barele de descoperire ale blocului → D3 ratificat ca cost scăzut, fără condiții suplimentare.
- Fereastră oarbă **1-5%** → D3 ratificat, DAR cu dezvăluire obligatorie per bloc în orice ipoteză care folosește acest detector (fracția exactă de date "oarbă" trebuie raportată alături de orice rezultat).
- Fereastră oarbă **> 5%** → D3 NU se ratifică ca fiind acceptabil în forma actuală — necesită reproiectare (ex. reconsiderarea lui k, sau un mecanism de bootstrap al referinței care nu traversează carantina altfel) înainte de a fi folosit pe date reale.

**De ce procent din bloc, nu bare absolute:** blocurile variază de la câteva zeci de zile la mii de zile — o cifră absolută de "câteva sute de bare" ar fi neglijabilă pe un bloc mare și catastrofală pe unul mic. Procentul normalizează corect.

---

## PARTEA 2 — PRE-ÎNREGISTRAREA

### Obiecția de denumire — susținută, nume ales

**Nu `E001_v2_Wick_Sweep_Execution`.** E001 a fost respins la parametrizarea lui specifică (sweep al extremei Asia, reversal la London Open, fereastră orară, clauză de sesiune) — un detector generic de wick-sweep pe orice bazin, orice sesiune, fără fereastră, e o ipoteză structural MAI LARGĂ, nu o revizuire a aceleiași. Numirea `_v2` ar sugera o resuscitare — exact ce am evitat explicit la cele 47 și la cele trei edge-uri respinse.

**Nume ales: `LM-001` (Liquidity Basin Wick-Sweep-Reject).** Prefix nou (`LM` = liquidity mechanics), în afara spațiului deja folosit E0xx (rezervat integral celor 40 V0 originale) și S0xx (S1-S51). **Proveniență, consemnată explicit, nu ca versiune:** mecanismul conceptual (sweep al unui nivel, urmat de respingere) e înrudit cu E001 — dar populația, definiția bazinului, și absența oricărei restricții de sesiune/fereastră fac din LM-001 o ipoteză nouă, cu propria evaluare completă de la zero, nu o continuare a uneia respinse.

### 1. Definiția detectorului

- **k=2**, fractal swing, `confirmed_idx = idx+2` (D1).
- **Departajare:** inegalitate strictă pe ambele laturi (D2) — o egalitate nu produce swing.
- **Tratamentul granițelor:** reset complet al mașinii de stare la fiecare graniță de bloc de descoperire; primul swing de fiecare tip per bloc = `UNCLASSIFIED`, fără referință împrumutată din blocul anterior (D3, principiu ratificat mai sus); bazinele nu supraviețuiesc golului dintre blocuri (D4).
- **Scop de rezoluție:** M15_v2, blocurile de descoperire (D5) — NU M5, până la o mapare de structură funcțională.

### 2. Definiția bazinului și semnătura de maturare

Bazin = nivel de preț stabilit de o structură CLASIFICATĂ (swing comparabil cu precedentul de același tip). **Semnătura de maturare (wick-sweep), integral pe bara curentă c, fără lookahead (D6):** pentru un bazin de suport, `low[c] < bazin ȘI close[c] > bazin`; simetric pentru un bazin de rezistență. **Bazinul maturat se consumă (D7)** — o singură maturare per bazin, nu se rearmează.

**Notă de transparență:** mecanica exactă de construcție a nivelului de bazin (care swing anume devine "bazinul" activ, cum se actualizează pe măsură ce apar structuri noi) e definită în modulele de referință, pe care nu le-am citit direct (draft, nu în repo). Această pre-înregistrare specifică regulile de INTRARE/IEȘIRE/TESTARE STATISTICĂ peste acea mecanică deja descrisă de cele șapte decizii — nu redefinesc mecanica bazinului.

### 3. Stratul de execuție

- **Intrare:** la deschiderea barei imediat următoare barei de maturare (bara c din D6) — direcție determinată de tipul bazinului matur (suport maturat = respingere bullish = LONG; rezistență maturată = SHORT). Aceeași convenție `entry@next-open`, lookahead-safe, deja stabilită — nu se intră pe bara de rezultat.
- **Stop:** oficial 40 pips = 4,00 dolari; variantă de senzitivitate 50 pips = 5,00 dolari (același rol V-A/V-B, nu test separat).
- **Țintă:** RR 1:1,5 și RR 1:2, raportate separat, niciodată combinate:

| Stop | RR 1:1,5 (țintă) | RR 1:2 (țintă) |
|---|---|---|
| 4,00 (oficial) | **6,00** | **8,00** |
| 5,00 (senzitivitate) | **7,50** | **10,00** |

- **Cost:** `cost_round_trip = 0,40`, aplicat identic, net-of-cost R.
- **Tie-break same-bar:** convenția implicită worst-case (stop-first), cu bracket obligatoriu worst/best pentru orice combinație a cărei stare depinde calitativ de tratament (§7c din `STATISTICIAN_M5_INDETERMINACY_THRESHOLD_SPEC_v1.0.md`, aplicat identic).

### 4. Familia și corecția de testare multiplă

**Doi membri: 1 detector × 2 RR = 2.** Nu patru (direcția long/short nu e o alegere liberă testată separat — e determinată mecanic de tipul bazinului matur, nu un parametru ales, deci nu multiplică familia). Stopul de 5,00 rămâne senzitivitate, nu membru al familiei — consecvent cu tratamentul deja stabilit la SS9.4.1.

**Test:** binomial exact one-sided, ratificat la §7 (`STATISTICIAN_EXECUTION_CONTRACT_STRUCTURAL_V1_v1.0.md`), contra pragului de break-even ajustat la cost (`w*=(1+cost/S)/(RR+1)`, tabelul de mai sus), numărători puși laolaltă peste regimurile testate (regim = defalcare descriptivă, nu multiplicator). BH-FDR la α=0,05 peste familia de 2.

**Regimuri testate:** aceleași 3 (bear/bull/correction, descoperire M15_v2) — regimul 2022-2026 exclus, `SAME-WINDOW-RESAMPLED`, consecvent cu tot ce s-a stabilit deja.

### 5. Criteriul de succes și eșec — scris ÎNAINTE de rulare

- **Succes (per membru RR):** trece BH-FDR la α=0,05 peste familia de 2, pe numărătorii puși laolaltă peste regimurile ELIGIBILE (vezi §6 mai jos pentru ce înseamnă eligibil).
- **Eșec:** nu trece BH-FDR, CU condiția ca cel puțin un regim să fi avut n suficient (§6) — un eșec pe date insuficiente nu e un eșec statistic, e o altă categorie (vezi mai jos).

### 6. Ce se întâmplă dacă detectorul produce prea puține evenimente într-un regim — regula scrisă ACUM

**Prag minim, reutilizare disclosed a convenției deja stabilite în laborator (Discovery Screen V1, poarta de profitabilitate a leaderboard-ului de persistență): n≥25 tranzacții calificate.**

- **Per regim:** dacă un regim produce sub 25 de evenimente calificate (din cauza ferestrei oarbe D3 combinată cu densitatea joasă de bazine în acel bloc), acel regim se marchează `INSUFFICIENT_N` pentru acea combinație — **exclus din numărătorul pus laolaltă pentru acel regim specific, NU tratat ca zero sau ca eșec.** Fracția exclusă se raportează explicit (`denominator_always_reported`, deja în registru).
- **Pooled (peste toate regimurile eligibile):** dacă, după excluderea regimurilor `INSUFFICIENT_N`, n-ul total pus laolaltă tot e sub 25, întregul membru RR primește verdictul **`TESTABLE BUT INSUFFICIENT EVIDENCE`** (vocabularul deja stabilit, ex. DC-0004) — **NU `REJECTED`.** Absența dovezii nu e dovada absenței — un detector rar nu înseamnă un edge fals, înseamnă o ipoteză netestată la această densitate.
- **Dacă AMBELE RR ale familiei ajung `TESTABLE BUT INSUFFICIENT EVIDENCE`:** întreaga linie LM-001 primește acest verdict, cu fereastra oarbă D3 consemnată explicit ca motiv principal probabil, nu ascunsă.

---

## CE URMEAZĂ, CONFIRMAT

Validation Engine implementează modulele DUPĂ ratificarea de mai sus. O altă divizie (nu producătorul) verifică conformitatea per `CROSS_VERIFICATION_SPEC`. Execuția pe date reale așteaptă AMBELE — nu se declanșează de acest document. Măsurătoarea D3 cerută mai sus e o precondiție separată, nu blocată de acest lanț, dar D3 nu e complet ratificat (doar principiul) până nu sosește.

**Nu am scris cod, nu am atins date, nu am ratificat module pe care nu le-am văzut. Statistician se oprește aici.**
