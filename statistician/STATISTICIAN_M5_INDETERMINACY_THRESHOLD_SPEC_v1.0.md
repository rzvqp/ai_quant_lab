# STATISTICIAN — SPECIFICAȚIE: PRAGUL §9 DE NEDETERMINARE M5

**Document ID:** STAT-M5-INDET-SPEC-v1.0
**Data:** 2026-07-27 · **Autor:** Statistician
**Superseda:** §3 ("Pragul M5 — regula de nedeterminare") din `STATISTICIAN_11YR_DATASET_PREREGISTRATION_RULES_v1.0.md` — acel §3 folosea un prag fix pe distanța stopului singură (Q1/Q3), fără RR și fără distribuția reală. Acest document îl înlocuiește, cu distribuția reală livrată de Data Acquisition.
**Distribuție folosită (per sesiune, high-low, puncte):** late n=30.673 mediana 0,735 IQR[0,415-1,610] p90 3,945; asia n=123.840 mediana 1,220 IQR[0,745-2,350] p90 4,725; london n=77.393 mediana 1,525 IQR[0,970-2,630] p90 4,730; ny n=122.763 mediana 1,710 IQR[0,975-3,095] p90 5,645; TOATE n=354.669 mediana 1,400 IQR[0,815-2,655] p90 4,995.

---

## Verdict asupra rezervei — 1.400 NU se susține ca prag de decizie

**Directiva CTO conflă două cantități diferite.** 1,400 e mediana amplitudinii barei (high-low) — o statistică descriptivă a pieței. Criteriul real de nedeterminare cere ca **ambele niveluri** (stop ȘI țintă) să încapă în aceeași bară decisivă — asta e o funcție a distanței stopului **ȘI** a RR, nu doar a amplitudinii tipice a barei.

## Criteriul derivat

Pentru o tranzacție cu distanță de stop `S` (puncte) și `RR` (țintă = RR × S): nivelul de stop și nivelul de țintă sunt distanțate `S + RR·S = S(1+RR)` puncte unul de celălalt. **Condiție necesară** ca o singură bară să poată conține ambele niveluri: amplitudinea barei decisive (high−low) trebuie să fie **≥ C(S,RR) = S × (1+RR)**.

Exemplul tău: S=1,4, RR=2 → C = 1,4×3 = **4,2 puncte** — nu 1,4. Verificat: 4,2 stă sub p90 (4,995 pe "TOATE"), deci chiar la această combinație S/RR, doar coada superioară a distribuției (aprox. sub 15% din bare, pe "TOATE") atinge amplitudinea NECESARĂ — ambiguitatea reală (care mai cere ȘI ca prețul să atingă efectiv ambele niveluri, nu doar ca bara să aibă loc) e cu mult sub acel procent. Folosirea lui 1,400 direct ca prag pe amplitudine ar fi comparat bara cu distanța stopului, nu cu C(S,RR) — o eroare de categorie, nu doar o cifră prea mică.

**Regulă, în două straturi, RR ca variabilă:**

1. **Pre-screening necesar, per sesiune:** dacă `C(S,RR) < Q1` al amplitudinii sesiunii relevante → improbabil ambiguu, se rulează totuși testul per-tranzacție ca verificare, nu ca presupunere. Dacă `C(S,RR)` depășește p90 al sesiunii → foarte probabil rar ambiguu (puține bare ating pragul necesar). Între Q1 și p90 → zona unde pre-screening-ul singur nu decide, testul per-tranzacție e obligatoriu.
2. **Testul per-tranzacție (neschimbat ca principiu, deja specificat):** pe bara decisivă, dacă `[low,high]` conține ATÂT nivelul de stop CÂT ȘI nivelul de țintă → rezultatul e NEDETERMINAT. Acesta rămâne testul DECISIV — pre-screening-ul de mai sus doar economisește calcul, nu înlocuiește verificarea reală.

**1,400 supraviețuiește DOAR ca input descriptiv** (mediana amplitudinii, per sesiune, folosită ca referință de context) — nu ca prag universal de decizie. Recomand ca directiva CTO să fie reformulată explicit: **"1,400 = mediana amplitudinii sesiune-pool, referință descriptivă; pragul de decizie e C(S,RR)=S(1+RR), evaluat per ipoteză și per sesiune."**

## Prag per sesiune sau global — per sesiune, justificat de distribuția livrată

