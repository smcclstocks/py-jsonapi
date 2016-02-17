#!/usr/bin/env python3

"""
jsonapi.motorengine
===================

:license: GNU Affero General Public License v3

This package contains the database adapter and schema for motorengine
documents. It will detect and add motorengine fields to the jsonapi schema
automatic.

Using motorengine models with *py-jsonapi* is quite straightforward:

.. literalinclude:: ../../examples/motorengine/example.py
    :linenos:

API
---

.. autoclass:: jsonapi.motorengine.schema.Schema
.. autoclass:: jsonapi.motorengine.database.Database
"""

# local
from .database import Database
from .schema import Schema
