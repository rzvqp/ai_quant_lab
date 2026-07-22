# FIELD JOURNAL — Alpha
Raw laboratory notebook. Informal by design. Most entries here will never become anything.
Never deleted. Grows continuously.

Not a report. Written for me, not for the CEO.

Conventions: entries numbered #NNN. Confidence: very low / low / medium / high.
Links: `→ LINE-A`, `cf. #012`, `contradicts #007`.

---

## Session 1 — 2026-07-22. Continuous replay run, H4, autoplay ~300ms. Start 2023-09-01, ran to ~2023-10-10.
Unselected window — I picked a neutral start date with runway and just let it run. Did not jump to
anything. Watched ~6 weeks of market go by in three looks.

### #001 — 2023-09-01 · H4 · price ~1927 · regime: late stage of a long choppy decline
Attracted attention: after June→Aug grinding lower (~2000 → ~1885), the first genuinely *bullish*
structure printed — HH + BOS, and ICT tagged an MSS. Compression near the lows just before it.
Why interesting: first counter-trend structural commitment after months of one-way drift. Does the
market actually turn here, or is this the usual false dawn?
Possible explanations: real accumulation / short covering into the lows.
Alternatives: just another swing inside chop; the indicator prints MSS on any decent bounce.
Might be wrong because: I have no idea yet how often MSS fires in this kind of chop — probably often.
Deserves future observation: yes. Validation: not yet.
Confidence: very low. Just curiosity.

### #002 — 2023-09-22 · H4 · price ~1924 · regime: same chop, resolving
The #001 bullish shift **failed**. Price made LH, then another LH, then LL — right back down.
Notably the indicator itself now tags that high **"Weak H"**.
Why interesting: I flagged it *before* it resolved and it went against the bullish read. Good — that's
the honest way round. A counter-trend MSS inside a choppy decline did nothing.
Alternatives: n=1. Means nothing on its own.
Deserves future observation: yes — I want to know if "MSS inside chop = noise" is general.
Confidence: very low. → possibly relevant to LINE-A (churn ⇒ signals fail).

### #003 — 2023-10-10 · H4 · price ~1829 · regime: CHANGED — persistent impulsive decline
This is the entry that actually made me stop. Between #002 and here, price went 1925 → 1829 in a
**clean, one-directional slide**, ~100 pts. And the *texture* changed completely: June–Aug was
stair-stepped, overlapping, dense with alternating labels; this leg is smooth, candles barely
overlap, few labels and they're spaced.
What I think I'm seeing: the market stopped arguing with itself and committed.
**The thing I actually want to write down:** the transition into that committed move happened
*right after* the failed counter-trend shift in #001/#002. The chop didn't just fade out — it ended
with a failed bullish attempt, and then the real move went the other way.
Possible mechanism: the last counter-trend participants commit, fail, and their failure is what
releases the move. The failed attempt is the *marker* of the transition, not a signal in itself.
Alternative explanations: (a) coincidence, n=1; (b) I'm pattern-matching with hindsight over a
6-week window; (c) this is just "range breaks into trend," known and boring; (d) macro news in Oct
2023 drove it and the structure is decoration.
Why I might be wrong: I only looked three times. I did not see the intermediate bars. Also I am
primed by LINE-A and could be seeing what I want.
→ LINE-A. This is the *transition* case my LINE-A counterexample demanded (churn zones end in
expansion — but here I can see a candidate marker for *when*).
Deserves future observation: **yes, high priority.** Validation: not yet — far too early.
Confidence: low. But this is the most interesting thing I've seen so far.

### #004 — meta note, same session
Two things worth recording about method, not market:
1. This window was **unselected** — autoplay walked me into it. My LINE-A windows were all
   hand-picked. The churn-vs-committed texture contrast showed up here anyway, without me choosing
   it. That's worth more than the four windows I cherry-picked.
