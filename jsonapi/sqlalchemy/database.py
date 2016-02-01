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
from itertools import groupby
import logging

# local
from jsonapi import base
from .marker import SQLAlchemyAttribute


__all__ = [
    "Database",
    "DatabaseSession"
]


log = logging.getLogger(__file__)


class Database(base.database.Database):
    """
    This adapter must be chosen for sqlalchemy models.

    :arg sessionmaker:
        The function used to get a sqlalchemy session. If not given, the api
        settings must contain a `sqlalchemy_sessionmaker` key.
    """

    def __init__(self, sessionmaker=None, api=None):
        super().__init__(api=api)

        if sessionmaker is None:
            sessionmaker = self.api.settings["sqlalchemy_sessionmaker"]
        self.sessionmaker = sessionmaker
        return None

    def session(self):
        """
        Returns a :class:`DatabaseSession`, which can be used to query
        sqlalchemy models.
        """
        return DatabaseSession(self.api, self.sessionmaker())


class DatabaseSession(base.database.DatabaseSession):
    """
    Implements the database adapter for sqlalchemy models.

    :arg jsonapi.base.api.API api:
    :arg sqla_session:
    """

    def __init__(self, api, sqla_session):
        """
        """
        super().__init__(api)
        self.sqla_session = sqla_session
        return None

    def _build_filter_criterion(self, markup, filters):
        """
        Builds the argument for the sqlalchemy query method
        :meth:`~sqlalchemy.orm.query.Query.filter`.

        .. todo::

            Support filtering also for relationships and hybrid methods.

        .. todo::

            Implement the *add*, *size*,
        """
        criterions = list()
        for field_name, filter_, value in filters:

            # For the moment, we only allow filterting on attributes.
            attr = markup.attributes.get(field_name)
            if not isinstance(attr, SQLAlchemyAttribute):
                raise errors.UnfilterableField(filter_, field_name)

            if filter_ == "eq":
                criterions.append(attr.class_attr == value)
            elif filter_ == "ne":
                criterions.append(attr.class_attr != value)
            elif filter_ == "lt":
                criterions.append(attr.class_attr < value)
            elif filter_ == "lte":
                criterions.append(attr.class_attr <= value)
            elif filter_ == "gt":
                criterions.append(attr.class_attr > value)
            elif filter_ == "gte":
                criterions.append(attr.class_attr >= value)
            elif filter_ == "in":
                criterions.append(attr.class_attr.in_(value))
            elif filter_ == "nin":
                criterions.append(attr.class_attr.notin_(value))
            elif filter_ == "all":
                raise errors.UnfilterableField(filter_, field_name)
            elif filter_ == "size":
                raise errors.UnfilterableField(filter_, field_name)
            elif filter_ == "exists":
                criterions.append(attr.class_attr != None)
            elif filter_ == "iexact":
                # .. todo:: Escape *value*
                criterions.append(attr.class_attr.ilike(value))
            elif filter_ == "contains":
                criterions.append(attr.class_attr.contains(value))
            elif filter_ == "icontains":
                # .. todo:: Escape *value*
                criterions.append(attr.class_attr.ilike("%" + value + "%"))
            elif filter_ == "startswith":
                criterions.append(attr.class_attr.startswith(value))
            elif filter_ == "istartswith":
                # .. todo:: Escape *value*
                criterions.append(attr.class_attr.ilike(value + "%"))
            elif filter_ == "endswith":
                criterions.append(attr.class_attr.endswith(value))
            elif filter_ == "iendswith":
                # .. todo:: Escape *value*
                criterions.append(attr.class_attr.ilike("%" + value))
            elif filter_ == "match":
                # .. todo:: This only works for MYSQL
                criterions.append(attr.class_attr.op("regexp")(value))
            else:
                raise errors.UnfilterableField(filter_, field_name)
        return criterions

    def _build_order_criterion(self, markup, order):
        """
        Builds the argument for the sqlalchemy query method
        :meth:`~sqlalchemy.orm.query.Query.order_by`.

        .. todo::

            Support ordering also for relationships and hybrid methods.
        """
        criterions = list()
        for direction, field_name in order:

            # We only support sorting for attributes at the moment.
            attr = markup.attributes.get(field_name)
            if not isinstance(attr, SQLAlchemyAttribute):
                raise errors.UnsortableField(markup.typename, field_name)

            if direction == "+":
                criterions.append(attr.class_attr.asc())
            else:
                criterions.append(attr.class_attr.desc())
        return criterions

    def _build_query(self, typename,
        *, order=None, limit=None, offset=None, filters=None
        ):
        """
        Maps the arguments to a sqlalchemy query object and returns it.
        """
        model = self.api.get_model(typename)
        markup = self.api.get_markup(typename)

        query = self.sqla_session.query(model)

        if filters:
            filter_criterion = self._build_filter_criterion(markup, filters)
            query = query.filter(*filter_criterion)

        if order:
            order_criterion = self._build_order_criterion(markup, order)
            query = query.order_by(*order_criterion)

        if offset:
            query = query.offset(offset)

        if limit:
            query = query.limit(limit)
        return query

    def query(self, typename,
        *, order=None, limit=None, offset=None, filters=None
        ):
        """
        """
        query = self._build_query(
            typename, order=order, limit=limit, offset=offset, filters=filters
        )
        return list(query)

    def query_size(self, typename,
        *, order=None, limit=None, offset=None, filters
        ):
        """
        """
        query = self._build_query(
            typename, order=order, limit=limit, offset=offset, filters=filters
        )
        return query.count()

    def get(self, identifier):
        """
        """
        typename, resource_id = identifier
        model = self.api.get_model(typename)
        resource = self.sqla_session.query(model).get(resource_id)
        return resource

    def get_many(self, identifiers):
        """
        .. todo:: Make this more efficient.
        """
        resources = {
            identifier: self.get(identifier) for identifier in identifiers
        }
        return resources

    def save(self, resources):
        """
        """
        self.sqla_session.add_all(resources)
        return None

    def delete(self, resources):
        """
        """
        for resource in resources:
            self.sqla_session.delete(resource)
        return None

    def commit(self):
        """
        """
        self.sqla_session.commit()
        return None
