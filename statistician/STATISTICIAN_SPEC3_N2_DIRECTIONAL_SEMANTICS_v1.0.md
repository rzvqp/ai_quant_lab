# SPEC 3 — N2: SEMANTICA DIRECȚIONALĂ. CORECȚIE FUNCȚIONALĂ

**Document ID:** STAT-SPEC3-N2-DIRECTIONAL-SEMANTICS-v1.0 · **Data:** 2026-08-11 · **Autor:** Statistician
**Obiectiv mărginit:** LONG / SHORT / UNKNOWN utilizabil de N6. **Atât.**
**Verificare de sursă:** citit `bias_h1.py`, funcția `compute_bias`, toți cei patru factori.

---

## 1. DEFECTUL DE ROL

**N2 emite `Factor(name, value, status, primitive)` cu `value` numeric brut: `structure_run_h1 = −7,0`, `displacement_h1 = 1,0`, `liquidity_above = 3,0`. N6 ar trebui să știe singur ce înseamnă semnul fiecăruia. Semantica există doar în capul cititorului, deci nimeni nu o consumă.**

## 2. MAPAREA, per factor. Fără agregare, fără procent.

```
structure_run_h1     run cu semn (market_structure.detect_breaks)
    > 0   → LONG          < 0   → SHORT          == 0 → UNKNOWN (măsurat, run nul)
    Semnul e INTRINSEC primitivei. Nicio asumpție.

displacement_h1      ±1 la expansiune, 0 fără expansiune (market_state.expansion)
    +1,0  → LONG         −1,0  → SHORT          0,0  → UNKNOWN (măsurat: nicio expansiune)
    Semnul e INTRINSEC. `0,0` e REZULTAT, nu absență → `Ok(UNKNOWN)`, NU `Unavailable`.
    Exact lecția Z4-L1: măsurat-și-neutru merită o stare; n-am-putut-măsura nu merită.

liquidity_above      număr de bazine NECONSUMATE deasupra (liquidity_mechanics.build_pools)
    > 0   → SHORT evidence, prin POLARITATE DECLARATĂ         == 0 → UNKNOWN
    `status = UNAVAILABLE` (contor negativ) → `Unavailable(reason=...)`
    ⚠ Semnul NU e intrinsec. Vezi §3.

momentum             ABSENT_NO_RATIFIED_PRIMITIVE
    → `Unavailable(reason="ABSENT_NO_RATIFIED_PRIMITIVE")`, PERMANENT.
    OBLIGATORIU în afara mulțimii necesare a lui N2, altfel N2 nu e disponibil niciodată.
```

## 3. SINGURA ASUMPȚIE, declarată în loc să fie îngropată

**CEO a întrebat deja: „lichiditate deasupra ca factor NEGATIV — de unde vine?" Răspunsul cinstit: dintr-o teză, nu dintr-o măsurătoare. Lichiditatea neconsumată deasupra e la fel de plauzibil o ȚINTĂ (magnet, deci LONG) cât o REZISTENȚĂ (deci SHORT).**

```
Se emite cu polaritate DECLARATĂ, marcată ca atare:
    Factor(name="liquidity_above", direction=SHORT, assumption=True,
           assumption_id="LIQ-ABOVE-POLARITY-v1")
`assumption=True` intră în `schema_hash`.
```

> **Marcajul nu rezolvă asumpția — o face ATACABILĂ. Red Team poate ținti eticheta; fără ea, ar trebui întâi s-o descopere. Nu proiectez testul care ar decide polaritatea: ar fi scop nou, și nu e necesar pentru milestone.**

## 4. CE EMITE N2, exact

```python
@dataclass(frozen=True)
class FactorDirection:
    name: str
    direction: Direction            # LONG | SHORT | UNKNOWN   ← enum, NU un număr cu semn
    raw: LevelOutput[float]         # valoarea, sub contract — pentru audit, nu pentru decizie
    primitive: str
    assumption: bool                # True doar pentru liquidity_above
```

```
BiasState emite:  factors: tuple[LevelOutput[FactorDirection], ...]
                  direction_share_long / short   — DESCRIPTIVE, neschimbate, NU o previziune
NU emite:         procent final, scor, sau vreo agregare. Aceea e a lui N6.
Mulțimea necesară a lui N2: {structure_run_h1}.  displacement și liquidity sunt opționale;
momentum e OBLIGATORIU în afara ei. Fără asta, N2 e permanent indisponibil → fail-mort.
```

**`UNKNOWN` (măsurat, fără direcție) și `Unavailable` (necalculabil) sunt stări DIFERITE și rămân distincte prin tip. Nu se acceptă `0 = unknown`, nici `neutral = unavailable`.**

## 5. CE RĂMÂNE DESCHIS

```
MATERIAL      polaritatea lui `liquidity_above` e o ASUMPȚIE declarată, nu un fapt măsurat.
              Marcată, hash-uită, atacabilă. Testul care ar decide-o: AMÂNAT — scop nou.
LIMITATION    N2 rămâne cu 3 factori utilizabili din 4. `momentum` cere o primitivă ratificată
              care nu există. Nu se substituie nimic în locul lui.
LIMITATION    `structure_run_h1 == 0` și `displacement_h1 == 0,0` sunt UNKNOWN prin măsurătoare.
              Frecvența lor nu e măsurată aici — dacă domină, N2 e tăcut mai des decât pare.
              MĂSURABIL de VE la implementare, cu o singură numărătoare.
NON-MATERIAL  regula de agregare a celor trei direcții rămâne la N6, nespecificată aici,
              conform mandatului. N2 nu emite procent.
```

**Nu cere: gate nou, framework nou, primitivă nouă, nivel nou, nicio refactorizare dincolo de tipul de ieșire. Cei patru factori se calculează exact ca acum.**
