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

# local
from ..response import Response
from ..database import BulkSession
from .. import errors


class BaseHandler(object):
    """
    The base class for a request handler.
    """

    def __init__(self, api, request):
        """
        """
        self.api = api
        self.request = request
        self.response = Response()
        self.db = BulkSession(api)
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
