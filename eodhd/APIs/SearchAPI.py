# APIs/SearchAPI.py

from .BaseAPI import BaseAPI


class SearchAPI(BaseAPI):
    """
    Wrapper for the Search endpoint:

        GET /api/search/{query}
    """

    def search(self, api_token: str, query: str, limit: int = None):
        """
        Search for stocks, ETFs, mutual funds, indices, and cryptocurrencies.

        Parameters
        ----------
        api_token : str
            Your EODHD API token.
        query : str
            Search query (company name, ticker, ISIN).
        limit : int, optional
            Maximum number of results to return.

        Returns
        -------
        list[dict]
            List of matching instruments.
        """
        if not query or not isinstance(query, str) or query.strip() == "":
            raise ValueError("Parameter 'query' is required and must be a non-empty string.")

        endpoint = "search"
        uri = query.strip()
        querystring = ""

        if limit is not None:
            querystring += f"&limit={int(limit)}"

        return self._rest_get_method(
            api_key=api_token,
            endpoint=endpoint,
            uri=uri,
            querystring=querystring,
        )
