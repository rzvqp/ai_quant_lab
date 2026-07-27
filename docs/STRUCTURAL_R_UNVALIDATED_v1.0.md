# LABEL — STRUCTURAL-R-UNVALIDATED (1544 hypotheses)

**Document ID:** STAT-STRUCT-R-UNVAL-v1.0 · **Autor:** Research Lab · **Data:** 2026-07-26
**Cerere:** Statisticianul (via CEO 2026-07-25) — etichetează ipotezele cu stop non-ATR ca **STRUCTURAL-R-UNVALIDATED** în documentație și în orice registru deținut. **NU proiecta remediul** (livrabil separat al Statisticianului).
**Registru:** `results/matched_null_validation/structural_r_unvalidated.json` (lista completă de ID-uri).

---

## Definiția și de ce eticheta contează
Aceste ipoteze **nu sunt „netestate"** și **nu sunt backlog generic.** Sunt **măsurate cu un instrument nepotrivit.**

**Raționamentul Statisticianului (potrivirea lui `R = pnl/risc`):**
- Stopul **ATR** are o **podea PRE-ÎNREGISTRATĂ** (`docs/MIN_STOP_FLOOR_PREREG.md`: `min_exec = max(2·spread, 5·tick, 0.10·ATR)`, iar setup-ul cere 1.5·ATR) care **mărginește varianța lui R prin construcție**. De aceea `matched_null@v1` validează **doar** acolo — nu e o limitare accidentală de scop, e o consecință a faptului că numitorul e mărginit.
- Stopul **structural** (și `ema`) **nu are podea analoagă** și poate fi **minuscul chiar prin definiția setup-ului** → varianța lui R e explozivă la risc→0.
- **Datele fine (M5/M1) NU rezolvă asta.** Măsoară mai bine numitorul, **nu îl mărginesc.** Nu e o problemă de măsurare, e o problemă de **definiție a variabilei de rezultat.**

**Distincția practică:** „netestat" sugerează că se rezolvă cu efort (date, calibrare). **STRUCTURAL-R-UNVALIDATED spune că NU se rezolvă cu efort pe R, indiferent de date sau de calibrare.** Poarta nu e mai multă muncă pe același instrument; e o decizie despre variabila de rezultat însăși.

## Domeniul de aplicare — 1544 din 1972
Eticheta = toate ipotezele cu **stop non-ATR** (fără podeaua care mărginește R):

| tip stop | count | | tip stop | count |
|---|---|---|---|---|
| structural | 592 | | ext | 48 |
| beyond_sweep | 576 | | struct | 52 |
| beyond_ext | 72 | | level | 32 |
| beyond_level | 48 | | prev_ext | 16 |
| bar | 48 | | ema | 12 |
| or_opp | 48 | | **TOTAL** | **1544** |

- **S1 integral (1152/1152)** + porțiuni structural-stop din S2-S20. Familii afectate: S1(1152), S2(72), S3(48), S5(48), S8(24), S10(24), S12(24), S16(20), S6/S9/S20(16), S4(16), S7-ema(12), S11/S13/S15/S17(12), S14(8).
- **NU** e inclus: regimul ATR-stop (428, validat) — inclusiv cele 412 pe care s-a rulat FDR-ul.
- **Distincție față de „~1560":** cele 16 ipoteze `atr`-stop-dar-n<25 sunt regim ATR (R mărginit) dar **ineligibile** (sub n≥25) — status **diferit** (ineligibil, nu R-unvalidated); nu sunt în această etichetă. 1544 (R-unvalidated) + 16 (ATR-ineligibil) + 412 (ATR-testat) = 1972.

## Relabel al framing-ului anterior
Ce documentele mele anterioare numeau „structural excluded / în afara domeniului validat / regim D2" (scoped-FDR, sizing, distribuție) = acum eticheta unică **STRUCTURAL-R-UNVALIDATED**. Închiderea D2 (WP-1..4) a curățat statistica R pe aceste ipoteze, dar **nu** a schimbat eticheta: R rămâne nepotrivit ca variabilă acolo (D2 e necesar dar nu suficient; vezi `D2_CLOSURE_SIZING_v1.0.md` Q3).

## Consecință de dimensiune (semnalată, nu remediată)
După închiderea D2, regimul STRUCTURAL-R-UNVALIDATED are **426** ipoteze net-profitabile (nu 357) și rămâne netestabil pe R. Numărul mai mare **nu** schimbă eticheta — schimbă doar cât de mult stă în afara instrumentului.

**NU proiectez remediul.** Definirea unei variabile de rezultat potrivite pentru regimul structural e livrabil separat al Statisticianului. Research Lab a aplicat doar eticheta. Holdout SEALED.
