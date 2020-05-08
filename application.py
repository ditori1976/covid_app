from application import app, start_multi, configuration

if __name__ == "__main__":

    start_multi()
    app.run_server(
        debug=True,
        port=configuration.port,
        host=configuration.host)
