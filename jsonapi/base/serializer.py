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

"""
jsonapi.base.serializer
=======================
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
    Defines the interface for a serializer.

    **How to subclass?**

    You can override almost all methods, as long as they satisfy the
    description. However, you don't have to. These are the methods, which
    must to be overridden:

    *   :meth:`id`
    *   :meth:`create_resource`
    *   :meth:`attributes`
    *   :meth:`get_attribute`
    *   :meth:`set_attribute`
    *   :meth:`relationships`
    *   :meth:`is_to_one_relationship`
    *   :meth:`get_relative_id`
    *   :meth:`get_relative_ids`
    *   :meth:`set_relative`
    *   :meth:`set_relatives`
    *   :meth:`extend_relationship`

    :arg model:
        The resource class (type)
    :arg str typename:
        The resource type name in the sense of the JSONapi specification
    :arg jsonapi.base.api.API api:
        The API, which owns the serializer. The api may be given later
        via :meth:`init_api`.
    """

    def __init__(self, model, typename, api=None):
        """
        """
        self.model = model
        self.typename = typename
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
        return (self.typename, self.id(resource))

    def id(self, resource):
        """
        **Must be overridden**

        Returns the id of the resource. The id is always a string.

        :arg resource:
        """
        raise NotImplementedError()

    # Creation
    # ~~~~~~~~

    def create_resource(self, attributes, relationships, meta):
        """
        **Must be overridden**

        Creates a new resource and returns it.

        :arg dict attributes:
            Maps the attribute names to their initial values.
        :arg dict relationships:
            Maps the relationship names to their initial related resources
        :arg dict meta:
            The meta dictionary, received with the request.
        """
        raise NotImplementedError()

    # Attributes
    # ~~~~~~~~~~

    def attributes(self):
        """
        **Must be overridden**

        Returns a list with the names of all attributes.
        """
        raise NotImplementedError()

    def has_attribute(self, attr_name):
        """
        Returns True, if an attribute with the name *attr_name* exists.

        :arg str attr_name:
        """
        return attr_name in self.attributes()

    def get_attribute(self, resource, attr_name):
        """
        **Must be overridden**

        Returns the value of an attribute.

        :arg resource:
        :arg str attr_name:
        """
        raise NotImplementedError()

    def set_attribute(self, resource, attr_name, attr_value):
        """
        **Must be overridden**

        Changes the value of an attribute.

        :arg resource:
        :arg str attr_name:
        :arg attr_value:
            The new value of the attribute.
        """
        raise NotImplementedError()

    def jupdate_attributes(self, resource, d):
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
        for attr_name, attr_value in d.items():
            self.set_attribute(resource, attr_name, attr_value)
        return None

    # Relationships
    # ~~~~~~~~~~~~~

    def relationships(self):
        """
        **Must be overridden**

        Returns a list with the names of all relationships.
        """
        raise NotImplementedError()

    def has_relationship(self, rel_name):
        """
        Returns True, if a relationship with the name *rel_name* exists.

        :arg str rel_name:
        """
        return rel_name in self.relationships()

    def is_to_one_relationship(self, rel_name):
        """
        **Must be overridden**

        Returns True, if the relationship is a to-one relationship.

        :arg str rel_name:
        """
        raise NotImplementedError()

    def is_to_many_relationship(self, rel_name):
        """
        Returns True, if the relationship is a to-many relationship.

        :arg str rel_name:
        """
        return not self.is_to_one_relationship(rel_name)

    def get_relative_id(self, resource, rel_name):
        """
        **Must be overridden**

        Returns the id of the related resource of a *to-one* relationship.

        :arg resource:
        :arg str rel_name:
        """
        raise NotImplementedError()

    def get_relative_ids(self, resource, rel_name):
        """
        **Must be overridden**

        Returns a list with the full ids of the related resources in the
        relationship with the name *rel_name*.

        :arg resource:
        :arg str rel_name:
        """
        raise NotImplementedError()

    def set_relative(self, resource, rel_name, relative):
        """
        **Must be overridden**

        Changes the related resource in the *to-one* relationship with the
        name *rel_name* to *relative*.

        :arg resource:
        :arg str rel_name:
        :arg relative:
            The new related resource or None
        """
        raise NotImplementedError()

    def set_relatives(self, resource, rel_name, relatives):
        """
        **Must be overridden**

        Changes the related resources in the *to-many* relationship with the
        name *rel_name* to *relatives*.

        :arg resource:
        :arg str rel_name:
        :arg list relatives:
            A list with the new related resources
        """
        raise NotImplementedError()

    def extend_relationship(self, resource, rel_name, relatives):
        """
        **Must be overridden**

        Adds the *relatives* to the *to-many* relationship with the name
        *rel_name*.

        :arg resource:
        :arg str rel_name:
        :arg list relatives:
            A list with the new related resources
        """
        raise NotImplementedError()

    def jupdate_relationship(self, resource, rel_name, relatives, meta):
        """
        Updates the relationship with the name *rel_name*, so that the related
        resources match *relatives*.

        :arg resource:
        :arg str rel_name:
        :arg relatives:
            A list of resources for a *to-many* relationship and a single
            resource or None for a *to-one* relationship.
        :arg dict meta:
            The meta dictionary sent with the request.

        .. todo::

            What should we do with *meta*?
        """
        if self.is_to_one_relationship(rel_name):
            self.set_relative(resource, rel_name, relatives)
        else:
            self.set_relatives(resource, rel_name, relatives)
        return None

    def jextend_relationship(self, resource, rel_name, relatives, meta):
        """
        Adds the resources in *relatives* to the relationship with the name
        *rel_name*.

        :arg resource:
        :arg str rel_name:
        :arg list relatives:
            The resources, which should be added to the relationship.
        :arg dict meta:
            The meta dictionary sent with the request.

        .. todo::

            What should we do with *meta*?
        """
        assert self.is_to_many_relationship(rel_name)
        self.extend_relationship(resource, rel_name, relatives)
        return None

    def jdelete_relationship(self, resource, rel_name, meta):
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
        d["type"] = self.typename
        d["id"] = self.id(resource)
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
        for attr_name in sorted(self.attributes()):
            if fields is None or attr_name in fields:
                d[attr_name] = self.get_attribute(resource, attr_name)
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
        for rel_name in sorted(self.relationships()):
            if fields is None or rel_name in fields:
                d[rel_name] = self.serialize_relationship(resource, rel_name)
        return d

    def serialize_relationship(self, resource, rel_name):
        """
        Creates the JSONapi relationship object for the relationship with the
        name *rel_name*.

        :arg resource:
        :arg str rel_name:

        :seealso: http://jsonapi.org/format/#document-resource-object-relationships
        """
        d = OrderedDict()

        # Serialize a to-one relationship.
        if self.is_to_one_relationship(rel_name):
            relative = self.get_relative_id(resource, rel_name)
            if relative is not None:
                d["data"] = ensure_identifier_object(self.api, relative)
            else:
                d["data"] = None

        # Serialize a to many relationship.
        else:
            relatives = self.get_relative_ids(resource, rel_name)
            relatives = [
                ensure_identifier_object(self.api, item) for item in relatives
            ]
            d["data"] = relatives
        return d
