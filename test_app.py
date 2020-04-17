"""
Unit test for app.py
"""
import unittest
from tools import DataLoader
from configparser import ConfigParser


# configuration
parser = ConfigParser()
parser.read("settings.ini")

data = DataLoader(parser)


class TestLoader(unittest.TestCase):
    def test_loader(self):

        self.assertTrue(data.regions)
        self.assertEqual(
            data.per_country_max.loc[
                data.per_country_max.region == "France", "continent"
            ].max(),
            "EU",
        )


class TestParser(unittest.TestCase):
    def test_parser(self):
        geonames_countries_url = "http://download.geonames.org/countries/"
        assert geonames_countries_url == parser.get("urls", "geonames_countries_url")


if __name__ == "__main__":
    unittest.main()
