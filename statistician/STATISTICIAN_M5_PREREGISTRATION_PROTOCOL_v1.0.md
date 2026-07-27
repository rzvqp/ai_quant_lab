# STATISTICIAN — PROTOCOL DE PRE-ÎNREGISTRARE M5 (împărțire, carantină, relația cu M15)

**Document ID:** STAT-M5-PREREG-v1.0
**Data:** 2026-07-27 · **Autor:** Statistician
**Statut:** Reguli, nu execuție. M5 e livrat (354.669 bare, 2021-07-27 → 2026-07-27), în carantină, NECONECTAT — acest document se scrie ÎNAINTE de conectare, ca precedentul deja stabilit (`STATISTICIAN_11YR_DATASET_PREREGISTRATION_RULES_v1.0.md`) cere.
**Nu transferă regula M15 mecanic:** M5 are altă acoperire (5 ani, nu 11-15), alt interval de bară (300s, nu 900s), și altă structură de regim (fără bear-ul 2011-2015). Fiecare regulă de mai jos e re-derivată din PRINCIPIUL M15, nu copiată ca număr.

---

## 1. Împărțirea descoperire/confirmare — principiul, re-derivat

**Principiul moștenit (neschimbat, doar reaplicat):** (i) harta de regimuri produsă printr-o regulă mecanică, disclosed, nu subiectivă; (ii) împărțirea în interiorul fiecărui segment continuu de regim, nu la o singură dată globală de tăiere; (iii) motiv pentru pondere mai mare pe partea sigilată acolo unde setul e o raritate.

**Re-derivare pentru M5:**
1. **Harta de regimuri se re-rulează independent pe fereastra M5** (2021-07-27 → 2026-07-27) — NU se importă harta produsă pentru M15/M15-extins. Structura de regim din acești 5 ani (care nu conțin bear-ul 2011-2015) e o întrebare empirică proprie, nu o presupunere moștenită.
2. **Split implicit 50/50 în interiorul fiecărui segment**, aceeași justificare de raritate ca la M15: M5 e, la data acestui document, singurul set de confirmare de rezoluție fină care există curat — o raritate comparabilă, nu mai mică. Ajustare la 60/40 DOAR pentru un segment specific dacă harta arată un segment prea scurt pentru ca 50% descoperire să fie utilă — decisă înainte de rezultate, nu retroactiv, exact regula M15.
3. Harta însăși nu raportează cifre calculate special pentru porțiunea care va fi sigilată — aceeași regulă M15 §1 punct 4, neschimbată.

**Ce NU se moștenește:** proporția exactă a segmentelor (M15 avea un bear multi-an; M5 poate avea o structură complet diferită — posibil un regim dominant lung, fără cicluri complete) — harta decide asta empiric, nu eu acum.

## 2. Carantina — derivată din principiu, nu din cifră

**Ce NU fac:** nu transfer "960 de bare" ca număr. La rezoluție M5, 960 de bare acoperă o treime din intervalul calendaristic pe care îl acoperea la M15 — exact problema pe care ai semnalat-o.

**Derivare corectă:** principiul embargo-ului e protecția unei DURATE CALENDARISTICE de dependență serială (orizontul cel mai lung folosit de o ipoteză înghețată — `TRACK_HORIZON=960` bare M15 din E015), nu un număr de bare per se. Bara M15 = 900 secunde; bara M5 = 300 secunde. Raport: 900/300 = 3.

Durata calendaristică protejată la M15: 960 × 900s = 864.000s = 240 ore = 10 zile.
Echivalentul în bare M5, aceeași durată calendaristică: 960 × 3 = **2.880 bare M5**.

**Asumpție declarată, nu ascunsă:** ambele serii (M15 și M5) exclud aceleași goluri de non-tranzacționare (weekend/sărbători) pe același instrument (XAUUSD) — raportul de conversie 3× e valid pe bare de tranzacționare, nu pe zile calendaristice brute, și rămâne consistent între cele două serii exact din acest motiv.

**Rotunjire de siguranță, același stil ca 960→1.000 la M15 (~4,2% marjă):** 2.880 → **3.000 bare M5**, rotunjire la un număr rotund curat, marjă comparabilă.

**Carantina M5 = 3.000 de bare, la fiecare graniță internă descoperire/confirmare, exclusă integral din ambele părți.**

## 3. Relația cu M15 — suprapunerea temporală, regulă obligatorie

**Constatare geometrică, verificată din acoperirile declarate:** M5 (2021-07-27 → 2026-07-27) se suprapune aproape integral cu M15 curent (2022-12-16 → ~2026-07-13, dataset-ul deja folosit pentru DC-0004 și restul) — M15 curent e, calendaristic, aproape în întregime un SUBSET al ferestrei M5. Singurele porțiuni M5 fără corespondent M15-curent sunt marginile: 2021-07-27 → 2022-12-16 (~1,4 ani, înainte de începutul M15 curent) și eventual câteva zile la coada 2026.

**Regula, obligatorie, indiferent de split-ul intern M5:**

> **Dacă parametrii/pragurile unei ipoteze au fost descoperiți sau fixați folosind date M15 dintr-o fereastră calendaristică W, o rulare pe M5 restrânsă la ACEEAȘI fereastră W nu constituie confirmare — indiferent dacă acea porțiune M5 cade în jumătatea de descoperire sau de confirmare a split-ului M5 însuși.** E aceeași cale de preț observată la altă rezoluție temporală, nu o probă independentă — bara M5 și bara M15 care o conține nu sunt trageri independente, sunt aceeași mișcare de preț descompusă altfel.

**Consecință obligatorie de verificare, per ipoteză, înainte de a raporta orice rezultat M5 ca "confirmare":** se declară explicit fereastra calendaristică M15 care a informat parametrizarea ipotezei (W), și se verifică suprapunerea cu fereastra M5 folosită pentru testare. Dacă suprapunerea e nenulă, rezultatul se etichetează **`SAME-WINDOW-RESAMPLED`** — raportat, dar NICIODATĂ tratat ca și confirmare out-of-sample sau cross-rezoluție. Doar porțiunea M5 STRICT calendaristic disjunctă de W poate purta eticheta de confirmare independentă.

**Notă practică, semnalată nu rezolvată aici:** dat fiind că majoritatea ipotezelor testabile din acest laborator au fost parametrizate pe fereastra 2022-2025 (deja stabilit în `STATISTICIAN_11YR_DATASET_PREREGISTRATION_RULES_v1.0.md` §2, proveniența convențiilor), porțiunea M5 cu adevărat disjunctă pentru MAJORITATEA lor s-ar putea reduce la marginile (2021-07-27→2022-XX și/sau coada post-2025-10-23). Cât de îngustă e acea felie, per ipoteză, e o întrebare de capacitate statistică pentru cine execută, nu ceva ce rezolv eu acum — regula de mai sus se aplică indiferent de cât de restrictivă se dovedește.

---

**Nu am atins date. Nu am implementat. Statistician se oprește aici.**
