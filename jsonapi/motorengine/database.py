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
jsonapi.motorengine.database
============================

The database adapter for motorengine documents.
"""

# std
import asyncio
from itertools import groupby

# third party
import motorengine
from tornado.platform.asyncio import to_asyncio_future
from bson.objectid import ObjectId

# local
import jsonapi
from . import schema


__all__ = [
    "Database",
    "Session"
]


class Database(jsonapi.base.database.Database):
    """
    This adapter must be chosen for motorengine models. We assume that the
    database connection has been created with ``motorengine.connect()``.

    This adapter only works with **asynchronous** apis.
    """

    def session(self):
        """
        """
        return Session(api=self.api)


class Session(jsonapi.asyncio.database.Session):
    """
    Loads motorengine documents from the database.
    """

    def __init__(self, api):
        super().__init__(api)

        # We cached the saved resources and deleted resources. The changes
        # will be sent to the database, when *commit()* is called.
        self._saved_resources = dict()
        self._added_resources = set()
        self._deleted_resources = dict()
        return None

    def _add_filter_criterions(self, query, schema_, filters):
        """
        Adds the filter criterions to the *query*.
        """
        d = dict()
        for fieldname, filtername, value in filters:

            # We only allow filtering for motorengine attributes.
            attribute = schema_.attributes.get(fieldname)
            if not isinstance(attribute, schema.Attribute):
                raise errors.UnfilterableField(
                    schema_.typename, filtername, fieldname
                )

            if filtername == "eq":
                d[attribute.name] = value
            elif filtername == "ne":
                d[attribute.name + "__ne"] = value
            elif filtername == "lt":
                d[attribute.name + "__lt"] = value
            elif filtername == "lte":
                d[attribute.name + "__lte"] = value
            elif filtername == "gt":
                d[attribute.name + "__gt"] = value
            elif filtername == "gte":
                d[attribute.name + "__gte"] = value
            elif filtername == "in":
                d[attribute.name + "__in"] = value
            elif filtername == "nin":
                d[attribute.name + "__nin"] = value
            elif filtername == "all":
                d[attribute.name + "__all"] = value
            elif filtername == "size":
                d[attribute.name + "__size"] = value
            elif filtername == "exists":
                d[attribute.name + "__exists"] = value
            elif filtername == "iexact":
                d[attribute.name + "__iexact"] = value
            elif filtername == "contains":
                d[attribute.name + "__contains"] = value
            elif filtername == "icontains":
                d[attribute.name + "__icontains"] = value
            elif filtername == "startswith":
                d[attribute.name + "__startswith"] = value
            elif filtername == "istartswith":
                d[attribute.name + "__istartswith"] = value
            elif filtername == "endswith":
                d[attribute.name + "__endswith"] = value
            elif filtername == "iendswith":
                d[attribute.name + "__iendswith"] = value
            elif filtername == "match":
                d[attribute.name + "__match"] = value
            else:
                raise errors.UnfilterableField(
                    schema_.typename, filtername, fieldname
                )

        query = query.filter(**d)
        return query

    def _add_order_criterion(self, query, schema_, order):
        """
        Adds the order criterions to the motorengine *query*.
        """
        for direction, fieldname in order:
            # We only support sorting for attributes at the moment.
            attribute = schema_.attributes.get(fieldname)
            if not isinstance(attribute, schema.Attribute):
                raise errors.UnsortableField(schema_.typename, fieldname)

            if direction == "+":
                query.order_by(attribute.name, motorengine.ASCENDING)
            else:
                query.order_by(attribute.name, motorengine.DESCENDING)
        return query

    def _build_query(self, typename,
        *, order=None, limit=None, offset=None, filters=None
        ):
        """
        """
        resource_class = self.api.get_resource_class(typename)
        schema_ = self.api.get_schema(typename)
        query = resource_class.objects
        if filters:
            query = self._add_filter_criterions(query, schema_, filters)
        if order:
            query = self._add_order_criterion(query, schema_, order)
        if offset:
            query = query.skip(offset)
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
        return to_asyncio_future(query.find_all())

    def query_size(self, typename,
        *, order=None, limit=None, offset=None, filters=None
        ):
        """
        """
        query = self._build_query(
            typename, order=order, limit=limit, offset=offset, filters=filters
        )
        return to_asyncio_future(query.count())

    @asyncio.coroutine
    def get(self, identifier, required=False):
        """
        """
        typename, resource_id = identifier
        resource_class = self.api.get_resource_class(typename)

        resource = yield from to_asyncio_future(
            resource_class.objects.get(resource_id)
        )
        if required and resource is None:
            raise jsonapi.base.errors.ResourceNotFound(identifier)
        return resource

    @asyncio.coroutine
    def get_many(self, identifiers, required=False):
        """
        .. todo:: Use bulk get.
        """
        resources = dict()
        for identifier in identifiers:
            resource = yield from self.get(identifier, required)
            resources[identifier] = resource
        return resources

    def save(self, resources):
        """
        """
        for resource in resources:
            schema = resource._jsonapi["schema"]
            identifier = (schema.typename, schema.id_attribute.get(resource))

            if identifier[1]:
                self._saved_resources[identifier] = resource
                self._deleted_resources.pop(identifier, None)
            else:
                self._added_resources.add(resource)
        return None

    def delete(self, resources):
        """
        """
        for resource in resources:
            schema = resource._jsonapi["schema"]
            identifier = (schema.typename, schema.id_attribute.get(resource))

            if identifier[1]:
                self._deleted_resources[identifier] = resource
                self._saved_resources.pop(identifier, None)
            else:
                self._added_resources.discard(resource)
        return None

    @asyncio.coroutine
    def commit(self):
        """
        .. todo:: Use bulk insert and bulk delete.
        """
        for resource in self._added_resources:
            yield from to_asyncio_future(resource.save())
            
        for resource in self._saved_resources.values():
            yield from to_asyncio_future(resource.save())

        for resource in self._deleted_resources.values():
            yield from to_asyncio_future(resource.delete())
        return None
