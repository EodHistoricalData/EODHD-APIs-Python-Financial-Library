"""Tests for UserAPI."""

import pytest
from unittest.mock import MagicMock

from eodhd.APIs.UserAPI import UserAPI


@pytest.fixture
def mock_session():
    return MagicMock()


def test_get_user_info(mock_session):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"name": "Test User", "subscriptionType": "allInOne"}
    mock_session.get.return_value = resp

    api = UserAPI(session=mock_session)
    result = api.get_user_info(api_token="test1234567890123456")

    call_url = mock_session.get.call_args[0][0]
    assert "/user/" in call_url
    assert result["name"] == "Test User"


def test_get_user_info_method_exists():
    api = UserAPI()
    assert hasattr(api, "get_user_info")
    assert callable(api.get_user_info)
