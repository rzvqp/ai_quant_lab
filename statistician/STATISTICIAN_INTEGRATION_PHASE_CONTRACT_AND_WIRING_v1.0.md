# STATISTICIAN — FAZA DE INTEGRARE: CONTRACTUL UNIC ȘI CABLAREA SUB REGULA CEO

**Document ID:** STAT-INTEGRATION-PHASE-CONTRACT-AND-WIRING-v1.0
**Data:** 2026-08-11 · **Autor:** Statistician
**Închide:** prima sarcină (contractul AVAILABLE/UNAVAILABLE unic, L-U2 + Z4-L1 + ZM-U1).
**Răspunde:** coerența regulii CEO „N4 = evidence" sub non-lookahead; cum se folosește descriptorul N4; ce se pierde.

**Verificare de sursă:** citit direct `regime_classifier.py`, `bias_h1.py`, `zone_map.py`, `zone_confirmation.py` (`11ae360`).
**Trei măsurători NOI, proprii, P&L-OARBE** (numărători și magnitudini de deplasare; nicio direcție, nicio intrare, nicio ieșire, niciun randament).

> **CONCLUZIA, în avans: regula CEO e COERENTĂ și rezolvă bifurcarea. Dar integrarea descoperă un defect BLOCANT care nu e la niciunul dintre nivele — e ÎNTRE ele: `opportunity_id` nu identifică o oportunitate. Și regula, ca să fie executabilă, cere UN element în plus pe care mandatul nu îl conține: CEASUL DECIZIEI.**

---

# PARTEA 1 — CONTRACTUL UNIC. Prima sarcină, înaintea oricărei cablări.

## 1.1 Tipul

```python
T = TypeVar("T")

@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T
    as_of: int            # indexul barei ÎNCHISE pe care s-a calculat
    valid_until: int      # exclusiv; dincolo de el nu se mai folosește
    schema_hash: str

@dataclass(frozen=True)
class Unavailable:
    reason: str           # motiv MAȘINĂ-LIZIBIL, nu text liber
    as_of: int
    # NU are `value`. NU are `schema_hash`. Absența e deliberată.

LevelOutput = Ok[T] | Unavailable
```

## 1.2 De ce impune `mypy --strict` — mecanismul exact, nu invocarea lui

**Îmi corectez o formulare proprie.** La v2.7.57 am scris că `mypy --strict` face din ramura lipsă „o eroare de tip". **Asta e adevărat doar dacă tipul e construit ca mai jos. Nu e o proprietate a lui `--strict`; e o proprietate a formei tipului.** Sunt două mecanisme, cu forță diferită:

```
(a) AUTOMAT, fără disciplină — `Unavailable` NU ARE atributul `value`.
    out: LevelOutput[RegimeState]
    out.value          ⇒  error: Item "Unavailable" has no attribute "value"
    Consumatorul NU POATE atinge payload-ul fără să restrângă tipul mai întâi.
    ACESTA e mecanismul portant. Nu se poate uita, pentru că nu se poate scrie.

(b) EXHAUSTIVITATE, cere o linie — `assert_never` pe ramura de cădere:
    match out:
        case Ok(): ...
        case Unavailable(): ...
        case _ as x: assert_never(x)
    Fără `assert_never`, mypy NU semnalează o ramură lipsă. CU el, adăugarea unui al
    treilea constructor devine eroare de compilare în TOATE consumatoarele.
```

> **Diferența contează: (a) protejează împotriva uitării de azi; (b) protejează împotriva extinderii de mâine. Se cer AMÂNDOUĂ, iar (b) trebuie scris, nu presupus.**

## 1.3 Ce se ȘTERGE — altfel contractul e decorativ

**Toate cele patru module au azi `status: str` CA ÂMP PE DATACLASS, alături de payload-ul care e populat oricum.** `zone_map._fail` întoarce `ZoneMap(zones=(), ..., status="unavailable")`; `zone_confirmation._fail` întoarce `ZoneConfirmationResult(confirmation=UNDETERMINED, ..., status="unavailable")`.

