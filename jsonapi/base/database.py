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
from .utilities import ensure_identifier
from . import validators


__all__ = [
    "Database",
    "DatabaseSession",
    "BulkSession"
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
        self._sessions = dict()
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
        if not db in self._sessions:
            self._sessions[db] = db.session()
        return self._sessions[db]

    def session_by_db(self, db):
        """
        If a session for the database adapter *db* already exists, it is
        returned. Otherwise, a new session is created.

        :arg jsonapi.base.database.Database db:
        :rtype: jsonapi.base.database.DatabaseSession

        .. seealso::

            *   :meth:`Database.session`
        """
        if not db in self._sessions:
            self._sessions[db] = db.session()
        return self._sessions[db]

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
        the *resources*.

        E.g.: The *article* resource class has a relationship called *comments*
        and *author*. The *comment* class itself has a relationship *author*:

        .. code-block:: python3

            # Include the authors of the comments related to the articles.
            ["comments", "author"]

            # Include the authors of the articles.
            ["author"]

        This method follow the include paths and returns a dictionary, which
        contains all related resources on every include path.

        :arg list resources:
        :arg list include_paths:

        :raises jsonapi.base.errors.IncludePathNotFound:

        .. seealso::

            *   :attr:`jsonapi.base.request.Request.japi_include`
            *   http://jsonapi.org/format/#fetching-includes

        .. todo::

            This method can be more efficient: Walk done the include paths
            simultaneous instead one by one. For example:

            .. code-block:: python3

                ["comments", "author"]
                ["author"]

            Wished behaviour: (2 calls of *get_many()*)

            1. Get the ids of the comments and the article authors
            2. Load these ids
            3. Get the ids of the comment authors

            Current behaviour: (3 calls of *get_many()*)

            1. Get the ids of the comments
            2. Load the comments
            3. Get the ids of the comment authors
            4. Load the comment authors
            5. Get the ids of the article authors
            6. Load the article authors
        """
        result = dict()
        for include_path in include_paths:

            # Follow the include path.
            # The include path is a list of relationship names and the
            # first relationship is defined on the *resources*.
            curr_resources = resources
            for relname in include_path:
                relative_identifiers = set()
                for resource in curr_resources:
                    typename = self.api.get_typename(resource)
                    schema_ = self.api.get_schema(typename)
                    rel = schema_.relationships.get(relname)

                    # Raise an exception, if we can not resolve the path.
                    if rel is None:
                        raise errors.IncludePathNotFound(include_path)

                    # Get the id the related resource (one or None)
                    elif rel.to_one:
                        identifier = rel.get(resource)
                        if identifier is not None:
                            identifier = ensure_identifier(self.api, identifier)
                            relative_identifiers.add(identifier)

                    # Get the ids of the related resources.
                    else:
                        identifiers = rel.get(resource)
                        identifiers = [
                            ensure_identifier(self.api, item) for item in identifiers
                        ]
                        relative_identifiers.update(identifiers)

                # Load all related resources.
                relatives = self.get_many(relative_identifiers)
                result.update(relatives)

                # The next relationship path component is defined on
                # *relatives*
                curr_resources = list(relatives.values())
        return result

    def load_japi_relationships(self, reldoc):
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

        :arg dict reldoc:
        """
        # Collect all ids.
        ids = set()
        for relname in reldoc.keys():
            reldata = reldoc[relname].get("data")
            if isinstance(reldata, dict):
                ids.add((reldata["type"], reldata["id"]))
            elif isinstance(reldata, list):
                ids.update(
                    (item["type"], item["id"]) for item in reldata
                )

        # Query the resources.
        relatives = self.get_many(ids)

        # Map the relationships to the related resources.
        result = dict()
        for relname in reldoc.keys():
            # Skip the relationship, if the *data* dictionary is not present.
            if not "data" in reldoc[relname]:
                continue

            reldata = reldoc[relname]["data"]
            if reldata is None:
                result[relname] = None
            elif isinstance(reldata, dict):
                result[relname] = relatives.get(
                    (reldata["type"], reldata["id"])
                )
            elif isinstance(reldata, list):
                result[relname] = [
                    relatives.get((item["type"], item["id"])) \
                    for item in reldata
                ]
        return result

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
        for session in self._sessions.values():
            session.commit()
        return None
