"""`hydrate_n1` decisive tests -- RT-N1-HYDRATION-0001. Fakes only, no real MT5 terminal; LIVE_SHADOW is
never touched. `FakeNewBrainLiveGateway.copy_rates_from` ignores its own `count` argument and always
returns the fixed `rates` tuple it was constructed with, so these tests can use small, fast synthetic bar
sets rather than the full ~460-bar `COMPRESSION_WINDOW` real hydration targets in production -- the
`required_bar_count()` derivation itself is checked directly against the real vendored constants, not
re-derived from a shrunk fixture."""

from __future__ import annotations

import dataclasses
import inspect
import time
from pathlib import Path
from typing import Any

from ai_trader.live_signal_source.bar_feed import LiveBarFeed, watermark_key
from ai_trader.live_signal_source.types import Bar
from ai_trader.new_brain_bridge.raw_axes_builder import RawAxesBuilder
from ai_trader.new_brain_live import n1_hydration
from ai_trader.new_brain_live.n1_hydration import hydrate, identity, snapshot
from ai_trader.new_brain_live.n1_hydration.hydrate import hydrate_n1
from ai_trader.new_brain_live.n1_hydration.identity import N1SnapshotIdentity
from ai_trader.new_brain_live.n1_hydration.snapshot import N1Snapshot, N1SnapshotStore
from ai_trader.new_brain_live.tests._fixtures import SYMBOL, FakeNewBrainLiveGateway
from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.structural_observer.vendor_bridge import ATR_WINDOW, COMPRESSION_WINDOW, K_DEFAULT

_BAR_SECONDS = 900
_MT5_TIMEFRAME = 15


@dataclasses.dataclass
class _RawRate:
    time: int
    open: float
    high: float
    low: float
    close: float
    tick_volume: float = 100.0


def _now() -> int:
    return int(time.time())


def _m15_rates(*, count: int, start_ts_open: int, start_price: float = 2400.0) -> tuple[_RawRate, ...]:
    price = start_price
    rates = []
    for i in range(count):
        ts_open = start_ts_open + i * _BAR_SECONDS
        rates.append(_RawRate(time=ts_open, open=price, high=price + 0.4, low=price - 0.4, close=price + 0.02))
        price += 0.02
    return tuple(rates)


def _safely_past_start(count: int, *, margin_bars: int = 4) -> int:
    """The first bar's `ts_open` such that all `count` bars close comfortably before real `now` --
    `LiveBarFeed.poll()`'s own `ts_close > now: continue` closed-bar filter must never exclude any of
    them for these tests to be about hydration logic, not accidental future-bar filtering."""
    return _now() - (count + margin_bars) * _BAR_SECONDS


def _probe(builder: RawAxesBuilder, *, after_ts_open: int, price: float = 2500.0) -> Any:
    """Feeds ONE more identical bar to `builder` and returns the resulting `RawAxes` -- used to compare
    two independently-hydrated builders' internal accumulated state by their OBSERVABLE next reading,
    since `RawAxesBuilder` has no other public accessor for "current axes"."""
    bar = Bar(
        symbol=SYMBOL, ts_open=after_ts_open, ts_close=after_ts_open + _BAR_SECONDS, open=price,
        high=price + 0.4, low=price - 0.4, close=price + 0.02, volume=100.0,
    )
    return builder.observe(bar)


def test_required_bar_count_is_derived_not_a_hardcoded_literal() -> None:
    assert identity.required_bar_count() == max(ATR_WINDOW, COMPRESSION_WINDOW, 2 * K_DEFAULT + 1)
    assert "460" not in inspect.getsource(identity.required_bar_count), (
        "required_bar_count() must read COMPRESSION_WINDOW from vendor_bridge, never a duplicated literal"
    )


def test_empty_state_backfill_matches_a_continuous_run(tmp_path: Path) -> None:
    count = 30
    start = _safely_past_start(count)
    rates = _m15_rates(count=count, start_ts_open=start)
    gateway = FakeNewBrainLiveGateway(rates=rates)
    state_store = SqliteStateStore(tmp_path / "state.db")

    result = hydrate_n1(symbol=SYMBOL, gateway=gateway, state_store=state_store)
    assert result.restored_from_snapshot is False
    assert result.rejection_reason is None
    assert result.bars_replayed_new == count

    continuous = RawAxesBuilder(SYMBOL)
    for rate in rates:
        continuous.observe(Bar(
            symbol=SYMBOL, ts_open=rate.time, ts_close=rate.time + _BAR_SECONDS, open=rate.open,
            high=rate.high, low=rate.low, close=rate.close, volume=rate.tick_volume,
        ))

    probe_ts = start + count * _BAR_SECONDS
    hydrated_probe = _probe(result.axes_builder, after_ts_open=probe_ts)
    continuous_probe = _probe(continuous, after_ts_open=probe_ts)
    assert hydrated_probe == continuous_probe
    state_store.close()


