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
jsonapi.sqlalchemy.schema
=========================

The *py-jsonapi* schema for *sqlalchemy* models.
"""

# std
import logging

# third party
import sqlalchemy

# local
import jsonapi


__all__ = [
    "Attribute",
    "IDAttribute",
    "ToOneRelationship",
    "ToManyRelationship",
    "Schema"
]


LOG = logging.getLogger(__file__)


class Attribute(jsonapi.base.schema.Attribute):
    """
    Wraps an sqlalchemy database column.

    :arg resource_class:
        The sqlchemy model
    :arg sqlattr:
        An sqlalchemy ColumnProperty
    """

    def __init__(self, resource_class, sqlattr):
        """
        """
        super().__init__(name=sqlattr.key)
        self.sqlattr = sqlattr
        self.class_attr = sqlattr.class_attribute
        self.resource_class = resource_class
        return None

    def get(self, resource):
        return self.class_attr.__get__(resource, None)

    def set(self, resource, value):
        return self.class_attr.__set__(resource, value)


class IDAttribute(jsonapi.base.schema.IDAttribute):
    """
    Wraps an sqlalchemy primary key. We only allow reading the id, but not
    changing it.

    .. todo::

        We currently support only primary keys with one column.
        Add support for composite primary keys.

    .. todo::

        We currently use the inspection module of sqlalchemy to get the
        primary key. Can we optimize this?

    :arg resource_class:
        The sqlalchemy model
    """

    def __init__(self, resource_class):
        super().__init__()
        self.resource_class = resource_class
        return None

    def get(self, resource):
        """
        We use the Inspector for :attr:`resource_class` to get the primary key
        for the resource.
        """
        keys = sqlalchemy.inspect(resource).identity
        return str(keys[0]) if keys is not None else None


class ToOneRelationship(jsonapi.base.schema.ToOneRelationship):
    """
    Wraps an sqlalchemy to-one relationship.

    :arg resource_class:
        The sqlalchemy model
    :arg sqlrel:
        The relationship defined on the model
    """

    def __init__(self, resource_class, sqlrel):
        super().__init__(name=sqlrel.key)
        self.sqlrel = sqlrel
        self.class_attr = sqlrel.class_attribute
        self.resource_class = resource_class
        return None

    def get(self, resource):
        return self.class_attr.__get__(resource, None)

    def set(self, resource, relative):
        return self.class_attr.__set__(resource, relative)

    def clear(self, resource):
        return self.class_attr.__delete__(resource)


class ToManyRelationship(jsonapi.base.schema.ToManyRelationship):
    """
    Wraps an sqlalchemy to-many relationship.

    :arg resource_class:
        The sqlalchemy model
    :arg sqlrel:
        The relationship defined on the model
    """

    def __init__(self, resource_class, sqlrel):
        super().__init__(name=sqlrel.key)
        self.sqlrel = sqlrel
        self.class_attr = sqlrel.class_attribute
        self.resource_class = resource_class
        return None

    def get(self, resource):
        return self.class_attr.__get__(resource, None)

    def set(self, resource, relatives):
        self.class_attr.__set__(resource, relatives)
        return None

    def clear(self, resource):
        self.class_attr.__get__(resource, None).clear()
        return None

    def add(self, resource, relative):
        relatives = self.class_attr.__get__(resource, None)
        relatives.append(relative)
        return None

    def extend(self, resource, new_relatives):
        relatives = self.class_attr.__get__(resource, None)
        relatives.extend(new_relatives)
        return None


class Schema(jsonapi.base.schema.Schema):
    """
    This schema subclass finds also sqlalchemy attributes and relationships
    defined on the resource class.

    :arg resource_class:
        The sqlalchemy model
    :arg str typename:
        The typename of the resources in the JSONapi. If not given, it is
        derived from the resource class.
    """

    def __init__(self, resource_class):
        """
        """
        super().__init__(resource_class)
        self.find_sqlalchemy_markers()
        return None

    def find_sqlalchemy_markers(self):
        """
        """
        inspection = sqlalchemy.inspect(self.resource_class)

        # Ignore the attributes used as primary key and relationship ids.
        ignore_columns = set()
        ignore_columns.update(col.key for col in inspection.primary_key)

        # Find the relationships
        for sql_rel in inspection.relationships.values():

            # Ignore the attributes, which are used as foreign keys.
            ignore_columns.update(col.key for col in sql_rel.local_columns)

            if sql_rel.key.startswith("_"):
                continue
            if sql_rel.key in self.fields:
                continue

            # *to-one*: MANYTOONE
            if sql_rel.direction == sqlalchemy.orm.interfaces.MANYTOONE:
                rel = ToOneRelationship(self.resource_class, sql_rel)
                self.relationships[rel.name] = rel
                self.fields.add(rel.name)

            # *to-many*: MANYTOMANY, ONETOMANY
            elif sql_rel.direction in (
                sqlalchemy.orm.interfaces.MANYTOMANY,
                sqlalchemy.orm.interfaces.ONETOMANY
                ):
                rel = ToManyRelationship(self.resource_class, sql_rel)
                self.relationships[rel.name] = rel
                self.fields.add(rel.name)

        # Find all attributes
        for sql_attr in inspection.attrs.values():
            if sql_attr.key.startswith("_"):
                continue
            if sql_attr.key in self.fields:
                continue
            if sql_attr.key in ignore_columns:
                continue

            attr = Attribute(self.resource_class, sql_attr)
            self.attributes[attr.name] = attr
            self.fields.add(attr.name)

        # Use the primary id of the resource_class, if no id marker is set.
        if self.id_attribute is None:
            self.id_attribute = IDAttribute(self.resource_class)
        return None
