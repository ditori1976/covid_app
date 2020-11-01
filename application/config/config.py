import os


class Config:
    def __init__(self):
        if "HOST" in os.environ:
            host = os.environ.get("HOST")
        else:
            host = "127.0.0.1"

        if "PORT" in os.environ:
            port = os.environ.get("PORT")
        else:
            port = "8080"

        if "UPDATE" in os.environ:
            UPDATE = os.environ.get("UPDATE")
        else:
            UPDATE = True

        self.port = port
        self.host = host
        self.mapbox = os.getenv("MAPBOX")
        self.UPDATE = UPDATE
        self.layout = dict(
            margin=dict(
                l=0,
                r=0,
                b=0,
                t=0,
                pad=0),
            dragmode="select")
        self.state = {
            "indicator": "cases",
            "aggregation": "7days",
            "per capita": True,
            "regions": ["World"],
            "active": "World",
            "axis": {
                "x": "date",
                "y": "linear"
            },
            "bbox": {
                "center": {
                    "lat": 0,
                    "lon": 0,
                },
                "zoom": 2
            }
        }
