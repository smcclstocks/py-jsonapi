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
