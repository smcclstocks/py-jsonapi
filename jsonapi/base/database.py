#!/usr/bin/env python3

"""
jsonapi.base.database
=====================

:license: GNU Affero General Public License v3
:copyright: 2016 by Benedikt Schmitt <benedikt@benediktschmitt.de>

This module defines some abstract classes, which provide a common interface
for the database interactions required by a JSONapi flow.

If you want to implement your own database adapter, you must extend
:class:`Database` and :class:`DatabaseSession` according to their documentation.
"""

# std
from itertools import groupby
import logging

# local
from . import errors
from .utilities import (
    ensure_identifier,
    relative_identifiers
)


__all__ = [
    "Database",
    "DatabaseSession"
]


LOG = logging.getLogger(__file__)


class Database(object):
    """
    This class defines the base for a database adapter.

    :arg jsonapi.base.api.API api:
        The api, which uses this database
        (see also: :meth:`~jsonapi.base.api.API.add_model`). The api may be
        given later via :meth:`init_api`.
    """

    def __init__(self, api=None):
        """
        """
        self.api = api
        return None

    def init_api(self, api):
        """
        :arg jsonapi.base.api.API api:
            The API, which uses this database adapter.
            See also :meth:`~jsonapi.base.api.API.add_model`
        """
        self.api = api
        return None

    def session(self):
        """
        **Must be overridden**

        Returns a new instance of :class:`DatabaseSession`.
        """
        raise NotImplementedError()


class DatabaseSession(object):
    """
    This class defines a base for a database session. A session wraps a
    transaction. Changes made on resources, must only be commited to the
    database, when :meth:`commit` is called.

    :arg jsonapi.base.api.API api:
    """

    def __init__(self, api):
        """
        """
        self.api = api
        return None

    def query(self, typename,
        *, sorting=None, limit=None, offset=None, filters=None
        ):
        """
        **Must be overridden**

        *   sorting

            Is a list of two tuples of the form:

                ``[("+"|"-", field name), ...]``,

            which describes how the resources should be sorted.

            This value may be ignored.

            .. seealso::

                *   :attr:`jsonapi.base.request.Request.japi_sort`
                *   http://jsonapi.org/format/#fetching-sorting

        *   limit (int or None)

            Describes how many resources should be returned.

            This value may be ignored.

            .. seealso::

                *   :attr:`jsonapi.base.request.Request.japi_limit`

        *   offset (int or None)

            This value is usually combined with *limit* and describes how
            many resources should be skipped in the result.

            This value may be ignored.

            .. seealso::

                *   :attr:`jsonapi.base.request.Request.japi_offset`

        *   filters (None or dictionary)

            Describes how the resources in the result should be filterd.
            Resources which do not match the filters, should not be included.

            This value may be ignored.

            .. seealso::

                *   :attr:`jsonapi.base.request.Request.japi_filters`

        :raises errors.UnsortableField:
        :raises errors.UnfilterableField:
        """
        raise NotImplementedError()

    def query_size(self, typename,
        *, sorting=None, limit=None, offset=None, filters=None
        ):
        """
        **Must be overridden**

        It takes the same arguments as :meth:`query`, but returns only the
        number of resources, which would be returned by :meth:`query`.
        """
        raise NotImplementedError()

    def get(self, identifier):
        """
        **Must be overridden**

        Returns the resource with the id ``identifier`` or None, if there is
        no resource with this id.

        :arg identifier:
            An identifier tuple: ``(typename, id)``
        """
        raise NotImplementedError()

    def get_many(self, identifiers):
        """
        **Must be overridden**

        Returns a dictionary, which maps each identifier in *identifiers*
        to a resource or None.

        .. code-block:: python3

            db.get_many([("people", "42"), ("articles", "18")])
            ... {
            ...     ("people", "42"): <People object at 0x.....>,
            ...     ("articles", "18"): None
            ... }

        :arg identifiers:
            A list of identifier tuples
        """
        raise NotImplementedError()

    def save(self, resources):
        """
        **Must be overridden**

        Schedules the resources for beeing saved in the database on the next
        :meth:`commit` call.

        :arg resources:
            A list of resource objects
        """
        raise NotImplementedError()

    def delete(self, resources):
        """
        **Must be overridden**

        Schedules the resources for beeing deleted in the database on the next
        :meth:`commit` call.

        :arg resources:
            A list of resource objects
        """
        raise NotImplementedError()

    def commit(self):
        """
        **Must be overridden**

        Commits all changes to the database.
        """
        raise NotImplementedError()

    def get_relatives(self, resources, path):
        """
        **May be overridden** for performance reasons.

        This method basically helps to implement the *include* query parameter
        defined in the JSONapi specification. *path* is a list of relationship
        names, starting with a relationship defined on every resource in
        *resources*. This method returns then all resources, which are related
        to at least one of the *resources*.

        E.g.:

        .. code-block:: python3

            db.get_relatives([lisa, bart, maggie], ["parent"])
            [<User (homer)>, <User (marge)>]

        :arg list resources:
            A list of resources.
        :arg list path:
            A list of relationship names. The first relationship must exist
            on every resource in *resources*.

        :raises UnresolvableIncludePath:
            If a relationship is not defined on any of the intermediate
            resources.

        .. seealso::

            *   :attr:`jsonapi.base.request.Request.japi_include`
            *   http://jsonapi.org/format/#fetching-includes
        """
        all_relatives = dict()
        for relname in path:
            # Collect the ids of all related resources.
            relids = set()
            for resource in resources:
                try:
                    tmp = relative_identifiers(self.api, resource, relname)
                except errors.RelationshipNotFound:
                    raise errors.UnresolvableIncludePath(path)
                else:
                    relids.update(tmp)

            # Query the relatives from the database.
            relatives = self.get_many(relids)
            all_relatives.update(relatives)

            # The next relationship name in the path is defined on the
            # previously fetched relatives.
            resources = relatives
        return all_relatives

    def get_relationships_dict(self, relobj):
        """
        Queries all resources named in the JSONapi relationships object *relobj*
        and returns a dictionary with the actual resources.

        .. code-block::
        """
        ids = collect_identifiers(relobj)
        relatives = self.get_many(ids)
        relationships = replace_identifiers_in_jsonapi_object(relobj, relatives)
        return relationships
