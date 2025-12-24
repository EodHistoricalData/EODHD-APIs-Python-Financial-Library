#APIs/IDMappingAPI.py

from .BaseAPI import BaseAPI


class IDMappingAPI(BaseAPI):
    """
    Wrapper for:
        GET /api/id-mapping

    Resolve identifiers (CUSIP/ISIN/FIGI/LEI/CIK) <-> tradable symbol.

    Notes:
    - At least one filter[...] value is required.
    - Pagination uses page[limit] (1..1000) and page[offset] (>=0).
    """

    def get_id_mapping(
        self,
        api_token: str,
        symbol: str = None,
        ex: str = None,
        isin: str = None,
        figi: str = None,
        lei: str = None,
        cusip: str = None,
        cik: str = None,
        page_limit: int = None,
        page_offset: int = None,
        fmt: str = None,  # "json" or "xml"
    ):
        # Validate: at least one filter must be provided
        if not any([symbol, ex, isin, figi, lei, cusip, cik]):
            raise ValueError(
                "At least one filter must be provided: symbol, ex, isin, figi, lei, cusip, cik."
            )

        if page_limit is not None:
            page_limit = int(page_limit)
            if page_limit < 1 or page_limit > 1000:
                raise ValueError("page_limit must be in range 1..1000.")
        if page_offset is not None:
            page_offset = int(page_offset)
            if page_offset < 0:
                raise ValueError("page_offset must be >= 0.")

        if fmt is not None:
            fmt = str(fmt).lower()
            if fmt not in ("json", "xml"):
                raise ValueError("fmt must be 'json' or 'xml'.")

        endpoint = "id-mapping"
        query_string = ""

        if symbol is not None:
            query_string += f"&filter[symbol]={symbol}"
        if ex is not None:
            query_string += f"&filter[ex]={ex}"
        if isin is not None:
            query_string += f"&filter[isin]={isin}"
        if figi is not None:
            query_string += f"&filter[figi]={figi}"
        if lei is not None:
            query_string += f"&filter[lei]={lei}"
        if cusip is not None:
            query_string += f"&filter[cusip]={cusip}"
        if cik is not None:
            # keep as string to preserve leading zeros if provided
            query_string += f"&filter[cik]={cik}"

        if page_limit is not None:
            query_string += f"&page[limit]={page_limit}"
        if page_offset is not None:
            query_string += f"&page[offset]={page_offset}"

        if fmt is not None:
            query_string += f"&fmt={fmt}"

        return self._rest_get_method(
            api_key=api_token,
            endpoint=endpoint,
            querystring=query_string,
        )
