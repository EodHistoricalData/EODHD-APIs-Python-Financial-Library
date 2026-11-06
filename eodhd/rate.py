# rate.py

from typing import Dict, Optional

LIMIT_HEADER = "X-RateLimit-Limit"
REMAINING_HEADER = "X-RateLimit-Remaining"


class RateLimitInfo:
    """Snapshot of the API rate-limit headers from the most recently seen response.

    Deliberately not a singleton: each APIClient instance keeps its own snapshot
    (attached to its own requests.Session), so multiple clients running in the
    same process — e.g. configured with different API keys — never share or
    clobber each other's rate-limit state.
    """

    __slots__ = ("_limit", "_remaining")

    def __init__(self, limit: Optional[int] = None, remaining: Optional[int] = None) -> None:
        self._limit = limit
        self._remaining = remaining

    @property
    def limit(self) -> Optional[int]:
        return self._limit

    @property
    def remaining(self) -> Optional[int]:
        return self._remaining

    def __str__(self) -> str:
        if self._limit is None or self._remaining is None:
            return "rate limit unknown"
        return f"{self._remaining} / {self._limit} remaining"

    def __repr__(self) -> str:
        return f"RateLimitInfo(limit={self._limit!r}, remaining={self._remaining!r})"

    @classmethod
    def from_headers(cls, headers: Dict[str, str]) -> Optional["RateLimitInfo"]:
        """Build a RateLimitInfo from response headers, or None if the pair is absent/malformed."""
        if LIMIT_HEADER not in headers or REMAINING_HEADER not in headers:
            return None
        try:
            limit = int(headers[LIMIT_HEADER])
            remaining = int(headers[REMAINING_HEADER])
        except (TypeError, ValueError):
            return None
        return cls(limit=limit, remaining=remaining)
