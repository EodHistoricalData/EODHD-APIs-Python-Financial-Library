#apiclient.py

import sys
from enum import Enum
from datetime import datetime, timedelta
from re import compile as re_compile

import pandas as pd
import numpy as np

from requests import get as requests_get
from requests import ConnectionError as requests_ConnectionError
from requests import Timeout as requests_Timeout
from requests.exceptions import HTTPError as requests_HTTPError
from requests.exceptions import JSONDecodeError as requests_JSONDecodeError

from rich.console import Console
from rich.progress import track

from eodhd.APIs import HistoricalDividendsAPI
from eodhd.APIs import UpcomingDividendsAPI
from eodhd.APIs import HistoricalSplitsAPI
from eodhd.APIs import TechnicalIndicatorAPI
from eodhd.APIs import LiveStockPricesAPI
from eodhd.APIs import LiveExtendedQuotesAPI
from eodhd.APIs import EconomicEventsDataAPI
from eodhd.APIs import InsiderTransactionsAPI
from eodhd.APIs import FundamentalDataAPI
from eodhd.APIs import BulkEodSplitsDividendsAPI
from eodhd.APIs import UpcomingEarningsAPI
from eodhd.APIs import EarningTrendsAPI
from eodhd.APIs import UpcomingIPOsAPI
from eodhd.APIs import UpcomingSplitsAPI
from eodhd.APIs import MacroIndicatorsAPI
from eodhd.APIs import ListOfExchangesAPI
from eodhd.APIs import TradingHours_StockMarketHolidays_SymbolsChangeHistoryAPI
from eodhd.APIs import StockMarketScreenerAPI
from eodhd.APIs import FinancialNewsAPI
from eodhd.APIs import IntradayDataAPI
from eodhd.APIs import EodHistoricalStockMarketDataAPI
from eodhd.APIs import StockMarketTickDataAPI
from eodhd.APIs import HistoricalMarketCapitalizationAPI
from eodhd.APIs import CBOEIndexFeedAPI
from eodhd.APIs import IDMappingAPI

# Marketplace endpoints
from eodhd.APIs import MPIndexComponentsAPI
from eodhd.APIs import MPIndicesListAPI
from eodhd.APIs import MPUSOptionsContractsAPI
from eodhd.APIs import MPUSOptionsEODAPI
from eodhd.APIs import MPUSOptionsUnderlyingSymbolsAPI

# minimal traceback
sys.tracebacklimit = 1


class Interval(Enum):
    """Enum: infraday"""

    MINUTE = "1m"
    FIVEMINUTES = "5m"
    HOUR = "1h"
    ONEDAY = "d"
    WEEK = "w"
    MONTH = "m"


