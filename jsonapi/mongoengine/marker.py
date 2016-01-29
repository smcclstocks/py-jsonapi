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
import logging

# third party
import mongoengine

# local
from jsonapi import marker


log = logging.getLogger(__file__)


__all__ = [
    "MongoEngineMarkup"
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


class MongoEngineAttribute(marker.markup.Attribute):
    """
    Wraps any mongoengine.BaseField instance, which does not represent a
    relationship.
    """

    def __init__(self, name, model, me_field):
        """
        """
        super().__init__(name=name)
        self.model = model

        # The field object (mongoengine.BaseField)
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


class MongoEngineIDAttribute(marker.markup.IDAttribute):
    """
    Returns the ID string (not the ObjectId instance). We only implement
    the :meth:`get` method, so the the id can not be changed by the user.
    """

    def __init__(self, name, model, me_field):
        super().__init__(name=name)
        self.me_field = me_field
        self.model = model
        return None

    def get(self, resource):
        """
        """
        # __get__() returns an ObjectId instance, but we only want the id
        # string.
        return str(self.me_field.__get__(resource, None))


class MongoEngineToOneRelationship(marker.markup.ToOneRelationship):
    """
    Wraps a *to-one* relationship. We assume, that a motorengine field
    describes a *to-one* relationship, if :func:`is_to_one_relationship`
    returns True.
    """

    def __init__(self, name, model, me_field):
        super().__init__(name=name)

        # The document class
        self.model = model

        # The motorengine BaseField instance.
        self.me_field = me_field
        return None

    def get(self, resource):
        with mongoengine.context_managers.no_dereference(self.model):
            return self.me_field.__get__(resource, None)

    def set(self, resource, relative):
        return self.me_field.__set__(resource, relative)

    def delete(self, resource):
        return self.me_field.__set__(resource, None)


class MongoEngineToManyRelationship(marker.markup.ToManyRelationship):
    """
    Wraps a *to-many* relationship. A motorengine field is considered as
    *to-many* relationship, if :func:`is_to_many_relationship` returns True.
    """

    def __init__(self, name, model, me_field):
        super().__init__(name=name)

        # The document class
        self.model = model

        # The motorengine BaseField instance.
        self.me_field = me_field
        return None

    def get(self, resource):
        with mongoengine.context_managers.no_dereference(self.model):
            return self.me_field.__get__(resource, None)

    def set(self, resource, relatives):
        return self.me_field.__set__(resource, relatives)

    def delete(self, resource):
        return self.me_field.__set__(resource, list())

    def add(self, resource, relative):
        return self.me_field.__get__(resource, None).append(relative)

    def remove(self, resource, relative):
        return self.me_field.__get__(resource, None).remove(relative)


class MongoEngineMarkup(marker.markup.Markup):
    """
    This subclass of Markup also finds also mongoengine fields.
    """

    def __init__(self, model):
        """
        """
        super().__init__(model)
        self.find_mongoengine_markers()
        return None

    def find_mongoengine_markers(self):
        """
        Finds all mongoengine attributes and relationships.
        """
        for name, field in self.model._fields.items():

            # Check if the field is the id field.
            if self.id_attribute is None \
                and self.model._db_field_map[name] == "_id":
                attribute = MongoEngineIDAttribute(
                    name, self.model, field
                )
                self.id_attribute = attribute

            # Check if the field is a *to-one* relationship.
            elif is_to_one_relationship(field):
                relationship = MongoEngineToOneRelationship(
                    name, self.model, field
                )

                assert not relationship.name in self.relationships
                self.relationships[relationship.name] = relationship
                self.fields.add(relationship.name)

            # Check if the field is a *to-many* relationship.
            elif is_to_many_relationship(field):
                relationship = MongoEngineToManyRelationship(
                    name, self.model, field
                )

                assert not relationship.name in self.relationships
                self.relationships[relationship.name] = relationship
                self.fields.add(relationship.name)

            # The field is an attribute.
            else:
                attribute = MongoEngineAttribute(
                    name, self.model, field
                )

                assert not attribute in self.attributes
                self.attributes[attribute.name] = attribute
                self.fields.add(attribute.name)
        return None