def test_compatible_snapshot_restore_and_catchup_matches_a_continuous_run(tmp_path: Path) -> None:
    warmup_count, catchup_count = 20, 10
    total = warmup_count + catchup_count
    start = _safely_past_start(total)
    all_rates = _m15_rates(count=total, start_ts_open=start)
    warmup_rates = all_rates[:warmup_count]

    state_store = SqliteStateStore(tmp_path / "state.db")
    gateway = FakeNewBrainLiveGateway(rates=warmup_rates)
    first = hydrate_n1(symbol=SYMBOL, gateway=gateway, state_store=state_store)
    assert first.restored_from_snapshot is False
    assert first.bars_replayed_new == warmup_count

    gateway_with_new = FakeNewBrainLiveGateway(rates=all_rates)
    second = hydrate_n1(symbol=SYMBOL, gateway=gateway_with_new, state_store=state_store)
    assert second.restored_from_snapshot is True
    assert second.rejection_reason is None
    assert second.bars_replayed_from_snapshot == warmup_count
    assert second.bars_replayed_new == catchup_count

    continuous_store = SqliteStateStore(tmp_path / "continuous_state.db")
    continuous_gateway = FakeNewBrainLiveGateway(rates=all_rates)
    continuous = hydrate_n1(symbol=SYMBOL, gateway=continuous_gateway, state_store=continuous_store)

    probe_ts = start + total * _BAR_SECONDS
    restored_probe = _probe(second.axes_builder, after_ts_open=probe_ts)
    continuous_probe = _probe(continuous.axes_builder, after_ts_open=probe_ts)
    assert restored_probe == continuous_probe
    assert second.watermark_ts_open == continuous.watermark_ts_open
    state_store.close()
    continuous_store.close()


def test_incompatible_snapshot_is_rejected_and_rebuilt_canonically(tmp_path: Path) -> None:
    count = 25
    start = _safely_past_start(count)
    rates = _m15_rates(count=count, start_ts_open=start)
    gateway = FakeNewBrainLiveGateway(rates=rates)
    state_store = SqliteStateStore(tmp_path / "state.db")

    # Hand-write a snapshot carrying a DIFFERENT implementation_commit than the one running now.
    bad_identity = N1SnapshotIdentity(
        n1_contract_version="wrong-contract", router_version="wrong-router",
        implementation_commit="deadbeef", detector_configuration_fingerprint="wrong-fp",
        symbol=SYMBOL, timeframe="M15", snapshot_schema_version=identity.SNAPSHOT_SCHEMA_VERSION,
        first_bar_ts_open=start, last_bar_ts_close=start + _BAR_SECONDS, bar_content_identity="wrong-bar-fp",
        watermark_ts_open=start,
    )
    stale_bar = Bar(
        symbol=SYMBOL, ts_open=start, ts_close=start + _BAR_SECONDS, open=1.0, high=1.1, low=0.9, close=1.05,
        volume=1.0,
    )
    N1SnapshotStore(state_store).record(N1Snapshot(identity=bad_identity, bars=(stale_bar,)))

    result = hydrate_n1(symbol=SYMBOL, gateway=gateway, state_store=state_store)
    assert result.restored_from_snapshot is False
    assert result.rejection_reason == "IDENTITY_MISMATCH"
    assert result.bars_replayed_new == count  # full canonical rebuild, the stale bar never touched
    assert result.identity.implementation_commit != "deadbeef"
    state_store.close()


def test_future_or_unclosed_bars_are_never_observed(tmp_path: Path) -> None:
    count = 15
    start = _safely_past_start(count)
    past_rates = list(_m15_rates(count=count, start_ts_open=start))
    future_bar = _RawRate(time=_now() + 10_000, open=9999.0, high=9999.5, low=9998.5, close=9999.2)
    gateway = FakeNewBrainLiveGateway(rates=tuple(past_rates + [future_bar]))
    state_store = SqliteStateStore(tmp_path / "state.db")

    result = hydrate_n1(symbol=SYMBOL, gateway=gateway, state_store=state_store)
    assert result.bars_replayed_new == count  # the future bar must be silently excluded, not observed
    assert result.identity.last_bar_ts_close < future_bar.time
    state_store.close()


def test_repeated_hydration_with_no_new_bars_produces_identical_state(tmp_path: Path) -> None:
    count = 18
    start = _safely_past_start(count)
    rates = _m15_rates(count=count, start_ts_open=start)
    state_store = SqliteStateStore(tmp_path / "state.db")

    first = hydrate_n1(symbol=SYMBOL, gateway=FakeNewBrainLiveGateway(rates=rates), state_store=state_store)
    second = hydrate_n1(symbol=SYMBOL, gateway=FakeNewBrainLiveGateway(rates=rates), state_store=state_store)

    assert second.restored_from_snapshot is True
    assert second.bars_replayed_new == 0, "no new bars available -- a repeated hydration must add nothing"
    assert second.watermark_ts_open == first.watermark_ts_open
    assert second.identity.bar_content_identity == first.identity.bar_content_identity
    state_store.close()


