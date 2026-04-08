# APIs/CommoditiesAPI.py

from .BaseAPI import BaseAPI


VALID_CODES = {
    # Energy
    "WTI", "BRENT", "NATURAL_GAS", "GASOLINE_US",
    "DIESEL_USGULF", "HEATING_OIL_NYH", "JET_FUEL_USGULF", "PROPANE_MBTX",
    "COAL_AU", "URANIUM",
    # Metals
    "COPPER", "ALUMINUM",
    # Agricultural
    "WHEAT", "CORN", "SUGAR", "COTTON", "COFFEE_MILD_ARABICA", "COFFEE_ROBUSTAS",
    # Indices
    "ALL_COMMODITIES", "ALL_COMMODITIES_PRODUCER", "ENERGY_INDEX", "NATGAS_EU", "LNG_ASIA",
}

VALID_INTERVALS = {"daily", "weekly", "monthly", "quarterly", "annual"}


class CommoditiesAPI(BaseAPI):
    """
    Wrapper for the Commodities Historical Data endpoint:

        GET /api/commodities/historical/{code}

    Parameters:
        code      - commodity code (e.g. "WTI", "NATURAL_GAS", "ALL_COMMODITIES")
        interval  - data interval: daily, weekly, monthly (default), quarterly, annual
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
            Commodity code, e.g. "WTI", "NATURAL_GAS", "ALL_COMMODITIES".
        interval : str, optional
            Data interval: "daily", "weekly", "monthly", "quarterly", or "annual".
        fmt : str, optional
            "json" or "xml".

        Returns
        -------
        dict
            JSON response with keys: meta, data, links.
        """
        if not code or not isinstance(code, str):
            raise ValueError("Parameter 'code' is required and must be a non-empty string (e.g. 'WTI', 'NATURAL_GAS').")

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
