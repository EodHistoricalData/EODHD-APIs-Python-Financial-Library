"""Tests for InterestRatesAPI."""

import pytest
from unittest.mock import MagicMock

from eodhd.APIs.InterestRatesAPI import InterestRatesAPI


@pytest.fixture
def mock_session():
    return MagicMock()


def _make_api(session):
    return InterestRatesAPI(session=session)


def _mock_response(session, data=None):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = data if data is not None else {"data": [], "meta": {}, "links": {}}
    session.get.return_value = resp


def test_reference_rates_url(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_reference_rates(api_token="test1234567890123456", code="SOFR", currency="USD")

    call_url = mock_session.get.call_args[0][0]
    assert "/rates/reference-rates" in call_url
    assert "filter[code]=SOFR" in call_url
    assert "filter[currency]=USD" in call_url


def test_reference_rates_pagination(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_reference_rates(
        api_token="test1234567890123456", from_date="2024-01-01", to_date="2024-06-01",
        page_offset=10, page_limit=100,
    )

    call_url = mock_session.get.call_args[0][0]
    assert "filter[from]=2024-01-01" in call_url
    assert "filter[to]=2024-06-01" in call_url
    assert "page[offset]=10" in call_url
    assert "page[limit]=100" in call_url


def test_reference_rates_invalid_currency(mock_session):
    api = _make_api(mock_session)
    with pytest.raises(ValueError):
        api.get_reference_rates(api_token="test1234567890123456", currency="JPY")


def test_policy_rates_url(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_policy_rates(
        api_token="test1234567890123456", code="FEDFUNDS", country="USA",
        central_bank="Federal Reserve",
    )

    call_url = mock_session.get.call_args[0][0]
    assert "/rates/policy-rates" in call_url
    assert "filter[code]=FEDFUNDS" in call_url
    assert "filter[country]=USA" in call_url
    # filter values are URL-encoded (spaces -> %20)
    assert "filter[central_bank]=Federal%20Reserve" in call_url


def test_funding_stress_url(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_funding_stress(
        api_token="test1234567890123456", code="SOFR_OIS", from_date="2024-01-01",
        to_date="2024-06-01",
    )

    call_url = mock_session.get.call_args[0][0]
    assert "/spreads/funding-stress" in call_url
    assert "filter[code]=SOFR_OIS" in call_url
    assert "filter[from]=2024-01-01" in call_url
    assert "filter[to]=2024-06-01" in call_url


def test_funding_stress_no_pagination_kwargs(mock_session):
    # funding-stress has no pagination params; calling with only filters works
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_funding_stress(api_token="test1234567890123456", code="TED")

    call_url = mock_session.get.call_args[0][0]
    assert "page[offset]" not in call_url
    assert "page[limit]" not in call_url


def test_invalid_pagination(mock_session):
    api = _make_api(mock_session)
    with pytest.raises(ValueError):
        api.get_reference_rates(api_token="test1234567890123456", page_offset=-1)
    with pytest.raises(ValueError):
        api.get_policy_rates(api_token="test1234567890123456", page_limit=0)
