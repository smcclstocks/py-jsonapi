#!/usr/bin/env python3

"""
jsonapi.base.response
=====================

:license: GNU Affero General Public License v3
:copyright: 2016 by Benedikt Schmitt <benedikt@benediktschmitt.de>
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
