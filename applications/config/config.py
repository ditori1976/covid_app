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

        self.header = """<!DOCTYPE html>
                            <html lang="en">
                                <head>
                                <meta charset="utf-8">
                                    <!-- Global site tag (gtag.js) - Google Analytics -->
                                    <script async src="https://www.googletagmanager.com/gtag/js?id=UA-164129496-1"></script>
                                    <script>
                                    window.dataLayer = window.dataLayer || [];
                                    function gtag(){dataLayer.push(arguments);}
                                    gtag('js', new Date());

                                    gtag('config', 'UA-164129496-1');
                                    </script>

                                    {%metas%}
                                    <title>{%title%}</title>
                                    {%favicon%}
                                    {%css%}
                                </head>
                                <body>
                                    {%app_entry%}
                                    <footer>
                                        {%config%}
                                        {%scripts%}
                                        {%renderer%}
                                    </footer>
                                </body>
                            </html>"""
