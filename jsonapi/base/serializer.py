#!/usr/bin/env python3

"""
jsonapi.base.serializer
=======================

:license: GNU Affero General Public License v3
:copyright: 2016 by Benedikt Schmitt <benedikt@benediktschmitt.de>

A JSONapi serializer based on the :class:`~jsonapi.base.schema.Schema`.
"""

# std
from collections import OrderedDict

# local
from .utilities import (
    ensure_identifier,
    ensure_identifier_object
)


__all__ = [
    "Serializer"
]


class Serializer(object):
    """
    The serializer is the glue between the request handlers and the schema.
    It receives the JSON data and creates, updates or serializes a resource.

    :arg jsonapi.base.schema.Schema schema:
        The schema used to serialize resources
    :arg jsonapi.base.api.API api:
        The API, which owns the serializer. The api may be given later
        via :meth:`init_api`.
    """

    def __init__(self, schema, api=None):
        """
        """
        self.schema = schema
        self.resource_class = schema.resource_class
        self.typename = schema.typename
        self.api = api
        return None

    def init_api(self, api):
        """
        The serializer is usually constructed before the API. So this method
        is called by the api, when the serializer is added.

        :seealso: :meth:`jsonapi.base.api.API.add_model`
        """
        self.api = api
        return None

    # ID
    # ~~

    def full_id(self, resource):
        """
        Returns the type, id pair of the resource.

        .. code-block:: python3

            ("people", "42")

        :arg resource:
        """
        return (self.typename, self.schema.id_attribute.get(resource))

    def id(self, resource):
        """
        Returns the id of the resource. The id is always a string.

        :arg resource:
        """
        return self.schema.id_attribute.get(resource)

    # Creation
    # ~~~~~~~~

    def create_resource(self, attributes, relationships, meta):
        """
        Creates a new resource and returns it.

        :arg dict attributes:
            Maps the attribute names to their initial values.
        :arg dict relationships:
            Maps the relationship names to their initial related resources
        :arg dict meta:
            The meta dictionary, received with the request.

        .. todo::

            What shall we do with *meta*?

            1.) We could check if the constructor accepts a keyword with the
                name **japi_meta** or **meta** and if it does, give it as
                keyword argument.
            2.) We could simply unpack all values together with *attributes**
                and **relationships**
        """
        kargs = dict()
        kargs.update(attributes)
        kargs.update(relationships)
        new_resource = self.schema.constructor.create(**kargs)
        return new_resource

    def update_attributes(self, resource, d):
        """
        Updates the resource based upon the dictionary *d*.

        .. code-block:: python3

            {
                "title": "To TDD or Not",
                "text": "TLDR; It's complicated... but check your test coverage regardless."
            }

        :arg resource:
        :arg dict d:

        :seealso: http://jsonapi.org/format/#crud-updating
        """
        for name, value in d.items():
            attr = self.schema.attributes[name]
            attr.set(resource, value)
        return None

    # Relationships
    # ~~~~~~~~~~~~~

    def has_relationship(self, name):
        """
        Returns True, if a relationship with the name *name* exists.

        :arg str name:
        """
        return name in self.schema.relationships

    def is_to_one_relationship(self, name):
        """
        Returns True, if the relationship is a to-one relationship.

        :arg str name:
        """
        rel = self.schema.relationships[name]
        return rel.to_one

    def is_to_many_relationship(self, name):
        """
        Returns True, if the relationship is a to-many relationship.

        :arg str name:
        """
        rel = self.schema.relationships[name]
        return rel.to_many

    def extend_relationship(self, resource, name, relatives):
        """
        **Must be overridden**

        Adds the *relatives* to the *to-many* relationship with the name
        *name*.

        :arg resource:
        :arg str name:
        :arg list relatives:
            A list with the new related resources
        """
        rel = self.schema.relationships[name]
        assert rel.to_many
        rel.extend(resource, relatives)
        return None

    def update_relationship(self, resource, name, relatives, meta):
        """
        Updates the relationship with the name *name*, so that the related
        resources match *relatives*.

        :arg resource:
        :arg str name:
        :arg relatives:
            A list of resources for a *to-many* relationship and a single
            resource or None for a *to-one* relationship.
        :arg dict meta:
            The meta dictionary sent with the request.

        .. todo::

            What should we do with *meta*?
        """
        rel = self.schma.relationship[name]
        rel.set(resource, relatives)
        return None

    def extend_relationship(self, resource, name, relatives, meta):
        """
        Adds the resources in *relatives* to the relationship with the name
        *name*.

        :arg resource:
        :arg str name:
        :arg list relatives:
            The resources, which should be added to the relationship.
        :arg dict meta:
            The meta dictionary sent with the request.

        .. todo::

            What should we do with *meta*?
        """
        rel = self.schema.relationships[name]
        assert rel.to_many
        rel.extend(resource, relatives)
        return None

    def delete_relationship(self, resource, rel_name, meta):
        """
        Removes all related resources from the relationship with the name
        *rel_name*.

        .. todo::

            What should we do with *meta*?
        """
        if self.is_to_one_relationship(rel_name):
            self.set_relative(resource, rel_name, None)
        else:
            self.set_relatives(resource, rel_name, list())
        return None

    # Serialization
    # ~~~~~~~~~~~~~

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
                d["data"] = ensure_identifier_object(self.api, relative)

        # Serialize a to many relationship.
        else:
            relatives = rel.get(resource)
            relatives = [
                ensure_identifier_object(self.api, item) for item in relatives
            ]
            d["data"] = relatives
        return d
