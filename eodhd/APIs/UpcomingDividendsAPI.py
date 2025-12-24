#APIs/UpcomingDividendsAPI.py

from .BaseAPI import BaseAPI


class UpcomingDividendsAPI(BaseAPI):

    def get_upcoming_dividends_data(
        self,
        api_token: str,
        symbol=None,
        date_eq=None,
        date_from=None,
        date_to=None,
        page_limit=None,
        page_offset=None,
    ):
        """
        Wrapper for the /calendar/dividends endpoint.

        Parameters
        ----------
        api_token : str
            Your EODHD API token.
        symbol : str, optional
            Ticker symbol, e.g. "AAPL.US".
            Required if `date_eq` is not provided.
        date_eq : str, optional
            Exact dividend date in format YYYY-MM-DD.
            Required if `symbol` is not provided.
        date_from : str, optional
            Return dividends on or after this date (YYYY-MM-DD).
            Usually used together with `symbol`.
        date_to : str, optional
            Return dividends on or before this date (YYYY-MM-DD).
            Usually used together with `symbol`.
        page_limit : int, optional
            Max results per page (1–1000). Default on API side is 1000.
        page_offset : int, optional
            Offset for pagination. Default on API side is 0.
        """

        # Enforce API requirement: at least one of symbol or date_eq
        if symbol is None and date_eq is None:
            raise ValueError("Either 'symbol' or 'date_eq' must be provided.")

        endpoint = "calendar/dividends"
        query_string = ""

        if symbol is not None:
            query_string += f"&filter[symbol]={symbol}"
        if date_eq is not None:
            query_string += f"&filter[date_eq]={date_eq}"
        if date_from is not None:
            query_string += f"&filter[date_from]={date_from}"
        if date_to is not None:
            query_string += f"&filter[date_to]={date_to}"
        if page_limit is not None:
            query_string += f"&page[limit]={page_limit}"
        if page_offset is not None:
            query_string += f"&page[offset]={page_offset}"

        return self._rest_get_method(
            api_key=api_token,
            endpoint=endpoint,
            querystring=query_string,
        )
