"""API example"""

import config as cfg
from eodhd import APIClient


def main() -> None:
    """Main"""

    api = APIClient(cfg.API_KEY)

    resp = api.get_exchanges()
    print(resp)
    # print(resp.dtypes)
    # print(resp.describe())

    resp = api.get_exchange_symbols("US")
    print(resp)
    # print(resp.dtypes)
    # print(resp.describe())

    resp = api.get_intraday_historical_data('BTC-USD.CC','1m')
    # resp = api.get_historical_data("BTC-USD.CC", "1m", "2021-11-27 23:56:00")
    # resp = api.get_historical_data("BTC-USD.CC", "1m", "2021-11-27 23:56:00", "2021-11-27 23:59:00")
    print(resp)
    # print(resp.dtypes)
    # print(resp.describe())

    resp = api.get_historical_data("BTC-USD.CC", "5m")
    # resp = api.get_historical_data("BTC-USD.CC", "5m", "2021-11-27 23:55:00")
    # resp = api.get_historical_data("BTC-USD.CC", "5m", "2021-11-27 23:55:00", "2021-11-28 02:00:00")
    print(resp)
    # print(resp.dtypes)
    # print(resp.describe())

    resp = api.get_historical_data("BTC-USD.CC", "1h")
    # resp = api.get_historical_data("BTC-USD.CC", "1h", "2021-11-27 23:00:00")
    # resp = api.get_historical_data("BTC-USD.CC", "1h", "2021-11-27 23:00:00", "2021-11-28 23:59:00")
    print(resp)
    # print(resp.dtypes)
    # print(resp.describe())

    resp = api.get_historical_data("BTC-USD.CC", "d")
    # resp = api.get_historical_data("BTC-USD.CC", "d", "2021-11-24")
    # resp = api.get_historical_data("BTC-USD.CC", "d", "2021-11-24", "2021-11-27")
    print(resp)
    # print(resp.dtypes)
    # print(resp.describe())

    resp = api.get_historical_data("BTC-USD.CC", "d", results=400)
    # resp = api.get_historical_data("BTC-USD.CC", "d", "2021-11-24")
    # resp = api.get_historical_data("BTC-USD.CC", "d", "2021-11-24", "2021-11-27")
    print(resp)
    # print(resp.dtypes)
    # print(resp.describe())

    resp = api.get_details_trading_hours_stock_market_holidays(code = 'US', from_date = '2022-12-01', to_date = '2023-01-03')
    # resp = api.get_details_trading_hours_stock_market_holidays(code = 'US')
    print(resp)

    resp = api.get_bonds_fundamentals_data(isin = 'DE000CB83CF0')
    print(resp)

    resp = api.get_eod_splits_dividends_data(country = 'US', type = 'splits', date = '2010-09-21', symbols = 'MSFT', filter = 'extended')
    # resp = api.get_eod_splits_dividends_data(country = 'US', type = 'dividends', date = '2010-09-21', symbols = 'MSFT', filter = 'extended')
    print(resp)

    resp = api.get_earning_trends_data(symbols = 'AAPL.US')
    # resp = api.get_earning_trends_data(symbols = 'AAPL.US, MS')
    print(resp)

    resp = api.get_economic_events_data(date_from = '2020-01-05', date_to = '2020-02-10', country = 'AU', comparison = 'mom',
                                  offset = 50, limit = 50)
    # resp = api.get_economic_events_data(date_from = '2020-01-05', date_to = '2020-02-10', country = 'AU', comparison = 'qoq', offset = 50, limit = 50)
    # resp = api.get_economic_events_data(date_from = '2020-01-05', date_to = '2020-02-10', country = 'AU', comparison = 'yoy', offset = 50, limit = 50)
    print(resp)

    resp = api.financial_news(s = 'AAPL.US', t = None, from_date = '2020-01-05', to_date = '2020-02-10', limit = 100, offset = 200)
    # resp = api.financial_news(s = None, t = 'balance sheet', from_date = '2020-01-05', to_date = '2020-02-10', limit = 100, offset = 200)
    print(resp)

    resp = api.get_fundamentals_data(ticker = 'AAPL')
    print(resp)

    resp = api.get_historical_dividends_data(date_from = '2020-01-05', date_to = '2020-02-10', ticker = 'AAPL.US')
    print(resp)

    resp = api.get_historical_splits_data(date_from = '2020-01-05', date_to = '2020-02-10', ticker = 'AAPL.US')
    print(resp)

    resp = api.get_insider_transactions_data(date_from = '2020-01-05', date_to = '2020-02-10', code = 'AAPL', limit = 200)
    #resp = api.get_insider_transactions_data(date_from = '2020-01-05', date_to = '2020-02-10', code = 'AAPL.US', limit = 200)
    print(resp)

    resp = api.get_live_stock_prices(date_from = '2020-01-05', date_to = '2020-02-10', ticker = 'AAPL.US')
    print(resp)

    resp = api.get_macro_indicators_data(country = 'US', indicator  = 'population_total')
    # resp = api.get_macro_indicators_data(country = 'US', indicator  = 'consumer_price_index')
    print(resp)

    resp = api.stock_market_screener(sort = 'market_capitalization.desc', filters = '[["market_capitalization",">",1000], ["name","match","apple"], ["code","=","AAPL"],["exchange","=","us"],["sector","=","Technology"]]', limit = 10, signals = 'bookvalue_neg', offset = 0)
    print(resp)

    resp = api.get_upcoming_earnings_data(from_date = '2020-01-05', to_date = '2020-02-10', symbols = 'MSFT')
    print(resp)

    resp = api.get_upcoming_IPOs_data(from_date = '2020-01-05', to_date = '2020-02-10')
    print(resp)

    resp = api.get_upcoming_splits_data(from_date = '2020-01-05', to_date = '2020-02-10')
    print(resp)

    resp = api.get_technical_indicator_data(ticker = 'AAPL.US', function = 'avgvolccy', period = 100, date_from = '2020-01-05', date_to = '2020-02-10',
                                            order = 'a', splitadjusted_only = '0')
    print(resp)

    resp = api.get_list_of_exchanges()
    print(resp)

    resp = api.get_list_of_tickers(delisted = 1, code = 'US')
    print(resp)

    resp = api.symbol_change_history(from_date = '2020-01-05', to_date = '2020-02-10')
    print(resp)

    resp = api.get_intraday_historical_data(symbol = 'AAPL.MX', from_unix_time = '1627896900', to_unix_time = '1630575300', interval='1h')
    print(resp)

    resp = api.get_eod_historical_stock_market_data(symbol = 'AAPL.MX', period='d', from_date = '2023-01-01', to_date = '2023-01-15', order='a')
    print(resp)

    resp = api.get_stock_market_tick_data(from_timestamp = '1627896900', to_timestamp = '1630575300', symbol = 'AAPL', limit = 1)
    print(resp)

    resp = api.get_sentiment(s = 'btc-usd.cc', from_date = '2023-01-01', to_date = '2023-01-15')
    print(resp)

    resp = api.get_historical_market_capitalization_data(ticker = 'AAPL.US', from_date = '2023-01-01', to_date = '2023-01-15')
    print(resp)


if __name__ == "__main__":
    main()
