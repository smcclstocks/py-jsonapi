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
from ..serializer import serialize_many
from .base import BaseHandler


class RelatedHandler(BaseHandler):
    """
    Returns the related resources for the resource.
    """

    def __init__(self, api, db, request):
        """
        """
        super().__init__(api, db, request)
        self.typename = request.japi_uri_arguments.get("type")
        self.relname = request.japi_uri_arguments.get("relname")

        # Initialised after the resource has been loaded.
        self.real_typename = None

        # The resource is loaded in *prepare()*
        self.resource_id = request.japi_uri_arguments.get("id")
        self.resource = None
        return None

    def prepare(self):
        """
        """
        if self.request.content_type[0] != "application/vnd.api+json":
            raise errors.UnsupportedMediaType()
        if not self.api.has_type(self.typename):
            raise errors.NotFound()

        # Load the resource.
        self.resource = self.db.get((self.typename, self.resource_id))
        if self.resource is None:
            raise errors.NotFound()

        self.real_typename = self.api.get_typename(self.resource)
        return None

    def get(self):
        """
        Handles a GET request.

        http://jsonapi.org/format/#fetching-relationships
        """
        resources = self.db.get_relatives([self.resource], [[self.relname]])
        resources = resources.values()

        included_resources = self.db.get_relatives(
            resources, self.request.japi_include
        )

        # Build the document.
        data = serialize_many(resources, fields=self.request.japi_fields)
        included = serialize_many(
            included_resources.values(), fields=self.request.japi_fields
        )
        meta = OrderedDict()
        links = OrderedDict()

        # Create the response
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
