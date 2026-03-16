"""Tests for APIClient._rest_get error propagation."""

import pytest
from unittest.mock import MagicMock, patch
from requests import ConnectionError as RequestsConnectionError, Timeout as RequestsTimeout

from eodhd.apiclient import APIClient
from eodhd.errors import EODHDHTTPError, EODHDConnectionError, EODHDTimeoutError


@pytest.fixture
def client():
    with patch("eodhd.apiclient.requests.Session") as MockSession:
        mock_session = MagicMock()
        MockSession.return_value = mock_session
        c = APIClient(api_key="demo1234567890123456")
        c._mock_session = mock_session
        yield c


def test_rest_get_raises_http_error(client):
    resp = MagicMock()
    resp.status_code = 403
    resp.text = '{"message":"forbidden"}'
    resp.json.return_value = {"message": "forbidden"}
    client._mock_session.get.return_value = resp

    with pytest.raises(EODHDHTTPError) as exc_info:
        client._rest_get(endpoint="test")

    assert exc_info.value.status_code == 403


def test_rest_get_raises_connection_error(client):
    client._mock_session.get.side_effect = RequestsConnectionError("refused")

    with pytest.raises(EODHDConnectionError):
        client._rest_get(endpoint="test")


def test_rest_get_raises_timeout_error(client):
    client._mock_session.get.side_effect = RequestsTimeout("timed out")

    with pytest.raises(EODHDTimeoutError):
        client._rest_get(endpoint="test")


def test_rest_get_success_list(client):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = [{"symbol": "AAPL", "close": 150}]
    client._mock_session.get.return_value = resp

    df = client._rest_get(endpoint="test")
    assert len(df) == 1
    assert "symbol" in df.columns


def test_rest_get_success_dict(client):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"symbol": "AAPL", "close": 150}
    client._mock_session.get.return_value = resp

    df = client._rest_get(endpoint="test")
    assert len(df) == 1


def test_context_manager():
    with patch("eodhd.apiclient.requests.Session") as MockSession:
        mock_session = MagicMock()
        MockSession.return_value = mock_session

        with APIClient(api_key="demo1234567890123456") as client:
            assert client is not None

        mock_session.close.assert_called_once()


def test_custom_timeout():
    with patch("eodhd.apiclient.requests.Session"):
        client = APIClient(api_key="demo1234567890123456", timeout=(1.0, 5.0))
        assert client._timeout == (1.0, 5.0)
