# APIs/CommoditiesAPI.py

from .BaseAPI import BaseAPI


VALID_CODES = {
    "WTI", "BRENT", "NG", "RBOB",
    "GOLD", "SILVER", "PLATINUM", "PALLADIUM", "COPPER",
    "WHEAT", "CORN", "SOYBEANS", "SUGAR", "COFFEE", "COTTON", "COCOA", "OATS", "RICE",
    "LUMBER", "RUBBER", "WOOL",
    "ALL_COMMODITIES",
}

VALID_INTERVALS = {"d", "w", "m", "q", "a"}


class CommoditiesAPI(BaseAPI):
    """
    Wrapper for the Commodities Historical Data endpoint:

        GET /api/commodities/historical/{code}

    Parameters:
        code      - commodity code (e.g. "WTI", "GOLD", "ALL_COMMODITIES")
        interval  - data interval: d (daily), w (weekly), m (monthly), q (quarterly), a (annual)
        fmt       - response format: "json" or "xml"
    """

    def get_commodity_history(
        self,
        api_token: str,
        code: str,
        interval: str = None,
        fmt: str = None,
    ):
        """
        Parameters
        ----------
        api_token : str
            Your EODHD API token.
        code : str
            Commodity code, e.g. "WTI", "GOLD", "ALL_COMMODITIES".
        interval : str, optional
            Data interval: "d", "w", "m", "q", or "a".
        fmt : str, optional
            "json" or "xml".

        Returns
        -------
        dict
            JSON response with keys: meta, data, links.
        """
        if not code or not isinstance(code, str):
            raise ValueError("Parameter 'code' is required and must be a non-empty string (e.g. 'WTI', 'GOLD').")

        code = code.upper()
        if code not in VALID_CODES:
            raise ValueError(f"Invalid commodity code '{code}'. Valid codes: {sorted(VALID_CODES)}")

        if interval is not None:
            interval = str(interval).lower()
            if interval not in VALID_INTERVALS:
                raise ValueError(f"Invalid interval '{interval}'. Valid intervals: {sorted(VALID_INTERVALS)}")

        if fmt is not None:
            fmt = str(fmt).lower()
            if fmt not in ("json", "xml"):
                raise ValueError("fmt must be 'json' or 'xml'.")

        endpoint = "commodities/historical"
        uri = code
        query_string = ""

        if interval is not None:
            query_string += f"&interval={interval}"

        if fmt is not None:
            query_string += f"&fmt={fmt}"

        return self._rest_get_method(
            api_key=api_token,
            endpoint=endpoint,
            uri=uri,
            querystring=query_string,
        )
