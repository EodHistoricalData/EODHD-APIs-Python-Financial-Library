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

    resp = api.get_historical_data("BTC-USD.CC", "1h")
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

    resp = api.get_historical_data("BTC-USD.CC", "1d")
    # resp = api.get_historical_data("BTC-USD.CC", "1d", "2021-11-24")
    # resp = api.get_historical_data("BTC-USD.CC", "1d", "2021-11-24", "2021-11-27")
    print(resp)
    # print(resp.dtypes)
    # print(resp.describe())

    resp = api.get_historical_data("BTC-USD.CC", "1d", results=400)
    # resp = api.get_historical_data("BTC-USD.CC", "1d", "2021-11-24")
    # resp = api.get_historical_data("BTC-USD.CC", "1d", "2021-11-24", "2021-11-27")
    print(resp)
    # print(resp.dtypes)
    # print(resp.describe())


if __name__ == "__main__":
    main()
