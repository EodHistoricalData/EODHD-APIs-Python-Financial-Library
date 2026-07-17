"""Tests for SanctionsAPI.

Note: sanctions endpoints use BARE query params (program=, q=, type=, active=,
imo=, flag=, vessel_type=, source=, country=), NOT filter[...]. Pagination still
uses page[offset]/page[limit].
"""

import pytest
from unittest.mock import MagicMock

from eodhd.APIs.SanctionsAPI import SanctionsAPI


@pytest.fixture
def mock_session():
    return MagicMock()


def _make_api(session):
    return SanctionsAPI(session=session)


def _mock_response(session, data=None):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = data if data is not None else {"data": [], "meta": {}, "links": {}}
    session.get.return_value = resp


def test_entities_url(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_entities(api_token="test1234567890123456")

    call_url = mock_session.get.call_args[0][0]
    assert "/sanctions/entities" in call_url
    assert "api_token=test1234567890123456" in call_url


def test_entities_bare_params(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_entities(
        api_token="test1234567890123456", q="Acme", program="OFAC-SDN",
        country="RU", source="ofac", entity_type="individual", active=True,
        page_offset=0, page_limit=25,
    )

    call_url = mock_session.get.call_args[0][0]
    # bare keys, not filter[...]
    assert "&q=Acme" in call_url
    assert "&program=OFAC-SDN" in call_url
    assert "&country=RU" in call_url
    assert "&source=ofac" in call_url
    assert "&type=individual" in call_url
    assert "&active=true" in call_url
    assert "page[offset]=0" in call_url
    assert "page[limit]=25" in call_url
    # must NOT use filter[...] style
    assert "filter[" not in call_url


def test_entities_active_false(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_entities(api_token="test1234567890123456", active=False)

    call_url = mock_session.get.call_args[0][0]
    assert "&active=false" in call_url


def test_entities_q_too_short(mock_session):
    api = _make_api(mock_session)
    with pytest.raises(ValueError):
        api.get_entities(api_token="test1234567890123456", q="a")


def test_entities_invalid_source(mock_session):
    api = _make_api(mock_session)
    with pytest.raises(ValueError):
        api.get_entities(api_token="test1234567890123456", source="eu")


def test_entities_invalid_type(mock_session):
    api = _make_api(mock_session)
    with pytest.raises(ValueError):
        api.get_entities(api_token="test1234567890123456", entity_type="ship")


def test_entities_value_url_encoded(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_entities(api_token="test1234567890123456", program="A & B")

    call_url = mock_session.get.call_args[0][0]
    assert "&program=A%20%26%20B" in call_url
    assert "&program=A & B" not in call_url


def test_vessels_url(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_vessels(
        api_token="test1234567890123456", imo="9074729", flag="RU",
        vessel_type="cargo", q="tanker", program="OFAC-SDN", source="ofac",
    )

    call_url = mock_session.get.call_args[0][0]
    assert "/sanctions/vessels" in call_url
    assert "&imo=9074729" in call_url
    assert "&flag=RU" in call_url
    assert "&vessel_type=cargo" in call_url
    assert "&q=tanker" in call_url
    assert "&program=OFAC-SDN" in call_url
    assert "&source=ofac" in call_url
    assert "filter[" not in call_url


def test_vessels_q_too_short(mock_session):
    api = _make_api(mock_session)
    with pytest.raises(ValueError):
        api.get_vessels(api_token="test1234567890123456", q="x")


def test_vessels_invalid_source(mock_session):
    api = _make_api(mock_session)
    with pytest.raises(ValueError):
        api.get_vessels(api_token="test1234567890123456", source="un")


def test_programs_url(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_programs(api_token="test1234567890123456")

    call_url = mock_session.get.call_args[0][0]
    assert "/sanctions/programs" in call_url
    # programs is not paginated server-side; no page params are sent
    assert "page[" not in call_url


def test_sources_url(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_sources(api_token="test1234567890123456")

    call_url = mock_session.get.call_args[0][0]
    assert "/sanctions/sources" in call_url
    assert "page[" not in call_url


def test_invalid_pagination(mock_session):
    api = _make_api(mock_session)
    with pytest.raises(ValueError):
        api.get_entities(api_token="test1234567890123456", page_offset=-1)
    with pytest.raises(ValueError):
        api.get_entities(api_token="test1234567890123456", page_limit=0)


def test_active_string_accepted(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_entities(api_token="test1234567890123456", active="TRUE")

    call_url = mock_session.get.call_args[0][0]
    assert "&active=true" in call_url


def test_active_invalid_value(mock_session):
    api = _make_api(mock_session)
    with pytest.raises(ValueError):
        api.get_entities(api_token="test1234567890123456", active="yes")


def test_source_whitespace_tolerated(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    # surrounding whitespace should not cause a spurious ValueError
    api.get_entities(api_token="test1234567890123456", source="ofac ")

    call_url = mock_session.get.call_args[0][0]
    assert "&source=ofac" in call_url


def test_blank_value_omitted(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    # empty/whitespace-only values are omitted, not sent as &program=
    api.get_entities(api_token="test1234567890123456", program="   ")

    call_url = mock_session.get.call_args[0][0]
    assert "&program=" not in call_url