```
OBLIGATORIU: câmpul `status: str` se ȘTERGE din ZoneMap, ZoneConfirmationResult, BiasState, Axis.
Statusul devine CONSTRUCTORUL, nu un câmp. Două surse de adevăr = niciuna.
Un `status` păstrat „pentru compatibilitate" reintroduce exact defectul, prin ușa din spate.
```

## 1.4 Cele trei manifestări, rezolvate — și NICIUNA nu cere reproiectare

**L-U2 (N1).** `Axis(label, weights, confidence, status)` → `LevelOutput[Axis]`, iar `Axis` pierde `status`. Regimul devine `LevelOutput[RegimeState]`. Aritmetica EV nu poate atinge un `Unavailable`. **Zero schimbări de logică.**

**ZM-U1 (N3).** `Ok(ZoneMap(zones=()))` ≠ `Unavailable`. Mulțimea vidă redevine ce am specificat că e: **un rezultat**. **Zero schimbări de logică** — doar `_fail` întoarce `Unavailable` în loc de un `ZoneMap` gol.

**Z4-L1 (N4) — și aici corectez formularea acuzației, în favoarea codului.** Problema NU e că `UNDETERMINED = 0` stă la mijlocul scalei −2..+2. Am verificat cele două căi care produc 0:

```
_outcome_label(...)  nici acceptare, nici absorbție  → am MĂSURAT, e neutru.  0 e CORECT.
_fail(...)           fereastră incompletă, ATR absent → n-am putut măsura.    0 e FALS.
```

> **Ordinala 0 nu e greșită. Ea căra DOUĂ înțelesuri. „Calculat și neutru" merită legitim 0 — e informație. „N-am putut calcula" nu merită NICIUN număr.** Separarea în `Ok` / `Unavailable` le desface exact, iar enumerarea cu semn rămâne intactă. **Zero schimbări de logică, și nicio reproiectare a scalei.**

## 1.5 Descoperirea care nu era în niciun reziduu: MULȚIMEA NECESARĂ

**Codul conține azi TREI reguli de cascadă DIFERITE, niciuna declarată:**

```
bias_h1.py:163      `if all(s == UNAVAILABLE for s in regime_axes_status)`   ← TOATE axele
zone_map.py:156     `cascade_level1_or_level2_unavailable`                    ← ORICARE nivel
zone_confirmation   fail-closed pe orice precondiție lipsă                    ← ORICARE intrare
```

**Iar două componente sunt PERMANENT indisponibile prin construcție, verificat în cod:**

```
N1 axa ȘTIRI      `news_val, news_status = False, Status.UNAVAILABLE`   până la calendarul DA
N2 momentum       `Factor("momentum", None, UNAVAILABLE, "ABSENT_NO_RATIFIED_PRIMITIVE")`
```

> **Dacă regula de cascadă ar fi „orice `Unavailable` la intrare ⇒ `Unavailable` la ieșire", aplicată uniform, N1 ar fi PERMANENT indisponibil — axa știri nu devine disponibilă niciodată — și lanțul n-ar produce niciodată nimic. Fail-closed devine fail-MORT.**

**`bias_h1` a evitat capcana deja, cu `all` în loc de `any`. Dar a evitat-o TĂCUT, într-o linie de cod, nu ca regulă.** Deci:

```
Fiecare consumator declară o MULȚIME NECESARĂ explicită de intrări.
   · intrare în mulțimea necesară + `Unavailable`  ⇒  ieșire `Unavailable`, motiv PROPAGAT
   · intrare în afara ei + `Unavailable`            ⇒  se continuă, ABSENȚA SE ÎNREGISTREAZĂ
Mulțimea necesară intră în `schema_hash`. Nu e o alegere de implementare — e o alegere
de MODEL, și trebuie să fie vizibilă și înghețată ca oricare alta.
```

**Aceasta e singura parte a primei sarcini care adaugă ceva ce nu exista. Restul doar mută în tip ce era deja în intenție.**

