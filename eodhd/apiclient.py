"""apiclient.py"""

from json.decoder import JSONDecodeError
import sys
from enum import Enum
from datetime import datetime
from datetime import timedelta
from re import compile as re_compile
import pandas as pd
import numpy as np
from requests import get as requests_get
from requests import ConnectionError as requests_ConnectionError
from requests import Timeout as requests_Timeout
from requests.exceptions import HTTPError as requests_HTTPError
from rich.console import Console
from rich.progress import track


from eodhd.APIs import *

# minimal traceback
sys.tracebacklimit = 1


class Interval(Enum):
    """Enum: infraday"""

    MINUTE = "1m"
    FIVEMINUTES = "5m"
    HOUR = "1h"
    ONEDAY = "1d"



class DateUtils:
    """Utility class"""

    @staticmethod
    def str2datetime(_datetime: str):
        """Convert yyyy-mm-dd hh:mm:ss to datetime"""

        # Validate string datetime
        prog = re_compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")
        if not prog.match(_datetime):
            raise ValueError("Incorrect datetime format: yyyy-mm-dd hh:mm:ss")

        return datetime.strptime(_datetime, "%Y-%m-%d %H:%M:%S")

    @staticmethod
    def str2epoch(_datetime: str):
        """Convert yyyy-mm-dd hh:mm:ss to datetime"""

        # Validate string datetime
        prog = re_compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")
        if not prog.match(_datetime):
            raise ValueError("Incorrect datetime format: yyyy-mm-dd hh:mm:ss")

        return int(datetime.strptime(_datetime, "%Y-%m-%d %H:%M:%S").timestamp())

    @staticmethod
    def previous_day_last_second():
        """Returns the last second of the previous day"""

        yesterday = datetime.today() - timedelta(days=1)
        return str(yesterday.date()) + " 23:59:59"

    @staticmethod
    def previous_day_last_minute():
        """Returns the last minute of the previous day"""

        yesterday = datetime.today() - timedelta(days=1)
        return str(yesterday.date()) + " 23:59:00"


