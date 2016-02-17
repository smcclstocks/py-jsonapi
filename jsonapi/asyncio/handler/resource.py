#!/usr/bin/env python3

"""
jsonapi.asyncio.handler.resource
================================

:license: GNU Affero General Public License v3
"""

# std
from collections import OrderedDict

# local
from jsonapi.base import errors
from jsonapi.base import validators
from jsonapi.base.serializer import serialize_many
from .base import BaseHandler


class ResourceHandler(BaseHandler):
    """
    Handles a resource endpoint.
    """

    def __init__(self, api, db, request):
        """
        """
        super().__init__(api, db, request)
        self.typename = request.japi_uri_arguments.get("type")

        # The *typename* is not sufficent for getting the correct schema and
        # serializer for the resource if the resource is a subtype of
        # *self.typename*. So we initialize this attributes in *prepare()*.
        self.real_typename = None

        # We will load the resource in *prepare()*.
        self.resource_id = self.request.japi_uri_arguments.get("id")
        self.resource = None
        return None

    async def prepare(self):
        """
        """
        if self.request.content_type[0] != "application/vnd.api+json":
            raise errors.UnsupportedMediaType()
        if not self.api.has_type(self.typename):
            raise errors.NotFound()

        # Load the resource
        self.resource = await self.db.get((self.typename, self.resource_id))
        if self.resource is None:
            raise errors.NotFound()

        self.real_typename = self.api.get_typename(self.resource, None)
        return None

    async def get(self):
        """
        Handles a GET request.

        http://jsonapi.org/format/#fetching-resources
        """
        # Fetch the included resources.
        included_resources = await self.db.get_relatives(
            [self.resource], self.request.japi_include
        )

        # Build the response document.
        serializer = self.api.get_serializer(self.real_typename)
        data = serializer.serialize_resource(
            self.resource, fields=self.request.japi_fields.get(self.typename)
        )

        included = serialize_many(
            included_resources.values(), self.request.japi_fields
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

    async def patch(self):
        """
        Handles a PATCH request.

        http://jsonapi.org/format/#crud-updating
        """
        data = self.request.json.get("data", dict())
        validators.assert_resource_object(data, source_pointer="/data/")

        # Get the unserializer
        unserializer = self.api.get_unserializer(self.real_typename)
        await unserializer.update_resource(self.db, self.resource, data)

        # Save the resource
        self.db.save([self.resource])
        await self.db.commit()

        # Create the response
        serializer = self.api.get_serializer(self.real_typename)
        data = serializer.serialize_resource(
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

    async def delete(self):
        """
        Handles a DELETE request.
        """
        self.db.delete([self.resource])
        await self.db.commit()

        # Create the response.
        self.response.status_code = 204
        return None
