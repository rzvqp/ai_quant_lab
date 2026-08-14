"""`BoundedTowerCache` tests -- CEO/Red Team remediation, 2026-08-14: "TowerClient._cache e NELIMITAT.
Red Team a demonstrat 5.000 de intrari fara eviction." Tests #10/#11 of the 18-item checklist (limit never
exceeded, TTL evicts) live here at the raw cache-API level; TowerClient-level integration
(`bind_session` clearing on restart, request-id-reuse refusal) is covered in `test_tower_client.py`."""

from __future__ import annotations

from ai_trader.new_brain_bridge.tower_cache import BoundedTowerCache


def test_put_and_get_round_trip() -> None:
    cache: BoundedTowerCache[str] = BoundedTowerCache(max_entries=10, ttl_seconds=60.0)
    cache.put("req-1", "fp-1", "result-1")
    assert cache.get("req-1", "fp-1") == "result-1"


def test_get_miss_on_wrong_fingerprint() -> None:
    cache: BoundedTowerCache[str] = BoundedTowerCache(max_entries=10, ttl_seconds=60.0)
    cache.put("req-1", "fp-1", "result-1")
    assert cache.get("req-1", "fp-2") is None


def test_check_reuse_true_for_different_fingerprint_same_id() -> None:
    cache: BoundedTowerCache[str] = BoundedTowerCache(max_entries=10, ttl_seconds=60.0)
    cache.put("req-1", "fp-1", "result-1")
    assert cache.check_reuse("req-1", "fp-2") is True
    assert cache.check_reuse("req-1", "fp-1") is False
    assert cache.check_reuse("req-unseen", "fp-anything") is False


def test_10_cache_never_exceeds_max_entries_via_direct_api() -> None:
    cache: BoundedTowerCache[int] = BoundedTowerCache(max_entries=5, ttl_seconds=3600.0)
    for i in range(50):
        cache.put(f"req-{i}", f"fp-{i}", i)
        assert cache.metrics.size <= 5
    assert cache.metrics.size == 5
    assert cache.metrics.evictions == 45


def test_10_cache_never_exceeds_max_entries_after_thousands_of_puts() -> None:
    cache: BoundedTowerCache[int] = BoundedTowerCache(max_entries=100, ttl_seconds=3600.0)
    for i in range(5000):
        cache.put(f"req-{i}", f"fp-{i}", i)
    assert cache.metrics.size == 100
    assert cache.metrics.evictions == 4900
    # LRU: the most recently inserted 100 entries survive
    assert cache.get("req-4999", "fp-4999") == 4999
    assert cache.get("req-0", "fp-0") is None


def test_lru_eviction_order_is_least_recently_used_not_insertion_order() -> None:
    cache: BoundedTowerCache[int] = BoundedTowerCache(max_entries=2, ttl_seconds=3600.0)
    cache.put("a", "fp-a", 1)
    cache.put("b", "fp-b", 2)
    cache.get("a", "fp-a")  # touch "a" -- "b" is now the least recently used
    cache.put("c", "fp-c", 3)  # should evict "b", not "a"
    assert cache.get("a", "fp-a") == 1
    assert cache.get("b", "fp-b") is None
    assert cache.get("c", "fp-c") == 3


def test_11_ttl_evicts_entries() -> None:
    clock = [0.0]
    cache: BoundedTowerCache[str] = BoundedTowerCache(max_entries=10, ttl_seconds=5.0, now_fn=lambda: clock[0])
    cache.put("req-1", "fp-1", "result-1")
    assert cache.get("req-1", "fp-1") == "result-1"
    clock[0] = 10.0  # past the TTL
    assert cache.get("req-1", "fp-1") is None
    assert cache.metrics.evictions == 1


def test_clear_empties_the_cache_and_resets_size_metric() -> None:
    cache: BoundedTowerCache[str] = BoundedTowerCache(max_entries=10, ttl_seconds=60.0)
    cache.put("req-1", "fp-1", "result-1")
    cache.clear()
    assert cache.metrics.size == 0
    assert cache.get("req-1", "fp-1") is None


def test_metrics_hits_and_misses() -> None:
    cache: BoundedTowerCache[str] = BoundedTowerCache(max_entries=10, ttl_seconds=60.0)
    cache.put("req-1", "fp-1", "result-1")
    cache.get("req-1", "fp-1")  # hit
    cache.get("req-1", "fp-1")  # hit
    cache.get("req-2", "fp-2")  # miss
    assert cache.metrics.hits == 2
    assert cache.metrics.misses == 1
