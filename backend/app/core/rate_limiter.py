"""In-memory sliding window rate limiter for security endpoints."""
import time
from collections import defaultdict, deque
from threading import Lock
from typing import Dict, Tuple

from starlette.requests import Request


def get_client_ip(request: Request) -> str:
    """Extract client IP safely; only trust forwarded headers from local/internal proxies."""
    # ponytail: trust loopback and private subnets; upgrade to explicit TRUSTED_PROXIES config when public facing
    host = request.client.host if request.client else "unknown"
    is_proxy = (
        host == "127.0.0.1"
        or host == "::1"
        or host.startswith("172.")
        or host.startswith("10.")
        or host.startswith("192.168.")
    )
    if is_proxy:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return host


class SlidingWindowRateLimiter:
    # ponytail: in-memory limiter ceiling ~10k keys; upgrade to Redis when multi-worker or multi-server
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._history: Dict[str, deque] = defaultdict(deque)
        self._lock = Lock()

    def is_allowed(self, key: str) -> Tuple[bool, int]:
        """
        Check if request is allowed for the given key.
        Returns (allowed: bool, retry_after_seconds: int).
        """
        now = time.time()
        window_start = now - self.window_seconds

        with self._lock:
            # Periodic cleanup if map grows too large
            if len(self._history) > 1000:
                dead_keys = [
                    k for k, q in self._history.items()
                    if not q or q[-1] <= window_start
                ]
                for k in dead_keys:
                    del self._history[k]

            timestamps = self._history[key]
            # Prune timestamps older than window
            while timestamps and timestamps[0] <= window_start:
                timestamps.popleft()

            if len(timestamps) < self.max_requests:
                timestamps.append(now)
                return True, 0

            # Calculate retry after
            oldest = timestamps[0]
            retry_after = max(1, int(oldest + self.window_seconds - now))
            return False, retry_after

    def reset(self, key: str) -> None:
        """Reset history for a key (e.g. on successful login)."""
        with self._lock:
            self._history.pop(key, None)


# 1. Login Rate Limiter: max 5 login attempts per 60 seconds per IP/Email
login_rate_limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=60)

# 2. Registration Rate Limiter: max 5 account registrations per 60 seconds per IP
register_rate_limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=60)

# 3. AI ChemBot Rate Limiter: max 10 requests per 60 seconds per User
chembot_rate_limiter = SlidingWindowRateLimiter(max_requests=10, window_seconds=60)
