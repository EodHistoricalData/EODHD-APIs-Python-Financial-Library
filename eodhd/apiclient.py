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