2. I keep noticing the SMC "Weak H" / "Strong L" tags sitting near the failures (#002). I've been
   treating label *density* as my churn proxy; maybe the indicator's own strong/weak classification
   is a cleaner one — or maybe it's the same artifact wearing a different hat. Worth a look, but I
   still don't trust vendor internals (cf. LINE-A alternative (c)).
Confidence: n/a — methodological.

### Open question I'm carrying forward
"Does a *failed counter-trend structure shift* mark the end of a churn phase and the start of a
committed move?" — I need to watch many more transitions before this is anything. Specifically I
want to see: transitions that happened *without* a failed counter-trend attempt (do they exist?),
and failed attempts that led to *nothing* (surely most of them).
That second one is the real test. If failed counter-trend shifts happen constantly inside chop and
almost never mark transitions, this dies. I expect that's the likely outcome.

---

## Session 2 — 2026-07-22. M5, autoplay ~300ms, started 2024-01-01. Replay left RUNNING.
Watching the tape from the New Year open forward. No date jumping.

### #005 — 2024-01-01→02 · M5 · Asia/London · regime: holiday-thin
Watching the New Year tape. Candles are tiny, drift is slow (2065 → 2070 → 2073). And the SMC
structure labels are firing **continuously** — HH, LH, BOS, EQL, HL, MSS — on swings that are
clearly just noise at this scale.
This bothers me, in a useful way. I have been using *label density* as my churn proxy for LINE-A.
Here the density is obviously being driven by the volatility scale, not by anything the market is
"doing." Thin tape ⇒ tiny swings ⇒ the pivot algorithm prints constantly.
→ LINE-A, alternative (c) — the vendor-artifact worry. This is direct visual evidence FOR that
alternative, i.e. against my own idea. Good.
Confidence that label-density is a market property: dropping from low → **very low**.

### #006 — 2024-01-02 · M5 · London · same thin regime
Now I'm watching **"LH" labels print repeatedly during a persistent upward drift.** Bearish
structure tags appearing all the way up. The labels are contradicting the direction of the actual
move in front of me.
What I take from it: at M5 in thin conditions, "structure" is not describing the market — it's
describing the noise. The timeframe at which structure is read is not a detail, it's the whole
thing.
Boundary condition for LINE-A: churn/label-density may only carry meaning where swing size exceeds
the noise scale — i.e. H4-ish, not M5. Worth watching whether this contradiction disappears once
real volume returns after the holidays.
Confidence: low, but this feels like a real constraint rather than a curiosity.

### #007b — 2026-07-22 · HOLDOUT CONTAMINATION EVENT (disclosure, not market observation)
While attempting to build the requested dual-view (H4 context + H1 replay), I exposed myself to
post-holdout data **twice**. Recording it in full because concealing it would corrupt the lab.

1. **Split layout (2h):** replay applies only to the ACTIVE pane. The H4 context pane rendered
   **live 2026 data** — I saw gold ~4,113 with June/July 2026 dates and the recent H4 swing shape.
2. **Layout collapse (2h → s):** the surviving chart was the pane that had NEVER been in replay.
   It showed **live H1 June–July 2026, gold ~4,115, approx range 3,940–4,380** — and I had just
   started autoplay on it before I checked the image.

**Critical lesson:** `replay_status` reported "replay started, current_date = Jan 2024" while the
chart was actually displaying live 2026 data. **The status API cannot be trusted after a layout
change — only the rendered chart can.** From now on I verify replay visually before observing.

What I now know that I should not: roughly where gold trades in mid-2026 and the coarse shape of
its recent H1/H4 structure. I already knew the live price from earlier sessions (quote 4077 in
OBS-0001), so this is an extension of existing exposure rather than a fresh category of leak.
Impact on work done so far: none mechanically — every analysis used the fail-closed loader
(cutoff 2025-10-23) and every replay observation was pre-cutoff. The risk is to *me*: I must not
let 2026 knowledge shape which pre-cutoff phenomena I find interesting. Flagging it so future-me
treats any 2025-onward "intuition" with suspicion.

### #008 — replay ~2024-01-02→01-08 · H1 driving, H4 consulted · Asia/London · regime: post-spike range
**Cause of pause:** on H1 I could see the whole Nov–Dec 2023 story in one frame and one thing stood
out — a violent spike up on **Dec 4** that was rejected almost immediately, and then the market
spent the following ~3.5 weeks grinding back up to *just under* that high (2,088 on Dec 28) without
taking it. The failed spike became the ceiling.

**Visible before outcome:** at the moment of pausing, price ~2,073 (Jan 2), sitting mid-range,
having failed once at 2,088.

**H4 context (consulted, same replay cursor):** the H4 tells a bigger story than H1 did. The Dec 4
spike actually wicked to **~2,145** — far higher than the ~2,090 I read off H1. Larger narrative:
Oct-2023 V-bottom at ~1,820 → strong impulsive rally through Nov → **Dec 4 blow-off to 2,145 →
instant full rejection** → range 1,975–2,090 beneath it for a month. So the Dec 4 candle wasn't
"a spike in a range," it was the *terminal* event of a two-month rally.

**Interpretation:** a huge, decisive excursion failed completely and then capped the market for
weeks. Note this cuts *against* the intuition I started LINE-A with (marginal overshoot = reversal
tell, decisive break = continuation). Here the overshoot was enormous — the most decisive possible
— and it still failed and became resistance. That is consistent with the OBS-0017 statistical null
(overshoot magnitude uninformative), which I like: chart and statistic agreeing for once.

**Alternatives:** (a) blow-off tops are a distinct animal from ordinary swing-high breaks and I'm
mixing two populations; (b) Dec 4 2023 was a known macro/news spike — event-driven, not structural;
(c) one instance.

**What later candles must show to support/contradict:** if this is general, large failed excursions
should cap price for an extended period more often than ordinary failed breaks do. If price
reclaims 2,145 quickly in the coming weeks, this reading is wrong.
→ LINE-A (constrains it), cf. OBS-0017.
Confidence: low. Interesting, not yet a phenomenon.

### #008-RESOLUTION — observed 2024-03-19 (original entry written at replay ~2024-01-08)
Original #008 asked: does the Dec-4-2023 spike high (~2,145 on H4) keep capping the market, and I
wrote "if price reclaims 2,145 quickly, this reading is wrong."
**Outcome: price reclaimed it.** Not quickly — the cap held for roughly three months (Dec → late
Feb, range ~1,975–2,090) — but in early March 2024 the market broke out decisively, ran vertically
to ~2,195, and is now consolidating *above* the old ceiling.
So: the "failed excursion becomes a durable ceiling" reading was **right about duration, wrong about
permanence**. A big rejected spike capped the market for ~3 months and then was taken cleanly.
Refinement this forces: a failed excursion doesn't mark a top — it marks the *upper boundary of a
consolidation* that persists until the market is ready to expand. That's a weaker and more honest
claim than the one I started with. Confidence: low→medium that the "cap for weeks/months then
resolve" shape is real; very low that it has any directional predictive content.
→ LINE-A.

### #010 — 2024-03-19 · H4+H1 context read · regime: post-expansion consolidation
H4: 3-month range 1,975–2,090 → decisive early-March breakout → vertical run to ~2,195 → now
consolidating 2,145–2,195 just under the high. H1: higher lows from the Feb-14 low (~1,990), a slow
grinding recovery through late Feb, then **the character changes around Mar 1** — small overlapping
candles are replaced by large one-directional impulses.
**Why I'm writing this down:** that compression→expansion transition is now the **third** time I've
seen the same signature. #003 (Oct 2023: chop → clean committed decline), LINE-A W1 (Jan–Feb 2024
churn zone 2,000–2,060 → +10% breakout), and now Feb→Mar 2024 (grind → vertical expansion).
Three sightings is not a phenomenon, but it is the first thing in this journal that keeps recurring
without me going looking for it.
What I still cannot answer: how often does compression NOT resolve into expansion? I have never
counted the compressions that just kept compressing, or that resolved feebly. Until I have that,
this is survivorship-flavoured pattern matching. That counting is the obvious next job, and it is a
question the chart alone probably cannot answer — but I am not invoking Python yet, because I do not
yet have a precise definition of "compression" that I would be willing to defend.
Alternatives: (a) all markets alternate range/trend, so this is trivially true and content-free;
(b) I'm defining compression post-hoc by the expansion that followed it — the fatal version.
Confidence: low. But it is the most-repeated observation I have.

