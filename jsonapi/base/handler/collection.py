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
from ..pagination import Pagination
from .base import BaseHandler


class CollectionHandler(BaseHandler):
    """
    Handles the collection endpoint.
    """

    def __init__(self, api, request):
        """
        """
        super().__init__(api, request)

        self.typename = request.japi_uri_arguments.get("type")
        self.serializer = api.get_serializer(self.typename, None)
        return None

    def prepare(self):
        """
        """
        # The typename is not mapped to a serializer. So the the type does not
        # exist.
        if self.serializer is None:
            raise errors.NotFound()

        # Make sure, the content type is valid.
        if self.request.content_type[0] != "application/vnd.api+json":
            raise errors.UnsupportedMediaType()
        return None

    def get(self):
        """
        Handles a GET request. This means to fetch many resourcs from the
        collection and return it.

        http://jsonapi.org/format/#fetching-resources
        """
        # All requested resources.
        if self.request.japi_paginate:
            offset = self.request.japi_page_offset
            limit = self.request.japi_page_limit
        else:
            offset = self.request.japi_offset
            limit = self.request.japi_limit

        resources = self.db.query(
            self.typename,
            order=self.request.japi_sort,
            limit=limit,
            offset=offset,
            filters=self.request.japi_filters
        )

        # Fetch all related resources, which should be included.
        included_resources = self.db.fetch_includes(
            resources, self.request.japi_include
        )

        # Build the response.
        data = list()
        for resource in resources:
            typename = self.api.get_typename(resource)
            serializer = self.api.get_serializer(typename)
            data.append(serializer.serialize_resource(
                resource, fields=self.request.japi_fields.get(typename)
            ))

        included = list()
        for resource in included_resources.values():
            typename = self.api.get_typename(resource)
            serializer = self.api.get_serializer(typename)
            included.append(serializer.serialize_resource(
                resource, fields=self.request.japi_fields.get(typename)
            ))

        meta = OrderedDict()
        links = OrderedDict()

        # Add the pagination links, if necessairy.
        if self.request.japi_paginate:
            total_resources = self.db.query_size(
                self.typename,
                filters=self.request.japi_filters
            )

            pagination = Pagination(self.request, total_resources)
            meta.update(pagination.json_meta)
            links.update(pagination.json_links)

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

    def post(self):
        """
        Handles a POST request. This means to create a new resource and to
        return it.

        http://jsonapi.org/format/#crud-creating
        """
        d = self.request.json.get("data", dict())
        validators.assert_resource_document(d, source_pointer="/data/")

        # Load the related resources.
        relationships = d.get("relationships", dict())
        relationships = self.db.load_japi_relationships(relationships)

        # Get the attributes.
        attributes = d.get("attributes", dict())

        # Get the meta values.
        meta = d.get("meta", dict())

        # Create a new resource.
        new_resource = self.serializer.create_resource(
            attributes, relationships, meta
        )

        # Save the resources.
        self.db.save([new_resource])
        self.db.commit()

        # Crate the response.
        data = self.serializer.serialize_resource(
            new_resource, fields=self.request.japi_fields.get(self.typename)
        )

        links = data.setdefault("links", dict())
        links["self"] = self.api.reverse_url(
            typename=self.typename, endpoint="resource", id=data["id"]
        )

        # Put everything together.
        self.response.headers["content-type"] = "application/vnd.api+json"
        self.response.headers["location"] = links["self"]
        self.response.status_code = 201
        self.response.body = self.api.dump_json(OrderedDict([
            ("data", data),
            ("links", links),
            ("jsonapi", self.api.jsonapi_object)
        ]))
        return None
