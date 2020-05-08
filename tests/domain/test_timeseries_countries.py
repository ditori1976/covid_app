import uuid
from application.domain.timeseries_countries import TimeseriesCountries


def test_timeseries_countries_init():

    timeseries_countries = TimeseriesCountries(
        date="2020-02-01",
        iso3="AFG",
        lon=67.709953,
        lat=33.93911,
        cases=14,
        deaths=7,
        recovered=1)

    assert timeseries_countries.date == "2020-02-01"
    assert timeseries_countries.iso3 == "AFG"
    assert timeseries_countries.lon == 67.709953
    assert timeseries_countries.lat == 33.93911
    assert timeseries_countries.cases == 14
    assert timeseries_countries.deaths == 7
    assert timeseries_countries.recovered == 1


def test_timeseries_countries_from_dict():

    timeseries_countries = TimeseriesCountries.from_dict(
        {
            "date": "2020-02-01",
            "iso3": "AFG",
            "lon": 67.709953,
            "lat": 33.93911,
            "cases": 14,
            "deaths": 7,
            "recovered": 1

        }
    )

    assert timeseries_countries.date == "2020-02-01"
    assert timeseries_countries.iso3 == "AFG"
    assert timeseries_countries.lon == 67.709953
    assert timeseries_countries.lat == 33.93911
    assert timeseries_countries.cases == 14
    assert timeseries_countries.deaths == 7
    assert timeseries_countries.recovered == 1
