#APIs/CBOEIndexFeedAPI.py

from .BaseAPI import BaseAPI


class CBOEIndexFeedAPI(BaseAPI):
    """
    Wrapper for the CBOE Index Feed endpoint:

        GET /api/cboe/index

    Required (deep object style):
        filter[index_code]
        filter[feed_type]
        filter[date]   (YYYY-MM-DD)

    Optional:
        fmt (json/xml)
    """

    def get_cboe_index_data(
        self,
        api_token: str,
        index_code: str,
        feed_type: str,
        date: str,
        fmt: str = None,
    ):
        """
        Parameters
        ----------
        api_token : str
            Your EODHD API token.
        index_code : str
            CBOE index code, e.g. "BDE30P"
        feed_type : str
            Feed type, e.g. "snapshot_official_closing"
        date : str
            Trading date in YYYY-MM-DD format, e.g. "2017-02-01"
        fmt : str, optional
            "json" or "xml". If omitted, API default applies (usually json).

        Returns
        -------
        dict
            JSON response with keys like meta, data (array), etc.
        """
        if not index_code or not isinstance(index_code, str):
            raise ValueError("Parameter 'index_code' is required and must be a non-empty string (e.g. 'BDE30P').")

        if not feed_type or not isinstance(feed_type, str):
            raise ValueError("Parameter 'feed_type' is required and must be a non-empty string (e.g. 'snapshot_official_closing').")

        if not date or not isinstance(date, str):
            raise ValueError("Parameter 'date' is required and must be a non-empty string in 'YYYY-MM-DD' format (e.g. '2017-02-01').")

        if fmt is not None:
            fmt = str(fmt).lower()
            if fmt not in ("json", "xml"):
                raise ValueError("fmt must be 'json' or 'xml'.")

        endpoint = "cboe/index"
        query_string = (
            f"&filter[index_code]={index_code}"
            f"&filter[feed_type]={feed_type}"
            f"&filter[date]={date}"
        )

        if fmt is not None:
            query_string += f"&fmt={fmt}"

        return self._rest_get_method(
            api_key=api_token,
            endpoint=endpoint,
            querystring=query_string,
        )

    def get_cboe_indices_list(self, api_token: str, fmt: str = None):
        """
        Parameters
        ----------
        api_token : str
            Your EODHD API token.
        fmt : str, optional
            "json" or "xml" (default is json on API side)

        Returns
        -------
        dict
            JSON response: { "meta": {...}, "data": [...], "links": {"next": ...} }
        """
        if fmt is not None:
            fmt = str(fmt).lower()
            if fmt not in ("json", "xml"):
                raise ValueError("fmt must be 'json' or 'xml'.")

        endpoint = "cboe/indices"
        query_string = ""

        if fmt is not None:
            query_string += f"&fmt={fmt}"

        return self._rest_get_method(
            api_key=api_token,
            endpoint=endpoint,
            querystring=query_string,
        )

