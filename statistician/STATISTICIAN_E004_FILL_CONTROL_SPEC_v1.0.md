# STATISTICIAN — SPECIFICAȚIA CONTROLULUI PE `E004 fill` (Mandat 3.6, opțiunea 1)

**Document ID:** STAT-E004-FILL-CONTROL-SPEC-v1.0
**Data:** 2026-07-27 · **Autor:** Statistician
**Scop:** singurul document pe care Flow A îl execută pentru a decide eticheta pe rata de umplere E004 (0,662–0,736 observat, `PENDING_CONTROL` per `STATISTICIAN_STRUCTURAL_V1_FINAL_VERDICT_v1.0.md`). Scris ÎNAINTE de a vedea rezultatul controlului — interpretarea de la §4 e pre-înregistrată, nu se ajustează după cifră.

---

## 1. Populația de control — "gap comparabil", definit matematic

**Detecție, identică cu E004, fără cele două restricții specifice:**
- Imbalance standard 3-bare (`E012 detect_fvgs`, `PRIMARY_MIN_GAP=0.0`) — identic, aceeași funcție, același prag.
- **FĂRĂ** restricția de fereastră 13:30–15:30 UTC.
- **FĂRĂ** condiția "primul FVG al sesiunii US".
- Deci: fiecare bară M15 din blocurile de descoperire care satisface criteriul standard de imbalance 3-bare e o instanță eligibilă de control, indiferent de oră.

**Selecție — o instanță per zi, nu toate, pentru comparabilitate structurală cu E004:**

E004 produce cel mult o instanță per zi (prima din fereastră). Un control care numără FIECARE imbalance din toată ziua ar avea o granulație diferită (multiple instanțe/zi, corelate serial prin același traseu de preț) — nu doar altă selecție, ci altă STRUCTURĂ de eșantion. Pentru comparabilitate:

1. Pentru fiecare zi de tranzacționare din blocurile de descoperire (cele 3 regimuri, §2), identifică TOATE instanțele de imbalance 3-bare din acea zi (fără restricție de fereastră).
2. Dacă ziua are ≥1 instanță, selectează **UNA singură, aleasă uniform aleator** dintre cele disponibile acea zi — nu prima, nu ultima, nu cea cu gap-ul cel mai mare.
3. **Sămânță fixă, disclosed, reutilizare a convenției deja stabilite în laborator:** `seed=7` (aceeași sămânță folosită la decizia decisivă K6/DC-0004) — reutilizare explicită a unei convenții generice deja existente, nu o alegere nouă ne-declarată.
4. Zilele fără nicio instanță de imbalance nu contribuie cu nimic (nici zero, nici o valoare implicită) — pur și simplu absente din eșantionul de control acea zi, exact ca la E004.

**Rezultat măsurat, identic cu E004:** binar `fill` = prețul reintră în `[zone_low, zone_high]` în interiorul aceluiași orizont de 50 bare M15 de la formare.

## 2. Fereastra de măsurare — identică cu E004, același motiv

**Aceleași 3 regimuri** (bear/bull/correction, 2011-07-26→2021-09-03, blocurile de descoperire M15_v2) — **NU** regimul 2022-2026, pentru exact motivul deja stabilit: acela e M15 legacy, fereastra care a informat parametrizarea V1, sub `SAME-WINDOW-RESAMPLED`. Controlul trebuie măsurat pe EXACT aceleași date pe care E004 însuși a fost măsurat — altfel comparația nu mai e curată (ar introduce o diferență de compoziție a pieței, nu doar de definiție a populației).

## 3. Statistic-testul — NU binomialul din §7, un test diferit, motivat

**§7 nu se aplică direct aici.** Testul binomial din §7 compară o singură proporție empirică (winrate) contra unui **prag teoretic fix** (break-even ajustat la cost) — are sens acolo pentru că break-even e o valoare calculabilă analitic, independentă de orice eșantion. Aici nu există un asemenea prag teoretic pentru "rata de umplere a unui gap" — întrebarea e o comparație între **DOUĂ proporții empirice** (rata E004 vs. rata de control), niciuna teoretică.

**Test ratificat pentru acest control: test exact Fisher, one-sided, pe tabelul de contingență 2×2** (umplut/neumplut × E004/control) — exact, nu aproximare normală, consecvent cu preferința deja stabilită în laborator pentru teste exacte. **H0: p(E004) ≤ p(control). H1: p(E004) > p(control).** One-sided, pentru că întrebarea originală e specific "E004 se umple mai des decât un gap generic", nu "diferă în orice direcție".

**Pooling:** numărătorii se pun laolaltă peste cele 3 regimuri, pentru E004 și pentru control separat, înainte de test — consecvent cu tratamentul regimului ca defalcare descriptivă, nu multiplicator de teste, deja stabilit la §6/§7.

**Nu e parte din familia BH de 6** — e un test de diagnostic de sine stătător, unic, nu o ipoteză de tranzacție adăugată la familie.

## 4. Interpretarea pre-înregistrată — scrisă înainte de rezultat

Bandă calculată direct din rata E004 observată (0,662–0,736), cu o marjă practică de semnificație de **±0,15** (15 puncte procentuale) — un prag declarat, nu derivat matematic, ca să separe o diferență practic relevantă de una statistic-detectabilă-dar-trivială pe un eșantion mare:

| Rata de control (pooled) | Testul Fisher one-sided | Etichetă |
|---|---|---|
| **≤ 0,512** (0,662 − 0,15) | respinge H0 la α=0,05 | **`CONFIRMED_STRUCTURAL_ANOMALY` devine candidat viabil** — necesită TOT verdictul final al Statisticianului, nu automat |
| **(0,512 – 0,886)** | ORICE rezultat al testului | **`OBSERVED_NOT_DISTINCTIVE`** — rata generică de umplere a gap-urilor explică observația, E004 nu arată nimic distinctiv |
| **≥ 0,886** (0,736 + 0,15) | — | **`OBSERVED_BELOW_BASELINE`** — E004 se umple MAI RAR decât un gap generic; o constatare reală, distinctă, semnalată separat, nu doar "nedistinctiv" |

**Dacă rata de control cade sub 0,512 dar testul Fisher NU respinge H0** (posibil la n mic): rămâne `OBSERVED_NOT_DISTINCTIVE` — pragul numeric singur nu e suficient, ambele condiții (banda ȘI testul) trebuie satisfăcute pentru candidatura de anomalie.

**De ce contează ordinea asta:** banda de ±0,15 și pragul α=0,05 sunt fixate ACUM, înainte ca oricine să vadă rata de control — dacă rezultatul ar veni întâi, orice bandă aleasă după ar fi suspectă de a fi modelată pe cifră, exact riscul pe care CEO l-a numit.

## 5. Ce NU decide acest document

Chiar dacă rata de control cade în banda care face `CONFIRMED_STRUCTURAL_ANOMALY` un candidat viabil, eticheta finală rămâne o determinare separată a Statisticianului (verificare a mecanismului propus, nu doar a pragului numeric) — consecvent cu poziția deja luată la Mandatul 3.6. Acest document fixează DOAR pragurile și etichetele intermediare, nu emite verdictul final în avans.

---

**Nu am atins date, nu am executat nimic. Statistician se oprește aici.**
