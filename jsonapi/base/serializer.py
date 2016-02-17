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
jsonapi.base.serializer
=======================

A JSONapi serializer and unserializer based on the
:class:`~jsonapi.base.schema.Schema`.
"""

# std
from collections import OrderedDict
import logging

# local
from . import errors
from .utilities import ensure_identifier_object


__all__ = [
    "Unserializer",
    "Serializer"
]


LOG = logging.getLogger(__file__)


class Unserializer(object):
    """
    Takes JSONapi documents and updates a resource.

    :arg jsonapi.base.schema.Schema schema:
        The schema used to update resources
    """

    def __init__(self, schema):
        self.schema = schema
        return None

    def _load_relationships_object(self, db, relationships_object):
        """
        Loads all resources referenced in the JSONapi relationships object
        *relationships_object* and returns a dictionary, which maps the
        relationship names to the related resources.

        :arg jsonapi.base.database.Session db:
            The database session used to query the related resources.
        :arg dict relationships_object:
            A JSONapi relationships object

        :raises jsonapi.base.errors.NotFound:
            If a relative does not exist.

        :seealso: http://jsonapi.org/format/#document-resource-object-relationships
        """
        # Collect the identifiers.
        identifiers = set()
        for relname, relobj in relationships_object.items():
            reldata = relobj.get("data")

            # *to-one* relationship (with target)
            # -> a single resource identifier object
            if isinstance(reldata, dict):
                identifiers.add((reldata["type"], reldata["id"]))

            # *to-many* relationship
            # -> a list of resource identifier objects
            elif isinstance(reldata, list):
                identifiers.update(
                    (item["type"], item["id"]) for item in reldata
                )

        # Load the resources
        relatives = db.get_many(identifiers, required=True)

        # Map the relationship names back to the related resources.
        result = dict()
        for relname, relobj in relationships_object.items():
            if "data" in relobj:
                reldata = relobj["data"]

                # *to-one* relationship with no target
                if reldata is None:
                    result[relname] = None
                # *to-one* relationship with target
                elif isinstance(reldata, dict):
                    identifier = (reldata["type"], reldata["id"])
                    result[relname] = relatives[identifier]
                # *to-many* relationship
                elif isinstance(reldata, list):
                    identifiers = [
                        (item["type"], item["id"]) for item in reldata
                    ]
                    result[relname] = [
                        relatives[identifier] for identifier in identifiers
                    ]
        return result

    def create_resource(self, db, resource_object):
        """
        Creates a new resource using the JSONapi resource object
        *resource object*.

        :arg jsonapi.base.database.Session db:
            The database session used to query related resources.
        :arg d resource_object:
            A JSONapi resource object, containing the initial values for
            the attributes and relationships.

        :seealso: http://jsonapi.org/format/#document-resource-objects
        """
        assert resource_object["type"] == self.schema.typename

        # Load all relatives
        relationships = resource_object.get("relationships", dict())
        relationships = self._load_relationships_object(db, relationships)

        # Get the attributes
        attributes = resource_object.get("attributes", dict())

        # Create the new resource.
        fields = dict()
        fields.update(attributes)
        fields.update(relationships)
        resource = self.schema.constructor.create(**fields)
        return resource

    def update_resource(self, db, resource, resource_object):
        """
        Updates the resource *resource* using the JSONapi resource object
        *resource_object*.

        :arg jsonapi.base.database.Session db:
            The database session used to query related resources.
        :arg resource:
            The resource, which is updated
        :arg dict resource_object:
            A JSONapi resource object containing the new attribute and
            relationship values.

        :seealso: http://jsonapi.org/format/#document-resource-objects
        :seealso: http://jsonapi.org/format/#crud-updating
        """
        assert resource_object["id"] == self.schema.id_attribute.get(resource)
        assert resource_object["type"] == self.schema.typename

        # Save all errors, which occur during the update.
        error_list = errors.ErrorList()

        # Update the attributes
        if "attributes" in resource_object:
            try:
                self.update_attributes(resource, resource_object["attributes"])
            except errors.Error as err:
                error_list.append(err)
            except errors.ErrorList as err:
                error_list.extend(err)

        # Update the relationships
        if "relationships" in resource_object:
            rels_object = resource_object["relationships"]
            for rel_name, rel_object in rels_object.items():
                try:
                    self.update_relationship(db, resource, rel_name, rel_object)
                except errors.Error as err:
                    error_list.append(err)
                except errors.ErrorList as err:
                    error_list.extend(err)

        if error_list:
            raise error_list
        return None

    def update_attributes(self, resource, attributes_object):
        """
        Updates the attributes of the resource *resource* using the JSONapi
        attributes object *attributes_object*.

        :arg resource:
            The resource, whichs attributes are updated.
        :arg dict attributes_object:
            A JSONapi attributes object, containing the new attribute values.

        :seealso: http://jsonapi.org/format/#document-resource-object-attributes
        """
        # Save all errors which occur in this error list. This way, the client
        # can get a feedback about the validation of all attribute values.
        error_list = errors.ErrorList()

        for name, value in attributes_object.items():
            attribute = self.schema.attributes[name]
            try:
                attribute.set(resource, value)
            except errors.Error as err:
                error_list.append(err)
            except errors.ErrorList as err:
                error_list.extend(err)

        if error_list:
            raise error_list
        return None

    def update_relationship(
        self, db, resource, relationship_name, relationship_object
        ):
        """
        Updates the relationship with the name *relationship_name* of the
        resource *resource* using the JSONapi relationship object
        *relationship_object*.

        :arg jsonapi.base.database.Session db:
            The database session used to query related resources.
        :arg resource:
            The resource, whichs relationships are updated.
        :arg str relationship_name:
            The name of the relationship, which is updated.
        :arg dict relationship_object:
            A JSONapi relationship object, containing the new relationship
            values.

        :seealso: http://jsonapi.org/format/#document-resource-object-relationships
        :seealso: http://jsonapi.org/format/#crud-updating-relationships
        """
        relationship = self.schema.relationships[relationship_name]

        # Break if no data key is given.
        if not "data" in relationship_object:
            return None

        # Update a *to-one* relationship
        if relationship.to_one:
            identifier = relationship_object["data"]
            if identifier is None:
                relative = None
            else:
                identifier = (identifier["type"], identifier["id"])
                relative = db.get(identifier, required=True)
            relationship.set(resource, relative)

        # Update a *to-many* relationship
        else:
            identifiers = relationship_object["data"]
            identifiers = [(item["type"], item["id"]) for item in identifiers]

            relatives = db.get_many(identifiers, required=True)
            relatives = list(relatives.values())

            relationship.set(resource, relatives)
        return None

    def extend_relationship(
        self, db, resource, relationship_name, relationship_object
        ):
        """
        Extends the **to-many** relationship with the name *relationship_name*
        of the resource *resource* using the JSONapi relationship object
        *relationship_object*.

        :arg jsonapi.base.database.Session db:
            The database session used to query related resources.
        :arg resource:
            The resource, whichs relationship is extended
        :arg str relationship_name:
            The name of the relationship, which is extended
        :arg dict relationship_object:
            A JSONapi relationship object, containing identifiers of the new
            relatives.

        :seealso: http://jsonapi.org/format/#document-resource-object-relationships
        :seealso: http://jsonapi.org/format/#crud-updating-relationships
        """
        relationship = self.schema.relationships[relationship_name]
        assert relationship.to_many

        if "data" in relationship_object:
            # Get the identifier tuples of the new relatives.
            identifiers = relationship_object["data"]
            identifiers = [(item["type"], item["id"]) for item in identifiers]

            # Load the new relatives.
            relatives = db.get_many(identifiers, required=True)
            relatives = list(relatives.values())

            relationship.extend(resource, relatives)
        return None

    def clear_relationship(self, resource, relationship_name):
        """
        Removes all relatives from the relationship with the name
        *relationship_name* of the resource *resource*.

        :arg resource:
            The resource, whichs relationship is cleared.
        :arg str relationship_name:
            The name oof the relationship, which is cleared.

        :seealso: http://jsonapi.org/format/#crud-updating-relationships
        """
        relationship = self.schema.relationships[relationship_name]
        relationship.clear(resource)
        return None


class Serializer(object):
    """
    A serializer takes a resource and creates a JSONapi document.

    :arg jsonapi.base.schema.Schema schema:
        The schema used to serialize resources
    """

    def __init__(self, schema):
        """
        """
        self.schema = schema
        return None

    def serialize_resource(self, resource, fields=None):
        """
        Creates the JSONapi resource object.

        :arg resource:
        :arg list fields:
            A list with the names of the fields, which should be included.

        :seealso: http://jsonapi.org/format/#document-resource-objects
        """
        d = OrderedDict()
        d.update(self.serialize_identifier(resource))

        attributes = self.serialize_attributes(resource, fields)
        if attributes:
            d["attributes"] = attributes

        relationships = self.serialize_relationships(resource, fields)
        if relationships:
            d["relationships"] = relationships
        return d

    def serialize_identifier(self, resource):
        """
        Creates the JSONapi resource identifier object.

        :arg resource:

        :seealso: http://jsonapi.org/format/#document-resource-identifier-objects
        """
        d = OrderedDict()
        d["type"] = self.schema.typename
        d["id"] = self.schema.id_attribute.get(resource)
        return d

    def serialize_attributes(self, resource, fields=None):
        """
        Creates the JSONapi attributes object.

        :arg resource:
        :arg list fields:
            A list with the names of the fields, which should be included.

        :seealso: http://jsonapi.org/format/#document-resource-object-attributes
        """
        d = OrderedDict()
        for name in sorted(self.schema.attributes):
            if fields is None or name in fields:
                attr = self.schema.attributes[name]
                d[name] = attr.get(resource)
        return d

    def serialize_relationships(self, resource, fields):
        """
        Creates the JSONapi relationships object.

        :arg resource:
        :arg list fields:
            A list with the names of the fields, which should be included.

        :seealso: http://jsonapi.org/format/#document-resource-object-relationships
        """
        d = OrderedDict()
        for name in sorted(self.schema.relationships):
            if fields is None or name in fields:
                d[name] = self.serialize_relationship(resource, name)
        return d

    def serialize_relationship(self, resource, name):
        """
        Creates the JSONapi relationship object for the relationship with the
        name *name*.

        :arg resource:
        :arg str name:

        :seealso: http://jsonapi.org/format/#document-resource-object-relationships
        """
        rel = self.schema.relationships[name]
        d = OrderedDict()

        # Serialize a to-one relationship.
        if rel.to_one:
            relative = rel.get(resource)
            if relative is None:
                d["data"] = None
            else:
                d["data"] = ensure_identifier_object(relative)

        # Serialize a to many relationship.
        else:
            relatives = rel.get(resource)
            relatives = [
                ensure_identifier_object(item) for item in relatives
            ]
            d["data"] = relatives
        return d


def serialize_many(resources, fields):
    """
    Returns a list with the serialized version of all *resources*.

    :arg resources:
        A list of resources
    :arg dict fields:
        A dictionary, mapping the typename to the fields, which should be
        included in the resource documents

    :seealso: :meth:`Serializer.serialize_resource`
    :seealso: :meth:`jsonapi.base.request.Request.japi_fields`
    """
    data = list()
    for resource in resources:
        serializer = resource._jsonapi["serializer"]
        typename = resource._jsonapi["typename"]
        data.append(
            serializer.serialize_resource(resource, fields=fields.get(typename))
        )
    return data
