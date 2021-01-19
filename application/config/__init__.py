import os
import logging
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html


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
        # startwerte mit DataLoader sync (DRY)
        self.state = {
            "indicator": "cases",
            "aggregation": "days",
            "per capita": True,
            "regions": ["Europe"],
            "active": "Europe",
            "axis": {
                "x": "date",
                "y": "linear"
            },
            "bbox": {
                "center": {
                    "lat": 50,
                    "lon": 5,
                },
                "zoom": 2
            }
        }


"""
logging
"""
# logging.basicConfig()
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)-20s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
