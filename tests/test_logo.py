"""Tests for LogoAPI."""

import pytest
from unittest.mock import MagicMock

from eodhd.APIs.LogoAPI import LogoAPI


@pytest.fixture
def mock_session():
    return MagicMock()


def test_get_logo_empty_symbol():
    api = LogoAPI()
    with pytest.raises(ValueError):
        api.get_logo(api_token="test1234567890123456", symbol="")


def test_get_logo_svg_empty_symbol():
    api = LogoAPI()
    with pytest.raises(ValueError):
        api.get_logo_svg(api_token="test1234567890123456", symbol="")


def test_get_logo_returns_bytes(mock_session):
    resp = MagicMock()
    resp.status_code = 200
    resp.content = b"\x89PNG\r\n\x1a\n"
    mock_session.get.return_value = resp

    api = LogoAPI(session=mock_session)
    result = api.get_logo(api_token="test1234567890123456", symbol="AAPL.US")

    call_url = mock_session.get.call_args[0][0]
    assert "/logo/AAPL.US" in call_url
    assert result == b"\x89PNG\r\n\x1a\n"


def test_get_logo_svg_returns_bytes(mock_session):
    resp = MagicMock()
    resp.status_code = 200
    resp.content = b"<svg></svg>"
    mock_session.get.return_value = resp

    api = LogoAPI(session=mock_session)
    result = api.get_logo_svg(api_token="test1234567890123456", symbol="AAPL.US")

    call_url = mock_session.get.call_args[0][0]
    assert "/logo-svg/AAPL.US" in call_url
    assert result == b"<svg></svg>"
