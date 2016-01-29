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
jsonapi.marker.markup
=====================
"""

__all__ = [
    "Attribute",
    "IDAttribute",
    "BaseRelationship",
    "ToOneRelationship",
    "ToManyRelationship",
    "Constructor",
    "InitConstructor",
    "Markup"
]


# Attributes
# ~~~~~~~~~~

class Attribute(object):
    """
    This class defines the interface for getting and changing the value of
    an attribute.

    :arg str name:
        The name of the attribute as it is displayed in the JSONapi
    """

    def __init__(self, name):
        self.name = name
        return None

    def get(self, resource):
        """
        **Must be overridden**

        Returns the value of the attribute.
        """
        raise NotImplementedError()

    def set(self, resource, value):
        """
        **Must be overridden**

        Changes the value of the attribute to *value*.
        """
        raise NotImplementedError()


class IDAttribute(Attribute):
    """
    The same as :class:`Attribute`, but must be used for the **id** attribute.
    """

    def __init__(self, name="id"):
        super().__init__(name)
        return None


# Relationships
# ~~~~~~~~~~~~~

class BaseRelationship(object):
    """
    This is the **base class** for a relationship.

    :seealso: :class:`ToOneRelationship`
    :seealso: :class:`ToManyRelationship`

    :arg str name:
        The name of the relationship as it is displayed in the JSONapi.
    """

    #: True, if ``isinstance(self, ToOneRelationship)`` holds for instances of
    #: the subclass.
    to_one = None

    #: True, if ``isinstance(self, ToManyRelationship)`` holds for instances
    #: of this subclass.
    to_many = None

    def __init__(self, name):
        self.name = name
        return None

    def get(self, resource):
        """
        **Must be overridden**
        """
        raise NotImplementedError()

    def set(self, resource, relatives):
        """
        **Must be overridden**
        """
        raise NotImplementedError()


class ToOneRelationship(BaseRelationship):
    """
    Describes a *to-one* relationship.
    """

    to_one = True
    to_many = False


class ToManyRelationship(BaseRelationship):
    """
    Describes a *to-many* relationship.
    """

    to_one = False
    to_many = True

    def add(self, resource, relative):
        """
        **Must be overridden**

        Adds the *relative* to the relationship.
        """
        raise NotImplementedError()

    def extend(self, resource, relatives):
        """
        **Can be overridden** for performance reasons.

        Adds the *relatives* to the relationship.
        """
        for relative in relatives:
            self.add(resource, relative)
        return None

    def remove(self, resource, relative):
        """
        **Must be overridden**

        Remopves the *relative* from the relationship.
        """
        raise NotImplementedError()


# Construction
# ~~~~~~~~~~~~

class Constructor(object):
    """
    Defines the interface for creating a new resource.
    """

    def create(self, **kargs):
        """
        **Must be overridden**

        Creates a new resource using the keyword arguments and returns it.
        The keyword arguments are the fields of the resource mapped to their
        initial value.
        """
        raise NotImplementedError()


class InitConstructor(Constructor):
    """
    This constructor simply uses the ``__init__`` method of the *model* class
    to create a new resource.

    :arg model:
        The resource class
    """

    def __init__(self, model):
        self.model = model
        return None

    def create(self, **kargs):
        return self.model(**kargs)


class Markup(object):
    """
    Describes how we can serialize a resource using the marker objects defined
    above:

    *   :class:`Constructor`
    *   :class:`Attribute`
    *   :class:`IDAttribute`
    *   :class:`ToOneRelationship`
    *   :class:`ToManyRelationship`

    .. todo::

        *   Add support for link objects
            http://jsonapi.org/format/#document-links

        *   Add support for meta objects
            http://jsonapi.org/format/#document-meta

    :arg model:
        The resource class
    :arg typename:
        The typename of the model in the JSONapi
    """

    def __init__(self, model, typename=None):
        """
        """
        #: The resource class
        self.model = model

        #: The typename of the resource class in the API
        self.typename = model.__name__ if typename is None else typename

        #: The constructor. If we do not find one, we will later assume
        #: the default __init__ function.
        self.constructor = None

        #: The id attribute getter
        self.id_attribute = None

        #: Contains all attribute markers.
        self.attributes = dict()

        #: The relationship markers.
        self.relationships = dict()

        #: Contains all field names.
        self.fields = set()

        self.find_markers()
        return None

    def find_markers(self):
        """
        We search for marker instances (attributes, relationships, ...),
        which are defined on the :attr:`model`.
        """
        # Find all markers.
        for name, prop in vars(self.model).items():

            # Constructor
            if isinstance(prop, Constructor):
                if not self.constructor is None:
                    LOG.warning(
                        "The constructor has been marked twice on %s.",
                        self.typename
                    )
                self.constructor = constructor

            # IDAttribute
            elif isinstance(prop, IDAttribute):
                if not self.id_attribute is None:
                    LOG.warning(
                        "The ID attribute has been marked twice on %s.",
                        self.typename
                    )
                self.id_attribute = prop

            # Attribute
            elif isinstance(prop, Attribute):
                if prop.name in self.attributes:
                    LOG.warning(
                        "The '%s' attribute has been marked twice on '%s'.",
                        prop.name, self.typename
                    )
                self.attributes[prop.name] = prop
                self.fields.add(prop.name)

            # Relationship
            elif isinstance(prop, (ToOneRelationship, ToManyRelationship)):
                if prop.name in self.relationships:
                    LOG.warning(
                        "The '%s' relationship has been marked twice on '%s'.",
                        prop.name, self.typename
                    )
                self.relationships[prop.name] = prop
                self.fields.add(prop.name)

        # Use the default constructor, if we no special classmethod has been
        # marked.
        if self.constructor is None:
            self.constructor = InitConstructor(self.model)
        return None