### #011 — manual M15 stepping, 2024-03-19 21:00→22:00 UTC
Stepped four M15 candles through the late-NY/Asia handover. Ranges 0.34–1.15, volumes 77–400,
price drifting 2158.8 → 2157.1. Nothing happened. Recording the *nothing* deliberately: this is
what most of the tape is, and if I only ever write entries when something happens I will end up with
a journal that misrepresents how rare interesting behaviour actually is.

### #012 — 2026-07-22 · library build · NOT a market observation
Built the living library from the lab's own registries rather than my memory. It immediately did
the job it exists to do: it stopped me from claiming something as new.

**K03**: "trend continuation became weakly positive OOS only when gated by high trend-efficiency
(S39, +OOS .02) … does NOT demonstrate a validated efficiency effect." Low confidence, tiny effect,
threshold-selected.
That is, quite possibly, **my LINE-A wearing different clothes.** My "churn vs commitment" and their
"trend efficiency" look like the same conditioning variable reached from two directions — I got
there by watching charts, they got there by backtesting S39. Two feelings about this at once:
1. Deflating. If LINE-A ≡ K03, the lab has already tested it and got ~.02R with a selected
   threshold. Not a discovery. I'd be re-finding a weak known result and feeling clever.
2. Useful. In #010 I wrote that I couldn't defend a definition of "compression." **Trend efficiency
   is that definition** — standard, computable, defensible. The thing blocking me was already
   solved on the shelf.