---

# PARTEA 2 — DEFECTUL BLOCANT: `opportunity_id` nu identifică o oportunitate

**Regula CEO se sprijină integral pe „ACELAȘI `opportunity_id`". Am verificat cum se construiește azi:**

```python
zone = Zone(zone_id=f"zone@{as_of}", ...)      # zone_map.py, în `_assemble`
```

**Un id NOU la FIECARE bară M15 care se califică. Măsurat pe date reale, la pragul ratificat `THRESHOLD_K = 4`:**

```
bare M15 evaluate                        128.991
emisii N3 (k >= 4)                        55.170     42,77% din bare
run-uri de emisii CONSECUTIVE              7.206     lungime mediană 4 bare, p90 = 22, max 31
zone ECONOMICE distincte                  10.553     (emisii grupate pe preț, bandă 1xATR)
                                     ─────────────
RAPORT id-uri / zone reale                  5,23x
```

**Și concurența, măsurată pe fereastra N4 (W=60 bare M5 = 5h = 20 bare M15):**

```
id-uri NOI apărute cât timp fereastra unuia e deschisă:  mediană 15,  medie 13,3,  max 20
fracția emisiilor cu ZERO suprapunere:                    2,24%
```

> # **`zone@{i}` numește o BARĂ, nu o oportunitate.**
>
> **Aceeași zonă economică emite în medie 5,23 id-uri. În 97,76% din cazuri, fereastra de dovezi a unei „oportunități" e deschisă în timp ce N3 mai emite încă 15 id-uri, aproape toate despre ACELAȘI loc din preț.**

**Consecința pentru regula CEO, care e directă și fatală în forma actuală:**

```
„o oportunitate = un slot de familie"  devine  „o BARĂ = un slot de familie".
Iar N4 ar atașa dovezi celor 5,23 id-uri ale aceleiași zone, ca și cum ar fi cinci
oportunități independente. Nu sunt. Sunt cinci fotografii ale aceleiași.
```

