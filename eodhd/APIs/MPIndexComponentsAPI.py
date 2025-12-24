#APIs/MPIndexComponentsAPI.py

from .BaseAPI import BaseAPI


class MPIndexComponentsAPI(BaseAPI):
    """
    Wrapper for the Index Components endpoint:

        GET /api/mp/unicornbay/spglobal/comp/{symbol}

    Provides:
    - Current list of components for an index.
    - Optional historical changes (2–12 years for major indices),
      including additions/exclusions with dates, and flags like
      IsActiveNow and IsDelisted.
    """

    def get_index_components(
        self,
        api_token: str,
        symbol: str,
        historical=None,
        from_date: str = None,
        to_date: str = None,
    ):
        """
        Get components (and optionally historical constituents) for a given index.

        Parameters
        ----------
        api_token : str
            Your EODHD Marketplace API token.
        symbol : str
            Index symbol, for example "GSPC.INDX".
            Can be obtained from the MPIndicesListAPI.
        historical : bool | int, optional
            If True / 1 — include historical changes.
            If False / 0 — only current components.
            If None — parameter is omitted.
        from_date : str, optional
            Start date (YYYY-MM-DD) for historical window.
        to_date : str, optional
            End date (YYYY-MM-DD) for historical window.

        Returns
        -------
        dict
            JSON object with keys such as:
            - "General"
            - "Components"
            - "HistoricalTickerComponents"
            - "HistoricalComponents"
        """
        if not symbol:
            raise ValueError("Parameter 'symbol' is required (index symbol, e.g. 'GSPC.INDX').")

        endpoint = "mp/unicornbay/spglobal/comp"
        uri = symbol

        query_string = ""

        if historical is not None:
            # Accept bool or int for convenience
            if isinstance(historical, bool):
                historical_value = 1 if historical else 0
            else:
                historical_value = int(historical)
            query_string += f"&historical={historical_value}"

        if from_date is not None:
            query_string += f"&from={from_date}"

        if to_date is not None:
            query_string += f"&to={to_date}"

        return self._rest_get_method(
            api_key=api_token,
            endpoint=endpoint,
            uri=uri,
            querystring=query_string,
        )
