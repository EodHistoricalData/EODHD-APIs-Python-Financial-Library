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
    (page[limit], page[offset], from, to are ignored by the API). The full
    dataset for a given year is always returned.
    """

    def _get_treasury_data(self, api_token: str, rate_type: str):
        """Internal helper for treasury endpoints."""
        endpoint = "ust"
        uri = rate_type

        return self._rest_get_method(
            api_key=api_token,
            endpoint=endpoint,
            uri=uri,
        )

    def get_treasury_bill_rates(self, api_token: str):
        """
        Get US Treasury bill rates.

        Parameters
        ----------
        api_token : str
            Your EODHD API token.

        Returns
        -------
        list[dict]
            Treasury bill rate data.
        """
        return self._get_treasury_data(api_token, "bill-rates")

    def get_treasury_yield_rates(self, api_token: str):
        """
        Get US Treasury yield curve rates.

        Parameters
        ----------
        api_token : str
            Your EODHD API token.

        Returns
        -------
        list[dict]
            Treasury yield rate data.
        """
        return self._get_treasury_data(api_token, "yield-rates")

    def get_treasury_long_term_rates(self, api_token: str):
        """
        Get US Treasury long-term rates.

        Parameters
        ----------
        api_token : str
            Your EODHD API token.

        Returns
        -------
        list[dict]
            Treasury long-term rate data.
        """
        return self._get_treasury_data(api_token, "long-term-rates")

    def get_treasury_real_yield_rates(self, api_token: str):
        """
        Get US Treasury real yield curve rates.

        Parameters
        ----------
        api_token : str
            Your EODHD API token.

        Returns
        -------
        list[dict]
            Treasury real yield rate data.
        """
        return self._get_treasury_data(api_token, "real-yield-rates")
