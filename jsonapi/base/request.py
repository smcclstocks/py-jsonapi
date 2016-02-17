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
jsonapi.base.request
====================
"""

# std
import logging
import re
import urllib.parse

# third party
from cached_property import cached_property

# local
from . import errors


LOG = logging.getLogger(__file__)


__all__ = [
    "Request"
]


class Request(object):
    """
    Wraps a request object, which can be used to call the View class.

    :arg str uri:
    :arg str method:
    :arg dict headers:
    :arg bytes body:
    :arg jsonapi.base.api.API api:
        The api, which handles this request. If None, the api will set the
        attribute in :meth:`jsonapi.base.api.API.handle_request`.
    """

    def __init__(self, uri, method, headers, body, api=None):
        self.api = api
        self.uri = uri
        self.method = method.lower()
        self.headers = {key.lower(): value for key, value in headers.items()}
        self.body = body

        #: Contains parameters, which are encoded into the URI.
        #: For example a resource uri: ``http://localhost:5000/api/User/1``
        #: contains the id ``{'id': '1'}``
        #:
        #: :seealso: :meth:`jsonapi.base.api.API.find_handler`
        self.japi_uri_arguments = dict()
        return None

    @cached_property
    def parsed_uri(self):
        """
        Returns a tuple with the uri components.
        """
        return urllib.parse.urlparse(self.uri)

    @cached_property
    def query(self):
        """
        Returns a dictionary which maps a query key to its values.
        """
        query = urllib.parse.parse_qs(self.parsed_uri.query)
        return query

    def get_query_argument(self, name, fallback=None):
        """
        Returns the (first) value of the query argument with the name *name*. If
        the argument does not exist, *fallback* is returned.

        :arg str name:
        :arg fallback:
        """
        value = self.query.get(name)
        return value[0] if value else fallback

    @cached_property
    def content_type(self):
        """
        Returns a tuple, with the media type and the parameters.

        .. code-block:: python3

            media_type, media_parameters = request.content_type

        :seealso: :attr:`media_parameters`
        :seealso: https://www.w3.org/Protocols/rfc1341/4_Content-Type.html
        """
        content_type = self.headers.get("content-type", "")
        type_, *parameters = content_type.split(";")

        for i, parameter in enumerate(parameters):
            parameter = parameter.split("=", 1)
            if len(parameter) != 2:
                detail="Invalid 'Content-Type' parameter '{}'."\
                    .format(parameter)
                raise errors.BadRequest(detail=detail)
            parameters[i] = parameter
        return (type_, dict(parameters))

    @cached_property
    def japi_page_number(self):
        """
        Returns the number of the requested page or None.

        Query parameter: ``page[number]``

        :raises jsonapi.base.errors.BadRequest:
            If ``page[number]`` is no integer
        :raises jsonapi.base.errors.BadRequest:
            If ``page[number]`` is less than 1

        :seealso: http://jsonapi.org/format/#fetching-pagination
        """
        tmp = self.get_query_argument("page[number]")

        # Try to convert it to an integer and make sure it is >= 1.
        if tmp is not None:
            try:
                tmp = int(tmp)
            except:
                raise errors.BadRequest(
                    detail="The 'page[number]' must be an integer.",
                    source_parameter="page[number]"
                )

            if tmp < 1:
                raise errors.BadRequest(
                    detail="The 'page[number]' must be >= 1.",
                    source_parameter="page[number]"
                )
        return tmp

    @cached_property
    def japi_page_size(self):
        """
        Returns the size of the pages or None.

        Query parameter: ``page[size]``

        :raises jsonapi.base.errors.BadRequest:
            If ``page[size]`` is no integer
        :raises jsonapi.base.errors.BadRequest:
            If ``page[size]`` is less than 1

        :seealso: http://jsonapi.org/format/#fetching-pagination
        """
        tmp = self.get_query_argument("page[size]")

        # Try to convert it to an integer and make sure, it is >= 1.
        if tmp is not None:
            try:
                tmp = int(tmp)
            except:
                raise errors.BadRequest(
                    detail="The 'page[size]' must be an integer.",
                    source_parameter="page[size]"
                )

            if tmp < 1:
                raise errors.BadRequest(
                    detail="The 'page[size]' must be >= 1.",
                    source_parameter="page[size]"
                )
        return tmp

    @cached_property
    def japi_page_limit(self):
        """
        Returns the limit based on the :attr:`japi_page_size`
        """
        return self.japi_page_size if self.japi_paginate else None

    @cached_property
    def japi_page_offset(self):
        """
        Returns the offset based on the :attr:`japi_page_size` and
        :attr:`japi_page_number`.
        """
        if self.japi_paginate:
            return self.japi_page_size*(self.japi_page_number - 1)
        else:
            return None

    @cached_property
    def japi_paginate(self):
        """
        Returns True, if the result should be paginated.
        This is the case, if ``page[size]`` and ``page[number]`` are both
        present and valid.

        .. seealso::

            *   :attr:`japi_page_size`
            *   :attr:`japi_page_number`
            *   http://jsonapi.org/format/#fetching-pagination
        """
        return self.japi_page_size is not None \
            and self.japi_page_number is not None

    @cached_property
    def japi_offset(self):
        """
        Return the offset when querying a collection.

        Query parameter: ``offset``

        :raises jsonapi.base.errors.BadRequest:
            If the offset is not an integer
        :raises jsonapi.base.errors.BadRequest:
            If the offset is negative
        :raises jsonapi.base.errors.BadRequest:
            If the offset is greater than the page size
        """
        offset = self.get_query_argument("offset")

        if offset is not None:
            try:
                offset = int(offset)
            except:
                raise errors.BadRequest(
                    detail="The 'offset' must be an integer.",
                    source_parameter="offset"
                )

            if offset < 0:
                raise errors.BadRequest(
                    detail="The 'offset' must be >= 0.",
                    source_parameter="offset"
                )

            if self.japi_paginate and offset >= self.japi_page_size:
                raise errors.BadRequest(
                    detail="The 'offset' must be less than the 'page[size]'.",
                    source_parameter="offset"
                )
        return offset

    @cached_property
    def japi_limit(self):
        """
        Extracts the limit parameter from the url query string and returns it.

        Query parameter: ``limit``

        :raises jsonapi.base.errors.BadRequest:
            If the limit is not an integer
        :raises jsonapi.base.errors.BadRequest:
            If the limit is not >= 0
        """
        limit = self.get_query_argument("limit")

        if limit is None and self.japi_paginate:
            limit = self.japi_page_size
        elif limit is not None:
            try:
                limit = int(limit)
            except:
                raise errors.BadRequest(
                    detail="The 'limit' must be an integer.",
                    source_parameter="limit"
                )

            if limit < 1:
                raise errors.BadRequest(
                    detail="The 'limit' must be >= 1.",
                    source_parameter="limit"
                )
        return limit

    @cached_property
    def japi_filters(self):
        """
        Returns a dictionary, which maps field names to the filter rules applied
        on them.

        A url query may contain these filters (not all of them may be supported
        by all database adapters):

        *   `eq`
        *   `ne`
        *   `lt`
        *   `lte`
        *   `gt`
        *   `gte`
        *   `in`
        *   `nin`
        *   `all`
        *   `size`
        *   `exists`
        *   `iexact`
        *   `contains`
        *   `icontains`
        *   `startswith`
        *   `istartswith`
        *   `endswith`
        *   `iendswith`
        *   `match`

        .. code-block:: python3

            >>> # /api/User/?filter[name]=endswith:'Simpson'
            >>> request.japi_filters
            ... [("name", "endswith", "Simpson")]

            >>> # /api/User/?filter[name]=in:['Homer Simpson', 'Darth Vader']
            >>> request.japi_filters
            ... [("name", "in", ["Homer Simpson", "Darth Vader"])]

            >>> # /api/User/?filter[email]=startswith:'lisa'&filter[age]=lt:20
            >>> request.japi_filters
            ... [("email", "startswith", "lisa"), ("age", "lt", 20)]

        :raises jsonapi.base.errors.BadRequest:
            If a filtername is used, which does not exist.
        :raises jsonapi.base.errors.BadRequest:
            If the value of a filter is not a JSON object.
        """
        filters = list()

        KEY_RE = re.compile(r"filter\[([A-z0-9_]+)\]")

        # The first group captures the filters, the second captures the value.
        VALUE_RE = re.compile(
            r"(eq:|ne:|lt:|lte:|gt:|gte:|in:|nin:|all:|exists:|iexact:"\
            r"|contains:|icontains:|startswith:|istartswith:|endswith:"\
            r"|iendswith:)(.*)"
        )

        for key, values in self.query.items():
            key_match = re.fullmatch(KEY_RE, key)
            value_match = re.fullmatch(VALUE_RE, values[0])

            # If the key indicates a filter, but the filtername does not exist,
            # throw a BadRequest exception.
            if key_match and not value_match:
                filtername = value_match.group(1)
                filtername = filtername[:-1]
                raise errors.BadRequest(
                    detail="The filter '{}' does not exist.".format(filtername),
                    source_parameter=key
                )
            # The key indicates a filter and the filternames exists.
            elif key_match and value_match:
                field = key_match.group(1)

                # Remove the tailing ":" from the filter.
                filtername = value_match.group(1)
                filtername = filtername[:-1]

                # The value may be encoded as json.
                value = value_match.group(2)
                try:
                    value = self.api.load_json(value)
                except Exception as err:
                    LOG.debug(err, exc_info=False)
                    raise errors.BadRequest(
                        detail="The value of the filter '{}' is not a JSON "\
                            "object.".format(filtername),
                        source_parameter=key
                    )

                # Add the filter.
                filters.append((field, filtername, value))
        return filters

    @cached_property
    def japi_fields(self):
        """
        Returns the fields, which should be included in the response
        (sparse fieldset).

        .. code-block:: python3

            >>> # /api/User?fields[User]=email,name&fields[Post]=comments
            >>> request.japi_fields
            ... {"User": ["email", "name"], "Post": ["comments"]}

        :seealso: http://jsonapi.org/format/#fetching-sparse-fieldsets
        """
        fields = dict()

        FIELDS_RE = re.compile(r"fields\[([A-z0-9_]+)\]")

        for key, value in self.query.items():
            match = re.fullmatch(FIELDS_RE, key)
            if match:
                typename = match.group(1)
                type_fields = value[0].split(",")
                type_fields = [
                    item.strip() for item in type_fields if item.strip()
                ]

                fields[typename] = type_fields
        return fields

    @cached_property
    def japi_include(self):
        """
        Returns the names of the relationships, which should be included into
        the response.

        .. code-block:: python3

            >>> # /api/Post?include=author,comments.author
            >>> req.japi_include
            ... [["author"], ["comments", "author"]

        :seealso: http://jsonapi.org/format/#fetching-includes
        """
        include = self.get_query_argument("include", "")
        include = [path.split(".") for path in include.split(",") if path]
        return include

    @cached_property
    def japi_sort(self):
        """
        Returns a list with two tuples, describing how the output should be
        sorted:

        .. code-block:: python3

            >>> # /api/Post?sort=name,-age
            ... [("+", "name"), ("-", "age")]

        :seealso: http://jsonapi.org/format/#fetching-sorting
        """
        tmp = self.get_query_argument("sort")
        tmp = tmp.split(",") if tmp else list()

        sort = list()
        for field in tmp:
            field = field.strip()
            if field[0] == "-":
                sort.append(("-", field[1:]))
            elif field[0] == "+":
                sort.append(("+", field[1:]))
            else:
                sort.append(("+", field))
        return sort

    @cached_property
    def json(self):
        """
        Parses the :attr:`body` and returns the result.

        .. seealso::

            *   :attr:`has_json`
            *   :meth:`jsonapi.base.api.API.load_json`
        """
        try:
            if not isinstance(self.body, str):
                text = self.body.decode()
            else:
                text = self.body

            json = self.api.load_json(text)
        except (UnicodeDecodeError, ValueError) as err:
            LOG.debug(err, exc_info=False)
            json = None
            self.has_json = False
        else:
            self.has_json = True
        return json

    @cached_property
    def has_json(self):
        """
        Returns True, if the body contains a json document.
        """
        # Parse the body (This will also set *has_json*)
        self.json
        return self.has_json

    def print(self):
        """
        Prints all information about the request to *stdout*. This method
        is only used for *debugging*.
        """
        print("Request")
        print("-------")
        print("\t", "uri", self.uri)
        print("\t", "method", self.method)
        print("\t", "headers", self.headers)
        print("\t", "body", self.body)
        print("\t", "japi_uri_arguments", self.japi_uri_arguments)
        print("\t", "parsed_uri", self.parsed_uri)
        print("\t", "query", self.query)
        print("\t", "japi_page_number", self.japi_page_number)
        print("\t", "japi_page_size", self.japi_page_size)
        print("\t", "japi_paginate", self.japi_paginate)
        print("\t", "japi_offset", self.japi_offset)
        print("\t", "japi_limit", self.japi_limit)
        print("\t", "japi_filters", self.japi_filters)
        print("\t", "japi_fields", self.japi_fields)
        print("\t", "japi_include", self.japi_include)
        print("\t", "japi_sort", self.japi_sort)
        print("\t", "json", self.json)
        print("\t", "has_json", self.has_json)
        return None
