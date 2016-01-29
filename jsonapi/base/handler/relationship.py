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
        self.serializer = api.get_serializer(self.typename, None)

        # The resource is loaded in *prepare()*
        self.resource_id = self.request.japi_uri_arguments.get("id")
        self.resource = None
        return None

    def prepare(self):
        """
        """
        # Make sure, the typename is known to the API.
        if self.serializer is None:
            raise errors.NotFound()

        # Make sure, the relationship exists.
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
        if not self.serializer.is_to_many_relationship(self.relname):
            raise errors.MethodNotAllowed()

        # Get the relationship document from the request.
        relationship = self.request.json
        validators.assert_relationship_document(relationship)

        # Get the new relatives
        relative_ids = relationship["data"]
        relative_ids = [
            ensure_identifier(self.api, item) for item in relative_ids
        ]

        relatives = self.db.get_many(relative_ids)
        relatives = [relatives[(item[0], item[1])] for item in relative_ids]

        # Get the meta object
        meta = relationship.get("meta", dict())

        # Extend the relationship
        self.serializer.jextend_relationship(
            self.resource, self.relname, relatives, meta
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
        relationship = self.request.json
        validators.assert_relationship_document(relationship)

        # Get the related resources.
        relative_ids = relationship["data"]
        relative_ids = [
            ensure_identifier(self.api, item) for item in relative_ids
        ]

        relatives = self.db.get_many(relative_ids)
        relatives = [relatives[(item[0], item[1])] for item in relative_ids]

        # Get the meta object.
        meta = relationship.get("meta", dict())

        # Update the relationship.
        self.serializer.jupdate_relationship(
            self.resource, self.relname, relatives, meta
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
        self.serializer.jdelete_relationship(
            self.resource, self.relname, meta=dict()
        )

        # Save the changes
        self.db.save([self.resource])
        self.db.commit()

        # Build the response
        self.response.headers["content-type"] = "application/vnd.api+json"
        self.response.status_code = 200
        self.response.body = self.build_body()
        return None
