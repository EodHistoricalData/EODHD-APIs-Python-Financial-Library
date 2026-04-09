# APIs/BaseAPI.py

from json.decoder import JSONDecodeError
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
