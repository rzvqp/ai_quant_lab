# AMENDAMENT DE INTERPRETARE — SCOPED GLOBAL-FDR (`ea36005`)
### De atașat de Research Lab ca addendum datat la `docs/SCOPED_FDR_PREREGISTRATION_v1.0.md` — nu edit al originalului

**Document ID:** STAT-SCOPED-FDR-INTERP-AMD-v1.0
**Data:** 2026-07-25 · **Autor:** Statistician
**Statut:** Amendament obligatoriu de interpretare, fixat înainte de rulare. Nu modific pre-înregistrarea originală — aceasta se atașează separat, conform convenției deja stabilite în lab (addenda datate, niciodată edit al documentului înghețat).

---

## Constrângerea de interpretare

**Rezultatul acestei runde — indiferent de semn — NU poate fi formulat ca "nimic nu supraviețuiește în corp" sau echivalent.**

**Formularea corectă, singura permisă:** *"Nimic nu supraviețuiește printre cele 412 ipoteze cu stop ATR, testate la pragul BH 1,2136×10⁻⁴."*

## De ce

Universul eligibil total (n≥25, peste toată gramatica) e **1.944** de ipoteze (412 ATR-stop + 1.532 stop structural). Subsetul testat acum acoperă **412/1.944 ≈ 21,2%** din acel univers. Celelalte **1.532 (≈78,8%)**, cu stop structural (regimul D2), sunt **invizibile prin construcție în această rundă** — nu pentru că au fost testate și au eșuat, ci pentru că motorul matched-null nu e calibrat pe acel regim și nu a fost rulat pe el deloc.

Aceasta nu e o critică a design-ului — scoparea e corectă tocmai pentru că rulezi testul unde e validat. Dar înseamnă că un rezultat "zero supraviețuitori" la cele 412 spune zero lucruri despre celelalte 1.532.

## De ce se fixează acum, nu după

Peste șase luni, cineva care deschide doar `docs/SCOPED_FDR_RESULT_v1.0.md` (rezultatul) fără acest amendament va citi "zero supraviețuitori" ca verdict asupra întregului corp S1-S51. Distincția între "am testat tot corpul și n-a supraviețuit nimic" și "am testat 21% din corp, restul rămâne netestat" trebuie să fie imposibil de ratat, nu dedusă din context.

## Text obligatoriu de inclus în orice raport de rezultat

> Acest rezultat privește exclusiv cele 412 ipoteze cu stop ATR (regimul validat). Cele 1.532 ipoteze cu stop structural (regimul D2) nu au fost testate în această rundă și rămân complet nedeterminate statistic. Un rezultat nul aici nu constituie infirmare pentru acele 1.532.

## Relație cu constatarea (5b) și cu analiza de putere (Sarcina 1)

Această limită de interpretare e distinctă de, dar complementară cu, limita de putere din `STATISTICIAN_POWER_ANALYSIS_SPEC_BH_THRESHOLD_v1.0.md`: aceasta din urmă spune ce nu se poate exclude *în interiorul* celor 412 (efecte sub MDES); aceasta de față spune ce nu se poate exclude *în afara* celor 412 (întreg regimul structural). Ambele trebuie citate împreună la orice raportare a rezultatului.

---

**Nu am modificat `docs/SCOPED_FDR_PREREGISTRATION_v1.0.md`. Acesta e un document separat, de atașat.**
