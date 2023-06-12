from .BaseAPI import BaseAPI

class BulkforEODSplitsDividendsAPI(BaseAPI):

    def exchange_EOD(self, api_token: str, country = 'US', date = None, symbols = None, filter = None):
        
        endpoint = 'eod-bulk-last-day'
        uri = f'{country}'

        query_string = ''
        
        if date is not None:
            query_string += '&date=' + str(date)
        if symbols:
            query_string += '&symbols=' + str(symbols)
        if filter is not None:
            query_string += '&filter=' + str(filter)    
        
       
        
        return self._rest_get_method(api_key = api_token, endpoint = endpoint, uri = uri, querystring = query_string)
    
