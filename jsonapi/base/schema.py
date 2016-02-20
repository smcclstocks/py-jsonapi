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
jsonapi.base.schema
===================

This module defines the base for the schema we use to represent the structure
of a resource. The schema is used to serialize, create and update a resource.

Because most of the will use an ORM, and therefore already have a metatype
class, this schema is **not** implemented as meta class.

.. seealso::

    *   :mod:`jsonapi.marker.method` to decorate methods
    *   :mod:`jsonapi.marker.property` to decorate properties
"""


__all__ = [
    "Attribute",
    "IDAttribute",
    "BaseRelationship",
    "ToOneRelationship",
    "ToManyRelationship",
    "Constructor",
    "InitConstructor",
    "Schema"
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

    def clear(self, resource):
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

    def clear(self, resource):
        """
        **Can be overridden**

        Default implementation is equal to:

        .. code-block:: python3

            self.set(resource, None)
        """
        self.set(resource, None)
        return None


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
        **Can be overridden**

        Adds all *relatives* to the relationship.
        """
        for relative in relatives:
            self.add(resource, relative)
        return None

    def clear(self, resource):
        """
        **Can be overridden**

        Default implementation is equal to:

        .. code-block:: python3

            self.set(resource, list())
        """
        self.set(resource, None)
        return None


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
    This constructor simply uses the ``__init__`` method of the *resource_class*
    class to create a new resource.

    :arg resource_class:
    """

    def __init__(self, resource_class):
        self.resource_class = resource_class
        return None

    def create(self, **kargs):
        return self.resource_class(**kargs)


class Schema(object):
    """
    Describes the structure of a resource class. The serializer will use a
    schema to serialize, create and update a resource.

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

    :arg resource_class:
        The resource class
    :arg typename:
        The typename of the resource_class in the JSONapi. If not given, we use
        the name of the resource class.
    """

    def __init__(self, resource_class, typename=None):
        """
        """
        self.resource_class = resource_class
        """The resource class"""

        self.typename = typename or resource_class.__name__
        """
        The typename of the resource class in the API.
        """

        self.constructor = None
        """
        The :class:`Constructor` marker, which can be used to create new
        instances of the resource. If no special constructor is defined on the
        resource_class, the default `__init__` method is used.
        """

        self.id_attribute = None
        """The :class:`IDAttribute` marker."""

        self.attributes = dict()
        """
        A dictionary, which maps the attributes names to the :class:`Attribute`
        instance.
        """

        #: The relationship markers.
        self.relationships = dict()
        """
        A dictionary, which maps the relationhip names to the
        :class:`ToOneRelationship` or :class:`ToManyRelationship`.
        """

        self.fields = set()
        """
        Contains the names of all attributes and relationships.
        """

        self.find_fields()
        return None

    def find_fields(self):
        """
        We search for fields instances on the :attr:`resource_class`. If we
        find an attriute, relationship, constructor, ... definition we
        add it to the schema.
        """
        # Find all markers.
        for name, prop in vars(self.resource_class).items():

            # Constructor
            if isinstance(prop, Constructor):
                if not self.constructor is None:
                    LOG.warning(
                        "Found two constructors on %s.", self.typename
                    )
                self.constructor = constructor

            # IDAttribute
            elif isinstance(prop, IDAttribute):
                if not self.id_attribute is None:
                    LOG.warning(
                        "Found two id attributes on %s.", self.typename
                    )
                self.id_attribute = prop

            # Attribute
            elif isinstance(prop, Attribute):
                if prop.name in self.attributes:
                    LOG.warning(
                        "Found the attribute %s twice on %s.",
                        prop.name, self.typename
                    )
                self.attributes[prop.name] = prop
                self.fields.add(prop.name)

            # Relationship
            elif isinstance(prop, (ToOneRelationship, ToManyRelationship)):
                if prop.name in self.relationships:
                    LOG.warning(
                        "Found the relationship %s twice on %s.",
                        prop.name, self.typename
                    )
                self.relationships[prop.name] = prop
                self.fields.add(prop.name)

        # Use the default constructor, if no special classmethod has been
        # marked.
        if self.constructor is None:
            self.constructor = InitConstructor(self.resource_class)
        return None
