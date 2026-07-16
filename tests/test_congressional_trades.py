"""Tests for CongressionalTradesAPI."""

import pytest
from unittest.mock import MagicMock

from eodhd.APIs.CongressionalTradesAPI import CongressionalTradesAPI


@pytest.fixture
def mock_session():
    return MagicMock()


def _make_api(session):
    return CongressionalTradesAPI(session=session)


def _mock_response(session, data=None):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = data or {
        "data": [],
        "meta": {"total": 0, "page": {"offset": 0, "limit": 20}},
        "links": {"next": None},
    }
    session.get.return_value = resp


def test_basic_request(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    result = api.get_congressional_trades(api_token="test1234567890123456")

    call_url = mock_session.get.call_args[0][0]
    assert "/congressional-trades" in call_url
    assert "meta" in result


def test_filters(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_congressional_trades(
        api_token="test1234567890123456",
        chamber="senate",
        transaction_type="purchase,sale",
        symbol="AAPL",
        bioguide_id="S000250",
    )

    call_url = mock_session.get.call_args[0][0]
    assert "&chamber=senate" in call_url
    assert "&transaction_type=purchase,sale" in call_url
    assert "&symbol=AAPL" in call_url
    assert "&bioguide_id=S000250" in call_url


def test_date_range_and_pagination(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_congressional_trades(
        api_token="test1234567890123456",
        transaction_date_from="2024-01-01",
        transaction_date_to="2024-12-31",
        page_offset=0,
        page_limit=50,
    )

    call_url = mock_session.get.call_args[0][0]
    assert "&transaction_date_from=2024-01-01" in call_url
    assert "&transaction_date_to=2024-12-31" in call_url
    assert "&page[offset]=0" in call_url
    assert "&page[limit]=50" in call_url


def test_invalid_chamber_raises(mock_session):
    api = _make_api(mock_session)
    with pytest.raises(ValueError):
        api.get_congressional_trades(api_token="test1234567890123456", chamber="duma")


def test_invalid_transaction_type_raises(mock_session):
    api = _make_api(mock_session)
    with pytest.raises(ValueError):
        api.get_congressional_trades(api_token="test1234567890123456", transaction_type="bribe")
