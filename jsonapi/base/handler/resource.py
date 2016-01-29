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
from .. import validators
from .base import BaseHandler


class ResourceHandler(BaseHandler):
    """
    Handles a resource endpoint.
    """

    def __init__(self, api, request):
        """
        """
        super().__init__(api, request)
        self.typename = request.japi_uri_arguments.get("type")
        self.serializer = api.get_serializer(self.typename, None)

        # We will load the resource in *prepare()*.
        self.resource_id = self.request.japi_uri_arguments.get("id")
        self.resource = None
        return None

    def prepare(self):
        """
        """
        # The typename is not mapped to a serializer. So the the type does not
        # exist.
        if self.serializer is None:
            raise errors.NotFound()

        # Make sure, the content type is valid.
        if self.request.media_type != "application/vnd.api+json":
            raise errors.UnsupportedMediaType()

        # Load the resource
        self.resource = self.db.get((self.typename, self.resource_id))
        if self.resource is None:
            raise errors.NotFound()
        return None

    def get(self):
        """
        Handles a GET request.

        http://jsonapi.org/format/#fetching-resources
        """
        # Fetch the included resources.
        included_resources = self.db.fetch_includes(
            [self.resource], self.request.japi_include
        )

        # Build the response document.
        typename = self.api.get_typename(self.resource)
        serializer = self.api.get_serializer(typename)
        data = serializer.serialize_resource(
            self.resource, fields=self.request.japi_fields.get(typename)
        )

        included = list()
        for resource in included_resources.values():
            typename = self.api.get_typename(self.resource)
            serializer = self.api.get_serializer(typename)
            data = serializer.serialize_resource(
                self.resource, fields=self.request.japi_fields.get(typename)
            )

        meta = OrderedDict()
        links = OrderedDict()

        # Put all together
        self.response.headers["content-type"] = "application/vnd.api+json"
        self.response.status_code = 200
        self.response.body = self.api.dump_json(OrderedDict([
            ("data", data),
            ("included", included),
            ("meta", meta),
            ("links", links),
            ("jsonapi", self.api.jsonapi_object)
        ]))
        return None

    def patch(self):
        """
        Handles a PATCH request.

        http://jsonapi.org/format/#crud-updating
        """
        data = self.request.json.get("data", dict())
        validators.assert_resource_document(data, source_pointer="/data/")

        # Update the attributes
        attributes = data.get("attributes", dict())
        self.serializer.jupdate_attributes(self.resource, attributes)

        # Update the relationships
        relationships = data.get("relationships", dict())
        relationships = self.db.load_japi_relationships(relationships)
        for relname, relatives in relationships.items():
            self.serializer.jupdate_relationships(self.resource, relname, relatives)

        # Save the resource
        self.db.save([self.resource])
        self.db.commit()

        # Create the response
        typename = self.api.get_typename(self.resource)
        serializer = self.api.get_serializer(typename)
        data = serializer.serialize_resource(
            self.resource, fields=self.request.japi_fields.get(typename)
        )

        included = list()
        meta = OrderedDict()
        links = OrderedDict()

        # Put all together.
        self.response.headers["content-type"] = "application/vnd.api+json"
        self.response.status_code = 200
        self.response.body = self.api.dump_json(OrderedDict([
            ("data", data),
            ("included", included),
            ("meta", meta),
            ("links", links),
            ("jsonapi", self.api.jsonapi_object)
        ]))
        return None

    def delete(self):
        """
        Handles a DELETE request.
        """
        self.db.delete([self.resource])
        self.db.commit()

        # Create the response.
        self.response.status_code = 204
        return None
