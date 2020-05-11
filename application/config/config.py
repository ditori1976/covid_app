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
