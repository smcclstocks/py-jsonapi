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

# std
from collections import OrderedDict

# local
from .. import errors
from .base import BaseHandler


class RelatedHandler(BaseHandler):
    """
    Returns the related resources for the resource.
    """

    def __init__(self, api, request):
        """
        """
        super().__init__(api, request)

        self.typename = request.japi_uri_arguments.get("type")
        self.relname = request.japi_uri_arguments.get("relname")
        self.serializer = self.api.get_serializer(self.typename, None)

        # The resource is loaded in *prepare()*
        self.resource_id = request.japi_uri_arguments.get("id")
        self.resource = None
        return None

    def prepare(self):
        """
        """
        # If the serializer is None, the typename is not known to the API.
        if self.serializer is None:
            raise errors.NotFound()

        # Make sure, that the relationship exists.
        if not self.serializer.has_relationship(self.relname):
            raise errors.NotFound()

        # Make sure, the content type is valid.
        if self.request.media_type != "application/vnd.api+json":
            raise errors.UnsupportedMediaType()

        # Load the resource.
        self.resource = self.db.get((self.typename, self.resource_id))
        if self.resource is None:
            raise errors.NotFound()
        return None

    def get(self):
        """
        Handles a GET request.

        http://jsonapi.org/format/#fetching-relationships
        """
        # Use the database *fetch_includes()* function, to fetch all resources
        # from the relationship.
        related_resources = self.db.fetch_includes(
            [self.resource], [(self.relname,)]
        )

        # Build the document.
        data = list()
        for resource in related_resources.values():
            typename = self.api.get_typename(resource)
            serializer = self.api.get_serializer(typename)
            data.append(serializer.serialize_resource(
                resource, fields=self.request.japi_fields.get(typename)
            ))

        meta = OrderedDict()
        links = OrderedDict()

        # Create the response
        self.response.headers["content-type"] = "application/vnd.api+json"
        self.response.status_code = 200
        self.response.body = self.api.dump_json(OrderedDict([
            ("data", data),
            ("meta", meta),
            ("links", links),
            ("jsonapi", self.api.jsonapi_object)
        ]))
        return None
