from application.data.data_loader import DataLoader
from configparser import ConfigParser

parser = ConfigParser()
parser.read("settings.ini")

data_load = DataLoader(parser)
data_load.load_data()
print(data_load.latest_load)
print(data_load.indicators["cases"])

print(data_load.latest_data(data_load.indicators["cases"]))
# print(data_load.timeseries)
