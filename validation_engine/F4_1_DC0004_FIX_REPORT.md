# F4.1 — RAPORT: FIX DC-0004 (PDH→H1) + CONFIRMARE ÎMPOTRIVA IN-SAMPLE
### Modificarea autorizată aplicată; a doua discrepanță descoperită — OPRIRE

**Document ID:** VE-F41-DC0004FIX-v1.0
**Data:** 2026-07-25 · **Autor:** Validation Engine
**Autoritate:** CEO 2026-07-25 — autorizat EXCLUSIV fix-ul PDH/PDL D1→H1 pe specificația oficială DC-0004.
**Statut:** fix aplicat și verificat. **A doua discrepanță (F4-2) descoperită la confirmare — OPRIT pentru raportare, conform instrucțiunii. DC-0004 NU reproduce încă integral experimentul in-sample.**

---

## 1. Modificarea autorizată — aplicată

| Element | Înainte | După |
|---|---|---|
| `pdh.params.source_id` | `OANDA_XAUUSD_D1@v1` | **`OANDA_XAUUSD_H1@v1`** |
| `pdl.params.source_id` | `OANDA_XAUUSD_D1@v1` | **`OANDA_XAUUSD_H1@v1`** |
| `pdh/pdl.availability.source_id` | D1 | H1 |
| `data` | H1 + D1 | **H1** (D1 devenit nefolosit, eliminat) |
| `spec_version` | 4.0 | 4.1 |

PDH/PDL se derivă acum din H1 grupat pe zi calendaristică UTC, cu `shift(periods_back)` — identic cu `_lab.add_prior_day` din scripturile Alpha (`df.groupby(df.dt.date).high.max().shift(1)`).

**Doar specificația oficială DC-0004 a fost modificată.** Verificat prin hash, neatinse:
- vocabular / registru (`capabilities.json` `fb78b935…`);
- schema (`SPEC_SCHEMA_v1.0.json` `f1ba7009…`);
- validatorul (`registry_validator.py` `4a6239bd…`);
- codul motorului (`materializer.py`, `domains.py` — hash-uri identice cu starea aprobată F4).

DC-0004 oficial validează în continuare cu 4×E3 (porți de calibrare), zero non-E3.

---

## 2. Reconstruirea populației (fereastra deschisă = datele in-sample)

Materializat metodologia DC-0004 pe **fereastra deschisă completă** (2023-01-02T23:00 → 2025-10-23T09:15, identică cu intervalul obs0012). Holdout neatins (`max_ts_read = 2025-10-23T09:00:00Z < graniță`, `sealed_window_touched = False`).

Adevăr de referință obținut rulând **scriptul Alpha `obs0012`** (in-sample):
```
cells tested=6 | Bonferroni thr=0.05/6=0.0083
up/ny 42 · up/london 34 · up/asia 135 · down/london 40 · down/asia 114 · down/ny 47
```

---

## 3. Confirmarea familiei empirice — IDENTICĂ

| | Validation Engine (materializat) | obs0012 (Alpha) | Potrivire |
|---|---|---|---|
| Celule eligibile (n≥25) | asia_up, asia_dn, london_up, london_dn, ny_up, ny_dn | idem | ✅ **identic** |
| `m` (mărimea familiei) | 6 | 6 | ✅ |
| Prag Bonferroni | 0.05/6 = 0.0083 | 0.0083 | ✅ |
| Celule excluse (n<25) | late_up, late_dn | late (sub prag) | ✅ |

**Familia empirică se reproduce integral** — aceleași 6 celule, m=6, aceleași celule excluse.

---

## 4. Distribuția pe sesiuni — O A DOUA DISCREPANȚĂ (F4-2)

Deși familia e identică, **n per celulă diferă** consistent:

| Celulă | VE (marker actual) | obs0012 | VE (definiție completă) |
|---|---|---|---|
| asia_up | 140 | **135** | **135** ✅ |
| london_up | 39 | **34** | **34** ✅ |
| ny_up | 43 | **42** | **42** ✅ |
| asia_dn | 128 | **114** | **114** ✅ |
| london_dn | 43 | **40** | **40** ✅ |
| ny_dn | 50 | **47** | **47** ✅ |

**Cauza (diagnosticată exact):** celulele DC-0004 marchează direcția prin `compare(high>pdh)` (up) / `compare(low<pdl)` (down), nu prin **evenimentul complet de reject**. **35 de bare de populație sparg AMBELE direcții** (high>PDH ȘI low<PDL); markerul ușor numără un eveniment down-reject și în celula up (și invers), supraestimând n.

**Dovadă:** înlocuind markerul cu definiția completă a evenimentului în celulă — `first_in_scope(high>pdh) ∧ close<pdh ∧ in_session(s)` — n-urile se potrivesc **EXACT** cu obs0012 (coloana din dreapta: 135/34/42/114/40/47).

**F4-2 nu este:**
- un gol de vocabular — definiția completă a celulei este exprimabilă (verificat);
- un defect de motor — motorul numără corect ce i se cere.

**F4-2 este** o eroare de definiție a celulelor în specificația oficială DC-0004 (marker de direcție în loc de eveniment complet).

---

## 5. Concluzie și oprire

Conform instrucțiunii CEO — „confirmă că nu apare nicio altă diferență față de scripturile Alpha; dacă mai apare orice discrepanță, oprește-te și raportează":

1. **Fix-ul autorizat (F4-1, PDH→H1) este aplicat și corect** — a adus familia empirică la identitate cu in-sample.
2. **A apărut o a doua discrepanță (F4-2)** — definiția celulelor prin marker de direcție supraestimează n per celulă. **Nu am rezolvat-o** (depășește modificarea autorizată).
3. **DC-0004 NU reproduce încă INTEGRAL experimentul in-sample** — familia e identică, dar populația per celulă diferă până la corecția F4-2.
4. Am **dovedit** că o singură corecție suplimentară (celule: marker → eveniment complet) aduce reproducerea la **potrivire exactă** cu obs0012.

Ambele discrepanțe sunt înregistrate în `VE_BACKLOG.md` §2.06 (F4-1 REZOLVAT, F4-2 CONSEMNAT).

---

## 6. Ce s-a modificat / ce nu

**Modificat:** `tests/fixtures/reference_spec_dc0004.json` (fix PDH→H1, autorizat), `tests/fixtures/dev_spec_open_window.json` (fereastră de confirmare aliniată la obs0012), `VE_BACKLOG.md`, acest raport.
**Neatins (hash verificat):** vocabular, registru, schema, validator, codul motorului, cele 4 surse de date (holdout inclus).
**Teste:** 389 passed. Metode `UNVALIDATED` 15/15; registru `PUBLISHED_NOT_EXECUTABLE`.

---

**Validation Engine se oprește aici. Fix-ul PDH→H1 este confirmat corect; familia empirică se reproduce integral; dar o a doua discrepanță (F4-2, definiția celulelor) împiedică reproducerea integrală. Aștept decizia CEO asupra F4-2 înainte de orice altă modificare — și confirmarea integrală a DC-0004 înainte de autorizarea F5.**
