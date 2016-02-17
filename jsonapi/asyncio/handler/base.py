#!/usr/bin/env python3

"""
jsonapi.asyncio.handler.base
============================

:license: GNU Affero General Public License v3
"""

# local
from jsonapi.base.response import Response
from jsonapi.base.errors import MethodNotAllowed


class BaseHandler(object):
    """
    The base class for a request handler.

    :arg jsonapi.base.api.API api:
    :arg jsonapi.base.database.Session db:
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

    async def handle(self):
        """
        Handles a requested.
        """
        if self.request.method == "head":
            return await self.head()
        elif self.request.method == "get":
            return await self.get()
        elif self.request.method == "post":
            return await self.post()
        elif self.request.method == "patch":
            return await self.patch()
        elif self.request.method == "delete":
            return await self.delete()
        raise MethodNotAllowed()

    async def head(self):
        """
        Handles a HEAD request.
        """
        raise MethodNotAllowed()

    async def get(self):
        """
        Handles a GET request.
        """
        raise MethodNotAllowed()

    async def post(self):
        """
        Handles a POST request.
        """
        raise MethodNotAllowed()

    async def patch(self):
        """
        Handles a PATCH request.
        """
        raise MethodNotAllowed()

    async def delete(self):
        """
        Handles a DELETE request.
        """
        raise MethodNotAllowed()
