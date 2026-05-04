# APIs/ExchangeDetailsV2API.py

from .BaseAPI import BaseAPI


class ExchangeDetailsV2API(BaseAPI):

    def get_exchange_details_v2_list(self, api_token: str):
        """Get list of all supported exchanges with basic details (v2).

        Returns a list of exchange objects with codes and metadata.
        Endpoint: GET /v2/exchange-details
        """
        endpoint = 'v2/exchange-details'

        return self._rest_get_method(api_key=api_token, endpoint=endpoint)

    def get_exchange_details_v2(self, api_token: str, code: str):
        """Get detailed information for a specific exchange (v2).

        Includes trading hours, holidays, and early close schedules.

        Parameters:
            api_token: EODHD API token
            code: Exchange code (e.g. 'US', 'LSE', 'TO')

        Endpoint: GET /v2/exchange-details/{code}
        """
        endpoint = 'v2/exchange-details'
        uri = f'{code}'

        return self._rest_get_method(api_key=api_token, endpoint=endpoint, uri=uri)
