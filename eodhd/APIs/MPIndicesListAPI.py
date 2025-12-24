#APIs/MPIndicesListAPI.py

from .BaseAPI import BaseAPI


class MPIndicesListAPI(BaseAPI):
    """
    Wrapper for the Indices List endpoint:

        GET /api/mp/unicornbay/spglobal/list

    Returns list of indices with details like following 100+ indices:
    Global S&P and Dow Jones Indexes, including S&P 500, 600, 100, 400,
    and key industry indices.
    """

    def get_indices_list(self, api_token: str):
        """
        Get the list of indices with details.

        Parameters
        ----------
        api_token : str
            Your EODHD Marketplace API token.

        Returns
        -------
        list[dict]
            List of index objects with fields like:
            ID, Code, Name, Constituents, Value, MarketCap, Divisor,
            DailyReturn, Dividend, AdjustedMarketCap, AdjustedDivisor,
            AdjustedConstituents, CurrencyCode, CurrencyName,
            CurrencySymbol, LastUpdate.
        """
        endpoint = "mp/unicornbay/spglobal/list"

        # No extra query parameters currently documented for this endpoint
        query_string = ""

        return self._rest_get_method(
            api_key=api_token,
            endpoint=endpoint,
            querystring=query_string,
        )
