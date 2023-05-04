from .BaseAPI import BaseAPI

class LiveStockPricesAPI(BaseAPI):

    def get_live_stock_prices(self, api_token: str, ticker: str):
        
        endpoint = 'real-time/'

        if ticker.strip() == "" or ticker is None:
            raise ValueError("Ticker is empty. You need to add ticker to args")
        

        return self._rest_get_method(api_key = api_token, endpoint = endpoint, uri = ticker)

