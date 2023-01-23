"""API example"""

import config as cfg
from eodhd import APIClient
from eodhd import EODHDGraphs


def main() -> None:
    """Main"""

    api = APIClient(cfg.API_KEY)
    graphs = EODHDGraphs()

    df = api.get_historical_data("GSPC.INDX", "1d")
    # graphs.fibonacci_extension(df, "uptrend", "adjusted_close", save_file="")
    # graphs.fibonacci_extension(df, "uptrend", "adjusted_close", save_file="", quiet=False)
    # graphs.fibonacci_retracement(df, "downtrend", "adjusted_close", save_file="fibonacci_retracement_downtrend.png", quiet=False)
    # graphs.fibonacci_retracement(df, "downtrend", "adjusted_close", save_file="fibonacci_retracement_uptrend.png", quiet=True)
    graphs.fibonacci_retracement(df, "downtrend", "adjusted_close", save_file="")


if __name__ == "__main__":
    main()