class APIClient:
    """API class"""

    def __init__(self, api_key: str) -> None:
        # Validate API key
        prog = re_compile(r"^[A-z0-9.]{16,32}$")
        if api_key != "demo" and not prog.match(api_key):
            raise ValueError("API key is invalid")

        self._api_key = api_key
        self._api_url = "https://eodhistoricaldata.com/api"

        self.console = Console()

    def _rest_get(self, endpoint: str = "", uri: str = "", querystring: str = "") -> pd.DataFrame():
        """Generic REST GET"""

        if endpoint.strip() == "":
            raise ValueError("endpoint is empty!")

        try:
            resp = requests_get(f"{self._api_url}/{endpoint}/{uri}?api_token={self._api_key}&fmt=json{querystring}")

            if resp.status_code != 200:
                try:
                    if "message" in resp.json():
                        resp_message = resp.json()["message"]
                    elif "errors" in resp.json():
                        self.console.log(resp.json())
                        sys.exit(1)
                    else:
                        resp_message = ""

                    message = f"({resp.status_code}) {self._api_url} - {resp_message}"
                    self.console.log(message)

                except JSONDecodeError as err:
                    self.console.log(err)

            try:
                resp.raise_for_status()

                if isinstance(resp.json(), list):
                    return pd.DataFrame.from_dict(resp.json())
                else:
                    return pd.DataFrame(resp.json(), index=[0])

            except ValueError as err:
                self.console.log(err)

        except requests_ConnectionError as err:
            self.console.log(err)
        except requests_HTTPError as err:
            self.console.log(err)
        except requests_Timeout as err:
            self.console.log(err)
        return pd.DataFrame()

    def get_exchanges(self) -> pd.DataFrame:
        """Get supported exchanges"""

        return self._rest_get("exchanges-list")

    def get_exchange_symbols(self, uri: str = "") -> pd.DataFrame:
        """Get supported exchange symbols"""

        try:
            if uri.strip() == "":
                raise ValueError("endpoint uri is empty!")

            return self._rest_get("exchange-symbol-list", uri)
        except ValueError as err:
            self.console.log(err)
            return pd.DataFrame()

    def get_historical_data(
        self,
        symbol: str,
        interval: str = Interval,
        range_start: str = "",
        range_end: str = "",
    ) -> dict:
        """Initiates a REST API call"""

        # default set of results
        results = 300

        # validate symbol
        prog = re_compile(r"^[A-z0-9-$\.+]{1,48}$")
        if not prog.match(symbol):
            raise ValueError(f"Symbol is invalid: {symbol}")

        # replace "." with "-" in markets
        if symbol.count(".") == 2:
            symbol = symbol.replace(".", "-", 1)

        minutes = 1
        if interval == "5m":
            minutes = 5
        elif interval == "1h":
            minutes = 60

        # validate interval
        try:
            Interval(interval)
        except ValueError as err:
            self.console.log(err)
            return pd.DataFrame()

        if interval == "1d":
            prog = re_compile(r"^\d{4}\-\d{2}-\d{2}$")

            if range_end == "" or (range_end != "" and not prog.match(range_end)):
                date_to = datetime.today().date()
            else:
                try:
                    date_to = datetime.strptime(range_end, "%Y-%m-%d").date()
                except ValueError:
                    self.console.log("invalid end date (yyyy-mm-dd):", range_end)
                    sys.exit()

            if range_start == "" or (range_start != "" and not prog.match(range_start)):
                date_from = date_to - timedelta(days=(results - 1))
            else:
                try:
                    date_from = datetime.strptime(range_start, "%Y-%m-%d").date()
                except ValueError:
                    self.console.log("invalid start date (yyyy-mm-dd):", range_start)
                    sys.exit()

            df_data = self._rest_get(
                "eod",
                symbol,
                f"&interval={interval}&from={str(date_from)}&to={str(date_to)}",
            )

        else:
            prog = re_compile(r"^\d{4}\-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")

            if range_end == "" or (range_end != "" and not prog.match(range_end)):
                epoch_to = ""
            else:
                try:
                    epoch_to = int(datetime.strptime(range_end, "%Y-%m-%d %H:%M:%S").timestamp())
                except ValueError:
                    self.console.log("invalid end date (yyyy-mm-dd hh:mm:ss):", range_end)
                    sys.exit()

            if range_start == "" or (range_start != "" and not prog.match(range_start)):
                if interval == "1m":
                    epoch_from = str(DateUtils.str2epoch(str(datetime.now() - timedelta(days=1)).split(".")[0]))
                elif interval == "5m":
                    epoch_from = str(DateUtils.str2epoch(str(datetime.now() - timedelta(days=2)).split(".")[0]))
                elif interval == "1h":
                    epoch_from = str(DateUtils.str2epoch(str(datetime.now() - timedelta(days=14)).split(".")[0]))
                else:
                    epoch_from = str(int(epoch_to) - (((60 * minutes) * results) - ((60 * minutes) + 1)))
            else:
                try:
                    epoch_from = int(datetime.strptime(range_start, "%Y-%m-%d %H:%M:%S").timestamp())
                except ValueError:
                    self.console.log("invalid start date (yyyy-mm-dd hh:mm:ss):", range_start)
                    sys.exit()

            if epoch_to != "":
                df_data = self._rest_get(
                    "intraday",
                    symbol,
                    f"&interval={interval}&from={str(epoch_from)}&to={str(epoch_to)}",
                )
            else:
                df_data = self._rest_get(
                    "intraday",
                    symbol,
                    f"&interval={interval}&from={str(epoch_from)}",
                )

            if len(df_data) == 0:
                return df_data[
                    [
                        "symbol",
                        "interval",
                        "open",
                        "high",
                        "low",
                        "close",
                        "adjusted_close",
                        "volume",
                    ]
                ]

            if range_start == "" and range_end == "":
                df_data = df_data.tail(300)
            elif range_start != "" and range_end == "":
                df_data = df_data.head(300)

        df_data["symbol"] = symbol
        df_data["interval"] = interval

        # convert dataframe to a time series
        if interval == "1d":
            tsidx = pd.DatetimeIndex(pd.to_datetime(df_data["date"]).dt.strftime("%Y-%m-%d"))
            df_data.set_index(tsidx, inplace=True)
            df_data = df_data.drop(columns=["date"])
        else:
            tsidx = pd.DatetimeIndex(pd.to_datetime(df_data["datetime"]).dt.strftime("%Y-%m-%d %H:%M:%S"))
            df_data.set_index(tsidx, inplace=True)
            df_data = df_data.drop(columns=["datetime"])

        # rename columns
        if interval != "1d":
            df_data.columns = [
                "epoch",
                "gmtoffset",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "symbol",
                "interval",
            ]

        # return dataset
        if interval == "1d":
            df_data["adjusted_close"] = df_data["adjusted_close"].astype(object)
            df_data.fillna(0, inplace=True)

            return df_data[
                [
                    "symbol",
                    "interval",
                    "open",
                    "high",
                    "low",
                    "close",
                    "adjusted_close",
                    "volume",
                ]
            ]

        # set object type to display large floats
        df_data.fillna(0, inplace=True)
        df_data["gmtoffset"] = df_data["gmtoffset"].astype(object)
        df_data["epoch"] = df_data["epoch"].astype(object)
        df_data["open"] = df_data["open"].astype(object)
        df_data["high"] = df_data["high"].astype(object)
        df_data["low"] = df_data["low"].astype(object)
        df_data["close"] = df_data["close"].astype(object)
        df_data["volume"] = df_data["volume"].astype(object)

        return df_data[
            [
                "epoch",
                "gmtoffset",
                "symbol",
                "interval",
                "open",
                "high",
                "low",
                "close",
                "volume",
            ]
        ]
    
    def get_historical_dividends_data(self, ticker, date_to = None, date_from = None) -> list:
        """Available args:
            ticker (required) - consists of two parts: [SYMBOL_NAME].[EXCHANGE_ID]. Example: AAPL.US
            date_from (not required) - date from with format Y-m-d. Example: 2000-01-01
            date_to (not required) - date from with format Y-m-d. Example: 2000-01-01
            If you skip date_from or date_to then you’ll get the maximum available data for the symbol.
            For more information visit: https://eodhistoricaldata.com/financial-apis/api-splits-dividends/"""

        api_call = HistoricalDividendsAPI()
        return api_call.get_historical_dividends_data(api_token = self._api_key, ticker = ticker, date_from = date_from, date_to = date_to)
    

    def get_historical_splits_data(self, ticker, date_to = None, date_from = None) -> list:
        """Available args:
            ticker (required) - consists of two parts: [SYMBOL_NAME].[EXCHANGE_ID]. Example: AAPL.US
            date_from (not required) - date from with format Y-m-d. Example: 2000-01-01
            date_to (not required) - date from with format Y-m-d. Example: 2000-01-01
            If you skip date_from or date_to then you’ll get the maximum available data for the symbol.
            For more information visit: https://eodhistoricaldata.com/financial-apis/api-splits-dividends/"""

        api_call = HistoricalSplitsAPI()
        return api_call.get_historical_splits_data(api_token = self._api_key, ticker = ticker, date_from = date_from, date_to = date_to)
    

    def get_technical_indicator_data(self, ticker: str, function: str, period: int = 50,
                                     date_from: str = None, date_to: str = None, order: str = 'a', 
                                     splitadjusted_only: str = '0') -> list:
        """Available args:
            ticker (required) - consists of two parts: [SYMBOL_NAME].[EXCHANGE_ID]. Example: AAPL.US
            function (required) – the function that will be applied to data series to get technical indicator data. 
                The list of possible functions with additional parameters you get here: 
                https://eodhistoricaldata.com/financial-apis/technical-indicators-api/
            period – the number of data points used to calculate each moving average value. 
                Valid range from 2 to 100000 with the default value – 50.
            date_from (not required) - date from with format Y-m-d. Example: 2000-01-01
            date_to (not required) - date from with format Y-m-d. Example: 2000-01-01
            order – use ‘a’ for ascending dates (from old to new) and ‘d’ for descending dates (from new to old). 
                By default, dates are shown in ascending order.
            splitadjusted_only – default value is ‘0’. 
                By default, we calculate data for some functions by closes adjusted with splits and dividends. 
                If you need to calculate the data by closes adjusted only with splits, set this parameter to ‘1’. 
                Works with the following functions: sma, ema, wma, volatility, rsi, slope, and macd.
            """

        api_call = TechnicalIndicatorAPI()
        return api_call.get_technical_indicator_data(api_token = self._api_key, ticker = ticker, function = function,
                                                     period = period, date_from = date_from, date_to = date_to,
                                                     order = order, splitadjusted_only = splitadjusted_only)
    

    def get_live_stock_prices(self, ticker, date_to = None, date_from = None) -> list:
        """Available args:
            ticker (required) - consists of two parts: [SYMBOL_NAME].[EXCHANGE_ID]. Example: AAPL.US
            For more information visit: https://eodhistoricaldata.com/financial-apis/live-realtime-stocks-api/
            """

        api_call = LiveStockPricesAPI()
        return api_call.get_live_stock_prices(api_token = self._api_key, ticker = ticker)
    
    
    def get_economic_events_data(self, date_from: str = None, date_to: str = None,
                                 country: str = None, comparison: str = None, offset: int = None, limit: int = None) -> list:
        """Available args:
            date_from (not required) - date from with format Y-m-d. Example: 2000-01-01
            date_to (not required) - date from with format Y-m-d. Example: 2000-01-01
            country (not required) - The country code is in ISO 3166 format, has 2 symbols
            comparison (not required) - Possible values: mom, qoq, yoy
            offset (not required) - Possible values from 0 to 1000. Default value: 0
            limit (not required) - Possible values from 0 to 1000. Default value: 50.
            For more information visit: https://eodhistoricaldata.com/financial-apis/economic-events-data-api/
            """

        api_call = EconomicEventsDataAPI()
        return api_call.get_economic_events_data(api_token = self._api_key, date_from = date_from, date_to = date_to,
                                 country = country, comparison = comparison, offset = offset, limit = limit)
    

    def get_insider_transactions_data(self, date_from: str = None, date_to: str = None,
                                 code: str = None, limit: int = None) -> list:
        """Available args:
            date_from (not required) - date from with format Y-m-d. Example: 2000-01-01
            date_to (not required) - date from with format Y-m-d. Example: 2000-01-01
            code (not required) - to get the data only for Apple Inc (AAPL), use AAPL.US or AAPL ticker code. 
                By default, all possible symbols will be displayed.
            limit (not required) - the limit for entries per result, from 1 to 1000. Default value: 100.
            For more information visit: https://eodhistoricaldata.com/financial-apis/insider-transactions-api/
            """

        api_call = InsiderTransactionsAPI()
        return api_call.get_insider_transactions_data(api_token = self._api_key, date_from = date_from, date_to = date_to,
                                 code = code, limit = limit)
    
    
    def get_fundamentals_data(self, ticker: str) -> list:
        """Available args:
            ticker (required) - consists of two parts: [SYMBOL_NAME].[EXCHANGE_ID]. Example: AAPL.US
            For more information visit: https://eodhistoricaldata.com/financial-apis/stock-etfs-fundamental-data-feeds/
            """

        api_call = FundamentalDataAPI()
        return api_call.get_fundamentals_data(api_token = self._api_key, ticker = ticker)
    

    def get_bulk_fundamentals_data(self, country = 'US', type = None, date = None,
                                   symbols = None, filter = None) -> list:
        """Available args:
            type (not required) - can get splits, empty or dividends. 
                for splits function returns all splits for US stocks in bulk for a particular day
                for dividends function returns all dividends for US stocks in bulk for a particular day
                if type will remain empty then returns end-of-day data for US stocks in bulk for a particular day
            date (not required) - By default, the data for last trading day will be downloaded, but if you need any specific date
                you can add parameter
            symbols (not required) - To download last day data for several symbols, for example, 
                for MSFT and AAPL, you can add the ‘symbols’ parameter. For non-US tickers, 
                you should use the exchange code, for example, BMW.XETRA or SAP.F
                If you want get data for several codes you need to input in the next type of format: AAPL,BMW.XETRA,SAP.F
            For more information visit: https://eodhistoricaldata.com/financial-apis/bulk-api-eod-splits-dividends/
            """

        api_call = BulkFundamentalDataAPI()
        return api_call.get_bulk_fundamentals_data(api_token = self._api_key, country = country, type = type,
                                                   date = date, symbols = symbols, filter = filter)
    

    def get_upcoming_earnings_data(self, from_date = None, to_date = None, symbols = None) -> list:
        """Available args:
            from_date (not required) - Format: YYYY-MM-DD. The start date for earnings data, if not provided, today will be used.
            to_date (not required) - Format: YYYY-MM-DD. The end date for earnings data, if not provided, today + 7 days will be used.
            symbols (not required) - OPTIONAL. You can request specific symbols to get historical and upcoming data. 
                If ‘symbols’ used, then ‘from’ and ‘to’ parameters will be ignored. 
                You can use one symbol: ‘AAPL.US’ or several symbols separated by a comma: ‘AAPL.US, MS’
            For more information visit: https://eodhistoricaldata.com/financial-apis/calendar-upcoming-earnings-ipos-and-splits/#Upcoming_Earnings_API
            """
    
        api_call = UpcomgingEarningsAPI()
        return api_call.get_upcoming_earnings_data(api_token = self._api_key, from_date = from_date, to_date = to_date,
                                                    symbols = symbols)



    def get_earning_trends_data(self, symbols) -> list:
        """Available args:
            symbols (required) - You can request specific symbols to get historical and upcoming data. 
                f ‘symbols’ used, then ‘from’ and ‘to’ parameters will be ignored. 
                ou can use one symbol: ‘AAPL.US’ or several symbols separated by a comma: ‘AAPL.US, MS’
            For more information visit: https://eodhistoricaldata.com/financial-apis/calendar-upcoming-earnings-ipos-and-splits/#Earnings_Trends_API
            """
        api_call = EarningTrendsAPI()
        return api_call.get_earning_trends_data(api_token = self._api_key, symbols = symbols)
    

    def get_upcoming_IPOs_data(self, from_date = None, to_date = None) -> list:
        """Available args:
            from_date (not required) - Format: YYYY-MM-DD. The start date for ipos data, if not provided, today will be used.
            to_date (not required) - Format: YYYY-MM-DD. The end date for ipos data, if not provided, today + 7 days will be used.
            For more information visit: https://eodhistoricaldata.com/financial-apis/calendar-upcoming-earnings-ipos-and-splits/#Upcoming_Earnings_API
            """
    
        api_call = UpcomingIPOsAPI()
        return api_call.get_upcoming_IPOs_data(api_token = self._api_key, from_date = from_date, to_date = to_date)
    

    def get_upcoming_splits_data(self, from_date = None, to_date = None) -> list:
        """Available args:
            from_date (not required) - Format: YYYY-MM-DD. The start date for splits data, if not provided, today will be used.
            to_date (not required) - Format: YYYY-MM-DD. The end date for splits data, if not provided, today + 7 days will be used.
            For more information visit: https://eodhistoricaldata.com/financial-apis/calendar-upcoming-earnings-ipos-and-splits/#Upcoming_Earnings_API
            """
        
        api_call = UpcomingSplitsAPI()
        return api_call.get_upcoming_splits_data(api_token = self._api_key, from_date = from_date, to_date = to_date)
    

    def get_macro_indicators_data(self, country, indicator = None) -> list:
        """Available args:
            country (required) - Defines the country for which the indicator will be shown. 
                The country should be defined in the Alpha-3 ISO format. Possible values: USA, FRA, DEU…
            indicator (not required) - Defines which macroeconomics data indicator will be shown. 
                See the list of possible indicators below. The default value is ‘gdp_current_usd‘.
            All possible indicators will be avaliable on: https://eodhistoricaldata.com/financial-apis/macroeconomics-data-and-macro-indicators-api/
            """

        api_call = MacroIndicatorsAPI()
        return api_call.get_macro_indicators_data(api_token = self._api_key, country = country, indicator = indicator)


    def get_bonds_fundamentals_data(self, isin = None) -> list:
        """Available args:
            isin - An International Securities Identification Number, in current function isin may be cusip-code. 
                Other IDs are not supported at the moment.
            For more information visit: https://eodhistoricaldata.com/financial-apis/bonds-fundamentals-and-historical-api/
            """
        
        api_call = BondsFundamentalsAPI()
        return api_call.get_bonds_fundamentals_data(api_token = self._api_key, isin = isin)
    

