# STATISTICIAN — CELE PATRU CONDIȚII DE RATIFICARE ALE MOTORULUI DE DECIZIE

**Document ID:** STAT-DECISION-ENGINE-RATIFICATION-CONDITIONS-v1.0
**Data:** 2026-08-04 · **Autor:** Statistician
**Închide:** condițiile 1-4 din ratificarea CEO (pas 4/4) pe RT-CODE-A-0008.

**O măsurătoare nouă, proprie, P&L-oarbă** (130.474 tranziții de bară). **A doua consemnare — plafonul de −1R — nu rămâne o limitare deschisă: se poate mărgini ACUM, și se închide mai jos.**

---

# CONDIȚIA 1 — FIȘA-UMBRĂ PE TOATE SETUP-URILE

**Bucla găsită de Red Team e o cenzură pe rezultatul propriei porți: blocat ⇒ nu tranzacționează ⇒ nu acumulează ⇒ blocat.** Nu se rupe prin relaxarea porții — se rupe schimbând SURSA numărătorilor.

## Regula, obligatorie

```
Se înregistrează o FIȘĂ-UMBRĂ pentru FIECARE declanșare de setup, indiferent de decizie
și indiferent de MOTIVUL refuzului (fezabilitate, EV, filtru dur, input lipsă).

Ce conține:  setup_id, celula de ierarhie, as_of (bara de declanșare),
             R, RR, rezultatul barierei, resolved_at (bara la care s-a decis rezultatul)
Ce NU conține: P&L, cost, slippage — bariera e o întrebare de TRAIECTORIE, nu de execuție.
```

**Excluderea unui singur motiv de refuz reface bucla pentru acel motiv. De aceea „toate" e literal.**

## Condiția fără de care amestecarea umbră/executat e nelegitimă

**Umbrele nu suferă niciodată o execuție reală, deci ar arăta sistematic mai bine decât cele executate — dacă rezultatul lor s-ar rezolva optimist.**

```
OBLIGATORIU: rezolvarea barierei folosește IDENTIC convenția S1 de caz cel mai rău
             (STOP > TIME-STOP > ȚINTĂ la coliziune intrabar).
```

> **Cu regulă de rezolvare identică, `p_t` e o proprietate a TRAIECTORIEI DE PREȚ, iar traiectoria e aceeași pentru o tranzacție executată și pentru una refuzată. Asta le face SCHIMBABILE, deci agregabile.** Nu e o presupunere de conveniență — e o consecință a faptului că bariera nu depinde de execuție. **Iar dacă regula de rezolvare diferă între cele două surse, argumentul cade și agregarea devine nevalidă.**

**Verificare care poate INFIRMA agregarea, obligatorie periodic:** `p_t` calculat separat pe subsetul EXECUTAT și pe cel UMBRĂ, în aceleași celule cu n suficient. **Divergență materială ⇒ regula de rezolvare nu e identică ⇒ se oprește agregarea și se caută defectul.** Nu presupun schimbabilitatea; o las măsurabilă.

**Volumul nu e o obiecție:** un candidat poate declanșa zeci de mii de ori (CAND-0020: 34.006). Sunt înregistrări, nu execuții.

---

# CONDIȚIA 2 — GARANȚIA AS-OF-DECIZIE

## Subtilitatea care decide totul: contează `resolved_at`, nu `as_of`

**O tranzacție INTRATĂ înainte de bara `j` dar încă DESCHISĂ la `j` nu are încă rezultat. A o include înseamnă lookahead.**

```
Tabela folosită la decizia de la bara j include EXCLUSIV fișele cu  resolved_at < j.
NU `as_of < j`. Rezultatul, nu declanșarea.
```

**E exact distincția `available_idx` vs `formed_idx` din primitivele deja ratificate (D1/Q4) — reutilizată, nu inventată.**

## Cum se garantează: prin construcție, apoi prin audit, apoi prin test

```
1. CONSTRUCȚIE   constructorul de tabelă cere `as_of` ca ARGUMENT OBLIGATORIU și filtrează
                 el însuși. NU există tabelă globală mutabilă pe care motorul „o citește".
                 Motorul îi pasează propriul timestamp de bară. Lookahead-ul devine
                 inexprimabil, nu doar interzis.
2. AUDIT         fiecare decizie loghează `decision_ts` ȘI `table_cutoff_ts`.
                 Aserțiune de audit: `table_cutoff_ts <= decision_ts` pe FIECARE decizie.
3. TEST          se construiește tabela la t; se adaugă o fișă cu `resolved_at >= t`;
                 se asertează că tabela NU se schimbă.
```

## Calea pe care nimeni n-ar verifica-o: `k`

