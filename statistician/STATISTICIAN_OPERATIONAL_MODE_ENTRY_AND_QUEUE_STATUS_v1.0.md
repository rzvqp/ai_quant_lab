# STATISTICIAN — INTRARE ÎN OPERATIONAL MODE, STAREA VERIFICATĂ A CANDIDATE QUEUE

**Document ID:** STAT-OPERATIONAL-MODE-ENTRY-QUEUE-STATUS-v1.0
**Data:** 2026-07-30 · **Autor:** Statistician

**Confirm intrarea în OPERATIONAL MODE, ca procedură standing.** De acum, nu mai aștept un "MANDAT" separat pentru fiecare candidat — momentul în care un candidat primește `SURVIVED_RED_TEAM_A`, definesc automat cele șapte elemente cerute, predau către VE, actualizez Candidate Queue, și trec la următorul candidat eligibil, fără ceremonie suplimentară.

**O clarificare tehnică, onestă, nu o rezervă:** eu operez turn-cu-turn — "buclă continuă" în sensul literal de proces care rulează neîntrerupt în fundal, între mesajele tale, ar necesita un mecanism explicit de reluare programată (skill-ul `/loop`), pe care nu-l pornesc singur fără cerere explicită, fiind o comandă orientată către utilizator. Ce POT și confirm acum: la FIECARE interacțiune viitoare, verific starea reală a cozii și procesez imediat orice candidat nou eligibil, fără să aștept reformularea completă a ordinului de azi.

---

## Verificare directă, nu presupunere: STAREA ACTUALĂ a Candidate Queue

**Citit direct `CANDIDATE_QUEUE.md` (`ai_quant_lab-alpha-automation`, branch `alpha-automation-v1`, comitul `f469c05`).** Căutat explicit orice candidat cu statusul `SURVIVED_RED_TEAM_A` — **zero, la acest moment.**

```
CAND-0001  PDH-PDL                     — queued → Red Team (A)   [NU a trecut încă]
CAND-0002  COMPRESSION-EXPANSION       — queued → Red Team (A)   [NU a trecut încă]
CAND-0003  FVG-CE50-REACTION           — queued → Red Team (A)   [NU a trecut încă]
CAND-0004  LIQUIDITY-VOID              — NOT CURRENTLY TESTABLE  [spec request → Statistician, ALT tip de sarcină]
CAND-0005  BPR                         — NOT CURRENTLY TESTABLE  [spec request → Statistician, ALT tip de sarcină]
CAND-0006  PWH-PWL                     — NOT CURRENTLY TESTABLE  [spec request → Statistician, ALT tip de sarcină]
CAND-0007  LEVEL-FVG-CONFLUENCE        — queued → Red Team (A)   [NU a trecut încă]
CAND-0008  VOID-DISPLACEMENT           — queued → Red Team (A)   [NU a trecut încă]
CAND-0009  LEVEL-BREAK-DRIVE           — queued → Red Team (A)   [NU a trecut încă]
CAND-0010  FVG-STACK-DENSITY           — queued → Red Team (A)   [NU a trecut încă]
```

**Nu inventez o rulare de protocol pe un candidat care n-a atins încă pragul.** "Queued → Red Team (A)" înseamnă exact ce spune — încă în așteptarea evaluării Red Team, nu după ea. Aș încălca exact instrucțiunea de azi ("preiei automat FIECARE candidat care PRIMEȘTE statusul") dacă aș defini un protocol pentru un candidat care nu l-a primit încă.

## Distincție care trebuie păstrată, nu amestecată

**CAND-0004/0005/0006 sunt adresate deja mie ("spec request → Statistician"), dar NU sub acest mandat.** Cererea lor e "ratifică un detector de reacție" (Liquidity Void, BPR, PWH/PWL) — o sarcină de RATIFICARE DE PRIMITIVĂ, exact genul de lucru făcut la revizia MK-01/MK-02 recentă — NU o definire de protocol statistic pe șapte puncte pentru un candidat care a trecut deja Red Team A. Nu le procesez sub eticheta de azi ca să "am ceva de arătat" — rămân semnalate, separate, în așteptarea unui mandat propriu dacă CTO vrea să le adreseze acum.

---

## Procedura standing, confirmată pentru fiecare candidat viitor care primește `SURVIVED_RED_TEAM_A`

Pentru fiecare, definesc (nu execut, nu optimizez, nu aleg parametri după rezultate):

1. **Protocolul statistic** — reutilizând întotdeauna infrastructura deja ratificată (WP-5' block_bootstrap, convențiile de cost/floor deja stabilite) unde se aplică, nu inventând un test nou fără motiv.
2. **Familia de teste** — fixată ÎNAINTE de a vedea rezultate, cu justificarea explicită a numărului (câți candidați înrudiți au fost deja "priviți" pe aceleași date).
3. **Ipoteza nulă** — H0 explicit, în termenii deja standard ai acestui laborator (`mean(net_R)<=0` sau echivalentul potrivit construcției candidatului).
4. **Criteriile de respingere** — pragul de semnificație, corecția pentru testare multiplă (BH-FDR sau echivalent, consecvent cu ce s-a folosit deja).
5. **Holdout-ul** — confirmarea explicită că rămâne sigilat, neatins, indiferent de rezultat.
6. **Walk-forward-ul** — specificat mecanic (fereastră, pas), nu doar menționat.
7. **Toate limitările** — consemnate explicit, nu ascunse (eșantion mic, colinearitate cu candidați deja testați, orice risc de circularitate).

Fiecare document se publică, se predă către VE, Candidate Queue se actualizează, și trec imediat la următorul candidat eligibil — fără să aștept un nou "DIVIZIE: STATISTICIAN" pentru fiecare.

---

**Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.32 (commit `41121d9`, `alpha-automation-v1`) — mypy --strict curat, content_hash reverificat independent (blank-and-rehash), pytest 139/143 trecute (aceleași 4 eșecuri pre-existente). Niciun protocol de definit azi — coada nu conține încă niciun candidat eligibil.**
