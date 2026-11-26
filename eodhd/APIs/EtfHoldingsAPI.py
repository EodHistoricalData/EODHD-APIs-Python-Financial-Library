# APIs/EtfHoldingsAPI.py

from urllib.parse import quote

from .BaseAPI import BaseAPI


class EtfHoldingsAPI(BaseAPI):
    """
    Wrapper for the ETF Holdings API (beta, SEC N-PORT data, US-listed ETFs only):

        GET /api/etf/holdings/{ticker}
        GET /api/etf/security/{ticker}/held-by

    Notes:
    - Both endpoints return a JSON envelope { data, meta, links }.
    - Each request costs 10 API calls. Plans: Fundamentals Data Feed and All-In-One.
    - Neither endpoint documents `fmt`; the response is always JSON (the shared
      request helper appends fmt=json, which the server ignores - see the smoke test).
    - On 404 the JSON error body carries a `code` such as FUND_NOT_FOUND,
      NOT_COVERED or NO_HOLDINGS_YET; it is in EODHDHTTPError.response_body.
    """

    _HELD_BY_MAX_LIMIT = 5000

    def get_holdings(self, api_token: str, ticker: str):
        """
        GET /api/etf/holdings/{ticker}

        Holdings of one US-listed ETF, all positions in one response (large funds
        can be several MB). `ticker` is the ETF ticker with or without the `.US`
        suffix (e.g. "VTI" or "VTI.US"). Other exchanges return 422.

        Cost: 10 API calls per request. The demo token works for VTI.

        Notes:
        - `data.Holdings` is an empty list (not an object) for a fund with no positions.
        """
        ticker = self._blank_to_none(ticker)
        if ticker is None:
            raise ValueError("ticker is required.")

        return self._rest_get_method(
            api_key=api_token,
            endpoint="etf",
            uri=f"holdings/{quote(str(ticker).strip(), safe='')}",
            querystring="",
        )

    def get_held_by(
        self,
        api_token: str,
        ticker: str,
        page_offset: int = None,
        page_limit: int = None,
    ):
        """
        GET /api/etf/security/{ticker}/held-by

        Funds that hold a given security, sorted by weight descending. `ticker` is
        the looked-up security (e.g. "NVDA", or "ASML.AS" for a foreign listing),
        not a fund.

        Query params:
            page[offset] - zero-based, default 0
            page[limit]  - 1 to 5000, default 100

        Cost: 10 API calls per request. The demo token is rejected (403).
        """
        ticker = self._blank_to_none(ticker)
        if ticker is None:
            raise ValueError("ticker is required.")

        query_string = ""
        if page_offset is not None:
            page_offset = self._coerce_page_int("page_offset", page_offset)
            if page_offset < 0:
                raise ValueError("page_offset must be >= 0.")
            query_string += f"&page[offset]={page_offset}"
        if page_limit is not None:
            page_limit = self._coerce_page_int("page_limit", page_limit)
            if page_limit < 1:
                raise ValueError("page_limit must be >= 1.")
            if page_limit > self._HELD_BY_MAX_LIMIT:
                raise ValueError(f"page_limit must be <= {self._HELD_BY_MAX_LIMIT}.")
            query_string += f"&page[limit]={page_limit}"

        return self._rest_get_method(
            api_key=api_token,
            endpoint="etf",
            uri=f"security/{quote(str(ticker).strip(), safe='')}/held-by",
            querystring=query_string,
        )
