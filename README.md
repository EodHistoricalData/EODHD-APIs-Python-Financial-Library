# Official EODHD APIs Python Library

[Full documentation](https://eodhd.com/financial-apis/python-financial-libraries-and-code-samples/)

This is the official Python library developed by [EODHD](https://eodhd.com) for accessing various financial data via API in your code. If you have any feedback or questions, you can reach out to our support team, available 24/7 via live chat on [our website](https://eodhd.com).

To access our APIs, you need to register on our site (it’s free) and obtain an API key. Access to some data requires a subscription to one of [our paid plans](https://eodhd.com/pricing).

## List of supported data:

* End of the Day Historical Stock Market Data
* Live (Delayed) Stock Prices and Macroeconomic Data
* Intraday Historical Data
* Historical Dividends
* Historical Splits
* Bulk API for EOD, Splits and Dividends
* Calendar. Upcoming Earnings, Trends, IPOs and Splits
* Economic Events
* Stock Market and Financial News
* List of supported Exchanges
* Insider Transactions
* Macro Indicators
* Exchange API. Trading Hours, Stock Market Holidays, Symbols Change History
* Stock Market Screener
* Technical Indicator
* Historical Market Capitalization
* Fundamental Data: Stocks, ETFs, Mutual Funds, Indices and Cryptocurrencies

All functions are described in our [documentation](https://eodhd.com/financial-apis/python-financial-libraries-and-code-samples/).

---

## Additional supported data (latest updates)

The library also includes newer endpoints and Marketplace datasets:

### Financial News (extended)

* **News Sentiment** (daily sentiment data for tickers)
* **News Word Weights** (weighted keywords from financial news for a ticker over a date range)

### Live v2 US Stocks

* **Extended Quotes (Delayed, exchange-compliant)** via `/us-quote-delayed`
  Batch tickers supported, optional pagination, JSON/CSV output.

### CBOE Indices Data

* **CBOE Indices List** via `/cboe/indices`
* **CBOE Index Feed (index + full constituents)** via `/cboe/index`
  Uses deep-object filters: `filter[index_code]`, `filter[feed_type]`, `filter[date]`.

### Identifier Resolution

* **ID Mapping API** (`CUSIP / ISIN / FIGI / LEI / CIK ↔ Symbol`) via `/id-mapping`
  Uses deep-object filters (e.g. `filter[symbol]`, `filter[isin]`) and supports pagination.

### Marketplace datasets (UnicornBay)

* **S&P Global / Indices List** via `/mp/unicornbay/spglobal/list`
* **Index Components (+ optional historical changes)** via `/mp/unicornbay/spglobal/comp/{symbol}`

### Marketplace datasets (US Stock Options Data API)

* **Underlying symbols list** via `/mp/unicornbay/options/underlying-symbols`
* **Options contracts** via `/mp/unicornbay/options/contracts`
* **Options EOD data** via `/mp/unicornbay/options/eod`
  Supports filters, sorting, pagination, field selection, and compact mode (where applicable).

### Technical Indicators (enhanced)

* Includes full function coverage from the current Technical Indicator API, including **BETA** and **DX (alias)**, plus support for:

  * `fmt=json|csv`
  * `filter` (e.g. `filter=last_ema`) where supported by the endpoint

---

## Installation

In short:

```bash
python3 -m pip install eodhd -U
```

If you have any difficulties, go to our full [documentation](https://eodhd.com/financial-apis/python-financial-libraries-and-code-samples/) with step by step instructions.

## Sample code and examples

The files below contain examples of available functions:

* `example_api.py`: describes the functions that can be used in the `APIClient` class (including new endpoints: Options, CBOE, ID Mapping, Live v2 Extended Quotes, News Word Weights, etc.).
* `example_scanner.py`: describes the functions that can be used in the `ScannerClient` class.
* `example_websockets.py`: describes the functions that can be used in the `WebSocketClient` class.

New features will be added to the example files. The most relevant functions can be viewed directly in the code files.
