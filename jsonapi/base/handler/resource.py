#!/usr/bin/env python3

"""
jsonapi.base.handler.resource
=============================

:license: GNU Affero General Public License v3
:copyright: 2016 by Benedikt Schmitt <benedikt@benediktschmitt.de>
"""

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

        # The *typename* is not sufficent for getting the correct schema and
        # serializer for the resource if the resource is a subtype of
        # *self.typename*. So we initialize this attributes in *prepare()*.
        self.real_typename = None
        self.schema = None
        self.serializer = None

        # We will load the resource in *prepare()*.
        self.resource_id = self.request.japi_uri_arguments.get("id")
        self.resource = None
        return None

    def prepare(self):
        """
        """
        if not self.api.has_type(self.typename):
            raise errors.NotFound()

        # Make sure, the content type is valid.
        if self.request.content_type[0] != "application/vnd.api+json":
            raise errors.UnsupportedMediaType()

        # Load the resource
        self.resource = self.db.get((self.typename, self.resource_id))
        if self.resource is None:
            raise errors.NotFound()

        self.real_typename = self.api.get_typename(self.resource)
        self.schema = self.api.get_schema(self.real_typename)
        self.serializer = self.api.get_serializer(self.real_typename)
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
        data = self.serializer.serialize_resource(
            self.resource, fields=self.request.japi_fields.get(self.typename)
        )

        included = list()
        for resource in included_resources.values():
            typename = self.api.get_typename(resource)
            serializer = self.api.get_serializer(typename)
            included.append(serializer.serialize_resource(
                resource, fields=self.request.japi_fields.get(typename)
            ))

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
        self.serializer.update_attributes(self.resource, attributes)

        # Update the relationships
        relationships = data.get("relationships", dict())
        relationships = self.db.load_japi_relationships(relationships)
        for relname, relatives in relationships.items():
            self.serializer.update_relationships(self.resource, relname, relatives)

        # Save the resource
        self.db.save([self.resource])
        self.db.commit()

        # Create the response
        data = self.serializer.serialize_resource(
            self.resource, fields=self.request.japi_fields.get(self.typename)
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
