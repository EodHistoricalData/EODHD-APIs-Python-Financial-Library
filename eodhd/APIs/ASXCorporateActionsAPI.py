# APIs/ASXCorporateActionsAPI.py

from urllib.parse import quote

from .BaseAPI import BaseAPI


class ASXCorporateActionsAPI(BaseAPI):
    """
    Wrapper for the ASX Corporate Actions endpoint:

        GET /api/asx-corporate-actions

    Notes:
    - Returns a JSON:API envelope { data, meta, links }.
      meta has { total, page: { offset, limit } }; links has { next }.
    - Filtering uses BARE query params (type=, symbol=, date_from=, date_to=),
      NOT filter[...]. Pagination uses page[offset] and page[limit].
    - data[] items vary by action type (dividends carry code/date/value/currency/
      exchange/recordDate/paymentDate/period/_asx_extra with franking fields;
      splits carry code/date/split/exchange; etc.).
    - 1 API call per request.
    """

    _TYPE_VALUES = (
        "dividends",
        "splits",
        "bonus-issues",
        "rights-issues",
        "buybacks",
        "capital-returns",
        "spp",
        "other",
    )

    @staticmethod
    def _param(name: str, value) -> str:
        """Build a URL-encoded &name=value fragment.

        Returns "" for None or blank/whitespace-only values (so an empty string
        is treated as "omit the param", not "send &name="). Values are
        URL-encoded; the key is a bare query param (not filter[...])."""
        if value is None:
            return ""
        text = str(value).strip()
        if text == "":
            return ""
        return f"&{name}={quote(text, safe='')}"

    @staticmethod
    def _pagination(page_offset: int = None, page_limit: int = None) -> str:
        query_string = ""
        if page_offset is not None:
            page_offset = int(page_offset)
            if page_offset < 0:
                raise ValueError("page_offset must be >= 0.")
            query_string += f"&page[offset]={page_offset}"
        if page_limit is not None:
            page_limit = int(page_limit)
            if page_limit < 1 or page_limit > 1000:
                raise ValueError("page_limit must be between 1 and 1000.")
            query_string += f"&page[limit]={page_limit}"
        return query_string

    def get_corporate_actions(
        self,
        api_token: str,
        type: str = None,
        symbol: str = None,
        date_from: str = None,
        date_to: str = None,
        page_offset: int = None,
        page_limit: int = None,
    ):
        """
        GET /api/asx-corporate-actions

        Query params (bare, not filter[...]):
            type      - action type: "dividends" | "splits" | "bonus-issues" |
                        "rights-issues" | "buybacks" | "capital-returns" |
                        "spp" | "other"
            symbol    - ASX ticker with .AU suffix, e.g. "PMV.AU"
            date_from - start date, YYYY-MM-DD
            date_to   - end date, YYYY-MM-DD
            page[offset] - pagination offset (default 0)
            page[limit]  - pagination limit, 1-1000 (default 100)

        Returns: dict envelope { data, meta, links }.
        """
        if type is not None and str(type).strip().lower() not in self._TYPE_VALUES:
            raise ValueError(f"type must be one of {self._TYPE_VALUES}.")

        query_string = ""
        if type is not None:
            query_string += self._param("type", str(type).strip().lower())
        query_string += self._param("symbol", symbol)
        query_string += self._param("date_from", date_from)
        query_string += self._param("date_to", date_to)
        query_string += self._pagination(page_offset, page_limit)

        return self._rest_get_method(
            api_key=api_token,
            endpoint="asx-corporate-actions",
            uri="",
            querystring=query_string,
        )
