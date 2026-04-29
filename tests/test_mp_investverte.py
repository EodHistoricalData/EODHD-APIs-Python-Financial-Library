"""Tests for MPInvestVerteAPI."""

import pytest
from unittest.mock import MagicMock

from eodhd.APIs.MPInvestVerteAPI import MPInvestVerteAPI


@pytest.fixture
def mock_session():
    return MagicMock()


def _mock_resp(session, data=None):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = data or [{"symbol": "AAPL.US"}]
    session.get.return_value = resp


def test_get_companies(mock_session):
    _mock_resp(mock_session)
    api = MPInvestVerteAPI(session=mock_session)
    result = api.get_companies(api_token="test1234567890123456")
    assert "/mp/investverte/companies" in mock_session.get.call_args[0][0]


def test_get_countries(mock_session):
    _mock_resp(mock_session)
    api = MPInvestVerteAPI(session=mock_session)
    api.get_countries(api_token="test1234567890123456")
    assert "/mp/investverte/countries" in mock_session.get.call_args[0][0]


def test_get_sectors(mock_session):
    _mock_resp(mock_session)
    api = MPInvestVerteAPI(session=mock_session)
    api.get_sectors(api_token="test1234567890123456")
    assert "/mp/investverte/sectors" in mock_session.get.call_args[0][0]


def test_get_esg(mock_session):
    _mock_resp(mock_session)
    api = MPInvestVerteAPI(session=mock_session)
    api.get_esg(api_token="test1234567890123456", symbol="AAPL.US")
    assert "/mp/investverte/esg/AAPL.US" in mock_session.get.call_args[0][0]


def test_get_esg_empty_symbol():
    api = MPInvestVerteAPI()
    with pytest.raises(ValueError):
        api.get_esg(api_token="test1234567890123456", symbol="")


def test_get_country(mock_session):
    _mock_resp(mock_session)
    api = MPInvestVerteAPI(session=mock_session)
    api.get_country(api_token="test1234567890123456", symbol="US")
    assert "/mp/investverte/country/US" in mock_session.get.call_args[0][0]


def test_get_sector(mock_session):
    _mock_resp(mock_session)
    api = MPInvestVerteAPI(session=mock_session)
    api.get_sector(api_token="test1234567890123456", symbol="Technology")
    assert "/mp/investverte/sector/Technology" in mock_session.get.call_args[0][0]
