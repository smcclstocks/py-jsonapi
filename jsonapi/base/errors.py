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
jsonapi.base.errors
===================

This module implements the base class for all JSONapi exceptions:
http://jsonapi.org/format/#errors
"""

# std
from collections import OrderedDict

# third party
from cached_property import cached_property


__all__ = [
    "Error",
    "error_to_response",

    "InternalServerError",
    "BadRequest",
    "Forbidden",
    "MethodNotAllowed",
    "Conflict",
    "UnsupportedMediaType",

    "InvalidDocument",
    "IncludePathNotFound",
    "ReadOnlyAttribute",
    "ReadOnlyRelationship",
    "UnsortableField",
    "UnfilterableField"
]


class Error(Exception):
    """
    .. hint::

        This class implements the error specification:

        http://jsonapi.org/format/#errors

    This is the base class for all exceptions thrown by your API. All subclasses
    of this exception are catched by the API and converted into a response.
    All other exception will not be catched.

    :arg int http_status:
        The HTTP status code applicable to this problem.
    :arg str id:
        A unique identifier for this particular occurrence of the problem.
    :arg str about:
        A link that leeds to further details about this particular occurrence
        of the problem.
    :arg str code:
        An application specific error code, expressed as a string value.
    :arg str title:
        A short, human-readable summay of the problem that SHOULD not change
        from occurrence to occurrence of the problem, except for purposes
        of localization. The default value is the class name.
    :arg str detail:
        A human-readable explanation specific to this occurrence of the problem.
    :arg str source_pointer:
        A JSON Pointer [RFC6901] to the associated entity in the request
        document [e.g. `"/data"` for a primary data object, or
        `"/data/attributes/title"` for a specific attribute].
    :arg str source_parameter:
        A string indicating which URI query parameter caused the error.
    :arg dict meta:
        A meta object containing non-standard meta-information about the error.
    """

    def __init__(
        self,
        http_status=500,
        id_=None,
        about="",
        code=None,
        title=None,
        detail="",
        source_parameter=None,
        source_pointer=None,
        meta=None
        ):
        """
        """
        self.http_status = http_status
        self.id = id_
        self.about = about
        self.code = code
        self.title = title if title is not None else type(self).__name__
        self.detail = detail
        self.source_pointer = source_pointer
        self.source_parameter = source_parameter
        self.meta = meta if meta is not None else dict()
        return None

    def __str__(self):
        """
        Returns the :attr:`detail` attribute per default.
        """
        return self.detail

    @cached_property
    def json(self):
        """
        The serialized version of this error.
        """
        d = OrderedDict()
        if self.id is not None:
            d["id"] = str(self.id)
        d["status"] = self.http_status
        d["title"] = self.title
        if self.about:
            d["links"] = OrderedDict()
            d["links"]["about"] = self.about
        if self.code:
            d["code"] = self.code
        if self.detail:
            d["detail"] = self.detail
        if self.source_pointer or self.source_parameter:
            d["source"] = OrderedDict()
            if self.source_pointer:
                d["source"]["pointer"] = self.source_pointer
            if self.source_parameter:
                d["source"]["parameter"] = self.source_parameter
        if self.meta:
            d["meta"] = meta
        return d


def error_to_response(error, json_dumps):
    """
    Converts an :class:`Error` to a :class:`~jsonapi.base.response.Response`.

    :arg Error error:
    :arg json_dumps:
        The json serializer, which is used to serialize :attr:`Error.json`
    :rtype: jsonapi.base.request.Request
    """
    from .response import Response

    headers = {
        "content-type": "application/vnd.api+json"
    }
    body = json_dumps(error.json)
    body = body.encode()

    resp = Response(
        status=error.http_status, headers=headers, body=body
    )
    return resp


# Common http errors
# ~~~~~~~~~~~~~~~~~~

class InternalServerError(Error):

    def __init__(self, **kargs):
        super().__init__(http_status=500, **kargs)
        return None


class BadRequest(Error):

    def __init__(self, **kargs):
        super().__init__(http_status=400, **kargs)
        return None


class Forbidden(Error):

    def __init__(self, **kargs):
        super().__init__(http_status=403, **kargs)
        return None


class NotFound(Error):

    def __init__(self, **kargs):
        super().__init__(http_status=404, **kargs)
        return None


class MethodNotAllowed(Error):

    def __init__(self, **kargs):
        super().__init__(http_status=405, **kargs)
        return None


class NotAcceptable(Error):

    def __init__(self, **kargs):
        super().__init__(http_status=406, **kargs)
        return None


class Conflict(Error):

    def __init__(self, **kargs):
        super().__init__(http_status=409, **kargs)
        return None


class UnsupportedMediaType(Error):

    def __init__(self, **kargs):
        super().__init__(http_status=415, **kargs)
        return None


# Special errors
# ~~~~~~~~~~~~~~

class InvalidDocument(BadRequest):
    """
    Raised, if the structure of a json document in a request body is invalid.

    :seealso: http://jsonapi.org/format/#document-structure
    :seealso: :mod:`jsonapi.base.validators`
    """

class IncludePathNotFound(BadRequest):
    """
    Raised, if an include path does not exist.

    .. seealso::

        *   :attr:`jsonapi.base.request.Request.japi_include`
        *   :attr:`jsonapi.base.database.DatabaseSession.fetch_includes`
    """

    def __init__(self, include_path, **kargs):
        self.include_path = include_path

        detail = "The include path '{}' does not exist."\
            .format(".".join(include_path))

        super().__init__(detail=detail, **kargs)
        return None


class ReadOnlyAttribute(Forbidden):
    """
    Raised, if an attribute value can not be changed.
    """


class ReadOnlyRelationship(Forbidden):
    """
    Raised, if the value of a relationship can not be modified.
    """


class UnsortableField(BadRequest):
    """
    If a field is used as sort key, but does not support sorting.
    """

    def __init__(self, typename, fieldname, **kargs):
        self.typename = typename
        self.fieldname = fieldname

        detail = "The field '{}.{}' can not be used for sorting."\
            .format(typename, fieldname)
        super().__init__(detail=detail, **kargs)
        return None


class UnfilterableField(BadRequest):
    """
    If a filter should be used on a field, which does not suppor the
    filter.
    """

    def __init__(self, filtername, fieldname, **kargs):
        self.filtername = filtername
        self.fieldname = fieldname

        detail = "The filter '{}' is not supported on the '{}' field."\
            .format(filtername, fieldname)
        super().__init__(detail=detail, **kargs)
        return None
