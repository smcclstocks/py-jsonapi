#!/usr/bin/env python3

"""
jsonapi.asyncio
===============

:license: GNU Affero General Public License v3

.. hint::

    This package is basically a copy of ``jsonapi.base``, but adds to each
    database call an *await*:

    .. code-block:: python3

        # in jsonapi.base
        db.get_many()

        # in jsonapi.asyncio
        await db.get_many()

    This is is the only difference. If you know how to merge the *base* and
    *async* code, please create a pull request or tell me how to do it on
    GitHub.

Contains an API base application for **asynchronous** database adapters.

.. automodule:: jsonapi.asyncio.api
.. automodule:: jsonapi.asyncio.database
.. automodule:: jsonapi.asyncio.handler
.. automodule:: jsonapi.asyncio.serializer
"""

# local
from . import api
from . import database
from . import handler
from . import serializer
