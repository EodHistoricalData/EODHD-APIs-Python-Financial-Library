"""Tests for BaseAPI session, timeout, and error raising."""

import pytest
from unittest.mock import MagicMock, patch
from requests import ConnectionError as RequestsConnectionError, Timeout as RequestsTimeout

from eodhd.APIs.BaseAPI import BaseAPI
from eodhd.errors import EODHDHTTPError, EODHDConnectionError, EODHDTimeoutError


@pytest.fixture
def mock_session():
    return MagicMock()


def test_uses_session_when_provided(mock_session):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = [{"a": 1}]
    mock_session.get.return_value = resp

    api = BaseAPI(session=mock_session, timeout=(3.0, 10.0))
    result = api._rest_get_method(api_key="demo1234567890123456", endpoint="test", uri="X")

    mock_session.get.assert_called_once()
    assert result == [{"a": 1}]


def test_raises_http_error_on_4xx(mock_session):
    resp = MagicMock()
    resp.status_code = 404
    resp.text = '{"message":"not found"}'
    resp.json.return_value = {"message": "not found"}
    mock_session.get.return_value = resp

    api = BaseAPI(session=mock_session)
    with pytest.raises(EODHDHTTPError) as exc_info:
        api._rest_get_method(api_key="demo1234567890123456", endpoint="test")

    assert exc_info.value.status_code == 404


def test_raises_http_error_on_5xx(mock_session):
    resp = MagicMock()
    resp.status_code = 500
    resp.text = "Internal Server Error"
    resp.json.side_effect = ValueError("no json")
    mock_session.get.return_value = resp

    api = BaseAPI(session=mock_session)
    with pytest.raises(EODHDHTTPError) as exc_info:
        api._rest_get_method(api_key="demo1234567890123456", endpoint="test")

    assert exc_info.value.status_code == 500


def test_raises_connection_error(mock_session):
    mock_session.get.side_effect = RequestsConnectionError("refused")

    api = BaseAPI(session=mock_session)
    with pytest.raises(EODHDConnectionError):
        api._rest_get_method(api_key="demo1234567890123456", endpoint="test")


def test_raises_timeout_error(mock_session):
    mock_session.get.side_effect = RequestsTimeout("timed out")

    api = BaseAPI(session=mock_session)
    with pytest.raises(EODHDTimeoutError):
        api._rest_get_method(api_key="demo1234567890123456", endpoint="test")


def test_default_timeout():
    api = BaseAPI()
    assert api._timeout == (5.0, 30.0)


def test_falls_back_to_bare_requests_without_session():
    with patch("eodhd.APIs.BaseAPI.requests.get") as mock_get:
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {"ok": True}
        mock_get.return_value = resp

        api = BaseAPI()
        result = api._rest_get_method(api_key="demo1234567890123456", endpoint="test")

        mock_get.assert_called_once()
        assert result == {"ok": True}
