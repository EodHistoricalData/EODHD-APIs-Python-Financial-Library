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
