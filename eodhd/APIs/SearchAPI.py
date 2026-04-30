# APIs/SearchAPI.py

from .BaseAPI import BaseAPI


class SearchAPI(BaseAPI):
    """
    Wrapper for the Search endpoint:

        GET /api/search/{query}
    """

    def search(self, api_token: str, query: str, limit: int = None,
               type: str = None, exchange: str = None, bonds_only: int = None):
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
        type : str, optional
            Filter by instrument type.
        exchange : str, optional
            Filter by exchange code.
        bonds_only : int, optional
            Set to 1 to return only bonds.

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
        if type is not None:
            querystring += f"&type={type}"
        if exchange is not None:
            querystring += f"&exchange={exchange}"
        if bonds_only is not None:
            querystring += f"&bonds_only={int(bonds_only)}"

        return self._rest_get_method(
            api_key=api_token,
            endpoint=endpoint,
            uri=uri,
            querystring=querystring,
        )
