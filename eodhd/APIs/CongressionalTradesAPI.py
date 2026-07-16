# APIs/CongressionalTradesAPI.py

from .BaseAPI import BaseAPI


class CongressionalTradesAPI(BaseAPI):
    """
    Wrapper for the Congressional Trades endpoint:

        GET /api/congressional-trades

    US Congress stock-trade disclosures filed under the STOCK Act, from the
    official Senate EFD and House Clerk sources. Requires the All-in-One plan;
    each request costs 10 API calls.

    Optional filters (flat query keys):
        symbol, chamber (senate/house), bioguide_id,
        transaction_type (purchase/sale/exchange, comma-separated for multiple),
        transaction_date_from, transaction_date_to,
        disclosure_date_from, disclosure_date_to

    Pagination:
        page_offset -> page[offset]   (default 0)
        page_limit  -> page[limit]    (default 20, max 100)
    """

    _CHAMBERS = ("senate", "house")
    _TRANSACTION_TYPES = ("purchase", "sale", "exchange")

    def get_congressional_trades(
        self,
        api_token: str,
        symbol: str = None,
        chamber: str = None,
        bioguide_id: str = None,
        transaction_type: str = None,
        transaction_date_from: str = None,
        transaction_date_to: str = None,
        disclosure_date_from: str = None,
        disclosure_date_to: str = None,
        page_offset: int = None,
        page_limit: int = None,
    ):
        """
        Parameters
        ----------
        api_token : str
            Your EODHD API token.
        symbol : str, optional
            Filter by a single ticker symbol, e.g. "AAPL".
        chamber : str, optional
            Filter by chamber: "senate" or "house".
        bioguide_id : str, optional
            Filter by a member's Bioguide ID, e.g. "S000250".
        transaction_type : str, optional
            One or more of "purchase", "sale", "exchange", comma-separated.
        transaction_date_from, transaction_date_to : str, optional
            Transaction date range, YYYY-MM-DD, inclusive.
        disclosure_date_from, disclosure_date_to : str, optional
            Disclosure date range, YYYY-MM-DD, inclusive.
        page_offset : int, optional
            Pagination offset (records to skip). Default 0.
        page_limit : int, optional
            Records per page. Default 20, maximum 100.

        Returns
        -------
        dict
            JSON response with keys: data (array), meta (total, page), links (next).
        """
        if chamber is not None:
            chamber = str(chamber).lower()
            if chamber not in self._CHAMBERS:
                raise ValueError("chamber must be 'senate' or 'house'.")

        if transaction_type is not None:
            for value in str(transaction_type).split(","):
                if value.strip().lower() not in self._TRANSACTION_TYPES:
                    raise ValueError(
                        "transaction_type values must be one of 'purchase', 'sale', 'exchange'."
                    )

        querystring = ""
        if symbol is not None:
            querystring += f"&symbol={symbol}"
        if chamber is not None:
            querystring += f"&chamber={chamber}"
        if bioguide_id is not None:
            querystring += f"&bioguide_id={bioguide_id}"
        if transaction_type is not None:
            querystring += f"&transaction_type={transaction_type}"
        if transaction_date_from is not None:
            querystring += f"&transaction_date_from={transaction_date_from}"
        if transaction_date_to is not None:
            querystring += f"&transaction_date_to={transaction_date_to}"
        if disclosure_date_from is not None:
            querystring += f"&disclosure_date_from={disclosure_date_from}"
        if disclosure_date_to is not None:
            querystring += f"&disclosure_date_to={disclosure_date_to}"
        if page_offset is not None:
            querystring += f"&page[offset]={int(page_offset)}"
        if page_limit is not None:
            querystring += f"&page[limit]={int(page_limit)}"

        return self._rest_get_method(
            api_key=api_token,
            endpoint="congressional-trades",
            querystring=querystring,
        )
