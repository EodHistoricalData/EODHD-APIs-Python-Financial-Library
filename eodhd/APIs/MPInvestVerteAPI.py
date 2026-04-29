# APIs/MPInvestVerteAPI.py

from .BaseAPI import BaseAPI


class MPInvestVerteAPI(BaseAPI):
    """
    Wrapper for the Marketplace InvestVerte ESG endpoints:

        GET /api/mp/investverte/companies
        GET /api/mp/investverte/countries
        GET /api/mp/investverte/sectors
        GET /api/mp/investverte/esg/{symbol}
        GET /api/mp/investverte/country/{symbol}
        GET /api/mp/investverte/sector/{symbol}
    """

    def get_companies(self, api_token: str):
        """Get list of companies with ESG data available."""
        return self._rest_get_method(
            api_key=api_token,
            endpoint="mp/investverte/companies",
        )

    def get_countries(self, api_token: str):
        """Get list of countries with ESG data available."""
        return self._rest_get_method(
            api_key=api_token,
            endpoint="mp/investverte/countries",
        )

    def get_sectors(self, api_token: str):
        """Get list of sectors with ESG data available."""
        return self._rest_get_method(
            api_key=api_token,
            endpoint="mp/investverte/sectors",
        )

    def get_esg(self, api_token: str, symbol: str):
        """
        Get ESG data for a specific company.

        Parameters
        ----------
        symbol : str
            Symbol in TICKER.EXCHANGE format (e.g. "AAPL.US").
        """
        if not symbol or not isinstance(symbol, str):
            raise ValueError("Parameter 'symbol' is required.")
        return self._rest_get_method(
            api_key=api_token,
            endpoint="mp/investverte/esg",
            uri=symbol.strip(),
        )

    def get_country(self, api_token: str, symbol: str):
        """
        Get country-level ESG data.

        Parameters
        ----------
        symbol : str
            Country symbol/code.
        """
        if not symbol or not isinstance(symbol, str):
            raise ValueError("Parameter 'symbol' is required.")
        return self._rest_get_method(
            api_key=api_token,
            endpoint="mp/investverte/country",
            uri=symbol.strip(),
        )

    def get_sector(self, api_token: str, symbol: str):
        """
        Get sector-level ESG data.

        Parameters
        ----------
        symbol : str
            Sector symbol/code.
        """
        if not symbol or not isinstance(symbol, str):
            raise ValueError("Parameter 'symbol' is required.")
        return self._rest_get_method(
            api_key=api_token,
            endpoint="mp/investverte/sector",
            uri=symbol.strip(),
        )
