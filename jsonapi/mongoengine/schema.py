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
jsonapi.mongoengine.schema
==========================

The JSONapi schema for mongoengine documents.
"""

# std
import logging

# third party
import mongoengine

# local
import jsonapi


LOG = logging.getLogger(__file__)


__all__ = [
    "is_to_one_relationship",
    "is_to_many_relationship",
    "Attribute",
    "IDAttribute",
    "ToOneRelationship",
    "ToManyRelationship",
    "Schema"
]


def is_to_one_relationship(field):
    """
    Returns True, if the *field* is a reference field:

    *   :class:`mongoengine.ReferenceField`
    *   :class:`mongoengine.CachedReferenceField`
    *   :class:`mongoengine.GenericReferenceField`

    All of these fields describe a *to-one* relationship.
    """
    return isinstance(field, mongoengine.ReferenceField)\
        or isinstance(field, mongoengine.CachedReferenceField)\
        or isinstance(field, mongoengine.GenericReferenceField)


def is_to_many_relationship(field):
    """
    Returns True, if the *field* describes a *to many* relationship.

    The field types are:

    *   :class:`mongoengine.ListField`
    *   :class:`mongoengine.SortedListField`

    with a simple reference field as element.
    """
    if isinstance(field, mongoengine.ListField) \
        and is_to_one_relationship(field.field):
        return True

    if isinstance(field, mongoengine.SortedListField)\
        and is_to_one_relationship(field.field):
        return True
    return False


class Attribute(jsonapi.base.schema.Attribute):
    """
    Wraps any *mongoengine.BaseField* instance, which does not represent a
    relationship or the id.

    :arg str name:
        The name of the mongoengine attribute
    :arg resource_class:
        The mongoengine document
    :arg me_field:
        The mongoengine BaseField wrapped by this Attribute.
    """

    def __init__(self, name, resource_class, me_field):
        """
        """
        super().__init__(name=name)
        self.resource_class = resource_class
        self.me_field = me_field
        return None

    def get(self, resource):
        """
        """
        return self.me_field.__get__(resource, None)

    def set(self, resource, value):
        """
        """
        self.me_field.__set__(resource, value)
        return None


class IDAttribute(jsonapi.base.schema.IDAttribute):
    """
    Returns the ID string (not the ObjectId instance). We only implement
    the :meth:`get` method, so the the id can not be changed by the user.

    :arg str name:
        The name of the id field.
    :arg str resource_class:
        The mongoengine document
    :arg me_field:
        The mongoengine id field of the resource class
    """

    def __init__(self, name, resource_class, me_field):
        super().__init__(name=name)
        self.resource_class = resource_class
        self.me_field = me_field
        return None

    def get(self, resource):
        """
        """
        # __get__() returns an ObjectId instance, but we only want the id
        # string.
        return str(self.me_field.__get__(resource, None))


class ToOneRelationship(jsonapi.base.schema.ToOneRelationship):
    """
    Wraps a *to-one* relationship. We assume, that a mongoengine field
    describes a *to-one* relationship, if :func:`is_to_one_relationship`
    returns True.
    """

    def __init__(self, name, resource_class, me_field):
        super().__init__(name=name)
        self.resource_class = resource_class
        self.me_field = me_field
        return None

    def get(self, resource):
        with mongoengine.context_managers.no_dereference(self.resource_class):
            return self.me_field.__get__(resource, None)

    def set(self, resource, relative):
        return self.me_field.__set__(resource, relative)

    def clear(self, resource):
        return self.me_field.__set__(resource, None)


class ToManyRelationship(jsonapi.base.schema.ToManyRelationship):
    """
    Wraps a *to-many* relationship. A mongoengine field is considered as
    *to-many* relationship, if :func:`is_to_many_relationship` returns True.

    :arg str name:
        The name of the mongoengine relationship
    :arg resource_class:
        The mongoengine document
    :arg me_field:
        The mongoengine BaseField, which describes the relationship
    """

    def __init__(self, name, resource_class, me_field):
        super().__init__(name=name)
        self.resource_class = resource_class
        self.me_field = me_field
        return None

    def get(self, resource):
        with mongoengine.context_managers.no_dereference(self.resource_class):
            return self.me_field.__get__(resource, None)

    def set(self, resource, relatives):
        return self.me_field.__set__(resource, relatives)

    def clear(self, resource):
        return self.me_field.__set__(resource, list())

    def add(self, resource, relative):
        return self.me_field.__get__(resource, None).append(relative)

    def extend(self, resource, relatives):
        self.me_field.__get__(resource, None).extend(relatives)


class Schema(jsonapi.base.schema.Schema):
    """
    This Schema subclass also finds mongoengine attributes and relationships.

    :arg resource_class:
        The mongoengine document (class)
    :arg str typename:
        The typename of the resources in the JSONapi. If not given, it is
        derived from the resource class.
    """

    def __init__(self, resource_class, typename=None):
        """
        """
        super().__init__(resource_class, typename)
        self.find_mongoengine_markers()
        return None

    def find_mongoengine_markers(self):
        """
        Finds all mongoengine attributes and relationships.
        """
        for name, field in self.resource_class._fields.items():

            # Check if the field is the id field.
            if self.id_attribute is None \
                and self.resource_class._db_field_map[name] == "_id":

                attribute = IDAttribute(name, self.resource_class, field)
                self.id_attribute = attribute

            # Check if the field is a *to-one* relationship.
            elif is_to_one_relationship(field):
                relationship = ToOneRelationship(
                    name, self.resource_class, field
                )

                assert not relationship.name in self.relationships
                self.relationships[relationship.name] = relationship
                self.fields.add(relationship.name)

            # Check if the field is a *to-many* relationship.
            elif is_to_many_relationship(field):
                relationship = ToManyRelationship(
                    name, self.resource_class, field
                )

                assert not relationship.name in self.relationships
                self.relationships[relationship.name] = relationship
                self.fields.add(relationship.name)

            # The field is an attribute.
            else:
                attribute = Attribute(
                    name, self.resource_class, field
                )

                assert not attribute in self.attributes
                self.attributes[attribute.name] = attribute
                self.fields.add(attribute.name)
        return None
