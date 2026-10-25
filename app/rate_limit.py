

import time
from collections import deque
from threading import Lock


class RateLimiter:
    def __init__(self, max_attempts: int, window_seconds: float):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self._attempts: dict[str, deque[float]] = {}
        self._lock = Lock()

    def _recent_attempts(self, key: str, now: float) -> deque[float]:
        attempts = self._attempts.get(key, deque())
        while attempts and now - attempts[0] > self.window_seconds:
            attempts.popleft()
        if attempts:
            self._attempts[key] = attempts
        else:
            self._attempts.pop(key, None)
        return attempts

    def is_blocked(self, key: str) -> bool:
        with self._lock:
            return len(self._recent_attempts(key, time.monotonic())) >= self.max_attempts

    def register(self, key: str) -> None:
        with self._lock:
            now = time.monotonic()
            attempts = self._recent_attempts(key, now)
            attempts.append(now)
            self._attempts[key] = attempts

    def reset(self) -> None:
        with self._lock:
            self._attempts.clear()