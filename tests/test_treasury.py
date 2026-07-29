"""Tests for TreasuryAPI."""

import pytest
from unittest.mock import MagicMock

from eodhd.APIs.TreasuryAPI import TreasuryAPI


@pytest.fixture
def mock_session():
    return MagicMock()


def _make_api(session):
    return TreasuryAPI(session=session)


def _mock_response(session, data=None):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = data or [{"date": "2024-01-01", "rate": 5.0}]
    session.get.return_value = resp


def test_bill_rates(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    result = api.get_treasury_bill_rates(api_token="test1234567890123456")

    call_url = mock_session.get.call_args[0][0]
    assert "/ust/bill-rates" in call_url
    assert len(result) == 1


def test_yield_rates(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    result = api.get_treasury_yield_rates(api_token="test1234567890123456")

    call_url = mock_session.get.call_args[0][0]
    assert "/ust/yield-rates" in call_url


def test_long_term_rates(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    result = api.get_treasury_long_term_rates(api_token="test1234567890123456")

    call_url = mock_session.get.call_args[0][0]
    assert "/ust/long-term-rates" in call_url


def test_real_yield_rates(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    result = api.get_treasury_real_yield_rates(api_token="test1234567890123456")

    call_url = mock_session.get.call_args[0][0]
    assert "/ust/real-yield-rates" in call_url


def test_no_pagination_or_date_params(mock_session):
    """UST endpoints ignore pagination/date-range params, so the SDK must not emit them."""
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_treasury_bill_rates(api_token="test1234567890123456")

    call_url = mock_session.get.call_args[0][0]
    assert "from=" not in call_url
    assert "to=" not in call_url
    assert "page[" not in call_url


def test_no_year_filter_when_omitted(mock_session):
    """When year is omitted, no filter[year] must be emitted (API defaults to current year)."""
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_treasury_bill_rates(api_token="test1234567890123456")

    call_url = mock_session.get.call_args[0][0]
    assert "filter[year]" not in call_url
    assert "filter[" not in call_url


def test_year_filter_emitted(mock_session):
    """When year is passed, filter[year]=<year> is emitted on every UST endpoint."""
    _mock_response(mock_session)
    api = _make_api(mock_session)

    for method, path in (
        (api.get_treasury_bill_rates, "/ust/bill-rates"),
        (api.get_treasury_yield_rates, "/ust/yield-rates"),
        (api.get_treasury_long_term_rates, "/ust/long-term-rates"),
        (api.get_treasury_real_yield_rates, "/ust/real-yield-rates"),
    ):
        method(api_token="test1234567890123456", year=2024)
        call_url = mock_session.get.call_args[0][0]
        assert path in call_url
        assert "filter[year]=2024" in call_url