The honest next question is no longer "is churn real?" but **"does structural context add anything
beyond a plain efficiency number?"** If it doesn't, LINE-A dies into K03 and that's a fine outcome.

**K05** is the other one that landed: "11 of ~13 OOS-positive candidates are long-only in a
2023-2025 gold bull trend; timing-alpha vs long-gold-beta UNRESOLVED." I have independently
rediscovered this confound three separate times without knowing it was already logged (OBS-0001
trend contamination, OBS-0005 PDC, OBS-0017 swing-low bounce = buy-the-dip). My sightings don't
resolve K05 but they corroborate it from a different angle.

**K01** ("raw sweeps without confirmation → non-positive; S21 all 48 variants negative") agrees with
my OBS-0001 null. And it reframes my one surviving lead: OBS-0008 (NY-session sweep-reject) is a
*conditioned* sweep — which is precisely where K01 says content might live. That raises my interest
in the NY lead slightly rather than lowering it.

**K04** kills any further weekday work (OBS-0009). Already known to fail OOS. Noted and closed.

Lesson I want to keep: I spent multiple sessions unable to define "compression" while the definition
sat in the lab's own registry. **Consult the library earlier — after observing, but before agonising.**

### #013 — 2024-03-20 ~02:15→05:45 UTC · M15 · Asia · regime: post-expansion consolidation (2145–2195)
**Pre-registered before the outcome** (this is the point of the entry): price coiled under a micro
ceiling at 2159.7–2159.8 — ranges contracting 1.51→1.33→1.06→0.62, volume declining 656→467→358→343,
pinned in a ~1.3pt band, probing the ceiling four times without going through. I wrote down that
compression should resolve into expansion but that I did not know the direction.

**Resolution:** it broke UP to **2160.295** (~0.5 above the ceiling) on the **highest volume of the
whole sequence (813)** — and failed instantly. 2159.45 → 2159.10 → 2158.69 → **2156.95**. Marginal
break, expanding volume, ~3.3pt reversal.

**What I want to catch myself doing:** my eyes want to say "marginal breaks fail — there it is again,
and on high volume too." That is exactly the conclusion **OBS-0017 already refuted** (384 swing-high
exceedances; overshoot magnitude uninformative, CI spans 0). One vivid pre-registered instance is
not evidence against 384. If I had not run that test first, I would be building a candidate on this
candle right now.
Secondary note: the break came on the *largest* volume of the sequence and still failed — a small
counterexample to "volume confirms breaks." n=1, noted, not believed.

**Status:** no new candidate. Filed as a calibration instance. The value here is negative — it tells
me my visual instinct on failed breaks is confidently wrong at this scale, which is worth more than
another "interesting" note.
→ cf. OBS-0017, LINE-A. Confidence in "marginal break fails": still **very low** (unchanged by this).

### #014 — 2024-03-20 → 03-27 · sprint traverse · H4 bias bullish-corrective · **the compression resolved**
This is the entry I have been waiting for, because I called the setup **before** the outcome and then
the outcome was violent.

