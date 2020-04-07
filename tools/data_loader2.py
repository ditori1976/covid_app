from pandas import read_csv


class DataLoader:
    """
    Loads data from CSV file "cities15000.txt" in the same folder and prepares data.
    """

    def __init__(self):

        # define column names and columns to use
        columns = {
            "name": "name",
            "population": "population",
            "dem": "elevation",
            "longitude": "lon",
            "latitude": "lat",
        }

        # load data into DataFrame
        csv_data = read_csv("tools/cities15000.txt", sep="\t")
        raw_data = csv_data.loc[csv_data["country code"] == "CH"]
        data = raw_data.loc[:, list(columns.keys())]
        data.rename(columns=columns, inplace=True)

        # format columns for geographical information
        cols = ["lat", "lon"]
        data.loc[:, cols] = data.loc[:, cols].round(5)
        data["lat"].astype("float")
        data["lon"].astype("float")

        self.data = data
