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

# third party
import tornado
import tornado.web
import tornado.gen

# local
import jsonapi


__all__ = [
    "TornadoAPI"
]


class Handler(tornado.web.RequestHandler):
    """
    This handler works as proxy for the API. Each request is forwarded to
    the *jsonapi*.
    """

    def initialize(self, jsonapi):
        """
        """
        self.jsonapi = jsonapi
        return None

    @tornado.gen.coroutine
    def prepare(self):
        """
        .. hint::

            Prepare is not the best way to dispatch the request. Try to find
            a better way.
        """
        # Transform the request
        request = jsonapi.base.Request(
            self.request.uri, self.request.method, self.request.headers,
            self.request.body
        )

        # Let the API handle it.
        resp = self.jsonapi.handle_request(request)

        # Create the response.
        for key, value in resp.headers.items():
            self.set_header(key, value)
        self.set_status(resp.status)

        if resp.is_file:
            raise RuntimeError("Sorry, files are not yet supported :(")
        elif resp.has_body:
            self.write(resp.body)

        self.finish()
        return None

    def head(self, *args, **kargs):
        """
        """
        # Overridden, to avoid a MethodNotAllowed error raised by tornado.
        return None

    def get(self, *args, **kargs):
        """
        """
        # Overridden, to avoid a MethodNotAllowed error raised by tornado.
        return None

    def post(self, *args, **kargs):
        """
        """
        # Overridden, to avoid a MethodNotAllowed error raised by tornado.
        return None

    def patch(self, *args, **kargs):
        """
        """
        # Overridden, to avoid a MethodNotAllowed error raised by tornado.
        return None

    def delete(self, *args, **kargs):
        """
        """
        # Overridden, to avoid a MethodNotAllowed error raised by tornado.
        return None


class TornadoAPI(jsonapi.base.api.API):
    """
    Integrates *py-jsonapi* into a tornado application.
    """

    def __init__(self, uri, settings=None, tornado_app=None):
        """
        """
        super().__init__(uri=uri, settings=settings)

        self._tornado_app = None
        if tornado_app is not None:
            self.init_app(tornado_app)
        return None

    @property
    def debug(self):
        """
        Proxy for the *debug* setting of the parent tornado application. If
        you want to enable the debug mode, you must do it on the tornado
        application.
        """
        return self._tornado_app.settings.get("debug")

    @property
    def tornado_app(self):
        """
        Returns the tornado application, which owns this API.
        """
        return self._tornado_app

    def init_app(self, app):
        """
        Registers the API handler on the tornado application.

        :arg tornado.web.Application app:
        """
        # Avoid double initialization
        if self._tornado_app is app:
            return None
        if self._tornado_app is not None:
            raise RuntimeError(
                "This API has already been registered on a tornado application."
            )

        self._tornado_app = app
        app.settings["jsonapi"] = self

        # Add the handler.
        url_rule = tornado.web.url(
            self.uri + "/.*", Handler, dict(jsonapi=self), name="jsonapi"
        )
        app.add_handlers(".*", [url_rule])
        return None
