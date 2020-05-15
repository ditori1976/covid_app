import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output, State, ALL, MATCH
import time
import json
import math
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from configparser import ConfigParser

from application.data.data_loader import DataLoader
from application.config.config import Config

# refactoring config/layout/stlyes
configuration = Config()
layout = dict(margin=dict(l=0, r=0, b=0, t=0, pad=0), dragmode="select")
style_full = {
    "height": "100%",
    "width": "100%",
    "paddingLeft": "0px",
    "paddingTop": "0px",
    "paddingRight": "0px",
    "paddingBottom": "0px"
}
style_todo = {"display": "inline", "margin": "10px"}

parser = ConfigParser()
parser.read("settings.ini")


data = DataLoader(parser)
# data.load_data()
print(data.data)
