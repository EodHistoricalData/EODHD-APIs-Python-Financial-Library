"""Unit tests for WebSocketClient"""

import pytest
from eodhd import WebSocketClient


def test_api_key_invalid():
    """API key is invalid"""
    with pytest.raises(ValueError) as execinfo:
        websocket = WebSocketClient(api_key="", endpoint="", symbols=[])
        assert isinstance(websocket, WebSocketClient)
    assert str(execinfo.value) == "API key is invalid"


def test_endpoint_invalid():
    """Endpoint is invalid"""
    with pytest.raises(ValueError) as execinfo:
        websocket = WebSocketClient(
            api_key="00000000000000000000000000000000", endpoint="", symbols=[]
        )
        assert isinstance(websocket, WebSocketClient)
    assert str(execinfo.value) == "Endpoint is invalid"


def test_symbols_empty():
    """No symbol(s) provided"""
    with pytest.raises(ValueError) as execinfo:
        websocket = WebSocketClient(
            api_key="00000000000000000000000000000000", endpoint="crypto", symbols=[]
        )
        assert isinstance(websocket, WebSocketClient)
    assert str(execinfo.value) == "No symbol(s) provided"


def test_symbols_invalid():
    """Symbol is invalid: !"""
    with pytest.raises(ValueError) as execinfo:
        websocket = WebSocketClient(
            api_key="00000000000000000000000000000000", endpoint="crypto", symbols=[""]
        )
        assert isinstance(websocket, WebSocketClient)
    assert str(execinfo.value) == "Symbol is invalid: "


def test_instantiate_success():
    """Instantiate success"""
    websocket = WebSocketClient(
        api_key="00000000000000000000000000000000", endpoint="crypto", symbols=["BTC-USD"]
    )
    assert isinstance(websocket, WebSocketClient)
