#!/usr/bin/env python3

"""
jsonapi.tornado.api
===================

:license: GNU Affero General Public License v3
"""

# std
import asyncio

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

    @asyncio.coroutine
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
        resp = yield from self.jsonapi.handle_request(request)

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


class TornadoAPI(jsonapi.asyncio.api.API):
    """
    Integrates *py-jsonapi* into a tornado application.
    """

    def __init__(self, uri, db, settings=None, tornado_app=None):
        """
        """
        super().__init__(uri=uri, db=db, settings=settings)

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
