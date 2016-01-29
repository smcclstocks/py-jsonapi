#!/usr/bin/env python3

# py-jsonapi - A toolkit for building a JSONapi
# Copyright (C) 2016 Benedikt Schmitt <benedikt@benediktschmitt.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# std
import logging

# third party
import flask
import werkzeug

# local
from jsonapi import base


__all__ = [
    "FlaskAPI",
    "current_api"
]


log = logging.getLogger(__file__)


def get_request(api):
    """
    Transforms the current flask request object in to a jsonapi request object.
    """
    uri = flask.request.base_url
    if flask.request.query_string:
        uri += "?" + flask.request.query_string.decode("utf-8")

    method = flask.request.method
    headers = dict(flask.request.headers)
    body = flask.request.get_data()
    return base.Request(api, uri, method, headers, body)


def to_response(jresponse):
    """
    Transforms the jsonapi response object into a flask response.
    """
    if jresponse.is_file:
        fresponse = flask.send_file(jresponse.file)
    elif jresponse.has_body:
        fresponse = flask.Response(jresponse.body)
    else:
        fresponse = flask.Response("")

    for key, value in jresponse.headers.items():
        fresponse.headers[str(key)] = value
    fresponse.status_code = jresponse.status
    return fresponse


class FlaskAPI(base.api.API):
    """
    Implements the API for flask. You can provide the flask application
    later via :meth:`init_app`.
    """

    def __init__(self, uri, settings=None, flask_app=None):
        """
        """
        super().__init__(uri=uri, settings=settings)

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
        app.extensions = getattr(app, "extensions", dict())
        app.extensions["jsonapi"] = self

        # Add the url rule.
        app.add_url_rule(
            rule=self._uri + "/<path:path>",
            endpoint="jsonapi",
            view_func=self.handle_request,
            methods=["get", "post", "patch", "delete", "head"]
        )

        # Add the api to the jinja environment
        app.jinja_env.globals["jsonapi"] = current_api
        return None

    def handle_request(self, path=None):
        """
        Handles a request to the API.
        """
        req = get_request(self)
        resp = super().handle_request(req)
        return to_response(resp)


#: Returns the FlaskAPI instance, which is by used by the current flask
#: application.
current_api = werkzeug.local.LocalProxy(
    lambda: flask.current_app.extensions["jsonapi"]
)
