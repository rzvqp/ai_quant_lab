"""Bounded, deterministic cache for `TowerClient` (CEO/Red Team remediation, 2026-08-14:
`TowerClient._cache` was unbounded -- Red Team demonstrated 5,000 entries with zero eviction).

Explicit `max_entries` + explicit `ttl_seconds` + LRU eviction (an `OrderedDict`, `move_to_end` on every
hit, `popitem(last=False)` when over budget) -- never "grows until something else notices". `clear()` is
called by the launcher on every new session (fresh `session_id`, i.e. every restart) -- a cached result
from a DIFFERENT worker process/session must never leak into a new one.

**Request-ID-reuse rule, kept separate from normal caching**: the same `request_id` with the SAME request
fingerprint may return the cached result (a genuine retry). The same `request_id` with a DIFFERENT
fingerprint is a distinct failure mode -- `check_reuse` reports it explicitly so the caller can refuse with
`REQUEST_ID_REUSE_MISMATCH` rather than silently caching two different answers under one key or, worse,
returning whichever happened to be cached first."""

from __future__ import annotations

import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True, slots=True, kw_only=True)
class CacheMetrics:
    size: int
    max_entries: int
    hits: int
    misses: int
    evictions: int


@dataclass(frozen=True, slots=True, kw_only=True)
class _Entry(Generic[T]):
    value: T
    fingerprint: str
    inserted_at: float


class BoundedTowerCache(Generic[T]):
    def __init__(
        self, *, max_entries: int = 1000, ttl_seconds: float = 300.0,
        now_fn: Callable[[], float] = time.monotonic,
    ) -> None:
        if max_entries < 1:
            raise ValueError("max_entries must be >= 1")
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be > 0")
        self._max_entries = max_entries
        self._ttl_seconds = ttl_seconds
        self._now_fn = now_fn
        self._entries: OrderedDict[str, _Entry[T]] = OrderedDict()
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    def check_reuse(self, request_id: str, fingerprint: str) -> bool:
        """True if `request_id` is already cached under a DIFFERENT fingerprint -- caller must refuse with
        `REQUEST_ID_REUSE_MISMATCH` rather than proceeding to `get`/`put`. Does not consult TTL: even an
        expired entry's fingerprint still proves the ID was already used for something else."""
        self._evict_expired()
        entry = self._entries.get(request_id)
        return entry is not None and entry.fingerprint != fingerprint

    def get(self, request_id: str, fingerprint: str) -> T | None:
        self._evict_expired()
        entry = self._entries.get(request_id)
        if entry is None or entry.fingerprint != fingerprint:
            self._misses += 1
            return None
        self._entries.move_to_end(request_id)
        self._hits += 1
        return entry.value

    def put(self, request_id: str, fingerprint: str, value: T) -> None:
        self._entries[request_id] = _Entry(value=value, fingerprint=fingerprint, inserted_at=self._now_fn())
        self._entries.move_to_end(request_id)
        while len(self._entries) > self._max_entries:
            self._entries.popitem(last=False)
            self._evictions += 1

    def clear(self) -> None:
        """Called on every new session (fresh handshake, i.e. every worker restart) -- a cached result
        belongs to the session that produced it, never carried forward into a new one."""
        self._entries.clear()

    def _evict_expired(self) -> None:
        now = self._now_fn()
        expired = [key for key, entry in self._entries.items() if now - entry.inserted_at > self._ttl_seconds]
        for key in expired:
            del self._entries[key]
            self._evictions += 1

    @property
    def metrics(self) -> CacheMetrics:
        return CacheMetrics(
            size=len(self._entries), max_entries=self._max_entries, hits=self._hits, misses=self._misses,
            evictions=self._evictions,
        )
