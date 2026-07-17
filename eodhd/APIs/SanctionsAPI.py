# APIs/SanctionsAPI.py

from urllib.parse import quote

from .BaseAPI import BaseAPI


class SanctionsAPI(BaseAPI):
    """
    Wrapper for Sanctions endpoints:

        GET /api/sanctions/entities
        GET /api/sanctions/vessels
        GET /api/sanctions/programs
        GET /api/sanctions/sources

    Notes:
    - All endpoints return a JSON envelope { data, meta, links }.
    - Filtering uses BARE query params (e.g. program=, q=, type=), NOT filter[...].
      (This differs from other EODHD endpoints; verified against prometheus-web
      request classes + live production.)
    - Pagination uses page[offset] and page[limit].
    """

    _SOURCE_VALUES = ("ofac",)
    _ENTITY_TYPE_VALUES = ("individual", "entity", "vessel", "aircraft")

    @staticmethod
    def _param(name: str, value) -> str:
        """Build a URL-encoded &name=value fragment.

        Returns "" for None or blank/whitespace-only values (so an empty string
        is treated as "omit the param", not "send &name="). Values are
        URL-encoded; the key is a bare query param (not filter[...])."""
        if value is None:
            return ""
        text = str(value).strip()
        if text == "":
            return ""
        return f"&{name}={quote(text, safe='')}"

    @staticmethod
    def _normalize_active(active):
        """Normalise the `active` filter to the API's "true"/"false" scalar.

        Accepts Python bools, or the strings "true"/"false" (any case). Anything
        else raises ValueError. Returns None if `active` is None."""
        if active is None:
            return None
        if isinstance(active, bool):
            return "true" if active else "false"
        text = str(active).strip().lower()
        if text not in ("true", "false"):
            raise ValueError("active must be a bool or one of 'true'/'false'.")
        return text

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

    def get_entities(
        self,
        api_token: str,
        q: str = None,
        program: str = None,
        country: str = None,
        source: str = None,
        entity_type: str = None,
        active: bool = None,
        page_offset: int = None,
        page_limit: int = None,
    ):
        """
        GET /api/sanctions/entities

        Query params (bare, not filter[...]):
            q           - free-text search (min 2 chars)
            program     - sanctions program
            country     - country
            source      - data source; currently only "ofac"
            type        - entity type: "individual" | "entity" | "vessel" | "aircraft"
                          (Python arg name: entity_type)
            active      - "true" | "false" (Python bool accepted)
            page[offset], page[limit] - pagination

        Fields: source, source_uid, entity_type, name, programs[], country,
        remarks, listed_date, is_active, aliases[], identifiers[].
        """
        if q is not None and len(str(q).strip()) < 2:
            raise ValueError("q (search) must be at least 2 characters.")
        if source is not None and str(source).strip().lower() not in self._SOURCE_VALUES:
            raise ValueError(f"source must be one of {self._SOURCE_VALUES}.")
        if entity_type is not None and str(entity_type).strip().lower() not in self._ENTITY_TYPE_VALUES:
            raise ValueError(f"type must be one of {self._ENTITY_TYPE_VALUES}.")
        active = self._normalize_active(active)

        query_string = ""
        query_string += self._param("q", q)
        query_string += self._param("program", program)
        query_string += self._param("country", country)
        if source is not None:
            query_string += self._param("source", str(source).strip().lower())
        if entity_type is not None:
            query_string += self._param("type", str(entity_type).strip().lower())
        if active is not None:
            query_string += self._param("active", active)
        query_string += self._pagination(page_offset, page_limit)

        return self._rest_get_method(
            api_key=api_token,
            endpoint="sanctions",
            uri="entities",
            querystring=query_string,
        )

    def get_vessels(
        self,
        api_token: str,
        q: str = None,
        imo: str = None,
        flag: str = None,
        vessel_type: str = None,
        program: str = None,
        source: str = None,
        page_offset: int = None,
        page_limit: int = None,
    ):
        """
        GET /api/sanctions/vessels

        Query params (bare, not filter[...]):
            q           - free-text search (min 2 chars)
            imo         - IMO number
            flag        - flag
            vessel_type - vessel type
            program     - sanctions program
            source      - data source; currently only "ofac"
            page[offset], page[limit] - pagination

        Fields: call_sign, vessel_type, flag, tonnage, gross_tonnage, owner,
        imo_number, mmsi, entity_source_uid, entity_name, source, programs[],
        country, is_active.
        """
        if q is not None and len(str(q).strip()) < 2:
            raise ValueError("q (search) must be at least 2 characters.")
        if source is not None and str(source).strip().lower() not in self._SOURCE_VALUES:
            raise ValueError(f"source must be one of {self._SOURCE_VALUES}.")

        query_string = ""
        query_string += self._param("q", q)
        query_string += self._param("imo", imo)
        query_string += self._param("flag", flag)
        query_string += self._param("vessel_type", vessel_type)
        query_string += self._param("program", program)
        if source is not None:
            query_string += self._param("source", str(source).strip().lower())
        query_string += self._pagination(page_offset, page_limit)

        return self._rest_get_method(
            api_key=api_token,
            endpoint="sanctions",
            uri="vessels",
            querystring=query_string,
        )

    def get_programs(self, api_token: str):
        """
        GET /api/sanctions/programs

        No params and no pagination (the server ignores any query params here).
        Fields: program, count.
        """
        return self._rest_get_method(
            api_key=api_token,
            endpoint="sanctions",
            uri="programs",
            querystring="",
        )

    def get_sources(self, api_token: str):
        """
        GET /api/sanctions/sources

        No params and no pagination (the server ignores any query params here).
        Fields: name.
        """
        return self._rest_get_method(
            api_key=api_token,
            endpoint="sanctions",
            uri="sources",
            querystring="",
        )
