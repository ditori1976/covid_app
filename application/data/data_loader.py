from configparser import ConfigParser
from application.data.load import Load
from datetime import datetime


class DataLoader(Load):
    def __init__(self, parser: ConfigParser):
        super().__init__(parser)

        self.regions = self.definition_regions()
        self.indicators = self.definition_indicators()

    def load_data(self):
        self.countries = self.countries_geojson()
        self.country_info = self.read_geonames_country_info()
        self.latest_load = datetime.now()
        self.jhu = self.load_jhu()

        self.data = self.add_country_info(self.jhu, self.country_info)
        self.timeseries = self.create_timeseries(self.data)
