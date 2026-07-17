"""Tests for CreditSovereignRiskAPI."""

import pytest
from unittest.mock import MagicMock

from eodhd.APIs.CreditSovereignRiskAPI import CreditSovereignRiskAPI


@pytest.fixture
def mock_session():
    return MagicMock()


def _make_api(session):
    return CreditSovereignRiskAPI(session=session)


def _mock_response(session, data=None):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = data if data is not None else {"data": [], "meta": {}, "links": {}}
    session.get.return_value = resp


def test_risk_premium_url(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_sovereign_risk_premium(api_token="test1234567890123456")

    call_url = mock_session.get.call_args[0][0]
    assert "/credit-risk/sovereign/risk-premium" in call_url
    assert "api_token=test1234567890123456" in call_url


def test_risk_premium_filters(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_sovereign_risk_premium(
        api_token="test1234567890123456", country="USA", region="North America",
        as_of="2024-01-01", page_offset=0, page_limit=50,
    )

    call_url = mock_session.get.call_args[0][0]
    assert "filter[country]=USA" in call_url
    # filter values are URL-encoded (spaces -> %20)
    assert "filter[region]=North%20America" in call_url
    assert "filter[as_of]=2024-01-01" in call_url
    assert "page[offset]=0" in call_url
    assert "page[limit]=50" in call_url


def test_credit_ratings_url(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_sovereign_credit_ratings(api_token="test1234567890123456", country="DEU")

    call_url = mock_session.get.call_args[0][0]
    assert "/credit-risk/sovereign/credit-ratings" in call_url
    assert "filter[country]=DEU" in call_url


def test_cds_spreads_url(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_sovereign_cds_spreads(api_token="test1234567890123456", as_of="2024-06-01")

    call_url = mock_session.get.call_args[0][0]
    assert "/credit-risk/sovereign/cds-spreads" in call_url
    assert "filter[as_of]=2024-06-01" in call_url


def test_default_spreads_url(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_sovereign_default_spreads(api_token="test1234567890123456", rating="Aaa")

    call_url = mock_session.get.call_args[0][0]
    assert "/credit-risk/sovereign/default-spreads" in call_url
    assert "filter[rating]=Aaa" in call_url


def test_corporate_cmdi_url(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_corporate_cmdi(api_token="test1234567890123456", from_date="2024-01-01", to_date="2024-12-31")

    call_url = mock_session.get.call_args[0][0]
    assert "/credit-risk/corporate/cmdi" in call_url
    assert "filter[from]=2024-01-01" in call_url
    assert "filter[to]=2024-12-31" in call_url


def test_hqm_yields_url(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_corporate_hqm_yields(api_token="test1234567890123456", tenor="10", type="par")

    call_url = mock_session.get.call_args[0][0]
    assert "/credit-risk/corporate/hqm-yields" in call_url
    assert "filter[tenor]=10" in call_url
    assert "filter[type]=par" in call_url


def test_hqm_yields_invalid_type(mock_session):
    api = _make_api(mock_session)
    with pytest.raises(ValueError):
        api.get_corporate_hqm_yields(api_token="test1234567890123456", type="bad")


def test_hqm_yields_csv_type(mock_session):
    # server uses CsvIn(['spot','par']) -> a comma-separated combo is valid
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_corporate_hqm_yields(api_token="test1234567890123456", type="Spot, Par")

    call_url = mock_session.get.call_args[0][0]
    # normalised to lowercase, comma-joined, URL-encoded (',' -> %2C)
    assert "filter[type]=spot%2Cpar" in call_url


def test_hqm_yields_partial_invalid_csv_type(mock_session):
    api = _make_api(mock_session)
    with pytest.raises(ValueError):
        api.get_corporate_hqm_yields(api_token="test1234567890123456", type="spot,bad")


def test_cds_market_aggregates_url(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_cds_market_aggregates(
        api_token="test1234567890123456", metric="gross_notional", dimension="grade",
        value="Investment Grade", region="North America",
    )

    call_url = mock_session.get.call_args[0][0]
    assert "/credit-risk/cds-market/aggregates" in call_url
    assert "filter[metric]=gross_notional" in call_url
    assert "filter[dimension]=grade" in call_url
    # value and region filters are supported (verified vs prometheus-web)
    assert "filter[value]=Investment%20Grade" in call_url
    assert "filter[region]=North%20America" in call_url


def test_invalid_pagination(mock_session):
    api = _make_api(mock_session)
    with pytest.raises(ValueError):
        api.get_sovereign_risk_premium(api_token="test1234567890123456", page_offset=-1)
    with pytest.raises(ValueError):
        api.get_sovereign_risk_premium(api_token="test1234567890123456", page_limit=0)


def test_filter_values_are_url_encoded(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    # a value with a space and an ampersand must not break the query string
    api.get_sovereign_risk_premium(api_token="test1234567890123456", region="A & B")

    call_url = mock_session.get.call_args[0][0]
    assert "filter[region]=A%20%26%20B" in call_url
    # the raw ampersand must not appear inside the filter value
    assert "filter[region]=A & B" not in call_url
