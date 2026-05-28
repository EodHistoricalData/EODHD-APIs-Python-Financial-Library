"""Tests for SecFilingsAPI — Insider Transactions v2 (SEC Form 4)."""

import pytest
from unittest.mock import MagicMock

from eodhd.APIs.SecFilingsAPI import SecFilingsAPI


@pytest.fixture
def mock_session():
    return MagicMock()


def _make_api(session):
    return SecFilingsAPI(session=session)


def _mock_response(session, data=None):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = data or {"data": [], "meta": {"total": 0, "page": {"offset": 0, "limit": 20}}, "links": {"next": None}}
    session.get.return_value = resp


# --- URL construction ---

def test_form4_constructs_correct_url(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_sec_filings_form4(api_token="test1234567890123456", symbol="AAPL")

    call_url = mock_session.get.call_args[0][0]
    assert "/sec-filings/AAPL/form4" in call_url
    assert "api_token=test1234567890123456" in call_url


def test_form4_dotted_symbol(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_sec_filings_form4(api_token="x", symbol="AAPL.US")

    call_url = mock_session.get.call_args[0][0]
    assert "/sec-filings/AAPL.US/form4" in call_url


def test_form4_pagination_params(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_sec_filings_form4(api_token="x", symbol="AAPL", page_offset=20, page_limit=50)

    call_url = mock_session.get.call_args[0][0]
    assert "page[offset]=20" in call_url
    assert "page[limit]=50" in call_url


def test_form4_omits_pagination_when_none(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_sec_filings_form4(api_token="x", symbol="AAPL")

    call_url = mock_session.get.call_args[0][0]
    assert "page[offset]" not in call_url
    assert "page[limit]" not in call_url


# --- Response handling ---

def test_form4_returns_dict(mock_session):
    payload = {
        "data": [
            {
                "accession_number": "0000320193-23-000077",
                "filed_at": "2023-08-04",
                "period_of_report": "2023-08-02",
                "non_derivative": [],
                "derivative": [],
                "footnotes": [],
            }
        ],
        "meta": {"total": 594, "page": {"offset": 0, "limit": 20}},
        "links": {"next": "https://eodhd.com/api/sec-filings/AAPL/form4?page[offset]=20&page[limit]=20"},
    }
    _mock_response(mock_session, data=payload)
    api = _make_api(mock_session)
    result = api.get_sec_filings_form4(api_token="x", symbol="AAPL")

    assert isinstance(result, dict)
    assert "data" in result
    assert "meta" in result
    assert "links" in result
    assert result["meta"]["total"] == 594
