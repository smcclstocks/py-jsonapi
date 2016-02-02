#!/usr/bin/env python3

"""
jsonapi.base.handler.related
============================

:license: GNU Affero General Public License v3
:copyright: 2016 by Benedikt Schmitt <benedikt@benediktschmitt.de>
"""

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

        # Initialized, when we know the exact typename of the resource.
        self.real_typename = None
        self.schema = None
        self.relationship = None

        # The resource is loaded in *prepare()*
        self.resource_id = request.japi_uri_arguments.get("id")
        self.resource = None
        return None

    def prepare(self):
        """
        """
        if not self.api.has_type(self.typename):
            raise errors.NotFound()

        if self.request.content_type[0] != "application/vnd.api+json":
            raise errors.UnsupportedMediaType()

        # Load the resource.
        self.resource = self.db.get((self.typename, self.resource_id))
        if self.resource is None:
            raise errors.NotFound()

        self.real_typename = self.api.get_typename(self.resource)
        self.schema = self.api.get_schema(self.real_typename)
        self.relationship = self.schema.relationships.get(self.relname)

        # Make sure the relationship exists.
        if self.relationship is None:
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
