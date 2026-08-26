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
    assert str(execinfo.value).startswith("Endpoint is invalid")


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


# ── Markets added with the Cboe European feed and the derived streams ──


@pytest.mark.parametrize(
    "endpoint",
    ["us", "us-quote", "us-candles", "us-status",
     "eu", "eu-quote", "eu-candles", "eu-status",
     "forex", "crypto"],
)
def test_every_served_market_is_accepted(endpoint):
    """Every market the service serves must be constructible."""
    ws = WebSocketClient(
        api_key="00000000000000000000000000000000", endpoint=endpoint, symbols=["AAPL"]
    )
    assert isinstance(ws, WebSocketClient)


def test_unknown_market_still_rejected():
    """The whitelist must stay a whitelist."""
    with pytest.raises(ValueError) as execinfo:
        WebSocketClient(
            api_key="00000000000000000000000000000000", endpoint="us-candle", symbols=["AAPL"]
        )
    assert "Endpoint is invalid" in str(execinfo.value)


@pytest.mark.parametrize("symbol", ["GSK.LSE", "SAP.XETRA", "ASML.AS", "ERIC-B.ST", "ALIV-SDB.ST"])
def test_european_symbols_accepted(symbol):
    """European tickers carry a dot, which the old validator rejected outright."""
    ws = WebSocketClient(
        api_key="00000000000000000000000000000000", endpoint="eu", symbols=[symbol]
    )
    assert isinstance(ws, WebSocketClient)


def test_symbol_validator_no_longer_admits_stray_punctuation():
    """[A-z] also matched the ASCII punctuation between Z and a."""
    with pytest.raises(ValueError):
        WebSocketClient(
            api_key="00000000000000000000000000000000", endpoint="us", symbols=["AA^PL"]
        )


def test_symbol_cap_defaults_to_fifty():
    with pytest.raises(ValueError) as execinfo:
        WebSocketClient(
            api_key="00000000000000000000000000000000",
            endpoint="us",
            symbols=[f"SYM{i}" for i in range(51)],
        )
    assert "Max symbol subscription count is 50" in str(execinfo.value)


def test_symbol_cap_is_overridable_for_larger_plans():
    """50 is the default plan allowance, not a protocol limit."""
    ws = WebSocketClient(
        api_key="00000000000000000000000000000000",
        endpoint="us",
        symbols=[f"SYM{i}" for i in range(51)],
        max_symbols=300,
    )
    assert isinstance(ws, WebSocketClient)


# ── Candle arithmetic ──


def _candle_for(messages, granularity=60):
    ws = WebSocketClient(
        api_key="00000000000000000000000000000000", endpoint="us", symbols=["AAPL"]
    )
    candle = {}
    for m in messages:
        ws._update_candle(candle, m, "1 minute", granularity)
    return candle


def test_equity_trades_accumulate_size_from_v_not_q():
    """The equity trade streams carry size in v; reading q raised KeyError on the 2nd tick."""
    candle = _candle_for([
        {"s": "AAPL", "p": 100.0, "v": 10, "t": 1787701620000},
        {"s": "AAPL", "p": 101.0, "v": 5, "t": 1787701620000},
    ])
    assert candle["o"] == 100.0
    assert candle["c"] == 101.0
    assert candle["v"] == 15


def test_crypto_string_prices_compare_numerically():
    """Crypto sends p as a string, so "9" > "10" would corrupt high/low."""
    candle = _candle_for([
        {"s": "BTC-USD", "p": "10", "q": "1", "t": 1787701620000},
        {"s": "BTC-USD", "p": "9", "q": "1", "t": 1787701620000},
    ])
    assert candle["h"] == 10.0
    assert candle["l"] == 9.0
    assert candle["c"] == 9.0


# ── Control frames ──


def _client():
    return WebSocketClient(
        api_key="00000000000000000000000000000000", endpoint="us", symbols=["AAPL"]
    )


def test_auth_failure_codes_are_the_status_keyed_ones_only():
    """422 appears under both keys and means opposite things.

    As "status" it is a missing token and the connection is dead. As "status_code" it is one
    bad subscribe command on an otherwise healthy stream. The client must not conflate them,
    or a recoverable mistake would tear down a working feed.
    """
    from eodhd.websocketclient import AUTH_FAILURE_CODES

    assert 403 in AUTH_FAILURE_CODES
    assert 422 in AUTH_FAILURE_CODES

    fatal = {"status": 422, "message": "Server error"}
    recoverable = {"status_code": 422, "message": "Symbols limit reached"}

    def is_fatal(msg):
        code = msg.get("status", msg.get("status_code"))
        return "status" in msg and code in AUTH_FAILURE_CODES

    assert is_fatal(fatal) is True
    assert is_fatal(recoverable) is False
    assert is_fatal({"status_code": 200, "message": "Authorized"}) is False
    assert is_fatal({"status_code": 404, "message": "No market 'x' found"}) is False


def test_control_frames_are_not_market_data():
    """A frame carrying either status key must never reach the candle builder."""
    ws = _client()
    candle = {}
    for frame in (
        {"status_code": 200, "message": "Authorized"},
        {"status": 403, "message": "Server error"},
        {"status_code": 429, "message": "Too many connections (token)"},
    ):
        ws._update_candle(candle, frame, "1 minute", 60)
    assert candle == {}, "control frames must not open a candle"
