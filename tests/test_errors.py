"""Tests for eodhd.errors hierarchy."""

import pytest
from eodhd.errors import EODHDError, EODHDHTTPError, EODHDConnectionError, EODHDTimeoutError


def test_hierarchy():
    assert issubclass(EODHDHTTPError, EODHDError)
    assert issubclass(EODHDConnectionError, EODHDError)
    assert issubclass(EODHDTimeoutError, EODHDError)


def test_http_error_attributes():
    err = EODHDHTTPError(status_code=404, response_body='{"message":"not found"}', message="Not Found")
    assert err.status_code == 404
    assert err.response_body == '{"message":"not found"}'
    assert err.message == "Not Found"
    assert str(err) == "Not Found"


def test_http_error_default_message():
    err = EODHDHTTPError(status_code=500, response_body="")
    assert err.message == "HTTP 500"


def test_catch_all():
    """All EODHD errors can be caught with EODHDError."""
    for exc_cls in (EODHDHTTPError, EODHDConnectionError, EODHDTimeoutError):
        with pytest.raises(EODHDError):
            if exc_cls is EODHDHTTPError:
                raise exc_cls(status_code=500, response_body="err")
            else:
                raise exc_cls("something went wrong")
