# M15 — DIAGNOSTIC AL CELOR 196 NEPOTRIVIRI (Opțiunea 1)

**Concluzie:** defect de puller — **bara de la cursorul de replay (marginea dreaptă / ultima bară a
fiecărei ferestre) e capturată cu close+volum provizorii.** NU e revizuire de sursă. Confirmat de trei
teste independente. Nimic corectat, nicio versiune aleasă, nimic integrat.

## TEST A — granițe de fereastră (decisiv)

Re-tragere instrumentată pe overlap; re-tragerea == staged pe 100% din 84.152 bare (reproduce fidel
structura de ferestre). Distribuția nepotrivirilor după poziția în fereastră:

| edgeFromRight | #bare | #nepotriviri | rată |
|---|---|---|---|
| **0 (margine dreaptă)** | 281 | **195** | **69,4%** |
| 1 | 281 | 0 | 0% |
| 2 | 281 | 0 | 0% |
| 3+ (interior) | 83.309 | 1 | 0,001% |

Raport margine/interior ≈ **57.800×**. 99,5% din nepotriviri sunt exact bara-cursor. Fereastră = 300 bare.

## TEST B — arbitraj prin citire interioară (nativul M15 nu panează, doar replay)

Fiecare bară nepotrivită recitită ca **interior** (cursor la T+3h), unde valoarea e finală:

- **11/12** → valoarea finală == **EXISTENT** (marginea mea era provizorie).
- **1/12** (2026-07-13 06:00) → valoarea finală == **STAGED** (acolo *existentul* avea bara provizorie —
  ultima lui bară, pe care niciun gap-fill ulterior n-o mai putea corecta).

## TEST C — două fenomene, separate

| |delta| volum | #bare |
|---|---|---|
| 1-10 | 103 |
| 11-100 | 90 |
| 101-1000 | 2 |
| 1001-10000 | 1 |

- 195 = revizuiri provizoriu→final minuscule (mediană 9 volum; close ≤0,2 la 176/196).
- 1 = delta uriașă (5263) = ultima bară provizorie a **existentului** (2026-07-13, vol 8201→13464).

## Artefactul documentat — clue fals

Barele de la 2026-01-29 (Observation Registry entry 17, inclusiv volumul-record 53.832) sunt
**identice bit-cu-bit** în existent și nou (MATCH). „0" din CHECK 5 apărea în **ambele** fișiere fiindcă
semnătura dată (120-136pt @ vol **748-3980**) nu descrie barele reale (volum mare, nu 748-3980).
**Artefactul nu a dispărut**; observația lui Alpha se referă la date intacte. Fără problemă de
provenanță acolo.

## Consecințe (semnalate, nerezolvate)

1. **Defectul e pe tot fișierul**, inclusiv cei 11 ani virgini: ~1 bară provizorie la fiecare 300
   (~1.186 în total), tăcută, fără referință de detecție acolo.
2. **Existentul laboratorului e în esență curat**: valorile interior sunt finale (== recitire); doar
   bara lui terminală (2026-07-13) e provizorie. Munca de până acum pe 2022-12-16+ nu e afectată de
   acest defect, cu excepția eventuală a acelei bare terminale.
3. **Datele sunt recuperabile curat**: valoarea interior e demonstrat corectă (== existent). Un fix de
   puller — ferestre suprapuse, astfel încât fiecare bară să fie citită cel puțin o dată ca interior
   (sau aruncarea barei-cursor și re-acoperirea ei de fereastra următoare) — ar produce date fără
   defect. Fix-ul de seek deja commis (5accefd) e separat: el a permis mersul până la podea, dar nu
   atinge bara-cursor provizorie. Acesta e un al doilea defect, distinct.

**Nu implementez fix-ul, nu re-trag, nu aleg versiune, nu propun standard, nu încep M5. Aștept decizia.**
