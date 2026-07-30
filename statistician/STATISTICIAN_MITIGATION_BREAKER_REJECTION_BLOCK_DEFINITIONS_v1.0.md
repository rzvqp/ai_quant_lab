# STATISTICIAN — DEFINIȚIILE MITIGATION BLOCK, BREAKER BLOCK ȘI REJECTION BLOCK (OBDZ)

**Document ID:** STAT-MITIGATION-BREAKER-REJECTION-BLOCK-DEFINITIONS-v1.0
**Data:** 2026-07-30 · **Autor:** Statistician

**Verificare de sursă:** confirmat direct `LiquidityPool` (`code/liquidity_mechanics.py:62`) are câmpul `formed_idx` (bara extremului); `SweepEvent` (linia 77) are câmpul `pool: LiquidityPool`. Confirmat `detect_sweeps(high, low, close, pools, blocks, require_close_back_inside=True)` — semnătura D6 (wick trece dincolo, close revine în range), block-scoped. Confirmat exact `_scan_reactions(ob: OrderBlock, ...)` — reconfirmă ce ai spus: `detect_mitigations`/`detect_rejections` primesc un OB deja format, nu-și definesc propria zonă.

---

# MITIGATION BLOCK vs BREAKER BLOCK

## Ratific distincția centrală, AMENDEZ compunerea lui `has_swept_liquidity`

**Distincția (sweep vs eșec de sweep înainte de BOS) e corectă și clară — ratific.** Compunerea propusă (`swept = any(s.pool.formed_idx == prior_swing_idx for s in sweeps)`) e corectă ca IDEE — zero primitive noi, confirmat — dar **incompletă: îi lipsește o fereastră temporală**, ceea ce ar introduce un risc real de lookahead.

**Problema, precis:** un `LiquidityPool` rămâne activ (D4) până la consumare sau sfârșitul blocului — dacă bazinul de la `prior_swing_idx` e eventual măturat MULT MAI TÂRZIU, într-un episod NELEGAT de acest BOS specific, verificarea propusă l-ar găsi oricum și ar clasifica greșit acest OB ca „Breaker" folosind un eveniment din VIITORUL față de bara de formare examinată — exact tipul de scurgere pe care disciplina anti-E010 din acest lab există s-o prevină.

**Compunere corectată, tot fără primitive noi:**
```
swept = any(s.pool.formed_idx == prior_swing_idx
            AND swing_high_idx < s.idx <= formation_idx
            for s in sweeps)
```
unde `swing_high_idx` = cel mai recent Swing HIGH clasificat înainte de bara de ancoră, iar `formation_idx` = bara de ancoră a OB-ului (bara `i-1`, corpul înghițit). **Fereastra se mărginește STRICT la coborârea dintre swing-ul HIGH și formarea OB-ului** — orice măturare ulterioară (chiar dacă a aceluiași bazin) NU contează pentru clasificarea ACESTUI OB.

**`prior_swing_idx` și `swing_high_idx` se localizează reutilizând `market_structure.py` Swing/StructureLabel** — ACEEAȘI primitivă deja folosită la Măsurătoarea A (SMC_S1_v2) și la `pullback_depth` (mandatul anterior): `swing_high_idx` = cel mai recent swing HIGH clasificat înainte de bara de ancoră; `prior_swing_idx` = cel mai recent swing LOW clasificat înainte de ACEL swing high. Zero primitive noi, a treia reutilizare a aceleiași mașinării.

## ATENȚIE — coliziune de nume cu „Breaker" deja existent în familia de 10

**„Breaker Block" al tău (bazat pe swing-sweep-apoi-BOS) NU e același lucru cu „Breaker" deja măsurat ca element separat în familia de 10 (`track_breaker`, criteriul E010/E012 de inversare — un OB deja format devine breaker când CLOSE trece decisiv dincolo de zona lui).** Sunt concepte diferite care împart același nume: unul descrie o STARE ULTERIOARĂ formării (invalidare prin close), celălalt descrie o CONDIȚIE DE FORMARE (manipulare prin măturare înainte de BOS). **Recomand redenumirea conceptului tău nou** — ex. „Swept Reversal Block" sau altă etichetă la alegerea ta — ca să nu se confunde cu `track_breaker` deja existent. Până la redenumire, îl citez ca „Breaker Block (nou, bazat pe swing)" explicit, distinct de „Breaker (existent, `track_breaker`)".

## Observația 1 — răspuns

**Confirmat: zero primitive noi pentru compunere, cu amendamentul de mai sus (fereastra temporală + localizarea prin Swing/StructureLabel).**

## Observația 2 — MB și „Breaker Block" (nou) numără ca 1 element, nu 2

