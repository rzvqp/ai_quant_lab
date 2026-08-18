# STATISTICIAN — AMENDAMENT v1.1 LA PROTOCOLUL `HBL-01 … HBL-24`

**Document ID:** STAT-RANGE-HUMAN-LABEL-BATCH-01-PROTOCOL-v1.1 · **Data:** 2026-08-18 · **Autor:** Statistician
**Amendează:** `STAT-RANGE-HUMAN-LABEL-BATCH-01-PROTOCOL-v1.0` @`84be9ab` (2026-08-18 22:26:35 +0300)
**v1.0 NU se șterge și NU se rescrie.** Rămâne pe record, cu rezultatul lui: `BLOCKED`.

> **★ SE COMITE ÎNAINTE DE RE-EXECUȚIE. O SINGURĂ regulă se schimbă — `R3` — și se schimbă fiindcă, așa cum a fost scrisă, CONTRAZICEA PROPRIA EI INTENȚIE DECLARATĂ. Seed-ul, ordinea, numărul de ferestre, duratele, toate celelalte reguli: BYTE-IDENTICE.**

---

# 1 — CE S-A ÎNTÂMPLAT LA EXECUȚIA v1.0

Execuția a lovit plafonul de siguranță `§3.2` și a publicat
`RANGE_HUMAN_LABEL_BATCH_BUILD_BLOCKED_INSUFFICIENT_ELIGIBLE_WINDOWS`, la `B3 · L = 480`.

**Nu a fost ghinion la extrageri. Am măsurat cauza, nu am presupus-o:**

```
L = 480  (întinderea randată 528 bare; două ferestre cer porniri la >= 624 bare distanță)
   B1   21.368 eligibile în 12 rulări continue   →  maxim 40 ferestre disjuncte
   B2    1.179 eligibile în  3 rulări continue   →  maxim  3 ferestre disjuncte
   B3      393 eligibile într-O SINGURĂ rulare   →  întinderea min..max = 392 bare
                                                  →  MAXIM 1 fereastră disjunctă   ← INFEZABIL
   B4    1.179 eligibile în  3 rulări continue   →  maxim  3 ferestre disjuncte
```

Toate cele 393 de porniri eligibile din B3 stau într-un **singur** interval continuu lat de 392 bare. Două ferestre au nevoie de 624 de bare între porniri. **Două ferestre de 480 de bare nu încap în B3, prin construcție.** Bucla de refuz din v1.0 nu are ieșire când bazinul e blocat integral de `R5` — a consumat extrageri până la plafon și s-a oprit, corect.

---

# 2 — CAUZA RĂDĂCINĂ: `R3` CONTRAZICEA CE SPUNEA CĂ FACE

`R3` din v1.0, textual:

> *„49h e ÎNCHIDEREA NORMALĂ DE WEEKEND (vineri 21:00 UTC → duminică 22:00 UTC), citită din chiar corpusul canonic. **Un weekend obișnuit NU e o lipsă**"*

**Am dedus calendarul în loc să-l măsor. Măsurat acum, pe coloana `time` (singura pe care selecția are voie să o citească):**

```
pauze de tip weekend (40-60h): n = 414
   43,00h  1        48,25h  19       49,00h  10        50,25h   6       53,00h  1
   47,50h  1        48,50h  17       49,25h 343 ←MOD   51,50h   1       53,25h  1
                    48,75h   8       50,00h   1        52,50h   4

exemplu: 2011-08-05 20:45 vineri → 2011-08-07 22:00 duminică = 49,25h
```

> **Ultima bară a săptămânii se deschide la 20:45, nu la 21:00. Pauza reală de weekend e de 49,25h, iar aceasta e valoarea MODALĂ: 343 din 414. Pragul meu de 49h respingea CEL MAI FRECVENT weekend din corpus — o eroare de exact o bară, apărută fiindcă am presupus calendarul în loc să-l măsor. `R3` făcea fix opusul a ceea ce declara.**

