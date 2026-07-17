"""Tests for RealEstateAPI (BIS property prices)."""

import pytest
from unittest.mock import MagicMock

from eodhd.APIs.RealEstate import RealEstateAPI


@pytest.fixture
def mock_session():
    return MagicMock()


def _make_api(session):
    return RealEstateAPI(session=session)


def _mock_response(session, data=None):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = data if data is not None else {"data": [], "meta": {}, "links": {}}
    session.get.return_value = resp


TOKEN = "test1234567890123456"


# ---------------------------------------------------------------- countries

def test_countries_url(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_real_estate_countries(api_token=TOKEN, sort="name", fmt="json")

    call_url = mock_session.get.call_args[0][0]
    assert "/real-estate/countries" in call_url
    assert "sort=name" in call_url


def test_countries_pagination(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_real_estate_countries(api_token=TOKEN, page_offset=50, page_limit=500)

    call_url = mock_session.get.call_args[0][0]
    assert "page[offset]=50" in call_url
    assert "page[limit]=500" in call_url


def test_countries_invalid_sort(mock_session):
    api = _make_api(mock_session)
    with pytest.raises(ValueError):
        api.get_real_estate_countries(api_token=TOKEN, sort="population")


def test_countries_invalid_fmt(mock_session):
    api = _make_api(mock_session)
    with pytest.raises(ValueError):
        api.get_real_estate_countries(api_token=TOKEN, fmt="xml")


# ------------------------------------------------------- selected prices (SPP)

def test_selected_prices_url(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_real_estate_selected_prices(
        api_token=TOKEN, code="US", type="real", metric="index",
    )

    call_url = mock_session.get.call_args[0][0]
    assert "/real-estate/US" in call_url
    assert "filter[type]=real" in call_url
    assert "filter[metric]=index" in call_url


def test_selected_prices_code_uppercased(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_real_estate_selected_prices(api_token=TOKEN, code="us")

    call_url = mock_session.get.call_args[0][0]
    assert "/real-estate/US?" in call_url


def test_selected_prices_from_to_and_sort(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_real_estate_selected_prices(
        api_token=TOKEN, code="US", from_date="2020-Q1", to_date="2023-Q4",
        sort="-period", page_limit=100, page_offset=0,
    )

    call_url = mock_session.get.call_args[0][0]
    assert "filter[from]=2020-Q1" in call_url
    assert "filter[to]=2023-Q4" in call_url
    assert "sort=-period" in call_url
    assert "page[limit]=100" in call_url
    assert "page[offset]=0" in call_url


def test_selected_prices_missing_code(mock_session):
    api = _make_api(mock_session)
    with pytest.raises(ValueError):
        api.get_real_estate_selected_prices(api_token=TOKEN, code="")


def test_selected_prices_invalid_sort(mock_session):
    api = _make_api(mock_session)
    with pytest.raises(ValueError):
        api.get_real_estate_selected_prices(api_token=TOKEN, code="US", sort="name")


# ------------------------------------------------------- detailed prices (DPP)

def test_detailed_prices_url(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_real_estate_detailed_prices(
        api_token=TOKEN, code="AE", property_type="1", freq="Q",
    )

    call_url = mock_session.get.call_args[0][0]
    assert "/real-estate/AE/detailed" in call_url
    assert "filter[property_type]=1" in call_url
    assert "filter[freq]=Q" in call_url


def test_detailed_prices_all_filters(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_real_estate_detailed_prices(
        api_token=TOKEN, code="us", area="0", vintage="2", from_date="2020-Q1",
        to_date="2023-Q4", sort="value",
    )

    call_url = mock_session.get.call_args[0][0]
    assert "/real-estate/US/detailed" in call_url
    assert "filter[area]=0" in call_url
    assert "filter[vintage]=2" in call_url
    assert "filter[from]=2020-Q1" in call_url
    assert "filter[to]=2023-Q4" in call_url
    assert "sort=value" in call_url


def test_detailed_prices_freq_uppercased(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_real_estate_detailed_prices(api_token=TOKEN, code="US", freq="a")

    call_url = mock_session.get.call_args[0][0]
    assert "filter[freq]=A" in call_url


def test_detailed_prices_invalid_freq(mock_session):
    api = _make_api(mock_session)
    with pytest.raises(ValueError):
        api.get_real_estate_detailed_prices(api_token=TOKEN, code="US", freq="Z")


def test_detailed_prices_missing_code(mock_session):
    api = _make_api(mock_session)
    with pytest.raises(ValueError):
        api.get_real_estate_detailed_prices(api_token=TOKEN, code=None)


# --------------------------------------------------- detailed series catalogue

def test_detailed_series_url(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_real_estate_detailed_series(api_token=TOKEN, code="US")

    call_url = mock_session.get.call_args[0][0]
    assert "/real-estate/US/detailed/series" in call_url


def test_detailed_series_code_uppercased(mock_session):
    _mock_response(mock_session)
    api = _make_api(mock_session)
    api.get_real_estate_detailed_series(api_token=TOKEN, code="de")

    call_url = mock_session.get.call_args[0][0]
    assert "/real-estate/DE/detailed/series" in call_url


def test_detailed_series_missing_code(mock_session):
    api = _make_api(mock_session)
    with pytest.raises(ValueError):
        api.get_real_estate_detailed_series(api_token=TOKEN, code="")


# -------------------------------------------------------------- pagination bounds

def test_pagination_limit_too_high(mock_session):
    api = _make_api(mock_session)
    with pytest.raises(ValueError):
        api.get_real_estate_countries(api_token=TOKEN, page_limit=501)


def test_pagination_negative_offset(mock_session):
    api = _make_api(mock_session)
    with pytest.raises(ValueError):
        api.get_real_estate_countries(api_token=TOKEN, page_offset=-1)


def test_pagination_limit_zero(mock_session):
    api = _make_api(mock_session)
    with pytest.raises(ValueError):
        api.get_real_estate_selected_prices(api_token=TOKEN, code="US", page_limit=0)
