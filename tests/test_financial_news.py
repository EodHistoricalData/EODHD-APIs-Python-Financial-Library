"""Tests for the News API `direction` parameter (GET /api/news)."""

from urllib.parse import parse_qs, urlsplit

import pytest
from unittest.mock import MagicMock

from eodhd import APIClient


@pytest.fixture
def client():
    api = APIClient(api_key="test1234567890123456")
    session = MagicMock()
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = []
    session.get.return_value = resp
    api._session = session
    return api


def _split(session):
    url = session.get.call_args[0][0]
    parts = urlsplit(url)
    return parts.path, parse_qs(parts.query, keep_blank_values=True)


def test_financial_news_direction_forwarded(client):
    client.financial_news(s="AAPL.US", from_date="2026-10-01", to_date="2026-10-15",
                          limit=100, offset=9900, direction=1)
    path, qs = _split(client._session)
    assert path.rstrip("/").endswith("/news")
    assert qs["direction"] == ["1"]
    assert qs["s"] == ["AAPL.US"]
    assert qs["from"] == ["2026-10-01"]
    assert qs["to"] == ["2026-10-15"]
    assert qs["limit"] == ["100"]
    assert qs["offset"] == ["9900"]


def test_financial_news_direction_zero_forwarded(client):
    client.financial_news(s="AAPL.US", direction=0)
    _, qs = _split(client._session)
    assert qs["direction"] == ["0"]


def test_financial_news_direction_absent_when_none(client):
    client.financial_news(s="AAPL.US", limit=10)
    _, qs = _split(client._session)
    assert "direction" not in qs


def test_financial_news_requires_s_or_t(client):
    with pytest.raises(ValueError):
        client.financial_news(direction=1)