**De acord cu analiza ta: e o partiție, nu doi candidați independenți.** Fiecare OB rupt cu corpul (via impuls E010+înghițire, deja detectat de `detect_order_blocks`) devine EXACT unul din cele două — niciodată ambele, niciodată niciunul. **MB și „Breaker Block" (nou) nu sunt zone GEOMETRIC diferite — sunt aceeași zonă OB, cu o ETICHETĂ CONDIȚIONALĂ NOUĂ** (a existat sau nu o măturare de lichiditate pe coborârea premergătoare). Nu creează o zonă nouă, distinctă de OB — clasifică OB-urile deja detectate după o variabilă suplimentară.

**Numără ca 1 element în familia de 10/12** (vezi mai jos) — comparația MB-vs-BB ÎNTRE ele e ea însăși partea informativă (spune dacă manipularea contează), deci se raportează ÎMPREUNĂ, nu separat, ca UN SINGUR test de familie. **Confirm și avertismentul tău despre putere:** fiecare subpopulație (MB, respectiv BB) e mai mică decât „OB nemitigat" plin — comparația fiecăreia cu brațele B/C are mai puțină putere statistică decât măsurătoarea OB simplă deja făcută; se raportează explicit, nu se ascunde în spatele unei medii pe toată populația combinată.

---

# REJECTION BLOCK

## Ratific definiția geometrică și regula de respingere

**Zona (fitil exclusiv, corp exclus complet) și regula de atingere/respingere sunt corecte, ratific.** Motivația (fitilele pe aur pot depăși 60 pips, zona-fitil-întreagă ar introduce zgomot masiv) e solidă și consecventă cu disciplina deja aplicată la separarea zonă-vs-fitil de la D6/OB (fitilul are rol exclusiv de atingere, nu de zonă).

## Observația 3 — cazul strapungerii complete, SPECIFICAT acum

**Confirmat: cazul `Low_c ≤ Floor` (fitilul trece prin toată zona, dincolo de propriul minim al barei RB) nu era acoperit — nici respingere (eșuează `Low_c > Floor`), nici declarat explicit.**

**Propunere, consecventă cu convenția deja stabilită la OB (fereastră de valabilitate cu DOUĂ evenimente posibile de încheiere — atingere de fitil D7 SAU close decisiv E010/E012):**

```
RESPINGERE (deja definită):  Low_c <= Ceiling  ȘI  Low_c > Floor  ȘI  Close_c > Ceiling
INVALIDARE (nou, propusă):   Low_c <= Floor  — INDIFERENT unde închide bara c
```

**Motivul pentru INVALIDARE necondiționată de close:** RB memorează „aici prețul anterior a respins agresiv" — dacă o bară ulterioară traversează prin ÎNTREG acel fitil istoric (nu doar îl testează), teza „acest nivel respinge" e falsificată pentru ACEASTĂ zonă specifică, indiferent unde se închide bara respectivă — analog cum, la OB, o traversare de fitil (D7) consumă zona o singură dată, fără re-armare. **RB devine invalid/consumat la prima strapungere completă, nu se re-testează.**

**De acord cu observația ta:** D6 (bazine de lichiditate) nu are limită inferioară similară — corect, și RB e mai strict DELIBERAT (zona RB e deja îngustă, doar fitilul, spre deosebire de un bazin de lichiditate care e un punct/nivel). Limita inferioară nu contrazice D6, extinde disciplina zonă-îngustă la un caz nou.

---

# CONSEMNARE — ambele sunt primitive NOI, confirmat, familia se ACTUALIZEAZĂ de la 10 la 12

**Confirmat, verificat direct în cod: `detect_mitigations`/`detect_rejections` primesc un `OrderBlock` deja format ca parametru (`_scan_reactions(ob: OrderBlock, ...)`) — nu-și definesc propria zonă din preț brut. Mitigation Block/Breaker Block (nou) ȘI Rejection Block sunt AMBELE primitive genuin noi**, fiecare cu propria geometrie derivată direct din bare, nu reutilizări sub alt nume.

**Actualizare necesară a familiei fixate în mandatul anterior (v2.7.18, family=10):** cele „trei primitive lipsă" (Session Open, Mitigation Block, Rejection Block) erau candidați ÎN PLUS față de cele 10 deja numărate, nu înlocuitori — acum că două din cele trei sunt confirmate ca reale și definite matematic, familia pentru orice test formal ulterior **se actualizează la 12** (10 originale + Mitigation/Breaker-Block-pereche ca 1 element + Rejection Block ca 1 element), cu **Session Open rămânând al 13-lea candidat, ÎN AȘTEPTARE**, condiționat de propria lui definiție (încă neclarificată). Fixat ACUM, înainte de orice măsurătoare pe aceste două — aceeași disciplină ca la family=10 inițial.

---

## Ce rămâne neatins

Nimic nu se rulează. Testul pereche pe OB×DemandZone rămâne poarta — fără verdictul lui, nu știm dacă metodologia găsește ceva real sau zgomot repetat, acum în douăsprezece forme posibile, nu zece. Sigilatul intact.

---

**Publicat pe `statistician-foundation`; manifestul se incrementează.**
