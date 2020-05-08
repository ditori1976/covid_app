

class TimeseriesCountries(object):
    def __init__(self, date, iso3, lon, lat, cases, deaths, recovered):

        self.date = date
        self.iso3 = iso3
        self.lon = lon
        self.lat = lat
        self.cases = cases
        self.deaths = deaths
        self.recovered = recovered

    # optional: for json
    @classmethod
    def from_dict(cls, adict):
        timeseries = TimeseriesCountries(
            date=adict["date"],
            iso3=adict["iso3"],
            lon=adict["lon"],
            lat=adict["lat"],
            cases=adict["cases"],
            deaths=adict["deaths"],
            recovered=adict["recovered"])
        return timeseries
