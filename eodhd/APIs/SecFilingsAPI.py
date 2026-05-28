# APIs/SecFilingsAPI.py

from .BaseAPI import BaseAPI


class SecFilingsAPI(BaseAPI):

    def get_sec_filings_form4(self, api_token: str, symbol: str,
                              page_offset: int = None, page_limit: int = None):
        """Insider Transactions v2 (SEC Form 4): GET /sec-filings/{symbol}/form4

        Returns paginated SEC Form 4 filings for a US-listed symbol, parsed directly
        from SEC EDGAR. Each filing contains non-derivative (direct stock) and derivative
        (options, RSUs, warrants) transactions plus referenced footnotes.

        Parameters:
            api_token: EODHD API token
            symbol: US ticker symbol (e.g. 'AAPL' or 'AAPL.US')
            page_offset: pagination offset (zero-based, default 0)
            page_limit: page size (1-100, default 20)

        Cost: 10 API calls per request.
        Plans: Fundamentals and All-In-One.

        For more information visit: https://eodhd.com/financial-apis/insider-transactions-api/
        """

        endpoint = 'sec-filings'
        uri = f'{symbol}/form4'

        query_string = ''
        if page_offset is not None:
            query_string += f"&page[offset]={page_offset}"
        if page_limit is not None:
            query_string += f"&page[limit]={page_limit}"

        return self._rest_get_method(api_key=api_token, endpoint=endpoint, uri=uri, querystring=query_string)
