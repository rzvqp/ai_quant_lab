# STATISTICIAN ↔ VALIDATION ENGINE CONTRACT v1.0
### Interfața oficială dintre proiectarea și execuția validării statistice

**Document ID:** STAT-VE-CONTRACT-v1.0
**Data ratificării:** 2026-07-24 · **Autoritate:** CEO
**Statut:** Contract oficial, permanent. Stă la baza definirii Validation Engine și guvernează orice interacțiune viitoare dintre Statistician și Validation Engine, pentru orice Discovery Candidate.

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

**Nu s-a modificat niciun Discovery Candidate, Addendum, Raport Red Team, sau Knowledge Base.**