> **`k` se estimează din varianța ÎNTRE celule, adică pe TOATĂ tabela. Dacă e estimat o dată, pe toate datele, lookahead-ul intră prin hiperparametru chiar dacă numărătorile sunt curate.**

```
OBLIGATORIU: k = k(as_of), estimat pe exact aceeași mulțime filtrată. Se loghează cu decizia.
```

**Garanția as-of acoperă hiperparametrul, nu doar numărătorile. Altfel e o ușă lăsată deschisă în spatele uneia încuiate.**

---

# CONDIȚIA 3 — SCHEMA HASH-UITĂ

**Red Team are dreptate că adâncirea oportunistă se auto-blochează prin interval lat. Dar asta apără împotriva EROARII DE EȘANTIONARE, nu împotriva ALEGERII DE STRUCTURĂ** — iar la n mare intervalul e îngust în jurul unei cifre care poate fi greșită din alt motiv.

```
schema_hash  ACOPERĂ:  lista ORDONATĂ a nivelurilor; numele descriptorului fiecărui nivel;
                       regula lui de discretizare/încadrare; maparea părinte-copil;
                       versiunea codului care le calculează.
             NU acoperă: numărătorile (acelea sunt `prob_table_hash`) și `k` (e derivat).
```

**Două hash-uri, două scopuri, niciodată amestecate — aceeași disciplină ca cele două registre de familie.**

## Hash-ul dovedește IDENTITATE. Pre-înregistrarea cere altceva.

> **Un hash nu dovedește că schema a existat ÎNAINTE de date — dovedește doar că nu s-a schimbat de atunci. Pre-înregistrarea are nevoie de o autoritate de timp.**

```
Schema se ÎNREGISTREAZĂ în split_manifest.json ÎNAINTE de orice decizie care o folosește.
Auditul devine: pentru fiecare decizie, `schema_hash` aparține unei scheme înregistrate
într-o versiune de manifest al cărei COMMIT precedă `decision_ts`.
Istoricul git al manifestului E autoritatea de timp. Nu se construiește un registru nou.
```

**Regula de modificare, și e monotonă ca familia:** o schemă nu se EDITEAZĂ, se ADAUGĂ. O versiune nouă de manifest, un hash nou; deciziile vechi păstrează hash-ul vechi. **Lista de scheme e append-only.** O editare în loc ar rescrie retroactiv ce s-a pre-înregistrat, adică exact ce se apără aici.

---

# CONDIȚIA 4 — TESTUL LIPSĂ

**Cerut lui VE. Dar îl generalizez, pentru că 0,5 la μ=0, n=0 nu e un caz — e o CLASĂ.**

## De ce tocmai 0,5 e valoarea periculoasă

> **O degenerare care returnează `NaN` e prinsă la prima rulare. Una care returnează un număr PLAUZIBIL trece neobservată — iar 0,5 e cea mai plauzibilă valoare pe care o poate produce un estimator de probabilitate.** Asta o face mai gravă decât o excepție, nu mai puțin gravă.

## Bateria cerută — tabel de frontieră, nu un singur test

```
μ_părinte    n_celulă   p_celulă      așteptat
   0            0          —          p̂_t == 0 (EXACT părintele). NICIODATĂ 0,5.
   1            0          —          p̂_t == 1 (EXACT părintele). NICIODATĂ 0,5.
   orice        >0         0          definit, fără fabricare
   orice        >0         1          definit, fără fabricare
   k → 0        oricare    —          p̂_t == p_celulă (datele proprii domină integral)
   k → ∞        oricare    —          p̂_t == μ_părinte (părintele domină integral)

Pentru FIECARE rând, DOUĂ aserțiuni:
  (a) câmpul de audit NU e 0,5 fabricat — e valoarea definită, sau fail-closed explicit;
  (b) decizia e NO-TRADE la n=0, indiferent de valoarea câmpului.
```

**(b) e cel care contează operațional: poarta a fost verificată sigură, iar testul o îngheață.** (a) împiedică un câmp de audit fals să inducă în eroare un cititor uman — **auditul e citit de oameni, iar un 0,5 fabricat arată exact ca o estimare reală.**

---

# CONSEMNAREA 1 — POARTA LA 80% E BLÂNDĂ, ȘI ASTA E DIRECȚIA CORECTĂ

**Accept observația integral: blochează n=10, lasă n=1000; la mii de tranzacții e cvasi-echivalentă cu EV > 0.**

**Dar direcția e cea proiectată, nu un defect:** poarta apără împotriva EROARII DE EȘANTIONARE. La n=1000 eroarea de eșantionare CHIAR e mică, deci poarta TREBUIE să fie aproape transparentă acolo. **Ar fi o eroare de design ca ea să adauge conservatorism unui caz bine estimat.**

