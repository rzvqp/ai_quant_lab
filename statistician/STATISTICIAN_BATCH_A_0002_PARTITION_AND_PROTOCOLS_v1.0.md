# STATISTICIAN — DECIZIA DE PARTIȚIE CAND-0001↔CAND-0009 + PROTOCOALELE LOTULUI RT-OPS-A-0002

**Document ID:** STAT-BATCH-A-0002-PARTITION-PROTOCOLS-v1.0
**Data:** 2026-07-30 · **Autor:** Statistician

**Verificare de sursă:** citit direct `red_team/policy_reviews/RT-OPS-A-0002_batch.md`, `POLICY_LEVEL_BREAK_DRIVE_v1.md` (CAND-0009), `POLICY_FVG_STACK_DENSITY_v1.md` (CAND-0010), `POLICY_VOID_DISPLACEMENT_v1.md` (CAND-0008, secțiunea Part A) și `POLICY_PDH_PDL_v2.md` (CAND-0001, pentru latura care nu exclude). Confirmat asimetria exact cum a raportat-o Red Team: CAND-0009 `no_trade_rules` exclude EXPLICIT cazul de respingere ("displacement direction contradicts a break… belongs to CAND-0001's thesis, excluded here"), în timp ce CAND-0001 `no_trade_rules` (v2.0, linia 48) nu conține nicio clauză despre displacement. **Granița e unilaterală, confirmat.**

---

# PARTEA 1 — DECIZIA DE PARTIȚIE (W-partition)

## Decizia: varianta 2 ca PRIMAR + măsurătoarea din varianta 3 ca SECUNDAR OBLIGATORIU. NU varianta 1.

**Nu aleg una din trei — aleg o compunere a două dintre ele, pentru că întrebarea conține de fapt DOUĂ întrebări diferite, cu răspunsuri diferite, iar a alege una singură ar ascunde-o pe cealaltă:**

