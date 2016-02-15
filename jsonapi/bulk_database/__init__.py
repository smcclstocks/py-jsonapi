#!/usr/bin/env python3

"""
jsonapi.bulk_database
=====================

:license: GNU Affero General Public License v3

This package contains a container for other database adapters. If your
application uses **different database engines**, you can use this adapter, which
provides a transparent layer and selects the correct database for each type
automatic.

Tutorial
--------

Our application has a *User* and *Session* model. The users are stored in an
sql database and the sessions in redis for performance reasons. To add both
models to the JSONapi, you can use the bulk database:

.. code-block:: python3

    bulk_db = jsonapi.bulk_database.Database()
    redis_db = jsonapi.redis.Database() # Does not exist yet :(
    sql_db = jsonapi.sqlalchemy.Database()

    api = jsonapi.base.api.API("/api", db=bulk_db)

    api.add_type(user_schema)
    api.add_type(session_schema)

    # Tell the bulk database, which database driver it must use for the
    # models.
    bulk_db.add_type(user_schema, sql_db)
    bulk_db.add_type(session_schema, redis_db)

API
---

.. autoclass:: jsonapi.bulk_database.database.Database
"""

# local
from . database import Database
