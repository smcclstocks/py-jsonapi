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
jsonapi.sqlalchemy.database
===========================

The database adapter for *sqlalchemy*.
"""

# std
from itertools import groupby
import logging

# local
import jsonapi
from . import schema


__all__ = [
    "Database",
    "Session"
]


LOG = logging.getLogger(__file__)


class Database(jsonapi.base.database.Database):
    """
    This adapter must be chosen for sqlalchemy models.

    :arg sessionmaker:
        The function used to get a sqlalchemy session. If not given, the api
        settings must contain a `sqlalchemy_sessionmaker` key.
    :arg jsonapi.base.api.API api:
    """

    def __init__(self, sessionmaker=None, api=None):
        super().__init__(api=api)

        if sessionmaker is None and api is not None:
            sessionmaker = self.api.settings["sqlalchemy_sessionmaker"]
        self.sessionmaker = sessionmaker
        return None

    def init_api(self, api):
        super().init_api(api)
        if self.sessionmaker is None:
            self.sessionmaker = self.api.settings["sqlalchemy_sessionmaker"]
        return None

    def session(self):
        return Session(self.api, self.sessionmaker())


class Session(jsonapi.base.database.Session):
    """
    Implements the database adapter for sqlalchemy models.

    :arg jsonapi.base.api.API api:
    :arg sqla_session:
        SQLAlchemy session instance
    """

    def __init__(self, api, sqla_session):
        """
        """
        super().__init__(api)
        self.sqla_session = sqla_session
        return None

    def _build_filter_criterion(self, schema_, filters):
        """
        Builds the argument for the sqlalchemy query method
        :meth:`~sqlalchemy.orm.query.Query.filter`.

        .. todo::

            Implement the *add*, *size*, .. filters
        """
        criterions = list()
        for fieldname, filtername, value in filters:

            # For the moment, we only allow filterting on attributes.
            attr = schema_.attributes.get(fieldname)
            if not isinstance(attr, schema.Attribute):
                raise jsonapi.base.errors.UnfilterableField(filtername, fieldname)

            if filtername == "eq":
                criterions.append(attr.class_attr == value)
            elif filtername == "ne":
                criterions.append(attr.class_attr != value)
            elif filtername == "lt":
                criterions.append(attr.class_attr < value)
            elif filtername == "lte":
                criterions.append(attr.class_attr <= value)
            elif filtername == "gt":
                criterions.append(attr.class_attr > value)
            elif filtername == "gte":
                criterions.append(attr.class_attr >= value)
            elif filtername == "in":
                criterions.append(attr.class_attr.in_(value))
            elif filtername == "nin":
                criterions.append(attr.class_attr.notin_(value))
            elif filtername == "all":
                # .. todo:: Implement it.
                raise jsonapi.base.errors.UnfilterableField(filtername, fieldname)
            elif filtername == "size":
                # .. todo:: Implement it.
                raise jsonapi.base.errors.UnfilterableField(filtername, fieldname)
            elif filtername == "exists":
                criterions.append(attr.class_attr != None)
            elif filtername == "iexact":
                # .. todo:: Escape *value*
                criterions.append(attr.class_attr.ilike(value))
            elif filtername == "contains":
                criterions.append(attr.class_attr.contains(value))
            elif filtername == "icontains":
                # .. todo:: Escape *value*
                criterions.append(attr.class_attr.ilike("%" + value + "%"))
            elif filtername == "startswith":
                criterions.append(attr.class_attr.startswith(value))
            elif filtername == "istartswith":
                # .. todo:: Escape *value*
                criterions.append(attr.class_attr.ilike(value + "%"))
            elif filtername == "endswith":
                criterions.append(attr.class_attr.endswith(value))
            elif filtername == "iendswith":
                # .. todo:: Escape *value*
                criterions.append(attr.class_attr.ilike("%" + value))
            elif filtername == "match":
                # .. todo:: This only works for MYSQL
                criterions.append(attr.class_attr.op("regexp")(value))
            else:
                raise jsonapi.base.errors.UnfilterableField(filtername, fieldname)
        return criterions

    def _build_order_criterion(self, schema_, order):
        """
        Builds the argument for the sqlalchemy query method
        :meth:`~sqlalchemy.orm.query.Query.order_by`.

        .. todo::

            Support ordering also for relationships and hybrid methods.
        """
        criterions = list()
        for direction, fieldname in order:

            # We only support sorting for attributes at the moment.
            attr = schema_.attributes.get(fieldname)
            if not isinstance(attr, schema.Attribute):
                raise jsonapi.base.errors.UnsortableField(schema_.typename, fieldname)

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
        resource_class = self.api.get_resource_class(typename)
        schema_ = self.api.get_schema(typename)

        query = self.sqla_session.query(resource_class)

        if filters:
            filter_criterion = self._build_filter_criterion(schema_, filters)
            query = query.filter(*filter_criterion)

        if order:
            order_criterion = self._build_order_criterion(schema_, order)
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

    def get(self, identifier, required=False):
        """
        """
        typename, resource_id = identifier
        resource_class = self.api.get_resource_class(typename)
        resource = self.sqla_session.query(resource_class).get(resource_id)

        if resource is None:
            raise jsonapi.base.errors.ResourceNotFound(identifier)
        return resource

    def get_many(self, identifiers, required=False):
        """
        .. todo::

            Can we require them in a bulk?
        """
        resources = {
            identifier: self.get(identifier, required)\
            for identifier in identifiers
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