> **Red Team indică însă exact unde e golul real: la n mare, un interval îngust în jurul unei cifre GREȘITE trece poarta fără rezistență. Poarta nu apără împotriva MIS-SPECIFICĂRII.** **Iar ce apără împotriva mis-specificării la n mare e CONDIȚIA 3 — schema pre-înregistrată — nu nivelul de credibilitate.**

**Cele două condiții sunt complementare, iar observația Red Team e tocmai ce arată de ce.** Poarta acoperă n mic; schema hash-uită acoperă n mare. **Fără condiția 3, la n mare motorul n-ar avea nicio apărare.** Confirmarea la 95% post-DEMO rămâne, cu condiția deja fixată.

---

# CONSEMNAREA 2 — PLAFONUL DE −1R. Nu îl las deschis: se mărginește ACUM.

**Constatarea e corectă: fail-closed la −1R e închis contra modelului fără-gap din mstrat, nu contra cozii live. Direcția erorii e cunoscută — EV e optimist.**

**Dar, spre deosebire de slippage, ASTA E MĂSURABILĂ FĂRĂ FILL-URI**, pentru că un gap e o proprietate a TRAIECTORIEI DE PREȚ, nu a execuției. **Măsurat de mine pe descoperire:**

```
                          gap = 0 exact    gap > podeaua de risc    depășire când se întâmplă
toate tranzițiile            99,98%              0,02%
DOAR granițe de zi           97,95%              1,62%          median 4,09 R  p90 9,04 R  max 23,75 R
DOAR intraday               100,00%              0,00%
```

## Trei consecințe, și prima schimbă domeniul problemei

```
1. INTRADAY RISCUL E ZERO, MĂSURAT. 100,00% dintre tranzițiile intraday au gap exact nul.
   ⇒ politicile cu time-stop de ZI (CAND-0001, 0007, 0029 — „exit + day time-stop")
     sunt IMUNE. Plafonul de −1R e exact pentru ele.
2. Expunerea e strict a politicilor care pot ține peste granița de zi
   (orizont de 20 bare, orizont de bloc).
3. Coada e RARĂ ȘI URIAȘĂ: 1,62% din granițe, dar median 4× riscul și maxim 24×.
   O frecvență mică nu o face neglijabilă — o face invizibilă în teste scurte.
```

## Termenul de corecție, specificat

```
EV_R  =  p_t·RR  −  p_s·(1 + g)  +  p_h·E[X|h]  −  c/R

g = P(traversare de graniță de zi cu poziție deschisă)
    × P(gap ADVERS > distanța de stop)          ← ~1,62% / 2, direcția e ~simetrică
    × E[depășire | gap]                          ← ~4-9 R, măsurat

g = 0  EXACT, prin construcție, pentru politicile mărginite la zi.
```

**Ordinul de mărime pentru o politică ce ține peste noapte: ~0,008 × ~6 ≈ 0,05 R — comparabil cu termenul de cost (`c/R` ≈ 0,10-0,15).** Material, nu dominant, și **nu mai e o limitare nemărginită, ci un termen cu cifre.**

**Ce rămâne totuși deschis, și o spun:** cifrele sunt de pe descoperire (M15, 2011-2020). Se REVERIFICĂ pe fill-uri reale când există, la fel ca slippage-ul — dar **spre deosebire de slippage, motorul nu trebuie să aștepte, pentru că are deja o estimare derivată din preț.**

---

## HANDOFF

**VE construiește, în ordine:** (1) fișa-umbră pe TOATE declanșările, cu rezolvarea S1 identică și verificarea periodică executat-vs-umbră; (2) constructorul de tabelă cu `as_of` obligatoriu — **inclusiv `k(as_of)`** — plus aserțiunea de audit și testul de invariabilitate; (3) `schema_hash` separat de `prob_table_hash`, cu schema înregistrată în manifest ÎNAINTE de prima decizie, append-only; (4) bateria de frontieră din Condiția 4, ambele aserțiuni per rând; (5) termenul `g`, zero pentru politicile mărginite la zi.
**Red Team:** ținte explicite — dacă rezolvarea identică a barierei chiar face umbrele schimbabile cu cele executate, și dacă istoricul git al manifestului e o autoritate de timp suficientă pentru pre-înregistrare.
**CEO:** cele patru condiții sunt închise. **Iar a doua consemnare nu rămâne deschisă: gap-ul e ZERO intraday, măsurat, deci politicile cu time-stop de zi n-au deloc expunerea; pentru cele care țin peste noapte termenul e ~0,05 R, adică de ordinul costului.** Nivelul 6 e complet; aștept specificația nivelului 1.

---

**Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.48 (`alpha-automation-v1`) — mypy --strict curat, content_hash reverificat independent, pytest 139/143 (aceleași 4 eșecuri pre-existente).**
