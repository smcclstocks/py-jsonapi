#!/usr/bin/env python3

"""
jsonapi.sqlalchemy
==================

:license: GNU Affero General Public License v3
:copyright: 2016 by Benedikt Schmitt <benedikt@benediktschmitt.de>

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
    :emphasize-lines: 4, 44, 46-47

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

    Support hybrid methods and properties
"""

from .database import Database
from .schema import Schema
