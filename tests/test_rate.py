"""Tests for RateLimitInfo and its wiring into BaseAPI / APIClient."""

import pytest
import requests
from unittest.mock import MagicMock, patch

from eodhd.rate import RateLimitInfo
from eodhd.APIs.BaseAPI import BaseAPI
from eodhd.apiclient import APIClient

# Captured before any test patches requests.Session, so `spec=` always sees the real class.
_RealSession = requests.Session


def test_from_headers_parses_pair():
    info = RateLimitInfo.from_headers({"X-RateLimit-Limit": "1200", "X-RateLimit-Remaining": "1199"})
    assert info.limit == 1200
    assert info.remaining == 1199


def test_from_headers_missing_pair_returns_none():
    assert RateLimitInfo.from_headers({}) is None
    assert RateLimitInfo.from_headers({"X-RateLimit-Limit": "1200"}) is None


def test_from_headers_malformed_returns_none():
    assert RateLimitInfo.from_headers({"X-RateLimit-Limit": "oops", "X-RateLimit-Remaining": "1199"}) is None


def test_default_rate_is_unknown():
    assert BaseAPI().rate.limit is None
    assert str(BaseAPI().rate) == "rate limit unknown"


def test_baseapi_tracks_rate_limit_on_session():
    mock_session = MagicMock(spec=requests.Session)
    resp = MagicMock()
    resp.status_code = 200
    resp.headers = {"X-RateLimit-Limit": "1200", "X-RateLimit-Remaining": "1199"}
    resp.json.return_value = {"ok": True}
    mock_session.get.return_value = resp

    api = BaseAPI(session=mock_session)
    api._rest_get_method(api_key="demo1234567890123456", endpoint="test")

    assert api.rate.limit == 1200
    assert api.rate.remaining == 1199
    # attached to the session, not the BaseAPI instance, so it is shared across
    # every endpoint wrapper built on top of the same session.
    assert mock_session._eodhd_rate_limit_info is api.rate


def test_baseapi_tracks_rate_limit_without_session():
    with patch("eodhd.APIs.BaseAPI.requests.get") as mock_get:
        resp = MagicMock()
        resp.status_code = 200
        resp.headers = {"X-RateLimit-Limit": "1200", "X-RateLimit-Remaining": "1199"}
        resp.json.return_value = {"ok": True}
        mock_get.return_value = resp

        api = BaseAPI()
        api._rest_get_method(api_key="demo1234567890123456", endpoint="test")

        assert api.rate.limit == 1200


def test_baseapi_tracks_rate_limit_on_error_response():
    mock_session = MagicMock(spec=requests.Session)
    resp = MagicMock()
    resp.status_code = 429
    resp.text = '{"message":"too many requests"}'
    resp.headers = {"X-RateLimit-Limit": "1200", "X-RateLimit-Remaining": "0"}
    resp.json.return_value = {"message": "too many requests"}
    mock_session.get.return_value = resp

    api = BaseAPI(session=mock_session)
    with pytest.raises(Exception):
        api._rest_get_method(api_key="demo1234567890123456", endpoint="test")

    assert api.rate.remaining == 0


def test_baseapi_tracks_rate_limit_on_post():
    mock_session = MagicMock(spec=requests.Session)
    resp = MagicMock()
    resp.status_code = 200
    resp.headers = {"X-RateLimit-Limit": "1200", "X-RateLimit-Remaining": "1150"}
    resp.json.return_value = {"ok": True}
    mock_session.post.return_value = resp

    api = BaseAPI(session=mock_session)
    api._rest_post_method(api_key="demo1234567890123456", endpoint="test", body={"a": 1})

    assert api.rate.remaining == 1150


