#!/usr/bin/env python3

"""
jsonapi.mongoengine
===================

:license: GNU Affero General Public License v3
:copyright: 2016 by Benedikt Schmitt <benedikt@benediktschmitt.de>

This package contains the database adapter and schema for mongoengine
documents. It will detect and add mongoengine fields to the jsonapi schema
automatic.

Using mongoengine models with *py-jsonapi* is quite straightforward:

.. literalinclude:: ../../examples/mongoengine/example.py
    :linenos:
    :emphasize-lines: 6, 30-31, 35, 40-41

API
---

.. automodule:: jsonapi.mongoengine.schema
.. automodule:: jsonapi.mongoengine.database
"""

# local
from .database import Database
from .schema import Schema
