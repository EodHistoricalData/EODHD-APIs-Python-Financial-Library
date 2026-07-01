# APIs/CreditSovereignRiskAPI.py

from urllib.parse import quote

from .BaseAPI import BaseAPI


class CreditSovereignRiskAPI(BaseAPI):
    """
    Wrapper for Credit & Sovereign Risk endpoints:

        GET /api/credit-risk/sovereign/risk-premium
        GET /api/credit-risk/sovereign/credit-ratings
        GET /api/credit-risk/sovereign/cds-spreads
        GET /api/credit-risk/sovereign/default-spreads
        GET /api/credit-risk/corporate/cmdi
        GET /api/credit-risk/corporate/hqm-yields
        GET /api/credit-risk/cds-market/aggregates

    Notes:
    - All endpoints return a JSON envelope { data, meta, links }.
    - Filtering uses filter[...] deep-object params.
    - Pagination uses page[offset] and page[limit].
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

    def get_sovereign_risk_premium(
        self,
        api_token: str,
        country: str = None,
        region: str = None,
        as_of: str = None,
        page_offset: int = None,
        page_limit: int = None,
    ):
        """
        GET /api/credit-risk/sovereign/risk-premium

        Fields: country_iso3, country_name, as_of_date, moodys_rating,
        adj_default_spread, country_risk_premium, equity_risk_premium,
        corporate_tax_rate, sovereign_cds (nullable), source.
        """
        query_string = ""
        query_string += self._filter("country", country)
        query_string += self._filter("region", region)
        query_string += self._filter("as_of", as_of)
        query_string += self._pagination(page_offset, page_limit)

        return self._rest_get_method(
            api_key=api_token,
            endpoint="credit-risk",
            uri="sovereign/risk-premium",
            querystring=query_string,
        )

    def get_sovereign_credit_ratings(
        self,
        api_token: str,
        country: str = None,
        as_of: str = None,
        page_offset: int = None,
        page_limit: int = None,
    ):
        """
        GET /api/credit-risk/sovereign/credit-ratings

        Fields: country_iso3, country_name, as_of_date, moodys_rating,
        sp_rating, fitch_rating, source.
        """
        query_string = ""
        query_string += self._filter("country", country)
        query_string += self._filter("as_of", as_of)
        query_string += self._pagination(page_offset, page_limit)

        return self._rest_get_method(
            api_key=api_token,
            endpoint="credit-risk",
            uri="sovereign/credit-ratings",
            querystring=query_string,
        )

    def get_sovereign_cds_spreads(
        self,
        api_token: str,
        country: str = None,
        as_of: str = None,
        page_offset: int = None,
        page_limit: int = None,
    ):
        """
        GET /api/credit-risk/sovereign/cds-spreads

        Fields: country_iso3, country_name, as_of_date, moodys_rating,
        cds_spread (nullable), cds_spread_net_of_switzerland (nullable), source.
        """
        query_string = ""
        query_string += self._filter("country", country)
        query_string += self._filter("as_of", as_of)
        query_string += self._pagination(page_offset, page_limit)

        return self._rest_get_method(
            api_key=api_token,
            endpoint="credit-risk",
            uri="sovereign/cds-spreads",
            querystring=query_string,
        )

    def get_sovereign_default_spreads(
        self,
        api_token: str,
        rating: str = None,
        as_of: str = None,
        page_offset: int = None,
        page_limit: int = None,
    ):
        """
        GET /api/credit-risk/sovereign/default-spreads

        Fields: rating, as_of_date, default_spread, source.
        """
        query_string = ""
        query_string += self._filter("rating", rating)
        query_string += self._filter("as_of", as_of)
        query_string += self._pagination(page_offset, page_limit)

        return self._rest_get_method(
            api_key=api_token,
            endpoint="credit-risk",
            uri="sovereign/default-spreads",
            querystring=query_string,
        )

    def get_corporate_cmdi(
        self,
        api_token: str,
        from_date: str = None,
        to_date: str = None,
        page_offset: int = None,
        page_limit: int = None,
    ):
        """
        GET /api/credit-risk/corporate/cmdi

        Filters: filter[from], filter[to].
        Fields: as_of_date, market_cmdi, ig_cmdi, hy_cmdi, source.
        """
        query_string = ""
        query_string += self._filter("from", from_date)
        query_string += self._filter("to", to_date)
        query_string += self._pagination(page_offset, page_limit)

        return self._rest_get_method(
            api_key=api_token,
            endpoint="credit-risk",
            uri="corporate/cmdi",
            querystring=query_string,
        )

    def get_corporate_hqm_yields(
        self,
        api_token: str,
        tenor: str = None,
        type: str = None,
        from_date: str = None,
        to_date: str = None,
        page_offset: int = None,
        page_limit: int = None,
    ):
        """
        GET /api/credit-risk/corporate/hqm-yields

        Filters: filter[tenor], filter[type] (par|spot), filter[from], filter[to].
        Fields: series_id, tenor_years, yield_type, as_of_date, yield_value, source.
        """
        if type is not None and str(type).lower() not in ("par", "spot"):
            raise ValueError("type must be 'par' or 'spot'.")

        query_string = ""
        query_string += self._filter("tenor", tenor)
        if type is not None:
            query_string += self._filter("type", str(type).lower())
        query_string += self._filter("from", from_date)
        query_string += self._filter("to", to_date)
        query_string += self._pagination(page_offset, page_limit)

        return self._rest_get_method(
            api_key=api_token,
            endpoint="credit-risk",
            uri="corporate/hqm-yields",
            querystring=query_string,
        )

    def get_cds_market_aggregates(
        self,
        api_token: str,
        metric: str = None,
        dimension: str = None,
        from_date: str = None,
        to_date: str = None,
        page_offset: int = None,
        page_limit: int = None,
    ):
        """
        GET /api/credit-risk/cds-market/aggregates

        Filters: filter[metric] (gross_notional), filter[dimension] (grade|cleared_status),
        filter[from], filter[to].
        Fields: as_of_date, release_date, metric, breakdown_dimension,
        breakdown_value, region, usd_notional_mn, source.
        """
        query_string = ""
        query_string += self._filter("metric", metric)
        query_string += self._filter("dimension", dimension)
        query_string += self._filter("from", from_date)
        query_string += self._filter("to", to_date)
        query_string += self._pagination(page_offset, page_limit)

        return self._rest_get_method(
            api_key=api_token,
            endpoint="credit-risk",
            uri="cds-market/aggregates",
            querystring=query_string,
        )
