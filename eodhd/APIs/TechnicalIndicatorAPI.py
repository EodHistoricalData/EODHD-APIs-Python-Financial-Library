from .BaseAPI import BaseAPI

class TechnicalIndicatorAPI(BaseAPI):

    def get_technical_indicator_data(self, api_token: str, ticker: str, function: str, period: int = 50,
                                     date_from: str = None, date_to: str = None, order: str = 'a', 
                                     splitadjusted_only: str = '0'):
        
        endpoint = 'technical/'

        if ticker.strip() == "" or ticker is None:
            raise ValueError("Ticker is empty. You need to add ticker to args")
        
        if function.strip() == "" or function is None:
            raise ValueError("Function is empty. You need to add function to args")
        
        query_string = f'&order={order}&splitadjusted_only={splitadjusted_only}&period={period}&function={function}'
        
        if date_to is not None:
            query_string += "&to=" + date_to
        if date_from is not None:
            query_string += "&from=" + date_from

        return self._rest_get_method(api_key = api_token, endpoint = endpoint, uri = ticker, querystring = query_string)




