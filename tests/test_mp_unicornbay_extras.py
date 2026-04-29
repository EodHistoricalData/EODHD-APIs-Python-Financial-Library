"""Tests for MPUnicornbayExtrasAPI."""

import pytest
from unittest.mock import MagicMock

from eodhd.APIs.MPUnicornbayExtrasAPI import MPUnicornbayExtrasAPI


@pytest.fixture
def mock_session():
    return MagicMock()


def test_get_tickdata_empty_symbol():
    api = MPUnicornbayExtrasAPI()
    with pytest.raises(ValueError):
        api.get_tickdata(api_token="test1234567890123456", symbol="")


def test_get_tickdata_url(mock_session):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"data": [], "meta": {}}
    mock_session.get.return_value = resp

    api = MPUnicornbayExtrasAPI(session=mock_session)
    api.get_tickdata(api_token="test1234567890123456", symbol="AAPL.US")

    call_url = mock_session.get.call_args[0][0]
    assert "/mp/unicornbay/tickdata/ticks" in call_url
    assert "&symbol=AAPL.US" in call_url


def test_get_tickdata_with_params(mock_session):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"data": []}
    mock_session.get.return_value = resp

    api = MPUnicornbayExtrasAPI(session=mock_session)
    api.get_tickdata(
        api_token="test1234567890123456", symbol="AAPL.US",
        from_timestamp=1700000000, to_timestamp=1700100000,
        page_offset=0, page_limit=100,
    )

    call_url = mock_session.get.call_args[0][0]
    assert "&from=1700000000" in call_url
    assert "&to=1700100000" in call_url


def test_get_logo_empty_symbol():
    api = MPUnicornbayExtrasAPI()
    with pytest.raises(ValueError):
        api.get_logo(api_token="test1234567890123456", symbol="")


def test_get_logo_returns_bytes(mock_session):
    resp = MagicMock()
    resp.status_code = 200
    resp.content = b"\x89PNG"
    mock_session.get.return_value = resp

    api = MPUnicornbayExtrasAPI(session=mock_session)
    result = api.get_logo(api_token="test1234567890123456", symbol="AAPL.US")

    assert "/mp/unicornbay/logo/AAPL.US" in mock_session.get.call_args[0][0]
    assert result == b"\x89PNG"
