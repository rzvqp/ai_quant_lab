# STATISTICIAN — PROTOCOL DE PRE-ÎNREGISTRARE H1 (împărțire, carantină, relația cu M15/M5)

**Document ID:** STAT-H1-PREREG-v1.0
**Data:** 2026-07-27 · **Autor:** Statistician
**Statut:** Reguli, nu execuție. H1 (122.601 bare, 2006-03-20 → 2026-07-27, 20,36 ani) rămâne în carantină, NECONECTAT, până la publicarea acestui document — precedentul deja aplicat la M5.
**Nu transferă regula M15/M5 mecanic:** H1 are altă acoperire (20+ ani, nu 5 sau 11-15), alt interval de bară (3.600s), și cel mai important — un segment (2006-2011) pe care nimeni din laborator nu l-a văzut vreodată, la nicio rezoluție, nici măcar în tentativa retrasă de M15-extins (care ar fi început 2011-07-25). Fiecare regulă de mai jos e re-derivată din principiu, nu copiată.

---

## 1. Împărțirea descoperire/confirmare

**Principiu neschimbat, re-derivat:** hartă de regim mecanică, disclosed, rulată INDEPENDENT pe fereastra H1 — NU importată din harta M15 sau M5. Structura de regim H1 e o întrebare empirică proprie: din schița livrată (2006 închidere 637 → criza 2008 → 2011 vârf 1565), segmentele exacte (acumulare/criză/recuperare, posibil unul sau mai multe) le decide harta mecanică a Data Acquisition, nu presupunerea mea.

**Split implicit 50/50 în interiorul fiecărui segment**, aceeași justificare de raritate ca M15/M5, aplicată acum celui mai rar segment pe care laboratorul l-a întâlnit vreodată. Ajustare la 60/40 doar pentru un segment specific prea scurt pentru utilitate la 50% descoperire — decisă înainte de rezultate, ca la M15/M5.

**Notă de vigilență, nu un raport de împărțire diferit:** 2006-2011 e ireproductibil — dacă vreodată se pierde (contaminat prin observație discreționară, cum s-a întâmplat cu fereastra DC-0004), nu există o a doua șansă să fie readus curat. Nu derivez un raport diferit de 50/50 fără o justificare la fel de fermă ca restul acestui document — dar semnalez explicit riscul, ca precedentul deja documentat ("de trei ori datele au fost accesibile înainte să existe o regulă") să nu devină a patra oară pe exact cea mai valoroasă felie din tot dataset-ul.

## 2. Carantina — derivată din durata calendaristică, nu din transferul cifrei

Bara H1 = 3.600s. Raport față de M15 (900s): 4. Raport față de M5 (300s): 12.

**Ce NU fac:** transferul direct al cifrei "960" ca număr de bare H1 ar da 960×3.600s = 960 ore = **40 de zile** — de 4 ori mai lung decât protecția calendaristică originală. Spre deosebire de M5 (unde transferul brut al cifrei SUB-protejează, dând doar 3,33 zile), la H1 transferul brut SUPRA-protejează. Ambele direcții de eroare confirmă că derivarea trebuie făcută din durata calendaristică, nu din numărul de bare — indiferent de direcția în care ar greși transferul naiv.

**Derivare corectă:** durata calendaristică protejată, deja stabilită la M15 (`TRACK_HORIZON=960` bare M15 × 900s = 864.000s = 240 ore = **10 zile**). Echivalentul în bare H1, aceeași durată: 960 ÷ 4 = **240 bare H1** (960 bare M15 = 240 bare H1, la aceeași durată calendaristică — un H1 acoperă 4 bare M15).

**Marja de siguranță — factor consistent, nu re-ales la fiecare rezoluție:** verificare directă: 960→1.000 (M15) și 2.880→3.000 (M5) sunt AMBELE exact multiplicarea cu **25/24** (≈4,17%): 960×25/24=1.000; 2.880×25/24=3.000. Aplic ACELAȘI factor, nu unul nou: 240×25/24 = **250 bare H1**, exact, fără rotunjire aproximativă.

**Carantina H1 = 250 de bare, la fiecare graniță internă descoperire/confirmare, exclusă integral din ambele părți.** (250 bare H1 × 3.600s = 900.000s = 250 ore ≈ 10,42 zile — consistentă cu marja de 25/24 aplicată și la M15/M5.)

## 3. Relația cu M15 și M5 — regulă generalizată, simetrică pe direcție

Regula `SAME-WINDOW-RESAMPLED` (stabilită la M5) se generalizează, neschimbată ca principiu: **aceeași cale de preț observată la altă rezoluție nu e o probă independentă**, indiferent dacă noua rezoluție e mai fină sau mai grosieră decât cea care a informat parametrizarea ipotezei.

**Regulă, obligatorie:** dacă parametrii unei ipoteze au fost fixați folosind date M15 și/sau M5 dintr-o fereastră calendaristică W, o rulare pe H1 restrânsă la (sau suprapusă cu) W nu constituie confirmare — se etichetează `SAME-WINDOW-RESAMPLED`, indiferent de jumătatea split-ului H1 (secțiunea 1) în care cade acea porțiune. Verificarea de suprapunere calendaristică (nu doar de rezoluție) e obligatorie per ipoteză, înainte de a raporta orice rezultat H1 ca și confirmare.

**Ce NU e afectat de această regulă — singura porțiune complet liberă din tot laboratorul:** **2006-03-20 → 2011-07-25** (începutul chiar și al tentativei retrase de M15-extins) nu se suprapune cu NICIO fereastră folosită vreodată, la nicio rezoluție, în acest laborator. E teritoriul cu adevărat nou — acumularea pre-criză, criza 2008, vârful 2011. Orice ipoteză testată exclusiv aici nu poate fi etichetată `SAME-WINDOW-RESAMPLED` — e cea mai curată felie de date pe care acest laborator o va avea vreodată.

**Proveniența parametrilor rămâne neschimbată:** regula deja stabilită (§2, `STATISTICIAN_11YR_DATASET_PREREGISTRATION_RULES_v1.0.md` v1.2) despre convenții împrumutate se aplică identic pe H1 — nu se rescrie aici, doar se reafirmă aplicabilitatea.

---

**H1 rămâne în carantină până la conectare conform acestui protocol. Nu am atins date, nu am implementat. Statistician se oprește aici.**
