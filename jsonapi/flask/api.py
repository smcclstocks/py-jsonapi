#!/usr/bin/env python3

# The MIT License (MIT)
#
# Copyright (c) 2016 Benedikt Schmitt
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
jsonapi.flask.api
=================
"""

# std
import logging

# third party
import flask
import werkzeug

# local
import jsonapi


__all__ = [
    "FlaskAPI",
    "current_api"
]


LOG = logging.getLogger(__file__)


def get_request():
    """
    Transforms the current flask request object in to a jsonapi request object.
    """
    uri = flask.request.base_url
    if flask.request.query_string:
        uri += "?" + flask.request.query_string.decode("utf-8")

    method = flask.request.method
    headers = dict(flask.request.headers)
    body = flask.request.get_data()
    return jsonapi.base.Request(uri, method, headers, body)


def to_response(japi_response):
    """
    Transforms the jsonapi response object into a flask response.
    """
    if japi_response.is_file:
        flask_response = flask.send_file(japi_response.file)
    elif japi_response.has_body:
        flask_response = flask.Response(japi_response.body)
    else:
        flask_response = flask.Response("")

    for key, value in japi_response.headers.items():
        flask_response.headers[str(key)] = value
    flask_response.status_code = japi_response.status
    return flask_response


class FlaskAPI(jsonapi.base.api.API):
    """
    Implements the API for flask. You can provide the flask application
    later via :meth:`init_app`.
    """

    def __init__(self, uri, db, settings=None, flask_app=None):
        """
        """
        super().__init__(uri=uri, db=db, settings=settings)

        self._flask_app = None
        if flask_app is not None:
            self.init_app(flask_app)
        return None

    @property
    def debug(self):
        """
        This is a proxy for the :attr:`flask_app` *debug* attribute. This means,
        that you must enable the debug mode on the flask application.
        """
        return self._flask_app.debug

    @property
    def flask_app(self):
        """
        The flask application, this API is registered on.
        """
        return self._flask_app

    def init_app(self, app):
        """
        Registers this API on the flask application *app*.

        :arg flask.Flask app:
        """
        # Avoid double initialization.
        if self._flask_app is app:
            return None
        if self._flask_app is not None:
            raise RuntimeError(
                "This api has already been registered on a flask application."
            )

        self._flask_app = app

        # Add the url rule.
        app.add_url_rule(
        rule=self._uri + "/<path:path>",
        endpoint="jsonapi",
        view_func=self.handle_request,
        methods=["get", "post", "patch", "delete", "head"]
        )

        # Register the jsonapi extension on the flask application.
        app.extensions = getattr(app, "extensions", dict())
        app.extensions["jsonapi"] = self

        # Add the api to the jinja environment
        app.jinja_env.globals["jsonapi"] = current_api
        return None

    def handle_request(self, path=None):
        """
        Handles a request to the API.
        """
        req = get_request()
        resp = super().handle_request(req)
        return to_response(resp)


#: Returns the FlaskAPI instance, which is by used by the current flask
#: application.
current_api = werkzeug.local.LocalProxy(
    lambda: flask.current_app.extensions["jsonapi"]
)
