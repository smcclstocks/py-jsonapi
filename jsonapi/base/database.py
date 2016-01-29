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

"""
jsonapi.base.database
=====================

This module defines some abstract classes, which provide a common interface
for using a database.

If you need to implement your own database adapter, you have to subclass
:class:`Database` and :class:`DatabaseSession`.
"""

# std
from itertools import groupby

# local
from . import utilities
from . import errors


__all__ = [
    "Database",
    "DatabaseSession",
    "BulkSession"
]


class Database(object):
    """
    This class defines the base for a database adapter. It is purely abstract.

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

        :raises UnsortableField:
            If the results can not be ordered by a field values.
        :raises UnsupportedFilter:
            If a filtername does not exist or is not supported on a
            specific field.
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


class BulkSession(object):
    """
    Works as container for all database adapters known to an
    :class:`~jsonapi.base.api.API`. Each request has its own bulk session,
    which allows it to access all database adapters through a common interface.

    :arg jsonapi.base.api.API api:
    """

    def __init__(self, api):
        """
        """
        self.api = api

        # Maps the database adapter to the database session.
        self.sessions = dict()
        return None

    def session(self, typename):
        """
        Returns the database session, which must be used for resources of the
        type *typename*. If no session for the database has been created, it
        will be done now.

        :arg str typename:
        :rtype: jsonapi.base.database.DatabaseSession

        .. seealso::

            *   :meth:`jsonapi.base.api.API.get_db`
            *   :meth:`Database.session`
        """
        db = self.api.get_db(typename)
        if not db in self.sessions:
            self.sessions[db] = db.session()
        return self.sessions[db]

    def session_by_db(self, db):
        """
        If a session for the database adapter *db* already exists, it is
        returned. Otherwise, a new session is created.

        :arg jsonapi.base.database.Database db:
        :rtype: jsonapi.base.database.DatabaseSession

        .. seealso::

            *   :meth:`Database.session`
        """
        if not db in self.sessions:
            self.sessions[db] = db.session()
        return self.sessions[db]

    def query(self, typename,
        *, order=None, limit=None, offset=None, filters=None
        ):
        """
        :seealso: :meth:`DatabaseSession.query`
        """
        session = self.session(typename)
        return session.query(
            typename, order=order, limit=limit, offset=offset, filters=filters
        )

    def query_size(self, typename,
        *, order=None, limit=None, offset=None, filters=None
        ):
        """
        :seealso: :meth:`DatabaseSession.query_size`
        """
        session = self.session(typename)
        return session.query_size(
            typename, order=order, limit=limit, offset=offset, filters=filters
        )

    def get(self, identifier):
        """
        :seealso: :meth:`DatabaseSession.get`
        """
        typename, resource_id = identifier
        session = self.session(typename)
        return session.get(identifier)

    def get_many(self, identifiers):
        """
        :seealso: :meth:`DatabaseSession.get_many`
        """
        result = dict()

        # Group the resources by the database, which is associated with them.
        group_key = lambda identifier: self.api.get_db(identifier[0])
        for db, identifiers in groupby(identifiers, group_key):
            # We need to *list()* the identifiers, because groupby() allows
            # us to only iterate once over them.
            identifiers = list(identifiers)
            session = self.session_by_db(db)
            resources = session.get_many(identifiers)
            result.update(resources)
        return result

    def fetch_includes(self, resources, include_paths):
        """
        *include_paths* is a list of include paths. An include path is a
        list of relationship names, starting with a relationship defined on
        the *resources*:

        .. code-block:: python3

            ("comments", "author")
            ("related_articles")

        This method follow the include paths and returns a dictionary, which
        contains all related resources on every include path.

        :arg list resources:
        :arg list include_paths:

        :raises jsonapi.base.errors.IncludePathNotFound:

        .. seealso::

            *   :attr:`jsonapi.base.request.Request.japi_include`
            *   http://jsonapi.org/format/#fetching-includes

        .. todo:: Optimize this method
        """
        # include_paths may be None
        if not include_paths:
            return dict()

        result = dict()
        for include_path in include_paths:

            # Follow the include path.
            # The include path is a list of relationship names and the
            # first relationship is defined on the *resources*.
            curr_resources = resources
            for relationship_name in include_path:
                relative_identifiers = set()
                for resource in curr_resources:
                    typename = self.api.get_typename(resource)
                    serializer = self.api.get_serializer(typename)

                    # Raise an exception, if we can not resolve the path.
                    if not serializer.has_relationship(relationship_name):
                        raise errors.IncludePathNotFound(include_path)

                    # Get the id the related resource (one or None)
                    elif serializer.is_to_one_relationship(relationship_name):
                        identifier = serializer.get_relative_id(
                            resource, relationship_name
                        )
                        if identifier is not None:
                            relative_identifiers.add(identifier)

                    # Get the ids of the related resources.
                    else:
                        identifiers = serializer.get_relative_ids(
                            resource, relationship_name
                        )
                        relative_identifiers.update(identifiers)

                # Load all related resources.
                relatives = self.get_many(relative_identifiers)
                result.update(relatives)

                # The next relationship path component is defined on
                # *relatives*
                curr_resources = list(relatives.values())
        return result

    def load_japi_relationships(self, rel_obj):
        """
        Loads the relationships based upon a JSONapi relationships object:

        .. code-block:: python3

            "author": {
                "data": {"type": "User", "id": 42}
            },
            "comments": {
                "data": [
                    {"type": "User", "id": "19"},
                    {"type": "User", "id": "20"}
                ]
            }
            "publisher": {
                "data": None
            }

        and returns a dictionary, which maps the relationship name to the
        related resources:

        .. code-block:: python3

            {
                "author": UserObject(...),
                "comments": [UserObject(...), UserObject(...)],
                "publisher": None
            }

        :arg dict rel_obj:
        """
        # Collect all resource ids.
        ids = utilities.collect_identifiers(rel_obj)

        # Query the related resources.
        resources = self.get_many(ids)

        # Map the relationship name to the related resources.
        relatives = dict()
        for rel_name in rel_obj.keys():
            rel_data = rel_obj[rel_name]["data"]
            # to-many relationship
            if isinstance(rel_data, list):
                relatives[rel_name] = [
                    resources[(item["type"], item["id"])]\
                    for item in rel_data
                ]
            # to-one relationship
            else:
                if rel_data is None:
                    relatives[rel_name] = None
                else:
                    relatives[rel_name] = resources[
                        (rel_data["type"], rel_data["id"])
                    ]
        return relatives

    def save(self, resources):
        """
        :seealso: :meth:`DatabaseSession.save`
        """
        # Group the resources by the database, which is associated with them.
        group_key = lambda res: self.api.get_db(self.api.get_typename(res))
        for db, resources in groupby(resources, group_key):
            # We need to *list()* the resources, because groupby() allows
            # us to only iterate once over them.
            resources = list(resources)
            session = self.session_by_db(db)
            session.save(resources)
        return None

    def delete(self, resources):
        """
        :seealso: :meth:`DatabaseSession.delete`
        """
        # Group the resources by the database, which is associated with them.
        group_key = lambda res: self.api.get_db(self.api.get_typename(res))
        for db, resources in groupby(resources, group_key):
            # We need to *list()* the resources, because groupby() allows
            # us to only iterate once over them.
            resources = list(resources)
            session = self.session_by_db(db)
            session.delete(resources)
        return None

    def commit(self):
        """
        :seealso: :meth:`DatabaseSession.commit`
        """
        for session in self.sessions.values():
            session.commit()
        return None
