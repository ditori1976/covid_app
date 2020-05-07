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
    assert data_load.latest_load is None


def test_data_loader_jhu_load():
    parser = ConfigParser()
    parser.read("settings.ini")
    data_load = DataLoader(parser)
    data_load.load_data()

    columns_data = [
        'date',
        'region',
        'iso3',
        'Lat',
        'Lon',
        'deaths',
        'cases',
        'recovered']

    assert data_load.latest_load <= datetime.now()
    assert data_load.latest_load >= datetime.now() - timedelta(seconds=10)
    assert data_load.data.empty is False
    assert data_load.data.columns.any() in columns_data
