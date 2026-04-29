# APIs/LogoAPI.py

from .BaseAPI import BaseAPI


class LogoAPI(BaseAPI):
    """
    Wrapper for the Logo endpoints:

        GET /api/logo/{symbol}      → PNG bytes
        GET /api/logo-svg/{symbol}  → SVG bytes
    """

    def get_logo(self, api_token: str, symbol: str):
        """
        Get a company logo as PNG bytes.

        Parameters
        ----------
        api_token : str
            Your EODHD API token.
        symbol : str
            Symbol in TICKER.EXCHANGE format (e.g. "AAPL.US").

        Returns
        -------
        bytes
            Raw PNG image data.
        """
        if not symbol or not isinstance(symbol, str) or symbol.strip() == "":
            raise ValueError("Parameter 'symbol' is required.")

        return self._rest_get_raw(
            api_key=api_token,
            endpoint="logo",
            uri=symbol.strip(),
        )

    def get_logo_svg(self, api_token: str, symbol: str):
        """
        Get a company logo as SVG bytes.

        Parameters
        ----------
        api_token : str
            Your EODHD API token.
        symbol : str
            Symbol in TICKER.EXCHANGE format (e.g. "AAPL.US").

        Returns
        -------
        bytes
            Raw SVG image data.
        """
        if not symbol or not isinstance(symbol, str) or symbol.strip() == "":
            raise ValueError("Parameter 'symbol' is required.")

        return self._rest_get_raw(
            api_key=api_token,
            endpoint="logo-svg",
            uri=symbol.strip(),
        )
