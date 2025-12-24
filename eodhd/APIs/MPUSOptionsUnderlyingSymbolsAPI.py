#APIs/MPUSOptionsUnderlyingSymbolsAPI.py

from .BaseAPI import BaseAPI


class MPUSOptionsUnderlyingSymbolsAPI(BaseAPI):
    """
    Wrapper for:
        GET /api/mp/unicornbay/options/underlying-symbols

    Returns JSON: meta, data (list), links.next

    Pagination may be supported via:
        page[offset], page[limit]
    """

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

    def get_us_options_underlyings(
        self,
        api_token: str,
        page_offset: int = None,
        page_limit: int = None,
        fmt: str = "json",
    ):
        # basic validation (keep permissive since pagination is "if supported")
        if page_offset is not None:
            page_offset = int(page_offset)
            if page_offset < 0:
                raise ValueError("'page_offset' must be >= 0.")
        if page_limit is not None:
            page_limit = int(page_limit)
            if page_limit < 1:
                raise ValueError("'page_limit' must be >= 1.")

        if fmt is not None:
            fmt = str(fmt).lower()
            if fmt not in ("json", "xml"):  # allow xml if server supports it
                raise ValueError("fmt must be 'json' or 'xml'.")

        endpoint = "mp/unicornbay/options/underlying-symbols"
        query_string = "&1=1"

        query_string += self._q("page[offset]", page_offset)
        query_string += self._q("page[limit]", page_limit)

        if fmt is not None:
            query_string += self._q("fmt", fmt)

        return self._rest_get_method(
            api_key=api_token,
            endpoint=endpoint,
            querystring=query_string,
        )
