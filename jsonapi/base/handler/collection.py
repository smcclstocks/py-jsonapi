#!/usr/bin/env python3

"""
jsonapi.base.handler.collection
===============================

:license: GNU Affero General Public License v3
:copyright: 2016 by Benedikt Schmitt <benedikt@benediktschmitt.de>
"""

# std
from collections import OrderedDict

# local
from .. import errors
from .. import validators
from ..serializer import serialize_many
from ..pagination import Pagination
from .base import BaseHandler


class CollectionHandler(BaseHandler):
    """
    Handles the collection endpoint.
    """

    def __init__(self, api, db, request):
        """
        """
        super().__init__(api, db, request)
        self.typename = request.japi_uri_arguments.get("type")
        return None

    def prepare(self):
        """
        """
        if self.request.content_type[0] != "application/vnd.api+json":
            raise errors.UnsupportedMediaType()
        if not self.api.has_type(self.typename):
            raise errors.NotFound()
        return None

    def get(self):
        """
        Handles a GET request. This means to fetch many resourcs from the
        collection and return it.

        http://jsonapi.org/format/#fetching-resources
        """
        # Fetch the requested resources.
        if self.request.japi_paginate:
            offset = self.request.japi_page_offset
            limit = self.request.japi_page_limit
        else:
            offset = self.request.japi_offset
            limit = self.request.japi_limit

        resources = self.db.query(
            self.typename, order=self.request.japi_sort, limit=limit,
            offset=offset, filters=self.request.japi_filters
        )

        # Fetch all related resources, which should be included.
        included_resources = self.db.get_relatives(
            resources, self.request.japi_include
        )

        # Build the response.
        data = serialize_many(resources, fields=self.request.japi_fields)
        included = serialize_many(
            included_resources.values(), fields=self.request.japi_fields
        )
        meta = OrderedDict()
        links = OrderedDict()

        # Add the pagination links, if necessairy.
        if self.request.japi_paginate:
            total_resources = self.db.query_size(
                self.typename, filters=self.request.japi_filters
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
        # Make sure the request contains a valid JSON resource object.
        resource_object = self.request.json.get("data", dict())
        validators.assert_resource_object(
            resource_object, source_pointer="/data/"
        )

        # Check if the *type* is supported by this collection endpoint.
        if resource_object["type"] != self.typename:
            raise errors.Conflict()

        # Create the new resource.
        unserializer = self.api.get_unserializer(self.typename)
        resource = unserializer.create_resource(self.db, resource_object)

        # Save the resources.
        self.db.save([resource])
        self.db.commit()

        # Crate the response.
        serializer = self.api.get_serializer(self.typename)
        data = serializer.serialize_resource(
            resource, fields=self.request.japi_fields.get(self.typename)
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