**Aceasta e reproiectarea pe care mandatul o permite explicit („decât dacă integrarea descoperă un defect BLOCANT"). E minimă și NU atinge măsurătoarea lui N3 — atinge doar CHEIA:**

```
`opportunity_id` se cheiază pe GEOMETRIE + CICLU DE VIAȚĂ, nu pe indexul barei:
   · ancoră de preț + banda ratificată (1xATR) definesc IDENTITATEA;
   · o emisie care cade în banda unei oportunități DESCHISE nu creează un id nou —
     REÎMPROSPĂTEAZĂ oportunitatea existentă (`last_seen`), contorizat în audit;
   · oportunitatea se ÎNCHIDE explicit: consumată (D7, convenție deja ratificată), expirată,
     sau invalidată prin părăsirea benzii. Închiderea e un EVENIMENT, nu o absență.
Efectul măsurat al cheii: 55.170 → 10.553 oportunități. Factor 5,23.
```

**Nu propun un prag nou: banda de 1×ATR și D7 sunt amândouă deja ratificate. Cheia doar le APLICĂ identității, unde până acum nu erau aplicate.**

---

# PARTEA 3 — E REGULA COERENTĂ SUB NON-LOOKAHEAD? Da. Dar e SUBDETERMINATĂ.

## 3.1 Ce am verificat întâi: N4 e curat cauzal

```python
descriptor_available_idx = win_end + 1     # zone_confirmation.py:175
```

**Fereastra citește DOAR bare ≤ hit+W; descriptorul e declarat disponibil abia la hit+W+1. Nu există lookahead în N4. Problema nu e acolo.**

## 3.2 Regula CEO nu conține un CEAS. Fără el, are trei citiri, și doar una e legală

**„N6 e singurul nivel care decide" nu spune CÂND decide N6. Iar aici totul depinde de asta:**

```
(A)  N6 decide la momentul N3 (la atingere),  ȘI folosește descriptorul N4 în EV
     ⇒ descriptorul nu există încă. LOOKAHEAD. INTERZIS, fără nuanțe.

(B)  N6 decide la hit+W+1,  folosește descriptorul N4 în EV
     ⇒ CAUZAL CURAT. O singură decizie, o singură populație, UN slot de familie.
        Bifurcarea pe care am găsit-o DISPARE — nu prin unificare, ci pentru că
        brațul „intrare la atingere" e ȘTERS.

(C)  N6 decide la momentul N3,  N4 devine obiect POST-DECIZIE (management/audit)
     ⇒ CAUZAL CURAT. Intrarea rămâne la zonă. UN slot de familie.
        Dar N4 NU intră în decizia de intrare. Contribuie zero la „există trade?".
```

> **Regula e coerentă în (B) și în (C). Formularea din mandat le AMESTECĂ: „N4 atașează evidence" sugerează (B); „intrarea rămâne la momentul N3" impune (C). Nu pot fi amândouă. Modificarea cerută e MINIMĂ și e una singură: CEASUL DECIZIEI trebuie DECLARAT, unic per politică, și pre-înregistrat în `schema_hash`.**

**O interdicție care decurge, și care e cea mai ușor de încălcat fără să se observe:**

```
Ceasul NU are voie să depindă de dovadă.
  „decid la atingere dacă N4 e UNDETERMINED, altfel aștept hit+W+1"  =  ALEGEREA
  MOMENTULUI DE INTRARE PE BAZA VALORII DOVEZII. E selecție, și e mai rea decât
  lookahead-ul pentru că arată legal: fiecare braț e cauzal curat separat.
```

## 3.3 Cele cinci ore. Nu e o problemă de lookahead — e una de COMENSURABILITATE

**Întrebarea CEO e cea corectă, și răspunsul e mai dur decât „descriptorul e vechi". Am măsurat deplasarea, oarbă la direcție: `|c[hit+W] − c[hit]| / ATR`, pe cele 10.547 zone economice.**

```
p10  0,32x     p25  0,85x     MEDIANA  1,94x     p75  3,69x     p90  6,17x     medie 2,79x
> 1,0xATR: 71,09%          > 2,0xATR: 48,59%          > 3,0xATR: 32,45%
```

> **Banda zonei e 1,00×ATR. Mediana deplasării la sosirea dovezii e 1,94×ATR — aproape DE DOUĂ ORI lățimea obiectului despre care vorbește dovada. La hit+W+1, în 71,1% din cazuri prețul NU MAI E în zonă.**

**Deci descriptorul rămâne ADEVĂRAT — el descrie corect o fereastră încheiată. Ce expiră nu e adevărul lui, ci PERTINENȚA lui pentru o intrare la zonă. Formularea exactă:**

```
NU e stale în sensul pe care l-am definit la cadență (as_of/valid_until sunt respectate).
E NECOMENSURABIL: dovada e despre un LOC, iar prețul a plecat din acel loc.
```

**Consecință obligatorie, care nu e opțională în nicio citire:**

```
La `decision_ts`, N6 face o VERIFICARE DE VIABILITATE, înaintea oricărei aritmetici de EV:
      prețul mai e în banda oportunității?   NU ⇒ NO_TRADE, motiv `zone_left`,
      indiferent cât de bun e descriptorul N4.
Atriția asta se PRE-DECLARĂ, nu se descoperă: la W actual, 71,1% din oportunități
ajung la decizie fără zonă. E o proprietate a cablării, nu un rezultat.
```

---

# PARTEA 4 — CUM SE FOLOSEȘTE DESCRIPTORUL N4. Răspuns direct: NU ca N1 și N2.

**Întrebarea CEO: „ca input în EV, ca la N1 și N2? Sau altfel?" — Altfel, și motivul e statistic, nu estetic.**

```
N1, N2   descriu MEDIUL. Există la FIECARE bară, pentru fiecare oportunitate, necondiționat.
         A condiționa pe ele PARTIȚIONEAZĂ populația. Nimic nu se pierde.
N4       descrie OPORTUNITATEA ÎNSĂȘI. Există doar dacă a existat o penetrare
         (`if hit < 0: nu intră în populație` — verificat în cod) ȘI oportunitatea a
         supraviețuit până la hit+W.
         A condiționa pe el CENSUREAZĂ populația. Se pierde exact ce n-a ajuns acolo.
```

> **Un descriptor a cărui DISPONIBILITATE e determinată de evoluția oportunității nu e o coordonată de mediu. Dacă se tratează ca N1 și N2, celulele goale nu sunt „lipsă de date" — sunt un SUBSET SELECTAT, iar selecția e făcută de exact procesul pe care încercăm să-l măsurăm.**

**Deci, concret:**

```
1. N4 e o coordonată de ierarhie, dar OBLIGATORIU CEA MAI ADÂNCĂ (frunza). Niciodată
   deasupra lui N1/N2/N3 — altfel censurarea contaminează și estimările lor.
2. „Oportunitatea a murit înainte de dovadă" e o CELULĂ PROPRIE, nu o linie ștearsă.
   Se evaluează, nu se filtrează — instrumentul shadow/evaluate-everything, a cincea
   oară aceeași unealtă pentru aceeași clasă de problemă.
3. `Unavailable` de la N4 din motiv STRUCTURAL (fereastră incompletă, ATR absent) și
   `Unavailable` din motiv de PROCES (oportunitatea a părăsit banda) sunt motive
   DISTINCTE, mașină-lizibile, raportate separat. Primul e zgomot; al doilea e semnal
   despre populație și NU are voie să fie confundat cu el.
```

---

# PARTEA 5 — CE SE PIERDE. Inclusiv un lucru pe care regula îl face NEMĂSURABIL.

```
1. BRAȚUL „INTRARE LA ZONĂ" (dacă se alege ceasul (B)).
   Nu se pierde uniform: se pierd oportunitățile care se REZOLVĂ REPEDE. Cele 71,1%
   care au plecat peste 1xATR sunt exact cele care au făcut o mișcare. Pierderea e
   CORELATĂ cu magnitudinea mișcării — cel mai prost tip de pierdere posibil.

2. CONTRIBUȚIA LUI N4 LA DECIZIA DE INTRARE (dacă se alege ceasul (C)).
   N4 rămâne construit, testat, ratificat — și nefolosit pentru „există trade?".

3. RĂSPUNSUL LA „AJUTĂ CONFIRMAREA?".
   Două ipoteze ar fi costat două sloturi de familie, dar ar fi RĂSPUNS la întrebare.
   Una singură răspunde doar dacă varianta ALEASĂ funcționează.
```

> **Și consecința pe care o semnalez fiindcă e neplăcută și e a mea de spus: sub regula CEO, pierderea de la (1) e NEMĂSURABILĂ PRIN CONSTRUCȚIE.** A o măsura înseamnă a rula ambele brațe și a le compara — adică exact cele două ipoteze pe care regula le interzice. **Alegerea ceasului trebuie făcută A PRIORI, pe argument structural, și pierderea acceptată necuantificată. Nu există aici o variantă în care aflăm mai întâi și decidem după: a afla ESTE decizia.**

**Ce se CÂȘTIGĂ, ca să fie tabloul complet: familia rămâne la m=16 în loc să se dubleze pe politicile de zonă. Familia e MONOTONĂ — un slot consumat nu se mai recuperează. Regula CEO cumpără asta, și e o achiziție reală.**

---

# PARTEA 6 — O ALTERNATIVĂ DERIVATĂ, pe care o PROPUN, nu o adopt

**Dacă intenția e ca N4 să conteze la intrare ȘI intrarea să fie la zonă, cele două se pot împăca doar dacă fereastra de dovezi e comensurabilă cu obiectul. Am măturat W, orb la direcție:**

```
 W(M15)   ~M5   minute    mediană      încă în bandă
      1      3      15      0,42x            83,4%
      3      9      45      0,73x            62,6%
      5     15      75      0,94x            52,3%   <-- mediana ≈ banda; ocupanță ≈ 1/2
      8     24     120      1,20x            43,7%
     20     60     300      1,94x            28,9%   <-- W ACTUAL
```

> **La W ≈ 15 bare M5 (75 minute), deplasarea mediană (0,94×ATR) egalează lățimea zonei (1,00×ATR), iar oportunitățile se împart aproximativ în jumătate între „încă în bandă" și „plecată". Ancoră de ocupanță egală — a treia oară același instrument, reutilizat, nu inventat.**

**Trei precizări, ca să nu fie citit mai tare decât e:**

```
· NU e o potrivire pe rezultate. Nu conține direcție, intrare, ieșire sau randament.
  E o cerință de COMENSURABILITATE: dovada să sosească pe cât timp obiectul mai există.
· INTRĂ ÎN CONFLICT cu derivarea actuală. W=60 vine din orizontul de dependență de 5 ore
  (același care a justificat H=20 pe M15). Sunt DOUĂ criterii legitime care dau DOUĂ
  răspunsuri — orizontul de dependență spune 300 min, comensurabilitatea spune 75.
  Nu declar unul câștigător: e o decizie de model.
· NU O ADOPT UNILATERAL. Ar fi o schimbare de constantă la un nivel ÎNGHEȚAT, deci
  cere propriul traseu: Statistician specifică → VE → Red Team → CEO.
```

---

# PARTEA 7 — AUDITUL CAP-COADĂ. Ce se înregistrează per oportunitate.

**Obiectivul fazei cere „audit complet al contribuției fiecărui nivel". Un audit care nu poate arăta că un nivel N-A contribuit nu e audit.**

```
opportunity_id            cheie pe geometrie+ciclu (Partea 2), NU pe bară
created_at / last_seen / refresh_count / closed_at / close_reason
decision_ts               CEASUL declarat; egal pentru TOATE oportunitățile politicii
schema_hash               agregat peste N1..N4 + mulțimea necesară + ceas + W
─── per nivel, IDENTIC ca formă ───
  ok / unavailable        CONSTRUCTORUL, nu un string
  reason                  mașină-lizibil; la N4 obligatoriu STRUCTURAL vs PROCES
  as_of / valid_until
  in_required_set         bool — dacă absența lui ar fi trebuit să oprească lanțul
  used_by_n6              bool — A INTRAT în aritmetică, sau doar a fost prezent?
─── la decizie ───
  viability               în bandă la decision_ts? (motiv `zone_left` altfel)
  no_trade_reason         sentinel tipat, niciodată absența unui câmp
```

> **Câmpul `used_by_n6` e cel care face auditul verificabil în loc de descriptiv. Fără el, un nivel prezent și un nivel FOLOSIT arată identic în jurnal — iar contorul k de la N3, despre care am măsurat deja că e cvasi-constant și anti-informativ față de nul, ar apărea ca „a contribuit" la fiecare oportunitate.**

---

# PARTEA 8 — DELIMITARE

```
CE ACOPERĂ    forma contractului și a cablării; identitatea oportunității; coerența
              cauzală a regulii; ce se pierde structural.
CE NU ACOPERĂ dacă lanțul PRODUCE EDGE. Nimic din acest document nu e o afirmație
              despre rentabilitate. Verdictul formal 001 rămâne singura afirmație
              despre edge din proiect, și el e ZERO PROMOVĂRI.
              N5, N8, N9 — neatinse, conform mandatului.
              W=15 e PROPUS, nu adoptat. W=60 rămâne constanta în vigoare.
```

**Precedență, ca să nu existe ambiguitate în implementare: dacă cheia oportunității (Partea 2) nu se aplică, restul cablării e corectă pe un obiect greșit. Se face PRIMA, sau nu se face niciuna.**

---

**Manifest:** `config/split_manifest.json` v2.7.59, secțiunea `integration_phase_contract_and_wiring_v2_7_59`.
