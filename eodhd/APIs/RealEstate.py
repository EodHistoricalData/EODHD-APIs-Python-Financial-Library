# APIs/RealEstate.py

from .BaseAPI import BaseAPI


class RealEstateAPI(BaseAPI):
    """
    Wrapper for the Real Estate Data API (BIS residential property prices):

        GET /api/real-estate/countries
        GET /api/real-estate/{code}                    (Selected Property Prices / SPP)
        GET /api/real-estate/{code}/detailed           (Detailed Property Prices / DPP)
        GET /api/real-estate/{code}/detailed/series    (catalogue of DPP series)

    Notes:
    - Country codes are ISO alpha-2 and case-insensitive (normalised to uppercase).
    - Most endpoints return a JSON envelope { data, meta, links }; the
      /detailed/series catalogue returns { data, meta } (no links).
    - Filtering uses filter[...] deep-object params; sort/fmt are bare params.
    - Pagination uses page[offset] (>= 0) and page[limit] (1..500, default 50).
    - fmt supports "json" and "csv" on every endpoint EXCEPT /detailed/series,
      which always returns JSON.
    - The underlying transport parses JSON, so pass fmt="csv" only if you handle
      the raw payload yourself.

    Docs: https://eodhd.com/financial-apis/real-estate-data-api
    """

    _SORT_COUNTRIES = ("code", "-code", "name", "-name")
    _SORT_SERIES = ("period", "-period", "value", "-value")

    @staticmethod
    def _real_estate_pagination(page_offset=None, page_limit=None) -> str:
        """Build &page[offset]/&page[limit] fragments for the Real Estate API,
        validating its bounds (offset >= 0, 1 <= limit <= 500)."""
        query_string = ""
        if page_offset is not None:
            page_offset = BaseAPI._coerce_page_int("page_offset", page_offset)
            if page_offset < 0:
                raise ValueError("page_offset must be >= 0.")
            query_string += f"&page[offset]={page_offset}"
        if page_limit is not None:
            page_limit = BaseAPI._coerce_page_int("page_limit", page_limit)
            if page_limit < 1:
                raise ValueError("page_limit must be >= 1.")
            if page_limit > 500:
                raise ValueError("page_limit must be <= 500.")
            query_string += f"&page[limit]={page_limit}"
        return query_string

    @staticmethod
    def _validate_code(code) -> str:
        """Validate an ISO alpha-2 country code and normalise it to uppercase."""
        if code is None or not isinstance(code, str) or code.strip() == "":
            raise ValueError("Parameter 'code' is required and must be a non-empty ISO alpha-2 string (e.g. 'US').")
        return code.strip().upper()

    @staticmethod
    def _validate_sort(sort, allowed):
        """Validate a sort value against an allowed enum; return it unchanged."""
        if sort is None:
            return None
        sort = str(sort).strip()
        if sort == "":
            return None
        if sort not in allowed:
            raise ValueError(f"sort must be one of {list(allowed)}.")
        return sort

    @staticmethod
    def _validate_fmt(fmt):
        """Validate fmt against the json/csv enum; return it lowercased."""
        if fmt is None:
            return None
        fmt = str(fmt).strip().lower()
        if fmt == "":
            return None
        if fmt not in ("json", "csv"):
            raise ValueError("fmt must be 'json' or 'csv'.")
        return fmt

    def get_real_estate_countries(
        self,
        api_token: str,
        sort: str = None,
        fmt: str = None,
        page_limit: int = None,
        page_offset: int = None,
    ):
        """
        GET /api/real-estate/countries

        List of covered countries and which datasets each carries.

        Params:
            sort: one of code, -code, name, -name.
            fmt: json (default) or csv.
            page_limit: 1..500 (default 50). page_offset: >= 0 (default 0).

        Response data[] item: { code, name, has_spp, has_dpp }.
        """
        sort = self._validate_sort(sort, self._SORT_COUNTRIES)
        fmt = self._validate_fmt(fmt)

        query_string = ""
        query_string += self._param("sort", sort)
        if fmt is not None:
            query_string += self._param("fmt", fmt)
        query_string += self._real_estate_pagination(page_offset, page_limit)

        return self._rest_get_method(
            api_key=api_token,
            endpoint="real-estate",
            uri="countries",
            querystring=query_string,
        )

    def get_real_estate_selected_prices(
        self,
        api_token: str,
        code: str,
        type: str = None,
        metric: str = None,
        from_date: str = None,
        to_date: str = None,
        sort: str = None,
        fmt: str = None,
        page_limit: int = None,
        page_offset: int = None,
    ):
        """
        GET /api/real-estate/{code}

        Selected Property Prices (SPP) — the headline harmonised series.

        Params:
            code: ISO alpha-2 country code (case-insensitive), e.g. "US".
            type: filter[type] — nominal or real.
            metric: filter[metric] — index or yoy.
            from_date: filter[from] — period YYYY-Qn (e.g. 2020-Q1).
            to_date: filter[to] — period YYYY-Qn.
            sort: one of period, -period, value, -value.
            fmt: json (default) or csv.
            page_limit: 1..500 (default 50). page_offset: >= 0 (default 0).

        Response data[] item: { period, value, type, metric }.
        """
        code = self._validate_code(code)
        sort = self._validate_sort(sort, self._SORT_SERIES)
        fmt = self._validate_fmt(fmt)

        query_string = ""
        query_string += self._filter("type", type)
        query_string += self._filter("metric", metric)
        query_string += self._filter("from", from_date)
        query_string += self._filter("to", to_date)
        query_string += self._param("sort", sort)
        if fmt is not None:
            query_string += self._param("fmt", fmt)
        query_string += self._real_estate_pagination(page_offset, page_limit)

        return self._rest_get_method(
            api_key=api_token,
            endpoint="real-estate",
            uri=code,
            querystring=query_string,
        )

    def get_real_estate_detailed_prices(
        self,
        api_token: str,
        code: str,
        area: str = None,
        property_type: str = None,
        vintage: str = None,
        freq: str = None,
        from_date: str = None,
        to_date: str = None,
        sort: str = None,
        fmt: str = None,
        page_limit: int = None,
        page_offset: int = None,
    ):
        """
        GET /api/real-estate/{code}/detailed

        Detailed Property Prices (DPP) — granular national BIS series.

        Params:
            code: ISO alpha-2 country code (case-insensitive), e.g. "AE".
            area: filter[area] — BIS covered-area dimension code.
            property_type: filter[property_type].
            vintage: filter[vintage].
            freq: filter[freq] — one of Q, A, M, H.
            from_date: filter[from] — period following the series frequency
                (e.g. 2020-01 or 2020-Q1).
            to_date: filter[to].
            sort: one of period, -period, value, -value.
            fmt: json (default) or csv.
            page_limit: 1..500 (default 50). page_offset: >= 0 (default 0).

        Response data[] item includes period, value, frequency, covered_area(+label),
        property_type(+label), vintage(+label), unit_measure(+label).
        """
        code = self._validate_code(code)
        sort = self._validate_sort(sort, self._SORT_SERIES)
        fmt = self._validate_fmt(fmt)

        if freq is not None:
            freq_value = str(freq).strip().upper()
            if freq_value != "" and freq_value not in ("Q", "A", "M", "H"):
                raise ValueError("freq must be one of 'Q', 'A', 'M', 'H'.")
        else:
            freq_value = None

        query_string = ""
        query_string += self._filter("area", area)
        query_string += self._filter("property_type", property_type)
        query_string += self._filter("vintage", vintage)
        query_string += self._filter("freq", freq_value)
        query_string += self._filter("from", from_date)
        query_string += self._filter("to", to_date)
        query_string += self._param("sort", sort)
        if fmt is not None:
            query_string += self._param("fmt", fmt)
        query_string += self._real_estate_pagination(page_offset, page_limit)

        return self._rest_get_method(
            api_key=api_token,
            endpoint="real-estate",
            uri=f"{code}/detailed",
            querystring=query_string,
        )

    def get_real_estate_detailed_series(self, api_token: str, code: str):
        """
        GET /api/real-estate/{code}/detailed/series

        Catalogue of the DPP series available for a country. Parameterless —
        fmt is not honoured here (the endpoint always returns JSON).

        Params:
            code: ISO alpha-2 country code (case-insensitive).

        Response data[] item includes covered_area(+label), property_type(+label),
        vintage(+label), compiling_org, priced_unit, seasonal_adj,
        unit_measure(+label), title. meta: { country_code, total }.
        """
        code = self._validate_code(code)

        return self._rest_get_method(
            api_key=api_token,
            endpoint="real-estate",
            uri=f"{code}/detailed/series",
            querystring="",
        )
