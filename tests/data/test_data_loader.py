from application.data.data_loader import DataLoader
from datetime import datetime, timedelta
from configparser import ConfigParser


def test_parser():
    parser = ConfigParser()
    parser.read("settings.ini")
    assert parser.get(
        "urls",
        "jhu_lookup_url") == 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv'


def test_data_loader_init():
    data_load = DataLoader(None)

    assert data_load.data is None
    assert data_load.latest_load == datetime(1900, 1, 1, 0, 0)
    assert data_load.jhu is None
    assert data_load.country_info is None
    assert data_load.countries is None


def test_data_loader_jhu_load():
    parser = ConfigParser()
    parser.read("settings.ini")
    data_load = DataLoader(parser)
    data_load.load_data()

    columns_jhu = [
        'date',
        'region',
        'iso3',
        'Lat',
        'Lon',
        'deaths',
        'cases',
        'recovered']
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

    assert data_load.latest_load <= datetime.now()
    assert data_load.latest_load >= datetime.now() - timedelta(seconds=10)
    assert data_load.jhu.empty is False
    assert data_load.jhu.columns.any() in columns_jhu
    assert data_load.country_info.empty is False
    assert data_load.country_info.columns.any() in columns_country_info


def test_data_loader_countries():
    parser = ConfigParser()
    parser.read("settings.ini")
    data_load = DataLoader(parser)
    data_load.load_data()

    assert len(data_load.countries) == 2


def test_data_loader_prepare():
    pass
