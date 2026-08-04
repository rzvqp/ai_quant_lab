# M1 — INVENTAR DE FEZABILITATE (înainte de descărcare)

**Divizie:** Data Acquisition · **Instrument:** OANDA:XAUUSD · **Data:** 2026-08-04
**Status:** DOAR INVENTAR — nu s-a descărcat/segmentat nimic. Nu s-a atins M15_v2/M5/H1/manifest.

## 1. Acoperire obtenabilă

**M1 ≈ 1 an, fereastră rulantă.** Podeaua măsurată în Faza 0 (verificată iterativ, blocaj ×3):
2025-07-24 la data de 2026-07-25 → rulantă, acum ~2025-08. Consistent cu memoria proiectului.
**SUB pragul de 3 ani — decisiv.**

Re-sondarea live de azi: **CDP (port 9222) verificat nereachable la nivel de OS** — TradingView Desktop
nu rulează cu CDP activat. Re-confirmarea live a podelei exacte + un eșantion M1 direct **rămân în
așteptare** până e relansat cu CDP. Verdictul de mai jos NU depinde de asta (podeaua ~1 an e robustă).

## 2. Volum / dimensiune (ancoră: fișierul M5 real = 70.940 bare/an, 49 bytes/bară)

| Scenariu | Bare | Dimensiune |
|----------|------|-----------|
| **~1 an (obtenabil)** | **~355.000** | **~17 MB** |
| 3 ani (ipotetic, indisponibil) | ~1,06 M | ~52 MB |
| „20M" din estimarea CEO | 20 M | ~980 MB (**ar cere ~56 ani** — imposibil) |

**Corecție:** M1 = 5× densitatea M5 = ~355k bare/**an**, nu 2M/an. Cei ~1 an obtenabili ≈ ~355k bare
(≈ cât întreg fișierul M5 actual), NU 20M. Estimările de 2M/an și 20M presupun ~56 ani sau 24/7 pe
decenii — indisponibil.

## 3. RISCURI (raportate, nerezolvate)

**A. COST.** Ancoră măsurată: mediana amplitudinii M5 = **1,400 pt** (IQR 0,815–2,655). Pe M1 barele
sunt sub-M5 (mai mici); stop-urile viabile sunt de ordinul zecimilor de punct până la ~1-2 pt. Cu un
cost fix (spread gold ~$0,20–0,50/oz) raportat la un astfel de stop, **costul devine o fracțiune mare
din R — mai rău decât cele 10% de pe M15 care au ucis toate strategiile testate.** Măsurătoarea directă
a ATR-median M1 → cost/R necesită CDP (în așteptare); ancora M5 arată deja direcția.

**B. REGIMURI.** ~1 an = doar 2025-2026 = **un singur regim (bull)**. Fără bear, fără corecție amplă.
**Validarea încrucișată pe regimuri dispare** — singurul mecanism care a prins fals-pozitivele până
acum. (M5 avea deja doar 2021-2026, fără bear; M1 e și mai îngust.)

**C. VOLUM/RUNTIME.** ~355k bare ≈ fișierul M5 actual. Detectoarele rulează „ore pe 130k bare" → ~**2,7×**
≈ câteva ore. **Mild — NU catastrofa de 20M** (aceea ar fi ~56× și ar cere ani de M1 indisponibili).

## 4. Verdict

Acoperirea M1 obtenabilă (~1 an, un singur regim) **NU trece pragul de 3 ani** și **colapsează validarea
încrucișată pe regimuri**. Plus riscul de cost (mai grav decât ucigașul de pe M15). Ca **bază de
cercetare/validare, M1 nu merită** — 1 an mono-regim nu poate valida nimic.

Singura utilizare defensabilă: un strat subțire de **rezoluție de execuție/confirmare** pentru §9 pe
fereastra recentă (~1 an), NU pentru validare. Dar și acolo, costul pe M1 e prohibitiv la stop-uri mici.

**Recomandare:** nu achiziționa M1 ca dataset de validare. Dacă vrei totuși stratul de execuție ~1 an,
e o decizie separată, mai îngustă — o iau doar la ordin explicit, după relansarea CDP pentru măsurători.
