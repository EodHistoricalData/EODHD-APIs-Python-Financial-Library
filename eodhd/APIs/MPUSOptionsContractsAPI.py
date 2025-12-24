#APIs/MPUSOptionsContractsAPI.py

from .BaseAPI import BaseAPI


class MPUSOptionsContractsAPI(BaseAPI):
    """
    GET /api/mp/unicornbay/options/contracts
    """

    ALLOWED_SORT = {"exp_date", "strike", "-exp_date", "-strike"}
    ALLOWED_TYPE = {None, "put", "call"}
    ALLOWED_FMT = {None, "json"}

    @staticmethod
    def _enc(val) -> str:

        s = str(val)
        return (
            s.replace("%", "%25")
             .replace(" ", "%20")
             .replace("&", "%26")
             .replace("=", "%3D")
             .replace("+", "%2B")
             .replace("#", "%23")
             .replace("?", "%3F")
        )

    @classmethod
    def _q(cls, key: str, val) -> str:
        if val is None or val == "":
            return ""
        return f"&{key}={cls._enc(val)}"

    @staticmethod
    def _q_fields_contracts(fields) -> str:
        """
        fields[options-contracts]
        Accepts:
          - None
          - "field1,field2"
          - ["field1", "field2", ...] / tuple / any iterable
        """
        if fields is None:
            return ""

        if isinstance(fields, str):
            value = fields.strip()
        else:
            parts = [str(f).strip() for f in fields if f is not None and str(f).strip()]
            if not parts:
                return ""
            value = ",".join(parts)

        # Don't encode commas; just encode unsafe characters
        value = (
            value.replace("%", "%25")
                 .replace(" ", "%20")
                 .replace("&", "%26")
                 .replace("=", "%3D")
                 .replace("+", "%2B")
                 .replace("#", "%23")
                 .replace("?", "%3F")
        )
        return f"&fields[options-contracts]={value}"

    def get_us_options_contracts(
        self,
        api_token: str,
        underlying_symbol: str = None,
        contract: str = None,
        exp_date_eq: str = None,
        exp_date_from: str = None,
        exp_date_to: str = None,
        tradetime_eq: str = None,
        tradetime_from: str = None,
        tradetime_to: str = None,
        type: str = None,
        strike_eq: float = None,
        strike_from: float = None,
        strike_to: float = None,
        sort: str = None,
        page_offset: int = 0,
        page_limit: int = 1000,
        fields=None,
        fmt: str = "json",
    ):
        # validate
        if type not in self.ALLOWED_TYPE:
            raise ValueError("Invalid 'type'. Allowed: 'put', 'call' or omit (None).")
        if sort is not None and sort not in self.ALLOWED_SORT:
            raise ValueError(f"Invalid 'sort'. Allowed: {sorted(self.ALLOWED_SORT)}")
        if not isinstance(page_offset, int) or not (0 <= page_offset <= 10000):
            raise ValueError("'page_offset' must be an integer between 0 and 10000.")
        if not isinstance(page_limit, int) or not (1 <= page_limit <= 1000):
            raise ValueError("'page_limit' must be an integer between 1 and 1000.")
        if fmt is not None:
            fmt = str(fmt).lower()
        if fmt not in self.ALLOWED_FMT:
            raise ValueError("Invalid 'fmt'. Allowed: 'json' or omit (None).")

        endpoint = "mp/unicornbay/options/contracts"
        query_string = "&1=1"

        # filters
        query_string += self._q("filter[contract]", contract)
        query_string += self._q("filter[underlying_symbol]", underlying_symbol)
        query_string += self._q("filter[exp_date_eq]", exp_date_eq)
        query_string += self._q("filter[exp_date_from]", exp_date_from)
        query_string += self._q("filter[exp_date_to]", exp_date_to)
        query_string += self._q("filter[tradetime_eq]", tradetime_eq)
        query_string += self._q("filter[tradetime_from]", tradetime_from)
        query_string += self._q("filter[tradetime_to]", tradetime_to)
        query_string += self._q("filter[type]", type)
        query_string += self._q("filter[strike_eq]", strike_eq)
        query_string += self._q("filter[strike_from]", strike_from)
        query_string += self._q("filter[strike_to]", strike_to)

        # sort & pagination
        query_string += self._q("sort", sort)
        query_string += self._q("page[offset]", page_offset)
        query_string += self._q("page[limit]", page_limit)

        # fields
        query_string += self._q_fields_contracts(fields)

        # format
        if fmt is not None:
            query_string += self._q("fmt", fmt)

        return self._rest_get_method(
            api_key=api_token,
            endpoint=endpoint,
            querystring=query_string,
        )
