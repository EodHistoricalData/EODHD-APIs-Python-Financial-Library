"""Custom exception hierarchy for the EODHD Python SDK."""


class EODHDError(Exception):
    """Base exception for all EODHD SDK errors."""


class EODHDHTTPError(EODHDError):
    """Raised when the API returns a non-2xx HTTP status."""

    def __init__(self, status_code: int, response_body: str, message: str = ""):
        self.status_code = status_code
        self.response_body = response_body
        self.message = message or f"HTTP {status_code}"
        super().__init__(self.message)


class EODHDConnectionError(EODHDError):
    """Raised when the API is unreachable."""


class EODHDTimeoutError(EODHDError):
    """Raised when an API request times out."""
