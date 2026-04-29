"""Tests for BulkFundamentalsAPI."""

import pytest
from unittest.mock import MagicMock

from eodhd.APIs.BulkFundamentalsAPI import BulkFundamentalsAPI


@pytest.fixture
def mock_session():
    return MagicMock()


def test_empty_exchange():
    api = BulkFundamentalsAPI()
    with pytest.raises(ValueError):
        api.get_bulk_fundamentals(api_token="test1234567890123456", exchange="")


def test_none_exchange():
    api = BulkFundamentalsAPI()
    with pytest.raises(ValueError):
        api.get_bulk_fundamentals(api_token="test1234567890123456", exchange=None)


def test_basic_call(mock_session):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = [{"Code": "AAPL", "General": {}}]
    mock_session.get.return_value = resp

    api = BulkFundamentalsAPI(session=mock_session)
    result = api.get_bulk_fundamentals(api_token="test1234567890123456", exchange="US")

    call_url = mock_session.get.call_args[0][0]
    assert "/bulk-fundamentals/US" in call_url
    assert len(result) == 1


def test_with_symbols_and_pagination(mock_session):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = []
    mock_session.get.return_value = resp

    api = BulkFundamentalsAPI(session=mock_session)
    api.get_bulk_fundamentals(
        api_token="test1234567890123456", exchange="US",
        symbols="AAPL,MSFT", offset=10, limit=5,
    )

    call_url = mock_session.get.call_args[0][0]
    assert "&symbols=AAPL,MSFT" in call_url
    assert "&offset=10" in call_url
    assert "&limit=5" in call_url
