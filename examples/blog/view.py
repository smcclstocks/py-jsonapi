#!/usr/bin/env python3

# third party
import flask

# local
from api import api


app = flask.Flask(__name__)
api.init_app(app)


@app.route("/")
def index():
    return flask.current_app.send_static_file("templates/layout.html")


if __name__ == "__main__":
    app.run(debug=True)
