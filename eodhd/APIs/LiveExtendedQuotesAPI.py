#APIs/LiveExtendedQuotesAPI.py

from .BaseAPI import BaseAPI


class LiveExtendedQuotesAPI(BaseAPI):
    """
    Wrapper for:
        GET /api/us-quote-delayed

    Live v2 for US Stocks: Extended Quotes (delayed, exchange-compliant).
    """

    def get_us_extended_quotes(
        self,
        api_token: str,
        symbols,
        page_limit: int = None,
        page_offset: int = None,
        fmt: str = None,  # "json" or "csv"
    ):
        """
        Get delayed extended quotes for one or more US symbols.

        Parameters
        ----------
        api_token : str
            Your EODHD API access token.
        symbols : str | list | tuple | set
            One or more tickers. Examples:
            - "AAPL.US"
            - "AAPL.US,TSLA.US"
            - ["AAPL.US", "TSLA.US"]
        page_limit : int, optional
            Number of symbols per page (max 100).
        page_offset : int, optional
            Offset for pagination (>= 0).
        fmt : str, optional
            "json" (default) or "csv".
        """
        if symbols is None or symbols == "" or symbols == [] or symbols == ():
            raise ValueError("Parameter 'symbols' is required (one or more tickers).")

        # Normalize symbols -> comma-separated string
        if isinstance(symbols, (list, tuple, set)):
            parts = [str(x).strip() for x in symbols if x is not None and str(x).strip()]
            if not parts:
                raise ValueError("Parameter 'symbols' is required (one or more tickers).")
            symbols_param = ",".join(parts)
        else:
            symbols_param = str(symbols).strip()
            if symbols_param == "":
                raise ValueError("Parameter 'symbols' is required (one or more tickers).")

        if page_limit is not None:
            page_limit = int(page_limit)
            if page_limit < 1 or page_limit > 100:
                raise ValueError("page_limit must be in range 1..100.")
        if page_offset is not None:
            page_offset = int(page_offset)
            if page_offset < 0:
                raise ValueError("page_offset must be >= 0.")

        if fmt is not None:
            fmt = str(fmt).lower()
            if fmt not in ("json", "csv"):
                raise ValueError("fmt must be 'json' or 'csv'.")

        endpoint = "us-quote-delayed"
        query_string = f"&s={symbols_param}"

        if page_limit is not None:
            query_string += f"&page[limit]={page_limit}"
        if page_offset is not None:
            query_string += f"&page[offset]={page_offset}"
        if fmt is not None:
            query_string += f"&fmt={fmt}"

        return self._rest_get_method(
            api_key=api_token,
            endpoint=endpoint,
            querystring=query_string,
        )
