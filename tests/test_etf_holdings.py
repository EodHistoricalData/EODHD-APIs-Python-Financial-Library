"""Tests for EtfHoldingsAPI (ETF Holdings, beta, SEC N-PORT, US-listed ETFs only)."""

import pytest
from unittest.mock import MagicMock

from eodhd import APIClient
from eodhd.APIs.EtfHoldingsAPI import EtfHoldingsAPI
from eodhd.errors import EODHDHTTPError


@pytest.fixture
def mock_session():
    return MagicMock()


def _make_api(session):
    return EtfHoldingsAPI(session=session)


def _mock_response(session, data=None, status=200, text=""):
    resp = MagicMock()
    resp.status_code = status
    resp.text = text
    resp.json.return_value = data if data is not None else {"data": {}, "meta": [], "links": []}
    session.get.return_value = resp


HOLDINGS_BODY = {
    "data": {
        "General": {"Code": "XLE", "Type": "ETF", "Exchange": "US", "Is_Complete": True},
        "Holdings": {
            "XOM.US": {"Code": "XOM", "Exchange": "US", "Name": "Exxon Mobil Corp",
                       "Assets_%": 23.1, "Shares": 1000.0, "Value_USD": 100000.0},
        },
        "Top_10_Holdings": {},
        "Holdings_Count": 1,
        "Asset_Allocation": {},
        "Sector_Weights": {},
        "World_Regions": {},
        "Performance": None,
    },
    "meta": [],
    "links": [],
}

HELD_BY_BODY = {
    "data": {
        "security": {"ticker": "NVDA", "exchange": "US", "name": "NVIDIA Corp"},
        "held_by_count": 791,
        "funds": [{"ticker": "VTI", "name": "Vanguard Total Stock Market ETF", "weight": 6.1,
                   "shares": 1.0, "value_usd": 2.0, "report_date": "2026-09-30"}],
    },
    "meta": {"total": 791, "offset": 0, "limit": 3},
    "links": {"next": "/api/etf/security/NVDA/held-by?page%5Boffset%5D=3&page%5Blimit%5D=3"},
}


# --- holdings ---

def test_holdings_url(mock_session):
    _mock_response(mock_session, HOLDINGS_BODY)
    result = _make_api(mock_session).get_holdings(api_token="test1234567890123456", ticker="XLE")

    call_url = mock_session.get.call_args[0][0]
    assert call_url.startswith("https://eodhd.com/api/etf/holdings/XLE?api_token=test1234567890123456")
    assert "page[" not in call_url
    assert result["data"]["Holdings_Count"] == 1


def test_holdings_ticker_with_suffix_is_encoded(mock_session):
    _mock_response(mock_session)
    _make_api(mock_session).get_holdings(api_token="t", ticker="VTI.US")
    assert "/etf/holdings/VTI.US?" in mock_session.get.call_args[0][0]


def test_holdings_blank_ticker_raises(mock_session):
    with pytest.raises(ValueError):
        _make_api(mock_session).get_holdings(api_token="t", ticker="  ")
    mock_session.get.assert_not_called()


def test_holdings_empty_list_edge_case(mock_session):
    """A fund with no positions returns Holdings as an empty list, not an object."""
    body = {"data": {"General": {"Code": "GAID"}, "Holdings": [], "Top_10_Holdings": [],
                     "Holdings_Count": 0}, "meta": [], "links": []}
    _mock_response(mock_session, body)
    result = _make_api(mock_session).get_holdings(api_token="t", ticker="GAID")
    assert result["data"]["Holdings"] == []
    assert result["data"]["Holdings_Count"] == 0


def test_holdings_404_raises_with_code_in_body(mock_session):
    body = {"errors": [{"status": "404", "title": "Symbol not found", "code": "NOT_COVERED",
                        "detail": "This ticker is outside ETF holdings coverage."}]}
    _mock_response(mock_session, body, status=404, text="NOT_COVERED")
    with pytest.raises(EODHDHTTPError) as exc:
        _make_api(mock_session).get_holdings(api_token="t", ticker="GLD")
    assert exc.value.status_code == 404
    assert "NOT_COVERED" in exc.value.response_body