def _source_excluding_docstrings(module: Any) -> str:
    """Every bare string-literal statement (module/function docstrings, and this repo's own convention of
    trailing bare-string "public alias" doc comments) stripped out -- so a forbidden-name check below
    inspects only real CODE, never prose that legitimately NAMES a forbidden module to explain its
    absence (as this package's own module docstrings do)."""
    import ast

    tree = ast.parse(inspect.getsource(module))
    lines = inspect.getsource(module).splitlines()
    keep = [True] * len(lines)
    for node in ast.walk(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            start = node.lineno - 1
            end = (node.end_lineno or node.lineno) - 1
            for i in range(start, end + 1):
                keep[i] = False
    return "\n".join(line for line, k in zip(lines, keep) if k)


def test_warmup_never_imports_a_decision_or_broker_module() -> None:
    """"Warmup nu produce candidate/trade" verified structurally, not just behaviorally: none of this
    package's own modules reach Router/EV/N6/RiskManager/broker code -- mirroring this repo's own
    established import-independence test convention
    (`mandate2_readiness/tests/test_import_independence.py`). Checked against source with every docstring
    stripped, since this package's own module docstrings legitimately NAME these forbidden symbols to
    explain their absence."""
    forbidden_substrings = (
        "decide_n6", "DecisionRequest", "StrategyRouter", "risk_gate", "execution_shadow",
        "BrokerOrderSubmissionGate", "order_send", "submit_new_brain_candidate",
    )
    for module in (hydrate, identity, snapshot, n1_hydration):
        code_only = _source_excluding_docstrings(module)
        for forbidden in forbidden_substrings:
            assert forbidden not in code_only, f"{module.__name__} must never reference {forbidden!r}"


def test_first_new_bar_after_hydration_is_processed_exactly_once(tmp_path: Path) -> None:
    warmup_count = 20
    start = _safely_past_start(warmup_count + 1)
    warmup_rates = _m15_rates(count=warmup_count, start_ts_open=start)
    state_store = SqliteStateStore(tmp_path / "state.db")

    result = hydrate_n1(
        symbol=SYMBOL, gateway=FakeNewBrainLiveGateway(rates=warmup_rates), state_store=state_store,
    )
    assert result.bars_replayed_new == warmup_count

    new_bar_ts_open = start + warmup_count * _BAR_SECONDS
    all_rates = tuple(warmup_rates) + _m15_rates(count=1, start_ts_open=new_bar_ts_open)
    real_feed = LiveBarFeed(
        FakeNewBrainLiveGateway(rates=all_rates), SYMBOL, _MT5_TIMEFRAME, _BAR_SECONDS,
        lookback_count=warmup_count + 5, state_store=state_store,
    )

    first_poll = real_feed.poll()
    assert len(first_poll) == 1, "only the genuinely new bar must be seen -- none of the warmup bars"
    assert first_poll[0].ts_open == new_bar_ts_open

    second_poll = real_feed.poll()
    assert second_poll == (), "the new bar must never be re-emitted on a subsequent poll"
    state_store.close()


def test_hydration_watermark_matches_the_real_bar_feed_key(tmp_path: Path) -> None:
    count = 12
    start = _safely_past_start(count)
    rates = _m15_rates(count=count, start_ts_open=start)
    state_store = SqliteStateStore(tmp_path / "state.db")
    hydrate_n1(symbol=SYMBOL, gateway=FakeNewBrainLiveGateway(rates=rates), state_store=state_store)

    persisted = state_store.get_value(watermark_key(SYMBOL, _MT5_TIMEFRAME))
    assert persisted is not None
    assert int(persisted) == start + (count - 1) * _BAR_SECONDS
    state_store.close()


def test_uncertain_regime_is_permitted_not_forced(tmp_path: Path) -> None:
    """A short, flat bar sequence with no confirmed break must hydrate into `structure=None,
    direction=None` (`SemanticRegime.UNCERTAIN`) -- never a fabricated regime just to make hydration
    "produce a result"."""
    count = 10
    start = _safely_past_start(count)
    rates = _m15_rates(count=count, start_ts_open=start, start_price=2400.0)
    state_store = SqliteStateStore(tmp_path / "state.db")

    result = hydrate_n1(symbol=SYMBOL, gateway=FakeNewBrainLiveGateway(rates=rates), state_store=state_store)
    probe_ts = start + count * _BAR_SECONDS
    axes = _probe(result.axes_builder, after_ts_open=probe_ts)
    assert axes.structure is None
    assert axes.direction is None
    state_store.close()
