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

# third party
import mongoengine
from bson.objectid import ObjectId

# local
from jsonapi import base
from jsonapi.base import errors
from .marker import MongoEngineAttribute


__all__ = [
    "Database",
    "DatabaseSession"
]


class Database(base.database.Database):
    """
    This adapter must be chosen for mongoengine models.
    """

    def session(self):
        """
        """
        return DatabaseSession(api=self.api)


class DatabaseSession(base.database.DatabaseSession):
    """
    Loads mongoengine documents from the database.
    """

    def _build_filter_criterion(self, markup, filters):
        """
        Builds a dictionary, which can be used inside a document's *objects()*
        method to filter the resources by the *japi_filters* dictionary.
        """
        d = dict()
        for fieldname, filtername, value in filters:

            # We only allow filtering for mongoengine attributes.
            attribute = markup.attributes.get(fieldname)
            if not isinstance(attribute, MongoEngineAttribute):
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

    def _build_order_criterion(self, markup, order):
        """
        Converts the *order* list into a representation, which can be used with
        mongoengine's queryset *order_by()* method.
        """
        criterion = list()
        for direction, field_name in order:

            # We only support sorting for attributes at the moment.
            attribute = markup.attributes.get(field_name)
            if not isinstance(attribute, me_markup.MongoEngineAttribute):
                raise errors.UnsortableField(markup.typename, field_name)

            criterion.append(direction + attribute.name)
        return criterion

    def _build_query(self, typename,
        *, order=None, limit=None, offset=None, filters=None
        ):
        """
        """
        model = self.api.get_model(typename)
        markup = self.api.get_markup(typename)

        if filters:
            filters = self._build_filter_criterion(markup, filters)
            query = model.objects(**filters)
        else:
            query = model.objects()

        if order:
            order = self._build_order_criterion(markup, order)
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

    def get(self, identifier):
        """
        """
        typename, resource_id = identifier
        model = self.api.get_model(typename)
        resource = model.objects(id=resource_id).first()
        return resource

    def get_many(self, identifiers):
        """
        """
        results = dict()

        # Group the identifiers by the typenames.
        group_key = lambda identifier: identifier[0]
        for typename, identifiers in groupby(identifiers, group_key):
            model = self.api.get_model(typename)
            markup = self.api.get_markup(typename)

            # Extract the resource ids, fetch the resources and add them
            # to the result.
            #
            # .. todo::
            #
            #   mongoengine requires an explicit ObjectId object here.
            #   Remove the conversion, when it is no longer needed.
            resource_ids = [ObjectId(e[1]) for e in identifiers]
            resources = model.objects().in_bulk(resource_ids)

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
        """
        for resource in resources:
            resource.save()
        return None

    def delete(self, resources):
        """
        .. todo::

            Don't save the resources instantly. Wait until :meth:`commit`
            is called.
        """
        for resource in resources:
            resource.delete()
        return None

    def commit(self):
        """
        """
        return None
