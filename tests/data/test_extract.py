from application.data.extract import Extract
from datetime import datetime, timedelta
from configparser import ConfigParser


def test_parser():
    parser = ConfigParser()
    parser.read("settings.ini")
    assert parser.get(
        "urls",
        "jhu_lookup_url") == 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv'


def test_extract_init():
    data_load = Extract(None)

    assert data_load.data is None
    assert data_load.latest_load is None
    assert data_load.jhu is None
    assert data_load.country_info is None
    assert data_load.countries is None


def test_extract_jhu_load():
    parser = ConfigParser()
    parser.read("settings.ini")
    data_load = Extract(parser)
    data = data_load.load_jhu()

    columns_jhu = [
        'date',
        'region',
        'iso3',
        'Lat',
        'Lon',
        'deaths',
        'cases',
        'recovered']

    assert data.empty is False
    assert data.columns.any() in columns_jhu


def test_extract_read_geonames_country_info():
    parser = ConfigParser()
    parser.read("settings.ini")
    data_load = Extract(parser)
    data = data_load.read_geonames_country_info()

    columns_country_info = [
        'iso_alpha2',
        'iso_alpha',
        'iso_num',
        'fips',
        'region',
        'Capital',
        'area',
        'population',
        'continent']

    assert data.empty is False
    assert data.columns.any() in columns_country_info


def test_extract_countries():
    parser = ConfigParser()
    parser.read("settings.ini")
    data_load = Extract(parser)
    data = data_load.countries_geojson()

    assert len(data) == 2
