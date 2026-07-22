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