# --- held-by ---

def test_held_by_url_and_pagination(mock_session):
    _mock_response(mock_session, HELD_BY_BODY)
    result = _make_api(mock_session).get_held_by(
        api_token="test1234567890123456", ticker="NVDA", page_offset=0, page_limit=3)

    call_url = mock_session.get.call_args[0][0]
    assert "/api/etf/security/NVDA/held-by?api_token=test1234567890123456" in call_url
    assert "&page[offset]=0" in call_url
    assert "&page[limit]=3" in call_url
    assert result["data"]["held_by_count"] == 791
    assert result["links"]["next"] is not None


def test_held_by_no_pagination_params_by_default(mock_session):
    _mock_response(mock_session, HELD_BY_BODY)
    _make_api(mock_session).get_held_by(api_token="t", ticker="XOM")
    assert "page[" not in mock_session.get.call_args[0][0]


def test_held_by_foreign_ticker_is_url_encoded(mock_session):
    _mock_response(mock_session, HELD_BY_BODY)
    _make_api(mock_session).get_held_by(api_token="t", ticker="ASML.AS")
    assert "/etf/security/ASML.AS/held-by?" in mock_session.get.call_args[0][0]


def test_held_by_limit_up_to_5000_allowed(mock_session):
    _mock_response(mock_session, HELD_BY_BODY)
    _make_api(mock_session).get_held_by(api_token="t", ticker="NVDA", page_limit=5000)
    assert "&page[limit]=5000" in mock_session.get.call_args[0][0]


@pytest.mark.parametrize("kwargs", [
    {"page_limit": 5001}, {"page_limit": 0}, {"page_offset": -1},
    {"page_limit": True}, {"page_offset": 1.5},
])
def test_held_by_invalid_pagination_raises(mock_session, kwargs):
    with pytest.raises(ValueError):
        _make_api(mock_session).get_held_by(api_token="t", ticker="NVDA", **kwargs)
    mock_session.get.assert_not_called()


def test_held_by_blank_ticker_raises(mock_session):
    with pytest.raises(ValueError):
        _make_api(mock_session).get_held_by(api_token="t", ticker="")


def test_held_by_past_the_end_is_empty_funds(mock_session):
    body = {"data": {"security": {"ticker": "NVDA"}, "held_by_count": 791, "funds": []},
            "meta": {"total": 791, "offset": 5000, "limit": 100}, "links": {"next": None}}
    _mock_response(mock_session, body)
    result = _make_api(mock_session).get_held_by(api_token="t", ticker="NVDA", page_offset=5000)
    assert result["data"]["funds"] == []
    assert result["links"]["next"] is None


def test_held_by_403_raises(mock_session):
    _mock_response(mock_session, status=403, text="Forbidden")
    mock_session.get.return_value.json.side_effect = ValueError("not json")
    with pytest.raises(EODHDHTTPError) as exc:
        _make_api(mock_session).get_held_by(api_token="demo", ticker="NVDA")
    assert exc.value.status_code == 403


# --- APIClient facade ---

def test_client_facade_methods(mock_session):
    client = APIClient("test1234567890123456")
    client._session = mock_session
    _mock_response(mock_session, HOLDINGS_BODY)
    client.get_etf_holdings("XLE")
    assert "/api/etf/holdings/XLE?api_token=test1234567890123456" in mock_session.get.call_args[0][0]

    _mock_response(mock_session, HELD_BY_BODY)
    client.get_etf_held_by("NVDA", page_offset=3, page_limit=3)
    url = mock_session.get.call_args[0][0]
    assert "/api/etf/security/NVDA/held-by?api_token=test1234567890123456" in url
    assert "&page[offset]=3" in url and "&page[limit]=3" in url
