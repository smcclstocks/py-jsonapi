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
jsonapi.base.database
=====================

This module defines some abstract classes, which provide a common interface
for the database interactions required by a JSONapi flow.

If you want to implement your own database adapter, you must extend
:class:`Database` and :class:`Session` according to their documentation. You
can take a look at the existing database adapters, if you need an example.
"""

# local
from . import errors
from .utilities import relative_identifiers


__all__ = [
    "Database",
    "Session"
]


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

        Returns a new instance of :class:`Session`.
        """
        raise NotImplementedError()


class Session(object):
    """
    This class defines a base for a database session. A session wraps a
    transaction. Changes made on resources, must only be commited to the
    database, when :meth:`commit` is called.

    If a resource is queried twice, the same object must be returned (The
    Python :func:`id` must be equal).

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

    def get(self, identifier, required=False):
        """
        **Must be overridden**

        Returns the resource with the id ``identifier`` or None, if there is
        no resource with this id.

        :arg identifier:
            An identifier tuple: ``(typename, id)``
        :arg bool required:
            If true, throw a ResourceNotFound error if the resource with the
            id does not exist.

        :raises jsonapi.base.errors.ResourceNotFound:
        """
        raise NotImplementedError()

    def get_many(self, identifiers, required=False):
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
        :arg bool required:
            If true, throw a ResourceNotFound error if a resource does not
            exist.

        :raises jsonapi.base.errors.ResourceNotFound:
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

    def get_relatives(self, resources, paths):
        """
        **May be overridden** for performance reasons.

        This method basically helps to implement the *include* query parameter
        defined in the JSONapi specification. *path* is a list of relationship
        names, starting with a relationship defined on every resource in
        *resources*. This method returns then all resources, which are related
        to at least one of the *resources*.

        E.g.:

        .. code-block:: python3

            # get_relatives() takes a **list** of paths and
            # ["parent"] is one path.
            db.get_relatives([lisa, bart, maggie], [["parent"]])
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

        .. todo::

            *get_relatives()* is not an expressive name for the functionality
            of this method.
        """
        all_relatives = dict()
        root_resources = resources

        for path in paths:
            resources = root_resources
            for relname in path:
                # Collect the ids of all related resources.
                relids = set()
                for resource in resources:
                    try:
                        tmp = relative_identifiers(relname, resource)
                    except errors.RelationshipNotFound:
                        raise errors.UnresolvableIncludePath(path)
                    else:
                        relids.update(tmp)

                # Query the relatives from the database.
                relatives = self.get_many(relids, required=True)
                all_relatives.update(relatives)

                # The next relationship name in the path is defined on the
                # previously fetched relatives.
                resources = relatives.values()
        return all_relatives
