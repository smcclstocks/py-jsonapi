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
jsonapi.bulk_database
=====================

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
