#!/usr/bin/env python3

"""
jsonapi.base
============

:license: GNU Affero General Public License v3
:copyright: 2016 by Benedikt Schmitt <benedikt@benediktschmitt.de>

This is the *base* of the *py-jsonapi* library. It contains the definition for
interfaces (database, serializer), which can be overridden and then used by an
API instance.

.. automodule:: jsonapi.base.handler
.. automodule:: jsonapi.base.api
.. automodule:: jsonapi.base.database
.. automodule:: jsonapi.base.errors
.. automodule:: jsonapi.base.pagination
.. automodule:: jsonapi.base.request
.. automodule:: jsonapi.base.response
.. automodule:: jsonapi.base.schema
.. automodule:: jsonapi.base.serializer
.. automodule:: jsonapi.base.utilities
.. automodule:: jsonapi.base.validators
"""

# local
from . import handler
from . import api
from . import database
from . import errors
from .request import Request
from .response import Response
from . import schema
from .serializer import Serializer
from . import utilities
from . import validators