def test_missing_headers_preserve_prior_snapshot():
    """A response without rate headers must not clear a previously known-good snapshot."""
    mock_session = MagicMock(spec=requests.Session)
    resp_with_headers = MagicMock()
    resp_with_headers.status_code = 200
    resp_with_headers.headers = {"X-RateLimit-Limit": "1200", "X-RateLimit-Remaining": "1199"}
    resp_with_headers.json.return_value = {"ok": True}

    resp_without_headers = MagicMock()
    resp_without_headers.status_code = 200
    resp_without_headers.headers = {}
    resp_without_headers.json.return_value = {"ok": True}

    mock_session.get.side_effect = [resp_with_headers, resp_without_headers]

    api = BaseAPI(session=mock_session)
    api._rest_get_method(api_key="demo1234567890123456", endpoint="test")
    assert api.rate.remaining == 1199

    api._rest_get_method(api_key="demo1234567890123456", endpoint="test")
    assert api.rate.remaining == 1199


def test_two_baseapi_instances_sharing_a_session_share_rate_state():
    """Endpoint wrapper objects share the APIClient's session, so they should
    all see the same up-to-date rate snapshot without stepping on each other."""
    mock_session = MagicMock(spec=requests.Session)
    resp = MagicMock()
    resp.status_code = 200
    resp.headers = {"X-RateLimit-Limit": "1200", "X-RateLimit-Remaining": "1199"}
    resp.json.return_value = {"ok": True}
    mock_session.get.return_value = resp

    api_a = BaseAPI(session=mock_session)
    api_b = BaseAPI(session=mock_session)
    api_a._rest_get_method(api_key="demo1234567890123456", endpoint="test")

    assert api_b.rate.remaining == 1199


def test_two_baseapi_instances_with_different_sessions_do_not_share_state():
    """No global singleton: separate sessions (separate APIClient instances /
    API keys) must not leak rate-limit state into each other."""
    session_a = MagicMock(spec=requests.Session)
    resp_a = MagicMock()
    resp_a.status_code = 200
    resp_a.headers = {"X-RateLimit-Limit": "1200", "X-RateLimit-Remaining": "1199"}
    resp_a.json.return_value = {"ok": True}
    session_a.get.return_value = resp_a

    session_b = MagicMock(spec=requests.Session)

    api_a = BaseAPI(session=session_a)
    api_b = BaseAPI(session=session_b)
    api_a._rest_get_method(api_key="demo1234567890123456", endpoint="test")

    assert api_a.rate.limit == 1200
    assert api_b.rate.limit is None


@pytest.fixture
def client():
    with patch("eodhd.apiclient.requests.Session") as MockSession:
        mock_session = MagicMock(spec=_RealSession)
        MockSession.return_value = mock_session
        c = APIClient(api_key="demo1234567890123456")
        c._mock_session = mock_session
        yield c


def test_apiclient_default_rate_is_unknown(client):
    assert client.rate.limit is None


def test_apiclient_rest_get_tracks_rate_limit(client):
    resp = MagicMock()
    resp.status_code = 200
    resp.headers = {"X-RateLimit-Limit": "1200", "X-RateLimit-Remaining": "1199"}
    resp.json.return_value = {"symbol": "AAPL", "close": 150}
    client._mock_session.get.return_value = resp

    client._rest_get(endpoint="test")

    assert client.rate.limit == 1200
    assert client.rate.remaining == 1199


def test_apiclient_rate_updates_across_successive_calls(client):
    resp1 = MagicMock()
    resp1.status_code = 200
    resp1.headers = {"X-RateLimit-Limit": "1200", "X-RateLimit-Remaining": "1199"}
    resp1.json.return_value = {"symbol": "AAPL", "close": 150}

    resp2 = MagicMock()
    resp2.status_code = 200
    resp2.headers = {"X-RateLimit-Limit": "1200", "X-RateLimit-Remaining": "1198"}
    resp2.json.return_value = {"symbol": "AAPL", "close": 151}

    client._mock_session.get.side_effect = [resp1, resp2]

    client._rest_get(endpoint="test")
    assert client.rate.remaining == 1199

    client._rest_get(endpoint="test")
    assert client.rate.remaining == 1198
