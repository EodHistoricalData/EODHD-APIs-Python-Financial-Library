# APIs/BaseAPI.py

from json.decoder import JSONDecodeError
from urllib.parse import quote
import requests
from requests import ConnectionError as requests_ConnectionError
from requests import Timeout as requests_Timeout
from rich.console import Console

from eodhd.errors import EODHDHTTPError, EODHDConnectionError, EODHDTimeoutError


class BaseAPI:

    def __init__(self, session: requests.Session = None, timeout: tuple = (5.0, 30.0)) -> None:
        self._api_url = "https://eodhd.com/api"
        self._session = session
        self._timeout = timeout
        self.console = Console()

    @staticmethod
    def _blank_to_none(value):
        """Return None for None or a blank/whitespace-only string, else the value unchanged."""
        if value is None:
            return None
        if isinstance(value, str) and value.strip() == "":
            return None
        return value

    @staticmethod
    def _filter(name: str, value) -> str:
        """Build a URL-encoded &filter[name]=value fragment for deep-object filters.

        None and blank/whitespace-only values are omitted (treated as "no filter"),
        so an empty string never becomes a spurious &filter[name]= on the wire.
        """
        if value is None:
            return ""
        text = str(value).strip()
        if text == "":
            return ""
        return f"&filter[{name}]={quote(text, safe='')}"

    @staticmethod
    def _param(name: str, value) -> str:
        """Build a URL-encoded &name=value fragment for BARE query params (not filter[...]).

        None and blank/whitespace-only values are omitted.
        """
        if value is None:
            return ""
        text = str(value).strip()
        if text == "":
            return ""
        return f"&{name}={quote(text, safe='')}"

    @staticmethod
    def _coerce_page_int(name: str, value) -> int:
        """Coerce a pagination value to int, rejecting bools and non-whole floats.

        Accepts real ints and integer-valued strings (e.g. "10"); rejects True/False
        and fractional floats so a request is never silently altered (e.g. 1.9 -> 1)."""
        if isinstance(value, bool):
            raise ValueError(f"{name} must be an integer.")
        try:
            ivalue = int(value)
        except (TypeError, ValueError) as err:
            raise ValueError(f"{name} must be an integer.") from err
        if isinstance(value, float) and ivalue != value:
            raise ValueError(f"{name} must be a whole number.")
        return ivalue

    @staticmethod
    def _pagination(page_offset=None, page_limit=None) -> str:
        """Build &page[offset]/&page[limit] fragments, validating the server's bounds
        (offset >= 0, 1 <= limit <= 100)."""
        query_string = ""
        if page_offset is not None:
            page_offset = BaseAPI._coerce_page_int("page_offset", page_offset)
            if page_offset < 0:
                raise ValueError("page_offset must be >= 0.")
            query_string += f"&page[offset]={page_offset}"
        if page_limit is not None:
            page_limit = BaseAPI._coerce_page_int("page_limit", page_limit)
            if page_limit < 1:
                raise ValueError("page_limit must be >= 1.")
            if page_limit > 100:
                raise ValueError("page_limit must be <= 100.")
            query_string += f"&page[limit]={page_limit}"
        return query_string

    def _do_get(self, url: str):
        """Execute GET using session if available, else bare requests.get."""
        if self._session is not None:
            return self._session.get(url, timeout=self._timeout)
        return requests.get(url, timeout=self._timeout)

    def _rest_get_method(self, api_key: str, endpoint: str = "", uri: str = "", querystring: str = ""):
        """Generic REST GET — raises EODHDHTTPError/EODHDConnectionError/EODHDTimeoutError on failure."""

        if endpoint.strip() == "":
            raise ValueError("endpoint is empty!")

        url = f"{self._api_url}/{endpoint}/{uri}?api_token={api_key}&fmt=json{querystring}"

        try:
            resp = self._do_get(url)
        except requests_ConnectionError as err:
            raise EODHDConnectionError(str(err)) from err
        except requests_Timeout as err:
            raise EODHDTimeoutError(str(err)) from err

        if resp.status_code != 200:
            try:
                body = resp.text
            except Exception:
                body = ""

            try:
                data = resp.json()
                message = data.get("message", "") or str(data.get("errors", ""))
            except (JSONDecodeError, ValueError):
                message = ""

            raise EODHDHTTPError(
                status_code=resp.status_code,
                response_body=body,
                message=f"({resp.status_code}) {self._api_url} - {message}" if message else f"HTTP {resp.status_code}",
            )

        try:
            return resp.json()
        except (JSONDecodeError, ValueError) as err:
            raise EODHDHTTPError(
                status_code=resp.status_code,
                response_body=resp.text,
                message=f"Invalid JSON response: {err}",
            ) from err

    def _rest_get_raw(self, api_key: str, endpoint: str = "", uri: str = "", querystring: str = ""):
        """Generic REST GET returning raw bytes (for binary endpoints like logo)."""

        if endpoint.strip() == "":
            raise ValueError("endpoint is empty!")

        url = f"{self._api_url}/{endpoint}/{uri}?api_token={api_key}&fmt=json{querystring}"

        try:
            resp = self._do_get(url)
        except requests_ConnectionError as err:
            raise EODHDConnectionError(str(err)) from err
        except requests_Timeout as err:
            raise EODHDTimeoutError(str(err)) from err

        if resp.status_code != 200:
            try:
                body = resp.text
            except Exception:
                body = ""

            try:
                data = resp.json()
                message = data.get("message", "") or str(data.get("errors", ""))
            except (JSONDecodeError, ValueError):
                message = ""

            raise EODHDHTTPError(
                status_code=resp.status_code,
                response_body=body,
                message=f"({resp.status_code}) {self._api_url} - {message}" if message else f"HTTP {resp.status_code}",
            )

        return resp.content

    def _rest_post_method(self, api_key: str, endpoint: str = "", uri: str = "", querystring: str = "", body=None):
        """Generic REST POST with JSON body."""

        if endpoint.strip() == "":
            raise ValueError("endpoint is empty!")

        url = f"{self._api_url}/{endpoint}/{uri}?api_token={api_key}&fmt=json{querystring}"

        try:
            if self._session is not None:
                resp = self._session.post(url, json=body, timeout=self._timeout)
            else:
                resp = requests.post(url, json=body, timeout=self._timeout)
        except requests_ConnectionError as err:
            raise EODHDConnectionError(str(err)) from err
        except requests_Timeout as err:
            raise EODHDTimeoutError(str(err)) from err

        if resp.status_code != 200:
            try:
                resp_body = resp.text
            except Exception:
                resp_body = ""

            try:
                data = resp.json()
                message = data.get("message", "") or str(data.get("errors", ""))
            except (JSONDecodeError, ValueError):
                message = ""

            raise EODHDHTTPError(
                status_code=resp.status_code,
                response_body=resp_body,
                message=f"({resp.status_code}) {self._api_url} - {message}" if message else f"HTTP {resp.status_code}",
            )

        try:
            return resp.json()
        except (JSONDecodeError, ValueError) as err:
            raise EODHDHTTPError(
                status_code=resp.status_code,
                response_body=resp.text,
                message=f"Invalid JSON response: {err}",
            ) from err
