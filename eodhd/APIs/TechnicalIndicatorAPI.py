#APIs/TechnicalIndicatorAPI.py

from .BaseAPI import BaseAPI


class TechnicalIndicatorAPI(BaseAPI):
    """
    Docs: https://eodhd.com/financial-apis/technical-indicators-api :contentReference[oaicite:4]{index=4}
    Endpoint:
        GET /api/technical/{ticker}?function=...&api_token=...&fmt=json|csv
    """

    # Full set from the documentation, including BETA and dx alias :contentReference[oaicite:5]{index=5}
    possible_functions = [
        "splitadjusted",
        "avgvol",
        "avgvolccy",
        "sma",
        "ema",
        "wma",
        "volatility",
        "stochastic",
        "rsi",
        "stddev",
        "stochrsi",
        "slope",
        "dmi",  # docs also mention dx alias
        "dx",   # alias -> will be normalized to dmi
        "adx",
        "macd",
        "atr",
        "cci",
        "sar",
        "beta",
        "bbands",
        "format_amibroker",
    ]

    _splitadjusted_only_supported = {
        "sma", "ema", "wma", "volatility", "rsi", "slope", "macd"
    }  # :contentReference[oaicite:6]{index=6}

    def get_technical_indicator_data(
        self,
        api_token: str,
        ticker: str,
        function: str,
        period: int = 50,
        date_from: str = None,
        date_to: str = None,
        order: str = "a",
        fmt: str = "json",
        filter_field: str = None,          # e.g. "last_ema", "last_volume" :contentReference[oaicite:7]{index=7}

        # splitadjusted
        agg_period: str = None,            # d|w|m

        # stochastic
        fast_kperiod: int = None,
        slow_kperiod: int = None,
        slow_dperiod: int = None,

        # stochrsi
        fast_dperiod: int = None,

        # macd
        fast_period: int = None,
        slow_period: int = None,
        signal_period: int = None,

        # sar
        acceleration: float = None,
        maximum: float = None,

        # beta
        code2: str = None,                 # default is GSPC.INDX :contentReference[oaicite:8]{index=8}

        # splitadjusted_only
        splitadjusted_only: str = "0",      # accepts "0"/"1" or bool-like
    ):
        endpoint = "technical/"

        # --- basic validation ---
        if ticker is None or str(ticker).strip() == "":
            raise ValueError("Ticker is empty. You need to add ticker to args")

        if function is None or str(function).strip() == "":
            raise ValueError("Function is empty. You need to add function to args")

        fn = str(function).strip().lower()

        # normalize dx -> dmi (docs list required function as dmi; heading mentions dx alias) :contentReference[oaicite:9]{index=9}
        if fn == "dx":
            fn = "dmi"

        if fn not in self.possible_functions and fn != "dmi":
            raise ValueError("Incorrect value for function parameter")

        if order is not None:
            order = str(order).lower()
            if order not in ("a", "d"):
                raise ValueError("order must be 'a' (asc) or 'd' (desc)")

        if fmt is not None:
            fmt = str(fmt).lower()
            if fmt not in ("json", "csv"):
                raise ValueError("fmt must be 'json' or 'csv'")

        # normalize splitadjusted_only
        if isinstance(splitadjusted_only, bool):
            splitadjusted_only = "1" if splitadjusted_only else "0"
        else:
            splitadjusted_only = str(splitadjusted_only)

        # validate period when used (docs: 2..100000, default 50) :contentReference[oaicite:10]{index=10}
        if period is not None:
            try:
                period_int = int(period)
            except Exception:
                raise ValueError("period must be an integer")
            if period_int < 2 or period_int > 100000:
                raise ValueError("period must be in range [2..100000]")
            period = period_int

        # --- build query ---
        query_string = f"&function={fn}"

        if order is not None:
            query_string += f"&order={order}"

        if date_from is not None:
            query_string += f"&from={date_from}"
        if date_to is not None:
            query_string += f"&to={date_to}"

        if fmt is not None:
            query_string += f"&fmt={fmt}"

        # filter fields (works with fmt=json per docs; we don't hard-enforce, just pass through) :contentReference[oaicite:11]{index=11}
        if filter_field is not None and str(filter_field).strip() != "":
            query_string += f"&filter={str(filter_field).strip()}"

        # period is applicable to most functions; keep it unless function is format_amibroker or splitadjusted
        if fn not in ("format_amibroker", "splitadjusted") and period is not None:
            query_string += f"&period={period}"

        # splitadjusted_only only for supported functions :contentReference[oaicite:12]{index=12}
        if fn in self._splitadjusted_only_supported:
            query_string += f"&splitadjusted_only={splitadjusted_only}"

        # splitadjusted function options :contentReference[oaicite:13]{index=13}
        if fn == "splitadjusted":
            if agg_period is not None:
                agg_period = str(agg_period).lower()
                if agg_period not in ("d", "w", "m"):
                    raise ValueError("agg_period must be in ['d', 'w', 'm']")
                query_string += f"&agg_period={agg_period}"

        # stochastic :contentReference[oaicite:14]{index=14}
        if fn == "stochastic":
            if fast_kperiod is not None:
                query_string += f"&fast_kperiod={int(fast_kperiod)}"
            if slow_kperiod is not None:
                query_string += f"&slow_kperiod={int(slow_kperiod)}"
            if slow_dperiod is not None:
                query_string += f"&slow_dperiod={int(slow_dperiod)}"

        # stochrsi :contentReference[oaicite:15]{index=15}
        if fn == "stochrsi":
            if fast_kperiod is not None:
                query_string += f"&fast_kperiod={int(fast_kperiod)}"
            if fast_dperiod is not None:
                query_string += f"&fast_dperiod={int(fast_dperiod)}"

        # macd :contentReference[oaicite:16]{index=16}
        if fn == "macd":
            if fast_period is not None:
                query_string += f"&fast_period={int(fast_period)}"
            if slow_period is not None:
                query_string += f"&slow_period={int(slow_period)}"
            if signal_period is not None:
                query_string += f"&signal_period={int(signal_period)}"

        # sar :contentReference[oaicite:17]{index=17}
        if fn == "sar":
            if acceleration is not None:
                query_string += f"&acceleration={acceleration}"
            if maximum is not None:
                query_string += f"&maximum={maximum}"

        # beta :contentReference[oaicite:18]{index=18}
        if fn == "beta":
            if code2 is not None and str(code2).strip() != "":
                query_string += f"&code2={str(code2).strip()}"
            else:
                # docs default is GSPC.INDX; omit to let server default, or set explicitly
                # query_string += "&code2=GSPC.INDX"
                pass
            if period is not None:
                query_string += f"&period={period}"

        return self._rest_get_method(
            api_key=api_token,
            endpoint=endpoint,
            uri=str(ticker).strip(),
            querystring=query_string,
        )
