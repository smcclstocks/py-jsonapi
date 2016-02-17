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
jsonapi.base.handler.relationship
=================================
"""

# std
from collections import OrderedDict

# local
from .. import errors
from .. import validators
from ..serializer import serialize_many
from .base import BaseHandler


class RelationshipHandler(BaseHandler):
    """
    Handles the relationship endpoint.
    """

    def __init__(self, api, db, request):
        """
        """
        super().__init__(api, db, request)
        self.typename = request.japi_uri_arguments.get("type")
        self.relname = request.japi_uri_arguments.get("relname")

        # Initiliased, after the resource has been loaded.
        self.real_typename = None

        # The resource is loaded in *prepare()*
        self.resource_id = self.request.japi_uri_arguments.get("id")
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

        # Check if the relationship exists.
        schema = self.api.get_schema(self.real_typename)
        if not self.relname in schema.relationships:
            raise errors.NotFound()

        self.relationship = schema.relationships[self.relname]
        return None

    def build_body(self):
        """
        Serializes the relationship and creates the JSONapi body.
        """
        serializer = self.api.get_serializer(self.real_typename)
        document = serializer.serialize_relationship(
            self.resource, self.relname
        )

        links = document.setdefault("links", OrderedDict())
        links["self"] = self.api.reverse_url(
            typename=self.typename, endpoint="relationship",
            id=self.resource_id, relname=self.relname
        )
        links["related"] = self.api.reverse_url(
            typename=self.typename, endpoint="related",
            id=self.resource_id, relname=self.relname
        )

        document.setdefault("jsonapi", self.api.jsonapi_object)

        body = self.api.dump_json(document)
        return body

    def get(self):
        """
        Handles a GET request.

        http://jsonapi.org/format/#fetching-relationships
        """
        self.response.headers["content-type"] = "application/vnd.api+json"
        self.response.status_code = 200
        self.response.body = self.build_body()
        return None

    def post(self):
        """
        Handles a POST request.

        This method is only allowed for to-many relationships.

        http://jsonapi.org/format/#crud-updating-relationships
        """
        # This method is only allowed for *to-many* relationships.
        if not self.relationship.to_many:
            raise errors.MethodNotAllowed()

        # Get the relationship document from the request.
        relationship_object = self.request.json
        validators.assert_relationship_object(relationship_object)

        # Extend the relationship.
        unserializer = self.api.get_unserializer(self.real_typename)
        unserializer.extend_relationship(
            self.db, self.resource, self.relname, relationship_object
        )

        # Save the resource.
        self.db.save([self.resource])
        self.db.commit()

        # Build the response
        self.response.headers["content-type"] = "application/vnd.api+json"
        self.response.status_code = 200
        self.response.body = self.build_body()
        return None

    def patch(self):
        """
        Handles a PATCH request.

        http://jsonapi.org/format/#crud-updating-relationships
        """
        # Make sure the request contains a valid JSONapi relationship object.
        relationship_object = self.request.json
        validators.assert_relationship_object(relationship_object)

        # Patch the relationship.
        unserializer = self.api.get_unserializer(self.real_typename)
        unserializer.update_relationship(
            self.db, self.resource, self.relname, relationship_object
        )

        # Save thte changes.
        self.db.save([self.resource])
        self.db.commit()

        # Build the response
        self.response.headers["content-type"] = "application/vnd.api+json"
        self.response.status_code = 200
        self.response.body = self.build_body()
        return None

    def delete(self):
        """
        Handles a DELETE request.
        """
        unserializer = self.api.get_unserializer(self.real_typename)
        unserializer.clear_relationship(self.resource, self.relname)

        # Save the changes
        self.db.save([self.resource])
        self.db.commit()

        # Build the response
        self.response.headers["content-type"] = "application/vnd.api+json"
        self.response.status_code = 200
        self.response.body = self.build_body()
        return None
