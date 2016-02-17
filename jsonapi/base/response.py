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