class ScannerClient:
    """Scanner class"""

    def __init__(self, api_key: str) -> None:
        # Validate API key
        prog = re_compile(r"^[A-z0-9.]{16,32}$")
        if api_key != "demo" and not prog.match(api_key):
            raise ValueError("API key is invalid")

        self.api = APIClient(api_key)

    def scan_markets(
        self,
        market_type: str = "CC",
        interval: str = Interval,
        quote_currency: str = "USD",
        request_limit: int = 5000,
    ):
        """Scan markets"""

        if request_limit < 0 or request_limit > 100000:
            raise ValueError("request limit is out of bounds!")

        df_dataset = pd.DataFrame()

        resp = self.api.get_exchange_symbols(market_type)
        symbol_list = resp[resp.Code.str.endswith(f"-{quote_currency}", na=False)].Code.to_numpy()

        if request_limit > 0:
            # truncate symbol list to request limit minus symbol list request
            symbol_list = symbol_list[0 : request_limit - 1]

        for symbol in track(symbol_list, description="Processing..."):
            df_data = self.api.get_historical_data(f"{symbol}.{market_type}", interval)
            if len(df_data) >= 200:

                df_data["sma50"] = df_data.adjusted_close.rolling(50, min_periods=1).mean()
                df_data["sma200"] = df_data.adjusted_close.rolling(200, min_periods=1).mean()
                df_data["bull_market"] = df_data.sma50 >= df_data.sma200

                df_data["ema12"] = df_data.adjusted_close.ewm(span=12, adjust=False).mean()
                df_data["ema26"] = df_data.adjusted_close.ewm(span=26, adjust=False).mean()
                df_data.loc[df_data["ema12"] > df_data["ema26"], "next_action"] = "sell"
                df_data["next_action"].fillna("buy", inplace=True)

                high_low = df_data["high"] - df_data["low"]
                high_close = abs(df_data["high"] - df_data["adjusted_close"].shift())
                low_close = abs(df_data["low"] - df_data["adjusted_close"].shift())
                ranges = pd.concat([high_low, high_close, low_close], axis=1)
                true_range = np.max(ranges, axis=1)
                df_data["atr14"] = true_range.rolling(14).sum() / 14
                df_data["atr14_pcnt"] = (df_data["atr14"] / df_data["adjusted_close"] * 100).round(2)

                df_dataset = df_dataset.append(df_data.tail(1))

        # drop infinite values
        df_dataset.replace([np.inf, -np.inf], np.nan, inplace=True)
        df_dataset.dropna(subset=["atr14_pcnt"], inplace=True)

        df_dataset.sort_values(
            by=["bull_market", "next_action", "volume", "atr14_pcnt"],
            ascending=[False, True, False, False],
            inplace=True,
        )
        df_dataset.to_csv("dataset.csv")

        return df_dataset
