# APIs/TreasuryAPI.py

from .BaseAPI import BaseAPI


class TreasuryAPI(BaseAPI):
    """
    Wrapper for US Treasury rate endpoints:

        GET /api/ust/bill-rates
        GET /api/ust/yield-rates
        GET /api/ust/long-term-rates
        GET /api/ust/real-yield-rates
    """

    def _get_treasury_data(self, api_token: str, rate_type: str, from_date: str = None, to_date: str = None):
        """Internal helper for treasury endpoints."""
        endpoint = "ust"
        uri = rate_type
        querystring = ""

        if from_date is not None:
            querystring += f"&from={from_date}"
        if to_date is not None:
            querystring += f"&to={to_date}"

        return self._rest_get_method(
            api_key=api_token,
            endpoint=endpoint,
            uri=uri,
            querystring=querystring,
        )

    def get_treasury_bill_rates(self, api_token: str, from_date: str = None, to_date: str = None):
        """
        Get US Treasury bill rates.

        Parameters
        ----------
        api_token : str
            Your EODHD API token.
        from_date : str, optional
            Start date in YYYY-MM-DD format.
        to_date : str, optional
            End date in YYYY-MM-DD format.

        Returns
        -------
        list[dict]
            Treasury bill rate data.
        """
        return self._get_treasury_data(api_token, "bill-rates", from_date, to_date)

    def get_treasury_yield_rates(self, api_token: str, from_date: str = None, to_date: str = None):
        """
        Get US Treasury yield curve rates.

        Parameters
        ----------
        api_token : str
            Your EODHD API token.
        from_date : str, optional
            Start date in YYYY-MM-DD format.
        to_date : str, optional
            End date in YYYY-MM-DD format.

        Returns
        -------
        list[dict]
            Treasury yield rate data.
        """
        return self._get_treasury_data(api_token, "yield-rates", from_date, to_date)

    def get_treasury_long_term_rates(self, api_token: str, from_date: str = None, to_date: str = None):
        """
        Get US Treasury long-term rates.

        Parameters
        ----------
        api_token : str
            Your EODHD API token.
        from_date : str, optional
            Start date in YYYY-MM-DD format.
        to_date : str, optional
            End date in YYYY-MM-DD format.

        Returns
        -------
        list[dict]
            Treasury long-term rate data.
        """
        return self._get_treasury_data(api_token, "long-term-rates", from_date, to_date)

    def get_treasury_real_yield_rates(self, api_token: str, from_date: str = None, to_date: str = None):
        """
        Get US Treasury real yield curve rates.

        Parameters
        ----------
        api_token : str
            Your EODHD API token.
        from_date : str, optional
            Start date in YYYY-MM-DD format.
        to_date : str, optional
            End date in YYYY-MM-DD format.

        Returns
        -------
        list[dict]
            Treasury real yield rate data.
        """
        return self._get_treasury_data(api_token, "real-yield-rates", from_date, to_date)
