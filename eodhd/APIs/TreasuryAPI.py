# APIs/TreasuryAPI.py

from .BaseAPI import BaseAPI


class TreasuryAPI(BaseAPI):
    """
    Wrapper for US Treasury rate endpoints:

        GET /api/ust/bill-rates
        GET /api/ust/yield-rates
        GET /api/ust/long-term-rates
        GET /api/ust/real-yield-rates

    These endpoints do not support pagination or date-range filtering
    (page[limit], page[offset], from, to are ignored by the API). The only
    supported filter is filter[year], which selects a single calendar year;
    when omitted the API returns the current year's dataset.
    """

    def _get_treasury_data(self, api_token: str, rate_type: str, year: int = None):
        """Internal helper for treasury endpoints.

        When ``year`` is provided it is sent as filter[year]=<year>; otherwise
        no filter is emitted and the API defaults to the current year.
        """
        endpoint = "ust"
        uri = rate_type

        query_string = self._filter("year", year)

        return self._rest_get_method(
            api_key=api_token,
            endpoint=endpoint,
            uri=uri,
            querystring=query_string,
        )

    def get_treasury_bill_rates(self, api_token: str, year: int = None):
        """
        Get US Treasury bill rates.

        Parameters
        ----------
        api_token : str
            Your EODHD API token.
        year : int, optional
            Calendar year to select (sent as filter[year]). Defaults to the
            current year when omitted. This is the only supported filter — the
            endpoint has no pagination and no date-range parameters.

        Returns
        -------
        list[dict]
            Treasury bill rate data.
        """
        return self._get_treasury_data(api_token, "bill-rates", year=year)

    def get_treasury_yield_rates(self, api_token: str, year: int = None):
        """
        Get US Treasury yield curve rates.

        Parameters
        ----------
        api_token : str
            Your EODHD API token.
        year : int, optional
            Calendar year to select (sent as filter[year]). Defaults to the
            current year when omitted. This is the only supported filter — the
            endpoint has no pagination and no date-range parameters.

        Returns
        -------
        list[dict]
            Treasury yield rate data.
        """
        return self._get_treasury_data(api_token, "yield-rates", year=year)

    def get_treasury_long_term_rates(self, api_token: str, year: int = None):
        """
        Get US Treasury long-term rates.

        Parameters
        ----------
        api_token : str
            Your EODHD API token.
        year : int, optional
            Calendar year to select (sent as filter[year]). Defaults to the
            current year when omitted. This is the only supported filter — the
            endpoint has no pagination and no date-range parameters.

        Returns
        -------
        list[dict]
            Treasury long-term rate data.
        """
        return self._get_treasury_data(api_token, "long-term-rates", year=year)

    def get_treasury_real_yield_rates(self, api_token: str, year: int = None):
        """
        Get US Treasury real yield curve rates.

        Parameters
        ----------
        api_token : str
            Your EODHD API token.
        year : int, optional
            Calendar year to select (sent as filter[year]). Defaults to the
            current year when omitted. This is the only supported filter — the
            endpoint has no pagination and no date-range parameters.

        Returns
        -------
        list[dict]
            Treasury real yield rate data.
        """
        return self._get_treasury_data(api_token, "real-yield-rates", year=year)
