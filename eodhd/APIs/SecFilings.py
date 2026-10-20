# APIs/SecFilings.py

from .BaseAPI import BaseAPI


class SecFilingsAPI(BaseAPI):
    """
    Wrapper for the SEC Filings API:

        GET /api/sec-filings/{symbol}        overview (counts + latest per form type)
        GET /api/sec-filings/{symbol}/10k    annual reports (10-K), paginated
        GET /api/sec-filings/{symbol}/10q    quarterly reports (10-Q), paginated
        GET /api/sec-filings/{symbol}/8k     material events (8-K), paginated

    Notes:
    - The overview endpoint returns { data, meta, links } where data is a dict
      { ticker, exchange, name, cik, filings } and filings is keyed by form type
      ("10k"/"10q"/"8k"/"form4"), each { count, latest, url }. meta and links are
      empty and there is no pagination.
    - The 10-K, 10-Q and 8-K endpoints return { data, meta, links } with data as a
      list of rows and meta { total, page: { offset, limit } }; links.next is a
      URL string or null.
    - Pagination uses page[offset] (>= 0, default 0) and page[limit] (1..100,
      default 20).
    - Any numeric field in a row may be null.
    - Responses are parsed JSON.

    Docs: https://eodhd.com/financial-apis/sec-filings-api
    """

    @staticmethod
    def _validate_symbol(symbol) -> str:
        """Validate a ticker symbol and return it stripped (e.g. 'AAPL.US')."""
        if symbol is None or not isinstance(symbol, str) or symbol.strip() == "":
            raise ValueError("Parameter 'symbol' is required and must be a non-empty string (e.g. 'AAPL.US').")
        return symbol.strip()

    def get_sec_filings_overview(self, api_token: str, symbol: str):
        """
        GET /api/sec-filings/{symbol}

        Overview of a company's SEC filings: counts, latest date and URL per form
        type. Parameterless (no pagination).

        Params:
            symbol: ticker symbol (e.g. "AAPL.US").

        Response data (dict): { ticker, exchange, name, cik,
            filings: { "10k": {count, latest, url}, "10q": {...},
                       "8k": {...}, "form4": {...} } }.
        """
        symbol = self._validate_symbol(symbol)

        return self._rest_get_method(
            api_key=api_token,
            endpoint="sec-filings",
            uri=symbol,
            querystring="",
        )

    def get_sec_filings_10k(self, api_token: str, symbol: str,
                            page_offset: int = 0, page_limit: int = 20):
        """
        GET /api/sec-filings/{symbol}/10k

        Annual reports (10-K) with parsed financials, paginated.

        Params:
            symbol: ticker symbol (e.g. "AAPL.US").
            page_offset: >= 0 (default 0). page_limit: 1..100 (default 20).

        Response data[] row: accession_number, filed_at, period_of_report,
        fiscal_year_end plus the parsed income-statement, balance-sheet and
        cash-flow financials (any numeric may be null).
        """
        symbol = self._validate_symbol(symbol)

        query_string = self._pagination(page_offset, page_limit)

        return self._rest_get_method(
            api_key=api_token,
            endpoint="sec-filings",
            uri=f"{symbol}/10k",
            querystring=query_string,
        )

    def get_sec_filings_10q(self, api_token: str, symbol: str,
                            page_offset: int = 0, page_limit: int = 20):
        """
        GET /api/sec-filings/{symbol}/10q

        Quarterly reports (10-Q) with parsed financials, paginated.

        Same shape as the 10-K rows except the period metadata is
        fiscal_quarter_end (str) instead of fiscal_year_end, plus fiscal_quarter
        (int).

        Params:
            symbol: ticker symbol (e.g. "AAPL.US").
            page_offset: >= 0 (default 0). page_limit: 1..100 (default 20).
        """
        symbol = self._validate_symbol(symbol)

        query_string = self._pagination(page_offset, page_limit)

        return self._rest_get_method(
            api_key=api_token,
            endpoint="sec-filings",
            uri=f"{symbol}/10q",
            querystring=query_string,
        )

    def get_sec_filings_8k(self, api_token: str, symbol: str,
                           page_offset: int = 0, page_limit: int = 20):
        """
        GET /api/sec-filings/{symbol}/8k

        Material events (8-K), paginated.

        Params:
            symbol: ticker symbol (e.g. "AAPL.US").
            page_offset: >= 0 (default 0). page_limit: 1..100 (default 20).

        Response data[] item: { accession_number, filed_at, period_of_report,
        items: [str], item_sections: [{item, title, text}],
        exhibits: [{number, description}] }.
        """
        symbol = self._validate_symbol(symbol)

        query_string = self._pagination(page_offset, page_limit)

        return self._rest_get_method(
            api_key=api_token,
            endpoint="sec-filings",
            uri=f"{symbol}/8k",
            querystring=query_string,
        )
