"""Unit tests for FundamentalDataAPI"""

import inspect

import pytest

from eodhd.apiclient import APIClient
from eodhd.APIs import FundamentalDataAPI


def test_get_fundamentals_data_empty_ticker():
    """Ticker is empty"""
    api = FundamentalDataAPI()
    with pytest.raises(ValueError) as execinfo:
        api.get_fundamentals_data(api_token="test", ticker="")
    assert str(execinfo.value) == "Ticker is empty. You need to add ticker to args"


def test_get_fundamentals_data_v1_1_empty_ticker():
    """Ticker is empty for v1.1"""
    api = FundamentalDataAPI()
    with pytest.raises(ValueError) as execinfo:
        api.get_fundamentals_data_v1_1(api_token="test", ticker="")
    assert str(execinfo.value) == "Ticker is empty. You need to add ticker to args"


def test_get_fundamentals_data_v1_1_method_exists():
    """v1.1 method exists on FundamentalDataAPI"""
    api = FundamentalDataAPI()
    assert hasattr(api, "get_fundamentals_data_v1_1")
    assert callable(api.get_fundamentals_data_v1_1)


def test_get_fundamentals_data_return_annotation_is_dict():
    """The /fundamentals endpoint returns a JSON object, so the client methods
    must be annotated -> dict, not -> list (see issue #71)."""
    client = APIClient.__new__(APIClient)
    assert inspect.signature(client.get_fundamentals_data).return_annotation is dict
    assert inspect.signature(client.get_fundamentals_data_v1_1).return_annotation is dict
