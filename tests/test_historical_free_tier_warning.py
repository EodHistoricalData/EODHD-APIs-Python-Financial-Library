"""Regression test for issue #66.

A free API key requesting more than one year of historical data gets an extra
'warning' column appended to the response. The fixed-width column relabelling in
get_historical_data then raised a confusing pandas "Length mismatch" error.
The warning must be surfaced and the column dropped instead.
"""

from unittest.mock import patch

import pandas as pd
import pytest

from eodhd.apiclient import APIClient


@pytest.fixture
def client():
    with patch("eodhd.apiclient.requests.Session"):
        yield APIClient(api_key="demo1234567890123456")


def _free_tier_eod_frame():
    """Mimics the EOD response a free key returns for a >1y request: a trailing
    'warning' column that is NaN on every row except the last."""
    return pd.DataFrame(
        {
            "date": ["2025-04-22", "2025-04-23"],
            "open": [14347.8896, 14404.0498],
            "high": [14414.0996, 14645.2598],
            "low": [14293.0303, 14403.5498],
            "close": [14404.0498, 14549.4199],
            "adjusted_close": [14404.0498, 14549.4199],
            "volume": [0, 0],
            "warning": [None, "Data is limited by one year as you have free subscription."],
        }
    )


def test_free_tier_warning_does_not_raise(client):
    with patch.object(client, "_rest_get", return_value=_free_tier_eod_frame()):
        df = client.get_historical_data("BUKAC.INDX", interval="d", results=10000)

    # Previously raised: ValueError: Length mismatch: Expected axis has 9 elements...
    assert "warning" not in df.columns
    assert list(df.columns) == [
        "symbol",
        "interval",
        "open",
        "high",
        "low",
        "close",
        "adjusted_close",
        "volume",
    ]
    assert len(df) == 2


def test_free_tier_warning_is_logged(client):
    with patch.object(client, "_rest_get", return_value=_free_tier_eod_frame()):
        with patch.object(client.console, "log") as mock_log:
            client.get_historical_data("BUKAC.INDX", interval="d", results=10000)

    logged = " ".join(str(a) for call in mock_log.call_args_list for a in call.args)
    assert "warning" in logged.lower()


def _free_tier_intraday_frame():
    """Mimics the intraday response a free key returns for an over-range request:
    the same trailing 'warning' column, on the intraday column shape
    (timestamp/gmtoffset/datetime/OHLC/volume). Column order matters — the client
    relabels positionally after dropping 'datetime'."""
    return pd.DataFrame(
        {
            "timestamp": [1745312400, 1745316000],
            "gmtoffset": [0, 0],
            "datetime": ["2025-04-22 09:00:00", "2025-04-22 10:00:00"],
            "open": [14347.8896, 14404.0498],
            "high": [14414.0996, 14645.2598],
            "low": [14293.0303, 14403.5498],
            "close": [14404.0498, 14549.4199],
            "volume": [0, 0],
            "warning": [None, "Data is limited by one year as you have free subscription."],
        }
    )


def test_free_tier_warning_intraday_does_not_raise(client):
    """The fix is applied in BOTH the EOD and the intraday branch of
    get_historical_data — guard the intraday branch too (#66)."""
    with patch.object(client, "_rest_get", return_value=_free_tier_intraday_frame()):
        df = client.get_historical_data("BUKAC.INDX", interval="1h", results=10000)

    assert "warning" not in df.columns
    assert list(df.columns) == [
        "epoch",
        "gmtoffset",
        "symbol",
        "interval",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]
    assert len(df) == 2


def _warning_only_frame():
    """Degenerate free-tier response: a single 'warning' row and no market data
    at all. After dropping the column the frame must be treated as empty rather
    than crashing on a missing date/OHLCV column."""
    return pd.DataFrame({"warning": ["Data is limited by one year as you have free subscription."]})


def test_free_tier_warning_only_response_returns_empty(client):
    with patch.object(client, "_rest_get", return_value=_warning_only_frame()):
        df = client.get_historical_data("BUKAC.INDX", interval="d", results=10000)

    # No crash; empty result with the standard EOD column set.
    assert "warning" not in df.columns
    assert len(df) == 0
