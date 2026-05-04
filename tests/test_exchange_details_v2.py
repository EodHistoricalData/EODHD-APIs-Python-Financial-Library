"""Tests for ExchangeDetailsV2API."""

import pytest
from unittest.mock import MagicMock

from eodhd.APIs.ExchangeDetailsV2API import ExchangeDetailsV2API


@pytest.fixture
def mock_session():
    return MagicMock()


def _make_api(session):
    return ExchangeDetailsV2API(session=session)


def _mock_response(session, data=None):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = data or []
    session.get.return_value = resp


# --- List endpoint tests ---

def test_list_constructs_correct_url(mock_session):
    _mock_response(mock_session, data=[{"Code": "US", "Name": "US Exchanges"}])
    api = _make_api(mock_session)
    result = api.get_exchange_details_v2_list(api_token="test1234567890123456")

    call_url = mock_session.get.call_args[0][0]
    assert "/v2/exchange-details/" in call_url
    assert "api_token=test1234567890123456" in call_url
    assert result == [{"Code": "US", "Name": "US Exchanges"}]


def test_list_returns_list(mock_session):
    exchanges = [
        {"Code": "US", "Name": "US Exchanges"},
        {"Code": "LSE", "Name": "London Stock Exchange"},
    ]
    _mock_response(mock_session, data=exchanges)
    api = _make_api(mock_session)
    result = api.get_exchange_details_v2_list(api_token="test1234567890123456")

    assert len(result) == 2
    assert result[0]["Code"] == "US"
    assert result[1]["Code"] == "LSE"


# --- Single exchange endpoint tests ---

def test_single_constructs_correct_url(mock_session):
    detail = {"Code": "US", "Name": "US Exchanges", "TradingHours": {}}
    _mock_response(mock_session, data=detail)
    api = _make_api(mock_session)
    result = api.get_exchange_details_v2(api_token="test1234567890123456", code="US")

    call_url = mock_session.get.call_args[0][0]
    assert "/v2/exchange-details/US" in call_url
    assert "api_token=test1234567890123456" in call_url
    assert result == detail


def test_single_different_code(mock_session):
    detail = {"Code": "LSE", "Name": "London Stock Exchange"}
    _mock_response(mock_session, data=detail)
    api = _make_api(mock_session)
    result = api.get_exchange_details_v2(api_token="test1234567890123456", code="LSE")

    call_url = mock_session.get.call_args[0][0]
    assert "/v2/exchange-details/LSE" in call_url
    assert result["Code"] == "LSE"


def test_single_returns_dict(mock_session):
    detail = {
        "Code": "TO",
        "Name": "Toronto Stock Exchange",
        "TradingHours": {"open": "09:30", "close": "16:00"},
        "Holidays": ["2026-01-01", "2026-07-01"],
    }
    _mock_response(mock_session, data=detail)
    api = _make_api(mock_session)
    result = api.get_exchange_details_v2(api_token="test1234567890123456", code="TO")

    assert isinstance(result, dict)
    assert result["Code"] == "TO"
    assert "TradingHours" in result
    assert "Holidays" in result


# --- Error handling tests ---

def test_list_http_error(mock_session):
    from eodhd.errors import EODHDHTTPError

    resp = MagicMock()
    resp.status_code = 401
    resp.text = "Unauthorized"
    resp.json.return_value = {"message": "Invalid API token"}
    mock_session.get.return_value = resp

    api = _make_api(mock_session)
    with pytest.raises(EODHDHTTPError):
        api.get_exchange_details_v2_list(api_token="bad_token")


def test_single_http_error(mock_session):
    from eodhd.errors import EODHDHTTPError

    resp = MagicMock()
    resp.status_code = 404
    resp.text = "Not Found"
    resp.json.return_value = {"message": "Exchange not found"}
    mock_session.get.return_value = resp

    api = _make_api(mock_session)
    with pytest.raises(EODHDHTTPError):
        api.get_exchange_details_v2(api_token="test1234567890123456", code="INVALID")


def test_url_has_fmt_json(mock_session):
    """Verify fmt=json query parameter is included in the URL."""
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_exchange_details_v2_list(api_token="test1234567890123456")

    call_url = mock_session.get.call_args[0][0]
    assert "fmt=json" in call_url
