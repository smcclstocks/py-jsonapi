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
jsonapi.bulk_database.database
==============================
"""

# std
from itertools import groupby

# local
import jsonapi


__all__ = [
    "Database"
]


class Database(jsonapi.base.database.Database):
    """
    This adapter is only a *proxy*. You must associate each type with a database
    adapter, on setup.
    """

    def __init__(self, api):
        super().__init__(api)

        # typename to database adapter
        self._dbs = dict()
        return None

    def session(self):
        return Session(api=self.api, db=self)

    def get_db(self, typename):
        """
        Returns the database adapter associated with the type *typename*.

        :arg str typename:
        :raises KeyError: If the typename is no associated with a database.
        """
        return self._dbs[typename]

    def add_type(self, typename, db):
        """
        Associates the type *typename* with the database adapter *db*. The
        models must be registered on the :attr:`api`.

        .. code-block:: python3

            db.add_type("users", sql_db)
            db.add_type("session", redis_db)

        :arg str typename:
        :arg jsonapi.base.database.Database db:

        :seealso: :meth:`add_schema`
        """
        self._dbs[typename] = db
        return None

    def add_schema(self, schema, db):
        """
        Associates the *schema* with the database adapter *db*.

        .. code-block:: python3

            db.add_schema(User, sql_db)
            db.add_schema(Session, redis_db)
        """
        self._dbs[schema.typename] = db
        return None


class Session(jsonapi.base.database.Session):
    """
    Works like the normal session object, but selects for each type the
    correct database adapter and forwards the query to it.

    :arg jsonapi.base.api.API api:
    :arg jsonapi.bulk_database.database.Database db:
    """

    def __init__(self, api, db):
        """
        """
        self.api = api
        self.db = db

        # Maps the database adapter to the database session.
        self._sessions = dict()
        return None

    def session(self, typename):
        """
        Returns the database session, which must be used for resources of the
        type *typename*. If no session for the database has been created yet, it
        will be done now.

        :arg str typename:
        :rtype: jsonapi.base.database.Session
        """
        db = self.db.get_db(typename)
        if not db in self._sessions:
            self._sessions[db] = db.session()
        return self._sessions[db]

    def session_by_db(self, db):
        """
        If a session for the database adapter *db* already exists, it is
        returned. Otherwise, a new session is created.

        :arg jsonapi.base.database.Database db:
        :rtype: jsonapi.base.database.Session
        """
        if not db in self._sessions:
            self._sessions[db] = db.session()
        return self._sessions[db]

    def query(self, typename,
        *, order=None, limit=None, offset=None, filters=None
        ):
        """
        """
        session = self.session(typename)
        return session.query(
            typename, order=order, limit=limit, offset=offset, filters=filters
        )

    def query_size(self, typename,
        *, order=None, limit=None, offset=None, filters=None
        ):
        """
        """
        session = self.session(typename)
        return session.query_size(
            typename, order=order, limit=limit, offset=offset, filters=filters
        )

    def get(self, identifier):
        """
        """
        typename, resource_id = identifier
        session = self.session(typename)
        return session.get(identifier)

    def get_many(self, identifiers):
        """
        :seealso: :meth:`Session.get_many`
        """
        result = dict()

        # Group the resources by the typenames
        group_key = lambda identifier: identifier[0]
        for typename, identifiers in groupby(identifiers, group_key):
            # We need to *list()* the identifiers, because groupby() allows
            # us to only iterate once over them.
            identifiers = list(identifiers)
            session = self.session(typename)
            resources = session.get_many(identifiers)
            result.update(resources)
        return result

    def save(self, resources):
        """
        """
        for typename, resources in groupby(resources, self.api.get_typename):
            # We need to *list()* the resources, because groupby() allows
            # us to only iterate once over them.
            resources = list(resources)
            session = self.session(typename)
            session.save(resources)
        return None

    def delete(self, resources):
        """
        """
        for typename, resources in groupby(resources, self.api.get_typename):
            # We need to *list()* the resources, because groupby() allows
            # us to only iterate once over them.
            resources = list(resources)
            session = self.session(typename)
            session.delete(resources)
        return None

    def commit(self):
        """
        """
        for session in self._sessions.values():
            session.commit()
        return None
