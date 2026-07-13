"""Tests for ASXCorporateActionsAPI.

Note: the ASX corporate actions endpoint uses BARE query params
(type=, symbol=, date_from=, date_to=), NOT filter[...]. Pagination still
uses page[offset]/page[limit].
"""

import pytest
from unittest.mock import MagicMock

from eodhd.APIs.ASXCorporateActionsAPI import ASXCorporateActionsAPI


@pytest.fixture
def mock_session():
    return MagicMock()


def _make_api(session):
    return ASXCorporateActionsAPI(session=session)


def _mock_response(session, data=None):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = (
        data
        if data is not None
        else {"data": [], "meta": {"total": 0, "page": {"offset": 0, "limit": 100}}, "links": {}}
    )
    session.get.return_value = resp


def test_corporate_actions_url(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_corporate_actions(api_token="test1234567890123456")

    call_url = mock_session.get.call_args[0][0]
    assert "/asx-corporate-actions" in call_url
    assert "api_token=test1234567890123456" in call_url
    assert "fmt=json" in call_url


def test_corporate_actions_bare_params(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_corporate_actions(
        api_token="test1234567890123456", type="dividends", symbol="PMV.AU",
        date_from="2026-01-01", date_to="2026-12-31",
        page_offset=0, page_limit=25,
    )

    call_url = mock_session.get.call_args[0][0]
    # bare keys, not filter[...]
    assert "&type=dividends" in call_url
    assert "&symbol=PMV.AU" in call_url
    assert "&date_from=2026-01-01" in call_url
    assert "&date_to=2026-12-31" in call_url
    assert "page[offset]=0" in call_url
    assert "page[limit]=25" in call_url
    # must NOT use filter[...] style
    assert "filter[" not in call_url


def test_corporate_actions_returns_envelope(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    result = api.get_corporate_actions(api_token="test1234567890123456")

    assert "data" in result
    assert "meta" in result
    assert "links" in result


def test_type_normalised_lowercase(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_corporate_actions(api_token="test1234567890123456", type="Dividends")

    call_url = mock_session.get.call_args[0][0]
    assert "&type=dividends" in call_url


def test_type_hyphenated_value(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_corporate_actions(api_token="test1234567890123456", type="capital-returns")

    call_url = mock_session.get.call_args[0][0]
    assert "&type=capital-returns" in call_url


def test_invalid_type(mock_session):
    api = _make_api(mock_session)
    with pytest.raises(ValueError):
        api.get_corporate_actions(api_token="test1234567890123456", type="mergers")


def test_symbol_url_encoded(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_corporate_actions(api_token="test1234567890123456", symbol="A & B.AU")

    call_url = mock_session.get.call_args[0][0]
    assert "&symbol=A%20%26%20B.AU" in call_url
    assert "&symbol=A & B.AU" not in call_url


def test_blank_value_omitted(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    # empty/whitespace-only values are omitted, not sent as &symbol=
    api.get_corporate_actions(api_token="test1234567890123456", symbol="   ")

    call_url = mock_session.get.call_args[0][0]
    assert "&symbol=" not in call_url


def test_invalid_pagination(mock_session):
    api = _make_api(mock_session)
    with pytest.raises(ValueError):
        api.get_corporate_actions(api_token="test1234567890123456", page_offset=-1)
    with pytest.raises(ValueError):
        api.get_corporate_actions(api_token="test1234567890123456", page_limit=0)
    with pytest.raises(ValueError):
        api.get_corporate_actions(api_token="test1234567890123456", page_limit=1001)


def test_client_facade_delegates(mock_session):
    _mock_response(mock_session)
    from eodhd.apiclient import APIClient

    client = APIClient("test1234567890123456")
    client._session = mock_session
    client.get_asx_corporate_actions(type="splits", symbol="BHP.AU", page_limit=10)

    call_url = mock_session.get.call_args[0][0]
    assert "/asx-corporate-actions" in call_url
    assert "&type=splits" in call_url
    assert "&symbol=BHP.AU" in call_url
    assert "page[limit]=10" in call_url
