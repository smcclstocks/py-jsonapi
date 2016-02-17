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
jsonapi.base.pagination
=======================

This module contains only a helper for the pagination feature:
http://jsonapi.org/format/#fetching-pagination
"""

# std
from collections import OrderedDict
import math
import urllib

# third party
from cached_property import cached_property


class Pagination(object):
    """
    A helper class for the pagination.

    The fist page has the number *1*.

    :arg jsonapi.base.request.Request request:
        The current jsonapi request
    :arg int total_resources:
        The total number of resources, which would have been returned without
        the pagination.

    .. seealso::

        *   :attr:`jsonapi.base.request.Request.japi_page_size`
        *   :attr:`jsonapi.base.request.Request.japi_page_number`
        *   :attr:`jsonapi.base.request.Request.japi_paginate`
        *   http://jsonapi.org/format/#fetching-pagination
    """

    def __init__(self, request, total_resources):
        """
        """
        assert request.japi_paginate

        self.request = request

        # Get the current page number and size.
        self.current_page = self.request.japi_page_number
        self.page_size = self.request.japi_page_size

        # Get the number of resources
        self.total_resources = total_resources
        self.total_pages = math.ceil(self.total_resources/self.page_size)

        # Build all links
        self.link_self = self._page_link(self.current_page, self.page_size)
        self.link_first = self._page_link(1, self.page_size)
        self.link_last = self._page_link(self.total_pages, self.page_size)

        self.has_prev = (self.current_page > 1)
        self.link_prev = self._page_link(self.current_page - 1, self.page_size)

        self.has_next = (self.current_page < self.total_pages)
        self.link_next = self._page_link(self.current_page + 1, self.page_size)
        return None

    def _page_link(self, page_number, page_size):
        parsed_uri = self.request.parsed_uri
        query = urllib.parse.urlencode({
            "page[number]": page_number,
            "page[size]": page_size
        })
        uri = "{scheme}://{netloc}{path}?{query}".format(
            scheme=parsed_uri.scheme,
            netloc=parsed_uri.netloc,
            path=parsed_uri.path,
            query=query
        )
        return uri

    @cached_property
    def json_meta(self):
        """
        Must be included in the top-level meta object.
        """
        d = OrderedDict()
        d["total-pages"] = self.total_pages
        d["total-resources"] = self.total_resources
        d["page"] = self.current_page
        d["page-size"] = self.page_size
        return d

    @cached_property
    def json_links(self):
        """
        Must be included in the top-level links object.
        """
        d = OrderedDict()
        d["self"] = self.link_self
        d["first"] = self.link_first
        d["last"] = self.link_last
        if self.has_prev:
            d["prev"] = self.link_prev
        if self.has_next:
            d["next"] = self.link_next
        return d
