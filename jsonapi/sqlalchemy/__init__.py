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
jsonapi.sqlalchemy
==================

Contains the *sqlalchemy* database adapter and JSONapi schema.

Tutorial
--------

If you have an *sqlalchemy* model, use the *sqlalchemy* database adapter and
the *sqlalchemy* JSONapi schema:

.. code-block:: python3

    schema = jsonapi.sqlalchemy.Serializer(MyModel)
    db = jsonapi.sqlalchemy.Database(sessionmaker=Session)

However, here is a short example:

.. literalinclude:: ../../examples/sqlalchemy/example.py
    :linenos:

sessionmaker
~~~~~~~~~~~~

.. seealso::

    http://docs.sqlalchemy.org/en/latest/orm/session.html

Performing *queries* with *sqlalchemy* requires a *Session*. The database
adapter requires a function *sessionmaker*, which returns a valid *session*.

You can provide the *sessionmaker* as *init* argument for the database
adapter:

.. code-block:: python3

    db = jsonapi.sqlalchemy.Database(sessionmaker=get_session)

or you use the *settings* dictionary of the API:

.. code-block:: python3

    api.settings["sqlalchemy_sessionmaker"] = get_session

API
---

.. autoclass:: jsonapi.sqlalchemy.schema.Schema
.. autoclass:: jsonapi.sqlalchemy.database.Database

Todo
----

.. todo::

    Find hybrid methods and properties
"""

from .database import Database
from .schema import Schema
