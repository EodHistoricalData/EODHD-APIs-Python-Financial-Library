"""
example_api.py

Examples of using the EODHD Python Financial Library (APIClient)
"""

import config as cfg
from eodhd import APIClient


def main() -> None:
    """Main"""
    api = APIClient(cfg.API_KEY)

    # --- Exchanges & symbols ---
    resp = api.get_exchanges()
    print(resp)

    resp = api.get_exchange_symbols("US")
    print(resp)

    # --- Intraday / Historical ---
    resp = api.get_intraday_historical_data("BTC-USD.CC", "1m")
    print(resp)

    resp = api.get_historical_data("BTC-USD.CC", "5m")
    print(resp)

    resp = api.get_historical_data("BTC-USD.CC", "1h")
    print(resp)

    resp = api.get_historical_data("BTC-USD.CC", "d")
    print(resp)

    resp = api.get_historical_data("BTC-USD.CC", "d", results=400)
    print(resp)

    # --- Trading hours / holidays ---
    resp = api.get_details_trading_hours_stock_market_holidays(
        code="US", from_date="2022-12-01", to_date="2023-01-03"
    )
    print(resp)

    # --- Bulk EOD splits/dividends ---
    resp = api.get_eod_splits_dividends_data(
        country="US",
        type="splits",
        date="2010-09-21",
        symbols="MSFT",
        filter="extended",
    )
    print(resp)

    # --- Earning trends ---
    resp = api.get_earning_trends_data(symbols="AAPL.US")
    print(resp)

    # --- Economic events ---
    resp = api.get_economic_events_data(
        date_from="2020-01-05",
        date_to="2020-02-10",
        country="AU",
        comparison="mom",
        offset=50,
        limit=50,
    )
    print(resp)

    # --- Financial News (ticker or tag) ---
    resp = api.financial_news(
        s="AAPL.US",
        t=None,
        from_date="2020-01-05",
        to_date="2020-02-10",
        limit=100,
        offset=200,
    )
    print(resp)

    # --- Fundamentals ---
    resp = api.get_fundamentals_data(ticker="AAPL")
    print(resp)

    # --- Historical dividends/splits ---
    resp = api.get_historical_dividends_data(
        date_from="2020-01-05", date_to="2020-02-10", ticker="AAPL.US"
    )
    print(resp)

    resp = api.get_historical_splits_data(
        date_from="2020-01-05", date_to="2020-02-10", ticker="AAPL.US"
    )
    print(resp)

    # --- Insider transactions ---
    resp = api.get_insider_transactions_data(
        date_from="2020-01-05", date_to="2020-02-10", code="AAPL", limit=200
    )
    print(resp)

    # --- Live stock prices ---
    resp = api.get_live_stock_prices(
        date_from="2020-01-05", date_to="2020-02-10", ticker="AAPL.US"
    )
    print(resp)

    # --- Macro indicators ---
    resp = api.get_macro_indicators_data(country="US", indicator="population_total")
    print(resp)

    # --- Screener ---
    resp = api.stock_market_screener(
        sort="market_capitalization.desc",
        filters='[["market_capitalization",">",1000], ["name","match","apple"], ["code","=","AAPL"],["exchange","=","us"],["sector","=","Technology"]]',
        limit=10,
        signals="bookvalue_neg",
        offset=0,
    )
    print(resp)

    # --- Calendars ---
    resp = api.get_upcoming_earnings_data(from_date="2020-01-05", to_date="2020-02-10", symbols="MSFT")
    print(resp)

    resp = api.get_upcoming_IPOs_data(from_date="2020-01-05", to_date="2020-02-10")
    print(resp)

    resp = api.get_upcoming_splits_data(from_date="2020-01-05", to_date="2020-02-10")
    print(resp)

    # --- Technical indicators  ---
    resp = api.get_technical_indicator_data(
        ticker="AAPL.US",
        function="avgvolccy",
        period=100,
        date_from="2020-01-05",
        date_to="2020-02-10",
        order="a",
        splitadjusted_only="0",
    )
    print(resp)

    # --- Lists / symbol change history ---
    resp = api.get_list_of_exchanges()
    print(resp)

    resp = api.get_list_of_tickers(delisted=1, code="US")
    print(resp)

    resp = api.symbol_change_history(from_date="2020-01-05", to_date="2020-02-10")
    print(resp)

    # --- Intraday (unix timestamps example) ---
    resp = api.get_intraday_historical_data(
        symbol="AAPL.MX",
        from_unix_time="1627896900",
        to_unix_time="1630575300",
        interval="1h",
    )
    print(resp)

    # --- EOD historical stock market data ---
    resp = api.get_eod_historical_stock_market_data(
        symbol="AAPL.MX",
        period="d",
        from_date="2023-01-01",
        to_date="2023-01-15",
        order="a",
    )
    print(resp)

    # --- Tick data ---
    resp = api.get_stock_market_tick_data(
        from_timestamp="1627896900",
        to_timestamp="1630575300",
        symbol="AAPL",
        limit=1,
    )
    print(resp)

    # --- News sentiment ---
    resp = api.get_sentiment(s="btc-usd.cc", from_date="2023-01-01", to_date="2023-01-15")
    print(resp)

    # --- News Word Weights (NEW) ---
    resp = api.news_word_weights(
        s="AAPL.US",
        date_from="2025-01-01",
        date_to="2025-01-15",
        limit=10,
    )
    print(resp)

    # --- Historical market cap ---
    resp = api.get_historical_market_capitalization_data(
        ticker="AAPL.US",
        from_date="2023-01-01",
        to_date="2023-01-15",
    )
    print(resp)


    # Live v2 US Stocks: Extended Quotes (Delayed) - /us-quote-delayed
    resp = api.us_extended_quotes(
        symbols=["AAPL.US", "TSLA.US"],
        page_limit=2,
        page_offset=0,
        fmt="json",  # or "csv"
    )
    print(resp)

    # CBOE Indices List - /cboe/indices
    resp = api.get_cboe_indices_list(fmt="json")
    print(resp)

    # CBOE Index Feed (index + components) - /cboe/index
    resp = api.get_cboe_index_data(
        index_code="BDE30P",
        feed_type="snapshot_official_closing",
        date="2017-02-01",
        fmt="json",
    )
    print(resp)

    # ID Mapping - /id-mapping
    # By symbol
    resp = api.get_id_mapping(symbol="AAPL.US", page_limit=100, page_offset=0, fmt="json")
    print(resp)

    # By ISIN
    resp = api.get_id_mapping(isin="US0378331005", fmt="json")
    print(resp)

    # By exchange code (example)
    resp = api.get_id_mapping(ex="US", page_limit=50, page_offset=0, fmt="json")
    print(resp)

    # Marketplace S&P Global / UnicornBay indices list
    resp = api.mp_indices_list()
    print(resp)

    # Marketplace S&P Global / UnicornBay index components
    resp = api.mp_index_components(symbol="GSPC.INDX", historical=False)
    print(resp)

    resp = api.mp_index_components(
        symbol="GSPC.INDX",
        historical=True,
        from_date="2015-01-01",
        to_date="2017-01-01",
    )
    print(resp)

    # US Options: underlying symbols list
    resp = api.get_us_options_underlyings(fmt="json")
    print(resp)

    # US Options: contracts
    resp = api.get_us_options_contracts(
        underlying_symbol="AAPL",
        exp_date_from="2025-01-01",
        exp_date_to="2025-06-01",
        type="call",
        sort="exp_date",
        page_offset=0,
        page_limit=50,
        fields=["contract", "exp_date", "strike", "type", "tradetime"],
        fmt="json",
    )
    print(resp)

    # US Options: EOD
    resp = api.get_us_options_eod(
        underlying_symbol="AAPL",
        exp_date_from="2025-01-01",
        exp_date_to="2025-06-01",
        type="put",
        strike_from=100,
        strike_to=200,
        sort="-exp_date",
        page_offset=0,
        page_limit=50,
        fields="contract,exp_date,strike,type,tradetime,volume,last,bid,ask",
        compact=1,
        fmt="json",
    )
    print(resp)

    # Technical Indicators enhancements
    # beta
    resp = api.get_technical_indicator_data(
        ticker="AAPL.US",
        function="beta",
        period=50,
        date_from="2020-01-05",
        date_to="2020-02-10",
        order="a",
        fmt="json",
        # code2="GSPC.INDX",  # optional, if your APIClient passes it through
    )
    print(resp)

    # dx alias -> dmi
    resp = api.get_technical_indicator_data(
        ticker="AAPL.US",
        function="dx",
        period=14,
        date_from="2020-01-05",
        date_to="2020-02-10",
        order="a",
        fmt="json",
    )
    print(resp)

    # filter_field example (last EMA only)
    resp = api.get_technical_indicator_data(
        ticker="AAPL.US",
        function="ema",
        period=50,
        filter_field="last_ema",
        fmt="json",
    )
    print(resp)


if __name__ == "__main__":
    main()