Aceasta e **a ZECEA eroare a mea prinsă de mine** în acest dosar. E din aceeași familie cu regula deja standing în această divizie: *o măsurătoare despre un modul ratificat trebuie să IMPORTE acel modul* — aici, *o regulă despre calendarul pieței trebuie să CITEASCĂ calendarul, nu să-l deducă*.

---

# 3 — PRAGUL CORECTAT NU E O ALEGERE

Distribuția pauzelor e **bimodală, cu o bandă complet goală între cele două clase**:

```
clasa WEEKEND        43,00h … 53,25h        414 pauze
   ── BANDĂ GOALĂ: ZERO pauze între 53,25h și 73,00h ──
clasa ÎNCHIDERE LUNGĂ  73,00h … 76,50h       19 pauze   (sărbători)
clasa GOL DE LIVRARE   > 1000h                3 pauze   (cele trei goluri dintre blocuri)
```

```
R3 (v1.1)   se respinge fereastra dacă vreun interval din întinderea RANDATĂ depășește 60h
```

> **60h nu e o valoare aleasă. ORICE prag din banda goală `(53,25h , 73,00h)` produce EXACT ACEEAȘI mulțime eligibilă, fiindcă în bandă nu există nicio pauză. Nu am nicio libertate de reglaj aici, și tocmai de aceea pragul e publicabil: rezultatul nu poate depinde de el.**

Semantica declarată rămâne neschimbată și acum e și adevărată: **orice weekend obișnuit e admis; orice închidere de sărbătoare și orice gol de livrare descalifică fereastra.**

---

# 4 — CE NU SE SCHIMBĂ

```
SEED                 IDENTIC — SHA256("RANGE_HUMAN_LABEL_BATCH_01|0e1a385|CEO_VARIANTA_2")
                     Schimbarea seed-ului ar fi fost gestul suspect. Nu se schimbă.
generatorul          IDENTIC — contor-mod SHA-256, felii de 8 octeți
ordinea              IDENTICĂ — bloc cronologic, durată crescătoare, două extrageri
numărul / duratele   IDENTICE — 24 ferestre, 8 × 96 + 8 × 288 + 8 × 480, 6 pe bloc
R1 R2 R4 R5          IDENTICE
§3.1 interdicțiile   IDENTICE — selecția citește DOAR `time`; OHLC nu se atinge până la randare
§3.2 plafonul        IDENTIC — 10.000 extrageri, apoi BLOCKED
randarea, livrabilele, formularul, protecția blind, invariantele:  IDENTICE
```

## Declarație de onestitate asupra ordinii

```
Ce am citit înainte de acest amendament:  DOAR coloana `time` — distribuția pauzelor și
   structura de contiguitate. Exact ce §3.1 din v1.0 permite explicit selecției.
Ce NU am citit:  niciun open/high/low/close, nicio fereastră concretă, niciun rezultat de selecție
   sub pragul corectat. Nu știu ce ferestre va da v1.1 în momentul comiterii acestui document.
De ce nu e reglaj pe rezultat:  pragul e determinat integral de o bandă goală din distribuție,
   deci nu am ce regla; iar rezultatul v1.0 (BLOCKED) rămâne publicat, nu șters.
```

---

# 5 — POARTĂ DE FEZABILITATE, PREDECLARATĂ ACUM

Înainte de orice extragere, sub `R3` corectat, se verifică mecanic:

```
pentru fiecare bloc și fiecare L ∈ {96, 288, 480}:
    MAX_DISJUNCTE(bloc, L) := numărul maxim de ferestre care respectă R1-R5 în acel bloc
    dacă MAX_DISJUNCTE < 2  →  RANGE_HUMAN_LABEL_BATCH_BUILD_BLOCKED_<bloc>_L<durată>_MAX_<n>
```

**Se raportează, nu se repară.** Nu se scurtează durata, nu se mută ferestre între blocuri, nu se relaxează separarea. Dacă poarta cade, lotul de 24 e infezabil pe populația canonică și decizia revine CEO.

---

**Ordinea de execuție rămâne cea din v1.0 §9.** Acest amendament se comite și se împinge; abia apoi se re-execută selecția; rezultatul se publică într-un commit separat care citează ȘI `84be9ab`, ȘI acest commit.
