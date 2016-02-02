#!/usr/bin/env python3

"""
jsonapi.base.handler.relationship
=================================

:license: GNU Affero General Public License v3
:copyright: 2016 by Benedikt Schmitt <benedikt@benediktschmitt.de>
"""

# std
from collections import OrderedDict

# local
from .. import errors
from .. import validators
from ..utilities import ensure_identifier
from .base import BaseHandler


class RelationshipHandler(BaseHandler):
    """
    Handles the relationship endpoint.
    """

    def __init__(self, api, request):
        """
        """
        super().__init__(api, request)
        self.typename = request.japi_uri_arguments.get("type")
        self.relname = request.japi_uri_arguments.get("relname")

        # We load the schema and serializer in prepare(), because we need to
        # know the real typename of the resource. This is only necessary, if
        # resource is a subtype of self.typename.
        self.real_typename = None
        self.schema = None
        self.serializer = None
        self.relationship = None

        # The resource is loaded in *prepare()*
        self.resource_id = self.request.japi_uri_arguments.get("id")
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
        self.serializer = self.api.get_serializer(self.real_typename)

        # Check if the relationship exists.
        if not self.relname in self.schema.relationships:
            raise errors.NotFound()
        self.relationship = self.schema.relationships[self.relname]
        return None

    def build_body(self):
        """
        Serializes the relationship and creates the JSONapi body.
        """
        document = self.serializer.serialize_relationship(
            self.resource, self.relname
        )

        links = document.setdefault("links", OrderedDict())
        links["self"] = self.api.reverse_url(
            typename=self.typename, endpoint="relationship", id=self.resource_id,
            relname=self.relname
        )
        links["related"] = self.api.reverse_url(
            typename=self.typename, endpoint="related", id=self.resource_id,
            relname=self.relname
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
        reldoc = self.request.json
        validators.assert_relationship_document(reldoc)

        # Get the new relatives
        relative_ids = reldoc["data"]
        relative_ids = [
            ensure_identifier(self.api, item) for item in relative_ids
        ]

        relatives = self.db.get_many(relative_ids)
        relatives = [relatives[(item[0], item[1])] for item in relative_ids]

        # Extend the relationship
        self.relationship.extend(self.resource, relatives)

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
        reldoc = self.request.json
        validators.assert_relationship_document(reldoc)

        if self.relationship.to_one:
            relative_id = reldoc["data"]
            relative_id = ensure_identifier(self.api, relative_id)

            relative = self.db.get(relative_id)

            self.relationship.set(self.resource, relative)
        else:
            relative_ids = reldoc["data"]
            relative_ids = [
                ensure_identifier(self.api, item) for item in relative_ids
            ]

            relatives = self.db.get_many(relative_ids)
            relatives = [relatives[(item[0], item[1])] for item in relative_ids]

            self.relationship.set(self.resource, relatives)

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
        self.relationship.delete(self.resource)

        # Save the changes
        self.db.save([self.resource])
        self.db.commit()

        # Build the response
        self.response.headers["content-type"] = "application/vnd.api+json"
        self.response.status_code = 200
        self.response.body = self.build_body()
        return None
