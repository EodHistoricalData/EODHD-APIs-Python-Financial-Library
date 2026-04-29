"""Tests for SearchAPI."""

import pytest
from unittest.mock import MagicMock

from eodhd.APIs.SearchAPI import SearchAPI


@pytest.fixture
def mock_session():
    return MagicMock()


def _make_api(session):
    return SearchAPI(session=session)


def test_search_empty_query():
    api = SearchAPI()
    with pytest.raises(ValueError):
        api.search(api_token="test1234567890123456", query="")


def test_search_none_query():
    api = SearchAPI()
    with pytest.raises(ValueError):
        api.search(api_token="test1234567890123456", query=None)


def test_search_constructs_correct_url(mock_session):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = [{"Code": "AAPL", "Name": "Apple Inc"}]
    mock_session.get.return_value = resp

    api = _make_api(mock_session)
    result = api.search(api_token="test1234567890123456", query="Apple")

    call_url = mock_session.get.call_args[0][0]
    assert "/search/Apple" in call_url
    assert "api_token=test1234567890123456" in call_url
    assert result == [{"Code": "AAPL", "Name": "Apple Inc"}]


def test_search_with_limit(mock_session):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = [{"Code": "AAPL"}]
    mock_session.get.return_value = resp

    api = _make_api(mock_session)
    api.search(api_token="test1234567890123456", query="Apple", limit=5)

    call_url = mock_session.get.call_args[0][0]
    assert "&limit=5" in call_url