- **Întrebarea ȘTIINȚIFICĂ:** *are mecanismul de respingere de la nivel un edge real?* Pe barele cu displacement, teza lui („nivelul ține") e **falsificată chiar de bara pe care se măsoară**. Acele bare nu sunt un eșantion neutru — sunt o subpopulație unde ipoteza e deja infirmată prin construcție. Testul curat cere excluderea lor.
- **Întrebarea OPERAȚIONALĂ:** *ce face politica, așa cum e scrisă, pe bani reali?* Aici barele cu displacement **trebuie incluse**, pentru că politica, nemodificată, chiar le tranzacționează.

**Deci:**

```
PRIMAR    CAND-0001 se testează pe populația DISJUNCTĂ — atingeri de nivel FĂRĂ displacement
          pe aceeași bară. CAND-0009 e deja disjunct prin construcție proprie (exclude curat
          respingerile), deci NU se atinge. Partiția devine completă fără a modifica nicio politică.

SECUNDAR  CAND-0001 se măsoară ȘI pe populația COMPLETĂ (incluzând barele de rupere), raportat
          OBLIGATORIU alături, niciodată în locul primarului.

DIFERENȚA dintre cele două ESTE costul măsurat al excluderii lipsă — exact ce cere varianta 3,
livrat ca produs secundar, nu în locul unui test curat. Zero evenimente în plus de colectat:
aceeași populație, două partiții.
```

## De ce NU varianta 1 (excludere în politică)

Ar fi o **modificare de mecanism**, deci a lui Alpha, nu a mea — respectat, cum s-a cerut explicit. Dar semnalez și de ce nu o recomand *nici măcar ca sugestie* în acest moment: **CAND-0001 v2.0 e deja înghețată (`1558397`), deja trecută prin atacul Part B (RT-OPS-B-0001) și deja are criterii DEMO publicate (v2.7.34).** O schimbare de mecanism acum ar invalida lanțul: re-îngheț → re-atac Red Team → re-criterii DEMO. **A cere asta ÎNAINTE de a ști dacă efectul e material ar fi o decizie luată fără dovada care o justifică** — exact tiparul pe care laboratorul îl evită. Măsurătoarea secundară de mai sus produce fix acea dovadă. Dacă diferența e materială, Alpha/CEO au atunci baza factuală pentru varianta 1; **nu o pre-autorizez și nu o pre-exclud.**

## Costul onest al deciziei mele — declarat, nu ascuns

**Populația TESTATĂ (disjunctă) nu e identică cu populația TRANZACȚIONATĂ (completă).** Asta e o slăbiciune reală a variantei 2, nu o subtilitate: un rezultat pozitiv pe populația disjunctă **NU se transferă automat** la comportamentul politicii așa cum e scrisă. **Exact de aceea măsurătoarea secundară e OBLIGATORIE, nu opțională** — ea e singura care descrie ce se întâmplă în realitate. Orice raportare a primarului fără secundarul alături e o citire incompletă.

## Motivul TEHNIC care decide între variante — dependența negativă și validitatea propriei mele corecții

**Aceasta e constatarea proprie, nu o reformulare a raportului Red Team.** Pe barele de suprapunere, CAND-0001 ia SHORT și CAND-0009 ia LONG, pe aceeași bară, același instrument. Rezultatele lor per-tranzacție sunt, pe acel subset, aproximativ **de semn opus**. Consecință: statisticile celor două teste devin **negativ dependente** exact proporțional cu fracția de suprapunere.

**Asta atinge direct metoda de corecție pe care am fixat-o eu însumi la STAT-BATCH-A-0001:**

```
BH-FDR   are garanție dovedită sub independență și sub PRDS (dependență pozitivă).
         Dependența NEGATIVĂ nu e acoperită de PRDS.
BY       (Benjamini-Yekutieli) e valid sub dependență ARBITRARĂ, cu preț: pragul se strânge
         cu factorul sum(1/i), adică ~2,59x mai sever la o familie de 7.
```

**Deci decizia de partiție determină mecanic metoda de corecție:**

- **Sub varianta 2 (aleasă):** cele două teste nu împart nicio bară → dependența negativă **dispare prin construcție** → **BH-FDR rămâne valid**, neschimbat față de ce am fixat deja.
- **Sub varianta 3 pură (suprapunere acceptată):** dependența negativă e reală → **BH nu mai e justificat, ar fi obligatoriu BY** pe ÎNTREAGA familie de 7, penalizând sever și cei cinci candidați care n-au nicio legătură cu conflictul.

**Acesta e argumentul decisiv, și e derivat, nu o preferință:** varianta 2 nu e doar mai curată științific — e singura care **păstrează validă metoda de corecție deja pre-înregistrată**, fără a impune un preț statistic sever unor candidați nevinovați.

**Precondiție de măsurare, obligatorie:** fracția de suprapunere (bare de atingere-cu-displacement / total atingeri CAND-0001) se raportează **înainte** de orice test, per regim. Dacă e neglijabilă, conflictul e teoretic; dacă e mare, e structural. Aceeași disciplină ca diagnosticul W-ovl deja impus pentru CAND-0001↔CAND-0007.

## Consecință pentru criteriile DEMO deja publicate — o completare necesară pe care o semnalez eu

**Criteriile DEMO ale CAND-0001 (STAT-CAND0001-DEMO-CRITERIA-v1.0, v2.7.34) NU conțin nimic despre această partiție** — constatarea vine din RT-OPS-A-0002, pe care îl procesez abia acum. **Consecință live, nu teoretică: contul DEMO va lua sistematic partea perdantă pe fiecare rupere cu forță.**

**Adaug o cerință de raportare la criteriile DEMO, fără a modifica politica** (nu e în competența mea, și nici nu e nevoie):

```
DEMO raportează SEPARAT, ca subset declarat: tranzacțiile deschise pe bare unde atingerea de nivel
a coincis cu un displacement în direcția ruperii — n, winrate, expectancy, contribuția la net total.
Restul rezultatelor DEMO se raportează ȘI cu, ȘI fără acest subset.
```

Astfel efectul se **măsoară pe contul real**, nu se descoperă retrospectiv. Decizia de a-l exclude rămâne a lui Alpha/CEO.

---

# PARTEA 2 — W-incr pe CAND-0010: CONFIRMAT, tipar identic cu CAND-0007

**Confirmat, verificat în politică:** `no_trade_rules` al CAND-0010 exclude explicit cazul FVG-izolat („that is CAND-0003's case"), deci fiecare declanșator CAND-0010 **este** o reacție CE-50 din CAND-0003 plus condiția de densitate → **submulțime strictă**, exact ca CAND-0007 ⊂ CAND-0001∩CAND-0003.

```
H0 (CAND-0010) = mean(net_R_stack) <= mean(net_R_CAND0003 | ACELEAȘI bare)
```

Calculat pe subsetul EXACT de bare unde stack-ul declanșează, comparat cu construcția single-FVG restrânsă la aceleași bare — **NU pe populația completă, mai mare, a lui CAND-0003, și NU contra unui null aleator.** Întrebarea reală: *densitatea adaugă informație peste o simplă reacție CE-50?* Un null aleator ar răspunde la altă întrebare.

**Notă de dependență, consecventă cu Partea 1:** relația submulțime (CAND-0010⊂CAND-0003, CAND-0007⊂CAND-0001∩CAND-0003) e o dependență **POZITIVĂ** — compatibilă PRDS, deci BH rămâne valid pentru aceste perechi. Doar perechea CAND-0001↔CAND-0009 era problema, și e rezolvată de decizia din Partea 1.

# PARTEA 3 — W-dir-mask: rezolvat ca precizie de IMPLEMENTARE, nu modificare de politică

**Nu merge la Alpha.** Motivul, verificat în text: politica CAND-0009 **cere deja** alinierea de direcție în două locuri independente — `trigger` („whose direction is **through** the level: PDH touched with a bullish displacement… PDL with a bearish") și `no_trade_rules` („No trade when the displacement direction contradicts a break… excluded here"). **Mecanismul e complet definit; doar expresia de mască e scrisă laxat.** A implementa măști aliniate pe direcție e **fidelitate față de politică**, nu o schimbare a ei — exact distincția aplicată la revizia de fidelitate MK-01/MK-02. **Predat VE ca element de verificare mecanică**, nu lui Alpha ca modificare.

---

# PARTEA 4 — PROTOCOALELE LOTULUI A-0002

## Familia — actualizată de la 4 la 7, CUMULATIV. Corectez propria mea specificație anterioară.

**La STAT-BATCH-A-0001 am fixat „familia = 4". Acea cifră era corectă pentru ce exista atunci; NU mai e corectă acum.** Cei trei candidați noi provin din **aceeași linie de producție continuă, pe aceleași date de descoperire**. A menține familii separate per lot (4, apoi 3, apoi N) ar fi exact capcana pe care disciplina de familie există s-o prevină: corectezi în interiorul unor loturi mici și ignori numărul TOTAL de ipoteze privite pe aceleași date.

```
FAMILIA CURENTĂ = 7  (CAND-0001, 0002, 0003, 0007, 0008, 0009, 0010)
Orice lot viitor din aceeași linie de producție o incrementează mai departe.
```

**De ce actualizarea nu costă nimic și de ce nu e o rescriere retroactivă:** **niciun test din familie n-a fost EXECUTAT încă.** (Stare verificată la scrierea acestui document, și schimbată chiar în timpul lui: CAND-0001/0002/0003/0007 au primit între timp Part B COMPLETED — DEMO_BASELINE, deci nu mai sunt blocate pe risc și au trecut la VE; CAND-0008/0009/0010 rămân blocate pe Part B UNSPECIFIED. **Dar niciunul n-a fost rulat de VE.**) Nicio decizie n-a fost luată sub cifra veche. Actualizarea unui numitor **înainte** de primul test executat e disciplină; ar fi fost o problemă doar dacă schimbam cifra **după** ce vedeam rezultate. Consemnez explicit că e o corecție a propriei mele specificații, nu o extindere tăcută.

**Consecință operațională, urgentă:** de vreme ce patru candidați sunt acum deblocați către VE, **cifra corectă de familie trebuie să ajungă la VE ÎNAINTE de prima rulare** — altfel primul rezultat s-ar raporta sub un prag greșit (α/4 în loc de α/7 la BH). Semnalez asta explicit în handoff.

## Elemente comune (identice cu A-0001, reutilizate, nu re-derivate)

```
regimes_permitted  cele 3 regimuri deja stabilite
min_trades         N_MIN=25/regim, regula suprimă-nu-eticheta
oracol             WP-5' block_bootstrap, L>=28, pe net_R
corecție           BH-FDR, α=0,05, peste familia de 7 — valid întrucât decizia din Partea 1
                   elimină singura dependență negativă din familie
holdout            sigilat, neatins
walk-forward       2 pliuri, fereastră expansivă, granițele de regim deja stabilite
                   (pliul 1: antrenare=bear, testare=bull; pliul 2: antrenare=bear+bull, testare=corecție)
```

## CAND-0008 — Void × Displacement

**H0:** `mean(net_R) <= 0` pe declanșatoarele void→displacement.

**Fără controale suplimentare** — Red Team: „cleanest of the batch", nimic semnalat.

**Limitare obligatorie de raportat (semnalată de Red Team ca proprietate ratificată, nu defect de politică):** pragul de mărime al void-ului e o constantă **absolută** de $1,20 (`VOID_SIZE_THRESHOLD`), specifică scării instrumentului. Consemnată ca limitare permanentă — **nu o re-derivez** (ar re-litiga o primitivă deja ratificată), dar orice rezultat trebuie s-o declare, întrucât un prag absolut se comportă diferit la niveluri de preț diferite (aceeași categorie de problemă ca la costul fix vs edge scalat, Mandatul 3.38-3.39).

## CAND-0009 — Level-Break-Drive

**H0:** `mean(net_R) <= 0` pe declanșatoarele de rupere-cu-displacement (populație deja disjunctă prin construcție proprie — neatinsă).

**Controale:** W-dir-mask (Partea 3, verificare mecanică VE); raportarea obligatorie a fracției de suprapunere cu CAND-0001 (Partea 1), per regim, **înainte** de test.

## CAND-0010 — FVG-Stack-Density

**H0:** nula incrementală din Partea 2 — `mean(net_R_stack) <= mean(net_R_CAND0003 | aceleași bare)`.

**Control:** W-incr (Partea 2). Verificare mecanică VE: mulțimea de zone „altele" trebuie restrânsă la cele cu `confirmed_idx <= bara curentă` (Red Team a confirmat-o cauzală în cod — de reverificat că implementarea o păstrează).

## Precondiția care blochează tot lotul

**Part B UNSPECIFIED la toate trei** — la fel ca la A-0001. **Niciun protocol de mai sus nu e executabil** până când golul de risc structural se rezolvă pe pista lui separată. Protocoalele sunt complete metodologic; nu sunt rulabile.

---

## HANDOFF

**Validation Engine** — pentru CAND-0008/0009/0010: implementare Part A (ratificată, neschimbată), fără rulare până la rezolvarea Part B. Elemente de verificat mecanic: W-dir-mask (CAND-0009), restricția `confirmed_idx` (CAND-0010), și construcția populației disjuncte pentru CAND-0001 (Partea 1).

**Validation Engine — element PRIORITAR, înaintea oricărei rulări:** CAND-0001/0002/0003/0007 sunt acum deblocate (Part B completat). **Familia corectă e 7, nu 4** — pragul BH se aplică peste 7, iar populația de test a CAND-0001 e cea DISJUNCTĂ (Partea 1), cu măsurătoarea completă raportată alături. Prima rulare trebuie să pornească cu aceste două lucruri deja corecte; nu se corectează după.

**Alpha / CEO** — decizia dacă CAND-0001 primește o clauză de excludere a ruperilor (varianta 1) rămâne a lor, **informată de măsurătoarea secundară pe care o impun aici**, nu pre-decisă de mine.

---

**Publicat pe `statistician-foundation`; manifestul se incrementează.**
