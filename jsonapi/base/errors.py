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
    "NotFound",
    "MethodNotAllowed",
    "NotAcceptable",
    "Conflict",
    "UnsupportedMediaType",

    "InvalidDocument",
    "UnresolvableIncludePath",
    "ReadOnlyAttribute",
    "ReadOnlyRelationship",
    "UnsortableField",
    "UnfilterableField",
    "RelationshipNotFound",
    "ResourceNotFound"
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


class ErrorList(Exception):
    """
    Can be used to store a list of exceptions, which occur during the
    execution of an api request.
    """

    def __init__(self, errors=None):
        self.errors = list()
        if errors:
            self.extend(errors)
        return None

    def __bool__(self):
        """
        """
        return bool(self.errors)

    def append(self, error):
        """
        """
        assert isinstance(error, Error)
        self.errors.append(error)

        # Invalidate the cache.
        del self.json
        return None

    def extend(self, error):
        """
        """
        assert isinstance(error, ErrorList)
        self.errors.extend(error.errors)

        # Invalidate the cache.
        del self.json
        return None

    @cached_property
    def json(self):
        """
        Creates the JSONapi error object.
        http://jsonapi.org/format/#error-objects
        """
        d = [err.json for err in self.errors]
        return d


def error_to_response(error, json_dumps):
    """
    Converts an :class:`Error` to a :class:`~jsonapi.base.response.Response`.

    :arg Error error:
    :arg json_dumps:
        The json serializer, which is used to serialize :attr:`Error.json`
    :rtype: jsonapi.base.request.Request

    :seealso: http://jsonapi.org/format/#error-objects
    """
    assert isinstance(error, (Error, ErrorList))

    from .response import Response

    headers = {
        "content-type": "application/vnd.api+json"
    }

    if isinstance(error, Error):
        body = json_dumps({"errors": [error.json]})
    elif isinstance(error, ErrorList):
        body = json_dumps({"errors": error.json})

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

    Please note, that this does not include semantic errors, like a wrong
    typename.

    :seealso: http://jsonapi.org/format/#document-structure
    :seealso: :mod:`jsonapi.base.validators`
    """


class UnresolvableIncludePath(BadRequest):
    """
    Raised, if an include path does not exist.

    .. seealso::

        *   :attr:`jsonapi.base.request.Request.japi_include`
        *   :attr:`jsonapi.base.database.Session.fetch_includes`
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
    If a filter should be used on a field, which does not support the
    filter.
    """

    def __init__(self, typename, filtername, fieldname, **kargs):
        self.typename = typename
        self.filtername = filtername
        self.fieldname = fieldname

        detail = "The filter '{}' is not supported on the '{}' field of '{}.'"\
            .format(filtername, fieldname)
        super().__init__(detail=detail, **kargs)
        return None


class RelationshipNotFound(NotFound):
    """
    Raised if a relationship does not exist.
    """

    def __init__(self, typename, relname, **kargs):
        self.typename = typename
        self.relname = relname

        detail = "The type '{}' has no relationship '{}'."\
            .format(typename, relname)
        super().__init__(detail=detail, **kargs)
        return None


class ResourceNotFound(NotFound):
    """
    Raised, if a resource does not exist.
    """

    def __init__(self, identifier, **kargs):
        self.identifier = identifier

        detail = "The resource (type={}, id={}) does not exist."\
            .format(*identifier)
        super().__init__(detail=detail, **kargs)
        return None
