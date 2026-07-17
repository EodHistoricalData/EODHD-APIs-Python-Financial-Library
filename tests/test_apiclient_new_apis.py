"""Facade-level tests for the Credit&Sovereign Risk / Sanctions / Interest Rates
methods on APIClient.

These complement the per-API-class tests: they exercise the public APIClient
methods end-to-end (arg forwarding, param names, path, and the bare-vs-filter[...]
convention) so a facade wiring regression (renamed/dropped kwarg, wrong path)
is caught.
"""

from urllib.parse import parse_qs, urlsplit

import pytest
from unittest.mock import MagicMock

from eodhd import APIClient


@pytest.fixture
def client():
    api = APIClient(api_key="test1234567890123456")
    session = MagicMock()
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"data": [], "meta": {}, "links": {}}
    session.get.return_value = resp
    api._session = session
    return api


def _split(session):
    url = session.get.call_args[0][0]
    parts = urlsplit(url)
    return parts.path, parse_qs(parts.query, keep_blank_values=True)


def test_facade_sovereign_risk_premium(client):
    client.get_sovereign_risk_premium(country="USA", region="North America",
                                      as_of="2024-01-01", page_offset=0, page_limit=50)
    path, qs = _split(client._session)
    assert path.endswith("/credit-risk/sovereign/risk-premium")
    assert qs["filter[country]"] == ["USA"]
    assert qs["filter[region]"] == ["North America"]
    assert qs["page[offset]"] == ["0"]
    assert qs["page[limit]"] == ["50"]


def test_facade_cds_market_aggregates_value_region(client):
    client.get_cds_market_aggregates(metric="gross_notional", dimension="grade",
                                     value="Investment Grade", region="North America")
    path, qs = _split(client._session)
    assert path.endswith("/credit-risk/cds-market/aggregates")
    assert qs["filter[value]"] == ["Investment Grade"]
    assert qs["filter[region]"] == ["North America"]


def test_facade_hqm_yields_yield_type(client):
    client.get_corporate_hqm_yields(tenor="10", yield_type="spot,par")
    path, qs = _split(client._session)
    assert path.endswith("/credit-risk/corporate/hqm-yields")
    assert qs["filter[tenor]"] == ["10"]
    assert qs["filter[type]"] == ["spot,par"]


def test_facade_sanctions_entities_bare_and_type_mapping(client):
    client.get_sanctions_entities(program="OFAC-SDN", country="RU",
                                  entity_type="individual", active=False)
    path, qs = _split(client._session)
    assert path.endswith("/sanctions/entities")
    # bare params, entity_type -> type, active=False serialised to "false"
    assert qs["program"] == ["OFAC-SDN"]
    assert qs["type"] == ["individual"]
    assert qs["active"] == ["false"]
    assert not any(k.startswith("filter[") for k in qs)


def test_facade_sanctions_vessels(client):
    client.get_sanctions_vessels(imo="9074729", flag="RU", source="ofac")
    path, qs = _split(client._session)
    assert path.endswith("/sanctions/vessels")
    assert qs["imo"] == ["9074729"]
    assert qs["source"] == ["ofac"]


def test_facade_sanctions_programs_sources_no_pagination(client):
    for call in (client.get_sanctions_programs, client.get_sanctions_sources):
        call()
        _path, qs = _split(client._session)
        assert not any(k.startswith("page[") for k in qs)


def test_facade_reference_rates(client):
    client.get_reference_rates(code="SOFR", currency="usd")
    path, qs = _split(client._session)
    assert path.endswith("/rates/reference-rates")
    assert qs["filter[code]"] == ["SOFR"]
    assert qs["filter[currency]"] == ["USD"]


def test_facade_funding_stress_no_pagination(client):
    client.get_funding_stress(code="SOFR_OIS")
    path, qs = _split(client._session)
    assert path.endswith("/spreads/funding-stress")
    assert not any(k.startswith("page[") for k in qs)
