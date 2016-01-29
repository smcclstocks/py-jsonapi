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
import sqlalchemy

# local
from jsonapi import marker


__all__ = [
    "SQLAlchemyMarkup"
]


log = logging.getLogger(__file__)


class SQLAlchemyAttribute(marker.markup.Attribute):
    """
    Wraps an sqlalchemy attribute.

    :arg model:
        The sqlchemy model class
    :arg sqlattr:
        An sqlalchemy ColumnProperty
    """

    def __init__(self, model, sqlattr):
        """
        """
        super().__init__(name=sqlattr.key)

        self.sqlattr = sqlattr
        self.class_attr = sqlattr.class_attribute
        self.model = model
        return None

    def get(self, resource):
        return self.class_attr.__get__(resource, None)

    def set(self, resource, value):
        return self.class_attr.__set__(resource, value)

    def delete(self, resource):
        return self.class_attr.__delete__(resource)


class SQLAlchemyIDAttribute(marker.markup.IDAttribute):
    """
    Wraps an sqlalchemy primary key. We only allow reading the id, but not
    changing it.

    .. todo::

        We currently support only primary keys with one column.
        Add support for composite primary keys.

    .. todo::

        We currently use the inspection module of sqlalchemy to get the
        primary key. Can we optimize this?
    """

    def __init__(self, model):
        super().__init__()

        self.model = model
        return None

    def get(self, resource):
        """
        We use the Inspector for :attr:`model` to get the primary key
        for the resource.
        """
        keys = sqlalchemy.inspect(resource).identity
        return str(keys[0]) if keys is not None else None


class SQLAlchemyToOneRelationship(marker.markup.ToOneRelationship):
    """
    Wraps an sqlalchemy to-one relationship.
    """

    def __init__(self, model, sqlrel):
        super().__init__(name=sqlrel.key)

        self.sqlrel = sqlrel
        self.class_attr = sqlrel.class_attribute
        self.model = model
        return None

    def get(self, resource):
        return self.class_attr.__get__(resource, None)

    def set(self, resource, relative):
        return self.class_attr.__set__(resource, relative)

    def delete(self, resource):
        return self.class_attr.__delete__(resource)


class SQLAlchemyToManyRelationship(marker.markup.ToManyRelationship):
    """
    Wraps an sqlalchemy to-many relationship.
    """

    def __init__(self, model, sqlrel):
        super().__init__(name=sqlrel.key)

        self.sqlrel = sqlrel
        self.class_attr = sqlrel.class_attribute
        self.model = model
        return None

    def get(self, resource):
        return self.class_attr.__get__(resource, None)

    def set(self, resource, relatives):
        self.class_attr.__set__(resource, relatives)
        return None

    def delete(self, resource):
        self.class_attr.__delete__(resource)
        return None

    def add(self, resource, relative):
        relatives = self.class_attr.__get__(resource, None)
        relatives.append(relative)
        return None

    def extend(self, resource, new_relatives):
        relatives = self.class_attr.__get__(resource, None)
        relatives.extend(new_relatives)
        return None

    def remove(self, resource, relative):
        relatives = self.class_attr.__get__(resource)
        try:
            relatives.remove(relative)
        except ValueError:
            pass
        return None


class SQLAlchemyMarkup(marker.markup.Markup):
    """
    Finds also sqlalchemy attributes and relationships on the model.
    """

    def __init__(self, model):
        """
        """
        super().__init__(model)
        self.find_sqlalchemy_markers()
        return None

    def find_sqlalchemy_markers(self):
        """
        .. todo:: Find hybrid methods and properties.
        .. todo:: Ignore the id (primary key) attributes.
        .. todo:: Ignore the foreign key attributes.
        """
        inspection = sqlalchemy.inspect(self.model)

        # Find the relationships
        for sql_rel in inspection.relationships.values():
            if sql_rel.key.startswith("_"):
                continue
            if sql_rel.key in self.fields:
                continue

            # *to-one*: MANYTOONE
            if sql_rel.direction == sqlalchemy.orm.interfaces.MANYTOONE:
                rel = SQLAlchemyToOneRelationship(
                    self.model, sql_rel
                )
                self.relationships[rel.name] = rel
                self.fields.add(rel.name)

            # *to-many*: MANYTOMANY, ONETOMANY
            elif sql_rel.direction in (
                sqlalchemy.orm.interfaces.MANYTOMANY,
                sqlalchemy.orm.interfaces.ONETOMANY
                ):
                rel = SQLAlchemyToManyRelationship(
                    self.model, sql_rel
                )
                self.relationships[rel.name] = rel
                self.fields.add(rel.name)

        # Find all attributes
        for sql_attr in inspection.attrs.values():
            if sql_attr.key.startswith("_"):
                continue
            if sql_attr.key in self.fields:
                continue

            attr = SQLAlchemyAttribute(self.model, sql_attr)
            self.attributes[attr.name] = attr
            self.fields.add(attr.name)

        # Use the primary id of the model, if not id marker is set.
        if self.id_attribute is None:
            self.id_attribute = SQLAlchemyIDAttribute(self.model)
        return None
