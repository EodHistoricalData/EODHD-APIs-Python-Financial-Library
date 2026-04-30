# APIs/FundamentalDataAPI.py

from .BaseAPI import BaseAPI


class FundamentalDataAPI(BaseAPI):

    def get_fundamentals_data(self, api_token: str, ticker: str, filter: str = None,
                              historical: int = None, from_date: str = None, to_date: str = None,
                              version: int = None, no_cache: int = None):
        endpoint = 'fundamentals'

        if ticker is None or ticker.strip() == "":
            raise ValueError("Ticker is empty. You need to add ticker to args")

        querystring = ""
        if filter is not None:
            querystring += f"&filter={filter}"
        if historical is not None:
            querystring += f"&historical={int(historical)}"
        if from_date is not None:
            querystring += f"&from={from_date}"
        if to_date is not None:
            querystring += f"&to={to_date}"
        if version is not None:
            querystring += f"&version={int(version)}"
        if no_cache is not None:
            querystring += f"&no_cache={int(no_cache)}"

        return self._rest_get_method(api_key=api_token, endpoint=endpoint, uri=ticker, querystring=querystring)

    def get_fundamentals_data_v1_1(self, api_token: str, ticker: str, filter: str = None,
                                    historical: int = None, from_date: str = None, to_date: str = None,
                                    version: int = None, no_cache: int = None):
        endpoint = 'v1.1/fundamentals'

        if ticker is None or ticker.strip() == "":
            raise ValueError("Ticker is empty. You need to add ticker to args")

        querystring = ""
        if filter is not None:
            querystring += f"&filter={filter}"
        if historical is not None:
            querystring += f"&historical={int(historical)}"
        if from_date is not None:
            querystring += f"&from={from_date}"
        if to_date is not None:
            querystring += f"&to={to_date}"
        if version is not None:
            querystring += f"&version={int(version)}"
        if no_cache is not None:
            querystring += f"&no_cache={int(no_cache)}"

        return self._rest_get_method(api_key=api_token, endpoint=endpoint, uri=ticker, querystring=querystring)
