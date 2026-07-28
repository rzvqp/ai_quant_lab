# Mandat 5.7 — Pasul 3: înghețarea definițiilor Order Block + Liquidity Void

**Rol:** Validation Engine (executiv). Am înghețat în cod cele două definiții RATIFICATE de Statistician
(manifest v2.5.9, `444e0e8`) și am raportat NUMĂRĂTOAREA MEA de Liquidity Void pe fișierul canonic cu
criteriul exact. Nu am proiectat, interpretat sau emis verdicte.

Cod: `code/order_block_void.py` (pur, mypy `--strict` curat, nu citește prețuri, inert).

---

## 1. Liquidity Void — definiție înghețată + numărătoarea MEA

**Criteriu hibrid ratificat** (o tranziție c→c+1 e Void dacă ORICARE):
- **(temporal)** `time[c+1] − time[c] > 900s`, EXCLUZÂND fereastra de mentenanță zilnică
  (`gap ≤ 75min ȘI ora(time[c]) ∈ {20,21} UTC`) — reutilizat **verbatim** din `code/gapfind.py`
  (linia `if mins<=75 and t0.hour in (20,21): continue`). **Weekend-urile sunt INCLUSE** (redeschiderile
  de weekend = void-uri temporale legitime, per `why_hybrid`).
- **(mărime)** `|Open[c+1] − Close[c]| > $1.20` (= 3 × cost_round_trip $0.40, prag **derivat**, nu ales).

**Fișier canonic:** `data/market/OANDA_XAUUSD_M15__SUPERSEDED_v1_2022-12-16_to_2026-07-13_R03terminal.csv`
(84.152 bare, deduplicat pe `time`, sortat crescător).

### Numărătoarea MEA (criteriul exact de mai sus)

| Categorie | Count |
|---|---|
| doar-mărime | **248** |
| doar-timp | **119** |
| ambele | **96** |
| **TOTAL tranziții calificate** | **463** |
| — total mărime (doar-mărime + ambele) | 344 |
| — total temporal (doar-timp + ambele) | 215 |

### Reconcilierea discrepanței de numărătoare

Numărătoarea mea reproduce **EXACT** decompoziția Statisticianului (248 / 119 / 96 = 463).

Discrepanța mea ANTERIOARĂ (24 doar-mărime / 602 doar-timp / 320 comune) provenea **integral din convenția
temporală**, nu din criteriul de mărime:
- vechea convenție folosea „gap > 1 bară" fără excluderea ferestrei de mentenanță → număra fiecare pauză
  zilnică de ~1h ca void temporal (→ 602 doar-timp umflat);
- criteriul înghețat exclude explicit mentenanța (`mins≤75 & hour∈{20,21}`) → 119 doar-timp.

Criteriul de mărime era identic în ambele; diferența de doar-mărime (24 vs 248) e un artefact de
clasificare: sub vechea convenție temporală permisivă, 320 dintre gap-urile de mărime cădeau și în categoria
temporală („ambele"), lăsând doar 24 „doar-mărime"; sub criteriul strict, majoritatea acelor tranziții nu
mai sunt temporale, deci reapar corect ca „doar-mărime". Totalul de mărime (344) e stabil între convenții.

**Concluzie de reconciliere:** singura sursă de divergență a fost excluderea ferestrei de mentenanță în
ramura temporală. Cu criteriul ratificat aplicat verbatim, numărătoarea mea și a Statisticianului coincid
la nivel de categorie.

---

## 2. Order Block — definiție înghețată (2 corecții + separarea ferestrelor)

**ZONA = CORPUL, `[min(Close,Open), max(Close,Open)]`** (bearish: `Close_Bdown .. Open_Bdown`).
NU `[Open, Low]` (corp+fitil): fitilul are rol EXCLUSIV de atingere (D6); includerea lui ar face
„atingerea OB" ambiguă. Implementat în `order_block_zone()`.

**Separarea structurală a ferestrelor** (pre-întâmpină circularitatea E010 prin CONSTRUCȚIE, nu prin
verificare adăugată):

1. **Fereastra de VALABILITATE** — OB activ de la formare până la PRIMUL dintre:
   - **(a)** atingere de FITIL în zonă (consumare analog D7: o dată, fără re-armare), SAU
   - **(b)** CLOSE decisiv dincolo de zonă → devine „breaker" (verbatim criteriul de inversare E010/E012).
   - (a) și (b) sunt evenimente **DIFERITE**; (a) NU implică (b).
2. **Fereastra de MĂSURARE** — începe DOAR la bara evenimentului calificator (a) sau (b), **niciodată la
   formare**. Orizontul grupei A (20 bare) rulează înainte DE ACOLO.
   - Prin construcție, cele două ferestre nu pot colapsa în aceeași (spre deosebire de E010, unde erau
     identice → circularitate).

Structuri înghețate: `OrderBlock` (zonă = corp), `ObValidityEvent` (fereastra de măsurare pornește de la
`event_idx`, se termină la `event_idx + 20`).

### Întrebare deschisă (enumerată, NErezolvată — semnalată, nu decisă de mine)

Criteriul de **FORMARE** al OB (care lumânare DEVINE un OB) NU e specificat în definiția ratificată — doar
ZONA și separarea ferestrelor sunt. `resolve_validity_and_measurement()` ridică `NotImplementedError`:
declanșarea (a)/(b) depinde de criteriul de formare (întrebare deschisă) + direcția „dincolo de zonă" per
tip. Zona și structura ferestrelor sunt înghețate; detectarea autonomă a OB rămâne blocată până la
ratificarea criteriului de formare. **Nu am inventat un criteriu de formare.**

---

## Note de guvernanță

- Numărătoarea Void a citit prețuri reale din fișierul canonic SUPERSEDED — audit structural (clasificare
  de tranziții), fără P&L, fără backtest, fără direcție/outcome LM-001. Conform disciplinei de audit
  structural (identic cu auditul de densitate/geometrie).
- `order_block_void.py` e cod PUR: nu citește prețuri, nu apelează `load()`. Numărătoarea s-a făcut într-un
  script efemer separat care importă detectorul.
- Tensiune CROSS_VERIFICATION_SPEC: modulul de definiții e cod persistent care va citi prin masca sigură a
  manifestului la utilizare — de semnalat dacă devine parte a pipeline-ului de verificare (caveat standard).
