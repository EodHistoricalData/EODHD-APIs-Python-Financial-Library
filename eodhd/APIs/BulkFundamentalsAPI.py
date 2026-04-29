# APIs/BulkFundamentalsAPI.py

from .BaseAPI import BaseAPI


class BulkFundamentalsAPI(BaseAPI):
    """
    Wrapper for the Bulk Fundamentals endpoint:

        GET /api/bulk-fundamentals/{exchange}
    """

    def get_bulk_fundamentals(self, api_token: str, exchange: str, symbols: str = None, offset: int = None, limit: int = None):
        """
        Get fundamental data in bulk for an entire exchange.

        Parameters
        ----------
        api_token : str
            Your EODHD API token.
        exchange : str
            Exchange code, e.g. "US".
        symbols : str, optional
            Comma-separated list of tickers to filter, e.g. "AAPL,MSFT".
        offset : int, optional
            Pagination offset.
        limit : int, optional
            Maximum number of results.

        Returns
        -------
        list[dict] or dict
            Bulk fundamentals data.
        """
        if not exchange or not isinstance(exchange, str) or exchange.strip() == "":
            raise ValueError("Parameter 'exchange' is required and must be a non-empty string.")

        endpoint = "bulk-fundamentals"
        uri = exchange.strip()
        querystring = ""

        if symbols is not None:
            querystring += f"&symbols={symbols}"
        if offset is not None:
            querystring += f"&offset={int(offset)}"
        if limit is not None:
            querystring += f"&limit={int(limit)}"

        return self._rest_get_method(
            api_key=api_token,
            endpoint=endpoint,
            uri=uri,
            querystring=querystring,
        )
