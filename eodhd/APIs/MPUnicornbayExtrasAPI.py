# APIs/MPUnicornbayExtrasAPI.py

from .BaseAPI import BaseAPI


class MPUnicornbayExtrasAPI(BaseAPI):
    """
    Wrapper for additional Unicornbay Marketplace endpoints:

        GET /api/mp/unicornbay/tickdata/ticks
        GET /api/mp/unicornbay/logo/{symbol}
    """

    def get_tickdata(self, api_token: str, symbol: str, from_timestamp: int = None, to_timestamp: int = None,
                     page_offset: int = None, page_limit: int = None):
        """
        Get tick-level data for a symbol.

        Parameters
        ----------
        symbol : str
            Symbol to get tick data for.
        from_timestamp : int, optional
            Start timestamp (Unix epoch).
        to_timestamp : int, optional
            End timestamp (Unix epoch).
        page_offset : int, optional
            Pagination offset.
        page_limit : int, optional
            Pagination limit.

        Returns
        -------
        dict
            Tick data with meta, data, and links.
        """
        if not symbol or not isinstance(symbol, str):
            raise ValueError("Parameter 'symbol' is required.")

        querystring = f"&symbol={symbol.strip()}"

        if from_timestamp is not None:
            querystring += f"&from={int(from_timestamp)}"
        if to_timestamp is not None:
            querystring += f"&to={int(to_timestamp)}"
        if page_offset is not None:
            querystring += f"&page[offset]={int(page_offset)}"
        if page_limit is not None:
            querystring += f"&page[limit]={int(page_limit)}"

        return self._rest_get_method(
            api_key=api_token,
            endpoint="mp/unicornbay/tickdata/ticks",
            querystring=querystring,
        )

    def get_logo(self, api_token: str, symbol: str):
        """
        Get a company logo via Unicornbay Marketplace.

        Parameters
        ----------
        symbol : str
            Symbol in TICKER.EXCHANGE format.

        Returns
        -------
        bytes
            Raw image data.
        """
        if not symbol or not isinstance(symbol, str):
            raise ValueError("Parameter 'symbol' is required.")

        return self._rest_get_raw(
            api_key=api_token,
            endpoint="mp/unicornbay/logo",
            uri=symbol.strip(),
        )
