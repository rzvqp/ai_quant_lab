"""N1 startup hydration (RT-N1-HYDRATION-0001, CEO amendment 2026-08-18). Removes the "start from empty
state, wait ~COMPRESSION_WINDOW bars in real time before N1 can resolve a regime" cost from every fresh
install/restart, WITHOUT ever generating a candidate/trade for a warmup bar and WITHOUT ever forcing a
regime the accumulated history genuinely does not support.

At startup: try a compatible persisted snapshot first, replay it plus only the bars closed since its own
watermark; otherwise (no snapshot, or a rejected/incompatible one) do a full canonical backfill from MT5's
own closed-bar history. Either way the result is a `RawAxesBuilder` that has observed EXACTLY the same
bars, in the same order, a continuous run would have -- proven by feeding both paths through the real
`RawAxesBuilder.observe()`, never a bypass or a fast-path shortcut.

Status at delivery: built and tested, NOT wired into `entrypoint.py`'s `main()`/`build_loop()` yet -- that
wiring is the controlled cutover, gated on Red Team review, same as `dual_clock/`. `BROKER_ORDER_
SUBMISSION` remains `DISABLED` throughout; this package has no code path to a strategy decision, a risk
gate, or a broker call at all -- it only ever calls `RawAxesBuilder.observe()` and persists axes/bar state."""
