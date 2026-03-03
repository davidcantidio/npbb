"""In-memory sliding-window rate limiting helpers."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from threading import Lock


@dataclass(frozen=True, slots=True)
class RateLimitDecision:
    allowed: bool
    remaining: int
    retry_after_seconds: int


class SlidingWindowRateLimiter:
    """Simple in-memory rate limiter for per-key request bursts."""

    def __init__(self, *, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max(1, int(max_requests))
        self.window_seconds = max(1, int(window_seconds))
        self._events: dict[str, deque[datetime]] = {}
        self._lock = Lock()

    def _now(self) -> datetime:
        return datetime.now(timezone.utc)

    def allow(self, key: str, *, now_fn: Callable[[], datetime] | None = None) -> RateLimitDecision:
        now = (now_fn or self._now)()
        window_start = now - timedelta(seconds=self.window_seconds)

        with self._lock:
            events = self._events.setdefault(key, deque())
            while events and events[0] < window_start:
                events.popleft()

            if len(events) >= self.max_requests:
                retry_after = int((events[0] + timedelta(seconds=self.window_seconds) - now).total_seconds())
                return RateLimitDecision(
                    allowed=False,
                    remaining=0,
                    retry_after_seconds=max(1, retry_after),
                )

            events.append(now)
            remaining = max(0, self.max_requests - len(events))
            return RateLimitDecision(
                allowed=True,
                remaining=remaining,
                retry_after_seconds=0,
            )