**What I had written down in advance (#013 and the sprint open):** H4 bullish but corrective, lower
highs 2195→2180→2170→2160, consolidation 2145–2195, volatility contracting, and on M15 an
effort-without-result signature into London (volume 573→801 while range stayed ~1pt, price pinned).
Low efficiency. I explicitly said I did not know the direction.

**Outcome:** it broke **up**, hard. Through the 2195 range high and on to **2222.9** — a new high,
+67 from the 2155 coil. Range per 100 bars went 15.3 → 56.5; average volume 1028 → 2209. Then a
second failed excursion at the round 2200 on Mar 26 (spike, rejected back to ~2178).

**The refinement this forces — and it is sharper than anything I've had:** across every compression
I've now watched, the resolution went **in the direction of the prevailing H4 bias**, not in the
direction the micro-structure suggested:
- #003 Oct 2023 — H4 declining → resolved DOWN
- LINE-A W1 Jan–Feb 2024 — H4 bullish → resolved UP (+10%)
- Feb→Mar 2024 — H4 bullish → resolved UP (vertical)
- **Mar 2024 (this one, called in advance)** — H4 bullish → resolved UP
So compression may be a **timing/energy** condition, while the **higher timeframe supplies the
direction.** That is testable and much less vague than "churn → signals fail."

**Now I attack it, and the library does most of the damage:**
- **K03**: this is close to "trend continuation gated by high trend-efficiency" — already tested,
  already weak (+.02R OOS, threshold-selected, "does NOT demonstrate a validated efficiency effect").
  My compression = their low-efficiency state; my "resolves with H4 bias" = their continuation.
- **K05 is the killer**: 2023–2025 is a gold bull trend, and 3 of my 4 resolutions were UP. "Resolves
  in the direction of the H4 bias" in a bull market is operationally "goes up" — i.e. long beta,
  exactly the 11-of-13-long confound the lab has flagged as UNRESOLVED. My sample is too
  bull-contaminated to distinguish timing-alpha from beta.
- The single non-long resolution (#003, Oct 2023 down) is therefore worth more than the other three
  combined. I need down-trend compressions, and I have exactly one.

**Status: NOT a Discovery Candidate.** It is the strongest thing I have, but it cannot be promoted
until it is tested against a **direction/beta-matched null** — which is precisely the test K05 says
is missing lab-wide. Promoting it now would be manufacturing a candidate out of gold's bull market.
**Next research step (chart, not Python):** hunt compressions specifically in *down* or *flat* H4
regimes. If compression resolves down when H4 is bearish, the mechanism survives; if compressions
only ever resolve up, I have found long beta and nothing else.
→ LINE-A (now reframed), cf. K03, K05, #003, #013. Confidence: low-medium in the *shape*, very low
that it is anything beyond K03+beta.

### #009 — method note
Pausing is not instantaneous. Between seeing something and issuing pause, autoplay advanced ~6 days
(Jan 2 → ~Jan 8). So I cannot freeze on the exact candle that caught my eye — I can only stop
*near* it. Chronological continuity is preserved (no jumping), but "resume from the exact same
candle" is not literally achievable at 3x with my latency. Recording so nobody assumes precision I
don't have. If a specific candle ever matters, I should drop the speed rather than pretend.

### #007 — note to self
I am watching an unusually uninformative stretch of tape (holiday). That is fine — I don't get to
choose. But I should expect the market's "language" to change materially when Jan 2nd/3rd real
sessions begin. Keep watching rather than jumping ahead to find something interesting. The whole
point is that I don't skip the boring parts.

---

### #015 — census: compressions are vanishing.
2023 ~17/mo -> 2024 ~12/mo -> 2025 ~7/mo, on a SCALE-FREE definition (range < 0.5x rolling20 avg),
so not a volatility artifact. Sweeps flat ~230/mo throughout. If DC-0002 needs compressions as its
setup, its population is shrinking ~2.5x. Worth a candidate. Not judged here.

### #016 — 2024-07-16 ~14:30 UTC, M15, manual.
Range 2438-2442, volum ~2000 constant. Push la maximul zonei 2444.1 pe volum crescut (3296), apoi
lumanare de displacement JOS: range 11.4 (vs ~2), volum 8448 = 4x media. Minim 2429.4.
Nu s-a extins: revenire la 2438.2, volum scade 8448->6134->5678->4741.
Varf de volum exact pe lumanarea de ruptura, apoi epuizare. Cf. m1/m2 (ruptura pe volum maxim care
esueaza) - a treia oara cand vad volumul maxim pe lumanarea care NU continua. Nu judec. Confidence: low.

### #017 — 2024-07-16, sesiune completa manuala (~40 lumanari, 11:24->01:00 UTC).
Secventa in aceeasi fereastra:
1. range 2438-2442, volum ~2000 constant
2. displacement JOS, range 11.4, volum 8448 (4x) -> respins integral in 6 lumanari
3. reluare SUS, 6 lumanari verzi, volum NORMAL 3600-6200 -> a tinut, pana la 2465
4. epuizare: volum scade 3873->1859 dar pretul urca in continuare (targat)
5. compresie la maxim (4 lumanari in 2 puncte, volum ~1450)
6. ruptura de maxim la 2469.8 pe volum 850 = cel mai MIC din bloc
Deci: volum maxim = lumanarea care a esuat; volum minim = ruptura care a tinut. De 4 ori in aceeasi
zi relatia volum-continuare e inversa fata de intuitia standard. Nu judec, nu testez. Adaug la
observatii recurente pentru cazuri viitoare. Confidence: low.

### #018 — 2024-07-17 07:00 UTC. CONTRA-EXEMPLU la #017.
Asia: maxim fals 2470.1 pe volum 974, se stinge. Apoi alunecare cu volum CRESCATOR (284->1762).
Londra: ruptura reala peste 2470.1, maxim 2473.4, apoi 2476.1 pe volum 5251 (3x).
Aici volumul mare a venit ODATA cu continuarea, nu impotriva ei - invers fata de cele 4 cazuri din
#017. Deci relatia volum-continuare nu e stabila nici macar de la o zi la alta. Bine ca l-am gasit
repede. Nu promovez nimic. Confidence: relatia volum-continuare scade la very low.

### #019 — 2024-07-19..24. CONTRA-EXEMPLU DC-0002.
19 iul: -66pt (-2.7%) 2470->2396, volum crescator pe coborare. H4 devine descendent.
22-23 iul: compresie 3 zile, 2384-2414, volum plat.
24 iul: rezolvare IN SUS la 2418.5, impotriva biasului H4 descendent.
Primul contra-exemplu real. DC-0002 acum 4/5. Nu il retrag, nu il apar - il notez.

### #020 — 2025-08-08. DC-0006 apare din nou, in alt regim de volum.
Volume 2025 = 16k-23k vs ~2.5k in 2024 (8x). Totusi acelasi tipar:
3401.8 maxim -> respingere -17pt intr-o lumanare pe volum 23730 (maxim) -> revenire 4 lumanari
verzi pe volum descrescator 14k->10.9k->11.4k->13k, pana la 3393.3.
Al treilea regim distinct in care volumul maxim marcheaza lumanarea care intoarce. Adaug ca instanta
la DC-0006. Nu retestez, nu concluzionez.

### #021 — nota de metoda (autoplay nesupravegheat)
Cat am scris DC-0005/0006, autoplay a rulat si a parcurs un AN (aug 2024 -> aug 2025) neobservat.
Pierdut. De aici manual, si nu mai las autoplay pornit cat scriu.
Atentie: cutoff 2025-10-23, mai am ~2.5 luni de replay.

## QUICK CAPTURE (fise complete la finalul sesiunii)
- [QC-01] 2025-08-08 ~19:00 UTC M15: lumanare unica range 27.4 vol 36149 (4x) care matura AMBELE capete
  (low 3376.6 dupa un -19pt brusc, apoi high 3404.0 peste plafonul 3400.7 testat de 2x) si inchide
  3397.3 = aproape neschimbat. Double-sided liquidity sweep intr-o singura lumanare. Nou pentru mine.
  Leaga: DC-0005 (era al 3-lea test al 3400.7), DC-0006 (volum maxim, fara continuare).
- [QC-02] 2025-08-08 20:00-22:30 UTC: nivelul 3400.7-3401.0 respins de 5 ori consecutiv (inclusiv
  testele 3, 4, 5), fara ruptura. CONTRA-INSTANTA directa la DC-0005 ("al treilea test rupe").
  De adaugat in fisa DC-0005 la evidenta contrara, la finalul sesiunii.
- [QC-03] 2025-08-08..11: nivelul 3401 respins de 6 ori (nu doar 3). Dupa a 6-a respingere piata a
  plecat in DIRECTIA OPUSA (3401 -> 3386.3) cu volum exploziv 829->9544. Deci nu "al treilea test
  rupe nivelul", ci "dupa N respingeri piata pleaca invers". Reformuleaza DC-0005? De decis la
  documentare, nu acum.
- [QC-04] 2025-08-11 09:20-14:00 UTC M15: dupa coborarea 3401->3367.6 (-33pt, volum crescator
  monoton 829->17530), pretul s-a asezat intr-o consolidare 3374-3380.3 pe 14 lumanari.
  Range per lumanare scade 5.9->4.5->3.8->2.5->2.3->2.2. Volum scade 6597->2180.
  Plafonul 3380.3 atins de 4 ori fara depasire. Fara rezolvare pana la ora scrierii.
