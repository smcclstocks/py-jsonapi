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
jsonapi.base.handler.base
=========================
"""

# local
from ..response import Response
from ..errors import MethodNotAllowed


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
        raise MethodNotAllowed()

    def head(self):
        """
        Handles a HEAD request.
        """
        raise MethodNotAllowed()

    def get(self):
        """
        Handles a GET request.
        """
        raise MethodNotAllowed()

    def post(self):
        """
        Handles a POST request.
        """
        raise MethodNotAllowed()

    def patch(self):
        """
        Handles a PATCH request.
        """
        raise MethodNotAllowed()

    def delete(self):
        """
        Handles a DELETE request.
        """
        raise MethodNotAllowed()
