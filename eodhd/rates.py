"""rates.py"""

from typing import Dict, Optional

LIMIT_HEADER = "X-RateLimit-Limit"
REMAINING_HEADER = "X-RateLimit-Remaining"


class Rate(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Rate, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        self._limit: Optional[int] = None
        self._remaining: Optional[int] = None

    def __str__(self):
        return f"{self.remaining} / {self.limit} remaining"

    @property
    def limit(self) -> Optional[int]:
        return self._limit
    
    @property
    def remaining(self) -> Optional[int]:
        return self._remaining
    
    def update_from_headers(self, headers: Dict[str, str]) -> None:
        if not all(key in headers for key in [LIMIT_HEADER, REMAINING_HEADER]):
            return

        limit = int(headers.get(LIMIT_HEADER))
        remaining = int(headers.get(REMAINING_HEADER))

        self._limit = limit
        self._remaining = remaining