class DateUtils:
    """Utility class"""

    @staticmethod
    def str2datetime(_datetime: str):
        """Convert yyyy-mm-dd hh:mm:ss to datetime"""

        prog = re_compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")
        if not prog.match(_datetime):
            raise ValueError("Incorrect datetime format: yyyy-mm-dd hh:mm:ss")

        return datetime.strptime(_datetime, "%Y-%m-%d %H:%M:%S")

    @staticmethod
    def str2epoch(_datetime: str):
        """Convert yyyy-mm-dd hh:mm:ss to epoch seconds"""

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
        prog = re_compile(r"^[A-z0-9.]{16,32}$")
        if api_key != "demo" and not prog.match(api_key):
            raise ValueError("API key is invalid")

        self._api_key = api_key
        self._api_url = "https://eodhd.com/api"

        self.console = Console()

    def _rest_get(self, endpoint: str = "", uri: str = "", querystring: str = "") -> pd.DataFrame:
        """Generic REST GET"""

        if endpoint.strip() == "":
            raise ValueError("endpoint is empty!")

        try:
            resp = requests_get(
                f"{self._api_url}/{endpoint}/{uri}?api_token={self._api_key}&fmt=json{querystring}"
            )

            if resp.status_code != 200:
                try:
                    if "message" in resp.json():
                        resp_message = resp.json()["message"]
                    elif "errors" in resp.json():
                        errors = resp.json()
                        self.console.log(errors)
                        raise RuntimeError(
                            f"EODHD API returned errors (HTTP {resp.status_code}): {errors}"
                        )
                    else:
                        resp_message = ""

                    message = f"({resp.status_code}) {self._api_url} - {resp_message}"
                    self.console.log(message)

                except requests_JSONDecodeError as err:
                    self.console.log(err)

            try:
                resp.raise_for_status()

                if isinstance(resp.json(), list):
                    return pd.DataFrame.from_dict(resp.json())
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

    def get_exchange_symbols(self, uri: str = "", delisted: bool = False) -> pd.DataFrame:
        """Get supported exchange symbols"""
        try:
            if uri.strip() == "":
                raise ValueError("endpoint uri is empty!")

            if delisted:
                return self._rest_get("exchange-symbol-list", uri, "&delisted=1")

            return self._rest_get("exchange-symbol-list", uri)
        except ValueError as err:
            self.console.log(err)
            return pd.DataFrame()

    def get_historical_data(
        self,
        symbol: str,
        interval: str = Interval.ONEDAY.value,
        iso8601_start: str = "",
        iso8601_end: str = "",
        results: int = 300,
    ) -> pd.DataFrame:
        """Initiates a REST API call"""

        prog = re_compile(r"^[A-z0-9-$\.+]{1,48}$")
        if not prog.match(symbol):
            raise ValueError(f"Symbol is invalid: {symbol}")

        if symbol.count(".") == 2:
            symbol = symbol.replace(".", "-", 1)

        try:
            Interval(interval)
        except ValueError as err:
            self.console.log(err)
            return pd.DataFrame()

        df_data = pd.DataFrame()

        if interval in ("d", "w", "m"):
            re_date_only = re_compile(r"^\d{4}\-\d{2}-\d{2}$")
            re_iso8601 = re_compile(r"^\d{4}\-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$")

            if iso8601_end == "" or (
                (iso8601_end != "" and not re_iso8601.match(iso8601_end))
                and (iso8601_end != "" and not re_date_only.match(iso8601_end))
            ):
                date_to = datetime.today().date()
            else:
                try:
                    if re_date_only.match(iso8601_end):
                        date_to = datetime.strptime(iso8601_end, "%Y-%m-%d").date()
                    elif re_iso8601.match(iso8601_end):
                        date_to = datetime.strptime(iso8601_end, "%Y-%m-%dT%H:%M:%S").date()
                    else:
                        date_to = datetime.today().date()
                except ValueError as e:
                    raise ValueError(
                        f"invalid end date (yyyy-mm-ddThh:mm:ss OR yyyy-mm-dd): {iso8601_end}"
                    ) from e

            if iso8601_start == "" or (
                (iso8601_start != "" and not re_iso8601.match(iso8601_start))
                and (iso8601_start != "" and not re_date_only.match(iso8601_start))
            ):
                date_from = date_to - timedelta(days=(results - 1))
            else:
                try:
                    if re_date_only.match(iso8601_start):
                        date_from = datetime.strptime(iso8601_start, "%Y-%m-%d").date()
                    elif re_iso8601.match(iso8601_start):
                        date_from = datetime.strptime(iso8601_start, "%Y-%m-%dT%H:%M:%S").date()
                    else:
                        date_from = datetime.today().date()
                except ValueError as e:
                    raise ValueError(
                        f"invalid start date (yyyy-mm-ddThh:mm:ss OR yyyy-mm-dd): {iso8601_start}"
                    ) from e

            df_data = self._rest_get("eod", symbol, f"&period={interval}&from={str(date_from)}&to={str(date_to)}")

            if len(df_data) == 0:
                columns_eod = [
                    "symbol",
                    "interval",
                    "open",
                    "high",
                    "low",
                    "close",
                    "adjusted_close",
                    "volume",
                ]
                return pd.DataFrame(columns=columns_eod)

            if iso8601_start == "" and iso8601_end == "":
                df_data = df_data.tail(results)
            elif iso8601_start != "" and iso8601_end == "":
                df_data = df_data.head(results)

            df_data["symbol"] = symbol
            df_data["interval"] = interval

            tsidx = pd.DatetimeIndex(pd.to_datetime(df_data["date"]).dt.strftime("%Y-%m-%d"))
            df_data.set_index(tsidx, inplace=True)
            df_data = df_data.drop(columns=["date"])

            df_data.columns = [
                "open",
                "high",
                "low",
                "close",
                "adjusted_close",
                "volume",
                "symbol",
                "interval",
            ]

            df_data.fillna(0, inplace=True)
            df_data["open"] = df_data["open"].astype(object)
            df_data["high"] = df_data["high"].astype(object)
            df_data["low"] = df_data["low"].astype(object)
            df_data["close"] = df_data["close"].astype(object)
            df_data["adjusted_close"] = df_data["adjusted_close"].astype(object)
            df_data["volume"] = df_data["volume"].astype(object)

            return df_data[
                ["symbol", "interval", "open", "high", "low", "close", "adjusted_close", "volume"]
            ]

        if interval in ("1m", "5m", "1h"):
            re_date_only = re_compile(r"^\d{4}\-\d{2}-\d{2}$")
            re_iso8601 = re_compile(r"^\d{4}\-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$")
            re_epoch = re_compile(r"^\d{10}$")

            if iso8601_end == "" or (
                (iso8601_end != "" and not re_iso8601.match(iso8601_end))
                and (iso8601_end != "" and not re_date_only.match(iso8601_end))
            ):
                date_to = str(int(datetime.today().timestamp()))
            else:
                try:
                    if re_date_only.match(iso8601_end):
                        date_to = str(int(datetime.strptime(iso8601_end, "%Y-%m-%d").timestamp()))
                    elif re_iso8601.match(iso8601_end):
                        date_to = str(int(datetime.strptime(iso8601_end, "%Y-%m-%dT%H:%M:%S").timestamp()))
                    elif re_epoch.match(iso8601_end):
                        date_to = str(iso8601_end)
                    else:
                        date_to = str(int(datetime.today().timestamp()))
                except ValueError as e:
                    raise ValueError(
                        f"invalid end date (yyyy-mm-ddThh:mm:ss OR yyyy-mm-dd OR epoch): {iso8601_end}"
                    ) from e

            LIMIT_FOR_1M = 120  # days
            if iso8601_start == "" or (
                (iso8601_start != "" and not re_iso8601.match(iso8601_start))
                and (iso8601_start != "" and not re_date_only.match(iso8601_start))
            ):
                date_from = str(int((datetime.fromtimestamp(int(date_to)) - timedelta(days=LIMIT_FOR_1M)).timestamp()))
            else:
                try:
                    if re_date_only.match(iso8601_start):
                        date_from = str(int(datetime.strptime(iso8601_start, "%Y-%m-%d").timestamp()))
                    elif re_iso8601.match(iso8601_start):
                        date_from = str(int(datetime.strptime(iso8601_start, "%Y-%m-%dT%H:%M:%S").timestamp()))
                    else:
                        date_from = str(int(datetime.today().timestamp()))
                except ValueError as e:
                    raise ValueError(
                        f"invalid start date (yyyy-mm-ddThh:mm:ss OR yyyy-mm-dd OR epoch): {iso8601_start}"
                    ) from e

            df_data = self._rest_get("intraday", symbol, f"&interval={interval}&from={str(date_from)}&to={str(date_to)}")

            if len(df_data) == 0:
                columns_eod = [
                    "symbol",
                    "interval",
                    "open",
                    "high",
                    "low",
                    "close",
                    "adjusted_close",
                    "volume",
                ]
                return pd.DataFrame(columns=columns_eod)

            if iso8601_start == "" and iso8601_end == "":
                df_data = df_data.tail(results)
            elif iso8601_start != "" and iso8601_end == "":
                df_data = df_data.head(results)

            df_data["symbol"] = symbol
            df_data["interval"] = interval

            tsidx = pd.DatetimeIndex(pd.to_datetime(df_data["datetime"]).dt.strftime("%Y-%m-%d %H:%M:%S"))
            df_data.set_index(tsidx, inplace=True)
            df_data = df_data.drop(columns=["datetime"])

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

            df_data.fillna(0, inplace=True)
            df_data["gmtoffset"] = df_data["gmtoffset"].astype(object)
            df_data["epoch"] = df_data["epoch"].astype(object)
            df_data["open"] = df_data["open"].astype(object)
            df_data["high"] = df_data["high"].astype(object)
            df_data["low"] = df_data["low"].astype(object)
            df_data["close"] = df_data["close"].astype(object)
            df_data["volume"] = df_data["volume"].astype(object)

            return df_data[
                ["epoch", "gmtoffset", "symbol", "interval", "open", "high", "low", "close", "volume"]
            ]

        raise ValueError(f"invalid interval (1m, 5m, 1h, d, w, m): {interval}")

    def get_historical_dividends_data(self, ticker, date_to=None, date_from=None) -> list:
        api_call = HistoricalDividendsAPI()
        return api_call.get_historical_dividends_data(
            api_token=self._api_key, ticker=ticker, date_from=date_from, date_to=date_to
        )

    def get_historical_splits_data(self, ticker, date_to=None, date_from=None) -> list:
        api_call = HistoricalSplitsAPI()
        return api_call.get_historical_splits_data(
            api_token=self._api_key, ticker=ticker, date_from=date_from, date_to=date_to
        )

    def get_technical_indicator_data(
        self,
        ticker: str,
        function: str,
        period: int = 50,
        date_from: str = None,
        date_to: str = None,
        order: str = "a",
        splitadjusted_only: str = "0",
        agg_period: str = None,
        fast_kperiod: int = None,
        slow_kperiod: int = None,
        slow_dperiod: int = None,
        fast_dperiod: int = None,
        fast_period: int = None,
        slow_period: int = None,
        signal_period: int = None,
        acceleration: float = None,
        maximum: float = None,
    ) -> list:
        api_call = TechnicalIndicatorAPI()
        return api_call.get_technical_indicator_data(
            api_token=self._api_key,
            ticker=ticker,
            function=function,
            period=period,
            date_from=date_from,
            date_to=date_to,
            order=order,
            splitadjusted_only=splitadjusted_only,
            agg_period=agg_period,
            fast_kperiod=fast_kperiod,
            slow_kperiod=slow_kperiod,
            slow_dperiod=slow_dperiod,
            fast_dperiod=fast_dperiod,
            fast_period=fast_period,
            slow_period=slow_period,
            signal_period=signal_period,
            acceleration=acceleration,
            maximum=maximum,
        )

    def get_live_stock_prices(self, ticker, s=None) -> list:
        api_call = LiveStockPricesAPI()
        return api_call.get_live_stock_prices(api_token=self._api_key, ticker=ticker, s=s)

    def get_us_extended_quotes(self, s, page_limit=None, page_offset=None, fmt=None) -> list:
        if fmt is not None and str(fmt).lower() != "json":
            raise ValueError("This library currently supports only fmt='json' for us-quote-delayed.")
        api_call = LiveExtendedQuotesAPI()
        return api_call.get_us_extended_quotes(
            api_token=self._api_key,
            symbols=s,
            page_limit=page_limit,
            page_offset=page_offset,
        )

    def get_economic_events_data(self, date_from=None, date_to=None, country=None, comparison=None, offset=None, limit=None) -> list:
        api_call = EconomicEventsDataAPI()
        return api_call.get_economic_events_data(
            api_token=self._api_key,
            date_from=date_from,
            date_to=date_to,
            country=country,
            comparison=comparison,
            offset=offset,
            limit=limit,
        )

    def get_insider_transactions_data(self, date_from=None, date_to=None, code=None, limit=None) -> list:
        api_call = InsiderTransactionsAPI()
        return api_call.get_insider_transactions_data(
            api_token=self._api_key,
            date_from=date_from,
            date_to=date_to,
            code=code,
            limit=limit,
        )

    def get_fundamentals_data(self, ticker: str) -> list:
        api_call = FundamentalDataAPI()
        return api_call.get_fundamentals_data(api_token=self._api_key, ticker=ticker)

    def get_eod_splits_dividends_data(self, country="US", type=None, date=None, symbols=None, filter=None) -> list:
        api_call = BulkEodSplitsDividendsAPI()
        return api_call.get_eod_splits_dividends_data(
            api_token=self._api_key,
            country=country,
            type=type,
            date=date,
            symbols=symbols,
            filter=filter,
        )

    def get_upcoming_earnings_data(self, from_date=None, to_date=None, symbols=None) -> list:
        api_call = UpcomingEarningsAPI()
        return api_call.get_upcoming_earnings_data(
            api_token=self._api_key,
            from_date=from_date,
            to_date=to_date,
            symbols=symbols,
        )

    def get_earning_trends_data(self, symbols) -> list:
        api_call = EarningTrendsAPI()
        return api_call.get_earning_trends_data(api_token=self._api_key, symbols=symbols)

    def get_upcoming_IPOs_data(self, from_date=None, to_date=None) -> list:
        api_call = UpcomingIPOsAPI()
        return api_call.get_upcoming_IPOs_data(api_token=self._api_key, from_date=from_date, to_date=to_date)

    def get_upcoming_splits_data(self, from_date=None, to_date=None) -> list:
        api_call = UpcomingSplitsAPI()
        return api_call.get_upcoming_splits_data(api_token=self._api_key, from_date=from_date, to_date=to_date)

    def get_upcoming_dividends_data(self, symbol=None, date_eq=None, date_from=None, date_to=None, page_limit=None, page_offset=None) -> list:
        api_call = UpcomingDividendsAPI()
        return api_call.get_upcoming_dividends_data(
            api_token=self._api_key,
            symbol=symbol,
            date_eq=date_eq,
            date_from=date_from,
            date_to=date_to,
            page_limit=page_limit,
            page_offset=page_offset,
        )

    def get_macro_indicators_data(self, country, indicator=None) -> list:
        api_call = MacroIndicatorsAPI()
        return api_call.get_macro_indicators_data(api_token=self._api_key, country=country, indicator=indicator)

    def get_list_of_exchanges(self):
        api_call = ListOfExchangesAPI()
        return api_call.get_list_of_exchanges(api_token=self._api_key)

    def get_list_of_tickers(self, code, delisted=0):
        api_call = ListOfExchangesAPI()
        return api_call.get_list_of_tickers(api_token=self._api_key, delisted=delisted, code=code)

    def get_details_trading_hours_stock_market_holidays(self, code, from_date=None, to_date=None):
        api_call = TradingHours_StockMarketHolidays_SymbolsChangeHistoryAPI()
        return api_call.get_details_trading_hours_stock_market_holidays(
            api_token=self._api_key, code=code, from_date=from_date, to_date=to_date
        )

    def symbol_change_history(self, from_date=None, to_date=None):
        api_call = TradingHours_StockMarketHolidays_SymbolsChangeHistoryAPI()
        return api_call.symbol_change_history(api_token=self._api_key, from_date=from_date, to_date=to_date)

    def stock_market_screener(self, sort=None, filters=None, limit=None, signals=None, offset=None):
        api_call = StockMarketScreenerAPI()
        return api_call.stock_market_screener(
            api_token=self._api_key,
            filters=filters,
            limit=limit,
            signals=signals,
            offset=offset,
            sort=sort,
        )

    def get_intraday_historical_data(self, symbol, interval="5m", from_unix_time=None, to_unix_time=None):
        api_call = IntradayDataAPI()
        return api_call.get_intraday_historical_data(
            api_token=self._api_key,
            symbol=symbol,
            interval=interval,
            to_unix_time=to_unix_time,
            from_unix_time=from_unix_time,
        )

    def get_eod_historical_stock_market_data(self, symbol, period="d", from_date=None, to_date=None, order=None):
        api_call = EodHistoricalStockMarketDataAPI()
        return api_call.get_eod_historical_stock_market_data(
            api_token=self._api_key,
            symbol=symbol,
            period=period,
            to_date=to_date,
            from_date=from_date,
            order=order,
        )

    def get_stock_market_tick_data(self, symbol, from_timestamp, to_timestamp, limit=None):
        api_call = StockMarketTickDataAPI()
        return api_call.get_stock_market_tick_data(
            api_token=self._api_key,
            symbol=symbol,
            to_timestamp=to_timestamp,
            from_timestamp=from_timestamp,
            limit=limit,
        )

    def financial_news(self, s=None, t=None, from_date=None, to_date=None, limit=None, offset=None):
        api_call = FinancialNewsAPI()
        return api_call.financial_news(
            api_token=self._api_key,
            s=s,
            t=t,
            from_date=from_date,
            to_date=to_date,
            limit=limit,
            offset=offset,
        )

    def get_sentiment(self, s, from_date=None, to_date=None):
        api_call = FinancialNewsAPI()
        return api_call.get_sentiment(api_token=self._api_key, s=s, from_date=from_date, to_date=to_date)

    def news_word_weights(self, s, date_from=None, date_to=None, limit=None):
        api_call = FinancialNewsAPI()
        return api_call.news_word_weights(
            api_token=self._api_key,
            s=s,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
        )

    def get_historical_market_capitalization_data(self, ticker, from_date=None, to_date=None):
        api_call = HistoricalMarketCapitalizationAPI()
        return api_call.get_historical_market_capitalization_data(
            api_token=self._api_key, ticker=ticker, from_date=from_date, to_date=to_date
        )

    def get_cboe_index_data(self, index_code, feed_type, date, fmt=None):
        api_call = CBOEIndexFeedAPI()
        return api_call.get_cboe_index_data(
            api_token=self._api_key,
            index_code=index_code,
            feed_type=feed_type,
            date=date,
            fmt=fmt,
        )

    def get_cboe_indices_list(self, fmt=None):
        api_call = CBOEIndexFeedAPI()
        return api_call.get_cboe_indices_list(api_token=self._api_key, fmt=fmt)

    def get_id_mapping(self, symbol=None, ex=None, isin=None, figi=None, lei=None, cusip=None, cik=None, page_limit=None, page_offset=None, fmt=None):
        api_call = IDMappingAPI()
        return api_call.get_id_mapping(
            api_token=self._api_key,
            symbol=symbol,
            ex=ex,
            isin=isin,
            figi=figi,
            lei=lei,
            cusip=cusip,
            cik=cik,
            page_limit=page_limit,
            page_offset=page_offset,
            fmt=fmt,
        )

    def mp_indices_list(self):
        api_call = MPIndicesListAPI()
        return api_call.get_indices_list(api_token=self._api_key)

    def mp_index_components(self, symbol, historical=None, from_date=None, to_date=None):
        api_call = MPIndexComponentsAPI()
        return api_call.get_index_components(
            api_token=self._api_key,
            symbol=symbol,
            historical=historical,
            from_date=from_date,
            to_date=to_date,
        )

    def get_us_options_contracts(
        self,
        underlying_symbol=None,
        contract=None,
        exp_date_eq=None,
        exp_date_from=None,
        exp_date_to=None,
        tradetime_eq=None,
        tradetime_from=None,
        tradetime_to=None,
        type=None,
        strike_eq=None,
        strike_from=None,
        strike_to=None,
        sort=None,
        page_offset=0,
        page_limit=1000,
        fields=None,
        fmt="json",
    ):
        api_call = MPUSOptionsContractsAPI()
        return api_call.get_us_options_contracts(
            api_token=self._api_key,
            underlying_symbol=underlying_symbol,
            contract=contract,
            exp_date_eq=exp_date_eq,
            exp_date_from=exp_date_from,
            exp_date_to=exp_date_to,
            tradetime_eq=tradetime_eq,
            tradetime_from=tradetime_from,
            tradetime_to=tradetime_to,
            type=type,
            strike_eq=strike_eq,
            strike_from=strike_from,
            strike_to=strike_to,
            sort=sort,
            page_offset=page_offset,
            page_limit=page_limit,
            fields=fields,
            fmt=fmt,
        )

    def get_us_options_eod(
        self,
        underlying_symbol=None,
        contract=None,
        exp_date_eq=None,
        exp_date_from=None,
        exp_date_to=None,
        tradetime_eq=None,
        tradetime_from=None,
        tradetime_to=None,
        type=None,
        strike_eq=None,
        strike_from=None,
        strike_to=None,
        sort=None,
        page_offset=0,
        page_limit=1000,
        fields=None,
        compact=None,
        fmt="json",
    ):
        api_call = MPUSOptionsEODAPI()
        return api_call.get_us_options_eod(
            api_token=self._api_key,
            underlying_symbol=underlying_symbol,
            contract=contract,
            exp_date_eq=exp_date_eq,
            exp_date_from=exp_date_from,
            exp_date_to=exp_date_to,
            tradetime_eq=tradetime_eq,
            tradetime_from=tradetime_from,
            tradetime_to=tradetime_to,
            type=type,
            strike_eq=strike_eq,
            strike_from=strike_from,
            strike_to=strike_to,
            sort=sort,
            page_offset=page_offset,
            page_limit=page_limit,
            fields=fields,
            compact=compact,
            fmt=fmt,
        )

    def get_us_options_underlyings(self, page_offset=None, page_limit=None, fmt="json"):
        api_call = MPUSOptionsUnderlyingSymbolsAPI()
        return api_call.get_us_options_underlyings(
            api_token=self._api_key,
            page_offset=page_offset,
            page_limit=page_limit,
            fmt=fmt,
        )


class ScannerClient:
    """Scanner class"""

    def __init__(self, api_key: str) -> None:
        prog = re_compile(r"^[A-z0-9.]{16,32}$")
        if api_key != "demo" and not prog.match(api_key):
            raise ValueError("API key is invalid")

        self.api = APIClient(api_key)

    def scan_markets(
        self,
        market_type: str = "CC",
        interval: str = Interval.ONEDAY.value,
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

        df_dataset.replace([np.inf, -np.inf], np.nan, inplace=True)
        df_dataset.dropna(subset=["atr14_pcnt"], inplace=True)

        df_dataset.sort_values(
            by=["bull_market", "next_action", "volume", "atr14_pcnt"],
            ascending=[False, True, False, False],
            inplace=True,
        )
        df_dataset.to_csv("dataset.csv")

        return df_dataset
