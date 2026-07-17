# APIs/CreditSovereignRiskAPI.py

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
    - Value-level validation is limited to the small closed enums the server
      guarantees (e.g. HQM yield type par/spot); other filter values (metric,
      dimension, tenor grid, dates, lengths) are validated server-side.
    """

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
        yield_type: str = None,
        from_date: str = None,
        to_date: str = None,
        page_offset: int = None,
        page_limit: int = None,
    ):
        """
        GET /api/credit-risk/corporate/hqm-yields

        Filters: filter[tenor], filter[type] (par|spot), filter[from], filter[to].
        Both filter[tenor] and filter[type] accept a comma-separated list
        (e.g. yield_type="spot,par"), matching the server's CsvIn validation.
        `yield_type` is serialised to filter[type]; the tenor grid is validated
        server-side. A blank/empty value is treated as "no filter", not an error.
        Fields: series_id, tenor_years, yield_type, as_of_date, yield_value, source.
        """
        yield_type_value = None
        if yield_type is not None:
            parts = [p.strip().lower() for p in str(yield_type).split(",") if p.strip()]
            if parts and any(p not in ("par", "spot") for p in parts):
                raise ValueError("yield_type must be 'par', 'spot', or a comma-separated combination (e.g. 'spot,par').")
            if parts:
                yield_type_value = ",".join(parts)

        query_string = ""
        query_string += self._filter("tenor", tenor)
        query_string += self._filter("type", yield_type_value)
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
        value: str = None,
        region: str = None,
        from_date: str = None,
        to_date: str = None,
        page_offset: int = None,
        page_limit: int = None,
    ):
        """
        GET /api/credit-risk/cds-market/aggregates

        Filters: filter[metric] (gross_notional), filter[dimension] (grade|cleared_status),
        filter[value] (a specific breakdown value), filter[region], filter[from], filter[to].
        Fields: as_of_date, release_date, metric, breakdown_dimension,
        breakdown_value, region, usd_notional_mn, source.
        """
        query_string = ""
        query_string += self._filter("metric", metric)
        query_string += self._filter("dimension", dimension)
        query_string += self._filter("value", value)
        query_string += self._filter("region", region)
        query_string += self._filter("from", from_date)
        query_string += self._filter("to", to_date)
        query_string += self._pagination(page_offset, page_limit)

        return self._rest_get_method(
            api_key=api_token,
            endpoint="credit-risk",
            uri="cds-market/aggregates",
            querystring=query_string,
        )
