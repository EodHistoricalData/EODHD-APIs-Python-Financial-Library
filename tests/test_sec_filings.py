"""Tests for SecFilingsAPI (SEC filings: overview, 10-K, 10-Q, 8-K)."""

import pytest
from unittest.mock import MagicMock

from eodhd.APIs.SecFilings import SecFilingsAPI


@pytest.fixture
def mock_session():
    return MagicMock()


def _make_api(session):
    return SecFilingsAPI(session=session)


def _mock_response(session, data=None):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = data if data is not None else {"data": [], "meta": {}, "links": {}}
    session.get.return_value = resp


TOKEN = "test1234567890123456"


# ------------------------------------------------------------------- overview

def test_overview_url(mock_session):
    _mock_response(mock_session, {"data": {}, "meta": {}, "links": {}})
    api = _make_api(mock_session)
    api.get_sec_filings_overview(api_token=TOKEN, symbol="AAPL.US")

    call_url = mock_session.get.call_args[0][0]
    assert "/sec-filings/AAPL.US?" in call_url
    assert "api_token=" + TOKEN in call_url
    # overview is parameterless: no pagination params
    assert "page[offset]" not in call_url
    assert "page[limit]" not in call_url


def test_overview_symbol_stripped(mock_session):
    _mock_response(mock_session, {"data": {}, "meta": {}, "links": {}})
    api = _make_api(mock_session)
    api.get_sec_filings_overview(api_token=TOKEN, symbol="  MSFT.US  ")

    call_url = mock_session.get.call_args[0][0]
    assert "/sec-filings/MSFT.US?" in call_url


def test_overview_missing_symbol(mock_session):
    api = _make_api(mock_session)
    with pytest.raises(ValueError):
        api.get_sec_filings_overview(api_token=TOKEN, symbol="")


def test_overview_none_symbol(mock_session):
    api = _make_api(mock_session)
    with pytest.raises(ValueError):
        api.get_sec_filings_overview(api_token=TOKEN, symbol=None)


# ------------------------------------------------------------------------ 10-K

def test_10k_url_and_defaults(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_sec_filings_10k(api_token=TOKEN, symbol="AAPL.US")

    call_url = mock_session.get.call_args[0][0]
    assert "/sec-filings/AAPL.US/10k" in call_url
    assert "page[offset]=0" in call_url
    assert "page[limit]=20" in call_url


def test_10k_custom_pagination(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_sec_filings_10k(api_token=TOKEN, symbol="AAPL.US", page_offset=40, page_limit=100)

    call_url = mock_session.get.call_args[0][0]
    assert "page[offset]=40" in call_url
    assert "page[limit]=100" in call_url


def test_10k_missing_symbol(mock_session):
    api = _make_api(mock_session)
    with pytest.raises(ValueError):
        api.get_sec_filings_10k(api_token=TOKEN, symbol="")


# ------------------------------------------------------------------------ 10-Q

def test_10q_url_and_defaults(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_sec_filings_10q(api_token=TOKEN, symbol="AAPL.US")

    call_url = mock_session.get.call_args[0][0]
    assert "/sec-filings/AAPL.US/10q" in call_url
    assert "page[offset]=0" in call_url
    assert "page[limit]=20" in call_url


def test_10q_custom_pagination(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_sec_filings_10q(api_token=TOKEN, symbol="MSFT.US", page_offset=20, page_limit=50)

    call_url = mock_session.get.call_args[0][0]
    assert "/sec-filings/MSFT.US/10q" in call_url
    assert "page[offset]=20" in call_url
    assert "page[limit]=50" in call_url


# ------------------------------------------------------------------------- 8-K

def test_8k_url_and_defaults(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_sec_filings_8k(api_token=TOKEN, symbol="AAPL.US")

    call_url = mock_session.get.call_args[0][0]
    assert "/sec-filings/AAPL.US/8k" in call_url
    assert "page[offset]=0" in call_url
    assert "page[limit]=20" in call_url


def test_8k_custom_pagination(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_sec_filings_8k(api_token=TOKEN, symbol="TSLA.US", page_offset=10, page_limit=5)

    call_url = mock_session.get.call_args[0][0]
    assert "/sec-filings/TSLA.US/8k" in call_url
    assert "page[offset]=10" in call_url
    assert "page[limit]=5" in call_url


# --------------------------------------------------------------- pagination bounds

def test_pagination_limit_too_high(mock_session):
    api = _make_api(mock_session)
    with pytest.raises(ValueError):
        api.get_sec_filings_10k(api_token=TOKEN, symbol="AAPL.US", page_limit=101)


def test_pagination_negative_offset(mock_session):
    api = _make_api(mock_session)
    with pytest.raises(ValueError):
        api.get_sec_filings_10q(api_token=TOKEN, symbol="AAPL.US", page_offset=-1)


def test_pagination_limit_zero(mock_session):
    api = _make_api(mock_session)
    with pytest.raises(ValueError):
        api.get_sec_filings_8k(api_token=TOKEN, symbol="AAPL.US", page_limit=0)


# --------------------------------------------------- apiclient facade delegation

def test_apiclient_facade_delegates():
    from eodhd.apiclient import APIClient

    client = APIClient(TOKEN)
    session = MagicMock()
    _mock_response(session)
    client._session = session

    client.get_sec_filings_overview("AAPL.US")
    assert "/sec-filings/AAPL.US?" in session.get.call_args[0][0]

    client.get_sec_filings_10k("AAPL.US", page_offset=0, page_limit=20)
    assert "/sec-filings/AAPL.US/10k" in session.get.call_args[0][0]

    client.get_sec_filings_10q("AAPL.US")
    assert "/sec-filings/AAPL.US/10q" in session.get.call_args[0][0]

    client.get_sec_filings_8k("AAPL.US")
    assert "/sec-filings/AAPL.US/8k" in session.get.call_args[0][0]
