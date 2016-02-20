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
jsonapi.motorengine.schema
==========================

The JSONapi schema for motorengine documents.
"""

# std
import logging

# third party
from bson.objectid import ObjectId
import motorengine

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

    *   :class:`motorengine.ReferenceField`

    All of these fields describe a *to-one* relationship.
    """
    return isinstance(field, motorengine.ReferenceField)


def is_to_many_relationship(field):
    """
    Returns True, if the *field* describes a *to many* relationship.

    The field types are:

    *   :class:`motorengine.ListField`

    with a simple reference field as element.
    """
    # We need the protected *_base_field* variable here. Check if there is
    # a way to implement this function without accessing private or protected
    # attributes.
    #
    # Please note, that *field.item_type* is not sufficient.
    return isinstance(field, motorengine.ListField) \
        and is_to_one_relationship(field._base_field)


class Attribute(jsonapi.base.schema.Attribute):
    """
    Returns the value of a motorengine attribute.

    :arg str name:
        The name of the motorengine attribute
    """

    def get(self, resource):
        """
        """
        return getattr(resource, self.name)

    def set(self, resource, value):
        """
        """
        setattr(resource, self.name, value)
        return None


class IDAttribute(jsonapi.base.schema.IDAttribute):
    """
    Returns the ID of a motorengine document. This is always:

    .. code-block:: python3

        resource._id
    """

    def get(self, resource):
        """
        """
        # We need to use str(), because resource._id is an ObjectId instance.
        return str(resource._id)


class ToOneRelationship(jsonapi.base.schema.ToOneRelationship):
    """
    Wraps a *to-one* relationship. We assume, that a motorengine field
    describes a *to-one* relationship, if :func:`is_to_one_relationship`
    returns True.

    :arg str name:
        The name of the relationship field.
    :arg me_field:
        The motorengine base field
    """

    def __init__(self, name, me_field):
        super().__init__(name=name)
        self.me_field = me_field
        return None

    def get(self, resource):
        """
        Returns the remote object, if it is loaded. Otherwise the id.
        """
        try:
            return getattr(resource, self.name)
        except motorengine.errors.LoadReferencesRequiredError:
            objectid = resource.get_field_value(self.name)
            objectid = str(objectid)

            reference_type = self.me_field.reference_type
            reference_typename = reference_type._jsonapi["typename"]
            return (reference_typename, objectid)

    def set(self, resource, relative):
        setattr(resource, self.name, relative)
        return None

    def clear(self, resource):
        setattr(resource, self.name, None)
        return None


class ToManyRelationship(jsonapi.base.schema.ToManyRelationship):
    """
    Wraps a *to-many* relationship. A motorengine field is considered as
    *to-many* relationship, if :func:`is_to_many_relationship` returns True.

    :arg str name:
        The name of the motorengine relationship
    :arg me_field:
        The motorengine base field
    """

    def __init__(self, name, me_field):
        super().__init__(name=name)
        self.me_field = me_field
        return None

    def get(self, resource):
        """
        Returns the related resources, if they are loaded. Otherwise only the
        identifiers are returned.
        """
        relatives = getattr(resource, self.name)
        if relatives and isinstance(relatives[0], ObjectId):
            reference_type = self.me_field.item_type
            reference_typename = reference_type._jsonapi["typename"]

            relatives = [
                (reference_typename, str(relative_id))\
                for relative_id in relatives
            ]
        return relatives

    def set(self, resource, relatives):
        setattr(resource, self.name, relatives)
        return None

    def clear(self, resource):
        setattr(resource, self.name, list())
        return None

    def extend(self, resource, relatives):
        """
        .. todo::

            The references must be loaded for this method. We can avoid
            loading the references, if we simply add the identifiers of
            the *relatives* to the list. This is acceptable after checking
            if their type is a subtype of *me_field.reference_type*, since
            the me attribute is public anyway and has no setter.
        """
        getattr(resource, self.name).extend(relatives)
        return None


class Schema(jsonapi.base.schema.Schema):
    """
    This Schema subclass also finds motorengine attributes and relationships.

    :arg resource_class:
        The motorengine document (class)
    :arg str typename:
        The typename of the resources in the JSONapi. If not given, it is
        derived from the resource class.
    """

    def __init__(self, resource_class, typename=None):
        """
        """
        super().__init__(resource_class, typename)
        self.find_motorengine_markers()
        return None

    def find_motorengine_markers(self):
        """
        Finds all motorengine attributes and relationships.
        """
        if self.id_attribute is not None:
            raise RuntimeError("Overwriting the _id attribute is not allowed.")
        self.id_attribute = IDAttribute()

        for name, field in self.resource_class._fields.items():
            # Check if the field is a *to-one* relationship.
            if is_to_one_relationship(field):
                relationship = ToOneRelationship(name, field)

                assert not relationship.name in self.relationships
                self.relationships[relationship.name] = relationship
                self.fields.add(relationship.name)

            # Check if the field is a *to-many* relationship.
            elif is_to_many_relationship(field):
                relationship = ToManyRelationship(name, field)

                assert not relationship.name in self.relationships
                self.relationships[relationship.name] = relationship
                self.fields.add(relationship.name)

            # The field is an attribute.
            else:
                attribute = Attribute(name)

                assert not attribute in self.attributes
                self.attributes[attribute.name] = attribute
                self.fields.add(attribute.name)
        return None
