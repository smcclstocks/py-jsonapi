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

"""
jsonapi.base.response
=====================
"""

__all__ = [
    "Response"
]


class Response(object):
    """
    Contains all information needed for a creating a proper http response.

    :arg int status:
        The http status code
    :arg dict headers:
        A dictionary containing all headers of the response.
    :arg bytes body:
        The body of the http response as bytes. This attribute maybe None.
    :arg file:
        If not None, this is a file like object or a filename.
    """

    def __init__(self, status=200, headers=None, body=None, file=None):
        self.status = status
        self.headers = headers if headers is not None else dict()
        self.body = body
        self.file = file
        return None

    @property
    def has_body(self):
        """
        Returns true, if the response contains a body (and not a file).
        """
        return self.body is not None

    @property
    def is_file(self):
        """
        Returns true, if the response is a file, which must be sent to the
        client.
        """
        return self.file is not None

    def print(self):
        """
        Prints information about the response object. This method is only
        used for debugging purposes.
        """
        print("Response")
        print("--------")
        print("\t", "status", self.status)
        print("\t", "headers", self.headers)
        print("\t", "body")
        print(self.body)
        print("\t", "is_file", self.is_file)
        print("\t", "file", self.file)
        return None
