#!/usr/bin/env python3

"""
jsonapi.base.handler.base
=========================

:license: GNU Affero General Public License v3
:copyright: 2016 by Benedikt Schmitt <benedikt@benediktschmitt.de>
"""

# local
from ..response import Response
from .. import errors


class BaseHandler(object):
    """
    The base class for a request handler.

    :arg jsonapi.base.api.API api:
    :arg jsonapi.base.database.DatabaseSession db:
    :arg jsonapi.base.request.Request request:
    """

    def __init__(self, api, db, request):
        """
        """
        self.api = api
        self.request = request
        self.response = Response()
        self.db = db
        return None

    def prepare(self):
        """
        Called directly before :meth:`handle`.
        """
        return None

    def handle(self):
        """
        Handles a requested.
        """
        if self.request.method == "head":
            return self.head()
        elif self.request.method == "get":
            return self.get()
        elif self.request.method == "post":
            return self.post()
        elif self.request.method == "patch":
            return self.patch()
        elif self.request.method == "delete":
            return self.delete()
        raise errors.MethodNotAllowed()

    def head(self):
        """
        Handles a HEAD request.
        """
        raise errors.MethodNotAllowed()

    def get(self):
        """
        Handles a GET request.
        """
        raise error.MethodNotAllowed()

    def post(self):
        """
        Handles a POST request.
        """
        raise error.MethodNotAllowed()

    def patch(self):
        """
        Handles a PATCH request.
        """
        raise error.MethodNotAllowed()

    def delete(self):
        """
        Handles a DELETE request.
        """
        raise error.MethodNotAllowed()
