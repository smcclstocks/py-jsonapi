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
jsonapi.mongoengine.database
============================

The database adapter for mongoengine documents.
"""

# std
from itertools import groupby

# third party
import mongoengine
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
    This adapter must be chosen for mongoengine models. We assume that the
    database connection has been created with ``mongoengine.connect()``.
    """

    def session(self):
        """
        """
        return Session(api=self.api)


class Session(jsonapi.base.database.Session):
    """
    Loads mongoengine documents from the database.
    """

    def _build_filter_criterion(self, schema_, filters):
        """
        Builds a dictionary, which can be used inside a document's *objects()*
        method to filter the resources by the *japi_filters* dictionary.

        :arg jsonapi.mongoengine.schema.Schema schema_:
        :arg filters:
        """
        d = dict()
        for fieldname, filtername, value in filters:

            # We only allow filtering for mongoengine attributes.
            attribute = schema_.attributes.get(fieldname)
            if not isinstance(attribute, schema.Attribute):
                raise errors.UnfilterableField(filtername, fieldname)

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
                raise errors.UnfilterableField(filtername, fieldname)
        return d

    def _build_order_criterion(self, schema_, order):
        """
        Converts the *order* list into a representation, which can be used with
        mongoengine's queryset *order_by()* method.

        :arg jsonapi.mongoengine.schema.Schema schema_:
        :arg order:
        """
        criterion = list()
        for direction, fieldname in order:

            # We only support sorting for attributes at the moment.
            attribute = schema_.attributes.get(fieldname)
            if not isinstance(attribute, schema.Attribute):
                raise errors.UnsortableField(schema_.typename, fieldname)

            criterion.append(direction + attribute.name)
        return criterion

    def _build_query(self, typename,
        *, order=None, limit=None, offset=None, filters=None
        ):
        """
        """
        resource_class = self.api.get_resource_class(typename)
        schema_ = self.api.get_schema(typename)

        if filters:
            filters = self._build_filter_criterion(schema_, filters)
            query = resource_class.objects(**filters)
        else:
            query = resource_class.objects()

        if order:
            order = self._build_order_criterion(schema_, order)
            query = query.order_by(*order)

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
        resources = list(query)
        return resources

    def query_size(self, typename,
        *, order=None, limit=None, offset=None, filters=None
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
        resource = resource_class.objects(id=resource_id).first()
        if required and resource is None:
            raise jsonapi.base.errors.ResourceNotFound(identifier)
        return resource

    def get_many(self, identifiers, required=False):
        """
        """
        results = dict()

        # Group the identifiers by the typenames.
        group_key = lambda identifier: identifier[0]
        for typename, identifiers in groupby(identifiers, group_key):
            resource_class = self.api.get_resource_class(typename)
            schema_ = self.api.get_schema(typename)

            # Extract the resource ids, fetch the resources and add them
            # to the result.
            #
            # .. todo::
            #
            #   mongoengine requires an explicit ObjectId object here.
            #   Remove the conversion, when it is no longer needed.
            resource_ids = [ObjectId(e[1]) for e in identifiers]
            resources = resource_class.objects().in_bulk(resource_ids)

            # Break, if a resource does not exist.
            not_found = resources.keys() - resource_ids
            if required and not_found:
                raise jsonapi.base.errors.ResourceNotFound(
                    identifier=(typename, not_found.pop())
                )

            results.update({
                (typename, str(resource_id)): resource\
                for resource_id, resource in resources.items()
            })
        return results

    def save(self, resources):
        """
        .. todo::

            Don't save the resources instantly. Wait until :meth:`commit`
            is called.

        .. todo::

            Is there something like *bulk_save()* ?
        """
        for resource in resources:
            resource.save()
        return None

    def delete(self, resources):
        """
        .. todo::

            Don't save the resources instantly. Wait until :meth:`commit`
            is called.

        .. todo::

            Is there something like *bulk_delete()* ?
        """
        for resource in resources:
            resource.delete()
        return None

    def commit(self):
        """
        """
        return None
