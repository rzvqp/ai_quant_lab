# F4.2 — RAPORT: FIX CELULE DC-0004 (EVENIMENT COMPLET) + A TREIA DISCREPANȚĂ
### Corecția F4-2 aplicată și confirmată EXACT; discrepanță nouă F4-3 la baseline — OPRIRE

**Document ID:** VE-F42-CELLFIX-v1.0
**Data:** 2026-07-25 · **Autor:** Validation Engine
**Autoritate:** CEO 2026-07-25 — autorizat EXCLUSIV corecția definiției celulelor (marker → eveniment complet).
**Statut:** corecție aplicată și confirmată exact. **A treia discrepanță (F4-3, baseline) descoperită la verificarea „orice altă diferență" — OPRIT pentru raportare, conform instrucțiunii.**

---

## 1. Corecția autorizată (F4-2) — aplicată

Celulele DC-0004 stabilesc acum direcția prin **evenimentul complet**, exact ca în scriptul Alpha:

| Direcție | Definiția celulei (conjuncție, pe aceeași bară) |
|---|---|
| **up** | `in_session(s)` ∧ `first_in_scope(day, high>PDH)` ∧ `close<PDH` |
| **down** | `in_session(s)` ∧ `first_in_scope(day, low<PDL)` ∧ `close>PDL` |

Markerul simplu `high>pdh` / `low<pdl` a fost eliminat. Filtrul de sesiune se aplică pe aceeași bară a evenimentului.

**Modificat:** `tests/fixtures/reference_spec_dc0004.json` (celulele T1_k6 și T2_k12) și `tests/fixtures/dev_spec_open_window.json` (confirmare). **Motor, registru, schema, validator — neatinse** (hash-uri identice). DC-0004 oficial validează cu 4×E3, zero non-E3.

---

## 2. Confirmarea împotriva obs0012 — POTRIVIRE EXACTĂ

Materializat pe fereastra deschisă completă (identică cu obs0012), holdout neatins.

| Celulă | VE (materializat) | obs0012 (Alpha) | Potrivire |
|---|---|---|---|
| asia_up | 135 | 135 | ✅ |
| london_up | 34 | 34 | ✅ |
| ny_up | 42 | 42 | ✅ |
| asia_dn | 114 | 114 | ✅ |
| london_dn | 40 | 40 | ✅ |
| ny_dn | 47 | 47 | ✅ |

- **Valorile 135/34/42/114/40/47 — confirmate exact.** ✅
- **Aceleași 6 celule eligibile** (n≥25): asia/london/ny × up/dn; **m = 6.** ✅
- **Celulele „late" excluse** (n=9<25). ✅
- **Total interacțiuni reject = 430** — identic cu `obs0003` („reject interactions: 430"). ✅

Populația și familia empirică ale DC-0004 se reproduc **integral și exact**.

---

## 3. Verificarea „orice altă diferență" — A TREIA DISCREPANȚĂ (F4-3)

La compararea baseline-ului per sesiune cu scripturile Alpha:

- **obs0008/0012** calculează baseline-ul = media forward K6 pe **TOATE** barele sesiunii (inclusiv barele-eveniment): `base = mean(fwd(i,K) for i in session_bars)`.
- **Specificația DC-0004** declară `baseline_forward_mean.exclude_event_bars: True` — adică ar exclude barele-eveniment.

Aceasta este o **diferență de definiție a baseline-ului** față de in-sample.

Observație tehnică: la F4, valoarea materializată a baseline-ului **coincide** cu obs, pentru că implementarea curentă a `baseline_forward_mean@v1` **nu implementează** `exclude_event_bars` (include toate barele). Deci:
- specificația **declară** `exclude_event_bars: True` (≠ obs);
- motorul **ignoră** parametrul și include toate barele (= obs).

Rezultă două aspecte cuplate:
1. **F4-3 (specificație):** `exclude_event_bars` ar trebui `False` pentru fidelitate cu obs;
2. **latent (motor):** `baseline_forward_mean@v1` nu implementează `exclude_event_bars` — dacă ar fi `True` și implementat, baseline-ul ar diferi de obs.

Baseline-ul este o **intrare a statisticii de test** (excess = forward − baseline), deci diferența se manifestă la **F5**, când se calculează statistica. Populația și familia (livrabilul F4) se reproduc exact.

---

## 4. Concluzie și oprire

Conform instrucțiunii CEO — „verifică dacă mai există orice altă diferență; dacă apare altă diferență, oprește-te și raportează":

1. **Corecția autorizată (F4-2) este aplicată și confirmată EXACT** — 135/34/42/114/40/47, 6 celule eligibile, m=6, total 430. Populația și familia DC-0004 se reproduc integral.
2. **A apărut o a treia discrepanță (F4-3)** — declarația `exclude_event_bars: True` din baseline diferă de obs (care include barele-eveniment). **Nu am rezolvat-o** (depășește corecția autorizată a celulelor).
3. **La nivel de populație/familie, DC-0004 reproduce acum EXACT experimentul in-sample.** La nivel de baseline (statistică F5), rămâne discrepanța F4-3.

Ambele corecții și discrepanța sunt în `VE_BACKLOG.md` §2.06 (F4-1 REZOLVAT, F4-2 REZOLVAT, F4-3 CONSEMNAT).

---

## 5. Ce s-a modificat / ce nu

**Modificat:** `tests/fixtures/reference_spec_dc0004.json` (celule → eveniment complet), `tests/fixtures/dev_spec_open_window.json`, `VE_BACKLOG.md`, acest raport.
**Neatins (hash verificat):** vocabular, registru (`capabilities.json` `fb78b935…`), schema (`f1ba7009…`), validatorul, **codul motorului** (`materialize.py`, `materializer.py` — hash-uri identice cu starea aprobată F4), cele 4 surse de date (holdout inclus).
**Teste:** 389 passed. Metode `UNVALIDATED` 15/15; registru `PUBLISHED_NOT_EXECUTABLE`.

---

**Validation Engine se oprește aici. Corecția celulelor (F4-2) reproduce EXACT populația și familia in-sample (135/34/42/114/40/47, m=6, total 430). Dar verificarea „orice altă diferență" a descoperit F4-3 (baseline `exclude_event_bars`) — o diferență la nivel de statistică. Aștept decizia CEO asupra F4-3 înainte de raportul final de închidere F4 și înainte de autorizarea F5.**
