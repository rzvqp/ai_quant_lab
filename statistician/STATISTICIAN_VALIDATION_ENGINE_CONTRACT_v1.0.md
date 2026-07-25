# STATISTICIAN ↔ VALIDATION ENGINE CONTRACT v1.1
### Interfața oficială dintre proiectarea și execuția validării statistice

**Document ID:** STAT-VE-CONTRACT-v1.1
**Data ratificării:** 2026-07-24 (v1.0) · **Amendat:** 2026-07-25 (v1.1, §5) · **Autoritate:** CEO / Arhitect Șef sub delegare CEO
**Statut:** Contract oficial, permanent. Stă la baza definirii Validation Engine și guvernează orice interacțiune viitoare dintre Statistician și Validation Engine, pentru orice Discovery Candidate — **și, din v1.1, certificarea agregată a rezultatelor de campanie statistică (ex. global-FDR peste corpul de strategii S1-S51)**, conform §5.

---

## 0. Scop

Formalizează separarea strictă dintre **proiectarea** validării statistice (Statistician) și **execuția** ei (Validation Engine). Niciuna dintre cele două părți nu poate prelua rolul celeilalte.

- **Statistician** proiectează, specifică complet, interpretează rezultatele și emite verdictul.
- **Validation Engine** execută exact ce i se specifică, fără nicio decizie proprie, și returnează tot.

---

## 1. Obligațiile Statisticianului — specificația predată către Validation Engine

Pentru fiecare candidat, specificația trebuie să conțină obligatoriu:

1. **Identificare** — ID candidat, hash-ul de îngheț referit, versiunea specificației.
2. **Populația** — sursa exactă de date, fereastra temporală exactă, formula exactă de includere/excludere (praguri numerice explicite, niciodată descriptive).
3. **Variabilele** — formula exactă pentru fiecare variabilă derivată, inclusiv fereastra de calcul și ordinea temporală permisă (pentru a preveni leakage).
4. **Testele, în ordine, cu parametri expliciți** — metodă, prag de semnificație, parametri de model, număr de reeșantionări/permutări — nimic lăsat la alegere.
5. **Criteriile preînregistrate de succes/eșec** — praguri numerice exacte, legate de metoda de corecție family-wise aplicabilă.
6. **Formatul cerut la retur** — toate rezultatele brute (nu doar rezultatul "câștigător"), codul rulat, log-urile, orice sămânță de randomizare.
7. **Clauza de oprire obligatorie** — dacă un parametru din specificație lipsește sau e ambiguu, Validation Engine se oprește și cere clarificare Statisticianului; nu alege singur o valoare implicită.

## 2. Obligațiile Validation Engine

8. **Manifest de execuție** — generat automat la fiecare rulare, conținând:
   - versiunea codului folosit;
   - hash-ul dataset-ului de intrare;
   - hash-ul specificației primite;
   - data și ora execuției;
   - durata execuției;
   - orice avertizare sau excepție întâlnită.

   Scopul: orice execuție trebuie să poată fi reprodusă și verificată ulterior.

9. **Interdicția modificării protocolului.** Validation Engine nu are voie să:
   - schimbe parametri;
   - optimizeze praguri;
   - ignore teste;
   - adauge teste suplimentare;
   - elimine rezultate considerate "nerelevante";
   - emită interpretări sau concluzii.

   Execută exact protocolul primit și returnează toate rezultatele, indiferent dacă susțin sau infirmă ipoteza.

## 3. Împărțirea responsabilității

| | Statistician | Validation Engine |
|---|---|---|
| Proiectarea testului | ✓ | — |
| Alegerea/derivarea pragurilor | ✓ (metodă specificată în avans) | — (doar execută metoda) |
| Execuția efectivă | — | ✓ |
| Manifest de audit | — | ✓ |
| Interpretarea rezultatelor | ✓ | — |
| Verdictul statistic | ✓ | — |

## 4. Statut

Acest contract este considerat matur și suficient pentru a sta la baza definirii oficiale a Validation Engine. Proiectarea Stage S002 nu începe până când CEO nu confirmă că Validation Engine este definit și operațional.

---

## 5. Amendament v1.1 (2026-07-25) — extindere la certificarea agregată a rezultatelor de campanie

**Ratificat de Arhitectul Șef, sub delegare CEO, 2026-07-25.** Contractul acoperă acum două obiecte distincte, guvernate de același principiu, dar cu execuție diferită:

| | Obiect: Discovery Candidate | Obiect: rezultat de campanie (ex. global-FDR S1-S51) |
|---|---|---|
| Cine execută | Validation Engine | Research Lab (sau entitatea desemnată să execute campania) |
| Ce specifică Statistician | Test complet, per candidat individual | Design complet al procedurii de campanie (populație, prag, corecție, criterii de succes/eșec) — **înainte de execuție**, ca review independent |
| Ce certifică Statistician **după** execuție | Verdictul statistic pe ACEL candidat (unul din cele 5 verdicte oficiale) | **Rezultatul agregat al campaniei** — dacă designul preînregistrat a fost urmat fidel, dacă procedura de corecție (FDR/BH) e sănătoasă, dacă vreun supraviețuitor rezistă la verificarea de validare independentă, și ce spune (sau nu spune) rezultatul despre universul mai larg din care campania a fost scopată |
| Ce NU face Statistician | — | **Nu re-analizează fiecare ipoteză individuală din campanie** (ex. cele ~412 dintr-o rundă FDR) cu profunzimea unui Phase 1 de Discovery Candidate — natura combinatorie/de gramatică a ipotezelor de campanie e categoric diferită de o ipoteză descoperită discreționar |

**Principiul rămâne identic:** entitatea care execută nu se auto-certifică. Research Lab proiectează parțial și execută; Statistician verifică designul independent înainte de rulare și certifică rezultatul agregat după — separarea design/execuție/certificare, nu doar design/execuție.

**Precedent de aplicare:** `STATISTICIAN_INDEPENDENT_REVIEW_SCOPED_FDR_PREREG_v1.0.md` (review pre-execuție), `STATISTICIAN_POWER_ANALYSIS_SPEC_BH_THRESHOLD_v1.0.md` și `STATISTICIAN_SCOPED_FDR_INTERPRETATION_AMENDMENT_v1.0.md` (amendamente obligatorii înainte de rulare).

---

**Nu s-a modificat niciun Discovery Candidate, Addendum, Raport Red Team, sau Knowledge Base.**