Medianele diferă de peste 2× (late 0,735 vs. ny 1,710); p90-urile diferă ~1,43× (late 3,945 vs. ny 5,645). Un prag global ar subestima sistematic amplitudinea disponibilă în sesiunile late/asia (marcând ambiguitate acolo unde e rară) și ar supraestima-o în ny/london (ratând ambiguitate reală acolo). **Verdict: pragul de nedeterminare se evaluează PER SESIUNE, folosind distribuția proprie a acelei sesiuni** — nu distribuția "TOATE" — pentru orice ipoteză a cărei populație e restrânsă la o sesiune (majoritatea campaniei S1-S51, parametrizată explicit pe sesiune). Pentru o ipoteză care tranzacționează pe toate sesiunile, distribuția "TOATE" rămâne relevantă pentru pre-screening-ul agregat, DAR raportarea (secțiunea următoare) trebuie să arate defalcarea pe sesiune — o rată agregată joasă poate ascunde o rată ridicată concentrată într-o singură sesiune.

## Tratamentul unei tranzacții nedeterminate

Neschimbat ca principiu de bază, cu o completare din lecția `bracket_69`: **excludere din calculul win/loss** (nu se numără nici câștig, nici pierdere), cu **rata de excludere raportată explicit, obligatoriu** (infrastructura `denominator_always_reported` din registru se aplică identic aici).

**Completare obligatorie, motivată direct de descoperirea recentă a celor 47 "EXCLUSION-DEPENDENT" (bracket-69):** o simplă excludere, fără verificare suplimentară, s-a dovedit insuficientă acolo — a ascuns o categorie de profitabilitate creată exclusiv de decizia de excludere. Aceeași disciplină se aplică aici: **pentru orice ipoteză al cărei status de profitabilitate depinde calitativ de tratamentul tranzacțiilor nedeterminate M5, se cere raportarea sub bracket-ul complet — worst-case (nedeterminatele scorate ca stop) și best-case (scorate ca țintă) — alături de numărul primar (excludere).** Dacă verdictul calitativ rămâne stabil pe acest interval, excluderea nu era load-bearing. Dacă se schimbă, statusul aparține tratamentului, nu ipotezei — exact tiparul `CONVENTION-ARTIFACT` deja stabilit.

## Plafonul pe procentul de tranzacții nedeterminate per ipoteză

**Confirm 25%, cu verificare împotriva distribuției reale, nu doar reafirmare.**

Spre deosebire de criteriul `C(S,RR)` (derivat matematic din mecanica stop/țintă), plafonul de 25% NU e derivabil din distribuția amplitudinii singură — e o convenție declarată despre câtă atriție e tolerabilă înainte ca sub-eșantionul rămas să nu mai fie reprezentativ (analog pragurilor de atriție din literatura de studii clinice/meta-analiză, unde nu există un număr universal, doar convenții). O declar, cu disclosure, ca reutilizare a aceleiași convenții generice de 25% deja folosită de două ori în acest laborator (regula M5 originală, testul de stabilitate al HMM) — trece propriul meu test de proveniență (§2, punct 1: fracție-prag generică, nu calculată din acest rezultat specific).

**Verificare împotriva distribuției livrate, ca să nu fie o reafirmare oarbă:** la S=1,4/RR=2 (C=4,2), pragul discriminează real — pe "TOATE," C=4,2 stă sub p90 (4,995), deci majoritatea ipotezelor cu acest profil nu vor atinge 25% nedeterminate. Pentru un stop mult mai strâns cu RR mare (ex. S=0,5, RR=3 → C=2,0), C=2,0 cade în interiorul IQR-ului ("TOATE": [0,815-2,655]) — o parte substanțială a barelor (plauzibil >25%) ating sau depășesc acel prag, deci un asemenea profil ar declanșa corect plafonul. **25% nu e nici vid (nu se declanșează niciodată), nici universal (nu se declanșează mereu) pe distribuția reală — rămâne o poartă cu sens.**

**Raportare obligatorie suplimentară:** fracția de nedeterminate se raportează atât agregat CÂT ȘI per sesiune — o ipoteză tranzacționată pe toate sesiunile poate avea o rată agregată sub 25% care ascunde o rată concentrată, mult peste plafon, într-o singură sesiune (de obicei ny/london, unde amplitudinea tipică e mai mare, deci C(S,RR) fix se atinge mai des). **Dacă ORICE sesiune individuală depășește 25% pentru acea ipoteză, se marchează `NOT-RESOLVABLE-AT-M5` pentru acea sesiune specific, chiar dacă agregatul trece** — statusul agregat nu poate masca un eșec sesiune-specific.

**Ce se întâmplă cu o ipoteză `NOT-RESOLVABLE-AT-M5` (agregat sau per sesiune):** neschimbat — nu se exclude definitiv, statut informativ (analog UNRESOLVED), rămâne eligibilă la rezoluție mai grosieră (M15) unde amplitudinea e confortabil suficientă. Nu se forțează un rezultat dintr-un subeșantion nereprezentativ doar pentru că există date.

---

**Nu am atins date, nu am implementat. Statistician se oprește aici.**
