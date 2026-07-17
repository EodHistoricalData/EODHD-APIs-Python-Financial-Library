# APIs/InterestRatesAPI.py

from urllib.parse import quote

from .BaseAPI import BaseAPI


class InterestRatesAPI(BaseAPI):
    """
    Wrapper for Interest Rates & Spreads endpoints:

        GET /api/rates/reference-rates
        GET /api/rates/policy-rates
        GET /api/spreads/funding-stress

    Notes:
    - All endpoints return a JSON envelope { data, meta, links }.
    - Filtering uses filter[...] deep-object params.
    - rates/* endpoints paginate with page[offset]/page[limit].
    - spreads/funding-stress does NOT support pagination.
    """

    @staticmethod
    def _filter(name: str, value) -> str:
        """Build a URL-encoded &filter[name]=value fragment (empty if value is None)."""
        if value is None:
            return ""
        return f"&filter[{name}]={quote(str(value), safe='')}"

    @staticmethod
    def _pagination(page_offset: int = None, page_limit: int = None) -> str:
        query_string = ""
        if page_offset is not None:
            page_offset = int(page_offset)
            if page_offset < 0:
                raise ValueError("page_offset must be >= 0.")
            query_string += f"&page[offset]={page_offset}"
        if page_limit is not None:
            page_limit = int(page_limit)
            if page_limit < 1:
                raise ValueError("page_limit must be >= 1.")
            query_string += f"&page[limit]={page_limit}"
        return query_string

    def get_reference_rates(
        self,
        api_token: str,
        code: str = None,
        currency: str = None,
        from_date: str = None,
        to_date: str = None,
        page_offset: int = None,
        page_limit: int = None,
    ):
        """
        GET /api/rates/reference-rates

        Filters: filter[code], filter[currency], filter[from], filter[to].
        Currently populated currencies are USD (SOFR), GBP (SONIA) and EUR (ESTR);
        the value is uppercased but not restricted client-side, since the server
        does not enforce a fixed currency set.
        Fields: date, code, currency, rate_type, rate, source, source_series_id.
        """
        query_string = ""
        query_string += self._filter("code", code)
        if currency is not None:
            query_string += self._filter("currency", str(currency).upper())
        query_string += self._filter("from", from_date)
        query_string += self._filter("to", to_date)
        query_string += self._pagination(page_offset, page_limit)

        return self._rest_get_method(
            api_key=api_token,
            endpoint="rates",
            uri="reference-rates",
            querystring=query_string,
        )

    def get_policy_rates(
        self,
        api_token: str,
        code: str = None,
        country: str = None,
        central_bank: str = None,
        from_date: str = None,
        to_date: str = None,
        page_offset: int = None,
        page_limit: int = None,
    ):
        """
        GET /api/rates/policy-rates

        Filters: filter[code], filter[country], filter[central_bank], filter[from], filter[to].
        Fields: date, code, country, central_bank, rate, source, source_series_id.
        """
        query_string = ""
        query_string += self._filter("code", code)
        query_string += self._filter("country", country)
        query_string += self._filter("central_bank", central_bank)
        query_string += self._filter("from", from_date)
        query_string += self._filter("to", to_date)
        query_string += self._pagination(page_offset, page_limit)

        return self._rest_get_method(
            api_key=api_token,
            endpoint="rates",
            uri="policy-rates",
            querystring=query_string,
        )

    def get_funding_stress(
        self,
        api_token: str,
        code: str = None,
        from_date: str = None,
        to_date: str = None,
    ):
        """
        GET /api/spreads/funding-stress

        Filters: filter[code], filter[from], filter[to]. NO pagination.
        Fields: date, code, value_bps, formula, leg_a, leg_b, leg_a_rate, leg_b_rate.
        """
        query_string = ""
        query_string += self._filter("code", code)
        query_string += self._filter("from", from_date)
        query_string += self._filter("to", to_date)

        return self._rest_get_method(
            api_key=api_token,
            endpoint="spreads",
            uri="funding-stress",
            querystring=query_string,
        )
